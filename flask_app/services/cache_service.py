"""
Сервис для кэширования и оптимизации изображений
"""
import os
from flask import current_app

def get_cached_images():
    """
    Получает список предварительно загруженных изображений пергол
    для быстрого отображения в интерфейсе
    
    Returns:
        dict: Словарь с путями к изображениям пергол
    """
    cached_images = {
        'B500NEW': '/static/images/B500_main.jpg',
        'B700NEW': '/static/images/B700_main.jpg',
        'B600': '/static/images/B600_main.jpg',
        'SOMFY': '/static/images/SOMFY_main.jpg',
    }
    
    return cached_images