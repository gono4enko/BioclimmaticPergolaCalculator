"""
Модуль для настройки логирования
"""
import logging
import os
from datetime import datetime

def setup_logger(log_file=None):
    """
    Настраивает логирование для приложения
    
    Args:
        log_file (str, optional): Путь к файлу лога. По умолчанию None.
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Определяем формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Очищаем существующие обработчики
    if logger.handlers:
        logger.handlers.clear()
    
    # Добавляем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Если указан файл, добавляем обработчик для записи в файл
    if log_file:
        # Создаем директорию для логов, если её нет
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Логирование настроено. Лог-файл: {log_file}")
    else:
        logger.info("Логирование настроено только для консоли")
    
    return logger

def log_user_action(action, details=None):
    """
    Логирует действие пользователя
    
    Args:
        action (str): Описание действия
        details (dict, optional): Детали действия. По умолчанию None.
    """
    logger = logging.getLogger(__name__)
    
    if details:
        logger.info(f"Пользовательское действие: {action}. Детали: {details}")
    else:
        logger.info(f"Пользовательское действие: {action}")

def log_calculation(dimensions, options, result=None, error=None):
    """
    Логирует процесс расчета
    
    Args:
        dimensions (dict): Размеры перголы
        options (dict): Выбранные опции
        result (dict, optional): Результат расчета. По умолчанию None.
        error (str, optional): Сообщение об ошибке. По умолчанию None.
    """
    logger = logging.getLogger(__name__)
    
    if error:
        logger.error(f"Ошибка расчета. Размеры: {dimensions}, Опции: {options}. Ошибка: {error}")
    elif result:
        logger.info(f"Успешный расчет. Размеры: {dimensions}, Опции: {options}. Итоговая стоимость: {result.get('total_cost')} евро")
    else:
        logger.info(f"Начат расчет. Размеры: {dimensions}, Опции: {options}")
