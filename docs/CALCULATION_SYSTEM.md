# Техническая документация системы расчета стоимости пергол

## Версия 3.1

Данный документ описывает алгоритмы и правила расчета стоимости пергол, примененные в калькуляторе.

## Основные принципы

Система расчета стоимости пергол основана на следующих принципах:

1. **Базовая цена** определяется из прайс-листов в зависимости от типа перголы, типа ламелей, ширины и выноса
2. **Количество модулей** определяется автоматически в зависимости от размеров перголы
3. **Тип привода** выбирается в зависимости от типа перголы, количества модулей и размеров
4. **Дополнительные опции** добавляются к базовой стоимости

## Алгоритмы расчета

### 1. Определение количества модулей

Количество модулей в перголе определяется в зависимости от ширины и выноса перголы:

```python
def get_modules_by_dimensions(width, length, pergola_type=None):
    # По-умолчанию 1 модуль
    modules = 1
    
    # Для пергол с шириной от 4.5 до 6 метров - обычно нужны 2 модуля
    if width > 4.5 and width <= 6.0:
        modules = 2
    
    # Для пергол с шириной более 6 метров - обычно нужны 3 модуля
    elif width > 6.0:
        modules = 3
    
    # Для B700NEW при выносе более 6 метров - минимум 2 модуля
    if pergola_type == "B700NEW" and length > 6.0 and modules < 2:
        modules = 2
    
    # Для B500NEW при выносе более 7 метров - минимум 2 модуля
    if pergola_type == "B500NEW" and length > 7.0 and modules < 2:
        modules = 2
    
    return modules
```

### 2. Расчет базовой стоимости

Базовая стоимость перголы определяется из прайс-листов, хранящихся в CSV файлах. При этом:

- Для модели B500NEW используются прайсы `Price_B500-20.csv` или `Price_B500-25.csv` в зависимости от размера ламелей
- Для модели B700NEW используются прайсы `Price_B700-20.csv` или `Price_B700-25.csv` в зависимости от размера ламелей 
- Для модели B600 используется прайс `Price_B600_PIR.csv`

Алгоритм определения базовой стоимости:

```python
def get_base_price(pergola_type, lamella_size, width_m, length_m):
    # Преобразование типа ламели в формат для имени файла
    lamella_size_str = "20" if lamella_size == "200" else "25" if lamella_size == "250" else "PIR"
    
    # Формирование имени файла прайс-листа
    if pergola_type == "B600":
        price_file = f"attached_assets/Price_B600_{lamella_size_str}.csv"
    else:
        pergola_type_base = pergola_type.replace("NEW", "")
        price_file = f"attached_assets/Price_{pergola_type_base}-{lamella_size_str}.csv"
    
    # Загрузка данных о ценах
    price_data = load_price_data(pergola_type, lamella_size)
    
    # Округление размеров до ближайших доступных значений
    available_widths = sorted(list(price_data.keys()))
    closest_width = min(available_widths, key=lambda x: abs(x - width_m))
    
    available_lengths = sorted(list(price_data[closest_width].keys()))
    closest_length = min(available_lengths, key=lambda x: abs(x - length_m))
    
    # Получение цены из таблицы
    price = price_data[closest_width][closest_length]
    
    return price
```

### 3. Определение типа привода

Тип привода определяется в зависимости от типа перголы, ширины, выноса и количества модулей:

```python
def get_drive_price(pergola_type, width_m, length_m, modules):
    if pergola_type == "B500NEW":
        # Для B500 используется привод Bansbach
        if length_m > 6.5 or width_m > 4.5 or modules > 1:
            # Для больших размеров или нескольких модулей - тандем-привод
            return "Привод Bansbach Tandem (двойной)", 2450, True
        else:
            # Для стандартных размеров - обычный привод
            return "Привод Bansbach (стандартный)", 1225, False
    
    elif pergola_type == "B700NEW":
        # Для B700 используется привод Somfy
        if length_m > 7.0 or width_m > 5.0 or modules > 1:
            # Для больших размеров или нескольких модулей - усиленный привод
            return "Привод Somfy WT 100 Nm", 1300, False
        else:
            # Для стандартных размеров - обычный привод
            return "Привод Somfy WT 50 Nm", 745, False
    
    else:
        # Для B600 привод не требуется
        return "", 0, False
```

