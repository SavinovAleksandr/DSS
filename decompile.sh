#!/bin/bash
# Скрипт для декомпиляции DynStabSpace.exe

EXE_FILE="DynStabSpace.exe"
OUTPUT_DIR="source_code"

echo "Декомпиляция $EXE_FILE..."

# Проверка наличия файла
if [ ! -f "$EXE_FILE" ]; then
    echo "Ошибка: файл $EXE_FILE не найден!"
    exit 1
fi

# Создание директории для исходного кода
mkdir -p "$OUTPUT_DIR"

# Попытка использовать ILSpy через GUI (требует ручного вмешательства)
echo ""
echo "Для декомпиляции используйте один из следующих методов:"
echo ""
echo "Метод 1: ILSpy GUI"
echo "  1. Откройте /Applications/ILSpy.app"
echo "  2. File → Open → выберите $EXE_FILE"
echo "  3. File → Save Code → выберите папку $OUTPUT_DIR"
echo ""
echo "Метод 2: ILSpy.CommandLine (если установлен)"
echo "  ilspycmd $EXE_FILE -o $OUTPUT_DIR"
echo ""
echo "Метод 3: Установка ILSpy.CommandLine через dotnet"
echo "  dotnet tool install --global ilspycmd"
echo "  ilspycmd $EXE_FILE -o $OUTPUT_DIR"
echo ""

# Попытка найти и использовать ilspycmd
if command -v ilspycmd &> /dev/null; then
    echo "Найден ilspycmd, начинаю декомпиляцию..."
    ilspycmd "$EXE_FILE" -o "$OUTPUT_DIR"
    echo "Декомпиляция завершена!"
elif command -v dotnet &> /dev/null; then
    echo "Попытка установить ilspycmd через dotnet..."
    dotnet tool install --global ilspycmd
    if command -v ilspycmd &> /dev/null; then
        echo "Найден ilspycmd, начинаю декомпиляцию..."
        ilspycmd "$EXE_FILE" -o "$OUTPUT_DIR"
        echo "Декомпиляция завершена!"
    else
        echo "Не удалось установить ilspycmd автоматически."
        echo "Используйте ILSpy GUI для декомпиляции."
    fi
else
    echo "dotnet не найден. Используйте ILSpy GUI для декомпиляции."
fi

