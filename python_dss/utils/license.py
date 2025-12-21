"""
Модуль проверки лицензии
"""

import os
from pathlib import Path
from .exceptions import UserLicenseException
from .config import config


def check_license() -> bool:
    """
    Проверка лицензии программы
    
    Returns:
        bool: True если лицензия валидна
        
    Raises:
        UserLicenseException: Если файл лицензии не найден или неверен
    """
    # ВРЕМЕННО ОТКЛЮЧЕНО: Проверка лицензии отключена для тестирования
    # TODO: Включить проверку лицензии в продакшене
    try:
        from .logger import logger
        logger.warning("⚠️  Проверка лицензии ОТКЛЮЧЕНА (режим тестирования)")
    except:
        pass
    return True
    
    # Старый код проверки лицензии (закомментирован, но сохранен для будущего использования)
    """
    # Проверка отключения лицензии (для тестирования)
    # Можно отключить через переменную окружения или конфиг
    disable_license = os.environ.get('STABLIMIT_DISABLE_LICENSE', '').lower() == 'true'
    
    # Логирование для отладки
    try:
        from .logger import logger
        if disable_license:
            logger.info("Проверка лицензии отключена через переменную окружения STABLIMIT_DISABLE_LICENSE")
    except:
        pass
    
    if not disable_license:
        try:
            disable_license = config.get("license.disable_check", False)
            if disable_license:
                try:
                    from .logger import logger
                    logger.info("Проверка лицензии отключена через конфигурацию (license.disable_check=True)")
                except:
                    pass
        except Exception as e:
            # Если конфиг еще не загружен, используем значение по умолчанию
            try:
                from .logger import logger
                logger.warning(f"Не удалось загрузить настройку license.disable_check: {e}")
            except:
                pass
            disable_license = False
    
    if disable_license:
        try:
            from .logger import logger
            logger.warning("⚠️  Проверка лицензии ОТКЛЮЧЕНА (режим тестирования)")
        except:
            pass  # Если logger еще не инициализирован, пропускаем
        return True
    
    machine_name = os.environ.get('COMPUTERNAME', '') or os.environ.get('HOSTNAME', '')
    
    # Путь к файлу лицензии (из конфигурации)
    license_path = config.get_path("paths.license_file", expand_user=False)
    
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
    """
