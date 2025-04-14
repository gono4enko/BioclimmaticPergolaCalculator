#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

# Директория с изображениями
assets_dir = "attached_assets"

# Копирование файлов с русскими именами на английские
files_to_copy = [
    ("В500 со вращением ламелей.png", "b500_rotation.png"),
    ("В700 со сдвижением ламелей.png", "b700_sliding.png"),
    ("В600 с сэндвич панелями.png", "b600_sandwich.png")
]

# Копирование файлов
for src_name, dst_name in files_to_copy:
    src_path = os.path.join(assets_dir, src_name)
    dst_path = os.path.join(assets_dir, dst_name)
    
    if os.path.exists(src_path):
        try:
            shutil.copy2(src_path, dst_path)
            print(f"Скопирован файл: {src_name} -> {dst_name}")
        except Exception as e:
            print(f"Ошибка при копировании {src_name}: {e}")
    else:
        print(f"Файл не найден: {src_path}")

# Вывод списка файлов после копирования
print("\nСписок файлов после копирования:")
for file in Path(assets_dir).glob("b*.png"):
    print(f"- {file.name}")