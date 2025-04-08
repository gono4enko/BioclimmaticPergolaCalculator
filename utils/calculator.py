"""
Модуль для расчета стоимости пергол на основе введенных данных
"""
import logging
import math
from utils.price_loader import get_base_price
from config.price_data import (
    get_option_price, LIGHTING_PRICES, ADDITIONAL_OPTIONS_PRICES,
    ADDITIONAL_COLUMNS_PRICES, ADDITIONAL_COLUMNS_THRESHOLDS,
    BANSBACH_PRICES, BANSBACH_TANDEM_CONDITIONS,
    SOMFY_PRICES, SOMFY_TANDEM_CONDITIONS,
    GUTTER_INSERT_THRESHOLD, GUTTER_INSERT_PRICE_PER_METER, GUTTER_COUNT_BY_MODULES
)
from utils.validation import validate_pergola_config
from config.pergola_types import LAMELLA_TYPES, LIGHTING_TYPES

# Получаем логгер
logger = logging.getLogger(__name__)

def calculate_lamella_count(length_m, lamella_type):
    """
    Расчет количества ламелей на основе длины и типа ламели
    
    Args:
        length_m (float): Длина перголы в метрах
        lamella_type (str): Тип ламели (ключ из LAMELLA_TYPES)
        
    Returns:
        int: Количество ламелей
    """
    # Для B600 не используются ламели
    if lamella_type == "B600":
        return 0
    
    # Получаем ширину ламели в мм и конвертируем в метры
    lamella_width_mm = LAMELLA_TYPES.get(lamella_type, {}).get("width", 0)
    
    if lamella_width_mm <= 0:
        return 0
    
    # Конвертируем ширину ламели в метры
    lamella_width_m = lamella_width_mm / 1000
    
    # Рассчитываем количество ламелей
    count = length_m / lamella_width_m
    
    # Округляем до ближайшего целого числа в большую сторону
    return math.ceil(count)

def calculate_additional_columns(pergola_type, lamella_type, length_m, width_m):
    """
    Определяет, требуются ли дополнительные колонны для перголы и рассчитывает их стоимость
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600PIR)
        lamella_type (str): Тип ламели
        length_m (float): Длина (вынос) перголы в метрах
        width_m (float): Ширина перголы в метрах
        
    Returns:
        tuple: (требуются ли дополнительные колонны (bool), стоимость дополнительных колонн (float), количество модулей)
    """
    # Определяем ключ для проверки порога длины
    if pergola_type == "B600NEW" or pergola_type == "B600":
        threshold_key = "B600PIR"
    else:
        # Определяем размер ламели (200 или 250 мм)
        lamella_size = "200" if "200" in lamella_type else "250"
        threshold_key = f"{pergola_type.replace('NEW', '')}-{lamella_size}"
    
    # Получаем пороговое значение для данного типа перголы и ламели
    threshold = ADDITIONAL_COLUMNS_THRESHOLDS.get(threshold_key, 0)
    
    # Если пороговое значение не указано, дополнительные колонны не требуются
    if threshold == 0:
        return False, 0, 0
    
    # Проверяем, превышает ли длина пороговое значение
    if length_m <= threshold:
        return False, 0, 0
    
    # Определяем количество модулей на основе ширины перголы
    # Модуль - это секция перголы определенной ширины
    # Используем функцию из price_loader для консистентности
    from utils.price_loader import get_modules_count_from_size
    # Используем логику из ценообразования для определения фактического количества модулей
    modules = get_modules_count_from_size(width_m)
    
    # Корректировка для ширины 8.0м: всегда должно быть 2 модуля
    if width_m == 8.0:
        modules = 2
        logger.info(f"Коррекция количества модулей: для ширины {width_m} м установлено 2 модуля")
    
    # Рассчитываем стоимость дополнительных колонн
    columns_cost = ADDITIONAL_COLUMNS_PRICES.get(modules, 0)
    
    return True, columns_cost, modules

