"""
Модуль для отображения галереи реализованных проектов и социальных доказательств.
Включает в себя галерею фотографий и счетчик установленных пергол.
Поддерживает работу с форматами JPEG, PNG и HEIC.
"""

import streamlit as st
import os
import sys
from PIL import Image
import random
from datetime import datetime

# Добавляем импорт нашего конвертера HEIC
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import heic_converter
import animations
from components import gallery_admin

# Путь к директории с изображениями
IMAGES_DIR = "attached_assets"

# Список фотографий реализованных проектов
REALIZED_PROJECTS = [
    "IMG_5914.jpg",  # Пергола у бассейна
    # "IMG_5974.heic",  # Пергола B500 с вращающимися ламелями - удалено по запросу
    # "pergola_b500_terrace.jpg",  # Пергола B500 с террасой - удалено по запросу
    "pergola_b500_led_lighting.jpg",  # Пергола B500 с LED подсветкой
    "pergola_terrace_sea_view.jpg",  # Пергола с видом на море
    "pergola_b700_poolside.jpg",  # Пергола B700 у бассейна
    "pergola_b500_garden_view.jpg",  # Пергола B500 с видом на сад
    "pergola_multi_module_terrace.jpg",  # Модульная пергола на террасе 
    "pergola_panoramic_glass_walls.jpg",  # Пергола с панорамным остеклением
    # "pergola_blue_led_lighting.jpg",  # Пергола с синей LED подсветкой - удалено по запросу
    "pergola_evening_lighting.jpg",  # Пергола с вечерним освещением
    # Новые проекты
    "IMG_0672 2.HEIC",  # Новый проект перголы 2025
    "IMG_0676.HEIC",    # Новый проект перголы 2025
    "IMG_0722 2.HEIC",  # Новый проект перголы 2025
    "IMG_0748.HEIC",    # Новый проект перголы 2025
    "IMG_0782.HEIC",    # Новый проект перголы 2025
    "IMG_0789.HEIC",    # Новый проект перголы 2025
    "IMG_0803.HEIC",    # Новый проект перголы 2025
    "IMG_0805 2.HEIC",  # Новый проект перголы 2025
    "IMG_0805 3.HEIC",  # Новый проект перголы 2025
]

# Словарь с описаниями проектов
PROJECT_DESCRIPTIONS = {
    "IMG_5914.jpg": "Премиальная пергола B700 у бассейна с зоной отдыха, Крым, 2025",
    "IMG_5974.heic": "Пергола B500 с вращающимися ламелями и дистанционным управлением, Москва, 2025",
    "pergola_b500_terrace.jpg": "Пергола B500 с открытыми ламелями для уютной террасы с деревянным настилом, 2025",
    "pergola_b500_led_lighting.jpg": "Пергола B500 с интегрированной LED подсветкой и летней кухней, вечернее освещение, 2025",
    "pergola_terrace_sea_view.jpg": "Пергола B500 с просторной зоной отдыха и видом на море, Крым, 2025",
    "pergola_b700_poolside.jpg": "Пергола B700 с закрытой крышей на территории частного дома с бассейном, Подмосковье, 2025",
    "pergola_b500_garden_view.jpg": "Пергола B500 с боковыми шторами для защиты от солнца и ветра, садовая зона, 2025",
    "pergola_multi_module_terrace.jpg": "Модульная система пергол B700 для большой террасы ресторана с зоной отдыха, 2025",
    "pergola_panoramic_glass_walls.jpg": "Пергола B700 с панорамным раздвижным остеклением и деревянным настилом, 2025",
    "pergola_blue_led_lighting.jpg": "Пергола B700 с RGB подсветкой (голубой цвет) у бассейна, вечернее освещение, 2025",
    "pergola_evening_lighting.jpg": "Премиальная пергола Camargue с встроенной LED подсветкой и боковыми шторами, 2025",
    
    # Описания для новых проектов
    "IMG_0672 2.HEIC": "Элегантная пергола B500 со стеклянным ограждением и встроенной LED-подсветкой по периметру, Москва, 2025",
    "IMG_0676.HEIC": "Пергола B700 с автоматическим управлением и максимальной защитой от осадков, загородный дом, 2025",
    "IMG_0722 2.HEIC": "Современная пергола B500 с интегрированной системой отопления для использования в прохладное время года, 2025",
    "IMG_0748.HEIC": "Двухмодульная пергола B700 с большой зоной отдыха у бассейна, черное исполнение, Сочи, 2025",
    "IMG_0782.HEIC": "Пергола B600 в классическом стиле с безрамным остеклением для круглогодичного использования, 2025",
    "IMG_0789.HEIC": "Индивидуальный проект перголы с нестандартной конфигурацией для сложного рельефа, частный дом, 2025",
    "IMG_0803.HEIC": "Пергола премиум-класса с дизайнерскими элементами и встроенной системой освещения, 2025",
    "IMG_0805 2.HEIC": "Современная пергола для летней веранды ресторана с вечерней RGB-подсветкой, Москва, 2025",
    "IMG_0805 3.HEIC": "Эксклюзивный проект перголы с панорамным видом и автоматической системой управления, частная вилла, 2025",
}

