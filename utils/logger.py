"""
Модуль для логирования действий пользователя и результатов расчетов в калькуляторе пергол.
"""
import os
import logging
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """
    Настраивает и возвращает логгер с заданным именем и файлом.
    
    Args:
        name (str): Имя логгера
        log_file (str): Путь к файлу логов
        level (int, optional): Уровень логирования (по умолчанию logging.INFO)
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

def log_user_action(action_type, action_details):
    """
    Логирует действие пользователя в системе.
    
    Args:
        action_type (str): Тип действия (например, 'calculation', 'export_pdf')
        action_details (dict): Детали действия в виде словаря
    """
    # Создаем директорию для логов, если она не существует
    os.makedirs('logs', exist_ok=True)
    
    # Настраиваем логгер для действий пользователя
    logger = setup_logger('user_actions', 'logs/user_actions.log')
    
    # Форматируем сообщение
    message = f"ACTION: {action_type} - {action_details}"
    
    # Записываем в лог
    logger.info(message)

def log_calculation(dimensions, options, results):
    """
    Логирует результаты расчета перголы.
    
    Args:
        dimensions (dict): Размеры перголы
        options (dict): Выбранные опции
        results (dict): Результаты расчета
    """
    # Создаем директорию для логов, если она не существует
    os.makedirs('logs', exist_ok=True)
    
    # Настраиваем логгер для расчетов
    logger = setup_logger('calculations', 'logs/calculations.log')
    
    # Создаем краткую версию результатов для лога
    log_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'dimensions': dimensions,
        'pergola_type': options.get('pergola_type', 'unknown'),
        'total_price_euro': results.get('total_price', 0),
        'total_price_rub': results.get('total_price', 0) * results.get('euro_rate', 85)
    }
    
    # Записываем в лог
    logger.info(f"CALCULATION: {log_data}")