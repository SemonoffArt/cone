import json
import re
import io
import time
import ssl
import urllib3
from typing import Optional, List, Dict, Any, Union
from requests import session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont

from utils.logger import app_logger

# Отключение предупреждений SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CustomHTTPAdapter(HTTPAdapter):
    """Кастомный HTTP адаптер с ослабленными настройками SSL"""
    
    def init_poolmanager(self, *args, **kwargs) -> None:
        """Инициализация пула менеджеров с отключенной проверкой SSL"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        kwargs['ssl_context'] = context
        super().init_poolmanager(*args, **kwargs)


def _remove_comments(text: str) -> str:
    """
    Удаляет C-style и // комментарии из JSON ответов Trassir.
    
    Args:
        text: Исходный текст с комментариями
        
    Returns:
        Текст без комментариев
    """
    pattern = r'\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$'
    return re.sub(pattern, '', str(text))


def _create_http_session() -> session:
    """
    Создает и настраивает HTTP сессию с повторными попытками и SSL отключением.
    
    Returns:
        Настроенная сессия requests
    """
    http_session = session()
    http_session.verify = False
    http_session.headers.update({'Connection': 'close'})
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = CustomHTTPAdapter(max_retries=retry_strategy)
    
    http_session.mount("http://", adapter)
    http_session.mount("https://", adapter)
    
    return http_session


def img_to_pillow(image_data: bytes) -> Image.Image:
    """
    Преобразует изображение из байтов в объект PIL Image.
    
    Args:
        image_data: Байтовое представление изображения
        
    Returns:
        Объект изображения PIL
        
    Raises:
        ValueError: Если данные изображения некорректны
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        # Создаем копию, чтобы избежать проблем с закрытием файла
        return image.copy()
    except Exception as e:
        raise ValueError(f"Failed to convert image data to PIL Image: {e}")


