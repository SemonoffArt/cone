"""
Калькулятор конуса
"""
import math
from .geometry import triangle_height
from utils.logger import app_logger


class ConeCalculator:
    @staticmethod
    def calculate_cone_volume(triangle_vertices, pixel_size_m, scale_factor=1.0):
        """
        Расчет объема конуса на основе треугольника
        """
        app_logger.debug(f"Calculating cone volume for vertices: {triangle_vertices}")
        if len(triangle_vertices) != 3:
            app_logger.warning("Invalid number of vertices for cone calculation")
            return 0

        point_a, point_b, point_c = triangle_vertices

        # Находим сторону, которая наиболее расположена в горизонтальной плоскости
        # Это сторона с наименьшей разницей по Y-координате
        sides = [
            (point_a, point_b, point_c),  # AB - основание, C - вершина
            (point_b, point_c, point_a),  # BC - основание, A - вершина
            (point_c, point_a, point_b)   # CA - основание, B - вершина
        ]

        # Выбираем сторону с минимальной разницей по Y (наиболее горизонтальную)
        min_y_diff = float('inf')
        best_base_p1 = None
        best_base_p2 = None
        best_opposite = None
        
        for base_p1, base_p2, opposite in sides:
            y_diff = abs(base_p2[1] - base_p1[1])  # Разница по вертикали
            if y_diff < min_y_diff:
                min_y_diff = y_diff
                best_base_p1 = base_p1
                best_base_p2 = base_p2
                best_opposite = opposite
        
        # Длина основания в пикселях отображаемого изображения
        base_length_px_display = ((best_base_p2[0] - best_base_p1[0]) ** 2 + (best_base_p2[1] - best_base_p1[1]) ** 2) ** 0.5
        # Преобразуем в пиксели оригинала
        base_length_px_original = base_length_px_display * scale_factor
        base_length_mm = base_length_px_original * pixel_size_m

        # Высота треугольника от основания до вершины
        max_height_px_display = triangle_height(best_base_p1, best_base_p2, best_opposite)
        # Преобразуем в пиксели оригинала
        max_height_px_original = max_height_px_display * scale_factor
        max_height = max_height_px_original * pixel_size_m

        # Радиус основания конуса - половина длины основания треугольника
        radius_mm = base_length_mm / 2

        # Объем конуса
        if max_height > 0 and radius_mm > 0:
            volume = (1 / 3) * math.pi * radius_mm ** 2 * max_height
            app_logger.info(f"Calculated cone volume: {volume}")
            return volume
        else:
            app_logger.warning("Unable to calculate cone volume - invalid dimensions")
            return 0

    @staticmethod
    def get_cone_parameters(triangle_vertices, pixel_size_m, scale_factor=1.0):
        """
        Получение параметров конуса
        """
        volume = ConeCalculator.calculate_cone_volume(triangle_vertices, pixel_size_m, scale_factor)

        # Находим основание и высоту для отображения
        if len(triangle_vertices) == 3:
            point_a, point_b, point_c = triangle_vertices
            
            # Находим сторону, которая наиболее расположена в горизонтальной плоскости
            sides = [
                (point_a, point_b, point_c),  # AB - основание, C - вершина
                (point_b, point_c, point_a),  # BC - основание, A - вершина
                (point_c, point_a, point_b)   # CA - основание, B - вершина
            ]

            # Выбираем сторону с минимальной разницей по Y
            min_y_diff = float('inf')
            best_base_p1 = None
            best_base_p2 = None
            best_opposite = None
            
            for base_p1, base_p2, opposite in sides:
                y_diff = abs(base_p2[1] - base_p1[1])
                if y_diff < min_y_diff:
                    min_y_diff = y_diff
                    best_base_p1 = base_p1
                    best_base_p2 = base_p2
                    best_opposite = opposite
            
            # Длина основания в пикселях отображаемого изображения
            base_length_px_display = ((best_base_p2[0] - best_base_p1[0]) ** 2 + (best_base_p2[1] - best_base_p1[1]) ** 2) ** 0.5
            
            # Преобразуем в пиксели оригинала
            base_length_px_original = base_length_px_display * scale_factor
            base_length_m = base_length_px_original * pixel_size_m
            radius_m = base_length_m / 2

            # Высота треугольника от основания до вершины
            height_px_display = triangle_height(best_base_p1, best_base_p2, best_opposite)
            height_px_original = height_px_display * scale_factor
            height_m = height_px_original * pixel_size_m

            return {
                'volume': volume,
                'radius_m': radius_m,
                'height_m': height_m,
                'base_length_m': base_length_m
            }
        else:
            return {
                'volume': 0,
                'radius_m': 0,
                'height_m': 0,
                'base_length_m': 0
            }
        