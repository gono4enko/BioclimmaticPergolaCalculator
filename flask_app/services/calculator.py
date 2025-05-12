"""
Сервис для расчетов стоимости перголы.
Содержит логику расчета с применением паттерна "Стратегия"
"""
import os
import csv
import math
import json
import logging
from functools import lru_cache
from flask import current_app
from ..models.pergola_model import PriceData, db

# Настройка логирования
logger = logging.getLogger(__name__)

class CalculationStrategy:
    """Базовый класс для стратегии расчета."""
    
    def calculate(self, pergola_type, width, length, modules, lamella_size, options):
        """
        Базовый метод для расчета стоимости перголы.
        
        Args:
            pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
            width (float): Ширина перголы в метрах
            length (float): Длина (вынос) перголы в метрах
            modules (int): Количество модулей
            lamella_size (str): Размер ламели (200, 250, PIR)
            options (dict): Словарь с выбранными опциями
            
        Returns:
            dict: Результаты расчета
        """
        raise NotImplementedError("Subclasses must implement calculate()")


class StandardCalculationStrategy(CalculationStrategy):
    """Стандартная стратегия расчета для всех типов пергол."""
    
    def calculate(self, pergola_type, width, length, modules, lamella_size, options):
        """
        Реализация стандартного расчета стоимости перголы.
        
        Args:
            pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
            width (float): Ширина перголы в метрах
            length (float): Длина (вынос) перголы в метрах
            modules (int): Количество модулей
            lamella_size (str): Размер ламели (200, 250, PIR)
            options (dict): Словарь с выбранными опциями
            
        Returns:
            dict: Результаты расчета
        """
        # Получение базовой цены из прайс-листа
        base_price = get_base_price(pergola_type, lamella_size, width, length)
        
        # Проверка, нужны ли дополнительные колонны
        needs_extra_columns = needs_additional_columns(pergola_type, lamella_size, length)
        extra_columns_price = 0
        if needs_extra_columns:
            extra_columns_price = get_extra_columns_price(pergola_type)
        
        # Расчет усилителя лотка
        needs_insert, gutter_insert_price, gutters_count, total_gutter_length = \
            calculate_gutter_insert_price(length, modules)
        
        # Определение привода
        drive_name, drive_price, needs_tandem = get_drive_price(pergola_type, width, length, modules)
        
        # Определение пульта управления
        remote_name, remote_price = get_remote_control(1)  # Всегда минимум 1 устройство (привод)
        
        # Расчет дополнительных опций
        options_items = []
        options_total = 0
        
        # LED-подсветка
        if options.get('led_lighting', False):
            led_price_per_meter = 5500  # Цена за метр подсветки
            led_perimeter = calculate_lighting_perimeter(width, length, modules)
            led_total_price = led_price_per_meter * led_perimeter
            options_items.append({
                'name': 'Светодиодная подсветка',
                'quantity': f"{led_perimeter:.1f} м",
                'price': led_total_price
            })
            options_total += led_total_price
        
        # Датчики дождя и ветра
        if options.get('rain_sensor', False):
            rain_sensor_price = 18000
            options_items.append({
                'name': 'Датчик дождя',
                'quantity': 1,
                'price': rain_sensor_price
            })
            options_total += rain_sensor_price
            
        if options.get('wind_sensor', False):
            wind_sensor_price = 15000
            options_items.append({
                'name': 'Датчик ветра',
                'quantity': 1,
                'price': wind_sensor_price
            })
            options_total += wind_sensor_price
        
        # Расчет скидки, если она указана в опциях
        discount_percent = float(options.get('discount', 0))
        
        # Подготовка базовых элементов
        items = [
            {
                'name': f'Пергола {pergola_type}, ламели {lamella_size} мм',
                'quantity': f"{width:.1f}x{length:.1f} м ({modules} модуль/-я/-ей)",
                'price': base_price
            },
            {
                'name': f'Привод {drive_name}' + (' (тандем)' if needs_tandem else ''),
                'quantity': 1 + (1 if needs_tandem else 0),
                'price': drive_price
            },
            {
                'name': f'Пульт управления {remote_name}',
                'quantity': 1,
                'price': remote_price
            }
        ]
        
        # Добавление дополнительных колонн, если нужны
        if needs_extra_columns:
            items.append({
                'name': 'Дополнительные колонны',
                'quantity': 2,  # Всегда добавляется 2 колонны
                'price': extra_columns_price
            })
        
        # Добавление усилителя лотка, если нужен
        if needs_insert:
            items.append({
                'name': 'Усилитель лотка',
                'quantity': f"{total_gutter_length:.1f} м ({gutters_count} лотка)",
                'price': gutter_insert_price
            })
        
        # Добавление дополнительных опций
        items.extend(options_items)
        
        # Расчет итоговой стоимости
        total_price = base_price + drive_price + remote_price + extra_columns_price + \
                      gutter_insert_price + options_total
        
        # Применение скидки
        total_after_discount = total_price
        if discount_percent > 0:
            total_after_discount = total_price * (1 - discount_percent / 100)
        
        # Формирование результата
        result = {
            'items': items,
            'total_price': total_price,
            'discount': discount_percent,
            'total_price_after_discount': total_after_discount
        }
        
        # Добавляем информацию об акции, если она применена
        if options.get('promotion_applied', False):
            result['promotion_applied'] = True
            result['promotion_name'] = options.get('promotion_name', 'Акция')
        
        return result


