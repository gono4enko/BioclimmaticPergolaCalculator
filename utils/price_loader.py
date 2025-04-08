"""
Модуль для загрузки и обработки данных о ценах из CSV-файлов
"""
import os
import logging
import pandas as pd

# Получаем логгер
logger = logging.getLogger(__name__)

# Путь к директории с файлами цен
PRICE_TABLES_DIR = 'attached_assets'

# Импортируем соответствие типов пергол и файлов с ценами из config
from config.price_data import PERGOLA_PRICE_FILES

# Словарь для хранения загруженных таблиц цен
price_tables = {}

def load_price_data(file_path):
    """
    Загружает данные о ценах из CSV-файла
    
    Args:
        file_path (str): Путь к файлу с ценами
        
    Returns:
        dict: Словарь с ценами в формате {(ширина, длина): (цена, модули)}
    """
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return {}
        
        # Проверяем, не пустой ли файл
        if os.path.getsize(file_path) == 0:
            logger.warning(f"Пропускаем пустой файл: {file_path}")
            return {}
        
        # Обработка потенциальных проблем с кодировкой
        try:
            df = pd.read_csv(file_path, delimiter=';', decimal=',', encoding='utf-8')
        except UnicodeDecodeError:
            # Пробуем альтернативную кодировку
            df = pd.read_csv(file_path, delimiter=';', decimal=',', encoding='cp1251')
        
        # Проверка на пустоту DataFrame
        if df.empty:
            logger.warning(f"Пустой DataFrame в файле: {file_path}")
            return {}
        
        # Проверка на минимальное количество строк и столбцов
        if df.shape[0] < 2 or df.shape[1] < 2:
            logger.warning(f"Недостаточно данных в файле: {file_path}, shape: {df.shape}")
            return {}
        
        # Создаем словарь для быстрого доступа к ценам по размерам
        price_dict = {}
        
        # Проверяем формат данных
        # Если есть строка "Количество модулей", значит это новый формат
        if "Количество модулей" in str(df.iloc[0, 0]):
            # Новый формат данных
            # Первая строка - информация о модулях
            # Вторая строка - заголовки с размерами ширины
            # Первый столбец - значения вылета (длины)
            
            # Получаем информацию о модулях
            modules_info = df.iloc[0, 1:].values.astype(str)
            
            # Получаем размеры ширины
            width_values = df.iloc[1, 1:].values.astype(str)
            
            # Получаем значения вылета (длины)
            length_values = df.iloc[2:, 0].values.astype(str)
            
            # Получаем цены
            price_values = df.iloc[2:, 1:].values
            
            # Создаем словарь для соответствия ширины и количества модулей
            modules_count_dict = {}
            for i, module_info in enumerate(modules_info):
                if i < len(width_values):
                    width_float = float(width_values[i].replace(',', '.'))
                    # Извлекаем количество модулей из строки (например, "1 модуль" -> 1)
                    modules_count = int(module_info.split()[0])
                    modules_count_dict[width_float] = modules_count
            
            for i, length in enumerate(length_values):
                for j, width in enumerate(width_values):
                    try:
                        # Проверяем, что значения не пустые
                        if not length or not width:
                            continue
                            
                        # Конвертируем из строк в числа с плавающей точкой
                        length_float = float(length.replace(',', '.'))
                        width_float = float(width.replace(',', '.'))
                        
                        # Получаем количество модулей для данной ширины
                        modules_count = modules_count_dict.get(width_float, 1)
                        
                        # Проверяем, что у нас есть значение цены для этой позиции
                        if i < len(price_values) and j < len(price_values[i]):
                            price_value = float(price_values[i][j])
                            
                            # Сохраняем цену и количество модулей по ключу (ширина, длина)
                            # Если для данного размера уже есть цена, проверяем количество модулей
                            if (width_float, length_float) in price_dict:
                                existing_price, existing_modules = price_dict[(width_float, length_float)]
                                # Если новый вариант имеет меньше модулей, обновляем запись
                                if modules_count < existing_modules:
                                    price_dict[(width_float, length_float)] = (price_value, modules_count)
                                    logger.debug(f"Обновлена цена для {width_float}x{length_float}: {price_value}€, {modules_count} модулей (было {existing_modules} модулей)")
                            else:
                                price_dict[(width_float, length_float)] = (price_value, modules_count)
                                logger.debug(f"Загружена цена {price_value}€ для размеров {width_float}x{length_float}, {modules_count} модулей")
                    except (ValueError, IndexError, TypeError) as e:
                        logger.warning(f"Ошибка обработки цены в файле {file_path} (новый формат): {width}x{length}, {e}")
        
        else:
            # Старый формат данных
            # Первая строка - ширина, вторая - заголовки
            # Первый столбец - вылет, остальные столбцы - ширина
            
            # Получаем названия столбцов (ширина в метрах)
            width_values = df.iloc[0].values[1:].astype(str)
            
            # Получаем значения вылета (длины в метрах)
            length_values = df.iloc[1:, 0].values.astype(str)
            
            # Получаем цены
            price_values = df.iloc[1:, 1:].values
            
            for i, length in enumerate(length_values):
                for j, width in enumerate(width_values):
                    # Преобразование строки в число с плавающей точкой
                    try:
                        # Проверяем, что значения не пустые
                        if not length or not width:
                            continue
                            
                        # Конвертируем из строк в числа с плавающей точкой
                        length_float = float(length.replace(',', '.'))
                        width_float = float(width.replace(',', '.'))
                        
                        # Определяем предполагаемое количество модулей по ширине
                        modules_count = get_modules_count_from_size(width_float)
                        
                        # Проверяем, что у нас есть значение цены для этой позиции
                        if i < len(price_values) and j < len(price_values[i]):
                            price_value = float(price_values[i][j])
                            
                            # Сохраняем цену и количество модулей по ключу (ширина, длина)
                            price_dict[(width_float, length_float)] = (price_value, modules_count)
                            
                            # Дополнительно логируем загруженные размеры для отладки
                            logger.debug(f"Загружена цена {price_value}€ для размеров {width_float}x{length_float}, {modules_count} модулей")
                    except (ValueError, IndexError, TypeError) as e:
                        logger.warning(f"Ошибка обработки цены в файле {file_path} (старый формат): {width}x{length}, {e}")
        
        if price_dict:
            logger.info(f"Загружена таблица цен из файла {file_path}, {len(price_dict)} записей")
            return price_dict
        else:
            logger.warning(f"Не удалось загрузить данные из файла {file_path}")
            return {}
                
    except Exception as e:
        logger.error(f"Ошибка обработки файла {file_path}: {str(e)}")
        return {}

