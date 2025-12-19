"""
Операции с RASTR через COM-интерфейс
"""

try:
    import win32com.client
    RASTR_AVAILABLE = True
except ImportError:
    RASTR_AVAILABLE = False

from .rastr_operations import RastrOperations
from .dynamic_result import DynamicResult
from .point import Point
from .shunt_kz_result import ShuntKZResult

__all__ = [
    'RastrOperations',
    'DynamicResult',
    'Point',
    'ShuntKZResult',
    'RASTR_AVAILABLE'
]

