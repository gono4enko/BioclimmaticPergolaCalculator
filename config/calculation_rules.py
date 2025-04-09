"""
Модуль с правилами расчета стоимости пергол

Этот файл содержит все правила и цены для расчета стоимости пергол.
Используется как централизованное хранилище данных для расчетов.
"""

# Правила определения количества модулей для разных типов пергол
MODULE_RULES = {
    "B500NEW": {
        "single_module_max_width": 4.5,  # макс. ширина для 1 модуля
        "double_module_max_width": 9.0,  # макс. ширина для 2 модулей
        "triple_module_max_width": 13.5,  # макс. ширина для 3 модулей
    },
    "B700NEW": {
        "single_module_max_width": 4.5,
        "double_module_max_width": 9.0,
        "triple_module_max_width": 13.5,
    },
    "B600": {
        "single_module_max_width": 4.5,
        "double_module_max_width": 9.0,
        "triple_module_max_width": 13.5,
    }
}

# Максимальные размеры для каждого типа пергол
MAX_DIMENSIONS = {
    "B500NEW": {"width": 15.0, "length": 8.0},
    "B700NEW": {"width": 15.0, "length": 7.25},
    "B600": {"width": 10.0, "length": 6.0}
}

# Правила расчета дополнительных колонн
ADDITIONAL_COLUMNS = {
    "threshold": {
        "B500NEW": {
            "lamella-250": 6.5,  # порог выноса в метрах для ламелей 250 мм
            "lamella-200": 6.85,  # порог выноса в метрах для ламелей 200 мм
        },
        "B700NEW": {
            "lamella-250": 6.5,
            "lamella-200": 6.85,
        },
        "B600": 6.5,  # порог выноса в метрах для B600
    },
    "cost": {
        1: 653,  # стоимость для 1 модуля (2 колонны)
        2: 980,  # стоимость для 2 модулей (3 колонны)
        3: 1306,  # стоимость для 3 модулей (4 колонны)
    }
}

# Правила выбора автоматики для B500NEW
B500_AUTOMATION_RULES = {
    "modules_1": [
        {"width_max": 2.5, "length_min": 8.0, "tandem": True},
        {"width_min": 2.5, "length_min": 7.5, "tandem": True},
        {"width_min": 3.0, "length_min": 6.5, "tandem": True},
        {"width_min": 3.5, "length_min": 5.5, "tandem": True},
        {"width_min": 4.0, "length_min": 5.0, "tandem": True},
    ],
    "modules_2": [
        {"width_min": 5.0, "length_min": 7.5, "tandem": True},
        {"width_min": 6.0, "length_min": 6.5, "tandem": True},
        {"width_min": 7.0, "length_min": 5.5, "tandem": True},
        {"width_min": 8.0, "length_min": 5.0, "tandem": True},
    ],
    "modules_3": [
        {"width_min": 7.5, "length_min": 7.5, "tandem": True},
        {"width_min": 9.0, "length_min": 6.5, "tandem": True},
        {"width_min": 10.5, "length_min": 5.5, "tandem": True},
        {"width_min": 12.0, "length_min": 5.0, "tandem": True},
    ]
}

# Правила выбора автоматики для B700NEW
B700_AUTOMATION_RULES = {
    "modules_1": [
        {"width_max": 3.0, "length_min": 7.0, "tandem": True},
        {"width_max": 3.5, "length_min": 6.0, "tandem": True},
    ],
    "modules_2": [
        {"width_min": 6.0, "length_min": 7.0, "tandem": True},
        {"width_min": 7.0, "length_min": 6.0, "tandem": True},
    ],
}

