# Система конфигурации

## Обзор

Реализована централизованная система управления конфигурацией приложения. Все настройки теперь хранятся в конфигурационном файле, что упрощает изменение параметров без правки кода.

## Расположение конфигурации

Конфигурация хранится в:
- **JSON**: `~/.stablimit/config.json` (основной формат)
- **YAML**: `~/.stablimit/config.yaml` (опционально, если установлен PyYAML)

При первом запуске автоматически создается файл конфигурации с настройками по умолчанию.

## Структура конфигурации

```yaml
paths:
  license_file: "C:/ПАРУС 6/licence.txt"
  results_dir: "~/StabLimit"
  logs_dir: "~/.stablimit/logs"
  cache_dir: "~/.stablimit/cache"
  error_reports_dir: "~/.stablimit/error_reports"
  rastr_template_dir: "~/RastrWIN3/SHABLON"

calculations:
  base_angle: 1.471
  crt_time_precision: 0.02
  crt_time_max: 1.0
  default_selected_sch: 0

settings:
  use_type_val_u: true
  use_sel_nodes: true
  calc_one_phase: true
  calc_two_phase: true
  dyn_no_pa: true
  dyn_with_pa: false
  save_grf: false
  use_lpn: false
  lpns: ""

ui:
  theme: "system"
  window_size: [900, 750]
  min_window_size: [800, 600]
  use_modern_ui: true

logging:
  max_bytes: 10485760  # 10 MB
  backup_count: 5
  error_log_max_bytes: 5242880  # 5 MB
  error_log_backup_count: 3

performance:
  max_workers: null  # null = автоматически
  cache_enabled: true
  cache_ttl: 3600  # 1 час
```

## Использование в коде

### Базовое использование

```python
from utils.config import config

# Получить значение
results_dir = config.get("paths.results_dir")
theme = config.get("ui.theme", "system")  # с значением по умолчанию

# Получить путь как Path объект
results_path = config.get_path("paths.results_dir")

# Установить значение
config.set("ui.theme", "dark", save=True)

# Перезагрузить конфигурацию
config.reload()

# Сохранить изменения
config.save()
```

### Примеры использования

```python
# В data_info.py
from utils.config import config

self.tmp_root = config.get_path("paths.results_dir")
self.base_angle = config.get("calculations.base_angle", 1.471)

# В license.py
license_path = config.get_path("paths.license_file", expand_user=False)

# В logger.py
log_dir = config.get_path("paths.logs_dir")
max_bytes = config.get("logging.max_bytes", 10 * 1024 * 1024)
```

## Миграция из хардкода

Все следующие настройки были мигрированы в конфигурацию:

### Пути
- ✅ `Path.home() / "StabLimit"` → `config.get_path("paths.results_dir")`
- ✅ `Path.home() / '.stablimit' / 'logs'` → `config.get_path("paths.logs_dir")`
- ✅ `"C:/ПАРУС 6/licence.txt"` → `config.get_path("paths.license_file")`
- ✅ Пути к кэшу, отчетам об ошибках, шаблонам RASTR

### Настройки расчетов
- ✅ `base_angle = 1.471` → `config.get("calculations.base_angle")`
- ✅ `crt_time_precision = 0.02` → `config.get("calculations.crt_time_precision")`
- ✅ Все настройки из `data_info.py`

### UI настройки
- ✅ `use_modern_ui` → `config.get("ui.use_modern_ui")`
- ✅ Размеры окон

### Логирование
- ✅ Размеры лог-файлов
- ✅ Количество резервных копий

## Обновленные модули

Следующие модули были обновлены для использования конфигурации:

1. ✅ `utils/config.py` - новый модуль конфигурации
2. ✅ `data_info.py` - пути и настройки расчетов
3. ✅ `utils/license.py` - путь к лицензии
4. ✅ `utils/logger.py` - пути к логам и параметры
5. ✅ `utils/error_handler.py` - путь к отчетам об ошибках
6. ✅ `utils/cache.py` - путь к кэшу и настройки
7. ✅ `main.py` - настройки UI
8. ✅ `calculations/shunt_kz.py` - путь к результатам
9. ✅ `calculations/max_kz_time.py` - путь к результатам
10. ✅ `calculations/dyn_stability.py` - путь к результатам
11. ✅ `calculations/mdp_stability.py` - путь к результатам
12. ✅ `calculations/uost_stability.py` - путь к результатам

## Обратная совместимость

Система полностью обратно совместима:
- Если конфиг не найден, используются значения по умолчанию
- Все значения по умолчанию соответствуют предыдущему хардкоду
- При первом запуске автоматически создается конфиг с дефолтными значениями

## Пример конфигурации

См. `config.yaml.example` для полного примера конфигурации с комментариями.

## Примечания

- Пути с `~` автоматически раскрываются в домашнюю директорию
- Конфигурация загружается один раз при первом обращении (singleton)
- Изменения в конфиге применяются после перезапуска приложения
- Для применения изменений без перезапуска используйте `config.reload()`

