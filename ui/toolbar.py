"""
Панель инструментов
"""
import tkinter as tk
from tkinter import ttk
from utils.logger import app_logger
from utils.resources import get_resource_path


class ToolTip:
    """Всплывающая подсказка для виджетов"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Привязываем события
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Показать подсказку"""
        if self.tooltip_window or not self.text:
            return
        
        # Получаем координаты виджета
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Создаем окно подсказки
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Убираем рамку окна
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("Arial", 9, "normal"))
        label.pack(ipadx=1)
    
    def hide_tooltip(self, event=None):
        """Скрыть подсказку"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class Toolbar:
    def __init__(self, parent, app):
        """
        Инициализация панели инструментов
        
        Args:
            parent: Родительский виджет
            app: Ссылка на главное окно приложения
        """
        self.parent = parent
        self.app = app
        self.toolbar_icons = {}
        self.frame = ttk.Frame(parent)
        self._create_toolbar()
    
    def _create_toolbar(self):
        """Создание панели инструментов"""
        icon_dir = "resources/icons"
        
        # Файл - Открыть
        try:
            icon_path = get_resource_path(f"{icon_dir}/document-open.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['open'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.open_image)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Открыть изображение")
        except Exception as e:
            app_logger.warning(f"Failed to load document-open.png: {e}")
        
        # Файл - Сохранить
        try:
            icon_path = get_resource_path(f"{icon_dir}/document-save.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['save'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.save_image)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Сохранить изображение")
        except Exception as e:
            app_logger.warning(f"Failed to load document-save.png: {e}")
        
        # Сепаратор
        ttk.Separator(self.frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Файл - Конус ЗИФ1
        try:
            icon_path = get_resource_path(f"{icon_dir}/camera-photo.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['zif1'] = icon
            btn = ttk.Button(self.frame, image=icon, 
                           command=self.app.load_cone_zif1)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Загрузить Конус ЗИФ1")
        except Exception as e:
            app_logger.warning(f"Failed to load camera-photo.png: {e}")
        
        # Файл - Конус ЗИФ2
        try:
            icon_path = get_resource_path(f"{icon_dir}/camera-photo.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['zif2'] = icon
            btn = ttk.Button(self.frame, image=icon, 
                           command=self.app.load_cone_zif2)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Загрузить Конус ЗИФ2")
        except Exception as e:
            app_logger.warning(f"Failed to load camera-photo.png for ZIF2: {e}")
        
        # Сепаратор
        ttk.Separator(self.frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Вид - Увеличить
        try:
            icon_path = get_resource_path(f"{icon_dir}/list-add.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['zoom_in'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.zoom_in)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Увеличить масштаб (+)")
        except Exception as e:
            app_logger.warning(f"Failed to load list-add.png: {e}")
        
        # Вид - Уменьшить
        try:
            icon_path = get_resource_path(f"{icon_dir}/list-remove.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['zoom_out'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.zoom_out)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Уменьшить масштаб (-)")
        except Exception as e:
            app_logger.warning(f"Failed to load list-remove.png: {e}")
        
        # Сепаратор
        ttk.Separator(self.frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Правка - Очистить треугольник
        try:
            icon_path = get_resource_path(f"{icon_dir}/edit-clear.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['clear'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.clear_triangle)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Очистить треугольник")
        except Exception as e:
            app_logger.warning(f"Failed to load edit-clear.png: {e}")
        
        # Правка - Автоматически построить треугольник
        try:
            icon_path = get_resource_path(f"{icon_dir}/face-monkey.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['auto_triangle'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.auto_build_triangle)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Автоматически построить треугольник")
        except Exception as e:
            app_logger.warning(f"Failed to load face-monkey.png: {e}")
        
        # Сепаратор
        ttk.Separator(self.frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Правка - Скопировать объем конуса
        try:
            icon_path = get_resource_path(f"{icon_dir}/edit-copy.png")
            icon = tk.PhotoImage(file=icon_path)
            self.toolbar_icons['copy'] = icon
            btn = ttk.Button(self.frame, image=icon, command=self.app.copy_cone_volume)
            btn.pack(side='left', padx=2)
            btn.image = icon
            ToolTip(btn, "Скопировать объем и массу конуса")
        except Exception as e:
            app_logger.warning(f"Failed to load edit-copy.png: {e}")
        
        # Справка - О программе (кнопка справа)
        # try:
        #     icon_path = get_resource_path("resources/icons/manky32.png")
        #     icon = tk.PhotoImage(file=icon_path)
        #     self.toolbar_icons['about'] = icon
        #     btn = ttk.Button(self.frame, image=icon, command=self.app.show_about)
        #     btn.pack(side='right', padx=2)
        #     btn.image = icon
        #     ToolTip(btn, "О программе")
        # except Exception as e:
        #     app_logger.warning(f"Failed to load pavlik_logo.png: {e}")
    
    def pack(self, **kwargs):
        """Упаковка панели инструментов"""
        self.frame.pack(**kwargs)
