"""
Модуль для кэширования изображений и ускорения загрузки.
Предварительно загружает все необходимые изображения и сохраняет их в кэше,
что позволяет мгновенно отображать изображения пергол при переключении типов.
"""

import os
import base64
import logging
import json
from typing import Dict, Tuple, Optional, Union
import streamlit as st
from PIL import Image
import io

# Настройка логгера
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация кэша
IMAGE_CACHE = {}  # Глобальный словарь для кэширования данных изображений в памяти

# Типы MIME для разных форматов изображений
MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
}

# Настройки для WebP конвертации
WEBP_QUALITY = 85  # Баланс между качеством и сжатием
WEBP_CACHE_DIR = "processed_images"  # Папка для хранения сконвертированных WebP изображений
ENABLE_WEBP_CONVERSION = False  # Временно отключено до полного тестирования

# Настройки для оптимизации размеров изображений
MAX_IMAGE_WIDTH = 1200  # Максимальная ширина изображения в пикселях
MAX_IMAGE_HEIGHT = 800  # Максимальная высота изображения в пикселях
RESIZE_IMAGES = True  # Включает автоматическое изменение размера больших изображений

# Создаем папку для кэша WebP, если её нет
if not os.path.exists(WEBP_CACHE_DIR):
    os.makedirs(WEBP_CACHE_DIR, exist_ok=True)

def resize_image_if_needed(image_path: str) -> Optional[str]:
    """
    Изменяет размер изображения, если оно слишком большое.
    
    Args:
        image_path (str): Путь к исходному изображению
        
    Returns:
        Optional[str]: Путь к изображению с измененным размером или None в случае ошибки
    """
    if not RESIZE_IMAGES:
        return None
        
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            logger.warning(f"Файл не найден: {image_path}")
            return None
            
        # Формируем имя файла для изображения с измененным размером
        base_name = os.path.basename(image_path)
        file_name, file_ext = os.path.splitext(base_name)
        resized_path = os.path.join(WEBP_CACHE_DIR, f"{file_name}_resized{file_ext}")
        
        # Если уже есть изображение с измененным размером и оно новее оригинала, используем его
        if os.path.exists(resized_path):
            if os.path.getmtime(resized_path) >= os.path.getmtime(image_path):
                logger.debug(f"Использую существующее сжатое изображение: {resized_path}")
                return resized_path
        
        # Открываем изображение
        img = Image.open(image_path)
        
        # Проверяем размеры изображения
        width, height = img.size
        if width <= MAX_IMAGE_WIDTH and height <= MAX_IMAGE_HEIGHT:
            # Размер в пределах нормы, не меняем
            return None
            
        # Вычисляем соотношение сторон и новые размеры с сохранением пропорций
        aspect_ratio = width / height
        
        if width > MAX_IMAGE_WIDTH:
            new_width = MAX_IMAGE_WIDTH
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = MAX_IMAGE_HEIGHT
            new_width = int(new_height * aspect_ratio)
            
        # Проверяем, не превышает ли новая высота/ширина максимальное значение
        if new_height > MAX_IMAGE_HEIGHT:
            new_height = MAX_IMAGE_HEIGHT
            new_width = int(new_height * aspect_ratio)
        if new_width > MAX_IMAGE_WIDTH:
            new_width = MAX_IMAGE_WIDTH
            new_height = int(new_width / aspect_ratio)
        
        # Изменяем размер изображения с высоким качеством
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Сохраняем с тем же форматом
        resized_img.save(resized_path, quality=95)
        logger.info(f"Изменен размер изображения ({width}x{height} -> {new_width}x{new_height}): {resized_path}")
        
        return resized_path
    except Exception as e:
        logger.error(f"Ошибка при изменении размера изображения {image_path}: {str(e)}")
        return None

