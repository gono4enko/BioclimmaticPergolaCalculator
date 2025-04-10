"""
Модуль для расчета стоимости пергол различных типов.
Содержит функции для расчетов базовых цен и дополнительных опций.
"""
import os
import pandas as pd
import math
import logging
from datetime import datetime

# Настраиваем логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs/calculator.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Константы для расчетов
DEFAULT_EURO_RATE = 85  # курс евро по умолчанию
LAMELLA_SIZES = {'200': 200, '250': 250, 'PIR': 100}  # размеры ламелей в мм
MARGIN_PERCENTAGE = 10  # процент наценки

def calculate_pergola_cost(dimensions, options, euro_rate=DEFAULT_EURO_RATE):
    """
    Выполняет расчет стоимости перголы на основе ее размеров и выбранных опций.
    
    Args:
        dimensions (dict): Словарь с размерами перголы (ширина, вынос)
        options (dict): Словарь с выбранными опциями (тип перголы, тип ламелей, освещение, etc.)
        euro_rate (float): Курс евро для пересчета в рубли
        
    Returns:
        dict: Словарь с результатами расчета
    """
    try:
        logger.info(f"Начат расчет перголы с параметрами: {dimensions}, {options}")
        
        # Извлекаем основные параметры
        width_m = float(dimensions.get('width', 3.0))
        length_m = float(dimensions.get('length', 4.0))
        pergola_type = options.get('pergola_type', 'B500NEW')
        lamella_size = options.get('lamella_size', '200')
        
        # Определяем количество модулей
        modules_count = get_modules_by_dimensions(width_m, length_m, pergola_type)
        
        # Корректируем длину в зависимости от размера ламелей
        lamella_size_mm = LAMELLA_SIZES.get(lamella_size, 200)
        adjusted_length_m = adjust_length_for_lamella_size(length_m, lamella_size_mm)
        
        # Получаем базовую цену перголы
        base_price = get_base_price(pergola_type, lamella_size, width_m, adjusted_length_m)
        
        # Рассчитываем общую стоимость с учетом опций
        total_price = base_price
        options_prices = []
        
        # Добавляем цену привода
        drive_name, drive_price, needs_tandem = get_drive_price(pergola_type, width_m, length_m, modules_count)
        options_prices.append({
            'name': f"Привод {drive_name}" + (" (тандем)" if needs_tandem else ""),
            'price': drive_price,
            'quantity': 1,
            'total': drive_price
        })
        total_price += drive_price
        
        # Добавляем цену пульта управления
        devices_count = 1  # Начальное количество устройств (привод)
        
        # Добавляем светодиодное освещение если выбрано
        if options.get('led_lighting', False):
            lighting_perimeter = calculate_lighting_perimeter(width_m, length_m, modules_count)
            led_price_per_meter = 90  # евро за метр светодиодной ленты
            led_price = lighting_perimeter * led_price_per_meter
            options_prices.append({
                'name': f"Светодиодное освещение по периметру",
                'price': led_price_per_meter,
                'quantity': f"{lighting_perimeter:.1f} м",
                'total': led_price
            })
            total_price += led_price
            devices_count += 1  # Добавляем устройство для освещения
        
        # Добавляем цену пульта
        remote_name, remote_price = get_remote_control(devices_count)
        options_prices.append({
            'name': f"Пульт управления {remote_name}",
            'price': remote_price,
            'quantity': 1,
            'total': remote_price
        })
        total_price += remote_price
        
        # Добавляем усилители лотка если нужно
        if needs_gutter_insert(adjusted_length_m):
            needs_insert, insert_price, gutters_count, total_length = calculate_gutter_insert_price(adjusted_length_m, modules_count)
            if needs_insert:
                options_prices.append({
                    'name': f"Усилитель лотка",
                    'price': insert_price / total_length,
                    'quantity': f"{total_length:.1f} м ({gutters_count} шт.)",
                    'total': insert_price
                })
                total_price += insert_price
        
        # Добавляем опцию доставки если выбрана
        if options.get('delivery', False):
            delivery_price = total_price * MARGIN_PERCENTAGE / 100
            options_prices.append({
                'name': "Доставка",
                'price': delivery_price,
                'quantity': 1,
                'total': delivery_price
            })
            total_price += delivery_price
        
        # Добавляем опцию установки если выбрана
        if options.get('installation', False):
            installation_price = total_price * MARGIN_PERCENTAGE / 100
            options_prices.append({
                'name': "Монтаж",
                'price': installation_price,
                'quantity': 1,
                'total': installation_price
            })
            total_price += installation_price
        
        # Формируем результаты
        results = {
            'base_price': base_price,
            'total_price': total_price,
            'euro_rate': euro_rate,
            'total_price_rub': total_price * euro_rate,
            'modules_count': modules_count,
            'options_prices': options_prices,
            'adjusted_length': adjusted_length_m,
            'drive_info': {
                'name': drive_name,
                'price': drive_price,
                'tandem': needs_tandem
            }
        }
        
        logger.info(f"Расчет завершен успешно. Итоговая цена: {total_price} евро")
        return results
    
    except Exception as e:
        logger.error(f"Ошибка при расчете стоимости перголы: {str(e)}")
        return {
            'error': str(e),
            'base_price': 0,
            'total_price': 0,
            'euro_rate': euro_rate,
            'total_price_rub': 0
        }

