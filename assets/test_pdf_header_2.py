#!/usr/bin/env python3
"""
Скрипт для тестирования обновленной шапки PDF.
Создает тестовый PDF с новой шапкой и проверяет её отображение.
"""

import os
import sys
from datetime import datetime
import pytz

# Устанавливаем рабочую директорию и добавляем её в путь импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
os.chdir(parent_dir)
sys.path.append(parent_dir)

# Импортируем модуль для PDF
from pdf_generator_fpdf_rus import PDF, generate_commercial_offer

# Подготовка тестовых данных
def create_test_pdf():
    """Создает тестовый PDF-файл с шапкой"""
    
    # Подготавливаем ресурсы
    try:
        from prepare_pdf_assets import prepare_pdf_assets
        prepare_pdf_assets()
    except ImportError:
        print("Модуль prepare_pdf_assets не найден, продолжаем без него")
    
    # Создаем директорию для выходных файлов, если её нет
    os.makedirs("generated_pdf", exist_ok=True)
    
    # Создаем объект PDF
    pdf = PDF()
    pdf.add_page()
    
    # Заголовок содержимого
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Тестовый документ - проверка шапки', 0, 1, 'C')
    
    # Добавляем текст содержимого
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, 'Этот документ создан для проверки отображения шапки в PDF.'
               '\nШапка должна содержать синий фон, белый текст и текстовое содержимое.'
               '\nВнизу страницы должен быть футер с номером страницы.', 0, 'L')
    
    # Создаем и сохраняем PDF
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    date_str = now.strftime("%Y%m%d_%H%M%S")
    pdf_path = f"generated_pdf/test_header2_{date_str}.pdf"
    
    pdf.output(pdf_path)
    print(f"Тестовый PDF создан: {pdf_path}")
    return pdf_path

def test_commercial_offer():
    """Тестирует функцию создания коммерческого предложения"""
    
    # Подготавливаем тестовые данные
    pergola_data = {
        'pergola_type': 'B700NEW',
        'width': 3.0,
        'length': 4.0,
        'lamella_type': 'Ламели 200 мм',
        'modules': 1,
        'base_price': 450000,
        'total_price': 520000,
        'options': [
            {'name': 'Двигатель Somfy (Франция)', 'price': 35000, 'quantity': 1},
            {'name': 'LED подсветка периметра', 'price': 15000, 'quantity': 1},
            {'name': 'Датчик дождя', 'price': 20000, 'quantity': 1}
        ],
        'client_name': 'Тестовый клиент',
        'phone': '+7 (999) 123-45-67',
        'date': datetime.now(pytz.timezone('Europe/Moscow')).strftime("%d.%m.%Y")
    }
    
    # Создаем коммерческое предложение
    pdf_path = generate_commercial_offer(pergola_data)
    print(f"Успешно создано тестовое коммерческое предложение: {pdf_path}")
    
    return pdf_path

if __name__ == "__main__":
    # Тест создания PDF
    simple_pdf_path = create_test_pdf()
    print(f"Успешно создан тестовый PDF с шапкой: {simple_pdf_path}")
    
    # Тест создания коммерческого предложения
    commercial_pdf_path = test_commercial_offer()
    print(f"Успешно создано тестовое коммерческое предложение: {commercial_pdf_path}")