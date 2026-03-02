"""
Калькулятор стоимости пергол - базовая версия без сложных стилей и модификаций
Максимально простой подход с использованием стандартных компонентов Streamlit
"""
import streamlit as st
import pandas as pd
import io
import json
import sys
import time
import os
# Импортируем функции для работы с Яндекс.Метрикой
from add_yandex_metrika import add_yandex_metrika, send_calc_success_event
# Импортируем функцию для плавного скролла
from scroll import smooth_scroll_to
# Импортируем функцию для виртуального скролла
from auto_scroll import create_growing_spacer
# Импортируем модуль для анимаций и визуальных эффектов
import animations
# Импортируем модуль для плавающих кнопок навигации
from floating_buttons import add_results_navigation_button, add_dimensions_edit_button
# Импортируем модуль кэширования и оптимизации изображений
from image_cache import preload_all_pergola_images, get_optimized_pergola_images, preload_images_js
# Импортируем модуль для генерации PDF
from pdf_generator_fpdf_rus import generate_commercial_offer, format_pergola_data_for_pdf
# Импортируем модуль оптимизации производительности
from performance_optimizations import optimize_images_loading, optimize_form_rendering, add_page_speed_optimizations
# Импортируем модуль оптимизации для iframe
from iframe_optimizer import optimize_for_iframe, add_content_visibility_optimizations, optimize_startup_sequence
# Импортируем модуль определения iframe
from iframe_detector import adapt_for_iframe
# Импортируем модуль для исправления отступов вверху страницы
from fix_top_padding import remove_padding_top
import os
import math
import csv
import time
import base64
import uuid
from datetime import datetime
# Импортируем модуль для отображения галереи проектов
from components.gallery import display_gallery_section
# Импортируем модуль настроек цен и наценок
from config import pricing_settings

def get_plural_form(number, one, two, five):
    """
    Возвращает правильную форму существительного для числительного по правилам русского языка.
    
    Args:
        number (int): Число, для которого нужно подобрать форму
        one (str): Форма для 1 (номинатив единственного числа)
        two (str): Форма для 2-4 (генитив единственного числа)
        five (str): Форма для 5-20 (генитив множественного числа)
        
    Returns:
        str: Правильная форма слова
    """
    n = abs(number) % 100
    if n >= 11 and n <= 19:
        return five
    n = n % 10
    if n == 1:
        return one
    if n >= 2 and n <= 4:
        return two
    return five
# Явно импортируем только из pdf_generator_fpdf_rus (строка 25)
# from pdf_generator_fpdf import generate_commercial_offer, format_pergola_data_for_pdf
from config.pergola_descriptions import (
    get_pergola_description,
    get_modular_system_description,
    get_drainage_system_description,
    get_bansbach_description,
    get_bioclimatic_install_description,
    get_lamella_engineering_description,
    get_pergola_images,
    get_pergola_image_caption
)

# Используем прямое определение структур данных для упрощения
# Типы пергол
PERGOLA_TYPES = {
    "B500NEW": "В500 - с поворотными ламелями",
    "B700NEW": "В700 - с поворотно-сдвижными ламелями",
    "B600": "В600 PIR - со стационарными панелями"
}

# Описания типов пергол
PERGOLA_TYPE_DESCRIPTIONS = {
    "B500NEW": "Современная пергола с поворотными алюминиевыми ламелями.",
    "B700NEW": "Премиальная пергола с поворотно-сдвижными ламелями.",
    "B600": "Пергола со стационарной крышей из PIR сэндвич-панелей."
}

# Типы ламелей
LAMELLA_TYPES = {
    "B500-20NEW": "Ламели 200 мм (усиленные)",
    "B500-25NEW": "Ламели 250 мм (стандарт)",
    "B700-20NEW": "Ламели 200 мм (усиленные)",
    "B700-25NEW": "Ламели 250 мм (стандарт)",
    "B600-PIR": "PIR сэндвич-панель",
    "lamella-200": "Ламели 200 мм (усиленные)",
    "lamella-250": "Ламели 250 мм (стандарт)"
}

# Максимально допустимые размеры для каждого типа пергол
MAX_DIMENSIONS = {
    # B500 с ламелями 250 мм - ширина 13.5м, вынос 8м
    "B500NEW_250": {"width": 13.5, "length": 8.0},
    # B500 с ламелями 200 мм - ширина 15м, вынос 8м
    "B500NEW_200": {"width": 15.0, "length": 8.0},
    # B700 с ламелями 250 мм - ширина 13.5м, вынос 8м
    "B700NEW_250": {"width": 13.5, "length": 8.0},
    # B700 с ламелями 200 мм - ширина 15м, вынос 8м
    "B700NEW_200": {"width": 15.0, "length": 8.0},
    # B600 - ширина 13.5м, вынос 8м
    "B600": {"width": 13.5, "length": 8.0}
}

# Правила для добавления дополнительных колонн в зависимости от размера выноса
ADDITIONAL_COLUMNS_RULES = {
    "B500NEW": {
        "250": 6.5,  # Для ламелей 250мм - если вынос > 6.5м, нужны доп. колонны
        "200": 6.85  # Для ламелей 200мм - если вынос > 6.85м, нужны доп. колонны
    },
    "B700NEW": {
        "250": 6.5,  # Для ламелей 250мм - если вынос > 6.5м, нужны доп. колонны
        "200": 6.85  # Для ламелей 200мм - если вынос > 6.85м, нужны доп. колонны
    },
    "B600": {
        "PIR": 6.5   # Для PIR панелей - если вынос > 6.5м, нужны доп. колонны
    }
}

# Стоимость дополнительных колонн в зависимости от количества модулей
COLUMNS_PRICES = {
    1: 653,  # 1 модуль - 2 колонны - 653 евро
    2: 980,  # 2 модуля - 3 колонны - 980 евро
    3: 1306  # 3 модуля - 4 колонны - 1306 евро
}

# Усилитель лотка добавляется автоматически при выносе > 6.5м
GUTTER_INSERT_THRESHOLD = 6.5
GUTTER_INSERT_PRICE_PER_METER = 80  # Цена усилителя лотка 80 евро за погонный метр

# Наценки за доставку и установку (в процентах от базовой стоимости) и курс евро
# загружаются из модуля pricing_settings, где они могут быть изменены через админпанель

# Правила для выбора привода Bansbach для B500NEW
BANSBACH_DRIVE_RULES = {
    1: [  # 1 модуль
        {"width": 2.5, "length": 8.0, "tandem": False},  # До 2.5м ширины и до 8м выноса - T1
        {"width": 3.0, "length": 6.5, "tandem": True},   # > 2.5м и > 6.5м выноса - Tandem (для 3.0x8.0 тоже нужен Tandem!)
        {"width": 3.5, "length": 5.5, "tandem": True},   # > 3.0м и > 5.5м выноса - Tandem
        {"width": 4.0, "length": 5.0, "tandem": True},   # > 3.5м и > 5.0м выноса - Tandem
        {"width": float('inf'), "length": 5.0, "tandem": True}  # > 4.0м и > 5.0м выноса - Tandem
    ],
    2: [  # 2 модуля
        {"width": 5.0, "length": 8.0, "tandem": False},  # До 5м ширины и до 8м выноса - T1
        {"width": 6.0, "length": 7.5, "tandem": True},   # > 5м и > 7.5м выноса - Tandem
        {"width": 7.0, "length": 6.5, "tandem": True},   # > 6м и > 6.5м выноса - Tandem
        {"width": 8.0, "length": 5.5, "tandem": True},   # > 7м и > 5.5м выноса - Tandem
        {"width": float('inf'), "length": 5.0, "tandem": True}  # > 8м и > 5.0м выноса - Tandem
    ],
    3: [  # 3 модуля
        {"width": 7.5, "length": 8.0, "tandem": False},  # До 7.5м ширины и до 8м выноса - T1
        {"width": 9.0, "length": 7.5, "tandem": True},   # > 7.5м и > 7.5м выноса - Tandem
        {"width": 10.5, "length": 6.5, "tandem": True},  # > 9м и > 6.5м выноса - Tandem
        {"width": 12.0, "length": 5.5, "tandem": True},  # > 10.5м и > 5.5м выноса - Tandem
        {"width": float('inf'), "length": 5.0, "tandem": True}  # > 12м и > 5.0м выноса - Tandem
    ]
}

# Правила для выбора привода Somfy для B700NEW
SOMFY_DRIVE_RULES = {
    1: [  # 1 модуль
        {"width": 3.0, "length": 7.0, "tandem": True},   # до 3м ширины и > 7м выноса - Tandem
        {"width": 3.5, "length": 6.0, "tandem": True},   # до 3.5м ширины и > 6м выноса - Tandem
        {"width": float('inf'), "length": float('inf'), "tandem": False}  # По умолчанию - M1
    ],
    2: [  # 2 модуля
        {"width": 6.0, "length": 7.0, "tandem": True},   # > 6м ширины и > 7м выноса - Tandem
        {"width": 7.0, "length": 6.0, "tandem": True},   # > 7м ширины и > 6м выноса - Tandem
        {"width": float('inf'), "length": float('inf'), "tandem": False}  # По умолчанию - M1
    ],
    3: [  # 3 модуля
        {"width": 9.0, "length": 7.0, "tandem": True},   # > 9м ширины и > 7м выноса - Tandem
        {"width": 10.5, "length": 6.0, "tandem": True},  # > 10.5м ширины и > 6м выноса - Tandem
        {"width": float('inf'), "length": float('inf'), "tandem": False}  # По умолчанию - M1
    ]
}

# Цены на приводы
DRIVE_PRICES = {
    "B500NEW": {
        "standard": 700,     # Bansbach T1 - 700 евро
        "tandem": 1250       # Bansbach Tandem - 1250 евро
    },
    "B700NEW": {
        "standard": 300,     # Somfy M1 - 300 евро
        "tandem": 1000       # Somfy M2 TANDEM - 1000 евро
    }
}

# Пульты дистанционного управления
REMOTE_CONTROL_TYPES = {
    1: {"name": "Simu 1K", "price": 25},    # 1 канал - 25 евро
    5: {"name": "Simu 5K", "price": 40},    # 5 каналов - 40 евро
    15: {"name": "Simu 15K", "price": 90}   # 15 каналов - 90 евро
}

# Освещение
LIGHTING_PRICES = {
    "controller": 300,       # Блок управления Somfy RTS Dimmer - 300 евро
    "white_led": 20,         # Сверхъяркая LED лента - 20 евро/м
    "rgb_led": 20            # Сверхъяркая RGB лента - 20 евро/м
}

# Функция для загрузки данных о ценах из CSV файлов
def load_price_data(pergola_type, lamella_size):
    """
    Загружает данные о ценах из соответствующего CSV файла
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        dict: Словарь с ценами для разных размеров перголы
    """
    # Определяем соответствие типов пергол и имен файлов
    # Ищем как русские, так и английские версии файлов
    file_mapping = {
        ("B500NEW", "200"): ["attached_assets/Price_B500-20.csv", "attached_assets/Прайс_В500-20.csv"],
        ("B500NEW", "250"): ["attached_assets/Price_B500-25.csv", "attached_assets/Прайс_В500-25.csv"],
        ("B700NEW", "200"): ["attached_assets/Price_B700-20.csv", "attached_assets/Прайс_B700-20.csv"],
        ("B700NEW", "250"): ["attached_assets/Price_B700-25.csv", "attached_assets/Прайс_B700-25.csv"],
        ("B600", "PIR"): ["attached_assets/Price_B600_PIR.csv", "attached_assets/Прайс_В600_PIR.csv"]
    }
    
    key = (pergola_type, lamella_size)
    if key not in file_mapping:
        print(f"Ошибка: Комбинация {pergola_type} и {lamella_size} не найдена в маппинге файлов")
        return {}
    
    # Получаем пути к файлам прайса (поддерживаем и английскую, и русскую версию)
    file_paths = file_mapping[key]
    
    # Проверяем, существует ли хотя бы один из файлов
    existing_file_path = None
    for path in file_paths:
        if os.path.exists(path):
            existing_file_path = path
            break
    
    if not existing_file_path:
        print(f"Ошибка: Файлы прайса {file_paths} не найдены")
        return {}
    
    # Используем найденный файл
    file_path = existing_file_path
    
    print(f"Загрузка прайс-листа из файла: {file_path}")
    
    prices = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Определяем разделитель CSV (точка с запятой или запятая)
            first_line = file.readline().strip()
            if ';' in first_line:
                delimiter = ';'
            else:
                delimiter = ','
            
            print(f"Обнаружен разделитель: '{delimiter}'")
            
            # Перематываем файл в начало
            file.seek(0)
            
            reader = csv.reader(file, delimiter=delimiter)
            
            # Пропускаем первую строку (если она содержит информацию о модулях)
            first_row = next(reader)
            if "модуль" in ' '.join(first_row).lower():
                print("Обнаружена строка с информацией о модулях, пропускаем")
                header = next(reader)  # Берем следующую строку как заголовок
            else:
                header = first_row  # Если первая строка не о модулях, она и есть заголовок
            
            print(f"Заголовок: {header}")
            
            # Извлекаем значения длины из заголовка
            length_values = []
            for val in header[1:]:  # Пропускаем первую колонку
                if val.strip():
                    try:
                        # Обрабатываем разные форматы чисел
                        cleaned_val = val.replace(',', '.').strip()
                        length_values.append(float(cleaned_val))
                    except ValueError:
                        print(f"Предупреждение: Не удалось преобразовать '{val}' в число")
                        continue  # Пропускаем, если не удалось преобразовать в число
            
            print(f"Значения длины из заголовка: {length_values}")
            
            # Обрабатываем строки с данными
            for row in reader:
                if not row or len(row) <= 1:
                    continue
                
                try:
                    # Получаем ширину из первой колонки
                    width_str = row[0].strip()
                    if not width_str:
                        continue
                    
                    width = float(width_str.replace(',', '.'))
                    
                    # Обрабатываем цены
                    for i, price_str in enumerate(row[1:]):
                        if i < len(length_values) and price_str.strip():
                            length = length_values[i]
                            try:
                                # Преобразуем строку цены в число
                                # Убираем пробелы и меняем запятую на точку для десятичных чисел
                                price = float(price_str.replace(' ', '').replace(',', '.'))
                                if width not in prices:
                                    prices[width] = {}
                                prices[width][length] = price
                            except ValueError:
                                print(f"Предупреждение: Не удалось преобразовать '{price_str}' в цену")
                                continue  # Пропускаем, если не удалось преобразовать в число
                except (ValueError, IndexError) as e:
                    print(f"Ошибка при обработке строки {row}: {str(e)}")
                    continue
        
        print(f"Загружено {len(prices)} значений ширины с ценами")
        
        # Выводим загруженные данные для отладки
        for width in sorted(prices.keys())[:3]:  # Показываем только 3 первых значения для краткости
            print(f"Ширина {width} м: {prices[width]}")
        
        return prices
    except Exception as e:
        print(f"Ошибка загрузки прайс-листа {file_path}: {str(e)}")
        return {}

def calculate_lighting_perimeter(width_m, length_m, modules=1):
    """
    Расчет периметра подсветки по правилам.
    Для 1 модуля - просто периметр.
    Для нескольких модулей - сумма периметров всех модулей.
    
    Args:
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        float: Длина периметра для светодиодной ленты
    """
    if modules <= 1:
        return 2 * (width_m + length_m)
    
    # Для многомодульных пергол
    module_width = width_m / modules
    module_perimeter = 2 * (module_width + length_m)
    return module_perimeter * modules

def adjust_length_for_lamella_size(length_m, lamella_size_mm):
    """
    Корректирует размер выноса перголы до ближайшего целого числа ламелей
    
    Args:
        length_m (float): Вынос перголы в метрах
        lamella_size_mm (int): Размер ламели в миллиметрах (200 или 250)
        
    Returns:
        float: Скорректированный размер выноса перголы
    """
    lamella_size_m = lamella_size_mm / 1000  # Перевод из мм в метры
    num_lamellas = length_m / lamella_size_m
    
    # Округляем до ближайшего целого числа ламелей в большую сторону
    num_lamellas_rounded = math.ceil(num_lamellas)
    
    # Вычисляем скорректированную длину
    adjusted_length = num_lamellas_rounded * lamella_size_m
    
    return adjusted_length

def get_base_price(pergola_type, lamella_size, width_m, length_m):
    """
    Получает базовую стоимость перголы из прайс-листа, используя точное соответствие
    шириной и длиной (выносом) из таблицы прайса
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        
    Returns:
        float: Базовая стоимость перголы
    """
    prices = load_price_data(pergola_type, lamella_size)
    if not prices:
        raise ValueError(f"Не удалось загрузить данные о ценах для {pergola_type} с ламелями {lamella_size}")
    
    # Логирование для отладки
    print(f"Поиск цены для {pergola_type} с ламелями {lamella_size}, размер {width_m}x{length_m}м")
    
    # Получаем доступные размеры
    available_widths = sorted(prices.keys())
    available_lengths = set()
    for width_data in prices.values():
        available_lengths.update(width_data.keys())
    available_lengths = sorted(available_lengths)
    
    # Логирование доступных размеров для отладки
    print(f"Доступные ширины: {available_widths}")
    print(f"Доступные длины: {available_lengths}")
    
    # В CSV файле цены указаны в формате "вынос (строка) x ширина (столбец)"
    # Но в калькуляторе параметры указаны как "ширина x вынос" 
    # Поэтому меняем местами параметры при поиске цены
    width_orig, length_orig = width_m, length_m
    
    # Находим точный размер или ближайший больший размер
    # В CSV файле цены указаны в формате "вынос (строка) x ширина (столбец)"
    # Но в калькуляторе параметры указаны как "ширина x вынос"
    # Поэтому для поиска в прайсе меняем местами ширину и вынос
    lookup_width = length_m  # Используем длину как ширину в прайсе
    lookup_length = width_m  # Используем ширину как длину в прайсе
    
    # Ищем точное совпадение по ширине (в прайсе это вынос)
    if lookup_width in available_widths:
        width_match = lookup_width
    else:
        # Если точного совпадения нет, ищем ближайшую большую ширину
        width_match = next((w for w in available_widths if w > lookup_width), max(available_widths))
    
    # Ищем точное совпадение по длине (в прайсе это ширина)
    if lookup_length in available_lengths:
        length_match = lookup_length
    else:
        # Если точного совпадения нет, ищем ближайшую большую длину
        length_match = next((l for l in available_lengths if l > lookup_length), max(available_lengths))
    
    # Проверяем, есть ли цена для найденной комбинации ширины и длины
    if width_match in prices and length_match in prices[width_match]:
        price = prices[width_match][length_match]
        print(f"Найдена цена для размера {width_match}x{length_match}м: {price} евро")
        return price
    
    # Если цены нет, ищем минимальную цену среди всех подходящих размеров
    # (размеров, которые больше или равны заданным)
    min_price = None
    min_width = None
    min_length = None
    
    for width in available_widths:
        if width >= lookup_width:  # Используем lookup_width вместо width_m
            for length in available_lengths:
                if length >= lookup_length:  # Используем lookup_length вместо length_m
                    if width in prices and length in prices[width]:
                        price = prices[width][length]
                        if min_price is None or price < min_price:
                            min_price = price
                            min_width = width
                            min_length = length
    
    if min_price is None:
        # Если не нашли ни одной подходящей цены, это ошибка
        raise ValueError(f"Не удалось найти цену для перголы {pergola_type} с размерами {width_m}x{length_m}м")
    
    print(f"Найдена ближайшая цена для размера {min_width}x{min_length}м: {min_price} евро")
    return min_price

