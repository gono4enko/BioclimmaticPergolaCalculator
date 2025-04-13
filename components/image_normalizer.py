"""
Модуль для нормализации размеров изображений галереи.
Обеспечивает единообразный размер и пропорции для всех изображений при отображении в галерее.
Позволяет автоматически обрабатывать изображения при загрузке:
1. Изменение размера до стандартных значений
2. Сохранение пропорций (соотношения сторон)
3. Опциональная обрезка для получения точных пропорций
4. Оптимизация качества и размера файла
"""

import os
import logging
import tempfile
from PIL import Image, ImageOps
import streamlit as st
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ImageNormalizer')

# Константы для нормализации изображений
GALLERY_STANDARD_WIDTH = 1200       # Стандартная ширина изображений в галерее
GALLERY_STANDARD_HEIGHT = 800       # Стандартная высота изображений в галерее
GALLERY_ASPECT_RATIO = 3/2          # Целевое соотношение сторон (3:2 - стандартное для фотографий)
THUMBNAIL_WIDTH = 400               # Ширина миниатюр
THUMBNAIL_HEIGHT = 300              # Высота миниатюр
JPEG_QUALITY = 85                   # Качество JPEG (0-100)
PROCESSED_DIR = "processed_images"  # Директория для обработанных изображений

def normalize_image_size(image_path, target_width=GALLERY_STANDARD_WIDTH, 
                         target_height=GALLERY_STANDARD_HEIGHT, quality=JPEG_QUALITY, 
                         force_aspect_ratio=False, create_thumbnail=False):
    """
    Нормализует размер изображения, фиксируя высоту и рассчитывая ширину пропорционально.
    Опционально может создать миниатюру.
    
    Args:
        image_path (str): Путь к исходному изображению
        target_width (int): Максимальная ширина (не используется при force_aspect_ratio=False)
        target_height (int): Фиксированная высота для всех изображений
        quality (int): Качество JPEG (0-100)
        force_aspect_ratio (bool): Принудительно установить соотношение сторон (обрезка)
        create_thumbnail (bool): Создать миниатюру
        
    Returns:
        tuple: (путь к нормализованному изображению, путь к миниатюре или None)
    """
    try:
        img = Image.open(image_path)
        
        # Получаем текущие размеры и соотношение сторон
        orig_width, orig_height = img.size
        orig_aspect = orig_width / orig_height
        
        # Определяем новые размеры
        if force_aspect_ratio:
            # Принудительно устанавливаем соотношение сторон через обрезку
            img = crop_to_aspect_ratio(img, GALLERY_ASPECT_RATIO)
            resized_img = img.resize((target_width, target_height), Image.LANCZOS)
        else:
            # Фиксируем высоту и рассчитываем ширину пропорционально
            # Это обеспечит одинаковую высоту для всех изображений
            new_height = target_height
            new_width = int(new_height * orig_aspect)
            
            # Проверка, если ширина получилась слишком большой
            if new_width > target_width * 2:  # Ограничиваем макс. ширину удвоенным значением target_width
                logger.warning(f"Изображение слишком широкое ({new_width}px), ограничиваем")
                new_width = target_width * 2
                
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Сохраняем нормализованное изображение
        file_name = os.path.basename(image_path)
        name, ext = os.path.splitext(file_name)
        
        # Создаем директорию для обработанных изображений, если её нет
        normalized_dir = os.path.join(os.path.dirname(image_path), PROCESSED_DIR)
        if not os.path.exists(normalized_dir):
            os.makedirs(normalized_dir)
        
        # Формируем пути для нормализованного изображения и миниатюры
        normalized_path = os.path.join(normalized_dir, f"{name}_normalized{ext}")
        
        # Сохраняем нормализованное изображение
        resized_img.save(normalized_path, quality=quality, optimize=True)
        logger.info(f"Изображение нормализовано: {normalized_path}")
        
        # Если требуется, создаем миниатюру
        thumbnail_path = None
        if create_thumbnail:
            thumbnail_path = os.path.join(normalized_dir, f"{name}_thumb{ext}")
            create_image_thumbnail(resized_img, thumbnail_path, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, quality)
            
        return normalized_path, thumbnail_path
    
    except Exception as e:
        logger.error(f"Ошибка нормализации изображения {image_path}: {str(e)}")
        return None, None

def crop_to_aspect_ratio(img, target_ratio):
    """
    Обрезает изображение до указанного соотношения сторон.
    
    Args:
        img (PIL.Image): Исходное изображение
        target_ratio (float): Целевое соотношение сторон (ширина/высота)
        
    Returns:
        PIL.Image: Обрезанное изображение
    """
    width, height = img.size
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        # Изображение шире, чем нужно - обрезаем по ширине
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        return img.crop((left, 0, left + new_width, height))
    elif current_ratio < target_ratio:
        # Изображение выше, чем нужно - обрезаем по высоте
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        return img.crop((0, top, width, top + new_height))
    else:
        # Соотношение сторон уже соответствует целевому
        return img

