#!/usr/bin/env python3
"""
Скрипт для отладки расчета стоимости перголы определенного размера
"""
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Импортируем необходимые модули
from utils.price_loader import get_base_price, price_tables, find_nearest_dimensions
from utils.calculator import calculate_pergola_cost
from config.price_data import PERGOLA_PRICE_FILES

# Размеры для тестирования
width_m = 13.0
length_m = 8.0
height_m = 3.0

# Создаем словарь с размерами
dimensions = {
    'width': width_m,
    'length': length_m,
    'height': height_m
}

# Проверяем для B500-20NEW
pergola_type = 'B500NEW'
lamella_type = 'B500-20NEW'

# Определяем файл с ценами
price_file = PERGOLA_PRICE_FILES.get(lamella_type)
print(f"Файл с ценами для {lamella_type}: {price_file}")

# Проверяем содержимое прайс-листа
if price_file in price_tables:
    price_dict = price_tables[price_file]
    
    # Выводим все доступные размеры и цены из прайса
    print(f"\nВсе размеры в прайсе {price_file}:")
    for size, price in sorted(price_dict.items()):
        print(f"{size[0]}x{size[1]} м: {price} €")
    
    # Пробуем найти ближайшие размеры
    nearest_width, nearest_length = find_nearest_dimensions(price_dict, width_m, length_m)
    print(f"\nБлижайшие размеры: {nearest_width}x{nearest_length} м")
    
    # Проверяем, есть ли такой размер в прайсе
    if (nearest_width, nearest_length) in price_dict:
        price = price_dict[(nearest_width, nearest_length)]
        print(f"Цена для размера {nearest_width}x{nearest_length} м: {price} €")
    else:
        print(f"Размер {nearest_width}x{nearest_length} м не найден в прайсе!")
    
    # Перебираем все возможные конфигурации для нашего размера
    print("\nПодходящие конфигурации:")
    suitable_configs = []
    for size, price in price_dict.items():
        conf_width, conf_length = size
        if conf_width >= width_m and conf_length >= length_m:
            print(f"{conf_width}x{conf_length} м: {price} €")
            suitable_configs.append((conf_width, conf_length, price))
    
    if not suitable_configs:
        print("Подходящие конфигурации не найдены!")
else:
    print(f"Файл с ценами {price_file} не загружен!")

# Теперь запускаем полный расчет через API
print("\nЗапуск полного расчета:")
options = {
    'pergola_type': pergola_type,
    'lamella_type': lamella_type,
    'lighting_type': 'none',
    'additional_options': []
}

results = calculate_pergola_cost(dimensions, options)
print("\nРезультаты расчета:")
for key, value in results.items():
    if key == 'detailed_costs':
        print(f"{key}:")
        for subkey, subvalue in value.items():
            print(f"  {subkey}: {subvalue}")
    else:
        print(f"{key}: {value}")

# Проверяем базовую цену непосредственно через функцию
base_price, modules, message = get_base_price(pergola_type, lamella_type, width_m, length_m)
print(f"\nРезультат get_base_price: {base_price} €, модулей: {modules}, сообщение: {message}")
