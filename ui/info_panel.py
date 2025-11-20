"""
Панель информации
"""
import tkinter as tk
from tkinter import ttk


class InfoPanel:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Информация", padding=10)
        self._create_widgets()

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

        ttk.Label(pixel_frame, text="Размер пикселя (мм):").pack(side='left')
        self.pixel_size_var = tk.StringVar(value="0.1")
        self.pixel_size_entry = ttk.Entry(pixel_frame, textvariable=self.pixel_size_var, width=8)
        self.pixel_size_entry.pack(side='left', padx=5)

    def update_triangle_info(self, sides_data):
        """Обновление информации о треугольнике"""
        side_names = ['AB', 'BC', 'CA']

        for i, side_name in enumerate(side_names):
            if i < len(sides_data):
                side = sides_data[i]
                text = f"Сторона {side_name}: {side['length_px']:.1f} px ({side['length_m']:.2f} m)"
                self.side_labels[i].config(text=text)
            else:
                self.side_labels[i].config(text=f"Сторона {side_name}: -")

    def update_cone_info(self, cone_parameters):
        """Обновление информации о конусе"""
        if cone_parameters['volume'] > 0:
            volume_text = f"Объем конуса: {cone_parameters['volume']:.2f} m³"
            params_text = f"Радиус: {cone_parameters['radius_m']:.2f} m, Высота: {cone_parameters['height_m']:.2f} m"
        else:
            volume_text = "Объем конуса: -"
            params_text = "Параметры конуса: -"

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

    def pack(self, **kwargs):
        """Упаковка панели"""
        self.frame.pack(**kwargs)