def load_price_tables():
    """
    Загружает все таблицы цен из CSV-файлов
    """
    global price_tables
    price_tables = {}
    
    try:
        # Сначала проверяем, существуют ли нужные файлы прайс-листов из PERGOLA_PRICE_FILES
        for pergola_type, file_name in PERGOLA_PRICE_FILES.items():
            file_path = os.path.join(PRICE_TABLES_DIR, file_name)
            if not os.path.exists(file_path):
                logger.warning(f"Файл прайс-листа не найден: {file_path} для типа {pergola_type}")
        
        # Загружаем все CSV-файлы из директории
        for file_name in os.listdir(PRICE_TABLES_DIR):
            if not file_name.endswith('.csv'):
                continue
                
            file_path = os.path.join(PRICE_TABLES_DIR, file_name)
            
            # Пропускаем пустые файлы
            if os.path.getsize(file_path) == 0:
                logger.warning(f"Пропускаем пустой файл: {file_path}")
                continue
            
            # Загружаем данные через функцию load_price_data
            price_dict = load_price_data(file_path)
            
            if price_dict:
                price_tables[file_name] = price_dict
                logger.info(f"Загружена таблица цен из файла {file_name}, {len(price_dict)} записей")
            else:
                logger.warning(f"Не удалось загрузить данные из файла {file_name}")
                
        return True
    except Exception as e:
        logger.error(f"Ошибка загрузки таблиц цен: {str(e)}", exc_info=True)
        return False

def get_modules_count_from_size(width_m):
    """
    Определяет предполагаемое количество модулей по ширине перголы
    на основе данных из CSV-файлов
    
    Args:
        width_m (float): Ширина перголы в метрах
        
    Returns:
        int: Количество модулей
    """
    # На основе анализа данных в CSV-файлах:
    # В первой строке каждого CSV файла указано количество модулей
    # Согласно загруженным прайсам:
    # B500-20: До 4.5м - 1 модуль, 6-10м - 2 модуля, 9-15м - 3 модуля
    # B500-25: До 4.5м - 1 модуль, 5-9м - 2 модуля, 7.5-13.5м - 3 модуля
    # B600_PIR: До 4.5м - 1 модуль, 6-9м - 2 модуля, 10.5-13.5м - 3 модуля
    # B700-20: До 4.5м - 1 модуль, 6-10м - 2 модуля, 9-15м - 3 модуля
    # B700-25: До 4.5м - 1 модуль, 5-9м - 2 модуля, 7.5-13.5м - 3 модуля
    
    if width_m <= 4.5:
        return 1
    elif width_m <= 9.0:
        return 2
    elif width_m <= 13.5:
        return 3
    else:
        return 3  # Максимальное количество модулей

