# python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re
import time
from requests import session
from requests.exceptions import RequestException

# from util.bothelper import resize_img, img_to_pillow
# import util.config

logger = logging.getLogger()


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
        self.channels = self.get_channels_list()
        self.channels_time = time.time()
        logger.info('Init class Trassir, IP: %s, Password: %s', self.ip, self.password)

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
        logger.info("Update Trassir Channels Result:%s", result)
        return result

    def get_channels_list(self):
        """Return list of channel objects from Trassir."""
        try:
            with session() as s:
                payload = {'password': self.password}
                resp = s.get(self.url + '/objects/', params=payload, verify=False)
                objects_text = resp.text
        except RequestException as e:
            logger.info('get objects from Trassir Fault %s', e)
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
                payload = {'password': self.password}
                url = f'{self.url}/screenshot/{guid}'
                resp = s.get(url, params=payload, verify=False)
                if resp.ok and len(resp.content) > 100:
                    if raw_img:
                        return resp.content
                    img = img_to_pillow(resp.content)
                    return resize_img(img) if resize else img
                raise Exception('Invalid screenshot response')
        except (RequestException, Exception) as e:
            logger.error('get screenshot from Trassir Fault %s', e)
            return None

    def get_channel_name(self, guid) -> str:
        """Return channel name by guid."""
        for channel in self.channels:
            if channel['guid'] == guid:
                return channel['name']
        return ""

    def get_channel_dic(self, channel_name):
        """Return channel dict by name (keeps original loop semantics)."""
        for channel in self.channels:
            if channel['name'] == channel_name:
                break
        return channel

    def _sort_channels(self, channels) -> list:
        """Return channels sorted by their 'name'."""
        return sorted(channels, key=lambda c: c['name'])


if __name__ == '__main__':
    tr = Trassir(ip='10.100.59.10')
    print(tr.channels)
    print(tr.update_channels())
