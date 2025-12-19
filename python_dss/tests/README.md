# Тесты для DynStabSpace

## Структура тестов

```
tests/
├── __init__.py              # Инициализация пакета тестов
├── conftest.py              # Конфигурация и фикстуры
├── test_validator.py        # Тесты валидации
├── test_error_handler.py    # Тесты обработки ошибок
├── test_cache.py            # Тесты кэширования
├── test_performance.py       # Тесты оптимизации производительности
├── test_visualization.py    # Тесты визуализации
├── test_models.py           # Тесты моделей данных
└── test_integration.py      # Интеграционные тесты
```

## Запуск тестов

### Все тесты
```bash
cd python_dss
pytest tests/ -v
```

### Конкретный файл
```bash
pytest tests/test_validator.py -v
```

### С покрытием кода
```bash
pytest tests/ --cov=. --cov-report=html
```

### Только unit-тесты
```bash
pytest tests/ -m unit -v
```

### Только integration-тесты
```bash
pytest tests/ -m integration -v
```

## Типы тестов

### Unit-тесты
- Тестируют отдельные модули и функции
- Быстрые и изолированные
- Не требуют внешних зависимостей

### Integration-тесты
- Тестируют взаимодействие компонентов
- Могут быть медленнее
- Используют mock-объекты для внешних зависимостей

## Маркеры

- `@pytest.mark.unit` - Unit-тесты
- `@pytest.mark.integration` - Integration-тесты
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.requires_rastr` - Требуют RASTR
- `@pytest.mark.requires_windows` - Требуют Windows
- `@pytest.mark.skip_if_no_plotly` - Пропустить если Plotly не установлен

## CI/CD

Тесты автоматически запускаются при каждом push через GitHub Actions:
- На разных ОС (Ubuntu, Windows, macOS)
- На разных версиях Python (3.8-3.11)
- С генерацией отчетов о покрытии

## Покрытие кода

Цель: >80% покрытия кода тестами

Текущее покрытие можно проверить:
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

