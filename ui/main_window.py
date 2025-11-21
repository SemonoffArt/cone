"""
Главное окно приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from .menu import Menu
from .info_panel import InfoPanel
from core.image_loader import ImageLoader
from core.triangle import TriangleManager
from core.cone_calculator import ConeCalculator
from utils.constants import *
from utils.config import Config
from utils.logger import app_logger

class MainWindow:
    def __init__(self):
        app_logger.info("Initializing main window")
        self.root = tk.Tk()
        self.root.title("Cone App - Построение треугольников и расчет конусов")
        self.root.geometry("1200x700")

        # Инициализация компонентов
        self.config = Config()
        self.triangle_manager = TriangleManager()
        self.triangle_manager.add_listener(self)

        self.current_image = None
        self.image_path = None
        self.dragging_vertex = None

        self._setup_ui()
        self._setup_bindings()
        app_logger.info("Main window initialized successfully")

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Меню
        self.menu = Menu(self.root, self)

        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Область изображения
        image_frame = ttk.LabelFrame(main_frame, text="Изображение")
        image_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(
            image_frame,
            bg=COLOR_BG,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT
        )
        self.canvas.pack(fill='both', expand=True, padx=5, pady=5)

        # Панель информации
        self.info_panel = InfoPanel(main_frame)
        self.info_panel.pack(side='right', fill='y', padx=(10, 0))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')

    def _setup_bindings(self):
        """Настройка обработчиков событий"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

        # Обновление при изменении размера пикселя
        self.info_panel.pixel_size_var.trace('w', self.on_pixel_size_changed)

    def on_canvas_click(self, event):
        """Обработка клика на canvas"""
        if not self.current_image:
            self.status_var.set("Сначала загрузите изображение")
            return

        # Проверяем, не кликаем ли на существующую вершину
        vertex_index = self.triangle_manager.get_vertex_at_position(event.x, event.y)
        if vertex_index is not None:
            self.dragging_vertex = vertex_index
            return

        # Добавляем новую вершину
        self.triangle_manager.add_vertex(event.x, event.y)
        self.redraw_canvas()

        if self.triangle_manager.is_complete():
            self.status_var.set("Треугольник построен. Можно перемещать вершины")
        else:
            self.status_var.set(f"Добавлена вершина {len(self.triangle_manager.vertices)}/3")

    def on_canvas_drag(self, event):
        """Обработка перетаскивания на canvas"""
        if self.dragging_vertex is not None and self.current_image:
            self.triangle_manager.update_vertex(self.dragging_vertex, event.x, event.y)
            self.redraw_canvas()

    def on_canvas_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.dragging_vertex = None

    def on_canvas_motion(self, event):
        """Обработка движения мыши над canvas"""
        if not self.current_image:
            return

        # Изменение курсора при наведении на вершину
        vertex_index = self.triangle_manager.get_vertex_at_position(event.x, event.y)
        if vertex_index is not None:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")

    def on_pixel_size_changed(self, *args):
        """Обработка изменения размера пикселя"""
        try:
            new_size = self.info_panel.get_pixel_size()
            if new_size > 0:
                self.config.set_pixel_size(new_size)
                self.triangle_manager._update_sides(new_size)
                self.on_triangle_changed()
        except ValueError:
            pass

    def on_triangle_changed(self):
        """Обработка изменения треугольника"""
        self.redraw_canvas()

        # Обновление информации
        pixel_size = self.info_panel.get_pixel_size()

        # Обновление информации о треугольниках
        self.info_panel.update_triangle_info(self.triangle_manager.sides)

        # Расчет и обновление информации о конусе
        if self.triangle_manager.is_complete():
            cone_params = ConeCalculator.get_cone_parameters(
                self.triangle_manager.vertices,
                pixel_size
            )
            self.info_panel.update_cone_info(cone_params)

    def redraw_canvas(self):
        """Перерисовка canvas"""
        self.canvas.delete("all")

        # Отображение изображения
        if self.current_image:
            self.canvas.create_image(0, 0, anchor='nw', image=self.current_image)

        # Отображение треугольника
        vertices = self.triangle_manager.vertices

        # Рисуем линии треугольника
        if len(vertices) >= 2:
            for i in range(len(vertices)):
                j = (i + 1) % len(vertices)
                x1, y1 = vertices[i]
                x2, y2 = vertices[j]

                # Линия
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=COLOR_TRIANGLE,
                    width=LINE_WIDTH,
                    tags="triangle"
                )

                # Текст с размером стороны (если есть данные)
                if i < len(self.triangle_manager.sides):
                    side = self.triangle_manager.sides[i]
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2

                    # Смещаем текст от линии для лучшей читаемости
                    text_x = mid_x + 10
                    text_y = mid_y + 10

                    self.canvas.create_text(
                        text_x, text_y,
                        text=f"{side['length_px']:.1f}px\n({side['length_m']:.4f}m)",
                        fill=COLOR_TEXT,
                        font=TEXT_FONT,
                        tags="triangle_text"
                    )

        # Рисуем вершины
        for i, (x, y) in enumerate(vertices):
            color = COLOR_HOVER if i == self.dragging_vertex else COLOR_VERTEX
            self.canvas.create_oval(
                x - VERTEX_RADIUS, y - VERTEX_RADIUS,
                x + VERTEX_RADIUS, y + VERTEX_RADIUS,
                fill=color,
                outline=COLOR_TRIANGLE,
                width=2,
                tags="vertex"
            )

    def open_image(self):
        """Открытие изображения"""
        app_logger.info("Opening image dialog")
        file_types = ImageLoader.get_supported_formats()

        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=file_types
        )

        if file_path:
            try:
                app_logger.info(f"Loading image: {file_path}")
                self.image_path = file_path
                self.current_image, image_size = ImageLoader.load_image(
                    file_path,
                    self.canvas.winfo_width() or CANVAS_WIDTH,
                    self.canvas.winfo_height() or CANVAS_HEIGHT
                )

                # Очищаем треугольник при загрузке нового изображения
                self.triangle_manager.clear()

                self.redraw_canvas()
                self.status_var.set(f"Загружено: {os.path.basename(file_path)} ({image_size[0]}x{image_size[1]})")
                app_logger.info(f"Image loaded successfully: {os.path.basename(file_path)} ({image_size[0]}x{image_size[1]})")

            except Exception as e:
                app_logger.error(f"Failed to load image: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def clear_triangle(self):
        """Очистка треугольника"""
        self.triangle_manager.clear()
        self.redraw_canvas()
        self.status_var.set("Треугольник очищен")

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()