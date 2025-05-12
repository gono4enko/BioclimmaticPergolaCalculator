"""
Скрипт для извлечения CSS стилей из оригинального приложения Streamlit
и их сохранения для использования в новом Flask-приложении.
"""
import re
import os
import requests
from bs4 import BeautifulSoup
from web_scraper import get_website_html

def extract_styles_from_url(url):
    """
    Извлекает CSS стили из указанного URL.
    
    Args:
        url (str): URL страницы для извлечения стилей
        
    Returns:
        tuple: (внешние CSS файлы, встроенные стили)
    """
    print(f"Получаем HTML с {url}")
    html = get_website_html(url)
    if not html:
        print(f"Не удалось получить HTML с {url}")
        return [], []
    
    print(f"Успешно получен HTML ({len(html)} байт)")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Извлекаем внешние CSS файлы
    external_css = []
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href and not href.startswith('data:'):
            if href.startswith('http'):
                external_css.append(href)
            else:
                # Обрабатываем относительные пути
                if href.startswith('/'):
                    external_css.append(f"{url.split('//', 1)[0]}//{url.split('//', 1)[1].split('/', 1)[0]}{href}")
                else:
                    base_url = '/'.join(url.split('/')[:-1])
                    external_css.append(f"{base_url}/{href}")
    
    # Извлекаем встроенные стили
    inline_css = []
    for style in soup.find_all('style'):
        inline_css.append(style.string)
    
    return external_css, inline_css

def download_css_file(url, output_dir):
    """
    Загружает CSS файл и сохраняет его локально.
    
    Args:
        url (str): URL CSS файла
        output_dir (str): Директория для сохранения
        
    Returns:
        str: Путь к сохраненному файлу или None в случае ошибки
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Создаем имя файла из URL
        filename = url.split('/')[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
        
        if not filename.endswith('.css'):
            filename += '.css'
        
        # Сохраняем файл
        output_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Сохранен CSS файл: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Ошибка при загрузке CSS ({url}): {str(e)}")
        return None

def save_inline_css(css_content, output_dir, index=0):
    """
    Сохраняет встроенный CSS в файл.
    
    Args:
        css_content (str): Содержимое CSS
        output_dir (str): Директория для сохранения
        index (int): Индекс для имени файла
        
    Returns:
        str: Путь к сохраненному файлу
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"inline_style_{index}.css")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"Сохранен встроенный CSS: {output_path}")
    return output_path

def extract_streamlit_theme_params(html_content):
    """
    Извлекает параметры темы Streamlit из HTML.
    
    Args:
        html_content (str): HTML-код страницы
        
    Returns:
        dict: Параметры темы или пустой словарь
    """
    # Ищем скрипт с настройками Streamlit
    match = re.search(r'Streamlit\.setComponentReady\([^)]*\)\s*;\s*var\s+theme\s*=\s*({.*?});\s*', html_content, re.DOTALL)
    if match:
        theme_json = match.group(1)
        # Преобразуем JS объект в словарь Python
        try:
            # Заменяем одинарные кавычки на двойные для JSON
            theme_json = theme_json.replace("'", '"')
            # Заменяем неэкранированные ключи на экранированные
            theme_json = re.sub(r'(\s*)(\w+)(\s*):([^,}]*)', r'\1"\2"\3:\4', theme_json)
            import json
            theme = json.loads(theme_json)
            return theme
        except Exception as e:
            print(f"Ошибка при парсинге темы: {str(e)}")
    
    return {}

def main():
    """Основная функция скрипта."""
    url = "https://bioclimmatic-pergola-calculator-gono4enko.replit.app"
    output_dir = "flask_app/static/css/original"
    
    external_css, inline_css = extract_styles_from_url(url)
    
    print(f"Найдено внешних CSS: {len(external_css)}")
    print(f"Найдено встроенных CSS: {len(inline_css)}")
    
    # Загружаем внешние CSS файлы
    for url in external_css:
        download_css_file(url, output_dir)
    
    # Сохраняем встроенные CSS
    for i, css in enumerate(inline_css):
        save_inline_css(css, output_dir, i)
    
    # Получаем HTML для извлечения темы Streamlit
    html = get_website_html(url)
    if html:
        theme = extract_streamlit_theme_params(html)
        if theme:
            print(f"Извлечены параметры темы Streamlit: {theme}")
            
            # Создаем CSS на основе темы Streamlit
            theme_css = """
            :root {
            """
            
            if 'primaryColor' in theme:
                theme_css += f"  --primary-color: {theme['primaryColor']};\n"
            if 'backgroundColor' in theme:
                theme_css += f"  --background-color: {theme['backgroundColor']};\n"
            if 'secondaryBackgroundColor' in theme:
                theme_css += f"  --secondary-background-color: {theme['secondaryBackgroundColor']};\n"
            if 'textColor' in theme:
                theme_css += f"  --text-color: {theme['textColor']};\n"
            if 'font' in theme:
                theme_css += f"  --font-family: {theme['font']};\n"
            
            theme_css += """
            }
            """
            
            save_inline_css(theme_css, output_dir, 99)  # Используем число вместо строки
    
    print("Завершено извлечение стилей.")

if __name__ == "__main__":
    main()