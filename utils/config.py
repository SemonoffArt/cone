"""
Конфигурация приложения
"""
import json
import os
import sys
from typing import Any, Dict
from .logger import app_logger


def get_app_directory():
    """
    Получить директорию запуска приложения.
    Работает как для PyInstaller, так и для обычного Python.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller создаёт временную папку, но нам нужна директория exe
        return os.path.dirname(sys.executable)
    else:
        # Для обычного Python - текущая директория
        return os.path.abspath(".")


class Config:
    """
    Класс для управления конфигурацией приложения.
    Читает/сохраняет настройки в config.json.
    """
    
    def __init__(self):
        self.config_path = os.path.join(get_app_directory(), "config.json")
        self.data: Dict[str, Any] = {}
        self._load_or_create_config()
        app_logger.info(f"Configuration loaded from {self.config_path}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Получить конфигурацию по умолчанию из constants.py"""
        from utils.constants import (
            VERSION, APP_NAME, DESCRIPTION, GITHUB_URL, AUTHOR, WEBSITE, 
            LICENSE, COPYRIGHT, EMAIL, LOG_LEVEL,
            COLOR_TRIANGLE, COLOR_VERTEX, COLOR_HOVER, COLOR_TEXT, COLOR_BG,
            VERTEX_RADIUS, LINE_WIDTH, TEXT_FONT,
            DEFAULT_PIXEL_SIZE_M, CANVAS_WIDTH, CANVAS_HEIGHT,
            CAM_CONE_ZIF1, CAM_CONE_ZIF2
        )
        
        return {
            "VERSION": VERSION,
            "APP_NAME": APP_NAME,
            "DESCRIPTION": DESCRIPTION,
            "GITHUB_URL": GITHUB_URL,
            "AUTHOR": AUTHOR,
            "WEBSITE": WEBSITE,
            "LICENSE": LICENSE,
            "COPYRIGHT": COPYRIGHT,
            "EMAIL": EMAIL,
            "LOG_LEVEL": LOG_LEVEL,
            "COLOR_TRIANGLE": COLOR_TRIANGLE,
            "COLOR_VERTEX": COLOR_VERTEX,
            "COLOR_HOVER": COLOR_HOVER,
            "COLOR_TEXT": COLOR_TEXT,
            "COLOR_BG": COLOR_BG,
            "VERTEX_RADIUS": VERTEX_RADIUS,
            "LINE_WIDTH": LINE_WIDTH,
            "TEXT_FONT": list(TEXT_FONT),  # Преобразуем tuple в list для JSON
            "DEFAULT_PIXEL_SIZE_M": DEFAULT_PIXEL_SIZE_M,
            "CANVAS_WIDTH": CANVAS_WIDTH,
            "CANVAS_HEIGHT": CANVAS_HEIGHT,
            "CAM_CONE_ZIF1": CAM_CONE_ZIF1,
            "CAM_CONE_ZIF2": CAM_CONE_ZIF2
        }
    
    def _load_or_create_config(self):
        """Загрузить или создать config.json"""
        from utils.constants import VERSION
        
        if not os.path.exists(self.config_path):
            # Файл не существует - создаём новый
            app_logger.info(f"Config file not found. Creating new config at {self.config_path}")
            self.data = self._get_default_config()
            self._save_config()
        else:
            # Файл существует - загружаем и проверяем версию
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                config_version = self.data.get("VERSION", "0.0.0")
                app_logger.info(f"Loaded config version: {config_version}, App version: {VERSION}")
                
                # Сравниваем версии
                if self._compare_versions(VERSION, config_version) > 0:
                    # Версия в constants.py выше - обновляем config
                    app_logger.info(f"App version ({VERSION}) is higher than config version ({config_version}). Updating config...")
                    self.data = self._get_default_config()
                    self._save_config()
                else:
                    app_logger.info("Config version is up to date. Using existing config.")
                    
            except (json.JSONDecodeError, IOError) as e:
                app_logger.error(f"Error loading config: {e}. Creating new config.")
                self.data = self._get_default_config()
                self._save_config()
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Сравнивает две версии.
        Возвращает: 1 если v1 > v2, -1 если v1 < v2, 0 если равны
        """
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            # Дополняем нулями до одинаковой длины
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except (ValueError, AttributeError):
            app_logger.warning(f"Failed to compare versions: {v1} vs {v2}")
            return 0
    
    def _save_config(self):
        """Сохранить конфигурацию в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            app_logger.debug(f"Config saved to {self.config_path}")
        except IOError as e:
            app_logger.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение из конфигурации"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Установить значение и сохранить"""
        self.data[key] = value
        self._save_config()
        app_logger.debug(f"Config updated: {key} = {value}")
    
    def update_camera_config(self, camera_name: str, param: str, value: Any):
        """
        Обновить параметр камеры.
        
        Args:
            camera_name: "CAM_CONE_ZIF1" или "CAM_CONE_ZIF2"
            param: Название параметра (pixel_size_m, k_vol, k_den, threshold)
            value: Новое значение
        """
        if camera_name in self.data and isinstance(self.data[camera_name], dict):
            self.data[camera_name][param] = value
            self._save_config()
            app_logger.debug(f"Camera config updated: {camera_name}.{param} = {value}")
        else:
            app_logger.warning(f"Camera config not found: {camera_name}")
    
    # Устаревшие методы для обратной совместимости
    @property
    def pixel_size_m(self):
        return self.get("DEFAULT_PIXEL_SIZE_M", 0.008)
    
    @pixel_size_m.setter
    def pixel_size_m(self, value):
        self.set("DEFAULT_PIXEL_SIZE_M", value)
    
    @property
    def canvas_width(self):
        return self.get("CANVAS_WIDTH", 800)
    
    @property
    def canvas_height(self):
        return self.get("CANVAS_HEIGHT", 600)
    
    def set_pixel_size(self, size_m):
        """Установка размера пикселя в метрах"""
        if size_m > 0:
            self.pixel_size_m = size_m
            app_logger.info(f"Pixel size set to {size_m} meters")
        else:
            app_logger.warning("Attempted to set invalid pixel size")