"""
Конфигурация приложения
"""


class Config:
    def __init__(self):
        self.pixel_size_mm = 0.1  # размер пикселя в мм
        self.canvas_width = 800
        self.canvas_height = 600

    def set_pixel_size(self, size_mm):
        """Установка размера пикселя в мм"""
        if size_mm > 0:
            self.pixel_size_mm = size_mm
            