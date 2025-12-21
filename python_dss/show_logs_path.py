#!/usr/bin/env python3
"""
Скрипт для вывода пути к лог-файлам StabLimit
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

try:
    from utils.config import config
    from utils.logger import logger
    
    log_dir = config.get_path("paths.logs_dir")
    
    print("=" * 60)
    print("Расположение лог-файлов StabLimit")
    print("=" * 60)
    print(f"\nДиректория с логами:")
    print(f"  {log_dir}")
    print(f"\nПолный путь (Windows):")
    print(f"  {log_dir.absolute()}")
    print(f"\nФайлы логов:")
    print(f"  - {log_dir / 'stablimit.log'} (основной лог)")
    print(f"  - {log_dir / 'errors.log'} (лог ошибок)")
    print(f"  - {log_dir / 'audit.log'} (лог аудита)")
    print("\n" + "=" * 60)
    print("\nДля открытия директории в Windows:")
    print(f"  1. Нажмите Win + R")
    print(f"  2. Введите: {log_dir.absolute()}")
    print(f"  3. Нажмите Enter")
    print("\nИли скопируйте путь и вставьте в проводник:")
    print(f"  {log_dir.absolute()}")
    print("=" * 60)
    
    # Проверяем существование файлов
    print("\nПроверка существования файлов:")
    log_file = log_dir / 'stablimit.log'
    error_file = log_dir / 'errors.log'
    
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"  ✓ stablimit.log существует ({size} байт)")
    else:
        print(f"  ✗ stablimit.log не найден")
    
    if error_file.exists():
        size = error_file.stat().st_size
        print(f"  ✓ errors.log существует ({size} байт)")
    else:
        print(f"  ✗ errors.log не найден")
    
except Exception as e:
    print(f"Ошибка при получении пути к логам: {e}")
    print("\nПопробуйте стандартный путь:")
    home = Path.home()
    default_log_dir = home / '.stablimit' / 'logs'
    print(f"  {default_log_dir.absolute()}")

