"""
Скрипт для восстановления PDF-генерации из опубликованной версии приложения.
Этот скрипт скачивает код из опубликованного приложения и сохраняет копии важных файлов.
"""

import os
import sys
import json
import requests
import re
import shutil
from pathlib import Path
from datetime import datetime
from web_scraper import get_website_html

# Константы
PUBLISHED_URL = "https://bioclimmatic-pergola-calculator-gono4enko.replit.app"
BACKUP_DIR = "restore_from_published"

def create_backup_directory():
    """Создает директорию для резервной копии"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}_{timestamp}"
    os.makedirs(backup_path, exist_ok=True)
    return backup_path

def download_published_html():
    """Скачивает HTML из опубликованной версии"""
    print(f"Загрузка HTML из {PUBLISHED_URL}...")
    try:
        html_content = get_website_html(PUBLISHED_URL)
        if not html_content:
            print("Ошибка: Не удалось загрузить HTML-контент")
            return None
        return html_content
    except Exception as e:
        print(f"Ошибка при загрузке HTML: {str(e)}")
        return None

def extract_js_files(html_content):
    """Извлекает пути к JavaScript-файлам из HTML"""
    js_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
    js_files = re.findall(js_pattern, html_content)
    return js_files

def extract_css_files(html_content):
    """Извлекает пути к CSS-файлам из HTML"""
    css_pattern = r'<link[^>]+href=["\']([^"\']+\.css)["\']'
    css_files = re.findall(css_pattern, html_content)
    return css_files

def download_resource(url, save_path):
    """Скачивает ресурс по URL и сохраняет по указанному пути"""
    try:
        # Обрабатываем относительные URL
        if url.startswith('/'):
            full_url = f"{PUBLISHED_URL}{url}"
        elif url.startswith('http'):
            full_url = url
        else:
            full_url = f"{PUBLISHED_URL}/{url}"
            
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()
        
        # Создаем директории, если не существуют
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Сохраняем файл
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Ошибка при скачивании {url}: {str(e)}")
        return False

def extract_streamlit_components(html_content):
    """Извлекает компоненты Streamlit из HTML"""
    # Ищем ключевые данные, которые инициализируют Streamlit
    init_pattern = r'Streamlit\.setComponentReady\(\s*({[^}]+})\s*\)'
    init_matches = re.findall(init_pattern, html_content)
    
    components_info = []
    for match in init_matches:
        try:
            # Преобразуем в валидный JSON (может потребоваться дополнительная обработка)
            cleaned_match = match.replace("'", '"')
            component_data = json.loads(cleaned_match)
            components_info.append(component_data)
        except json.JSONDecodeError:
            print(f"Не удалось распарсить данные компонента: {match}")
    
    return components_info

def extract_pdf_generation_code(html_content):
    """
    Ищет в HTML-коде ссылки на скрипты и функции, связанные с генерацией PDF
    """
    # Ищем ссылки на функции генерации PDF
    pdf_patterns = [
        r'function\s+generate\w*PDF\s*\([^)]*\)\s*{([^}]+)}',
        r'def\s+generate\w*pdf\s*\([^)]*\):([^#]+)',
        r'def\s+export_to_pdf\s*\([^)]*\):([^#]+)'
    ]
    
    pdf_code_snippets = []
    for pattern in pdf_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        pdf_code_snippets.extend(matches)
    
    return pdf_code_snippets

def create_simple_restoration_script(backup_path):
    """Создает простой скрипт для восстановления кода PDF из опубликованной версии"""
    script_content = """
import os
import shutil
import requests
import json
from datetime import datetime

# URL опубликованного приложения для восстановления PDF-генерации
PUBLISHED_URL = "https://bioclimmatic-pergola-calculator-gono4enko.replit.app"

def restore_pdf_generator():
    """Восстанавливает генератор PDF из опубликованной версии"""
    # Создаем директорию для логов, если она не существует
    os.makedirs("logs", exist_ok=True)
    
    # Создаем директорию для PDF, если она не существует
    os.makedirs("generated_pdf", exist_ok=True)

    # Проверяем, есть ли упрощенный PDF-генератор и создаем его, если нет
    if not os.path.exists("simple_pdf.py"):
        print("Создаем упрощенный генератор PDF...")
        create_simple_pdf_generator()
    
    # Обновляем функцию export_to_pdf в app.py для использования упрощенного генератора
    update_export_function()
    
    print("Восстановление PDF-генератора завершено!")
    return True

