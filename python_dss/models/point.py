"""
Модель точки на графике
"""


class Point:
    """Точка с координатами X и Y"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

