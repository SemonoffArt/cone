"""
Геометрические расчеты
"""
import math

def distance_between_points(point1, point2):
    """
    Расчет расстояния между двумя точками в пикселях
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx*dx + dy*dy)

def calculate_side_length(point1, point2, pixel_size_m):
    """
    Расчет длины стороны в пикселях и миллиметрах
    """
    length_pixels = distance_between_points(point1, point2)
    length_m = length_pixels * pixel_size_m
    return length_pixels, length_m

def triangle_area(point1, point2, point3):
    """
    Расчет площади треугольника по трем точкам
    """
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2.0

def triangle_height(base_point1, base_point2, opposite_point):
    """
    Расчет высоты треугольника относительно основания
    """
    area = triangle_area(base_point1, base_point2, opposite_point)
    base_length = distance_between_points(base_point1, base_point2)
    return (2 * area) / base_length if base_length > 0 else 0
