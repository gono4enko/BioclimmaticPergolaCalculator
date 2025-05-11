#!/usr/bin/env python3
"""
Тестовый скрипт для проверки шапки PDF
"""

import os
import sys
from datetime import datetime
import pytz

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем класс PDF из модуля pdf_generator_fpdf_rus
from pdf_generator_fpdf_rus import PDF

# Константы
ROSTOV_TZ = pytz.timezone('Europe/Moscow')  # МСК = Ростов

def generate_test_pdf():
    """
    Создает тестовый PDF файл с шапкой
    """
    # Создаем директорию для выходного файла, если она не существует
    output_dir = "generated_pdf"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Формируем имя файла с временной меткой
    now_utc = datetime.now(pytz.utc)
    now_rostov = now_utc.astimezone(ROSTOV_TZ)
    timestamp = now_rostov.strftime("%Y%m%d_%H%M%S")
    
    # Путь к выходному файлу
    output_path = f"{output_dir}/test_header_{timestamp}.pdf"
    
    # Создаем экземпляр PDF
    pdf = PDF()
    
    # Добавляем страницу
    pdf.add_page()
    
    # Добавляем заголовок
    pdf.chapter_title("Тестовый документ")
    
    # Добавляем несколько строк текста
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, "Это тестовый документ для проверки шапки PDF.\nШапка должна содержать логотип компании на синем фоне и контактную информацию.")
    
    # Добавляем подзаголовок
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, "Проверка оформления документа", 0, 1)
    
    # Еще текст
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, "Текст должен быть четко отделен от шапки. Между шапкой и основным содержимым должно быть достаточно свободного пространства.")
    
    # Добавляем информацию о перголе (как в обычном PDF)
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 8, "Параметры перголы:", 0, 1, "L")
    
    # Добавляем таблицу параметров
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(80, 8, "Тип перголы:", 0, 0)
    pdf.cell(0, 8, "B500NEW", 0, 1)
    
    pdf.cell(80, 8, "Ширина:", 0, 0)
    pdf.cell(0, 8, "3.5 м", 0, 1)
    
    pdf.cell(80, 8, "Вынос (длина):", 0, 0)
    pdf.cell(0, 8, "4.0 м", 0, 1)
    
    pdf.cell(80, 8, "Высота опор:", 0, 0)
    pdf.cell(0, 8, "2.5 м", 0, 1)
    
    pdf.cell(80, 8, "Количество модулей:", 0, 0)
    pdf.cell(0, 8, "1", 0, 1)
    
    # Сохраняем PDF-файл
    pdf.output(output_path)
    
    print(f"Тестовый PDF создан: {output_path}")
    
    return output_path

if __name__ == "__main__":
    try:
        pdf_path = generate_test_pdf()
        print(f"Успешно создан тестовый PDF с шапкой: {pdf_path}")
    except Exception as e:
        print(f"Ошибка при создании тестового PDF: {e}")