"""
Модуль для валидации входных данных калькулятора пергол
"""
import logging
from config.pergola_types import PERGOLA_TYPES, PERGOLA_LIMITS

# Получаем логгер
logger = logging.getLogger(__name__)

def validate_dimensions(dimensions):
    """
    Проверяет валидность введенных размеров перголы
    
    Args:
        dimensions (dict): Словарь с размерами перголы в метрах
        
    Returns:
        str or None: Сообщение об ошибке или None, если данные валидны
    """
    try:
        width = dimensions.get('width', 0)
        length = dimensions.get('length', 0)
        height = dimensions.get('height', 0)
        
        # Проверка наличия всех необходимых размеров
        if not width or not length:
            return "Необходимо указать ширину и длину перголы"
        
        # Проверка типов данных
        if not isinstance(width, (int, float)) or not isinstance(length, (int, float)):
            return "Ширина и длина должны быть числами"
        
        if height and not isinstance(height, (int, float)):
            return "Высота должна быть числом"
        
        # Проверка ограничений по минимальным и максимальным размерам
        if width < 1.0 or width > 7.0:
            return "Ширина должна быть от 1.0 до 7.0 м"
        
        if length < 1.0 or length > 7.0:
            return "Длина должна быть от 1.0 до 7.0 м"
        
        if height and (height < 2.0 or height > 3.0):
            return "Высота должна быть от 2.0 до 3.0 м"
        
        return None
    
    except Exception as e:
        logger.error(f"Ошибка при валидации размеров: {str(e)}", exc_info=True)
        return f"Произошла ошибка при проверке размеров: {str(e)}"

def validate_pergola_config(pergola_type, lamella_type, width_m, length_m):
    """
    Проверяет совместимость выбранных типов перголы и ламелей,
    а также соответствие размеров перголы ограничениям модели
    
    Args:
        pergola_type (str): Тип перголы
        lamella_type (str): Тип ламелей
        width_m (float): Ширина перголы в метрах
        length_m (float): Длина перголы в метрах
        
    Returns:
        str or None: Сообщение об ошибке или None, если конфигурация валидна
    """
    try:
        # Проверка наличия типа перголы в списке доступных
        if pergola_type not in PERGOLA_TYPES:
            return f"Тип перголы '{pergola_type}' не поддерживается"
        
        # Проверка наличия типа ламелей в списке доступных для выбранного типа перголы
        pergola_info = PERGOLA_TYPES.get(pergola_type, {})
        available_lamellas = pergola_info.get('lamella_types', [])
        
        if lamella_type not in available_lamellas:
            return f"Тип ламелей '{lamella_type}' не доступен для перголы типа '{pergola_type}'"
        
        # Проверка соответствия размеров ограничениям для выбранного типа перголы
        limits = PERGOLA_LIMITS.get(pergola_type, {})
        
        # Конвертируем ограничения из мм в метры
        min_width_m = limits.get('min_width', 1000) / 1000
        max_width_m = limits.get('max_width', 7000) / 1000
        min_length_m = limits.get('min_length', 1000) / 1000
        max_length_m = limits.get('max_length', 7000) / 1000
        
        if width_m < min_width_m or width_m > max_width_m:
            return f"Ширина перголы должна быть от {min_width_m:.1f} до {max_width_m:.1f} м для типа '{pergola_type}'"
        
        if length_m < min_length_m or length_m > max_length_m:
            return f"Длина перголы должна быть от {min_length_m:.1f} до {max_length_m:.1f} м для типа '{pergola_type}'"
        
        return None
    
    except Exception as e:
        logger.error(f"Ошибка при валидации конфигурации перголы: {str(e)}", exc_info=True)
        return f"Произошла ошибка при проверке конфигурации: {str(e)}"