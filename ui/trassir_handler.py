"""
Обработчик интеграции с Trassir
"""
from tkinter import messagebox
from PIL import Image
from utils.trassir import Trassir
from utils.logger import app_logger


class TrassirHandler:
    """Класс для управления интеграцией с Trassir"""
    
    def __init__(self, config, image_handler, info_panel):
        """
        Инициализация обработчика Trassir.
        
        Args:
            config: Объект конфигурации
            image_handler: Обработчик изображений
            info_panel: Информационная панель
        """
        self.config = config
        self.image_handler = image_handler
        self.info_panel = info_panel
        
        self.trassir = None
        self.current_cone_type = None
    
    def load_cone_screenshot(self, cone_type):
        """
        Загрузить скриншот конуса с Trassir.
        
        Args:
            cone_type: Тип конуса ("ZIF1" или "ZIF2")
        """
        app_logger.info(f"Loading {cone_type} screenshot from Trassir")
        
        # Устанавливаем тип конуса
        self.current_cone_type = cone_type
        self.info_panel.set_current_cone_type(cone_type)
        
        # Получаем конфигурацию камеры
        cam_config = self._get_camera_config(cone_type)
        
        if not cam_config:
            messagebox.showerror(
                "Ошибка",
                f"Конфигурация для {cone_type} не найдена"
            )
            return
        
        # Извлекаем параметры
        trassir_ip = cam_config.get("trassir_ip")
        channel_name = cam_config.get("chanel_name")
        pixel_size_m = cam_config.get("pixel_size_m")
        
        if not trassir_ip or not channel_name:
            messagebox.showerror(
                "Ошибка",
                f"Некорректная конфигурация для {cone_type}"
            )
            return
        
        # Подключаемся к Trassir и загружаем скриншот
        self._connect_and_load(trassir_ip, channel_name, pixel_size_m, cone_type, cam_config)
    
    def _get_camera_config(self, cone_type):
        """
        Получить конфигурацию камеры.
        
        Args:
            cone_type: Тип конуса ("ZIF1" или "ZIF2")
            
        Returns:
            Словарь с конфигурацией или None
        """
        camera_key = f"CAM_CONE_{cone_type}"
        return self.config.get(camera_key, {})
    
    def _connect_and_load(self, trassir_ip, channel_name, pixel_size_m, cone_type, cam_config):
        """
        Подключиться к Trassir и загрузить скриншот.
        
        Args:
            trassir_ip: IP адрес Trassir
            channel_name: Имя канала
            pixel_size_m: Размер пикселя в метрах
            cone_type: Тип конуса
            cam_config: Конфигурация камеры
        """
        try:
            # Получаем пароль из конфигурации (по умолчанию 'master')
            password = cam_config.get("password", "master")
            
            # Создаём или обновляем подключение к Trassir
            if self.trassir is None or self.trassir.ip != trassir_ip:
                app_logger.info(f"Connecting to Trassir at {trassir_ip} with password: {password}")
                try:
                    self.trassir = Trassir(ip=trassir_ip, password=password)
                except ValueError as e:
                    # Ошибка автентификации
                    raise ValueError(f"Не удалось подключиться к Trassir:\n{str(e)}")
            
            # Обновляем кэш каналов
            self.trassir.update_channels_cache()
            app_logger.debug(f"Available channels: {len(self.trassir.channels)}")
            
            # Получаем информацию о канале по имени
            app_logger.info(f"Getting channel info for: {channel_name}")
            channel_info = self.trassir.get_channel_by_name(channel_name)
            
            if not channel_info:
                raise ValueError(f"Канал не найден: {channel_name}")
            
            channel_guid = channel_info['guid']
            app_logger.info(f"Found channel {channel_name} with GUID: {channel_guid}")
            
            # Получаем скриншот по GUID канала
            app_logger.info(f"Getting screenshot from channel: {channel_name}")
            screenshot = self.trassir.get_channel_screenshot(channel_guid)
            
            if screenshot is None:
                raise ValueError(f"Не удалось получить скриншот с канала {channel_name}")
            
            # Масштабируем изображение до ширины 1920px
            screenshot = self._scale_screenshot(screenshot)
            
            # Загружаем изображение
            self.image_handler.load_image_from_pil(screenshot, f"{cone_type} ({channel_name})")
            
            # Обновляем параметры на панели информации
            self._update_cone_parameters(cam_config)
            
            app_logger.info(f"{cone_type} screenshot loaded successfully")
            
        except Exception as e:
            app_logger.error(f"Failed to load {cone_type} screenshot: {str(e)}")
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить скриншот {cone_type}:\n{str(e)}"
            )
    
    def _scale_screenshot(self, screenshot):
        """
        Масштабировать скриншот до ширины 1920px.
        
        Args:
            screenshot: PIL изображение
            
        Returns:
            Масштабированное изображение
        """
        original_width, original_height = screenshot.size
        
        if original_width != 1920:
            app_logger.info(f"Scaling screenshot from {original_width}x{original_height} to 1920px width")
            scale_factor = 1920 / original_width
            new_height = int(original_height * scale_factor)
            screenshot = screenshot.resize((1920, new_height), Image.Resampling.LANCZOS)
            app_logger.info(f"Screenshot scaled to {screenshot.size}")
        
        return screenshot
    
    def _update_cone_parameters(self, cam_config):
        """
        Обновить параметры конуса на панели информации.
        
        Args:
            cam_config: Конфигурация камеры
        """
        pixel_size_m = cam_config.get("pixel_size_m", 0.1)
        k_vol = cam_config.get("k_vol", 1.0)
        k_den = cam_config.get("k_den", 1.7)
        threshold = cam_config.get("threshold", 50)
        
        self.info_panel.set_pixel_size(pixel_size_m)
        self.info_panel.set_k_vol(k_vol)
        self.info_panel.set_k_den(k_den)
        self.info_panel.set_threshold(threshold)
    
    def get_current_cone_type(self):
        """
        Получить текущий тип конуса.
        
        Returns:
            Тип конуса ("ZIF1", "ZIF2" или None)
        """
        return self.current_cone_type
