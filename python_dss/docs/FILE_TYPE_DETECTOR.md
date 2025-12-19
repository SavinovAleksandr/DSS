# FileTypeDetector - Определение типов файлов

## Обзор

Реализован единый класс `FileTypeDetector` для определения типов файлов по расширению. Это упростило код и убрало дублирование логики определения типов файлов.

## Преимущества

1. **Единая точка определения** - все типы файлов определяются в одном месте
2. **Упрощение кода** - `data_info.py` стал более читаемым (разбит на отдельные методы)
3. **Легкое расширение** - добавление новых типов файлов требует изменения только одного класса
4. **Консистентность** - одинаковое определение типов во всех модулях

## Использование

### Базовое определение типа

```python
from utils.file_type_detector import FileTypeDetector

file_type = FileTypeDetector.detect("file.rg2")
# Возвращает: 'rems'
```

### Проверка расширения

```python
is_valid = FileTypeDetector.is_valid_extension("file.rg2", "rems")
# Возвращает: True
```

### Получение расширений для типа

```python
extensions = FileTypeDetector.get_extensions("rems")
# Возвращает: ['.rg2', '.rst']
```

### Получение человекочитаемого имени

```python
name = FileTypeDetector.get_file_type_name("rems")
# Возвращает: 'Расчетный режим'
```

## Поддерживаемые типы файлов

| Тип | Расширения | Описание |
|-----|------------|----------|
| `rems` | `.rg2`, `.rst` | Расчетный режим |
| `scenario` | `.scn` | Аварийный процесс |
| `vir` | `.ut2` | Траектория утяжеления |
| `sechen` | `.sch` | Файл сечений |
| `rems_vrn` | `.vrn` | Ремонтные схемы |
| `grf` | `.kpr` | Графический вывод |
| `shunt_kz` | `.csv` | Файл задания для шунтов КЗ |
| `lapnu` | `.dwf`, `.lpn` | Файл ПА |

## Рефакторинг data_info.py

Метод `add_files()` был рефакторен:

**До:**
- Большой if-elif блок (120+ строк)
- Дублирование логики определения типов
- Сложно поддерживать

**После:**
- Использование `FileTypeDetector.detect()`
- Разделение на отдельные методы обработки:
  - `_handle_rems_file()`
  - `_handle_scenario_file()`
  - `_handle_vir_file()`
  - `_handle_sechen_file()`
  - `_handle_rems_vrn_file()`
  - `_handle_grf_file()`
  - `_handle_shunt_kz_file()`
  - `_handle_lapnu_file()`

## Обновленные модули

1. ✅ `utils/file_type_detector.py` - новый модуль
2. ✅ `data_info.py` - рефакторинг метода `add_files()`
3. ✅ `utils/validator.py` - использование `FileTypeDetector` вместо `FILE_EXTENSIONS`
4. ✅ `utils/__init__.py` - экспорт `FileTypeDetector`

## Пример использования в коде

```python
# В data_info.py
file_type = FileTypeDetector.detect(file_path)

if file_type == 'rems':
    self._handle_rems_file(file_path)
elif file_type == 'scenario':
    self._handle_scenario_file(file_path)
# ...

# В validator.py
expected_extensions = FileTypeDetector.get_extensions(file_type)
if not FileTypeDetector.is_valid_extension(file_path, file_type):
    # Обработка ошибки
    pass
```

## Расширение функциональности

Для добавления нового типа файла:

1. Добавить в `FILE_TYPES`:
```python
'.new_ext': 'new_type',
```

2. Добавить в `TYPE_EXTENSIONS`:
```python
'new_type': ['.new_ext'],
```

3. Добавить имя в `get_file_type_name()`:
```python
'new_type': 'Новое имя типа',
```

4. Добавить метод обработки в `data_info.py`:
```python
def _handle_new_type_file(self, file_path: str):
    # Обработка файла
    pass
```

## Примечания

- Все методы класса статические - не требуется создание экземпляра
- Типы файлов определяются только по расширению
- Регистр расширения не важен (автоматически приводится к нижнему)

