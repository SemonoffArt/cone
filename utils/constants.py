"""
Константы приложения
"""

# Цвета
COLOR_TRIANGLE = "blue"
COLOR_VERTEX = "red"
COLOR_HOVER = "green"
COLOR_TEXT = "white"
COLOR_BG = "white"

# Размеры
VERTEX_RADIUS = 6
LINE_WIDTH = 2
TEXT_FONT = ("Arial", 10)

# Настройки по умолчанию
DEFAULT_PIXEL_SIZE_M = 0.001  # размер пикселя в метрах (1 мм = 0.001 м)
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Настройки Trassir
TRASSIR_ZIF1_IP = "10.100.59.10"
TRASSIR_ZIF2_IP = "10.100.72.14"
CAM_NAME_CONE_ZIF1 = "ЗИФ-1 19. Конус Руда"
CAM_NAME_CONE_ZIF2 = "ККД-2 115. Конус"
CAM_CONE_ZIF1 = {"chanel_name": "ЗИФ-1 19. Конус Руда", "trassir_ip": "10.100.59.10", "pixel_size_m": 0.08}
CAM_CONE_ZIF2 = {"chanel_name": "ККД-2 115. Конус", "trassir_ip": "10.100.72.14", "pixel_size_m": 0.16}