def determine_bansbach_drive_type(pergola_type, width_m, length_m, modules_count):
    """
    Определяет тип привода Bansbach для перголы B500NEW в зависимости от ее размеров
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600PIR)
        width_m (float): Ширина перголы в метрах
        length_m (float): Длина (вынос) перголы в метрах
        modules_count (int): Количество модулей перголы
        
    Returns:
        tuple: (тип привода ('T1' или 'Tandem'), стоимость привода, сообщение)
    """
    # Проверяем, подходит ли размер перголы для использования Tandem привода
    # По умолчанию всегда используется привод T1
    drive_type = "T1"
    drive_cost_per_module = BANSBACH_PRICES["T1"]
    
    # Если перголa B500, проверяем условия для использования Tandem
    if "B500" in pergola_type and 1 <= modules_count <= 4:
        # Получаем список условий для данного количества модулей
        conditions = BANSBACH_TANDEM_CONDITIONS.get(modules_count, [])
        
        # Проверяем условия для всех модулей одинаково:
        # Если ШИРИНА > порогового значения И ДЛИНА > порогового значения,
        # то нужен более мощный привод Tandem
        for width_threshold, length_threshold in conditions:
            if width_m > width_threshold and length_m > length_threshold:
                drive_type = "Tandem"
                drive_cost_per_module = BANSBACH_PRICES["Tandem"]
                # Добавляем лог для отладки
                logger.info(f"Выбран привод Tandem для перголы размером {width_m}x{length_m} м, "
                           f"т.к. ширина > {width_threshold} и длина > {length_threshold}")
                break
                
        # Если TANDEM не выбран, записываем в лог причину
        if drive_type == "T1":
            logger.info(f"Выбран стандартный привод T1 для перголы размером {width_m}x{length_m} м, "
                      f"т.к. не выполнены условия для Tandem при {modules_count} модулях")
    
    # Общая стоимость приводов зависит от количества модулей
    drive_cost = drive_cost_per_module * modules_count
    
    # Формируем сообщение в зависимости от типа привода и количества модулей
    if drive_type == "Tandem":
        message = (
            f"Для автоматизации перголы размером {width_m:.2f}x{length_m:.2f} м "
            f"({modules_count} {'модуль' if modules_count == 1 else 'модуля' if modules_count < 5 else 'модулей'}) "
            f"требуется {modules_count} {'привод' if modules_count == 1 else 'привода' if modules_count < 5 else 'приводов'} "
            f"Bansbach Tandem"
        )
    else:
        message = (
            f"Для автоматизации перголы требуется {modules_count} "
            f"{'стандартный привод' if modules_count == 1 else 'стандартных привода' if modules_count < 5 else 'стандартных приводов'} "
            f"Bansbach T1"
        )
    
    return drive_type, drive_cost, message

def calculate_gutter_insert_cost(length_m, modules_count):
    """
    Рассчитывает стоимость вставки для усиления лотка для пергол с выносом более 6.5 метров
    
    Args:
        length_m (float): Длина (вынос) перголы в метрах (скорректированная с учетом ламелей)
        modules_count (int): Количество модулей перголы
        
    Returns:
        tuple: (нужна ли вставка (bool), стоимость вставки (float), сообщение)
    """
    # Проверяем, нужна ли вставка для усиления лотка
    if length_m <= GUTTER_INSERT_THRESHOLD:
        return False, 0, None
    
    # Определяем количество лотков в зависимости от количества модулей
    gutter_count = GUTTER_COUNT_BY_MODULES.get(modules_count, 2)
    
    # Вычисляем общую длину лотков
    total_gutter_length = length_m * gutter_count
    
    # Вычисляем стоимость вставки
    insert_cost = total_gutter_length * GUTTER_INSERT_PRICE_PER_METER
    
    # Округляем стоимость до 2 знаков после запятой
    insert_cost = round(insert_cost, 2)
    
    # Формируем сообщение
    message = (
        f"Для перголы с выносом {length_m:.2f} м требуется вставка для усиления лотка. "
        f"Общая длина лотков: {total_gutter_length:.2f} м "
        f"({gutter_count} лотка × {length_m:.2f} м). "
        f"Стоимость усиления: {insert_cost} €"
    )
    
    return True, insert_cost, message

