"""
Модуль содержит данные о типах пергол, ламелей и других опциях,
извлеченные из каталога.
"""

# Список доступных типов пергол и их характеристики
PERGOLA_TYPES = {
    "B500NEW": {
        "name": "B500NEW",
        "description": "Современная пергола B500NEW с алюминиевыми ламелями",
        "lamella_types": ["B500-20NEW", "B500-25NEW"],
        "default_lamella": "B500-20NEW",
        "available_lighting": ["none", "strip", "spot", "rgb"],
        "default_lighting": "none",
        "additional_options": ["sensors", "remote", "motor", "heater"]
    },
    "B700NEW": {
        "name": "B700NEW",
        "description": "Премиальная пергола B700NEW с увеличенной нагрузочной способностью",
        "lamella_types": ["B700-20NEW", "B700-25NEW"],
        "default_lamella": "B700-20NEW",
        "available_lighting": ["none", "strip", "spot", "rgb"],
        "default_lighting": "none",
        "additional_options": ["sensors", "remote", "motor", "heater", "sound"]
    },
    "B600": {
        "name": "B600",
        "description": "Пергола B600 с ламелями из PIR-панелей",
        "lamella_types": ["B600"],
        "default_lamella": "B600",
        "available_lighting": ["none", "strip", "spot"],
        "default_lighting": "none",
        "additional_options": ["sensors", "remote", "motor"]
    }
}

# Ограничения по размерам для разных типов пергол
PERGOLA_LIMITS = {
    "B500NEW": {
        "min_width": 1500,
        "max_width": 4500,
        "min_length": 1500,
        "max_length": 6000,
        "min_height": 2200,
        "max_height": 3000
    },
    "B700NEW": {
        "min_width": 1500,
        "max_width": 6000,
        "min_length": 1500,
        "max_length": 7000,
        "min_height": 2200,
        "max_height": 3000
    },
    "B600": {
        "min_width": 1500,
        "max_width": 4000,
        "min_length": 1500,
        "max_length": 5000,
        "min_height": 2200,
        "max_height": 3000
    }
}

# Описания для доступных типов ламелей
LAMELLA_TYPES = {
    "B500-20NEW": {
        "name": "B500-20NEW",
        "description": "Алюминиевые ламели 200 мм для перголы B500NEW",
        "width": 200,
        "material": "Алюминий"
    },
    "B500-25NEW": {
        "name": "B500-25NEW",
        "description": "Алюминиевые ламели 250 мм для перголы B500NEW",
        "width": 250,
        "material": "Алюминий"
    },
    "B700-20NEW": {
        "name": "B700-20NEW",
        "description": "Алюминиевые ламели 200 мм для перголы B700NEW",
        "width": 200,
        "material": "Алюминий"
    },
    "B700-25NEW": {
        "name": "B700-25NEW",
        "description": "Алюминиевые ламели 250 мм для перголы B700NEW",
        "width": 250,
        "material": "Алюминий"
    },
    "B600": {
        "name": "B600",
        "description": "Ламели из PIR-панелей для перголы B600",
        "width": 200,
        "material": "PIR-панель"
    }
}

# Описания для типов освещения
LIGHTING_TYPES = {
    "none": {
        "name": "Без освещения",
        "description": "Пергола без дополнительного освещения"
    },
    "strip": {
        "name": "Линейное освещение",
        "description": "Светодиодные ленты по периметру"
    },
    "spot": {
        "name": "Точечное освещение",
        "description": "Встроенные точечные светильники"
    },
    "rgb": {
        "name": "RGB освещение",
        "description": "Светодиодные RGB-ленты с возможностью смены цвета"
    }
}

# Описания для дополнительных опций
ADDITIONAL_OPTIONS = {
    "sensors": {
        "name": "Датчики",
        "description": "Датчики ветра, дождя и снега"
    },
    "remote": {
        "name": "ДУ",
        "description": "Пульт дистанционного управления"
    },
    "motor": {
        "name": "Мотор",
        "description": "Электропривод для управления ламелями"
    },
    "heater": {
        "name": "Обогреватель",
        "description": "Встроенные инфракрасные обогреватели"
    },
    "sound": {
        "name": "Аудиосистема",
        "description": "Встроенная аудиосистема с Bluetooth"
    }
}