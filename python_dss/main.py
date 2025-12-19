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


def main():
    """Главная функция"""
    try:
        app = MainWindow()
        app.run()
    except UserLicenseException as e:
        print(f"Ошибка лицензии: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

