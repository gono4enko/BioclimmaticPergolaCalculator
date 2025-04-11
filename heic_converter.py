"""
Конвертер HEIC в JPEG для обработки файлов в формате Apple HEIC
Используется внешний инструмент heif-convert из пакета libheif
"""

import os
import subprocess
from pathlib import Path

def heic_to_jpeg(heic_path, output_dir=None):
    """
    Конвертирует файл HEIC в формат JPEG с использованием внешнего инструмента heif-convert
    
    Args:
        heic_path (str): Путь к HEIC файлу
        output_dir (str, optional): Директория для сохранения JPEG файла. 
                                   Если не указана, используется та же директория
    
    Returns:
        str: Путь к сконвертированному JPEG файлу или None при ошибке
    """
    heic_path = Path(heic_path)
    
    if not heic_path.exists():
        print(f"Ошибка: Файл {heic_path} не существует")
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
    
    try:
        # Используем утилиту heif-convert для конвертации
        cmd = ["heif-convert", str(heic_path), str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if output_path.exists():
            print(f"Файл конвертирован успешно: {output_path}")
            return str(output_path)
        else:
            print(f"Ошибка: Файл не был создан, хотя команда выполнена без ошибок")
            print(f"Вывод команды: {result.stdout}")
            print(f"Ошибки: {result.stderr}")
            return None
    
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды конвертации: {e}")
        print(f"Вывод команды: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return None
    
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {str(e)}")
        return None

# Функция для конвертации всех HEIC файлов в директории
def batch_convert_heic(directory):
    """
    Конвертирует все файлы HEIC в директории в формат JPEG
    
    Args:
        directory (str): Директория с HEIC файлами
        
    Returns:
        list: Список путей к сконвертированным JPEG файлам
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        print(f"Ошибка: Директория {directory} не существует")
        return []
    
    converted_files = []
    
    # Ищем все файлы HEIC (с разными вариантами регистра) 
    heic_files = []
    for ext in ['.heic', '.HEIC', '.Heic']:
        heic_files.extend(list(directory.glob(f"*{ext}")))
    
    for heic_file in heic_files:
        jpeg_path = heic_to_jpeg(heic_file)
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

if __name__ == "__main__":
    # Пример использования
    if check_heif_convert():
        print("Утилита heif-convert найдена, можно конвертировать HEIC файлы")
        # Конвертируем все HEIC в директории attached_assets
        batch_convert_heic("attached_assets")
    else:
        print("Утилита heif-convert не найдена. Установите пакет libheif.")