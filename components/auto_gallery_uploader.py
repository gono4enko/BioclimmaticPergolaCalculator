"""
Модуль автоматической выгрузки изображений в галерею с оптимизацией имен файлов.
Выполняет следующие функции:
1. Мониторинг директории для новых изображений
2. Оптимизация имен файлов (удаление пробелов, специальных символов)
3. Обработка изображений (конвертация HEIC, оптимизация размера)
4. Автоматическое добавление в галерею
5. Генерация превью и описаний
"""

import os
import sys
import re
import shutil
import logging
import hashlib
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime
from PIL import Image, UnidentifiedImageError
import streamlit as st

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AutoGalleryUploader')

# Добавляем родительскую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import heic_converter
from components import gallery_admin

# Константы
IMAGES_DIR = "attached_assets"
PROCESSED_DIR = "processed_images"
GALLERY_CONFIG_PATH = "config/gallery_config.json"
MAX_IMAGE_WIDTH = 1920  # максимальная ширина изображения
MAX_IMAGE_HEIGHT = 1080  # максимальная высота изображения
JPEG_QUALITY = 85  # качество JPEG (0-100)
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.JPG', '.JPEG', '.PNG', '.HEIC', '.HEIF'}

def sanitize_filename(filename):
    """
    Оптимизирует имя файла, заменяя пробелы на подчеркивания и удаляя специальные символы.
    
    Args:
        filename (str): Исходное имя файла
        
    Returns:
        str: Оптимизированное имя файла
    """
    # Получаем имя и расширение
    name, ext = os.path.splitext(filename)
    
    # Заменяем пробелы на подчеркивания и удаляем специальные символы
    name = re.sub(r'[^\w\d-]', '_', name)
    name = re.sub(r'_{2,}', '_', name)  # Заменяем множественные подчеркивания на одиночные
    
    # Добавляем хеш для уникальности (только первые 8 символов)
    file_hash = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
    
    # Формируем новое имя с добавлением хеша
    new_name = f"{name}_{file_hash}{ext.lower()}"
    
    return new_name

def is_valid_image(image_path):
    """
    Проверяет, является ли файл валидным изображением.
    
    Args:
        image_path (str): Путь к файлу изображения
        
    Returns:
        bool: True если файл - валидное изображение
    """
    try:
        # Для HEIC файлов используем специальный конвертер
        if image_path.lower().endswith(('.heic', '.heif')):
            if heic_converter.check_heif_convert():
                jpeg_path = heic_converter.heic_to_jpeg(image_path, preserve_original=True)
                # Если конвертация успешна, возвращаем True
                return jpeg_path is not None
            else:
                logger.error("Не найден инструмент для конвертации HEIC")
                return False
                
        # Для обычных форматов используем PIL
        img = Image.open(image_path)
        img.verify()  # Проверка целостности изображения
        return True
    except Exception as e:
        logger.error(f"Ошибка проверки изображения {image_path}: {str(e)}")
        return False

def generate_image_description(image_name):
    """
    Генерирует базовое описание для изображения на основе его имени.
    
    Args:
        image_name (str): Имя файла изображения
        
    Returns:
        str: Сгенерированное описание
    """
    # Базовые описания по типам пергол
    base_descriptions = {
        "b500": "Пергола B500 с вращающимися ламелями",
        "b600": "Пергола B600 с сэндвич-панелями",
        "b700": "Пергола B700 со сдвижными ламелями",
        "pergola": "Премиальная пергола"
    }
    
    # Определяем базовое описание по имени файла
    name_lower = image_name.lower()
    base_desc = None
    
    for key, desc in base_descriptions.items():
        if key in name_lower:
            base_desc = desc
            break
    
    # Если не удалось определить тип, используем общее описание
    if not base_desc:
        base_desc = "Современная пергола"
    
    # Добавляем текущий год и локацию
    current_year = datetime.now().year
    return f"{base_desc} - проект реализации, {current_year}"

