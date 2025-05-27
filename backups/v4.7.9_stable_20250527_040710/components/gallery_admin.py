"""
Модуль администрирования галереи фотографий.
Предоставляет функции для управления отображаемыми фотографиями
и включения/отключения отдельных изображений.
"""

import os
import streamlit as st
import sys
import json
import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import io

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

def delete_image_permanently(image_name, images_dir):
    """
    Физически удаляет изображение из директории и обновляет конфигурацию.
    
    Args:
        image_name (str): Имя файла изображения для удаления
        images_dir (str): Путь к директории с изображениями
        
    Returns:
        bool: True если удаление прошло успешно, False в противном случае
    """
    config = load_gallery_config()
    img_path = os.path.join(images_dir, image_name)
    
    # Пытаемся удалить файл
    try:
        # Проверяем, существует ли файл
        if os.path.exists(img_path):
            # Создаем директорию для резервных копий если нужно
            backup_dir = os.path.join(images_dir, "deleted_images")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                
            # Создаем резервную копию файла
            backup_path = os.path.join(backup_dir, image_name)
            shutil.copy2(img_path, backup_path)
            
            # Удаляем файл
            os.remove(img_path)
            
            # Обновляем конфигурацию
            if image_name in config["excluded_images"]:
                config["excluded_images"].remove(image_name)
                
            if image_name in config["manual_include"]:
                config["manual_include"].remove(image_name)
                
            save_gallery_config(config)
            
            logging.info(f"Изображение {image_name} было физически удалено")
            return True
        else:
            logging.warning(f"Файл {image_name} не найден, не удается удалить")
            return False
            
    except Exception as e:
        logging.error(f"Ошибка при удалении изображения {image_name}: {str(e)}")
        return False

