"""
Модель значения контролируемой величины
"""


class Values:
    """Значение контролируемой величины"""
    
    def __init__(self, id: int = 0, name: str = "", value: float = 0.0):
        self.id = id
        self.name = name
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"