def needs_additional_columns(pergola_type, lamella_size, length_m):
    """
    Проверяет, нужны ли дополнительные колонны
    
    Args:
        pergola_type (str): Тип перголы
        lamella_size (str): Размер ламели
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужны дополнительные колонны
    """
    threshold = ADDITIONAL_COLUMNS_RULES.get(pergola_type, {}).get(lamella_size)
    if threshold is None:
        return False
    
    return length_m > threshold

def calculate_gutter_insert_price(length_m, modules):
    """
    Рассчитывает стоимость усилителя лотка по формуле:
    Стоимость = цена за метр * длина выноса * количество лотков
    
    В перголах с 1 модулем - 2 лотка
    В перголах с 2 модулями - 3 лотка
    В перголах с 3 модулями - 4 лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
    
    Returns:
        tuple: (нужен ли усилитель, стоимость усилителя, количество лотков, общая длина лотков)
    """
    # Проверяем, нужен ли усилитель лотка (вынос > 6.5м)
    needs_insert = length_m > GUTTER_INSERT_THRESHOLD
    
    # Если не нужен усилитель, возвращаем нули
    if not needs_insert:
        return (False, 0, 0, 0)
    
    # Определяем количество лотков в зависимости от модулей
    gutters_count = 0
    if modules == 1:
        gutters_count = 2
    elif modules == 2:
        gutters_count = 3
    elif modules == 3:
        gutters_count = 4
    else:
        gutters_count = modules + 1  # По умолчанию - на 1 больше чем модулей
    
    # Общая длина лотков = вынос * количество лотков
    total_gutter_length = length_m * gutters_count
    
    # Общая стоимость = цена за метр * общая длина
    total_price = GUTTER_INSERT_PRICE_PER_METER * total_gutter_length
    
    return (True, total_price, gutters_count, total_gutter_length)


def needs_gutter_insert(length_m):
    """
    Проверяет, нужен ли усилитель лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужен усилитель лотка
    """
    return length_m > GUTTER_INSERT_THRESHOLD

def get_drive_price(pergola_type, width_m, length_m, modules):
    """
    Определяет тип и стоимость привода для перголы
    
    Args:
        pergola_type (str): Тип перголы
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        tuple: (название привода, цена привода, нужен ли танем-привод)
    """
    if pergola_type == "B500NEW":
        rules = BANSBACH_DRIVE_RULES.get(modules, [])
        # Специальный случай для размера 3x8 (нужен Tandem)
        if abs(width_m - 3.0) < 0.01 and abs(length_m - 8.0) < 0.01:
            return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
            
        # Проверяем правила
        for rule in rules:
            # При большом выносе (> 6м) всегда нужен Tandem, даже если ширина небольшая
            if length_m > 6.0:
                return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
            
            if width_m > rule["width"] and length_m > rule["length"]:
                if rule["tandem"]:
                    return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
                else:
                    return "Bansbach Т1, Germany", DRIVE_PRICES["B500NEW"]["standard"], False
        
        # По умолчанию - стандартный привод
        return "Bansbach Т1, Germany", DRIVE_PRICES["B500NEW"]["standard"], False
    
    elif pergola_type == "B700NEW":
        rules = SOMFY_DRIVE_RULES.get(modules, [])
        for rule in rules:
            # Для 1 модуля: проверяем, что ширина <= указанной, для других модулей: ширина > указанной
            width_check = width_m <= rule["width"] if modules == 1 else width_m > rule["width"]
            
            if width_check and length_m > rule["length"]:
                if rule["tandem"]:
                    return "Somfy M2 TANDEM", DRIVE_PRICES["B700NEW"]["tandem"], True
                else:
                    return "Somfy M1", DRIVE_PRICES["B700NEW"]["standard"], False
        
        # По умолчанию - стандартный привод
        return "Somfy M1", DRIVE_PRICES["B700NEW"]["standard"], False
    
    return "", 0, False

def get_remote_control(devices_count):
    """
    Определяет тип и стоимость пульта управления
    
    Args:
        devices_count (int): Количество устройств для управления
        
    Returns:
        tuple: (название пульта, цена пульта)
    """
    if devices_count <= 1:
        return "Simu 1K", REMOTE_CONTROL_TYPES[1]["price"]
    elif devices_count <= 5:
        return "Simu 5K", REMOTE_CONTROL_TYPES[5]["price"]
    else:
        return "Simu 15K", REMOTE_CONTROL_TYPES[15]["price"]

def perform_calculation(dimensions, options):
    """Выполнить расчет стоимости перголы"""
    try:
        # Извлекаем данные из ввода пользователя
        width_m = float(dimensions.get("width", 0))
        length_m = float(dimensions.get("length", 0))
        pergola_type = options.get("pergola_type", "")
        lamella_type = options.get("lamella_type", "")
        
        # Определяем размер ламели для проверки максимальных размеров
        check_lamella_size = "PIR" if "PIR" in lamella_type else ("200" if "200" in lamella_type else "250")
        
        # Формируем ключ для MAX_DIMENSIONS с учётом типа перголы и размера ламелей
        if pergola_type == "B600":
            dimensions_check_key = pergola_type
        else:
            dimensions_check_key = f"{pergola_type}_{check_lamella_size}"
        
        # Проверяем, не превышает ли размер максимально допустимый для данного типа перголы
        if dimensions_check_key in MAX_DIMENSIONS:
            max_width = MAX_DIMENSIONS[dimensions_check_key]["width"]
            max_length = MAX_DIMENSIONS[dimensions_check_key]["length"]
            
            if width_m > max_width:
                raise ValueError(f"Ширина перголы ({width_m} м) превышает максимально допустимую ({max_width} м) для типа {pergola_type}")
            
            if length_m > max_length:
                raise ValueError(f"Вынос перголы ({length_m} м) превышает максимально допустимый ({max_length} м) для типа {pergola_type}")
        modules = get_modules_by_dimensions(width_m, length_m, pergola_type)  # Автоматически определяем модули по размерам
        lighting_options = options.get("lighting", [])
        installation = options.get("installation", False)  # Опция установки
        
        # Определяем размер ламели в миллиметрах
        lamella_size = "PIR" if "PIR" in lamella_type else ("200" if "200" in lamella_type else "250")
        
        # Корректируем размер выноса в соответствии с размером ламелей для B500NEW и B700NEW
        if pergola_type in ["B500NEW", "B700NEW"]:
            lamella_size_mm = 200 if lamella_size == "200" else 250
            original_length = length_m
            length_m = adjust_length_for_lamella_size(length_m, lamella_size_mm)
            # Рассчитываем количество ламелей
            lamellas_count = math.ceil(length_m / (lamella_size_mm / 1000))
        
        # Определяем базовую стоимость перголы из прайс-листа
        base_price = get_base_price(pergola_type, lamella_size, width_m, length_m)
        
        # Инициализируем результаты расчета
        results = {
            "dimensions": {
                "width": width_m,
                "length": length_m,
                "modules": modules
            },
            "options": {
                "pergola_type": pergola_type,
                "lamella_type": lamella_type,
                "lighting": lighting_options,
                "installation": installation
            },
            "base_price": base_price,
            "items": [],
            "total_price": base_price
        }
        
        # Определяем размер ламели для отображения
        lamella_display = "250 мм" if lamella_size == "250" else "200 мм" if lamella_size == "200" else "PIR"
        
        # Добавляем стоимость самой перголы в список позиций
        # Это исправляет проблему с отсутствием стоимости перголы в PDF
        pergola_name = f"Пергола серии {pergola_type} - с поворотными ламелями {width_m:.2f}×{length_m:.2f} м. Ламели {lamella_display} (стандарт), Количество модулей - {modules}"
        
        # Для B500 и B700 добавляем количество ламелей
        if pergola_type in ["B500NEW", "B700NEW"]:
            # Расчет количества ламелей
            lamella_size_mm = 200 if lamella_size == "200" else 250
            lamellas_count = int(length_m * 1000 / lamella_size_mm)
            pergola_name = f"Пергола серии {pergola_type} - с поворотными ламелями {width_m:.2f}×{length_m:.2f} м. Ламели {lamella_display} (стандарт), Количество ламелей - {lamellas_count} шт. ({modules} модуля)"
        
        # Добавляем перголу в список товаров
        results["items"].append({
            "name": pergola_name,
            "price": base_price
        })
        
        # Проверяем, нужны ли дополнительные колонны
        need_columns = needs_additional_columns(pergola_type, lamella_size, length_m)
        if need_columns:
            columns_price = COLUMNS_PRICES.get(modules, 0)
            results["additional_columns"] = {
                "required": True,
                "count": modules + 1,  # Количество колонн зависит от модулей
                "price": columns_price
            }
            results["items"].append({
                "name": f"Дополнительные колонны ({modules + 1} шт.)",
                "price": columns_price
            })
            results["total_price"] += columns_price
        else:
            results["additional_columns"] = {"required": False}
        
        # Проверяем, нужен ли усилитель лотка и рассчитываем его стоимость
        gutter_needed, gutter_price, gutters_count, total_gutter_length = calculate_gutter_insert_price(length_m, modules)
        if gutter_needed:
            results["gutter_insert"] = {
                "required": True,
                "gutters_count": gutters_count,
                "length": total_gutter_length,
                "price_per_meter": GUTTER_INSERT_PRICE_PER_METER,
                "total_price": gutter_price
            }
            results["items"].append({
                "name": f"Усилитель лотка ({gutters_count} лотка, {total_gutter_length:.2f} м)",
                "price": gutter_price
            })
            results["total_price"] += gutter_price
        else:
            results["gutter_insert"] = {"required": False}
        
        # Определяем тип и стоимость привода
        if pergola_type in ["B500NEW", "B700NEW"]:
            drive_name, drive_price, is_tandem = get_drive_price(pergola_type, width_m, length_m, modules)
            drive_count = modules  # Один привод на каждый модуль
            total_drive_price = drive_price * drive_count
            
            results["drive"] = {
                "name": drive_name,
                "count": drive_count,
                "is_tandem": is_tandem,
                "price": drive_price,
                "total_price": total_drive_price
            }
            
            results["items"].append({
                "name": f"Привод {drive_name} (для {drive_count} {get_plural_form(drive_count, 'модуль', 'модуля', 'модулей')})",
                "price": total_drive_price
            })
            
            results["total_price"] += total_drive_price
            
            # Количество устройств для пульта ДУ (привод + освещение)
            devices_count = drive_count
            if "white_led" in lighting_options or "rgb_led" in lighting_options:
                # Добавляем блоки управления освещением - по одному на каждый тип подсветки
                # Для одной перголы независимо от количества модулей используется
                # один блок управления для каждого типа подсветки
                led_controllers = 0
                if "white_led" in lighting_options:
                    led_controllers += 1
                if "rgb_led" in lighting_options:
                    led_controllers += 1
                devices_count += led_controllers
            
            # Определяем тип и стоимость пульта ДУ
            remote_name, remote_price = get_remote_control(devices_count)
            
            results["remote_control"] = {
                "name": remote_name,
                "devices_count": devices_count,
                "price": remote_price
            }
            
            results["items"].append({
                "name": f"Пульт ДУ {remote_name} ({devices_count} {get_plural_form(devices_count, 'канал', 'канала', 'каналов')})",
                "price": remote_price
            })
            
            results["total_price"] += remote_price
        
        # Расчет стоимости освещения
        has_lighting = "white_led" in lighting_options or "rgb_led" in lighting_options
        if has_lighting:
            lighting_perimeter = calculate_lighting_perimeter(width_m, length_m, modules)
            
            lighting_cost = 0
            led_types = []
            
            # Блок управления освещением - 1 блок на каждый тип подсветки
            if has_lighting:
                # Для одной перголы независимо от количества модулей используется
                # один блок управления для каждого типа подсветки
                controllers_count = 0
                
                # Если есть белая подсветка - добавляем один блок управления
                if "white_led" in lighting_options:
                    controllers_count += 1
                
                # Если есть RGB подсветка - добавляем ещё один блок управления
                if "rgb_led" in lighting_options:
                    controllers_count += 1
                
                total_controller_price = LIGHTING_PRICES["controller"] * controllers_count
                lighting_cost += total_controller_price
                results["items"].append({
                    "name": f"Блок управления освещением Somfy RTS Dimmer ({controllers_count} шт.)",
                    "price": total_controller_price
                })
            
            # Белая светодиодная лента
            if "white_led" in lighting_options:
                white_led_cost = LIGHTING_PRICES["white_led"] * lighting_perimeter
                lighting_cost += white_led_cost
                led_types.append("белая")
                results["items"].append({
                    "name": f"Светодиодная лента белая ({lighting_perimeter:.2f} м)",
                    "price": white_led_cost
                })
            
            # RGB светодиодная лента
            if "rgb_led" in lighting_options:
                rgb_led_cost = LIGHTING_PRICES["rgb_led"] * lighting_perimeter
                lighting_cost += rgb_led_cost
                led_types.append("RGB")
                results["items"].append({
                    "name": f"Светодиодная лента RGB ({lighting_perimeter:.2f} м)",
                    "price": rgb_led_cost
                })
                
            # Для B600 добавляем пульт управления освещением
            if pergola_type == "B600":
                # Для B600 нужен отдельный пульт для освещения
                # Количество устройств = количество блоков освещения (по одному на каждый модуль)
                lighting_devices_count = controllers_count  
                remote_name, remote_price = get_remote_control(lighting_devices_count)
                
                results["lighting_remote"] = {
                    "name": remote_name,
                    "devices_count": lighting_devices_count,
                    "price": remote_price
                }
                
                results["items"].append({
                    "name": f"Пульт ДУ {remote_name} для освещения ({lighting_devices_count} {get_plural_form(lighting_devices_count, 'канал', 'канала', 'каналов')})",
                    "price": remote_price
                })
                
                lighting_cost += remote_price
            
            results["lighting"] = {
                "types": led_types,
                "perimeter": lighting_perimeter,
                "total_price": lighting_cost
            }
            
            results["total_price"] += lighting_cost
        
        # Добавляем информацию о спецификации (без цен)
        specification = []
        
        # Определяем тип ламелей и их количество
        lamella_info = ""
        if pergola_type in ["B500NEW", "B700NEW"]:
            lamella_info = LAMELLA_TYPES.get(lamella_type, lamella_type)
            lamellas_count_text = f", Количество ламелей - {lamellas_count} шт." if 'lamellas_count' in locals() else ""
        else:
            lamellas_count_text = ""
                
        # Основная пергола
        specification.append({
            "name": f"Пергола серии {PERGOLA_TYPES.get(pergola_type, pergola_type)} {width_m:.2f}×{length_m:.2f} м. {lamella_info}{lamellas_count_text}",
            "count": f"{modules} {get_plural_form(modules, 'модуль', 'модуля', 'модулей')}",
            "price": ""
        })
        
        # Дополнительные колонны и усилитель лотка
        if need_columns:
            specification.append({
                "name": "Дополнительные колонны",
                "count": f"{modules + 1} шт.",
                "price": ""
            })
        
        if gutter_needed:
            specification.append({
                "name": "Усилитель лотка",
                "count": f"{total_gutter_length:.2f} м ({gutters_count} {get_plural_form(gutters_count, 'лоток', 'лотка', 'лотков')})",
                "price": ""
            })
        
        # Привод
        if pergola_type in ["B500NEW", "B700NEW"]:
            drive_name, _, _ = get_drive_price(pergola_type, width_m, length_m, modules)
            specification.append({
                "name": f"Привод {drive_name}",
                "count": f"{modules} шт.",
                "price": ""
            })
            
            # Пульт ДУ
            remote_name, _ = get_remote_control(devices_count)
            specification.append({
                "name": f"Пульт ДУ {remote_name}",
                "count": "1 шт.",
                "price": ""
            })
        
        # Освещение
        if has_lighting:
            # Определяем количество блоков управления освещением (по одному на каждый тип подсветки)
            led_controllers = 0
            if "white_led" in lighting_options:
                led_controllers += 1
            if "rgb_led" in lighting_options:
                led_controllers += 1
                
            # Добавляем блок управления освещением - по 1 блоку на каждый тип подсветки
            specification.append({
                "name": "Блок управления освещением Somfy RTS Dimmer",
                "count": f"{led_controllers} шт.",
                "price": ""
            })
            
            # Увеличиваем счетчик устройств для определения типа пульта
            lighting_devices_count = led_controllers  # По 1 блоку управления на каждый тип подсветки
            
            if "white_led" in lighting_options:
                specification.append({
                    "name": "Светодиодная лента белая",
                    "count": f"{lighting_perimeter:.2f} м",
                    "price": ""
                })
            
            if "rgb_led" in lighting_options:
                specification.append({
                    "name": "Светодиодная лента RGB",
                    "count": f"{lighting_perimeter:.2f} м",
                    "price": ""
                })
            
            # Добавляем пульт для управления освещением
            # Если уже есть пульт от привода перголы (B500/B700), выбираем пульт с большим числом каналов
            # Если перголы B600 без привода, добавляем пульт для освещения
            if pergola_type in ["B500NEW", "B700NEW"]:
                # Обновляем devices_count для выбора пульта с большим числом каналов
                devices_count += lighting_devices_count
                
                # Обновляем информацию о пульте в спецификации
                for i, item in enumerate(specification):
                    if "Пульт ДУ" in item["name"]:
                        remote_name, _ = get_remote_control(devices_count)
                        specification[i] = {
                            "name": f"Пульт ДУ {remote_name}",
                            "count": "1 шт.",
                            "price": ""
                        }
                        break
            else:
                # Для B600 добавляем отдельный пульт для освещения
                remote_name, _ = get_remote_control(lighting_devices_count)
                specification.append({
                    "name": f"Пульт ДУ {remote_name} для освещения",
                    "count": f"1 шт. ({lighting_devices_count} {get_plural_form(lighting_devices_count, 'канал', 'канала', 'каналов')})",
                    "price": ""
                })
        
        results["specification"] = specification
        
        # Базовая стоимость (без наценок)
        base_total_price = results["total_price"]
        
        # Добавляем наценку за доставку из модуля настроек
        delivery_markup_percent = pricing_settings.get_delivery_markup_percent()
        delivery_price = round(base_total_price * delivery_markup_percent / 100, 2)
        results["delivery"] = {
            "percentage": delivery_markup_percent,
            "price": delivery_price
        }
        results["items"].append({
            "name": "Доставка",
            "price": delivery_price
        })
        results["total_price"] += delivery_price
        
        # Добавляем наценку за установку из модуля настроек, если выбрана опция
        if installation:
            installation_markup_percent = pricing_settings.get_installation_markup_percent()
            installation_price = round(base_total_price * installation_markup_percent / 100, 2)
            results["installation"] = {
                "selected": True,
                "percentage": installation_markup_percent,
                "price": installation_price
            }
            results["items"].append({
                "name": "Установка",
                "price": installation_price
            })
            results["total_price"] += installation_price
        else:
            results["installation"] = {
                "selected": False,
                "price": 0
            }
        
        # Обновляем итоговую стоимость в спецификации
        specification.append({
            "name": "Доставка",
            "count": "1",
            "price": ""
        })
        
        if installation:
            specification.append({
                "name": "Установка",
                "count": "1",
                "price": ""
            })
        
        # Округляем общую стоимость
        results["total_price"] = round(results["total_price"], 2)
        
        # Техническая информация для вывода в результатах
        results["debug"] = {
            "length_corrected": length_m,
            "width": width_m,
            "modules": modules,
            "need_columns": need_columns,
            "need_gutter": gutter_needed,
            "pergola_type": pergola_type,
            "lamella_type": lamella_type,
            "lamella_size": lamella_size,
            "lamellas_count": lamellas_count if 'lamellas_count' in locals() else 0,
            "installation": installation
        }
        
        return results
    
    except Exception as e:
        error_msg = f"Ошибка при расчете: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

