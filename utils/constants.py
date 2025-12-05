"""
Константы приложения
"""

VERSION = "0.3.0"
APP_NAME = "Cone App"
DESCRIPTION = "Приложение для построения треугольников и расчета объемов конусов"
GITHUB_URL = "https://github.com/SemonoffArt/cone"
AUTHOR = "Артемий Семёнов"
WEBSITE = "https://semonoffart.github.io/"
LICENSE = "MIT License"
COPYRIGHT = "Copyright © 2025 Semonoff Art"
EMAIL = "semonoff@gmail.com"

# (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = 'INFO' # Level of logging

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
DEFAULT_PIXEL_SIZE_M = 0.008  # размер пикселя в метрах (1 мм = 0.001 м)
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Настройки Trassir
TRASSIR_ZIF1_IP = "10.100.59.10"
TRASSIR_ZIF2_IP = "10.100.72.14"
CAM_NAME_CONE_ZIF1 = "ЗИФ-1 19. Конус Руда"
CAM_NAME_CONE_ZIF2 = "ККД-2 115. Конус"
#0.08
CAM_CONE_ZIF1 = {"chanel_name": "ЗИФ-1 19. Конус Руда", "trassir_ip": "10.100.59.10", "pixel_size_m": 0.135, 
                "roi":[740,1055,230,425], "cone_center":[45,65], "threshold":65, "k_vol":1, "k_den":1.76}
CAM_CONE_ZIF2 = {"chanel_name": "ККД-2 115. Конус", "trassir_ip": "10.100.72.14", "pixel_size_m": 0.16, 
                "roi":[716,1180,170,360], "cone_center":[40,60], "threshold":85, "k_vol":0.55, "k_den":1.76}