def create_simple_pdf_generator():
    """Создает простой генератор PDF на основе FPDF"""
    code = '''
"""
Простой генератор PDF для перголы с минимальными зависимостями.
Создает простой PDF-документ с информацией о перголе и ее стоимости.
Используется как резервный вариант, если основной генератор PDF не работает.
"""

import os
import datetime
from fpdf import FPDF
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_pdf")

def generate_simple_pdf(pergola_data):
    """
    Создает простой PDF-документ с информацией о перголе.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе
    
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    try:
        # Создаем директорию для PDF, если она не существует
        os.makedirs("generated_pdf", exist_ok=True)
        
        # Получаем данные из pergola_data
        pergola_type = pergola_data.get("pergola_type", "B500NEW")
        width = pergola_data.get("width", 3.0)
        length = pergola_data.get("length", 4.0)
        modules = pergola_data.get("modules", 1)
        items = pergola_data.get("items", [])
        total_price = pergola_data.get("total_price", 0)
        discount = pergola_data.get("discount", 0)
        total_after_discount = pergola_data.get("total_price_after_discount", 0)
        
        # Генерируем имя файла
        today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"КП_пергола_{pergola_type}_{width}x{length}м_{today}.pdf"
        pdf_path = os.path.join("generated_pdf", filename)
        
        # Создаем PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Добавляем заголовок
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Коммерческое предложение", ln=True, align="C")
        pdf.ln(5)
        
        # Добавляем информацию о перголе
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Тип перголы: {pergola_type}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 8, f"Размеры: {width} x {length} м", ln=True)
        pdf.cell(190, 8, f"Модули: {modules}", ln=True)
        pdf.ln(5)
        
        # Добавляем таблицу с опциями
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Выбранные опции:", ln=True)
        pdf.ln(2)
        
        # Заголовки таблицы
        pdf.set_font("Arial", "B", 10)
        pdf.cell(110, 7, "Наименование", 1)
        pdf.cell(40, 7, "Количество", 1)
        pdf.cell(40, 7, "Цена (руб.)", 1)
        pdf.ln()
        
        # Строки таблицы
        pdf.set_font("Arial", "", 10)
        for item in items:
            name = item.get("name", "")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            
            # Добавляем строку в таблицу
            pdf.cell(110, 7, name, 1)
            pdf.cell(40, 7, str(quantity), 1)
            pdf.cell(40, 7, f"{price:,.0f}", 1)
            pdf.ln()
        
        # Добавляем информацию о стоимости
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 8, "Общая стоимость:", 0)
        pdf.cell(40, 8, f"{total_price:,.0f} руб.", 0, ln=True)
        
        if discount > 0:
            pdf.set_font("Arial", "", 12)
            pdf.cell(150, 8, f"Скидка ({discount}%):", 0)
            discount_amount = total_price - total_after_discount
            pdf.cell(40, 8, f"-{discount_amount:,.0f} руб.", 0, ln=True)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(150, 8, "Итоговая стоимость:", 0)
            pdf.cell(40, 8, f"{total_after_discount:,.0f} руб.", 0, ln=True)
        
        # Добавляем дату и дисклеймер
        pdf.ln(15)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(190, 6, f"Предложение сформировано: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
        pdf.cell(190, 6, "Предложение действительно в течение 30 дней.", ln=True)
        
        # Сохраняем PDF-файл
        pdf.output(pdf_path)
        logger.info(f"PDF успешно создан по пути: {pdf_path}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {str(e)}", exc_info=True)
        return None
'''
    
    with open("simple_pdf.py", "w", encoding="utf-8") as f:
        f.write(code.strip())
    
    return True

