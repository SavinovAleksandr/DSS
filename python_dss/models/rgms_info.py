"""
Модель информации о расчетном режиме
"""

from pathlib import Path
from typing import Optional


class RgmsInfo:
    """Информация о расчетном режиме"""
    
    def __init__(self, name: Optional[str] = None):
        self._name = name
    
    @property
    def name(self) -> Optional[str]:
        """Полный путь к файлу режима"""
        return self._name
    
    @name.setter
    def name(self, value: Optional[str]):
        self._name = value
    
    @property
    def display_name(self) -> Optional[str]:
        """Имя файла без расширения для отображения"""
        if self._name:
            return Path(self._name).stem
        return None
    
    def __str__(self) -> str:
        return self.display_name or ""

