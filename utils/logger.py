"""
Модуль для настройки логирования в приложении
"""
import os
import logging
import datetime

# Создаем директорию для логов, если она не существует
os.makedirs('logs', exist_ok=True)

def setup_logger(name=None, level=logging.INFO):
    """
    Настраивает логгер с указанным именем и уровнем логирования
    
    Args:
        name (str, optional): Имя логгера
        level (int, optional): Уровень логирования
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Если имя не указано, используем корневой логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Проверяем, есть ли уже обработчики у этого логгера
    if not logger.handlers:
        # Создаем обработчик для вывода в файл
        log_file = f"logs/{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # Создаем форматтер для логов
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Назначаем форматтер обработчику
        file_handler.setFormatter(formatter)
        
        # Добавляем обработчик к логгеру
        logger.addHandler(file_handler)
        
        # Также добавим обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def log_user_action(action, details=None):
    """
    Логирует действие пользователя
    
    Args:
        action (str): Название действия
        details (dict, optional): Дополнительные детали о действии
    """
    logger = logging.getLogger('user_actions')
    
    if details:
        logger.info(f"USER ACTION: {action} - {details}")
    else:
        logger.info(f"USER ACTION: {action}")

def log_calculation(dimensions, options, results):
    """
    Логирует расчет стоимости перголы
    
    Args:
        dimensions (dict): Размеры перголы
        options (dict): Опции перголы
        results (dict): Результаты расчета
    """
    logger = logging.getLogger('calculations')
    
    # Краткий результат для лога
    if results.get('success', False):
        price_eur = results.get('total_price_eur', 0)
        price_rub = results.get('total_price_rub', 0)
        logger.info(f"CALCULATION: {dimensions} + {options} = {price_eur}€ / {price_rub}₽")
    else:
        error = results.get('error_message', 'Unknown error')
        logger.error(f"CALCULATION FAILED: {dimensions} + {options} - {error}")

# Настройка корневого логгера при импорте модуля
root_logger = setup_logger()