"""
Модель информации о сечении
"""


class SchInfo:
    """Информация о контролируемом сечении"""
    
    def __init__(self, id: int = 0, num: int = 0, name: str = "", control: bool = False):
        self.id = id
        self.num = num
        self.name = name
        self.control = control
    
    def __str__(self) -> str:
        return self.name