def get_modules_from_price_data(width, length, pergola_type, lamella_size):
    """
    Определяет количество модулей на основе данных из прайс-листа.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        int: Количество модулей или None, если не удалось определить
    """
    # Определяем соответствие типов пергол и имен файлов
    file_mapping = {
        ("B500NEW", "200"): ["attached_assets/Price_B500-20.csv", "attached_assets/Прайс_В500-20.csv"],
        ("B500NEW", "250"): ["attached_assets/Price_B500-25.csv", "attached_assets/Прайс_В500-25.csv"],
        ("B700NEW", "200"): ["attached_assets/Price_B700-20.csv", "attached_assets/Прайс_B700-20.csv"],
        ("B700NEW", "250"): ["attached_assets/Price_B700-25.csv", "attached_assets/Прайс_B700-25.csv"],
        ("B600", "PIR"): ["attached_assets/Price_B600_PIR.csv", "attached_assets/Прайс_В600_PIR.csv"]
    }
    
    key = (pergola_type, lamella_size)
    if key not in file_mapping:
        print(f"Ошибка: Комбинация {pergola_type} и {lamella_size} не найдена в маппинге файлов")
        return None
    
    # Получаем пути к файлам прайса
    file_paths = file_mapping[key]
    
    # Проверяем, существует ли хотя бы один из файлов
    existing_file_path = None
    for path in file_paths:
        if os.path.exists(path):
            existing_file_path = path
            break
    
    if not existing_file_path:
        print(f"Ошибка: Файлы прайса {file_paths} не найдены")
        return None
    
    # Используем найденный файл
    file_path = existing_file_path
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Определяем разделитель CSV (точка с запятой или запятая)
            first_line = file.readline().strip()
            if ';' in first_line:
                delimiter = ';'
            else:
                delimiter = ','
            
            # Перематываем файл в начало
            file.seek(0)
            
            reader = csv.reader(file, delimiter=delimiter)
            
            # Читаем первую строку (с информацией о модулях)
            first_row = next(reader)
            if "модуль" not in ' '.join(first_row).lower():
                print("Ошибка: Не найдена информация о модулях в первой строке прайса")
                return None
            
            # Читаем вторую строку (с размерами)
            width_row = next(reader)
            
            # Найдем ближайшие значения ширины и длины
            closest_width_idx = None
            closest_width_diff = float('inf')
            
            # Пропускаем первую колонку (она содержит описание)
            for i, w in enumerate(width_row[1:], 1):
                try:
                    w_value = float(w.replace(',', '.'))
                    diff = abs(w_value - width)
                    if diff < closest_width_diff:
                        closest_width_diff = diff
                        closest_width_idx = i
                except (ValueError, TypeError):
                    continue
            
            if closest_width_idx is None:
                print(f"Ошибка: Не удалось найти ближайшую ширину к {width} в прайсе")
                return None
            
            closest_length_row = None
            closest_length_diff = float('inf')
            
            # Перебираем строки с длинами
            for row in reader:
                try:
                    length_value = float(row[0].replace(',', '.'))
                    diff = abs(length_value - length)
                    if diff < closest_length_diff:
                        closest_length_diff = diff
                        closest_length_row = row
                except (ValueError, TypeError, IndexError):
                    continue
            
            if closest_length_row is None:
                print(f"Ошибка: Не удалось найти ближайший вынос к {length} в прайсе")
                return None
            
            # Получаем информацию о модулях из первой строки для найденной ячейки
            if closest_width_idx < len(first_row):
                module_info = first_row[closest_width_idx]
                if "1 модуль" in module_info:
                    return 1
                elif "2 модуля" in module_info:
                    return 2
                elif "3 модуля" in module_info:
                    return 3
                else:
                    # Пытаемся извлечь число модулей из строки
                    import re
                    match = re.search(r'(\d+)\s*модул', module_info)
                    if match:
                        return int(match.group(1))
            
            print(f"Предупреждение: Не удалось определить количество модулей из прайса для {width}x{length}")
            return None
            
    except Exception as e:
        print(f"Ошибка при чтении прайса для определения модулей: {str(e)}")
        return None

def get_modules_by_dimensions(width, length, pergola_type=None):
    """
    Определяет количество модулей в зависимости от размеров перголы и ее типа.
    Сначала пытается получить информацию из прайс-листа, затем использует логические правила.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str, optional): Тип перголы
        
    Returns:
        int: Количество модулей
    """
    # Если указан тип перголы, пытаемся определить по прайсу
    if pergola_type:
        # Определяем размер ламели в зависимости от типа перголы
        if pergola_type == "B600":
            lamella_size = "PIR"
        else:
            # По умолчанию используем стандартный размер 250мм
            lamella_size = "250"
        
        # Пытаемся получить количество модулей из прайса
        modules_from_price = get_modules_from_price_data(width, length, pergola_type, lamella_size)
        if modules_from_price is not None:
            return modules_from_price
    
    # Если не удалось определить по прайсу, используем логические правила
    
    # Специальный случай для размера 3x8
    if abs(width - 3.0) < 0.01 and abs(length - 8.0) < 0.01:
        return 1  # Размер 3x8 всегда имеет 1 модуль (согласно прайсу)
    
    # Стандартные правила по ширине и длине
    if width <= 4.5:
        # Для ширины до 4.5м обычно 1 модуль, но при большом выносе может быть больше
        return 1 if length <= 6.0 else 2
    elif width <= 9.0:
        return 2  # Для ширины 5-9м - 2 модуля
    else:
        return 3  # Для ширины 9.5м и более - 3 модуля
        
def get_modules_by_width(width):
    """
    Устаревшая функция, оставлена для совместимости.
    Используйте get_modules_by_dimensions вместо нее.
    
    Args:
        width (float): Ширина перголы в метрах
        
    Returns:
        int: Количество модулей
    """
    return get_modules_by_dimensions(width, 4.0)  # Используем стандартный вынос 4.0

def _dimension_input_html(label, field_id, value, min_val, max_val, step=0.5):
    """Генерирует HTML для быстрого поля ввода размера с мгновенными +/- кнопками."""
    return f'''
    <div style="margin-bottom:8px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
        <span style="font-size:14px;font-weight:500;color:#333;">{label}</span>
        <span style="font-size:11px;color:#888;">({min_val} — {max_val} м)</span>
      </div>
      <div style="display:flex;align-items:center;gap:0;border:1.5px solid #d0d5dd;border-radius:8px;overflow:hidden;height:48px;background:#fff;">
        <button id="btn_minus_{field_id}" onclick="dimChange('{field_id}',-{step},{min_val},{max_val})"
          style="width:52px;height:100%;border:none;background:#f8f9fa;cursor:pointer;font-size:22px;font-weight:600;color:#0066cc;
                 display:flex;align-items:center;justify-content:center;user-select:none;transition:background 0.1s;"
          onmousedown="this.style.background='#e0e7ff'" onmouseup="this.style.background='#f8f9fa'"
          onmouseleave="this.style.background='#f8f9fa'">−</button>
        <input id="inp_{field_id}" type="text" value="{value:.2f}"
          style="flex:1;height:100%;border:none;border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0;
                 text-align:center;font-size:18px;font-weight:500;color:#1a1a1a;outline:none;background:#fff;
                 -moz-appearance:textfield;padding:0;"
          onchange="dimManual('{field_id}',this.value,{min_val},{max_val})"
          onkeydown="if(event.key==='Enter'){{event.preventDefault();dimManual('{field_id}',this.value,{min_val},{max_val})}}"
          inputmode="decimal" />
        <button id="btn_plus_{field_id}" onclick="dimChange('{field_id}',{step},{min_val},{max_val})"
          style="width:52px;height:100%;border:none;background:#f8f9fa;cursor:pointer;font-size:22px;font-weight:600;color:#0066cc;
                 display:flex;align-items:center;justify-content:center;user-select:none;transition:background 0.1s;"
          onmousedown="this.style.background='#e0e7ff'" onmouseup="this.style.background='#f8f9fa'"
          onmouseleave="this.style.background='#f8f9fa'">+</button>
      </div>
    </div>'''


def _dimensions_js():
    """JavaScript для мгновенного управления размерами с debounced синхронизацией."""
    return '''
    <script>
    var dimTimers = {};
    var dimValues = {};
    
    function dimChange(id, delta, mn, mx) {
      var inp = document.getElementById('inp_' + id);
      if (!inp) return;
      var cur = parseFloat(inp.value.replace(',', '.')) || 0;
      var nv = Math.round((cur + delta) * 100) / 100;
      if (nv < mn) nv = mn;
      if (nv > mx) nv = mx;
      inp.value = nv.toFixed(2);
      dimValues[id] = nv;
      dimScheduleSync();
    }
    
    function dimManual(id, rawVal, mn, mx) {
      var v = parseFloat(rawVal.replace(',', '.'));
      if (isNaN(v)) return;
      v = Math.round(v * 100) / 100;
      if (v < mn) v = mn;
      if (v > mx) v = mx;
      var inp = document.getElementById('inp_' + id);
      inp.value = v.toFixed(2);
      dimValues[id] = v;
      dimScheduleSync();
    }
    
    function dimScheduleSync() {
      if (dimTimers._sync) clearTimeout(dimTimers._sync);
      dimTimers._sync = setTimeout(function() {
        dimDoSync();
      }, 800);
    }
    
    function dimDoSync() {
      var w = dimValues['width'];
      var l = dimValues['length'];
      if (w === undefined && l === undefined) return;
      
      var doc = window.parent.document;
      var inputs = doc.querySelectorAll('input[type="number"]');
      
      inputs.forEach(function(el) {
        var label = '';
        var container = el.closest('[data-testid="stNumberInput"]');
        if (container) {
          var lbl = container.querySelector('label');
          if (lbl) label = lbl.textContent.toLowerCase();
        }
        
        if (w !== undefined && label.indexOf('ширина') >= 0) {
          setNativeValue(el, w);
        }
        if (l !== undefined && label.indexOf('вынос') >= 0) {
          setNativeValue(el, l);
        }
      });
      
      dimValues = {};
    }
    
    function setNativeValue(el, val) {
      var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.parent.HTMLInputElement.prototype, 'value').set;
      nativeInputValueSetter.call(el, val);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    </script>'''


def render_dimensions_form():
    """
    Отображает форму для ввода размеров перголы.
    Использует кастомный HTML/JS для мгновенного отклика кнопок +/-
    и скрытые st.number_input для синхронизации с Streamlit.
    """
    from streamlit.components.v1 import html
    
    st.markdown("<h2 class='section-header' style='text-align: center; margin-bottom: 5px;'>Размеры перголы</h2>", unsafe_allow_html=True)
    
    current_pergola_type = st.session_state.get("pergola_type")
    current_lamella_size = st.session_state.get("lamella_size", "250")
    
    if current_pergola_type == "B600":
        dimensions_key = current_pergola_type
    else:
        dimensions_key = f"{current_pergola_type}_{current_lamella_size}"
    
    if dimensions_key in MAX_DIMENSIONS:
        max_width = MAX_DIMENSIONS[dimensions_key]["width"]
        max_length = MAX_DIMENSIONS[dimensions_key]["length"]
    else:
        max_width = 13.5
        max_length = 8.0
    
    min_width = 2.0
    min_length = 2.0
    
    width_key = "dim_width"
    length_key = "dim_length"
    
    combined_key = f"{current_pergola_type}_{current_lamella_size}"
    if st.session_state.get('_prev_dim_key') != combined_key:
        st.session_state['_prev_dim_key'] = combined_key
        st.session_state[width_key] = 3.0
        st.session_state[length_key] = 4.0
    
    cur_w = st.session_state.get(width_key, 3.0)
    cur_l = st.session_state.get(length_key, 4.0)
    cur_w = min(max(cur_w, min_width), max_width)
    cur_l = min(max(cur_l, min_length), max_length)
    
    w_html = _dimension_input_html("Ширина (м)", "width", cur_w, min_width, max_width)
    l_html = _dimension_input_html("Вынос (м)", "length", cur_l, min_length, max_length)
    js = _dimensions_js()
    
    combined_html = f'''
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:8px 0;">
      <div>{w_html}</div>
      <div>{l_html}</div>
    </div>
    {js}
    '''
    combined_html += '''
    <script>
    (function hideSync() {
        var doc = window.parent.document;
        if (!doc.getElementById('dim-sync-style')) {
            var s = doc.createElement('style');
            s.id = 'dim-sync-style';
            s.textContent = '.dim-sync-hide { height:0 !important; overflow:hidden !important; margin:0 !important; padding:0 !important; opacity:0 !important; position:absolute !important; pointer-events:none !important; }';
            doc.head.appendChild(s);
        }
        var inputs = doc.querySelectorAll('input[type="number"]');
        var found = 0;
        inputs.forEach(function(el) {
            var c = el.closest('[data-testid="stNumberInput"]');
            if (!c) return;
            var lbl = c.querySelector('label');
            if (!lbl) return;
            var t = lbl.textContent.toLowerCase();
            if (t.indexOf('ширина') >= 0 || t.indexOf('вынос') >= 0) {
                var cols = c.closest('[data-testid="stHorizontalBlock"]');
                if (cols) { cols.classList.add('dim-sync-hide'); found++; }
            }
        });
        if (found < 1) setTimeout(hideSync, 300);
    })();
    </script>
    '''
    html(combined_html, height=110)
    
    c1, c2 = st.columns(2)
    with c1:
        width = st.number_input("Ширина (м)", min_value=min_width, max_value=max_width,
                                 value=cur_w, step=0.5, format="%.2f", key=width_key,
                                 label_visibility="collapsed")
    with c2:
        length = st.number_input("Вынос (м)", min_value=min_length, max_value=max_length,
                                  value=cur_l, step=0.5, format="%.2f", key=length_key,
                                  label_visibility="collapsed")
    
    modules = get_modules_by_dimensions(width, length)
    
    if modules > 1:
        st.markdown(f"""<div style="padding: 5px 10px; background-color: #e6f3ff; border-radius: 3px; font-size: 0.85rem; margin: 2px 0;">
        При размере {width:.2f}×{length:.2f} м будет автоматически использовано {modules} {get_plural_form(modules, 'модуль', 'модуля', 'модулей')}
        </div>""", unsafe_allow_html=True)
    
    return {
        "width": width,
        "length": length,
        "modules": modules
    }

