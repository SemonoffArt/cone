"""
Главное окно приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from .menu import Menu
from .toolbar import Toolbar
from .info_panel import InfoPanel
from core.image_loader import ImageLoader
from core.triangle import TriangleManager
from core.cone_calculator import ConeCalculator
from utils.constants import *
from utils.config import Config
from utils.logger import app_logger
from utils.trassir import Trassir
from PIL import Image, ImageTk


class MainWindow:
    def __init__(self):
        app_logger.info("Initializing main window")
        self.root = tk.Tk()
        self.root.title("Конус - расчёт объёма конуса руды на складе")
        self.root.geometry("1200x700")
        # self.root.iconbitmap(default="./resources/icons/icon.ico")
        self.root.iconbitmap(default="./resources/icons/pavlik_logo.ico")
        
        # Инициализация компонентов
        self.config = Config()
        self.triangle_manager = TriangleManager()
        self.triangle_manager.add_listener(self)

        self.current_image = None
        self.image_path = None
        self.dragging_vertex = None
        self.trassir_image = None
        self.zoom_level = 1.0
        self.original_pil_image = None  # Сохраняем оригинальное изображение PIL
        # Базовый размер изображения (при zoom=1.0)
        self.base_image_size = None
        self.current_image_size = None  # Текущий размер отображаемого изображения
        self.original_image_size = None  # Размер оригинального изображения

        self._setup_ui()
        self._setup_bindings()
        # Инициализируем trassir как None, подключение будет установлено при первом использовании
        self.trassir = None
        app_logger.info("Main window initialized successfully")

        # Автоматическая загрузка скриншота Конус ЗИФ1 при запуске
        self.root.after(500, self.load_cone_zif1)

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Меню
        self.menu = Menu(self.root, self)

        # Панель инструментов (Toolbar)
        self.toolbar = Toolbar(self.root, self)
        self.toolbar.pack(side='top', fill='x', padx=5, pady=(5,0))

        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=(0, 5))

        # Область изображения
        image_frame = ttk.LabelFrame(main_frame, text="")
        image_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Создаем полосы прокрутки
        self.h_scrollbar = tk.Scrollbar(image_frame, orient='horizontal')
        self.h_scrollbar.pack(side='bottom', fill='x')

        self.v_scrollbar = tk.Scrollbar(image_frame, orient='vertical')
        self.v_scrollbar.pack(side='right', fill='y')

        self.canvas = tk.Canvas(
            image_frame,
            bg=COLOR_BG,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.canvas.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        # Привязываем полосы прокрутки к canvas
        self.h_scrollbar.config(command=self.canvas.xview)
        self.v_scrollbar.config(command=self.canvas.yview)

        # Панель информации
        self.info_panel = InfoPanel(main_frame)
        self.info_panel.pack(side='right', fill='y', padx=(10, 0))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')

    def _setup_bindings(self):
        """Настройка обработчиков событий"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

        # Обновление при изменении размера пикселя
        self.info_panel.pixel_size_var_zif1.trace(
            'w', self.on_pixel_size_changed)

        # Горячие клавиши для масштабирования
        self.root.bind("<plus>", lambda e: self.zoom_in())  # +
        # = (тоже + без Shift)
        self.root.bind("<equal>", lambda e: self.zoom_in())
        self.root.bind("<minus>", lambda e: self.zoom_out())  # -
        # + на цифровой клавиатуре
        self.root.bind("<KP_Add>", lambda e: self.zoom_in())
        # - на цифровой клавиатуре
        self.root.bind("<KP_Subtract>", lambda e: self.zoom_out())

        # Обработка изменения размера окна
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def _setup_trassir(self, trassir_ip='10.100.59.11'):
        """Настройка подключения к Trassir"""
        try:
            self.trassir = Trassir(ip=trassir_ip)
        except Exception as e:
            app_logger.error(f"Failed to initialize Trassir connection: {e}")
            self.trassir = None

    def _on_trassir_click(self, button_type='ZIF1'):
        """Обработка нажатия на кнопку Trassir"""
        if button_type == 'ZIF1':
            # Используем IP и имя канала из конфигурации
            trassir_ip = CAM_CONE_ZIF1["trassir_ip"]
            channel_name = CAM_CONE_ZIF1["chanel_name"]
            pixel_size_m = CAM_CONE_ZIF1["pixel_size_m"]
            self._setup_trassir(trassir_ip)
            self._load_trassir_screenshot(channel_name, pixel_size_m)
        elif button_type == 'ZIF2':
            # Используем IP и имя канала из конфигурации
            trassir_ip = CAM_CONE_ZIF2["trassir_ip"]
            channel_name = CAM_CONE_ZIF2["chanel_name"]
            pixel_size_m = CAM_CONE_ZIF2["pixel_size_m"]
            self._setup_trassir(trassir_ip)
            self._load_trassir_screenshot(channel_name, pixel_size_m)
        else:
            # По умолчанию загружаем скриншот для ЗИФ1
            trassir_ip = CAM_CONE_ZIF1["trassir_ip"]
            channel_name = CAM_CONE_ZIF1["chanel_name"]
            pixel_size_m = CAM_CONE_ZIF1["pixel_size_m"]
            self._setup_trassir(trassir_ip)
            self._load_trassir_screenshot(channel_name, pixel_size_m)

    def on_canvas_click(self, event):
        """Обработка клика на canvas"""
        if not self.current_image:
            self.status_var.set("Сначала загрузите изображение")
            return

        # Преобразуем координаты с учетом прокрутки
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # Проверяем, не кликаем ли на существующую вершину
        vertex_index = self.triangle_manager.get_vertex_at_position(
            canvas_x, canvas_y)
        if vertex_index is not None:
            self.dragging_vertex = vertex_index
            return

        # Добавляем новую вершину
        self.triangle_manager.add_vertex(canvas_x, canvas_y)
        self.redraw_canvas()

        if self.triangle_manager.is_complete():
            self.status_var.set(
                "Треугольник построен. Можно перемещать вершины")
        else:
            self.status_var.set(
                f"Добавлена вершина {len(self.triangle_manager.vertices)}/3")

    def on_canvas_drag(self, event):
        """Обработка перетаскивания на canvas"""
        if self.dragging_vertex is not None and self.current_image:
            # Преобразуем координаты с учетом прокрутки
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            self.triangle_manager.update_vertex(
                self.dragging_vertex, canvas_x, canvas_y)
            self.redraw_canvas()

    def on_canvas_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.dragging_vertex = None

    def on_canvas_motion(self, event):
        """Обработка движения мыши над canvas"""
        if not self.current_image:
            return

        # Преобразуем координаты с учетом прокрутки
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # Изменение курсора при наведении на вершину
        vertex_index = self.triangle_manager.get_vertex_at_position(
            canvas_x, canvas_y)
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

    def on_canvas_resize(self, event):
        """Обработка изменения размера canvas"""
        if not self.original_pil_image:
            return

        # Проверяем, что размер действительно изменился
        if event.width > 1 and event.height > 1:
            # Пересчитываем базовый размер и применяем текущий zoom
            self._recalculate_image_size()

    def on_triangle_changed(self):
        """Обработка изменения треугольника"""
        self.redraw_canvas()

        # Обновление информации
        pixel_size = self.info_panel.get_pixel_size()

        # Вычисляем коэффициент масштаба (от отображаемого к оригиналу)
        scale_factor = 1.0
        if self.original_image_size and self.current_image_size:
            scale_factor = self.original_image_size[0] / \
                self.current_image_size[0]

        # Обновление информации о треугольниках с учетом масштаба
        self.triangle_manager._update_sides(pixel_size, scale_factor)
        self.info_panel.update_triangle_info(self.triangle_manager.sides)

        # Расчет и обновление информации о конусе
        if self.triangle_manager.is_complete():
            cone_params = ConeCalculator.get_cone_parameters(
                self.triangle_manager.vertices,
                pixel_size,
                scale_factor
            )
            self.info_panel.update_cone_info(cone_params)

    def redraw_canvas(self):
        """Перерисовка canvas"""
        self.canvas.delete("all")

        # Отображение изображения
        if self.current_image:
            self.canvas.create_image(
                0, 0, anchor='nw', image=self.current_image)
            # Устанавливаем область прокрутки
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

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

    def load_cone_zif1(self):
        """Загрузка скриншота для Конус ЗИФ1"""
        self._on_trassir_click('ZIF1')

    def load_cone_zif2(self):
        """Загрузка скриншота для Конус ЗИФ2"""
        self._on_trassir_click('ZIF2')

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

                # Загружаем оригинальное изображение
                from PIL import Image
                self.original_pil_image = Image.open(file_path)
                self.original_image_size = self.original_pil_image.size  # Сохраняем размер оригинала
                self.zoom_level = 1.0

                # Масштабируем для первоначального отображения
                canvas_width = self.canvas.winfo_width() or CANVAS_WIDTH
                canvas_height = self.canvas.winfo_height() or CANVAS_HEIGHT

                display_image = self.original_pil_image.copy()
                display_image.thumbnail(
                    (canvas_width, canvas_height), Image.Resampling.LANCZOS)
                self.current_image = ImageTk.PhotoImage(display_image)
                image_size = display_image.size

                # Сохраняем базовый и текущий размеры
                self.base_image_size = image_size
                self.current_image_size = image_size

                self.redraw_canvas()
                self.status_var.set(
                    f"Загружено: {os.path.basename(file_path)} ({image_size[0]}x{image_size[1]})")
                app_logger.info(
                    f"Image loaded successfully: {os.path.basename(file_path)} ({image_size[0]}x{image_size[1]})")

                # Обновляем информацию об изображении
                self._update_image_info()
                
                # Подстраиваем размер окна под изображение (масштаб 100%)
                self._adjust_window_size()

            except Exception as e:
                app_logger.error(f"Failed to load image: {str(e)}")
                messagebox.showerror(
                    "Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def save_image(self):
        """Сохранение текущего изображения"""
        if not self.original_pil_image:
            messagebox.showwarning(
                "Предупреждение", "Нет загруженного изображения для сохранения")
            return

        app_logger.info("Opening save image dialog")

        # Определяем формат по умолчанию
        default_extension = ".png"
        if self.image_path:
            # Если изображение было загружено из файла, используем его расширение
            default_extension = os.path.splitext(self.image_path)[1]
            default_name = os.path.basename(self.image_path)
        else:
            # Для Trassir скриншотов
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"screenshot_{timestamp}.png"

        # Диалог сохранения
        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            initialfile=default_name,
            defaultextension=default_extension,
            filetypes=[
                ("Все поддерживаемые", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("GIF", "*.gif"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                app_logger.info(f"Saving image to: {file_path}")
                # Сохраняем оригинальное изображение в исходном разрешении
                self.original_pil_image.save(file_path)
                self.status_var.set(
                    f"Изображение сохранено: {os.path.basename(file_path)}")
                app_logger.info(f"Image saved successfully: {file_path}")
                messagebox.showinfo(
                    "Успех", f"Изображение сохранено:\n{file_path}")
            except Exception as e:
                app_logger.error(f"Failed to save image: {str(e)}")
                messagebox.showerror(
                    "Ошибка", f"Не удалось сохранить изображение:\n{str(e)}")

    def _load_trassir_screenshot(self, channel_name, pixel_size_m=None):
        """Загрузка скриншота с Trassir и отображение его в canvas"""
        app_logger.info(
            f"Loading Trassir screenshot for channel: {channel_name}")

        if not self.trassir:
            app_logger.error("Trassir connection not initialized")
            messagebox.showerror(
                "Ошибка", "Подключение к Trassir не установлено")
            return

        try:
            # Получаем список каналов
            self.trassir.update_channels_cache()
            app_logger.debug(
                f"Available channels: {len(self.trassir.channels)}")

            # Извлекаем GUID канала по имени
            channel_info = self.trassir.get_channel_by_name(channel_name)
            if not channel_info:
                app_logger.error(f"Channel not found: {channel_name}")
                messagebox.showerror(
                    "Ошибка", f"Канал не найден: {channel_name}")
                return

            channel_guid = channel_info['guid']
            app_logger.info(
                f"Found channel {channel_name} with GUID: {channel_guid}")

            # Получаем скриншот канала
            screenshot = self.trassir.get_channel_screenshot(channel_guid)
            if not screenshot:
                app_logger.error(
                    f"Failed to get screenshot for channel: {channel_name}")
                messagebox.showerror(
                    "Ошибка", f"Не удалось получить скриншот канала: {channel_name}")
                return

            # Преобразуем PIL Image в PhotoImage для Tkinter
            # Масштабируем изображение под размер canvas
            canvas_width = self.canvas.winfo_width() or CANVAS_WIDTH
            canvas_height = self.canvas.winfo_height() or CANVAS_HEIGHT

            # Сохраняем оригинальное изображение
            self.original_pil_image = screenshot.copy()
            self.original_image_size = self.original_pil_image.size  # Сохраняем размер оригинала
            self.zoom_level = 1.0

            # Изменяем размер изображения
            screenshot = screenshot.resize(
                (canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.trassir_image = ImageTk.PhotoImage(screenshot)

            # Сохраняем базовый и текущий размеры
            self.base_image_size = (canvas_width, canvas_height)
            self.current_image_size = (canvas_width, canvas_height)

            # Устанавливаем изображение
            self.current_image = self.trassir_image
            self.image_path = None  # Не сохраняем путь для Trassir изображений

            # Устанавливаем размер пикселя если был передан
            if pixel_size_m is not None:
                self.info_panel.set_pixel_size(pixel_size_m)
                self.config.set_pixel_size(pixel_size_m)
                self.triangle_manager._update_sides(pixel_size_m)

            # Перерисовываем canvas
            self.redraw_canvas()
            self.status_var.set(f"Загружен скриншот: {channel_name}")
            app_logger.info(
                f"Successfully loaded screenshot for channel: {channel_name}")

            # Обновляем информацию об изображении
            self._update_image_info()
            
            # Подстраиваем размер окна под изображение (масштаб 100%)
            self._adjust_window_size()

        except Exception as e:
            app_logger.error(f"Error loading Trassir screenshot: {e}")
            messagebox.showerror(
                "Ошибка", f"Ошибка при загрузке скриншота:\n{str(e)}")

    def zoom_in(self):
        """Увеличение изображения"""
        if not self.original_pil_image:
            self.status_var.set("Сначала загрузите изображение")
            return

        self.zoom_level *= 1.2  # Увеличение на 20%
        self._apply_zoom()
        app_logger.info(f"Zoom in: {self.zoom_level:.2f}x")
        self.status_var.set(f"Масштаб: {self.zoom_level:.2f}x")
        self._update_image_info()  # Обновляем информацию

    def zoom_out(self):
        """Уменьшение изображения"""
        if not self.original_pil_image:
            self.status_var.set("Сначала загрузите изображение")
            return

        if self.zoom_level > 0.2:  # Минимальный зум 20%
            self.zoom_level /= 1.2  # Уменьшение на 20%
            self._apply_zoom()
            app_logger.info(f"Zoom out: {self.zoom_level:.2f}x")
            self.status_var.set(f"Масштаб: {self.zoom_level:.2f}x")
            self._update_image_info()  # Обновляем информацию

    def _apply_zoom(self):
        """Применение масштабирования к изображению"""
        if not self.original_pil_image or not self.base_image_size:
            return

        # Сохраняем текущие вершины треугольника в относительных координатах (0-1)
        if self.current_image_size and len(self.triangle_manager.vertices) > 0:
            relative_vertices = []
            for x, y in self.triangle_manager.vertices:
                rel_x = x / self.current_image_size[0]
                rel_y = y / self.current_image_size[1]
                relative_vertices.append((rel_x, rel_y))
        else:
            relative_vertices = []

        # Вычисляем новый размер
        new_width = int(self.base_image_size[0] * self.zoom_level)
        new_height = int(self.base_image_size[1] * self.zoom_level)

        # Создаем масштабированное изображение
        # Сначала масштабируем оригинал до базового размера, затем применяем zoom
        canvas_width = self.canvas.winfo_width() or CANVAS_WIDTH
        canvas_height = self.canvas.winfo_height() or CANVAS_HEIGHT

        # Получаем изображение, масштабированное до базового размера
        img_copy = self.original_pil_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height),
                           Image.Resampling.LANCZOS)

        # Теперь применяем zoom к этому размеру
        zoomed_width = int(img_copy.width * self.zoom_level)
        zoomed_height = int(img_copy.height * self.zoom_level)

        zoomed_image = self.original_pil_image.resize(
            (zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
        self.current_image = ImageTk.PhotoImage(zoomed_image)

        # Обновляем текущий размер
        self.current_image_size = (zoomed_width, zoomed_height)

        # Восстанавливаем вершины треугольника в новых координатах
        if relative_vertices:
            new_vertices = []
            for rel_x, rel_y in relative_vertices:
                new_x = rel_x * self.current_image_size[0]
                new_y = rel_y * self.current_image_size[1]
                new_vertices.append((new_x, new_y))

            # Обновляем вершины без уведомления слушателей
            self.triangle_manager.vertices = new_vertices
            # Вычисляем коэффициент масштаба
            scale_factor = 1.0
            if self.original_image_size and self.current_image_size:
                scale_factor = self.original_image_size[0] / \
                    self.current_image_size[0]
            self.triangle_manager._update_sides(
                self.info_panel.get_pixel_size(), scale_factor)

        # Перерисовываем
        self.redraw_canvas()

    def _recalculate_image_size(self):
        """Перерасчет размера изображения при изменении размера окна"""
        if not self.original_pil_image:
            return

        # Сохраняем текущие вершины в относительных координатах
        if self.current_image_size and len(self.triangle_manager.vertices) > 0:
            relative_vertices = []
            for x, y in self.triangle_manager.vertices:
                rel_x = x / self.current_image_size[0]
                rel_y = y / self.current_image_size[1]
                relative_vertices.append((rel_x, rel_y))
        else:
            relative_vertices = []

        # Получаем новый размер canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # Вычисляем новый базовый размер
        img_copy = self.original_pil_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height),
                           Image.Resampling.LANCZOS)

        # Обновляем базовый размер
        self.base_image_size = img_copy.size

        # Применяем текущий zoom
        zoomed_width = int(self.base_image_size[0] * self.zoom_level)
        zoomed_height = int(self.base_image_size[1] * self.zoom_level)

        zoomed_image = self.original_pil_image.resize(
            (zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
        self.current_image = ImageTk.PhotoImage(zoomed_image)

        # Обновляем текущий размер
        self.current_image_size = (zoomed_width, zoomed_height)

        # Восстанавливаем вершины в новых координатах
        if relative_vertices:
            new_vertices = []
            for rel_x, rel_y in relative_vertices:
                new_x = rel_x * self.current_image_size[0]
                new_y = rel_y * self.current_image_size[1]
                new_vertices.append((new_x, new_y))

            # Обновляем вершины
            self.triangle_manager.vertices = new_vertices
            # Вычисляем коэффициент масштаба
            scale_factor = 1.0
            if self.original_image_size and self.current_image_size:
                scale_factor = self.original_image_size[0] / \
                    self.current_image_size[0]
            self.triangle_manager._update_sides(
                self.info_panel.get_pixel_size(), scale_factor)

        # Перерисовываем
        self.redraw_canvas()

    def _update_image_info(self):
        """Обновление информации об изображении в панели"""
        if not self.original_pil_image:
            return

        # Определяем формат
        image_format = self.original_pil_image.format if self.original_pil_image.format else "Unknown"

        # Определяем источник
        if self.image_path:
            source = os.path.basename(self.image_path)
        else:
            source = "Trassir скриншот"

        image_info = {
            'original_size': self.original_image_size,
            'display_size': self.current_image_size,
            'format': image_format,
            'source': source,
            'zoom_level': self.zoom_level
        }

        self.info_panel.update_image_info(image_info)

    def _adjust_window_size(self):
        """Подстраивание размера окна под размер изображения при масштабе 100%"""
        if not self.original_image_size:
            return
        
        # Получаем параметры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Не делаем окно больше 70% экрана
        max_window_width = int(screen_width * 0.7)
        max_window_height = int(screen_height * 0.7)
        
        # Оригинальные размеры изображения
        img_width, img_height = self.original_image_size
        
        # Нужные значения для размера окна
        # Добавляем место для панели информации (правая сторона, около 250 пикселей)
        canvas_width = min(img_width, max_window_width - 300)
        canvas_height = min(img_height, max_window_height - 100)  # 100 для меню и статус бара
        
        # Общие размеры окна
        window_width = canvas_width + 320  # +320 для панели
        window_height = canvas_height + 100  # +100 для меню и статуса
        
        # Устанавливаем новые размеры
        self.root.geometry(f"{window_width}x{window_height}")
        app_logger.info(f"Window resized to {window_width}x{window_height} for image {img_width}x{img_height}")

    def clear_triangle(self):
        """Очистка треугольника"""
        self.triangle_manager.clear()
        self.redraw_canvas()
        self.status_var.set("Треугольник очищен")

    def copy_cone_volume(self):
        """Копирование объема конуса в буфер обмена"""
        if not self.triangle_manager.is_complete():
            messagebox.showwarning("Предупреждение", "Сначала постройте треугольник")
            return
        
        # Получаем параметры конуса
        pixel_size = self.info_panel.get_pixel_size()
        scale_factor = 1.0
        if self.original_image_size and self.current_image_size:
            scale_factor = self.original_image_size[0] / self.current_image_size[0]
        
        cone_params = ConeCalculator.get_cone_parameters(
            self.triangle_manager.vertices,
            pixel_size,
            scale_factor
        )
        
        if cone_params['volume'] > 0:
            volume_text = f"{cone_params['volume']:.2f}"
            # Заменяем точку на запятую для буфера
            volume_for_clipboard = volume_text.replace('.', ',')
            self.root.clipboard_clear()
            self.root.clipboard_append(volume_for_clipboard)
            self.root.update()  # Обновить буфер
            self.status_var.set(f"Объем скопирован: {volume_text} m³")
            app_logger.info(f"Cone volume copied to clipboard: {volume_for_clipboard} m³")
        else:
            messagebox.showwarning("Предупреждение", "Не удалось рассчитать объем")
    
    def show_about(self):
        """Показать информацию о программе"""
        from utils.constants import VERSION, APP_NAME, DESCRIPTION, GITHUB_URL, AUTHOR, WEBSITE, EMAIL
        about_text = f"""Cone App
Версия {VERSION}

{DESCRIPTION}.

GitHub:
{GITHUB_URL}

{AUTHOR}
{WEBSITE}
{EMAIL}
2025
"""
        messagebox.showinfo("О программе", about_text)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
