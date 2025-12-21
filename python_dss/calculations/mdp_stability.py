"""
Расчет максимально допустимых перетоков мощности (МДП ДУ)
"""

import os
import math
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from models import (
    RgmsInfo, ScnsInfo, VrnInfo, SchInfo, KprInfo,
    MdpResults, MdpShems, MdpEvents, Values
)
from rastr_operations import RastrOperations
from utils.exceptions import InitialDataException


class MdpStabilityCalc:
    """Расчет максимально допустимых перетоков мощности по критерию ДУ"""
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]],
                 rgms: List[RgmsInfo], scns: List[ScnsInfo], vrns: List[VrnInfo],
                 rems_path: Optional[str], vir_path: Optional[str], sechen_path: Optional[str],
                 lapnu_path: Optional[str], schs: List[SchInfo], kprs: List[KprInfo],
                 lpns: str, selected_sch: int, no_pa: bool, with_pa: bool, use_lpn: bool):
        """
        Инициализация расчета МДП ДУ
        
        Args:
            progress_callback: Функция обратного вызова для обновления прогресса
            rgms: Список расчетных режимов
            scns: Список аварийных процессов
            vrns: Список вариантов (ремонтных схем)
            rems_path: Путь к файлу ремонтных схем
            vir_path: Путь к файлу траектории утяжеления
            sechen_path: Путь к файлу сечений
            lapnu_path: Путь к файлу ПА
            schs: Список сечений
            kprs: Список контролируемых величин
            lpns: Строка с номерами LPN
            selected_sch: Номер выбранного сечения
            no_pa: Расчет без ПА
            with_pa: Расчет с ПА
            use_lpn: Использовать формат LPN
        """
        if not rgms or not scns or not vir_path or not sechen_path or (lapnu_path is None and with_pa) or (use_lpn and not sechen_path):
            error_msg = "Не заданы все исходные данные для определения допустимых перетоков мощности!\n\n"
            error_msg += f"Результаты проверки:\n"
            error_msg += f"Загружено расчетных режимов - {len(rgms)}\n"
            error_msg += f"Загружено аварийных процесслов - {len(scns)}\n"
            if not vir_path:
                error_msg += "Отсутствует траектория утяжеления!\n"
            if not sechen_path:
                error_msg += "Отсутствует файл контролируемых сечений!\n"
            if lapnu_path is None and with_pa:
                error_msg += "Включен расчет МДП с учетом ПА, но файл ПА отсутствует!\n"
            if use_lpn and not sechen_path:
                error_msg += "Используется файл ПА в формате lpn, но не загружен файл сечений!\n"
            raise InitialDataException(error_msg)
        
        self._progress_callback = progress_callback
        self._rgms = rgms
        self._scns = scns
        self._vrns = [v for v in vrns if not v.deactive]
        self._rems_path = rems_path
        self._vir_path = vir_path
        self._sechen_path = sechen_path
        self._lapnu_path = lapnu_path
        self._schs = schs
        self._kprs = kprs
        self._lpns = lpns
        self._selected_sch = selected_sch
        self._no_pa = no_pa
        self._with_pa = with_pa
        self._use_lpn = use_lpn
        
        # Создание папки для результатов
        from utils.config import config
        results_dir = config.get_path("paths.results_dir")
        self._root = results_dir / f"{datetime.now():%Y-%m-%d %H-%M-%S} МДП ДУ"
        self._root.mkdir(parents=True, exist_ok=True)
    
    @property
    def root(self) -> str:
        """Путь к папке с результатами"""
        return str(self._root)
    
    @property
    def max(self) -> int:
        """Максимальное количество шагов расчета"""
        num_modes = (1 if self._no_pa else 0) + (1 if self._with_pa else 0)
        return len(self._rgms) * len(self._vrns) * len(self._scns) * num_modes + 1
    
    def calc(self) -> List[MdpResults]:
        """Выполнение расчета"""
        progress = 0
        results = []
        tmp_file = self._root / "mdp_calc_tmp.rst"
        
        # Начальный прогресс
        if self._progress_callback:
            self._progress_callback(progress)
        
        for rgm in self._rgms:
            mdp_shems_list = []
            
            for vrn in self._vrns:
                mdp_shem = MdpShems(
                    sheme_name=vrn.name,
                    is_ready=False,
                    is_stable=False,
                    max_step=0.0,
                    p_pred=0.0,
                    p_start=0.0,
                    events=[]
                )
                events_list = []
                
                for scn in self._scns:
                    rastr = RastrOperations()
                    
                    # Инициализация схемы (только один раз)
                    if not mdp_shem.is_ready:
                        # Обновление прогресса при начале инициализации схемы
                        if self._progress_callback:
                            self._progress_callback(progress)
                        
                        rastr.load(rgm.name)
                        rastr.dyn_settings()
                        
                        mdp_shem.is_stable = (rastr.rgm() if vrn.id == -1 else rastr.apply_variant(vrn.num, self._rems_path))
                        rastr.save(str(tmp_file))
                        mdp_shem.is_ready = True
                        
                        if mdp_shem.is_stable:
                            rastr.load(str(tmp_file))
                            rastr.load(self._sechen_path)
                            rastr.load(self._vir_path)
                            
                            mdp_shem.p_start = rastr.get_val("sechen", "psech", self._selected_sch)
                            mdp_shem.max_step = rastr.run_ut()
                            mdp_shem.p_pred = rastr.get_val("sechen", "psech", self._selected_sch)
                            
                            # Калибровка шага
                            rastr.load(str(tmp_file))
                            rastr.load(self._vir_path)
                            mdp_shem.max_step = rastr.step(mdp_shem.max_step * 0.9)
                            
                            p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                            iteration = 0
                            max_calibration_iterations = 50  # Максимум итераций калибровки
                            while abs(p_current - mdp_shem.p_pred * 0.9) > 2.0 and iteration < max_calibration_iterations:
                                rastr.load(str(tmp_file))
                                rastr.load(self._vir_path)
                                mdp_shem.max_step = rastr.step(mdp_shem.max_step * mdp_shem.p_pred * 0.9 / p_current)
                                p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                                iteration += 1
                                # Обновление прогресса при калибровке (каждые 3 итерации)
                                if iteration % 3 == 0 and self._progress_callback:
                                    self._progress_callback(progress)
                            
                            if iteration >= max_calibration_iterations:
                                from utils.logger import logger
                                logger.warning(f"Достигнуто максимальное количество итераций калибровки ({max_calibration_iterations}) для схемы {vrn.name}")
                            
                            rastr.save(str(tmp_file))
                    
                    if not mdp_shem.is_stable:
                        break
                    
                    no_pa_sechen = []
                    no_pa_kpr = []
                    with_pa_sechen = []
                    with_pa_kpr = []
                    no_pa_mdp = -1.0
                    with_pa_mdp = -1.0
                    
                    precision = max(2.0, min(10.0, math.floor(mdp_shem.p_pred * 0.02)))
                    
                    # Расчет без ПА
                    if self._no_pa:
                        # Обновление прогресса при начале расчета без ПА
                        if self._progress_callback:
                            self._progress_callback(progress)
                        
                        rastr.load(str(tmp_file))
                        rastr.load(self._sechen_path)
                        rastr.load(self._vir_path)
                        rastr.load(scn.name)
                        rastr.load_template(".dfw")
                        
                        dyn_result = rastr.run_dynamic(ems=True)
                        
                        if dyn_result.is_success and not dyn_result.is_stable:
                            p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                            p_stable = mdp_shem.p_start
                            step_min = 0.0
                            step_max = 0.0 - mdp_shem.max_step
                            step_current = step_min + (step_max - step_min) * 0.5
                            
                            iteration = 0
                            max_mdp_iterations = 100  # Максимум итераций поиска МДП
                            prev_step_current = None
                            stagnation_count = 0
                            
                            while dyn_result.is_success and (abs(p_current - p_stable) > precision or not dyn_result.is_stable) and iteration < max_mdp_iterations:
                                rastr.load(str(tmp_file))
                                rastr.load(self._vir_path)
                                step_actual = rastr.step(step_current)
                                dyn_result = rastr.run_dynamic(ems=True)
                                
                                if dyn_result.is_success and dyn_result.is_stable:
                                    step_max = step_actual
                                    p_stable = rastr.get_val("sechen", "psech", self._selected_sch)
                                else:
                                    step_min = step_actual
                                    p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                                    if step_min <= step_max or math.floor(p_current) <= math.floor(p_stable) + 2.0:
                                        step_max -= 2.0
                                
                                step_current = step_min + (step_max - step_min) * 0.5
                                
                                # Проверка на застой (если step_current не меняется)
                                if prev_step_current is not None and abs(step_current - prev_step_current) < 0.001:
                                    stagnation_count += 1
                                    if stagnation_count >= 10:
                                        from utils.logger import logger
                                        logger.warning(f"Обнаружен застой в поиске МДП без ПА (итерация {iteration}), прерываем цикл")
                                        break
                                else:
                                    stagnation_count = 0
                                
                                prev_step_current = step_current
                                iteration += 1
                                # Обновление прогресса при итерациях поиска МДП (каждые 3 итерации)
                                if iteration % 3 == 0 and self._progress_callback:
                                    self._progress_callback(progress)
                            
                            if iteration >= max_mdp_iterations:
                                from utils.logger import logger
                                logger.warning(f"Достигнуто максимальное количество итераций поиска МДП без ПА ({max_mdp_iterations}) для сценария {Path(scn.name).stem}")
                            
                            no_pa_mdp = rastr.get_val("sechen", "psech", self._selected_sch)
                        elif dyn_result.is_success and dyn_result.is_stable:
                            no_pa_mdp = rastr.get_val("sechen", "psech", self._selected_sch)
                        
                        # Сбор данных по сечениям
                        for sch in [s for s in self._schs if s.control]:
                            no_pa_sechen.append(Values(
                                id=sch.id,
                                name=sch.name,
                                value=rastr.get_val("sechen", "psech", sch.id)
                            ))
                        
                        # Сбор данных по контролируемым величинам
                        for kpr in self._kprs:
                            no_pa_kpr.append(Values(
                                id=kpr.id,
                                name=kpr.name,
                                value=rastr.get_val(kpr.table, kpr.col, kpr.selection)
                            ))
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                    
                    # Расчет с ПА
                    if self._with_pa:
                        # Обновление прогресса при начале расчета с ПА
                        if self._progress_callback:
                            self._progress_callback(progress)
                        
                        rastr.load(str(tmp_file))
                        rastr.load(self._sechen_path)
                        rastr.load(self._vir_path)
                        
                        if self._use_lpn:
                            rastr.load(self._sechen_path)
                            rastr.create_scn_from_lpn(self._lapnu_path, self._lpns, scn.name)
                        else:
                            rastr.load(scn.name)
                            rastr.load(self._lapnu_path)
                        
                        dyn_result = rastr.run_dynamic(ems=True)
                        
                        if dyn_result.is_success and not dyn_result.is_stable:
                            p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                            p_stable = mdp_shem.p_start
                            step_min = 0.0
                            step_max = 0.0 - mdp_shem.max_step
                            step_current = step_min + (step_max - step_min) * 0.5
                            
                            iteration = 0
                            max_mdp_iterations = 100  # Максимум итераций поиска МДП
                            prev_step_current = None
                            stagnation_count = 0
                            
                            while dyn_result.is_success and (abs(p_current - p_stable) > precision or not dyn_result.is_stable) and iteration < max_mdp_iterations:
                                rastr.load(str(tmp_file))
                                rastr.load(self._vir_path)
                                step_actual = rastr.step(step_current)
                                
                                if self._use_lpn:
                                    rastr.load(self._sechen_path)
                                    rastr.create_scn_from_lpn(self._lapnu_path, self._lpns, scn.name)
                                else:
                                    rastr.load(scn.name)
                                    rastr.load(self._lapnu_path)
                                
                                dyn_result = rastr.run_dynamic(ems=True)
                                
                                if dyn_result.is_success and dyn_result.is_stable:
                                    step_max = step_actual
                                    p_stable = rastr.get_val("sechen", "psech", self._selected_sch)
                                else:
                                    step_min = step_actual
                                    p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                                    if step_min <= step_max or math.floor(p_current) <= math.floor(p_stable) + 2.0:
                                        step_max -= 2.0
                                
                                step_current = step_min + (step_max - step_min) * 0.5
                                
                                # Проверка на застой (если step_current не меняется)
                                if prev_step_current is not None and abs(step_current - prev_step_current) < 0.001:
                                    stagnation_count += 1
                                    if stagnation_count >= 10:
                                        from utils.logger import logger
                                        logger.warning(f"Обнаружен застой в поиске МДП с ПА (итерация {iteration}), прерываем цикл")
                                        break
                                else:
                                    stagnation_count = 0
                                
                                prev_step_current = step_current
                                iteration += 1
                                # Обновление прогресса при итерациях поиска МДП с ПА (каждые 3 итерации)
                                if iteration % 3 == 0 and self._progress_callback:
                                    self._progress_callback(progress)
                            
                            if iteration >= max_mdp_iterations:
                                from utils.logger import logger
                                logger.warning(f"Достигнуто максимальное количество итераций поиска МДП с ПА ({max_mdp_iterations}) для сценария {Path(scn.name).stem}")
                            
                            with_pa_mdp = rastr.get_val("sechen", "psech", self._selected_sch)
                        elif dyn_result.is_success and dyn_result.is_stable:
                            with_pa_mdp = rastr.get_val("sechen", "psech", self._selected_sch)
                        
                        # Сбор данных по сечениям
                        for sch in [s for s in self._schs if s.control]:
                            with_pa_sechen.append(Values(
                                id=sch.id,
                                name=sch.name,
                                value=rastr.get_val("sechen", "psech", sch.id)
                            ))
                        
                        # Сбор данных по контролируемым величинам
                        for kpr in self._kprs:
                            with_pa_kpr.append(Values(
                                id=kpr.id,
                                name=kpr.name,
                                value=rastr.get_val(kpr.table, kpr.col, kpr.selection)
                            ))
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                    
                    events_list.append(MdpEvents(
                        name=Path(scn.name).stem,
                        no_pa_sechen=no_pa_sechen,
                        no_pa_kpr=no_pa_kpr,
                        no_pa_mdp=no_pa_mdp,
                        with_pa_sechen=with_pa_sechen,
                        with_pa_kpr=with_pa_kpr,
                        with_pa_mdp=with_pa_mdp
                    ))
                
                mdp_shem.events = events_list
                mdp_shems_list.append(mdp_shem)
            
            results.append(MdpResults(
                rg_name=Path(rgm.name).stem,
                mdp_shems=mdp_shems_list
            ))
        
        # Финальное обновление прогресса (100%)
        if self._progress_callback:
            self._progress_callback(progress)
        
        # Удаление временного файла
        if tmp_file.exists():
            tmp_file.unlink()
        
        return results

