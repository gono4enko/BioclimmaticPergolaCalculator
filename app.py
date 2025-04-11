"""
Калькулятор стоимости пергол - базовая версия без сложных стилей и модификаций
Максимально простой подход с использованием стандартных компонентов Streamlit
"""
import streamlit as st
import pandas as pd
# Импортируем функции для работы с Яндекс.Метрикой
from add_yandex_metrika import add_yandex_metrika, send_calc_success_event
import os
import math
import csv
import time
from datetime import datetime

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
from pdf_generator_fpdf import generate_commercial_offer, format_pergola_data_for_pdf
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
    "B500NEW": {"width": 15.0, "length": 8.0},
    "B700NEW": {"width": 15.0, "length": 7.25},
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

# Наценки за доставку и установку (в процентах от базовой стоимости)
DELIVERY_MARKUP_PERCENT = 10  # 10% наценка за доставку (добавляется автоматически)
INSTALLATION_MARKUP_PERCENT = 10  # 10% наценка за установку (опционально)

# Курс евро в рублях
EURO_RATE = 110  # 1 евро = 110 рублей

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
                # Добавляем блоки управления освещением - по одному на каждый модуль
                devices_count += modules  # Каждый модуль требует отдельного канала для освещения
            
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
            
            # Блок управления освещением - по 1 блоку на каждый модуль
            if has_lighting:
                # Количество блоков управления зависит от количества модулей
                controllers_count = modules
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
            # Добавляем блок управления освещением - по 1 блоку на каждый модуль
            specification.append({
                "name": "Блок управления освещением Somfy RTS Dimmer",
                "count": f"{modules} шт.",
                "price": ""
            })
            
            # Увеличиваем счетчик устройств для определения типа пульта
            lighting_devices_count = modules  # По 1 блоку управления на каждый модуль
            
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
        
        # Добавляем наценку за доставку (10% автоматически)
        delivery_price = round(base_total_price * 0.1, 2)
        results["delivery"] = {
            "percentage": 10,
            "price": delivery_price
        }
        results["items"].append({
            "name": "Доставка",
            "price": delivery_price
        })
        results["total_price"] += delivery_price
        
        # Добавляем наценку за установку (10%, если выбрана опция)
        if installation:
            installation_price = round(base_total_price * 0.1, 2)
            results["installation"] = {
                "selected": True,
                "percentage": 10,
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

def get_modules_by_dimensions(width, length, pergola_type=None):
    """
    Определяет количество модулей в зависимости от размеров перголы и ее типа.
    Учитывает как ширину, так и вынос (длину) перголы.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str, optional): Тип перголы
        
    Returns:
        int: Количество модулей
    """
    # Особые правила для больших выносов
    if length > 6.0:
        if width <= 4.5:
            return 2  # Для выноса > 6.0м даже при малой ширине нужно 2 модуля
        elif width <= 9.0:
            return 2  # Для ширины 5-9м - 2 модуля
        else:
            return 3  # Для ширины 9.5м и более - 3 модуля
    
    # Стандартные правила по ширине
    if width <= 4.5:
        return 1  # Для ширины до 4.5м - 1 модуль
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

def render_dimensions_form():
    """
    Отображает форму для ввода размеров перголы
    
    Returns:
        dict: Словарь с введенными размерами
    """
    st.markdown("<h2 class='section-header' style='text-align: center; margin-bottom: 5px;'>Размеры перголы</h2>", unsafe_allow_html=True)
    
    # Начало блока с классом dimensions-form для умной адаптации
    st.markdown("<div class='dimensions-form'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        width = st.number_input(
            "Ширина (м)",
            min_value=2.0,
            max_value=15.0,
            value=3.0,
            step=0.5,
            format="%.2f",
            help="Ширина перголы в метрах (2.0 - 15.0 м)"
        )
    
    with col2:
        length = st.number_input(
            "Вынос (м)",
            min_value=2.0,
            max_value=8.0,
            value=4.0,
            step=0.5,
            format="%.2f",
            help="Глубина (вынос) перголы в метрах (2.0 - 8.0 м)"
        )
    
    # Определяем количество модулей автоматически по обоим параметрам - ширине и выносу
    modules = get_modules_by_dimensions(width, length)
    
    # Показываем информацию о модулях (только для отображения) с уменьшенным отступом
    if modules > 1:
        st.markdown(f"""<div style="padding: 5px 10px; background-color: #e6f3ff; border-radius: 3px; font-size: 0.85rem; margin: 2px 0;">
        При размере {width:.2f}×{length:.2f} м будет автоматически использовано {modules} {get_plural_form(modules, 'модуль', 'модуля', 'модулей')}
        </div>""", unsafe_allow_html=True)
    
    # Закрываем блок с классом dimensions-form
    st.markdown("</div>", unsafe_allow_html=True)
    
    return {
        "width": width,
        "length": length,
        "modules": modules
    }

def render_options_form():
    """
    Отображает форму для выбора опций перголы в плиточном дизайне
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    st.markdown("<h2 class='section-header' style='text-align: center; margin-bottom: 5px;'>Параметры перголы</h2>", unsafe_allow_html=True)
    
    # Тип перголы
    pergola_type = st.radio(
        "Выберите тип перголы",
        options=list(PERGOLA_TYPES.keys()),
        format_func=lambda x: PERGOLA_TYPES.get(x, x),
        horizontal=True
    )
    
    # Тип ламелей - зависит от выбранного типа перголы
    lamella_options = []
    if pergola_type == "B500NEW":
        lamella_options = ["B500-25NEW", "B500-20NEW"]  # Стандартные 250 мм первыми
    elif pergola_type == "B700NEW":
        lamella_options = ["B700-25NEW", "B700-20NEW"]  # Стандартные 250 мм первыми
    elif pergola_type == "B600":
        lamella_options = ["B600-PIR"]
    
    lamella_type = st.radio(
        "Выберите тип ламелей",
        options=lamella_options,
        format_func=lambda x: LAMELLA_TYPES.get(x, x),
        horizontal=True
    )
    
    # Освещение - без лишних отступов, с CSS классом для адаптивности
    st.markdown("<p style='font-weight: 500; margin-bottom: 0px; margin-top: 0px;'>Освещение</p>", unsafe_allow_html=True)
    
    # Начало блока с классом lighting-options для умной адаптации
    st.markdown("<div class='lighting-options'>", unsafe_allow_html=True)
    
    lighting_options = []
    col1, col2 = st.columns(2)
    
    with col1:
        if st.checkbox("Белая светодиодная лента", value=False, key="white_led_checkbox", label_visibility="visible"):
            lighting_options.append("white_led")
    
    with col2:
        if st.checkbox("RGB светодиодная лента", value=False, key="rgb_led_checkbox", label_visibility="visible"):
            lighting_options.append("rgb_led")
    
    # Закрытие блока с классом lighting-options
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Установка - с минимальным отступом
    st.markdown("<p style='font-weight: 500; margin-bottom: 0px; margin-top: 0px;'>Установка</p>", unsafe_allow_html=True)
    
    installation = st.checkbox("С установкой", value=True, key="installation_checkbox", label_visibility="visible")
    
    # Возвращаем выбранные опции (не включаем модули, т.к. они рассчитываются автоматически)
    return {
        "pergola_type": pergola_type,
        "lamella_type": lamella_type,
        "lighting": lighting_options,
        "installation": installation
    }

def render_results(results):
    """
    Отображает результаты расчета стоимости перголы
    
    Args:
        results (dict): Словарь с результатами расчета
    """
    # Импортируем модуль отображения акций
    from components.promotion_display import promotions_section
    
    # Создаем якорь для скролла с ID 
    st.markdown('<div id="results" name="results"></div>', unsafe_allow_html=True)
    
    # Добавляем JavaScript для отправки высоты страницы родительскому окну после загрузки результатов
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
    euro_rate = EURO_RATE
    total_price = results["total_price"]
    
    # Рассчитываем общую стоимость опций для определения скидок
    options_price = total_price - base_price
    
    # Отображаем акции и считаем скидку перед отображением результатов
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 2.0rem; font-weight: 600; color: #0066cc; margin-top: 10px; margin-bottom: 15px;'>Акции и скидки</h3>", unsafe_allow_html=True)
    
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
        <div style='font-size: 1.4rem; color: #0066cc; font-weight: 700; margin-top: 15px; padding-top: 10px; border-top: 1px solid #e0e0e0; text-align: center;'>
            Итоговая стоимость: <span style='font-size: 1.5rem; color: #0066cc;'>{formatted_price} ₽</span>
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
        if "освещен" in item["name"].lower() or "лента" in item["name"].lower():
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
    
    # Проверяем, есть ли скидка
    rub_total = total_price * euro_rate
    if "discount" in results and results["discount"] > 0:
        # Добавляем строку со скидкой (скидка отображается зеленым цветом)
        discount_amount = results["discount"]
        items_data.append(["Скидка по акции", f"-{format_price(discount_amount)}"])
        # Обновляем итоговую сумму с учетом скидки
        rub_total = results.get("total_price_after_discount", rub_total - discount_amount)
    
    # Итоговая строка
    items_data.append(["Итого", format_price(rub_total)])
    
    # Добавляем строку с весенней акцией до 1 июня (если скидка > 0)
    if "discount" in results and results["discount"] > 0:
        # Добавляем строку с ценой после скидки
        final_price = results.get("total_price_after_discount", rub_total)
        items_data.append(["Весенняя акция до 1.06.2025", format_price(final_price)])
    
    # Создаем HTML-таблицу напрямую для обхода проблем с шириной
    html_table = '<table style="width:100%; border-collapse:collapse; margin-bottom:20px;">'
    
    # Добавляем заголовки
    html_table += '<tr>'
    html_table += '<th style="text-align:left; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:70%; font-size:0.9rem;">Наименование</th>'
    html_table += '<th style="text-align:right; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:30%; font-size:0.9rem;">Стоимость</th>'
    html_table += '</tr>'
    
    # Добавляем строки с данными
    for i, item in enumerate(items_data):
        # Особое форматирование для строки "Итого"
        if i == len(items_data) - 1:
            html_table += '<tr style="background-color:#e0f0ff;">'
            # Добавляем адаптивный CSS-класс для строки "Итого"
            html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:2px solid #3f6daa; word-wrap:break-word; font-weight:bold; font-size:1.35rem; white-space:nowrap;">{item[0]}</td>'
            
            # Применяем специальный класс для значения "Итого" с переносом строки для общей ширины
            html_table += f"""
            <td style="text-align:right; padding:8px 5px; border-bottom:2px solid #3f6daa; font-weight:bold; color:#0066cc; white-space:nowrap;" class="responsive-total">
                <div style="display:inline-block; width:100%;">{item[1]}</div>
            </td>
            """
            html_table += '</tr>'
        else:
            # Проверяем, является ли строка скидкой (скидки начинаются с минуса) или весенней акцией
            is_discount = item[0] == "Скидка по акции" or item[1].startswith("-")
            is_spring_promo = "Весенняя акция" in item[0]
            
            # Применяем специальные стили для скидок и весенней акции
            if is_discount:
                html_table += '<tr style="background-color:#eaffea;">' # Светло-зеленый фон для скидок
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.9rem; color:#2e7d32; font-weight:500;">{item[0]}</td>'
                html_table += f'<td style="text-align:right; padding:8px 10px; border-bottom:1px solid #eee; font-size:0.9rem; color:#2e7d32; font-weight:500;">{item[1]}</td>'
            elif is_spring_promo:
                # Стиль для отображения весенней акции с зеленым цветом
                html_table += '<tr style="background-color:#e0ffea;">' # Зеленый фон для весенней акции
                html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:1.0rem; color:#1b5e20; font-weight:600;">{item[0]}</td>'
                html_table += f'<td style="text-align:right; padding:8px 10px; border-bottom:1px solid #eee; font-size:1.0rem; color:#1b5e20; font-weight:600;">{item[1]}</td>'
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
    
    # Отображаем разделитель между таблицей стоимости и описанием перголы
    st.markdown("<hr style='margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Добавляем информацию о типе перголы и изображение только один раз в сессии
    if not st.session_state.get('description_shown', False):
        # Устанавливаем флаг, что описание уже было показано в этой сессии
        st.session_state.description_shown = True
        
        # Отображаем информацию о выбранном типе перголы с использованием модуля описаний
        if pergola_type in ["B500NEW", "B700NEW", "B600"]:
            # Используем описание из модуля конфигурации
            description_html = get_pergola_description(pergola_type)
            display_formatted_description(description_html)
            
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
            display_formatted_description(modular_description)
            
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
            display_formatted_description(drainage_description)
            
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
                display_formatted_description(bansbach_description)
                
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
                display_formatted_description(somfy_description)
                
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
            display_formatted_description(bioclimatic_install_description)
            
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
                display_formatted_description(lamella_engineering_description)
                
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

def display_formatted_description(description_text):
    """
    Отображает форматированное описание в стилизованном контейнере,
    избегая проблем с видимостью HTML-тегов.
    
    Args:
        description_text (str): HTML-текст с описанием
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
            font-size: 3.2rem; /* Увеличенный размер для h1 и h2 */
            margin-top: 30px;
            margin-bottom: 20px;
            color: #333333;
            font-weight: 700;
        }
        .description-container h3 {
            font-size: 2.86rem; /* Увеличено на 30% от 2.2rem */
            margin-top: 25px;
            margin-bottom: 20px;
            color: #333333;
            font-weight: 600;
        }
        .description-container h4 {
            font-size: 2.34rem; /* Увеличено на 30% от 1.8rem */
            margin-top: 20px;
            margin-bottom: 15px;
            color: #333333;
            font-weight: 500;
        }
        .description-container p {
            margin-bottom: 10px;
            line-height: 1.5;
            font-size: 1.25rem; /* Увеличенный размер параграфов */
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
        
        # 6. Обрамляем весь текст в div-контейнер для изоляции стилей и добавляем контейнер с отступами
        # Уменьшаем отступ справа для более компактного вида
        final_html = f"""
        <div style="width:95%; margin:0 auto; padding-left:15px; padding-right:15px;">
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

def display_image_with_padding(image_path, caption=None, padding_percent=5):
    """
    Отображает изображение с отступами по краям и подписью.
    
    Args:
        image_path (str): Путь к изображению
        caption (str, optional): Подпись к изображению
        padding_percent (int, optional): Процент отступа от ширины контейнера (по умолчанию 5%)
    """
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
                margin-bottom: 20px;
            }}
            </style>
            """, unsafe_allow_html=True)
            st.session_state.image_style_added = True
        
        # Проверяем существование файла
        import os
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Изображение не найдено: {image_path}")
            
        # Отображаем изображение
        # Вместо параметра use_container_width=True используем width=None для занятия всей ширины
        st.image(image_path, caption=caption, width=None)

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

