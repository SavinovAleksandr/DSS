"""
Пакетный расчет динамической устойчивости
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from models import (
    RgmsInfo, ScnsInfo, VrnInfo, KprInfo,
    DynResults, DynShems, Events
)
from rastr_operations import RastrOperations, DynamicResult
from utils.exceptions import InitialDataException


class DynStabilityCalc:
    """Пакетный расчет динамической устойчивости"""
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]],
                 rgms: List[RgmsInfo], scns: List[ScnsInfo], vrns: List[VrnInfo],
                 rems_path: Optional[str], kprs: List[KprInfo], sechen_path: Optional[str],
                 lapnu_path: Optional[str], save_grf: bool, lpns: str,
                 dyn_no_pa: bool, dyn_with_pa: bool, use_lpn: bool):
        """
        Инициализация пакетного расчета ДУ
        
        Args:
            progress_callback: Функция обратного вызова для обновления прогресса
            rgms: Список расчетных режимов
            scns: Список аварийных процессов
            vrns: Список вариантов (ремонтных схем)
            rems_path: Путь к файлу ремонтных схем
            kprs: Список контролируемых величин для графиков
            sechen_path: Путь к файлу сечений
            lapnu_path: Путь к файлу ПА
            save_grf: Сохранять графики
            lpns: Строка с номерами LPN
            dyn_no_pa: Расчет без ПА
            dyn_with_pa: Расчет с ПА
            use_lpn: Использовать формат LPN
        """
        if not rgms or not scns or (use_lpn and not sechen_path) or (save_grf and not kprs) or (dyn_with_pa and not lapnu_path):
            error_msg = "Не заданы все исходные данные для выполнения пакетного расчета динамической устойчивости!\n\n"
            error_msg += f"Результаты проверки:\n"
            error_msg += f"Загружено расчетных режимов - {len(rgms)}\n"
            error_msg += f"Загружено аварийных процесслов - {len(scns)}\n"
            if use_lpn and not sechen_path:
                error_msg += "Используется файл ПА в формате lpn, но не загружен файл сечений!\n"
            if lapnu_path is None and dyn_with_pa:
                error_msg += "Включен расчет МДП с учетом ПА, но файл ПА отсутствует!\n"
            if save_grf and not kprs:
                error_msg += "Включена опция сохранения графиков, но отсутствует файл графического вывода!\n"
            raise InitialDataException(error_msg)
        
        self._progress_callback = progress_callback
        self._rgms = rgms
        self._scns = scns
        self._vrns = [v for v in vrns if not v.deactive]
        self._rems_path = rems_path
        self._kprs = kprs
        self._sechen_path = sechen_path
        self._lapnu_path = lapnu_path
        self._save_grf = save_grf
        self._lpns = lpns
        self._dyn_no_pa = dyn_no_pa
        self._dyn_with_pa = dyn_with_pa
        self._use_lpn = use_lpn
        
        # Группировка графиков по номерам
        self._grf_groups = {}
        for kpr in kprs:
            if kpr.num not in self._grf_groups:
                self._grf_groups[kpr.num] = []
            self._grf_groups[kpr.num].append(kpr)
        
        # Создание папки для результатов
        from utils.config import config
        results_dir = config.get_path("paths.results_dir")
        self._root = results_dir / f"{datetime.now():%Y-%m-%d %H-%M-%S} Пакетный расчет ДУ"
        self._root.mkdir(parents=True, exist_ok=True)
    
    @property
    def root(self) -> str:
        """Путь к папке с результатами"""
        return str(self._root)
    
    @property
    def max(self) -> int:
        """Максимальное количество шагов расчета"""
        num_modes = (1 if self._dyn_no_pa else 0) + (1 if self._dyn_with_pa else 0)
        return len(self._rgms) * len(self._vrns) * len(self._scns) * num_modes + 1
    
    def calc(self) -> List[DynResults]:
        """Выполнение расчета"""
        progress = 0
        results = []
        
        for rgm_idx, rgm in enumerate(self._rgms):
            dyn_shems_list = []
            
            for vrn in self._vrns:
                dyn_shem = DynShems(sheme_name=vrn.name, is_stable=False, events=[])
                events_list = []
                
                for scn_idx, scn in enumerate(self._scns):
                    rastr = RastrOperations()
                    rastr.load(rgm.name)
                    rastr.dyn_settings()
                    
                    # Применение варианта
                    if vrn.id == -1:
                        is_stable = rastr.rgm()
                    else:
                        is_stable = rastr.apply_variant(vrn.num, self._rems_path)
                    
                    dyn_shem.is_stable = is_stable
                    
                    if not is_stable:
                        break
                    
                    no_pa_result = DynamicResult()
                    with_pa_result = DynamicResult()
                    no_pa_pic = []
                    with_pa_pic = []
                    
                    # Расчет без ПА
                    if self._dyn_no_pa:
                        rastr.load(scn.name)
                        rastr.load_template(".dfw")
                        
                        if self._save_grf:
                            no_pa_result = rastr.run_dynamic(ems=False)
                            # Сохранение графиков
                            for grf_num, kprs_group in self._grf_groups.items():
                                pic_path = self._root / f"Рисунок - {rgm_idx + 1}.{vrn.num + 1}.{scn_idx + 1}.{grf_num}(без ПА).png"
                                self._save_picture(rastr, kprs_group, str(pic_path))
                                no_pa_pic.append(str(pic_path))
                        else:
                            no_pa_result = rastr.run_dynamic(ems=True)
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                    
                    # Расчет с ПА
                    if self._dyn_with_pa:
                        if self._use_lpn:
                            rastr.load(self._sechen_path)
                            rastr.create_scn_from_lpn(self._lapnu_path, self._lpns, scn.name)
                        else:
                            rastr.load(scn.name)
                            rastr.load(self._lapnu_path)
                        
                        if self._save_grf:
                            with_pa_result = rastr.run_dynamic(ems=False)
                            # Сохранение графиков
                            for grf_num, kprs_group in self._grf_groups.items():
                                pic_path = self._root / f"Рисунок - {rgm_idx + 1}.{vrn.num + 1}.{scn_idx + 1}.{grf_num}(с ПА).png"
                                self._save_picture(rastr, kprs_group, str(pic_path))
                                with_pa_pic.append(str(pic_path))
                        else:
                            with_pa_result = rastr.run_dynamic(ems=True)
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                    
                    events_list.append(Events(
                        name=Path(scn.name).stem,
                        no_pa_result=no_pa_result,
                        with_pa_result=with_pa_result,
                        no_pa_pic=no_pa_pic,
                        with_pa_pic=with_pa_pic
                    ))
                
                dyn_shem.events = events_list
                dyn_shems_list.append(dyn_shem)
            
            results.append(DynResults(
                rg_name=Path(rgm.name).stem,
                dyn_shems=dyn_shems_list
            ))
        
        return results
    
    def _save_picture(self, rastr: RastrOperations, kprs: List[KprInfo], file_path: str):
        """Сохранение графика (интерактивный Plotly или статический matplotlib)"""
        try:
            # Пытаемся использовать Plotly для интерактивных графиков
            try:
                from visualization.plotly_visualizer import plotly_visualizer
                
                if plotly_visualizer:
                    # Подготовка данных для Plotly
                    data_series = []
                    for kpr in kprs:
                        points = rastr.get_points_from_exit_file(kpr.table, kpr.col, kpr.selection)
                        if points:
                            x_vals = [p.x for p in points]
                            y_vals = [p.y for p in points]
                            data_series.append({
                                'name': kpr.name,
                                'x': x_vals,
                                'y': y_vals,
                                'line_width': 2
                            })
                    
                    if data_series:
                        # Сохраняем как интерактивный HTML
                        html_path = Path(file_path).with_suffix('.html')
                        result = plotly_visualizer.create_time_series_plot(
                            data_series=data_series,
                            title="Динамическая устойчивость",
                            x_label="Время, с",
                            y_label="Значение",
                            output_path=html_path,
                            interactive=True
                        )
                        
                        # Также сохраняем статическое изображение для совместимости
                        try:
                            static_path = Path(file_path)
                            if static_path.suffix != '.png':
                                static_path = static_path.with_suffix('.png')
                            plotly_visualizer.save_static_image(
                                html_path,
                                static_path,
                                format='png',
                                width=1200,
                                height=800
                            )
                        except Exception as e:
                            # Если не удалось сохранить статическое изображение,
                            # используем matplotlib как fallback
                            self._save_picture_matplotlib(rastr, kprs, file_path)
                        
                        return
            except ImportError:
                # Plotly не доступен, используем matplotlib
                pass
            except Exception as e:
                # Ошибка при использовании Plotly, fallback на matplotlib
                from utils.logger import logger
                logger.warning(f"Не удалось использовать Plotly: {e}, используется matplotlib")
            
            # Fallback на matplotlib
            self._save_picture_matplotlib(rastr, kprs, file_path)
        
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Ошибка при сохранении графика {file_path}: {e}")
    
    def _save_picture_matplotlib(self, rastr: RastrOperations, kprs: List[KprInfo], file_path: str):
        """Сохранение графика через matplotlib (fallback)"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Для сохранения без GUI
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            for kpr in kprs:
                points = rastr.get_points_from_exit_file(kpr.table, kpr.col, kpr.selection)
                if points:
                    x_vals = [p.x for p in points]
                    y_vals = [p.y for p in points]
                    ax.plot(x_vals, y_vals, linewidth=2, label=kpr.name)
            
            ax.set_xlabel("Время, с", fontsize=18)
            ax.grid(True, linestyle='-', linewidth=0.5)
            ax.legend(loc='lower right', frameon=True, framealpha=1.0, facecolor='white', edgecolor='black')
            
            plt.tight_layout()
            plt.savefig(file_path, dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Ошибка при сохранении графика через matplotlib: {e}")

