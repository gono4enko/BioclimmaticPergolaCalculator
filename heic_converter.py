"""
Конвертер HEIC в JPEG для обработки файлов в формате Apple HEIC
Используется внешний инструмент heif-convert из пакета libheif
Оптимизирован для работы с галереей проектов перголы
"""

import os
import subprocess
import logging
import hashlib
from pathlib import Path
from PIL import Image

def get_image_hash(image_path):
    """
    Создает MD5-хеш содержимого изображения для проверки дубликатов
    
    Args:
        image_path (str): Путь к изображению
        
    Returns:
        str: MD5-хеш содержимого файла или None при ошибке
    """
    try:
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        logging.error(f"Ошибка при создании хеша для {image_path}: {str(e)}")
        return None

def clean_filename(filename):
    """
    Очищает имя файла от специальных символов, пробелов и т.д.
    
    Args:
        filename (str): Исходное имя файла
        
    Returns:
        str: Очищенное имя файла
    """
    # Заменяем пробелы на подчеркивания
    cleaned = filename.replace(' ', '_')
    # Удаляем специальные символы
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
    cleaned = ''.join(c for c in cleaned if c in allowed_chars)
    return cleaned

def is_duplicate_image(new_image_path, directory, check_content=True):
    """
    Проверяет, является ли изображение дубликатом одного из существующих файлов
    
    Args:
        new_image_path (str): Путь к новому изображению
        directory (str): Директория с существующими изображениями
        check_content (bool): Проверять содержимое или только имя файла
        
    Returns:
        tuple: (является ли дубликатом, путь к дубликату если найден)
    """
    # Проверяем наличие файла с таким же именем
    new_path = Path(new_image_path)
    base_filename = new_path.stem
    base_extension = new_path.suffix.lower()
    
    # Проверка по имени - без учета случайного суффикса
    normalized_name = base_filename.split('_')[0].lower()
    
    # Если для проверки нужен хеш содержимого
    if check_content and new_path.exists():
        new_file_hash = get_image_hash(new_image_path)
        if not new_file_hash:
            return False, None
    else:
        new_file_hash = None
    
    # Проверяем все изображения в директории
    directory = Path(directory)
    for file_path in directory.glob("*.*"):
        # Сначала проверяем, является ли файл изображением
        if file_path.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.heic', '.heif'):
            continue
            
        # Проверка по имени
        curr_file_stem = file_path.stem.lower()
        if normalized_name in curr_file_stem and file_path.name != new_path.name:
            # Если имя похоже, проверяем содержимое если требуется
            if check_content and new_file_hash:
                curr_file_hash = get_image_hash(file_path)
                if curr_file_hash and curr_file_hash == new_file_hash:
                    return True, str(file_path)
            else:
                return True, str(file_path)
    
    return False, None

def heic_to_jpeg(heic_path, output_dir=None, quality=90, check_duplicates=True):
    """
    Конвертирует файл HEIC в формат JPEG с использованием внешнего инструмента heif-convert
    
    Args:
        heic_path (str): Путь к HEIC файлу
        output_dir (str, optional): Директория для сохранения JPEG файла. 
                                   Если не указана, используется та же директория
        quality (int): Качество выходного JPEG файла (0-100)
        check_duplicates (bool): Проверять на дубликаты
    
    Returns:
        str: Путь к сконвертированному JPEG файлу или None при ошибке
    """
    heic_path = Path(heic_path)
    
    if not heic_path.exists():
        logging.error(f"Ошибка: Файл {heic_path} не существует")
        return None
    
    if output_dir is None:
        output_dir = heic_path.parent
    else:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем имя для выходного файла, заменяя расширение на .jpg
    output_filename = heic_path.stem + ".jpg"
    output_path = output_dir / output_filename
    
    # Проверка на дубликаты
    if check_duplicates:
        is_duplicate, duplicate_path = is_duplicate_image(str(heic_path), output_dir, False)
        if is_duplicate and duplicate_path:
            logging.warning(f"Обнаружен потенциальный дубликат: {duplicate_path}")
            if duplicate_path and duplicate_path.lower().endswith(('.jpg', '.jpeg')):
                # Если дубликат уже в формате JPEG, возвращаем его
                return duplicate_path
    
    try:
        # Используем утилиту heif-convert для конвертации
        cmd = ["heif-convert", str(heic_path), str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if output_path.exists():
            # Оптимизируем размер файла
            try:
                with Image.open(output_path) as img:
                    img.save(output_path, quality=quality, optimize=True)
            except Exception as e:
                logging.warning(f"Невозможно оптимизировать изображение: {str(e)}")
                
            logging.info(f"Файл конвертирован успешно: {output_path}")
            return str(output_path)
        else:
            logging.error(f"Ошибка: Файл не был создан, хотя команда выполнена без ошибок")
            logging.error(f"Вывод команды: {result.stdout}")
            logging.error(f"Ошибки: {result.stderr}")
            return None
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении команды конвертации: {e}")
        logging.error(f"Вывод команды: {e.stdout}")
        logging.error(f"Ошибки: {e.stderr}")
        return None
    
    except Exception as e:
        logging.error(f"Произошла неизвестная ошибка: {str(e)}")
        return None

def convert_image_to_jpeg(image_path, output_dir=None, quality=90, check_duplicates=True):
    """
    Универсальная функция для конвертации различных форматов изображений в JPEG
    
    Args:
        image_path (str): Путь к изображению
        output_dir (str, optional): Директория для сохранения JPEG файла
        quality (int): Качество выходного JPEG (0-100)
        check_duplicates (bool): Проверять на дубликаты
        
    Returns:
        str: Путь к JPEG файлу или None при ошибке
    """
    image_path = Path(image_path)
    
    # Если файл уже JPEG, просто возвращаем путь
    if image_path.suffix.lower() in ('.jpg', '.jpeg'):
        return str(image_path)
    
    # Для HEIC используем специальную функцию
    if image_path.suffix.lower() in ('.heic', '.heif'):
        return heic_to_jpeg(image_path, output_dir, quality, check_duplicates)
    
    # Для других форматов используем PIL
    try:
        if output_dir is None:
            output_dir = image_path.parent
        else:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)
        
        output_filename = image_path.stem + ".jpg"
        output_path = output_dir / output_filename
        
        # Проверка на дубликаты
        if check_duplicates:
            is_duplicate, duplicate_path = is_duplicate_image(str(image_path), output_dir, False)
            if is_duplicate:
                logging.warning(f"Обнаружен потенциальный дубликат: {duplicate_path}")
                if duplicate_path.lower().endswith(('.jpg', '.jpeg')):
                    return duplicate_path
        
        # Конвертируем в JPEG через PIL
        with Image.open(image_path) as img:
            # Если у изображения есть прозрачность, делаем белый фон
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                background.save(output_path, 'JPEG', quality=quality, optimize=True)
            else:
                img.convert('RGB').save(output_path, 'JPEG', quality=quality, optimize=True)
                
        return str(output_path)
    
    except Exception as e:
        logging.error(f"Ошибка при конвертации {image_path} в JPEG: {str(e)}")
        return None

