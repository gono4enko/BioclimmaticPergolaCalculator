"""
Модуль администрирования галереи фотографий.
Предоставляет функции для управления отображаемыми фотографиями
и включения/отключения отдельных изображений.
"""

import os
import streamlit as st
import sys
import json
from pathlib import Path

# Файл с конфигурацией отображаемых изображений
GALLERY_CONFIG_PATH = "config/gallery_config.json"

# Настройки по умолчанию
DEFAULT_CONFIG = {
    "excluded_images": [],  # Список исключенных изображений
    "manual_include": []    # Список явно включенных изображений
}

def ensure_config_directory():
    """Убедиться, что директория с конфигурациями существует"""
    config_dir = os.path.dirname(GALLERY_CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

def load_gallery_config():
    """
    Загружает конфигурацию галереи из файла.
    Если файл не существует, создает его с настройками по умолчанию.
    
    Returns:
        dict: Конфигурация галереи
    """
    ensure_config_directory()
    
    if not os.path.exists(GALLERY_CONFIG_PATH):
        save_gallery_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(GALLERY_CONFIG_PATH, 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config
    except Exception as e:
        st.error(f"Ошибка загрузки конфигурации галереи: {str(e)}")
        return DEFAULT_CONFIG.copy()

def save_gallery_config(config):
    """
    Сохраняет конфигурацию галереи в файл.
    
    Args:
        config (dict): Конфигурация галереи для сохранения
    """
    ensure_config_directory()
    
    try:
        with open(GALLERY_CONFIG_PATH, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Ошибка сохранения конфигурации галереи: {str(e)}")

def exclude_image(image_name):
    """
    Исключает изображение из галереи.
    
    Args:
        image_name (str): Имя файла изображения для исключения
    """
    config = load_gallery_config()
    
    if image_name not in config["excluded_images"]:
        config["excluded_images"].append(image_name)
        
    # Если изображение было явно включено, удаляем его оттуда
    if image_name in config["manual_include"]:
        config["manual_include"].remove(image_name)
        
    save_gallery_config(config)
    
def include_image(image_name):
    """
    Включает изображение в галерею.
    
    Args:
        image_name (str): Имя файла изображения для включения
    """
    config = load_gallery_config()
    
    # Если изображение было исключено, удаляем его из списка исключений
    if image_name in config["excluded_images"]:
        config["excluded_images"].remove(image_name)
        
    # Добавляем в список явно включенных
    if image_name not in config["manual_include"]:
        config["manual_include"].append(image_name)
        
    save_gallery_config(config)

def is_image_allowed(image_name):
    """
    Проверяет, разрешено ли отображение изображения в галерее.
    
    Args:
        image_name (str): Имя файла изображения
        
    Returns:
        bool: True если изображение разрешено к отображению
    """
    config = load_gallery_config()
    
    # Если изображение в списке исключенных - не показываем
    if image_name in config["excluded_images"]:
        return False
    
    # Если список явного включения не пуст и изображения там нет - не показываем
    if config["manual_include"] and image_name not in config["manual_include"]:
        return False
    
    # В остальных случаях показываем
    return True

def get_all_gallery_images(images_dir):
    """
    Получает список всех изображений в указанной директории.
    
    Args:
        images_dir (str): Путь к директории с изображениями
        
    Returns:
        list: Список имен файлов изображений
    """
    image_extensions = ('.jpg', '.jpeg', '.png', '.heic', '.heif')
    images = []
    
    try:
        for file in os.listdir(images_dir):
            if file.lower().endswith(image_extensions):
                images.append(file)
    except Exception as e:
        st.error(f"Ошибка чтения директории с изображениями: {str(e)}")
    
    return images

def get_active_gallery_images(images_dir):
    """
    Получает список активных (разрешенных к отображению) изображений.
    
    Args:
        images_dir (str): Путь к директории с изображениями
        
    Returns:
        list: Список имен файлов изображений, разрешенных к отображению
    """
    all_images = get_all_gallery_images(images_dir)
    return [img for img in all_images if is_image_allowed(img)]

def detect_duplicate_images(images_dir):
    """
    Обнаруживает дубликаты изображений по размеру файла.
    Простой подход - считаем дубликатами файлы с одинаковыми размерами.
    
    Args:
        images_dir (str): Путь к директории с изображениями
        
    Returns:
        list: Список групп дубликатов
    """
    all_images = get_all_gallery_images(images_dir)
    size_map = {}
    
    # Группируем файлы по размеру
    for img_name in all_images:
        img_path = os.path.join(images_dir, img_name)
        try:
            size = os.path.getsize(img_path)
            if size not in size_map:
                size_map[size] = []
            size_map[size].append(img_name)
        except Exception as e:
            st.error(f"Ошибка определения размера файла {img_name}: {str(e)}")
    
    # Отбираем только группы с дубликатами (больше 1 файла)
    duplicates = [group for group in size_map.values() if len(group) > 1]
    return duplicates

def render_gallery_admin_interface(images_dir):
    """
    Отображает интерфейс администрирования галереи.
    
    Args:
        images_dir (str): Путь к директории с изображениями
    """
    st.title("Администрирование галереи")
    
    # Загружаем конфигурацию
    config = load_gallery_config()
    
    # Получаем все изображения
    all_images = get_all_gallery_images(images_dir)
    
    # Обнаруживаем дубликаты
    duplicates = detect_duplicate_images(images_dir)
    
    if duplicates:
        st.warning(f"Обнаружено {len(duplicates)} групп дубликатов")
        if st.checkbox("Показать дубликаты"):
            for i, group in enumerate(duplicates):
                st.subheader(f"Группа дубликатов {i+1}")
                cols = st.columns(len(group))
                
                for j, img_name in enumerate(group):
                    with cols[j]:
                        img_path = os.path.join(images_dir, img_name)
                        st.image(img_path, caption=img_name, width=150)
                        if st.button(f"Исключить {img_name}"):
                            exclude_image(img_name)
                            st.success(f"Изображение {img_name} исключено из галереи")
                            st.rerun()
    
    # Вкладки для управления изображениями
    tab1, tab2, tab3 = st.tabs(["Все изображения", "Активные", "Исключенные"])
    
    with tab1:
        st.subheader("Все доступные изображения")
        
        # Разбиваем на строки с 3 колонками
        for i in range(0, len(all_images), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(all_images):
                    img_name = all_images[i+j]
                    img_path = os.path.join(images_dir, img_name)
                    
                    with cols[j]:
                        st.image(img_path, caption=img_name, width=150)
                        
                        # Показываем соответствующую кнопку в зависимости от статуса
                        if img_name in config["excluded_images"]:
                            if st.button(f"Включить {img_name}"):
                                include_image(img_name)
                                st.success(f"Изображение {img_name} включено в галерею")
                                st.rerun()
                        else:
                            if st.button(f"Исключить {img_name}"):
                                exclude_image(img_name)
                                st.success(f"Изображение {img_name} исключено из галереи")
                                st.rerun()
    
    with tab2:
        st.subheader("Активные изображения")
        active_images = get_active_gallery_images(images_dir)
        
        if not active_images:
            st.info("Нет активных изображений")
        else:
            for i in range(0, len(active_images), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(active_images):
                        img_name = active_images[i+j]
                        img_path = os.path.join(images_dir, img_name)
                        
                        with cols[j]:
                            st.image(img_path, caption=img_name, width=150)
                            if st.button(f"Исключить {img_name} из активных"):
                                exclude_image(img_name)
                                st.success(f"Изображение {img_name} исключено из галереи")
                                st.rerun()
    
    with tab3:
        st.subheader("Исключенные изображения")
        
        if not config["excluded_images"]:
            st.info("Нет исключенных изображений")
        else:
            for i in range(0, len(config["excluded_images"]), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(config["excluded_images"]):
                        img_name = config["excluded_images"][i+j]
                        img_path = os.path.join(images_dir, img_name)
                        
                        with cols[j]:
                            if os.path.exists(img_path):
                                st.image(img_path, caption=img_name, width=150)
                            else:
                                st.error(f"Файл {img_name} не найден")
                                
                            if st.button(f"Вернуть {img_name} в галерею"):
                                include_image(img_name)
                                st.success(f"Изображение {img_name} возвращено в галерею")
                                st.rerun()
    
    # Кнопка для сброса настроек
    if st.button("Сбросить настройки галереи"):
        save_gallery_config(DEFAULT_CONFIG)
        st.success("Настройки галереи сброшены")
        st.rerun()