def scroll_to_results():
    """
    Добавляет JavaScript для перехода к якорю результатов при нажатии на скрытую кнопку
    """
    # Добавляем JavaScript для автоматического нажатия на ссылку-якорь
    st.markdown("""
    <script>
        // Используем URL-хэш для скролла
        function scrollToResults() {
            console.log('Attempting to scroll to results...');
            
            // Ищем элемент с id="results"
            const resultsElement = document.getElementById('results');
            
            if (resultsElement) {
                console.log('Found results element, scrolling...');
                
                // Программно создаем и кликаем по ссылке на якорь
                const scrollLink = document.createElement('a');
                scrollLink.href = '#results';
                scrollLink.style.display = 'none';
                document.body.appendChild(scrollLink);
                
                // Прокручиваем с задержкой для надежности
                setTimeout(() => {
                    scrollLink.click();
                    console.log('Clicked on results anchor link');
                    
                    // Удаляем ссылку после использования
                    setTimeout(() => {
                        document.body.removeChild(scrollLink);
                    }, 100);
                }, 500);
                
                return true;
            }
            
            console.log('Results element not found');
            
            // Если якорь не найден, ищем заголовок или просто скроллим вниз
            const resultsHeadings = Array.from(document.querySelectorAll('h2'))
                .filter(h => h.textContent.includes('Результаты расчета'));
            
            if (resultsHeadings.length > 0) {
                console.log('Found results heading, scrolling...');
                const heading = resultsHeadings[0];
                window.scrollTo({
                    top: heading.offsetTop - 80,
                    behavior: 'smooth'
                });
                return true;
            }
            
            // Крайний случай - просто скроллим на определенное расстояние вниз
            console.log('No targets found, scrolling down as fallback');
            window.scrollTo({
                top: document.body.scrollHeight / 2,  // Примерно в середину страницы
                behavior: 'smooth'
            });
            
            return false;
        }
        
        // Выполняем скролл после загрузки DOM
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM fully loaded, scheduling scroll');
            setTimeout(scrollToResults, 300);
        });
        
        // Также выполняем скролл сразу (для случая, когда DOM уже загружен)
        console.log('Script loaded, scheduling immediate scroll');
        setTimeout(scrollToResults, 500);
        
        // И выполняем третью попытку для надежности
        setTimeout(scrollToResults, 1500);
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
    # Настраиваем страницу
    st.set_page_config(
        page_title="Калькулятор пергол DecoLife",
        page_icon="🏠",
        layout="centered"  # Изменено с "wide" на "centered" для более узкого интерфейса
    )
    
    # Добавляем умную адаптацию для различных размеров экрана
    add_smart_device_adaptation()
    
    # Добавляем код счетчика Яндекс.Метрики
    add_yandex_metrika()
    
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
        div[data-testid="stTable"],
        div[data-testid="stDataFrame"] {
            width: 100% !important;
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
    st.markdown("<h1 style='text-align: center; margin-top: 10px; margin-bottom: 5px; font-size: 2.2rem; font-weight: 600; color: #0066cc;'>Калькулятор стоимости перголы</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 10px; font-size: 1rem;'>Введите размеры и параметры перголы для расчета стоимости в рублях (₽)</p>", unsafe_allow_html=True)
    
    # Получаем размеры перголы
    dimensions = render_dimensions_form()
    
    # Сохраняем размеры в session_state
    st.session_state.dimensions = dimensions
    
    # Получаем опции перголы
    options = render_options_form()
    
    # Добавляем отступ перед кнопкой расчета
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    # Кнопка для расчета с улучшенным стилем
    if st.button("Рассчитать стоимость", type="primary", use_container_width=True):
        with st.spinner("Выполняется расчет..."):
            # Проверяем, что у нас есть данные для расчета
            if dimensions and options:
                # Выполняем расчет
                results = perform_calculation(dimensions, options)
                
                # Сохраняем результаты и опции в состоянии сессии
                st.session_state.results = results
                st.session_state.options = options
                
                # Добавляем флаг, что нужно прокрутить к результатам
                st.session_state.scroll_to_results = True
                
                # Сбрасываем флаг описания, чтобы оно обновлялось при каждом новом расчете
                st.session_state.description_shown = False
                
                # Устанавливаем флаг для отправки события в Яндекс.Метрику после перезагрузки
                st.session_state.send_ya_metrika_event = True
                
                # Перезагружаем страницу для отображения результатов
                st.rerun()
    
    # Добавляем разделитель (компактный)
    st.markdown("<hr style='margin-top: 0.2rem; margin-bottom: 0.2rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
    # Отображаем кнопку для скролла к результатам (если есть результаты)
    if 'results' in st.session_state:
        # Кнопка для скролла к результатам (компактная и заметная)
        st.markdown("""
        <a href="#results" style="display: block; width: 90%; margin: 10px auto; padding: 10px; 
                       background-color: #0066cc; color: white; text-align: center; 
                       border-radius: 5px; text-decoration: none; font-weight: bold;">
           ↓ Перейти к результатам расчета ↓
        </a>
        """, unsafe_allow_html=True)
        
        # Показываем общий результат и детальную информацию
        render_results(st.session_state.results)
        
        # Если нужна прокрутка к результатам, добавляем JS код
        if st.session_state.get('scroll_to_results', False):
            scroll_to_results()
            # Сбрасываем флаг, чтобы не добавлять скрипт при каждом обновлении
            st.session_state.scroll_to_results = False
    
    # Добавляем информацию о версии внизу страницы (компактно)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.3rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #999;'>© 2025 Комфортный дом | Калькулятор пергол v4.3.5</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    # Создаем директории, если они не существуют
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/price_tables", exist_ok=True)
    
    # Запускаем приложение
    main()