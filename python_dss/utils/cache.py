"""
Система кэширования для оптимизации производительности
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps
import time

from utils.logger import logger


class CacheManager:
    """Менеджер кэша для промежуточных результатов"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if CacheManager._initialized:
            return
        
        CacheManager._initialized = True
        self.cache_dir = Path.home() / '.dynstabspace' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}  # Кэш в памяти
        self.max_memory_size = 100  # Максимальное количество элементов в памяти
        self.cache_enabled = True
        
        logger.info("Менеджер кэша инициализирован")
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Генерация ключа кэша из аргументов"""
        # Создаем строку из аргументов
        key_data = {
            'args': str(args),
            'kwargs': json.dumps(kwargs, sort_keys=True, default=str)
        }
        key_string = json.dumps(key_data, sort_keys=True)
        # Хешируем для получения короткого ключа
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Получить путь к файлу кэша"""
        return self.cache_dir / f"{key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if not self.cache_enabled:
            return None
        
        # Сначала проверяем память
        if key in self.memory_cache:
            logger.debug(f"Кэш попадание (память): {key[:8]}...")
            return self.memory_cache[key]
        
        # Затем проверяем файловый кэш
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                logger.debug(f"Кэш попадание (файл): {key[:8]}...")
                # Сохраняем в память для быстрого доступа
                self._add_to_memory(key, data)
                return data
            except Exception as e:
                logger.warning(f"Ошибка чтения кэша {key[:8]}...: {e}")
                # Удаляем поврежденный файл
                try:
                    cache_path.unlink()
                except:
                    pass
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Сохранить значение в кэш"""
        if not self.cache_enabled:
            return
        
        try:
            # Сохраняем в память
            self._add_to_memory(key, value)
            
            # Сохраняем в файл
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            logger.debug(f"Значение сохранено в кэш: {key[:8]}...")
        except Exception as e:
            logger.warning(f"Ошибка сохранения в кэш: {e}")
    
    def _add_to_memory(self, key: str, value: Any):
        """Добавить значение в кэш памяти"""
        # Если кэш переполнен, удаляем старые элементы
        if len(self.memory_cache) >= self.max_memory_size:
            # Удаляем первый элемент (FIFO)
            first_key = next(iter(self.memory_cache))
            del self.memory_cache[first_key]
        
        self.memory_cache[key] = value
    
    def clear(self, pattern: Optional[str] = None):
        """Очистить кэш"""
        if pattern:
            # Очистка по паттерну
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
            logger.info(f"Очищен кэш по паттерну: {pattern}")
        else:
            # Полная очистка
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Не удалось удалить {cache_file}: {e}")
            logger.info("Кэш полностью очищен")
    
    def get_stats(self) -> dict:
        """Получить статистику кэша"""
        memory_size = len(self.memory_cache)
        file_count = len(list(self.cache_dir.glob("*.cache")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))
        
        return {
            'memory_items': memory_size,
            'file_items': file_count,
            'total_size_mb': total_size / (1024 * 1024),
            'enabled': self.cache_enabled
        }


# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()


def cached(func: Callable) -> Callable:
    """Декоратор для кэширования результатов функции"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Генерируем ключ кэша
        cache_key = f"{func.__module__}.{func.__name__}.{cache_manager._get_cache_key(*args, **kwargs)}"
        
        # Пытаемся получить из кэша
        cached_value = cache_manager.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        # Выполняем функцию
        result = func(*args, **kwargs)
        
        # Сохраняем в кэш
        cache_manager.set(cache_key, result)
        
        return result
    
    return wrapper


def timed(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.debug(f"{func.__name__} выполнен за {elapsed:.3f} сек")
        return result
    
    return wrapper

