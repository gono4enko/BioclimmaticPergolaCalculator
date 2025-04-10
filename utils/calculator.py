"""
Модуль для расчета стоимости пергол на основе введенных данных
"""
import logging
import math
from utils.price_loader import get_base_price
from config.price_data import (
    get_option_price, LIGHTING_PRICES, ADDITIONAL_OPTIONS_PRICES,
    ADDITIONAL_COLUMNS_PRICES, ADDITIONAL_COLUMNS_THRESHOLDS,
    BANSBACH_PRICES, BANSBACH_TANDEM_CONDITIONS,
    SOMFY_PRICES
)

# Настройка логгера
logger = logging.getLogger(__name__)

# Курс евро к рублю
EUR_TO_RUB = 107.5

def calculate_pergola_cost(dimensions, options):
    """
    Рассчитывает стоимость перголы на основе введенных размеров и опций
    
    Args:
        dimensions (dict): Словарь с размерами перголы (ширина, длина)
        options (dict): Словарь с выбранными опциями
        
    Returns:
        dict: Словарь с результатами расчета стоимости
    """
    try:
        # Логируем входные данные для отладки
        logger.debug(f"Расчет стоимости перголы с размерами: {dimensions}")
        logger.debug(f"Выбранные опции: {options}")
        
        # Извлекаем необходимые параметры из словарей
        width_m = float(dimensions.get('width', 3.0))
        length_m = float(dimensions.get('length', 3.0))
        pergola_type = options.get('pergola_type', 'B500NEW')
        lamella_type = options.get('lamella_type', 'lamella-200')
        
        # Определяем размер ламелей по выбранному типу
        if '200' in lamella_type:
            lamella_size = '200'
        elif '250' in lamella_type:
            lamella_size = '250'
        else:
            lamella_size = 'PIR'  # Для B600
        
        # Получаем базовую стоимость перголы
        base_price_eur, modules_count, config_message = get_base_price(pergola_type, lamella_size, width_m, length_m)
        
        # Если не удалось получить цену, возвращаем ошибку
        if base_price_eur == 0:
            return {
                'success': False,
                'error_message': 'Не удалось определить базовую стоимость для выбранной конфигурации'
            }
        
        # Конвертируем в рубли
        base_price_rub = base_price_eur * EUR_TO_RUB
        
        # Инициализируем словарь для результатов
        result = {
            'success': True,
            'base_price_eur': base_price_eur,
            'base_price_rub': base_price_rub,
            'modules_count': modules_count,
            'config_message': config_message,
            'pergola_type': pergola_type,
            'lamella_type': lamella_type,
            'width_m': width_m,
            'length_m': length_m,
            'additional_items': [],
            'total_price_eur': base_price_eur,
            'total_price_rub': base_price_rub
        }
        
        # Добавляем привод
        drive_type, drive_price_eur, needs_tandem = get_drive_type(pergola_type, width_m, length_m, modules_count)
        
        if drive_price_eur > 0:
            drive_price_rub = drive_price_eur * EUR_TO_RUB
            result['additional_items'].append({
                'name': f"Привод {drive_type}" + (" (тандем)" if needs_tandem else ""),
                'price_eur': drive_price_eur,
                'price_rub': drive_price_rub,
                'quantity': modules_count
            })
            result['total_price_eur'] += drive_price_eur
            result['total_price_rub'] += drive_price_rub
        
        # Добавляем освещение, если выбрано
        if options.get('has_lighting', False):
            lighting_type = options.get('lighting_type', 'LED')
            lighting_perimeter = calculate_lighting_perimeter(width_m, length_m, modules_count)
            
            # Стоимость светодиодной ленты
            led_price_eur = get_option_price(lighting_type, lighting_perimeter)
            led_price_rub = led_price_eur * EUR_TO_RUB
            
            result['additional_items'].append({
                'name': f"Светодиодная подсветка {lighting_type}",
                'price_eur': led_price_eur,
                'price_rub': led_price_rub,
                'quantity': lighting_perimeter,
                'unit': 'м'
            })
            
            result['total_price_eur'] += led_price_eur
            result['total_price_rub'] += led_price_rub
            
            # Добавляем блок питания для освещения
            psu_count = math.ceil(lighting_perimeter / 5)  # 1 блок на каждые 5 метров
            psu_price_eur = get_option_price('PSU', psu_count)
            psu_price_rub = psu_price_eur * EUR_TO_RUB
            
            result['additional_items'].append({
                'name': "Блок питания для светодиодной подсветки",
                'price_eur': psu_price_eur,
                'price_rub': psu_price_rub,
                'quantity': psu_count,
                'unit': 'шт'
            })
            
            result['total_price_eur'] += psu_price_eur
            result['total_price_rub'] += psu_price_rub
        
        # Добавляем дополнительные колонны, если требуется
        if needs_additional_columns(pergola_type, length_m) and options.get('has_additional_columns', False):
            column_type = options.get('column_type', 'standard')
            column_count = 2  # По умолчанию добавляем 2 колонны
            
            column_price_eur = get_option_price(column_type, column_count)
            column_price_rub = column_price_eur * EUR_TO_RUB
            
            result['additional_items'].append({
                'name': f"Дополнительные колонны ({column_type})",
                'price_eur': column_price_eur,
                'price_rub': column_price_rub,
                'quantity': column_count,
                'unit': 'шт'
            })
            
            result['total_price_eur'] += column_price_eur
            result['total_price_rub'] += column_price_rub
        
        # Добавляем усилитель лотка, если требуется
        if needs_gutter_insert(length_m) and pergola_type != "B600":
            gutter_insert_needed, gutter_price_eur, gutter_count, gutter_length = calculate_gutter_insert_price(length_m, modules_count)
            
            if gutter_insert_needed:
                gutter_price_rub = gutter_price_eur * EUR_TO_RUB
                
                result['additional_items'].append({
                    'name': "Усилитель лотка",
                    'price_eur': gutter_price_eur,
                    'price_rub': gutter_price_rub,
                    'quantity': gutter_length,
                    'unit': 'м'
                })
                
                result['total_price_eur'] += gutter_price_eur
                result['total_price_rub'] += gutter_price_rub
        
        # Добавляем установку, если выбрана
        if options.get('installation', False):
            # Стоимость установки рассчитывается как 20% от общей стоимости
            installation_price_eur = result['total_price_eur'] * 0.2
            installation_price_rub = installation_price_eur * EUR_TO_RUB
            
            result['additional_items'].append({
                'name': "Установка и монтаж",
                'price_eur': installation_price_eur,
                'price_rub': installation_price_rub,
                'percentage': "20%"
            })
            
            result['total_price_eur'] += installation_price_eur
            result['total_price_rub'] += installation_price_rub
        
        # Добавляем доставку, если выбрана
        if options.get('delivery', False):
            # Стоимость доставки - фиксированная 500 евро
            delivery_price_eur = 500
            delivery_price_rub = delivery_price_eur * EUR_TO_RUB
            
            result['additional_items'].append({
                'name': "Доставка",
                'price_eur': delivery_price_eur,
                'price_rub': delivery_price_rub
            })
            
            result['total_price_eur'] += delivery_price_eur
            result['total_price_rub'] += delivery_price_rub
        
        # Округляем итоговые суммы до целых
        result['total_price_eur'] = round(result['total_price_eur'])
        result['total_price_rub'] = round(result['total_price_rub'])
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка в расчете стоимости перголы: {str(e)}")
        return {
            'success': False,
            'error_message': f"Ошибка в расчете: {str(e)}"
        }

