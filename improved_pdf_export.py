"""
Модуль для улучшенного экспорта PDF с поддержкой корректного именования файлов.
Этот модуль реализует функциональность экспорта PDF-файлов с правильным названием
при сохранении, используя современные приемы работы с HTTP-заголовками и JavaScript.
"""

import os
import base64
from datetime import datetime
import pytz
from urllib.parse import quote
import json
import logging
import shutil
import glob

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
    
    # Определяем московскую временную зону для корректной даты
    moscow_tz = pytz.timezone('Europe/Moscow')
    now_utc = datetime.now(pytz.utc)
    now_moscow = now_utc.astimezone(moscow_tz)
    current_date = now_moscow.strftime("%d.%m.%Y")
    
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

def get_improved_pdf_download_link(pdf_path):
    """
    Создает улучшенную ссылку для скачивания PDF с правильным именем файла.
    Использует современные техники для обеспечения корректного именования файлов
    при скачивании с поддержкой кириллицы.
    
    Args:
        pdf_path (str): Путь к PDF-файлу
        
    Returns:
        str: HTML-код с кнопкой и JavaScript для скачивания PDF
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return ""
    
    # Получаем имя файла для отображения и установки в заголовках
    file_name = os.path.basename(pdf_path)
    
    # Формируем уникальный идентификатор для этого файла
    file_id = file_name.replace('.', '_').replace(' ', '_')
    
    # Читаем файл в бинарном режиме
    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()
    
    # Кодируем в base64
    b64 = base64.b64encode(pdf_bytes).decode()
    
    # Размер файла в килобайтах для отображения
    file_size_kb = os.path.getsize(pdf_path) // 1024

    # URL-кодируем имя файла для использования в HTTP-заголовках
    file_name_url_encoded = quote(file_name)

    # Создаем улучшенный JavaScript для скачивания с поддержкой правильного имени файла
    download_script = f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const pdfDownloadBtn = document.getElementById('pdf-download-{file_id}');
        const pdfViewBtn = document.getElementById('pdf-view-{file_id}');
        
        if (pdfDownloadBtn) {{
            pdfDownloadBtn.addEventListener('click', function(e) {{
                e.preventDefault();
                
                try {{
                    // Создаем объект Blob из данных PDF
                    const pdfData = atob('{b64}');
                    const byteCharacters = pdfData;
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {{type: 'application/pdf'}});
                    
                    // Декодированное имя файла с кириллицей
                    const fileName = decodeURIComponent('{file_name_url_encoded}');
                    console.log('Скачивание файла с именем: ' + fileName);
                    
                    // Создаем ссылку для скачивания
                    const downloadLink = document.createElement('a');
                    downloadLink.href = URL.createObjectURL(blob);
                    downloadLink.download = fileName;
                    
                    // Добавляем элемент на страницу и запускаем скачивание
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    
                    // Удаляем элемент и освобождаем ресурсы
                    setTimeout(() => {{
                        document.body.removeChild(downloadLink);
                        URL.revokeObjectURL(downloadLink.href);
                    }}, 100);
                    
                    // Показываем уведомление об успешном скачивании
                    const alertContainer = document.createElement('div');
                    
                    // Добавляем стили для анимации как текст
                    const styleText = '@keyframes fadeInOut { ' +
                                    '0% { opacity: 0; transform: translateY(10px); } ' +
                                    '10% { opacity: 1; transform: translateY(0); } ' +
                                    '80% { opacity: 1; } ' +
                                    '100% { opacity: 0; } ' +
                                    '}';
                    const styleElem = document.createElement('style');
                    styleElem.textContent = styleText;
                    document.head.appendChild(styleElem);
                    
                    // Создаем контейнер уведомления
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'pdf-alert';
                    alertDiv.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background-color: #f0f8ff; border: 1px solid #007bff; border-radius: 5px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 9999; animation: fadeInOut 5s;';
                    
                    // Создаем верхнюю часть с иконкой
                    const headerDiv = document.createElement('div');
                    headerDiv.style.cssText = 'display: flex; align-items: center; margin-bottom: 8px;';
                    
                    // Создаем SVG иконку
                    const svgIcon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    svgIcon.setAttribute('style', 'width: 20px; height: 20px; fill: #007bff; margin-right: 10px;');
                    svgIcon.setAttribute('viewBox', '0 0 16 16');
                    
                    const iconPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    iconPath.setAttribute('d', 'M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm3.707-9.293a1 1 0 0 0-1.414-1.414L7 8.586 5.707 7.293a1 1 0 0 0-1.414 1.414l2 2a1 1 0 0 0 1.414 0l4-4z');
                    svgIcon.appendChild(iconPath);
                    
                    // Добавляем заголовок
                    const titleDiv = document.createElement('div');
                    titleDiv.style.fontWeight = 'bold';
                    titleDiv.textContent = 'PDF файл скачивается';
                    
                    // Собираем верхнюю часть
                    headerDiv.appendChild(svgIcon);
                    headerDiv.appendChild(titleDiv);
                    
                    // Создаем нижнюю часть с именем файла
                    const fileInfoDiv = document.createElement('div');
                    fileInfoDiv.style.cssText = 'font-size: 0.9rem; margin-left: 30px;';
                    fileInfoDiv.textContent = 'Имя файла: ';
                    
                    const fileNameSpan = document.createElement('span');
                    fileNameSpan.style.fontFamily = 'monospace';
                    fileNameSpan.textContent = fileName;
                    fileInfoDiv.appendChild(fileNameSpan);
                    
                    // Собираем все вместе
                    alertDiv.appendChild(headerDiv);
                    alertDiv.appendChild(fileInfoDiv);
                    alertContainer.appendChild(alertDiv);
                    
                    // Добавляем на страницу
                    document.body.appendChild(alertContainer);
                    
                    // Удаляем уведомление через 5 секунд
                    setTimeout(() => {{
                        document.body.removeChild(alertContainer);
                    }}, 5000);
                    
                    // Отправляем событие в Яндекс.Метрику
                    if (typeof ym !== 'undefined') {{
                        ym(94463245, 'reachGoal', 'pdf_download');
                        console.log('Отправлено событие pdf_download в Яндекс.Метрику');
                    }}
                }} catch(error) {{
                    console.error('Ошибка при скачивании PDF:', error);
                    alert('Произошла ошибка при скачивании PDF. Пожалуйста, попробуйте ещё раз.');
                }}
            }});
        }}
        
        if (pdfViewBtn) {{
            pdfViewBtn.addEventListener('click', function(e) {{
                e.preventDefault();
                
                try {{
                    // Создаем ссылку для просмотра в новой вкладке
                    const dataUrl = 'data:application/pdf;base64,{b64}';
                    const newWindow = window.open();
                    
                    if (newWindow) {{
                        newWindow.document.write(`
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>{file_name}</title>
                                <style>
                                    body, html {{ margin: 0; padding: 0; height: 100%; overflow: hidden; }}
                                    #pdf-viewer {{ width: 100%; height: 100%; }}
                                </style>
                            </head>
                            <body>
                                <embed id="pdf-viewer" src="${{dataUrl}}" type="application/pdf" />
                            </body>
                            </html>
                        `);
                    }} else {{
                        // Если блокировщик всплывающих окон предотвратил открытие
                        window.location.href = dataUrl;
                    }}
                    
                    // Отправляем событие в Яндекс.Метрику
                    if (typeof ym !== 'undefined') {{
                        ym(94463245, 'reachGoal', 'pdf_view');
                        console.log('Отправлено событие pdf_view в Яндекс.Метрику');
                    }}
                }} catch(error) {{
                    console.error('Ошибка при просмотре PDF:', error);
                    alert('Произошла ошибка при открытии PDF. Пожалуйста, попробуйте ещё раз.');
                }}
            }});
        }}
    }});
    </script>
    """
    
    # Создаем HTML-код с двумя кнопками: скачать и просмотреть
    html = f"""
    <div class="pdf-actions-container" style="text-align: center; margin: 20px 0; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
        <div style="margin-bottom: 10px; font-weight: bold;">
            Коммерческое предложение готово!
        </div>
        
        <div style="display: flex; justify-content: center; gap: 15px; margin: 15px 0; flex-wrap: wrap;">
            <button id="pdf-download-{file_id}" style="display: inline-flex; align-items: center; 
                   padding: 10px 15px; background-color: #007bff; color: white; 
                   border: none; border-radius: 4px; cursor: pointer; font-size: 14px;
                   min-width: 150px; min-height: 40px;">
                <svg style="width: 16px; height: 16px; margin-right: 8px; fill: currentColor;" 
                     viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 12l-4-4h2.5V3h3v5H12l-4 4z"/>
                    <path d="M2 14h12v1H2z"/>
                </svg>
                Скачать PDF
            </button>
            
            <button id="pdf-view-{file_id}" style="display: inline-flex; align-items: center; 
                   padding: 10px 15px; background-color: #6c757d; color: white; 
                   border: none; border-radius: 4px; cursor: pointer; font-size: 14px;
                   min-width: 150px; min-height: 40px;">
                <svg style="width: 16px; height: 16px; margin-right: 8px; fill: currentColor;" 
                     viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 3C4.5 3 1.5 6 1.5 8s3 5 6.5 5 6.5-3 6.5-5-3-5-6.5-5zm0 8c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3-1.3 3-3 3z"/>
                    <circle cx="8" cy="8" r="1.5"/>
                </svg>
                Просмотреть
            </button>
        </div>
        
        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">
            Файл <strong>{file_name}</strong> ({file_size_kb} KB)
        </div>
    </div>
    {download_script}
    """
    
    return html

# Функция для интеграции с Streamlit
def get_streamlit_download_component(pdf_path):
    """
    Создает компонент для отображения в Streamlit для скачивания PDF.
    
    Args:
        pdf_path (str): Путь к PDF-файлу
        
    Returns:
        str: HTML-код с компонентом для скачивания PDF
    """
    return get_improved_pdf_download_link(pdf_path)