def get_base_price(pergola_type, lamella_size, width_m, length_m):
    """
    Получает базовую стоимость перголы из прайс-листа, используя точное соответствие
    шириной и длиной (выносом) из таблицы прайса
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        
    Returns:
        float: Базовая стоимость перголы
    """
    try:
        # Формируем имя файла
        file_path = ""
        if pergola_type == "B600":
            file_path = f"attached_assets/Price_B600_PIR.csv"
        else:
            file_path = f"attached_assets/Price_{pergola_type.replace('NEW', '')}-{lamella_size}.csv"
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            logger.warning(f"Файл прайса не найден: {file_path}, используем резервную копию")
            file_path = f"attached_assets/Прайс_{pergola_type.replace('NEW', '')}-{lamella_size}.csv"
            if not os.path.exists(file_path):
                logger.error(f"Резервная копия прайса не найдена: {file_path}")
                raise FileNotFoundError(f"Файл с ценами не найден: {file_path}")
        
        # Загружаем таблицу цен
        logger.info(f"Загрузка прайс-листа из файла: {file_path}")
        price_data = load_price_data(pergola_type, lamella_size)
        
        # Ищем ближайшие значения по ширине и длине
        available_widths = sorted(list(price_data.keys()))
        available_lengths = sorted(list(price_data[available_widths[0]].keys()))
        
        logger.info(f"Поиск цены для {pergola_type} с ламелями {lamella_size}, размер {width_m}x{length_m}м")
        logger.info(f"Доступные ширины: {available_widths}")
        logger.info(f"Доступные длины: {available_lengths}")
        
        # Ищем точное соответствие или ближайшее большее значение
        width_match = find_nearest_size(width_m, available_widths)
        length_match = find_nearest_size(length_m, available_lengths)
        
        # Получаем цену из таблицы
        price = price_data[width_match][length_match]
        logger.info(f"Найдена цена для размера {width_match}x{length_match}м: {price} евро")
        
        return price
    
    except Exception as e:
        logger.error(f"Ошибка при получении базовой цены: {str(e)}")
        raise

def find_nearest_size(target_size, available_sizes):
    """
    Находит ближайший больший размер из доступных.
    Если точного соответствия нет, берет ближайший больший.
    
    Args:
        target_size (float): Целевой размер
        available_sizes (list): Список доступных размеров
        
    Returns:
        float: Ближайший размер из доступных
    """
    # Сначала проверяем точное соответствие
    if target_size in available_sizes:
        return target_size
    
    # Ищем ближайший больший размер
    greater_sizes = [size for size in available_sizes if size > target_size]
    if greater_sizes:
        return min(greater_sizes)
    
    # Если нет большего, возвращаем максимальный доступный
    return max(available_sizes)