def get_installation_count():
    """
    Возвращает количество установленных пергол в текущем году,
    используя формулу: номер недели в году - 6.
    
    Returns:
        int: Количество установленных пергол
    """
    # Получаем текущую дату
    current_date = datetime.now()
    
    # Определяем номер недели для текущего дня
    current_week = current_date.isocalendar()[1]
    
    # Применяем формулу: номер недели в году - 6
    pergolas_count = max(1, current_week - 6)
    
    return pergolas_count

def display_installation_counter():
    """
    Отображает счетчик установленных пергол в текущем году
    с анимированным оформлением.
    """
    count = get_installation_count()
    
    # Нулевой отступ перед счетчиком
    st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
    
    # Создаем контейнер с красивой анимацией и стилем, согласованным со статьями
    counter_html = f"""
    <div class="installation-counter">
        <div class="counter-number">Более {count} пергол</div>
        <div class="counter-label">установлено в 2025 году</div>
    </div>
    
    <style>
    .installation-counter {{
        background-color: #004B9A;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px 20px 20px 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        animation: pulse 2s infinite;
        z-index: 1000;
        position: relative;
    }}
    
    .counter-number {{
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    
    .counter-label {{
        font-size: 1.4rem;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.03); }}
        100% {{ transform: scale(1); }}
    }}
    
    @media (max-width: 768px) {{
        .installation-counter {{
            margin: 10px 15px 25px 15px;
        }}
        
        .counter-number {{
            font-size: 2.8rem;
        }}
    }}
    </style>
    """
    
    # Применяем анимацию появления через модуль animations
    animated_html = animations.animate_section(counter_html, animation_type='fadeIn', delay=0)
    
    # Отображаем счетчик в интерфейсе
    st.markdown(animated_html, unsafe_allow_html=True)

def load_and_resize_image(image_path, max_width=800):
    """
    Загружает и изменяет размер изображения, сохраняя пропорции.
    Поддерживает форматы JPEG, PNG и HEIC.
    
    Args:
        image_path (str): Путь к изображению
        max_width (int): Максимальная ширина для отображения
        
    Returns:
        PIL.Image: Изображение с измененным размером
    """
    try:
        # Проверяем, является ли файл HEIC
        if image_path.lower().endswith(('.heic', '.heif')):
            # Проверяем, установлен ли конвертер
            if heic_converter.check_heif_convert():
                # Конвертируем HEIC в JPEG
                jpeg_path = heic_converter.heic_to_jpeg(image_path)
                if jpeg_path:
                    # Обновляем путь к изображению на новый JPEG
                    image_path = jpeg_path
                else:
                    st.error(f"Не удалось конвертировать HEIC файл: {image_path}")
                    return None
            else:
                st.error("Не найден инструмент для конвертации HEIC. Установите пакет libheif.")
                return None

        # Открываем изображение (теперь уже в поддерживаемом формате)
        img = Image.open(image_path)
        width, height = img.size
        
        # Сохраняем пропорции при изменении размера
        if width > max_width:
            ratio = max_width / width
            new_width = max_width
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height))
            
        return img
    except Exception as e:
        st.error(f"Ошибка при загрузке изображения {image_path}: {str(e)}")
        return None

def create_gallery_html(image_urls, captions):
    """
    Создает HTML-код для галереи изображений с подписями
    
    Args:
        image_urls (list): Список URL изображений
        captions (list): Список подписей к изображениям
        
    Returns:
        str: HTML-код галереи
    """
    gallery_html = """
    <div class="gallery-container">
        <style>
        .gallery-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin: 10px auto 30px auto;
            padding: 0 10px;
            text-align: center;
            max-width: 1200px;
        }
        
        .gallery-item {
            position: relative;
            width: 48%;
            max-width: 400px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin-bottom: 20px;
            display: inline-block;
        }
        
        .gallery-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        
        .gallery-image {
            width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        
        .gallery-caption {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 75, 154, 0.8);
            color: white;
            padding: 10px;
            font-size: 0.9rem;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .gallery-item {
                width: 100%;
                max-width: none;
            }
            
            .gallery-container {
                padding: 0 15px;
                margin: 10px auto 25px auto;
                max-width: 95%;
            }
        }
        </style>
    """
    
    for i, (url, caption) in enumerate(zip(image_urls, captions)):
        gallery_html += f"""
        <div class="gallery-item">
            <img src="{url}" alt="{caption}" class="gallery-image">
            <div class="gallery-caption">{caption}</div>
        </div>
        """
    
    gallery_html += "</div>"
    return gallery_html

