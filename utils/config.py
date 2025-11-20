"""
Конфигурация приложения
"""


class Config:
    def __init__(self):
        self.pixel_size_m = 0.001  # размер пикселя в метрах
        self.canvas_width = 800
        self.canvas_height = 600

    def set_pixel_size(self, size_m):
        """Установка размера пикселя в метрах"""
        if size_m > 0:
            self.pixel_size_m = size_m
            