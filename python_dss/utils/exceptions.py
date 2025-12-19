"""
Исключения для StabLimit
"""


class InitialDataException(Exception):
    """Исключение при отсутствии необходимых исходных данных"""
    pass


class UserLicenseException(Exception):
    """Исключение при проблемах с лицензией"""
    pass


class UncorrectFileException(Exception):
    """Исключение при некорректном формате файла"""
    pass

