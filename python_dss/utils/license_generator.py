#!/usr/bin/env python3
"""
Утилита для генерации файлов лицензии StabLimit
"""

import os
import sys
from pathlib import Path
from typing import Optional


def split_machine_name(machine_name: str) -> tuple[str, str, str]:
    """
    Разделение имени машины на части (аналогично проверке лицензии)
    
    Args:
        machine_name: Имя компьютера
        
    Returns:
        Кортеж из трех частей: (text, text2, text3)
    """
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
    
    return text, text2, text3


def generate_license_file(
    machine_name: str,
    output_path: Path,
    license_text: Optional[str] = None
) -> bool:
    """
    Генерация файла лицензии
    
    Args:
        machine_name: Имя компьютера
        output_path: Путь для сохранения файла лицензии
        license_text: Опциональный текст для заполнения файла (если None, используется шаблон)
        
    Returns:
        True если файл успешно создан
    """
    # Разделение имени на части
    text, text2, text3 = split_machine_name(machine_name)
    
    print(f"Имя компьютера: {machine_name}")
    print(f"Часть 1 (строка 43): '{text}'")
    print(f"Часть 2 (строка 45): '{text2}'")
    print(f"Часть 3 (строка 46): '{text3}'")
    print(f"Маркер (строка 52): 'p5'")
    print()
    
    # Создание содержимого файла
    lines = []
    
    if license_text:
        # Использование предоставленного текста
        lines = license_text.split('\n')
        # Дополнение до 53 строк, если нужно
        while len(lines) < 53:
            lines.append("")
    else:
        # Генерация шаблона
        for i in range(53):
            if i == 43:
                # Строка 43: первая часть имени
                lines.append(f"License information: {text} - Part 1 of machine name")
            elif i == 45:
                # Строка 45: вторая часть имени
                lines.append(f"License information: {text2} - Part 2 of machine name")
            elif i == 46:
                # Строка 46: третья часть имени
                lines.append(f"License information: {text3} - Part 3 of machine name")
            elif i == 52:
                # Строка 52: маркер "p5"
                lines.append(f"License key: p5 - StabLimit License")
            else:
                # Остальные строки
                lines.append(f"License line {i + 1}")
    
    # Запись файла
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Файл лицензии успешно создан: {output_path}")
        print(f"   Всего строк: {len(lines)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return False


def main():
    """Главная функция утилиты"""
    print("=" * 60)
    print("Генератор лицензий StabLimit")
    print("=" * 60)
    print()
    
    # Определение имени компьютера
    machine_name = os.environ.get('COMPUTERNAME', '') or os.environ.get('HOSTNAME', '')
    
    if not machine_name:
        print("❌ Не удалось определить имя компьютера")
        print("   Укажите имя компьютера вручную:")
        machine_name = input("Имя компьютера: ").strip()
        if not machine_name:
            print("❌ Имя компьютера не может быть пустым")
            sys.exit(1)
    
    # Путь для сохранения
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        # Путь по умолчанию (из конфига)
        default_path = Path("C:/ПАРУС 6/licence.txt")
        print(f"Путь по умолчанию: {default_path}")
        print("Использовать путь по умолчанию? (y/n): ", end='')
        use_default = input().strip().lower()
        
        if use_default == 'y':
            output_path = default_path
        else:
            output_path_str = input("Введите путь к файлу лицензии: ").strip()
            if not output_path_str:
                print("❌ Путь не может быть пустым")
                sys.exit(1)
            output_path = Path(output_path_str)
    
    # Проверка существования файла
    if output_path.exists():
        print(f"⚠️  Файл уже существует: {output_path}")
        print("Перезаписать? (y/n): ", end='')
        overwrite = input().strip().lower()
        if overwrite != 'y':
            print("Отменено")
            sys.exit(0)
    
    # Генерация файла
    print()
    success = generate_license_file(machine_name, output_path)
    
    if success:
        print()
        print("=" * 60)
        print("✅ Лицензия успешно создана!")
        print("=" * 60)
        print()
        print("Проверка лицензии:")
        print(f"  - Файл: {output_path}")
        print(f"  - Имя компьютера: {machine_name}")
        print()
        print("Теперь программа должна работать с этой лицензией.")
    else:
        print()
        print("=" * 60)
        print("❌ Ошибка при создании лицензии")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

