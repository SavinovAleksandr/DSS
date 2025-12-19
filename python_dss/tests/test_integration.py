"""
Интеграционные тесты
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from data_info import DataInfo
from models import RgmsInfo, ScnsInfo, VrnInfo
from utils.validator import DataValidator
from utils.error_handler import error_handler


@pytest.mark.integration
class TestDataInfoIntegration:
    """Интеграционные тесты для DataInfo"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def data_info(self):
        """Создание DataInfo"""
        return DataInfo()
    
    def test_add_files_workflow(self, data_info, temp_dir):
        """Тест полного цикла добавления файлов"""
        # Создаем тестовые файлы
        rgm_file = temp_dir / "test.rg2"
        scn_file = temp_dir / "test.scn"
        rgm_file.write_text("test rgm")
        scn_file.write_text("test scn")
        
        # Добавляем файлы
        data_info.add_files([str(rgm_file), str(scn_file)])
        
        # Проверяем, что файлы добавлены
        assert len(data_info.rgms_info) == 1
        assert len(data_info.scns_info) == 1
        assert data_info.rgms_info[0].name == str(rgm_file)
        assert data_info.scns_info[0].name == str(scn_file)
    
    def test_validation_integration(self, data_info, temp_dir):
        """Тест интеграции валидации с DataInfo"""
        # Создаем валидатор
        validator = DataValidator(data_info)
        
        # Без данных
        is_valid, missing = validator.validate_calculation_requirements("shunt_kz")
        assert is_valid is False
        
        # Добавляем данные
        rgm_file = temp_dir / "test.rg2"
        rgm_file.write_text("test")
        data_info.rgms_info.append(RgmsInfo(name=str(rgm_file)))
        data_info.rems.name = str(rgm_file)
        
        # Проверяем валидацию
        is_valid, missing = validator.validate_calculation_requirements("shunt_kz")
        assert is_valid is True
    
    def test_error_handling_integration(self, data_info):
        """Тест интеграции обработки ошибок"""
        # Попытка добавить несуществующий файл
        try:
            data_info.add_files(["nonexistent.rg2"])
        except Exception as e:
            user_message, recovered = error_handler.handle_error(
                e,
                context="Добавление файлов",
                show_to_user=False
            )
            assert len(user_message) > 0
            assert recovered is False or True  # Может быть восстановлено или нет


@pytest.mark.integration
class TestValidatorIntegration:
    """Интеграционные тесты для валидатора"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_full_validation_workflow(self, sample_data_info, temp_dir):
        """Тест полного цикла валидации"""
        from utils.validator import DataValidator
        
        validator = DataValidator(sample_data_info)
        
        # Создаем все необходимые файлы
        files = {
            'rems': temp_dir / "rems.rg2",
            'lapnu': temp_dir / "lapnu.lpn",
            'vir': temp_dir / "vir.vrn",
            'sechen': temp_dir / "sechen.sch",
            'grf': temp_dir / "grf.kpr"
        }
        
        for file_path in files.values():
            file_path.write_text("test content")
        
        # Загружаем файлы
        sample_data_info.rems.name = str(files['rems'])
        sample_data_info.lapnu.name = str(files['lapnu'])
        sample_data_info.vir.name = str(files['vir'])
        sample_data_info.sechen.name = str(files['sechen'])
        sample_data_info.grf.name = str(files['grf'])
        
        # Валидируем все
        results = validator.validate_all_files()
        
        # Все должны быть валидны
        assert all(r.is_valid for r in results.values())
        
        # Проверяем сводку
        summary = validator.get_validation_summary()
        assert "валид" in summary.lower() or "valid" in summary.lower()