def render_pergola_type_form():
    """
    Отображает форму для выбора типа перголы
    
    Returns:
        str: Выбранный тип перголы
    """
    st.markdown("<h2 class='section-header' style='text-align: center; margin-bottom: 5px;'>Выберите тип перголы</h2>", unsafe_allow_html=True)
    
    # Стили для всех заголовков полей
    st.markdown("""
    <style>
    /* Стиль для заголовков всех полей ввода */
    .stRadio > label, div[data-testid="stRadio"] label {
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Тип перголы - заголовок в том же стиле, что и для освещения
    st.write("Выберите тип перголы")
    
    pergola_type = st.radio(
        "",  # Пустая строка, так как заголовок добавляем отдельно
        options=list(PERGOLA_TYPES.keys()),
        format_func=lambda x: PERGOLA_TYPES.get(x, x),
        horizontal=True,
        label_visibility="collapsed",  # Скрываем стандартный заголовок
        on_change=lambda: None,
        key="pergola_type"  # Ключ для session_state, чтобы форма размеров могла получить текущий тип
    )
    
    # Добавляем визуализацию выбранного типа перголы
    with st.container():
        st.markdown(
            """
            <style>
            .pergola-image-container {
                margin-top: 15px;
                margin-bottom: 15px;
                text-align: center;
                display: flex;
                justify-content: center;
            }
            .pergola-image {
                max-width: 100%;
                max-height: 300px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .pergola-image-caption {
                font-size: 0.9rem;
                text-align: center;
                margin-top: 8px;
                color: #555;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        # Отображаем два изображения рядом для выбранного типа перголы
        left_image_path = None
        right_image_path = None
        left_caption = ""
        right_caption = ""
        
        # Левое изображение - общий вид перголы
        if pergola_type == "B500NEW":
            left_image_path = "attached_assets/b500_rotation.png"
            left_caption = "Пергола В500 с поворотными ламелями"
        elif pergola_type == "B700NEW":
            left_image_path = "attached_assets/b700_sliding.png"
            left_caption = "Пергола В700 с поворотно-сдвижными ламелями"
        elif pergola_type == "B600":
            left_image_path = "attached_assets/b600_sandwich.png"
            left_caption = "Пергола В600 со стационарными PIR панелями"
        
        # Правое изображение - детальное изображение (добавляется программно в других частях кода)
        # Для B600 не будем показывать правое изображение
        if pergola_type == "B500NEW":
            # Пробуем сначала английское название файла, а затем кириллическое - для совместимости
            # Используем изображение линейного привода с красным элементом
            if os.path.exists("attached_assets/linear_drive_b500.png"):
                right_image_path = "attached_assets/linear_drive_b500.png"
            elif os.path.exists("attached_assets/Линейный привод-2.png"):
                right_image_path = "attached_assets/Линейный привод-2.png"
            else:
                # Пробуем найти любое подходящее изображение привода
                right_image_path = "attached_assets/Линейный привод.png" if os.path.exists("attached_assets/Линейный привод.png") else None
            
            right_caption = "Линейный привод для перголы В500"
        elif pergola_type == "B700NEW":
            # Пробуем сначала английское название файла в формате jpg, затем png, и наконец кириллическое название
            # Используем новое изображение системы Somfy для B700
            if os.path.exists("attached_assets/somfy_pergola_b700.jpg"):
                right_image_path = "attached_assets/somfy_pergola_b700.jpg"
            elif os.path.exists("attached_assets/Somfy Pergola.jpg"):
                right_image_path = "attached_assets/Somfy Pergola.jpg"
            elif os.path.exists("attached_assets/somfy_pergola_b700.png"):
                right_image_path = "attached_assets/somfy_pergola_b700.png"
            elif os.path.exists("attached_assets/Somfy Pergola.png"):
                right_image_path = "attached_assets/Somfy Pergola.png"
            else:
                # Пробуем найти любое подходящее изображение для B700
                right_image_path = "attached_assets/Lin gate.jpg" if os.path.exists("attached_assets/Lin gate.jpg") else None
            
            right_caption = "Система уплотнения ламелей перголы В700"
            
        # Создаем контейнер с изображениями в две колонки с использованием оптимизированного кэша
        # Получаем оптимизированные HTML-теги для изображений перголы из кэша
        left_image_html, right_image_html = get_optimized_pergola_images(pergola_type)
        
        if left_image_html:
            # Добавляем стили для изображений и контейнеров
            st.markdown("""
            <style>
            .image-header {
                text-align: center;
                font-weight: 500;
                color: #1E88E5;
                margin-bottom: 10px;
                font-size: 1rem;
            }
            .pergola-image-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto;
                width: 100%;
                padding: 5px;
            }
            .pergola-image {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            .pergola-image:hover {
                transform: scale(1.02);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Диагностический вывод убран
            
            # Создаем колонки на основе наличия второго изображения
            cols = st.columns([1, 1] if right_image_html else [1])
            
            # Левая колонка с основным изображением (всегда доступна)
            with cols[0]:
                # Отображаем основное изображение перголы через HTML
                st.markdown(
                    f'<div class="pergola-image-container">{left_image_html}</div>',
                    unsafe_allow_html=True
                )
            
            # Правая колонка с дополнительным изображением (если есть)
            if right_image_html and len(cols) > 1:
                with cols[1]:
                    # Отображаем дополнительное изображение перголы через HTML
                    st.markdown(
                        f'<div class="pergola-image-container">{right_image_html}</div>',
                        unsafe_allow_html=True
                    )
    
    # Добавляем вертикальный отступ после изображений
    st.markdown("""
    <div style="height: 30px;"></div>
    """, unsafe_allow_html=True)
    
    return pergola_type

def render_lamella_type_form():
    """
    Отображает форму для выбора типа ламелей (зависит от выбранного типа перголы)
    
    Returns:
        str: Выбранный тип ламелей
    """
    # Получаем тип перголы из session_state
    pergola_type = st.session_state.get("pergola_type", "B500NEW")
    
    st.markdown("<h2 class='section-header' style='text-align: center; margin-bottom: 5px;'>Выберите тип ламелей</h2>", unsafe_allow_html=True)
    
    # Тип ламелей - зависит от выбранного типа перголы
    lamella_options = []
    if pergola_type == "B500NEW":
        lamella_options = ["B500-25NEW", "B500-20NEW"]  # Стандартные 250 мм первыми
    elif pergola_type == "B700NEW":
        lamella_options = ["B700-25NEW", "B700-20NEW"]  # Стандартные 250 мм первыми
    elif pergola_type == "B600":
        lamella_options = ["B600-PIR"]
    
    # Получаем размер ламелей из типа для сохранения в session_state
    def get_lamella_size(lamella_type):
        if "20" in lamella_type:
            return "200"
        elif "25" in lamella_type:
            return "250"
        elif "PIR" in lamella_type:
            return "PIR"
        return "250"  # По умолчанию 250 мм
    
    lamella_type = st.radio(
        "",  # Пустая строка, так как заголовок добавляем отдельно
        options=lamella_options,
        format_func=lambda x: LAMELLA_TYPES.get(x, x),
        horizontal=True,
        label_visibility="collapsed",  # Скрываем стандартный заголовок
        key="lamella_type"
    )
    
    # Сохраняем размер ламелей в session_state для использования в render_dimensions_form
    st.session_state["lamella_size"] = get_lamella_size(lamella_type)
    
    return lamella_type

def render_additional_options_form():
    """
    Отображает форму для выбора дополнительных опций перголы
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    
    # Глобальный CSS для заголовков разделов и выравнивания всех элементов формы
    st.markdown("""
    <style>
    /* Отступы для заголовков всех секций формы */
    div.stMarkdown p {
        font-weight: 500 !important;
        margin-bottom: 10px !important;
    }
    
    /* Отступы для радиокнопок и чекбоксов */
    div.stRadio > div {
        margin-bottom: 10px !important;
    }
    
    /* Принудительный стиль для всех чекбоксов */
    div.stCheckbox > div {
        margin-left: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Прямой подход к созданию чекбоксов для освещения с фиксированными отступами
    st.write("Освещение")
    
    # Добавляем CSS для установки точных отступов как у radio buttons
    st.markdown("""
    <style>
    /* Строгое задание отступов для чекбоксов освещения */
    div[data-testid="stVerticalBlock"] > div:has(label:contains("LED-подсветка")) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    div[data-testid="stVerticalBlock"] > div:has(label:contains("RGB-подсветка")) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }

    /* Убираем отступы у родительского контейнера чекбоксов */
    div.stCheckbox {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем чекбоксы напрямую
    lighting_options = []
    
    if st.checkbox("LED-подсветка", value=False, key="white_led_direct"):
        lighting_options.append("white_led")
        
    if st.checkbox("RGB-подсветка", value=False, key="rgb_led_direct"):
        lighting_options.append("rgb_led")
    
    # Удаляем преобразование, так как теперь чекбоксы напрямую добавляют правильные значения
    
    # Прямой подход к созданию чекбокса для установки - такой же как для освещения
    st.write("Установка")
    
    # Добавляем CSS для чекбокса установки с теми же стилями, что у освещения
    st.markdown("""
    <style>
    /* Строгое задание отступов для чекбокса установки */
    div[data-testid="stVerticalBlock"] > div:has(label:contains("С установкой")) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # По умолчанию установка включена
    installation = st.checkbox("С установкой", value=True, key="installation_direct")
    
    # Возвращаем выбранные дополнительные опции
    return {
        "lighting": lighting_options,
        "installation": installation
    }

def render_results(results, show_articles=False):
    """
    Отображает результаты расчета стоимости перголы
    
    Args:
        results (dict): Словарь с результатами расчета
        show_articles (bool, optional): Флаг для отображения статей с описаниями. По умолчанию False.
    """
    import os  # Импортируем модуль os внутри функции
    # Добавляем стили для кнопок экспорта PDF
    st.markdown("""
    <style>
    .pdf-export-button {
        background-color: #3f6daa;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        text-align: center;
        margin: 10px 0;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
    }
    .pdf-export-button:hover {
        background-color: #2c4b75;
        transform: translateY(-2px);
    }
    .download-button {
        display: inline-block;
        background-color: #4CAF50;
        color: white !important;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    .download-button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .download-link {
        display: inline-block;
        color: #3f6daa !important;
        text-decoration: none;
        margin-top: 5px;
        padding: 5px 10px;
        font-size: 0.85rem;
        border: 1px solid #3f6daa;
        border-radius: 4px;
        transition: all 0.3s;
    }
    .download-link:hover {
        background-color: #f0f5ff;
        color: #2c4b75 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    # Импортируем модуль отображения акций
    from components.promotion_display import promotions_section
    
    send_page_height_to_parent()
    
    if "error" in results:
        st.error(f"Ошибка при расчете: {results['error']}")
        return
    
    # Основная информация о перголе
    pergola_type = results["options"]["pergola_type"]
    width = results["dimensions"]["width"]
    length = results["dimensions"]["length"]
    modules = results["dimensions"]["modules"]
    base_price = results["base_price"]
    
    # Курс евро для конвертации цен
    euro_rate = pricing_settings.get_euro_rate()
    total_price = results["total_price"]
    
    # Рассчитываем общую стоимость опций для определения скидок
    options_price = total_price - base_price
    
    # Отображаем акции и считаем скидку перед отображением результатов
    # Устанавливаем значительный отрицательный верхний отступ, чтобы убрать лишнее пространство
    st.markdown("""
    <div style='width:85%; margin:0 auto; margin-top: -60px; margin-bottom: 0;'>
        <h3 style='font-size: 2.0rem; font-weight: 600; color: #0066cc; margin-top: 0; margin-bottom: 0; text-align: center;'>Акции и скидки</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Вызываем компонент с акциями и скидками
    total_discount = promotions_section(
        pergola_type=pergola_type,
        width=width,
        length=length,
        base_price=base_price * euro_rate,  # Конвертируем в рубли для акций
        options_price=options_price * euro_rate,  # Конвертируем в рубли для акций
        options=results.get("selected_options", {})
    )
    
    # Применяем скидку к общей стоимости
    rub_total = total_price * euro_rate
    if total_discount > 0:
        rub_total -= total_discount
        # Сохраняем скидку в результаты для дальнейшего использования
        results["discount"] = total_discount
        results["total_price_after_discount"] = rub_total
    
    # Получаем информацию о ламелях
    lamella_type = results["options"]["lamella_type"]
    lamella_info = LAMELLA_TYPES.get(lamella_type, lamella_type)
    
    # Получаем количество ламелей
    lamellas_count = results["debug"].get("lamellas_count", 0)
    
    # Форматируем цену в бухгалтерском стиле с разделителями тысяч
    formatted_price = "{:,.0f}".format(rub_total).replace(",", " ")
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <h2 style='margin-top: 0; color: #0066cc; font-size: 3.2rem; font-weight: 700; text-align: center; margin-bottom: 15px; padding-bottom: 5px; border-bottom: 2px solid #e5eeff;'>Результаты расчета</h2>
        <p style='font-size: 1.1rem; margin-bottom: 5px;'>
            <strong>Пергола:</strong> {PERGOLA_TYPES.get(pergola_type, pergola_type)} {width:.2f}×{length:.2f} м
        </p>
        <p style='font-size: 1.1rem; margin-bottom: 5px;'>
            <strong>Тип ламелей:</strong> {lamella_info}
        </p>
        <p style='font-size: 1.1rem; margin-bottom: 5px;'>
            <strong>Количество модулей:</strong> {modules} {get_plural_form(modules, 'модуль', 'модуля', 'модулей')}
        </p>
        <div id="scroll-target-price" style='font-size: 1.4rem; font-weight: 700; margin-top: 15px; padding-top: 10px; border-top: 1px solid #e0e0e0; text-align: center;'>
            {f'Итоговая стоимость со скидкой:' if total_discount > 0 else 'Итоговая стоимость:'} <span style='font-size: 1.5rem; color: {"#1b5e20" if total_discount > 0 else "#0066cc"};'>{formatted_price} ₽</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Отображаем спецификацию перголы
    if "specification" in results:
        st.markdown("<h3 style='font-size: 2.5rem; font-weight: 700; color: #0066cc; margin-top: 10px; margin-bottom: 15px; text-align: center; padding-bottom: 5px; border-bottom: 2px solid #e5eeff;'>Спецификация перголы</h3>", unsafe_allow_html=True)
        
        # Создаем таблицу спецификации
        spec_data = []
        for item in results["specification"]:
            spec_data.append([item["name"], item["count"]])
        
        # Преобразуем данные в DataFrame и отображаем
        import pandas as pd
        spec_df = pd.DataFrame(spec_data, columns=["Наименование", "Количество"])
        
        # Создаем уникальный ключ для таблицы спецификации (для применения уникальных стилей)
        spec_table_key = "spec_table_" + str(hash(str(spec_data)))
        
        # Создаем HTML-таблицу напрямую для обхода проблем с шириной
        html_table = '<table style="width:100%; border-collapse:collapse; margin-bottom:20px;">'
        
        # Добавляем заголовки
        html_table += '<tr>'
        html_table += '<th style="text-align:left; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:70%; font-size:0.9rem;">Наименование</th>'
        html_table += '<th style="text-align:center; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:30%; font-size:0.9rem;">Количество</th>'
        html_table += '</tr>'
        
        # Добавляем строки с данными
        for item in spec_data:
            html_table += '<tr>'
            html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.9rem;">{item[0]}</td>'
            html_table += f'<td style="text-align:center; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.9rem;">{item[1]}</td>'
            html_table += '</tr>'
        
        html_table += '</table>'
        
        # Выводим HTML-таблицу напрямую через markdown
        st.markdown(f"""
        <div style="width:85%; margin:0 auto; padding-left:25px; padding-right:25px;">
            {html_table}
        </div>
        """, unsafe_allow_html=True)
    
    # Отображаем таблицу стоимости
    st.markdown("<h3 style='font-size: 2.5rem; font-weight: 700; color: #0066cc; margin-top: 15px; margin-bottom: 15px; text-align: center; padding-bottom: 5px; border-bottom: 2px solid #e5eeff;'>Стоимость</h3>", unsafe_allow_html=True)
    
    # Создаем таблицу стоимости
    items_data = []
    
    # Получаем информацию о ламелях
    lamella_info = LAMELLA_TYPES.get(results["options"]["lamella_type"], results["options"]["lamella_type"])
    lamellas_count = results["debug"].get("lamellas_count", 0)
    lamellas_info = ""
    
    # Формируем описание ламелей для таблицы стоимости
    if pergola_type in ["B500NEW", "B700NEW"]:
        lamellas_info = f". {lamella_info}"
        if lamellas_count > 0:
            lamellas_info += f", Количество ламелей - {lamellas_count} шт."
    elif pergola_type == "B600":
        lamellas_info = f". {lamella_info}"
    
    # Функция для форматирования цены в бухгалтерском стиле
    def format_price(price):
        # Округляем цену до целого числа
        price = round(price)
        
        # Используем полный формат без сокращений, с пробелами в качестве разделителей тысяч
        return "{:,.0f}₽".format(price).replace(",", " ")
    
    # Базовая стоимость перголы - всегда первой строкой
    rub_base_price = base_price * euro_rate
    items_data.append([f"Пергола серии {PERGOLA_TYPES.get(pergola_type, pergola_type)} {width:.2f}×{length:.2f} м{lamellas_info} ({modules} {get_plural_form(modules, 'модуль', 'модуля', 'модулей')})", format_price(rub_base_price)])
    
    # Привод и автоматика - второй строкой, если есть
    if pergola_type in ["B500NEW", "B700NEW"]:
        for item in results["items"]:
            if "Привод" in item["name"] or "привод" in item["name"]:
                rub_price = item['price'] * euro_rate
                items_data.append([item["name"], format_price(rub_price)])
    
    # Пульт ДУ - третьей строкой, если есть (для всех типов пергол)
    for item in results["items"]:
        if "Пульт" in item["name"] or "пульт" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Освещение - четвертой строкой, если есть
    for item in results["items"]:
        if "освещен" in item["name"].lower() or "лента" in item["name"].lower() or "LED" in item["name"] or "RGB" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Дополнительные опции - усилитель лотка и колонны
    for item in results["items"]:
        if "Усилитель" in item["name"] or "усилитель" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
        
        if "колон" in item["name"].lower():
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Доставка и установка
    for item in results["items"]:
        if "Доставка" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
            
        if "Установка" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Расчет сумм для отображения
    rub_total = total_price * euro_rate
    discount_amount = 0
    final_price = rub_total
    
    if "discount" in results and results["discount"] > 0:
        discount_amount = results["discount"]
        final_price = results.get("total_price_after_discount", rub_total - discount_amount)
    
    # Условие: если есть скидка > 0
    if "discount" in results and results["discount"] > 0:
        # Итоговая строка БЕЗ учета скидки (если есть скидка)
        items_data.append(["Итого:", format_price(rub_total)])
        
        # Добавляем строку со скидкой (скидка отображается зеленым цветом)
        items_data.append(["Скидка по акции:", f"-{format_price(discount_amount)}"])
        
        # Добавляем строку с итоговой ценой после скидки
        items_data.append(["Итого:", format_price(final_price)])
    else:
        # Если скидки нет, показываем только итоговую строку
        items_data.append(["Итоговая стоимость:", format_price(rub_total)])
    
    # Создаем HTML-таблицу напрямую для обхода проблем с шириной
    html_table = '<table style="width:100%; border-collapse:collapse; margin-bottom:20px;">'
    
    # Добавляем заголовки
    html_table += '<tr>'
    html_table += '<th style="text-align:left; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:70%; font-size:0.9rem;">Наименование</th>'
    html_table += '<th style="text-align:right; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:30%; font-size:0.9rem;">Стоимость</th>'
    html_table += '</tr>'
    
    # Добавляем строки с данными
    for i, item in enumerate(items_data):
        # Особое форматирование для итоговой строки
        if i == len(items_data) - 1:
            # Проверяем, является ли это итоговая строка со скидкой или без
            is_final_with_discount = item[0] == "Итого:" and i == len(items_data) - 1
            is_final_without_discount = "Итоговая стоимость:" in item[0]
            
            if is_final_with_discount:
                # Стиль для итоговой строки СО скидкой (зеленый)
                html_table += '<tr style="background-color:#e0ffea;">'
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:2px solid #1b5e20; word-wrap:break-word; font-weight:bold; font-size:1.35rem; white-space:nowrap;">{item[0]}</td>'
                
                # Применяем специальный класс для значения "Итоговая стоимость со скидкой"
                html_table += f"""
                <td style="text-align:right; padding:8px 5px; border-bottom:2px solid #1b5e20; font-weight:bold; color:#1b5e20; white-space:nowrap;" class="responsive-total">
                    <div style="display:inline-block; width:100%;">{item[1]}</div>
                </td>
                """
            elif is_final_without_discount:
                # Стиль для итоговой строки БЕЗ скидки (синий)
                html_table += '<tr style="background-color:#e0f0ff;">'
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:2px solid #3f6daa; word-wrap:break-word; font-weight:bold; font-size:1.35rem; white-space:nowrap;">{item[0]}</td>'
                
                # Применяем специальный класс для значения "Итоговая стоимость" (без скидки)
                html_table += f"""
                <td style="text-align:right; padding:8px 5px; border-bottom:2px solid #3f6daa; font-weight:bold; color:#0066cc; white-space:nowrap;" class="responsive-total">
                    <div style="display:inline-block; width:100%;">{item[1]}</div>
                </td>
                """
            else:
                # Стиль для строки "Итого" (нейтральный серый)
                html_table += '<tr style="background-color:#f5f5f5;">'
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #cccccc; word-wrap:break-word; font-weight:bold; font-size:1.1rem; white-space:nowrap;">{item[0]}</td>'
                
                # Применяем специальный класс для значения "Итого" 
                html_table += f"""
                <td style="text-align:right; padding:8px 5px; border-bottom:1px solid #cccccc; font-weight:bold; color:#333333; white-space:nowrap;" class="responsive-total">
                    <div style="display:inline-block; width:100%;">{item[1]}</div>
                </td>
                """
            html_table += '</tr>'
        else:
            # Проверяем, является ли строка скидкой (скидки начинаются с минуса)
            is_discount = item[0] == "Скидка по акции:" or item[1].startswith("-")
            
            # Применяем специальные стили для скидок
            if is_discount:
                html_table += '<tr style="background-color:#eaffea;">' # Светло-зеленый фон для скидок
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.9rem; color:#2e7d32; font-weight:500;">{item[0]}</td>'
                html_table += f'<td style="text-align:right; padding:8px 10px; border-bottom:1px solid #eee; font-size:0.9rem; color:#2e7d32; font-weight:500;">{item[1]}</td>'
            else:
                html_table += '<tr>'
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.9rem;">{item[0]}</td>'
                html_table += f'<td style="text-align:right; padding:8px 10px; border-bottom:1px solid #eee; font-size:0.9rem;">{item[1]}</td>'
            
            html_table += '</tr>'
    
    html_table += '</table>'
    
    # Добавляем CSS для адаптивного шрифта строки "Итого"
    st.markdown("""
    <style>
    /* Базовый размер для строки Итого на больших экранах */
    .responsive-total {
        font-size: 1.5rem !important;
        white-space: nowrap !important;
    }
    
    /* Медиа-запросы для адаптивности */
    @media screen and (max-width: 992px) {
        .responsive-total {
            font-size: 1.2rem !important;
        }
    }
    
    @media screen and (max-width: 768px) {
        .responsive-total {
            font-size: 1.0rem !important;
        }
    }
    
    @media screen and (max-width: 576px) {
        .responsive-total {
            font-size: 0.85rem !important;
        }
    }
    
    /* Дополнительные стили для мобильной версии таблицы */
    @media screen and (max-width: 480px) {
        .responsive-total {
            font-size: 0.75rem !important;
        }
        
        /* Уменьшаем размер шрифта во всей таблице для мобильных устройств */
        table th, table td {
            font-size: 0.85rem !important;
            padding: 6px 4px !important;
        }
        
        /* Уменьшаем отступы в таблице */
        table {
            width: 100% !important;
            margin: 0 !important;
            table-layout: fixed !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Выводим HTML-таблицу напрямую через markdown
    st.markdown(f"""
    <div style="width:85%; margin:0 auto; padding-left:25px; padding-right:25px;">
        {html_table}
    </div>
    """, unsafe_allow_html=True)
    
    # Добавляем кнопку для экспорта PDF
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] > button {
            background-color: #0066cc !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 1rem !important;
            font-size: 1.1rem !important;
            height: 60px !important;
            min-width: 300px !important;
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
            white-space: nowrap !important;
            border-radius: 8px !important;
            animation: pdf-btn-pulse 2s ease-in-out infinite !important;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            background-color: #0055aa !important;
            box-shadow: 0 6px 15px rgba(0, 102, 204, 0.4) !important;
            transform: scale(1.03) !important;
        }
        div[data-testid="stDownloadButton"] > button p {
            color: white !important;
            white-space: nowrap !important;
            font-size: 1.1rem !important;
            line-height: 1 !important;
        }
        @keyframes pdf-btn-pulse {
            0% { transform: scale(1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); background-color: #0066cc; }
            50% { transform: scale(1.03); box-shadow: 0 6px 15px rgba(0, 102, 204, 0.4); background-color: #0077dd; }
            100% { transform: scale(1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); background-color: #0066cc; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        pdf_bytes, file_name = export_to_pdf()
        
        if pdf_bytes:
            st.download_button(
                label="📄 ЭКСПОРТ КП В PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                key="export_pdf_button",
                help="Скачать коммерческое предложение в PDF",
                use_container_width=True,
            )
        else:
            st.button(
                "📄 ЭКСПОРТ КП В PDF",
                key="export_pdf_button_disabled",
                use_container_width=True,
                disabled=True,
            )
    
    # Отображаем разделитель между таблицей стоимости и описанием перголы
    st.markdown("<hr style='margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Добавляем информацию о типе перголы и изображение только если show_articles=True
    if show_articles and not st.session_state.get('description_shown', False):
        # Устанавливаем флаг, что описание уже было показано в этой сессии
        st.session_state.description_shown = True
        
        # Отображаем информацию о выбранном типе перголы с использованием модуля описаний
        if pergola_type in ["B500NEW", "B700NEW", "B600"]:
            # Используем описание из модуля конфигурации
            description_html = get_pergola_description(pergola_type)
            display_formatted_description(description_html, pergola_type)
            
            # Отображаем изображения с использованием списка из конфигурации
            images = get_pergola_images(pergola_type)
            caption = get_pergola_image_caption(pergola_type)
            
            if images:
                # Пробуем загрузить изображения по очереди, пока не найдем рабочее
                for img_path in images:
                    try:
                        # Проверяем, существует ли файл
                        import os
                        if not os.path.exists(img_path):
                            continue
                            
                        display_image_with_padding(img_path, caption=caption)
                        break  # Прерываем цикл, если изображение успешно загружено
                    except Exception as e:
                        continue  # Пробуем следующее изображение
                else:
                    st.warning(f"Не удалось загрузить изображение для {pergola_type}")
            
            # Добавляем информацию о масштабируемости для всех типов пергол
            # Отображаем описание модульной системы из модуля конфигурации
            modular_description = get_modular_system_description()
            display_formatted_description(modular_description, "MODULAR")
            
            # Отображаем изображение модульной системы
            modular_images = get_pergola_images("MODULAR")
            modular_caption = get_pergola_image_caption("MODULAR")
            
            if modular_images:
                # Пробуем загрузить изображения по очереди, пока не найдем рабочее
                for img_path in modular_images:
                    try:
                        # Проверяем, существует ли файл
                        import os
                        if not os.path.exists(img_path):
                            continue
                        
                        display_image_with_padding(img_path, caption=modular_caption)
                        break
                    except Exception as e:
                        continue
                else:
                    st.warning(f"Не удалось загрузить изображение модульной системы")
            
            # Добавляем информацию о системе водоотведения для всех типов пергол
            # Отображаем описание системы водоотведения из модуля конфигурации
            drainage_description = get_drainage_system_description()
            display_formatted_description(drainage_description, "DRAINAGE")
            
            # Отображаем изображение системы водоотведения
            drainage_images = get_pergola_images("DRAINAGE")
            drainage_caption = get_pergola_image_caption("DRAINAGE")
            
            if drainage_images:
                for img_path in drainage_images:
                    try:
                        display_image_with_padding(img_path, caption=drainage_caption)
                        break
                    except Exception as e:
                        continue
                else:
                    st.warning(f"Не удалось загрузить изображение системы водоотведения")
            
            # Добавляем информацию о приводе Bansbach только для пергол B500NEW
            if pergola_type == "B500NEW":
                bansbach_description = get_bansbach_description()
                display_formatted_description(bansbach_description, "BANSBACH")
                
                # Отображаем изображение привода Bansbach
                bansbach_images = get_pergola_images("BANSBACH")
                bansbach_caption = get_pergola_image_caption("BANSBACH")
                
                if bansbach_images:
                    for img_path in bansbach_images:
                        try:
                            display_image_with_padding(img_path, caption=bansbach_caption)
                            break
                        except Exception as e:
                            continue
                    else:
                        st.warning(f"Не удалось загрузить изображение привода Bansbach")
            
            # Добавляем информацию о приводе Somfy только для пергол B700NEW
            if pergola_type == "B700NEW":
                somfy_description = get_pergola_description("SOMFY")
                display_formatted_description(somfy_description, "SOMFY")
                
                # Отображаем изображение привода Somfy
                somfy_images = get_pergola_images("SOMFY")
                somfy_caption = get_pergola_image_caption("SOMFY")
                
                if somfy_images:
                    for img_path in somfy_images:
                        try:
                            display_image_with_padding(img_path, caption=somfy_caption)
                            break
                        except Exception as e:
                            continue
                    else:
                        st.warning(f"Не удалось загрузить изображение привода Somfy")
            
            # Добавляем описание вариантов установки и вертикальных систем для всех типов пергол
            bioclimatic_install_description = get_bioclimatic_install_description()
            display_formatted_description(bioclimatic_install_description, "INSTALL_SYSTEM")
            
            # Отображаем изображение вариантов установки
            install_system_images = get_pergola_images("INSTALL_SYSTEM")
            install_system_caption = get_pergola_image_caption("INSTALL_SYSTEM")
            
            if install_system_images:
                for img_path in install_system_images:
                    try:
                        display_image_with_padding(img_path, caption=install_system_caption)
                        break
                    except Exception as e:
                        continue
                else:
                    st.warning(f"Не удалось загрузить изображение вариантов установки")
            
            # Добавляем техническое описание ламелей только для пергол B500 и B700, не для B600
            if pergola_type in ["B500NEW", "B700NEW"]:
                lamella_engineering_description = get_lamella_engineering_description()
                display_formatted_description(lamella_engineering_description, "LAMELLA_ENGINEERING")
                
                # Отображаем изображение технических характеристик ламелей
                lamella_engineering_images = get_pergola_images("LAMELLA_ENGINEERING")
                lamella_engineering_caption = get_pergola_image_caption("LAMELLA_ENGINEERING")
                
                if lamella_engineering_images:
                    for img_path in lamella_engineering_images:
                        try:
                            display_image_with_padding(img_path, caption=lamella_engineering_caption)
                            break
                        except Exception as e:
                            continue
                    else:
                        st.warning(f"Не удалось загрузить изображение технических характеристик ламелей")
    
    # Добавляем отступ в конце страницы
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

def display_formatted_description(description_text, article_type=None):
    """
    Отображает форматированное описание в стилизованном контейнере,
    избегая проблем с видимостью HTML-тегов.
    
    Args:
        description_text (str): HTML-текст с описанием
        article_type (str, optional): Тип статьи/перголы для отображения даты публикации
    """
    # Создаем стиль для описания один раз при первом вызове
    if 'description_style_added' not in st.session_state:
        st.markdown("""
        <style>
        .description-container {
            width: 100%;
            margin: 0 auto;
            padding: 5px 5px; /* Минимальные отступы слева и справа */
            background-color: #ffffff;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 1.2rem; /* Увеличиваем базовый размер шрифта для всего контента */
        }
        
        /* Стили только для статей внутри описания */
        .description-container * {
            padding-left: 0px !important;
            padding-right: 0px !important;
        }
        /* Стили для корректного отображения разных HTML элементов */
        .section, section {
            display: block;
            margin-bottom: 15px;
            width: 100%;
        }
        .description-container h1, .description-container h2 {
            font-size: 2.2rem; /* Размер для h1 и h2 */
            margin-top: 30px;
            margin-bottom: 20px;
            color: #333333;
            font-weight: 700; /* Жирный шрифт */
            font-family: inherit; /* Использовать основной шрифт */
            text-align: center; /* Центрирование заголовков */
        }
        .description-container h3 {
            font-size: 1.9rem; /* Размер для h3 */
            margin-top: 25px;
            margin-bottom: 20px;
            color: #333333;
            font-weight: 700; /* Жирный шрифт */
            font-family: inherit; /* Использовать основной шрифт */
            text-align: center; /* Центрирование заголовков */
        }
        .description-container h4 {
            font-size: 1.7rem; /* Размер для h4 */
            margin-top: 20px;
            margin-bottom: 15px;
            color: #333333;
            font-weight: 700; /* Жирный шрифт */
            font-family: inherit; /* Использовать основной шрифт */
            text-align: center; /* Центрирование заголовков */
        }
        .description-container p {
            margin-bottom: 10px;
            line-height: 1.5;
            font-size: 1.25rem; /* Размер параграфов */
            font-family: inherit; /* Использовать основной шрифт */
        }
        .description-container ul {
            margin-left: 20px;
            margin-bottom: 15px;
            font-size: 1.25rem; /* Увеличенный размер для списков */
        }
        .description-container li {
            margin-bottom: 8px;
        }
        .description-container strong, .description-container b {
            font-weight: 600;
            color: #333333; /* Стандартный цвет текста вместо синего */
        }
        .description-container em, .description-container i {
            font-style: italic;
            color: #333333; /* Стандартный цвет текста вместо синего */
        }
        /* Стили для таблиц внутри описаний */
        .description-container table {
            width: 100%;
            margin-bottom: 20px;
            border-collapse: collapse;
        }
        .description-container th {
            background-color: #f5f5f5; /* Светло-серый фон для заголовков */
            color: #333333;
            font-weight: 600;
            font-size: 1.2rem;
            padding: 10px;
            text-align: left;
            border: 1px solid #dddddd;
        }
        .description-container td {
            padding: 10px;
            border: 1px solid #dddddd;
            font-size: 1.2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.description_style_added = True
    
    try:
        # Предварительная обработка для устранения проблем с форматированием
        
        # 1. Удаляем отступы в начале строк, которые создают проблемы с HTML
        import re
        # Определяем, есть ли отступы в начале описания, что характерно для проблемных статей
        lines = description_text.split('\n')
        cleaned_lines = []
        
        # Проверяем каждую строку и удаляем лишние пробелы в начале
        for line in lines:
            # Если строка начинается с пробелов и содержит HTML-тег
            if line.strip() and line.strip()[0] == '<':
                # Удаляем все пробелы перед HTML-тегом
                cleaned_lines.append(line.strip())
            else:
                # Оставляем пустые строки или неструктурированный текст как есть
                cleaned_lines.append(line)
        
        # Собираем очищенный текст обратно
        clean_text = '\n'.join(cleaned_lines)
        
        # 2. Заменяем все экземпляры <section> на <div class="section">
        formatted_text = clean_text.replace("<section>", "<div class='section'>")
        formatted_text = formatted_text.replace("</section>", "</div>")
        
        # 3. Для надежности заменяем еще и вариации с пробелами или атрибутами
        formatted_text = re.sub(r'<section\s+[^>]*>', '<div class="section">', formatted_text)
        
        # 4. Проверяем финальный результат на любые оставшиеся <section> теги
        if "<section" in formatted_text:
            # Если остались, применяем более радикальную замену
            formatted_text = re.sub(r'<section.*?>', '<div class="section">', formatted_text)
        
        # 5. Удаляем двойные пробелы для надежности
        formatted_text = re.sub(r'\s{2,}', ' ', formatted_text)
        
        # 6. Добавляем дату публикации, если статья указана
        publication_date_html = ""
        if article_type:
            # Импортируем функцию для получения даты публикации
            from config.pergola_descriptions import get_publication_date
            pub_date = get_publication_date(article_type)
            if pub_date:
                publication_date_html = f"""
                <div style="text-align: right; font-size: 0.9rem; color: #666; margin-top: 5px; margin-bottom: 10px; font-style: italic;">
                    Дата публикации: {pub_date}
                </div>
                """
        
        # 7. Обрамляем весь текст в div-контейнер для изоляции стилей и добавляем контейнер с отступами
        # Уменьшаем отступ справа для более компактного вида
        final_html = f"""
        <div style="width:95%; margin:0 auto; padding-left:15px; padding-right:15px;">
            {publication_date_html}
            <div class="description-container">{formatted_text}</div>
        </div>
        """
        
        # Используем контейнер для изоляции стилей и предотвращения конфликтов
        container = st.container()
        with container:
            st.markdown(final_html, unsafe_allow_html=True)
    
    except Exception as e:
        # В случае ошибки показываем сообщение и используем безопасный метод отображения
        st.error(f"Ошибка при форматировании HTML: {str(e)}")
        # Резервный вариант отображения с вырезанием HTML
        import re
        plain_text = re.sub(r'<.*?>', ' ', description_text)
        st.write(plain_text)

def create_simple_pdf(pergola_data):
    """
    Создает простой PDF-файл с поддержкой кириллицы.
    
    Args:
        pergola_data (dict): Данные о перголе для включения в PDF
        
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    import io
    import time
    import os
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    # Создаем директорию для PDF, если её нет
    os.makedirs("generated_pdf", exist_ok=True)
    
    # Регистрируем шрифт с поддержкой кириллицы
    font_path = os.path.join('fonts', 'DejaVuSans.ttf')
    bold_font_path = os.path.join('fonts', 'DejaVuSans-Bold.ttf')
    
    # Проверяем наличие шрифтов и создаем простую версию
    if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
        return create_very_simple_pdf(pergola_data)
    
    # Регистрируем шрифты
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
    
    # Генерируем информативное имя файла на основе данных перголы
    try:
        from improved_pdf_export import generate_pdf_file_name
        file_name = generate_pdf_file_name(pergola_data)
        pdf_path = os.path.join("generated_pdf", file_name)
    except ImportError:
        # Запасной вариант, если модуль улучшенного экспорта не доступен
        from datetime import datetime
        import pytz
        
        # Определяем временную зону Ростова-на-Дону (та же, что и в Москве)
        rostov_tz = pytz.timezone('Europe/Moscow')
        now_utc = datetime.now(pytz.utc)
        now_rostov = now_utc.astimezone(rostov_tz)
        timestamp = now_rostov.strftime("%Y%m%d_%H%M%S")
        pdf_path = f"generated_pdf/KP_Pergola_{timestamp}.pdf"
    
    # Создаем документ
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        title="Коммерческое предложение - Пергола",
        author="Калькулятор пергол"
    )
    
    # Создаем стили
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Russian', 
        fontName='DejaVuSans',
        fontSize=12,
        leading=14
    ))
    
    # Создаем свои стили с кириллическими шрифтами
    title_style = ParagraphStyle(
        name='CustomTitle',
        fontName='DejaVuSans-Bold',
        fontSize=18,
        alignment=1,  # По центру
        spaceAfter=12
    )
    
    heading2_style = ParagraphStyle(
        name='CustomHeading2',
        fontName='DejaVuSans-Bold',
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        name='CustomNormal',
        fontName='DejaVuSans',
        fontSize=12,
        leading=14
    )
    
    footer_style = ParagraphStyle(
        name='CustomFooter',
        fontName='DejaVuSans',
        fontSize=10,
        alignment=1,  # По центру
        leading=12,
        fontStyle='italic'
    )
    
    # Создаем элементы для PDF
    elements = []
    
    # Заголовок
    elements.append(Paragraph("Коммерческое предложение", title_style))
    elements.append(Paragraph("Биоклиматическая пергола", title_style))
    elements.append(Spacer(1, 20))
    
    # Параметры перголы
    elements.append(Paragraph("Параметры перголы:", heading2_style))
    elements.append(Spacer(1, 10))
    
    # Основная информация
    pergola_type = pergola_data.get("pergola_type", "")
    width = pergola_data.get("width", 0)
    length = pergola_data.get("length", 0)
    modules = pergola_data.get("modules", 1)
    
    elements.append(Paragraph(f"Модель: {pergola_type}", normal_style))
    elements.append(Paragraph(f"Ширина: {width} м", normal_style))
    elements.append(Paragraph(f"Длина (вынос): {length} м", normal_style))
    elements.append(Paragraph(f"Количество модулей: {modules}", normal_style))
    elements.append(Spacer(1, 10))
    
    # Добавление изображения перголы
    image_path = get_pergola_image_path(pergola_type)
    print(f"Тип перголы для изображения: {pergola_type}")
    print(f"Путь к изображению: {image_path}")
    
    if image_path and os.path.exists(image_path):
        print(f"Файл изображения существует: {os.path.exists(image_path)}")
        try:
            # Создаем изображение из файла
            from reportlab.lib.units import inch
            from reportlab.platypus import Image
            
            # Определяем размеры изображения (ширина ~70% от ширины страницы, чтобы избежать ошибки "too large")
            img_width = 4.5 * inch  # уменьшенный размер для безопасности
            print(f"Ширина изображения: {img_width}")
            
            # Получаем реальные размеры изображения для расчета пропорций
            from PIL import Image as PILImage
            pil_img = PILImage.open(image_path)
            orig_width, orig_height = pil_img.size
            pil_img.close()
            
            # Вычисляем высоту с сохранением пропорций
            aspect_ratio = orig_height / orig_width
            img_height = img_width * aspect_ratio
            
            # Проверяем, не слишком ли высокое изображение (ограничиваем 5 дюймами)
            if img_height > 5 * inch:
                img_height = 5 * inch
                img_width = img_height / aspect_ratio
                print(f"Изображение слишком высокое, ограничиваем высоту. Новые размеры: {img_width}x{img_height}")
            
            # Создаем изображение с указанными размерами
            img = Image(image_path, width=img_width, height=img_height)
            
            # Добавляем изображение
            elements.append(img)
            print("Изображение добавлено в PDF")
            
            # Добавляем подпись
            caption_style = ParagraphStyle('Caption', fontName='DejaVuSans', fontSize=10, alignment=1)
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("Визуализация модели", caption_style))
        except Exception as e:
            # Если возникла проблема с добавлением изображения, пропускаем
            print(f"Ошибка при добавлении изображения в PDF: {e}")
            import traceback
            print(traceback.format_exc())
    else:
        print(f"Файл изображения не существует: {image_path}")
    
    elements.append(Spacer(1, 20))
    
    # Добавляем разрыв страницы перед таблицей стоимости, чтобы она начиналась с новой страницы
    elements.append(PageBreak())
    
    # Секция стоимости
    elements.append(Paragraph("Стоимость:", heading2_style))
    elements.append(Spacer(1, 10))
    
    # Таблица со стоимостью
    items = pergola_data.get("items", [])
    euro_rate = pergola_data.get("euro_rate", 110)
    
    # Подготовка данных для таблицы
    table_data = [["Наименование", "Стоимость"]]
    total_cost = 0
    
    for item in items:
        name = item.get("name", "")
        price = item.get("price", 0)
        # Конвертируем в рубли
        price_rub = price * euro_rate
        total_cost += price_rub
        
        # Форматируем цену
        price_str = f"{price_rub:,.2f}".replace(",", " ").replace(".", ",") + " ₽"
        
        # Добавляем строку в таблицу
        table_data.append([name, price_str])
    
    # Итоговая строка 
    total_str = f"{total_cost:,.2f}".replace(",", " ").replace(".", ",") + " ₽"
    table_data.append(["ИТОГО:", total_str])
    
    # Если есть скидка, добавляем строку со скидкой и итоговую сумму со скидкой
    discount = pergola_data.get("discount", 0)
    if discount > 0:
        discount_str = f"{discount:,.2f}".replace(",", " ").replace(".", ",") + " ₽"
        table_data.append(["СКИДКА:", discount_str])
        
        total_after_discount = pergola_data.get("total_price_after_discount", total_cost)
        total_after_discount_str = f"{total_after_discount:,.2f}".replace(",", " ").replace(".", ",") + " ₽"
        table_data.append(["ИТОГО СО СКИДКОЙ:", total_after_discount_str])
    
    # Создаем таблицу
    table = Table(table_data, colWidths=[350, 150])
    
    # Стиль таблицы
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (1, 0), 'DejaVuSans-Bold'),  # Используем кириллический шрифт
        ('FONTNAME', (0, 1), (-1, -2), 'DejaVuSans'),     # Используем кириллический шрифт
        ('FONTNAME', (0, -1), (1, -1), 'DejaVuSans-Bold'), # Используем кириллический шрифт для итоговой строки
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Раздел Спецификации перголы, если есть данные
    specification = pergola_data.get("specification", [])
    if specification:
        # Добавляем отступ перед спецификацией (без разрыва страницы)
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Спецификация перголы:", heading2_style))
        elements.append(Spacer(1, 10))
        
        # Создаем таблицу спецификации
        spec_table_data = [["Наименование", "Количество"]]
        
        for item in specification:
            name = item.get("name", "")
            count = item.get("count", "")
            
            # Проверяем, что имя не слишком длинное
            if len(name) > 60:
                # Находим подходящее место для переноса (пробел после 50-60 символов)
                split_position = name.rfind(' ', 50, 60)
                
                if split_position == -1:  # Если не нашли подходящий пробел
                    split_position = 60   # Просто разделим на 60 символе
                
                # Разбиваем имя на две строки
                first_line = name[:split_position]
                second_line = name[split_position:].strip()
                
                # Создаем параграф с авто-переносом
                paragraph_style = ParagraphStyle(
                    'SpecItem',
                    fontName='DejaVuSans',
                    fontSize=10,
                    leading=12,
                    spaceBefore=0,
                    spaceAfter=0
                )
                # Вместо использования Paragraph, лучше разобьем данные на две строки напрямую
                name_cell = Table([[first_line], [second_line]], colWidths=[350])
                name_cell_style = TableStyle([
                    ('FONTNAME', (0, 0), (0, 1), 'DejaVuSans'),
                    ('FONTSIZE', (0, 0), (0, 1), 10),
                    ('ALIGN', (0, 0), (0, 1), 'LEFT'),
                    ('VALIGN', (0, 0), (0, 1), 'MIDDLE'),
                    ('GRID', (0, 0), (0, 1), 0, colors.white) # Без внутренних границ
                ])
                name_cell.setStyle(name_cell_style)
                spec_table_data.append([name_cell, count])
            else:
                spec_table_data.append([name, count])
        
        # Создаем таблицу
        spec_table = Table(spec_table_data, colWidths=[350, 150])
        
        # Стиль таблицы спецификации
        spec_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        spec_table.setStyle(spec_table_style)
        elements.append(spec_table)
        elements.append(Spacer(1, 30))
    
    # Добавляем раздел примечаний
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Примечания:", heading2_style))
    elements.append(Spacer(1, 10))
    
    # Стиль для текста примечаний
    note_style = ParagraphStyle(
        'Notes',
        fontName='DejaVuSans',
        fontSize=10,
        leading=14,
        spaceBefore=3,
        spaceAfter=3
    )
    
    # Добавляем каждое примечание отдельной строкой с нумерацией
    remarks = [
        "Расчет является предварительным и может быть уточнен при обращении в компанию.",
        "Срок действия предложения: 14 дней с даты расчета.",
        "Срок поставки: 6 недель с момента подтверждения заказа.",
        "Условия оплаты: 80% предоплата, 20% после монтажа."
    ]
    
    for i, remark in enumerate(remarks, 1):
        elements.append(Paragraph(f"{i}. {remark}", note_style))
    
    elements.append(Spacer(1, 10))
    
    # Информация о компании
    from datetime import datetime
    import pytz
    
    # Определяем московскую временную зону
    moscow_tz = pytz.timezone('Europe/Moscow')
    now_utc = datetime.now(pytz.utc)
    now_moscow = now_utc.astimezone(moscow_tz)
    current_date = now_moscow.strftime("%d.%m.%Y")
    
    # Добавляем разделительную линию
    elements.append(Spacer(1, 10))
    
    # Горизонтальная линия (разделитель)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))
    
    # Стиль для названия компании (жирный)
    company_style = ParagraphStyle(
        'CompanyTitle',
        fontName='DejaVuSans-Bold',
        fontSize=11,
        leading=13,
        alignment=1  # По центру
    )
    
    # Стиль для остальной информации (обычный)
    info_style = ParagraphStyle(
        'CompanyInfo',
        fontName='DejaVuSans',
        fontSize=9,
        leading=11,
        alignment=1  # По центру
    )
    
    # Стиль для даты (меньший размер)
    date_style = ParagraphStyle(
        'DateInfo',
        fontName='DejaVuSans',
        fontSize=8,
        leading=10,
        alignment=1  # По центру
    )
    
    # Добавляем колонтитул с информацией о компании
    elements.append(Paragraph("Компания «Комфортный дом»", company_style))
    elements.append(Paragraph("Комплексные решения для обустройства террас, веранды и беседок.", info_style))
    elements.append(Paragraph("ИП Гоноченко А.В. ОГРНИП 321619600249231", info_style))
    elements.append(Paragraph("Тел.: +7-906-429-74-20 Сайт: pergolamarket.ru", info_style))
    
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"Коммерческое предложение сформировано: {current_date}", date_style))
    
    # Строим PDF
    doc.build(elements)
    
    return pdf_path

def get_pergola_image_path(pergola_type):
    """
    Возвращает путь к изображению перголы на основе ее типа.
    
    Args:
        pergola_type (str): Тип перголы (B500, B600, B700)
        
    Returns:
        str: Путь к изображению или None, если изображение не найдено
    """
    # Стандартизируем тип перголы (приводим к верхнему регистру)
    pergola_type = pergola_type.upper() if pergola_type else ""
    
    # Словарь с соответствиями типа перголы и путей к изображениям
    image_paths = {
        "B500": "attached_assets/b500_rotation.png",
        "B600": "attached_assets/b600_sandwich.png", 
        "B700": "attached_assets/b700_sliding.png",
        "B500NEW": "attached_assets/b500_rotation.png",
        "B600NEW": "attached_assets/b600_sandwich.png",
        "B700NEW": "attached_assets/b700_sliding.png"
    }
    
    # Возвращаем путь к изображению или None, если тип не найден
    return image_paths.get(pergola_type)

def create_very_simple_pdf(pergola_data):
    """
    Создает предельно простой PDF без кириллических шрифтов для случаев, когда шрифтов нет.
    Использует английские названия и ASCII-символы.
    
    Args:
        pergola_data (dict): Данные о перголе для включения в PDF
        
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    import io
    from datetime import datetime
    import pytz
    from fpdf import FPDF
    
    # Создаем директорию для PDF, если её нет
    os.makedirs("generated_pdf", exist_ok=True)
    
    # Генерируем информативное имя файла на основе данных перголы
    try:
        from improved_pdf_export import generate_pdf_file_name
        file_name = generate_pdf_file_name(pergola_data)
        pdf_path = os.path.join("generated_pdf", file_name)
    except ImportError:
        # Запасной вариант, если модуль улучшенного экспорта не доступен
        moscow_tz = pytz.timezone('Europe/Moscow')
        now_utc = datetime.now(pytz.utc)
        now_moscow = now_utc.astimezone(moscow_tz)
        timestamp = now_moscow.strftime("%Y%m%d_%H%M%S")
        pdf_path = f"generated_pdf/KP_Pergola_{timestamp}.pdf"
    
    # Создаем PDF с базовыми настройками
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Проверяем и пытаемся использовать шрифты DejaVu
    font_path = os.path.join('fonts', 'DejaVuSans.ttf')
    bold_font_path = os.path.join('fonts', 'DejaVuSans-Bold.ttf')
    
    use_dejavu = False
    print(f"Проверка наличия шрифтов: font_path={font_path}, exists={os.path.exists(font_path)}")
    print(f"Проверка наличия шрифтов: bold_font_path={bold_font_path}, exists={os.path.exists(bold_font_path)}")
    
    if os.path.exists(font_path) and os.path.exists(bold_font_path):
        try:
            # Добавляем шрифты в PDF
            pdf.add_font('DejaVu', '', font_path, uni=True)
            pdf.add_font('DejaVu', 'B', bold_font_path, uni=True)
            use_dejavu = True
            print(f"Шрифты DejaVu успешно загружены, use_dejavu={use_dejavu}")
        except Exception as e:
            # Если не удалось загрузить шрифты, используем базовые
            print(f"Не удалось загрузить шрифты DejaVu: {e}")
    
    # Выбираем подходящий шрифт
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 16)
    else:
        pdf.set_font("Arial", "B", 16)
    
    # Заголовок
    if use_dejavu:
        pdf.cell(0, 10, "Коммерческое предложение - Биоклиматическая пергола", ln=True, align="C")
    else:
        pdf.cell(0, 10, "Commercial Offer - Pergola System", ln=True, align="C")
    pdf.ln(10)
    
    # Информация о перголе
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "Параметры перголы:", ln=True)
    else:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Pergola Parameters:", ln=True)
    
    if use_dejavu:
        pdf.set_font("DejaVu", "", 12)
    else:
        pdf.set_font("Arial", "", 12)
    pergola_type = pergola_data.get("pergola_type", "")
    width = pergola_data.get("width", 0)
    length = pergola_data.get("length", 0)
    modules = pergola_data.get("modules", 1)
    
    if use_dejavu:
        pdf.cell(0, 10, f"Модель: {pergola_type}", ln=True)
        pdf.cell(0, 10, f"Ширина: {width} м", ln=True)
        pdf.cell(0, 10, f"Вынос: {length} м", ln=True)
        pdf.cell(0, 10, f"Количество модулей: {modules}", ln=True)
    else:
        pdf.cell(0, 10, f"Model: {pergola_type}", ln=True)
        pdf.cell(0, 10, f"Width: {width} m", ln=True)
        pdf.cell(0, 10, f"Length: {length} m", ln=True)
        pdf.cell(0, 10, f"Number of modules: {modules}", ln=True)
    pdf.ln(10)
    
    # Добавляем изображение перголы в зависимости от выбранного типа
    image_path = get_pergola_image_path(pergola_type)
    print(f"Простая версия PDF - Тип перголы: {pergola_type}, путь: {image_path}")
    
    if image_path and os.path.exists(image_path):
        print(f"Файл изображения для простой версии PDF существует: {os.path.exists(image_path)}")
        try:
            # Устанавливаем ширину изображения, чтобы оно занимало часть страницы
            from PIL import Image as PILImage
            
            # Открываем изображение и получаем его размеры
            pil_img = PILImage.open(image_path)
            orig_width, orig_height = pil_img.size
            pil_img.close()
            
            # Вычисляем соотношение сторон
            aspect_ratio = orig_height / orig_width
            
            # Устанавливаем ограничения для размеров (не более 70% ширины и не более 40% высоты страницы)
            page_width = pdf.w - 60  # ширина страницы с отступами
            max_img_width = page_width * 0.7
            max_img_height = pdf.h * 0.4
            
            # Вычисляем размеры с сохранением пропорций
            image_width = max_img_width
            image_height = image_width * aspect_ratio
            
            # Если высота получается слишком большой, ограничиваем её
            if image_height > max_img_height:
                image_height = max_img_height
                image_width = image_height / aspect_ratio
                print(f"Изображение слишком высокое, ограничиваем высоту. Новые размеры: {image_width}x{image_height}")
            
            # Вычисляем X координату для центрирования изображения
            x_pos = (pdf.w - image_width) / 2
            
            # Сохраняем текущую Y позицию
            current_y = pdf.get_y()
            
            # Добавляем изображение
            pdf.image(image_path, x=x_pos, y=current_y, w=image_width, h=image_height)
            
            # Перемещаем текущую позицию после изображения
            pdf.set_y(current_y + image_height + 10)  # +10 для отступа
            
            # Добавляем подпись
            pdf.cell(0, 10, "Model visualization", ln=True, align="C")
            pdf.ln(10)
            
            print("Изображение успешно добавлено в простую версию PDF")
        except Exception as e:
            # Если возникла ошибка при вставке изображения, продолжаем без него
            print(f"Ошибка при добавлении изображения перголы в простую версию PDF: {e}")
            import traceback
            print(traceback.format_exc())
    
    # Добавляем отступ перед таблицей стоимости
    pdf.ln(15)
    
    # Секция стоимости
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 12)
    else:
        pdf.set_font("Arial", "B", 12)
    if use_dejavu:
        pdf.cell(0, 10, "Стоимость:", ln=True)
    else:
        pdf.cell(0, 10, "Cost table:", ln=True)
    
    # Заголовки таблицы
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 10)
    else:
        pdf.set_font("Arial", "B", 10)
    if use_dejavu:
        pdf.cell(130, 10, "Наименование", 1, 0)
        pdf.cell(60, 10, "Цена", 1, 1, align="R")
    else:
        pdf.cell(130, 10, "Item", 1, 0)
        pdf.cell(60, 10, "Price", 1, 1, align="R")
    
    # Данные таблицы
    if use_dejavu:
        pdf.set_font("DejaVu", "", 10)
    else:
        pdf.set_font("Arial", "", 10)
    
    # Получаем данные
    items = pergola_data.get("items", [])
    euro_rate = pergola_data.get("euro_rate", 110)
    total_cost = 0
    
    for item in items:
        name = item.get("name", "")
        # Упрощаем имена для ASCII
        name = name.replace("привод", "drive")
        name = name.replace("подсветка", "lighting")
        name = name.replace("лотка", "gutter")
        name = name.replace("усилитель", "reinforcement")
        name = name.replace("пульт", "remote")
        
        price = item.get("price", 0)
        # Конвертируем в рубли
        price_rub = price * euro_rate
        total_cost += price_rub
        
        # Форматируем цену
        price_str = f"{price_rub:,.2f} RUB".replace(",", " ")
        
        # Ограничиваем длину имени
        if len(name) > 60:
            name = name[:57] + "..."
            
        pdf.cell(130, 10, name, 1, 0)
        pdf.cell(60, 10, price_str, 1, 1, align="R")
    
    # Итоговая строка
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 10)
    else:
        pdf.set_font("Arial", "B", 10)
    if use_dejavu:
        pdf.cell(130, 10, "ИТОГО:", 1, 0)
        pdf.cell(60, 10, f"{total_cost:,.2f} ₽".replace(",", " "), 1, 1, align="R")
    else:
        pdf.cell(130, 10, "TOTAL:", 1, 0)
        pdf.cell(60, 10, f"{total_cost:,.2f} RUB".replace(",", " "), 1, 1, align="R")
    
    # Если есть скидка, добавляем строку скидки и итоговую сумму со скидкой
    discount = pergola_data.get("discount", 0)
    if discount > 0:
        # Шрифт и стиль уже установлены выше
        if use_dejavu:
            pdf.cell(130, 10, "СКИДКА:", 1, 0)
            pdf.cell(60, 10, f"{discount:,.2f} ₽".replace(",", " "), 1, 1, align="R")
            
            total_after_discount = pergola_data.get("total_price_after_discount", total_cost)
            pdf.cell(130, 10, "ИТОГО СО СКИДКОЙ:", 1, 0)
            pdf.cell(60, 10, f"{total_after_discount:,.2f} ₽".replace(",", " "), 1, 1, align="R")
        else:
            pdf.cell(130, 10, "DISCOUNT:", 1, 0)
            pdf.cell(60, 10, f"{discount:,.2f} RUB".replace(",", " "), 1, 1, align="R")
            
            total_after_discount = pergola_data.get("total_price_after_discount", total_cost)
            pdf.cell(130, 10, "TOTAL WITH DISCOUNT:", 1, 0)
            pdf.cell(60, 10, f"{total_after_discount:,.2f} RUB".replace(",", " "), 1, 1, align="R")
    
    # Добавляем раздел Спецификации перголы, если есть данные
    specification = pergola_data.get("specification", [])
    if specification:
        # Добавляем отступ перед спецификацией (без разрыва страницы)
        pdf.ln(15)
        
        if use_dejavu:
            pdf.set_font("DejaVu", "B", 12)
        else:
            pdf.set_font("Arial", "B", 12)
        if use_dejavu:
            pdf.cell(0, 10, "Спецификация перголы:", ln=True)
        else:
            pdf.cell(0, 10, "Pergola Specification:", ln=True)
        
        # Заголовки таблицы спецификации
        if use_dejavu:
            pdf.set_font("DejaVu", "B", 10)
        else:
            pdf.set_font("Arial", "B", 10)
        if use_dejavu:
            pdf.cell(130, 10, "Наименование", 1, 0)
            pdf.cell(60, 10, "Количество", 1, 1, align="C")
        else:
            pdf.cell(130, 10, "Item", 1, 0)
            pdf.cell(60, 10, "Quantity", 1, 1, align="C")
        
        # Данные таблицы спецификации
        if use_dejavu:
            pdf.set_font("DejaVu", "", 10)
        else:
            pdf.set_font("Arial", "", 10)
        
        for item in specification:
            name = item.get("name", "")
            count = item.get("count", "")
            
            # Упрощаем имена для ASCII
            name = name.replace("привод", "drive")
            name = name.replace("подсветка", "lighting")
            name = name.replace("лотка", "gutter")
            name = name.replace("усилитель", "reinforcement")
            name = name.replace("пульт", "remote")
            name = name.replace("ламели", "lamellas")
            name = name.replace("модуль", "module")
            
            # Создаем функцию для переноса текста на несколько строк
            def split_text_into_lines(text, max_width, font_size=10):
                """
                Разбивает текст на строки, которые помещаются в указанную ширину.
                Особенность: корректно обрабатывает длинные слова, разбивая их при необходимости.
                """
                lines = []
                
                # Предварительная обработка текста
                if not text:
                    return [""]
                
                # Если текст короткий, возвращаем его как есть
                if pdf.get_string_width(text) <= max_width:
                    return [text]
                
                # Корректируем ширину, добавляя небольшой запас
                effective_width = max_width - 2
                
                # Разбиваем текст на слова
                words = text.split()
                current_line = ""
                
                for word in words:
                    # Проверяем, поместится ли слово в текущую строку
                    test_line = current_line + (" " if current_line else "") + word
                    
                    if pdf.get_string_width(test_line) <= effective_width:
                        # Слово помещается - добавляем его к текущей строке
                        current_line = test_line
                    else:
                        # Слово не помещается - начинаем новую строку
                        
                        # Сначала сохраняем текущую строку
                        if current_line:
                            lines.append(current_line)
                        
                        # Проверяем, поместится ли само слово в строку
                        if pdf.get_string_width(word) <= effective_width:
                            # Слово помещается в новую строку
                            current_line = word
                        else:
                            # Слово слишком длинное - разбиваем его на части
                            current_part = ""
                            for char in word:
                                test_part = current_part + char
                                if pdf.get_string_width(test_part) <= effective_width:
                                    current_part = test_part
                                else:
                                    # Часть слова не помещается - добавляем в строки
                                    lines.append(current_part)
                                    current_part = char
                            
                            # Используем последнюю часть для текущей строки
                            current_line = current_part
                
                # Добавляем последнюю строку
                if current_line:
                    lines.append(current_line)
                
                # Если ни одной строки не получилось, добавляем пустую
                if not lines:
                    lines = [""]
                
                return lines
            
            # Получаем доступную ширину для текста (с учетом отступов)
            available_width = 120  # 130 - 10 отступы
            
            # Разбиваем текст на строки
            text_lines = split_text_into_lines(name, available_width)
            
            # Если текст нужно разбить на несколько строк
            if len(text_lines) > 1:
                # Сохраняем текущую позицию
                current_x = pdf.get_x()
                current_y = pdf.get_y()
                
                # Высота одной строки текста
                line_height = 6
                # Общая высота ячейки
                total_height = line_height * len(text_lines)
                
                # Рисуем ячейку для подсчета с полными границами
                pdf.set_xy(current_x + 130, current_y)
                pdf.cell(60, total_height, count, 1, 0, align="C")
                
                # Возвращаемся к начальной позиции
                pdf.set_xy(current_x, current_y)
                
                # Рисуем прямоугольник для текста
                pdf.rect(current_x, current_y, 130, total_height)
                
                # Выводим каждую строку текста
                for i, line in enumerate(text_lines):
                    pdf.set_xy(current_x + 2, current_y + i * line_height)  # +2 для отступа слева
                    pdf.cell(126, line_height, line, 0, 0, align="L")
                
                # Перемещаем позицию после всех ячеек
                pdf.set_xy(current_x, current_y + total_height)
            else:
                # Для однострочного текста используем обычный вывод
                pdf.cell(130, 10, name, 1, 0, align="L")
                pdf.cell(60, 10, count, 1, 1, align="C")
    
    
    
    # Добавляем примечания после таблиц
    pdf.ln(15)  # Отступ перед примечаниями
    
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 12)
    else:
        pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Примечания:" if use_dejavu else "Notes:", ln=True)
    
    # Настраиваем шрифт для текста примечаний
    if use_dejavu:
        pdf.set_font("DejaVu", "", 10)
    else:
        pdf.set_font("Arial", "", 10)
    
    # Добавляем каждое примечание отдельной строкой с нумерацией
    if use_dejavu:
        # Русская версия примечаний при наличии шрифта с кириллицей
        remarks = [
            "Расчет является предварительным и может быть уточнен при обращении в компанию.",
            "Срок действия предложения: 14 дней с даты расчета.",
            "Срок поставки: 6 недель с момента подтверждения заказа.",
            "Условия оплаты: 80% предоплата, 20% после монтажа."
        ]
    else:
        # Английская версия для совместимости
        remarks = [
            "The calculation is preliminary and may be clarified when contacting the company.",
            "Offer validity: 14 days from the calculation date.",
            "Delivery time: 6 weeks from the order confirmation.",
            "Payment terms: 80% prepayment, 20% after installation."
        ]
    
    for i, remark in enumerate(remarks, 1):
        pdf.cell(0, 7, f"{i}. {remark}", ln=True)
    
    # Дата с использованием московского времени
    from datetime import datetime
    import pytz
    
    # Определяем московскую временную зону
    moscow_tz = pytz.timezone('Europe/Moscow')
    now_utc = datetime.now(pytz.utc)
    now_moscow = now_utc.astimezone(moscow_tz)
    current_date = now_moscow.strftime("%d.%m.%Y")
    
    pdf.ln(10)
    
    # Добавляем разделительную линию перед колонтитулом
    pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
    pdf.ln(5)
    
    # Информация о компании
    if use_dejavu:
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(0, 8, "Компания \"Комфортный дом\"", ln=True, align="C")
    else:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Company \"Komfortny dom\"", ln=True, align="C")
    
    if use_dejavu:
        pdf.set_font("DejaVu", "I", 9)
        pdf.cell(0, 6, "Комплексные решения для террас, веранд и беседок.", ln=True, align="C")
        pdf.cell(0, 6, "ИП Гоноченко А.В. ОГРНИП 321619600249231", ln=True, align="C")
        pdf.cell(0, 6, "Тел.: +7-906-429-74-20 Сайт: pergolamarket.ru", ln=True, align="C")
    else:
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 6, "Complex solutions for terraces, verandas and gazebos.", ln=True, align="C")
        pdf.cell(0, 6, "IP Gonochenko A.V. OGRNIP 321619600249231", ln=True, align="C")
        pdf.cell(0, 6, "Tel.: +7-906-429-74-20 Website: pergolamarket.ru", ln=True, align="C")
    
    # Дата создания
    pdf.ln(5)
    if use_dejavu:
        pdf.set_font("DejaVu", "I", 8)
        pdf.cell(0, 6, f"Коммерческое предложение сформировано: {current_date}", ln=True, align="C")
    else:
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 6, f"Commercial offer generated on: {current_date}", ln=True, align="C")
    
    # Сохраняем PDF
    pdf.output(pdf_path)
    
    return pdf_path

def _results_hash():
    """Возвращает хеш текущих результатов для определения необходимости перегенерации PDF."""
    import hashlib, json
    results = st.session_state.get('results', {})
    key_data = json.dumps({
        'total_price': results.get('total_price', 0),
        'total_price_after_discount': results.get('total_price_after_discount', 0),
        'items': str(results.get('items', [])),
        'dimensions': str(results.get('dimensions', {})),
        'options': str(results.get('options', {})),
    }, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def export_to_pdf():
    """
    Генерирует PDF коммерческого предложения на основе данных расчёта.
    Кэширует результат — перегенерирует только при изменении результатов расчёта.
    
    Returns:
        tuple: (pdf_bytes, file_name) или (None, None) при ошибке
    """
    if 'results' not in st.session_state:
        return None, None
    
    current_hash = _results_hash()
    if (st.session_state.get('_pdf_hash') == current_hash 
            and st.session_state.get('_pdf_cache_bytes')):
        return st.session_state['_pdf_cache_bytes'], st.session_state['_pdf_cache_name']
    
    results = st.session_state.results
    options = results.get("options", {})
    dimensions = results.get("dimensions", {})
    
    os.makedirs("fonts", exist_ok=True)
    os.makedirs("processed_images", exist_ok=True)
    
    try:
        from pdf_generator_fpdf_rus import generate_commercial_offer, format_pergola_data_for_pdf
        
        pergola_data = format_pergola_data_for_pdf(results, options, dimensions, "")
        pdf_bytes = generate_commercial_offer(pergola_data)
        
        if not pdf_bytes:
            return None, None
        
        pergola_type = options.get("pergola_type", "pergola") or "pergola"
        width = round(float(dimensions.get("width", 0) or 0), 1)
        length = round(float(dimensions.get("length", 0) or 0), 1)
        
        import pytz
        rostov_tz = pytz.timezone('Europe/Moscow')
        current_date = datetime.now(pytz.utc).astimezone(rostov_tz).strftime("%d.%m.%Y")
        file_name = f"КП_пергола_{pergola_type}_{width}x{length}м_{current_date}.pdf"
        
        st.session_state['_pdf_hash'] = current_hash
        st.session_state['_pdf_cache_bytes'] = pdf_bytes
        st.session_state['_pdf_cache_name'] = file_name
        
        return pdf_bytes, file_name
        
    except Exception as e:
        print(f"Ошибка при генерации PDF: {str(e)}")
        return None, None



def display_image_with_padding(image_path, caption=None, padding_percent=5):
    """
    Отображает изображение с отступами по краям и подписью.
    
    Args:
        image_path (str): Путь к изображению
        caption (str, optional): Подпись к изображению
        padding_percent (int, optional): Процент отступа от ширины контейнера (по умолчанию 5%)
    """
    # Добавляем верхний отступ перед изображением
    st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
    
    # Создаем контейнер с отступами для изображения
    container = st.container()
    with container:
        # Применяем стиль для изображения
        if 'image_style_added' not in st.session_state:
            st.markdown(f"""
            <style>
            .image-container {{
                width: {100 - 2*padding_percent}%;
                margin: 0 auto;
                margin-top: 30px;
                margin-bottom: 20px;
            }}
            </style>
            """, unsafe_allow_html=True)
            st.session_state.image_style_added = True
        
        # Проверяем существование файла
        import os
        
        # Преобразуем путь в абсолютный, если он относительный
        # Это поможет при запуске на Replit или в другом окружении
        if not os.path.isabs(image_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            abs_image_path = os.path.join(base_dir, image_path)
        else:
            abs_image_path = image_path
        
        # Проверяем существование файла по абсолютному пути
        if not os.path.exists(abs_image_path):
            st.warning(f"Изображение не найдено: {image_path}")
            return
            
        # Отображаем изображение
        # Вместо параметра use_container_width=True используем width=None для занятия всей ширины
        try:
            st.image(abs_image_path, caption=caption, width=None)
        except Exception as e:
            st.warning(f"Ошибка при загрузке изображения: {e}")

def send_page_height_to_parent():
    """
    Добавляет JavaScript для отправки высоты страницы родительскому окну.
    Используется для адаптивного изменения высоты iframe после расчета.
    """
    st.markdown("""
    <script>
        // Функция для отправки высоты страницы родительскому окну
        function sendPageHeightToParent() {
            try {
                // Получаем высоту всего документа
                const pageHeight = Math.max(
                    document.body.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.clientHeight,
                    document.documentElement.scrollHeight,
                    document.documentElement.offsetHeight
                );
                
                // Добавляем немного отступа для надежности
                const heightWithPadding = pageHeight + 100;
                
                // Отправляем сообщение родительскому окну
                window.parent.postMessage({
                    height: heightWithPadding,
                    needsScroll: true,
                    timestamp: Date.now()
                }, '*');  // '*' - отправляем всем возможным родителям для надежности
                
                console.log('Sent page height to parent:', heightWithPadding);
                
                // Повторяем отправку через короткое время, чтобы убедиться, что высота корректна
                setTimeout(function() {
                    const updatedHeight = Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    ) + 100;
                    
                    window.parent.postMessage({
                        height: updatedHeight,
                        needsScroll: true,
                        timestamp: Date.now() + 1
                    }, '*');
                    
                    console.log('Updated page height sent to parent:', updatedHeight);
                }, 500);
                
                // Еще одна отправка через 1 секунду для надежности
                setTimeout(function() {
                    const finalHeight = Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    ) + 150;
                    
                    window.parent.postMessage({
                        height: finalHeight,
                        needsScroll: true,
                        timestamp: Date.now() + 2
                    }, '*');
                    
                    console.log('Final page height sent to parent:', finalHeight);
                }, 1000);
            } catch(e) {
                console.error('Error sending page height to parent:', e);
            }
        }
        
        // Прослушиваем сообщения от родительского окна
        window.addEventListener('message', function(event) {
            // Проверяем, запрашивает ли родитель высоту страницы
            if (event.data && event.data.type === 'REQUEST_HEIGHT') {
                sendPageHeightToParent();
            }
        });
        
        // Отправляем высоту при загрузке страницы
        window.addEventListener('load', function() {
            setTimeout(sendPageHeightToParent, 500);
        });
        
        // Отправляем высоту при изменении размера окна
        window.addEventListener('resize', function() {
            setTimeout(sendPageHeightToParent, 200);
        });
        
        // Выполняем отправку сразу после загрузки скрипта
        setTimeout(sendPageHeightToParent, 300);
        
        // Повторно отправляем высоту через 2 секунды для надежности
        setTimeout(sendPageHeightToParent, 2000);
    </script>
    """, unsafe_allow_html=True)

def add_common_script():
    """
    Добавляет универсальный JS-скрипт.
    Примечание: функция прокрутки удалена, т.к. теперь используется кастомный компонент из scroll.py
    Осталась только функция изменения высоты iframe, которая необходима для встраивания в Tilda.
    """
    st.markdown("""
    <script>
    console.log("💻 DEBUG: Инициализация скрипта add_common_script (обновленная версия)");
    
    // Автоизменение размера iframe (если вставлено в Tilda или другой сайт)
    function adjustHeight() {
        console.log("💻 DEBUG: Начинаю adjustHeight()");
        const height = document.documentElement.scrollHeight;
        console.log(`💻 DEBUG: Высота документа = ${height}px`);
        window.parent.postMessage({ type: "streamlit:height", height: height }, "*");
        console.log("💻 DEBUG: Отправлено сообщение изменения высоты родителю");
    }

    // Устаревшая функция для совместимости со старыми вставками
    function scrollToResultsWhenReady() {
        console.log("💻 DEBUG: Вызвана устаревшая функция scrollToResultsWhenReady()");
        console.log("💻 DEBUG: Скролл теперь обрабатывается компонентом из модуля scroll.py");
        // Функция оставлена для обратной совместимости, но ничего не делает
    }

    // Установим слушатель событий для хеша в URL (только для обратной совместимости)
    window.addEventListener('hashchange', function() {
        console.log(`💻 DEBUG: Обнаружено изменение хеша в URL: ${window.location.hash}`);
        // Функционал обрабатывается компонентом из модуля scroll.py
    });

    // Запускаем после загрузки страницы (только изменение высоты)
    setTimeout(() => {
        console.log("💻 DEBUG: Страница загружена, выполняю основные функции");
        
        // Всегда подгоняем размер фрейма
        adjustHeight();
        
        console.log("💻 DEBUG: Функция скролла переведена на модуль scroll.py");
    }, 300);
    </script>
    """, unsafe_allow_html=True)

# Обновленная функция, использующая скрипт JavaScript для прокрутки к якорю
def scroll_to_results():
    """
    Использует JavaScript для прокрутки к элементу с ID "scroll-target".
    """
    # Добавляем отладочное сообщение для трассировки вызовов
    st.markdown("""
    <script>
        console.log("🔄 DEBUG: Вызвана scroll_to_results(), используется скролл к якорю");
    </script>
    """, unsafe_allow_html=True)
    
    # Создаем якорь перед результатами, если его еще нет
    st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)
    
    # Добавляем скрипт для скролла к якорю
    st.markdown("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            try {
                const target = document.getElementById('scroll-target');
                if (target) {
                    setTimeout(() => {
                        target.scrollIntoView({ behavior: 'auto', block: 'start' });
                        console.log("🚀 Выполнен скролл к якорю #scroll-target");
                    }, 300);
                }
            } catch(e) {
                console.error("Ошибка скролла:", e);
            }
        });
    </script>
    """, unsafe_allow_html=True)

def add_smart_device_adaptation():
    """
    Добавляет умную адаптацию для различных размеров экрана.
    Определяет тип устройства (смартфон, планшет, ноутбук) и применяет соответствующие стили.
    """
    st.markdown("""
    <script>
        // Функция для определения типа устройства и добавления классов
        function detectDeviceAndAddClass() {
            const width = window.innerWidth;
            const html = document.documentElement;
            
            // Удаляем предыдущие классы устройств
            html.classList.remove('device-smartphone', 'device-tablet', 'device-laptop', 'device-desktop');
            
            // Добавляем соответствующий класс на основе ширины экрана
            if (width <= 480) {
                html.classList.add('device-smartphone');
                console.log('Device detected: Smartphone');
            } else if (width <= 768) {
                html.classList.add('device-tablet');
                console.log('Device detected: Tablet');
            } else if (width <= 1200) {
                html.classList.add('device-laptop');
                console.log('Device detected: Laptop');
            } else {
                html.classList.add('device-desktop');
                console.log('Device detected: Desktop');
            }
            
            // Также добавляем классы для более точной настройки
            // Вертикальная ориентация (портретная)
            if (window.innerHeight > window.innerWidth) {
                html.classList.add('orientation-portrait');
                html.classList.remove('orientation-landscape');
            } else {
                // Горизонтальная ориентация (альбомная)
                html.classList.add('orientation-landscape');
                html.classList.remove('orientation-portrait');
            }
        }
        
        // Выполняем функцию при загрузке документа
        document.addEventListener('DOMContentLoaded', detectDeviceAndAddClass);
        
        // Также выполняем сразу для случая, когда DOM уже загружен
        detectDeviceAndAddClass();
        
        // Обновляем классы при изменении размера окна
        window.addEventListener('resize', detectDeviceAndAddClass);
    </script>
    
    <style>
    /* Умная адаптация для различных размеров экрана */
    
    /* Предотвращение горизонтальной прокрутки на всех устройствах */
    html, body {
        width: 100%;
        max-width: 100%;
        overflow-x: hidden !important;
    }
    
    .main, .block-container, .stApp {
        width: 100%;
        max-width: 100%;
        overflow-x: hidden !important;
    }
    
    /* Стили для всех устройств (базовые) */
    :root {
        --spacing-base: 0.5rem;
        --font-size-base: 1rem;
        --input-padding: 0.5rem;
        --container-padding: 1rem;
    }
    
    /* Базовые улучшения для всех устройств */
    .stApp [data-testid="stVerticalBlock"] {
        gap: var(--spacing-base) !important;
    }
    
    .stCheckbox, .stRadio {
        line-height: 1.2 !important;
    }
    
    /* Стили для блоков с адаптивными классами */
    .dimensions-form {
        margin-bottom: 0.5rem;
    }
    
    .lighting-options {
        padding: 0;
        margin-bottom: 0.3rem;
    }
    
    /* Уменьшаем отступы для всех полей ввода */
    div.stNumberInput, div.stTextInput, div.stSelectbox,
    div.stRadio, div.stCheckbox, div.stSlider, div.stButton {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Стили для смартфонов */
    .device-smartphone .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
    }
    
    /* Специальные стили для блоков с формой размеров на смартфонах */
    .device-smartphone .dimensions-form {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .device-smartphone .dimensions-form [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .device-smartphone h1 {
        font-size: 1.2rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    .device-smartphone h2, 
    .device-smartphone h3 {
        font-size: 1.0rem !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    .device-smartphone p, 
    .device-smartphone li,
    .device-smartphone label {
        font-size: 0.75rem !important;
        line-height: 1.1 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Сверхкомпактная форма ввода для смартфонов */
    .device-smartphone .stRadio > div {
        padding: 0.1rem !important;
    }
    
    .device-smartphone .stRadio label {
        padding: 0.05rem !important;
    }
    
    .device-smartphone .stCheckbox > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    .device-smartphone .stButton > button {
        padding: 0.25rem 0.8rem !important;
    }
    
    /* Супер-компактные отступы между элементами формы */
    .device-smartphone [data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
    }
    
    /* Оптимизация для радио-кнопок */
    .device-smartphone .stRadio [data-testid="stHorizontalBlock"] > div {
        min-width: auto !important;
        margin-right: 10px !important;
    }
    
    /* Оптимизация для полей ввода */
    .device-smartphone .stNumberInput input {
        padding: 0.2rem !important;
        height: 1.8rem !important;
    }
    
    /* Более компактный размер для заголовка страницы */
    .device-smartphone h1[style*="text-align: center"] {
        font-size: 1.1rem !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Уменьшение размера подзаголовка */
    .device-smartphone p[style*="text-align: center"] {
        font-size: 0.7rem !important;
        margin-top: 0 !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* Сверхкомпактные отступы для всех вертикальных блоков */
    .device-smartphone [data-testid="stVerticalBlock"] > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Специальная оптимизация для блока подсветки на смартфонах */
    .device-smartphone .lighting-options [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    
    .device-smartphone .lighting-options .stCheckbox {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    
    /* Оптимизация для стиля кнопки на смартфонах */
    .device-smartphone button[data-testid="baseButton-primary"] {
        margin-top: 0.2rem !important;
    }
    
    /* Стили для планшетов */
    .device-tablet .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    .device-tablet h1 {
        font-size: 1.5rem !important;
    }
    
    .device-tablet h2,
    .device-tablet h3 {
        font-size: 1.2rem !important;
    }
    
    .device-tablet p,
    .device-tablet li,
    .device-tablet label {
        font-size: 0.85rem !important;
    }
    
    /* Стили для ноутбуков */
    .device-laptop .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Стили для настольных компьютеров */
    .device-desktop .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Основная функция приложения"""
    # Импортируем модуль для плавающих кнопок
    from floating_buttons import add_results_navigation_button, add_dimensions_edit_button
    # Импортируем модуль для прямого внедрения кнопок
    from direct_buttons import inject_direct_buttons
    
    # Настраиваем страницу - это должно быть первой командой Streamlit
    st.set_page_config(
        page_title="Калькулятор биоклиматических пергол DecoLife",
        page_icon="🏠",
        layout="centered",  # Изменено с "wide" на "centered" для более узкого интерфейса
        initial_sidebar_state="collapsed"  # Боковая панель будет свернута по умолчанию
    )
    
    # Удаляем лишние отступы вверху страницы после настройки страницы
    # для минимизации отступа между верхним краем и заголовком
    remove_padding_top()
    
    # Определяем, запущено ли приложение в iframe, и адаптируем интерфейс
    in_iframe = adapt_for_iframe()
    
    # Добавляем дополнительные оптимизации для iframe
    if in_iframe:
        # Если в iframe, применяем специальные оптимизации
        st.session_state['iframe_mode'] = True
        optimize_for_iframe()
    
    # Добавляем CSS-оптимизации для ускорения загрузки контента
    st.markdown(add_content_visibility_optimizations(), unsafe_allow_html=True)
    
    # Добавляем общие оптимизации страницы для быстрой загрузки
    st.markdown(add_page_speed_optimizations(), unsafe_allow_html=True)
    
    # Определяем критически важные изображения для быстрой первоначальной загрузки
    critical_images = [
        "attached_assets/b500_rotation.png",
        "attached_assets/linear_drive_b500.png"
    ]
    
    # Второстепенные изображения, загружаемые с задержкой для ускорения отображения формы
    secondary_images = [
        "attached_assets/b700_sliding.png",
        "attached_assets/b600_sandwich.png",
        "attached_assets/somfy_pergola_b700.jpg"
    ]
    
    # Добавляем оптимизированную многоуровневую загрузку изображений
    st.markdown(optimize_images_loading(
        critical_images=critical_images,
        secondary_images=secondary_images
    ), unsafe_allow_html=True)
    
    # Предварительно загружаем только критические изображения для быстрого отображения
    # Используем кэш в памяти для предотвращения повторной обработки при обновлении страницы
    if 'images_preloaded' not in st.session_state:
        # Загружаем только критические изображения сначала для ускорения начальной загрузки
        for img_path in critical_images:
            if os.path.exists(img_path):
                # Извлекаем имя файла без пути и расширения
                file_name = img_path.split('/')[-1]
                base_name = file_name.split('.')[0]
                
                # Используем функцию для предварительной загрузки изображения в кэш
                # Передаем стандартный тип перголы "B500NEW" для загрузки базовых изображений
                get_optimized_pergola_images("B500NEW")
        st.session_state['images_preloaded'] = True
    
    # Добавляем оптимизацию для форм, чтобы пользователь мог быстрее вводить данные
    st.markdown(optimize_form_rendering(), unsafe_allow_html=True)
    
    # Добавляем оптимизацию последовательности загрузки для приоритизации формы ввода
    st.markdown(optimize_startup_sequence(), unsafe_allow_html=True)
    
    # Импортируем компоненты для аутентификации администратора
    from components.admin_auth import admin_login_form
    
    # Инициализируем переменные состояния сессии для аутентификации
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    if "auth_error" not in st.session_state:
        st.session_state.auth_error = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "last_attempt_time" not in st.session_state:
        st.session_state.last_attempt_time = 0
    
    # Добавляем форму авторизации в боковую панель
    admin_login_form(location="sidebar")
    
    # Добавляем глобальные CSS-стили для улучшения скролла и анимаций
    st.markdown("""
    <style>
    html {
        scroll-behavior: smooth !important;
        overflow-y: scroll;
    }
    
    body, .main {
        height: auto !important;
        min-height: 100vh;
    }
    
    /* Убираем лишние отступы */
    .block-container {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* Улучшенный скролл для Safari и других браузеров */
    body {
        -webkit-overflow-scrolling: touch;
    }
    
    /* Стили для обеспечения видимости элементов при скролле */
    #results-section {
        display: block;
        min-height: 50px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Добавляем умную адаптацию для различных размеров экрана
    add_smart_device_adaptation()
    
    # Добавляем код счетчика Яндекс.Метрики
    add_yandex_metrika()
    
    # Добавляем прямые плавающие кнопки навигации (новый метод)
    # Проверяем, что мы не на странице администрирования
    # Используем только один метод работы с query_params - новый API
    page_param = st.query_params.get("_stcore_page_id")
    current_path = "main"  # значение по умолчанию
    
    if page_param is not None:
        current_path = page_param.lower()
        
    if not any(admin_term in current_path for admin_term in ["admin", "prices_admin", "promotions_admin"]):
        inject_direct_buttons()
    
    # Добавляем общий JavaScript скрипт для автоматического изменения высоты и прокрутки
    add_common_script()
    
    if st.session_state.get('set_hash_to_results', False):
        st.session_state.set_hash_to_results = False
    
    # Проверяем, нужно ли отправить событие в Яндекс.Метрику
    if st.session_state.get('send_ya_metrika_event', False):
        # Отправляем событие через JavaScript
        send_calc_success_event()
        # Сбрасываем флаг, чтобы не отправлять событие снова
        st.session_state.send_ya_metrika_event = False
    
    # Задаем стили для компактного и читаемого интерфейса по новому дизайну
    # Уменьшаем отступы между формами ввода для более компактного вида
    st.markdown("""
    <style>
    /* Глобальный контейнер */
    .block-container {
        max-width: 800px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        margin: 0 auto;
    }
    
    /* Применяем стандартные отступы для форм ввода */
    div.stNumberInput, div.stTextInput, div.stSelectbox, div.stRadio, 
    div.stCheckbox, div.stSlider, div.stButton, div.stMultiselect {
        width: 95% !important;
        margin: 0 auto !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        margin-top: 2px !important;
        margin-bottom: 2px !important;
    }
    
    /* Отступы для секций заголовков */
    div.stMarkdown h2 {
        width: 95% !important;
        margin: 0 auto !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
    }
    
    /* Отступы для всех заголовков в статьях */
    div.stMarkdown h1, div.stMarkdown h2, div.stMarkdown h3, div.stMarkdown h4, div.stMarkdown h5, div.stMarkdown h6 {
        padding-left: 0px !important;
        padding-right: 0px !important;
    }
    
    /* Отступы для текстовых параграфов (общие) */
    div.stMarkdown p {
        width: 95% !important;
        margin: 0 auto !important;
    }
    
    /* Специальные отступы только для параграфов в контейнере description-container */
    .description-container p {
        padding-left: 0px !important;
        padding-right: 0px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        width: 100% !important;
        background-color: rgba(240, 240, 240, 0.2) !important; /* Немного выделяем параграфы для отладки */
    }
    
    /* Отступы для списков в статьях */
    div.stMarkdown ul, div.stMarkdown ol {
        width: 95% !important;
        margin: 0 auto !important;
        padding-left: 15px !important; /* Небольшой отступ для маркеров списка */
        padding-right: 0px !important;
    }
    
    /* Отступы для горизонтальных разделителей */
    div.stMarkdown hr {
        width: 95% !important;
        margin: 0 auto !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    
    /* Глобальные стили для улучшения читаемости */
    .stApp, .stApp p, .stApp div {
        font-size: 1rem;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 2.0rem;
        font-weight: 600;
        color: #0066cc;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Таблицы */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }
    
    th, td {
        padding: 8px 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    
    th {
        background-color: #f8f9fa;
        font-weight: 600;
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .block-container {
            max-width: 100%;
            padding: 0.25rem !important;
        }
        
        /* Устанавливаем нормальные отступы на мобильных */
        div.stNumberInput, div.stTextInput, div.stSelectbox, div.stRadio, 
        div.stCheckbox, div.stSlider, div.stButton, div.stMultiselect,
        div.stMarkdown h2, div.stMarkdown p, div.stMarkdown hr {
            width: 95% !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
            margin-top: 3px !important;
            margin-bottom: 3px !important;
        }
        
        .stButton {
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
        
        /* Убираем горизонтальный скролл на мобильных */
        html, body, .stApp, .main, .block-container, 
        div.gallery-container, div[data-testid="stTable"],
        div[data-testid="stDataFrame"], section[data-testid="stVerticalBlock"] {
            width: 100% !important;
            max-width: 100% !important;
            overflow-x: hidden !important;
        }
        
        /* Уменьшаем размер шрифта в элементах форм */
        .stSelectbox, .stRadio, .stCheckbox {
            font-size: 0.8rem !important;
        }
        
        /* Уменьшаем размер текста везде */
        .stApp, .stApp p, .stApp div, .stMarkdown {
            font-size: 0.85rem !important;
        }
        
        /* Делаем строки радио-кнопок и чекбоксов более компактными */
        div.stRadio > div[data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;
        }
        
        /* Уменьшаем отступы между чекбоксами */
        .stCheckbox {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Уменьшаем отступы внутри колонок */
        div.column {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Уменьшаем вертикальный размер полей ввода */
        input, select, button {
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок калькулятора - крупный и четкий
    # Добавляем стили для уменьшения отступов страницы
    st.markdown("""
    <style>
    /* Уменьшаем отступы в начале страницы */
    .main .block-container {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }
    /* Уменьшаем отступы для заголовков */
    h1 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    /* Уменьшаем отступы для всех элементов Streamlit */
    .stHeadingContainer {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок с минимальным отступом
    st.markdown("<h1 style='text-align: center; margin-top: 0px; margin-bottom: 5px; font-size: 2.1rem; font-weight: 600; color: #0066cc;'>Калькулятор расчета стоимости биоклиматических пергол</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 10px; font-size: 1rem;'>Введите размеры и параметры перголы для расчета стоимости в рублях (₽)</p>", unsafe_allow_html=True)
    
    # 1. ПЕРВЫМ - Выбор типа перголы
    st.markdown('<div id="pergola-type-form"></div>', unsafe_allow_html=True)
    pergola_type = render_pergola_type_form()
    
    # 2. ВТОРЫМ - Выбор типа ламелей (зависит от типа перголы)
    st.markdown('<div id="lamella-type-form"></div>', unsafe_allow_html=True)
    lamella_type = render_lamella_type_form()
    
    # 3. ТРЕТЬИМ - Размеры перголы (после выбора типа перголы и ламелей)
    st.markdown('<div id="dimensions-form"></div>', unsafe_allow_html=True)
    dimensions = render_dimensions_form()
    
    # 4. ЧЕТВЕРТЫМ - Дополнительные опции (освещение, установка)
    st.markdown('<div id="additional-options-form"></div>', unsafe_allow_html=True)
    additional_options = render_additional_options_form()
    
    # Собираем все опции в один словарь
    options = {
        "pergola_type": pergola_type,
        "lamella_type": lamella_type,
        "lighting": additional_options["lighting"],
        "installation": additional_options["installation"]
    }
    
    # Сохраняем размеры в session_state
    st.session_state.dimensions = dimensions
    
    # Добавляем отступ перед кнопкой расчета
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Используем прямое создание кнопки с нашими стилями для большей надежности
    st.markdown("""
    <style>
    /* Улучшенный стиль для кнопки калькулятора */
    div.stButton > button:first-child {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100%;
        height: 70px !important;
        background-color: #0066cc !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
        margin: 15px 0 !important;
        cursor: pointer;
        animation: pulse-button 1s infinite !important;
        letter-spacing: 0.8px !important;
        border: none !important;
        text-transform: uppercase !important;
        padding: 0 !important;
    }
    
    div.stButton > button:first-child p {
        margin: 0 !important;
        padding: 0 !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    @keyframes pulse-button {
        0% { transform: scale(1) translateY(0); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); background-color: #0066cc !important; }
        50% { transform: scale(1.08) translateY(-8px); box-shadow: 0 10px 25px rgba(0, 102, 204, 0.6); background-color: #0088ff !important; }
        100% { transform: scale(1) translateY(0); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); background-color: #0066cc !important; }
    }
    </style>
    
    <script>
    // Для обеспечения анимации также через JavaScript
    document.addEventListener('DOMContentLoaded', function() {
        function animateCalculateButton() {
            setTimeout(function() {
                const buttons = document.querySelectorAll('div.stButton > button');
                if (buttons.length > 0) {
                    const calculationButton = buttons[0]; // первая кнопка - это кнопка расчета
                    
                    // Добавляем стили для анимации и выравнивания текста по центру
                    calculationButton.style.backgroundColor = '#0066cc';
                    calculationButton.style.fontSize = '20px';
                    calculationButton.style.fontWeight = '900';
                    calculationButton.style.height = '70px';
                    calculationButton.style.letterSpacing = '0.8px';
                    calculationButton.style.textTransform = 'uppercase';
                    calculationButton.style.display = 'flex';
                    calculationButton.style.justifyContent = 'center';
                    calculationButton.style.alignItems = 'center';
                    
                    // Центрируем текст внутри кнопки
                    const buttonText = calculationButton.querySelector('p');
                    if (buttonText) {
                        buttonText.style.margin = '0';
                        buttonText.style.padding = '0';
                        buttonText.style.textAlign = 'center';
                        buttonText.style.width = '100%';
                    }
                    
                    // Запускаем анимацию
                    let direction = 1;
                    let scale = 1;
                    let translateY = 0;
                    setInterval(function() {
                        scale += 0.005 * direction;
                        translateY += 0.4 * direction;
                        
                        if (scale >= 1.08) direction = -1;
                        if (scale <= 1) direction = 1;
                        
                        calculationButton.style.transform = `scale(${scale}) translateY(${-translateY}px)`;
                        calculationButton.style.boxShadow = `0 ${4 + translateY * 2}px ${10 + translateY * 2}px rgba(0, 102, 204, ${0.3 + translateY * 0.03})`;
                    }, 50);
                }
            }, 1000); // Даем время Streamlit отрендерить кнопку
        }
        
        animateCalculateButton();
        
        // Для случаев, когда DOM обновляется
        const observer = new MutationObserver(animateCalculateButton);
        observer.observe(document.body, { subtree: true, childList: true });
    });
    </script>
    <style>
    </style>
    """, unsafe_allow_html=True)
    
    # Добавляем CSS для анимации кнопки (применяется через класс)
    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        height: 55px;
        background-color: #0066cc;
        color: white;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        animation: pulse-button 2s ease-in-out infinite;
        text-transform: uppercase;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        width: 100%;
    }
    
    /* Более тонкая и медленная анимация */
    @keyframes pulse-button {
        0% { transform: scale(1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); background-color: #0066cc; }
        50% { transform: scale(1.03); box-shadow: 0 6px 15px rgba(0, 102, 204, 0.4); background-color: #0077dd; }
        100% { transform: scale(1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); background-color: #0066cc; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Добавляем стили для кнопки, чтобы текст отображался в одну строку
    st.markdown("""
    <style>
    /* Стили для кнопки "РАССЧИТАТЬ СТОИМОСТЬ" */
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
        white-space: nowrap !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 1rem !important;
        min-width: 300px !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important; /* Добавлено для вертикального центрирования */
        height: 60px !important; /* Задаем фиксированную высоту */
    }
    
    /* Стили для текста внутри кнопки */
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"] p {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        display: inline-block !important;
        margin: auto !important; /* Центрирование по вертикали */
        padding: 0 !important; /* Убираем отступы */
        line-height: 1 !important; /* Уменьшаем межстрочный интервал */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Добавляем CSS для кнопки, чтобы текст был в одну строку и кнопка по центру
    st.markdown("""
    <style>
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
        margin: 0 auto;
    }
    
    div[data-testid="stButton"] > button {
        width: auto !important;
        min-width: 300px !important;
        max-width: 400px !important;
        white-space: nowrap !important;
        padding: 0.5rem 1rem !important;
        height: 60px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    div[data-testid="stButton"] > button p {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        font-size: 1.1rem !important;
        line-height: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Кнопка по центру, без использования колонок
    calculate_button = st.button("РАССЧИТАТЬ СТОИМОСТЬ", key="calc_button", 
                              type="primary", 
                              help="Нажмите, чтобы рассчитать стоимость перголы")
    
    # Обрабатываем нажатие на кнопку
    if calculate_button:
        with st.spinner("Выполняется расчет..."):
            # Проверяем, что у нас есть данные для расчета
            if dimensions and options:
                # Выполняем расчет
                results = perform_calculation(dimensions, options)
                
                # Сохраняем результаты и опции в состоянии сессии
                # Инициализируем переменную results, если не был выполнен расчет
                if 'results' not in locals():
                    results = {}
                
                st.session_state.results = results
                
                st.session_state.show_floating_buttons = True
                st.session_state.options = options
                
                # Включаем автоматический скролл к результатам
                st.session_state.scroll_to_results = True
                
                # Сбрасываем флаг описания, чтобы оно обновлялось при каждом новом расчете
                st.session_state.description_shown = False
                
                # Устанавливаем флаг для отправки события в Яндекс.Метрику
                st.session_state.send_ya_metrika_event = True
                
                # Запоминаем, что нужно установить хэш #results
                st.session_state.set_hash_to_results = True
                
                # Добавляем отладочную информацию для проверки состояния флага
                st.markdown(f"""
                <script>
                    console.log("✅ DEBUG: Расчет завершен, show_floating_buttons = {st.session_state.show_floating_buttons}");
                </script>
                """, unsafe_allow_html=True)
                
                pass
    
    # Добавляем разделитель (компактный)
    st.markdown("<hr style='margin-top: 0.2rem; margin-bottom: 0.2rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    
    # Здесь был код для создания якоря, теперь используем только компонент scroll.py
        
    # Отображаем результаты (если есть)
    if 'results' in st.session_state:
        st.markdown('<div id="scroll-target-results" style="height:0;margin:0;padding:0;"></div>', unsafe_allow_html=True)
        
        render_results(st.session_state.results, show_articles=False)
        
        if st.session_state.get('scroll_to_results', False):
            smooth_scroll_to('scroll-target-price', center=True)
            st.session_state.scroll_to_results = False
        
        # Добавляем кнопку навигации к результатам расчета
        add_results_navigation_button()
        
        # Добавляем кнопку для возврата к форме размеров
        add_dimensions_edit_button()
    
    # Добавляем стили для уменьшения вертикального пробела между результатами и галереей
    st.markdown("""
    <style>
    /* Уменьшаем отступы между результатами и галереей - глобальное правило */
    [data-testid="stVerticalBlock"] > div:last-child > div {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Минимизируем все отступы внизу таблицы */
    .stTable {
        margin-bottom: 0 !important;
    }
    
    /* Применяем крайне минимальные отступы для всех элементов галереи */
    .gallery-container {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Дополнительные правила для удаления отступов между секциями */
    [data-testid="stVerticalBlock"] > div:nth-last-child(2) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Компактные стили для кнопки экспорта PDF */
    [data-testid="baseButton-secondary"] {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Уменьшение отступов для заголовка галереи */
    h1 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Супер-компактные стили для разделителей */
    hr {
        margin: 0 !important;
        padding: 0 !important;
        height: 1px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Всегда отображаем галерею проектов и счетчик установленных пергол
    display_gallery_section()
    
    # Добавляем информацию о версии внизу страницы (компактно)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.3rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #999;'>© 2025 Комфортный дом | Калькулятор пергол v4.7.7</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    # Создаем директории, если они не существуют
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/price_tables", exist_ok=True)
    
    # Запускаем приложение
    main()