"""
Расчет остаточного напряжения на шинах энергообъекта при КЗ на границе устойчивости
"""

import os
import math
import locale
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from models import (
    RgmsInfo, ScnsInfo, VrnInfo, KprInfo,
    UostResults, UostShems, UostEvents, Values
)
from rastr_operations import RastrOperations, DynamicResult
from utils.exceptions import InitialDataException


class UostStabilityCalc:
    """Расчет остаточного напряжения при КЗ на границе устойчивости"""
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]],
                 rgms: List[RgmsInfo], scns: List[ScnsInfo], vrns: List[VrnInfo],
                 rems_path: Optional[str], kprs: List[KprInfo]):
        """
        Инициализация расчета остаточного напряжения
        
        Args:
            progress_callback: Функция обратного вызова для обновления прогресса
            rgms: Список расчетных режимов
            scns: Список аварийных процессов
            vrns: Список вариантов (ремонтных схем)
            rems_path: Путь к файлу ремонтных схем
            kprs: Список контролируемых величин
        """
        if not rgms or not scns:
            error_msg = "Не заданы все исходные данные для определения остаточного напряжения!\n\n"
            error_msg += f"Результаты проверки:\n"
            error_msg += f"Загружено расчетных режимов - {len(rgms)}\n"
            error_msg += f"Загружено аварийных процесслов - {len(scns)}\n"
            raise InitialDataException(error_msg)
        
        self._progress_callback = progress_callback
        self._rgms = rgms
        self._scns = scns
        self._vrns = [v for v in vrns if not v.deactive]
        self._rems_path = rems_path
        self._kprs = kprs
        
        # Создание папки для результатов
        self._root = Path.home() / "DynStabSpace" / f"{datetime.now():%Y-%m-%d %H-%M-%S} Uост на границе устойчивости"
        self._root.mkdir(parents=True, exist_ok=True)
    
    @property
    def root(self) -> str:
        """Путь к папке с результатами"""
        return str(self._root)
    
    @property
    def max(self) -> int:
        """Максимальное количество шагов расчета"""
        return len(self._rgms) * len([v for v in self._vrns if not v.deactive]) * len(self._scns) + 1
    
    def calc(self) -> List[UostResults]:
        """Выполнение расчета"""
        progress = 0
        results = []
        
        for rgm in self._rgms:
            uost_shems_list = []
            
            for vrn in self._vrns:
                events_list = []
                
                for scn in self._scns:
                    rastr = RastrOperations()
                    rastr.load(rgm.name)
                    rastr.dyn_settings()
                    
                    # Применение варианта
                    is_stable = (rastr.rgm() if vrn.id == -1 else rastr.apply_variant(vrn.num, self._rems_path))
                    
                    if not is_stable:
                        continue
                    
                    rastr.load(scn.name)
                    
                    # Извлечение информации о КЗ из сценария
                    distance = 100.0
                    line_key = ""
                    node_kz = 0
                    time_start = 0.0
                    r_shunt = -1.0
                    x_shunt = -1.0
                    r_id = 0
                    x_id = 0
                    
                    actions = rastr.selection("DFWAutoActionScn")
                    for action_id in actions:
                        obj_class = rastr.get_val("DFWAutoActionScn", "ObjectClass", action_id)
                        
                        if obj_class == "vetv":
                            line_key = rastr.get_val("DFWAutoActionScn", "ObjectKey", action_id)
                            rastr.set_val("DFWAutoActionScn", "State", action_id, 1)
                        
                        if obj_class == "node":
                            node_kz = int(rastr.get_val("DFWAutoActionScn", "ObjectKey", action_id))
                            time_start = rastr.get_val("DFWAutoActionScn", "TimeStart", action_id)
                            
                            # Создание нового узла для расчета
                            new_node_id = rastr.add_table_row("node")
                            rastr.set_val("node", "ny", new_node_id, len(actions) + 1)
                            u_nom = rastr.get_val("node", "uhom", f"ny={node_kz}")
                            rastr.set_val("node", "uhom", new_node_id, u_nom)
                            
                            obj_prop = rastr.get_val("DFWAutoActionScn", "ObjectProp", action_id)
                            if obj_prop == "r":
                                r_shunt = float(str(rastr.get_val("DFWAutoActionScn", "Formula", action_id)).replace(".", locale.localeconv()['decimal_point']))
                                r_id = action_id
                            if obj_prop == "x":
                                x_shunt = float(str(rastr.get_val("DFWAutoActionScn", "Formula", action_id)).replace(".", locale.localeconv()['decimal_point']))
                                x_id = action_id
                    
                    # Парсинг ключа линии
                    line_parts = line_key.split(",")
                    if len(line_parts) >= 3:
                        ip = int(line_parts[0])
                        iq = int(line_parts[1])
                        np = int(line_parts[2])
                    else:
                        continue
                    
                    # Получение параметров линии
                    r_line = rastr.get_val("vetv", "r", f"ip={ip} & iq={iq} & np={np}")
                    x_line = rastr.get_val("vetv", "x", f"ip={ip} & iq={iq} & np={np}")
                    b_line = rastr.get_val("vetv", "b", f"ip={ip} & iq={iq} & np={np}")
                    
                    # Отключение исходной линии и добавление новой
                    rastr.set_val("vetv", "sta", f"ip={ip} & iq={iq} & np={np}", 1)
                    rastr.set_val("node", "bsh", f"ny={ip}", b_line / 2.0)
                    rastr.set_val("node", "bsh", f"ny={iq}", b_line / 2.0)
                    
                    new_node_id = rastr.add_table_row("node")
                    rastr.set_val("node", "ny", new_node_id, len(actions) + 1)
                    rastr.set_val("node", "uhom", new_node_id, rastr.get_val("node", "uhom", f"ny={node_kz}"))
                    
                    # Добавление новых ветвей
                    branch1_id = rastr.add_table_row("vetv")
                    branch2_id = rastr.add_table_row("vetv")
                    
                    rastr.set_val("vetv", "ip", branch1_id, ip)
                    rastr.set_val("vetv", "iq", branch1_id, new_node_id)
                    rastr.set_val("vetv", "ip", branch2_id, new_node_id)
                    rastr.set_val("vetv", "iq", branch2_id, iq)
                    
                    rastr.rgm()
                    
                    # Расчет угла и модуля шунта
                    z_angle = (math.pi / 2.0) if r_shunt == -1.0 else math.atan(x_shunt / r_shunt)
                    z_mod = math.sqrt((r_shunt ** 2 if r_shunt != -1.0 else 0) + x_shunt ** 2)
                    
                    # Определение начальной позиции КЗ
                    l_start = (0.1 if ip == node_kz else 99.9)
                    l_end = 100.0 - l_start
                    
                    # Первый расчет
                    rastr.set_line_for_uost_calc(branch1_id, branch2_id, r_line, x_line, l_start)
                    dyn_result1 = rastr.run_dynamic(ems=True)
                    
                    # Второй расчет
                    rastr.set_line_for_uost_calc(branch1_id, branch2_id, r_line, x_line, l_end)
                    dyn_result2 = rastr.run_dynamic(ems=True)
                    
                    # Определение границы устойчивости
                    if (dyn_result1.is_success and dyn_result2.is_success and 
                        (dyn_result1.is_stable != dyn_result2.is_stable)):
                        # Бинарный поиск границы
                        l_stable = l_start if dyn_result1.is_stable else l_end
                        l_unstable = l_end if dyn_result1.is_stable else l_start
                        l_current = abs(l_stable - l_unstable) * 0.5
                        
                        rastr.set_line_for_uost_calc(branch1_id, branch2_id, r_line, x_line, l_current)
                        dyn_result3 = rastr.run_dynamic(ems=True)
                        
                        while dyn_result3.is_success and (not dyn_result3.is_stable or abs(l_stable - l_unstable) > 0.5):
                            if dyn_result3.is_stable:
                                l_stable = l_current
                            else:
                                l_unstable = l_current
                            
                            l_current += abs(l_unstable - l_stable) * 0.5 * (1 if ((dyn_result1.is_stable and dyn_result3.is_stable) or 
                                                                                  (not dyn_result1.is_stable and not dyn_result3.is_stable)) else -1)
                            distance = l_current
                            
                            rastr.set_line_for_uost_calc(branch1_id, branch2_id, r_line, x_line, l_current)
                            dyn_result3 = rastr.run_dynamic(ems=True)
                    elif (dyn_result1.is_success and not dyn_result1.is_stable and 
                          dyn_result2.is_success and not dyn_result2.is_stable):
                        # Оба неустойчивы - увеличиваем шунт
                        distance = -1.0
                        rastr.set_line_for_uost_calc(branch1_id, branch2_id, r_line, x_line, (99.9 if ip == node_kz else 0.1))
                        
                        z_mod_new = (z_mod * 2.0) if z_mod > 0.1 else 1.0
                        z_mod_old = z_mod
                        
                        if r_shunt == -1.0:
                            rastr.change_rx_for_uost_calc(x_id, z_mod_new * math.sin(z_angle))
                        else:
                            rastr.change_rx_for_uost_calc(x_id, z_mod_new * math.sin(z_angle), 
                                                          r_id, z_mod_new * math.cos(z_angle))
                        
                        dyn_result4 = rastr.run_dynamic(ems=True)
                        
                        while dyn_result4.is_success and not dyn_result4.is_stable:
                            z_mod_old = z_mod_new
                            z_mod_new += (z_mod if z_mod > 0.1 else 1.0)
                            
                            if r_shunt == -1.0:
                                rastr.change_rx_for_uost_calc(x_id, z_mod_new * math.sin(z_angle))
                            else:
                                rastr.change_rx_for_uost_calc(x_id, z_mod_new * math.sin(z_angle),
                                                              r_id, z_mod_new * math.cos(z_angle))
                            
                            dyn_result4 = rastr.run_dynamic(ems=True)
                        
                        # Уточнение границы
                        while dyn_result4.is_success and (not dyn_result4.is_stable or (1.0 - z_mod_old / z_mod_new) > 0.025):
                            z_step = (z_mod_old - z_mod_new) * 0.5 if dyn_result4.is_stable else (z_mod_new - z_mod_old) * 0.5
                            z_current = z_mod_new + z_step
                            
                            if r_shunt == -1.0:
                                rastr.change_rx_for_uost_calc(x_id, z_current * math.sin(z_angle))
                            else:
                                rastr.change_rx_for_uost_calc(x_id, z_current * math.sin(z_angle),
                                                              r_id, z_current * math.cos(z_angle))
                            
                            dyn_result4 = rastr.run_dynamic(ems=True)
                            
                            if dyn_result4.is_stable:
                                z_mod_new = z_current
                            else:
                                z_mod_old = z_current
                    
                    # Получение остаточных напряжений
                    begin_uost = -1.0
                    end_uost = -1.0
                    
                    dyn_result5 = rastr.run_dynamic(ems=False, max_time=time_start + 0.02)
                    if dyn_result5.is_success and dyn_result5.is_stable:
                        points_ip = rastr.get_points_from_exit_file("node", "vras", f"ny={ip}")
                        points_iq = rastr.get_points_from_exit_file("node", "vras", f"ny={iq}")
                        
                        for point in points_ip:
                            if abs(point.x - time_start) < 0.001:
                                begin_uost = point.y
                                break
                        
                        for point in points_iq:
                            if abs(point.x - time_start) < 0.001:
                                end_uost = point.y
                                break
                    
                    # Сбор контролируемых величин
                    values_list = []
                    for kpr in self._kprs:
                        values_list.append(Values(
                            id=kpr.id,
                            name=kpr.name,
                            value=rastr.get_val(kpr.table, kpr.col, kpr.selection)
                        ))
                    
                    events_list.append(UostEvents(
                        name=Path(scn.name).stem,
                        begin_node=ip,
                        end_node=iq,
                        np=np,
                        distance=distance,
                        begin_uost=begin_uost,
                        end_uost=end_uost,
                        values=values_list
                    ))
                    
                    progress += 1
                    if self._progress_callback:
                        self._progress_callback(progress)
                
                uost_shems_list.append(UostShems(
                    sheme_name=vrn.name,
                    is_stable=is_stable,
                    events=events_list
                ))
            
            results.append(UostResults(
                rg_name=Path(rgm.name).stem,
                uost_shems=uost_shems_list
            ))
        
        return results

