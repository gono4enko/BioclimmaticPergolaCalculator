"""
Сервис кэширования изображений и других статических ресурсов.
"""
import os
import io
import time
import base64
import hashlib
import logging
from functools import lru_cache
from PIL import Image, UnidentifiedImageError
from flask import current_app, url_for

# Настройка логирования
logger = logging.getLogger(__name__)

# Словарь для хранения кэшированных изображений
IMAGE_CACHE = {}

# Константы
MAX_IMAGE_SIZE = (1200, 1200)  # Максимальный размер изображения
CACHE_EXPIRY = 3600 * 24  # Время жизни кэша в секундах (24 часа)
WEBP_QUALITY = 85  # Качество для WebP (0-100)
JPEG_QUALITY = 90  # Качество для JPEG (0-100)


def get_image_hash(image_path):
    """
    Вычисляет хеш изображения для идентификации дубликатов.
    
    Args:
        image_path (str): Путь к изображению
        
    Returns:
        str: Хеш изображения или None в случае ошибки
    """
    try:
        with open(image_path, 'rb') as f:
            file_data = f.read()
            return hashlib.md5(file_data).hexdigest()
    except Exception as e:
        logger.error(f"Ошибка при вычислении хеша изображения {image_path}: {str(e)}")
        return None


def optimize_image(image_path, output_format='webp'):
    """
    Оптимизирует изображение: конвертирует в WebP, изменяет размер если нужно.
    
    Args:
        image_path (str): Путь к изображению
        output_format (str): Формат вывода ('webp', 'jpeg')
        
    Returns:
        tuple: (байты изображения, тип MIME) или (None, None) в случае ошибки
    """
    try:
        # Открытие и оптимизация изображения
        with Image.open(image_path) as img:
            # Изменение размера при необходимости
            if img.width > MAX_IMAGE_SIZE[0] or img.height > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Сохранение в байтовый буфер
            buffer = io.BytesIO()
            
            if output_format.lower() == 'webp':
                mime_type = 'image/webp'
                img.save(buffer, format='WEBP', quality=WEBP_QUALITY)
            else:
                mime_type = 'image/jpeg'
                img.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
                
            buffer.seek(0)
            return buffer.getvalue(), mime_type
    
    except UnidentifiedImageError:
        logger.warning(f"Некорректное изображение {image_path}")
        return None, None
    except Exception as e:
        logger.error(f"Ошибка при оптимизации изображения {image_path}: {str(e)}")
        return None, None


def get_base64_image(image_path, output_format='webp'):
    """
    Получает изображение в формате Base64 для встраивания в CSS/HTML.
    
    Args:
        image_path (str): Путь к изображению
        output_format (str): Формат вывода ('webp', 'jpeg')
        
    Returns:
        str: Строка с изображением в формате Data URL или None в случае ошибки
    """
    # Проверка кэша
    cache_key = f"{image_path}_{output_format}"
    if cache_key in IMAGE_CACHE:
        cache_entry = IMAGE_CACHE[cache_key]
        # Проверка срока действия кэша
        if time.time() - cache_entry['timestamp'] < CACHE_EXPIRY:
            return cache_entry['data_url']
    
    try:
        # Оптимизация изображения
        image_bytes, mime_type = optimize_image(image_path, output_format)
        
        if not image_bytes or not mime_type:
            return None
        
        # Кодирование в Base64
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_data}"
        
        # Сохранение в кэш
        IMAGE_CACHE[cache_key] = {
            'data_url': data_url,
            'timestamp': time.time()
        }
        
        return data_url
    
    except Exception as e:
        logger.error(f"Ошибка при кодировании изображения {image_path} в Base64: {str(e)}")
        return None


def clear_image_cache():
    """Очищает кэш изображений."""
    global IMAGE_CACHE
    IMAGE_CACHE = {}
    logger.info("Кэш изображений очищен")


@lru_cache(maxsize=100)
def get_cached_images():
    """
    Получает список кэшированных изображений для предзагрузки.
    
    Returns:
        list: Список путей к часто используемым изображениям
    """
    try:
        images = []
        
        # Получение путей к папкам с изображениями
        static_folder = current_app.static_folder
        if not static_folder or not os.path.exists(static_folder):
            return images
        
        # Папки с изображениями
        image_folders = ['images', 'img', 'assets']
        
        for folder_name in image_folders:
            folder_path = os.path.join(static_folder, folder_name)
            if not os.path.exists(folder_path):
                continue
            
            # Обработка изображений в папке
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    image_path = os.path.join(folder_path, filename)
                    url = url_for('static', filename=f'{folder_name}/{filename}')
                    images.append({
                        'path': image_path,
                        'url': url
                    })
        
        return images
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка кэшированных изображений: {str(e)}")
        return []


def preload_images():
    """
    Предварительно загружает и кэширует часто используемые изображения.
    
    Returns:
        str: HTML-код для предзагрузки изображений
    """
    try:
        images = get_cached_images()
        preload_tags = []
        
        for image in images:
            preload_tags.append(f'<link rel="preload" href="{image["url"]}" as="image">')
        
        return "\n".join(preload_tags)
    
    except Exception as e:
        logger.error(f"Ошибка при создании тегов предзагрузки: {str(e)}")
        return ""