def display_projects_gallery():
    """
    Отображает галерею реализованных проектов с описаниями.
    Использует систему администрирования для фильтрации изображений.
    """
    # Заголовок и информационный текст теперь добавляются в функции display_gallery_section
    
    # Получаем полные пути к изображениям
    image_paths = []
    available_images = []
    captions = []
    
    # Фильтруем и проверяем наличие файлов
    for img_name in REALIZED_PROJECTS:
        # Проверяем, разрешено ли изображение через систему администрирования
        if gallery_admin.is_image_allowed(img_name):
            img_path = os.path.join(IMAGES_DIR, img_name)
            if os.path.exists(img_path):
                image_paths.append(img_path)
                available_images.append(img_name)
                # Получаем описание из словаря или используем имя файла
                caption = PROJECT_DESCRIPTIONS.get(img_name, "Реализованный проект перголы")
                captions.append(caption)
    
    # Отображаем галерею, если есть доступные изображения
    if image_paths:
        # Создаем список для хранения URL изображений в Streamlit
        image_urls = []
        
        # Загружаем и отображаем изображения через Streamlit для получения URL
        for img_path in image_paths:
            img = load_and_resize_image(img_path)
            if img:
                # Используем контейнер для скрытия стандартного отображения
                with st.container():
                    col = st.columns([0.01, 0.98, 0.01])[1]  # Используем колонки для центрирования
                    with col:
                        # Отображаем изображение и получаем его URL
                        img_placeholder = st.image(img, use_column_width=True)
                        # Получаем URL изображения из DOM
                        # В реальном приложении здесь был бы код для получения URL
                        # В данном случае используем путь как заменитель URL
                        img_url = img_path  # Это будет заменено на актуальный URL в рабочей версии
                        image_urls.append(img_url)
                        
                        # Скрываем отображенное изображение, так как оно будет показано в галерее
                        # st.markdown(
                        #     f"""
                        #     <style>
                        #         [data-testid="stImage"]:nth-of-type({len(image_urls)}) {{
                        #             display: none;
                        #         }}
                        #     </style>
                        #     """, 
                        #     unsafe_allow_html=True
                        # )
        
        # Создаем и отображаем HTML-галерею с анимацией
        gallery_html = create_gallery_html(image_urls, captions)
        
        # Добавляем анимацию и сразу отображаем
        animated_gallery = animations.animate_section(gallery_html, animation_type='fadeInUp', delay=0)
        st.markdown(animated_gallery, unsafe_allow_html=True)
    else:
        # Изображения недоступны, отображаем сообщение с анимацией
        animations.animate_text("Изображения проектов временно недоступны", tag="p", css_class="fadeIn", delay=0, additional_style="color: #666; font-style: italic; text-align: center;")

def display_gallery_section():
    """
    Основная функция для отображения секции с галереей и счетчиком
    """
    with st.container():
        # Добавляем стиль для текста галереи как в статьях с выравниванием по центру
        st.markdown("""
        <style>
        .gallery-description {
            padding: 15px 20px;
            margin-bottom: 20px;
            font-size: 1.1rem;
            line-height: 1.5;
            color: #333;
            text-align: center;
        }
        .gallery-subtitle {
            font-size: 1.8rem;
            color: #0066cc;
            font-weight: 600;
            margin: 15px 20px;
            padding-bottom: 10px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Заголовок раздела в стиле статей с выравниванием по центру
        st.markdown("""
        <div style="padding: 15px 20px 0px 20px; max-width: 100%; text-align: center;">
            <h1 style="font-size: 2.2rem; color: #0066cc; font-weight: 600; margin-bottom: 5px; text-align: center;">
                Наша галерея и проекты
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Счетчик установленных пергол
        display_installation_counter()
        st.markdown('<div class="gallery-description">Взгляните на некоторые из наших недавних проектов. Каждая пергола уникальна и создана в соответствии с потребностями и пожеланиями клиента.</div>', unsafe_allow_html=True)
        
        # Отображаем галерею с проектами
        display_projects_gallery()