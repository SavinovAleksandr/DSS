"""
Модели результатов расчетов
"""

from typing import List, Optional
from .values import Values
from .dynamic_result import DynamicResult


# ========== Шунты КЗ ==========

class ShuntKZ:
    """Информация о шунте КЗ для узла"""
    
    def __init__(self, node: int = 0, r1: float = -1.0, x1: float = -1.0,
                 u1: float = -1.0, r2: float = -1.0, x2: float = -1.0,
                 u2: float = -1.0):
        self.node = node
        self.r1 = r1
        self.x1 = x1
        self.u1 = u1
        self.r2 = r2
        self.x2 = x2
        self.u2 = u2


class Shems:
    """Результаты расчетов для схемы (шунты КЗ)"""
    
    def __init__(self, sheme_name: str = "", is_stable: bool = False,
                 nodes: Optional[List[ShuntKZ]] = None):
        self.sheme_name = sheme_name
        self.is_stable = is_stable
        self.nodes = nodes or []


class ShuntResults:
    """Результаты расчетов шунтов КЗ"""
    
    def __init__(self, rg_name: str = "", shems: Optional[List[Shems]] = None):
        self.rg_name = rg_name
        self.shems = shems or []


# ========== Предельное время КЗ ==========

class CrtTimes:
    """Предельное время отключения КЗ для сценария"""
    
    def __init__(self, scn_name: str = "", crt_time: float = 0.0):
        self.scn_name = scn_name
        self.crt_time = crt_time


class CrtShems:
    """Результаты расчетов для схемы (предельное время КЗ)"""
    
    def __init__(self, sheme_name: str = "", is_stable: bool = False,
                 times: Optional[List[CrtTimes]] = None):
        self.sheme_name = sheme_name
        self.is_stable = is_stable
        self.times = times or []


class CrtTimeResults:
    """Результаты расчетов предельного времени КЗ"""
    
    def __init__(self, rg_name: str = "", crt_shems: Optional[List[CrtShems]] = None):
        self.rg_name = rg_name
        self.crt_shems = crt_shems or []


# ========== Пакетный расчет ДУ ==========

class Events:
    """Результаты расчета для аварийного процесса"""
    
    def __init__(self, name: str = "",
                 no_pa_result: Optional[DynamicResult] = None,
                 with_pa_result: Optional[DynamicResult] = None,
                 no_pa_pic: Optional[List[str]] = None,
                 with_pa_pic: Optional[List[str]] = None):
        self.name = name
        self.no_pa_result = no_pa_result or DynamicResult()
        self.with_pa_result = with_pa_result or DynamicResult()
        self.no_pa_pic = no_pa_pic or []
        self.with_pa_pic = with_pa_pic or []


class DynShems:
    """Результаты расчетов для схемы (пакетный расчет ДУ)"""
    
    def __init__(self, sheme_name: str = "", is_stable: bool = False,
                 events: Optional[List[Events]] = None):
        self.sheme_name = sheme_name
        self.is_stable = is_stable
        self.events = events or []


class DynResults:
    """Результаты пакетного расчета динамической устойчивости"""
    
    def __init__(self, rg_name: str = "", dyn_shems: Optional[List[DynShems]] = None):
        self.rg_name = rg_name
        self.dyn_shems = dyn_shems or []


# ========== МДП ДУ ==========

class MdpEvents:
    """Результаты расчета МДП для аварийного процесса"""
    
    def __init__(self, name: str = "",
                 no_pa_sechen: Optional[List[Values]] = None,
                 no_pa_kpr: Optional[List[Values]] = None,
                 no_pa_mdp: float = -1.0,
                 with_pa_sechen: Optional[List[Values]] = None,
                 with_pa_kpr: Optional[List[Values]] = None,
                 with_pa_mdp: float = -1.0):
        self.name = name
        self.no_pa_sechen = no_pa_sechen or []
        self.no_pa_kpr = no_pa_kpr or []
        self.no_pa_mdp = no_pa_mdp
        self.with_pa_sechen = with_pa_sechen or []
        self.with_pa_kpr = with_pa_kpr or []
        self.with_pa_mdp = with_pa_mdp


class MdpShems:
    """Результаты расчетов для схемы (МДП ДУ)"""
    
    def __init__(self, sheme_name: str = "", is_ready: bool = False,
                 is_stable: bool = False, max_step: float = 0.0,
                 p_pred: float = 0.0, p_start: float = 0.0,
                 events: Optional[List[MdpEvents]] = None):
        self.sheme_name = sheme_name
        self.is_ready = is_ready
        self.is_stable = is_stable
        self.max_step = max_step
        self.p_pred = p_pred
        self.p_start = p_start
        self.events = events or []


class MdpResults:
    """Результаты определения МДП ДУ"""
    
    def __init__(self, rg_name: str = "", mdp_shems: Optional[List[MdpShems]] = None):
        self.rg_name = rg_name
        self.mdp_shems = mdp_shems or []


# ========== Остаточное напряжение при КЗ ==========

class UostEvents:
    """Результаты расчета остаточного напряжения для аварийного процесса"""
    
    def __init__(self, name: str = "", begin_node: int = 0, end_node: int = 0,
                 np: int = 0, distance: float = 100.0,
                 begin_uost: float = -1.0, end_uost: float = -1.0,
                 values: Optional[List[Values]] = None):
        self.name = name
        self.begin_node = begin_node
        self.end_node = end_node
        self.np = np
        self.distance = distance
        self.begin_uost = begin_uost
        self.end_uost = end_uost
        self.values = values or []


class UostShems:
    """Результаты расчетов для схемы (остаточное напряжение)"""
    
    def __init__(self, sheme_name: str = "", is_stable: bool = False,
                 events: Optional[List[UostEvents]] = None):
        self.sheme_name = sheme_name
        self.is_stable = is_stable
        self.events = events or []


class UostResults:
    """Результаты определения остаточного напряжения при КЗ"""
    
    def __init__(self, rg_name: str = "", uost_shems: Optional[List[UostShems]] = None):
        self.rg_name = rg_name
        self.uost_shems = uost_shems or []

