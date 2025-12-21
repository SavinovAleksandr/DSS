"""
Централизованная обработка ошибок для StabLimit
"""

import traceback
import os
from typing import Optional, Callable, Any
from pathlib import Path
import json
from datetime import datetime

from utils.logger import logger
from utils.config import config
from utils.exceptions import (
    InitialDataException,
    UserLicenseException,
    UncorrectFileException,
    RastrUnavailableException
)


class ErrorHandler:
    """Класс для централизованной обработки ошибок"""
    
    # Словарь понятных сообщений об ошибках
    ERROR_MESSAGES = {
        InitialDataException: "Не все необходимые исходные данные загружены. Пожалуйста, проверьте наличие всех требуемых файлов.",
        UserLicenseException: "Проблема с лицензией. Обратитесь к администратору.",
        UncorrectFileException: "Некорректный формат файла. Проверьте, что файл не поврежден и соответствует требуемому формату.",
        RastrUnavailableException: "RASTR недоступен на данной платформе. Для выполнения расчетов требуется Windows с установленным RASTR (ПК RUSTab).\n\nПриложение может работать на Linux/macOS для просмотра интерфейса и работы с данными, но расчеты будут недоступны.",
        FileNotFoundError: None,  # Будет обработано динамически с учетом конфигурации
        PermissionError: "Нет доступа к файлу. Проверьте права доступа.",
        ValueError: "Некорректное значение параметра. Проверьте введенные данные.",
        KeyError: "Отсутствует необходимый параметр в данных.",
        TypeError: "Некорректный тип данных.",
        MemoryError: "Недостаточно памяти для выполнения операции. Закройте другие приложения и попробуйте снова.",
        OSError: "Ошибка операционной системы. Проверьте доступность ресурсов.",
    }
    
    # Типы ошибок, которые можно автоматически восстановить
    RECOVERABLE_ERRORS = (
        FileNotFoundError,
        PermissionError,
        ValueError,
        KeyError,
    )
    
    def __init__(self):
        self.error_reports_dir = config.get_path("paths.error_reports_dir")
        self.error_reports_dir.mkdir(parents=True, exist_ok=True)
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[str] = None,
        show_to_user: bool = True,
        recover_callback: Optional[Callable[[], Any]] = None
    ) -> tuple[str, bool]:
        """
        Обработать ошибку
        
        Args:
            error: Исключение
            context: Контекст, в котором произошла ошибка
            show_to_user: Показывать ли сообщение пользователю
            recover_callback: Функция для попытки восстановления
        
        Returns:
            tuple: (сообщение для пользователя, успешно ли восстановлено)
        """
        # Логирование ошибки
        error_context = f" в {context}" if context else ""
        logger.exception(f"Ошибка{error_context}: {type(error).__name__}: {str(error)}")
        
        # Получение понятного сообщения
        user_message = self._get_user_message(error)
        
        # Попытка автоматического восстановления
        recovered = False
        if isinstance(error, self.RECOVERABLE_ERRORS) and recover_callback:
            try:
                logger.info(f"Попытка автоматического восстановления после {type(error).__name__}")
                recover_callback()
                recovered = True
                user_message += "\n\nПроблема была автоматически исправлена. Попробуйте повторить операцию."
                logger.info("Автоматическое восстановление успешно")
            except Exception as recovery_error:
                logger.error(f"Не удалось восстановить: {recovery_error}")
                user_message += "\n\nАвтоматическое восстановление не удалось."
        
        # Сохранение отчета об ошибке
        if not recovered:
            self._save_error_report(error, context)
        
        # Аудит ошибки
        logger.audit("ERROR", f"{type(error).__name__}: {str(error)} | Context: {context or 'N/A'}")
        
        return user_message, recovered
    
    def _get_user_message(self, error: Exception) -> str:
        """Получить понятное сообщение об ошибке для пользователя"""
        error_type = type(error)
        base_message: str
        
        # Специальная обработка FileNotFoundError для шаблонов RASTR
        if isinstance(error, FileNotFoundError):
            error_str = str(error)
            # Проверяем, связана ли ошибка с шаблоном RASTR
            if ("шаблон" in error_str.lower() or "template" in error_str.lower() or
                ".sch" in error_str or ".rst" in error_str or ".dfw" in error_str):
                template_dir = config.get_path("paths.rastr_template_dir")
                base_message = (
                    f"Файл не найден. Проверьте путь к файлу.\n\n"
                    f"Если ошибка связана с шаблоном RASTR, проверьте:\n"
                    f"1. Существует ли директория шаблонов: {template_dir}\n"
                    f"2. Есть ли в ней файл с нужным расширением "
                    f"(.rst, .sch, .dfw и т.д.)\n"
                    f"3. Правильно ли настроен путь в конфигурации "
                    f"(paths.rastr_template_dir)"
                )
            else:
                base_message = "Файл не найден. Проверьте путь к файлу."
        # Проверка точного совпадения типа
        elif error_type in self.ERROR_MESSAGES:
            msg = self.ERROR_MESSAGES[error_type]
            base_message = msg if msg is not None else f"Произошла ошибка: {str(error)}"
        else:
            # Проверка базовых классов
            base_message = f"Произошла ошибка: {str(error)}"
            for err_class, message in self.ERROR_MESSAGES.items():
                if isinstance(error, err_class):
                    base_message = message if message is not None else base_message
                    break
        
        # Добавление деталей, если они есть
        if str(error) and str(error) != str(error_type):
            base_message += f"\n\nДетали: {str(error)}"
        
        return base_message
    
    def _save_error_report(self, error: Exception, context: Optional[str] = None):
        """Сохранить отчет об ошибке"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.error_reports_dir / f"error_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "traceback": traceback.format_exc(),
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Отчет об ошибке сохранен: {report_file}")
        except Exception as e:
            logger.error(f"Не удалось сохранить отчет об ошибке: {e}")
    
    def validate_file_path(self, file_path: Path, must_exist: bool = True) -> tuple[bool, Optional[str]]:
        """
        Валидация пути к файлу
        
        Returns:
            tuple: (валиден ли путь, сообщение об ошибке если невалиден)
        """
        try:
            file_path = Path(file_path)
            
            if must_exist and not file_path.exists():
                return False, f"Файл не найден: {file_path}"
            
            if must_exist and not file_path.is_file():
                return False, f"Путь не является файлом: {file_path}"
            
            # Проверка доступности для чтения (используем os.access вместо несуществующего is_readable)
            if must_exist:
                if not os.access(file_path, os.R_OK):
                    return False, f"Нет доступа для чтения файла: {file_path}"
            
            return True, None
        except Exception as e:
            return False, f"Ошибка при проверке файла: {str(e)}"
    
    def validate_data(self, data: Any, required_fields: list[str]) -> tuple[bool, Optional[str]]:
        """
        Валидация данных на наличие обязательных полей
        
        Returns:
            tuple: (валидны ли данные, сообщение об ошибке если невалидны)
        """
        if not isinstance(data, dict):
            return False, "Данные должны быть словарем"
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        
        return True, None


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()

