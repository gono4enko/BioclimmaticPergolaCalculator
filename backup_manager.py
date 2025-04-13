#!/usr/bin/env python3
"""
Скрипт для управления бэкапами в директории backups.
Сохраняет только последние 4 бэкапа, удаляя остальные для экономии дискового пространства.
Это помогает избежать проблем с деплоем из-за слишком большого размера проекта.
"""

import os
import shutil
import glob
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/backup_manager.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def clean_backups(backups_dir="backups", keep_latest=4):
    """
    Очищает директорию бэкапов, оставляя только указанное количество последних бэкапов.
    
    Args:
        backups_dir (str): Путь к директории с бэкапами
        keep_latest (int): Количество последних бэкапов, которые нужно оставить
        
    Returns:
        tuple: (количество удаленных бэкапов, освобожденное место в байтах)
    """
    # Убедимся, что директория существует
    if not os.path.exists(backups_dir):
        logger.warning(f"Директория {backups_dir} не существует")
        return 0, 0
    
    # Получаем все элементы в директории с их временем создания
    items = []
    total_size = 0
    
    for item in os.listdir(backups_dir):
        item_path = os.path.join(backups_dir, item)
        
        # Получаем время модификации и размер
        try:
            mtime = os.path.getmtime(item_path)
            
            # Вычисляем размер (для директорий - размер всех файлов внутри)
            if os.path.isdir(item_path):
                size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, _, filenames in os.walk(item_path)
                    for filename in filenames
                    if os.path.exists(os.path.join(dirpath, filename))
                )
            else:
                size = os.path.getsize(item_path)
                
            items.append((item_path, mtime, size))
            total_size += size
            
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Не удалось обработать {item_path}: {e}")
    
    # Сортируем по времени модификации (сначала новые)
    items.sort(key=lambda x: x[1], reverse=True)
    
    # Логируем общую информацию
    logger.info(f"Всего найдено {len(items)} бэкапов, общий размер: {total_size / (1024 * 1024):.2f} MB")
    
    # Оставляем только последние keep_latest элементов
    items_to_remove = items[keep_latest:]
    removed_count = 0
    freed_space = 0
    
    for item_path, _, size in items_to_remove:
        try:
            logger.info(f"Удаление {item_path} (размер: {size / (1024 * 1024):.2f} MB)")
            
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
                
            removed_count += 1
            freed_space += size
            
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Не удалось удалить {item_path}: {e}")
    
    # Логируем результаты
    if removed_count > 0:
        logger.info(f"Удалено {removed_count} бэкапов, освобождено {freed_space / (1024 * 1024):.2f} MB")
    else:
        logger.info(f"Нет бэкапов для удаления (всего {len(items)}, нужно оставить {keep_latest})")
    
    return removed_count, freed_space

if __name__ == "__main__":
    # Создаем директорию для логов, если её нет
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Запуск очистки бэкапов")
    removed, freed = clean_backups()
    
    if removed > 0:
        print(f"✅ Очистка завершена: удалено {removed} бэкапов, освобождено {freed / (1024 * 1024):.2f} MB")
    else:
        print("✅ Очистка завершена: нет бэкапов для удаления")