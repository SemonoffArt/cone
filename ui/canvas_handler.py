"""
Обработчик холста для отрисовки изображения и треугольника
"""
import tkinter as tk
from PIL import Image, ImageTk
from utils.constants import (
    COLOR_TRIANGLE, COLOR_VERTEX, COLOR_HOVER, 
    VERTEX_RADIUS, LINE_WIDTH
)
from utils.logger import app_logger


class CanvasHandler:
    """Класс для управления холстом и отрисовкой"""
    
    def __init__(self, canvas, triangle_manager, info_panel=None):
        """
        Инициализация обработчика холста.
        
        Args:
            canvas: Виджет Canvas для отрисовки
            triangle_manager: Менеджер треугольника
            info_panel: Панель информации (для получения pixel_size)
        """
        self.canvas = canvas
        self.triangle_manager = triangle_manager
        self.info_panel = info_panel
        
        # Изображение
        self.current_image = None
        self.original_pil_image = None
        self.base_image_size = None
        self.current_image_size = None
        self.original_image_size = None
        
        # Параметры масштабирования
        self.zoom_level = 1.0
        
        # Параметры взаимодействия
        self.dragging_vertex = None
        self.hovered_vertex = None
    
    def set_image(self, pil_image):
        """
        Установить изображение на холсте.
        
        Args:
            pil_image: PIL изображение
        """
        self.original_pil_image = pil_image
        self.original_image_size = pil_image.size
        
        # Получаем размер холста
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Если холст ещё не отрисован, используем значения по умолчанию
        if canvas_width <= 1:
            from utils.constants import CANVAS_WIDTH, CANVAS_HEIGHT
            canvas_width = CANVAS_WIDTH
            canvas_height = CANVAS_HEIGHT
        
        # Вычисляем размер изображения, сохраняя пропорции
        img_width, img_height = pil_image.size
        
        # Вычисляем коэффициенты масштабирования по ширине и высоте
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        
        # Выбираем меньший коэффициент, чтобы изображение полностью вмещалось
        scale = min(scale_w, scale_h)
        
        # Вычисляем новый размер с сохранением пропорций
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Устанавливаем базовый размер
        self.base_image_size = (new_width, new_height)
        self.current_image_size = (new_width, new_height)
        self.zoom_level = 1.0
        
        app_logger.info(
            f"Image scaled from {img_width}x{img_height} to {new_width}x{new_height} "
            f"to fit canvas {canvas_width}x{canvas_height} (scale: {scale:.2f})"
        )
        
        self.redraw()
    
    def redraw(self):
        """Перерисовать холст с изображением и треугольником"""
        if not self.original_pil_image:
            return
        
        # Очистить холст
        self.canvas.delete("all")
        
        try:
            # Вычисляем размер изображения с учётом масштаба
            base_width, base_height = self.base_image_size
            new_width = int(base_width * self.zoom_level)
            new_height = int(base_height * self.zoom_level)
            
            # Изменяем размер изображения
            resized_image = self.original_pil_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # Конвертируем в PhotoImage
            self.current_image = ImageTk.PhotoImage(resized_image)
            self.current_image_size = (new_width, new_height)
            
            # Отображаем изображение на холсте
            self.canvas.create_image(0, 0, anchor='nw', image=self.current_image)
            
            # Обновляем размер холста
            self.canvas.config(scrollregion=(0, 0, new_width, new_height))
            
            # Рисуем треугольник
            self._draw_triangle()
            
        except Exception as e:
            app_logger.error(f"Failed to redraw canvas: {e}")
    
    def _draw_triangle(self):
        """Отрисовать треугольник на холсте"""
        vertices = self.triangle_manager.vertices
        
        if len(vertices) < 2:
            # Рисуем только точки
            for i, vertex in enumerate(vertices):
                self._draw_vertex(vertex, i)
        elif len(vertices) == 2:
            # Рисуем линию и две точки
            self.canvas.create_line(
                vertices[0][0], vertices[0][1],
                vertices[1][0], vertices[1][1],
                fill=COLOR_TRIANGLE,
                width=LINE_WIDTH
            )
            for i, vertex in enumerate(vertices):
                self._draw_vertex(vertex, i)
        else:
            # Рисуем полный треугольник
            for i in range(3):
                start = vertices[i]
                end = vertices[(i + 1) % 3]
                self.canvas.create_line(
                    start[0], start[1], end[0], end[1],
                    fill=COLOR_TRIANGLE,
                    width=LINE_WIDTH
                )
            
            for i, vertex in enumerate(vertices):
                self._draw_vertex(vertex, i)
            
            # Отрисовываем подписи сторон (размеры в px и м)
            self._draw_side_labels()
    
    def _draw_vertex(self, vertex, index):
        """
        Отрисовать вершину треугольника.
        
        Args:
            vertex: Координаты вершины (x, y)
            index: Индекс вершины
        """
        x, y = vertex
        color = COLOR_HOVER if index == self.hovered_vertex else COLOR_VERTEX
        
        self.canvas.create_oval(
            x - VERTEX_RADIUS, y - VERTEX_RADIUS,
            x + VERTEX_RADIUS, y + VERTEX_RADIUS,
            fill=color,
            outline=COLOR_TRIANGLE
        )
    
    def _draw_side_labels(self):
        """
        Отрисовать подписи сторон треугольника (размеры в px и м).
        """
        if not self.info_panel:
            return
        
        vertices = self.triangle_manager.vertices
        if len(vertices) < 3:
            return
        
        # Получаем информацию о сторонах
        pixel_size = self.info_panel.get_pixel_size()
        scale_factor = self.get_scale_factor()
        self.triangle_manager._update_sides(pixel_size, scale_factor)
        sides = self.triangle_manager.sides
        
        if len(sides) < 3:
            return
        
        # Названия сторон
        side_names = ['AB', 'BC', 'CA']
        
        for i in range(3):
            # Координаты середины стороны
            start = vertices[i]
            end = vertices[(i + 1) % 3]
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            
            # Текст с размерами
            length_px = sides[i]['length_px']
            length_m = sides[i]['length_m']
            label_text = f"{side_names[i]}: {length_px:.0f}px\n ({length_m:.2f}м)"
            
            # Вычисляем смещение для текста (перпендикулярно стороне)
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
                # Нормализованный перпендикулярный вектор
                perp_x = -dy / length
                perp_y = dx / length
                
                # Смещение текста от линии
                offset = 15
                text_x = mid_x + perp_x * offset
                text_y = mid_y + perp_y * offset
                
                # Рисуем текст с белым фоном
                self.canvas.create_text(
                    text_x, text_y,
                    text=label_text,
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor="center"
                )
    
    def find_vertex_at(self, x, y):
        """
        Найти вершину треугольника в указанной точке.
        
        Args:
            x, y: Координаты точки
            
        Returns:
            Индекс вершины или None
        """
        for i, vertex in enumerate(self.triangle_manager.vertices):
            vx, vy = vertex
            distance = ((x - vx) ** 2 + (y - vy) ** 2) ** 0.5
            if distance <= VERTEX_RADIUS:
                return i
        return None
    
    def set_hovered_vertex(self, index):
        """
        Установить индекс вершины под курсором.
        
        Args:
            index: Индекс вершины или None
        """
        if self.hovered_vertex != index:
            self.hovered_vertex = index
            self.redraw()
    
    def start_drag(self, vertex_index):
        """
        Начать перетаскивание вершины.
        
        Args:
            vertex_index: Индекс перетаскиваемой вершины
        """
        self.dragging_vertex = vertex_index
    
    def drag_vertex(self, x, y):
        """
        Обновить позицию перетаскиваемой вершины.
        
        Args:
            x, y: Новые координаты
        """
        if self.dragging_vertex is not None:
            self.triangle_manager.update_vertex(self.dragging_vertex, x, y)  # Передаём x и y отдельно
    
    def stop_drag(self):
        """Завершить перетаскивание вершины"""
        self.dragging_vertex = None
    
    def zoom_in(self):
        """Увеличить масштаб"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.redraw()
    
    def zoom_out(self):
        """Уменьшить масштаб"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.redraw()
    
    def resize_to_canvas(self):
        """
        Пересчитать размер изображения под текущий размер холста.
        Сохраняет пропорции и относительные позиции вершин треугольника.
        """
        if not self.original_pil_image:
            return
        
        # Сохраняем текущие вершины в относительных координатах
        relative_vertices = []
        if self.current_image_size and len(self.triangle_manager.vertices) > 0:
            for x, y in self.triangle_manager.vertices:
                rel_x = x / self.current_image_size[0]
                rel_y = y / self.current_image_size[1]
                relative_vertices.append((rel_x, rel_y))
        
        # Получаем новый размер холста
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Вычисляем размер изображения, сохраняя пропорции
        img_width, img_height = self.original_pil_image.size
        
        # Вычисляем коэффициенты масштабирования
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        scale = min(scale_w, scale_h)
        
        # Вычисляем новый базовый размер
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Обновляем базовый размер
        self.base_image_size = (new_width, new_height)
        
        app_logger.info(
            f"Canvas resized: Image rescaled from base {self.current_image_size} to {new_width}x{new_height} "
            f"(canvas: {canvas_width}x{canvas_height}, zoom: {self.zoom_level:.2f})"
        )
        
        # Перерисовываем с текущим zoom
        self.redraw()
        
        # Восстанавливаем вершины в новых координатах
        if relative_vertices:
            new_vertices = []
            for rel_x, rel_y in relative_vertices:
                new_x = rel_x * self.current_image_size[0]
                new_y = rel_y * self.current_image_size[1]
                new_vertices.append((new_x, new_y))
            
            # Обновляем вершины треугольника
            self.triangle_manager.vertices = new_vertices
            
            # Перерисовываем еще раз с новыми вершинами
            self.redraw()
    
    def get_scale_factor(self):
        """
        Получить коэффициент масштаба от отображаемого к оригинальному изображению.
        
        Returns:
            Коэффициент масштаба
        """
        if self.original_image_size and self.current_image_size:
            return self.original_image_size[0] / self.current_image_size[0]
        return 1.0
