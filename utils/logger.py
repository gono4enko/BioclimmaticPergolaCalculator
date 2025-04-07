"""
Модуль для настройки логирования
"""
import os
import json
import logging
import datetime

# Форматтер для логов
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Путь к директории логов
LOG_DIR = 'logs'

def setup_logger(log_file=None):
    """
    Настраивает логирование для приложения
    
    Args:
        log_file (str, optional): Путь к файлу лога. По умолчанию None.
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию для логов, если она не существует
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Если файл лога не указан, создаем файл с датой и временем
    if log_file is None:
        now = datetime.datetime.now()
        log_file = os.path.join(LOG_DIR, f'calculator_{now.strftime("%Y%m%d_%H%M%S")}.log')
    
    # Настраиваем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Очищаем существующие обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Добавляем обработчик для вывода в файл
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Добавляем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    logger.info(f"Логирование настроено в файл: {log_file}")
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
        try:
            details_str = json.dumps(details, ensure_ascii=False)
            logger.info(f"Действие пользователя: {action}, детали: {details_str}")
        except Exception as e:
            logger.warning(f"Не удалось сериализовать детали действия: {str(e)}")
            logger.info(f"Действие пользователя: {action}")
    else:
        logger.info(f"Действие пользователя: {action}")

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
    
    try:
        # Логируем входные данные
        dimensions_str = json.dumps(dimensions, ensure_ascii=False)
        options_str = json.dumps(options, ensure_ascii=False)
        
        logger.info(f"Расчет стоимости перголы, размеры: {dimensions_str}, опции: {options_str}")
        
        # Логируем результат или ошибку
        if error:
            logger.error(f"Ошибка расчета: {error}")
        elif result:
            result_str = json.dumps(result, ensure_ascii=False)
            logger.info(f"Результат расчета: {result_str}")
        
    except Exception as e:
        logger.warning(f"Не удалось записать лог расчета: {str(e)}")