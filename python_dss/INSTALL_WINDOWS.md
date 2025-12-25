# Установка StabLimit на Windows

Пошаговая инструкция по клонированию и установке программы на Windows.

## Предварительные требования

1. **Git** - для клонирования репозитория
2. **Python 3.9+** - для запуска программы
3. **RASTR** (опционально) - для выполнения расчетов (только на Windows)

## Шаг 1: Установка Git (если не установлен)

### Проверка установки Git:
```cmd
git --version
```

### Если Git не установлен:
1. Скачайте Git с официального сайта: https://git-scm.com/download/win
2. Установите с настройками по умолчанию
3. Перезапустите командную строку (CMD) или PowerShell

## Шаг 2: Установка Python (если не установлен)

### Проверка установки Python:
```cmd
python --version
```
или
```cmd
python3 --version
```

### Если Python не установлен:
1. Скачайте Python 3.9+ с официального сайта: https://www.python.org/downloads/
2. **Важно:** При установке отметьте галочку **"Add Python to PATH"**
3. Установите Python
4. Перезапустите командную строку

### Проверка pip (менеджер пакетов):
```cmd
pip --version
```

## Шаг 3: Клонирование репозитория

Откройте командную строку (CMD) или PowerShell и выполните:

```cmd
# Перейдите в нужную директорию (например, C:\Projects)
cd C:\Projects

# Клонируйте репозиторий
git clone https://github.com/SavinovAleksandr/DSS.git

# Перейдите в директорию проекта
cd DSS\python_dss
```

## Шаг 4: Установка зависимостей

```cmd
# Установите все зависимости из requirements.txt
pip install -r requirements.txt
```

**Примечание:** На Windows автоматически установится `pywin32` для работы с RASTR через COM-интерфейс.

## Шаг 5: Настройка конфигурации (опционально)

### Создание конфигурационного файла:

```cmd
# Создайте директорию для конфигурации
mkdir %USERPROFILE%\.stablimit

# Скопируйте пример конфигурации
copy config.yaml.example %USERPROFILE%\.stablimit\config.yaml
```

### Редактирование конфигурации:

Откройте файл `%USERPROFILE%\.stablimit\config.yaml` в текстовом редакторе и настройте:

- **Путь к лицензии:** `paths.license_file` (по умолчанию: `C:/ПАРУС 6/licence.txt`)
- **Директория результатов:** `paths.results_dir` (по умолчанию: `~/StabLimit`)
- **Параметры расчетов:** `calculations.*`

## Шаг 6: Отключение проверки лицензии (для тестирования)

Если нужно временно отключить проверку лицензии:

### Вариант 1: Через переменную окружения
```cmd
set STABLIMIT_DISABLE_LICENSE=true
python main.py
```

### Вариант 2: Через конфигурационный файл
Отредактируйте `%USERPROFILE%\.stablimit\config.yaml`:
```yaml
license:
  disable_check: true
```

## Шаг 7: Запуск приложения

```cmd
# Из директории python_dss
python main.py
```

## Быстрый старт (все команды подряд)

```cmd
# 1. Клонирование
cd C:\Projects
git clone https://github.com/SavinovAleksandr/DSS.git
cd DSS\python_dss

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Создание конфигурации (опционально)
mkdir %USERPROFILE%\.stablimit
copy config.yaml.example %USERPROFILE%\.stablimit\config.yaml

# 4. Запуск приложения
python main.py
```

## Проверка установки

После установки проверьте:

```cmd
# Проверка Python
python --version

# Проверка зависимостей
pip list | findstr "openpyxl customtkinter matplotlib"

# Проверка pywin32 (только на Windows)
pip list | findstr "pywin32"
```

## Решение проблем

### Проблема: "python не является внутренней или внешней командой"
**Решение:** Python не добавлен в PATH. Переустановите Python с галочкой "Add Python to PATH" или добавьте вручную.

### Проблема: "pip не является внутренней или внешней командой"
**Решение:** Используйте `python -m pip` вместо `pip`:
```cmd
python -m pip install -r requirements.txt
```

### Проблема: Ошибка при установке pywin32
**Решение:** Установите вручную:
```cmd
pip install pywin32
python Scripts\pywin32_postinstall.py -install
```

### Проблема: "RASTR недоступен"
**Решение:** Это нормально, если RASTR не установлен. Программа будет работать, но расчеты с RASTR будут недоступны.

### Проблема: Ошибка при импорте customtkinter
**Решение:** Установите вручную:
```cmd
pip install customtkinter
```

## Структура директорий после установки

```
C:\Projects\DSS\
├── python_dss\          # Основная директория программы
│   ├── main.py          # Точка входа
│   ├── requirements.txt # Зависимости
│   └── ...
├── .git\                # Git репозиторий
└── ...

%USERPROFILE%\.stablimit\  # Конфигурация пользователя
├── config.yaml          # Файл конфигурации
├── logs\                # Логи (создается автоматически)
└── cache\               # Кэш (создается автоматически)

%USERPROFILE%\StabLimit\  # Результаты расчетов
└── [дата и время]\      # Папки с результатами
```

## Обновление программы

Для получения последних изменений:

```cmd
cd C:\Projects\DSS
git pull origin main
cd python_dss
pip install -r requirements.txt --upgrade
```

## Дополнительная информация

- **Документация:** См. файлы в папке `docs/`
- **Конфигурация:** См. `docs/CONFIG_SYSTEM.md`
- **Лицензия:** См. `docs/LICENSE_GENERATION.md`
- **Кроссплатформенность:** См. `CROSSPLATFORM.md`

