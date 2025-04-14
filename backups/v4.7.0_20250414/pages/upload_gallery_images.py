"""
Страница для загрузки и управления изображениями в галерее.
Автоматизирует процесс обработки и оптимизации изображений перед добавлением.
"""

import os
import tempfile
import streamlit as st
import logging
import sys
from datetime import datetime
from PIL import Image

# Добавляем путь для импорта компонентов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Импортируем компоненты для работы с галереей
from components import auto_gallery_uploader, gallery_admin, gallery
from components.admin_auth import admin_required, check_admin_auth, admin_login_form
import heic_converter

# Настройка страницы
st.set_page_config(
    page_title="Управление изображениями галереи",
    page_icon="🖼️",
    layout="wide"
)

# Настройка стилей
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        margin-bottom: 1rem;
    }
    .step-container {
        border-left: 3px solid #4A90E2;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    .success-message {
        background-color: #E6F4EA;
        border-left: 4px solid #34A853;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .warning-message {
        background-color: #FEF7E0;
        border-left: 4px solid #FBBC04;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .info-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def render_upload_section():
    """Отображает секцию загрузки индивидуальных изображений."""
    st.subheader("Загрузка изображений")
    
    with st.expander("Инструкция по загрузке", expanded=False):
        st.markdown("""
        ### Как загружать изображения
        1. **Выберите файл** с помощью кнопки "Обзор файлов"
        2. **Добавьте описание** или оставьте поле пустым для автоматической генерации
        3. **Выберите опции обработки**:
            - Автоматическое добавление в галерею
            - Оптимизация размера
            - Конвертация из HEIC
        4. **Нажмите кнопку "Обработать изображение"**
        """)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.write("Выберите изображение для загрузки в галерею:")
        uploaded_file = st.file_uploader(
            "Поддерживаемые форматы: JPG, PNG, HEIC",
            type=['jpg', 'jpeg', 'png', 'heic', 'heif'],
            key="main_uploader"
        )
        
        # Опции обработки
        options_cols = st.columns(4)
        with options_cols[0]:
            add_to_gallery = st.checkbox("Добавить в галерею", value=True)
        with options_cols[1]:
            optimize_size = st.checkbox("Оптимизировать размер", value=True)
        with options_cols[2]:
            normalize_size = st.checkbox("Нормализовать размер", value=True, 
                                         help="Приведение всех изображений к единому стандартному размеру для галереи")
        with options_cols[3]:
            convert_heic = st.checkbox("Конвертировать HEIC", value=True)
            
        # Поле для описания
        custom_description = st.text_area(
            "Описание изображения (оставьте пустым для автоматической генерации)", 
            height=100
        )
        
        # Кнопка обработки
        process_button = st.button(
            "Обработать изображение", 
            type="primary",
            use_container_width=True
        )
    
    # Предпросмотр изображения и информация
    with col2:
        if uploaded_file is not None:
            try:
                # Временное сохранение для предпросмотра
                temp_file = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Обработка HEIC файлов для предпросмотра
                preview_path = temp_file
                if temp_file.lower().endswith(('.heic', '.heif')) and convert_heic:
                    jpeg_path = heic_converter.heic_to_jpeg(temp_file, preserve_original=True)
                    if jpeg_path:
                        preview_path = jpeg_path
                
                # Показываем предпросмотр
                st.image(preview_path, caption="Предпросмотр изображения", use_column_width=True)
                
                # Информация о файле
                file_name = os.path.basename(temp_file)
                file_size_mb = os.path.getsize(temp_file) / (1024 * 1024)
                
                st.markdown(f"""
                <div class="info-card">
                    <h4>Информация о файле:</h4>
                    <p><strong>Имя файла:</strong> {file_name}</p>
                    <p><strong>Размер:</strong> {file_size_mb:.2f} МБ</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Оптимизированное имя файла
                optimized_name = auto_gallery_uploader.sanitize_filename(file_name)
                st.markdown(f"""
                <div class="info-card">
                    <h4>После обработки:</h4>
                    <p><strong>Имя файла:</strong> {optimized_name}</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Ошибка предпросмотра: {str(e)}")
        else:
            st.markdown("""
            <div class="info-card" style="text-align: center; padding: 50px 20px;">
                <h3>Предпросмотр изображения</h3>
                <p>Загрузите файл для просмотра</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Обработка загрузки изображения
    if process_button and uploaded_file is not None:
        with st.spinner("Обработка изображения..."):
            try:
                # Сохраняем временно загруженный файл
                temp_file = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Обрабатываем загруженный файл
                success, target_path, message = auto_gallery_uploader.process_image(
                    temp_file, 
                    add_to_gallery=add_to_gallery,
                    preserve_original=True,
                    normalize_size=normalize_size
                )
                
                if success:
                    # Если есть пользовательское описание, обновляем его
                    if custom_description.strip() and target_path:
                        filename = os.path.basename(target_path)
                        auto_gallery_uploader.update_image_description(
                            filename, custom_description.strip()
                        )
                        
                    st.success(message)
                    
                    # Отображаем обработанное изображение
                    if target_path:
                        filename = os.path.basename(target_path)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(target_path, caption=f"Обработанное изображение", use_column_width=True)
                        with col2:
                            st.markdown(f"""
                            <div class="success-message">
                                <h4>Изображение успешно обработано!</h4>
                                <p><strong>Имя файла:</strong> {filename}</p>
                                <p><strong>Путь:</strong> {target_path}</p>
                                <p><strong>Добавлено в галерею:</strong> {'Да' if add_to_gallery else 'Нет'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Ошибка при обработке: {str(e)}")

def render_batch_processing():
    """Отображает секцию для пакетной обработки изображений."""
    st.subheader("Пакетная обработка изображений")
    
    with st.expander("О пакетной обработке", expanded=False):
        st.markdown("""
        ### Пакетная обработка изображений
        
        Эта функция позволяет обработать сразу несколько изображений из указанной директории.
        
        **Возможности:**
        - Обработка всех изображений в директории
        - Рекурсивный режим для вложенных папок
        - Автоматическое добавление в галерею
        - Подробный отчет о результатах
        
        **Поддерживаемые форматы:** JPG, PNG, HEIC, HEIF
        """)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        directory_path = st.text_input(
            "Путь к директории с изображениями", 
            value=gallery.IMAGES_DIR
        )
        
        batch_options = st.columns(3)
        with batch_options[0]:
            batch_add_to_gallery = st.checkbox("Добавить в галерею", value=True, key="batch_add_gallery")
        with batch_options[1]:
            batch_normalize_size = st.checkbox("Нормализовать размеры", value=True, key="batch_normalize",
                                            help="Приведение всех изображений к единому стандартному размеру для галереи")
        with batch_options[2]:
            recursive = st.checkbox("Рекурсивный режим", value=False, key="batch_recursive")
        
        start_batch = st.button(
            "Начать пакетную обработку", 
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if os.path.exists(directory_path):
            # Подсчитываем количество изображений в директории
            image_count = 0
            supported_exts = auto_gallery_uploader.SUPPORTED_EXTENSIONS
            
            for root, _, files in os.walk(directory_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in supported_exts:
                        image_count += 1
                        
                # Если не рекурсивный режим, прерываем после первой директории
                if not recursive:
                    break
            
            st.markdown(f"""
            <div class="info-card">
                <h4>Информация о директории:</h4>
                <p><strong>Путь:</strong> {directory_path}</p>
                <p><strong>Найдено изображений:</strong> {image_count}</p>
                <p><strong>Режим:</strong> {'Рекурсивный' if recursive else 'Только текущая директория'}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-message">
                <h4>Внимание!</h4>
                <p>Указанная директория не существует.</p>
                <p>Укажите правильный путь к директории с изображениями.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Обработка пакетной загрузки
    if start_batch:
        if os.path.exists(directory_path):
            with st.spinner("Выполняется пакетная обработка изображений..."):
                success_count, error_count, processed_files, errors = auto_gallery_uploader.batch_process_directory(
                    directory_path, 
                    add_to_gallery=batch_add_to_gallery, 
                    recursive=recursive, 
                    preserve_original=True,
                    normalize_size=batch_normalize_size
                )
                
                # Отображаем результаты
                st.markdown(f"""
                <div class="info-card">
                    <h4>Результаты пакетной обработки:</h4>
                    <p><strong>Успешно обработано:</strong> {success_count} изображений</p>
                    <p><strong>Ошибки:</strong> {error_count}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Показываем список обработанных файлов
                if processed_files:
                    with st.expander(f"Обработанные файлы ({len(processed_files)})", expanded=False):
                        for file_path in processed_files:
                            st.write(f"- {os.path.basename(file_path)}")
                
                # Показываем ошибки
                if errors:
                    with st.expander(f"Ошибки ({len(errors)})", expanded=True):
                        for error in errors:
                            st.markdown(f"<div class='warning-message'>{error}</div>", unsafe_allow_html=True)
        else:
            st.error("Указанная директория не существует")

def render_gallery_links():
    """Отображает ссылки на галерею и другие связанные страницы."""
    st.markdown("""
    <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
        <h3>Полезные ссылки</h3>
        <ul>
            <li><a href="/" target="_self">Главная страница калькулятора</a></li>
            <li><a href="/gallery_admin" target="_self">Управление галереей (включить/отключить изображения)</a></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_settings():
    """Отображает настройки обработки изображений."""
    st.subheader("Настройки обработки изображений")
    
    with st.form("image_settings_form"):
        st.write("Настройки качества и размера изображений:")
        
        col1, col2 = st.columns(2)
        with col1:
            max_width = st.number_input(
                "Максимальная ширина (пикс)", 
                min_value=800, 
                max_value=4000, 
                value=auto_gallery_uploader.MAX_IMAGE_WIDTH
            )
        with col2:
            max_height = st.number_input(
                "Максимальная высота (пикс)", 
                min_value=600, 
                max_value=3000, 
                value=auto_gallery_uploader.MAX_IMAGE_HEIGHT
            )
            
        jpeg_quality = st.slider(
            "Качество JPEG", 
            min_value=50, 
            max_value=100, 
            value=auto_gallery_uploader.JPEG_QUALITY
        )
        
        st.write("Настройки обработки имени файла:")
        filename_example = auto_gallery_uploader.sanitize_filename("Пример имени файла с пробелами 01.jpg")
        st.write(f"Пример: `Пример имени файла с пробелами 01.jpg` → `{filename_example}`")
        
        submit_button = st.form_submit_button("Сохранить настройки")
        
        if submit_button:
            # В реальном приложении здесь был бы код для сохранения настроек в конфигурацию
            st.success("Настройки сохранены успешно!")

def render_content():
    """Отображает основное содержимое страницы."""
    st.title("Управление изображениями галереи")
    
    # Проверка авторизации администратора
    if not check_admin_auth():
        admin_login_form("Для доступа к управлению изображениями галереи требуется аутентификация")
        st.stop()
    
    st.markdown("""
    Этот инструмент позволяет загружать и обрабатывать изображения для галереи проектов.
    Оптимизация изображений включает изменение размера, улучшение качества и автоматическое
    добавление в галерею с генерацией описаний.
    """)
    
    # Создаем вкладки для разных режимов
    tab1, tab2, tab3 = st.tabs([
        "📥 Загрузка изображений", 
        "📦 Пакетная обработка", 
        "⚙️ Настройки"
    ])
    
    with tab1:
        render_upload_section()
        
    with tab2:
        render_batch_processing()
        
    with tab3:
        render_settings()
    
    # Ссылки на другие страницы
    render_gallery_links()
    
    # Информация о времени последнего обновления
    st.markdown(f"""
    <div style="text-align: center; color: #888; margin-top: 30px; font-size: 0.8rem;">
        Последнее обновление: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_content()