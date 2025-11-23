"""
Меню приложения
"""
import tkinter as tk
from core.image_loader import ImageLoader


class Menu:
    def __init__(self, parent, app):
        self.app = app
        self.menu_bar = tk.Menu(parent)

        # Меню "Файл"
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Открыть", command=self.app.open_image)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Конус ЗИФ1", command=self.app.load_cone_zif1)
        self.file_menu.add_command(label="Конус ЗИФ2", command=self.app.load_cone_zif2)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=parent.quit)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)

        # Меню "Вид"
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Увеличить", command=self.app.zoom_in)
        self.view_menu.add_command(label="Уменьшить", command=self.app.zoom_out)
        self.menu_bar.add_cascade(label="Вид", menu=self.view_menu)

        # Меню "Правка"
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Очистить треугольник", command=self.app.clear_triangle)
        self.menu_bar.add_cascade(label="Правка", menu=self.edit_menu)

        # Меню "Справка"
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="О программе", command=self.show_about)
        self.menu_bar.add_cascade(label="Справка", menu=self.help_menu)

        parent.config(menu=self.menu_bar)

    def show_about(self):
        """Показать информацию о программе"""
        about_text = """Cone App
Версия 1.0

Графическое приложение для построения треугольников 
и расчета объемов конусов.

Функции:
- Загрузка изображений
- Построение треугольников
- Расчет объемов конусов"""

        tk.messagebox.showinfo("О программе", about_text)