def get_drive_type(pergola_type, width_m, length_m, modules_count):
    """
    Определяет тип и стоимость привода для перголы
    
    Args:
        pergola_type (str): Тип перголы
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules_count (int): Количество модулей
        
    Returns:
        tuple: (название привода, цена привода, нужен ли танем-привод)
    """
    try:
        # Для B500 используем привод Bansbach
        if pergola_type == "B500NEW":
            # Определяем, нужен ли тандем-привод
            needs_tandem = (width_m >= BANSBACH_TANDEM_CONDITIONS['min_width'] and 
                          length_m >= BANSBACH_TANDEM_CONDITIONS['min_length'])
            
            # Выбираем тип привода в зависимости от размеров и количества модулей
            if needs_tandem:
                # Для больших размеров используем тандем-привод
                drive_type = "Bansbach T2"
                drive_price = BANSBACH_PRICES["T2"] * modules_count
            else:
                # Для стандартных размеров используем обычный привод
                drive_type = "Bansbach T1"
                drive_price = BANSBACH_PRICES["T1"] * modules_count
                
            return drive_type, drive_price, needs_tandem
            
        # Для B700 используем привод Somfy
        elif pergola_type == "B700NEW":
            # Для B700 тандем-привод нужен для ещё больших размеров, чем для B500
            needs_tandem = (width_m >= 9.0 and length_m >= 6.0)
            
            if needs_tandem:
                drive_type = "Somfy M2"
                drive_price = SOMFY_PRICES["M2"] * modules_count
            else:
                drive_type = "Somfy M1"
                drive_price = SOMFY_PRICES["M1"] * modules_count
                
            return drive_type, drive_price, needs_tandem
            
        # Для B600 используем упрощенный привод
        else:
            drive_type = "Стандартный"
            drive_price = 250 * modules_count  # Фиксированная цена для B600
            needs_tandem = False
            
            return drive_type, drive_price, needs_tandem
    
    except Exception as e:
        logger.error(f"Ошибка при определении типа привода: {str(e)}")
        return "Стандартный", 0, False

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
    if modules == 1:
        return 2 * (width_m + length_m)
    elif modules == 2:
        # Для 2 модулей считаем как два отдельных периметра
        # Ширина каждого модуля - половина общей ширины
        module_width = width_m / 2
        return 2 * modules * (module_width + length_m)
    elif modules == 3:
        # Для 3 модулей считаем как три отдельных периметра
        # Ширина каждого модуля - треть общей ширины
        module_width = width_m / 3
        return 2 * modules * (module_width + length_m)
    else:
        # На всякий случай, для других значений
        return 2 * (width_m + length_m)

def needs_additional_columns(pergola_type, length_m):
    """
    Проверяет, нужны ли дополнительные колонны
    
    Args:
        pergola_type (str): Тип перголы
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужны дополнительные колонны
    """
    if pergola_type in ADDITIONAL_COLUMNS_THRESHOLDS:
        threshold = ADDITIONAL_COLUMNS_THRESHOLDS[pergola_type]
        return length_m >= threshold
    return False

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
    if not needs_gutter_insert(length_m):
        return False, 0, 0, 0
        
    # Количество лотков: кол-во модулей + 1
    gutters_count = modules + 1
    
    # Общая длина лотков: длина выноса * количество лотков
    total_gutter_length = length_m * gutters_count
    
    # Цена усилителя лотка за метр
    price_per_meter = get_option_price('gutter_insert', 1)
    
    # Общая стоимость усилителя лотка
    total_price = price_per_meter * total_gutter_length
    
    return True, total_price, gutters_count, total_gutter_length

def needs_gutter_insert(length_m):
    """
    Проверяет, нужен ли усилитель лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужен усилитель лотка
    """
    # Усилитель лотка нужен для пергол с выносом более 4 метров
    return length_m > 4.0