"""
Модуль с настройками цен и наценок для калькулятора пергол.
Значения могут быть изменены через панель администрирования.
"""
import os
import json
from pathlib import Path

# Файл для хранения настроек
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "pricing_settings.json")

# Значения по умолчанию
DEFAULT_SETTINGS = {
    "euro_rate": 110,                    # 1 евро = 110 рублей
    "delivery_markup_percent": 8,        # 8% наценка за доставку
    "installation_markup_percent": 13,   # 13% наценка за установку
    "content_order": {                   # Порядок отображения блоков контента
        "gallery": 1,                    # Галерея проектов
        "lamella_description": 2,        # Описание ламелей
        "drive_description": 3,          # Описание привода
        "drainage_description": 4,       # Описание системы водоотвода
        "installation_description": 5    # Описание системы установки
    }
}

def get_settings():
    """
    Получает текущие настройки из JSON файла или создает файл с настройками по умолчанию.
    
    Returns:
        dict: Словарь с настройками цен и наценок
    """
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        print(f"Ошибка чтения файла настроек: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """
    Сохраняет настройки в JSON файл.
    
    Args:
        settings (dict): Словарь с настройками для сохранения
    
    Returns:
        bool: True если сохранение прошло успешно, False в случае ошибки
    """
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")
        return False

def get_euro_rate():
    """
    Получает текущий курс евро.
    
    Returns:
        float: Курс евро в рублях
    """
    return get_settings().get("euro_rate", DEFAULT_SETTINGS["euro_rate"])

def get_delivery_markup_percent():
    """
    Получает текущий процент наценки за доставку.
    
    Returns:
        float: Процент наценки за доставку
    """
    return get_settings().get("delivery_markup_percent", DEFAULT_SETTINGS["delivery_markup_percent"])

def get_installation_markup_percent():
    """
    Получает текущий процент наценки за установку.
    
    Returns:
        float: Процент наценки за установку
    """
    return get_settings().get("installation_markup_percent", DEFAULT_SETTINGS["installation_markup_percent"])

def get_content_order():
    """
    Получает порядок отображения блоков контента.
    
    Returns:
        dict: Словарь с порядком отображения контента
    """
    return get_settings().get("content_order", DEFAULT_SETTINGS["content_order"])

def update_euro_rate(new_rate):
    """
    Обновляет курс евро.
    
    Args:
        new_rate (float): Новый курс евро
        
    Returns:
        bool: True если обновление прошло успешно, False в случае ошибки
    """
    settings = get_settings()
    settings["euro_rate"] = float(new_rate)
    return save_settings(settings)

def update_delivery_markup(new_markup):
    """
    Обновляет процент наценки за доставку.
    
    Args:
        new_markup (float): Новый процент наценки за доставку
        
    Returns:
        bool: True если обновление прошло успешно, False в случае ошибки
    """
    settings = get_settings()
    settings["delivery_markup_percent"] = float(new_markup)
    return save_settings(settings)

def update_installation_markup(new_markup):
    """
    Обновляет процент наценки за установку.
    
    Args:
        new_markup (float): Новый процент наценки за установку
        
    Returns:
        bool: True если обновление прошло успешно, False в случае ошибки
    """
    settings = get_settings()
    settings["installation_markup_percent"] = float(new_markup)
    return save_settings(settings)

def update_content_order(new_order):
    """
    Обновляет порядок отображения блоков контента.
    
    Args:
        new_order (dict): Новый порядок отображения контента
        
    Returns:
        bool: True если обновление прошло успешно, False в случае ошибки
    """
    settings = get_settings()
    settings["content_order"] = new_order
    return save_settings(settings)