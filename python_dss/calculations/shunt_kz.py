"""
Расчет шунтов короткого замыкания
"""

import os
import math
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from models import (
    RgmsInfo, VrnInfo, ShuntKZ, ShuntResults, Shems
)
from rastr_operations import RastrOperations, ShuntKZResult
from utils.exceptions import InitialDataException


class ShuntKZCalc:
    """Расчет шунтов короткого замыкания"""
    
    BASE_ANGLE = 1.471  # 84.32 градуса в радианах
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]],
                 rgms: List[RgmsInfo], vrns: List[VrnInfo], rems_path: Optional[str],
                 shunt_kz_inf: List[ShuntKZ], use_sel_nodes: bool, use_type_val_u: bool,
                 calc_one_phase: bool, calc_two_phase: bool):
        """
        Инициализация расчета шунтов КЗ
        
        Args:
            progress_callback: Функция обратного вызова для обновления прогресса
            rgms: Список расчетных режимов
            vrns: Список вариантов (ремонтных схем)
            rems_path: Путь к файлу ремонтных схем
            shunt_kz_inf: Список узлов для расчета шунтов КЗ
            use_sel_nodes: Использовать отмеченные узлы
            use_type_val_u: Использовать типовые значения остаточного напряжения
            calc_one_phase: Расчет для однофазного КЗ
            calc_two_phase: Расчет для двухфазного КЗ
        """
        if not rgms or (not shunt_kz_inf and not use_sel_nodes) or (not calc_one_phase and not calc_two_phase):
            error_msg = "Не заданы все исходные данные для определения шунтов КЗ!\n\n"
            error_msg += f"Результаты проверки:\n"
            error_msg += f"Загружено расчетных режимов - {len(rgms)}\n"
            if not shunt_kz_inf and not use_sel_nodes:
                error_msg += "Отсутствуют узлы в файле задания или отключен чекбокс Использовать отмеченные узлы!\n"
            if not calc_one_phase and not calc_two_phase:
                error_msg += "Отключены чекбосы расчетов однофазного и двухфазного КЗ!\n"
            raise InitialDataException(error_msg)
        
        self._progress_callback = progress_callback
        self._rgms = rgms
        self._vrns = [v for v in vrns if not v.deactive]
        self._rems_path = rems_path
        self._shunt_kz_inf = shunt_kz_inf
        self._use_sel_nodes = use_sel_nodes
        self._use_type_val_u = use_type_val_u
        self._calc_one_phase = calc_one_phase
        self._calc_two_phase = calc_two_phase
        
        # Создание папки для результатов
        self._root = Path.home() / "DynStabSpace" / f"{datetime.now():%Y-%m-%d %H-%M-%S} Шунты КЗ"
        self._root.mkdir(parents=True, exist_ok=True)
    
    @property
    def root(self) -> str:
        """Путь к папке с результатами"""
        return str(self._root)
    
    @property
    def max(self) -> int:
        """Максимальное количество шагов расчета"""
        num_phases = (1 if self._calc_one_phase else 0) + (1 if self._calc_two_phase else 0)
        
        if not self._use_sel_nodes:
            return len(self._rgms) * len(self._vrns) * len(self._shunt_kz_inf) * num_phases + 1
        
        # Подсчет отмеченных узлов для каждого режима
        total_nodes = 0
        rastr = RastrOperations()
        for rgm in self._rgms:
            try:
                rastr.load(rgm.name)
                selected = rastr.selection("node", "sel = 1")
                total_nodes += len(selected) * len(self._vrns) * num_phases
            except:
                pass
        
        return total_nodes + 1
    
    def calc(self) -> List[ShuntResults]:
        """Выполнение расчета"""
        progress = 0
        results = []
        
        for rgm in self._rgms:
            shems_list = []
            
            for vrn in self._vrns:
                nodes_list = []
                rastr = RastrOperations()
                rastr.load(rgm.name)
                
                # Применение варианта
                if vrn.id == -1:
                    is_stable = rastr.rgm()
                else:
                    is_stable = rastr.apply_variant(vrn.num, self._rems_path)
                
                if not is_stable:
                    shems_list.append(Shems(
                        sheme_name=vrn.name,
                        is_stable=False,
                        nodes=[]
                    ))
                    continue
                
                # Расчет шунтов КЗ
                if not self._use_sel_nodes:
                    # Использование узлов из файла задания
                    for shunt_node in self._shunt_kz_inf:
                        shunt_result = ShuntKZ()
                        shunt_result.node = shunt_node.node
                        
                        rastr.rgm()
                        v_initial = rastr.get_val("node", "vras", f"ny={shunt_node.node}")
                        
                        # Расчет однофазного КЗ
                        if self._calc_one_phase:
                            if shunt_node.x1 != -1.0 and (shunt_node.u1 != -1.0 or self._use_type_val_u):
                                u_target = shunt_node.u1 if shunt_node.u1 != -1.0 else (v_initial * 0.66)
                                result = rastr.find_shunt_kz(
                                    shunt_node.node, u_target, shunt_node.x1, shunt_node.r1
                                )
                                shunt_result.r1 = result.r
                                shunt_result.x1 = result.x
                                shunt_result.u1 = result.u
                            elif shunt_node.x1 == -1.0 and (shunt_node.u1 != -1.0 or self._use_type_val_u):
                                u_target = shunt_node.u1 if shunt_node.u1 != -1.0 else (v_initial * 0.66)
                                result = rastr.find_shunt_kz(
                                    shunt_node.node, u_target,
                                    math.sin(self.BASE_ANGLE), math.cos(self.BASE_ANGLE)
                                )
                                shunt_result.r1 = result.r
                                shunt_result.x1 = result.x
                                shunt_result.u1 = result.u
                            
                            progress += 1
                            if self._progress_callback:
                                self._progress_callback(progress)
                        
                        # Расчет двухфазного КЗ
                        if self._calc_two_phase:
                            if shunt_node.x2 != -1.0 and (shunt_node.u2 != -1.0 or self._use_type_val_u):
                                u_target = shunt_node.u2 if shunt_node.u2 != -1.0 else (v_initial * 0.33)
                                result = rastr.find_shunt_kz(
                                    shunt_node.node, u_target, shunt_node.x2, shunt_node.r2
                                )
                                shunt_result.r2 = result.r
                                shunt_result.x2 = result.x
                                shunt_result.u2 = result.u
                            elif shunt_node.x2 == -1.0 and (shunt_node.u2 != -1.0 or self._use_type_val_u):
                                u_target = shunt_node.u2 if shunt_node.u2 != -1.0 else (v_initial * 0.33)
                                result = rastr.find_shunt_kz(
                                    shunt_node.node, u_target,
                                    math.sin(self.BASE_ANGLE), math.cos(self.BASE_ANGLE)
                                )
                                shunt_result.r2 = result.r
                                shunt_result.x2 = result.x
                                shunt_result.u2 = result.u
                            
                            progress += 1
                            if self._progress_callback:
                                self._progress_callback(progress)
                        
                        nodes_list.append(shunt_result)
                else:
                    # Использование отмеченных узлов
                    selected_nodes = rastr.selection("node", "sel = 1")
                    
                    for node_idx in selected_nodes:
                        shunt_result = ShuntKZ()
                        rastr.rgm()
                        v_initial = rastr.get_val("node", "vras", node_idx)
                        node_num = rastr.get_val("node", "ny", node_idx)
                        shunt_result.node = node_num
                        
                        # Расчет однофазного КЗ
                        if self._calc_one_phase:
                            result = rastr.find_shunt_kz(
                                node_num, v_initial * 0.66,
                                math.sin(self.BASE_ANGLE), math.cos(self.BASE_ANGLE)
                            )
                            shunt_result.r1 = result.r
                            shunt_result.x1 = result.x
                            shunt_result.u1 = result.u
                            
                            progress += 1
                            if self._progress_callback:
                                self._progress_callback(progress)
                        
                        # Расчет двухфазного КЗ
                        if self._calc_two_phase:
                            result = rastr.find_shunt_kz(
                                node_num, v_initial * 0.33,
                                math.sin(self.BASE_ANGLE), math.cos(self.BASE_ANGLE)
                            )
                            shunt_result.r2 = result.r
                            shunt_result.x2 = result.x
                            shunt_result.u2 = result.u
                            
                            progress += 1
                            if self._progress_callback:
                                self._progress_callback(progress)
                        
                        nodes_list.append(shunt_result)
                
                shems_list.append(Shems(
                    sheme_name=vrn.name,
                    is_stable=is_stable,
                    nodes=nodes_list
                ))
            
            results.append(ShuntResults(
                rg_name=Path(rgm.name).stem,
                shems=shems_list
            ))
        
        return results

