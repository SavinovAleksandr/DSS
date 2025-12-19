#!/usr/bin/env python3
"""
Главный файл запуска StabLimit
"""

import sys
import os
from pathlib import Path

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent))

import os
from ui.main_window import MainWindow
try:
    from ui.modern_main_window import ModernMainWindow
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False
    ModernMainWindow = None
from utils.exceptions import UserLicenseException
from utils.logger import logger
from utils.error_handler import error_handler
from utils.config import config


def main():
    """Главная функция"""
    try:
        logger.info("Запуск StabLimit")
        logger.audit("APPLICATION_START", "Запуск приложения")
        
        # Выбор UI: проверяем переменную окружения, конфиг или используем современный UI по умолчанию
        use_modern_ui = os.getenv('DSS_USE_MODERN_UI', '').lower()
        if not use_modern_ui:
            use_modern_ui = str(config.get("ui.use_modern_ui", True)).lower()
        use_modern_ui = use_modern_ui == 'true'
        
        if use_modern_ui and MODERN_UI_AVAILABLE:
            try:
                logger.info("Использование современного UI (CustomTkinter)")
                app = ModernMainWindow()
            except Exception as e:
                logger.warning(f"Не удалось загрузить современный UI: {e}, используется классический")
                app = MainWindow()
        else:
            logger.info("Использование классического UI (tkinter)")
            app = MainWindow()
        
        app.run()
        
        logger.info("Завершение работы StabLimit")
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

