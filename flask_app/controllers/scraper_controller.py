"""
Контроллер для веб-скрапинга и сбора данных о перголах с различных сайтов.
Использует trafilatura для эффективного извлечения содержимого.
"""

import logging
import json
import re
from datetime import datetime
import traceback
from flask import Blueprint, request, jsonify, render_template, current_app, abort
from urllib.parse import urlparse
import trafilatura

# Создаем блюпринт для скрапинга
scraper_bp = Blueprint('scraper', __name__, url_prefix='/scraper')
api_scraper_bp = Blueprint('api_scraper', __name__, url_prefix='/api')

# Настройка логирования
logger = logging.getLogger(__name__)


@scraper_bp.route('/', methods=['GET'])
def scraper_page():
    """Отображает страницу с интерфейсом для веб-скрапинга."""
    return render_template('scraper.html')


@api_scraper_bp.route('/scrape-data', methods=['POST'])
def scrape_data():
    """
    API-метод для скрапинга данных с указанного URL.
    
    Ожидает JSON-запрос с параметрами:
    - url: URL для скрапинга
    - scrape_type: Тип данных для скрапинга (general, prices, specifications, reviews)
    
    Возвращает JSON с результатами скрапинга.
    """
    try:
        # Получаем параметры запроса
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL не указан'}), 400
        
        url = data['url']
        scrape_type = data.get('scrape_type', 'general')
        
        # Валидация URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({'error': 'Некорректный URL'}), 400
        
        # Проверяем разрешенные домены (для безопасности)
        allowed_domains = current_app.config.get('ALLOWED_SCRAPING_DOMAINS', [
            'pergolamarket.ru', 'pergolas.ru', 'decolife.ru', 'forumhouse.ru', 
            'stroyka.ru', 'wikipedia.org', 'dizainland.ru', 'houzz.ru', 
            'inmyroom.ru', 'ivd.ru', 'elitepergola.ru'
        ])
        
        domain = parsed_url.netloc.lower()
        if not any(allowed_domain in domain for allowed_domain in allowed_domains):
            return jsonify({
                'error': f'Скрапинг данного домена запрещен. Разрешены: {", ".join(allowed_domains)}'
            }), 403
        
        # Скрапим данные
        result = perform_scraping(url, scrape_type)
        
        # Логируем успешный скрапинг
        logger.info(f"Успешный скрапинг: {url}, тип: {scrape_type}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Ошибка при скрапинге: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Ошибка при обработке запроса: {str(e)}'}), 500


def perform_scraping(url, scrape_type):
    """
    Выполняет скрапинг данных с указанного URL.
    
    Args:
        url (str): URL для скрапинга
        scrape_type (str): Тип данных для скрапинга (general, prices, specifications, reviews)
    
    Returns:
        dict: Результаты скрапинга
    """
    try:
        # Получаем HTML-контент
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {'error': 'Не удалось получить содержимое с указанного URL'}
        
        # Извлекаем текст
        text_content = trafilatura.extract(downloaded)
        if not text_content:
            return {'error': 'Не удалось извлечь текстовое содержимое'}
        
        # Обрабатываем в зависимости от типа скрапинга
        if scrape_type == 'general':
            return extract_general_info(text_content, url)
        elif scrape_type == 'prices':
            return extract_price_info(text_content, url)
        elif scrape_type == 'specifications':
            return extract_specifications(text_content, url)
        elif scrape_type == 'reviews':
            return extract_reviews(text_content, url)
        else:
            return {'error': f'Неизвестный тип скрапинга: {scrape_type}'}
    
    except Exception as e:
        logger.error(f"Ошибка при скрапинге {url}: {str(e)}")
        return {'error': f'Ошибка при скрапинге: {str(e)}'}


def extract_general_info(text_content, url):
    """
    Извлекает общую информацию из текстового содержимого.
    
    Args:
        text_content (str): Текстовое содержимое страницы
        url (str): URL, с которого взяты данные
    
    Returns:
        dict: Извлеченная информация
    """
    # Ограничиваем размер текста для анализа
    text_sample = text_content[:10000]
    
    # Базовые параметры результата
    result = {
        'summary': '',
        'data': [],
        'source_url': url,
        'timestamp': datetime.now().isoformat()
    }
    
    # Извлекаем информацию о перголах
    pergola_types = extract_pergola_types(text_sample)
    pergola_features = extract_pergola_features(text_sample)
    pergola_materials = extract_pergola_materials(text_sample)
    
    # Добавляем найденные типы пергол
    if pergola_types:
        result['data'].append({
            'name': 'Типы пергол',
            'value': ', '.join(pergola_types)
        })
    
    # Добавляем особенности пергол
    if pergola_features:
        result['data'].append({
            'name': 'Особенности',
            'value': ', '.join(pergola_features)
        })
    
    # Добавляем материалы пергол
    if pergola_materials:
        result['data'].append({
            'name': 'Материалы',
            'value': ', '.join(pergola_materials)
        })
    
    # Извлекаем параметры размеров
    dimensions = extract_dimensions(text_sample)
    if dimensions:
        for dim_name, dim_value in dimensions.items():
            result['data'].append({
                'name': dim_name,
                'value': dim_value
            })
    
    # Создаем краткую сводку
    result['summary'] = create_summary(text_sample, url)
    
    return result


def extract_price_info(text_content, url):
    """
    Извлекает информацию о ценах из текстового содержимого.
    
    Args:
        text_content (str): Текстовое содержимое страницы
        url (str): URL, с которого взяты данные
    
    Returns:
        dict: Извлеченная информация о ценах
    """
    result = {
        'summary': '',
        'data': [],
        'comparison': [],
        'source_url': url,
        'timestamp': datetime.now().isoformat()
    }
    
    # Поиск цен с помощью регулярных выражений
    # Ищем цены в формате "XXX XXX руб" или "XXX XXX ₽" или "от XXX XXX руб"
    price_patterns = [
        r'от\s+(\d+[\s\d]*(?:,\d+)?)\s*(?:руб|\₽|рублей)',
        r'(\d+[\s\d]*(?:,\d+)?)\s*(?:руб|\₽|рублей)',
        r'цена[^\d]*(\d+[\s\d]*(?:,\d+)?)\s*(?:руб|\₽|рублей)',
        r'стоимость[^\d]*(\d+[\s\d]*(?:,\d+)?)\s*(?:руб|\₽|рублей)',
        r'(\d+[\s\d]*(?:,\d+)?)\s*(?:руб|\₽|рублей)[^\d]*за\s+м2'
    ]
    
    found_prices = []
    
    for pattern in price_patterns:
        matches = re.finditer(pattern, text_content, re.IGNORECASE)
        for match in matches:
            price_str = match.group(1).replace(' ', '')
            price_str = price_str.replace(',', '.')
            try:
                price = float(price_str)
                context = text_content[max(0, match.start() - 100):min(len(text_content), match.end() + 100)]
                found_prices.append({
                    'price': price,
                    'context': context.strip()
                })
            except ValueError:
                continue
    
    # Группируем найденные цены по контексту
    grouped_prices = {}
    for price_info in found_prices:
        # Пытаемся найти название продукта в контексте
        context = price_info['context']
        product_match = re.search(r'([БB]\d+(?:NEW)?|[Пп]ергола\s+\w+)', context)
        product_name = product_match.group(1) if product_match else "Пергола"
        
        if product_name not in grouped_prices:
            grouped_prices[product_name] = []
        
        grouped_prices[product_name].append(price_info['price'])
    
    # Добавляем сгруппированные цены в результат
    for product, prices in grouped_prices.items():
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        result['data'].append({
            'name': f'{product} (мин.)',
            'value': f"{min_price:,.2f} ₽".replace(',', ' ')
        })
        
        result['data'].append({
            'name': f'{product} (макс.)',
            'value': f"{max_price:,.2f} ₽".replace(',', ' ')
        })
        
        result['data'].append({
            'name': f'{product} (средняя)',
            'value': f"{avg_price:,.2f} ₽".replace(',', ' ')
        })
        
        # Добавляем в сравнение
        result['comparison'].append({
            'name': product,
            'price': avg_price
        })
    
    # Добавляем дату сбора информации
    result['data'].append({
        'name': 'Дата сбора',
        'value': datetime.now().strftime('%d.%m.%Y')
    })
    
    # Создаем краткую сводку
    if grouped_prices:
        products_count = len(grouped_prices)
        avg_all = sum([sum(prices) / len(prices) for prices in grouped_prices.values()]) / products_count
        
        result['summary'] = (
            f"Найдена информация о ценах на {products_count} видов пергол. "
            f"Средняя стоимость составляет {avg_all:,.2f} ₽. "
            f"Данные собраны {datetime.now().strftime('%d.%m.%Y')}."
        ).replace(',', ' ')
    else:
        result['summary'] = "Информация о ценах на перголы не найдена."
    
    return result


def extract_specifications(text_content, url):
    """
    Извлекает технические характеристики из текстового содержимого.
    
    Args:
        text_content (str): Текстовое содержимое страницы
        url (str): URL, с которого взяты данные
    
    Returns:
        dict: Извлеченные технические характеристики
    """
    result = {
        'summary': '',
        'data': [],
        'source_url': url,
        'timestamp': datetime.now().isoformat()
    }
    
    # Ищем характеристики в формате "Название: значение"
    spec_patterns = [
        r'([А-Яа-яA-Za-z\s]+):\s*([^\.:\n]+)',
        r'([А-Яа-яA-Za-z\s]+)\s*-\s*([^\.:\n]+)'
    ]
    
    found_specs = []
    
    for pattern in spec_patterns:
        matches = re.finditer(pattern, text_content)
        for match in matches:
            name = match.group(1).strip()
            value = match.group(2).strip()
            
            # Фильтруем только релевантные характеристики
            relevant_keywords = [
                'размер', 'ширина', 'длина', 'высота', 'вес', 'материал',
                'мощность', 'цвет', 'привод', 'ламел', 'нагрузка', 'управление',
                'количество', 'производитель', 'гарантия', 'класс', 'тип'
            ]
            
            if any(keyword in name.lower() for keyword in relevant_keywords) and len(value) < 100:
                found_specs.append({
                    'name': name,
                    'value': value
                })
    
    # Удаляем дубликаты, сохраняя порядок
    unique_specs = []
    seen_names = set()
    
    for spec in found_specs:
        if spec['name'].lower() not in seen_names:
            unique_specs.append(spec)
            seen_names.add(spec['name'].lower())
    
    # Добавляем спецификации в результат
    result['data'] = unique_specs
    
    # Создаем краткую сводку
    if unique_specs:
        result['summary'] = (
            f"Найдено {len(unique_specs)} технических характеристик перголы. "
            f"Включая информацию о размерах, материалах и функциональных особенностях."
        )
    else:
        result['summary'] = "Технические характеристики перголы не найдены."
    
    return result


def extract_reviews(text_content, url):
    """
    Извлекает отзывы клиентов из текстового содержимого.
    
    Args:
        text_content (str): Текстовое содержимое страницы
        url (str): URL, с которого взяты данные
    
    Returns:
        dict: Извлеченные отзывы
    """
    result = {
        'summary': '',
        'data': [],
        'source_url': url,
        'timestamp': datetime.now().isoformat()
    }
    
    # Разделяем текст на параграфы
    paragraphs = text_content.split('\n\n')
    
    # Ищем потенциальные отзывы
    review_keywords = ['отзыв', 'понравил', 'рекоменд', 'доволен', 'спасибо', 'качество', 'оценка']
    found_reviews = []
    
    for paragraph in paragraphs:
        # Если параграф слишком короткий, пропускаем
        if len(paragraph) < 30 or len(paragraph) > 1000:
            continue
        
        # Проверяем, похож ли параграф на отзыв
        paragraph_lower = paragraph.lower()
        if any(keyword in paragraph_lower for keyword in review_keywords):
            # Ищем имя автора
            author_match = re.search(r'([А-Я][а-я]+\s+[А-Я]\.(?:[А-Я]\.)?)', paragraph)
            author = author_match.group(1) if author_match else "Клиент"
            
            # Ищем дату
            date_match = re.search(r'(\d{1,2}[\.\/]\d{1,2}[\.\/]\d{2,4})', paragraph)
            date = date_match.group(1) if date_match else "Не указана"
            
            # Ищем оценку
            rating_match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:из|\/)\s*[5５]', paragraph)
            rating = rating_match.group(1) if rating_match else "Нет оценки"
            
            # Добавляем отзыв
            found_reviews.append({
                'name': f"Отзыв от {author}, {date}",
                'value': paragraph
            })
            
            # Если нашли достаточно отзывов, останавливаемся
            if len(found_reviews) >= 5:
                break
    
    # Добавляем отзывы в результат
    result['data'] = found_reviews
    
    # Создаем краткую сводку
    if found_reviews:
        result['summary'] = f"Найдено {len(found_reviews)} отзывов клиентов о перголах."
    else:
        result['summary'] = "Отзывы клиентов не найдены."
    
    return result


