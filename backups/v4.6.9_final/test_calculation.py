"""
Тестирование обновленных расчетов стоимости пергол с учетом новых данных из прайсов
"""
import logging
from utils.calculator import calculate_pergola_cost
from config.price_data import REMOTE_CONTROL_PRICES, BANSBACH_PRICES, SOMFY_PRICES

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test_calculation.log',
    filemode='w'
)

logger = logging.getLogger(__name__)

def test_calculation_with_modules():
    """
    Тестирование расчетов с учетом количества модулей
    """
    logger.info("Тестирование расчетов с учетом количества модулей")
    
    # Тест B500NEW с ламелями 200 мм (1 модуль)
    dimensions_small = {'width': 3.5, 'length': 4.0, 'height': 2.5}
    options_small = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-20NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B500NEW с ламелями 200 мм (2 модуля)
    dimensions_medium = {'width': 7.0, 'length': 4.0, 'height': 2.5}
    options_medium = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-20NEW',
        'lighting_type': 'led',
        'additional_options': []
    }
    
    # Тест B500NEW с ламелями 200 мм (3 модуля)
    dimensions_large = {'width': 10.5, 'length': 4.0, 'height': 2.5}
    options_large = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-20NEW',
        'lighting_type': 'led_rgb',
        'additional_options': []
    }
    
    # Проводим расчеты
    results_small = calculate_pergola_cost(dimensions_small, options_small)
    results_medium = calculate_pergola_cost(dimensions_medium, options_medium)
    results_large = calculate_pergola_cost(dimensions_large, options_large)
    
    # Проверяем количество модулей
    logger.info(f"Результаты расчета для перголы {dimensions_small['width']}x{dimensions_small['length']} м: {results_small.keys()}")
    
    # Используем правильные ключи для доступа к количеству модулей
    modules_small = results_small.get('detailed_costs', {}).get('modules', 1)
    modules_medium = results_medium.get('detailed_costs', {}).get('modules', 2)
    modules_large = results_large.get('detailed_costs', {}).get('modules', 3)
    
    logger.info(f"Перголы шириной {dimensions_small['width']} м: {modules_small} модуль")
    logger.info(f"Перголы шириной {dimensions_medium['width']} м: {modules_medium} модуля")
    logger.info(f"Перголы шириной {dimensions_large['width']} м: {modules_large} модуля")
    
    # Проверяем стоимость пультов ДУ
    logger.info(f"Пульт для перголы с 1 модулем: {results_small['detailed_costs'].get('remote_control')} - {results_small['detailed_costs'].get('remote_control_cost')} €")
    logger.info(f"Пульт для перголы с 2 модулями: {results_medium['detailed_costs'].get('remote_control')} - {results_medium['detailed_costs'].get('remote_control_cost')} €")
    logger.info(f"Пульт для перголы с 3 модулями: {results_large['detailed_costs'].get('remote_control')} - {results_large['detailed_costs'].get('remote_control_cost')} €")
    
    # Проверяем стоимость автоматики
    automation_small = results_small['detailed_costs'].get('additional_options', {}).get('automation', 0)
    automation_medium = results_medium['detailed_costs'].get('additional_options', {}).get('automation', 0)
    automation_large = results_large['detailed_costs'].get('additional_options', {}).get('automation', 0)
    
    logger.info(f"Автоматика для перголы с 1 модулем: {automation_small} € ({results_small['detailed_costs'].get('automation_type')})")
    logger.info(f"Автоматика для перголы с 2 модулями: {automation_medium} € ({results_medium['detailed_costs'].get('automation_type')})")
    logger.info(f"Автоматика для перголы с 3 модулями: {automation_large} € ({results_large['detailed_costs'].get('automation_type')})")
    
    # Проверяем стоимость освещения
    led_small = results_small['detailed_costs'].get('additional_options', {}).get('lighting', 0)
    led_medium = results_medium['detailed_costs'].get('additional_options', {}).get('lighting', 0)
    led_large = results_large['detailed_costs'].get('additional_options', {}).get('lighting', 0)
    
    logger.info(f"Освещение для перголы с 1 модулем: {led_small} € ({options_small['lighting_type']})")
    logger.info(f"Освещение для перголы с 2 модулями: {led_medium} € ({options_medium['lighting_type']})")
    logger.info(f"Освещение для перголы с 3 модулями: {led_large} € ({options_large['lighting_type']})")

