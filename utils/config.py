"""
Конфигурация приложения
"""
from .logger import app_logger


class Config:
    def __init__(self):
        self.pixel_size_m = 0.001  # размер пикселя в метрах
        self.canvas_width = 800
        self.canvas_height = 600
        app_logger.info("Configuration initialized")

    def set_pixel_size(self, size_m):
        """Установка размера пикселя в метрах"""
        if size_m > 0:
            self.pixel_size_m = size_m
            app_logger.info(f"Pixel size set to {size_m} meters")
        else:
            app_logger.warning("Attempted to set invalid pixel size")
            