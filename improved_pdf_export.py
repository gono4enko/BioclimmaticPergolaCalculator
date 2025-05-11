"""
Модуль для улучшенного экспорта PDF с поддержкой корректного именования файлов.
Этот модуль реализует функциональность экспорта PDF-файлов с правильным названием
при сохранении, используя встроенные компоненты Streamlit для скачивания.
"""

import os
import base64
from datetime import datetime
import pytz
import logging
import glob
import io
import uuid
import streamlit as st

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Константы для управления PDF-директорией
PDF_DIRECTORY = "generated_pdf"
MAX_PDF_FILES = 50  # Максимальное количество PDF-файлов в директории

def ensure_pdf_directory():
    """
    Создает директорию для PDF-файлов, если она не существует.
    Также проверяет количество файлов и удаляет старые файлы при превышении лимита.
    
    Returns:
        str: Путь к директории для PDF-файлов
    """
    # Создаем директорию, если она не существует
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), PDF_DIRECTORY)
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Проверяем количество файлов и удаляем старые при необходимости
    cleanup_old_files(pdf_dir)
    
    return pdf_dir

def cleanup_old_files(directory):
    """
    Удаляет старые PDF-файлы, если их количество превышает MAX_PDF_FILES.
    Файлы сортируются по времени изменения, и самые старые удаляются первыми.
    
    Args:
        directory (str): Путь к директории с PDF-файлами
    """
    try:
        # Получаем список всех PDF-файлов в директории
        pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
        
        # Если количество файлов меньше максимального, ничего не делаем
        if len(pdf_files) <= MAX_PDF_FILES:
            return
        
        # Сортируем файлы по времени изменения (от старых к новым)
        pdf_files.sort(key=os.path.getmtime)
        
        # Определяем количество файлов для удаления
        files_to_delete = len(pdf_files) - MAX_PDF_FILES
        
        # Удаляем самые старые файлы
        for i in range(files_to_delete):
            os.remove(pdf_files[i])
            logger.info(f"Удален устаревший PDF-файл: {os.path.basename(pdf_files[i])}")
    
    except Exception as e:
        logger.error(f"Ошибка при очистке старых PDF-файлов: {str(e)}")

def generate_pdf_file_name(pergola_data):
    """
    Генерирует информативное имя файла для PDF на основе данных о перголе.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе
        
    Returns:
        str: Информативное имя файла в формате "КП_Пергола_тип_ширинаxдлина_дата.pdf"
    """
    pergola_type = pergola_data.get("pergola_type", "unknown")
    width = pergola_data.get("width", 0)
    length = pergola_data.get("length", 0)
    
    # Определяем временную зону Ростова-на-Дону для корректной даты (та же, что и у Москвы)
    rostov_tz = pytz.timezone('Europe/Moscow')
    now_utc = datetime.now(pytz.utc)
    now_rostov = now_utc.astimezone(rostov_tz)
    current_date = now_rostov.strftime("%d.%m.%Y")
    
    # Формируем информативное имя файла
    file_name = f"КП_пергола_{pergola_type}_{width}x{length}м_{current_date}.pdf"
    
    return file_name

def save_pdf_for_debugging(pdf_data, file_name):
    """
    Сохраняет копию PDF-файла для отладки и архивирования.
    Использует улучшенное управление директорией с автоматической очисткой старых файлов.
    
    Args:
        pdf_data (bytes): Бинарные данные PDF-файла
        file_name (str): Имя файла
        
    Returns:
        str: Путь к сохраненному файлу
    """
    # Получаем директорию с проверкой и очисткой старых файлов
    pdf_dir = ensure_pdf_directory()
    
    # Полный путь к файлу
    debug_file_path = os.path.join(pdf_dir, file_name)
    
    # Записываем PDF в файл
    with open(debug_file_path, 'wb') as f:
        f.write(pdf_data)
    
    logger.info(f"PDF сохранен: {debug_file_path}")
    return debug_file_path

def get_streamlit_download_component(pdf_path):
    """
    Создает компонент Streamlit для скачивания PDF с правильным именем файла.
    Вместо использования сложного JavaScript и HTML, использует
    встроенный компонент Streamlit st.download_button.
    
    Args:
        pdf_path (str): Путь к PDF-файлу
        
    Returns:
        str: Пустая строка, чтобы не отображать None в интерфейсе
    """
    if not pdf_path or not os.path.exists(pdf_path):
        st.error("PDF файл не найден")
        return ""
    
    # Получаем имя файла 
    file_name = os.path.basename(pdf_path)
    
    # Читаем файл в бинарном режиме
    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()
    
    # Размер файла в килобайтах для отображения
    file_size_kb = int(len(pdf_bytes) / 1024)
    
    # Создаем контейнер с информацией
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <h3>Коммерческое предложение готово!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Создаем гарантированно уникальные ключи с использованием UUID
    unique_id = str(uuid.uuid4())[:8]  # Используем первые 8 символов UUID для краткости
    download_key = f"download_pdf_{unique_id}"
    
    # Кнопка скачивания по центру
    st.download_button(
        label="Скачать PDF",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf",
        key=download_key,
        help="Скачать PDF-файл на компьютер",
        use_container_width=True,  # Растягиваем кнопку на всю ширину контейнера
    )
    
    # Отображаем информацию о файле
    st.markdown(f"""
    <div style="font-size: 12px; color: #6c757d; margin-top: 5px; text-align: center;">
        Файл <strong>{file_name}</strong> ({file_size_kb} KB)
    </div>
    """, unsafe_allow_html=True)
    
    # Скрипт для отправки события в Яндекс.Метрику
    # Примечание: в Streamlit не поддерживается JavaScript для обработки нажатий на кнопки,
    # поэтому отправляем только событие о создании PDF без отслеживания скачивания/просмотра
    st.markdown("""
    <script>
        // Отправляем событие в Яндекс.Метрику при загрузке страницы
        if (typeof ym !== 'undefined') {
            ym(94463245, 'reachGoal', 'pdf_generated');
            console.log('Отправлено событие pdf_generated в Яндекс.Метрику');
        }
    </script>
    """, unsafe_allow_html=True)
    
    # Возвращаем пустую строку вместо None
    return ""