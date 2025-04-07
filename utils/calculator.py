"""
Модуль для расчета стоимости пергол на основе введенных данных
"""
import logging
import math
from utils.price_loader import get_base_price
from config.price_data import (
    get_option_price, LIGHTING_PRICES, ADDITIONAL_OPTIONS_PRICES,
    ADDITIONAL_COLUMNS_PRICES, ADDITIONAL_COLUMNS_THRESHOLDS
)
from utils.validation import validate_pergola_config
from config.pergola_types import LAMELLA_TYPES

# Получаем логгер
logger = logging.getLogger(__name__)

def calculate_lamella_count(length_m, lamella_type):
    """
    Расчет количества ламелей на основе длины и типа ламели
    
    Args:
        length_m (float): Длина перголы в метрах
        lamella_type (str): Тип ламели (ключ из LAMELLA_TYPES)
        
    Returns:
        int: Количество ламелей
    """
    # Для B600 не используются ламели
    if lamella_type == "B600":
        return 0
    
    # Получаем ширину ламели в мм и конвертируем в метры
    lamella_width_mm = LAMELLA_TYPES.get(lamella_type, {}).get("width", 0)
    
    if lamella_width_mm <= 0:
        return 0
    
    # Конвертируем ширину ламели в метры
    lamella_width_m = lamella_width_mm / 1000
    
    # Рассчитываем количество ламелей
    count = length_m / lamella_width_m
    
    # Округляем до ближайшего целого числа в большую сторону
    return math.ceil(count)

def calculate_additional_columns(pergola_type, lamella_type, length_m, width_m):
    """
    Определяет, требуются ли дополнительные колонны для перголы и рассчитывает их стоимость
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600PIR)
        lamella_type (str): Тип ламели
        length_m (float): Длина (вынос) перголы в метрах
        width_m (float): Ширина перголы в метрах
        
    Returns:
        tuple: (требуются ли дополнительные колонны (bool), стоимость дополнительных колонн (float), количество модулей)
    """
    # Определяем ключ для проверки порога длины
    if pergola_type == "B600NEW" or pergola_type == "B600":
        threshold_key = "B600PIR"
    else:
        # Определяем размер ламели (200 или 250 мм)
        lamella_size = "200" if "200" in lamella_type else "250"
        threshold_key = f"{pergola_type.replace('NEW', '')}-{lamella_size}"
    
    # Получаем пороговое значение для данного типа перголы и ламели
    threshold = ADDITIONAL_COLUMNS_THRESHOLDS.get(threshold_key, 0)
    
    # Если пороговое значение не указано, дополнительные колонны не требуются
    if threshold == 0:
        return False, 0, 0
    
    # Проверяем, превышает ли длина пороговое значение
    if length_m <= threshold:
        return False, 0, 0
    
    # Определяем количество модулей на основе ширины перголы
    # Модуль - это секция перголы определенной ширины
    # Примерные размеры: 1 модуль - до 4м, 2 модуля - до 7м, 3 модуля - до 10м
    modules = 1
    if width_m > 7:
        modules = 3
    elif width_m > 4:
        modules = 2
    
    # Рассчитываем стоимость дополнительных колонн
    columns_cost = ADDITIONAL_COLUMNS_PRICES.get(modules, 0)
    
    return True, columns_cost, modules

def adjust_length_to_lamella_count(length_m, lamella_type):
    """
    Корректирует длину (вынос) перголы для соответствия целому числу ламелей
    
    Args:
        length_m (float): Оригинальная длина перголы в метрах
        lamella_type (str): Тип ламели
        
    Returns:
        tuple: (скорректированная длина в метрах, количество ламелей, сообщение о корректировке)
    """
    # Для перголы B600 корректировка не нужна
    if lamella_type == "B600":
        return length_m, 0, None
    
    # Получаем ширину ламели в мм и конвертируем в метры
    lamella_width_mm = LAMELLA_TYPES.get(lamella_type, {}).get("width", 0)
    
    if lamella_width_mm <= 0:
        return length_m, 0, None
    
    # Конвертируем ширину ламели в метры
    lamella_width_m = lamella_width_mm / 1000
    
    # Рассчитываем количество ламелей
    lamella_count_exact = length_m / lamella_width_m
    lamella_count = math.ceil(lamella_count_exact)
    
    # Если количество ламелей не целое число, корректируем длину
    if lamella_count != lamella_count_exact:
        adjusted_length_m = lamella_count * lamella_width_m
        
        # Округляем до 3 знаков после запятой
        adjusted_length_m = round(adjusted_length_m, 3)
        
        correction_message = (
            f"Длина перголы была скорректирована с {length_m:.3f} м до {adjusted_length_m:.3f} м "
            f"для соответствия целому числу ламелей ({lamella_count} шт.)"
        )
        
        return adjusted_length_m, lamella_count, correction_message
    
    # Если корректировка не требуется
    return length_m, lamella_count, None

