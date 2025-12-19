"""
Управление темами интерфейса
"""

import json
from pathlib import Path
from typing import Literal
from utils.logger import logger

ThemeMode = Literal["light", "dark", "system"]


class ThemeManager:
    """Класс для управления темами приложения"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if ThemeManager._initialized:
            return
        
        ThemeManager._initialized = True
        self.config_dir = Path.home() / '.dynstabspace'
        self.config_file = self.config_dir / 'theme_config.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Загрузка сохраненной темы
        self._theme_mode: ThemeMode = self._load_theme()
        logger.info(f"Тема загружена: {self._theme_mode}")
    
    def _load_theme(self) -> ThemeMode:
        """Загрузить сохраненную тему"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme = config.get('theme', 'system')
                    if theme in ['light', 'dark', 'system']:
                        return theme
        except Exception as e:
            logger.warning(f"Не удалось загрузить тему: {e}")
        
        return 'system'  # По умолчанию
    
    def _save_theme(self, theme: ThemeMode):
        """Сохранить тему"""
        try:
            config = {'theme': theme}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"Тема сохранена: {theme}")
        except Exception as e:
            logger.error(f"Не удалось сохранить тему: {e}")
    
    @property
    def theme_mode(self) -> ThemeMode:
        """Получить текущую тему"""
        return self._theme_mode
    
    def set_theme(self, theme: ThemeMode):
        """Установить тему"""
        if theme not in ['light', 'dark', 'system']:
            logger.warning(f"Некорректная тема: {theme}, используется 'system'")
            theme = 'system'
        
        self._theme_mode = theme
        self._save_theme(theme)
        logger.audit("THEME_CHANGE", f"Тема изменена на: {theme}")
    
    def toggle_theme(self):
        """Переключить между светлой и темной темой"""
        if self._theme_mode == 'light':
            self.set_theme('dark')
        elif self._theme_mode == 'dark':
            self.set_theme('light')
        else:
            # Если system, переключаем на dark
            self.set_theme('dark')
    
    def get_color_scheme(self) -> dict:
        """Получить цветовую схему для текущей темы"""
        if self._theme_mode == 'dark':
            return {
                'bg': '#1a1a1a',
                'fg': '#ffffff',
                'select_bg': '#2b2b2b',
                'select_fg': '#ffffff',
                'button_bg': '#1f538d',
                'button_hover': '#14375e',
                'entry_bg': '#2b2b2b',
                'entry_fg': '#ffffff',
            }
        elif self._theme_mode == 'light':
            return {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#e0e0e0',
                'select_fg': '#000000',
                'button_bg': '#0078d4',
                'button_hover': '#005a9e',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
            }
        else:  # system
            # Используем темную тему по умолчанию для system
            return self.get_color_scheme() if False else {
                'bg': '#1a1a1a',
                'fg': '#ffffff',
                'select_bg': '#2b2b2b',
                'select_fg': '#ffffff',
                'button_bg': '#1f538d',
                'button_hover': '#14375e',
                'entry_bg': '#2b2b2b',
                'entry_fg': '#ffffff',
            }


# Глобальный экземпляр менеджера тем
theme_manager = ThemeManager()