def determine_somfy_drive_type(pergola_type, width_m, length_m, modules_count):
    """
    Определяет тип привода Somfy для перголы B700NEW в зависимости от ее размеров
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600PIR)
        width_m (float): Ширина перголы в метрах
        length_m (float): Длина (вынос) перголы в метрах
        modules_count (int): Количество модулей перголы
        
    Returns:
        tuple: (тип привода ('M1' или 'M2_TANDEM'), стоимость привода, сообщение)
    """
    # По умолчанию всегда используется стандартный привод Somfy M1
    drive_type = "M1"
    drive_cost_per_module = SOMFY_PRICES["M1"]
    
    # Для перголы B700NEW используем привод Somfy
    if "B700" in pergola_type and 1 <= modules_count <= 4:
        # Получаем список условий для данного количества модулей
        conditions = SOMFY_TANDEM_CONDITIONS.get(modules_count, [])
        
        # Для 1 модуля используем противоположные правила (ширина <= threshold)
        # Для остальных модулей используем стандартные правила (ширина > threshold)
        for width_threshold, length_threshold in conditions:
            if modules_count == 1:
                # Для 1 модуля: если ШИРИНА <= порогового значения И ДЛИНА > порогового значения 
                if width_m <= width_threshold and length_m > length_threshold:
                    drive_type = "M2_TANDEM"
                    drive_cost_per_module = SOMFY_PRICES["M2_TANDEM"]
                    # Добавляем лог для отладки
                    logger.info(f"Выбран привод Somfy M2 TANDEM для перголы размером {width_m}x{length_m} м, "
                               f"т.к. ширина <= {width_threshold} и длина > {length_threshold}")
                    break
            else:
                # Для 2+ модулей: если ШИРИНА > порогового значения И ДЛИНА > порогового значения 
                if width_m > width_threshold and length_m > length_threshold:
                    drive_type = "M2_TANDEM"
                    drive_cost_per_module = SOMFY_PRICES["M2_TANDEM"]
                    # Добавляем лог для отладки
                    logger.info(f"Выбран привод Somfy M2 TANDEM для перголы размером {width_m}x{length_m} м, "
                               f"т.к. ширина > {width_threshold} и длина > {length_threshold}")
                    break
                
        # Если TANDEM не выбран, записываем в лог причину
        if drive_type == "M1":
            logger.info(f"Выбран стандартный привод Somfy M1 для перголы размером {width_m}x{length_m} м, "
                      f"т.к. не выполнены условия для M2 TANDEM при {modules_count} модулях")
    
    # Общая стоимость приводов зависит от количества модулей
    drive_cost = drive_cost_per_module * modules_count
    
    # Формируем сообщение в зависимости от типа привода и количества модулей
    if drive_type == "M2_TANDEM":
        message = (
            f"Для автоматизации перголы размером {width_m:.2f}x{length_m:.2f} м "
            f"({modules_count} {'модуль' if modules_count == 1 else 'модуля' if modules_count < 5 else 'модулей'}) "
            f"требуется {modules_count} {'привод' if modules_count == 1 else 'привода' if modules_count < 5 else 'приводов'} "
            f"Somfy M2 TANDEM"
        )
    else:
        message = (
            f"Для автоматизации перголы требуется {modules_count} "
            f"{'стандартный привод' if modules_count == 1 else 'стандартных привода' if modules_count < 5 else 'стандартных приводов'} "
            f"Somfy M1"
        )
    
    return drive_type, drive_cost, message

def adjust_length_to_lamella_count(length_m, lamella_type):
    """
    Корректирует длину (вынос) перголы для соответствия целому числу ламелей
    
    Args:
        length_m (float): Оригинальная длина перголы в метрах
        lamella_type (str): Тип ламели
        
    Returns:
        tuple: (скорректированная длина в метрах, количество ламелей, сообщение о корректировке)
    """
    # Для перголы B600 корректировка не нужна
    if lamella_type == "B600":
        return length_m, 0, None
    
    # Получаем ширину ламели в мм и конвертируем в метры
    lamella_width_mm = LAMELLA_TYPES.get(lamella_type, {}).get("width", 0)
    
    if lamella_width_mm <= 0:
        return length_m, 0, None
    
    # Конвертируем ширину ламели в метры
    lamella_width_m = lamella_width_mm / 1000
    
    # Рассчитываем количество ламелей
    lamella_count_exact = length_m / lamella_width_m
    lamella_count = math.ceil(lamella_count_exact)
    
    # Если количество ламелей не целое число, корректируем длину
    if lamella_count != lamella_count_exact:
        adjusted_length_m = lamella_count * lamella_width_m
        
        # Округляем до 3 знаков после запятой
        adjusted_length_m = round(adjusted_length_m, 3)
        
        correction_message = (
            f"Длина перголы была скорректирована с {length_m:.2f} м до {adjusted_length_m:.2f} м "
            f"для соответствия целому числу ламелей ({lamella_count} шт.)"
        )
        
        return adjusted_length_m, lamella_count, correction_message
    
    # Если корректировка не требуется
    return length_m, lamella_count, None

