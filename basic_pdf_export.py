"""
Максимально простой модуль для экспорта PDF без дополнительных зависимостей.
Использует только базовую библиотеку fpdf с минимальным функционалом.
"""
import os
from datetime import datetime
from fpdf import FPDF

def create_pergola_pdf(data):
    """
    Создает простой PDF с информацией о перголе.
    
    Args:
        data (dict): Данные о перголе для включения в PDF
        
    Returns:
        str: Путь к сгенерированному PDF-файлу или None в случае ошибки
    """
    try:
        # Создаем директорию, если не существует
        output_dir = "generated_pdf"
        os.makedirs(output_dir, exist_ok=True)
        
        # Имя файла с меткой времени для уникальности
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pergola_type = data.get('pergola_type', 'B500')
        pdf_filename = f"КП_пергола_{pergola_type}_{timestamp}.pdf"
        pdf_file_path = os.path.join(output_dir, pdf_filename)
        
        # Создаем PDF объект
        pdf = FPDF()
        pdf.add_page()
        
        # Заголовок
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Коммерческое предложение", 0, 1, "C")
        pdf.ln(5)
        
        # Дата и информация о документе
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, f"Дата: {datetime.now().strftime('%d.%m.%Y')}", 0, 1, "R")
        pdf.ln(10)
        
        # Информация о клиенте
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Информация о заказчике:", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Название компании: ___________________________", 0, 1)
        pdf.cell(0, 6, "Контактное лицо: ___________________________", 0, 1)
        pdf.cell(0, 6, "Телефон: ___________________________", 0, 1)
        pdf.ln(10)
        
        # Информация о перголе
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Спецификация перголы:", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        # Основные параметры
        width = data.get('width', 3.0)
        length = data.get('length', 4.0)
        modules = data.get('modules', 1)
        color = data.get('color', 'White')
        
        pdf.cell(60, 6, "Модель:", 0, 0)
        pdf.cell(0, 6, f"{pergola_type}", 0, 1)
        
        pdf.cell(60, 6, "Ширина:", 0, 0)
        pdf.cell(0, 6, f"{width} м", 0, 1)
        
        pdf.cell(60, 6, "Длина (вынос):", 0, 0)
        pdf.cell(0, 6, f"{length} м", 0, 1)
        
        pdf.cell(60, 6, "Количество модулей:", 0, 0)
        pdf.cell(0, 6, f"{modules}", 0, 1)
        
        pdf.cell(60, 6, "Цвет:", 0, 0)
        pdf.cell(0, 6, f"{color}", 0, 1)
        
        pdf.ln(5)
        
        # Дополнительное оборудование
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Дополнительное оборудование:", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        # Извлекаем опции
        has_lighting = data.get('has_lighting', False)
        has_sensors = data.get('has_sensors', False)
        
        if has_lighting:
            pdf.cell(0, 6, "• Светодиодная подсветка RGB", 0, 1)
        
        if has_sensors:
            pdf.cell(0, 6, "• Датчики осадков и ветра", 0, 1)
        
        pdf.ln(10)
        
        # Стоимость
        total_price = data.get('total_price', 0)
        discount = data.get('discount', 0)
        price_after_discount = data.get('total_price_after_discount', 0)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Стоимость:", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        pdf.cell(60, 6, "Базовая стоимость:", 0, 0)
        pdf.cell(0, 6, f"{total_price:,.0f} руб.", 0, 1)
        
        pdf.cell(60, 6, "Скидка:", 0, 0)
        pdf.cell(0, 6, f"{discount:,.0f} руб.", 0, 1)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(60, 6, "Итоговая стоимость:", 0, 0)
        pdf.cell(0, 6, f"{price_after_discount:,.0f} руб.", 0, 1)
        
        pdf.ln(15)
        
        # Подпись
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 10, "С уважением,", 0, 1)
        pdf.cell(0, 6, "Компания «Комфортный Дом»", 0, 1)
        pdf.cell(0, 6, "Тел: +7 (XXX) XXX-XX-XX", 0, 1)
        pdf.cell(0, 6, "Email: info@example.com", 0, 1)
        
        # Примечание
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 6, "Предложение действительно в течение 30 дней с даты формирования", 0, 1)
        
        # Сохраняем PDF
        pdf.output(pdf_file_path)
        
        return pdf_file_path
    except Exception as e:
        import traceback
        print(f"Ошибка при создании PDF: {e}")
        traceback.print_exc()
        return None