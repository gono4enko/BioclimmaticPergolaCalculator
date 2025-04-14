"""
Модуль для управления кэшем расчетов перголы.
Позволяет сохранять и быстро получать результаты расчетов для типовых размеров,
что существенно ускоряет работу приложения.
"""

import os
import json
import hashlib
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    filename='logs/cache.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cache_manager')

# Константы
CACHE_DIR = "data/cache"
CACHE_EXPIRY_DAYS = 30  # Срок действия кэша в днях
STANDARD_SIZES = {
    # Стандартные размеры пергол, которые часто запрашиваются
    "B500NEW": [
        (3.0, 3.0), (3.0, 4.0), (3.0, 5.0),
        (4.0, 3.0), (4.0, 4.0), (4.0, 5.0),
        (5.0, 3.0), (5.0, 4.0), (5.0, 5.0),
        (6.0, 3.0), (6.0, 4.0), (6.0, 5.0)
    ],
    "B700NEW": [
        (3.0, 3.0), (3.0, 4.0), (3.0, 5.0),
        (4.0, 3.0), (4.0, 4.0), (4.0, 5.0),
        (5.0, 3.0), (5.0, 4.0), (5.0, 5.0),
        (6.0, 3.0), (6.0, 4.0), (6.0, 5.0)
    ],
    "B600": [
        (3.0, 3.0), (3.0, 4.0), (3.0, 5.0),
        (4.0, 3.0), (4.0, 4.0), (4.0, 5.0),
        (5.0, 3.0), (5.0, 4.0), (5.0, 5.0),
        (6.0, 3.0), (6.0, 4.0), (6.0, 5.0)
    ]
}


