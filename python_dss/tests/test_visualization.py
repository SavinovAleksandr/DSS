"""
Тесты для модуля визуализации
"""

import pytest
from pathlib import Path
import tempfile
import shutil

try:
    from visualization.plotly_visualizer import PlotlyVisualizer, PLOTLY_AVAILABLE
except ImportError:
    PLOTLY_AVAILABLE = False
    PlotlyVisualizer = None


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly не установлен")
class TestPlotlyVisualizer:
    """Тесты для PlotlyVisualizer"""
    
    @pytest.fixture
    def visualizer(self):
        """Создание визуализатора"""
        if not PLOTLY_AVAILABLE:
            pytest.skip("Plotly не установлен")
        return PlotlyVisualizer()
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_create_time_series_plot(self, visualizer, temp_dir):
        """Тест создания временного ряда"""
        data_series = [
            {'name': 'Серия 1', 'x': [0, 1, 2, 3], 'y': [1, 2, 3, 4]},
            {'name': 'Серия 2', 'x': [0, 1, 2, 3], 'y': [2, 3, 4, 5]}
        ]
        
        output_path = temp_dir / "test_plot.html"
        result = visualizer.create_time_series_plot(
            data_series=data_series,
            title="Тестовый график",
            output_path=output_path,
            interactive=True
        )
        
        assert result == str(output_path)
        assert output_path.exists()
    
    def test_create_time_series_plot_no_output(self, visualizer):
        """Тест создания графика без сохранения"""
        data_series = [
            {'name': 'Серия 1', 'x': [0, 1, 2], 'y': [1, 2, 3]}
        ]
        
        result = visualizer.create_time_series_plot(
            data_series=data_series,
            title="Тест"
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert 'html' in result.lower() or '<html' in result
    
    def test_create_comparison_plot(self, visualizer, temp_dir):
        """Тест создания графика сравнения"""
        comparison_data = {
            'Группа 1': [
                {'name': 'Серия 1', 'x': [0, 1, 2], 'y': [1, 2, 3]}
            ],
            'Группа 2': [
                {'name': 'Серия 2', 'x': [0, 1, 2], 'y': [2, 3, 4]}
            ]
        }
        
        output_path = temp_dir / "comparison.html"
        result = visualizer.create_comparison_plot(
            comparison_data=comparison_data,
            output_path=output_path
        )
        
        assert result == str(output_path)
        assert output_path.exists()
    
    def test_create_3d_plot(self, visualizer, temp_dir):
        """Тест создания 3D графика"""
        x_data = [0, 1, 2, 3]
        y_data = [0, 1, 2, 3]
        z_data = [0, 1, 4, 9]
        
        output_path = temp_dir / "3d_plot.html"
        result = visualizer.create_3d_plot(
            x_data=x_data,
            y_data=y_data,
            z_data=z_data,
            title="3D тест",
            output_path=output_path
        )
        
        assert result == str(output_path)
        assert output_path.exists()
    
    def test_create_heatmap(self, visualizer, temp_dir):
        """Тест создания тепловой карты"""
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        x_labels = ['X1', 'X2', 'X3']
        y_labels = ['Y1', 'Y2', 'Y3']
        
        output_path = temp_dir / "heatmap.html"
        result = visualizer.create_heatmap(
            data=data,
            x_labels=x_labels,
            y_labels=y_labels,
            title="Тепловая карта",
            output_path=output_path
        )
        
        assert result == str(output_path)
        assert output_path.exists()