### 4. Расчет периметра для освещения

Периметр для расчета длины светодиодной ленты определяется в зависимости от размеров и количества модулей:

```python
def calculate_lighting_perimeter(width_m, length_m, modules=1):
    # Для одного модуля - просто периметр
    if modules == 1:
        return 2 * (width_m + length_m)
    
    # Для нескольких модулей - модификация периметра
    elif modules == 2:
        # Две секции по ширине
        width_per_module = width_m / 2
        # Периметр двух модулей плюс линия разделения
        return 2 * (width_m + length_m) + length_m
    
    elif modules == 3:
        # Три секции по ширине
        width_per_module = width_m / 3
        # Периметр трех модулей плюс две линии разделения
        return 2 * (width_m + length_m) + 2 * length_m
    
    return 0
```

### 5. Определение количества контроллеров и блоков питания

Количество контроллеров и блоков питания определяется в зависимости от типа освещения и длины периметра:

```python
def calculate_lighting_controllers(lighting_perimeter, lighting_type):
    # Для LED освещения - 1 контроллер на 10 метров
    if "LED" in lighting_type and "RGB" not in lighting_type:
        controllers_count = max(1, math.ceil(lighting_perimeter / 10))
        return "Контроллер LED", 60, controllers_count
    
    # Для RGB освещения - 1 контроллер на 5 метров
    elif "RGB" in lighting_type:
        controllers_count = max(1, math.ceil(lighting_perimeter / 5))
        return "Контроллер RGB", 95, controllers_count
    
    return "", 0, 0

def calculate_power_supplies(lighting_perimeter, lighting_type):
    # Блоки питания для светодиодного освещения
    if "LED" in lighting_type or "RGB" in lighting_type:
        # 1 блок питания 60W на каждые 5 метров периметра
        power_supplies_count = max(1, math.ceil(lighting_perimeter / 5))
        return "Блок питания 60W", 40, power_supplies_count
    
    return "", 0, 0
```

### 6. Определение типа пульта управления

Тип пульта определяется в зависимости от количества устройств, требующих управления:

```python
def get_remote_control(devices_count):
    if devices_count == 0:
        return "", 0
    
    if devices_count == 1:
        return "Пульт ДУ одноканальный", 95
    elif devices_count == 2:
        return "Пульт ДУ двухканальный", 110
    elif devices_count <= 5:
        return "Пульт ДУ пятиканальный", 160
    else:
        return "Пульт ДУ многоканальный", 200
```

### 7. Расчет усилителя лотка

Необходимость и стоимость усилителя лотка определяется в зависимости от выноса перголы и количества модулей:

```python
def calculate_gutter_insert_price(length_m, modules):
    # Проверяем, нужен ли усилитель лотка
    needs_insert = length_m > 6.5
    
    if not needs_insert:
        return False, 0, 0, 0
    
    # Определяем количество лотков в зависимости от количества модулей
    if modules == 1:
        gutters_count = 2  # Два лотка для одного модуля
    elif modules == 2:
        gutters_count = 3  # Три лотка для двух модулей
    else:
        gutters_count = 4  # Четыре лотка для трех модулей
    
    # Определяем общую длину лотков
    total_gutters_length = gutters_count * length_m
    
    # Цена за метр усилителя лотка
    price_per_meter = 80
    
    # Итоговая стоимость
    total_price = price_per_meter * total_gutters_length
    
    return needs_insert, total_price, gutters_count, total_gutters_length
```

### 8. Расчет наценок за доставку и установку

Стоимость доставки и установки рассчитывается как процент от базовой стоимости перголы:

```python
# Расчет стоимости доставки (10% от базовой стоимости)
delivery_price = base_price * 0.1

# Если выбрана опция установки, добавляем 10% от стоимости с доставкой
if options.get("installation", False):
    installation_price = (base_price + delivery_price) * 0.1
else:
    installation_price = 0
```

## Итоговый расчет

Итоговая стоимость перголы рассчитывается как сумма всех компонентов:

```python
total_price = (
    base_price +                    # Базовая стоимость перголы
    drive_price +                   # Стоимость привода
    remote_control_price +          # Стоимость пульта ДУ
    lighting_price +                # Стоимость освещения
    controllers_price +             # Стоимость контроллеров
    power_supplies_price +          # Стоимость блоков питания
    gutter_insert_price +           # Стоимость усилителя лотка
    additional_columns_price +      # Стоимость дополнительных колонн
    delivery_price +                # Стоимость доставки
    installation_price              # Стоимость установки
)
```

## Конвертация цен

Все цены в прайс-листах указаны в евро. Для отображения цен в рублях используется фиксированный курс:

```python
# Курс евро к рублю
euro_rate = 110.0

# Конвертация в рубли
rub_price = price_in_euro * euro_rate
```

## Форматирование цен

Для удобства восприятия, цены форматируются с разделителями тысяч:

```python
def format_price(price):
    # Для больших сумм используем сокращения
    price_in_thousands = price / 1000
    if price >= 1000000:
        price_in_millions = price / 1000000
        return "{:.1f}M₽".format(price_in_millions)
    
    # Для сотен тысяч используем формат с K
    if price >= 100000:
        return "{:.0f}K₽".format(price_in_thousands)
    
    # Для десятков тысяч тоже используем формат с K, но с 1 знаком после запятой
    if price >= 10000:
        return "{:.1f}K₽".format(price_in_thousands)
    
    # Для маленьких чисел используем обычный формат с разделителями
    return "{:,.0f}₽".format(price).replace(",", " ")
```

## Внутренняя структура данных результатов

Результаты расчета хранятся в структуре данных следующего формата:

```python
results = {
    "dimensions": {
        "width": width_m,
        "length": length_m
    },
    "options": {
        "pergola_type": pergola_type,
        "lamella_type": lamella_type,
        "lighting_type": lighting_type,
        "installation": installation_option
    },
    "base_price": base_price,
    "total_price": total_price,
    "modules": modules,
    "items": [
        {"name": "Пергола...", "count": 1, "price": base_price},
        {"name": "Привод...", "count": 1, "price": drive_price},
        # Список всех компонентов с ценами
    ],
    "specification": [
        {"name": "Пергола...", "count": 1},
        {"name": "Привод...", "count": 1},
        # Список всех компонентов без цен
    ],
    "debug": {
        "lamellas_count": lamellas_count,
        "lighting_perimeter": lighting_perimeter,
        # Дополнительная отладочная информация
    }
}
```

## Логирование расчетов

Система ведет подробное логирование всех этапов расчета для отладки и диагностики:

```python
def log_calculation_steps(dimensions, options, results):
    """Логирование этапов расчета для диагностики"""
    log_file = "logs/calculation_log.txt"
    
    with open(log_file, "a") as f:
        f.write(f"\n--- Расчет от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Размеры: {dimensions}\n")
        f.write(f"Опции: {options}\n")
        f.write(f"Тип перголы: {options['pergola_type']}\n")
        f.write(f"Тип ламелей: {options['lamella_type']}\n")
        f.write(f"Базовая цена: {results['base_price']} евро\n")
        f.write(f"Итоговая цена: {results['total_price']} евро ({results['total_price'] * 110} рублей)\n")
        f.write("Компоненты:\n")
        
        for item in results["items"]:
            f.write(f"  - {item['name']}: {item['count']} шт, {item['price']} евро\n")
        
        f.write(f"Количество модулей: {results['modules']}\n")
        
        if "debug" in results:
            f.write("Отладочная информация:\n")
            for key, value in results["debug"].items():
                f.write(f"  - {key}: {value}\n")
        
        f.write("---------------\n")
```

## Ограничения системы

Текущая версия системы расчета имеет следующие ограничения:

1. Не учитывается стоимость изменения цвета RAL
2. Не поддерживается расчет стоимости остекления
3. Используется фиксированный курс евро
4. Не поддерживается расчет стоимости дополнительных аксессуаров (обогреватели, вентиляторы и т.д.)
5. Не учитываются скидки и специальные предложения