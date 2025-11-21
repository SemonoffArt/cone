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
        self.volume_var = tk.StringVar(value="Объем конуса: -")
        self.parameters_var = tk.StringVar(value="Параметры конуса: -")

    def _create_widgets(self):
        """Создание виджетов панели"""
        # Метки для сторон треугольника
        self.side_labels = []
        for i in range(3):
            label = ttk.Label(self.frame, text=f"Сторона {chr(65 + i)}: -")
            label.pack(anchor='w', pady=2)
            self.side_labels.append(label)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        # Информация о конусе
        self.volume_label = ttk.Label(self.frame, text="Объем конуса: -", font=('Arial', 10, 'bold'))
        self.volume_label.pack(anchor='w', pady=2)

        self.parameters_label = ttk.Label(self.frame, text="Параметры конуса: -")
        self.parameters_label.pack(anchor='w', pady=2)

        # Настройка размера пикселя
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        pixel_frame = ttk.Frame(self.frame)
        pixel_frame.pack(fill='x', pady=5)

        ttk.Label(pixel_frame, text="Размер пикселя (м):").pack(side='left')
        self.pixel_size_var = tk.StringVar(value="0.1")
        self.pixel_size_entry = ttk.Entry(pixel_frame, textvariable=self.pixel_size_var, width=8)
        self.pixel_size_entry.pack(side='left', padx=5)

        # Кнопка загрузки с Trassir (внешний обработчик устанавливается через set_trassir_callback)
        self.trassir_button = ttk.Button(self.frame, text="Загрузить с Trassir", command=self._on_trassir_click)
        self.trassir_button.pack(fill='x', pady=8)

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
            volume_text = f"Объем конуса: {cone_parameters['volume']:.2f} m³"
            params_text = f"Радиус: {cone_parameters['radius_m']:.2f} m, Высота: {cone_parameters['height_m']:.2f} m"
            app_logger.info(f"Cone calculated - Volume: {cone_parameters['volume']:.2f} m³")
        else:
            volume_text = "Объем конуса: -"
            params_text = "Параметры конуса: -"
            app_logger.debug("No cone data to display")

        self.volume_label.config(text=volume_text)
        self.parameters_label.config(text=params_text)

    def get_pixel_size(self):
        """Получение размера пикселя из поля ввода"""
        try:
            return float(self.pixel_size_var.get())
        except ValueError:
            return 0.1

    def set_pixel_size(self, size_m):
        """Установка размера пикселя"""
        self.pixel_size_var.set(str(size_m))

    def set_trassir_callback(self, callback):
        """Установить callback для кнопки 'Загрузить с Trassir'"""
        self._trassir_callback = callback

    def _on_trassir_click(self):
        """Вызов внешнего callback при нажатии на кнопку Trassir"""
        if callable(self._trassir_callback):
            try:
                self._trassir_callback()
            except Exception:
                # Простая защита — не даем упасть приложению при ошибке в callback
                pass

    def pack(self, **kwargs):
        """Упаковка панели"""
        self.frame.pack(**kwargs)