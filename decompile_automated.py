#!/usr/bin/env python3
"""
Автоматическая декомпиляция .NET приложения с использованием ICSharpCode.Decompiler
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Пути к ILSpy
ILSPY_PATH = "/Applications/ILSpy.app/Contents/MacOS"
# Проверка реального пути
if os.path.exists(os.path.join(ILSPY_PATH, "ICSharpCode.Decompiler.dll")):
    DECOMPILER_DLL = os.path.join(ILSPY_PATH, "ICSharpCode.Decompiler.dll")
else:
    # Альтернативный путь
    DECOMPILER_DLL = None
ILSPY_CORE_DLL = os.path.join(ILSPY_PATH, "ILSpy.Core.dll")

# Целевой файл и выходная папка
TARGET_EXE = "DynStabSpace.exe"
OUTPUT_DIR = "source_code"

def check_files():
    """Проверка наличия необходимых файлов"""
    if not os.path.exists(TARGET_EXE):
        print(f"❌ Ошибка: файл {TARGET_EXE} не найден!")
        return False
    
    if DECOMPILER_DLL and not os.path.exists(DECOMPILER_DLL):
        print(f"⚠️  Библиотека декомпилятора не найдена, будет использован альтернативный метод")
        # Не критично, продолжим
    
    print("✅ Все необходимые файлы найдены")
    return True

def create_csharp_decompiler_script():
    """Создание C# скрипта для декомпиляции"""
    script = """
using System;
using System.IO;
using System.Linq;
using ICSharpCode.Decompiler;
using ICSharpCode.Decompiler.CSharp;
using ICSharpCode.Decompiler.Metadata;
using ICSharpCode.Decompiler.Solution;

class Program
{
    static void Main(string[] args)
    {
        string assemblyPath = args[0];
        string outputPath = args[1];
        
        Console.WriteLine($"Декомпиляция: {assemblyPath}");
        Console.WriteLine($"Выходная папка: {outputPath}");
        
        if (!File.Exists(assemblyPath))
        {
            Console.WriteLine($"Ошибка: файл не найден: {assemblyPath}");
            Environment.Exit(1);
        }
        
        Directory.CreateDirectory(outputPath);
        
        var decompiler = new CSharpDecompiler(assemblyPath, new DecompilerSettings());
        var projectFile = new ProjectInfo();
        
        try
        {
            var project = projectFile.CreateProject(assemblyPath, outputPath);
            project.AddAssembly(assemblyPath);
            
            var solution = new SolutionInfo();
            solution.AddProject(project);
            
            solution.Save(outputPath);
            
            Console.WriteLine("✅ Декомпиляция завершена успешно!");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Ошибка декомпиляции: {ex.Message}");
            Environment.Exit(1);
        }
    }
}
"""
    return script

def try_dotnet_decompile():
    """Попытка использовать dotnet для декомпиляции"""
    print("Попытка использовать dotnet для декомпиляции...")
    
    # Проверка наличия dotnet
    try:
        result = subprocess.run(["dotnet", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Найден dotnet версии: {result.stdout.strip()}")
            
            # Попытка установить ilspycmd
            print("Установка ilspycmd...")
            install_result = subprocess.run(
                ["dotnet", "tool", "install", "--global", "ilspycmd"],
                capture_output=True, text=True, timeout=60
            )
            
            if install_result.returncode == 0:
                print("✅ ilspycmd установлен")
                
                # Выполнение декомпиляции
                print(f"Декомпиляция {TARGET_EXE}...")
                decompile_result = subprocess.run(
                    ["ilspycmd", TARGET_EXE, "-o", OUTPUT_DIR, "--project-file"],
                    capture_output=True, text=True, timeout=300
                )
                
                if decompile_result.returncode == 0:
                    print("✅ Декомпиляция завершена успешно!")
                    print(decompile_result.stdout)
                    return True
                else:
                    print(f"❌ Ошибка декомпиляции: {decompile_result.stderr}")
            else:
                print(f"❌ Не удалось установить ilspycmd: {install_result.stderr}")
        else:
            print("❌ dotnet не найден")
    except FileNotFoundError:
        print("❌ dotnet не установлен")
    except subprocess.TimeoutExpired:
        print("❌ Превышено время ожидания")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    return False

def create_manual_instructions():
    """Создание инструкций для ручной декомпиляции"""
    instructions = f"""
╔══════════════════════════════════════════════════════════════╗
║  ИНСТРУКЦИЯ ПО РУЧНОЙ ДЕКОМПИЛЯЦИИ                          ║
╚══════════════════════════════════════════════════════════════╝

Для декомпиляции {TARGET_EXE} выполните следующие шаги:

1. ОТКРОЙТЕ ILSpy:
   open /Applications/ILSpy.app

2. ОТКРОЙТЕ ФАЙЛ:
   - В меню: File → Open
   - Или нажмите: Cmd+O
   - Выберите файл: {os.path.abspath(TARGET_EXE)}

3. СОХРАНИТЕ КОД:
   - В меню: File → Save Code...
   - Или нажмите: Cmd+Shift+S
   - Выберите папку: {os.path.abspath(OUTPUT_DIR)}
   - Нажмите: Save

4. ПРОВЕРЬТЕ РЕЗУЛЬТАТ:
   ls -la {OUTPUT_DIR}/

АЛЬТЕРНАТИВНЫЙ МЕТОД (если установлен dotnet):

1. Установите ilspycmd:
   dotnet tool install --global ilspycmd

2. Выполните декомпиляцию:
   ilspycmd {TARGET_EXE} -o {OUTPUT_DIR} --project-file

═══════════════════════════════════════════════════════════════
"""
    return instructions

def main():
    """Главная функция"""
    print("=" * 60)
    print("АВТОМАТИЧЕСКАЯ ДЕКОМПИЛЯЦИЯ DynStabSpace.exe")
    print("=" * 60)
    print()
    
    # Проверка файлов
    if not check_files():
        sys.exit(1)
    
    # Создание выходной папки
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Создана папка: {OUTPUT_DIR}")
    print()
    
    # Попытка автоматической декомпиляции
    print("🔍 Попытка автоматической декомпиляции...")
    print()
    
    if try_dotnet_decompile():
        print()
        print("=" * 60)
        print("✅ ДЕКОМПИЛЯЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        return
    
    # Если автоматическая декомпиляция не удалась
    print()
    print("=" * 60)
    print("⚠️  АВТОМАТИЧЕСКАЯ ДЕКОМПИЛЯЦИЯ НЕВОЗМОЖНА")
    print("=" * 60)
    print()
    print(create_manual_instructions())
    
    # Сохранение инструкций в файл
    instructions_file = "DECOMPILE_INSTRUCTIONS.txt"
    with open(instructions_file, "w", encoding="utf-8") as f:
        f.write(create_manual_instructions())
    print(f"📄 Инструкции сохранены в: {instructions_file}")
    print()

if __name__ == "__main__":
    main()

