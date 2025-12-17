"""
Главное окно приложения (Refactored)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os

from .menu import Menu
from .toolbar import Toolbar
from .info_panel import InfoPanel
from .canvas_handler import CanvasHandler
from .image_handler import ImageHandler
from .trassir_handler import TrassirHandler
from .save_handler import SaveHandler
from core.triangle import TriangleManager
from core.cone_calculator import ConeCalculator
from core.vision import auto_detect_triangle
from utils.constants import COLOR_BG, CANVAS_WIDTH, CANVAS_HEIGHT
from utils.config import Config
from utils.logger import app_logger
from utils.resources import get_resource_path


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        app_logger.info("Initializing main window")
        
        # Создание главного окна
        self.root = tk.Tk()
        self.root.title("Конус - расчёт объёма конуса руды на складе")
        
        # Вычисляем размер окна на основе CANVAS_WIDTH и CANVAS_HEIGHT
        # + 320 для правой панели информации
        # + 20 для отступов
        # + 100 для меню, toolbar и статус-бара
        window_width = CANVAS_WIDTH + 320 + 20
        window_height = CANVAS_HEIGHT + 100
        self.root.geometry(f"{window_width}x{window_height}")
        
        self._set_window_icon()
        
        # Инициализация компонентов
        self.config = Config()
        self.triangle_manager = TriangleManager()
        self.triangle_manager.add_listener(self)
        
        # Создание UI
        self._setup_ui()
        self._setup_handlers()
        self._setup_bindings()
        
        app_logger.info("Main window initialized successfully")
        
        # Автоматическая загрузка скриншота Конус ЗИФ1 при запуске
        self.root.after(500, self.load_cone_zif1)
    
    def _set_window_icon(self):
        """Установить иконку окна"""
        try:
            icon_path = get_resource_path("resources/icons/pavlik_logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
            else:
                app_logger.warning(f"Icon file not found: {icon_path}")
        except Exception as e:
            app_logger.warning(f"Failed to set window icon: {e}")
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Меню
        self.menu = Menu(self.root, self)
        
        # Панель инструментов
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
        
        # Холст
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
        self.info_panel = InfoPanel(main_frame, config=self.config)
        self.info_panel.pack(side='right', fill='y', padx=(0, 0))
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief='sunken'
        )
        status_bar.pack(side='bottom', fill='x')
    
    def _setup_handlers(self):
        """Инициализация обработчиков"""
        # Canvas handler
        self.canvas_handler = CanvasHandler(self.canvas, self.triangle_manager, self.info_panel)
        
        # Image handler
        self.image_handler = ImageHandler(
            self.canvas_handler, 
            self.info_panel, 
            self.status_var
        )
        
        # Trassir handler
        self.trassir_handler = TrassirHandler(
            self.config,
            self.image_handler,
            self.info_panel
        )
        
        # Save handler
        self.save_handler = SaveHandler(
            self.canvas_handler,
            self.image_handler,
            self.triangle_manager,
            self.info_panel,
            self.status_var
        )
    
    def _setup_bindings(self):
        """Настройка обработчиков событий"""
        # События холста
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Обновление информации при изменении параметров
        self.info_panel.pixel_size_var_zif1.trace('w', self.on_pixel_size_changed)
        self.info_panel.k_vol_var.trace('w', lambda *args: self.on_triangle_changed())
        self.info_panel.k_den_var.trace('w', lambda *args: self.on_triangle_changed())
        
        # Горячие клавиши для масштабирования
        self.root.bind("<plus>", lambda e: self.zoom_in())
        self.root.bind("<equal>", lambda e: self.zoom_in())
        self.root.bind("<minus>", lambda e: self.zoom_out())
        self.root.bind("<KP_Add>", lambda e: self.zoom_in())
        self.root.bind("<KP_Subtract>", lambda e: self.zoom_out())
    
    # ==================== Обработчики событий холста ====================
    
    def on_canvas_click(self, event):
        """Обработка клика по холсту"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Проверяем, кликнули ли на вершину
        vertex_index = self.canvas_handler.find_vertex_at(x, y)
        
        if vertex_index is not None:
            # Начинаем перетаскивание вершины
            self.canvas_handler.start_drag(vertex_index)
        else:
            # Добавляем новую вершину
            if not self.triangle_manager.is_complete():
                self.triangle_manager.add_vertex(x, y)  # Передаём x и y отдельно
                vertex_count = len(self.triangle_manager.vertices)
                self.status_var.set(f"Добавлена вершина {vertex_count}/3")
                
                if self.triangle_manager.is_complete():
                    self.status_var.set("Треугольник построен")
    
    def on_canvas_drag(self, event):
        """Обработка перетаскивания на холсте"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas_handler.drag_vertex(x, y)
    
    def on_canvas_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.canvas_handler.stop_drag()
    
    def on_canvas_motion(self, event):
        """Обработка движения мыши над холстом"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        vertex_index = self.canvas_handler.find_vertex_at(x, y)
        self.canvas_handler.set_hovered_vertex(vertex_index)
        
        # Изменяем курсор при наведении на вершину
        if vertex_index is not None:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")
    
    def on_canvas_resize(self, event):
        """Обработка изменения размера холста"""
        # Проверяем, что размер действительно изменился
        if event.width > 1 and event.height > 1:
            # Пересчитываем размер изображения
            self.canvas_handler.resize_to_canvas()
            self._update_zoom_info()
    
    # ==================== Обработчики изменений ====================
    
    def on_triangle_changed(self):
        """Обработка изменения треугольника"""
        self.canvas_handler.redraw()
        
        # Обновление информации
        pixel_size = self.info_panel.get_pixel_size()
        scale_factor = self.canvas_handler.get_scale_factor()
        
        # Обновление информации о треугольниках
        self.triangle_manager._update_sides(pixel_size, scale_factor)
        self.info_panel.update_triangle_info(self.triangle_manager.sides)
        
        # Расчет и обновление информации о конусе
        if self.triangle_manager.is_complete():
            k_vol = self.info_panel.get_k_vol()
            cone_params = ConeCalculator.get_cone_parameters(
                self.triangle_manager.vertices,
                pixel_size,
                scale_factor,
                k_vol
            )
            self.info_panel.update_cone_info(cone_params)
    
    def on_pixel_size_changed(self, *args):
        """Обработка изменения размера пикселя"""
        self.on_triangle_changed()
    
    # ==================== Публичные методы ====================
    
    def run(self):
        """Запустить главный цикл приложения"""
        self.root.mainloop()
    
    def open_image(self):
        """Открыть изображение из файла"""
        self.image_handler.open_image()
    
    def save_image(self):
        """Сохранить изображение"""
        current_cone_type = self.trassir_handler.get_current_cone_type()
        self.save_handler.save_image(current_cone_type)
    
    def load_cone_zif1(self):
        """Загрузить скриншот конуса ЗИФ1"""
        self.trassir_handler.load_cone_screenshot("ZIF1")
    
    def load_cone_zif2(self):
        """Загрузить скриншот конуса ЗИФ2"""
        self.trassir_handler.load_cone_screenshot("ZIF2")
    
    def zoom_in(self):
        """Увеличить масштаб"""
        self.canvas_handler.zoom_in()
        self._update_zoom_info()
    
    def zoom_out(self):
        """Уменьшить масштаб"""
        self.canvas_handler.zoom_out()
        self._update_zoom_info()
    
    def clear_triangle(self):
        """Очистить треугольник"""
        self.triangle_manager.clear()
        self.canvas_handler.redraw()
        self.status_var.set("Треугольник очищен")
        app_logger.info("Triangle cleared")
    
    def auto_build_triangle(self):
        """Автоматически построить треугольник"""
        current_image = self.image_handler.get_current_image()
        
        if not current_image:
            messagebox.showwarning(
                "Предупреждение",
                "Сначала загрузите изображение"
            )
            return
        
        current_cone_type = self.trassir_handler.get_current_cone_type()
        
        if not current_cone_type:
            messagebox.showwarning(
                "Предупреждение",
                "Автоопределение работает только для снимков с Trassir (ЗИФ1 или ЗИФ2)"
            )
            return
        
        try:
            app_logger.info(f"Auto-building triangle for {current_cone_type}")
            self.status_var.set("Автоматическое построение треугольника...")
            
            # Получаем порог бинаризации
            threshold = self.info_panel.get_threshold()
            
            # Получаем конфигурацию камеры
            cam_config = self.config.get(f"CAM_CONE_{current_cone_type}", {})
            
            # Запускаем автоопределение
            vertices = auto_detect_triangle(
                current_image,
                current_cone_type,
                threshold,
                cam_config
            )
            
            if vertices:
                # Очищаем старый треугольник
                self.triangle_manager.clear()
                
                # Преобразуем координаты с учётом масштаба изображения
                # auto_detect_triangle() возвращает координаты для оригинального изображения
                original_size = self.canvas_handler.original_image_size
                current_size = self.canvas_handler.current_image_size
                
                if original_size and current_size:
                    # Вычисляем коэффициент масштаба (от оригинала к отображаемому)
                    scale_x = current_size[0] / original_size[0]
                    scale_y = current_size[1] / original_size[1]
                    
                    app_logger.info(
                        f"Scaling vertices from {original_size} to {current_size} "
                        f"(scale_x: {scale_x:.3f}, scale_y: {scale_y:.3f})"
                    )
                    
                    # Добавляем масштабированные вершины
                    for vertex in vertices:
                        x_orig, y_orig = vertex
                        x_scaled = x_orig * scale_x
                        y_scaled = y_orig * scale_y
                        self.triangle_manager.add_vertex(x_scaled, y_scaled)
                        app_logger.debug(f"Vertex: ({x_orig:.0f}, {y_orig:.0f}) -> ({x_scaled:.0f}, {y_scaled:.0f})")
                else:
                    # Если нет информации о размерах, используем координаты как есть
                    for vertex in vertices:
                        x, y = vertex
                        self.triangle_manager.add_vertex(x, y)
                
                self.status_var.set("Треугольник построен автоматически")
                app_logger.info("Triangle auto-built successfully")
            else:
                self.status_var.set("Не удалось автоматически определить треугольник")
                messagebox.showwarning(
                    "Предупреждение",
                    "Не удалось автоматически определить контур конуса.\n"
                    "Попробуйте построить треугольник вручную."
                )
        
        except Exception as e:
            app_logger.error(f"Failed to auto-build triangle: {str(e)}")
            messagebox.showerror(
                "Ошибка",
                f"Ошибка при автоматическом построении:\n{str(e)}"
            )
            self.status_var.set("Ошибка автопостроения")
    
    def copy_cone_volume(self):
        """Скопировать объём и массу конуса в буфер обмена"""
        if not self.triangle_manager.is_complete():
            messagebox.showwarning(
                "Предупреждение",
                "Сначала постройте треугольник"
            )
            return
        
        try:
            # Получаем параметры
            pixel_size = self.info_panel.get_pixel_size()
            k_vol = self.info_panel.get_k_vol()
            k_den = self.info_panel.get_k_den()
            scale_factor = self.canvas_handler.get_scale_factor()
            
            # Вычисляем параметры конуса
            cone_params = ConeCalculator.get_cone_parameters(
                self.triangle_manager.vertices,
                pixel_size,
                scale_factor,
                k_vol
            )
            
            volume = cone_params['volume']
            mass = volume * k_den
            
            # Форматируем для Excel (запятая как разделитель, табуляция между значениями)
            clipboard_text = f"{volume:.2f}\t{mass:.2f}".replace('.', ',')
            
            # Копируем в буфер обмена
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            self.root.update()
            
            self.status_var.set(f"Скопировано: Объём={volume:.2f} м³, Масса={mass:.2f} т")
            app_logger.info(f"Copied to clipboard: {clipboard_text}")
            
        except Exception as e:
            app_logger.error(f"Failed to copy cone volume: {str(e)}")
            messagebox.showerror(
                "Ошибка",
                f"Ошибка при копировании:\n{str(e)}"
            )
    
    def _update_zoom_info(self):
        """Обновить информацию о масштабе"""
        current_image = self.image_handler.get_current_image()
        if current_image:
            # Получаем текущий источник из лейбла
            source_text = self.info_panel.image_source_label.cget("text")
            source = source_text.replace("Источник: ", "") if source_text else "Unknown"
            
            image_info = {
                'original_size': current_image.size,
                'display_size': self.canvas_handler.current_image_size,
                'format': current_image.format if current_image.format else "Unknown",
                'source': source,
                'zoom_level': self.canvas_handler.zoom_level
            }
            self.info_panel.update_image_info(image_info)
