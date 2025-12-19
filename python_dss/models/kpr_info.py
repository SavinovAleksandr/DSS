"""
Модель информации о контролируемой величине
"""


class KprInfo:
    """Информация о контролируемой величине для графического вывода"""
    
    def __init__(self, id: int = 0, num: int = 0, name: str = "", 
                 table: str = "", selection: str = "", col: str = ""):
        self.id = id
        self.num = num
        self.name = name
        self.table = table
        self.selection = selection
        self.col = col
    
    def __str__(self) -> str:
        return self.name

