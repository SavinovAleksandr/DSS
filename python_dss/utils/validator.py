"""
Валидация данных в реальном времени
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple
from enum import Enum

from utils.logger import logger
from utils.error_handler import error_handler
from utils.file_type_detector import FileTypeDetector
from data_info import DataInfo


class ValidationStatus(Enum):
    """Статус валидации"""
    VALID = "valid"           # ✅ Валидно
    INVALID = "invalid"       # ❌ Невалидно
    WARNING = "warning"       # ⚠️ Предупреждение
    UNKNOWN = "unknown"       # ❓ Неизвестно


class ValidationResult:
    """Результат валидации"""
    
    def __init__(self, status: ValidationStatus, message: str = "", details: Optional[str] = None):
        self.status = status
        self.message = message
        self.details = details
    
    @property
    def is_valid(self) -> bool:
        """Проверка, валидны ли данные"""
        return self.status == ValidationStatus.VALID
    
    @property
    def icon(self) -> str:
        """Получить иконку для статуса"""
        icons = {
            ValidationStatus.VALID: "✅",
            ValidationStatus.INVALID: "❌",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.UNKNOWN: "❓"
        }
        return icons.get(self.status, "❓")
    
    def __str__(self):
        if self.message:
            return f"{self.icon} {self.message}"
        return self.icon


class DataValidator:
    """Класс для валидации данных"""
    
    def __init__(self, data_info: DataInfo):
        self.data_info = data_info
        self.validation_cache: Dict[str, ValidationResult] = {}
    
    def validate_file(self, file_path: Optional[str], file_type: str) -> ValidationResult:
        """
        Валидация файла
        
        Args:
            file_path: Путь к файлу
            file_type: Тип файла (rems, lapnu, vir, sechen, grf)
        
        Returns:
            ValidationResult
        """
        cache_key = f"{file_type}:{file_path}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        # Если файл не указан
        if not file_path:
            result = ValidationResult(
                ValidationStatus.UNKNOWN,
                "Файл не загружен"
            )
            self.validation_cache[cache_key] = result
            return result
        
        file_path_obj = Path(file_path)
        
        # Проверка существования
        is_valid, error_msg = error_handler.validate_file_path(file_path_obj, must_exist=True)
        if not is_valid:
            result = ValidationResult(
                ValidationStatus.INVALID,
                error_msg or "Файл не найден"
            )
            self.validation_cache[cache_key] = result
            return result
        
        # Проверка расширения
        expected_extensions = FileTypeDetector.get_extensions(file_type)
        if expected_extensions:
            if not FileTypeDetector.is_valid_extension(file_path, file_type):
                file_ext = file_path_obj.suffix.lower()
                result = ValidationResult(
                    ValidationStatus.WARNING,
                    f"Неожиданное расширение файла: {file_ext}",
                    f"Ожидаемые расширения: {', '.join(expected_extensions)}"
                )
                self.validation_cache[cache_key] = result
                return result
        
        # Проверка размера файла (не должен быть пустым)
        try:
            if file_path_obj.stat().st_size == 0:
                result = ValidationResult(
                    ValidationStatus.INVALID,
                    "Файл пуст"
                )
                self.validation_cache[cache_key] = result
                return result
        except Exception as e:
            logger.warning(f"Не удалось проверить размер файла {file_path}: {e}")
        
        # Все проверки пройдены
        result = ValidationResult(
            ValidationStatus.VALID,
            f"Файл валиден: {file_path_obj.name}"
        )
        self.validation_cache[cache_key] = result
        return result
    
    def validate_calculation_requirements(self, calculation_type: str) -> Tuple[bool, List[str]]:
        """
        Проверка требований для расчета
        
        Args:
            calculation_type: Тип расчета (shunt_kz, max_kz_time, dyn_stability, mdp_stability, uost_stability)
        
        Returns:
            tuple: (валидны ли данные, список отсутствующих полей)
        """
        missing_fields = []
        
        # Общие требования
        if not self.data_info.rgms_info:
            missing_fields.append("Расчетные режимы")
        
        if not self.data_info.scns_info:
            missing_fields.append("Аварийные процессы")
        
        # Специфичные требования для каждого типа расчета
        if calculation_type == "shunt_kz":
            if not self.data_info.rems.name:
                missing_fields.append("Ремонтные схемы")
        
        elif calculation_type == "max_kz_time":
            if not self.data_info.rems.name:
                missing_fields.append("Ремонтные схемы")
        
        elif calculation_type == "dyn_stability":
            if not self.data_info.rems.name:
                missing_fields.append("Ремонтные схемы")
            if not self.data_info.vir.name:
                missing_fields.append("Траектория")
            if not self.data_info.sechen.name:
                missing_fields.append("Сечения")
            if not self.data_info.grf.name:
                missing_fields.append("Графический вывод")
        
        elif calculation_type == "mdp_stability":
            if not self.data_info.rems.name:
                missing_fields.append("Ремонтные схемы")
            if not self.data_info.vir.name:
                missing_fields.append("Траектория")
            if not self.data_info.sechen.name:
                missing_fields.append("Сечения")
            if not self.data_info.grf.name:
                missing_fields.append("Графический вывод")
        
        elif calculation_type == "uost_stability":
            if not self.data_info.rems.name:
                missing_fields.append("Ремонтные схемы")
            if not self.data_info.sechen.name:
                missing_fields.append("Сечения")
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
    
    def validate_all_files(self) -> Dict[str, ValidationResult]:
        """Валидация всех файлов"""
        results = {}
        
        results['rems'] = self.validate_file(self.data_info.rems.filename, 'rems')
        results['lapnu'] = self.validate_file(self.data_info.lapnu.filename, 'lapnu')
        results['vir'] = self.validate_file(self.data_info.vir.filename, 'vir')
        results['sechen'] = self.validate_file(self.data_info.sechen.filename, 'sechen')
        results['grf'] = self.validate_file(self.data_info.grf.filename, 'grf')
        
        return results
    
    def clear_cache(self):
        """Очистить кэш валидации"""
        self.validation_cache.clear()
        logger.debug("Кэш валидации очищен")
    
    def get_validation_summary(self) -> str:
        """Получить краткую сводку валидации"""
        all_results = self.validate_all_files()
        valid_count = sum(1 for r in all_results.values() if r.is_valid)
        total_count = len(all_results)
        
        if valid_count == total_count:
            return f"✅ Все файлы валидны ({valid_count}/{total_count})"
        else:
            invalid_count = total_count - valid_count
            return f"⚠️ Валидных: {valid_count}/{total_count}, невалидных: {invalid_count}"

