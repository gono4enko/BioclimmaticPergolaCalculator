"""
Тестирование актуальных данных о ценах в калькуляторе пергол
"""
import logging
from config.price_data import (
    REMOTE_CONTROL_PRICES, LIGHTING_PRICES, BANSBACH_PRICES, SOMFY_PRICES,
    calculate_lighting_perimeter
)

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test_prices.log',
    filemode='w'
)

logger = logging.getLogger(__name__)

def test_remote_control_prices():
    """
    Тест цен на пульты ДУ
    """
    logger.info("Тестирование цен на пульты ДУ")
    logger.info(f"Simu 1K: {REMOTE_CONTROL_PRICES['Simu 1K']} евро")
    logger.info(f"Simu 5K: {REMOTE_CONTROL_PRICES['Simu 5K']} евро")
    logger.info(f"Simu 15K: {REMOTE_CONTROL_PRICES['Simu 15K']} евро")
    
    assert REMOTE_CONTROL_PRICES['Simu 1K'] == 25, "Неверная цена на пульт Simu 1K"
    assert REMOTE_CONTROL_PRICES['Simu 5K'] == 40, "Неверная цена на пульт Simu 5K"
    assert REMOTE_CONTROL_PRICES['Simu 15K'] == 90, "Неверная цена на пульт Simu 15K"
    
    logger.info("Тест цен на пульты ДУ успешно пройден")

def test_lighting_prices():
    """
    Тест цен на освещение
    """
    logger.info("Тестирование цен на освещение")
    
    # Проверка для одномодульной перголы 4x4 м (периметр 16 м)
    width_m, length_m = 4, 4
    modules = 1
    
    perimeter = calculate_lighting_perimeter(width_m, length_m, modules)
    logger.info(f"Периметр одномодульной перголы {width_m}x{length_m} м: {perimeter} м")
    
    # Проверка цены LED освещения (20 евро/метр + 300 евро блок управления)
    led_price = LIGHTING_PRICES['led'](width_m, length_m, modules)
    expected_led_price = 20 * perimeter + 300 * modules
    logger.info(f"Цена LED освещения: {led_price} евро")
    assert led_price == expected_led_price, "Неверная цена на LED освещение"
    
    # Проверка цены RGB освещения (20 евро/метр + 300 евро блок управления)
    rgb_price = LIGHTING_PRICES['rgb'](width_m, length_m, modules)
    expected_rgb_price = 20 * perimeter + 300 * modules
    logger.info(f"Цена RGB освещения: {rgb_price} евро")
    assert rgb_price == expected_rgb_price, "Неверная цена на RGB освещение"
    
    # Проверка цены комбинированного LED+RGB освещения (40 евро/метр + 300 евро блок управления)
    led_rgb_price = LIGHTING_PRICES['led_rgb'](width_m, length_m, modules)
    expected_led_rgb_price = 40 * perimeter + 300 * modules
    logger.info(f"Цена LED+RGB освещения: {led_rgb_price} евро")
    assert led_rgb_price == expected_led_rgb_price, "Неверная цена на LED+RGB освещение"
    
    logger.info("Тест цен на освещение успешно пройден")

def test_drive_prices():
    """
    Тест цен на системы автоматизации
    """
    logger.info("Тестирование цен на системы автоматизации")
    
    # Проверка цен автоматики Bansbach для B500NEW
    logger.info(f"Bansbach T1: {BANSBACH_PRICES['T1']} евро")
    logger.info(f"Bansbach Tandem: {BANSBACH_PRICES['Tandem']} евро")
    
    assert BANSBACH_PRICES['T1'] == 700, "Неверная цена на привод Bansbach T1"
    assert BANSBACH_PRICES['Tandem'] == 1250, "Неверная цена на привод Bansbach Tandem"
    
    # Проверка цен автоматики Somfy для B700NEW
    logger.info(f"Somfy M1: {SOMFY_PRICES['M1']} евро")
    logger.info(f"Somfy M2 TANDEM: {SOMFY_PRICES['M2_TANDEM']} евро")
    
    assert SOMFY_PRICES['M1'] == 300, "Неверная цена на привод Somfy M1"
    assert SOMFY_PRICES['M2_TANDEM'] == 1000, "Неверная цена на привод Somfy M2 TANDEM"
    
    logger.info("Тест цен на системы автоматизации успешно пройден")

if __name__ == "__main__":
    logger.info("Начало тестирования цен")
    test_remote_control_prices()
    test_lighting_prices()
    test_drive_prices()
    logger.info("Все тесты цен успешно пройдены")
    print("Все тесты цен успешно пройдены")