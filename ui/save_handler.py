"""
Обработчик сохранения изображений с аннотациями
"""
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
from core.cone_calculator import ConeCalculator
from utils.constants import COLOR_TRIANGLE, COLOR_VERTEX, VERTEX_RADIUS, LINE_WIDTH
from utils.logger import app_logger


class SaveHandler:
    """Класс для сохранения изображений с аннотациями"""
    
    def __init__(self, canvas_handler, image_handler, triangle_manager, info_panel, status_var):
        """
        Инициализация обработчика сохранения.
        
        Args:
            canvas_handler: Обработчик холста
            image_handler: Обработчик изображений
            triangle_manager: Менеджер треугольника
            info_panel: Информационная панель
            status_var: Переменная для статусной строки
        """
        self.canvas_handler = canvas_handler
        self.image_handler = image_handler
        self.triangle_manager = triangle_manager
        self.info_panel = info_panel
        self.status_var = status_var
    
    def save_image(self, current_cone_type=None):
        """
        Сохранить изображение с наложенным треугольником и метаданными.
        
        Args:
            current_cone_type: Текущий тип конуса ("ZIF1" или "ZIF2")
        """
        original_pil_image = self.canvas_handler.original_pil_image
        
        if not original_pil_image:
            messagebox.showwarning(
                "Предупреждение", 
                "Нет загруженного изображения для сохранения"
            )
            return
        
        app_logger.info("Opening save image dialog")
        
        # Определяем формат по умолчанию
        file_path = self._get_save_path()
        
        if file_path:
            self._save_with_annotations(file_path, original_pil_image, current_cone_type)
    
    def _get_save_path(self):
        """
        Получить путь для сохранения файла.
        
        Returns:
            Путь к файлу или None
        """
        default_extension = ".png"
        image_path = self.image_handler.get_image_path()
        
        if image_path:
            default_extension = os.path.splitext(image_path)[1]
            default_name = os.path.basename(image_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"screenshot_{timestamp}.png"
        
        return filedialog.asksaveasfilename(
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
    
    def _save_with_annotations(self, file_path, original_pil_image, current_cone_type):
        """
        Сохранить изображение с аннотациями.
        
        Args:
            file_path: Путь для сохранения
            original_pil_image: Оригинальное изображение
            current_cone_type: Тип конуса
        """
        try:
            app_logger.info(f"Saving image to: {file_path}")
            
            # Создаём копию изображения для наложения
            output_image = original_pil_image.copy()
            draw = ImageDraw.Draw(output_image)
            
            # Получаем коэффициент масштаба
            scale_factor = self.canvas_handler.get_scale_factor()
            
            # Наложение треугольника
            if self.triangle_manager.is_complete():
                output_image = self._draw_triangle_on_image(output_image, scale_factor)
                draw = ImageDraw.Draw(output_image)
            
            # Подготовка метаданных
            text_lines = self._prepare_metadata_text(scale_factor, current_cone_type)
            
            # Наложение текста
            if text_lines:
                output_image = self._draw_metadata_text(output_image, text_lines, scale_factor)
            
            # Сохраняем изображение
            output_image.save(file_path)
            self.status_var.set(f"Изображение сохранено: {os.path.basename(file_path)}")
            app_logger.info(f"Image saved successfully with overlay: {file_path}")
            messagebox.showinfo("Успех", f"Изображение сохранено:\n{file_path}")
            
        except Exception as e:
            app_logger.error(f"Failed to save image: {str(e)}")
            messagebox.showerror(
                "Ошибка", 
                f"Не удалось сохранить изображение:\n{str(e)}"
            )
    
    def _draw_triangle_on_image(self, output_image, scale_factor):
        """
        Нарисовать треугольник на изображении.
        
        Args:
            output_image: Изображение для рисования
            scale_factor: Коэффициент масштаба
            
        Returns:
            Изображение с треугольником
        """
        draw = ImageDraw.Draw(output_image)
        
        # Переводим координаты вершин в масштаб оригинального изображения
        original_vertices = [
            (x * scale_factor, y * scale_factor) 
            for x, y in self.triangle_manager.vertices
        ]
        
        # Рисуем линии треугольника
        line_width = max(2, int(LINE_WIDTH * scale_factor))
        for i in range(3):
            start = original_vertices[i]
            end = original_vertices[(i + 1) % 3]
            draw.line([start, end], fill=COLOR_TRIANGLE, width=line_width)
        
        # Рисуем вершины
        vertex_radius = max(4, int(VERTEX_RADIUS * scale_factor))
        for x, y in original_vertices:
            draw.ellipse(
                [x - vertex_radius, y - vertex_radius, 
                 x + vertex_radius, y + vertex_radius],
                fill=COLOR_VERTEX,
                outline=COLOR_TRIANGLE
            )
        
        # Подписываем стороны
        output_image = self._draw_side_labels(output_image, original_vertices, scale_factor)
        
        return output_image
    
    def _draw_side_labels(self, output_image, original_vertices, scale_factor):
        """
        Нарисовать подписи сторон треугольника.
        
        Args:
            output_image: Изображение для рисования
            original_vertices: Вершины треугольника в оригинальном масштабе
            scale_factor: Коэффициент масштаба
            
        Returns:
            Изображение с подписями
        """
        draw = ImageDraw.Draw(output_image)
        
        # Загружаем шрифт для подписей сторон
        label_font = self._get_font(max(10, int(12 * scale_factor)))
        
        # Получаем информацию о сторонах
        pixel_size = self.info_panel.get_pixel_size()
        self.triangle_manager._update_sides(pixel_size, scale_factor)
        sides = self.triangle_manager.sides
        
        # Названия сторон
        side_names = ['AB', 'BC', 'CA']
        
        for i in range(3):
            if i < len(sides):
                # Координаты середины стороны
                start = original_vertices[i]
                end = original_vertices[(i + 1) % 3]
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
                
                # Текст с размерами
                length_px = sides[i]['length_px']
                length_m = sides[i]['length_m']
                label_text = f"{side_names[i]}: {length_px:.0f}px ({length_m:.2f}м)"
                
                # Вычисляем смещение для текста (перпендикулярно стороне)
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = (dx**2 + dy**2)**0.5
                
                if length > 0:
                    # Нормализованный перпендикулярный вектор
                    perp_x = -dy / length
                    perp_y = dx / length
                    
                    # Смещение текста от линии
                    offset = max(15, int(20 * scale_factor))
                    text_x = mid_x + perp_x * offset
                    text_y = mid_y + perp_y * offset
                    
                    # Получаем размер текста для фона
                    bbox = draw.textbbox((0, 0), label_text, font=label_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Рисуем полупрозрачный фон для текста
                    padding = max(3, int(4 * scale_factor))
                    bg_box = [
                        text_x - padding,
                        text_y - padding,
                        text_x + text_width + padding,
                        text_y + text_height + padding
                    ]
                    
                    # Создаём временный слой для фона
                    temp_overlay = Image.new('RGBA', output_image.size, (0, 0, 0, 0))
                    temp_draw = ImageDraw.Draw(temp_overlay)
                    temp_draw.rectangle(bg_box, fill=(255, 255, 255, 200))
                    
                    # Накладываем фон
                    output_image = output_image.convert('RGBA')
                    output_image = Image.alpha_composite(output_image, temp_overlay)
                    output_image = output_image.convert('RGB')
                    draw = ImageDraw.Draw(output_image)
                    
                    # Рисуем текст
                    draw.text((text_x, text_y), label_text, fill=(0, 0, 0), font=label_font)
        
        return output_image
    
    def _prepare_metadata_text(self, scale_factor, current_cone_type):
        """
        Подготовить текст метаданных.
        
        Args:
            scale_factor: Коэффициент масштаба
            current_cone_type: Тип конуса
            
        Returns:
            Список строк текста
        """
        text_lines = []
        
        # Дата-время
        now = datetime.now()
        datetime_str = now.strftime("%d.%m.%Y %H:%M:%S")
        text_lines.append(datetime_str)
        
        # Информация о конусе
        if self.triangle_manager.is_complete():
            pixel_size = self.info_panel.get_pixel_size()
            k_vol = self.info_panel.get_k_vol()
            k_den = self.info_panel.get_k_den()
            
            cone_params = ConeCalculator.get_cone_parameters(
                self.triangle_manager.vertices,
                pixel_size,
                scale_factor,
                k_vol
            )
            
            if cone_params['volume'] > 0:
                volume = cone_params['volume']
                mass = volume * k_den
                radius = cone_params['radius_m']
                height = cone_params['height_m']
                
                # Добавляем информацию о конусе
                text_lines.append("")
                if current_cone_type:
                    text_lines.append(f"Конус {current_cone_type}")
                text_lines.append(f"Объём: {volume:.2f} м³")
                text_lines.append(f"Масса: {mass:.2f} т")
                text_lines.append(f"Радиус: {radius:.2f} м")
                text_lines.append(f"Высота: {height:.2f} м")
                
                # Добавляем параметры через разделитель
                text_lines.append(" ")
                text_lines.append("-" * 30)
                text_lines.append(" ")
                text_lines.append(f"Размер пикселя: {pixel_size:.4f} м")
                text_lines.append(f"Коэффициент объёма: {k_vol:.2f}")
                text_lines.append(f"Плотность: {k_den:.2f} т/м³")
        
        return text_lines
    
    def _draw_metadata_text(self, output_image, text_lines, scale_factor):
        """
        Нарисовать текст метаданных на изображении.
        
        Args:
            output_image: Изображение для рисования
            text_lines: Список строк текста
            scale_factor: Коэффициент масштаба
            
        Returns:
            Изображение с текстом
        """
        draw = ImageDraw.Draw(output_image)
        
        # Пытаемся загрузить шрифт
        font_size = max(12, int(14 * scale_factor))
        font = self._get_font(font_size)
        
        # Размеры изображения
        img_width, img_height = output_image.size
        
        # Отступы
        margin = max(10, int(15 * scale_factor))
        line_spacing = max(2, int(5 * scale_factor))
        
        # Вычисляем высоту текста
        total_height = 0
        max_width = 0
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_width = bbox[2] - bbox[0]
            total_height += line_height + line_spacing
            max_width = max(max_width, line_width)
        
        # Позиция текста (левый нижний угол)
        text_x = margin
        text_y = img_height - total_height - margin
        
        # Рисуем полупрозрачный фон для текста
        padding = max(5, int(8 * scale_factor))
        bg_box = [
            text_x - padding,
            text_y - padding,
            text_x + max_width + padding * 2,
            img_height - margin + padding
        ]
        
        # Создаём полупрозрачный слой
        overlay = Image.new('RGBA', output_image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(bg_box, fill=(0, 0, 0, 180))
        
        # Накладываем фон
        output_image = output_image.convert('RGBA')
        output_image = Image.alpha_composite(output_image, overlay)
        output_image = output_image.convert('RGB')
        draw = ImageDraw.Draw(output_image)
        
        # Рисуем текст
        current_y = text_y
        for line in text_lines:
            draw.text((text_x, current_y), line, fill=(255, 255, 255), font=font)
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            current_y += line_height + line_spacing
        
        return output_image
    
    def _get_font(self, size):
        """
        Получить шрифт заданного размера.
        
        Args:
            size: Размер шрифта
            
        Returns:
            Объект шрифта
        """
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.load_default()
            except:
                return ImageFont.load_default()
