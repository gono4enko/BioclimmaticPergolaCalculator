"""
Модуль для валидации входных данных калькулятора пергол
"""
import logging
from config.pergola_types import PERGOLA_TYPES, LAMELLA_TYPES, PERGOLA_LAMELLA_COMPATIBILITY

# Получаем логгер
logger = logging.getLogger(__name__)

def validate_dimensions(dimensions):
    """
    Проверяет валидность введенных размеров перголы
    
    Args:
        dimensions (dict): Словарь с размерами перголы
        
    Returns:
        str or None: Сообщение об ошибке или None, если данные валидны
    """
    try:
        # Проверка на наличие всех необходимых размеров
        required_dims = ['width', 'length', 'height']
        for dim in required_dims:
            if dim not in dimensions:
                return f"Отсутствует обязательный размер: {dim}"
        
        # Проверка типов данных
        for dim, value in dimensions.items():
            if not isinstance(value, (int, float)) or value <= 0:
                return f"Неверное значение для {dim}: {value}. Должно быть положительное число."
        
        # Проверка минимальных и максимальных значений (общие ограничения)
        min_width, max_width = 2000, 7000
        min_length, max_length = 2000, 8000
        min_height, max_height = 2000, 7000
        
        width = dimensions['width']
        length = dimensions['length']
        height = dimensions['height']
        
        if not (min_width <= width <= max_width):
            return f"Ширина должна быть в диапазоне от {min_width} до {max_width} мм"
        
        if not (min_length <= length <= max_length):
            return f"Длина должна быть в диапазоне от {min_length} до {max_length} мм"
        
        if not (min_height <= height <= max_height):
            return f"Высота должна быть в диапазоне от {min_height} до {max_height} мм"
        
        logger.info(f"Размеры валидны: {dimensions}")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при валидации размеров: {str(e)}", exc_info=True)
        return f"Ошибка при валидации размеров: {str(e)}"

def validate_pergola_config(pergola_type, lamella_type, width, length):
    """
    Проверяет совместимость выбранных типов перголы и ламелей,
    а также соответствие размеров перголы ограничениям модели
    
    Args:
        pergola_type (str): Тип перголы
        lamella_type (str): Тип ламелей
        width (int): Ширина перголы в мм
        length (int): Длина перголы в мм
        
    Returns:
        str or None: Сообщение об ошибке или None, если конфигурация валидна
    """
    try:
        # Проверка наличия типа перголы в списке допустимых
        if pergola_type not in PERGOLA_TYPES:
            return f"Неизвестный тип перголы: {pergola_type}"
        
        # Проверка наличия типа ламелей в списке допустимых
        if lamella_type not in LAMELLA_TYPES:
            return f"Неизвестный тип ламелей: {lamella_type}"
        
        # Проверка совместимости типа перголы и ламелей
        if lamella_type not in PERGOLA_LAMELLA_COMPATIBILITY.get(pergola_type, []):
            return f"Ламель типа {lamella_type} не совместима с перголой {pergola_type}"
        
        # Проверка размеров на соответствие ограничениям модели
        pergola_data = PERGOLA_TYPES[pergola_type]
        lamella_data = LAMELLA_TYPES[lamella_type]
        
        if width < pergola_data['min_width'] or width > pergola_data['max_width']:
            return f"Для модели {pergola_type} ширина должна быть в диапазоне от {pergola_data['min_width']} до {pergola_data['max_width']} мм"
        
        if length < pergola_data['min_length'] or length > pergola_data['max_length']:
            return f"Для модели {pergola_type} длина должна быть в диапазоне от {pergola_data['min_length']} до {pergola_data['max_length']} мм"
        
        # Проверка ограничений по ширине ламелей
        if width > lamella_data['max_width']:
            return f"Для ламелей {lamella_type} максимально допустимая ширина перголы: {lamella_data['max_width']} мм"
        
        logger.info(f"Конфигурация валидна: тип {pergola_type}, ламели {lamella_type}, размеры {width}x{length}")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при валидации конфигурации: {str(e)}", exc_info=True)
        return f"Ошибка при валидации конфигурации: {str(e)}"