def extract_pergola_types(text):
    """
    Извлекает упоминаемые типы пергол из текста.
    
    Args:
        text (str): Текст для анализа
    
    Returns:
        list: Найденные типы пергол
    """
    # Ищем упоминания типов пергол в тексте
    type_patterns = [
        r'[BБ]\s*(\d+)(?:\s*NEW)?',  # B500, B700, B600 и т.д.
        r'пергола\s+([а-яА-Яa-zA-Z]+[a-zA-Z0-9]+)',  # пергола Classic, пергола Premium и т.д.
        r'биоклиматическая\s+пергола'
    ]
    
    found_types = set()
    
    for pattern in type_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.groups():
                pergola_type = f"B{match.group(1)}"
                found_types.add(pergola_type)
            else:
                found_types.add(match.group(0).strip())
    
    # Добавляем стандартные типы, если они упоминаются в тексте
    standard_types = ['B500', 'B600', 'B700']
    for std_type in standard_types:
        if std_type.lower() in text.lower() or f"B {std_type[1:]}".lower() in text.lower():
            found_types.add(std_type)
    
    return list(found_types)


def extract_pergola_features(text):
    """
    Извлекает упоминаемые особенности пергол.
    
    Args:
        text (str): Текст для анализа
    
    Returns:
        list: Найденные особенности пергол
    """
    # Ключевые слова для поиска особенностей
    feature_keywords = [
        'автоматическ', 'электропривод', 'пульт', 'дистанционн', 'управлен',
        'поворотн', 'ламел', 'водонепроницаем', 'защит', 'датчик', 'освещен',
        'подсветк', 'RGB', 'LED', 'обогрев', 'климат', 'солнцезащит', 'модул'
    ]
    
    found_features = set()
    
    # Разбиваем текст на предложения
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for keyword in feature_keywords:
            if keyword in sentence_lower:
                # Извлекаем фразу с особенностью
                start = max(0, sentence_lower.find(keyword) - 30)
                end = min(len(sentence_lower), sentence_lower.find(keyword) + 30)
                
                feature_snippet = sentence[start:end].strip()
                if feature_snippet and len(feature_snippet) > 5:
                    # Очищаем от лишних символов
                    feature_snippet = re.sub(r'[^\w\s\-\.,]', '', feature_snippet)
                    feature_snippet = ' '.join(feature_snippet.split())
                    
                    # Если фраза слишком длинная, сокращаем
                    if len(feature_snippet) > 50:
                        feature_snippet = feature_snippet[:47] + '...'
                    
                    found_features.add(feature_snippet)
    
    return list(found_features)