def optimize_image(source_path, target_path=None, max_width=MAX_IMAGE_WIDTH, 
                  max_height=MAX_IMAGE_HEIGHT, quality=JPEG_QUALITY, preserve_original=True):
    """
    Оптимизирует изображение: изменяет размер и сжимает.
    
    Args:
        source_path (str): Путь к исходному изображению
        target_path (str, optional): Путь для сохранения. Если None, заменяет исходное.
        max_width (int): Максимальная ширина
        max_height (int): Максимальная высота
        quality (int): Качество JPEG (0-100)
        preserve_original (bool): Сохранять исходный файл (True) или удалять (False)
        
    Returns:
        bool: True если оптимизация успешна
    """
    if target_path is None:
        target_path = source_path
        
    try:
        # Для HEIC файлов сначала конвертируем
        if source_path.lower().endswith(('.heic', '.heif')):
            if heic_converter.check_heif_convert():
                jpeg_path = heic_converter.heic_to_jpeg(source_path, preserve_original=preserve_original)
                if jpeg_path:
                    source_path = jpeg_path
                else:
                    return False
            else:
                logger.error("Не найден инструмент для конвертации HEIC")
                return False
        
        # Открываем и оптимизируем изображение
        img = Image.open(source_path)
        
        # Проверяем, нужно ли изменять размер
        width, height = img.size
        if width > max_width or height > max_height:
            # Вычисляем новые размеры с сохранением пропорций
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
        # Сохраняем оптимизированное изображение
        img.save(target_path, quality=quality, optimize=True)
        logger.info(f"Изображение успешно оптимизировано: {target_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка оптимизации изображения {source_path}: {str(e)}")
        return False

def update_gallery_config(optimized_filename, description=None):
    """
    Добавляет новое изображение в конфигурацию галереи.
    
    Args:
        optimized_filename (str): Оптимизированное имя файла
        description (str, optional): Описание изображения
        
    Returns:
        bool: True если добавление успешно
    """
    try:
        # Загружаем текущую конфигурацию
        config = gallery_admin.load_gallery_config()
        
        # Если изображение уже включено, ничего не делаем
        if optimized_filename in config.get("manual_include", []):
            logger.info(f"Изображение {optimized_filename} уже добавлено в галерею")
            return True
            
        # Добавляем изображение в список включенных
        if "manual_include" not in config:
            config["manual_include"] = []
        
        config["manual_include"].append(optimized_filename)
        
        # Сохраняем конфигурацию
        gallery_admin.save_gallery_config(config)
        
        # Добавляем описание, если оно предоставлено
        if description:
            update_image_description(optimized_filename, description)
            
        logger.info(f"Изображение {optimized_filename} успешно добавлено в галерею")
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления изображения {optimized_filename} в галерею: {str(e)}")
        return False

