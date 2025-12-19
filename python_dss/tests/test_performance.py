"""
Тесты для модуля оптимизации производительности
"""

import pytest
import numpy as np

from utils.performance import PerformanceOptimizer, performance_optimizer


class TestPerformanceOptimizer:
    """Тесты для PerformanceOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Создание оптимизатора"""
        return PerformanceOptimizer(max_workers=2)
    
    def test_vectorize_sum(self, optimizer):
        """Тест векторизации суммы"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = optimizer.vectorize_calculation(data, 'sum')
        
        assert result == 15.0
    
    def test_vectorize_mean(self, optimizer):
        """Тест векторизации среднего"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = optimizer.vectorize_calculation(data, 'mean')
        
        assert result == 3.0
    
    def test_vectorize_max(self, optimizer):
        """Тест векторизации максимума"""
        data = [1.0, 5.0, 3.0, 2.0, 4.0]
        result = optimizer.vectorize_calculation(data, 'max')
        
        assert result == 5.0
    
    def test_vectorize_min(self, optimizer):
        """Тест векторизации минимума"""
        data = [1.0, 5.0, 3.0, 2.0, 4.0]
        result = optimizer.vectorize_calculation(data, 'min')
        
        assert result == 1.0
    
    def test_vectorize_std(self, optimizer):
        """Тест векторизации стандартного отклонения"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = optimizer.vectorize_calculation(data, 'std')
        
        assert isinstance(result, float)
        assert result > 0
    
    def test_vectorize_empty(self, optimizer):
        """Тест векторизации пустого списка"""
        result = optimizer.vectorize_calculation([], 'sum')
        assert result == 0.0
    
    def test_vectorize_invalid_operation(self, optimizer):
        """Тест неверной операции"""
        with pytest.raises(ValueError):
            optimizer.vectorize_calculation([1, 2, 3], 'invalid')
    
    def test_batch_process(self, optimizer):
        """Тест разбиения на батчи"""
        items = list(range(25))
        batches = optimizer.batch_process(items, batch_size=10)
        
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5
    
    def test_batch_process_empty(self, optimizer):
        """Тест разбиения пустого списка"""
        batches = optimizer.batch_process([], batch_size=10)
        assert len(batches) == 0
    
    def test_parallel_map(self, optimizer):
        """Тест параллельного выполнения"""
        def square(x):
            return x * x
        
        items = [1, 2, 3, 4, 5]
        results = optimizer.parallel_map(square, items)
        
        assert len(results) == len(items)
        assert results == [1, 4, 9, 16, 25]
    
    def test_parallel_map_empty(self, optimizer):
        """Тест параллельного выполнения пустого списка"""
        results = optimizer.parallel_map(lambda x: x, [])
        assert len(results) == 0
    
    def test_parallel_map_single(self, optimizer):
        """Тест параллельного выполнения одного элемента"""
        results = optimizer.parallel_map(lambda x: x * 2, [5])
        assert results == [10]
    
    def test_optimize_array_operations(self, optimizer):
        """Тест оптимизации операций с массивами"""
        data = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
        arr = optimizer.optimize_array_operations(data)
        
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (3, 2)
        assert arr[0, 0] == 1.0
    
    def test_calculate_statistics(self, optimizer):
        """Тест расчета статистики"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = optimizer.calculate_statistics(data)
        
        assert 'mean' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'sum' in stats
        assert 'count' in stats
        
        assert stats['mean'] == 3.0
        assert stats['min'] == 1.0
        assert stats['max'] == 5.0
        assert stats['sum'] == 15.0
        assert stats['count'] == 5
    
    def test_calculate_statistics_empty(self, optimizer):
        """Тест статистики пустого списка"""
        stats = optimizer.calculate_statistics([])
        
        assert stats['mean'] == 0.0
        assert stats['std'] == 0.0
        assert stats['min'] == 0.0
        assert stats['max'] == 0.0
        assert stats['sum'] == 0.0
        assert stats['count'] == 0