class Trassir:
    """Класс для работы с сервером Trassir"""
    
    # Константы времени
    CHANNELS_CACHE_TIMEOUT = 300  # 5 минут по умолчанию
    
    def __init__(
        self, 
        ip: str = '127.0.0.1', 
        port: str = '8080', 
        password: str = 'master', 
        uptime: int = 0
    ) -> None:
        """
        Инициализация подключения к серверу Trassir.
        
        Args:
            ip: IP адрес сервера
            port: Порт сервера
            password: Пароль для аутентификации
            uptime: Время жизни кэша каналов в секундах
        """
        self.ip = ip
        self.port = port
        self.password = password
        self.uptime = uptime or self.CHANNELS_CACHE_TIMEOUT
        self.url = f'https://{self.ip}:{self.port}'
        
        # Инициализация кэша каналов
        self._channels: List[Dict[str, Any]] = []
        self._channels_timestamp: float = 0.0
        
        self._initialize_channels()
        app_logger.info(
            'Initialized Trassir connection - IP: %s, Password: %s', 
            self.ip, 
            self.password
        )
    
    def _initialize_channels(self) -> None:
        """Инициализирует список каналов при создании объекта."""
        try:
            self._channels = self._fetch_channels_list()
            self._channels_timestamp = time.time()
        except Exception as e:
            app_logger.error('Failed to initialize Trassir channels: %s', e)
            self._channels = []
    
    @property
    def channels(self) -> List[Dict[str, Any]]:
        """Возвращает текущий список каналов."""
        return self._channels
    
    def clear_channels_cache(self) -> None:
        """Очищает кэш каналов."""
        self._channels.clear()
        self._channels_timestamp = 0.0
        app_logger.debug('Channels cache cleared')
    
    def update_channels_cache(self) -> bool:
        """
        Обновляет кэш каналов, если истек интервал времени.
        
        Returns:
            True если кэш был обновлен, False в противном случае
        """
        if self._is_channels_cache_expired():
            new_channels = self._fetch_channels_list()
            if new_channels:
                self._channels = new_channels
                self._channels_timestamp = time.time()
                app_logger.info("Channels cache updated successfully")
                return True
        
        app_logger.debug("Channels cache update not required")
        return False
    
    def _is_channels_cache_expired(self) -> bool:
        """Проверяет, истекло ли время жизни кэша каналов."""
        return (time.time() - self._channels_timestamp) > self.uptime
    
    def _fetch_channels_list(self) -> List[Dict[str, Any]]:
        """
        Получает список каналов с сервера Trassir.
        
        Returns:
            Список объектов каналов
            
        Raises:
            RequestException: При ошибках сетевого запроса
            JSONDecodeError: При ошибках парсинга JSON
        """
        try:
            with _create_http_session() as http_session:
                payload = {'password': self.password}
                response = http_session.get(
                    f'{self.url}/objects/', 
                    params=payload, 
                    timeout=15
                )
                objects_text = response.text
        except RequestException as e:
            app_logger.error('Failed to fetch objects from Trassir: %s', e)
            return []
        
        if not objects_text:
            app_logger.warning('Empty response from Trassir server')
            return []
        
        try:
            cleaned_text = _remove_comments(objects_text)
            objects = json.loads(cleaned_text)
            channels = [obj for obj in objects if obj.get('class') == 'Channel']
            return self._sort_channels(channels)
        except json.JSONDecodeError as e:
            app_logger.error('Failed to parse JSON response: %s', e)
            raise
    
    def get_channel_screenshot(
        self, 
        guid: str, 
        resize: bool = False, 
        raw_img: bool = False
    ) -> Optional[Union[bytes, Image.Image]]:
        """
        Получает скриншот канала.
        
        Args:
            guid: GUID канала
            resize: Нужно ли изменять размер (не реализовано)
            raw_img: Возвращать сырые байты или объект PIL Image
            
        Returns:
            Скриншот в виде байтов или PIL Image, или None при ошибке
        """
        try:
            with _create_http_session() as http_session:
                payload = {'password': self.password}
                url = f'{self.url}/screenshot/{guid}'
                response = http_session.get(url, params=payload, timeout=15)
                
                if response.ok and len(response.content) > 100:
                    if raw_img:
                        return response.content
                    
                    # TODO: Добавить реализацию resize_img при необходимости
                    # if resize:
                    #     return resize_img(img_to_pillow(response.content))
                    
                    return img_to_pillow(response.content)
                else:
                    raise ValueError(
                        f'Invalid screenshot response: status {response.status_code}, '
                        f'content length {len(response.content)}'
                    )
                    
        except (RequestException, ValueError, Exception) as e:
            app_logger.error('Failed to get screenshot for channel %s: %s', guid, e)
            return None
    
    def get_channel_name(self, guid: str) -> str:
        """
        Возвращает имя канала по его GUID.
        
        Args:
            guid: GUID канала
            
        Returns:
            Имя канала или пустая строка если не найден
        """
        for channel in self._channels:
            if channel['guid'] == guid:
                return channel['name']
        return ""
    
    def get_channel_by_name(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает информацию о канале по его имени.
        
        Args:
            channel_name: Имя канала
            
        Returns:
            Словарь с информацией о канале или None если не найден
        """
        for channel in self._channels:
            if channel['name'] == channel_name:
                return channel
        return None
    
    def _sort_channels(self, channels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Сортирует каналы по имени.
        
        Args:
            channels: Список каналов для сортировки
            
        Returns:
            Отсортированный список каналов
        """
        return sorted(channels, key=lambda channel: channel['name'])


def main() -> None:
    """Пример использования класса Trassir."""
    try:
        trassir = Trassir(ip='10.100.59.11')
        
        # Вывод информации о каналах
        print("Available channels:", trassir.channels)
        print("Cache update result:", trassir.update_channels_cache())
        
        # Поиск конкретного канала
        channel_info = trassir.get_channel_by_name('ЗИФ-1 17. Измельчение купол')
        print("Channel info:", channel_info)
        
        # Получение скриншота (раскомментировать при необходимости)
        if channel_info:
            screenshot = trassir.get_channel_screenshot(channel_info['guid'])
            if screenshot:
                screenshot.show()
                
    except Exception as e:
        print(f"Error initializing Trassir: {e}")
        app_logger.error('Error in main: %s', e)


if __name__ == '__main__':
    main()