class CalculationFactory:
    """Фабрика для создания стратегий расчета."""
    
    @staticmethod
    def get_strategy(pergola_type):
        """
        Возвращает подходящую стратегию расчета для типа перголы.
        
        Args:
            pergola_type (str): Тип перголы
            
        Returns:
            CalculationStrategy: Стратегия расчета
        """
        # В будущем здесь можно добавить разные стратегии для разных типов пергол
        return StandardCalculationStrategy()


def get_pergola_types():
    """
    Возвращает список доступных типов пергол.
    
    Returns:
        list: Список типов пергол
    """
    return [
        {'id': 'B500NEW', 'name': 'B500 NEW'},
        {'id': 'B700NEW', 'name': 'B700 NEW'},
        {'id': 'B600', 'name': 'B600'}
    ]


def get_lamella_sizes():
    """
    Возвращает список доступных размеров ламелей.
    
    Returns:
        list: Список размеров ламелей
    """
    return [
        {'id': '200', 'name': '200 мм'},
        {'id': '250', 'name': '250 мм'},
        {'id': 'PIR', 'name': 'PIR (теплоизоляционные)'}
    ]


@lru_cache(maxsize=128)
def load_price_data(pergola_type, lamella_size):
    """
    Загружает данные о ценах из базы данных или CSV файлов.
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        dict: Словарь с ценами для разных размеров перголы
    """
    # Проверяем в базе данных
    price_data = {}
    db_prices = PriceData.query.filter_by(
        pergola_type=pergola_type,
        lamella_size=lamella_size
    ).all()
    
    if db_prices:
        for price in db_prices:
            key = f"{price.width}x{price.length}"
            price_data[key] = {
                'price': price.price,
                'modules': price.modules
            }
        return price_data
    
    # Если в базе нет, загружаем из файла
    try:
        # Путь к файлу с ценами
        file_path = os.path.join('data', 'prices', f"{pergola_type}_{lamella_size}.csv")
        
        if not os.path.exists(file_path):
            logger.error(f"Price file not found: {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                width = float(row['width'])
                length = float(row['length'])
                price = float(row['price'])
                modules = int(row.get('modules', 1))
                
                key = f"{width}x{length}"
                price_data[key] = {
                    'price': price,
                    'modules': modules
                }
                
                # Сохраняем данные в базу для будущего использования
                db_price = PriceData(
                    pergola_type=pergola_type,
                    lamella_size=lamella_size,
                    width=width,
                    length=length,
                    price=price,
                    modules=modules
                )
                db.session.add(db_price)
            
            db.session.commit()
                
        return price_data
    
    except Exception as e:
        logger.error(f"Error loading price data: {str(e)}")
        return {}


def get_base_price(pergola_type, lamella_size, width, length):
    """
    Получает базовую стоимость перголы из прайс-листа.
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        width (float): Ширина перголы в метрах
        length (float): Вынос перголы в метрах
        
    Returns:
        float: Базовая стоимость перголы
    """
    # Загрузка данных о ценах
    price_data = load_price_data(pergola_type, lamella_size)
    
    # Поиск точного соответствия
    key = f"{width}x{length}"
    if key in price_data:
        return price_data[key]['price']
    
    # Если точного соответствия нет, ищем ближайший больший размер
    best_price = None
    for size, data in price_data.items():
        size_width, size_length = map(float, size.split('x'))
        
        if size_width >= width and size_length >= length:
            if best_price is None or data['price'] < best_price:
                best_price = data['price']
    
    if best_price is not None:
        return best_price
    
    # Если нет ни точного, ни ближайшего большего размера, вычисляем цену на основе площади
    area = width * length
    prices_per_sqm = []
    
    for size, data in price_data.items():
        size_width, size_length = map(float, size.split('x'))
        size_area = size_width * size_length
        price_per_sqm = data['price'] / size_area
        prices_per_sqm.append(price_per_sqm)
    
    if prices_per_sqm:
        avg_price_per_sqm = sum(prices_per_sqm) / len(prices_per_sqm)
        return avg_price_per_sqm * area
    
    # Если совсем нет данных, возвращаем базовую цену
    logger.warning(f"No price data found for {pergola_type} {lamella_size} {width}x{length}")
    return 150000  # Минимальная базовая цена


def needs_additional_columns(pergola_type, lamella_size, length):
    """
    Проверяет, нужны ли дополнительные колонны.
    
    Args:
        pergola_type (str): Тип перголы
        lamella_size (str): Размер ламели
        length (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужны дополнительные колонны
    """
    if pergola_type == 'B500NEW':
        if lamella_size == '200' and length > 6.0:
            return True
        if lamella_size == '250' and length > 7.0:
            return True
        if lamella_size == 'PIR' and length > 6.0:
            return True
    elif pergola_type == 'B700NEW':
        if lamella_size == '200' and length > 7.0:
            return True
        if lamella_size == '250' and length > 8.0:
            return True
        if lamella_size == 'PIR' and length > 7.0:
            return True
    elif pergola_type == 'B600':
        if lamella_size == '200' and length > 6.0:
            return True
        if lamella_size == '250' and length > 7.0:
            return True
        if lamella_size == 'PIR' and length > 6.0:
            return True
    
    return False


def get_extra_columns_price(pergola_type):
    """
    Возвращает стоимость дополнительных колонн.
    
    Args:
        pergola_type (str): Тип перголы
        
    Returns:
        float: Стоимость дополнительных колонн
    """
    if pergola_type == 'B500NEW':
        return 35000
    elif pergola_type == 'B700NEW':
        return 45000
    elif pergola_type == 'B600':
        return 40000
    
    return 35000  # По умолчанию


def calculate_gutter_insert_price(length, modules):
    """
    Рассчитывает стоимость усилителя лотка.
    
    Args:
        length (float): Вынос перголы в метрах
        modules (int): Количество модулей
    
    Returns:
        tuple: (нужен ли усилитель, стоимость усилителя, количество лотков, общая длина лотков)
    """
    # Проверка, нужен ли усилитель
    if length <= 4.0:
        return False, 0, 0, 0
    
    # Определение количества лотков
    gutters_count = modules + 1
    
    # Общая длина лотков
    total_gutter_length = length * gutters_count
    
    # Цена за метр усилителя
    price_per_meter = 3500
    
    # Общая стоимость
    total_price = price_per_meter * total_gutter_length
    
    return True, total_price, gutters_count, total_gutter_length


def get_drive_price(pergola_type, width, length, modules):
    """
    Определяет тип и стоимость привода для перголы.
    
    Args:
        pergola_type (str): Тип перголы
        width (float): Ширина перголы в метрах
        length (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        tuple: (название привода, цена привода, нужен ли танем-привод)
    """
    area = width * length
    
    if area <= 16:  # до 16 кв.м
        return "Somfy WT 40 Нм", 35000, False
    elif area <= 25:  # до 25 кв.м
        return "Somfy WT 60 Нм", 40000, False
    elif area <= 35:  # до 35 кв.м
        return "Somfy WT 120 Нм", 50000, False
    else:  # более 35 кв.м или 3+ модуля - тандем
        return "Somfy WT 120 Нм", 100000, True  # двойная цена за тандем


def get_remote_control(devices_count):
    """
    Определяет тип и стоимость пульта управления.
    
    Args:
        devices_count (int): Количество устройств для управления
        
    Returns:
        tuple: (название пульта, цена пульта)
    """
    if devices_count <= 1:
        return "Somfy Smoove Origin RTS", 8000
    elif devices_count <= 4:
        return "Somfy Situo 5 IO", 12000
    else:
        return "Somfy Nina Timer IO", 25000


def calculate_lighting_perimeter(width, length, modules=1):
    """
    Расчет периметра подсветки по правилам.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        float: Длина периметра для светодиодной ленты
    """
    if modules == 1:
        # Периметр одного модуля
        return 2 * (width + length)
    else:
        # Для нескольких модулей периметр каждого считается отдельно
        module_width = width / modules
        return modules * 2 * (module_width + length)


def adjust_length_for_lamella_size(length, lamella_size):
    """
    Корректирует размер выноса перголы до ближайшего целого числа ламелей.
    
    Args:
        length (float): Вынос перголы в метрах
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        float: Скорректированный размер выноса перголы
    """
    if lamella_size == 'PIR':
        lamella_size_mm = 250  # PIR ламели имеют размер 250 мм
    else:
        lamella_size_mm = int(lamella_size)
    
    # Пересчет длины в миллиметры
    length_mm = length * 1000
    
    # Расчет количества ламелей
    lamellas_count = math.ceil(length_mm / lamella_size_mm)
    
    # Пересчет обратно в метры с округлением до 1 знака
    adjusted_length = round(lamellas_count * lamella_size_mm / 1000, 1)
    
    return adjusted_length


def get_modules_from_price_data(width, length, pergola_type, lamella_size):
    """
    Определяет количество модулей на основе данных из прайс-листа.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        int: Количество модулей или None, если не удалось определить
    """
    price_data = load_price_data(pergola_type, lamella_size)
    
    # Поиск точного соответствия
    key = f"{width}x{length}"
    if key in price_data and 'modules' in price_data[key]:
        return price_data[key]['modules']
    
    # Если точного соответствия нет, ищем ближайший больший размер
    best_match = None
    for size, data in price_data.items():
        if 'modules' not in data:
            continue
            
        size_width, size_length = map(float, size.split('x'))
        
        if size_width >= width and size_length >= length:
            if best_match is None or size_width * size_length < best_match[0] * best_match[1]:
                best_match = (size_width, size_length, data['modules'])
    
    if best_match is not None:
        return best_match[2]
    
    return None


def get_modules_by_dimensions(width, length, pergola_type=None):
    """
    Определяет количество модулей в зависимости от размеров перголы и ее типа.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str, optional): Тип перголы
        
    Returns:
        int: Количество модулей
    """
    # Если указан тип перголы и размер ламелей, ищем в прайс-листе
    if pergola_type:
        for lamella_size in ['200', '250', 'PIR']:
            modules = get_modules_from_price_data(width, length, pergola_type, lamella_size)
            if modules is not None:
                return modules
    
    # Если не удалось найти в прайс-листе, используем логику по размерам
    if width <= 4.0:
        return 1
    elif width <= 7.0:
        return 2
    else:
        return 3


def calculate_pergola_price(pergola_type, width, length, modules, lamella_size, options):
    """
    Расчет стоимости перголы с использованием паттерна "Стратегия".
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        width (float): Ширина перголы в метрах
        length (float): Длина (вынос) перголы в метрах
        modules (int): Количество модулей
        lamella_size (str): Размер ламели (200, 250, PIR)
        options (dict): Словарь с выбранными опциями
        
    Returns:
        dict: Результаты расчета
    """
    strategy = CalculationFactory.get_strategy(pergola_type)
    return strategy.calculate(pergola_type, width, length, modules, lamella_size, options)