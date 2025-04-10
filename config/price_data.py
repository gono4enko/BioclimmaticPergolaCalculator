"""
Модуль с данными о ценах на перголы из официальных прайс-листов

Этот файл содержит данные о ценах из официальных прайс-листов для пергол B500NEW, B700NEW и B600.
"""
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Соответствие типов пергол и файлов с ценами
PERGOLA_PRICE_FILES = {
    # Тип перголы -> Имя файла с ценами
    "B500NEW": "Price_B500-20.csv",
    "B700NEW": "Price_B700-20.csv",
    "B600": "Price_B600_PIR.csv",
    # Специальные типы ламелей
    "lamella-200": "Price_B500-20.csv",
    "lamella-250": "Price_B500-25.csv",
    "B500-200": "Price_B500-20.csv",
    "B500-250": "Price_B500-25.csv", 
    "B700-200": "Price_B700-20.csv",
    "B700-250": "Price_B700-25.csv",
    "B600-PIR": "Price_B600_PIR.csv",
}

# Цены на приводы Bansbach для B500
BANSBACH_PRICES = {
    "T1": 700,    # Стандартный линейный привод
    "T2": 1400,   # Тандем-привод для больших пергол
    "T3": 2100,   # Тройной привод для очень больших пергол
}

# Цены на приводы Somfy для B700
SOMFY_PRICES = {
    "M1": 300,    # Стандартный моторизованный привод
    "M2": 600,    # Двойной привод для больших пергол
    "M3": 900,    # Тройной привод для очень больших пергол
}

# Граничные условия для использования тандем-привода Bansbach
BANSBACH_TANDEM_CONDITIONS = {
    "min_width": 7.0,  # Минимальная ширина в метрах
    "min_length": 5.0  # Минимальный вынос в метрах
}

# Цены на светодиодную подсветку
LIGHTING_PRICES = {
    "LED": 120,    # Цена за метр
    "RGB": 180,    # Цена за метр для RGB-подсветки
    "PSU": 50      # Стоимость блока питания
}

# Дополнительные опции
ADDITIONAL_OPTIONS_PRICES = {
    "gutter_insert": 40,    # Цена за метр водостока
    "water_drain": 120,     # Цена за дренажную систему
    "remote_control": 80,   # Цена за пульт дистанционного управления
    "sensors": 150,         # Цена за датчики (дождь, ветер)
    "vertical_screens": 250  # Цена за вертикальные экраны (за кв. метр)
}

# Цены на дополнительные колонны
ADDITIONAL_COLUMNS_PRICES = {
    "standard": 200,     # Стандартная колонна
    "reinforced": 350,   # Усиленная колонна
    "decorative": 450    # Декоративная колонна
}

# Пороговые значения для дополнительных колонн
ADDITIONAL_COLUMNS_THRESHOLDS = {
    "B500NEW": 6.0,      # Минимальная длина в метрах для B500
    "B700NEW": 7.0,      # Минимальная длина в метрах для B700
    "B600": 5.5          # Минимальная длина в метрах для B600
}

def get_option_price(option_name, quantity=1):
    """
    Возвращает стоимость опции на основе её названия и количества
    
    Args:
        option_name (str): Название опции
        quantity (float): Количество (метры, штуки и т.д.)
        
    Returns:
        float: Стоимость опции
    """
    try:
        # Проверяем наличие опции в каждом из словарей с ценами
        if option_name in LIGHTING_PRICES:
            price = LIGHTING_PRICES[option_name] * quantity
        elif option_name in ADDITIONAL_OPTIONS_PRICES:
            price = ADDITIONAL_OPTIONS_PRICES[option_name] * quantity
        elif option_name in ADDITIONAL_COLUMNS_PRICES:
            price = ADDITIONAL_COLUMNS_PRICES[option_name] * quantity
        elif option_name in BANSBACH_PRICES:
            price = BANSBACH_PRICES[option_name] * quantity
        elif option_name in SOMFY_PRICES:
            price = SOMFY_PRICES[option_name] * quantity
        else:
            logger.warning(f"Неизвестная опция: {option_name}")
            price = 0
            
        return price
    except Exception as e:
        logger.error(f"Ошибка при расчете стоимости опции {option_name}: {str(e)}")
        return 0