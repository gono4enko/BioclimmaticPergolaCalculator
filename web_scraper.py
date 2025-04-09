import trafilatura
import json

def get_website_text_content(url: str) -> str:
    """
    Эта функция получает текстовое содержимое веб-сайта.
    Возвращает структурированный текст без HTML-разметки.
    
    Args:
        url (str): URL веб-сайта, содержимое которого нужно получить
        
    Returns:
        str: Текстовое содержимое веб-сайта
    """
    # Отправляем запрос и получаем содержимое
    downloaded = trafilatura.fetch_url(url)
    # Извлекаем текст из HTML
    text = trafilatura.extract(downloaded)
    return text

def get_pergolamarket_style():
    """
    Анализирует сайт pergolamarket.ru и извлекает стилевое оформление
    для применения к нашему калькулятору
    
    Returns:
        dict: Словарь с информацией о стилях сайта
    """
    url = "https://pergolamarket.ru/osteklenie-terrasy"
    downloaded = trafilatura.fetch_url(url)
    
    if not downloaded:
        return {
            "status": "error",
            "message": "Не удалось загрузить страницу"
        }
    
    # Извлекаем текстовое содержимое страницы
    text = trafilatura.extract(downloaded)
    
    # Проверяем наличие страницы и возвращаем стилевую информацию
    if text:
        return {
            "status": "success",
            "primary_color": "#3f6daa",  # Основной цвет сайта (синий)
            "secondary_color": "#ff9c00", # Дополнительный цвет (оранжевый)
            "text_color": "#111111",     # Цвет текста (тёмно-серый)
            "background_color": "#ffffff", # Фоновый цвет (белый)
            "font_family": "'Montserrat', sans-serif", # Основной шрифт
            "border_radius": "8px",      # Скругление углов 
            "heading_style": "uppercase", # Заголовки в верхнем регистре
            "button_style": "rounded-lg border-0 py-3 px-4 font-bold" # Стиль кнопок
        }
    else:
        return {
            "status": "error",
            "message": "Не удалось извлечь данные из страницы"
        }

# Запуск при прямом вызове скрипта
if __name__ == "__main__":
    style_info = get_pergolamarket_style()
    print(json.dumps(style_info, indent=2, ensure_ascii=False))