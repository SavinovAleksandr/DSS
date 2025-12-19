"""
Конфигурация pytest и общие фикстуры
"""

import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Создание временной директории для тестов"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_file(temp_dir):
    """Создание тестового файла"""
    file_path = temp_dir / "test_file.rg2"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def sample_data_info():
    """Создание тестового DataInfo"""
    from data_info import DataInfo
    return DataInfo()

