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
        
def upload_new_image(uploaded_file, images_dir, auto_include=True):
    """
    Загружает новое изображение в директорию галереи и автоматически включает его в активные
    
    Args:
        uploaded_file: Загруженный файл из st.file_uploader
        images_dir (str): Путь к директории галереи
        auto_include (bool): Автоматически включить в активные изображения
        
    Returns:
        tuple: (успешно ли загружено, имя файла)
    """
    if uploaded_file is None:
        return False, None
        
    # Создаем уникальное имя для файла, чтобы избежать конфликтов
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    random_suffix = uuid.uuid4().hex[:8]
    new_filename = f"{os.path.splitext(uploaded_file.name)[0]}_{random_suffix}{file_extension}"
    
    # Полный путь к новому файлу
    new_file_path = os.path.join(images_dir, new_filename)
    
    try:
        # Проверяем формат файла через PIL
        try:
            with Image.open(uploaded_file) as img:
                # Сохраняем временный файл для проверки
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    img.save(tmp_file.name)
                    
                    # Проверяем корректность сохраненного изображения
                    if not is_valid_image(tmp_file.name):
                        os.unlink(tmp_file.name)
                        return False, None
                        
                    # Если все хорошо, копируем во целевую директорию
                    shutil.copy2(tmp_file.name, new_file_path)
                    os.unlink(tmp_file.name)
        except UnidentifiedImageError:
            # Если это HEIC/HEIF формат, попробуем конвертировать
            if file_extension.lower() in ('.heic', '.heif'):
                # Сначала сохраняем загруженный файл
                with open(new_file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Проверяем доступность модуля heic_converter
                try:
                    import heic_converter
                    # Конвертируем HEIC в JPEG
                    jpeg_path = heic_converter.heic_to_jpeg(new_file_path)
                    
                    # Если конвертация не удалась, удаляем исходный файл
                    if not jpeg_path or not os.path.exists(jpeg_path):
                        if os.path.exists(new_file_path):
                            os.remove(new_file_path)
                        return False, None
                        
                    # Новый файл с расширением jpg - его имя возвращается из heic_to_jpeg
                    new_filename = os.path.basename(jpeg_path)
                    
                except ImportError:
                    # Если модуль не найден, просто удаляем файл
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    return False, None
            else:
                # Если не HEIC и не распознается PIL, отклоняем файл
                return False, None
                
        # Если нужно автоматически включить в галерею
        if auto_include:
            include_image(new_filename)
            
        return True, new_filename
        
    except Exception as e:
        logging.error(f"Ошибка при загрузке изображения: {str(e)}")
        # Очистка - удаляем файл в случае ошибки
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        return False, None

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
                        success, img_name = upload_new_image(uploaded_file, images_dir, auto_publish)
                        if success:
                            success_count += 1
                            st.session_state.uploaded_images.append(img_name)
                        else:
                            error_count += 1
                    
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
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Выбрать все", key="select_all_btn"):
                    st.session_state.selected_images = set(all_images)
                    st.rerun()
            
            with col2:
                if st.button("Снять выбор", key="deselect_all_btn"):
                    st.session_state.selected_images = set()
                    st.rerun()
            
            with col3:
                # Кнопка групповой публикации
                if st.button("📢 Опубликовать выбранные", disabled=len(st.session_state.selected_images) == 0):
                    success_count, error_count = batch_process_images(images_dir, 'include', list(st.session_state.selected_images))
                    st.success(f"✅ Опубликовано {success_count} изображений")
                    if error_count > 0:
                        st.error(f"❌ Не удалось опубликовать {error_count} изображений")
                    # Очищаем выбор после операции
                    st.session_state.selected_images = set()
                    st.rerun()
            
            with col4:
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