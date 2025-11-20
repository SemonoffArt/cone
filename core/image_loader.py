"""
Загрузка и обработка изображений
"""
from PIL import Image, ImageTk
import tkinter as tk


class ImageLoader:
    @staticmethod
    def load_image(file_path, canvas_width, canvas_height):
        """
        Загрузка и масштабирование изображения
        """
        try:
            image = Image.open(file_path)

            # Масштабирование с сохранением пропорций
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)

            # Конвертация для tkinter
            photo_image = ImageTk.PhotoImage(image)

            return photo_image, image.size
        except Exception as e:
            raise Exception(f"Ошибка загрузки изображения: {str(e)}")

    @staticmethod
    def get_supported_formats():
        """Получение поддерживаемых форматов файлов"""
        return [
            ("Все поддерживаемые", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("BMP", "*.bmp"),
            ("GIF", "*.gif"),
            ("Все файлы", "*.*")
        ]