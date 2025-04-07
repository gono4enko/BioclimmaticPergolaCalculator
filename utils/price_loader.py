"""
Модуль для загрузки и обработки данных о ценах из CSV-файлов
"""
import os
import logging
import pandas as pd

# Получаем логгер
logger = logging.getLogger(__name__)

# Путь к директории с файлами цен
PRICE_TABLES_DIR = 'attached_assets'

# Соответствие типов пергол и файлов с ценами
PERGOLA_PRICE_FILES = {
    "B500NEW": "Прайс_В500-20.csv",  # По умолчанию используем прайс для B500-20
    "B500-20NEW": "Прайс_В500-20.csv",
    "B500-25NEW": "Прайс_В500-25.csv",
    "B700NEW": "Прайс_B700-20.csv",  # По умолчанию используем прайс для B700-20
    "B700-20NEW": "Прайс_B700-20.csv",
    "B700-25NEW": "Прайс_B700-25.csv",
    "B600": "Прайс_В600_PIR.csv",
}

# Словарь для хранения загруженных таблиц цен
price_tables = {}

def load_price_tables():
    """
    Загружает все таблицы цен из CSV-файлов
    """
    global price_tables
    price_tables = {}
    
    try:
        for file_name in os.listdir(PRICE_TABLES_DIR):
            if file_name.endswith('.csv'):
                file_path = os.path.join(PRICE_TABLES_DIR, file_name)
                
                # Обработка потенциальных проблем с кодировкой
                try:
                    df = pd.read_csv(file_path, delimiter=';', decimal=',', encoding='utf-8')
                except UnicodeDecodeError:
                    # Пробуем альтернативную кодировку
                    df = pd.read_csv(file_path, delimiter=';', decimal=',', encoding='cp1251')
                
                # Обработка данных
                # Первая строка - количество модулей, вторая - заголовки
                # Первый столбец - вылет, остальные столбцы - ширина
                
                # Получаем названия столбцов (ширина в метрах)
                width_values = df.iloc[0].values[1:].astype(str)
                
                # Получаем значения вылета (длины в метрах)
                length_values = df.iloc[1:, 0].values.astype(str)
                
                # Получаем цены
                price_values = df.iloc[1:, 1:].values
                
                # Создаем словарь для быстрого доступа к ценам по размерам
                price_dict = {}
                
                for i, length in enumerate(length_values):
                    for j, width in enumerate(width_values):
                        # Преобразование строки в число с плавающей точкой
                        try:
                            length_float = float(length.replace(',', '.'))
                            width_float = float(width.replace(',', '.'))
                            price_value = float(price_values[i][j])
                            
                            # Сохраняем цену по ключу (ширина, длина)
                            price_dict[(width_float, length_float)] = price_value
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Ошибка обработки цены в файле {file_name}: {width}x{length}, {e}")
                
                price_tables[file_name] = price_dict
                logger.info(f"Загружена таблица цен из файла {file_name}, {len(price_dict)} записей")
                
        return True
    except Exception as e:
        logger.error(f"Ошибка загрузки таблиц цен: {str(e)}", exc_info=True)
        return False

def get_base_price(pergola_type, lamella_type, width_m, length_m):
    """
    Получает базовую цену перголы на основе типа и размеров
    
    Args:
        pergola_type (str): Тип перголы
        lamella_type (str): Тип ламелей
        width_m (float): Ширина в метрах
        length_m (float): Длина в метрах
        
    Returns:
        float: Базовая цена перголы или None, если цена не найдена
    """
    try:
        # Определяем файл с ценами в зависимости от типа перголы и ламелей
        price_file = None
        
        # Если указан конкретный тип ламелей, используем соответствующий прайс
        if lamella_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[lamella_type]
        # Иначе используем прайс для типа перголы
        elif pergola_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[pergola_type]
        
        if not price_file or price_file not in price_tables:
            logger.warning(f"Файл с ценами не найден для {pergola_type}/{lamella_type}")
            return None
        
        # Получаем таблицу цен
        price_dict = price_tables[price_file]
        
        # Округляем размеры до ближайших стандартных
        width_m_rounded, length_m_rounded = find_nearest_dimensions(price_dict, width_m, length_m)
        
        if (width_m_rounded, length_m_rounded) in price_dict:
            price = price_dict[(width_m_rounded, length_m_rounded)]
            logger.info(f"Найдена цена {price} для {pergola_type}/{lamella_type} ({width_m_rounded}x{length_m_rounded})")
            return price
        else:
            logger.warning(f"Цена не найдена для {pergola_type}/{lamella_type} ({width_m}x{length_m})")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при получении цены: {str(e)}", exc_info=True)
        return None

def find_nearest_dimensions(price_dict, width_m, length_m):
    """
    Находит ближайшие большие стандартные размеры в таблице цен
    
    Args:
        price_dict (dict): Словарь с ценами
        width_m (float): Заданная ширина в метрах
        length_m (float): Заданная длина в метрах
        
    Returns:
        tuple: (ближайшая большая ширина, ближайшая большая длина)
    """
    if not price_dict:
        return width_m, length_m
    
    # Получаем все доступные ширины и длины
    widths = sorted(set([dim[0] for dim in price_dict.keys()]))
    lengths = sorted(set([dim[1] for dim in price_dict.keys()]))
    
    # Находим ближайшую большую ширину
    filtered_widths = [w for w in widths if w >= width_m]
    nearest_width = min(filtered_widths) if filtered_widths else max(widths)
    
    # Находим ближайшую большую длину
    filtered_lengths = [l for l in lengths if l >= length_m]
    nearest_length = min(filtered_lengths) if filtered_lengths else max(lengths)
    
    # Логируем информацию о подборе размеров
    logger.info(f"Подбор размеров: запрос {width_m}x{length_m}, выбрано {nearest_width}x{nearest_length}")
    
    return nearest_width, nearest_length

# Загружаем таблицы цен при импорте модуля
load_price_tables()