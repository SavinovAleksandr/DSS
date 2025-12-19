"""
Тесты для моделей данных
"""

import pytest
from models import (
    RgmsInfo, ScnsInfo, VrnInfo, KprInfo, SchInfo,
    FileInfo, ShuntKZ, Point, Values
)


class TestFileInfo:
    """Тесты для FileInfo"""
    
    def test_file_info_creation(self):
        """Тест создания FileInfo"""
        file_info = FileInfo()
        assert file_info.name is None
        assert file_info.filename is None
    
    def test_file_info_with_name(self):
        """Тест FileInfo с именем"""
        file_info = FileInfo()
        file_info.name = "test.rg2"
        assert file_info.name == "test.rg2"
        assert file_info.filename == "test.rg2"


class TestRgmsInfo:
    """Тесты для RgmsInfo"""
    
    def test_rgms_info_creation(self):
        """Тест создания RgmsInfo"""
        rgm = RgmsInfo(name="test.rg2")
        assert rgm.name == "test.rg2"
        assert rgm.display_name is None
    
    def test_rgms_info_with_display_name(self):
        """Тест RgmsInfo с отображаемым именем"""
        rgm = RgmsInfo(name="test.rg2", display_name="Тестовый режим")
        assert rgm.name == "test.rg2"
        assert rgm.display_name == "Тестовый режим"


class TestVrnInfo:
    """Тесты для VrnInfo"""
    
    def test_vrn_info_creation(self):
        """Тест создания VrnInfo"""
        vrn = VrnInfo(id=1, name="Вариант 1", num=1, deactive=False)
        assert vrn.id == 1
        assert vrn.name == "Вариант 1"
        assert vrn.num == 1
        assert vrn.deactive is False
    
    def test_vrn_info_deactive(self):
        """Тест деактивированного варианта"""
        vrn = VrnInfo(id=2, name="Вариант 2", num=2, deactive=True)
        assert vrn.deactive is True


class TestPoint:
    """Тесты для Point"""
    
    def test_point_creation(self):
        """Тест создания Point"""
        point = Point(x=1.0, y=2.0)
        assert point.x == 1.0
        assert point.y == 2.0
    
    def test_point_equality(self):
        """Тест сравнения точек"""
        point1 = Point(x=1.0, y=2.0)
        point2 = Point(x=1.0, y=2.0)
        point3 = Point(x=2.0, y=3.0)
        
        assert point1.x == point2.x
        assert point1.y == point2.y
        assert point1.x != point3.x


class TestValues:
    """Тесты для Values"""
    
    def test_values_creation(self):
        """Тест создания Values"""
        values = Values(time=0.0, value=1.0)
        assert values.time == 0.0
        assert values.value == 1.0

