"""
Модуль для отображения галереи реализованных проектов и социальных доказательств.
Включает в себя галерею фотографий и счетчик установленных пергол.
"""

import streamlit as st
import os
from PIL import Image
import random
from datetime import datetime
import animations

# Путь к директории с изображениями
IMAGES_DIR = "attached_assets"

# Список фотографий реализованных проектов
REALIZED_PROJECTS = [
    "IMG_1001.jpeg",  # Пергола на частном участке
    "IMG_1002.jpeg",  # Пергола с подсветкой
    "IMG_1025.jpeg",  # Пергола на террасе
    "IMG_1026.jpeg",  # Пергола с открытой крышей
    "IMG_1030.jpeg",  # Пергола в загородном доме
    "IMG_1032.jpeg",  # Пергола в современном стиле
    "IMG_1109.jpeg",  # Пергола в саду
    "Somfy Pergola.jpeg",  # Пергола с автоматикой Somfy
    "Модульная система пергол.jpeg",  # Модульная система
    "IMG_5914.jpg",  # Пергола у бассейна
]

# Словарь с описаниями проектов
PROJECT_DESCRIPTIONS = {
    "IMG_1001.jpeg": "Пергола B500 на частном участке в Подмосковье, 2025",
    "IMG_1002.jpeg": "Пергола B700 с RGB подсветкой в коттеджном поселке 'Сосновый бор', 2024",
    "IMG_1025.jpeg": "Пергола B500 на террасе ресторана, 2025",
    "IMG_1026.jpeg": "Пергола B700 с дистанционным управлением, Москва, 2024",
    "IMG_1030.jpeg": "Пергола B600 с панелями PIR на загородном участке, 2025",
    "IMG_1032.jpeg": "Пергола B500 в современном стиле с белой рамой, Санкт-Петербург, 2025",
    "IMG_1109.jpeg": "Пергола B700 в ландшафтном дизайне сада, 2024",
    "Somfy Pergola.jpeg": "Пергола с автоматикой Somfy и датчиками погоды, 2025",
    "Модульная система пергол.jpeg": "Модульная система пергол для большой площади отдыха, 2025",
    "IMG_5914.jpg": "Премиальная пергола B700 у бассейна с зоной отдыха, Крым, 2025",
}

def get_installation_count():
    """
    Возвращает количество установленных пергол в текущем году.
    В реальном приложении здесь был бы запрос к API или базе данных.
    
    Returns:
        int: Количество установленных пергол
    """
    # В рамках тестовой реализации используем датазависимую логику:
    # базовое число + дни года для динамического роста числа
    current_date = datetime.now()
    day_of_year = current_date.timetuple().tm_yday
    
    # Базовое число + прирост от дня года (примерно 1-2 перголы в день)
    base_count = 285
    dynamic_count = day_of_year * 1.5
    
    return int(base_count + dynamic_count)

def display_installation_counter():
    """
    Отображает счетчик установленных пергол в текущем году
    с анимированным оформлением.
    """
    count = get_installation_count()
    
    # Создаем контейнер с красивой анимацией и стилем, согласованным со статьями
    counter_html = f"""
    <div class="installation-counter">
        <div class="counter-number">{count}</div>
        <div class="counter-label">пергол установлено в 2025 году</div>
    </div>
    
    <style>
    .installation-counter {{
        background-color: #004B9A;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 20px 30px 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        animation: pulse 2s infinite;
    }}
    
    .counter-number {{
        font-size: 3.2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    
    .counter-label {{
        font-size: 1.2rem;
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
    animations.animate_section(counter_html, animation_type='fadeIn', delay=0)

def load_and_resize_image(image_path, max_width=800):
    """
    Загружает и изменяет размер изображения, сохраняя пропорции
    
    Args:
        image_path (str): Путь к изображению
        max_width (int): Максимальная ширина для отображения
        
    Returns:
        PIL.Image: Изображение с измененным размером
    """
    try:
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
            justify-content: space-around;
            gap: 15px;
            margin: 10px 20px 30px 20px;
            padding: 0 10px;
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
        }
        
        .gallery-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        
        .gallery-image {
            width: 100%;
            height: auto;
            display: block;
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
                margin: 10px 15px 25px 15px;
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
    Отображает галерею реализованных проектов с описаниями
    """
    # Заголовок и информационный текст теперь добавляются в функции display_gallery_section
    
    # Получаем полные пути к изображениям
    image_paths = []
    available_images = []
    captions = []
    
    # Проверяем наличие файлов и собираем доступные
    for img_name in REALIZED_PROJECTS:
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
        animations.animate_section(gallery_html, animation_type='fadeInUp', delay=0)
    else:
        animations.animate_text("Изображения проектов временно недоступны", tag="p", delay=0)

def display_gallery_section():
    """
    Основная функция для отображения секции с галереей и счетчиком
    """
    with st.container():
        # Заголовок раздела в стиле статей
        st.markdown("""
        <div style="padding: 15px 20px; max-width: 100%;">
            <h1 style="font-size: 2.2rem; color: #0066cc; font-weight: 600; margin-bottom: 15px;">
                Наши достижения и реализованные проекты
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Счетчик установленных пергол
        display_installation_counter()
        
        # Добавляем стиль для текста галереи как в статьях
        st.markdown("""
        <style>
        .gallery-description {
            padding: 15px 20px;
            margin-bottom: 20px;
            font-size: 1.1rem;
            line-height: 1.5;
            color: #333;
        }
        .gallery-subtitle {
            font-size: 1.8rem;
            color: #0066cc;
            font-weight: 600;
            margin: 15px 20px;
            padding-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Галерея проектов с правильными отступами
        st.markdown('<h2 class="gallery-subtitle">Наши реализованные проекты</h2>', unsafe_allow_html=True)
        st.markdown('<div class="gallery-description">Взгляните на некоторые из наших недавних проектов. Каждая пергола уникальна и создана в соответствии с потребностями и пожеланиями клиента.</div>', unsafe_allow_html=True)
        
        # Отображаем галерею с проектами
        display_projects_gallery()