"""
Константы приложения
"""

VERSION = "0.8.2"
APP_NAME = "Cone App"
DESCRIPTION = "Приложение для построения треугольников и расчета объемов и масс конусов"
GITHUB_URL = "https://github.com/SemonoffArt/cone"
AUTHOR = "Артемий Семёнов"
WEBSITE = "https://semonoffart.github.io/"
LICENSE = "MIT License"
COPYRIGHT = "Copyright © 2025 Semonoff Art"
EMAIL = "semonoff@gmail.com"

# (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = 'WARNING' # Level of logging

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
# WIN_WIDTH = 1024
# WIN_HEIGHT = 768
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 768

# Настройки Trassir камер
CAM_CONE_ZIF1 = {"chanel_name": "ЗИФ-1 19. Конус Руда", "trassir_ip": "10.100.59.10", "password":"master", "pixel_size_m": 0.091, 
                "roi":[1125,1545,345,615], "cone_center":[45,65], "threshold":50, "k_vol":0.8, "k_den":1.76}
CAM_CONE_ZIF2 = {"chanel_name": "ККД-2 115. Конус", "trassir_ip": "10.100.72.14", "password":"master", "pixel_size_m": 0.16, 
                "roi":[716,1180,170,360], "cone_center":[40,60], "threshold":85, "k_vol":0.55, "k_den":1.76}
