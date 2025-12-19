"""
Расчет предельного времени отключения КЗ
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from models import (
    RgmsInfo, ScnsInfo, VrnInfo, CrtTimeResults, CrtShems, CrtTimes
)
from rastr_operations import RastrOperations
from utils.exceptions import InitialDataException


class MaxKZTimeCalc:
    """Расчет предельного времени отключения КЗ"""
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]],
                 rgms: List[RgmsInfo], scns: List[ScnsInfo], vrns: List[VrnInfo],
                 rems_path: Optional[str], time_precision: float, max_time: float):
        """
        Инициализация расчета предельного времени КЗ
        
        Args:
            progress_callback: Функция обратного вызова для обновления прогресса
            rgms: Список расчетных режимов
            scns: Список аварийных процессов
            vrns: Список вариантов (ремонтных схем)
            rems_path: Путь к файлу ремонтных схем
            time_precision: Точность расчета (секунды)
            max_time: Максимальное время отключения КЗ (секунды)
        """
        if not rgms or not scns or max_time == 0.0:
            error_msg = "Не заданы все исходные данные для определения предельного времени отключения КЗ!\n\n"
            error_msg += f"Результаты проверки:\n"
            error_msg += f"Загружено расчетных режимов - {len(rgms)}\n"
            error_msg += f"Загружено аварийных процесслов - {len(scns)}\n"
            error_msg += f"Максимальное время отключения КЗ составляет - {max_time}\n"
            raise InitialDataException(error_msg)
        
        self._progress_callback = progress_callback
        self._rgms = rgms
        self._scns = scns
        self._vrns = [v for v in vrns if not v.deactive]
        self._rems_path = rems_path
        self._time_precision = time_precision
        self._max_time = max_time
        
        # Создание папки для результатов
        self._root = Path.home() / "DynStabSpace" / f"{datetime.now():%Y-%m-%d %H-%M-%S} Предельное время КЗ"
        self._root.mkdir(parents=True, exist_ok=True)
    
    @property
    def root(self) -> str:
        """Путь к папке с результатами"""
        return str(self._root)
    
    @property
    def max(self) -> int:
        """Максимальное количество шагов расчета"""
        return len(self._rgms) * len(self._vrns) * len(self._scns) + 1
    
    def calc(self) -> List[CrtTimeResults]:
        """Выполнение расчета"""
        progress = 0
        results = []
        
        for rgm in self._rgms:
            crt_shems_list = []
            
            for vrn in self._vrns:
                times_list = []
                crt_shem = CrtShems(sheme_name=vrn.name, is_stable=False, times=[])
                
                for scn in self._scns:
                    rastr = RastrOperations()
                    rastr.load(rgm.name)
                    rastr.load(scn.name)
                    
                    # Применение варианта
                    if vrn.id == -1:
                        is_stable = rastr.rgm()
                    else:
                        is_stable = rastr.apply_variant(vrn.num, self._rems_path)
                    
                    crt_shem.is_stable = is_stable
                    
                    if is_stable:
                        # Поиск критического времени
                        crt_time = rastr.find_crt_time(self._time_precision, self._max_time)
                        
                        times_list.append(CrtTimes(
                            scn_name=Path(scn.name).stem,
                            crt_time=crt_time
                        ))
                        
                        progress += 1
                        if self._progress_callback:
                            self._progress_callback(progress)
                
                crt_shem.times = times_list
                crt_shems_list.append(crt_shem)
            
            results.append(CrtTimeResults(
                rg_name=Path(rgm.name).stem,
                crt_shems=crt_shems_list
            ))
        
        return results

