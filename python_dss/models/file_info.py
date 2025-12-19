"""
Модель информации о файле
"""

from pathlib import Path
from typing import Optional


class FileInfo:
    """Информация о файле"""
    
    def __init__(self, name: Optional[str] = None):
        self._name = name
    
    @property
    def name(self) -> Optional[str]:
        """Полный путь к файлу"""
        return self._name
    
    @name.setter
    def name(self, value: Optional[str]):
        self._name = value
    
    @property
    def filename(self) -> Optional[str]:
        """Имя файла без пути"""
        if self._name:
            return Path(self._name).name
        return None
    
    def __str__(self) -> str:
        return self.filename or ""

