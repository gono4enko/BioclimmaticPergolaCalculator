"""
Модуль для извлечения текстового содержимого веб-страниц
с использованием библиотеки trafilatura для более качественного
извлечения текста из HTML-структуры.
"""

import trafilatura


def get_website_text_content(url: str) -> str:
    """
    Эта функция принимает URL и возвращает основное текстовое содержимое веб-сайта.
    Текстовое содержимое извлекается с помощью trafilatura и легче для понимания,
    чем исходный HTML. Результат не предназначен для прямого чтения и будет
    лучше, если его обработать перед показом пользователю.

    Примеры веб-сайтов для получения информации:
    Новости о перголах: https://pergolamarket.ru/news
    Документация технических решений: https://pergolamarket.ru/documents
    
    Args:
        url (str): URL веб-страницы для извлечения текста

    Returns:
        str: Извлеченный текст страницы без HTML-разметки
    """
    # Отправляем запрос на веб-сайт
    downloaded = trafilatura.fetch_url(url)
    
    # Извлекаем текстовое содержимое
    text = trafilatura.extract(downloaded)
    
    return text


def get_website_html(url: str) -> str:
    """
    Получает полное HTML-содержимое веб-страницы.
    Может использоваться, если требуется сохранить форматирование
    или получить дополнительные элементы, которые trafilatura не извлекает.
    
    Args:
        url (str): URL веб-страницы для извлечения HTML

    Returns:
        str: Полный HTML-код страницы
    """
    # Отправляем запрос на веб-сайт и получаем исходный HTML
    return trafilatura.fetch_url(url)


def parse_product_info(url: str) -> dict:
    """
    Анализирует страницу продукта и извлекает структурированную информацию.
    Пример использования для страниц с пергольной продукцией.
    
    Args:
        url (str): URL страницы продукта
        
    Returns:
        dict: Словарь с извлеченной информацией о продукте
    """
    # Получаем HTML страницы
    html = get_website_html(url)
    
    # Извлекаем основной текст
    text = trafilatura.extract(html)
    
    # Получаем метаданные (заголовок, описание и т.д.)
    metadata = trafilatura.extract_metadata(html)
    
    # Формируем структурированную информацию
    product_info = {
        "title": metadata.title if metadata else "Нет заголовка",
        "description": metadata.description if metadata else "Нет описания",
        "content": text if text else "Нет содержимого",
        "url": url
    }
    
    return product_info


if __name__ == "__main__":
    # Пример использования
    import argparse
    
    parser = argparse.ArgumentParser(description="Инструмент для извлечения текста с веб-страниц")
    parser.add_argument("--url", type=str, help="URL страницы для анализа")
    parser.add_argument("--port", type=int, default=5001, help="Порт для запуска сервиса")
    
    args = parser.parse_args()
    
    if args.url:
        print(f"Извлечение текста из {args.url}")
        content = get_website_text_content(args.url)
        print("\nИзвлеченный текст:")
        print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("Модуль web_scraper запущен. Используйте параметр --url для анализа конкретной страницы.")
        print(f"Сервис доступен на порту: {args.port}")