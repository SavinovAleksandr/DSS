"""
Система управления конфигурацией приложения
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Ленивый импорт logger для избежания циклического импорта
def _get_logger():
    from utils.logger import logger
    return logger

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


class Config:
    """Класс для управления конфигурацией приложения"""
    
    _instance: Optional['Config'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Config._initialized:
            return
        
        Config._initialized = True
        
        # Путь к директории конфигурации
        self.config_dir = Path.home() / '.stablimit'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу конфигурации
        self.config_file = self.config_dir / 'config.json'
        
        # Загрузка конфигурации
        self._config: Dict[str, Any] = self._load_config()
        
        # Логирование после загрузки (избегаем циклический импорт)
        try:
            _get_logger().info(f"Конфигурация загружена из {self.config_file}")
        except:
            pass  # Если logger еще не инициализирован, пропускаем
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Получить конфигурацию по умолчанию"""
        return {
            "paths": {
                "license_file": "C:/ПАРУС 6/licence.txt",
                "results_dir": "~/StabLimit",
                "logs_dir": "~/.stablimit/logs",
                "cache_dir": "~/.stablimit/cache",
                "error_reports_dir": "~/.stablimit/error_reports",
                "rastr_template_dir": "~/Documents/RastrWin3/SHABLON"  # Современные версии RASTR используют Documents
            },
            "calculations": {
                "base_angle": 1.471,
                "crt_time_precision": 0.02,
                "crt_time_max": 1.0,
                "default_selected_sch": 0
            },
            "settings": {
                "use_type_val_u": True,
                "use_sel_nodes": True,
                "calc_one_phase": True,
                "calc_two_phase": True,
                "dyn_no_pa": True,
                "dyn_with_pa": False,
                "save_grf": False,
                "use_lpn": False,
                "lpns": ""
            },
            "ui": {
                "theme": "system",
                "window_size": [900, 750],
                "min_window_size": [800, 600],
                "use_modern_ui": True
            },
            "logging": {
                "max_bytes": 10 * 1024 * 1024,  # 10 MB
                "backup_count": 5,
                "error_log_max_bytes": 5 * 1024 * 1024,  # 5 MB
                "error_log_backup_count": 3
            },
            "performance": {
                "max_workers": None,  # None = автоматически
                "cache_enabled": True,
                "cache_ttl": 3600  # 1 час
            },
            "license": {
                "disable_check": True  # True для отключения проверки лицензии (только для тестирования!)
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию из файла или создать по умолчанию"""
        default_config = self._get_default_config()
        
        # Попытка загрузить из JSON
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Слияние с конфигурацией по умолчанию
                merged_config = self._merge_config(default_config, user_config)
                
                # Сохраняем исправленную конфигурацию, если она была изменена
                if self._config_was_modified(user_config, merged_config):
                    try:
                        self._save_config(merged_config)
                        try:
                            _get_logger().info("Конфигурация исправлена и сохранена")
                        except:
                            pass
                    except Exception as e:
                        try:
                            _get_logger().warning(f"Не удалось сохранить исправленную конфигурацию: {e}")
                        except:
                            pass
                
                try:
                    _get_logger().info("Конфигурация загружена из файла")
                except:
                    pass
                return merged_config
            except Exception as e:
                try:
                    _get_logger().warning(f"Не удалось загрузить конфигурацию: {e}, используются значения по умолчанию")
                except:
                    pass
        
        # Попытка загрузить из YAML (если доступен)
        yaml_config_file = self.config_dir / 'config.yaml'
        if YAML_AVAILABLE and yaml_config_file.exists():
            try:
                with open(yaml_config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                
                if user_config:
                    merged_config = self._merge_config(default_config, user_config)
                    
                    # Сохраняем исправленную конфигурацию в JSON, если она была изменена
                    if self._config_was_modified(user_config, merged_config):
                        try:
                            self._save_config(merged_config)
                            try:
                                _get_logger().info("Конфигурация исправлена и сохранена")
                            except:
                                pass
                        except Exception as e:
                            try:
                                _get_logger().warning(f"Не удалось сохранить исправленную конфигурацию: {e}")
                            except:
                                pass
                    
                    try:
                        _get_logger().info("Конфигурация загружена из YAML файла")
                    except:
                        pass
                    return merged_config
            except Exception as e:
                try:
                    _get_logger().warning(f"Не удалось загрузить YAML конфигурацию: {e}")
                except:
                    pass
        
        # Создание файла конфигурации по умолчанию
        try:
            self._save_config(default_config)
            try:
                _get_logger().info("Создан файл конфигурации по умолчанию")
            except:
                pass
        except Exception as e:
            try:
                _get_logger().warning(f"Не удалось сохранить конфигурацию: {e}")
            except:
                pass
        
        return default_config
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Рекурсивное слияние конфигураций"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        # Автоматическое исправление старого пути к шаблонам RASTR
        if "paths" in result and "rastr_template_dir" in result["paths"]:
            old_path = result["paths"]["rastr_template_dir"]
            # Если используется старый путь RastrWIN3, заменяем на новый
            if isinstance(old_path, str) and "RastrWIN3" in old_path and "Documents" not in old_path:
                result["paths"]["rastr_template_dir"] = "~/Documents/RastrWin3/SHABLON"
                try:
                    _get_logger().info(
                        f"Автоматически исправлен путь к шаблонам RASTR: "
                        f"{old_path} -> ~/Documents/RastrWin3/SHABLON"
                    )
                except:
                    pass
        
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """Сохранить конфигурацию в файл"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Получить значение конфигурации по пути
        
        Args:
            key_path: Путь к значению через точку (например, "paths.results_dir")
            default: Значение по умолчанию, если ключ не найден
        
        Returns:
            Значение конфигурации или default
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any, save: bool = True):
        """
        Установить значение конфигурации
        
        Args:
            key_path: Путь к значению через точку
            value: Новое значение
            save: Сохранить в файл сразу
        """
        keys = key_path.split('.')
        config = self._config
        
        # Создание вложенных словарей при необходимости
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Установка значения
        config[keys[-1]] = value
        
        if save:
            self._save_config(self._config)
            try:
                _get_logger().debug(f"Конфигурация обновлена: {key_path} = {value}")
            except:
                pass
    
    def get_path(self, key_path: str, expand_user: bool = True) -> Path:
        """
        Получить путь из конфигурации как Path объект
        
        Args:
            key_path: Путь к значению через точку
            expand_user: Раскрыть ~ в домашнюю директорию
        
        Returns:
            Path объект
        """
        path_str = self.get(key_path, "")
        if not path_str:
            raise ValueError(f"Путь не найден в конфигурации: {key_path}")
        
        path = Path(path_str)
        if expand_user and path_str.startswith("~"):
            path = path.expanduser()
        
        return path
    
    def reload(self):
        """Перезагрузить конфигурацию из файла"""
        self._config = self._load_config()
        try:
            _get_logger().info("Конфигурация перезагружена")
        except:
            pass
    
    def save(self):
        """Сохранить текущую конфигурацию в файл"""
        self._save_config(self._config)
        try:
            _get_logger().info("Конфигурация сохранена")
        except:
            pass


# Глобальный экземпляр конфигурации
config = Config()

