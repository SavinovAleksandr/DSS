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
        from utils.logger import logger
        
        logger.info("=" * 80)
        logger.info("НАЧАЛО МЕТОДА calc() В MdpStabilityCalc")
        logger.info("=" * 80)
        logger.info(f"Количество режимов: {len(self._rgms)}")
        logger.info(f"Количество вариантов: {len(self._vrns)}")
        logger.info(f"Количество сценариев: {len(self._scns)}")
        logger.info(f"Максимальное количество шагов: {self.max}")
        
        progress = 0
        results = []
        tmp_file = self._root / "mdp_calc_tmp.rst"
        tmp_file_base = self._root / "mdp_calc_tmp_base.rst"  # Базовое состояние до калибровки
        logger.info(f"Временный файл: {tmp_file}")
        logger.info(f"Базовый временный файл: {tmp_file_base}")
        
        # Начальный прогресс
        logger.info(f"Вызов progress_callback с progress={progress}")
        if self._progress_callback:
            try:
                self._progress_callback(progress)
                logger.info("progress_callback выполнен успешно")
            except Exception as e:
                logger.error(f"Ошибка в progress_callback: {e}")
        else:
            logger.warning("progress_callback не установлен!")
        
        logger.info("Начало цикла по режимам (rgms)")
        for rgm_idx, rgm in enumerate(self._rgms):
            logger.info(f"[РЕЖИМ {rgm_idx + 1}/{len(self._rgms)}] Обработка режима: {Path(rgm.name).stem}")
            mdp_shems_list = []
            
            logger.info(f"[РЕЖИМ {rgm_idx + 1}] Начало цикла по вариантам (vrns)")
            for vrn_idx, vrn in enumerate(self._vrns):
                logger.info(f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}/{len(self._vrns)}] Обработка варианта: {vrn.name}")
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
                
                logger.info(f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}/{len(self._vrns)}] Обработка варианта: {vrn.name}")
                logger.info(f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}] Начало цикла по сценариям (scns)")
                for scn_idx, scn in enumerate(self._scns):
                    logger.info(f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}/{len(self._scns)}] Обработка сценария: {Path(scn.name).stem}")
                    
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Создание объекта RastrOperations")
                    rastr = RastrOperations()
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] RastrOperations создан")
                    
                    # Инициализация схемы (только один раз)
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Проверка is_ready: {mdp_shem.is_ready}")
                    if not mdp_shem.is_ready:
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] ИНИЦИАЛИЗАЦИЯ СХЕМЫ: {vrn.name} для режима {Path(rgm.name).stem}")
                        # Обновление прогресса при начале инициализации схемы
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Вызов progress_callback (инициализация)")
                        if self._progress_callback:
                            try:
                                self._progress_callback(progress)
                            except Exception as e:
                                logger.error(f"Ошибка в progress_callback: {e}")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Загрузка режима: {rgm.name}")
                        rastr.load(rgm.name)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Режим загружен")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Настройка параметров динамики")
                        rastr.dyn_settings()
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Параметры динамики настроены")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Применение варианта: vrn.id={vrn.id}, vrn.num={vrn.num}")
                        if vrn.id == -1:
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Вызов rgm() (базовый вариант)")
                            mdp_shem.is_stable = rastr.rgm()
                        else:
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Вызов apply_variant({vrn.num}, {self._rems_path})")
                            mdp_shem.is_stable = rastr.apply_variant(vrn.num, self._rems_path)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Результат применения варианта (is_stable): {mdp_shem.is_stable}")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Сохранение базового состояния во временный файл: {tmp_file_base}")
                        rastr.save(str(tmp_file_base))
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Базовый файл сохранен")
                        mdp_shem.is_ready = True
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] is_ready установлен в True")
                        
                        if mdp_shem.is_stable:
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Схема устойчива, продолжаем инициализацию")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Загрузка базового временного файла: {tmp_file_base}")
                            rastr.load(str(tmp_file_base))
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Загрузка файла сечений: {self._sechen_path}")
                            rastr.load(self._sechen_path)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Загрузка файла VIR: {self._vir_path}")
                            rastr.load(self._vir_path)
                            
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Получение p_start для сечения {self._selected_sch}")
                            mdp_shem.p_start = rastr.get_val("sechen", "psech", self._selected_sch)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] p_start = {mdp_shem.p_start}")
                            
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Вызов run_ut() для определения max_step")
                            mdp_shem.max_step = rastr.run_ut()
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] max_step = {mdp_shem.max_step}")
                            
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Получение p_pred для сечения {self._selected_sch}")
                            mdp_shem.p_pred = rastr.get_val("sechen", "psech", self._selected_sch)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] p_pred = {mdp_shem.p_pred}")
                            
                            # Калибровка шага
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] НАЧАЛО КАЛИБРОВКИ ШАГА")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Загрузка базового временного файла для калибровки: {tmp_file_base}")
                            rastr.load(str(tmp_file_base))
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Загрузка VIR для калибровки")
                            rastr.load(self._vir_path)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Вызов step({mdp_shem.max_step * 0.9})")
                            mdp_shem.max_step = rastr.step(mdp_shem.max_step * 0.9)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] max_step после первого step = {mdp_shem.max_step}")
                            
                            p_current = rastr.get_val("sechen", "psech", self._selected_sch)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] p_current после первого step = {p_current}")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Целевое значение: p_pred * 0.9 = {mdp_shem.p_pred * 0.9}")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Разница: {abs(p_current - mdp_shem.p_pred * 0.9)}")
                            
                            iteration = 0
                            max_calibration_iterations = 50  # Максимум итераций калибровки
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Начало цикла калибровки (макс. {max_calibration_iterations} итераций)")
                            while abs(p_current - mdp_shem.p_pred * 0.9) > 2.0 and iteration < max_calibration_iterations:
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}] Калибровка, итерация {iteration + 1}: p_current={p_current:.2f}, цель={mdp_shem.p_pred * 0.9:.2f}, разница={abs(p_current - mdp_shem.p_pred * 0.9):.2f}")
                                logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Калибровка, итерация {iteration + 1}: загрузка базового файла: {tmp_file_base}")
                                rastr.load(str(tmp_file_base))
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
                            
                            # Сохраняем состояние после калибровки (но это не нужно для других сценариев)
                            # rastr.save(str(tmp_file))  # Убрано, чтобы не влиять на другие сценарии
                    
                    if not mdp_shem.is_stable:
                        logger.warning(f"[СЦЕНАРИЙ {scn_idx + 1}] Схема нестабильна, пропуск дальнейших расчетов")
                        break
                    
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Схема устойчива, продолжаем расчеты")
                    no_pa_sechen = []
                    no_pa_kpr = []
                    with_pa_sechen = []
                    with_pa_kpr = []
                    no_pa_mdp = -1.0
                    with_pa_mdp = -1.0
                    
                    precision = max(2.0, min(10.0, math.floor(mdp_shem.p_pred * 0.02)))
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Точность расчета: {precision}")
                    
                    # Расчет без ПА
                    if self._no_pa:
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] ========== НАЧАЛО РАСЧЕТА БЕЗ ПА ==========")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Начало расчета МДП без ПА для сценария {Path(scn.name).stem}")
                        # Обновление прогресса при начале расчета без ПА
                        if self._progress_callback:
                            self._progress_callback(progress)
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Загрузка файлов для расчета")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Загрузка базового временного файла: {tmp_file_base}")
                        rastr.load(str(tmp_file_base))
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Загрузка файла сечений")
                        rastr.load(self._sechen_path)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Загрузка файла VIR")
                        rastr.load(self._vir_path)
                        
                        # Получаем значение сечения ДО загрузки сценария (для сравнения)
                        p_before_scn = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Значение сечения ДО загрузки сценария: {p_before_scn:.2f}")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Загрузка сценария: {scn.name}")
                        rastr.load(scn.name)
                        
                        # Получаем значение сечения ПОСЛЕ загрузки сценария (ДО расчета динамики)
                        p_after_scn = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Значение сечения ПОСЛЕ загрузки сценария (ДО run_dynamic): {p_after_scn:.2f} (изменение от базового: {p_after_scn - p_before_scn:.2f})")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Сценарий: {Path(scn.name).stem}")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Загрузка шаблона .dfw")
                        rastr.load_template(".dfw")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Все файлы загружены")
                        
                        # Получаем значение сечения ДО расчета динамики (после загрузки шаблона)
                        p_before_dyn = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Значение сечения ДО run_dynamic (после загрузки шаблона): {p_before_dyn:.2f}")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Вызов run_dynamic(ems=True)")
                        dyn_result = rastr.run_dynamic(ems=True)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Результат динамики: успех={dyn_result.is_success}, устойчивость={dyn_result.is_stable}")
                        
                        # Получаем значение сечения ПОСЛЕ расчета динамики для диагностики
                        p_after_dyn = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Значение сечения ПОСЛЕ run_dynamic: {p_after_dyn:.2f} (изменение: {p_after_dyn - p_before_dyn:.2f})")
                        
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
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Итерация {iteration + 1}: загрузка файлов")
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Итерация {iteration + 1}: загрузка базового файла: {tmp_file_base}")
                                rastr.load(str(tmp_file_base))
                                rastr.load(self._vir_path)
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Итерация {iteration + 1}: вызов step({step_current:.2f})")
                                step_actual = rastr.step(step_current)
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Итерация {iteration + 1}: step_actual={step_actual:.2f}")
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Итерация {iteration + 1}: вызов run_dynamic(ems=True)")
                                dyn_result = rastr.run_dynamic(ems=True)
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Итерация {iteration + 1}: результат динамики: success={dyn_result.is_success}, stable={dyn_result.is_stable}")
                                
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
                                
                                # Логирование каждые 20 итераций для диагностики
                                if iteration % 20 == 0:
                                    logger.debug(f"Поиск МДП без ПА: итерация {iteration}, p_current={p_current:.2f}, p_stable={p_stable:.2f}, precision={precision:.2f}")
                            
                            if iteration >= max_mdp_iterations:
                                from utils.logger import logger
                                logger.warning(f"Достигнуто максимальное количество итераций поиска МДП без ПА ({max_mdp_iterations}) для сценария {Path(scn.name).stem}")
                            
                            no_pa_mdp = rastr.get_val("sechen", "psech", self._selected_sch)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] МДП найден после итераций: {no_pa_mdp:.2f}")
                        elif dyn_result.is_success and dyn_result.is_stable:
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Результат сразу устойчив, МДП = значение сечения ПОСЛЕ загрузки сценария")
                            # Используем значение ПОСЛЕ загрузки сценария (ДО run_dynamic)
                            # Это значение отражает состояние после применения конкретного сценария
                            # и должно быть разным для разных сценариев
                            no_pa_mdp = p_after_scn
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] МДП (устойчив): {no_pa_mdp:.2f}")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Сценарий: {Path(scn.name).stem}")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Значения: p_start={mdp_shem.p_start:.2f}, p_before_scn={p_before_scn:.2f}, p_after_scn={p_after_scn:.2f}, p_before_dyn={p_before_dyn:.2f}, p_after_dyn={p_after_dyn:.2f}")
                        else:
                            logger.warning(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Расчет динамики не успешен, МДП = -1")
                            no_pa_mdp = -1.0
                        
                        # Сбор данных по сечениям (всегда, если расчет выполнен)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Сбор данных по сечениям ПОСЛЕ расчета динамики")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Сценарий: {Path(scn.name).stem}, no_pa_mdp={no_pa_mdp:.2f}")
                        for sch in [s for s in self._schs if s.control]:
                            try:
                                value = rastr.get_val("sechen", "psech", sch.id)
                                no_pa_sechen.append(Values(
                                    id=sch.id,
                                    name=sch.name,
                                    value=value
                                ))
                                logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Сечение {sch.name} (ID {sch.id}): {value:.2f}")
                            except Exception as e:
                                logger.error(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Ошибка при получении значения сечения {sch.name} (ID {sch.id}): {e}")

                        # Сбор данных по контролируемым величинам (всегда, если расчет выполнен)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Сбор данных по контролируемым величинам")
                        for kpr in self._kprs:
                            try:
                                value = rastr.get_val(kpr.table, kpr.col, kpr.selection)
                                no_pa_kpr.append(Values(
                                    id=kpr.id,
                                    name=kpr.name,
                                    value=value
                                ))
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] КПР {kpr.name} (ID {kpr.id}): {value:.2f}")
                            except Exception as e:
                                logger.error(f"[СЦЕНАРИЙ {scn_idx + 1}, БЕЗ ПА] Ошибка при получении значения КПР {kpr.name} (ID {kpr.id}): {e}")
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                    
                    # Расчет с ПА
                    if self._with_pa:
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] ========== НАЧАЛО РАСЧЕТА С ПА ==========")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Начало расчета МДП с ПА для сценария {Path(scn.name).stem}")
                        # Обновление прогресса при начале расчета с ПА
                        if self._progress_callback:
                            self._progress_callback(progress)
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Загрузка файлов для расчета")
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Загрузка базового временного файла: {tmp_file_base}")
                        rastr.load(str(tmp_file_base))
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Загрузка файла сечений")
                        rastr.load(self._sechen_path)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Загрузка файла VIR")
                        rastr.load(self._vir_path)
                        
                        # Получаем значение сечения ДО загрузки сценария/ПА (для сравнения)
                        p_before_scn_pa = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Значение сечения ДО загрузки сценария/ПА: {p_before_scn_pa:.2f}")
                        
                        if self._use_lpn:
                            rastr.load(self._sechen_path)
                            rastr.create_scn_from_lpn(self._lapnu_path, self._lpns, scn.name)
                        else:
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Загрузка сценария: {scn.name}")
                            rastr.load(scn.name)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Загрузка ПА: {self._lapnu_path}")
                            rastr.load(self._lapnu_path)
                        
                        # Получаем значение сечения ПОСЛЕ загрузки сценария/ПА (ДО расчета динамики)
                        p_after_scn_pa = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Значение сечения ПОСЛЕ загрузки сценария/ПА (ДО run_dynamic): {p_after_scn_pa:.2f} (изменение от базового: {p_after_scn_pa - p_before_scn_pa:.2f})")
                        
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Вызов run_dynamic(ems=True)")
                        dyn_result = rastr.run_dynamic(ems=True)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Результат динамики: успех={dyn_result.is_success}, устойчивость={dyn_result.is_stable}")
                        
                        # Получаем значение сечения ПОСЛЕ расчета динамики для диагностики
                        p_after_dyn_pa = rastr.get_val("sechen", "psech", self._selected_sch)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Значение сечения ПОСЛЕ run_dynamic: {p_after_dyn_pa:.2f} (изменение: {p_after_dyn_pa - p_after_scn_pa:.2f})")
                        
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
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Итерация {iteration + 1}: загрузка базового файла: {tmp_file_base}")
                                rastr.load(str(tmp_file_base))
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
                                
                                # Логирование каждые 20 итераций для диагностики
                                if iteration % 20 == 0:
                                    logger.debug(f"Поиск МДП с ПА: итерация {iteration}, p_current={p_current:.2f}, p_stable={p_stable:.2f}, precision={precision:.2f}")
                            
                            if iteration >= max_mdp_iterations:
                                from utils.logger import logger
                                logger.warning(f"Достигнуто максимальное количество итераций поиска МДП с ПА ({max_mdp_iterations}) для сценария {Path(scn.name).stem}")
                            
                            with_pa_mdp = rastr.get_val("sechen", "psech", self._selected_sch)
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] МДП найден после итераций: {with_pa_mdp:.2f}")
                        elif dyn_result.is_success and dyn_result.is_stable:
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Результат сразу устойчив, МДП = значение сечения ПОСЛЕ загрузки сценария/ПА")
                            # Используем значение ПОСЛЕ загрузки сценария/ПА (ДО run_dynamic)
                            # Это значение отражает состояние после применения конкретного сценария и ПА
                            with_pa_mdp = p_after_scn_pa
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] МДП (устойчив): {with_pa_mdp:.2f}")
                            logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Значения: p_start={mdp_shem.p_start:.2f}, p_before_scn_pa={p_before_scn_pa:.2f}, p_after_scn_pa={p_after_scn_pa:.2f}, p_after_dyn_pa={p_after_dyn_pa:.2f}")
                        else:
                            logger.warning(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Расчет динамики не успешен, МДП = -1")
                            with_pa_mdp = -1.0
                        
                        # Сбор данных по сечениям (всегда, если расчет выполнен)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Сбор данных по сечениям")
                        for sch in [s for s in self._schs if s.control]:
                            try:
                                value = rastr.get_val("sechen", "psech", sch.id)
                                with_pa_sechen.append(Values(
                                    id=sch.id,
                                    name=sch.name,
                                    value=value
                                ))
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Сечение {sch.name} (ID {sch.id}): {value:.2f}")
                            except Exception as e:
                                logger.error(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Ошибка при получении значения сечения {sch.name} (ID {sch.id}): {e}")

                        # Сбор данных по контролируемым величинам (всегда, если расчет выполнен)
                        logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Сбор данных по контролируемым величинам")
                        for kpr in self._kprs:
                            try:
                                value = rastr.get_val(kpr.table, kpr.col, kpr.selection)
                                with_pa_kpr.append(Values(
                                    id=kpr.id,
                                    name=kpr.name,
                                    value=value
                                ))
                                logger.debug(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] КПР {kpr.name} (ID {kpr.id}): {value:.2f}")
                            except Exception as e:
                                logger.error(f"[СЦЕНАРИЙ {scn_idx + 1}, С ПА] Ошибка при получении значения КПР {kpr.name} (ID {kpr.id}): {e}")
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                    
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Создание объекта MdpEvents для сценария: {Path(scn.name).stem}")
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] Данные для сохранения: no_pa_mdp={no_pa_mdp:.2f}, сечений={len(no_pa_sechen)}, КПР={len(no_pa_kpr)}")
                    mdp_event = MdpEvents(
                        name=Path(scn.name).stem,
                        no_pa_sechen=no_pa_sechen.copy() if no_pa_sechen else [],
                        no_pa_kpr=no_pa_kpr.copy() if no_pa_kpr else [],
                        no_pa_mdp=no_pa_mdp,
                        with_pa_sechen=with_pa_sechen.copy() if with_pa_sechen else [],
                        with_pa_kpr=with_pa_kpr.copy() if with_pa_kpr else [],
                        with_pa_mdp=with_pa_mdp
                    )
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] MdpEvents создан: name={mdp_event.name}, no_pa_mdp={mdp_event.no_pa_mdp:.2f}")
                    events_list.append(mdp_event)
                    logger.info(f"[СЦЕНАРИЙ {scn_idx + 1}] MdpEvents добавлен в events_list. Всего событий: {len(events_list)}")
                
                mdp_shem.events = events_list
                mdp_shems_list.append(mdp_shem)
            
            results.append(MdpResults(
                rg_name=Path(rgm.name).stem,
                mdp_shems=mdp_shems_list
            ))
        
        logger.info("Завершение всех циклов")
        logger.info(f"Получено результатов для режимов: {len(results)}")
        
        # Финальное обновление прогресса (100%)
        progress += 1
        logger.info(f"Финальное обновление прогресса: {progress}/{self.max}")
        if self._progress_callback:
            try:
                self._progress_callback(progress)
                logger.info("Финальный progress_callback выполнен")
            except Exception as e:
                logger.error(f"Ошибка в финальном progress_callback: {e}")
        else:
            logger.warning("Финальный progress_callback не установлен")
        
        # Удаление временных файлов
        logger.info(f"Удаление временных файлов")
        if tmp_file.exists():
            tmp_file.unlink()
            logger.info(f"Временный файл удален: {tmp_file}")
        else:
            logger.warning(f"Временный файл не найден для удаления: {tmp_file}")
        if tmp_file_base.exists():
            tmp_file_base.unlink()
            logger.info(f"Базовый временный файл удален: {tmp_file_base}")
        else:
            logger.warning(f"Базовый временный файл не найден для удаления: {tmp_file_base}")
        
        logger.info("=" * 80)
        logger.info("КОНЕЦ МЕТОДА calc() В MdpStabilityCalc")
        logger.info(f"Возвращаем {len(results)} результатов")
        logger.info("=" * 80)
        return results