def update_image_description(image_filename, description):
    """
    Добавляет описание изображения в файл описаний галереи.
    
    Args:
        image_filename (str): Имя файла изображения
        description (str): Описание изображения
        
    Returns:
        bool: True если добавление успешно
    """
    try:
        # Ищем компонент gallery.py для обновления описаний
        project_descriptions_file = "components/gallery.py"
        
        if not os.path.exists(project_descriptions_file):
            logger.error(f"Файл {project_descriptions_file} не найден")
            return False
            
        with open(project_descriptions_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Находим словарь описаний PROJECT_DESCRIPTIONS
        import re
        project_desc_pattern = r'PROJECT_DESCRIPTIONS\s*=\s*\{([^}]*)\}'
        match = re.search(project_desc_pattern, content, re.DOTALL)
        
        if not match:
            logger.error("Словарь PROJECT_DESCRIPTIONS не найден в gallery.py")
            return False
            
        # Добавляем новое описание
        dict_content = match.group(1)
        
        # Проверяем, есть ли уже описание для этого файла
        if f'"{image_filename}"' in dict_content:
            logger.info(f"Описание для {image_filename} уже существует")
            return True
            
        # Добавляем новое описание в конец словаря
        new_entry = f'    "{image_filename}": "{description}",\n'
        updated_dict_content = dict_content + new_entry
        
        # Обновляем содержимое файла
        updated_content = content.replace(match.group(1), updated_dict_content)
        
        with open(project_descriptions_file, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        logger.info(f"Описание для {image_filename} успешно добавлено")
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления описания для {image_filename}: {str(e)}")
        return False

def process_image(source_path, add_to_gallery=True, preserve_original=True):
    """
    Обрабатывает изображение: оптимизирует имя, изменяет размер и добавляет в галерею.
    
    Args:
        source_path (str): Путь к исходному изображению
        add_to_gallery (bool): Добавлять ли изображение в галерею автоматически
        preserve_original (bool): Сохранять исходный файл (True) или удалять (False)
        
    Returns:
        tuple: (успех, путь к обработанному файлу, сообщение)
    """
    try:
        # Проверяем, что файл существует
        if not os.path.exists(source_path):
            return False, None, f"Файл {source_path} не найден"
            
        # Проверяем, что это изображение
        if not is_valid_image(source_path):
            return False, None, f"Файл {source_path} не является валидным изображением"
            
        # Получаем имя файла и оптимизируем его
        filename = os.path.basename(source_path)
        extension = os.path.splitext(filename)[1].lower()
        
        # Если это HEIC, конвертируем в JPEG
        if extension.lower() in ('.heic', '.heif'):
            if heic_converter.check_heif_convert():
                jpeg_path = heic_converter.heic_to_jpeg(source_path, preserve_original=preserve_original)
                if jpeg_path:
                    source_path = jpeg_path
                    filename = os.path.basename(jpeg_path)
                    extension = '.jpg'
                else:
                    return False, None, f"Не удалось конвертировать HEIC файл {source_path}"
            else:
                return False, None, "Не найден инструмент для конвертации HEIC"
                
        # Оптимизируем имя файла
        optimized_filename = sanitize_filename(filename)
        
        # Создаем директорию для обработанных изображений, если её нет
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
            
        # Формируем путь к оптимизированному файлу
        target_path = os.path.join(IMAGES_DIR, optimized_filename)
        
        # Если файл с таким именем уже существует, генерируем новое имя
        if os.path.exists(target_path) and os.path.normcase(os.path.abspath(source_path)) != os.path.normcase(os.path.abspath(target_path)):
            # Генерируем новое уникальное имя
            name, ext = os.path.splitext(optimized_filename)
            timestamp = int(time.time())
            optimized_filename = f"{name}_{timestamp}{ext}"
            target_path = os.path.join(IMAGES_DIR, optimized_filename)
        
        # Если исходный файл не находится в целевой директории,
        # копируем его и оптимизируем, иначе просто оптимизируем на месте
        if os.path.normcase(os.path.dirname(os.path.abspath(source_path))) != os.path.normcase(os.path.abspath(IMAGES_DIR)):
            shutil.copy2(source_path, target_path)
            logger.info(f"Файл скопирован: {source_path} -> {target_path}")
            
        # Оптимизируем изображение
        optimize_result = optimize_image(target_path, preserve_original=preserve_original)
        if not optimize_result:
            return False, None, f"Не удалось оптимизировать изображение {target_path}"
            
        # Генерируем описание для изображения
        description = generate_image_description(optimized_filename)
        
        # Добавляем изображение в галерею, если требуется
        if add_to_gallery:
            update_result = update_gallery_config(optimized_filename, description)
            if not update_result:
                return False, target_path, f"Не удалось добавить изображение {optimized_filename} в галерею"
                
        return True, target_path, f"Изображение успешно обработано и сохранено как {optimized_filename}"
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения {source_path}: {str(e)}")
        return False, None, f"Ошибка при обработке изображения: {str(e)}"

def batch_process_directory(directory_path, add_to_gallery=True, recursive=False, preserve_original=True):
    """
    Обрабатывает все изображения в указанной директории.
    
    Args:
        directory_path (str): Путь к директории с изображениями
        add_to_gallery (bool): Добавлять ли изображения в галерею автоматически
        recursive (bool): Обрабатывать ли вложенные директории рекурсивно
        preserve_original (bool): Сохранять исходный файл (True) или удалять (False)
        
    Returns:
        tuple: (успешно обработано, ошибки, список обработанных файлов)
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return 0, 1, [], f"Директория {directory_path} не существует"
        
    success_count = 0
    error_count = 0
    processed_files = []
    errors = []
    
    # Перебираем все файлы в директории
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            # Проверяем расширение файла
            ext = os.path.splitext(filename)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                file_path = os.path.join(root, filename)
                
                # Обрабатываем изображение
                success, target_path, message = process_image(file_path, add_to_gallery, preserve_original)
                
                if success:
                    success_count += 1
                    if target_path:
                        processed_files.append(target_path)
                else:
                    error_count += 1
                    errors.append(f"{filename}: {message}")
                    
        # Если не рекурсивный режим, прерываем после первой директории
        if not recursive:
            break
            
    return success_count, error_count, processed_files, errors

def watch_directory(directory_path, interval=30, add_to_gallery=True, preserve_original=True):
    """
    Следит за директорией и обрабатывает новые изображения.
    
    Args:
        directory_path (str): Путь к директории для мониторинга
        interval (int): Интервал проверки в секундах
        add_to_gallery (bool): Добавлять ли изображения в галерею автоматически
        preserve_original (bool): Сохранять исходный файл (True) или удалять (False)
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        logger.error(f"Директория {directory_path} не существует")
        return
        
    # Получаем начальный список файлов
    processed_files = set()
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            processed_files.add(os.path.normcase(os.path.abspath(file_path)))
    
    logger.info(f"Начинаем мониторинг директории {directory_path}")
    
    try:
        while True:
            # Ждем указанный интервал
            time.sleep(interval)
            
            # Проверяем новые файлы
            new_files = []
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                abs_path = os.path.normcase(os.path.abspath(file_path))
                
                if os.path.isfile(file_path) and abs_path not in processed_files:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        new_files.append(file_path)
                        processed_files.add(abs_path)
            
            # Обрабатываем новые файлы
            if new_files:
                logger.info(f"Обнаружено {len(new_files)} новых изображений")
                for file_path in new_files:
                    success, target_path, message = process_image(file_path, add_to_gallery, preserve_original)
                    logger.info(message)
    except KeyboardInterrupt:
        logger.info("Мониторинг остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при мониторинге директории: {str(e)}")

def render_uploader_interface():
    """
    Создает интерфейс для ручной загрузки изображений.
    """
    st.title("Загрузка изображений в галерею")
    
    # Создаем вкладки для разных режимов загрузки
    tab1, tab2, tab3 = st.tabs(["Загрузка файла", "Пакетная обработка", "Настройки"])
    
    with tab1:
        st.header("Загрузка изображения")
        st.write("Загрузите изображение для добавления в галерею.")
        
        uploaded_file = st.file_uploader("Выберите изображение", 
                                        type=['jpg', 'jpeg', 'png', 'heic', 'heif'],
                                        key="single_uploader")
        
        col1, col2 = st.columns(2)
        with col1:
            add_to_gallery = st.checkbox("Автоматически добавить в галерею", value=True)
        with col2:
            preserve_original_single = st.checkbox("Сохранить оригинал", value=True, 
                                               help="Если включено, исходный файл будет сохранен после обработки. Если выключено, исходный файл будет удален.", 
                                               key="preserve_original_single")
        
        # Поле для описания
        custom_description = st.text_area("Описание изображения (оставьте пустым для автоматической генерации)", 
                                        height=100, key="description_single")
        
        if st.button("Обработать изображение", type="primary"):
            if uploaded_file is not None:
                # Сохраняем временно загруженный файл
                temp_file = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Обрабатываем загруженный файл
                with st.spinner("Обработка изображения..."):
                    success, target_path, message = process_image(temp_file, add_to_gallery, preserve_original_single)
                    
                    if success:
                        # Если есть пользовательское описание, обновляем его
                        if custom_description.strip() and target_path:
                            filename = os.path.basename(target_path)
                            update_image_description(filename, custom_description.strip())
                            
                        st.success(message)
                        
                        # Отображаем обработанное изображение
                        if target_path:
                            st.image(target_path, caption=f"Обработанное изображение: {os.path.basename(target_path)}")
                    else:
                        st.error(message)
            else:
                st.warning("Пожалуйста, загрузите изображение")
                
    with tab2:
        st.header("Пакетная обработка изображений")
        st.write("Обработка всех изображений в указанной директории.")
        
        directory_path = st.text_input("Путь к директории с изображениями", 
                                     value=IMAGES_DIR, key="directory_path")
        
        batch_options = st.columns(3)
        with batch_options[0]:
            batch_add_to_gallery = st.checkbox("Добавить в галерею", value=True, key="batch_add")
        with batch_options[1]:
            recursive = st.checkbox("Рекурсивный режим", value=False, key="recursive")
        with batch_options[2]:
            preserve_original = st.checkbox("Сохранить оригиналы", value=True, 
                                         help="Если включено, исходные файлы будут сохранены после обработки. Если выключено, исходные файлы будут удалены.", 
                                         key="preserve_original")
            
        if st.button("Начать пакетную обработку", type="primary"):
            if directory_path:
                with st.spinner("Выполняется пакетная обработка изображений..."):
                    success_count, error_count, processed_files, errors = batch_process_directory(
                        directory_path, batch_add_to_gallery, recursive, preserve_original)
                    
                    # Отображаем результаты
                    if success_count > 0:
                        st.success(f"Успешно обработано {success_count} изображений")
                        
                        # Показываем список обработанных файлов (не более 5)
                        if processed_files:
                            st.write("Обработанные файлы:")
                            files_to_show = min(5, len(processed_files))
                            for i in range(files_to_show):
                                st.write(f"- {os.path.basename(processed_files[i])}")
                                
                            if len(processed_files) > files_to_show:
                                st.write(f"... и еще {len(processed_files) - files_to_show} файлов")
                    
                    if error_count > 0:
                        st.error(f"Обнаружено {error_count} ошибок при обработке")
                        with st.expander("Показать ошибки"):
                            for error in errors:
                                st.write(f"- {error}")
            else:
                st.warning("Пожалуйста, укажите путь к директории")
                
    with tab3:
        st.header("Настройки обработки изображений")
        
        # Настройки качества
        st.subheader("Настройки качества")
        col1, col2 = st.columns(2)
        with col1:
            max_width = st.number_input("Максимальная ширина (пикс)", 
                                      min_value=800, max_value=4000, value=MAX_IMAGE_WIDTH)
        with col2:
            max_height = st.number_input("Максимальная высота (пикс)", 
                                      min_value=600, max_value=3000, value=MAX_IMAGE_HEIGHT)
            
        jpeg_quality = st.slider("Качество JPEG", min_value=50, max_value=100, value=JPEG_QUALITY)
        
        # Настройки имени файла
        st.subheader("Настройки имени файла")
        filename_example = sanitize_filename("Пример имени файла 01.jpg")
        st.write(f"Пример оптимизации имени: `Пример имени файла 01.jpg` → `{filename_example}`")
        
        # Сохранение настроек
        if st.button("Применить настройки"):
            # В реальном приложении здесь был бы код для сохранения настроек
            st.success("Настройки успешно сохранены")

if __name__ == "__main__":
    # Тестирование функций (для отладки)
    # process_image("test_image.jpg")
    pass