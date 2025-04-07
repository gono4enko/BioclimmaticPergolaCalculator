"""
Модуль содержит данные о типах пергол, ламелей и других опциях,
извлеченные из каталога.
"""

# Типы пергол
PERGOLA_TYPES = {
    "B500NEW": {
        "name": "B500 NEW с поворотными ламелями",
        "description": "Пергола с нижней осью вращения ламелей",
        "min_width": 2000,
        "max_width": 7000,
        "min_length": 2000,
        "max_length": 8000,
        "min_height": 2000,
        "max_height": 7000,
        "base_price_factor": 1.0,  # Базовый коэффициент стоимости
    },
    "B700NEW": {
        "name": "B700 NEW со сдвижными ламелями",
        "description": "Пергола со сдвижными ламелями",
        "min_width": 2000,
        "max_width": 7000,
        "min_length": 2000,
        "max_length": 8000,
        "min_height": 2000,
        "max_height": 7000,
        "base_price_factor": 1.2,  # На 20% дороже базовой модели
    },
    "B400": {
        "name": "B400 с поворотными ламелями",
        "description": "Пергола с центральной осью вращения ламелей",
        "min_width": 2000,
        "max_width": 6000,
        "min_length": 2000,
        "max_length": 7000,
        "min_height": 2000,
        "max_height": 6000,
        "base_price_factor": 0.9,  # На 10% дешевле базовой модели
    },
}

# Типы ламелей
LAMELLA_TYPES = {
    "B500-25NEW": {
        "name": "Ламель B500-25 NEW (250х53 мм)",
        "width": 250,
        "height": 53,
        "mass": 4.684,  # кг/м
        "step": 250,    # шаг ламелей в мм
        "price_factor": 1.05,
        "max_width": 5000,  # максимальная ширина ламели
    },
    "B500-20NEW": {
        "name": "Ламель B500-20 NEW (200х56 мм)",
        "width": 200,
        "height": 56,
        "mass": 4.375,  # кг/м
        "step": 200,    # шаг ламелей в мм
        "price_factor": 1.0,
        "max_width": 5000,  # максимальная ширина ламели
    },
    "B700-25NEW": {
        "name": "Ламель B700-25 NEW (250х53 мм)",
        "width": 250,
        "height": 53,
        "mass": 4.684,  # кг/м
        "step": 250,    # шаг ламелей в мм
        "price_factor": 1.1,
        "max_width": 5000,  # максимальная ширина ламели
    },
    "B700-20NEW": {
        "name": "Ламель B700-20 NEW (200х56 мм)",
        "width": 200,
        "height": 56,
        "mass": 4.375,  # кг/м
        "step": 200,    # шаг ламелей в мм
        "price_factor": 1.05,
        "max_width": 5000,  # максимальная ширина ламели
    },
    "B400-25": {
        "name": "Ламель B400-25 (250х50 мм)",
        "width": 250,
        "height": 50,
        "mass": 4.0,    # кг/м (примерно)
        "step": 250,    # шаг ламелей в мм
        "price_factor": 0.95,
        "max_width": 4500,  # максимальная ширина ламели
    },
}

# Типы монтажа
INSTALLATION_TYPES = {
    "standalone": {
        "name": "Отдельностоящая",
        "price_factor": 1.0,
    },
    "wall": {
        "name": "Пристенная",
        "price_factor": 0.85,  # На 15% дешевле отдельностоящей
    },
    "suspended": {
        "name": "Подвесная",
        "price_factor": 0.9,   # На 10% дешевле отдельностоящей
    },
    "integrated": {
        "name": "Интегрированная",
        "price_factor": 0.95,  # На 5% дешевле отдельностоящей
    },
}

# Типы освещения
LIGHTING_TYPES = {
    "none": {
        "name": "Без освещения",
        "price": 0,
    },
    "led": {
        "name": "LED подсветка",
        "price_per_meter": 50,  # евро за метр периметра
    },
    "rgb": {
        "name": "RGB подсветка с диммером",
        "price_per_meter": 85,  # евро за метр периметра
    },
}

# Дополнительные системы
ADDITIONAL_SYSTEMS = {
    "glazing_guillotine": {
        "name": "Гильотинное остекление (W-серия)",
        "price_per_m2": 450,  # евро за кв.м
    },
    "glazing_sliding": {
        "name": "Раздвижное остекление (S-серия)",
        "price_per_m2": 380,  # евро за кв.м
    },
    "zip_screen": {
        "name": "Подъемный ZIP экран",
        "price_per_m2": 280,  # евро за кв.м
    },
}

# Соответствие типов пергол и доступных ламелей
PERGOLA_LAMELLA_COMPATIBILITY = {
    "B500NEW": ["B500-25NEW", "B500-20NEW"],
    "B700NEW": ["B700-25NEW", "B700-20NEW"],
    "B400": ["B400-25"],
}
