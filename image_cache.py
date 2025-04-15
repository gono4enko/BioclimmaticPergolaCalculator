"""
Модуль для кэширования изображений и ускорения загрузки.
Предварительно загружает все необходимые изображения и сохраняет их в кэше,
что позволяет мгновенно отображать изображения пергол при переключении типов.
"""

import os
import base64
import logging
from typing import Dict, Tuple, Optional
import streamlit as st

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

@st.cache_data(ttl=3600, show_spinner=False)
def get_image_base64(image_path: str) -> Tuple[str, str]:
    """
    Загружает изображение и преобразует его в base64 с кэшированием.
    
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
        
        # Читаем и кодируем изображение
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
    html = f"""<img src="data:{mime_type};base64,{base64_data}" 
                   alt="{alt_text}" 
                   {class_attr} 
                   {style_attr} 
                   loading="eager" 
                   decoding="async">"""
    
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
        "attached_assets/Somfy Pergola.jpg"
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
    """
    return """
    <script>
        // Функция для предварительной загрузки изображений
        function preloadImages() {
            // Список всех изображений для предзагрузки
            const imagesToPreload = [
                "data:image/png;base64,",  // Заглушка для демонстрации
            ];
            
            // Создаем невидимые элементы img для предзагрузки
            imagesToPreload.forEach(src => {
                const img = new Image();
                img.src = src;
            });
            
            console.log("🚀 Предварительная загрузка изображений выполнена");
        }
        
        // Запускаем предзагрузку изображений
        document.addEventListener('DOMContentLoaded', preloadImages);
        
        // Добавляем кэширующие заголовки через мета-теги
        const metaCache = document.createElement('meta');
        metaCache.httpEquiv = 'Cache-Control';
        metaCache.content = 'public, max-age=31536000';
        document.head.appendChild(metaCache);
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
        right_image_path = None  # Для B600 нет дополнительного изображения
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