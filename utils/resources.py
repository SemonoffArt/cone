"""
Утилиты для работы с ресурсами приложения
"""
import os
import sys


def get_resource_path(relative_path):
    """
    Получить абсолютный путь к ресурсу для работы с PyInstaller.
    
    Args:
        relative_path: Относительный путь к ресурсу
    
    Returns:
        Абсолютный путь к ресурсу
    """
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Если не запущено через PyInstaller, используем текущую директорию
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