# Функция для конвертации всех HEIC файлов в директории
def batch_convert_heic(directory, quality=90):
    """
    Конвертирует все файлы HEIC в директории в формат JPEG
    
    Args:
        directory (str): Директория с HEIC файлами
        quality (int): Качество выходного JPEG (0-100)
        
    Returns:
        list: Список путей к сконвертированным JPEG файлам
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        logging.error(f"Ошибка: Директория {directory} не существует")
        return []
    
    converted_files = []
    
    # Ищем все файлы HEIC (с разными вариантами регистра) 
    heic_files = []
    for ext in ['.heic', '.HEIC', '.Heif', '.HEIF']:
        heic_files.extend(list(directory.glob(f"*{ext}")))
    
    for heic_file in heic_files:
        jpeg_path = heic_to_jpeg(heic_file, quality=quality)
        if jpeg_path:
            converted_files.append(jpeg_path)
    
    return converted_files

# Функция проверки наличия инструмента heif-convert
def check_heif_convert():
    """
    Проверяет наличие утилиты heif-convert
    
    Returns:
        bool: True если утилита найдена, иначе False
    """
    try:
        result = subprocess.run(["which", "heif-convert"], 
                               capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def find_duplicates_in_directory(directory, check_content=True):
    """
    Находит дубликаты изображений в директории
    
    Args:
        directory (str): Директория для поиска
        check_content (bool): Проверять содержимое файлов или только имена
        
    Returns:
        list: Список групп дубликатов
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        logging.error(f"Ошибка: Директория {directory} не существует")
        return []
    
    # Словарь для хранения хешей файлов
    hash_map = {}
    name_map = {}
    
    # Собираем все изображения
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.heic', '.heif', '.JPG', '.JPEG', '.PNG', '.HEIC', '.HEIF']:
        image_files.extend(list(directory.glob(f"*{ext}")))
    
    # Анализируем каждый файл
    for img_path in image_files:
        # Проверка по содержимому
        if check_content:
            img_hash = get_image_hash(img_path)
            if img_hash:
                if img_hash not in hash_map:
                    hash_map[img_hash] = []
                hash_map[img_hash].append(str(img_path))
        
        # Проверка по базовому имени
        base_name = img_path.stem.split('_')[0].lower()
        if base_name not in name_map:
            name_map[base_name] = []
        name_map[base_name].append(str(img_path))
    
    # Формируем группы дубликатов
    duplicates = []
    
    # По содержимому
    if check_content:
        for img_hash, paths in hash_map.items():
            if len(paths) > 1:
                duplicates.append(paths)
    
    # По имени
    for base_name, paths in name_map.items():
        if len(paths) > 1:
            # Проверяем, чтобы группа не была уже добавлена
            if paths not in duplicates:
                duplicates.append(paths)
    
    return duplicates

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Пример использования
    if check_heif_convert():
        logging.info("Утилита heif-convert найдена, можно конвертировать HEIC файлы")
        # Конвертируем все HEIC в директории attached_assets
        converted = batch_convert_heic("attached_assets")
        logging.info(f"Конвертировано {len(converted)} файлов")
        
        # Поиск дубликатов
        duplicates = find_duplicates_in_directory("attached_assets")
        logging.info(f"Найдено {len(duplicates)} групп дубликатов")
    else:
        logging.warning("Утилита heif-convert не найдена. Установите пакет libheif.")