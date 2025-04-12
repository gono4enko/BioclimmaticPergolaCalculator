"""
Модуль защиты существующего контента от непреднамеренных изменений.
Отслеживает файлы контента, изображения и конфигурации, чтобы предотвратить
случайные изменения во время разработки новых функций.
"""

import os
import hashlib
import json
import time
import streamlit as st
from datetime import datetime


# Пути, которые нужно защитить от изменений
PROTECTED_PATHS = [
    'config/pergola_descriptions.py',
    'config/promotions.py',
    'attached_assets',  # Директория с изображениями
]

# Файл для хранения хешей защищенных файлов
CONTENT_HASHES_FILE = '.content_protection_hashes.json'

# Глобальный флаг, разрешающий изменения (может быть установлен через аргументы)
ALLOW_CHANGES = False


def calculate_file_hash(file_path):
    """
    Вычисляет MD5-хеш файла
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        str: MD5-хеш содержимого файла
    """
    if not os.path.exists(file_path):
        return ""
        
    if os.path.isdir(file_path):
        return calculate_directory_hash(file_path)
        
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Ошибка при вычислении хеша {file_path}: {str(e)}")
        return ""


def calculate_directory_hash(dir_path):
    """
    Вычисляет хеш директории на основе хешей всех файлов внутри
    
    Args:
        dir_path (str): Путь к директории
        
    Returns:
        str: Хеш директории
    """
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        return ""
        
    files_hashes = []
    
    try:
        for root, _, files in os.walk(dir_path):
            for filename in sorted(files):  # Сортируем для стабильности
                if filename.startswith('.'):
                    continue  # Пропускаем скрытые файлы
                    
                file_path = os.path.join(root, filename)
                file_hash = calculate_file_hash(file_path)
                rel_path = os.path.relpath(file_path, dir_path)
                files_hashes.append((rel_path, file_hash))
    except Exception as e:
        print(f"Ошибка при обходе директории {dir_path}: {str(e)}")
        return ""
    
    # Создаем хеш из отсортированного списка пар (путь, хеш)
    dir_hash = hashlib.md5()
    for path, file_hash in sorted(files_hashes):
        dir_hash.update(f"{path}:{file_hash}".encode())
    
    return dir_hash.hexdigest()


def save_content_hashes():
    """
    Сохраняет хеши защищенных файлов в JSON-файл
    """
    hashes = {}
    
    for path in PROTECTED_PATHS:
        abs_path = os.path.abspath(path)
        hashes[path] = calculate_file_hash(abs_path)
    
    try:
        with open(CONTENT_HASHES_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'hashes': hashes
            }, f, indent=2)
        print(f"Хеши защищенного контента сохранены в {CONTENT_HASHES_FILE}")
    except Exception as e:
        print(f"Ошибка при сохранении хешей: {str(e)}")


def load_content_hashes():
    """
    Загружает хеши защищенных файлов из JSON-файла
    
    Returns:
        dict: Словарь с хешами файлов
    """
    if not os.path.exists(CONTENT_HASHES_FILE):
        return {}
    
    try:
        with open(CONTENT_HASHES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('hashes', {})
    except Exception as e:
        print(f"Ошибка при загрузке хешей: {str(e)}")
        return {}


def verify_content_protection():
    """
    Проверяет, не были ли изменены защищенные файлы
    
    Returns:
        bool: True если все файлы соответствуют сохраненным хешам, False в противном случае
    """
    if ALLOW_CHANGES:
        return True
        
    old_hashes = load_content_hashes()
    if not old_hashes:
        print("Хеши защищенного контента не найдены. Создаем новые...")
        save_content_hashes()
        return True
    
    changed_files = []
    
    for path in PROTECTED_PATHS:
        abs_path = os.path.abspath(path)
        current_hash = calculate_file_hash(abs_path)
        stored_hash = old_hashes.get(path, "")
        
        if current_hash != stored_hash:
            changed_files.append(path)
    
    if changed_files:
        print("\nВНИМАНИЕ! Обнаружены изменения в защищенных файлах:")
        for file in changed_files:
            print(f" - {file}")
        print("\nЭти файлы защищены от случайных изменений.")
        print("Если изменения преднамеренны, установите флаг ALLOW_CHANGES = True в content_protection.py")
        print("или вызовите функцию set_allow_changes(True) перед изменением.\n")
        return False
    
    return True


def set_allow_changes(allow=True):
    """
    Устанавливает флаг, разрешающий изменения защищенных файлов
    
    Args:
        allow (bool): True, чтобы разрешить изменения, False - запретить
    """
    global ALLOW_CHANGES
    ALLOW_CHANGES = allow
    print(f"Изменения защищенных файлов {'разрешены' if allow else 'запрещены'}")


def update_protected_hashes():
    """
    Обновляет хеши защищенных файлов после преднамеренных изменений
    """
    set_allow_changes(True)
    save_content_hashes()
    print("Хеши защищенных файлов обновлены.")


def create_backup_before_changes():
    """
    Создает резервную копию защищенных файлов перед внесением изменений
    
    Returns:
        str: Путь к директории с резервной копией
    """
    backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}_content_protection"
    os.makedirs(backup_dir, exist_ok=True)
    
    for path in PROTECTED_PATHS:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            continue
            
        dest_path = os.path.join(backup_dir, path)
        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)
        
        if os.path.isdir(abs_path):
            import shutil
            shutil.copytree(abs_path, dest_path, dirs_exist_ok=True)
        else:
            import shutil
            shutil.copy2(abs_path, dest_path)
    
    print(f"Резервная копия защищенных файлов создана в {backup_dir}")
    return backup_dir


def display_protected_files_info():
    """
    Отображает информацию о защищенных файлах в streamlit
    """
    st.subheader("Защищенные файлы контента")
    st.write("Следующие файлы и директории защищены от непреднамеренных изменений:")
    
    for path in PROTECTED_PATHS:
        if os.path.isdir(path):
            st.write(f"📁 {path} (директория)")
        else:
            st.write(f"📄 {path}")
    
    old_hashes = load_content_hashes()
    if old_hashes:
        timestamp = json.load(open(CONTENT_HASHES_FILE))['timestamp']
        st.write(f"Последнее обновление хешей: {timestamp}")
    else:
        st.warning("Хеши защищенных файлов еще не созданы.")
        
    cols = st.columns(2)
    with cols[0]:
        if st.button("Создать резервную копию"):
            backup_path = create_backup_before_changes()
            st.success(f"Резервная копия создана: {backup_path}")
    
    with cols[1]:
        if st.button("Обновить хеши"):
            update_protected_hashes()
            st.success("Хеши файлов обновлены.")


def initialize_content_protection():
    """
    Инициализирует систему защиты контента при запуске приложения
    """
    # Если файла хешей нет, создаем его для текущего состояния файлов
    if not os.path.exists(CONTENT_HASHES_FILE):
        save_content_hashes()
        print("Создан файл хешей защищенного контента.")
    
    # Проверяем целостность файлов
    if not verify_content_protection():
        # Если файлы изменены, можно предпринять дополнительные действия
        # Например, автоматически создать резервную копию
        backup_path = create_backup_before_changes()
        print(f"Автоматически создана резервная копия: {backup_path}")


# Инициализируем защиту при импорте модуля
if __name__ == "__main__":
    initialize_content_protection()
    print("Модуль защиты контента инициализирован.")