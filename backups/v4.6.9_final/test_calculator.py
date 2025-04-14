"""
Тестирование функциональности калькулятора стоимости пергол
"""
import logging
import sys
from utils.calculator import calculate_pergola_cost
from utils.price_loader import load_price_tables

# Настройка логгирования с выводом на консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_calculator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_b500_standard():
    """
    Тест расчета B500NEW с ламелями 200 мм (стандартная конфигурация)
    """
    logger.info("-" * 80)
    logger.info("Тест B500NEW со стандартными ламелями 200 мм")
    
    dimensions = {'width': 3.0, 'length': 4.0, 'height': 2.3}
    options = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-20NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    result = calculate_pergola_cost(dimensions, options)
    
    logger.info(f"Результат расчета: {result}")
    logger.info(f"Базовая цена: {result.get('detailed_costs', {}).get('base_price', 0)} €")
    logger.info(f"Автоматика: {result.get('detailed_costs', {}).get('additional_options', {}).get('automation', 0)} €")
    logger.info(f"Общая стоимость: {result.get('total_cost', 0)} €")
    
    if result.get('error'):
        logger.error(f"Ошибка расчета: {result.get('error')}")
    else:
        logger.info(f"Проверка на оптимизацию длины: {result.get('correction_message', '')}")
    
    return result
    
def test_b500_with_led():
    """
    Тест расчета B500NEW с освещением LED
    """
    logger.info("-" * 80)
    logger.info("Тест B500NEW со стандартными ламелями 200 мм и LED освещением")
    
    dimensions = {'width': 3.0, 'length': 4.0, 'height': 2.3}
    options = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-20NEW',
        'lighting_type': 'led',
        'additional_options': []
    }
    
    result = calculate_pergola_cost(dimensions, options)
    
    logger.info(f"Результат расчета: {result}")
    logger.info(f"Базовая цена: {result.get('detailed_costs', {}).get('base_price', 0)} €")
    logger.info(f"Автоматика: {result.get('detailed_costs', {}).get('additional_options', {}).get('automation', 0)} €")
    logger.info(f"Освещение: {result.get('detailed_costs', {}).get('lighting', 0)} €")
    logger.info(f"Общая стоимость: {result.get('total_cost', 0)} €")
    
    if result.get('error'):
        logger.error(f"Ошибка расчета: {result.get('error')}")
    
    return result
    
def test_b500_large_with_led():
    """
    Тест расчета большой B500NEW (требующей дополнительных колонн)
    """
    logger.info("-" * 80)
    logger.info("Тест большой B500NEW с ламелями 200 мм (требующей дополнительных колонн)")
    
    dimensions = {'width': 7.0, 'length': 7.0, 'height': 2.3}
    options = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-20NEW',
        'lighting_type': 'led',
        'additional_options': []
    }
    
    result = calculate_pergola_cost(dimensions, options)
    
    logger.info(f"Результат расчета: {result}")
    logger.info(f"Базовая цена: {result.get('detailed_costs', {}).get('base_price', 0)} €")
    logger.info(f"Автоматика: {result.get('detailed_costs', {}).get('additional_options', {}).get('automation', 0)} €")
    logger.info(f"Освещение: {result.get('detailed_costs', {}).get('lighting', 0)} €")
    logger.info(f"Дополнительные колонны: {result.get('detailed_costs', {}).get('additional_columns', 0)} €")
    logger.info(f"Общая стоимость: {result.get('total_cost', 0)} €")
    
    if result.get('error'):
        logger.error(f"Ошибка расчета: {result.get('error')}")
    else:
        logger.info(f"Проверка на дополнительные колонны: {result.get('correction_message', '')}")
    
    return result
    
def test_b700_standard():
    """
    Тест расчета B700NEW со стандартными ламелями 250 мм
    """
    logger.info("-" * 80)
    logger.info("Тест B700NEW со стандартными ламелями 250 мм")
    
    dimensions = {'width': 3.0, 'length': 4.0, 'height': 2.3}
    options = {
        'pergola_type': 'B700NEW',
        'lamella_type': 'B700-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    result = calculate_pergola_cost(dimensions, options)
    
    logger.info(f"Результат расчета: {result}")
    logger.info(f"Базовая цена: {result.get('detailed_costs', {}).get('base_price', 0)} €")
    logger.info(f"Автоматика: {result.get('detailed_costs', {}).get('additional_options', {}).get('automation', 0)} €")
    logger.info(f"Общая стоимость: {result.get('total_cost', 0)} €")
    
    if result.get('error'):
        logger.error(f"Ошибка расчета: {result.get('error')}")
    
    return result
    
def test_b600_standard():
    """
    Тест расчета B600 (станционарные панели PIR)
    """
    logger.info("-" * 80)
    logger.info("Тест B600 со стационарными PIR панелями")
    
    dimensions = {'width': 3.0, 'length': 4.0, 'height': 2.3}
    options = {
        'pergola_type': 'B600',
        'lamella_type': 'B600',
        'lighting_type': 'none',
        'additional_options': ['automation']
    }
    
    result = calculate_pergola_cost(dimensions, options)
    
    logger.info(f"Результат расчета: {result}")
    logger.info(f"Базовая цена: {result.get('detailed_costs', {}).get('base_price', 0)} €")
    logger.info(f"Автоматика: {result.get('detailed_costs', {}).get('additional_options', {}).get('automation', 0)} €")
    logger.info(f"Общая стоимость: {result.get('total_cost', 0)} €")
    
    if result.get('error'):
        logger.error(f"Ошибка расчета: {result.get('error')}")
    
    return result

def test_b700_with_non_standard_size():
    """
    Тест расчета B700NEW с нестандартным размером (проверка выбора ближайшей цены)
    """
    logger.info("-" * 80)
    logger.info("Тест B700NEW с нестандартным размером (проверка выбора ближайшей цены)")
    
    dimensions = {'width': 3.2, 'length': 4.3, 'height': 2.3}
    options = {
        'pergola_type': 'B700NEW',
        'lamella_type': 'B700-20NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    result = calculate_pergola_cost(dimensions, options)
    
    logger.info(f"Результат расчета: {result}")
    logger.info(f"Исходные размеры: {dimensions['width']}x{dimensions['length']} м")
    logger.info(f"Базовая цена: {result.get('detailed_costs', {}).get('base_price', 0)} €")
    logger.info(f"Автоматика: {result.get('detailed_costs', {}).get('additional_options', {}).get('automation', 0)} €")
    logger.info(f"Общая стоимость: {result.get('total_cost', 0)} €")
    
    if result.get('error'):
        logger.error(f"Ошибка расчета: {result.get('error')}")
    else:
        logger.info(f"Корректировка размеров: {result.get('correction_message', '')}")
    
    return result

if __name__ == "__main__":
    logger.info("Запуск тестирования калькулятора стоимости пергол")
    
    # Перезагружаем таблицы цен
    load_price_tables()
    
    # Запускаем тесты
    test_b500_standard()
    test_b500_with_led()
    test_b500_large_with_led()
    test_b700_standard()
    test_b600_standard()
    test_b700_with_non_standard_size()
    
    logger.info("Тестирование завершено")