def ensure_cache_dir():
    """Создает директорию для кэша, если она не существует"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def generate_cache_key(dimensions: Dict[str, float], options: Dict[str, Any]) -> str:
    """
    Генерирует уникальный ключ кэша на основе параметров расчета
    
    Args:
        dimensions (dict): Размеры перголы (ширина, вынос)
        options (dict): Опции перголы (тип, материалы, освещение и т.д.)
        
    Returns:
        str: Хеш-ключ для идентификации этого расчета в кэше
    """
    # Создаем сортированный словарь для стабильной генерации хеша
    sorted_data = {
        "dimensions": dict(sorted(dimensions.items())),
        "options": dict(sorted(options.items()))
    }
    
    # Преобразуем в строку и создаем хеш
    data_str = json.dumps(sorted_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()


def get_cache_path(cache_key: str) -> str:
    """
    Получает путь к файлу кэша для данного ключа
    
    Args:
        cache_key (str): Ключ кэша
        
    Returns:
        str: Путь к файлу кэша
    """
    return os.path.join(CACHE_DIR, f"{cache_key}.json")


def is_cache_valid(cache_path: str) -> bool:
    """
    Проверяет, действителен ли кэш (не просрочен)
    
    Args:
        cache_path (str): Путь к файлу кэша
        
    Returns:
        bool: True если кэш действителен, иначе False
    """
    if not os.path.exists(cache_path):
        return False
    
    # Проверяем возраст файла
    file_time = os.path.getmtime(cache_path)
    current_time = time.time()
    days_old = (current_time - file_time) / (60 * 60 * 24)
    
    return days_old < CACHE_EXPIRY_DAYS


def save_to_cache(dimensions: Dict[str, float], options: Dict[str, Any], 
                 results: Dict[str, Any]) -> str:
    """
    Сохраняет результаты расчета в кэш
    
    Args:
        dimensions (dict): Размеры перголы
        options (dict): Опции перголы
        results (dict): Результаты расчета
        
    Returns:
        str: Ключ кэша, использованный для сохранения
    """
    ensure_cache_dir()
    cache_key = generate_cache_key(dimensions, options)
    cache_path = get_cache_path(cache_key)
    
    # Добавляем метаданные к результатам
    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "dimensions": dimensions,
        "options": options,
        "results": results
    }
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Сохранен в кэш: {cache_key}")
    return cache_key


def get_from_cache(dimensions: Dict[str, float], options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Получает результаты расчета из кэша если они существуют и действительны
    
    Args:
        dimensions (dict): Размеры перголы
        options (dict): Опции перголы
        
    Returns:
        dict or None: Результаты расчета или None если кэш не найден или недействителен
    """
    cache_key = generate_cache_key(dimensions, options)
    cache_path = get_cache_path(cache_key)
    
    if not is_cache_valid(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        logger.info(f"Получен из кэша: {cache_key}")
        return cache_data["results"]
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        logger.warning(f"Ошибка при чтении кэша {cache_key}: {str(e)}")
        return None


def prepare_standard_sizes_cache(calculate_func):
    """
    Предварительно рассчитывает и кэширует стандартные размеры пергол
    
    Args:
        calculate_func: Функция расчета, которая принимает dimensions и options
                       и возвращает результаты расчета
    """
    logger.info("Начинаем предварительный расчет стандартных размеров...")
    
    # Базовые опции для каждого типа
    base_options = {
        "B500NEW": {
            "pergola_type": "B500NEW",
            "lamella_size": "200",
            "rgb_lighting": False,
            "white_lighting": False,
            "installation": False
        },
        "B700NEW": {
            "pergola_type": "B700NEW",
            "lamella_size": "200",
            "rgb_lighting": False,
            "white_lighting": False,
            "installation": False
        },
        "B600": {
            "pergola_type": "B600",
            "lamella_size": "PIR",
            "rgb_lighting": False,
            "white_lighting": False,
            "installation": False
        }
    }
    
    total_cached = 0
    
    # Для каждого типа перголы
    for pergola_type, sizes in STANDARD_SIZES.items():
        options = base_options[pergola_type].copy()
        
        # Для каждого стандартного размера
        for width, length in sizes:
            dimensions = {
                "width": width,
                "length": length
            }
            
            # Проверяем, есть ли уже в кэше
            cache_key = generate_cache_key(dimensions, options)
            cache_path = get_cache_path(cache_key)
            
            if not is_cache_valid(cache_path):
                # Выполняем расчет и сохраняем в кэш
                try:
                    results = calculate_func(dimensions, options)
                    save_to_cache(dimensions, options, results)
                    total_cached += 1
                except Exception as e:
                    logger.error(f"Ошибка при расчете {pergola_type} {width}x{length}м: {str(e)}")
    
    logger.info(f"Предварительный расчет завершен. Кэшировано {total_cached} стандартных размеров.")


def clean_expired_cache():
    """
    Удаляет устаревшие записи кэша
    """
    ensure_cache_dir()
    cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
    
    removed = 0
    for filename in cache_files:
        cache_path = os.path.join(CACHE_DIR, filename)
        if not is_cache_valid(cache_path):
            try:
                os.remove(cache_path)
                removed += 1
            except OSError as e:
                logger.error(f"Ошибка при удалении кэша {filename}: {str(e)}")
    
    logger.info(f"Очистка кэша завершена. Удалено {removed} устаревших записей.")


def get_cache_stats() -> Dict[str, Any]:
    """
    Получает статистику использования кэша
    
    Returns:
        dict: Статистика кэша (общее количество, размер, действительных записей и т.д.)
    """
    ensure_cache_dir()
    cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
    
    total_files = len(cache_files)
    valid_files = 0
    cache_size_bytes = 0
    
    for filename in cache_files:
        cache_path = os.path.join(CACHE_DIR, filename)
        if is_cache_valid(cache_path):
            valid_files += 1
        
        try:
            cache_size_bytes += os.path.getsize(cache_path)
        except OSError:
            pass
    
    return {
        "total_entries": total_files,
        "valid_entries": valid_files,
        "expired_entries": total_files - valid_files,
        "cache_size_bytes": cache_size_bytes,
        "cache_size_mb": round(cache_size_bytes / (1024 * 1024), 2),
        "cache_dir": CACHE_DIR,
        "expiry_days": CACHE_EXPIRY_DAYS
    }