def calculate_pergola_cost(dimensions, options):
    """
    Рассчитывает стоимость перголы на основе заданных размеров и опций.
    
    Args:
        dimensions (dict): Словарь с размерами перголы (ширина, длина, высота) в метрах
        options (dict): Словарь с выбранными опциями
        
    Returns:
        dict: Словарь с результатами расчетов
    """
    try:
        # Извлекаем данные из входных параметров (уже в метрах)
        width_m = dimensions.get('width', 0)
        length_m = dimensions.get('length', 0)
        height_m = dimensions.get('height', 0)
        
        # Округляем до 3 знаков после запятой для точности расчетов
        width_m = round(width_m, 3)
        length_m = round(length_m, 3)
        height_m = round(height_m, 3)
        
        # Конвертируем в миллиметры для некоторых расчетов
        width_mm = width_m * 1000
        length_mm = length_m * 1000
        height_mm = height_m * 1000
        
        pergola_type = options.get('pergola_type', '')
        lamella_type = options.get('lamella_type', '')
        lighting_type = options.get('lighting_type', 'none')
        additional_options = options.get('additional_options', [])
        
        # Валидация конфигурации перголы
        validation_error = validate_pergola_config(pergola_type, lamella_type, width_m, length_m)
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
            length_m, lamella_count, correction_message = adjust_length_to_lamella_count(length_m, lamella_type)
            if correction_message:
                logger.info(correction_message)
                # Обновляем длину в мм после корректировки
                length_mm = length_m * 1000
        else:
            # Если коррекция не применяется, просто рассчитываем количество ламелей
            lamella_count = calculate_lamella_count(length_m, lamella_type)
        
        # Получаем базовую цену перголы
        # Сохраняем исходные размеры для проверки корректировки размеров из прайс-листа
        original_width_m, original_length_m = width_m, length_m
        
        base_price = get_base_price(pergola_type, lamella_type, width_m, length_m)
        
        # Получаем скорректированные размеры для проверки изменений
        from utils.price_loader import find_nearest_dimensions, price_tables, PERGOLA_PRICE_FILES
        
        # Определяем файл с ценами
        price_file = None
        if lamella_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[lamella_type]
        elif pergola_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[pergola_type]
        
        # Проверяем изменение размеров для соответствия прайс-листу
        if price_file and price_file in price_tables:
            price_dict = price_tables[price_file]
            adjusted_width_m, adjusted_length_m = find_nearest_dimensions(price_dict, width_m, length_m)
            
            # Если размеры были скорректированы для соответствия прайс-листу
            if (abs(adjusted_width_m - original_width_m) > 0.01 or 
                abs(adjusted_length_m - original_length_m) > 0.01):
                
                # Добавляем информацию о корректировке размеров
                price_correction_message = (
                    f"Расчет произведен по размерам {adjusted_width_m:.1f}×{adjusted_length_m:.1f} м "
                    f"в соответствии с прайс-листом (ближайшее большее значение)"
                )
                
                # Обновляем или добавляем сообщение о корректировке
                if correction_message:
                    correction_message = f"{correction_message}. {price_correction_message}"
                else:
                    correction_message = price_correction_message
                
                logger.info(price_correction_message)
                
                # Обновляем размеры в соответствии с прайс-листом
                width_m, length_m = adjusted_width_m, adjusted_length_m
                width_mm, length_mm = width_m * 1000, length_m * 1000
        
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
            'additional_columns': 0,
            'additional_options': {}
        }
        
        # Проверяем необходимость добавления дополнительных колонн
        need_additional_columns, columns_cost, modules_count = calculate_additional_columns(
            pergola_type, lamella_type, length_m, width_m
        )
        
        # Если нужны дополнительные колонны, добавляем их стоимость
        if need_additional_columns:
            detailed_costs['additional_columns'] = columns_cost
            
            # Добавляем информацию о дополнительных колоннах в сообщение
            columns_message = (
                f"Для перголы с выносом {length_m:.3f} м необходимы дополнительные колонны "
                f"({modules_count} {'модуль' if modules_count == 1 else 'модуля' if modules_count < 5 else 'модулей'}, "
                f"стоимость: {columns_cost} €)"
            )
            
            # Добавляем сообщение о колоннах к общему сообщению о корректировке
            if correction_message:
                correction_message = f"{correction_message}. {columns_message}"
            else:
                correction_message = columns_message
                
            logger.info(columns_message)
        
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
        total_cost += detailed_costs['additional_columns']
        total_cost += sum(detailed_costs['additional_options'].values())
        
        # Формируем результат
        result = {
            'total_cost': round(total_cost, 2),
            'detailed_costs': detailed_costs,
            'dimensions': {
                'width_mm': width_mm,
                'width_m': round(width_m, 3),
                'length_mm': length_mm,
                'length_m': round(length_m, 3),
                'height_mm': height_mm,
                'height_m': round(height_m, 3)
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