def extract_pergola_materials(text):
    """
    Извлекает упоминаемые материалы пергол.
    
    Args:
        text (str): Текст для анализа
    
    Returns:
        list: Найденные материалы пергол
    """
    # Ключевые слова для поиска материалов
    material_keywords = [
        'алюмини', 'сталь', 'нержавеющ', 'дерев', 'пластик', 'композит',
        'поликарбонат', 'стекл', 'ткан', 'акрил', 'полиэстер'
    ]
    
    found_materials = set()
    
    # Разбиваем текст на предложения
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for keyword in material_keywords:
            if keyword in sentence_lower:
                # Находим фразу с материалом
                match = re.search(fr'{keyword}\w*(?:\s+\w+){{0,2}}', sentence_lower)
                if match:
                    material = match.group(0).strip()
                    if material and len(material) > 3:
                        # Преобразуем первую букву в верхний регистр
                        material = material[0].upper() + material[1:]
                        found_materials.add(material)
    
    return list(found_materials)


def extract_dimensions(text):
    """
    Извлекает упоминаемые размеры пергол.
    
    Args:
        text (str): Текст для анализа
    
    Returns:
        dict: Найденные размеры (ширина, длина, высота)
    """
    dimensions = {}
    
    # Шаблоны для поиска размеров
    dimension_patterns = {
        'Ширина': [
            r'ширина[^\d]*(\d+(?:[,.]\d+)?)\s*(?:м|метр)',
            r'ширина[^\d]*от\s*(\d+(?:[,.]\d+)?)\s*до\s*\d+(?:[,.]\d+)?\s*(?:м|метр)'
        ],
        'Длина (вынос)': [
            r'длина[^\d]*(\d+(?:[,.]\d+)?)\s*(?:м|метр)',
            r'вынос[^\d]*(\d+(?:[,.]\d+)?)\s*(?:м|метр)',
            r'длина[^\d]*от\s*(\d+(?:[,.]\d+)?)\s*до\s*\d+(?:[,.]\d+)?\s*(?:м|метр)'
        ],
        'Высота': [
            r'высота[^\d]*(\d+(?:[,.]\d+)?)\s*(?:м|метр|см|сантиметр)',
            r'высота[^\d]*от\s*(\d+(?:[,.]\d+)?)\s*до\s*\d+(?:[,.]\d+)?\s*(?:м|метр|см|сантиметр)'
        ]
    }
    
    for dim_name, patterns in dimension_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '.')
                dimensions[dim_name] = f"{value} м"
                break
    
    return dimensions


def create_summary(text, url):
    """
    Создает краткую сводку на основе текста страницы.
    
    Args:
        text (str): Текст для анализа
        url (str): URL, с которого взяты данные
    
    Returns:
        str: Краткая сводка
    """
    # Извлекаем типы пергол
    types = extract_pergola_types(text)
    types_str = ', '.join(types) if types else "различные модели"
    
    # Извлекаем материалы
    materials = extract_pergola_materials(text)
    materials_str = ', '.join(materials) if materials else "различных материалов"
    
    # Создаем сводку
    domain = urlparse(url).netloc
    
    summary = (
        f"На сайте {domain} представлена информация о перголах {types_str}, "
        f"изготовленных из {materials_str}. "
        f"Сайт содержит информацию о технических характеристиках, "
        f"возможностях комплектации и установки конструкций."
    )
    
    return summary


# Регистрируем блюпринты в приложении
def register_scraper_blueprints(app):
    app.register_blueprint(scraper_bp)
    app.register_blueprint(api_scraper_bp)