def calculate_total_cost_with_automation(base_price, modules_count, pergola_type):
    """
    Рассчитывает общую стоимость перголы с учетом автоматики и освещения для разных конфигураций
    
    Args:
        base_price (float): Базовая цена перголы
        modules_count (int): Количество модулей
        pergola_type (str): Тип перголы
    
    Returns:
        float: Общая стоимость с учетом автоматики
    """
    total_cost = base_price
    
    # Стоимость автоматики в зависимости от типа перголы и количества модулей
    from config.price_data import BANSBACH_PRICES, SOMFY_PRICES
    if "B500" in pergola_type:
        # Стандартный привод Bansbach T1 (700€ за модуль)
        automation_cost = BANSBACH_PRICES["T1"] * modules_count
    elif "B700" in pergola_type:
        # Стандартный привод Somfy M1 (300€ за модуль)
        automation_cost = SOMFY_PRICES["M1"] * modules_count
    else:
        automation_cost = 0
    
    total_cost += automation_cost
    return total_cost

def get_base_price(pergola_type, lamella_type, width_m, length_m):
    """
    Получает базовую цену перголы на основе типа и размеров,
    выбирая оптимальную конфигурацию с учетом количества модулей
    
    Args:
        pergola_type (str): Тип перголы
        lamella_type (str): Тип ламелей
        width_m (float): Ширина в метрах
        length_m (float): Длина в метрах
        
    Returns:
        tuple: (Базовая цена перголы или None, если цена не найдена,
                Количество модулей для оптимальной конфигурации,
                Сообщение о выбранной конфигурации)
    """
    try:
        # Определяем файл с ценами в зависимости от типа перголы и ламелей
        price_file = None
        
        # Если указан конкретный тип ламелей, используем соответствующий прайс
        if lamella_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[lamella_type]
        # Иначе используем прайс для типа перголы
        elif pergola_type in PERGOLA_PRICE_FILES:
            price_file = PERGOLA_PRICE_FILES[pergola_type]
        
        if not price_file or price_file not in price_tables:
            logger.warning(f"Файл с ценами не найден для {pergola_type}/{lamella_type}")
            return None, 1, None
        
        # Получаем таблицу цен
        price_dict = price_tables[price_file]
        
        # Сначала проверяем, есть ли точное соответствие размеров в прайс-листе
        if (width_m, length_m) in price_dict:
            # Получаем цену и количество модулей
            if isinstance(price_dict[(width_m, length_m)], tuple):
                exact_price, exact_modules = price_dict[(width_m, length_m)]
            else:
                # Для обратной совместимости
                exact_price = price_dict[(width_m, length_m)]
                exact_modules = get_modules_count_from_size(width_m)
                
            # Рассчитываем общую стоимость с учетом автоматики
            exact_total_cost = calculate_total_cost_with_automation(exact_price, exact_modules, pergola_type)
            
            logger.info(f"Найдена точная цена {exact_price}€ для {pergola_type}/{lamella_type} ({width_m}x{length_m}, {exact_modules} модулей)")
            return exact_price, exact_modules, None
        
        # Если точного соответствия нет, находим все возможные конфигурации
        # и выбираем оптимальную с учетом стоимости модулей и автоматики
        
        # Находим все размеры, которые могли бы подойти (ближайшие большие)
        suitable_configs = []
        
        for size, price_data in price_dict.items():
            conf_width, conf_length = size
            
            # Проверяем, что размеры не меньше запрошенных
            if conf_width >= width_m and conf_length >= length_m:
                # Получаем цену и количество модулей
                if isinstance(price_data, tuple):
                    price_value, modules_count = price_data
                else:
                    # Для обратной совместимости
                    price_value = price_data
                    modules_count = get_modules_count_from_size(conf_width)
                
                # Рассчитываем общую стоимость с учетом автоматики
                total_cost = calculate_total_cost_with_automation(price_value, modules_count, pergola_type)
                
                suitable_configs.append({
                    'width': conf_width,
                    'length': conf_length, 
                    'price': price_value,
                    'modules': modules_count,
                    'total_cost': total_cost
                })
        
        if not suitable_configs:
            logger.warning(f"Подходящие конфигурации не найдены для {pergola_type}/{lamella_type} ({width_m}x{length_m})")
            return None, 1, None
        
        # Сортируем конфигурации сначала по ширине и длине, чтобы выбрать наиболее близкую
        # А потом при равных размерах - по общей стоимости
        suitable_configs.sort(key=lambda x: (abs(x['width'] - width_m) + abs(x['length'] - length_m), x['total_cost']))
        
        # Выбираем оптимальную (наиболее близкую по размерам) конфигурацию
        optimal_config = suitable_configs[0]
        
        # Выводим сравнение для отладки
        if len(suitable_configs) > 1:
            logger.info(f"Найдено {len(suitable_configs)} подходящих конфигураций для {pergola_type}/{lamella_type} ({width_m}x{length_m}):")
            for i, config in enumerate(suitable_configs[:3]):  # Выводим только первые 3 конфигурации
                logger.info(f"  {i+1}. {config['width']}x{config['length']} ({config['modules']} модулей): базовая цена {config['price']}€, с автоматикой {config['total_cost']}€")
        
        # Запишем информацию в лог, но не будем показывать пользователю
        log_message = (
            f"Выбрана оптимальная конфигурация перголы: {optimal_config['width']}x{optimal_config['length']} м "
            f"({optimal_config['modules']} {'модуль' if optimal_config['modules'] == 1 else 'модуля' if optimal_config['modules'] < 5 else 'модулей'}), "
            f"базовая стоимость: {optimal_config['price']} €"
        )
        
        # Для пользователя не формируем сообщение
        config_message = None
        
        logger.info(log_message)
        return optimal_config['price'], optimal_config['modules'], config_message
            
    except Exception as e:
        logger.error(f"Ошибка при получении цены: {str(e)}", exc_info=True)
        return None, 1, None

