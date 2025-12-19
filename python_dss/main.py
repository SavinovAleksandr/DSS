#!/usr/bin/env python3
"""
Главный файл запуска DynStabSpace
"""

import sys
import os
from pathlib import Path

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from utils.exceptions import UserLicenseException
from utils.logger import logger
from utils.error_handler import error_handler


def main():
    """Главная функция"""
    try:
        logger.info("Запуск DynStabSpace")
        logger.audit("APPLICATION_START", "Запуск приложения")
        
        app = MainWindow()
        app.run()
        
        logger.info("Завершение работы DynStabSpace")
        logger.audit("APPLICATION_EXIT", "Нормальное завершение работы")
        
    except UserLicenseException as e:
        user_message, _ = error_handler.handle_error(
            e,
            context="Проверка лицензии при запуске",
            show_to_user=True
        )
        logger.critical(f"Ошибка лицензии при запуске: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Прервано пользователем")
        logger.audit("APPLICATION_EXIT", "Прервано пользователем (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        user_message, _ = error_handler.handle_error(
            e,
            context="Критическая ошибка при запуске",
            show_to_user=True
        )
        logger.critical(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

