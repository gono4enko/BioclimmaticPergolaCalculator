"""
Модуль для расчета стоимости пергол на основе введенных данных
"""
import logging
from utils.price_loader import get_base_price
from config.price_data import get_option_price, LIGHTING_PRICES, ADDITIONAL_OPTIONS_PRICES
from utils.validation import validate_pergola_config

# Получаем логгер
logger = logging.getLogger(__name__)

def calculate_lamella_count(length, lamella_step):
    """Расчет количества ламелей на основе длины и шага"""
    if lamella_step <= 0:
        return 0
    return round(length / lamella_step)

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
                if callable(option_price):
                    option_cost = option_price(width_mm, length_mm)
                else:
                    option_cost = option_price
                    
                detailed_costs['additional_options'][option] = option_cost
        
        # Вычисляем общую стоимость
        total_cost = base_price
        total_cost += detailed_costs['lighting']
        total_cost += sum(detailed_costs['additional_options'].values())
        
        # Рассчитываем количество ламелей
        lamella_count = calculate_lamella_count(length_mm, lamella_step)
        
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
            'lamella_count': lamella_count
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