def test_somfy_drive_selection():
    """
    Тестирование выбора привода Somfy для B700NEW
    """
    logger.info("Тестирование выбора привода Somfy для B700NEW")
    
    # Тест B700NEW с шириной 3.0м и выносом 7.5м - должен выбираться M2_TANDEM
    dimensions_tandem1 = {'width': 3.0, 'length': 7.5, 'height': 2.5}
    options_tandem1 = {
        'pergola_type': 'B700NEW',
        'lamella_type': 'B700-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B700NEW с шириной 3.5м и выносом 6.5м - должен выбираться M2_TANDEM
    dimensions_tandem2 = {'width': 3.5, 'length': 6.5, 'height': 2.5}
    options_tandem2 = {
        'pergola_type': 'B700NEW',
        'lamella_type': 'B700-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B700NEW с шириной 7.0м и выносом 6.5м - должен выбираться M2_TANDEM
    dimensions_tandem3 = {'width': 7.0, 'length': 6.5, 'height': 2.5}
    options_tandem3 = {
        'pergola_type': 'B700NEW',
        'lamella_type': 'B700-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B700NEW с шириной 10.5м и выносом 6.5м - должен выбираться M2_TANDEM
    dimensions_tandem4 = {'width': 10.5, 'length': 6.5, 'height': 2.5}
    options_tandem4 = {
        'pergola_type': 'B700NEW',
        'lamella_type': 'B700-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Проводим расчеты
    results_tandem1 = calculate_pergola_cost(dimensions_tandem1, options_tandem1)
    results_tandem2 = calculate_pergola_cost(dimensions_tandem2, options_tandem2)
    results_tandem3 = calculate_pergola_cost(dimensions_tandem3, options_tandem3)
    results_tandem4 = calculate_pergola_cost(dimensions_tandem4, options_tandem4)
    
    # Проверяем типы приводов
    logger.info(f"Привод для B700NEW {dimensions_tandem1['width']}x{dimensions_tandem1['length']} м: {results_tandem1['detailed_costs'].get('automation_type')}")
    logger.info(f"Привод для B700NEW {dimensions_tandem2['width']}x{dimensions_tandem2['length']} м: {results_tandem2['detailed_costs'].get('automation_type')}")
    logger.info(f"Привод для B700NEW {dimensions_tandem3['width']}x{dimensions_tandem3['length']} м: {results_tandem3['detailed_costs'].get('automation_type')}")
    logger.info(f"Привод для B700NEW {dimensions_tandem4['width']}x{dimensions_tandem4['length']} м: {results_tandem4['detailed_costs'].get('automation_type')}")

def test_bansbach_drive_selection():
    """
    Тестирование выбора привода Bansbach для B500NEW
    """
    logger.info("Тестирование выбора привода Bansbach для B500NEW")
    
    # Тест B500NEW с шириной 3.0м и выносом 7.0м - должен выбираться Tandem
    dimensions_tandem1 = {'width': 3.0, 'length': 7.0, 'height': 2.5}
    options_tandem1 = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B500NEW с шириной 4.0м и выносом 5.5м - должен выбираться Tandem
    dimensions_tandem2 = {'width': 4.0, 'length': 5.5, 'height': 2.5}
    options_tandem2 = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B500NEW с шириной 7.0м и выносом 6.0м - должен выбираться Tandem
    dimensions_tandem3 = {'width': 7.0, 'length': 6.0, 'height': 2.5}
    options_tandem3 = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B500NEW с шириной 10.5м и выносом 6.0м - должен выбираться Tandem
    dimensions_tandem4 = {'width': 10.5, 'length': 6.0, 'height': 2.5}
    options_tandem4 = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Проводим расчеты
    results_tandem1 = calculate_pergola_cost(dimensions_tandem1, options_tandem1)
    results_tandem2 = calculate_pergola_cost(dimensions_tandem2, options_tandem2)
    results_tandem3 = calculate_pergola_cost(dimensions_tandem3, options_tandem3)
    results_tandem4 = calculate_pergola_cost(dimensions_tandem4, options_tandem4)
    
    # Проверяем типы приводов
    logger.info(f"Привод для B500NEW {dimensions_tandem1['width']}x{dimensions_tandem1['length']} м: {results_tandem1['detailed_costs'].get('automation_type')}")
    logger.info(f"Привод для B500NEW {dimensions_tandem2['width']}x{dimensions_tandem2['length']} м: {results_tandem2['detailed_costs'].get('automation_type')}")
    logger.info(f"Привод для B500NEW {dimensions_tandem3['width']}x{dimensions_tandem3['length']} м: {results_tandem3['detailed_costs'].get('automation_type')}")
    logger.info(f"Привод для B500NEW {dimensions_tandem4['width']}x{dimensions_tandem4['length']} м: {results_tandem4['detailed_costs'].get('automation_type')}")

def test_gutter_insert():
    """
    Тестирование добавления вставки для усиления лотка при выносе > 6.5м
    """
    logger.info("Тестирование добавления вставки для усиления лотка")
    
    # Тест B500NEW с выносом 7.0м - должна добавляться вставка для усиления лотка
    dimensions_insert = {'width': 4.0, 'length': 7.0, 'height': 2.5}
    options_insert = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Тест B500NEW с выносом 6.0м - не должна добавляться вставка для усиления лотка
    dimensions_no_insert = {'width': 4.0, 'length': 6.0, 'height': 2.5}
    options_no_insert = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # Проводим расчеты
    results_insert = calculate_pergola_cost(dimensions_insert, options_insert)
    results_no_insert = calculate_pergola_cost(dimensions_no_insert, options_no_insert)
    
    # Проверяем наличие вставки для усиления лотка
    gutter_insert = results_insert['detailed_costs'].get('additional_options', {}).get('gutter_insert', 0)
    no_gutter_insert = results_no_insert['detailed_costs'].get('additional_options', {}).get('gutter_insert', 0)
    
    logger.info(f"Вставка для усиления лотка для перголы с выносом {dimensions_insert['length']} м: {gutter_insert} €")
    logger.info(f"Вставка для усиления лотка для перголы с выносом {dimensions_no_insert['length']} м: {no_gutter_insert} €")

def test_remote_control_prices():
    """
    Тестирование цен на пульты ДУ
    """
    logger.info("Тестирование цен на пульты ДУ")
    
    # Проверка цен из конфигурации
    logger.info(f"Simu 1K: {REMOTE_CONTROL_PRICES['Simu 1K']} евро")
    logger.info(f"Simu 5K: {REMOTE_CONTROL_PRICES['Simu 5K']} евро")
    logger.info(f"Simu 15K: {REMOTE_CONTROL_PRICES['Simu 15K']} евро")
    
    # Проверка выбора пультов в зависимости от количества модулей и освещения
    
    # 1 модуль без освещения - Simu 1K
    dimensions_1m = {'width': 4.0, 'length': 4.0, 'height': 2.5}
    options_1m_no_led = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # 1 модуль с освещением - Simu 1K
    options_1m_led = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'led',
        'additional_options': []
    }
    
    # 2 модуля без освещения - Simu 5K
    dimensions_2m = {'width': 7.0, 'length': 4.0, 'height': 2.5}
    options_2m_no_led = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'none',
        'additional_options': []
    }
    
    # 2 модуля с освещением - Simu 5K
    options_2m_led = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'led',
        'additional_options': []
    }
    
    # 3 модуля с освещением - Simu 15K
    dimensions_3m = {'width': 10.5, 'length': 4.0, 'height': 2.5}
    options_3m_led = {
        'pergola_type': 'B500NEW',
        'lamella_type': 'B500-25NEW',
        'lighting_type': 'led',
        'additional_options': []
    }
    
    # Проводим расчеты
    results_1m_no_led = calculate_pergola_cost(dimensions_1m, options_1m_no_led)
    results_1m_led = calculate_pergola_cost(dimensions_1m, options_1m_led)
    results_2m_no_led = calculate_pergola_cost(dimensions_2m, options_2m_no_led)
    results_2m_led = calculate_pergola_cost(dimensions_2m, options_2m_led)
    results_3m_led = calculate_pergola_cost(dimensions_3m, options_3m_led)
    
    # Проверяем выбор пультов
    logger.info(f"1 модуль без освещения: {results_1m_no_led['detailed_costs'].get('remote_control')} - {results_1m_no_led['detailed_costs'].get('remote_control_cost')} €")
    logger.info(f"1 модуль с освещением: {results_1m_led['detailed_costs'].get('remote_control')} - {results_1m_led['detailed_costs'].get('remote_control_cost')} €")
    logger.info(f"2 модуля без освещения: {results_2m_no_led['detailed_costs'].get('remote_control')} - {results_2m_no_led['detailed_costs'].get('remote_control_cost')} €")
    logger.info(f"2 модуля с освещением: {results_2m_led['detailed_costs'].get('remote_control')} - {results_2m_led['detailed_costs'].get('remote_control_cost')} €")
    logger.info(f"3 модуля с освещением: {results_3m_led['detailed_costs'].get('remote_control')} - {results_3m_led['detailed_costs'].get('remote_control_cost')} €")

if __name__ == "__main__":
    logger.info("Начало тестирования расчетов")
    test_calculation_with_modules()
    test_somfy_drive_selection()
    test_bansbach_drive_selection()
    test_gutter_insert()
    test_remote_control_prices()
    logger.info("Тестирование расчетов завершено")
    print("Тестирование расчетов завершено. Результаты в файле test_calculation.log")