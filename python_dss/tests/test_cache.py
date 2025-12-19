"""
Тесты для модуля кэширования
"""

import pytest
import time
from pathlib import Path

from utils.cache import CacheManager, cache_manager, cached, timed


class TestCacheManager:
    """Тесты для CacheManager"""
    
    @pytest.fixture
    def cache(self):
        """Создание менеджера кэша"""
        manager = CacheManager()
        manager.clear()  # Очищаем перед тестом
        return manager
    
    def test_cache_set_get(self, cache):
        """Тест сохранения и получения из кэша"""
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        
        assert value == "test_value"
    
    def test_cache_memory_first(self, cache):
        """Тест приоритета кэша в памяти"""
        cache.set("test_key", "test_value")
        
        # Значение должно быть в памяти
        assert "test_key" in cache.memory_cache
        assert cache.memory_cache["test_key"] == "test_value"
    
    def test_cache_file_persistence(self, cache):
        """Тест персистентности файлового кэша"""
        cache.set("test_key", "test_value")
        
        # Создаем новый экземпляр (симуляция перезапуска)
        new_cache = CacheManager()
        value = new_cache.get("test_key")
        
        # Должно загрузиться из файла
        assert value == "test_value"
    
    def test_cache_clear(self, cache):
        """Тест очистки кэша"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.memory_cache) > 0
        
        cache.clear()
        
        assert len(cache.memory_cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_clear_pattern(self, cache):
        """Тест очистки кэша по паттерну"""
        cache.set("test_key1", "value1")
        cache.set("test_key2", "value2")
        cache.set("other_key", "value3")
        
        cache.clear(pattern="test_")
        
        assert cache.get("test_key1") is None
        assert cache.get("test_key2") is None
        assert cache.get("other_key") == "value3"  # Не должно быть удалено
    
    def test_cache_disabled(self, cache):
        """Тест отключенного кэша"""
        cache.cache_enabled = False
        
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        
        assert value is None
    
    def test_cache_stats(self, cache):
        """Тест статистики кэша"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        
        assert 'memory_items' in stats
        assert 'file_items' in stats
        assert 'total_size_mb' in stats
        assert 'enabled' in stats
        assert stats['memory_items'] >= 0
        assert stats['enabled'] is True


class TestCacheDecorator:
    """Тесты для декоратора @cached"""
    
    call_count = 0
    
    @cached
    def cached_function(self, arg1, arg2):
        """Тестовая функция с кэшированием"""
        TestCacheDecorator.call_count += 1
        return arg1 + arg2
    
    def test_cached_decorator(self):
        """Тест декоратора кэширования"""
        TestCacheDecorator.call_count = 0
        
        # Первый вызов - должно выполниться
        result1 = self.cached_function(1, 2)
        assert result1 == 3
        assert TestCacheDecorator.call_count == 1
        
        # Второй вызов с теми же аргументами - должно быть из кэша
        result2 = self.cached_function(1, 2)
        assert result2 == 3
        assert TestCacheDecorator.call_count == 1  # Не должно увеличиться
        
        # Третий вызов с другими аргументами - должно выполниться
        result3 = self.cached_function(2, 3)
        assert result3 == 5
        assert TestCacheDecorator.call_count == 2


class TestTimedDecorator:
    """Тесты для декоратора @timed"""
    
    @timed
    def timed_function(self, delay=0.1):
        """Тестовая функция с измерением времени"""
        import time
        time.sleep(delay)
        return "done"
    
    def test_timed_decorator(self):
        """Тест декоратора измерения времени"""
        result = self.timed_function(0.01)
        assert result == "done"
        # Декоратор должен логировать время выполнения