def convert_to_webp(image_path: str) -> Optional[str]:
    """
    Конвертирует изображение в формат WebP для более быстрой загрузки.
    
    Args:
        image_path (str): Путь к исходному изображению
        
    Returns:
        Optional[str]: Путь к конвертированному WebP-изображению или None в случае ошибки
    """
    if not ENABLE_WEBP_CONVERSION:
        return None
        
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            logger.warning(f"Файл не найден: {image_path}")
            return None
            
        # Формируем имя файла WebP
        base_name = os.path.basename(image_path)
        file_name, _ = os.path.splitext(base_name)
        webp_path = os.path.join(WEBP_CACHE_DIR, f"{file_name}.webp")
        
        # Если WebP-версия уже существует и новее оригинала, возвращаем её
        if os.path.exists(webp_path):
            if os.path.getmtime(webp_path) >= os.path.getmtime(image_path):
                logger.debug(f"Использую существующий WebP: {webp_path}")
                return webp_path
        
        # Открываем изображение
        img = Image.open(image_path)
        
        # Конвертируем в RGB, если это PNG с прозрачностью
        if img.mode == 'RGBA':
            # Создаем белый фон
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Накладываем изображение с альфа-каналом
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Сохраняем в формате WebP
        img.save(webp_path, 'WEBP', quality=WEBP_QUALITY)
        logger.info(f"Изображение конвертировано в WebP: {webp_path}")
        
        return webp_path
    except Exception as e:
        logger.error(f"Ошибка при конвертации в WebP {image_path}: {str(e)}")
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_image_base64(image_path: str) -> Tuple[str, str]:
    """
    Загружает изображение и преобразует его в base64 с кэшированием.
    При необходимости и если включено, конвертирует в WebP для ускорения.
    
    Args:
        image_path (str): Путь к изображению
        
    Returns:
        Tuple[str, str]: Кортеж (mime_type, base64_data)
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            logger.warning(f"Файл не найден: {image_path}")
            return None, None
            
        # Определяем MIME-тип на основе расширения файла
        file_extension = os.path.splitext(image_path)[1].lower()
        mime_type = MIME_TYPES.get(file_extension, 'image/jpeg')  # По умолчанию JPEG
        
        # Если изображение уже в кэше, возвращаем его
        cache_key = f"{image_path}:{os.path.getmtime(image_path)}"
        if cache_key in IMAGE_CACHE:
            logger.debug(f"Использую кэшированное изображение: {image_path}")
            return mime_type, IMAGE_CACHE[cache_key]
        
        # Пробуем изменить размер больших изображений
        if RESIZE_IMAGES:
            resized_path = resize_image_if_needed(image_path)
            if resized_path and os.path.exists(resized_path):
                # Используем изображение с измененным размером
                logger.info(f"Используем изображение с измененным размером для {image_path}")
                # Обновляем путь к исходному изображению для дальнейшей обработки
                image_path = resized_path
                # Обновляем MIME-тип, если изменился формат
                file_extension = os.path.splitext(image_path)[1].lower()
                mime_type = MIME_TYPES.get(file_extension, 'image/jpeg')
                
        # Если включена конвертация в WebP и это не WebP, пробуем конвертировать
        if ENABLE_WEBP_CONVERSION and file_extension != '.webp':
            webp_path = convert_to_webp(image_path)
            if webp_path and os.path.exists(webp_path):
                # Используем WebP вместо оригинала
                logger.info(f"Используем оптимизированную WebP версию для {image_path}")
                with open(webp_path, 'rb') as webp_file:
                    img_data = webp_file.read()
                    base64_data = base64.b64encode(img_data).decode()
                    # Сохраняем в кэш
                    IMAGE_CACHE[cache_key] = base64_data
                    return 'image/webp', base64_data
        
        # Если WebP не используется или конвертация не удалась, используем оригинал (возможно, с измененным размером)
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            base64_data = base64.b64encode(img_data).decode()
            
            # Сохраняем в кэш
            IMAGE_CACHE[cache_key] = base64_data
            logger.debug(f"Изображение закэшировано: {image_path}")
            
            return mime_type, base64_data
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения {image_path}: {str(e)}")
        return None, None

def get_html_image_tag(image_path: str, alt_text: str = "", css_class: str = "", 
                       width: str = "", height: str = "") -> str:
    """
    Создает HTML-тег img для оптимизированного отображения закэшированного изображения.
    
    Args:
        image_path (str): Путь к изображению
        alt_text (str): Альтернативный текст для изображения
        css_class (str): CSS-класс для изображения
        width (str): Ширина изображения (с единицами измерения, например "300px")
        height (str): Высота изображения (с единицами измерения, например "200px")
        
    Returns:
        str: HTML-тег img с закэшированным Base64-кодированным изображением или пустую строку в случае ошибки
    """
    mime_type, base64_data = get_image_base64(image_path)
    
    if not mime_type or not base64_data:
        logger.warning(f"Не удалось получить данные изображения для {image_path}")
        return ""
    
    # Формируем стили
    style = ""
    if width:
        style += f"width:{width};"
    if height:
        style += f"height:{height};"
    
    style_attr = f'style="{style}"' if style else ""
    class_attr = f'class="{css_class}"' if css_class else ""
    
    # Создаем тег img с data URI и атрибутами для оптимизации загрузки
    html = f'<img src="data:{mime_type};base64,{base64_data}" alt="{alt_text}" {class_attr} {style_attr} loading="eager" decoding="async">'
    
    return html

def preload_all_pergola_images():
    """
    Предварительно загружает все изображения пергол для быстрого отображения.
    Вызывается при инициализации приложения.
    """
    logger.info("Начинаю предварительную загрузку изображений пергол...")
    
    # Основные изображения пергол
    pergola_images = [
        "attached_assets/b500_rotation.png",
        "attached_assets/b700_sliding.png", 
        "attached_assets/b600_sandwich.png"
    ]
    
    # Дополнительные изображения (детали пергол)
    detail_images = [
        "attached_assets/linear_drive_b500.png",
        "attached_assets/Линейный привод-2.png",
        "attached_assets/Линейный привод.png",
        "attached_assets/somfy_pergola_b700.jpg",
        "attached_assets/Somfy Pergola.jpg",
        "attached_assets/pir_sandwich_panel_b600.png",
        "attached_assets/Снимок экрана 2025-04-16 в 00.35.39.png"
    ]
    
    # Создаем список всех изображений
    all_images = pergola_images + detail_images
    
    # Загружаем все изображения в кэш
    for image_path in all_images:
        if os.path.exists(image_path):
            get_image_base64(image_path)
            logger.info(f"Предварительно загружено: {image_path}")
        else:
            logger.warning(f"Не найдено изображение для предварительной загрузки: {image_path}")
    
    logger.info("Предварительная загрузка изображений завершена.")

def preload_images_js():
    """
    Возвращает JavaScript-код для предварительной загрузки изображений на стороне браузера.
    Использует современные техники оптимизации и приоритизации загрузки.
    """
    # Создаем список путей ко всем основным изображениям пергол
    image_paths = [
        "attached_assets/b500_rotation.png",
        "attached_assets/b700_sliding.png", 
        "attached_assets/b600_sandwich.png",
        "attached_assets/linear_drive_b500.png",
        "attached_assets/somfy_pergola_b700.jpg",
        "attached_assets/pir_sandwich_panel_b600.png",
        "attached_assets/Линейный привод-2.png",
        "attached_assets/Линейный привод.png",
        "attached_assets/Somfy Pergola.jpg",
        "attached_assets/Снимок экрана 2025-04-16 в 00.35.39.png"
    ]
    
    # Генерируем Base64 данные для всех изображений, которые существуют
    preloaded_images = []
    for path in image_paths:
        if os.path.exists(path):
            mime_type, base64_data = get_image_base64(path)
            preloaded_images.append(f"data:{mime_type};base64,{base64_data}")
            logger.info(f"Подготовлено для предзагрузки: {path}")
        else:
            logger.warning(f"Не найдено изображение для предзагрузки: {path}")
    
    # Собираем JSON-строку для встраивания в JavaScript
    images_json = json.dumps(preloaded_images)
    
    return f"""
    <script>
        // Функция для предварительной загрузки изображений с высоким приоритетом
        function preloadImagesHighPriority() {{
            // Список всех изображений для предзагрузки (заполняется из Python)
            const imagesToPreload = {images_json};
            
            // Создаем элементы link для предзагрузки с высоким приоритетом
            imagesToPreload.forEach(src => {{
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = src;
                link.as = 'image';
                link.importance = 'high'; // Высокий приоритет загрузки
                link.fetchpriority = 'high'; // Новое свойство для Chromium
                document.head.appendChild(link);
                
                // Также создаем невидимые img для реальной загрузки
                const img = new Image();
                img.src = src;
                img.style.position = 'absolute';
                img.style.opacity = '0';
                img.style.width = '1px';
                img.style.height = '1px';
                img.style.zIndex = '-1000';
                document.body.appendChild(img);
            }});
            
            console.log("🚀 Предварительная загрузка " + imagesToPreload.length + " изображений выполнена с высоким приоритетом");
        }}
        
        // Запускаем предзагрузку изображений сразу
        preloadImagesHighPriority();
        
        // Добавляем кэширующие заголовки через мета-теги
        const metaCache = document.createElement('meta');
        metaCache.httpEquiv = 'Cache-Control';
        metaCache.content = 'public, max-age=31536000, immutable';
        document.head.appendChild(metaCache);
        
        // Добавляем мета-тег для отключения масштабирования на мобильных устройствах
        const metaViewport = document.createElement('meta');
        metaViewport.name = 'viewport';
        metaViewport.content = 'width=device-width, initial-scale=1, maximum-scale=1';
        document.head.appendChild(metaViewport);
        
        // Улучшенный обработчик предзагрузки при изменении URL
        window.addEventListener('pushstate', preloadImagesHighPriority);
        window.addEventListener('popstate', preloadImagesHighPriority);
        
        // Улучшаем память браузера, удаляя неиспользуемые элементы
        setTimeout(() => {{
            const preloadedImages = document.querySelectorAll('img[style*="opacity: 0"]');
            preloadedImages.forEach(img => {{
                if (img.complete) {{
                    img.remove();
                }}
            }});
        }}, 10000);
    </script>
    """

def get_optimized_pergola_images(pergola_type: str) -> Tuple[str, str]:
    """
    Возвращает оптимизированные HTML-теги изображений для указанного типа перголы.
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        
    Returns:
        Tuple[str, str]: (html_основного_изображения, html_дополнительного_изображения)
    """
    left_image_html = ""
    right_image_html = ""
    
    # Определяем пути к изображениям в зависимости от типа перголы
    if pergola_type == "B500NEW":
        left_image_path = "attached_assets/b500_rotation.png"
        # Приоритет: сначала английское название, потом кириллическое
        if os.path.exists("attached_assets/linear_drive_b500.png"):
            right_image_path = "attached_assets/linear_drive_b500.png"
        elif os.path.exists("attached_assets/Линейный привод-2.png"):
            right_image_path = "attached_assets/Линейный привод-2.png"
        else:
            right_image_path = "attached_assets/Линейный привод.png" if os.path.exists("attached_assets/Линейный привод.png") else None

    elif pergola_type == "B700NEW":
        left_image_path = "attached_assets/b700_sliding.png"
        # Приоритет: сначала JPG с английским названием, затем кириллическое
        if os.path.exists("attached_assets/somfy_pergola_b700.jpg"):
            right_image_path = "attached_assets/somfy_pergola_b700.jpg"
        elif os.path.exists("attached_assets/Somfy Pergola.jpg"):
            right_image_path = "attached_assets/Somfy Pergola.jpg"
        elif os.path.exists("attached_assets/somfy_pergola_b700.png"):
            right_image_path = "attached_assets/somfy_pergola_b700.png"
        elif os.path.exists("attached_assets/Somfy Pergola.png"):
            right_image_path = "attached_assets/Somfy Pergola.png"
        else:
            right_image_path = "attached_assets/Lin gate.jpg" if os.path.exists("attached_assets/Lin gate.jpg") else None

    elif pergola_type == "B600":
        left_image_path = "attached_assets/b600_sandwich.png"
        # Добавляем детальное изображение для B600 со структурой PIR панели
        if os.path.exists("attached_assets/pir_sandwich_panel_b600.png"):
            right_image_path = "attached_assets/pir_sandwich_panel_b600.png"
        elif os.path.exists("attached_assets/Снимок экрана 2025-04-16 в 00.35.39.png"):
            right_image_path = "attached_assets/Снимок экрана 2025-04-16 в 00.35.39.png"
        else:
            right_image_path = None
    else:
        left_image_path = None
        right_image_path = None
    
    # Создаем оптимизированные HTML-теги для изображений
    if left_image_path and os.path.exists(left_image_path):
        left_image_html = get_html_image_tag(
            left_image_path, 
            alt_text=f"Пергола {pergola_type}", 
            css_class="pergola-image"
        )
    
    if right_image_path and os.path.exists(right_image_path):
        right_image_html = get_html_image_tag(
            right_image_path, 
            alt_text=f"Детали перголы {pergola_type}", 
            css_class="pergola-image"
        )
    
    return left_image_html, right_image_html