"""
Модель результата расчета шунта КЗ
"""


class ShuntKZResult:
    """Результат расчета шунта короткого замыкания"""
    
    def __init__(self, r: float = -1.0, x: float = 0.0, u: float = 0.0):
        self.r = r
        self.x = x
        self.u = u
    
    def __str__(self) -> str:
        return f"R={self.r:.3f} Ом, X={self.x:.3f} Ом, U={self.u:.1f} кВ"