def is_image_allowed(image_name, check_duplicates=False, images_dir=None):
    """
    Проверяет, разрешено ли отображение изображения в галерее.
    
    Args:
        image_name (str): Имя файла изображения
        check_duplicates (bool): Проверять также содержимое файла на дубликаты
        images_dir (str): Директория с изображениями, нужна для проверки дубликатов по содержимому
        
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
        
    # Проверка на дубликаты по содержимому, если это необходимо
    if check_duplicates and images_dir:
        import heic_converter
        img_path = os.path.join(images_dir, image_name)
        if os.path.exists(img_path):
            # Получаем все активные изображения 
            active_images = get_active_gallery_images(images_dir)
            for active_img in active_images:
                if active_img != image_name:  # Не сравниваем файл с самим собой
                    active_path = os.path.join(images_dir, active_img)
                    if os.path.exists(active_path):
                        is_duplicate, _ = heic_converter.is_duplicate_image(img_path, active_path, by_content=True)
                        if is_duplicate:
                            # Нашли дубликат по содержимому среди уже активных изображений
                            logging.info(f"Обнаружен дубликат по содержимому: {image_name} похож на {active_img}")
                            return False
    
    # В остальных случаях показываем
    return True

def is_valid_image(img_path):
    """
    Проверяет, является ли файл корректным изображением, которое можно открыть с помощью PIL.
    
    Args:
        img_path (str): Путь к файлу изображения
        
    Returns:
        bool: True если изображение можно открыть, False в противном случае
    """
    try:
        # Пробуем открыть изображение
        with Image.open(img_path) as img:
            # Проверяем базовую информацию
            img.verify()  # Проверка корректности данных изображения
            return True
    except Exception as e:
        logging.warning(f"Некорректное изображение {img_path}: {str(e)}")
        return False
        
def upload_new_image(uploaded_file, images_dir, auto_include=True, check_duplicates=True, quality=90):
    """
    Загружает новое изображение в директорию галереи и автоматически включает его в активные.
    Проверяет на дубликаты и конвертирует HEIC в JPEG.
    
    Args:
        uploaded_file: Загруженный файл из st.file_uploader
        images_dir (str): Путь к директории галереи
        auto_include (bool): Автоматически включить в активные изображения
        check_duplicates (bool): Проверять на дубликаты перед загрузкой
        quality (int): Качество выходного JPEG при конвертации (0-100)
        
    Returns:
        tuple: (успешно ли загружено, имя файла, сообщение)
    """
    if uploaded_file is None:
        return False, None, "Файл не был предоставлен"
    
    # Генерируем очищенное имя файла без специальных символов
    try:
        import heic_converter
        original_filename = uploaded_file.name
        file_extension = os.path.splitext(original_filename)[1].lower()
        file_stem = os.path.splitext(original_filename)[0]
        clean_stem = heic_converter.clean_filename(file_stem)
        
        # Создаем уникальное имя для файла, чтобы избежать конфликтов
        random_suffix = uuid.uuid4().hex[:8]
        new_filename = f"{clean_stem}_{random_suffix}{file_extension}"
        
        # Полный путь к новому файлу
        new_file_path = os.path.join(images_dir, new_filename)
        
        # Сохраняем загруженный файл во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name
        
        # Проверка на дубликаты на основе хеша содержимого
        if check_duplicates:
            is_duplicate, duplicate_path = heic_converter.is_duplicate_image(tmp_file_path, images_dir, True)
            if is_duplicate:
                os.unlink(tmp_file_path)  # Удаляем временный файл
                
                # Если обнаружен дубликат, просто включаем его в галерею и возвращаем
                if duplicate_path:
                    duplicate_filename = os.path.basename(duplicate_path)
                    
                    # Если необходимо, включаем дубликат в активные изображения
                    if auto_include:
                        include_image(duplicate_filename)
                    
                    return True, duplicate_filename, f"Обнаружен дубликат: {duplicate_filename}"
                else:
                    # На случай если duplicate_path пустой, продолжаем загрузку
                    pass
        
        # Обработка файла в зависимости от типа
        if file_extension.lower() in ('.heic', '.heif'):
            # Сначала копируем временный файл в целевую директорию
            shutil.copy2(tmp_file_path, new_file_path)
            os.unlink(tmp_file_path)  # Удаляем временный файл
            
            # Конвертируем HEIC в JPEG
            jpeg_path = heic_converter.heic_to_jpeg(new_file_path, quality=quality, check_duplicates=False)
            
            # Если конвертация не удалась, удаляем исходный файл
            if not jpeg_path or not os.path.exists(jpeg_path):
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                return False, None, "Ошибка при конвертации HEIC в JPEG"
            
            # Получаем имя JPEG файла и удаляем оригинальный HEIC
            jpeg_filename = os.path.basename(jpeg_path)
            
            # Если нужно автоматически включить в галерею
            if auto_include:
                include_image(jpeg_filename)
            
            return True, jpeg_filename, "HEIC успешно конвертирован в JPEG"
            
        else:
            # Для других форматов используем универсальную функцию
            try:
                # Копируем временный файл в целевую директорию и проверяем на валидность
                with Image.open(tmp_file_path) as img:
                    # Проверка на валидность изображения
                    try:
                        img.verify()  # Проверка корректности данных
                    except Exception as e:
                        os.unlink(tmp_file_path)
                        return False, None, f"Некорректное изображение: {str(e)}"
                    
                    # Если формат не JPEG/JPG, конвертируем в JPEG для унификации
                    if file_extension.lower() not in ('.jpg', '.jpeg'):
                        jpeg_path = heic_converter.convert_image_to_jpeg(
                            tmp_file_path, 
                            images_dir, 
                            quality=quality, 
                            check_duplicates=False
                        )
                        
                        if jpeg_path:
                            jpeg_filename = os.path.basename(jpeg_path)
                            # Если нужно автоматически включить в галерею
                            if auto_include:
                                include_image(jpeg_filename)
                            os.unlink(tmp_file_path)
                            return True, jpeg_filename, f"Формат {file_extension} успешно конвертирован в JPEG"
                    
                    # Если это уже JPEG, просто копируем файл
                    shutil.copy2(tmp_file_path, new_file_path)
                    os.unlink(tmp_file_path)
                    
                    # Если нужно автоматически включить в галерею
                    if auto_include:
                        include_image(new_filename)
                    
                    return True, new_filename, "Изображение успешно загружено"
                    
            except UnidentifiedImageError:
                os.unlink(tmp_file_path)
                return False, None, f"Неподдерживаемый формат изображения: {file_extension}"
            
            except Exception as e:
                os.unlink(tmp_file_path)
                return False, None, f"Ошибка при обработке изображения: {str(e)}"
    
    except Exception as e:
        logging.error(f"Ошибка при загрузке изображения: {str(e)}")
        # Очистка временных файлов
        try:
            # Проверяем, существуют ли переменные и файлы перед удалением
            if 'tmp_file_path' in locals():
                tmp_path = locals()['tmp_file_path']
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
            if 'new_file_path' in locals():
                new_path = locals()['new_file_path']
                if os.path.exists(new_path):
                    os.remove(new_path)
        except Exception as cleanup_error:
            logging.error(f"Ошибка при очистке временных файлов: {str(cleanup_error)}")
            
        return False, None, f"Ошибка: {str(e)}"

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
                img_path = os.path.join(images_dir, file)
                if is_valid_image(img_path):
                    images.append(file)
                else:
                    logging.warning(f"Пропускаем некорректное изображение: {file}")
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

def detect_duplicate_images(images_dir, check_content=True):
    """
    Обнаруживает дубликаты изображений с использованием различных методов проверки.
    
    Args:
        images_dir (str): Путь к директории с изображениями
        check_content (bool): Использовать хеш содержимого для поиска дубликатов
        
    Returns:
        list: Список групп дубликатов
    """
    import heic_converter
    
    # Проверяем существование директории
    if not os.path.exists(images_dir) or not os.path.isdir(images_dir):
        st.error(f"Директория {images_dir} не существует")
        return []
    
    # Используем более продвинутую функцию из heic_converter
    try:
        duplicates = heic_converter.find_duplicates_in_directory(images_dir, check_content)
        return duplicates
    except Exception as e:
        st.error(f"Ошибка при поиске дубликатов: {str(e)}")
        
        # Запасной вариант - проверка по размеру файла
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

def batch_process_images(images_dir, action, image_names):
    """
    Выполняет пакетную обработку изображений
    
    Args:
        images_dir (str): Путь к директории с изображениями
        action (str): Действие для выполнения ('include', 'exclude', 'delete')
        image_names (list): Список имен изображений для обработки
        
    Returns:
        tuple: (успешно обработано, ошибки)
    """
    success_count = 0
    error_count = 0
    
    for img_name in image_names:
        try:
            if action == 'include':
                include_image(img_name)
                success_count += 1
            elif action == 'exclude':
                exclude_image(img_name)
                success_count += 1
            elif action == 'delete':
                if delete_image_permanently(img_name, images_dir):
                    success_count += 1
                else:
                    error_count += 1
        except Exception as e:
            logging.error(f"Ошибка при пакетной обработке {img_name}: {str(e)}")
            error_count += 1
    
    return success_count, error_count

def get_image_status_statistics(images_dir):
    """
    Получает статистику по статусу изображений (активные/исключенные)
    
    Args:
        images_dir (str): Путь к директории с изображениями
    
    Returns:
        dict: Словарь с количеством активных и исключенных изображений
    """
    all_images = get_all_gallery_images(images_dir)
    config = load_gallery_config()
    
    active_count = 0
    excluded_count = 0
    
    for image in all_images:
        if image in config["excluded_images"]:
            excluded_count += 1
        else:
            active_count += 1
    
    return {
        "total": len(all_images),
        "active": active_count,
        "excluded": excluded_count
    }

def render_gallery_admin_interface(images_dir):
    """
    Отображает интерфейс администрирования галереи.
    
    Args:
        images_dir (str): Путь к директории с изображениями
    """
    st.title("Администрирование галереи")
    
    # Инициализируем в сессионном стейте хранилище выбранных изображений
    if 'selected_images' not in st.session_state:
        st.session_state.selected_images = set()
        
    # Инициализируем состояние для отслеживания успешных загрузок
    if 'uploaded_images' not in st.session_state:
        st.session_state.uploaded_images = []
    
    # Загружаем конфигурацию
    config = load_gallery_config()
    
    # Получаем все изображения
    all_images = get_all_gallery_images(images_dir)
    
    # Секция для загрузки новых изображений
    st.header("📤 Загрузка новых изображений")
    
    with st.expander("Открыть форму загрузки новых изображений", expanded=False):
        # Описание функциональности
        st.markdown("""
        ### Загрузите одно или несколько изображений для добавления в галерею
        Поддерживаемые форматы: JPG, PNG, HEIC (будет конвертирован в JPEG автоматически)
        
        Изображения будут добавлены в галерею и автоматически опубликованы.
        """)
        
        # Загрузчик файлов с поддержкой множественной загрузки
        uploaded_files = st.file_uploader("Выберите изображения для загрузки", 
                                            type=["jpg", "jpeg", "png", "heic", "heif"], 
                                            accept_multiple_files=True)
        
        auto_publish = st.checkbox("Автоматически публиковать загруженные изображения", value=True)
        
        if uploaded_files:
            if st.button("Загрузить выбранные изображения", type="primary"):
                with st.spinner("Загрузка и обработка изображений..."):
                    success_count = 0
                    error_count = 0
                    st.session_state.uploaded_images = []
                    
                    for uploaded_file in uploaded_files:
                        success, img_name, message = upload_new_image(uploaded_file, images_dir, auto_publish, check_duplicates=True, quality=90)
                        if success:
                            success_count += 1
                            st.session_state.uploaded_images.append(img_name)
                            st.info(message) # Отображаем информационное сообщение о результате
                        else:
                            error_count += 1
                            st.warning(message) # Отображаем предупреждение с причиной ошибки
                    
                    if success_count > 0:
                        st.success(f"Успешно загружено {success_count} изображений")
                    if error_count > 0:
                        st.error(f"Не удалось загрузить {error_count} изображений")
                        
                    # Обновляем список всех изображений
                    all_images = get_all_gallery_images(images_dir)
                    
                    # Добавляем небольшую задержку для корректного обновления UI
                    import time
                    time.sleep(0.5)
                    st.rerun()
        
        # Если были успешно загруженные изображения, показываем их
        if st.session_state.uploaded_images:
            st.subheader("Недавно загруженные изображения")
            
            # Показываем загруженные изображения в сетке
            cols = st.columns(min(3, len(st.session_state.uploaded_images)))
            for i, img_name in enumerate(st.session_state.uploaded_images):
                img_path = os.path.join(images_dir, img_name)
                if os.path.exists(img_path):
                    with cols[i % 3]:
                        try:
                            st.image(img_path, caption=img_name, width=150)
                        except Exception as e:
                            st.error(f"Ошибка отображения загруженного изображения: {str(e)}")
    
    # Секция для поиска и обработки дубликатов
    st.header("🔍 Поиск дубликатов изображений")
    
    # Форма для запуска поиска дубликатов
    st.markdown("""
    ### Инструменты обнаружения дубликатов
    Система может автоматически находить похожие изображения, которые могут быть дубликатами.
    Проверка может выполняться по имени файла или по содержимому (наиболее точный метод).
    """)
    
    check_content = st.checkbox("Использовать проверку по содержимому (более точная, но медленнее)", value=True)
    
    if st.button("Найти дубликаты", type="primary"):
        with st.spinner("Поиск дубликатов..."):
            # Обнаруживаем дубликаты
            duplicates = detect_duplicate_images(images_dir, check_content=check_content)
            st.session_state.duplicates = duplicates
            
            if duplicates:
                st.warning(f"Обнаружено {len(duplicates)} групп дубликатов")
            else:
                st.success("Дубликаты не обнаружены")
    
    # Если есть найденные дубликаты, показываем их
    if 'duplicates' in st.session_state and st.session_state.duplicates:
        duplicates = st.session_state.duplicates
        
        st.subheader(f"Найденные дубликаты ({len(duplicates)} групп)")
        
        # Отображаем каждую группу дубликатов
        for i, group in enumerate(duplicates):
            st.markdown(f"### Группа дубликатов {i+1} ({len(group)} файлов)")
            
            # Форма группового удаления
            if len(group) > 1:
                group_message = f"Оставить только первое изображение, исключить остальные {len(group)-1}"
                if st.button(group_message, key=f"clean_duplicates_{i}"):
                    keep_file = group[0]
                    files_to_exclude = group[1:]
                    
                    for img_name in files_to_exclude:
                        exclude_image(img_name)
                    
                    st.success(f"Оставлено изображение '{keep_file}', исключены: {', '.join(files_to_exclude)}")
                    st.rerun()
            
            # Макс. количество изображений в одной строке
            max_cols = min(3, len(group))
            for j in range(0, len(group), max_cols):
                cols = st.columns(max_cols)
                for k in range(max_cols):
                    if j+k < len(group):
                        img_name = group[j+k]
                        img_path = os.path.join(images_dir, img_name)
                        with cols[k]:
                            try:
                                st.image(img_path, caption=img_name, width=150)
                                
                                is_excluded = img_name in load_gallery_config()["excluded_images"]
                                status = "🚫 Исключено" if is_excluded else "✅ Активно"
                                
                                st.write(f"Статус: {status}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if is_excluded:
                                        if st.button(f"📢 Опубликовать", key=f"dupl_include_{i}_{j+k}"):
                                            include_image(img_name)
                                            st.success(f"Изображение {img_name} опубликовано")
                                            st.rerun()
                                    else:
                                        if st.button(f"🚫 Исключить", key=f"dupl_exclude_{i}_{j+k}"):
                                            exclude_image(img_name)
                                            st.success(f"Изображение {img_name} исключено из галереи")
                                            st.rerun()
                                
                                with col2:
                                    if st.button(f"❌ Удалить", key=f"dupl_delete_{i}_{j+k}", type="primary"):
                                        if delete_image_permanently(img_name, images_dir):
                                            st.success(f"Изображение {img_name} удалено")
                                            st.rerun()
                                        else:
                                            st.error(f"Не удалось удалить {img_name}")
                            except Exception as e:
                                st.error(f"Ошибка отображения {img_name}: {str(e)}")
                                if st.button(f"❌ Удалить поврежденный файл", key=f"dupl_delete_corrupt_{i}_{j+k}"):
                                    if delete_image_permanently(img_name, images_dir):
                                        st.success(f"Изображение {img_name} удалено")
                                        st.rerun()
                                    else:
                                        st.error(f"Не удалось удалить {img_name}")
            # Разделитель между группами дубликатов
            st.markdown("---")
    
    # Вкладки для управления изображениями
    tab1, tab2, tab3 = st.tabs(["Все изображения", "Активные", "Исключенные"])
    
    with tab1:
        st.subheader("Все доступные изображения")
        
        # Функция для обработки изменения чекбокса
        def handle_checkbox_change(img_name):
            if img_name in st.session_state.selected_images:
                st.session_state.selected_images.remove(img_name)
            else:
                st.session_state.selected_images.add(img_name)
        
        # Кнопки для групповых операций с выбранными изображениями
        if all_images:
            st.markdown("### Групповые операции")
            st.markdown("Выберите изображения с помощью чекбоксов для группового изменения статуса")
            
            # Получаем статистику по изображениям
            stats = get_image_status_statistics(images_dir)
            status_cols = st.columns(3)
            with status_cols[0]:
                st.metric("Всего изображений", stats["total"])
            with status_cols[1]:
                st.metric("Активных изображений", stats["active"])
            with status_cols[2]:
                st.metric("Исключенных", stats["excluded"])
                
            # Добавляем выпадающий список с опциями для быстрого выбора
            select_options = [
                "Все изображения",
                "Только активные изображения",
                "Только исключенные изображения",
                "Снять выделение"
            ]
            selection_action = st.selectbox(
                "Быстрое выделение изображений:",
                select_options,
                index=0,
                key="quick_selection"
            )
            
            # Обработка выбора пользователя
            if st.button("Применить выбор", key="apply_selection_btn"):
                config = load_gallery_config()
                
                if selection_action == select_options[0]:  # Выбрать все
                    st.session_state.selected_images = set(all_images)
                elif selection_action == select_options[1]:  # Только активные
                    active_images = [img for img in all_images if img not in config["excluded_images"]]
                    st.session_state.selected_images = set(active_images)
                elif selection_action == select_options[2]:  # Только исключенные
                    excluded_images = [img for img in all_images if img in config["excluded_images"]]
                    st.session_state.selected_images = set(excluded_images)
                elif selection_action == select_options[3]:  # Снять выделение
                    st.session_state.selected_images = set()
                
                st.rerun()
            
            # Основные кнопки действий
            action_cols = st.columns(4)
            with action_cols[0]:
                if st.button("Выбрать все", key="select_all_btn"):
                    st.session_state.selected_images = set(all_images)
                    st.rerun()
            
            with action_cols[1]:
                if st.button("Снять выбор", key="deselect_all_btn"):
                    st.session_state.selected_images = set()
                    st.rerun()
            
            with action_cols[2]:
                # Кнопка групповой публикации
                if st.button("📢 Опубликовать выбранные", disabled=len(st.session_state.selected_images) == 0):
                    success_count, error_count = batch_process_images(images_dir, 'include', list(st.session_state.selected_images))
                    st.success(f"✅ Опубликовано {success_count} изображений")
                    if error_count > 0:
                        st.error(f"❌ Не удалось опубликовать {error_count} изображений")
                    # Очищаем выбор после операции
                    st.session_state.selected_images = set()
                    st.rerun()
            
            with action_cols[3]:
                # Кнопка группового исключения
                if st.button("🚫 Исключить выбранные", disabled=len(st.session_state.selected_images) == 0):
                    success_count, error_count = batch_process_images(images_dir, 'exclude', list(st.session_state.selected_images))
                    st.success(f"✅ Исключено {success_count} изображений")
                    if error_count > 0:
                        st.error(f"❌ Не удалось исключить {error_count} изображений")
                    # Очищаем выбор после операции
                    st.session_state.selected_images = set()
                    st.rerun()
            
            # Кнопка группового удаления с запросом подтверждения
            delete_confirm = st.checkbox("Подтвердить удаление выбранных изображений", key="confirm_batch_delete")
            if st.button("❌ Удалить выбранные навсегда", 
                        disabled=len(st.session_state.selected_images) == 0 or not delete_confirm,
                        type="primary"):
                success_count, error_count = batch_process_images(images_dir, 'delete', list(st.session_state.selected_images))
                st.success(f"✅ Удалено {success_count} изображений")
                if error_count > 0:
                    st.error(f"❌ Не удалось удалить {error_count} изображений")
                # Очищаем выбор после операции
                st.session_state.selected_images = set()
                st.rerun()
            
            st.markdown(f"Выбрано изображений: **{len(st.session_state.selected_images)}**")
            
        # Разбиваем на строки с 2 колонками для лучшего отображения кнопок
        for i in range(0, len(all_images), 2):
            cols = st.columns(2)
            for j in range(2):
                if i+j < len(all_images):
                    img_name = all_images[i+j]
                    img_path = os.path.join(images_dir, img_name)
                    
                    with cols[j]:
                        # Добавляем чекбокс для выбора изображения
                        is_selected = img_name in st.session_state.selected_images
                        checkbox_key = f"cb_all_{img_name}"
                        
                        row_cols = st.columns([1, 9])
                        with row_cols[0]:
                            # Чекбокс с уникальным ключом
                            st.checkbox("Выбрать", value=is_selected, key=checkbox_key, 
                                       on_change=handle_checkbox_change, args=(img_name,),
                                       label_visibility="collapsed")
                        
                        with row_cols[1]:
                            try:
                                st.image(img_path, caption=img_name, width=150)
                            except Exception as e:
                                st.error(f"Ошибка отображения {img_name}: {str(e)}")
                                st.warning("Рекомендуется исключить этот файл")
                        
                        # Добавляем кнопки управления в ряд
                        button_cols = st.columns(3)
                        
                        # Первая кнопка - включить/исключить
                        with button_cols[0]:
                            if img_name in config["excluded_images"]:
                                if st.button(f"📢 Опубликовать", key=f"all_include_{img_name}"):
                                    include_image(img_name)
                                    st.success(f"Изображение {img_name} включено в галерею")
                                    st.rerun()
                            else:
                                if st.button(f"🚫 Исключить", key=f"all_exclude_{img_name}"):
                                    exclude_image(img_name)
                                    st.success(f"Изображение {img_name} исключено из галереи")
                                    st.rerun()
                        
                        # Вторая кнопка - статус
                        with button_cols[1]:
                            if img_name in config["excluded_images"]:
                                st.error("Исключено")
                            else:
                                st.success("Активно")
                                
                        # Третья кнопка - удалить навсегда
                        with button_cols[2]:
                            if st.button(f"❌ Удалить", key=f"all_delete_{img_name}", type="primary"):
                                # Запрашиваем подтверждение
                                if st.checkbox(f"Подтвердить удаление {img_name}", key=f"all_confirm_{img_name}"):
                                    if delete_image_permanently(img_name, images_dir):
                                        st.success(f"Изображение {img_name} удалено навсегда (резервная копия в {images_dir}/deleted_images)")
                                    else:
                                        st.error(f"Не удалось удалить изображение {img_name}")
                                    st.rerun()
    
    with tab2:
        st.subheader("Активные изображения")
        active_images = get_active_gallery_images(images_dir)
        
        if not active_images:
            st.info("Нет активных изображений")
        else:
            # Кнопки для групповых операций с выбранными активными изображениями
            st.markdown("### Групповые операции")
            st.markdown("Выберите изображения с помощью чекбоксов для группового изменения статуса")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Выбрать все активные", key="select_all_active_btn"):
                    st.session_state.selected_images = set(active_images)
                    st.rerun()
            
            with col2:
                # Кнопка группового исключения
                if st.button("🚫 Исключить выбранные", key="batch_exclude_active_btn", 
                           disabled=len(st.session_state.selected_images) == 0):
                    success_count, error_count = batch_process_images(images_dir, 'exclude', list(st.session_state.selected_images))
                    st.success(f"✅ Исключено {success_count} изображений")
                    if error_count > 0:
                        st.error(f"❌ Не удалось исключить {error_count} изображений")
                    # Очищаем выбор после операции
                    st.session_state.selected_images = set()
                    st.rerun()
            
            with col3:
                # Кнопка группового удаления с запросом подтверждения
                delete_confirm = st.checkbox("Подтвердить удаление выбранных активных изображений", key="confirm_batch_delete_active")
                if st.button("❌ Удалить выбранные навсегда", key="batch_delete_active_btn", 
                          disabled=len(st.session_state.selected_images) == 0 or not delete_confirm,
                          type="primary"):
                    success_count, error_count = batch_process_images(images_dir, 'delete', list(st.session_state.selected_images))
                    st.success(f"✅ Удалено {success_count} изображений")
                    if error_count > 0:
                        st.error(f"❌ Не удалось удалить {error_count} изображений")
                    # Очищаем выбор после операции
                    st.session_state.selected_images = set()
                    st.rerun()
            
            st.markdown(f"Выбрано активных изображений: **{len([img for img in st.session_state.selected_images if img in active_images])}**")
            
            # Отображаем изображения с чекбоксами
            for i in range(0, len(active_images), 2):  # Уменьшаем до 2 колонок для более удобного размещения кнопок
                cols = st.columns(2)
                for j in range(2):
                    if i+j < len(active_images):
                        img_name = active_images[i+j]
                        img_path = os.path.join(images_dir, img_name)
                        
                        with cols[j]:
                            # Добавляем чекбокс для выбора изображения
                            is_selected = img_name in st.session_state.selected_images
                            checkbox_key = f"cb_active_{img_name}"
                            
                            row_cols = st.columns([1, 9])
                            with row_cols[0]:
                                # Чекбокс с уникальным ключом
                                st.checkbox("Выбрать", value=is_selected, key=checkbox_key, 
                                           on_change=handle_checkbox_change, args=(img_name,),
                                           label_visibility="collapsed")
                            
                            with row_cols[1]:
                                try:
                                    st.image(img_path, caption=img_name, width=150)
                                except Exception as e:
                                    st.error(f"Ошибка отображения {img_name}: {str(e)}")
                                    st.warning("Рекомендуется исключить этот файл из галереи")
                            
                            # Добавляем три кнопки управления в один ряд  
                            button_cols = st.columns(3)
                            with button_cols[0]:
                                if st.button(f"📢 Опубликовать", key=f"publish_{img_name}"):
                                    # Уже опубликовано, так как это активный режим, поэтому просто показываем сообщение
                                    st.success(f"Изображение {img_name} опубликовано")
                                    st.rerun()
                            
                            with button_cols[1]:
                                if st.button(f"🚫 Исключить", key=f"exclude_{img_name}"):
                                    exclude_image(img_name)
                                    st.success(f"Изображение {img_name} исключено из галереи")
                                    st.rerun()
                            
                            with button_cols[2]:
                                # Добавляем предупреждающий цвет для кнопки удаления
                                if st.button(f"❌ Удалить", key=f"delete_{img_name}", type="primary"):
                                    # Запрашиваем подтверждение удаления
                                    if st.checkbox(f"Подтвердить удаление {img_name}", key=f"confirm_{img_name}"):
                                        if delete_image_permanently(img_name, images_dir):
                                            st.success(f"Изображение {img_name} удалено навсегда (резервная копия сохранена в {images_dir}/deleted_images)")
                                        else:
                                            st.error(f"Не удалось удалить изображение {img_name}")
                                        st.rerun()
    
    with tab3:
        st.subheader("Исключенные изображения")
        
        if not config["excluded_images"]:
            st.info("Нет исключенных изображений")
        else:
            # Кнопки для групповых операций с выбранными исключенными изображениями
            st.markdown("### Групповые операции")
            st.markdown("Выберите изображения с помощью чекбоксов для группового изменения статуса")
            
            excluded_files_exist = False
            # Проверяем, существуют ли файлы хотя бы для одного исключенного изображения
            for img_name in config["excluded_images"]:
                img_path = os.path.join(images_dir, img_name)
                if os.path.exists(img_path) and is_valid_image(img_path):
                    excluded_files_exist = True
                    break
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Выбрать все исключенные", key="select_all_excluded_btn"):
                    # Выбираем только те исключенные файлы, которые физически существуют
                    valid_excluded = []
                    for img_name in config["excluded_images"]:
                        img_path = os.path.join(images_dir, img_name)
                        if os.path.exists(img_path) and is_valid_image(img_path):
                            valid_excluded.append(img_name)
                    
                    st.session_state.selected_images = set(valid_excluded)
                    st.rerun()
            
            with col2:
                # Кнопка групповой публикации
                if st.button("📢 Вернуть выбранные в галерею", key="batch_include_excluded_btn", 
                           disabled=len(st.session_state.selected_images) == 0 or not excluded_files_exist):
                    success_count, error_count = batch_process_images(images_dir, 'include', list(st.session_state.selected_images))
                    st.success(f"✅ Возвращено в галерею {success_count} изображений")
                    if error_count > 0:
                        st.error(f"❌ Не удалось вернуть {error_count} изображений")
                    # Очищаем выбор после операции
                    st.session_state.selected_images = set()
                    st.rerun()
            
            # Кнопка группового удаления с запросом подтверждения
            delete_confirm = st.checkbox("Подтвердить удаление выбранных исключенных изображений", key="confirm_batch_delete_excluded")
            if st.button("❌ Удалить выбранные навсегда", key="batch_delete_excluded_btn", 
                        disabled=len(st.session_state.selected_images) == 0 or not delete_confirm or not excluded_files_exist,
                        type="primary"):
                success_count, error_count = batch_process_images(images_dir, 'delete', list(st.session_state.selected_images))
                st.success(f"✅ Удалено {success_count} изображений")
                if error_count > 0:
                    st.error(f"❌ Не удалось удалить {error_count} изображений")
                # Очищаем выбор после операции
                st.session_state.selected_images = set()
                st.rerun()
            
            st.markdown(f"Выбрано исключенных изображений: **{len([img for img in st.session_state.selected_images if img in config['excluded_images']])}**")
            
            # Отображаем изображения с чекбоксами
            for i in range(0, len(config["excluded_images"]), 2):  # Уменьшаем до 2 колонок для лучшего отображения кнопок
                cols = st.columns(2)
                for j in range(2):
                    if i+j < len(config["excluded_images"]):
                        img_name = config["excluded_images"][i+j]
                        img_path = os.path.join(images_dir, img_name)
                        
                        with cols[j]:
                            if os.path.exists(img_path) and is_valid_image(img_path):
                                # Добавляем чекбокс для выбора изображения
                                is_selected = img_name in st.session_state.selected_images
                                checkbox_key = f"cb_excluded_{img_name}"
                                
                                row_cols = st.columns([1, 9])
                                with row_cols[0]:
                                    # Чекбокс с уникальным ключом
                                    st.checkbox("Выбрать", value=is_selected, key=checkbox_key, 
                                               on_change=handle_checkbox_change, args=(img_name,),
                                               label_visibility="collapsed")
                                
                                with row_cols[1]:
                                    try:
                                        st.image(img_path, caption=img_name, width=150)
                                    except Exception as e:
                                        st.error(f"Ошибка отображения {img_name}: {str(e)}")
                                        st.warning("Рекомендуется удалить этот файл")
                                
                                # Добавляем кнопки управления в ряд
                                button_cols = st.columns(2)
                                with button_cols[0]:
                                    if st.button(f"📢 Вернуть в галерею", key=f"return_{img_name}"):
                                        include_image(img_name)
                                        st.success(f"Изображение {img_name} возвращено в галерею")
                                        st.rerun()
                                
                                with button_cols[1]:
                                    # Добавляем кнопку для удаления
                                    if st.button(f"❌ Удалить навсегда", key=f"delete_excluded_{img_name}", type="primary"):
                                        # Запрашиваем подтверждение удаления
                                        if st.checkbox(f"Подтвердить удаление {img_name}", key=f"confirm_excluded_{img_name}"):
                                            if delete_image_permanently(img_name, images_dir):
                                                st.success(f"Изображение {img_name} удалено навсегда (резервная копия сохранена в {images_dir}/deleted_images)")
                                            else:
                                                st.error(f"Не удалось удалить изображение {img_name}")
                                            st.rerun()
                            else:
                                # Для несуществующих или некорректных файлов не показываем чекбокс
                                if not os.path.exists(img_path):
                                    st.error(f"Файл {img_name} не найден")
                                else:
                                    st.error(f"Файл {img_name} поврежден или имеет неподдерживаемый формат")
                                
                                # Добавляем кнопку только для удаления из списка исключенных
                                if st.button(f"🧹 Удалить из списка исключенных", key=f"remove_from_excluded_{img_name}"):
                                    if img_name in config["excluded_images"]:
                                        config["excluded_images"].remove(img_name)
                                        save_gallery_config(config)
                                        st.success(f"Изображение {img_name} удалено из списка исключенных")
                                        st.rerun()
    
    # Секция для обработки проблемных файлов HEIC
    st.markdown("---")
    st.subheader("🛠️ Обработка проблемных файлов")
    
    # Проверяем наличие файлов HEIC в директории
    heic_files = []
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.heic', '.heif')):
            heic_files.append(file)
    
    if heic_files:
        st.warning(f"Обнаружено {len(heic_files)} файлов формата HEIC/HEIF, которые могут не отображаться корректно")
        st.info("Эти файлы можно автоматически конвертировать в JPEG для корректного отображения в галерее")
        
        # Кнопка для конвертации всех HEIC файлов
        if st.button("Конвертировать все HEIC файлы в JPEG"):
            try:
                # Пытаемся импортировать модуль конвертера
                import heic_converter
                
                success_count = 0
                error_count = 0
                
                for heic_file in heic_files:
                    heic_path = os.path.join(images_dir, heic_file)
                    try:
                        # Конвертируем файл, получаем путь к новому файлу
                        jpeg_path = heic_converter.heic_to_jpeg(heic_path)
                        
                        if jpeg_path:
                            success_count += 1
                            # Обновляем список исключений, если файл был исключен
                            if heic_file in config["excluded_images"]:
                                # Извлекаем имя файла из полного пути
                                jpeg_filename = os.path.basename(jpeg_path)
                                # Исключаем также и JPEG версию
                                if jpeg_filename not in config["excluded_images"]:
                                    config["excluded_images"].append(jpeg_filename)
                        else:
                            error_count += 1
                    except Exception as e:
                        st.error(f"Ошибка конвертации {heic_file}: {str(e)}")
                        error_count += 1
                
                # Сохраняем обновленную конфигурацию
                save_gallery_config(config)
                
                if success_count > 0:
                    st.success(f"Успешно конвертировано {success_count} файлов HEIC в JPEG")
                if error_count > 0:
                    st.error(f"Не удалось конвертировать {error_count} файлов")
                    
                # Перезагружаем страницу для отображения изменений
                st.rerun()
                    
            except ImportError:
                st.error("Модуль heic_converter не найден. Убедитесь, что файл heic_converter.py существует в проекте.")
    else:
        st.success("Проблемных файлов HEIC/HEIF не обнаружено.")
    
    # Кнопка для сброса настроек
    st.markdown("---")
    if st.button("Сбросить настройки галереи"):
        save_gallery_config(DEFAULT_CONFIG)
        st.success("Настройки галереи сброшены")
        st.rerun()