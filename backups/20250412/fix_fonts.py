import re
import os

def replace_arial_with_dejavu(file_path):
    print(f"Обработка файла {file_path}")
    
    # Открываем файл для чтения
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Заменяем все упоминания Arial на DejaVu
    # Учитываем разные варианты кавычек и форматирования
    pattern = r'self\.set_font\(["\']Arial["\']'
    replacement = r'self.set_font("DejaVu"'
    modified_content = re.sub(pattern, replacement, content)
    
    pattern = r'pdf\.set_font\(["\']Arial["\']'
    replacement = r'pdf.set_font("DejaVu"'
    modified_content = re.sub(pattern, replacement, modified_content)
    
    # Заменяем комментарии про Arial
    pattern = r'# Arial поддерживает кириллицу и является стандартным шрифтом'
    replacement = r'# DejaVu поддерживает кириллицу и используется вместо Arial'
    modified_content = re.sub(pattern, replacement, modified_content)
    
    pattern = r'# Указываем, что мы будем использовать стандартный шрифт Arial'
    replacement = r'# Указываем, что мы будем использовать шрифт DejaVu с поддержкой кириллицы'
    modified_content = re.sub(pattern, replacement, modified_content)
    
    # Сохраняем изменения
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print(f"Файл {file_path} успешно обновлен")

# Обрабатываем основной PDF-генератор
replace_arial_with_dejavu('pdf_generator_fpdf.py')

print("Обработка шрифтов завершена.")