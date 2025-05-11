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

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    
    Args:
        pdf_data (bytes): Бинарные данные PDF-файла
        file_name (str): Имя файла
        
    Returns:
        str: Путь к сохраненному файлу
    """
    # Создаем директорию, если она не существует
    debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_pdf')
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    # Полный путь к файлу
    debug_file_path = os.path.join(debug_dir, file_name)
    
    # Записываем PDF в файл
    with open(debug_file_path, 'wb') as f:
        f.write(pdf_data)
    
    logger.info(f"PDF сохранен для отладки: {debug_file_path}")
    return debug_file_path

def get_improved_pdf_download_link(pdf_path):
    """
    Создает улучшенную ссылку для скачивания PDF с правильным именем файла.
    
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

    # Создаем улучшенный JavaScript для скачивания с поддержкой правильного имени файла
    download_script = f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const pdfDownloadBtn = document.getElementById('pdf-download-{file_id}');
        const pdfViewBtn = document.getElementById('pdf-view-{file_id}');
        
        if (pdfDownloadBtn) {{
            pdfDownloadBtn.addEventListener('click', function(e) {{
                e.preventDefault();
                
                // Создаем объект Blob из данных PDF
                const pdfData = atob('{b64}');
                const byteCharacters = pdfData;
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{type: 'application/pdf'}});
                
                // Создаем ссылку для скачивания
                const downloadLink = document.createElement('a');
                downloadLink.href = URL.createObjectURL(blob);
                downloadLink.download = '{file_name}';
                
                // Добавляем элемент на страницу и запускаем скачивание
                document.body.appendChild(downloadLink);
                downloadLink.click();
                
                // Удаляем элемент и освобождаем ресурсы
                setTimeout(() => {{
                    document.body.removeChild(downloadLink);
                    URL.revokeObjectURL(downloadLink.href);
                }}, 100);
                
                // Отправляем событие в Яндекс.Метрику
                if (typeof ym !== 'undefined') {{
                    ym(94463245, 'reachGoal', 'pdf_download');
                    console.log('Отправлено событие pdf_download в Яндекс.Метрику');
                }}
            }});
        }}
        
        if (pdfViewBtn) {{
            pdfViewBtn.addEventListener('click', function(e) {{
                e.preventDefault();
                
                // Создаем ссылку для просмотра в новой вкладке
                const dataUrl = 'data:application/pdf;base64,{b64}';
                window.open(dataUrl, '_blank');
                
                // Отправляем событие в Яндекс.Метрику
                if (typeof ym !== 'undefined') {{
                    ym(94463245, 'reachGoal', 'pdf_view');
                    console.log('Отправлено событие pdf_view в Яндекс.Метрику');
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
        
        <div style="display: flex; justify-content: center; gap: 15px; margin: 15px 0;">
            <button id="pdf-download-{file_id}" style="display: inline-flex; align-items: center; 
                   padding: 10px 15px; background-color: #007bff; color: white; 
                   border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                <svg style="width: 16px; height: 16px; margin-right: 8px; fill: currentColor;" 
                     viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 12l-4-4h2.5V3h3v5H12l-4 4z"/>
                    <path d="M2 14h12v1H2z"/>
                </svg>
                Скачать PDF
            </button>
            
            <button id="pdf-view-{file_id}" style="display: inline-flex; align-items: center; 
                   padding: 10px 15px; background-color: #6c757d; color: white; 
                   border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
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