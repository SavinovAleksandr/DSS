"""
Главный класс управления данными и расчетами
"""

import csv
import locale
import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional, Callable

from models import (
    RgmsInfo, ScnsInfo, VrnInfo, KprInfo, SchInfo, ShuntKZ,
    FileInfo, ShuntResults, CrtTimeResults, DynResults, MdpResults, UostResults
)
from calculations import (
    ShuntKZCalc, MaxKZTimeCalc, DynStabilityCalc, MdpStabilityCalc, UostStabilityCalc
)
from excel_operations import ExcelOperations
from utils.exceptions import UncorrectFileException, RastrUnavailableException
from utils.config import config
from utils.file_type_detector import FileTypeDetector
from utils.logger import logger

# Условный импорт RastrOperations для кроссплатформенности
try:
    from rastr_operations import RastrOperations, RASTR_AVAILABLE
except ImportError:
    RastrOperations = None
    RASTR_AVAILABLE = False


class DataInfo:
    """Главный класс для управления данными и расчетами"""
    
    def __init__(self):
        """Инициализация DataInfo"""
        self.is_active = False
        
        # Коллекции данных
        self.rgms_info: List[RgmsInfo] = []
        self.scns_info: List[ScnsInfo] = []
        self.vrn_inf: List[VrnInfo] = [
            VrnInfo(id=-1, name="Нормальная схема", num=0, deactive=False)
        ]
        
        # Файлы
        self.sechen = FileInfo()
        self.vir = FileInfo()
        self.grf = FileInfo()
        self.rems = FileInfo()
        self.lapnu = FileInfo()
        self.shunt_kz = FileInfo()
        
        # Данные
        self.sch_inf: List[SchInfo] = []
        self.kpr_inf: List[KprInfo] = []
        self.shunt_kz_inf: List[ShuntKZ] = []
        
        # Настройки (из конфигурации)
        self.use_type_val_u = config.get("settings.use_type_val_u", True)
        self.use_sel_nodes = config.get("settings.use_sel_nodes", True)
        self.calc_one_phase = config.get("settings.calc_one_phase", True)
        self.calc_two_phase = config.get("settings.calc_two_phase", True)
        self.base_angle = config.get("calculations.base_angle", 1.471)
        self.crt_time_precision = config.get("calculations.crt_time_precision", 0.02)
        self.crt_time_max = config.get("calculations.crt_time_max", 1.0)
        self.selected_sch = config.get("calculations.default_selected_sch", 0)
        self.dyn_no_pa = config.get("settings.dyn_no_pa", True)
        self.dyn_with_pa = config.get("settings.dyn_with_pa", False)
        self.save_grf = config.get("settings.save_grf", False)
        self.use_lpn = config.get("settings.use_lpn", False)
        self.lpns = config.get("settings.lpns", "")
        
        # Результаты
        self.shunt_results: List[ShuntResults] = []
        self.crt_time_results: List[CrtTimeResults] = []
        self.dyn_results: List[DynResults] = []
        self.mdp_results: List[MdpResults] = []
        self.uost_results: List[UostResults] = []
        
        # Прогресс
        self.progress = 0
        self.max_progress = 1
        self.label = ""
        
        # Путь для результатов (из конфигурации)
        self.tmp_root = config.get_path("paths.results_dir")
        self.tmp_root.mkdir(parents=True, exist_ok=True)
    
    def add_files(self, file_paths: List[str]):
        """Добавление файлов в проект"""
        for file_path in file_paths:
            try:
                file_type = FileTypeDetector.detect(file_path)
                
                if file_type == 'rems':
                    self._handle_rems_file(file_path)
                elif file_type == 'scenario':
                    self._handle_scenario_file(file_path)
                elif file_type == 'vir':
                    self._handle_vir_file(file_path)
                elif file_type == 'sechen':
                    self._handle_sechen_file(file_path)
                elif file_type == 'rems_vrn':
                    self._handle_rems_vrn_file(file_path)
                elif file_type == 'grf':
                    self._handle_grf_file(file_path)
                elif file_type == 'shunt_kz':
                    self._handle_shunt_kz_file(file_path)
                elif file_type == 'lapnu':
                    self._handle_lapnu_file(file_path)
                else:
                    raise UncorrectFileException(f"Неподдерживаемый тип файла: {Path(file_path).suffix}")
            
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")
                raise
    
    def _handle_rems_file(self, file_path: str):
        """Обработка файла расчетного режима"""
        if not any(rgm.name == file_path for rgm in self.rgms_info):
            self.rgms_info.append(RgmsInfo(name=file_path))
    
    def _handle_scenario_file(self, file_path: str):
        """Обработка файла аварийного процесса"""
        if not any(scn.name == file_path for scn in self.scns_info):
            self.scns_info.append(ScnsInfo(name=file_path))
    
    def _handle_vir_file(self, file_path: str):
        """Обработка файла траектории утяжеления"""
        self.vir.name = file_path
    
    def _handle_sechen_file(self, file_path: str):
        """Обработка файла сечений"""
        self.sechen.name = file_path
        self.sch_inf.clear()
        
        if not RASTR_AVAILABLE or RastrOperations is None:
            raise RastrUnavailableException(
                "RASTR недоступен на данной платформе. "
                "Для работы с файлами сечений требуется Windows с установленным RASTR."
            )
        
        rastr = RastrOperations()
        rastr.load(file_path)
        sections = rastr.selection("sechen")
        
        if not sections:
            logger.warning(f"В файле сечений {file_path} не найдено ни одного сечения")
            return
        
        for section_id in sections:
            try:
                # Безопасное получение значений с обработкой ошибок
                name = rastr.get_val("sechen", "name", section_id) or ""
                num = rastr.get_val("sechen", "ns", section_id) or 0
                control = rastr.get_val("sechen", "sta", section_id) or 0
                
                self.sch_inf.append(SchInfo(
                    id=section_id,
                    name=name,
                    num=num,
                    control=control
                ))
            except Exception as e:
                logger.error(f"Ошибка при чтении сечения с ID {section_id}: {e}")
                # Продолжаем обработку остальных сечений
                continue
    
    def _handle_rems_vrn_file(self, file_path: str):
        """Обработка файла ремонтных схем"""
        self.rems.name = file_path
        self.vrn_inf.clear()
        self.vrn_inf.append(VrnInfo(id=-1, name="Нормальная схема", num=0, deactive=False))
        
        if not RASTR_AVAILABLE or RastrOperations is None:
            raise RastrUnavailableException(
                "RASTR недоступен на данной платформе. "
                "Для работы с файлами ремонтных схем требуется Windows с установленным RASTR."
            )
        
        rastr = RastrOperations()
        rastr.load(file_path)
        variants = rastr.selection("var_mer")
        
        for variant_id in variants:
            self.vrn_inf.append(VrnInfo(
                id=variant_id,
                name=rastr.get_val("var_mer", "name", variant_id),
                num=rastr.get_val("var_mer", "Num", variant_id),
                deactive=rastr.get_val("var_mer", "sta", variant_id)
            ))
    
    def _handle_grf_file(self, file_path: str):
        """Обработка файла графического вывода"""
        self.grf.name = file_path
        self.kpr_inf.clear()
        
        if not RASTR_AVAILABLE or RastrOperations is None:
            raise RastrUnavailableException(
                "RASTR недоступен на данной платформе. "
                "Для работы с файлами графического вывода требуется Windows с установленным RASTR."
            )
        
        rastr = RastrOperations()
        rastr.load(file_path)
        ots_vals = rastr.selection("ots_val")
        
        for ots_id in ots_vals:
            self.kpr_inf.append(KprInfo(
                id=ots_id,
                num=rastr.get_val("ots_val", "Num", ots_id),
                name=rastr.get_val("ots_val", "name", ots_id),
                table=rastr.get_val("ots_val", "tabl", ots_id),
                selection=rastr.get_val("ots_val", "vibork", ots_id),
                col=rastr.get_val("ots_val", "formula", ots_id)
            ))
    
    def _handle_shunt_kz_file(self, file_path: str):
        """Обработка файла задания для шунтов КЗ"""
        self.shunt_kz.name = file_path
        self.use_sel_nodes = False
        self.shunt_kz_inf.clear()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            header = next(reader)
            
            if (len(header) != 7 or header[0] != "node" or header[1] != "r1" or
                header[2] != "x1" or header[3] != "u1" or header[4] != "r2" or
                header[5] != "x2" or header[6] != "u2"):
                raise UncorrectFileException("Некорректный файл для задания шунтов КЗ")
            
            decimal_sep = locale.localeconv()['decimal_point']
            alt_sep = "," if decimal_sep == "." else "."
            
            for row in reader:
                if len(row) >= 7:
                    self.shunt_kz_inf.append(ShuntKZ(
                        node=int(row[0]),
                        r1=float(row[1].replace(alt_sep, decimal_sep)) if row[1] and row[1] != "0" else -1.0,
                        x1=float(row[2].replace(alt_sep, decimal_sep)) if row[2] and row[2] != "0" else -1.0,
                        u1=float(row[3].replace(alt_sep, decimal_sep)) if row[3] and row[3] != "0" else -1.0,
                        r2=float(row[4].replace(alt_sep, decimal_sep)) if row[4] and row[4] != "0" else -1.0,
                        x2=float(row[5].replace(alt_sep, decimal_sep)) if row[5] and row[5] != "0" else -1.0,
                        u2=float(row[6].replace(alt_sep, decimal_sep)) if row[6] and row[6] != "0" else -1.0
                    ))
    
    def _handle_lapnu_file(self, file_path: str):
        """Обработка файла ПА"""
        self.dyn_with_pa = True
        self.lapnu.name = file_path
        ext = Path(file_path).suffix.lower()
        self.use_lpn = (ext == '.lpn')
        
        if self.use_lpn:
            if not RASTR_AVAILABLE or RastrOperations is None:
                raise RastrUnavailableException(
                    "RASTR недоступен на данной платформе. "
                    "Для работы с файлами ПА (.lpn) требуется Windows с установленным RASTR."
                )
            
            rastr = RastrOperations()
            rastr.load(file_path)
            lapnu_ids = rastr.selection("LAPNU", "sta = 0")
            self.lpns = "=" + ";".join(str(rastr.get_val("LAPNU", "Id", lap_id)) for lap_id in lapnu_ids)
    
    def delete_selected(self, selected_rgm: Optional[RgmsInfo] = None, 
                       selected_scn: Optional[ScnsInfo] = None):
        """Удаление выбранных элементов"""
        if selected_rgm and selected_rgm in self.rgms_info:
            self.rgms_info.remove(selected_rgm)
        if selected_scn and selected_scn in self.scns_info:
            self.scns_info.remove(selected_scn)
    
    def calc_shunt_kz(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Расчет шунтов КЗ"""
        if self.is_active:
            return
        
        self.is_active = True
        try:
            self._clear_all_results()
            
            calc = ShuntKZCalc(
                progress_callback,
                self.rgms_info, self.vrn_inf, self.rems.name,
                self.shunt_kz_inf, self.use_sel_nodes, self.use_type_val_u,
                self.calc_one_phase, self.calc_two_phase
            )
            
            self.max_progress = calc.max
            self.progress = 0
            
            self.shunt_results = calc.calc()
            self._save_results_to_excel(calc.root)
            self._open_results_folder(calc.root)
            return calc.root
        finally:
            self.is_active = False
            self.progress = 0
            self.label = ""
    
    def calc_max_kz_time(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Расчет предельного времени КЗ"""
        if self.is_active:
            return
        
        self.is_active = True
        try:
            self._clear_all_results()
            
            calc = MaxKZTimeCalc(
                progress_callback,
                self.rgms_info, self.scns_info, self.vrn_inf,
                self.rems.name, self.crt_time_precision, self.crt_time_max
            )
            
            self.max_progress = calc.max
            self.progress = 0
            
            self.crt_time_results = calc.calc()
            self._save_results_to_excel(calc.root)
            self._open_results_folder(calc.root)
            return calc.root
        finally:
            self.is_active = False
            self.progress = 0
            self.label = ""
    
    def calc_dyn_stability(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Пакетный расчет динамической устойчивости"""
        if self.is_active:
            return
        
        self.is_active = True
        try:
            self._clear_all_results()
            
            # ИСПРАВЛЕНО: Проверка наличия файлов перед передачей (как в C# конструкторе)
            rems_name = self.rems.name if self.rems.name else None
            sechen_name = self.sechen.name if self.sechen.name else None
            lapnu_name = self.lapnu.name if self.lapnu.name else None
            
            calc = DynStabilityCalc(
                progress_callback,
                self.rgms_info, self.scns_info, self.vrn_inf,
                rems_name, self.kpr_inf, sechen_name,
                lapnu_name, self.save_grf, self.lpns,
                self.dyn_no_pa, self.dyn_with_pa, self.use_lpn
            )
            
            self.max_progress = calc.max
            self.progress = 0
            
            self.dyn_results = calc.calc()
            self._save_results_to_excel(calc.root)
            self._open_results_folder(calc.root)
            return calc.root
        finally:
            self.is_active = False
            self.progress = 0
            self.label = ""
    
    def calc_mdp_stability(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Расчет МДП ДУ"""
        logger.info("=" * 80)
        logger.info("НАЧАЛО РАСЧЕТА МДП ДУ")
        logger.info("=" * 80)
        
        if self.is_active:
            logger.warning("Расчет уже выполняется, пропуск")
            return
        
        logger.info(f"is_active до установки: {self.is_active}")
        self.is_active = True
        logger.info(f"is_active после установки: {self.is_active}")
        
        try:
            logger.info("Очистка предыдущих результатов")
            self._clear_all_results()
            
            logger.info("Проверка исходных данных:")
            logger.info(f"  - Режимов (rgms): {len(self.rgms_info)}")
            logger.info(f"  - Сценариев (scns): {len(self.scns_info)}")
            logger.info(f"  - Вариантов (vrns): {len(self.vrn_inf)}")
            logger.info(f"  - Сечений (schs): {len(self.sch_inf)}")
            logger.info(f"  - Контролируемых величин (kprs): {len(self.kpr_inf)}")
            logger.info(f"  - REMS путь: {self.rems.name}")
            logger.info(f"  - VIR путь: {self.vir.name}")
            logger.info(f"  - Сечения путь: {self.sechen.name}")
            logger.info(f"  - ПА путь: {self.lapnu.name}")
            logger.info(f"  - Выбранное сечение: {self.selected_sch}")
            logger.info(f"  - Без ПА: {self.dyn_no_pa}")
            logger.info(f"  - С ПА: {self.dyn_with_pa}")
            logger.info(f"  - Использовать LPN: {self.use_lpn}")
            logger.info(f"  - LPNs: {self.lpns}")
            
            logger.info("Создание объекта MdpStabilityCalc")
            calc = MdpStabilityCalc(
                progress_callback,
                self.rgms_info, self.scns_info, self.vrn_inf,
                self.rems.name, self.vir.name, self.sechen.name,
                self.lapnu.name, self.sch_inf, self.kpr_inf,
                self.lpns, self.selected_sch, self.dyn_no_pa,
                self.dyn_with_pa, self.use_lpn
            )
            
            self.max_progress = calc.max
            self.progress = 0
            logger.info(f"Максимальное количество шагов: {self.max_progress}")
            logger.info(f"Корневая директория результатов: {calc.root}")
            
            logger.info("Запуск расчета calc.calc()")
            self.mdp_results = calc.calc()
            logger.info(f"Расчет завершен. Получено результатов: {len(self.mdp_results)}")
            
            logger.info("Сохранение результатов в Excel")
            self._save_results_to_excel(calc.root)
            logger.info(f"Результаты сохранены в: {calc.root}")
            
            # Открываем папку с результатами
            self._open_results_folder(calc.root)
            
            return calc.root
        except Exception as e:
            logger.exception(f"ОШИБКА В calc_mdp_stability: {type(e).__name__}: {e}")
            raise
        finally:
            logger.info("Сброс флагов в finally блоке")
            self.is_active = False
            self.progress = 0
            self.label = ""
            logger.info(f"is_active после сброса: {self.is_active}")
            logger.info("=" * 80)
            logger.info("КОНЕЦ РАСЧЕТА МДП ДУ")
            logger.info("=" * 80)
    
    def calc_uost_stability(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Расчет остаточного напряжения при КЗ"""
        if self.is_active:
            return
        
        self.is_active = True
        try:
            self._clear_all_results()
            
            calc = UostStabilityCalc(
                progress_callback,
                self.rgms_info, self.scns_info, self.vrn_inf,
                self.rems.name, self.kpr_inf
            )
            
            self.max_progress = calc.max
            self.progress = 0
            
            self.uost_results = calc.calc()
            self._save_results_to_excel(calc.root)
            self._open_results_folder(calc.root)
            return calc.root
        finally:
            self.is_active = False
            self.progress = 0
            self.label = ""
    
    def _open_results_folder(self, folder_path: str):
        """Открыть папку с результатами в проводнике/файловом менеджере"""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                logger.warning(f"Папка результатов не существует: {folder_path}")
                return
            
            if platform.system() == "Windows":
                os.startfile(str(folder))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(folder)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder)])
            
            logger.info(f"Открыта папка с результатами: {folder_path}")
        except Exception as e:
            logger.error(f"Не удалось открыть папку с результатами: {e}")
    
    def _clear_all_results(self):
        """Очистка всех результатов"""
        self.shunt_results.clear()
        self.crt_time_results.clear()
        self.dyn_results.clear()
        self.mdp_results.clear()
        self.uost_results.clear()
    
    def _save_results_to_excel(self, root: str):
        """Сохранение результатов в Excel"""
        root_path = Path(root)
        
        # Определение типа результатов
        result_type = 0
        if self.shunt_results:
            result_type = 1
        elif self.crt_time_results:
            result_type = 2
        elif self.dyn_results:
            result_type = 3
        elif self.mdp_results:
            result_type = 4
        elif self.uost_results:
            result_type = 5
        
        excel = ExcelOperations("Результаты расчетов")
        excel.font()
        
        # Заголовки
        excel.set_val(1, 1, "Наименование режима")
        excel.width(1, 40)
        excel.set_val(1, 2, "Схема сети")
        excel.width(2, 40)
        
        row = 2
        
        if result_type == 1:
            # Шунты КЗ
            excel.merge(1, 1, 2, 1, horizontal=True, vertical=True)
            excel.merge(1, 2, 2, 2, horizontal=True, vertical=True)
            excel.set_val(1, 3, "Номер узла")
            excel.merge(1, 3, 2, 3, horizontal=True, vertical=True)
            excel.width(3, 15)
            
            excel.set_val(1, 4, "Однофазное КЗ")
            excel.merge(1, 4, 1, 6, horizontal=True, vertical=True)
            excel.set_val(2, 4, "R, Ом")
            excel.width(4, 15)
            excel.set_val(2, 5, "X, Ом")
            excel.width(5, 15)
            excel.set_val(2, 6, "U1, кВ")
            excel.width(6, 15)
            
            excel.set_val(1, 7, "Двухфазное КЗ")
            excel.merge(1, 7, 1, 9, horizontal=True, vertical=True)
            excel.set_val(2, 7, "R, Ом")
            excel.width(7, 15)
            excel.set_val(2, 8, "X, Ом")
            excel.width(8, 15)
            excel.set_val(2, 9, "U1, кВ")
            excel.width(9, 15)
            
            excel.format(1, 1, 2, 9, horizontal='center', vertical='center')
            excel.borders(1, 1, 2, 9)
            
            row = 3
            for shunt_result in self.shunt_results:
                start_row = row
                for shem in shunt_result.shems:
                    shem_start_row = row
                    excel.set_val(row, 2, shem.sheme_name)
                    
                    if shem.is_stable:
                        for node in shem.nodes:
                            excel.set_val(row, 3, node.node)
                            excel.set_val(row, 4, f"{node.r1:.3f}")
                            excel.set_val(row, 5, f"{node.x1:.3f}")
                            excel.set_val(row, 6, f"{node.u1:.1f}")
                            excel.set_val(row, 7, f"{node.r2:.3f}")
                            excel.set_val(row, 8, f"{node.x2:.3f}")
                            excel.set_val(row, 9, f"{node.u2:.1f}")
                            excel.format(row, 3, row, 9, horizontal='center', vertical='center')
                            row += 1
                    else:
                        excel.set_val(row, 3, "Схема не балансируется")
                        excel.merge(row, 3, row, 9, horizontal=True, vertical=True)
                        row += 1
                    
                    excel.merge(shem_start_row, 2, row - 1, 2, horizontal=True, vertical=True)
                
                excel.set_val(start_row, 1, shunt_result.rg_name)
                excel.merge(start_row, 1, row - 1, 1, horizontal=True, vertical=True)
                excel.borders(start_row, 1, row - 1, 9)
            
            if not self.calc_one_phase:
                excel.hide_column(4)
                excel.hide_column(5)
                excel.hide_column(6)
            if not self.calc_two_phase:
                excel.hide_column(7)
                excel.hide_column(8)
                excel.hide_column(9)
        
        elif result_type == 2:
            # Предельное время КЗ
            excel.set_val(1, 3, "Расчетное КЗ")
            excel.width(3, 40)
            excel.set_val(1, 4, "Предельное время отключения, с")
            excel.width(4, 15)
            excel.format(1, 1, 1, 4, horizontal='center', vertical='center')
            excel.borders(1, 1, 1, 4)
            
            row = 2
            for crt_result in self.crt_time_results:
                start_row = row
                for crt_shem in crt_result.crt_shems:
                    shem_start_row = row
                    excel.set_val(row, 2, crt_shem.sheme_name)
                    
                    if crt_shem.is_stable:
                        for time in crt_shem.times:
                            excel.set_val(row, 3, time.scn_name)
                            if self.crt_time_max != time.crt_time:
                                excel.set_val(row, 4, f"{time.crt_time:.3f}")
                            else:
                                excel.set_val(row, 4, f">{time.crt_time}")
                            row += 1
                    else:
                        excel.set_val(row, 3, "Схема не балансируется")
                        excel.merge(row, 3, row, 4, horizontal=True, vertical=True)
                        row += 1
                    
                    excel.merge(shem_start_row, 2, row - 1, 2, horizontal=True, vertical=True)
                
                excel.set_val(start_row, 1, crt_result.rg_name)
                excel.merge(start_row, 1, row - 1, 1, horizontal=True, vertical=True)
                excel.format(start_row, 1, row - 1, 4, horizontal='center', vertical='center')
                excel.borders(start_row, 1, row - 1, 4)
        
        elif result_type == 3:
            # Пакетный расчет ДУ
            excel.merge(1, 1, 2, 1, horizontal=True, vertical=True)
            excel.merge(1, 2, 2, 2, horizontal=True, vertical=True)
            excel.set_val(1, 3, "Расчетный сценарий")
            excel.merge(1, 3, 2, 3, horizontal=True, vertical=True)
            excel.width(3, 15)
            
            excel.set_val(1, 4, "Без учета действия ПА")
            excel.merge(1, 4, 1, 6, horizontal=True, vertical=True)
            excel.set_val(2, 4, "Результат расчета ДУ")
            excel.width(4, 20)
            excel.set_val(2, 5, "Критерий нарушения ДУ")
            excel.width(5, 40)
            excel.set_val(2, 6, "Рисунок")
            excel.width(6, 20)
            
            excel.set_val(1, 7, "С учетом действия ПА")
            excel.merge(1, 7, 1, 9, horizontal=True, vertical=True)
            excel.set_val(2, 7, "Результат расчета ДУ")
            excel.width(7, 20)
            excel.set_val(2, 8, "Критерий нарушения ДУ")
            excel.width(8, 40)
            excel.set_val(2, 9, "Рисунок")
            excel.width(9, 20)
            
            excel.format(1, 1, 2, 9, horizontal='center', vertical='center')
            excel.borders(1, 1, 2, 9)
            
            row = 3
            for dyn_result in self.dyn_results:
                start_row = row
                for dyn_shem in dyn_result.dyn_shems:
                    shem_start_row = row
                    excel.set_val(row, 2, dyn_shem.sheme_name)
                    
                    if dyn_shem.is_stable:
                        for event in dyn_shem.events:
                            excel.set_val(row, 3, event.name)
                            
                            if event.no_pa_result.is_success:
                                excel.set_val(row, 4, "Устойчиво" if event.no_pa_result.is_stable else "Неустойчиво")
                                excel.set_val(row, 5, "-" if event.no_pa_result.is_stable else event.no_pa_result.result_message)
                                pic_names = "\n".join(Path(p).stem for p in event.no_pa_pic)
                                excel.set_val(row, 6, pic_names)
                            
                            if event.with_pa_result.is_success:
                                excel.set_val(row, 7, "Устойчиво" if event.with_pa_result.is_stable else "Неустойчиво")
                                excel.set_val(row, 8, "-" if event.with_pa_result.is_stable else event.with_pa_result.result_message)
                                pic_names = "\n".join(Path(p).stem for p in event.with_pa_pic)
                                excel.set_val(row, 9, pic_names)
                            
                            excel.format(row, 3, row, 9, horizontal='center', vertical='center')
                            row += 1
                    else:
                        excel.set_val(row, 3, "Схема не балансируется")
                        excel.merge(row, 3, row, 9, horizontal=True, vertical=True)
                        row += 1
                    
                    excel.merge(shem_start_row, 2, row - 1, 2, horizontal=True, vertical=True)
                
                excel.set_val(start_row, 1, dyn_result.rg_name)
                excel.merge(start_row, 1, row - 1, 1, horizontal=True, vertical=True)
                excel.borders(start_row, 1, row - 1, 9)
            
            if not self.save_grf:
                excel.hide_column(6)
                excel.hide_column(9)
            if not self.dyn_no_pa:
                excel.hide_column(4)
                excel.hide_column(5)
                excel.hide_column(6)
            if not self.dyn_with_pa:
                excel.hide_column(7)
                excel.hide_column(8)
                excel.hide_column(9)
        
        elif result_type == 4:
            # МДП ДУ
            num_sch = len([s for s in self.sch_inf if s.control])
            num_kpr = len(self.kpr_inf)
            
            excel.merge(1, 1, 3, 1, horizontal=True, vertical=True)
            excel.merge(1, 2, 3, 2, horizontal=True, vertical=True)
            excel.set_val(1, 3, "Расчетный сценарий")
            excel.merge(1, 3, 3, 3, horizontal=True, vertical=True)
            excel.width(3, 15)
            
            excel.set_val(1, 4, "Без учета действия ПА")
            excel.set_val(2, 4, "МДП, МВт")
            excel.width(4, 15)
            excel.merge(2, 4, 3, 4, horizontal=True, vertical=True)
            
            # Столбцы "С учетом действия ПА" создаются только если включен расчет с ПА
            last_col_no_pa = 4 + num_sch + num_kpr
            if self.dyn_with_pa:
                excel.set_val(1, 5 + num_sch + num_kpr, "С учетом действия ПА")
                excel.set_val(2, 5 + num_sch + num_kpr, "МДП, МВт")
                excel.width(5 + num_sch + num_kpr, 15)
                excel.merge(2, 5 + num_sch + num_kpr, 3, 5 + num_sch + num_kpr, horizontal=True, vertical=True)
            
            # Заголовки для сечений и контролируемых величин
            if num_sch > 0:
                excel.set_val(2, 5, "Перетоки в КС, МВт")
                for idx, sch in enumerate([s for s in self.sch_inf if s.control]):
                    excel.set_val(3, 5 + idx, sch.name)
                    excel.width(5 + idx, 15)
                excel.merge(2, 5, 2, 5 + num_sch - 1, horizontal=True, vertical=True)
                
                # Столбцы для ПА создаются только если включен расчет с ПА
                if self.dyn_with_pa:
                    excel.set_val(2, 6 + num_sch + num_kpr, "Перетоки в КС, МВт")
                    for idx, sch in enumerate([s for s in self.sch_inf if s.control]):
                        excel.set_val(3, 6 + num_sch + num_kpr + idx, sch.name)
                        excel.width(6 + num_sch + num_kpr + idx, 15)
                    excel.merge(2, 6 + num_sch + num_kpr, 2, 6 + num_sch + num_kpr + num_sch - 1, horizontal=True, vertical=True)
            
            if num_kpr > 0:
                excel.set_val(2, 5 + num_sch, "Контролируемые величины")
                for idx, kpr in enumerate(self.kpr_inf):
                    excel.set_val(3, 5 + num_sch + idx, kpr.name)
                    excel.width(5 + num_sch + idx, 15)
                excel.merge(2, 5 + num_sch, 2, 5 + num_sch + num_kpr - 1, horizontal=True, vertical=True)
                
                # Столбцы для ПА создаются только если включен расчет с ПА
                if self.dyn_with_pa:
                    excel.set_val(2, 6 + 2 * num_sch + num_kpr, "Контролируемые величины")
                    for idx, kpr in enumerate(self.kpr_inf):
                        excel.set_val(3, 6 + 2 * num_sch + num_kpr + idx, kpr.name)
                        excel.width(6 + 2 * num_sch + num_kpr + idx, 15)
                    excel.merge(2, 6 + 2 * num_sch + num_kpr, 2, 6 + 2 * num_sch + num_kpr + num_kpr - 1, horizontal=True, vertical=True)
            
            # Объединение заголовков
            if num_sch > 0 or num_kpr > 0:
                excel.merge(1, 4, 1, last_col_no_pa, horizontal=True, vertical=True)
                if self.dyn_with_pa:
                    last_col_with_pa = 5 + 2 * num_sch + 2 * num_kpr
                    excel.merge(1, 5 + num_sch + num_kpr, 1, last_col_with_pa, horizontal=True, vertical=True)
                    last_col = last_col_with_pa
                else:
                    last_col = last_col_no_pa
            else:
                last_col = 4
            
            excel.format(1, 1, 3, last_col, horizontal='center', vertical='center')
            excel.borders(1, 1, 3, last_col)
            
            row = 4
            for mdp_result in self.mdp_results:
                start_row = row
                for mdp_shem in mdp_result.mdp_shems:
                    shem_start_row = row
                    excel.set_val(row, 2, mdp_shem.sheme_name)
                    
                    if mdp_shem.is_stable:
                        for mdp_event in mdp_shem.events:
                            excel.set_val(row, 3, mdp_event.name)
                            excel.set_val(row, 4, f"{mdp_event.no_pa_mdp:.0f}")
                            
                            # Заполнение данных для ПА только если включен расчет с ПА
                            if self.dyn_with_pa:
                                excel.set_val(row, 5 + num_sch + num_kpr, f"{mdp_event.with_pa_mdp:.0f}")
                            
                            if num_sch > 0:
                                for idx in range(num_sch):
                                    if idx < len(mdp_event.no_pa_sechen):
                                        excel.set_val(row, 5 + idx, f"{mdp_event.no_pa_sechen[idx].value:.0f}")
                                    if self.dyn_with_pa and idx < len(mdp_event.with_pa_sechen):
                                        excel.set_val(row, 6 + num_sch + num_kpr + idx, f"{mdp_event.with_pa_sechen[idx].value:.0f}")
                            
                            if num_kpr > 0:
                                for idx in range(num_kpr):
                                    if idx < len(mdp_event.no_pa_kpr):
                                        excel.set_val(row, 5 + num_sch + idx, f"{mdp_event.no_pa_kpr[idx].value:.2f}")
                                    if self.dyn_with_pa and idx < len(mdp_event.with_pa_kpr):
                                        excel.set_val(row, 6 + 2 * num_sch + num_kpr + idx, f"{mdp_event.with_pa_kpr[idx].value:.2f}")
                            
                            # Определяем последний столбец для форматирования
                            if self.dyn_with_pa:
                                last_data_col = 5 + 2 * num_sch + 2 * num_kpr
                            else:
                                last_data_col = 4 + num_sch + num_kpr
                            
                            excel.format(row, 3, row, last_data_col, horizontal='center', vertical='center')
                            row += 1
                    else:
                        # Определяем последний столбец для объединения
                        if self.dyn_with_pa:
                            last_data_col = 5 + 2 * num_sch + 2 * num_kpr
                        else:
                            last_data_col = 4 + num_sch + num_kpr
                        excel.set_val(row, 3, "Схема не балансируется")
                        excel.merge(row, 3, row, last_data_col, horizontal=True, vertical=True)
                        row += 1
                    
                    excel.merge(shem_start_row, 2, row - 1, 2, horizontal=True, vertical=True)
                
                excel.set_val(start_row, 1, mdp_result.rg_name)
                excel.merge(start_row, 1, row - 1, 1, horizontal=True, vertical=True)
                
                # Определяем последний столбец для границ
                if self.dyn_with_pa:
                    last_data_col = 5 + 2 * num_sch + 2 * num_kpr
                else:
                    last_data_col = 4 + num_sch + num_kpr
                excel.borders(start_row, 1, row - 1, last_data_col)
            
            # Скрытие столбцов больше не нужно, так как они не создаются
            if not self.dyn_no_pa:
                for col in range(4, 5 + num_sch + num_kpr):
                    excel.hide_column(col)
        
        elif result_type == 5:
            # Остаточное напряжение при КЗ
            num_kpr = len(self.kpr_inf)
            
            excel.merge(1, 1, 2, 1, horizontal=True, vertical=True)
            excel.merge(1, 2, 2, 2, horizontal=True, vertical=True)
            excel.set_val(1, 3, "Расчетный сценарий")
            excel.width(3, 15)
            excel.merge(1, 3, 2, 3, horizontal=True, vertical=True)
            
            excel.set_val(1, 4, "ЛЭП")
            excel.set_val(2, 4, "Узел начала")
            excel.width(4, 15)
            excel.set_val(2, 5, "Узел конца")
            excel.width(5, 15)
            excel.set_val(2, 6, "Np")
            excel.width(6, 7)
            excel.merge(1, 4, 1, 6, horizontal=True, vertical=True)
            
            excel.set_val(1, 7, "Область устойчивости, %")
            excel.width(7, 15)
            excel.merge(1, 7, 2, 7, horizontal=True, vertical=True)
            
            excel.set_val(1, 8, "Остаточное напряжение в узлах ЛЭП, кВ")
            excel.set_val(2, 8, "Узел начала")
            excel.width(8, 15)
            excel.set_val(2, 9, "Узел конца")
            excel.width(9, 15)
            excel.merge(1, 8, 1, 9, horizontal=True, vertical=True)
            
            excel.set_val(1, 10, "Шунт КЗ, Ом")
            excel.merge(1, 10, 1, 11, horizontal=True, vertical=True)
            excel.set_val(2, 10, "Узел начала")
            excel.width(10, 15)
            excel.set_val(2, 11, "Узел конца")
            excel.width(11, 15)
            
            if num_kpr > 0:
                excel.set_val(1, 12, "Контролируемые величины")
                for idx, kpr in enumerate(self.kpr_inf):
                    excel.set_val(2, 12 + idx, kpr.name)
                excel.merge(1, 12, 1, 12 + num_kpr - 1, horizontal=True, vertical=True)
            
            excel.format(1, 1, 2, 11 + num_kpr, horizontal='center', vertical='center')
            excel.borders(1, 1, 2, 11 + num_kpr)
            
            row = 3
            for uost_result in self.uost_results:
                start_row = row
                for uost_shem in uost_result.uost_shems:
                    shem_start_row = row
                    excel.set_val(row, 2, uost_shem.sheme_name)
                    
                    if uost_shem.is_stable:
                        for uost_event in uost_shem.events:
                            excel.set_val(row, 3, uost_event.name)
                            excel.set_val(row, 4, uost_event.begin_node)
                            excel.set_val(row, 5, uost_event.end_node)
                            excel.set_val(row, 6, uost_event.np)
                            
                            if uost_event.distance == -1.0:
                                excel.set_val(row, 7, ">100")
                            elif uost_event.distance == 100.0:
                                excel.set_val(row, 7, "<0")
                            else:
                                # ИСПРАВЛЕНО: distance уже в процентах (0.1-99.9), не нужно умножать на 100
                                excel.set_val(row, 7, f"{uost_event.distance:.2f}")
                            
                            excel.set_val(row, 8, f"{uost_event.begin_uost:.2f}")
                            excel.set_val(row, 9, f"{uost_event.end_uost:.2f}")
                            
                            # ДОБАВЛЕНО: Значения шунта КЗ для узлов начала и конца
                            if uost_event.begin_shunt >= 0:
                                excel.set_val(row, 10, f"{uost_event.begin_shunt:.4f}")
                            else:
                                excel.set_val(row, 10, "-")
                            
                            if uost_event.end_shunt >= 0:
                                excel.set_val(row, 11, f"{uost_event.end_shunt:.4f}")
                            else:
                                excel.set_val(row, 11, "-")
                            
                            if num_kpr > 0:
                                for idx, value in enumerate(uost_event.values):
                                    excel.set_val(row, 12 + idx, value.value)
                            
                            excel.format(row, 3, row, 11 + num_kpr, horizontal='center', vertical='center')
                            row += 1
                    else:
                        excel.set_val(row, 3, "Схема не балансируется")
                        excel.merge(row, 3, row, 11 + num_kpr, horizontal=True, vertical=True)
                        row += 1
                    
                    excel.merge(shem_start_row, 2, row - 1, 2, horizontal=True, vertical=True)
                
                excel.set_val(start_row, 1, uost_result.rg_name)
                excel.merge(start_row, 1, row - 1, 1, horizontal=True, vertical=True)
                excel.borders(start_row, 1, row - 1, 11 + num_kpr)
        
        # Сохранение файла
        excel_file = root_path / "Результат расчетов.xlsx"
        # Автоматическое выравнивание столбцов по содержимому
        excel.auto_fit_columns()
        excel.save(str(excel_file))
        
        # Удаление временных файлов
        for tmp_file in root_path.glob("*.rst"):
            tmp_file.unlink()
        for tmp_file in root_path.glob("*.scn"):
            tmp_file.unlink()

