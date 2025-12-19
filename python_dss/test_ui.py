#!/usr/bin/env python3
"""
Скрипт для тестирования интерфейса StabLimit
"""

import os
import sys
from pathlib import Path

# Отключение проверки лицензии
os.environ['STABLIMIT_DISABLE_LICENSE'] = 'true'

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Тестирование интерфейса StabLimit")
print("=" * 60)
print()

try:
    print("1. Импорт модулей...")
    from ui.main_window import MainWindow
    print("   ✅ MainWindow импортирован")
    
    try:
        from ui.modern_main_window import ModernMainWindow
        print("   ✅ ModernMainWindow импортирован")
        MODERN_UI_AVAILABLE = True
    except ImportError as e:
        print(f"   ⚠️  ModernMainWindow недоступен: {e}")
        MODERN_UI_AVAILABLE = False
        ModernMainWindow = None
    
    print()
    print("2. Выбор интерфейса...")
    
    # Выбор UI
    use_modern = os.environ.get('DSS_USE_MODERN_UI', '').lower() == 'true'
    
    if use_modern and MODERN_UI_AVAILABLE:
        print("   Использование ModernMainWindow (CustomTkinter)")
        app = ModernMainWindow()
    else:
        print("   Использование MainWindow (tkinter)")
        app = MainWindow()
    
    print()
    print("=" * 60)
    print("✅ Интерфейс успешно создан!")
    print("=" * 60)
    print()
    print("Окно должно открыться. Закройте его для завершения.")
    print()
    
    # Запуск приложения
    app.run()
    
    print()
    print("✅ Тестирование завершено")
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ Ошибка при тестировании")
    print("=" * 60)
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

