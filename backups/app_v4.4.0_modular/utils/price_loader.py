"""
Модуль для загрузки данных о ценах из CSV файлов.
Обеспечивает унифицированный доступ к данным о ценах пергол различных типов.
"""
import os
import pandas as pd
import logging

# Настраиваем логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs/price_loader.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

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