def find_nearest_dimensions(price_dict, width_m, length_m):
    """
    Находит ближайшие большие стандартные размеры в таблице цен
    
    Args:
        price_dict (dict): Словарь с ценами
        width_m (float): Заданная ширина в метрах
        length_m (float): Заданная длина в метрах
        
    Returns:
        tuple: (ближайшая большая ширина, ближайшая большая длина)
    """
    if not price_dict:
        return width_m, length_m
    
    # Получаем все доступные ширины и длины
    widths = sorted(set([dim[0] for dim in price_dict.keys()]))
    lengths = sorted(set([dim[1] for dim in price_dict.keys()]))
    
    # Выводим доступные значения для отладки
    logger.debug(f"Доступные значения ширины: {widths}")
    logger.debug(f"Доступные значения длины: {lengths}")
    
    # Особый случай для очень широких пергол (более 9 метров)
    # В этом случае в прайс-листе width - это ширина одного модуля, а не общая ширина перголы
    if width_m > 9.0 and max(widths) < 9.0:
        # Для широких пергол используем самое крупное значение ширины из прайса
        # (это соответствует максимальной ширине одного модуля)
        nearest_width = max(widths)
        logger.debug(f"Для широкой перголы {width_m}м выбрана ширина модуля {nearest_width}м")
    else:
        # Стандартный случай - ищем ближайшую большую ширину
        # Проверяем, есть ли точное совпадение по ширине
        if width_m in widths:
            nearest_width = width_m
            logger.debug(f"Найдено точное совпадение по ширине: {width_m}")
        else:
            # Находим ближайшую большую ширину
            filtered_widths = [w for w in widths if w >= width_m]
            if filtered_widths:
                nearest_width = min(filtered_widths)
                logger.debug(f"Выбрана ближайшая большая ширина: {nearest_width}")
            else:
                nearest_width = max(widths)
                logger.debug(f"Выбрана максимальная ширина: {nearest_width}")
    
    # Проверяем, есть ли точное совпадение по длине
    if length_m in lengths:
        nearest_length = length_m
        logger.debug(f"Найдено точное совпадение по длине: {length_m}")
    else:
        # Находим ближайшую большую длину
        filtered_lengths = [l for l in lengths if l >= length_m]
        if filtered_lengths:
            nearest_length = min(filtered_lengths)
            logger.debug(f"Выбрана ближайшая большая длина: {nearest_length}")
        else:
            nearest_length = max(lengths)
            logger.debug(f"Выбрана максимальная длина: {nearest_length}")
    
    # Логируем информацию о подборе размеров
    logger.info(f"Подбор размеров: запрос {width_m}x{length_m}, выбрано {nearest_width}x{nearest_length}")
    
    return nearest_width, nearest_length

# Загружаем таблицы цен при импорте модуля
load_price_tables()