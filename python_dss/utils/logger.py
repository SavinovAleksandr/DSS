"""
Система логирования для StabLimit
"""

import logging
import logging.handlers
from pathlib import Path
import sys
from datetime import datetime
from typing import Optional
from .config import config


class Logger:
    """Класс для управления логированием"""
    
    _instance: Optional['Logger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._initialized:
            return
        
        Logger._initialized = True
        self.logger = logging.getLogger('StabLimit')
        self.logger.setLevel(logging.DEBUG)
        
        # Предотвращение дублирования логов
        if self.logger.handlers:
            return
        
        # Создание директории для логов (из конфигурации)
        try:
            self.log_dir = config.get_path("paths.logs_dir")
            # Логируем путь ДО создания (используем print, так как logger еще не инициализирован)
            print(f"[DEBUG] Попытка создать директорию для логов: {self.log_dir.absolute()}")
            
            # Создаем директорию с обработкой ошибок
            try:
                self.log_dir.mkdir(parents=True, exist_ok=True)
                print(f"[DEBUG] Директория для логов создана/существует: {self.log_dir.absolute()}")
            except PermissionError as e:
                # Если нет прав, пробуем альтернативный путь
                print(f"[WARNING] Нет прав на создание директории {self.log_dir.absolute()}: {e}")
                fallback_dir = Path.home() / '.stablimit' / 'logs'
                print(f"[WARNING] Используем альтернативный путь: {fallback_dir.absolute()}")
                fallback_dir.mkdir(parents=True, exist_ok=True)
                self.log_dir = fallback_dir
            except Exception as e:
                # Другая ошибка - используем альтернативный путь
                print(f"[ERROR] Ошибка при создании директории {self.log_dir.absolute()}: {e}")
                fallback_dir = Path.home() / '.stablimit' / 'logs'
                print(f"[ERROR] Используем альтернативный путь: {fallback_dir.absolute()}")
                fallback_dir.mkdir(parents=True, exist_ok=True)
                self.log_dir = fallback_dir
        except Exception as e:
            # Если вообще не удалось получить путь из конфигурации
            print(f"[ERROR] Не удалось получить путь к логам из конфигурации: {e}")
            self.log_dir = Path.home() / '.stablimit' / 'logs'
            self.log_dir.mkdir(parents=True, exist_ok=True)
            print(f"[ERROR] Используем путь по умолчанию: {self.log_dir.absolute()}")
        
        # Формат логов
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный обработчик (INFO и выше)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)
        
        # Файловый обработчик (DEBUG и выше) с ротацией по размеру
        log_file = self.log_dir / 'stablimit.log'
        max_bytes = config.get("logging.max_bytes", 10 * 1024 * 1024)
        backup_count = config.get("logging.backup_count", 5)
        
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                str(log_file),  # Явно преобразуем в строку для Windows
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(log_format)
            self.logger.addHandler(file_handler)
            print(f"[DEBUG] Файловый обработчик создан: {log_file.absolute()}")
        except Exception as e:
            print(f"[ERROR] Не удалось создать файловый обработчик для {log_file.absolute()}: {e}")
            # Пробуем альтернативный путь
            fallback_log_file = Path.home() / '.stablimit' / 'logs' / 'stablimit.log'
            try:
                fallback_log_file.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.handlers.RotatingFileHandler(
                    str(fallback_log_file),
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(log_format)
                self.logger.addHandler(file_handler)
                self.log_dir = fallback_log_file.parent
                print(f"[WARNING] Используется альтернативный путь для логов: {fallback_log_file.absolute()}")
            except Exception as e2:
                print(f"[CRITICAL] Не удалось создать файловый обработчик даже в альтернативном пути: {e2}")
                # Продолжаем без файлового обработчика - только консольный
        
        # Обработчик ошибок (ERROR и выше) в отдельный файл
        error_log_file = self.log_dir / 'errors.log'
        error_max_bytes = config.get("logging.error_log_max_bytes", 5 * 1024 * 1024)
        error_backup_count = config.get("logging.error_log_backup_count", 3)
        try:
            error_handler = logging.handlers.RotatingFileHandler(
                str(error_log_file),  # Явно преобразуем в строку для Windows
                maxBytes=error_max_bytes,
                backupCount=error_backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(log_format)
            self.logger.addHandler(error_handler)
        except Exception as e:
            print(f"[WARNING] Не удалось создать обработчик ошибок для {error_log_file.absolute()}: {e}")
        
        # Лог операций пользователя (отдельный файл)
        audit_log_file = self.log_dir / 'audit.log'
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_format = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        audit_handler.setFormatter(audit_format)
        self.audit_logger = logging.getLogger('StabLimit.Audit')
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.setLevel(logging.INFO)
        
        self.logger.info("Система логирования инициализирована")
    
    def debug(self, message: str, *args, **kwargs):
        """Логирование на уровне DEBUG"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Логирование на уровне INFO"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Логирование на уровне WARNING"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Логирование на уровне ERROR"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Логирование на уровне CRITICAL"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info=True, **kwargs):
        """Логирование исключения с traceback"""
        self.logger.error(message, *args, exc_info=exc_info, **kwargs)
    
    def audit(self, action: str, details: Optional[str] = None):
        """Логирование действий пользователя для аудита"""
        log_message = f"ACTION: {action}"
        if details:
            log_message += f" | DETAILS: {details}"
        self.audit_logger.info(log_message)
    
    def get_log_file_path(self) -> Path:
        """Получить путь к основному лог-файлу"""
        return self.log_dir / 'stablimit.log'
    
    def get_error_log_file_path(self) -> Path:
        """Получить путь к лог-файлу ошибок"""
        return self.log_dir / 'errors.log'
    
    def set_level(self, level: str):
        """Установить уровень логирования"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.logger.info(f"Уровень логирования изменен на {level}")


# Глобальный экземпляр логгера
logger = Logger()

