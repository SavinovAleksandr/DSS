"""
Визуализация данных с использованием Plotly
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from utils.logger import logger

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly не установлен, визуализация будет ограничена")


class PlotlyVisualizer:
    """Класс для создания интерактивных графиков с Plotly"""
    
    def __init__(self):
        """Инициализация визуализатора"""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly не установлен. Установите: pip install plotly")
        
        self.default_width = 1200
        self.default_height = 800
        self.default_template = "plotly_white"
        logger.info("Plotly визуализатор инициализирован")
    
    def create_time_series_plot(
        self,
        data_series: List[Dict[str, Any]],
        title: str = "График",
        x_label: str = "Время, с",
        y_label: str = "Значение",
        output_path: Optional[Path] = None,
        interactive: bool = True
    ) -> Optional[str]:
        """
        Создание временного ряда
        
        Args:
            data_series: Список словарей с ключами 'name', 'x', 'y'
            title: Заголовок графика
            x_label: Подпись оси X
            y_label: Подпись оси Y
            output_path: Путь для сохранения (если None, возвращает HTML)
            interactive: Сохранять как интерактивный HTML
        
        Returns:
            Путь к сохраненному файлу или HTML строка
        """
        if not PLOTLY_AVAILABLE:
            logger.error("Plotly недоступен")
            return None
        
        try:
            fig = go.Figure()
            
            # Добавляем серии данных
            for series in data_series:
                name = series.get('name', 'Серия')
                x_data = series.get('x', [])
                y_data = series.get('y', [])
                color = series.get('color', None)
                line_width = series.get('line_width', 2)
                
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines',
                    name=name,
                    line=dict(
                        width=line_width,
                        color=color
                    ),
                    hovertemplate=f'<b>{name}</b><br>' +
                                'Время: %{x:.3f} с<br>' +
                                'Значение: %{y:.3f}<extra></extra>'
                ))
            
            # Настройка осей
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=20)
                ),
                xaxis=dict(
                    title=x_label,
                    titlefont=dict(size=16),
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True
                ),
                yaxis=dict(
                    title=y_label,
                    titlefont=dict(size=16),
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True
                ),
                legend=dict(
                    x=1.02,
                    y=1,
                    bgcolor='white',
                    bordercolor='black',
                    borderwidth=1
                ),
                template=self.default_template,
                width=self.default_width,
                height=self.default_height,
                hovermode='x unified'
            )
            
            # Сохранение
            if output_path:
                if interactive:
                    output_path = Path(output_path)
                    if output_path.suffix != '.html':
                        output_path = output_path.with_suffix('.html')
                    fig.write_html(str(output_path))
                    logger.info(f"Интерактивный график сохранен: {output_path}")
                else:
                    # Статическое изображение
                    output_path = Path(output_path)
                    if output_path.suffix not in ['.png', '.jpg', '.pdf', '.svg']:
                        output_path = output_path.with_suffix('.png')
                    fig.write_image(str(output_path), width=self.default_width, height=self.default_height)
                    logger.info(f"График сохранен как изображение: {output_path}")
                return str(output_path)
            else:
                # Возвращаем HTML строку
                return fig.to_html(include_plotlyjs='cdn')
        
        except Exception as e:
            logger.error(f"Ошибка при создании графика: {e}")
            return None
    
    def create_comparison_plot(
        self,
        comparison_data: Dict[str, List[Dict[str, Any]]],
        title: str = "Сравнение результатов",
        x_label: str = "Время, с",
        y_label: str = "Значение",
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Создание графика для сравнения нескольких результатов
        
        Args:
            comparison_data: Словарь {название: список серий данных}
            title: Заголовок
            x_label: Подпись оси X
            y_label: Подпись оси Y
            output_path: Путь для сохранения
        
        Returns:
            Путь к сохраненному файлу
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            fig = make_subplots(
                rows=len(comparison_data),
                cols=1,
                subplot_titles=list(comparison_data.keys()),
                vertical_spacing=0.1
            )
            
            for idx, (group_name, series_list) in enumerate(comparison_data.items(), 1):
                for series in series_list:
                    name = series.get('name', 'Серия')
                    x_data = series.get('x', [])
                    y_data = series.get('y', [])
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_data,
                            y=y_data,
                            mode='lines',
                            name=name,
                            showlegend=(idx == 1)  # Легенда только для первого графика
                        ),
                        row=idx,
                        col=1
                    )
            
            fig.update_xaxes(title_text=x_label)
            fig.update_yaxes(title_text=y_label)
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                height=self.default_height * len(comparison_data),
                template=self.default_template
            )
            
            if output_path:
                output_path = Path(output_path)
                if output_path.suffix != '.html':
                    output_path = output_path.with_suffix('.html')
                fig.write_html(str(output_path))
                logger.info(f"График сравнения сохранен: {output_path}")
                return str(output_path)
            else:
                return fig.to_html(include_plotlyjs='cdn')
        
        except Exception as e:
            logger.error(f"Ошибка при создании графика сравнения: {e}")
            return None
    
    def create_3d_plot(
        self,
        x_data: List[float],
        y_data: List[float],
        z_data: List[float],
        title: str = "3D график",
        labels: Dict[str, str] = None,
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Создание 3D графика
        
        Args:
            x_data: Данные по оси X
            y_data: Данные по оси Y
            z_data: Данные по оси Z
            title: Заголовок
            labels: Словарь с подписями осей {'x': 'X', 'y': 'Y', 'z': 'Z'}
            output_path: Путь для сохранения
        
        Returns:
            Путь к сохраненному файлу
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            labels = labels or {'x': 'X', 'y': 'Y', 'z': 'Z'}
            
            fig = go.Figure(data=[go.Scatter3d(
                x=x_data,
                y=y_data,
                z=z_data,
                mode='lines+markers',
                marker=dict(
                    size=4,
                    color=z_data,
                    colorscale='Viridis',
                    showscale=True
                ),
                line=dict(
                    color='darkblue',
                    width=2
                )
            )])
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                scene=dict(
                    xaxis_title=labels.get('x', 'X'),
                    yaxis_title=labels.get('y', 'Y'),
                    zaxis_title=labels.get('z', 'Z'),
                    bgcolor='white'
                ),
                width=self.default_width,
                height=self.default_height,
                template=self.default_template
            )
            
            if output_path:
                output_path = Path(output_path)
                if output_path.suffix != '.html':
                    output_path = output_path.with_suffix('.html')
                fig.write_html(str(output_path))
                logger.info(f"3D график сохранен: {output_path}")
                return str(output_path)
            else:
                return fig.to_html(include_plotlyjs='cdn')
        
        except Exception as e:
            logger.error(f"Ошибка при создании 3D графика: {e}")
            return None
    
    def create_heatmap(
        self,
        data: List[List[float]],
        x_labels: List[str] = None,
        y_labels: List[str] = None,
        title: str = "Тепловая карта",
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Создание тепловой карты
        
        Args:
            data: Двумерный массив данных
            x_labels: Подписи по оси X
            y_labels: Подписи по оси Y
            title: Заголовок
            output_path: Путь для сохранения
        
        Returns:
            Путь к сохраненному файлу
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            fig = go.Figure(data=go.Heatmap(
                z=data,
                x=x_labels,
                y=y_labels,
                colorscale='Viridis',
                showscale=True
            ))
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                width=self.default_width,
                height=self.default_height,
                template=self.default_template
            )
            
            if output_path:
                output_path = Path(output_path)
                if output_path.suffix != '.html':
                    output_path = output_path.with_suffix('.html')
                fig.write_html(str(output_path))
                logger.info(f"Тепловая карта сохранена: {output_path}")
                return str(output_path)
            else:
                return fig.to_html(include_plotlyjs='cdn')
        
        except Exception as e:
            logger.error(f"Ошибка при создании тепловой карты: {e}")
            return None
    
    def save_static_image(
        self,
        html_path: Path,
        output_path: Path,
        format: str = 'png',
        width: int = None,
        height: int = None
    ) -> bool:
        """
        Сохранение интерактивного графика как статического изображения
        
        Args:
            html_path: Путь к HTML файлу
            output_path: Путь для сохранения изображения
            format: Формат ('png', 'jpg', 'pdf', 'svg')
            width: Ширина
            height: Высота
        
        Returns:
            True если успешно
        """
        try:
            import plotly.io as pio
            
            # Загружаем HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Парсим и сохраняем
            fig = pio.from_html(html_content)
            
            width = width or self.default_width
            height = height or self.default_height
            
            fig.write_image(
                str(output_path),
                format=format,
                width=width,
                height=height
            )
            
            logger.info(f"Статическое изображение сохранено: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при сохранении статического изображения: {e}")
            return False


# Глобальный экземпляр визуализатора
plotly_visualizer = PlotlyVisualizer() if PLOTLY_AVAILABLE else None

