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

        # Находим самую длинную сторону как основание
        sides = [
            (point_a, point_b, point_c),
            (point_b, point_c, point_a),
            (point_c, point_a, point_b)
        ]

        max_height = 0
        base_length_mm = 0

        for base_p1, base_p2, opposite in sides:
            # Длина основания в пикселях отображаемого изображения
            base_length_px_display = ((base_p2[0] - base_p1[0]) ** 2 + (base_p2[1] - base_p1[1]) ** 2) ** 0.5
            # Преобразуем в пиксели оригинала
            base_length_px_original = base_length_px_display * scale_factor
            current_base_length_m = base_length_px_original * pixel_size_m

            # Высота треугольника
            current_height_px_display = triangle_height(base_p1, base_p2, opposite)
            # Преобразуем в пиксели оригинала
            current_height_px_original = current_height_px_display * scale_factor
            current_height_mm = current_height_px_original * pixel_size_m

            if current_height_mm > max_height:
                max_height = current_height_mm
                base_length_mm = current_base_length_m

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
            
            # Длины в пикселях отображаемого изображения
            base_length_px_display = max([
                ((point_b[0] - point_a[0]) ** 2 + (point_b[1] - point_a[1]) ** 2) ** 0.5,
                ((point_c[0] - point_b[0]) ** 2 + (point_c[1] - point_b[1]) ** 2) ** 0.5,
                ((point_a[0] - point_c[0]) ** 2 + (point_a[1] - point_c[1]) ** 2) ** 0.5
            ])
            
            # Преобразуем в пиксели оригинала
            base_length_px_original = base_length_px_display * scale_factor
            base_length_m = base_length_px_original * pixel_size_m
            radius_m = base_length_m / 2

            # Приблизительная высота (можно улучшить)
            height_m = (volume * 3) / (math.pi * radius_m ** 2) if radius_m > 0 else 0

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
        