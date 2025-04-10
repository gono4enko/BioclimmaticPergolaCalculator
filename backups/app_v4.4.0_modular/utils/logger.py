"""
Модуль для настройки логирования в приложении калькулятора пергол.
"""
import os
import logging
from datetime import datetime

# Создаем директорию для логов, если она не существует
os.makedirs('logs', exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO):
    """
    Настраивает и возвращает логгер с указанным именем и файлом для записи.
    
    Args:
        name (str): Имя логгера
        log_file (str): Путь к файлу для записи логов
        level (int): Уровень логирования (по умолчанию logging.INFO)
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем логгер с указанным именем
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Предотвращаем дублирование обработчиков при повторном вызове
    if not logger.handlers:
        # Создаем обработчик для записи в файл
        file_handler = logging.FileHandler(log_file)
        
        # Создаем форматтер для логов
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Добавляем обработчик к логгеру
        logger.addHandler(file_handler)
    
    return logger

# Создаем основной логгер приложения
app_logger = setup_logger('pergola_calculator', 'logs/app.log')

def log_app_start():
    """
    Записывает в лог информацию о запуске приложения
    """
    app_logger.info(f"Приложение запущено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def log_calculation(dimensions, options, results=None, error=None):
    """
    Записывает в лог информацию о выполненном расчете
    
    Args:
        dimensions (dict): Размеры перголы
        options (dict): Выбранные опции
        results (dict, optional): Результаты расчета
        error (str, optional): Сообщение об ошибке, если расчет не удался
    """
    if error:
        app_logger.error(f"Ошибка при расчете перголы: {error}")
        app_logger.error(f"Параметры: {dimensions}, {options}")
    else:
        app_logger.info(f"Выполнен расчет перголы с параметрами: {dimensions}, {options}")
        if results:
            app_logger.info(f"Базовая стоимость: {results.get('base_price', 0)} евро")
            app_logger.info(f"Общая стоимость: {results.get('total_price', 0)} евро")

def log_user_interaction(action, details=None):
    """
    Записывает в лог информацию о действиях пользователя
    
    Args:
        action (str): Действие пользователя
        details (dict, optional): Дополнительная информация о действии
    """
    log_str = f"Пользовательское действие: {action}"
    if details:
        log_str += f", детали: {details}"
    app_logger.info(log_str)