def update_export_function():
    """Обновляет функцию export_to_pdf в app.py для использования упрощенного генератора PDF"""
    try:
        # Находим функцию export_to_pdf в app.py
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Шаблон для поиска функции export_to_pdf
        export_pattern = r'def export_to_pdf\(\):[^#]*?(?=def |$)'
        match = re.search(export_pattern, content, re.DOTALL)
        
        if not match:
            print("Не удалось найти функцию export_to_pdf в файле app.py")
            return False
        
        # Новый код функции
        new_function = '''
def export_to_pdf():
    """
    Формирует данные для экспорта и генерирует PDF-файл с улучшенным скачиванием.
    Использует простую версию PDF-генератора для максимальной надежности.
    
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    import os
    import sys
    import logging
    import time
    
    # Настраиваем логирование для отладки PDF-генерации
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join("logs", "pdf_generation.log"),
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("export_to_pdf")
    
    # Проверяем, были ли выполнены расчеты
    if 'results' not in st.session_state:
        st.error("Сначала нужно выполнить расчет!")
        return None
    
    results = st.session_state.results
    options = results.get("options", {})
    dimensions = results.get("dimensions", {})
    pergola_type = options.get("pergola_type", "")
    
    # Создаем необходимые директории
    os.makedirs("generated_pdf", exist_ok=True)
    
    # Получаем параметры из результатов расчета
    default_width = st.session_state.get('cached_width') or 3.0
    default_length = st.session_state.get('cached_length') or 4.0
    
    # Логируем данные для отладки
    logger.info(f"Экспорт PDF для перголы: {pergola_type}")
    logger.info(f"Размеры из результатов: {dimensions}")
    
    # Формируем данные для PDF
    pdf_data = {
        "pergola_type": pergola_type,
        "width": dimensions.get("width", default_width),
        "length": dimensions.get("length", default_length),
        "modules": dimensions.get("modules", 1),
        "items": results.get("items", []),
        "total_price": results.get("total_price", 0),
        "discount": results.get("discount", 0),
        "total_price_after_discount": results.get("total_price_after_discount", 0)
    }
    
    try:
        # Показываем индикатор загрузки
        with st.spinner("Создание PDF-документа..."):
            # Пробуем использовать простой генератор PDF
            try:
                logger.info("Используем simple_pdf для создания PDF")
                from simple_pdf import generate_simple_pdf
                pdf_file_path = generate_simple_pdf(pdf_data)
                
                if pdf_file_path and os.path.exists(pdf_file_path):
                    # Выводим читаемую для пользователя информацию о созданном PDF
                    logger.info(f"PDF файл успешно создан: {pdf_file_path}")
                    return pdf_file_path
                else:
                    # Пробуем запасной вариант
                    logger.warning("Не удалось создать PDF через simple_pdf, пробуем основной генератор")
                    
                    # Пробуем использовать основной PDF-генератор
                    from pdf_generator_fpdf_rus import generate_commercial_offer, format_pergola_data_for_pdf
                    
                    # Генерируем PDF с полными данными
                    pergola_data = format_pergola_data_for_pdf(results, options, dimensions, "")
                    pdf_file_path = generate_commercial_offer(pergola_data)
                    
                    if pdf_file_path and os.path.exists(pdf_file_path):
                        logger.info(f"PDF успешно создан через основной генератор: {pdf_file_path}")
                        return pdf_file_path
                    else:
                        st.error("Не удалось создать PDF документ")
                        return None
                
            except ImportError as ie:
                logger.error(f"Ошибка импорта модуля для PDF: {str(ie)}")
                st.error(f"Ошибка при создании PDF: модуль не найден")
                return None
                
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при генерации PDF: {str(e)}", exc_info=True)
        st.error(f"Не удалось сгенерировать PDF. Пожалуйста, попробуйте еще раз.")
        return None
'''
        
        # Заменяем функцию в файле
        new_content = content.replace(match.group(0), new_function)
        
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("Функция export_to_pdf успешно обновлена в app.py")
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении функции export_to_pdf: {str(e)}")
        return False