def create_image_thumbnail(img, thumbnail_path, thumb_width, thumb_height, quality):
    """
    Создает миниатюру для изображения с фиксированной высотой.
    
    Args:
        img (PIL.Image): Исходное изображение
        thumbnail_path (str): Путь для сохранения миниатюры
        thumb_width (int): Максимальная ширина миниатюры
        thumb_height (int): Фиксированная высота миниатюры
        quality (int): Качество JPEG (0-100)
        
    Returns:
        bool: True если миниатюра успешно создана
    """
    try:
        # Создаем копию, чтобы не изменять оригинал
        thumb_img = img.copy()
        
        # Получаем размеры исходного изображения
        orig_width, orig_height = thumb_img.size
        orig_aspect = orig_width / orig_height
        
        # Определяем новые размеры с фиксированной высотой
        new_height = thumb_height
        new_width = int(new_height * orig_aspect)
        
        # Если новая ширина превышает максимально допустимую, ограничиваем её
        if new_width > thumb_width * 2:
            new_width = thumb_width * 2
            
        # Изменяем размер
        thumb_img = thumb_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Сохраняем миниатюру
        thumb_img.save(thumbnail_path, quality=quality, optimize=True)
        logger.info(f"Миниатюра создана: {thumbnail_path}, размер: {new_width}x{new_height}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка создания миниатюры: {str(e)}")
        return False

def process_gallery_images_batch(gallery_dir, recursive=False, force_aspect_ratio=False):
    """
    Обрабатывает все изображения в галерее для приведения их к единому размеру.
    
    Args:
        gallery_dir (str): Директория с изображениями галереи
        recursive (bool): Обрабатывать ли подкаталоги рекурсивно
        force_aspect_ratio (bool): Принудительно устанавливать соотношение сторон
        
    Returns:
        tuple: (количество успешно обработанных, количество ошибок)
    """
    success_count = 0
    error_count = 0
    
    if not os.path.exists(gallery_dir) or not os.path.isdir(gallery_dir):
        logger.error(f"Директория {gallery_dir} не существует")
        return 0, 1
    
    # Поддерживаемые расширения изображений
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    
    # Перебираем все файлы в директории
    for root, dirs, files in os.walk(gallery_dir):
        for file in files:
            file_ext = os.path.splitext(file.lower())[1]
            
            # Пропускаем файлы, которые не являются изображениями или уже обработаны
            if file_ext not in valid_extensions or '_normalized' in file or '_thumb' in file:
                continue
                
            file_path = os.path.join(root, file)
            
            # Нормализуем изображение
            result, _ = normalize_image_size(
                file_path, 
                force_aspect_ratio=force_aspect_ratio,
                create_thumbnail=True
            )
            
            if result:
                success_count += 1
            else:
                error_count += 1
                
        # Если не рекурсивный режим, останавливаемся после первой директории
        if not recursive:
            break
    
    logger.info(f"Обработка пакета изображений завершена. Успешно: {success_count}, Ошибок: {error_count}")
    return success_count, error_count

def get_display_size(original_width, original_height, max_display_width, max_display_height, 
                  fixed_height=False):
    """
    Вычисляет оптимальный размер для отображения изображения в интерфейсе.
    Можно использовать два режима:
    1. fixed_height=False: соблюдение пропорций с ограничением по макс. ширине и высоте
    2. fixed_height=True: фиксированная высота для всех изображений
    
    Args:
        original_width (int): Исходная ширина изображения
        original_height (int): Исходная высота изображения
        max_display_width (int): Максимальная ширина для отображения
        max_display_height (int): Максимальная или фиксированная высота для отображения
        fixed_height (bool): Использовать фиксированную высоту для всех изображений
        
    Returns:
        tuple: (display_width, display_height) - размеры для отображения
    """
    if fixed_height:
        # Фиксированная высота для галереи - все изображения будут одинаковой высоты
        display_height = max_display_height
        
        # Вычисляем ширину с сохранением пропорций
        display_width = int(original_width * (display_height / original_height))
        
        # Ограничиваем ширину, если она слишком большая
        if display_width > max_display_width * 2:
            display_width = max_display_width * 2
    else:
        # Стандартный режим - сохранение пропорций с ограничением размеров
        # Вычисляем соотношение ширины и высоты
        width_ratio = max_display_width / original_width
        height_ratio = max_display_height / original_height
        
        # Используем меньшее соотношение для сохранения пропорций
        ratio = min(width_ratio, height_ratio)
        
        # Вычисляем новые размеры
        display_width = int(original_width * ratio)
        display_height = int(original_height * ratio)
    
    return display_width, display_height