def load_price_data(pergola_type, lamella_size):
    """
    Загружает данные о ценах из соответствующего CSV файла
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        dict: Словарь с ценами для разных размеров перголы
    """
    # Формируем имя файла
    file_path = ""
    if pergola_type == "B600":
        file_path = f"attached_assets/Price_B600_PIR.csv"
    else:
        file_path = f"attached_assets/Price_{pergola_type.replace('NEW', '')}-{lamella_size}.csv"
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        file_path = f"attached_assets/Прайс_{pergola_type.replace('NEW', '')}-{lamella_size}.csv"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл с ценами не найден: {file_path}")
    
    # Определяем разделитель
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if ';' in first_line:
            delimiter = ';'
            logger.info("Обнаружен разделитель: ';'")
        else:
            delimiter = ','
    
    # Загружаем CSV файл
    try:
        df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
        
        # Проверяем наличие информации о модулях в первой строке
        if 'модуль' in str(df.iloc[0, 0]).lower():
            logger.info("Обнаружена строка с информацией о модулях, пропускаем")
            # Пропускаем первую строку с информацией о модулях
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8', skiprows=1)
        
        # Извлекаем заголовок
        header = df.columns.tolist()
        logger.info(f"Заголовок: {header}")
        
        # Получаем значения длины из заголовка
        # Первый столбец - это названия ширин, остальные - длины
        length_values = [float(val) for val in header[1:] if str(val).replace('.', '', 1).isdigit()]
        logger.info(f"Значения длины из заголовка: {length_values}")
        
        # Создаем словарь цен с ключами по ширине и длине
        price_dict = {}
        for _, row in df.iterrows():
            try:
                # Проверяем, что значение ширины является числом
                width_str = str(row[0]).replace(',', '.')
                if width_str.replace('.', '', 1).isdigit():
                    width = float(width_str)
                    price_dict[width] = {}
                    
                    # Заполняем цены для каждой длины
                    for i, length in enumerate(length_values):
                        try:
                            # Получаем цену из ячейки, преобразуем в число
                            price_str = str(row[i+1]).replace(',', '.').replace(' ', '')
                            if price_str and price_str.replace('.', '', 1).isdigit():
                                price_dict[width][length] = float(price_str)
                        except Exception as e:
                            logger.error(f"Ошибка при обработке цены для ширины {width}м и длины {length}м: {str(e)}")
            except Exception as e:
                logger.error(f"Ошибка при обработке строки {row[0]}: {str(e)}")
        
        # Выводим первые несколько записей для проверки
        for width in list(price_dict.keys())[:3]:
            logger.info(f"Ширина {width} м: {price_dict[width]}")
        
        return price_dict
    
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из файла {file_path}: {str(e)}")
        raise

def get_modules_by_dimensions(width, length, pergola_type=None):
    """
    Определяет количество модулей в зависимости от размеров перголы и ее типа.
    Учитывает как ширину, так и вынос (длину) перголы.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str, optional): Тип перголы
        
    Returns:
        int: Количество модулей
    """
    # Для B700NEW с шириной более 5 метров требуется 2 модуля,
    # а при ширине более 7 метров - 3 модуля
    if pergola_type == "B700NEW":
        if width > 7:
            return 3
        elif width > 5:
            return 2
    
    # Для других типов пергол или B700NEW меньшей ширины
    if width > 7:
        return 3
    elif width > 4.5:
        return 2
    else:
        return 1