if __name__ == "__main__":
    # Запускаем восстановление
    restore_pdf_generator()
    """
    
    script_path = os.path.join(backup_path, "restore_pdf_generator.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"Скрипт восстановления создан: {script_path}")
    return script_path
    
def download_streamlit_backend_file():
    """Пытается загрузить исходный код Python из опубликованной версии"""
    # Это сложно сделать напрямую, но мы можем попробовать использовать GitHub API,
    # если репозиторий публичный, или создать запрос к бэкэнду Replit
    backend_urls = [
        f"{PUBLISHED_URL}/__replit_streamlit_backend__/app.py",
        f"{PUBLISHED_URL}/__backend__/app.py",
        f"{PUBLISHED_URL}/api/streamlit/app.py"
    ]
    
    for url in backend_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and "def export_to_pdf" in response.text:
                print(f"Найден исходный код в: {url}")
                return response.text
        except Exception:
            continue
    
    print("Не удалось найти исходный код Python напрямую")
    return None

def main():
    """Основная функция скрипта"""
    print("Начинаем восстановление из опубликованной версии...")
    
    # Создаем директорию для бэкапа
    backup_path = create_backup_directory()
    print(f"Создана директория для бэкапа: {backup_path}")
    
    # Скачиваем HTML из опубликованной версии
    html_content = download_published_html()
    if not html_content:
        print("Критическая ошибка: не удалось загрузить HTML. Восстановление невозможно.")
        return False
    
    # Сохраняем HTML для анализа
    html_path = os.path.join(backup_path, "published_version.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML сохранен в {html_path}")
    
    # Извлекаем информацию о JavaScript и CSS файлах
    js_files = extract_js_files(html_content)
    css_files = extract_css_files(html_content)
    
    print(f"Найдено JavaScript файлов: {len(js_files)}")
    print(f"Найдено CSS файлов: {len(css_files)}")
    
    # Скачиваем ресурсы
    resources_dir = os.path.join(backup_path, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    for js_file in js_files:
        js_filename = os.path.basename(js_file)
        save_path = os.path.join(resources_dir, js_filename)
        if download_resource(js_file, save_path):
            print(f"Скачан JavaScript файл: {js_filename}")
    
    for css_file in css_files:
        css_filename = os.path.basename(css_file)
        save_path = os.path.join(resources_dir, css_filename)
        if download_resource(css_file, save_path):
            print(f"Скачан CSS файл: {css_filename}")
    
    # Извлекаем компоненты Streamlit
    components_info = extract_streamlit_components(html_content)
    
    components_path = os.path.join(backup_path, "streamlit_components.json")
    with open(components_path, "w", encoding="utf-8") as f:
        json.dump(components_info, f, indent=2)
    print(f"Информация о компонентах Streamlit сохранена в {components_path}")
    
    # Ищем код для генерации PDF
    pdf_code_snippets = extract_pdf_generation_code(html_content)
    
    if pdf_code_snippets:
        pdf_code_path = os.path.join(backup_path, "pdf_generation_code.txt")
        with open(pdf_code_path, "w", encoding="utf-8") as f:
            for i, snippet in enumerate(pdf_code_snippets, 1):
                f.write(f"--- Фрагмент {i} ---\n\n")
                f.write(snippet.strip())
                f.write("\n\n")
        print(f"Найдены фрагменты кода для генерации PDF: {len(pdf_code_snippets)}")
        print(f"Сохранены в {pdf_code_path}")
    else:
        print("Фрагменты кода для генерации PDF не найдены")
    
    # Пробуем загрузить исходный код Python
    backend_code = download_streamlit_backend_file()
    if backend_code:
        backend_path = os.path.join(backup_path, "backend_app.py")
        with open(backend_path, "w", encoding="utf-8") as f:
            f.write(backend_code)
        print(f"Исходный код Python сохранен в {backend_path}")
    
    # Создаем скрипт для восстановления PDF
    script_path = create_simple_restoration_script(backup_path)
    
    print("\nВосстановление завершено!")
    print(f"Все данные сохранены в {backup_path}")
    print(f"Для восстановления PDF-генерации запустите скрипт: {script_path}")
    
    # Создаем скрипт для быстрого восстановления в корневой директории
    shutil.copy(script_path, "./restore_pdf_generator.py")
    print("Создан скрипт для быстрого восстановления: ./restore_pdf_generator.py")
    print("Выполните 'python restore_pdf_generator.py' для восстановления PDF-генерации")
    
    return True

if __name__ == "__main__":
    main()