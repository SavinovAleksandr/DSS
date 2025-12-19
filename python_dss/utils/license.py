"""
Модуль проверки лицензии
"""

import os
from pathlib import Path
from .exceptions import UserLicenseException


def check_license() -> bool:
    """
    Проверка лицензии программы
    
    Returns:
        bool: True если лицензия валидна
        
    Raises:
        UserLicenseException: Если файл лицензии не найден или неверен
    """
    machine_name = os.environ.get('COMPUTERNAME', '') or os.environ.get('HOSTNAME', '')
    
    # Путь к файлу лицензии (Windows)
    license_path = Path("C:/ПАРУС 6/licence.txt")
    
    if not license_path.exists():
        raise UserLicenseException("Файл лицензии не обнаружен")
    
    # Разделение имени машины на части
    length = len(machine_name)
    num = length // 3
    num2 = length - 2 * num
    
    text = machine_name[:num]  # Первая часть
    text2 = machine_name[num:num + num]  # Вторая часть
    
    # Обработка дефисов
    if text2 and text2[0] == "-":
        text += "-"
        text2 = text2.replace("-", "")
    
    text3 = machine_name[length - num2:]  # Третья часть
    
    if text3 and text3[0] == "-":
        text2 += "-"
        text3 = text3.replace("-", "")
    
    # Чтение файла лицензии
    try:
        with open(license_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if len(lines) < 53:
            raise UserLicenseException("Некорректный файл лицензии")
        
        # Проверка соответствия
        check1 = text in lines[43] if len(lines) > 43 else False
        check2 = text2 in lines[45] if len(lines) > 45 else False
        check3 = text3 in lines[46] if len(lines) > 46 else False
        check4 = "p5" in lines[52] if len(lines) > 52 else False
        
        if check1 and check2 and check3 and check4:
            return True
        else:
            raise UserLicenseException("Некорректный файл лицензии")
            
    except Exception as e:
        if isinstance(e, UserLicenseException):
            raise
        raise UserLicenseException(f"Ошибка при чтении файла лицензии: {str(e)}")

