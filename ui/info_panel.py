"""
Панель информации
"""
import tkinter as tk
from tkinter import ttk
from utils.logger import app_logger


class InfoPanel:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Информация", padding=10)
        self._create_widgets()
        # Callback for Trassir load button (set by MainWindow)
        self._trassir_callback = None

        # Данные для отображения
        self.side_vars = {
            'AB': tk.StringVar(value="Сторона AB: -"),
            'BC': tk.StringVar(value="Сторона BC: -"),
            'CA': tk.StringVar(value="Сторона CA: -")
        }
        self.volume_var = tk.StringVar(value="Объем: -")
        self.parameters_var = tk.StringVar(value="Параметры конуса: -")

    def _create_widgets(self):
        """Создание виджетов панели"""

        # Информация о конусе
        ttk.Label(self.frame, text="Конус:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.volume_label = ttk.Label(self.frame, text="Объем: -", font=('Arial', 15, 'bold'))
        self.volume_label.pack(anchor='w', pady=2)

        self.parameters_label = ttk.Label(self.frame, text="Параметры конуса: -")
        self.parameters_label.pack(anchor='w', pady=2)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        # Метки для сторон треугольника
        ttk.Label(self.frame, text="Треугольник:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.side_labels = []
        for i in range(3):
            label = ttk.Label(self.frame, text=f"Сторона {chr(65 + i)}: -")
            label.pack(anchor='w', pady=2)
            self.side_labels.append(label)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        # Настройка размера пикселя ZIF1
        pixel_frame_zif1 = ttk.Frame(self.frame)
        pixel_frame_zif1.pack(fill='x', pady=5)

        ttk.Label(pixel_frame_zif1, text="Размер пикселя (м):").pack(side='left')
        self.pixel_size_var_zif1 = tk.StringVar(value="0.1")
        self.pixel_size_entry_zif1 = ttk.Entry(pixel_frame_zif1, textvariable=self.pixel_size_var_zif1, width=8)
        self.pixel_size_entry_zif1.pack(side='left', padx=5)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        # Информация об изображении
        ttk.Label(self.frame, text="Изображение:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.image_size_label = ttk.Label(self.frame, text="Размер: -")
        self.image_size_label.pack(anchor='w', pady=2)
        
        self.image_format_label = ttk.Label(self.frame, text="Формат: -")
        self.image_format_label.pack(anchor='w', pady=2)
        
        self.image_source_label = ttk.Label(self.frame, text="Источник: -")
        self.image_source_label.pack(anchor='w', pady=2)
        
        self.display_size_label = ttk.Label(self.frame, text="Отображение: -")
        self.display_size_label.pack(anchor='w', pady=2)
        
        self.zoom_label = ttk.Label(self.frame, text="Масштаб: 100%")
        self.zoom_label.pack(anchor='w', pady=2)
        
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)
        # Кнопки загрузки с Trassir
        ttk.Label(self.frame, text="Загрузить с Trassir:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        # Кнопка загрузки с Trassir (внешний обработчик устанавливается через set_trassir_callback)
        self.get_screen_cone_zif1_button = ttk.Button(self.frame, text="Конус ЗИФ1", command=self._on_trassir1_click)
        self.get_screen_cone_zif1_button.pack(fill='x', pady=8)

        # Кнопка загрузки с Trassir (внешний обработчик устанавливается через set_trassir_callback)
        self.get_screen_cone_zif2_button = ttk.Button(self.frame, text="Конус ЗИФ2", command=self._on_trassir2_click)
        self.get_screen_cone_zif2_button.pack(fill='x', pady=8)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

    def update_triangle_info(self, sides_data):
        """Обновление информации о треугольнике"""
        app_logger.debug(f"Updating triangle info with {len(sides_data)} sides")
        side_names = ['AB', 'BC', 'CA']

        for i, side_name in enumerate(side_names):
            if i < len(sides_data):
                side = sides_data[i]
                text = f"Сторона {side_name}: {side['length_px']:.1f} px ({side['length_m']:.2f} m)"
                self.side_labels[i].config(text=text)
                app_logger.debug(f"Updated side {side_name}: {side['length_px']:.1f} px ({side['length_m']:.2f} m)")
            else:
                self.side_labels[i].config(text=f"Сторона {side_name}: -")
                app_logger.debug(f"Side {side_name}: no data")

    def update_cone_info(self, cone_parameters):
        """Обновление информации о конусе"""
        app_logger.debug(f"Updating cone info: {cone_parameters}")
        if cone_parameters['volume'] > 0:
            volume_text = f"Объем: {cone_parameters['volume']:.2f} m³"
            params_text = f"Радиус: {cone_parameters['radius_m']:.2f} m, Высота: {cone_parameters['height_m']:.2f} m"
            # app_logger.info(f"Cone calculated - Volume: {cone_parameters['volume']:.2f} m³")
        else:
            volume_text = "Объем: -"
            params_text = "Параметры конуса: -"
            app_logger.debug("No cone data to display")

        self.volume_label.config(text=volume_text)
        self.parameters_label.config(text=params_text)

    def update_image_info(self, image_info):
        """Обновление информации об изображении"""
        app_logger.debug(f"Updating image info: {image_info}")
        
        # Размер оригинального изображения
        if 'original_size' in image_info and image_info['original_size']:
            width, height = image_info['original_size']
            megapixels = (width * height) / 1_000_000
            size_text = f"Размер: {width} x {height} px ({megapixels:.1f} MP)"
        else:
            size_text = "Размер: -"
        self.image_size_label.config(text=size_text)
        
        # Формат изображения
        if 'format' in image_info and image_info['format']:
            format_text = f"Формат: {image_info['format']}"
        else:
            format_text = "Формат: -"
        self.image_format_label.config(text=format_text)
        
        # Источник
        if 'source' in image_info and image_info['source']:
            source_text = f"Источник: {image_info['source']}"
        else:
            source_text = "Источник: -"
        self.image_source_label.config(text=source_text)
        
        # Размер отображения
        if 'display_size' in image_info and image_info['display_size']:
            width, height = image_info['display_size']
            display_text = f"Отображение: {width} x {height} px"
        else:
            display_text = "Отображение: -"
        self.display_size_label.config(text=display_text)
        
        # Масштаб
        if 'zoom_level' in image_info and image_info['zoom_level']:
            zoom_percent = int(image_info['zoom_level'] * 100)
            zoom_text = f"Масштаб: {zoom_percent}%"
        else:
            zoom_text = "Масштаб: 100%"
        self.zoom_label.config(text=zoom_text)

    def get_pixel_size(self):
        """Получение размера пикселя из поля ввода"""
        try:
            return float(self.pixel_size_var_zif1.get())
        except ValueError:
            return 0.1

    def set_pixel_size(self, size_m):
        """Установка размера пикселя"""
        self.pixel_size_var_zif1.set(str(size_m))

    def set_trassir1_callback(self, callback):
        """Установить callback для кнопки 'Загрузить с Trassir'"""
        self._trassir1_callback = callback

    def set_trassir2_callback(self, callback):
        """Установить callback для кнопки 'Загрузить с Trassir2'"""
        self._trassir2_callback = callback  

    def _on_trassir1_click(self):
        """Вызов внешнего callback при нажатии на кнопку Trassir"""
        if callable(self._trassir1_callback):
            try:
                self._trassir1_callback('ZIF1')
            except Exception:
                # Простая защита — не даем упасть приложению при ошибке в callback
                pass  

    def _on_trassir2_click(self):
        """Вызов внешнего callback при нажатии на кнопку Trassir"""
        if callable(self._trassir2_callback):
            try:
                self._trassir2_callback('ZIF2')
            except Exception:
                # Простая защита — не даем упасть приложению при ошибке в callback
                pass
    
            

    def pack(self, **kwargs):
        """Упаковка панели"""
        self.frame.pack(**kwargs)