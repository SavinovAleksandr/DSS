"""
Утилиты для оптимизации производительности
"""

import numpy as np
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import partial
import threading

from utils.logger import logger


class PerformanceOptimizer:
    """Класс для оптимизации производительности расчетов"""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Инициализация оптимизатора
        
        Args:
            max_workers: Максимальное количество потоков/процессов
        """
        self.max_workers = max_workers or min(4, (threading.active_count() or 1) + 4)
        logger.info(f"Оптимизатор производительности инициализирован (workers: {self.max_workers})")
    
    @staticmethod
    def vectorize_calculation(data: List[float], operation: str = 'sum') -> float:
        """
        Векторизация вычислений с использованием NumPy
        
        Args:
            data: Список чисел
            operation: Операция ('sum', 'mean', 'max', 'min', 'std')
        
        Returns:
            Результат операции
        """
        if not data:
            return 0.0
        
        arr = np.array(data, dtype=np.float64)
        
        operations = {
            'sum': np.sum,
            'mean': np.mean,
            'max': np.max,
            'min': np.min,
            'std': np.std,
        }
        
        if operation in operations:
            return float(operations[operation](arr))
        else:
            raise ValueError(f"Неизвестная операция: {operation}")
    
    @staticmethod
    def batch_process(items: List, batch_size: int = 10) -> List:
        """
        Разбить список на батчи для обработки
        
        Args:
            items: Список элементов
            batch_size: Размер батча
        
        Returns:
            Список батчей
        """
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    def parallel_map(self, func: callable, items: List, use_processes: bool = False) -> List:
        """
        Параллельное выполнение функции для списка элементов
        
        Args:
            func: Функция для выполнения
            items: Список элементов
            use_processes: Использовать процессы вместо потоков
        
        Returns:
            Список результатов
        """
        if not items:
            return []
        
        if len(items) == 1:
            return [func(items[0])]
        
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        results = []
        
        try:
            with executor_class(max_workers=self.max_workers) as executor:
                # Отправляем задачи
                future_to_item = {executor.submit(func, item): item for item in items}
                
                # Собираем результаты по мере выполнения
                for future in as_completed(future_to_item):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        item = future_to_item[future]
                        logger.error(f"Ошибка при обработке элемента {item}: {e}")
                        results.append(None)
        except Exception as e:
            logger.error(f"Ошибка при параллельном выполнении: {e}")
            # Fallback на последовательное выполнение
            results = [func(item) for item in items]
        
        return results
    
    def parallel_calc(self, calc_func: callable, calc_params: List[dict], 
                     progress_callback: Optional[callable] = None) -> List:
        """
        Параллельное выполнение расчетов
        
        Args:
            calc_func: Функция расчета
            calc_params: Список параметров для каждого расчета
            progress_callback: Функция обратного вызова для прогресса
        
        Returns:
            Список результатов
        """
        if not calc_params:
            return []
        
        if len(calc_params) == 1:
            result = calc_func(**calc_params[0])
            if progress_callback:
                progress_callback(1)
            return [result]
        
        results = []
        completed = 0
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Создаем частично примененные функции
                futures = []
                for params in calc_params:
                    future = executor.submit(calc_func, **params)
                    futures.append(future)
                
                # Собираем результаты
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        completed += 1
                        if progress_callback:
                            progress_callback(completed)
                    except Exception as e:
                        logger.error(f"Ошибка при расчете: {e}")
                        results.append(None)
                        completed += 1
                        if progress_callback:
                            progress_callback(completed)
        except Exception as e:
            logger.error(f"Ошибка при параллельном расчете: {e}")
            # Fallback на последовательное выполнение
            for params in calc_params:
                try:
                    result = calc_func(**params)
                    results.append(result)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed)
                except Exception as e:
                    logger.error(f"Ошибка при расчете: {e}")
                    results.append(None)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed)
        
        return results
    
    @staticmethod
    def optimize_array_operations(data: List[List[float]]) -> np.ndarray:
        """
        Оптимизация операций с массивами через NumPy
        
        Args:
            data: Список списков чисел
        
        Returns:
            NumPy массив
        """
        return np.array(data, dtype=np.float64)
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> dict:
        """
        Быстрый расчет статистики через NumPy
        
        Args:
            data: Список чисел
        
        Returns:
            Словарь со статистикой
        """
        if not data:
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'sum': 0.0
            }
        
        arr = np.array(data, dtype=np.float64)
        
        return {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'sum': float(np.sum(arr)),
            'count': len(data)
        }


# Глобальный экземпляр оптимизатора
performance_optimizer = PerformanceOptimizer()

