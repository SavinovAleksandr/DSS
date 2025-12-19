"""
Тесты для модуля обработки ошибок
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from utils.error_handler import ErrorHandler, error_handler
from utils.exceptions import (
    InitialDataException,
    UserLicenseException,
    UncorrectFileException
)


class TestErrorHandler:
    """Тесты для ErrorHandler"""
    
    @pytest.fixture
    def handler(self):
        """Создание обработчика ошибок"""
        return ErrorHandler()
    
    def test_handle_file_not_found_error(self, handler):
        """Тест обработки FileNotFoundError"""
        error = FileNotFoundError("file.rg2 not found")
        user_message, recovered = handler.handle_error(
            error,
            context="Тест",
            show_to_user=False
        )
        
        assert "файл не найден" in user_message.lower() or "file not found" in user_message.lower()
        assert recovered is False
    
    def test_handle_permission_error(self, handler):
        """Тест обработки PermissionError"""
        error = PermissionError("Access denied")
        user_message, recovered = handler.handle_error(
            error,
            context="Тест",
            show_to_user=False
        )
        
        assert "доступ" in user_message.lower() or "access" in user_message.lower()
    
    def test_handle_custom_exceptions(self, handler):
        """Тест обработки пользовательских исключений"""
        error = InitialDataException("Не все данные загружены")
        user_message, recovered = handler.handle_error(
            error,
            context="Тест",
            show_to_user=False
        )
        
        assert "исходные данные" in user_message.lower() or "данные" in user_message.lower()
    
    def test_handle_unknown_error(self, handler):
        """Тест обработки неизвестной ошибки"""
        error = ValueError("Custom error message")
        user_message, recovered = handler.handle_error(
            error,
            context="Тест",
            show_to_user=False
        )
        
        assert len(user_message) > 0
        assert "custom error message" in user_message.lower() or "некорректное значение" in user_message.lower()
    
    def test_validate_file_path_exists(self, handler, temp_dir):
        """Тест валидации существующего файла"""
        test_file = temp_dir / "test.rg2"
        test_file.write_text("test")
        
        is_valid, error_msg = handler.validate_file_path(test_file, must_exist=True)
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_file_path_not_exists(self, handler):
        """Тест валидации несуществующего файла"""
        test_file = Path("nonexistent.rg2")
        
        is_valid, error_msg = handler.validate_file_path(test_file, must_exist=True)
        assert is_valid is False
        assert error_msg is not None
        assert "не найден" in error_msg.lower() or "not found" in error_msg.lower()
    
    def test_validate_file_path_not_file(self, handler, temp_dir):
        """Тест валидации директории вместо файла"""
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        
        is_valid, error_msg = handler.validate_file_path(test_dir, must_exist=True)
        assert is_valid is False
        assert "файл" in error_msg.lower() or "file" in error_msg.lower()
    
    def test_validate_data_valid(self, handler):
        """Тест валидации валидных данных"""
        data = {
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        }
        required_fields = ['field1', 'field2']
        
        is_valid, error_msg = handler.validate_data(data, required_fields)
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_data_missing_fields(self, handler):
        """Тест валидации данных с отсутствующими полями"""
        data = {'field1': 'value1'}
        required_fields = ['field1', 'field2', 'field3']
        
        is_valid, error_msg = handler.validate_data(data, required_fields)
        assert is_valid is False
        assert "field2" in error_msg or "field3" in error_msg
    
    def test_validate_data_not_dict(self, handler):
        """Тест валидации не-словаря"""
        data = "not a dict"
        required_fields = ['field1']
        
        is_valid, error_msg = handler.validate_data(data, required_fields)
        assert is_valid is False
        assert "словар" in error_msg.lower() or "dict" in error_msg.lower()
    
    def test_error_report_saving(self, handler):
        """Тест сохранения отчета об ошибке"""
        error = ValueError("Test error")
        handler._save_error_report(error, "Test context")
        
        # Проверяем, что директория создана
        assert handler.error_reports_dir.exists()
        
        # Проверяем наличие файлов отчетов
        report_files = list(handler.error_reports_dir.glob("error_*.json"))
        assert len(report_files) > 0
        
        # Проверяем содержимое последнего отчета
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        with open(latest_report, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            assert report_data['error_type'] == 'ValueError'
            assert report_data['error_message'] == 'Test error'
            assert report_data['context'] == 'Test context'

