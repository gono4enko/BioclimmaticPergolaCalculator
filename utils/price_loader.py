"""
Модуль для загрузки данных о ценах пергол из файлов и конфигурации
"""
import os
import logging
import pandas as pd

# Путь к директории с файлами цен
PRICE_TABLES_DIR = 'attached_assets'

# Импортируем данные из конфигурации
from config.price_data import PERGOLA_PRICE_FILES

# Настройка логгера
logger = logging.getLogger(__name__)

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
        tuple: (базовая стоимость перголы, количество модулей, текстовое сообщение о конфигурации)
    """
    try:
        # Определяем файл с ценами
        price_file = None
        full_lamella_type = None
        
        # Формируем полный тип ламелей (например, B500-200 или B700-250)
        if pergola_type == "B500NEW":
            full_lamella_type = f"B500-{lamella_size}"
        elif pergola_type == "B700NEW":
            full_lamella_type = f"B700-{lamella_size}"
        elif pergola_type == "B600":
            full_lamella_type = "B600-PIR"
            
        # Проверяем, есть ли прайс для данного типа ламелей
        if full_lamella_type and full_lamella_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[full_lamella_type]
        # Если нет, ищем для типа перголы
        elif pergola_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[pergola_type]
            
        if not price_file:
            logger.warning(f"Не найден файл с ценами для {pergola_type} и ламелей {lamella_size}")
            return 0, 1, "Ошибка: Не найден прайс-лист"
            
        # Полный путь к файлу с ценами
        file_path = os.path.join(PRICE_TABLES_DIR, price_file)
        
        if not os.path.exists(file_path):
            logger.error(f"Файл с ценами не найден: {file_path}")
            return 0, 1, "Ошибка: Файл прайс-листа не найден"
            
        # Загружаем таблицу цен из CSV-файла
        price_data = load_price_table(file_path)
        
        # Ищем соответствие размерам в таблице
        if price_data:
            # Конвертируем размеры в float для сравнения
            width_float = float(width_m)
            length_float = float(length_m)
            
            # Получаем все доступные размеры ширины и длины
            available_widths = sorted([float(w) for w in price_data.keys()])
            logger.debug(f"Доступные ширины: {available_widths}")
            
            available_lengths = []
            for w in available_widths:
                for l in price_data[w].keys():
                    if float(l) not in available_lengths:
                        available_lengths.append(float(l))
            available_lengths = sorted(available_lengths)
            logger.debug(f"Доступные длины: {available_lengths}")
            
            # Определяем количество модулей по ширине
            modules_count = 1
            if width_float > 7.0:
                modules_count = 2
            if width_float > 10.5:
                modules_count = 3
                
            # Ищем точное соответствие
            if width_float in price_data and length_float in price_data[width_float]:
                price = price_data[width_float][length_float]
                logger.info(f"Найдена цена для размера {width_float}x{length_float}м: {price} евро")
                message = f"Стандартная конфигурация {pergola_type} {width_float}×{length_float} м"
                return price, modules_count, message
                
            # Если нет точного соответствия, ищем ближайший больший размер
            # Сначала для ширины
            best_width = None
            for w in available_widths:
                if w >= width_float:
                    best_width = w
                    break
                    
            # Затем для длины
            best_length = None
            if best_width:
                available_lengths_for_width = sorted([float(l) for l in price_data[best_width].keys()])
                for l in available_lengths_for_width:
                    if l >= length_float:
                        best_length = l
                        break
                        
            # Если нашли подходящие размеры
            if best_width and best_length:
                price = price_data[best_width][best_length]
                logger.info(f"Найдена цена для ближайшего размера {best_width}x{best_length}м: {price} евро")
                message = f"Ближайшая доступная конфигурация {pergola_type} {best_width}×{best_length} м"
                return price, modules_count, message
            
            # В крайнем случае, возвращаем минимальную цену из прайса
            min_price = float('inf')
            for w in price_data:
                for l in price_data[w]:
                    if price_data[w][l] < min_price:
                        min_price = price_data[w][l]
                        
            if min_price != float('inf'):
                logger.warning(f"Не найдено точное соответствие для {width_float}x{length_float}м, возвращаем базовую цену: {min_price} евро")
                message = f"Базовая конфигурация {pergola_type} (стоимость может быть уточнена)"
                return min_price, modules_count, message
            
        # Если всё равно не нашли цену
        logger.error(f"Не удалось найти подходящую цену для {pergola_type} с ламелями {lamella_size}, размеры {width_m}x{length_m}")
        return 0, 1, "Ошибка: Не удалось найти подходящую конфигурацию"
        
    except Exception as e:
        logger.error(f"Ошибка при получении цены для {pergola_type}, ламели {lamella_size}, размеры {width_m}x{length_m}: {str(e)}")
        return 0, 1, f"Ошибка: {str(e)}"


def load_price_table(file_path):
    """
    Загружает таблицу цен из CSV-файла
    
    Args:
        file_path (str): Путь к CSV-файлу с ценами
        
    Returns:
        dict: Словарь с ценами вида {ширина: {длина: цена}}
    """
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return {}
            
        # Проверяем, имеет ли файл размер
        if os.path.getsize(file_path) == 0:
            logger.warning(f"Файл пуст: {file_path}")
            return {}
            
        # Определяем разделитель в CSV-файле
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if ';' in first_line:
                delimiter = ';'
            else:
                delimiter = ','
        logger.debug(f"Обнаружен разделитель: '{delimiter}'")
            
        # Читаем файл с помощью pandas
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, decimal=',', encoding='utf-8')
        except UnicodeDecodeError:
            # Пробуем другую кодировку
            df = pd.read_csv(file_path, delimiter=delimiter, decimal=',', encoding='cp1251')
            
        # Проверяем, имеет ли таблица строки
        if df.empty:
            logger.warning(f"Таблица пуста: {file_path}")
            return {}
            
        # Проверяем, есть ли строка с информацией о модулях
        if "модулей" in str(df.iloc[0, 0]) or "модуль" in str(df.iloc[0, 0]):
            logger.debug("Обнаружена строка с информацией о модулях, пропускаем")
            # Первая строка - информация о модулях, пропускаем
            df = df.iloc[1:]
            
        # Получаем заголовок с размерами ширины
        header = df.iloc[0].values
        logger.debug(f"Заголовок: {header}")
        
        # Первый элемент заголовка обычно "Вылет\\Ширина (м)" или подобное, пропускаем его
        length_values = header[1:]
        
        # Конвертируем значения длины в числа
        length_values = [float(str(value).replace(',', '.')) for value in length_values]
        logger.debug(f"Значения длины из заголовка: {length_values}")
        
        # Создаем словарь для цен
        prices = {}
        
        # Перебираем строки таблицы, начиная со второй (индекс 1)
        for i in range(1, len(df)):
            # Получаем значение ширины из первого столбца
            width = float(str(df.iloc[i, 0]).replace(',', '.'))
            
            # Создаем вложенный словарь для этой ширины
            prices[width] = {}
            
            # Заполняем цены для каждой длины
            for j, length in enumerate(length_values):
                try:
                    # Индекс столбца начинается с 1, т.к. первый - ширина
                    price_value = df.iloc[i, j+1]
                    
                    # Преобразуем в число, если это строка
                    if isinstance(price_value, str):
                        price_value = float(price_value.replace(',', '.').replace(' ', ''))
                    else:
                        price_value = float(price_value)
                        
                    prices[width][length] = price_value
                except (ValueError, IndexError) as e:
                    # Пропускаем ячейки с некорректными данными
                    logger.warning(f"Не удалось обработать цену для {width}x{length}: {str(e)}")
                    continue
                    
        logger.info(f"Загружено {len(prices)} значений ширины с ценами")
        
        # Выводим для отладки первые несколько строк
        debug_limit = 3
        for i, (width, length_prices) in enumerate(prices.items()):
            if i < debug_limit:
                logger.debug(f"Ширина {width} м: {length_prices}")
                
        return prices
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке таблицы цен из {file_path}: {str(e)}")
        return {}