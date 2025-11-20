"""
Калькулятор конуса
"""
import math
from .geometry import triangle_height


class ConeCalculator:
    @staticmethod
    def calculate_cone_volume(triangle_vertices, pixel_size_mm):
        """
        Расчет объема конуса на основе треугольника
        """
        if len(triangle_vertices) != 3:
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
            # Длина основания в мм
            base_length_px = ((base_p2[0] - base_p1[0]) ** 2 + (base_p2[1] - base_p1[1]) ** 2) ** 0.5
            current_base_length_mm = base_length_px * pixel_size_mm

            # Высота треугольника
            current_height_px = triangle_height(base_p1, base_p2, opposite)
            current_height_mm = current_height_px * pixel_size_mm

            if current_height_mm > max_height:
                max_height = current_height_mm
                base_length_mm = current_base_length_mm

        # Радиус основания конуса - половина длины основания треугольника
        radius_mm = base_length_mm / 2

        # Объем конуса
        if max_height > 0 and radius_mm > 0:
            volume = (1 / 3) * math.pi * radius_mm ** 2 * max_height
            return volume
        else:
            return 0

    @staticmethod
    def get_cone_parameters(triangle_vertices, pixel_size_mm):
        """
        Получение параметров конуса
        """
        volume = ConeCalculator.calculate_cone_volume(triangle_vertices, pixel_size_mm)

        # Находим основание и высоту для отображения
        if len(triangle_vertices) == 3:
            point_a, point_b, point_c = triangle_vertices
            base_length_px = max([
                ((point_b[0] - point_a[0]) ** 2 + (point_b[1] - point_a[1]) ** 2) ** 0.5,
                ((point_c[0] - point_b[0]) ** 2 + (point_c[1] - point_b[1]) ** 2) ** 0.5,
                ((point_a[0] - point_c[0]) ** 2 + (point_a[1] - point_c[1]) ** 2) ** 0.5
            ])

            base_length_mm = base_length_px * pixel_size_mm
            radius_mm = base_length_mm / 2

            # Приблизительная высота (можно улучшить)
            height_mm = (volume * 3) / (math.pi * radius_mm ** 2) if radius_mm > 0 else 0

            return {
                'volume': volume,
                'radius_mm': radius_mm,
                'height_mm': height_mm,
                'base_length_mm': base_length_mm
            }
        else:
            return {
                'volume': 0,
                'radius_mm': 0,
                'height_mm': 0,
                'base_length_mm': 0
            }
        