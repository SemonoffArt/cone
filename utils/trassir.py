import json
import re
import io
import time
import ssl
import urllib3
from requests import session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
from utils.logger import app_logger

from PIL import ImageFont, ImageDraw, Image

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CustomHTTPAdapter(HTTPAdapter):
    """Custom HTTP Adapter with relaxed SSL settings"""
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Try to disable SSL verification completely
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# from util.bothelper import resize_img, img_to_pillow
# import util.config




def _remove_comments(text):
    """Remove C-style and // comments from Trassir JSON responses."""
    pattern = r'\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$'
    return re.sub(pattern, '', str(text))


class Trassir:
    def __init__(self, ip='127.0.0.1', port='8080', password='master', uptime=0):
        self.ip = ip
        self.port = port
        self.password = password
        self.uptime = uptime
        self.url = f'https://{self.ip}:{self.port}'
        
        try:
            self.channels = self.get_channels_list()
        except Exception as e:
            app_logger.error('Failed to initialize Trassir channels: %s', e)
            self.channels = []
        self.channels_time = time.time()
        app_logger.info('Init class Trassir, IP: %s, Password: %s', self.ip, self.password)

    def clear_channels(self):
        self.channels.clear()

    def update_channels(self) -> bool:
        """Update channels if uptime interval passed; return True on update."""
        result = False
        if (time.time() - self.channels_time) > self.uptime:
            new = self.get_channels_list()
            if new:
                self.channels = new
                self.channels_time = time.time()
                result = True
        app_logger.info("Update Trassir Channels Result:%s", result)
        return result

    def get_channels_list(self):
        """Return list of channel objects from Trassir."""
        try:
            with session() as s:
                # Configure session to handle SSL issues
                s.verify = False
                s.headers.update({'Connection': 'close'})
                
                # Use custom adapter with relaxed SSL settings
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = CustomHTTPAdapter(max_retries=retry_strategy)
                s.mount("http://", adapter)
                s.mount("https://", adapter)
                
                # Add timeout to prevent hanging
                payload = {'password': self.password}
                resp = s.get(self.url + '/objects/', params=payload, verify=False, timeout=15)
                objects_text = resp.text
        except RequestException as e:
            app_logger.info('get objects from Trassir Fault %s', e)
            objects_text = None

        if not objects_text:
            return []

        objects_text = _remove_comments(objects_text)
        try:
            objects = json.loads(objects_text)
        except json.decoder.JSONDecodeError:
            raise

        channels = [obj for obj in objects if obj.get('class') == 'Channel']
        return self._sort_channels(channels)

    def get_channel_screenshot(self, guid, resize=False, raw_img=False):
        """Return channel screenshot as Pillow image or raw bytes."""
        try:
            with session() as s:
                # Configure session to handle SSL issues
                s.verify = False
                s.headers.update({'Connection': 'close'})
                
                # Use custom adapter with relaxed SSL settings
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = CustomHTTPAdapter(max_retries=retry_strategy)
                s.mount("http://", adapter)
                s.mount("https://", adapter)
                
                # Add timeout to prevent hanging
                payload = {'password': self.password}
                url = f'{self.url}/screenshot/{guid}'
                resp = s.get(url, params=payload, verify=False, timeout=15)
                if resp.ok and len(resp.content) > 100:
                    if raw_img:
                        return resp.content
                    # Note: img_to_pillow and resize_img functions are not imported
                    # return resize_img(img) if resize else img
                    return img_to_pillow(resp.content)

                raise Exception('Invalid screenshot response')
        except (RequestException, Exception) as e:
            app_logger.error('get screenshot from Trassir Fault %s', e)
            return None

    def get_channel_name(self, guid) -> str:
        """Return channel name by guid."""
        for channel in self.channels:
            if channel['guid'] == guid:
                return channel['name']
        return ""

    def get_channel_dic(self, channel_name):
        """Return channel dict by name (keeps original loop semantics)."""
        channel = None
        for channel in self.channels:
            if channel['name'] == channel_name:
                break
        return channel

    def _sort_channels(self, channels) -> list:
        """Return channels sorted by their 'name'."""
        return sorted(channels, key=lambda c: c['name'])

@staticmethod
def img_to_pillow(img) -> Image.Image:
    """Преобразование изображение из байт в объект библиотеки PILLOW"""
    try:
        img.verify()
    except Exception:
        img = Image.open(io.BytesIO(img))
        img = img.copy()
    return img


if __name__ == '__main__':
    try:
        tr = Trassir(ip='10.100.59.11')
        print(tr.channels)
        print(tr.update_channels())

        # print("\n\n\n")

        print(tr.get_channel_dic('ЗИФ-1 17. Измельчение купол'))
        # img = img_to_pillow(tr.get_channel_screenshot('Mdvw3cwZ'))
        img = tr.get_channel_screenshot('Mdvw3cwZ', raw_img=False)
        img.show()

    except Exception as e:
        print(f"Error initializing Trassir: {e}")
        app_logger.error('Error in main: %s', e)