def adjust_length_for_lamella_size(length_m, lamella_size_mm):
    """
    Корректирует размер выноса перголы до ближайшего целого числа ламелей
    
    Args:
        length_m (float): Вынос перголы в метрах
        lamella_size_mm (int): Размер ламели в миллиметрах (200 или 250)
        
    Returns:
        float: Скорректированный размер выноса перголы
    """
    # Переводим метры в миллиметры
    length_mm = length_m * 1000
    
    # Вычисляем количество ламелей (округляем вверх)
    lamellas_count = math.ceil(length_mm / lamella_size_mm)
    
    # Вычисляем новый размер выноса в метрах
    adjusted_length_m = (lamellas_count * lamella_size_mm) / 1000
    
    # Округляем до ближайшего значения из прайса
    standard_lengths = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 7.5, 8.0, 9.0, 10.5, 12.0, 13.5]
    for std_length in sorted(standard_lengths):
        if adjusted_length_m <= std_length:
            return std_length
    
    # Если длина больше всех стандартных, возвращаем максимальную стандартную
    return max(standard_lengths)

def calculate_lighting_perimeter(width_m, length_m, modules=1):
    """
    Расчет периметра подсветки по правилам.
    Для 1 модуля - просто периметр.
    Для нескольких модулей - сумма периметров всех модулей.
    
    Args:
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        float: Длина периметра для светодиодной ленты
    """
    if modules == 1:
        # Для одного модуля - просто периметр
        return 2 * (width_m + length_m)
    else:
        # Для нескольких модулей - делим ширину на модули и считаем сумму периметров
        module_width = width_m / modules
        return modules * 2 * (module_width + length_m)

def needs_gutter_insert(length_m):
    """
    Проверяет, нужен ли усилитель лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужен усилитель лотка
    """
    # Для выноса более 5 метров нужен усилитель лотка
    return length_m > 5.0

def calculate_gutter_insert_price(length_m, modules):
    """
    Рассчитывает стоимость усилителя лотка по формуле:
    Стоимость = цена за метр * длина выноса * количество лотков
    
    В перголах с 1 модулем - 2 лотка
    В перголах с 2 модулями - 3 лотка
    В перголах с 3 модулями - 4 лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
    
    Returns:
        tuple: (нужен ли усилитель, стоимость усилителя, количество лотков, общая длина лотков)
    """
    # Проверяем необходимость усилителя
    needs_insert = length_m > 5.0
    
    if not needs_insert:
        return (False, 0, 0, 0)
    
    # Определяем количество лотков
    gutters_count = modules + 1
    
    # Цена за метр усилителя лотка
    price_per_meter = 55  # евро
    
    # Общая длина лотков
    total_length = gutters_count * length_m
    
    # Общая стоимость
    total_price = price_per_meter * total_length
    
    return (True, total_price, gutters_count, total_length)

def get_drive_price(pergola_type, width_m, length_m, modules):
    """
    Определяет тип и стоимость привода для перголы
    
    Args:
        pergola_type (str): Тип перголы
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        tuple: (название привода, цена привода, нужен ли танем-привод)
    """
    # Для перголы B700NEW выбираем линейный привод
    if pergola_type == "B700NEW":
        if width_m <= 4.5:
            return ("Linear", 990, False)
        elif width_m <= 6.5:
            return ("Linear", 990, True)  # Тандем привод
        else:
            # Для больших размеров используем более мощный привод
            controllers_count = math.ceil(width_m / 3.5)
            return (f"Linear-{controllers_count}x", 990 * controllers_count, True)
    
    # Для перголы B500NEW используем привод от Somfy
    if pergola_type == "B500NEW":
        if width_m <= 5:
            return ("Somfy", 880, False)
        else:
            return ("Somfy", 880, True)  # Тандем привод
    
    # Для перголы B600 используем стандартный привод
    return ("Standard", 850, width_m > 5)

def get_remote_control(devices_count):
    """
    Определяет тип и стоимость пульта управления
    
    Args:
        devices_count (int): Количество устройств для управления
        
    Returns:
        tuple: (название пульта, цена пульта)
    """
    if devices_count <= 1:
        return ("Single-Channel", 120)
    elif devices_count <= 5:
        return ("5-Channel", 155)
    else:
        return ("Multi-Channel", 190)