"""
Логика работы с треугольником
"""
from .geometry import calculate_side_length
from utils.logger import app_logger


class TriangleManager:
    def __init__(self):
        self.vertices = []  # Список вершин треугольника
        self.sides = []  # Длины сторон в пикселях и мм
        self.listeners = []  # Подписчики на изменения

    def add_vertex(self, x, y):
        """Добавление вершины"""
        app_logger.debug(f"Adding vertex at ({x}, {y})")
        self.vertices.append((x, y))
        if len(self.vertices) > 3:
            removed = self.vertices.pop(0)
            app_logger.debug(f"Removed oldest vertex at {removed}")
        self._update_sides()
        self._notify_listeners()
        app_logger.info(f"Triangle now has {len(self.vertices)} vertices")

    def update_vertex(self, index, x, y):
        """Обновление позиции вершины"""
        if 0 <= index < len(self.vertices):
            self.vertices[index] = (x, y)
            self._update_sides()
            self._notify_listeners()

    def clear(self):
        """Очистка треугольника"""
        app_logger.info("Clearing triangle")
        self.vertices.clear()
        self.sides.clear()
        self._notify_listeners()

    def is_complete(self):
        """Проверка, построен ли полный треугольник"""
        return len(self.vertices) == 3

    def get_vertex_at_position(self, x, y, tolerance=10):
        """
        Поиск вершины в заданной позиции
        Возвращает индекс вершины или None
        """
        for i, (vx, vy) in enumerate(self.vertices):
            if abs(vx - x) <= tolerance and abs(vy - y) <= tolerance:
                return i
        return None

    def _update_sides(self, pixel_size_m=0.1):
        """Обновление расчетов сторон"""
        self.sides.clear()

        if len(self.vertices) >= 2:
            for i in range(len(self.vertices)):
                j = (i + 1) % len(self.vertices)
                point1 = self.vertices[i]
                point2 = self.vertices[j]

                length_px, length_m = calculate_side_length(point1, point2, pixel_size_m)
                self.sides.append({
                    'points': (point1, point2),
                    'length_px': length_px,
                    'length_m': length_m
                })

    def _notify_listeners(self):
        """Уведомление подписчиков об изменениях"""
        for listener in self.listeners:
            listener.on_triangle_changed()

    def add_listener(self, listener):
        """Добавление подписчика"""
        self.listeners.append(listener)

    def remove_listener(self, listener):
        """Удаление подписчика"""
        self.listeners.remove(listener)
        