# Стоимость автоматики
AUTOMATION_COST = {
    "B500NEW": {
        "standard": {
            "name": "Bansbach T1",
            "cost": 700,
            "components": [
                "Двигатель easyE-lift-50 Bansbach - 1 шт.",
                "Блок управления для 1-го двигателя + блок питания - 1 шт.",
                "Приемник - 1 шт."
            ]
        },
        "tandem": {
            "name": "Bansbach Tandem",
            "cost": 1250,
            "components": [
                "Двигатель easyE-lift-50 Bansbach - 2 шт.",
                "Блок управления для 2-х двигателей + блок питания - 1 шт.",
                "Приемник - 1 шт."
            ]
        }
    },
    "B700NEW": {
        "standard": {
            "name": "Somfy M1",
            "cost": 300,
            "components": [
                "Привод Somfy Altus RTS 120/12 - 1 шт.",
                "Блок управления Somfy - 1 шт."
            ]
        },
        "tandem": {
            "name": "Somfy M2 TANDEM",
            "cost": 1000,
            "components": [
                "Привод Somfy Altus RTS 120/12 - 2 шт.",
                "Блок управления Somfy для двух двигателей - 1 шт."
            ]
        }
    },
    "B600": {
        "standard": {
            "name": "Стандартный привод для PIR-панелей",
            "cost": 580,
            "components": [
                "Стандартный привод для PIR-панелей - 1 шт.",
                "Блок управления - 1 шт."
            ]
        }
    }
}

# Стоимость пультов ДУ
REMOTE_CONTROL = {
    "Simu 1K": {
        "channels": 1,
        "cost": 25,
        "description": "Пульт Simu 1K (1 канал) - 1 шт."
    },
    "Simu 5K": {
        "channels": 5,
        "cost": 40,
        "description": "Пульт Simu 5K (5 каналов) - 1 шт."
    },
    "Simu 15K": {
        "channels": 15,
        "cost": 90,
        "description": "Пульт Simu 15K (15 каналов) - 1 шт."
    }
}

# Стоимость освещения
LIGHTING = {
    "white": {
        "name": "Белая LED",
        "price_per_meter": 20,
        "controller_price": 300,
        "controller_name": "Блок управления освещением Somfy RTS Dimmer"
    },
    "rgb": {
        "name": "RGB LED",
        "price_per_meter": 20,
        "controller_price": 300,
        "controller_name": "Блок управления освещением Somfy RTS Dimmer"
    },
    "rgbw": {
        "name": "RGBW LED (белая + RGB)",
        "price_per_meter": 40,  # 20 + 20 за оба типа ленты
        "controller_price": 300,
        "controller_name": "Блок управления освещением Somfy RTS Dimmer"
    }
}

# Правило расчета периметра подсветки
def calculate_lighting_perimeter(width_m, length_m, modules=1):
    """
    Расчет периметра подсветки согласно инструкции
    
    Args:
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей перголы
        
    Returns:
        float: Периметр для расчета длины светодиодной ленты
    """
    if modules == 1:
        # Для одного модуля - просто периметр
        return 2 * (width_m + length_m)
    else:
        # Для нескольких модулей считаем периметр для каждого модуля
        module_width = width_m / modules
        return modules * 2 * (module_width + length_m)

# Правило корректировки размера выноса перголы
def adjust_length_for_lamella_size(length_m, lamella_size_mm):
    """
    Корректирует размер выноса перголы до ближайшего целого числа ламелей
    
    Args:
        length_m (float): Вынос перголы в метрах
        lamella_size_mm (int): Размер ламели в миллиметрах (200 или 250)
        
    Returns:
        float: Скорректированный размер выноса перголы
    """
    # Расчет количества ламелей
    lamella_size_m = lamella_size_mm / 1000  # переводим в метры
    num_lamellas = length_m / lamella_size_m
    
    # Округляем до ближайшего целого в большую сторону
    rounded_num_lamellas = int(num_lamellas) + (1 if num_lamellas % 1 > 0 else 0)
    
    # Вычисляем новый размер выноса
    adjusted_length_m = rounded_num_lamellas * lamella_size_m
    
    return adjusted_length_m