"""
Операции с RASTR через COM-интерфейс
"""

import os
import math
import locale
from pathlib import Path
from typing import List, Optional, Union, Any
from .dynamic_result import DynamicResult
from .point import Point
from .shunt_kz_result import ShuntKZResult

try:
    import win32com.client
    RASTR_AVAILABLE = True
except ImportError:
    RASTR_AVAILABLE = False
    win32com = None


class RastrOperations:
    """Класс для работы с RASTR через COM-интерфейс"""
    
    # GUID для RASTR COM объекта
    RASTR_CLSID = "{EFC5E4AD-A3DD-11D3-B73F-00500454CF3F}"
    
    def __init__(self):
        if not RASTR_AVAILABLE:
            raise ImportError("pywin32 не установлен. RASTR операции недоступны на этой платформе.")
        
        try:
            self._rastr = win32com.client.Dispatch(self.RASTR_CLSID)
        except Exception as e:
            raise RuntimeError(f"Не удалось подключиться к RASTR: {str(e)}")
    
    def __del__(self):
        """Очистка ресурсов"""
        self._rastr = None
    
    @staticmethod
    def find_template_path_with_extension(extension: str) -> Optional[str]:
        """Поиск шаблона по расширению"""
        from utils.config import config
        
        from utils.logger import logger
        
        # Получаем путь к директории шаблонов из конфигурации
        template_dir = config.get_path("paths.rastr_template_dir")
        
        if not template_dir.exists():
            logger.warning(f"Директория шаблонов не найдена: {template_dir}")
            # Пробуем стандартные пути (в разных версиях RASTR может быть разное расположение)
            possible_paths = [
                Path.home() / "Documents" / "RastrWin3" / "SHABLON",  # Современные версии RASTR
                Path.home() / "RastrWIN3" / "SHABLON",  # Старые версии
                Path.home() / "RastrWin3" / "SHABLON",  # Альтернативный вариант
            ]
            
            for possible_path in possible_paths:
                if possible_path.exists():
                    logger.info(f"Найдена директория шаблонов: {possible_path}")
                    template_dir = possible_path
                    break
            else:
                logger.warning(f"Директория шаблонов не найдена ни в одном из стандартных мест")
                return None
        
        # Ищем шаблон с нужным расширением
        for file in template_dir.glob(f"*{extension}"):
            if file.stem != "базовый режим мт":
                logger.debug(f"Найден шаблон: {file}")
                return str(file)
        
        logger.warning(f"Шаблон для расширения {extension} не найден в {template_dir}")
        return None
    
    def load(self, file: str):
        """Загрузка файла в RASTR"""
        from utils.config import config
        from utils.logger import logger
        
        file_path = Path(file)
        extension = file_path.suffix
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file}")
        
        shabl = self.find_template_path_with_extension(extension)
        if shabl:
            self._rastr.NewFile(shabl)
            # RG_REPL = 0 (замена)
            self._rastr.Load(0, str(file_path), shabl)
        else:
            # Более подробное сообщение об ошибке
            template_dir = config.get_path("paths.rastr_template_dir")
            error_msg = (
                f"Шаблон для расширения {extension} не найден.\n\n"
                f"Проверьте:\n"
                f"1. Существует ли директория шаблонов: {template_dir}\n"
                f"2. Есть ли в ней файл с расширением {extension}\n"
                f"3. Правильно ли настроен путь в конфигурации (paths.rastr_template_dir)"
            )
            raise FileNotFoundError(error_msg)
    
    def load_template(self, extension: str):
        """Загрузка шаблона"""
        shabl = self.find_template_path_with_extension(extension)
        if shabl:
            self._rastr.NewFile(shabl)
        else:
            raise FileNotFoundError(f"Шаблон для расширения {extension} не найден")
    
    def save(self, file: str):
        """Сохранение файла"""
        shabl = self.find_template_path_with_extension(Path(file).suffix)
        if shabl:
            self._rastr.Save(file, shabl)
        else:
            raise FileNotFoundError(f"Шаблон для расширения {Path(file).suffix} не найден")
    
    def add(self, file: str):
        """Добавление файла (RG_ADD = 1)"""
        shabl = self.find_template_path_with_extension(Path(file).suffix)
        if shabl:
            self._rastr.Load(1, file, shabl)
        else:
            raise FileNotFoundError(f"Шаблон для расширения {Path(file).suffix} не найден")
    
    def rgm(self, param: str = "", iterations: Optional[int] = None, voltage: Optional[float] = None) -> bool:
        """Расчет установившегося режима"""
        table = self._rastr.Tables.Item("com_regim")
        col_it_max = table.Cols.Item("it_max")
        col_dv_min = table.Cols.Item("dv_min")
        
        if iterations is not None:
            col_it_max.set_Z(0, iterations)
        if voltage is not None:
            col_dv_min.set_Z(0, voltage)
        
        # AST_OK = 0
        return self._rastr.rgm(param) == 0
    
    def add_table_row(self, table_name: str) -> int:
        """Добавление строки в таблицу"""
        table = self._rastr.Tables.Item(table_name)
        table.AddRow()
        return table.Size - 1
    
    def set_line_for_uost_calc(self, id1: int, id2: int, r: float, x: float, l: float):
        """Установка параметров линии для расчета остаточного напряжения"""
        table = self._rastr.Tables.Item("vetv")
        col_r = table.Cols.Item("r")
        col_x = table.Cols.Item("x")
        
        r_part = l * r / 100.0
        x_part = l * x / 100.0
        
        col_r.set_Z(id1, r_part)
        col_r.set_Z(id2, r - r_part)
        col_x.set_Z(id1, x_part)
        col_x.set_Z(id2, x - x_part)
        
        self.rgm()
    
    def change_rx_for_uost_calc(self, x_id: int, x: float, r_id: int = 0, r: float = -1.0):
        """Изменение R/X для расчета остаточного напряжения"""
        table = self._rastr.Tables.Item("DFWAutoActionScn")
        col_formula = table.Cols.Item("Formula")
        
        col_formula.set_Z(x_id, str(x).replace(",", "."))
        if r != -1.0:
            col_formula.set_Z(r_id, str(r).replace(",", "."))
    
    def selection(self, table_name: str, selection: str = "") -> List[int]:
        """Выборка строк по условию"""
        table = self._rastr.Tables.Item(table_name)
        table.SetSel(selection)
        
        result = []
        idx = table.FindNextSel(-1)
        while idx != -1:
            result.append(idx)
            idx = table.FindNextSel(idx)
        
        return result
    
    def apply_variant(self, num: int, file: str) -> bool:
        """Применение варианта из файла"""
        self.load(file)
        self._rastr.ApplyVariant(num)
        return self.rgm()
    
    def get_val(self, table_name: str, col_name: str, selection_or_index: Union[str, int]) -> Any:
        """Получение значения из таблицы"""
        table = self._rastr.Tables.Item(table_name)
        col = table.Cols.Item(col_name)
        
        if isinstance(selection_or_index, str):
            table.SetSel(selection_or_index)
            idx = table.FindNextSel(-1)
            if idx != -1:
                return col.get_Z(idx)
            return None
        else:
            return col.get_Z(selection_or_index)
    
    def set_val(self, table_name: str, col_name: str, index: int, value: Any) -> bool:
        """Установка значения в таблицу"""
        table = self._rastr.Tables.Item(table_name)
        col = table.Cols.Item(col_name)
        col.set_Z(index, value)
        return True
    
    def set_val_by_selection(self, table_name: str, col_name: str, selection: str, value: Any) -> bool:
        """Установка значения по условию выборки"""
        table = self._rastr.Tables.Item(table_name)
        col = table.Cols.Item(col_name)
        table.SetSel(selection)
        idx = table.FindNextSel(-1)
        
        if idx != -1:
            col.set_Z(idx, value)
            return True
        return False
    
    def create_scn_from_lpn(self, lpn_file: str, lpn: str, scn_file: str, save_file: str = ""):
        """Создание сценария из LPN файла"""
        self.load_template(".vrn")
        self.load(lpn_file)
        
        table = self._rastr.Tables.Item("var_mer")
        col_num = table.Cols.Item("Num")
        col_type = table.Cols.Item("Type")
        
        table.AddRow()
        col_num.set_Z(0, 1)
        col_type.set_Z(0, 1)
        
        self._rastr.LAPNUSMZU("1" + lpn)
        self.add(scn_file)
        
        if save_file:
            self.save(save_file)
    
    def run_ut(self) -> float:
        """Запуск утяжеления и получение суммы коэффициентов"""
        table_vetv = self._rastr.Tables.Item("vetv")
        table_ut = self._rastr.Tables.Item("ut_common")
        col_sum_kfc = table_ut.Cols.Item("sum_kfc")
        
        # step_ut("i") - инициализация
        # step_ut("z") - шаг утяжеления
        # AST_OK = 0
        while self._rastr.step_ut("i") == 0:
            pass
        
        while self._rastr.step_ut("z") == 0:
            pass
        
        return col_sum_kfc.get_Z(0)
    
    def step(self, step_value: float = 1.0, init: bool = True) -> float:
        """Выполнение шага утяжеления"""
        table_ut = self._rastr.Tables.Item("ut_common")
        col_sum_kfc = table_ut.Cols.Item("sum_kfc")
        col_kfc = table_ut.Cols.Item("kfc")
        
        if init:
            self._rastr.step_ut("i")
        
        col_kfc.set_Z(0, step_value)
        self._rastr.step_ut("z")
        
        return col_sum_kfc.get_Z(0)
    
    def dyn_settings(self):
        """Настройка параметров динамики"""
        table = self._rastr.Tables.Item("com_dynamics")
        col_max_result_files = table.Cols.Item("MaxResultFiles")
        col_snap_auto_load = table.Cols.Item("SnapAutoLoad")
        col_snap_max_count = table.Cols.Item("SnapMaxCount")
        
        col_max_result_files.set_Z(0, 1)
        col_snap_auto_load.set_Z(0, 1)
        col_snap_max_count.set_Z(0, 1)
    
    def run_dynamic(self, ems: bool = False, max_time: float = -1.0) -> DynamicResult:
        """Запуск динамического расчета"""
        result = DynamicResult()
        
        table = self._rastr.Tables.Item("com_dynamics")
        col_tras = table.Cols.Item("Tras")
        original_time = col_tras.get_Z(0)
        
        self.load_template(".dfw")
        
        if ems and max_time != -1.0:
            col_tras.set_Z(0, max_time)
        
        fw_dynamic = self._rastr.FWDynamic()
        
        # SYNC_LOSS_NONE = 0
        if ems:
            ret_code = fw_dynamic.RunEMSmode()
        else:
            ret_code = fw_dynamic.Run()
        
        result.is_success = (ret_code == 0)
        result.is_stable = (fw_dynamic.SyncLossCause == 0)  # SYNC_LOSS_NONE
        result.result_message = fw_dynamic.ResultMessage if fw_dynamic.ResultMessage else " - "
        result.time_reached = fw_dynamic.TimeReached
        
        col_tras.set_Z(0, original_time)
        
        return result
    
    def find_crt_time(self, precision: float, max_time: float) -> float:
        """Поиск критического времени отключения КЗ"""
        crt_time = max_time
        self.load_template(".dfw")
        
        self._reset_crt_time(max_time)
        
        fw_dynamic = self._rastr.FWDynamic()
        ret_code = fw_dynamic.RunEMSmode()
        
        # SYNC_LOSS_NONE = 0
        if fw_dynamic.SyncLossCause != 0:
            time_max = max_time
            time_min = 0.0
            time_step = (time_max - time_min) * 0.5
            
            while abs(time_step) > precision or fw_dynamic.SyncLossCause != 0:
                crt_time += time_step * (1 if fw_dynamic.SyncLossCause == 0 else -1)
                self._reset_crt_time(crt_time)
                
                fw_dynamic = self._rastr.FWDynamic()
                ret_code = fw_dynamic.RunEMSmode()
                
                if fw_dynamic.SyncLossCause == 0:
                    time_min = crt_time
                else:
                    time_max = crt_time
                
                time_step = (time_max - time_min) * 0.5
        
        return crt_time
    
    def _reset_crt_time(self, dt: float):
        """Сброс времени КЗ для расчета критического времени"""
        time_start = 1.0
        items = self.selection("DFWAutoActionScn")
        
        for item in items:
            obj_class = self.get_val("DFWAutoActionScn", "ObjectClass", item)
            
            if obj_class == "node":
                self.set_val("DFWAutoActionScn", "TimeStart", item, time_start)
                self.set_val("DFWAutoActionScn", "DT", item, dt)
            elif obj_class == "vetv":
                self.set_val("DFWAutoActionScn", "TimeStart", item, time_start + dt)
                self.set_val("DFWAutoActionScn", "DT", item, 999)
        
        self.set_val("com_dynamics", "Tras", 0, time_start + dt + 3.0)
    
    def find_shunt_kz(self, node: int, u_ost: float, x_isx: float, r_isx: float = -1.0) -> ShuntKZResult:
        """Поиск шунта КЗ для заданного остаточного напряжения"""
        table = self._rastr.Tables.Item("com_dynamics")
        col_tras = table.Cols.Item("Tras")
        col_tras.set_Z(0, 1.1)
        
        self.load_template(".dfw")
        
        # Логирование результатов
        prot = []
        
        def on_log_handler(code, level, stage_id, table_name, table_index, description, form_name):
            if code == 0 and "Величина остаточного напряжения в узле" in description:
                prot.append(description)
        
        # Подключение обработчика событий (упрощенная версия)
        # В реальной реализации нужно использовать win32com события
        
        z_mod = math.sqrt((r_isx ** 2 if r_isx != -1.0 else 0) + x_isx ** 2)
        z_angle = (math.pi / 2.0) if r_isx == -1.0 else math.atan(x_isx / r_isx)
        
        if r_isx == -1.0:
            self._create_shunt_scn(node, z_mod * math.sin(z_angle))
        else:
            self._create_shunt_scn(node, z_mod * math.sin(z_angle), z_mod * math.cos(z_angle))
        
        fw_dynamic = self._rastr.FWDynamic()
        ret_code = fw_dynamic.Run()
        
        # Парсинг результата из протокола
        if prot:
            last_msg = prot[-1]
            # Извлечение напряжения из сообщения
            # Формат: "Величина остаточного напряжения в узле ... (Uкз=XXX кВ, ...)"
            try:
                u_kz_str = last_msg.split("Uкз=")[1].split(" кВ")[0].replace(".", locale.localeconv()['decimal_point'])
                u_current = float(u_kz_str)
            except:
                u_current = 0.0
        else:
            u_current = 0.0
        
        u_nom = self.get_val("node", "uhom", f"ny={node}")
        precision = min(2.0, 0.02 * u_nom)
        
        while abs(u_current - u_ost) > precision:
            z_mod = z_mod * u_ost / u_current if u_current > 0 else z_mod
            
            if r_isx == -1.0:
                self._create_shunt_scn(node, z_mod * math.sin(z_angle))
            else:
                self._create_shunt_scn(node, z_mod * math.sin(z_angle), z_mod * math.cos(z_angle))
            
            fw_dynamic = self._rastr.FWDynamic()
            ret_code = fw_dynamic.Run()
            
            prot.clear()
            if prot:
                last_msg = prot[-1]
                try:
                    u_kz_str = last_msg.split("Uкз=")[1].split(" кВ")[0].replace(".", locale.localeconv()['decimal_point'])
                    u_current = float(u_kz_str)
                except:
                    break
        
        return ShuntKZResult(
            r=(-1.0 if r_isx == -1.0 else z_mod * math.cos(z_angle)),
            x=z_mod * math.sin(z_angle),
            u=u_current
        )
    
    def _create_shunt_scn(self, node: int, x: float, r: float = -1.0):
        """Создание сценария с шунтом КЗ"""
        self.load_template(".scn")
        
        table = self._rastr.Tables.Item("DFWAutoActionScn")
        col_id = table.Cols.Item("Id")
        col_type = table.Cols.Item("Type")
        col_formula = table.Cols.Item("Formula")
        col_obj_class = table.Cols.Item("ObjectClass")
        col_obj_prop = table.Cols.Item("ObjectProp")
        col_obj_key = table.Cols.Item("ObjectKey")
        col_runs_count = table.Cols.Item("RunsCount")
        col_time_start = table.Cols.Item("TimeStart")
        col_dt = table.Cols.Item("DT")
        
        # Добавление строки для X
        table.AddRow()
        row_idx = table.Size - 1
        col_id.set_Z(row_idx, table.Size)
        col_type.set_Z(row_idx, 1)
        col_formula.set_Z(row_idx, str(x).replace(",", "."))
        col_obj_class.set_Z(row_idx, "node")
        col_obj_prop.set_Z(row_idx, "x")
        col_obj_key.set_Z(row_idx, node)
        col_runs_count.set_Z(row_idx, 1)
        col_time_start.set_Z(row_idx, 1)
        col_dt.set_Z(row_idx, 0.06)
        
        # Добавление строки для R (если задано)
        if r != -1.0:
            table.AddRow()
            row_idx = table.Size - 1
            col_id.set_Z(row_idx, table.Size)
            col_type.set_Z(row_idx, 1)
            col_formula.set_Z(row_idx, str(r).replace(",", "."))
            col_obj_class.set_Z(row_idx, "node")
            col_obj_prop.set_Z(row_idx, "r")
            col_obj_key.set_Z(row_idx, node)
            col_runs_count.set_Z(row_idx, 1)
            col_time_start.set_Z(row_idx, 1)
            col_dt.set_Z(row_idx, 0.06)
    
    def get_points_from_exit_file(self, table_name: str, col_name: str, selection: str) -> List[Point]:
        """Получение точек из выходного файла для построения графика"""
        table = self._rastr.Tables.Item(table_name)
        table.SetSel(selection)
        
        points = []
        idx = table.FindNextSel(-1)
        
        if idx < 0:
            return points
        
        # Получение цепочки снимков
        graph_data = self._rastr.GetChainedGraphSnapshot(table_name, col_name, idx, 0)
        
        # graph_data - двумерный массив [time, value]
        for i in range(len(graph_data)):
            if len(graph_data[i]) >= 2:
                points.append(Point(graph_data[i][1], graph_data[i][0]))  # X=time, Y=value
        
        return points

