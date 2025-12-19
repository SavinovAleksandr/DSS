"""
Модель результата динамического расчета
"""


class DynamicResult:
    """Результат выполнения динамического расчета"""
    
    def __init__(self, is_success: bool = False, is_stable: bool = False,
                 result_message: str = "", time_reached: float = 0.0):
        self.is_success = is_success
        self.is_stable = is_stable
        self.result_message = result_message
        self.time_reached = time_reached
    
    def __str__(self) -> str:
        return (f"Результат: {self.result_message}\n"
                f"Рассчитанное время: {self.time_reached}\n"
                f"Успешно: {self.is_success}\n"
                f"Устойчиво: {self.is_stable}")