def calculate_pergola_cost(dimensions, options):
    """
    Рассчитывает стоимость перголы на основе заданных размеров и опций.
    
    Args:
        dimensions (dict): Словарь с размерами перголы (ширина, длина, высота) в метрах
        options (dict): Словарь с выбранными опциями
        
    Returns:
        dict: Словарь с результатами расчетов
    """
    try:
        # Извлекаем данные из входных параметров (уже в метрах)
        width_m = dimensions.get('width', 0)
        length_m = dimensions.get('length', 0)
        height_m = dimensions.get('height', 0)
        
        # Округляем до 3 знаков после запятой для точности расчетов
        width_m = round(width_m, 3)
        length_m = round(length_m, 3)
        height_m = round(height_m, 3)
        
        # Конвертируем в миллиметры для некоторых расчетов
        width_mm = width_m * 1000
        length_mm = length_m * 1000
        height_mm = height_m * 1000
        
        pergola_type = options.get('pergola_type', '')
        lamella_type = options.get('lamella_type', '')
        lighting_type = options.get('lighting_type', 'none')
        additional_options = options.get('additional_options', [])
        
        # Валидация конфигурации перголы
        validation_error = validate_pergola_config(pergola_type, lamella_type, width_m, length_m)
        if validation_error:
            logger.error(f"Ошибка валидации: {validation_error}")
            return {
                'error': validation_error,
                'total_cost': 0,
                'detailed_costs': {}
            }
        
        # Применяем корректировку длины (выноса) перголы в соответствии с размером ламелей
        # для пергол B500NEW и B700NEW
        correction_message = None
        if pergola_type in ["B500NEW", "B700NEW"]:
            length_m, lamella_count, correction_message = adjust_length_to_lamella_count(length_m, lamella_type)
            if correction_message:
                logger.info(correction_message)
                # Обновляем длину в мм после корректировки
                length_mm = length_m * 1000
        else:
            # Если коррекция не применяется, просто рассчитываем количество ламелей
            lamella_count = calculate_lamella_count(length_m, lamella_type)
        
        # Получаем базовую цену перголы и количество модулей для оптимальной конфигурации
        # Сохраняем исходные размеры для проверки корректировки размеров из прайс-листа
        original_width_m, original_length_m = width_m, length_m
        
        # Получаем базовую цену, количество модулей и сообщение от оптимизированной функции выбора цены
        from utils.price_loader import get_base_price
        base_price, optimal_modules_count, config_message = get_base_price(pergola_type, lamella_type, width_m, length_m)
        
        # Добавляем информацию о выбранной конфигурации, если она есть
        if config_message:
            if correction_message:
                correction_message = f"{correction_message}. {config_message}"
            else:
                correction_message = config_message
        
        if base_price is None:
            logger.error(f"Не удалось найти базовую цену для {pergola_type}/{lamella_type} ({width_m}x{length_m})")
            return {
                'error': f"Не удалось найти базовую цену для выбранной конфигурации перголы",
                'total_cost': 0,
                'detailed_costs': {}
            }
        
        # Рассчитываем детальные расходы
        detailed_costs = {
            'base_price': base_price,
            'lighting': 0,
            'additional_columns': 0,
            'gutter_insert': 0,
            'additional_options': {}
        }
        
        # Определяем количество модулей на основе фактической ширины перголы
        # Это важно для правильного выбора пультов ДУ и других компонентов
        from utils.price_loader import get_modules_count_from_size
        modules_count = get_modules_count_from_size(width_m)
        
        # Корректировка для ширины 8.0м: всегда должно быть 2 модуля
        if width_m == 8.0:
            modules_count = 2
            logger.info(f"Коррекция количества модулей в основном расчете: для ширины {width_m} м установлено 2 модуля")
        
        # Не переопределяем количество модулей из оптимальной конфигурации
        # optimal_modules_count используется только для определения базовой цены
        
        # Проверяем необходимость добавления дополнительных колонн
        need_additional_columns, columns_cost, calculated_modules_count = calculate_additional_columns(
            pergola_type, lamella_type, length_m, width_m
        )
        
        # Если нужны дополнительные колонны, добавляем их стоимость
        if need_additional_columns:
            detailed_costs['additional_columns'] = columns_cost
            
            # Используем количество модулей из рассчитанной конфигурации, если оно больше
            if calculated_modules_count > modules_count:
                modules_count = calculated_modules_count
            
            # Добавляем информацию о дополнительных колоннах в сообщение
            columns_message = (
                f"Для перголы с выносом {length_m:.2f} м необходимы дополнительные колонны "
                f"({modules_count} {'модуль' if modules_count == 1 else 'модуля' if modules_count < 5 else 'модулей'})"
            )
            
            if correction_message:
                correction_message = f"{correction_message}. {columns_message}"
            else:
                correction_message = columns_message
                
            logger.info(columns_message)
                
        # Проверяем необходимость добавления вставки для усиления лотка
        need_gutter_insert, insert_cost, insert_message = calculate_gutter_insert_cost(
            length_m, modules_count
        )
        
        # Если нужна вставка для усиления лотка, добавляем её стоимость
        if need_gutter_insert:
            detailed_costs['gutter_insert'] = insert_cost
            
            # Добавляем сообщение о вставке к общему сообщению о корректировке
            if correction_message:
                correction_message = f"{correction_message}. {insert_message}"
            else:
                correction_message = insert_message
                
            logger.info(insert_message)
        
        # Добавляем стоимость освещения
        if lighting_type != 'none' and lighting_type in LIGHTING_PRICES:
            lighting_price = LIGHTING_PRICES[lighting_type]
            
            # Рассчитываем стоимость освещения в зависимости от размеров перголы и количества модулей
            # Используем скорректированную длину!
            if callable(lighting_price):
                # Преобразуем мм в метры для расчета освещения
                width_m = width_mm / 1000
                length_m = length_mm / 1000
                
                # Используем актуальное количество модулей для расчета освещения
                modules_for_lighting = modules_count
                
                # Вызываем функцию с параметрами в метрах и количеством модулей
                lighting_cost = lighting_price(width_m, length_m, modules_for_lighting)
                
                # Добавляем информацию о длине ленты и блоках управления в детализацию
                from config.price_data import calculate_lighting_perimeter
                
                led_length = calculate_lighting_perimeter(width_m, length_m, modules_for_lighting)
                controllers_count = modules_for_lighting
                
                # Рассчитываем стоимость компонентов в зависимости от типа освещения
                if lighting_type == "led" or lighting_type == "rgb":
                    led_meter_price = 20
                    led_cost = led_meter_price * led_length
                    controllers_cost = 300 * controllers_count
                elif lighting_type == "led_rgb":
                    led_meter_price = 40  # 20€ LED + 20€ RGB
                    led_cost = led_meter_price * led_length
                    controllers_cost = 300 * controllers_count
                else:
                    led_cost = 0
                    controllers_cost = 0
                
                # Сохраняем детализацию освещения
                detailed_costs['lighting'] = lighting_cost
                detailed_costs['lighting_details'] = {
                    'type': lighting_type,
                    'led_length': round(led_length, 2),
                    'led_cost': round(led_cost, 2),
                    'controllers_count': controllers_count,
                    'controllers_cost': round(controllers_cost, 2)
                }
                
                # Добавляем информацию об освещении в сообщение
                lighting_message = (
                    f"Установлено освещение типа '{LIGHTING_TYPES[lighting_type]['name']}'. "
                    f"Общая длина ленты: {led_length:.2f} м. "
                    f"Блоков управления Somfy RTS Dimmer: {controllers_count} шт."
                )
                
                # Добавляем сообщение об освещении к общему сообщению
                if correction_message:
                    correction_message = f"{correction_message}. {lighting_message}"
                else:
                    correction_message = lighting_message
                
                logger.info(lighting_message)
            else:
                detailed_costs['lighting'] = lighting_price
        
        # Для B500NEW и B700NEW автоматизация включена по умолчанию
        from config.pergola_types import PERGOLA_TYPES
        is_automation_included = PERGOLA_TYPES.get(pergola_type, {}).get("included_automation", False)
        
        # Если для перголы автоматизация включена по умолчанию, добавляем её в расчет
        if is_automation_included:
            drive_message = None
            
            if "B500" in pergola_type:
                # Для B500NEW используем привод Bansbach
                # Всегда используем актуальное количество модулей, независимо от дополнительных колонн
                drive_type, drive_cost, drive_message = determine_bansbach_drive_type(
                    pergola_type, width_m, length_m, modules_count
                )
                
                # Сохраняем стоимость и сообщение о выбранном приводе
                detailed_costs['additional_options']["automation"] = drive_cost
                detailed_costs['automation_type'] = drive_type
                detailed_costs['automation_message'] = drive_message
                detailed_costs['automation_manufacturer'] = "Bansbach"
                
                # Считаем количество устройств для пульта ДУ
                # Каждый модуль требует 1 привод
                # Если есть освещение, каждый модуль требует дополнительно 1 блок управления освещением
                devices_count = modules_count  # По 1 приводу на модуль
                if lighting_type != 'none':
                    devices_count += modules_count  # Добавляем по 1 устройству управления освещением на модуль
                
                # Выбираем подходящий пульт в зависимости от количества устройств и модулей
                if modules_count == 1:
                    # Для одномодульной перголы (с освещением или без) используем одноканальный пульт
                    detailed_costs['remote_control'] = "Simu 1K"
                    detailed_costs['remote_control_cost'] = 25
                    logger.info("Для одномодульной перголы выбран пульт Simu 1K (1-канальный)")
                elif devices_count <= 5:
                    detailed_costs['remote_control'] = "Simu 5K"
                    detailed_costs['remote_control_cost'] = 40
                    logger.info(f"Для управления {devices_count} устройствами выбран пульт Simu 5K (5-канальный)")
                else:
                    detailed_costs['remote_control'] = "Simu 15K"
                    detailed_costs['remote_control_cost'] = 90
                    logger.info(f"Для управления {devices_count} устройствами выбран пульт Simu 15K (15-канальный)")
                
            elif "B700" in pergola_type:
                # Для B700NEW используем привод Somfy
                # Всегда используем актуальное количество модулей для выбора привода
                drive_type, drive_cost, drive_message = determine_somfy_drive_type(
                    pergola_type, width_m, length_m, modules_count
                )
                
                # Сохраняем стоимость и сообщение о выбранном приводе
                detailed_costs['additional_options']["automation"] = drive_cost
                detailed_costs['automation_type'] = drive_type
                detailed_costs['automation_message'] = drive_message
                detailed_costs['automation_manufacturer'] = "Somfy"
                
                # Считаем количество устройств для пульта ДУ
                # Каждый модуль требует 1 привод
                # Если есть освещение, каждый модуль требует дополнительно 1 блок управления освещением
                devices_count = modules_count  # По 1 приводу на модуль
                if lighting_type != 'none':
                    devices_count += modules_count  # Добавляем по 1 устройству управления освещением на модуль
                
                # Выбираем подходящий пульт в зависимости от количества устройств и модулей
                if modules_count == 1:
                    # Для одномодульной перголы (с освещением или без) используем одноканальный пульт
                    detailed_costs['remote_control'] = "Simu 1K"
                    detailed_costs['remote_control_cost'] = 25
                    logger.info("Для одномодульной перголы выбран пульт Simu 1K (1-канальный)")
                elif devices_count <= 5:
                    detailed_costs['remote_control'] = "Simu 5K"
                    detailed_costs['remote_control_cost'] = 40
                    logger.info(f"Для управления {devices_count} устройствами выбран пульт Simu 5K (5-канальный)")
                else:
                    detailed_costs['remote_control'] = "Simu 15K"
                    detailed_costs['remote_control_cost'] = 90
                    logger.info(f"Для управления {devices_count} устройствами выбран пульт Simu 15K (15-канальный)")
            
            # Добавляем информацию о выбранном приводе в сообщение о корректировке
            if drive_message:
                if correction_message:
                    correction_message = f"{correction_message}. {drive_message}"
                else:
                    correction_message = drive_message
                
                logger.info(drive_message)
        
        # Добавляем стоимость дополнительных опций, выбранных пользователем
        for option in additional_options:
            if option == "automation" and not is_automation_included:
                # Определяем тип привода в зависимости от типа перголы и размеров
                if "B500" in pergola_type:
                    # Для B500NEW/B500 используем привод Bansbach
                    # Всегда используем актуальное количество модулей
                    drive_type, drive_cost, drive_message = determine_bansbach_drive_type(
                        pergola_type, width_m, length_m, modules_count
                    )
                    detailed_costs['automation_manufacturer'] = "Bansbach"
                elif "B700" in pergola_type:
                    # Для B700NEW/B700 используем привод Somfy
                    # Всегда используем актуальное количество модулей
                    drive_type, drive_cost, drive_message = determine_somfy_drive_type(
                        pergola_type, width_m, length_m, modules_count
                    )
                    detailed_costs['automation_manufacturer'] = "Somfy"
                else:
                    # Для других типов пергол используем привод Bansbach по умолчанию
                    # Всегда используем актуальное количество модулей
                    drive_type, drive_cost, drive_message = determine_bansbach_drive_type(
                        pergola_type, width_m, length_m, modules_count
                    )
                    detailed_costs['automation_manufacturer'] = "Bansbach"
                
                # Сохраняем стоимость и сообщение о выбранном приводе
                detailed_costs['additional_options'][option] = drive_cost
                detailed_costs['automation_type'] = drive_type
                detailed_costs['automation_message'] = drive_message
                
                # Добавляем информацию о выбранном приводе в сообщение о корректировке
                if correction_message:
                    correction_message = f"{correction_message}. {drive_message}"
                else:
                    correction_message = drive_message
                
                logger.info(drive_message)
            elif option in ADDITIONAL_OPTIONS_PRICES:
                option_price = ADDITIONAL_OPTIONS_PRICES[option]
                
                # Рассчитываем стоимость опции в зависимости от размеров перголы
                # Используем скорректированную длину!
                if callable(option_price):
                    option_cost = option_price(width_mm, length_mm)
                else:
                    option_cost = option_price
                    
                detailed_costs['additional_options'][option] = option_cost
        
        # Вычисляем общую стоимость
        total_cost = base_price
        total_cost += detailed_costs['lighting']
        total_cost += detailed_costs['additional_columns']
        total_cost += detailed_costs['gutter_insert']
        total_cost += sum(detailed_costs['additional_options'].values())
        
        # Формируем результат - используем исходные размеры пользователя, а не округленные
        result = {
            'total_cost': round(total_cost, 2),
            'detailed_costs': detailed_costs,
            'dimensions': {
                'width_mm': dimensions.get('width', 0) * 1000,  # Конвертируем м в мм из исходных размеров
                'width_m': round(dimensions.get('width', 0), 2),  # Используем исходную ширину
                'length_mm': dimensions.get('length', 0) * 1000,  # Конвертируем м в мм из исходных размеров
                'length_m': round(dimensions.get('length', 0), 2),  # Используем исходную длину
                'height_mm': dimensions.get('height', 0) * 1000,  # Конвертируем м в мм из исходных размеров
                'height_m': round(dimensions.get('height', 0), 2)  # Используем исходную высоту
            },
            'lamella_count': lamella_count,
            'correction_message': correction_message
        }
        
        logger.info(f"Расчет выполнен успешно: {result['total_cost']} евро")
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при расчете стоимости: {str(e)}", exc_info=True)
        return {
            'error': f"Произошла ошибка при расчете: {str(e)}",
            'total_cost': 0,
            'detailed_costs': {}
        }