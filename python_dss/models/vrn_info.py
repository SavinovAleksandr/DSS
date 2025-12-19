"""
Модель информации о варианте (ремонтной схеме)
"""


class VrnInfo:
    """Информация о варианте ремонтной схемы"""
    
    def __init__(self, id: int = -1, name: str = "", num: int = 0, deactive: bool = False):
        self.id = id
        self.name = name
        self.num = num
        self.deactive = deactive
    
    def __str__(self) -> str:
        return self.name

