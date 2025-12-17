"""
Обработчик загрузки и обработки изображений
"""
import os
from tkinter import filedialog, messagebox
from PIL import Image
from core.image_loader import ImageLoader
from utils.logger import app_logger


class ImageHandler:
    """Класс для управления загрузкой и обработкой изображений"""
    
    def __init__(self, canvas_handler, info_panel, status_var):
        """
        Инициализация обработчика изображений.
        
        Args:
            canvas_handler: Обработчик холста
            info_panel: Информационная панель
            status_var: Переменная для статусной строки
        """
        self.canvas_handler = canvas_handler
        self.info_panel = info_panel
        self.status_var = status_var
        
        self.image_path = None
    
    def open_image(self):
        """Открыть изображение из файла"""
        app_logger.info("Opening file dialog for image selection")
        
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            self.load_image_from_file(file_path)
    
    def load_image_from_file(self, file_path):
        """
        Загрузить изображение из файла.
        
        Args:
            file_path: Путь к файлу изображения
        """
        try:
            app_logger.info(f"Loading image from file: {file_path}")
            
            # Загружаем изображение
            pil_image = Image.open(file_path)
            
            # Сохраняем путь
            self.image_path = file_path
            
            # Устанавливаем изображение на холсте
            self.canvas_handler.set_image(pil_image)
            
            # Обновляем информационную панель
            self._update_image_info(pil_image, file_path)
            
            # Обновляем статус
            self.status_var.set(f"Загружено: {os.path.basename(file_path)}")
            app_logger.info(f"Image loaded successfully: {pil_image.size}")
            
        except Exception as e:
            app_logger.error(f"Failed to load image: {str(e)}")
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить изображение:\n{str(e)}"
            )
    
    def load_image_from_pil(self, pil_image, source_name="Trassir"):
        """
        Загрузить изображение из PIL объекта.
        
        Args:
            pil_image: PIL изображение
            source_name: Название источника изображения
        """
        try:
            app_logger.info(f"Loading image from {source_name}")
            
            # Очищаем путь к файлу
            self.image_path = None
            
            # Устанавливаем изображение на холсте
            self.canvas_handler.set_image(pil_image)
            
            # Обновляем информационную панель
            self._update_image_info(pil_image, source_name)
            
            # Обновляем статус
            self.status_var.set(f"Загружено из {source_name}")
            app_logger.info(f"Image loaded successfully: {pil_image.size}")
            
        except Exception as e:
            app_logger.error(f"Failed to load image from {source_name}: {str(e)}")
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить изображение:\n{str(e)}"
            )
    
    def _update_image_info(self, pil_image, source):
        """
        Обновить информацию об изображении на панели.
        
        Args:
            pil_image: PIL изображение
            source: Источник изображения (путь или название)
        """
        width, height = pil_image.size
        image_format = pil_image.format if pil_image.format else "Unknown"
        
        # Определяем источник для отображения
        if isinstance(source, str) and os.path.exists(source):
            source_display = os.path.basename(source)
        else:
            source_display = str(source)
        
        # Создаём словарь с информацией
        image_info = {
            'original_size': (width, height),
            'display_size': self.canvas_handler.current_image_size,
            'format': image_format,
            'source': source_display,
            'zoom_level': self.canvas_handler.zoom_level
        }
        
        self.info_panel.update_image_info(image_info)
    
    def get_current_image(self):
        """
        Получить текущее изображение PIL.
        
        Returns:
            PIL изображение или None
        """
        return self.canvas_handler.original_pil_image
    
    def get_image_path(self):
        """
        Получить путь к текущему файлу изображения.
        
        Returns:
            Путь к файлу или None
        """
        return self.image_path
