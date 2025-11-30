"""
Конфигурация приложения
"""
from .logger import app_logger
from utils.constants import DEFAULT_PIXEL_SIZE_M, CANVAS_WIDTH, CANVAS_HEIGHT




class Config:
    def __init__(self):
        self.pixel_size_m = DEFAULT_PIXEL_SIZE_M  # размер пикселя в метрах
        self.canvas_width = CANVAS_WIDTH
        self.canvas_height = CANVAS_HEIGHT
        app_logger.info("Configuration initialized")

    def set_pixel_size(self, size_m):
        """Установка размера пикселя в метрах"""
        if size_m > 0:
            self.pixel_size_m = size_m
            app_logger.info(f"Pixel size set to {size_m} meters")
        else:
            app_logger.warning("Attempted to set invalid pixel size")
            