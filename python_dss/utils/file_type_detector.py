"""
Определение типов файлов по расширению
"""

from pathlib import Path
from typing import Optional, List, Dict


class FileTypeDetector:
    """Класс для определения типа файла по расширению"""
    
    # Маппинг расширений на типы файлов
    FILE_TYPES: Dict[str, str] = {
        # Расчетные режимы
        '.rg2': 'rems',
        '.rst': 'rems',
        
        # Аварийные процессы
        '.scn': 'scenario',
        
        # Траектория утяжеления
        '.ut2': 'vir',
        
        # Файл сечений
        '.sch': 'sechen',
        
        # Ремонтные схемы
        '.vrn': 'rems_vrn',
        
        # Графический вывод
        '.kpr': 'grf',
        
        # Файл задания для шунтов КЗ
        '.csv': 'shunt_kz',
        
        # Файлы ПА
        '.dwf': 'lapnu',
        '.lpn': 'lapnu',
    }
    
    # Обратный маппинг: тип файла -> расширения (для валидации)
    TYPE_EXTENSIONS: Dict[str, List[str]] = {
        'rems': ['.rg2', '.rst'],
        'scenario': ['.scn'],
        'vir': ['.ut2'],
        'sechen': ['.sch'],
        'rems_vrn': ['.vrn'],
        'grf': ['.kpr'],
        'shunt_kz': ['.csv'],
        'lapnu': ['.dwf', '.lpn'],
    }
    
    @classmethod
    def detect(cls, file_path: str) -> Optional[str]:
        """
        Определить тип файла по расширению
        
        Args:
            file_path: Путь к файлу
        
        Returns:
            Тип файла или None, если тип не определен
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        return cls.FILE_TYPES.get(ext)
    
    @classmethod
    def get_extensions(cls, file_type: str) -> List[str]:
        """
        Получить список расширений для типа файла
        
        Args:
            file_type: Тип файла
        
        Returns:
            Список расширений
        """
        return cls.TYPE_EXTENSIONS.get(file_type, [])
    
    @classmethod
    def is_valid_extension(cls, file_path: str, file_type: str) -> bool:
        """
        Проверить, соответствует ли расширение файла указанному типу
        
        Args:
            file_path: Путь к файлу
            file_type: Ожидаемый тип файла
        
        Returns:
            True если расширение соответствует типу
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        valid_extensions = cls.get_extensions(file_type)
        return ext in valid_extensions
    
    @classmethod
    def get_all_extensions(cls) -> List[str]:
        """
        Получить все поддерживаемые расширения
        
        Returns:
            Список всех расширений
        """
        return list(cls.FILE_TYPES.keys())
    
    @classmethod
    def get_file_type_name(cls, file_type: str) -> str:
        """
        Получить человекочитаемое имя типа файла
        
        Args:
            file_type: Тип файла
        
        Returns:
            Имя типа файла
        """
        names = {
            'rems': 'Расчетный режим',
            'scenario': 'Аварийный процесс',
            'vir': 'Траектория утяжеления',
            'sechen': 'Файл сечений',
            'rems_vrn': 'Ремонтные схемы',
            'grf': 'Графический вывод',
            'shunt_kz': 'Файл задания для шунтов КЗ',
            'lapnu': 'Файл ПА',
        }
        return names.get(file_type, file_type)

