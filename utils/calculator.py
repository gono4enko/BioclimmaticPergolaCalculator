"""
Модуль для расчета стоимости пергол на основе введенных данных
"""
import logging
import math
from utils.price_loader import get_base_price
from config.price_data import get_option_price, LIGHTING_PRICES, ADDITIONAL_OPTIONS_PRICES
from utils.validation import validate_pergola_config
from config.pergola_types import LAMELLA_TYPES

# Получаем логгер
logger = logging.getLogger(__name__)

def calculate_lamella_count(length, lamella_type):
    """
    Расчет количества ламелей на основе длины и типа ламели
    
    Args:
        length (float): Длина перголы в мм
        lamella_type (str): Тип ламели (ключ из LAMELLA_TYPES)
        
    Returns:
        int: Количество ламелей
    """
    # Для B600 не используются ламели
    if lamella_type == "B600":
        return 0
    
    # Получаем ширину ламели в мм
    lamella_width = LAMELLA_TYPES.get(lamella_type, {}).get("width", 0)
    
    if lamella_width <= 0:
        return 0
    
    # Конвертируем мм в метры
    lamella_width_m = lamella_width / 1000
    length_m = length / 1000
    
    # Рассчитываем количество ламелей
    count = length_m / lamella_width_m
    
    # Округляем до ближайшего целого числа в большую сторону
    return math.ceil(count)

def adjust_length_to_lamella_count(length_mm, lamella_type):
    """
    Корректирует длину (вынос) перголы для соответствия целому числу ламелей
    
    Args:
        length_mm (float): Оригинальная длина перголы в мм
        lamella_type (str): Тип ламели
        
    Returns:
        tuple: (скорректированная длина в мм, количество ламелей, сообщение о корректировке)
    """
    # Для перголы B600 корректировка не нужна
    if lamella_type == "B600":
        return length_mm, 0, None
    
    # Получаем ширину ламели в мм
    lamella_width = LAMELLA_TYPES.get(lamella_type, {}).get("width", 0)
    
    if lamella_width <= 0:
        return length_mm, 0, None
    
    # Конвертируем в метры
    length_m = length_mm / 1000
    lamella_width_m = lamella_width / 1000
    
    # Рассчитываем количество ламелей
    lamella_count_exact = length_m / lamella_width_m
    lamella_count = math.ceil(lamella_count_exact)
    
    # Если количество ламелей не целое число, корректируем длину
    if lamella_count != lamella_count_exact:
        adjusted_length_m = lamella_count * lamella_width_m
        adjusted_length_mm = adjusted_length_m * 1000
        
        correction_message = (
            f"Длина перголы была скорректирована с {length_mm} мм до {int(adjusted_length_mm)} мм "
            f"для соответствия целому числу ламелей ({lamella_count} шт.)"
        )
        
        return adjusted_length_mm, lamella_count, correction_message
    
    # Если корректировка не требуется
    return length_mm, lamella_count, None

def calculate_pergola_cost(dimensions, options):
    """
    Рассчитывает стоимость перголы на основе заданных размеров и опций.
    
    Args:
        dimensions (dict): Словарь с размерами перголы (ширина, длина, высота)
        options (dict): Словарь с выбранными опциями
        
    Returns:
        dict: Словарь с результатами расчетов
    """
    try:
        # Извлекаем данные из входных параметров
        width_mm = dimensions.get('width', 0)
        length_mm = dimensions.get('length', 0)
        height_mm = dimensions.get('height', 0)
        
        pergola_type = options.get('pergola_type', '')
        lamella_type = options.get('lamella_type', '')
        lamella_step = options.get('lamella_step', 200)  # По умолчанию шаг ламелей 200мм
        lighting_type = options.get('lighting_type', 'none')
        additional_options = options.get('additional_options', [])
        
        # Валидация конфигурации перголы
        validation_error = validate_pergola_config(pergola_type, lamella_type, width_mm, length_mm)
        if validation_error:
            logger.error(f"Ошибка валидации: {validation_error}")
            return {
                'error': validation_error,
                'total_cost': 0,
                'detailed_costs': {}
            }
        
        # Применяем корректировку длины (выноса) перголы в соответствии с размером ламелей
        # для пергол B500NEW и B700NEW
        correction_message = None
        if pergola_type in ["B500NEW", "B700NEW"]:
            length_mm, lamella_count, correction_message = adjust_length_to_lamella_count(length_mm, lamella_type)
            if correction_message:
                logger.info(correction_message)
        else:
            # Если коррекция не применяется, просто рассчитываем количество ламелей
            lamella_count = calculate_lamella_count(length_mm, lamella_type)
        
        # Конвертируем мм в метры для расчета цены
        width_m = width_mm / 1000
        length_m = length_mm / 1000
        
        # Получаем базовую цену перголы
        base_price = get_base_price(pergola_type, lamella_type, width_m, length_m)
        
        if base_price is None:
            logger.error(f"Не удалось найти базовую цену для {pergola_type}/{lamella_type} ({width_m}x{length_m})")
            return {
                'error': f"Не удалось найти базовую цену для выбранной конфигурации перголы",
                'total_cost': 0,
                'detailed_costs': {}
            }
        
        # Рассчитываем детальные расходы
        detailed_costs = {
            'base_price': base_price,
            'lighting': 0,
            'additional_options': {}
        }
        
        # Добавляем стоимость освещения
        if lighting_type != 'none' and lighting_type in LIGHTING_PRICES:
            lighting_price = LIGHTING_PRICES[lighting_type]
            
            # Рассчитываем стоимость освещения в зависимости от размеров перголы
            # Используем скорректированную длину!
            if callable(lighting_price):
                lighting_cost = lighting_price(width_mm, length_mm)
            else:
                lighting_cost = lighting_price
                
            detailed_costs['lighting'] = lighting_cost
        
        # Добавляем стоимость дополнительных опций
        for option in additional_options:
            if option in ADDITIONAL_OPTIONS_PRICES:
                option_price = ADDITIONAL_OPTIONS_PRICES[option]
                
                # Рассчитываем стоимость опции в зависимости от размеров перголы
                # Используем скорректированную длину!
                if callable(option_price):
                    option_cost = option_price(width_mm, length_mm)
                else:
                    option_cost = option_price
                    
                detailed_costs['additional_options'][option] = option_cost
        
        # Вычисляем общую стоимость
        total_cost = base_price
        total_cost += detailed_costs['lighting']
        total_cost += sum(detailed_costs['additional_options'].values())
        
        # Формируем результат
        result = {
            'total_cost': round(total_cost, 2),
            'detailed_costs': detailed_costs,
            'dimensions': {
                'width_mm': width_mm,
                'width_m': width_m,
                'length_mm': length_mm,
                'length_m': length_m,
                'height_mm': height_mm,
                'height_m': height_mm / 1000
            },
            'lamella_count': lamella_count,
            'correction_message': correction_message
        }
        
        logger.info(f"Расчет выполнен успешно: {result['total_cost']} евро")
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при расчете стоимости: {str(e)}", exc_info=True)
        return {
            'error': f"Произошла ошибка при расчете: {str(e)}",
            'total_cost': 0,
            'detailed_costs': {}
        }