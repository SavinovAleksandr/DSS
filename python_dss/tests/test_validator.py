"""
Тесты для модуля валидации
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from utils.validator import DataValidator, ValidationStatus, ValidationResult
from data_info import DataInfo


class TestValidationResult:
    """Тесты для ValidationResult"""
    
    def test_valid_result(self):
        """Тест валидного результата"""
        result = ValidationResult(ValidationStatus.VALID, "Файл валиден")
        assert result.is_valid is True
        assert result.icon == "✅"
        assert "✅" in str(result)
    
    def test_invalid_result(self):
        """Тест невалидного результата"""
        result = ValidationResult(ValidationStatus.INVALID, "Файл не найден")
        assert result.is_valid is False
        assert result.icon == "❌"
    
    def test_warning_result(self):
        """Тест предупреждения"""
        result = ValidationResult(ValidationStatus.WARNING, "Неожиданное расширение")
        assert result.is_valid is False
        assert result.icon == "⚠️"


class TestDataValidator:
    """Тесты для DataValidator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def validator(self, sample_data_info):
        """Создание валидатора"""
        return DataValidator(sample_data_info)
    
    def test_validate_file_not_exists(self, validator):
        """Тест валидации несуществующего файла"""
        result = validator.validate_file("nonexistent.rg2", "rems")
        assert result.status == ValidationStatus.INVALID
        assert "не найден" in result.message.lower() or "not found" in result.message.lower()
    
    def test_validate_file_exists(self, validator, temp_dir):
        """Тест валидации существующего файла"""
        test_file = temp_dir / "test.rg2"
        test_file.write_text("test content")
        
        result = validator.validate_file(str(test_file), "rems")
        assert result.status == ValidationStatus.VALID
        assert result.is_valid is True
    
    def test_validate_file_wrong_extension(self, validator, temp_dir):
        """Тест валидации файла с неправильным расширением"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        result = validator.validate_file(str(test_file), "rems")
        assert result.status == ValidationStatus.WARNING
        assert "расширение" in result.message.lower() or "extension" in result.message.lower()
    
    def test_validate_file_empty(self, validator, temp_dir):
        """Тест валидации пустого файла"""
        test_file = temp_dir / "empty.rg2"
        test_file.write_text("")
        
        result = validator.validate_file(str(test_file), "rems")
        assert result.status == ValidationStatus.INVALID
        assert "пуст" in result.message.lower() or "empty" in result.message.lower()
    
    def test_validate_file_none(self, validator):
        """Тест валидации None файла"""
        result = validator.validate_file(None, "rems")
        assert result.status == ValidationStatus.UNKNOWN
        assert "не загружен" in result.message.lower()
    
    def test_validate_calculation_requirements_shunt_kz(self, validator, sample_data_info):
        """Тест проверки требований для расчета шунтов КЗ"""
        # Без данных
        is_valid, missing = validator.validate_calculation_requirements("shunt_kz")
        assert is_valid is False
        assert "Расчетные режимы" in missing
        
        # С расчетными режимами
        from models import RgmsInfo
        sample_data_info.rgms_info.append(RgmsInfo(name="test.rg2"))
        is_valid, missing = validator.validate_calculation_requirements("shunt_kz")
        assert is_valid is False  # Все еще нет ремонтных схем
        
        # С ремонтными схемами
        sample_data_info.rems.name = "test_rems.rg2"
        is_valid, missing = validator.validate_calculation_requirements("shunt_kz")
        assert is_valid is True
        assert len(missing) == 0
    
    def test_validate_calculation_requirements_dyn_stability(self, validator, sample_data_info):
        """Тест проверки требований для расчета ДУ"""
        from models import RgmsInfo, ScnsInfo
        sample_data_info.rgms_info.append(RgmsInfo(name="test.rg2"))
        sample_data_info.scns_info.append(ScnsInfo(name="test.scn"))
        
        is_valid, missing = validator.validate_calculation_requirements("dyn_stability")
        assert is_valid is False
        assert "Ремонтные схемы" in missing or "Траектория" in missing or "Сечения" in missing
        
        # Добавляем все необходимые данные
        sample_data_info.rems.name = "test_rems.rg2"
        sample_data_info.vir.name = "test_vir.vrn"
        sample_data_info.sechen.name = "test_sechen.sch"
        sample_data_info.grf.name = "test_grf.kpr"
        
        is_valid, missing = validator.validate_calculation_requirements("dyn_stability")
        assert is_valid is True
    
    def test_validate_all_files(self, validator, sample_data_info, temp_dir):
        """Тест валидации всех файлов"""
        # Создаем тестовые файлы
        test_files = {
            'rems': temp_dir / "rems.rg2",
            'lapnu': temp_dir / "lapnu.lpn",
            'vir': temp_dir / "vir.vrn",
            'sechen': temp_dir / "sechen.sch",
            'grf': temp_dir / "grf.kpr"
        }
        
        for file_path in test_files.values():
            file_path.write_text("test content")
        
        sample_data_info.rems.name = str(test_files['rems'])
        sample_data_info.lapnu.name = str(test_files['lapnu'])
        sample_data_info.vir.name = str(test_files['vir'])
        sample_data_info.sechen.name = str(test_files['sechen'])
        sample_data_info.grf.name = str(test_files['grf'])
        
        results = validator.validate_all_files()
        
        assert len(results) == 5
        assert all(r.status == ValidationStatus.VALID for r in results.values())
    
    def test_cache_clearing(self, validator):
        """Тест очистки кэша валидации"""
        validator.validate_file("test.rg2", "rems")
        assert len(validator.validation_cache) > 0
        
        validator.clear_cache()
        assert len(validator.validation_cache) == 0
    
    def test_validation_summary(self, validator, sample_data_info, temp_dir):
        """Тест сводки валидации"""
        # Без файлов
        summary = validator.get_validation_summary()
        assert "❓" in summary or "не загружен" in summary.lower()
        
        # С валидными файлами
        test_file = temp_dir / "test.rg2"
        test_file.write_text("test")
        sample_data_info.rems.name = str(test_file)
        
        summary = validator.get_validation_summary()
        assert "валид" in summary.lower() or "valid" in summary.lower()

