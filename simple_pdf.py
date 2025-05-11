"""
Простой генератор PDF для перголы с минимальными зависимостями.
Создает простой PDF-документ с информацией о перголе и ее стоимости.
Используется как резервный вариант, если основной генератор PDF не работает.
"""

import os
import uuid
import datetime
from fpdf import FPDF
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_pdf")

def generate_simple_pdf(pergola_data):
    """
    Создает простой PDF-документ с информацией о перголе.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе
    
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    try:
        # Создаем директорию для PDF, если она не существует
        os.makedirs("generated_pdf", exist_ok=True)
        
        # Получаем данные из pergola_data
        pergola_type = pergola_data.get("pergola_type", "B500NEW")
        width = pergola_data.get("width", 3.0)
        length = pergola_data.get("length", 4.0)
        modules = pergola_data.get("modules", 1)
        items = pergola_data.get("items", [])
        total_price = pergola_data.get("total_price", 0)
        discount = pergola_data.get("discount", 0)
        total_after_discount = pergola_data.get("total_price_after_discount", 0)
        
        # Генерируем имя файла
        today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"КП_пергола_{pergola_type}_{width}x{length}м_{today}.pdf"
        pdf_path = os.path.join("generated_pdf", filename)
        
        # Создаем PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Добавляем заголовок
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Pergola Commercial Offer", ln=True, align="C")
        pdf.ln(5)
        
        # Добавляем информацию о перголе
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Pergola Type: {pergola_type}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 8, f"Dimensions: {width} x {length} m", ln=True)
        pdf.cell(190, 8, f"Modules: {modules}", ln=True)
        pdf.ln(5)
        
        # Добавляем таблицу с опциями
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Selected Options:", ln=True)
        pdf.ln(2)
        
        # Заголовки таблицы
        pdf.set_font("Arial", "B", 10)
        pdf.cell(110, 7, "Item", 1)
        pdf.cell(40, 7, "Quantity", 1)
        pdf.cell(40, 7, "Price (RUB)", 1)
        pdf.ln()
        
        # Строки таблицы
        pdf.set_font("Arial", "", 10)
        for item in items:
            name = item.get("name", "")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            
            # Добавляем строку в таблицу
            pdf.cell(110, 7, name, 1)
            pdf.cell(40, 7, str(quantity), 1)
            pdf.cell(40, 7, f"{price:,.0f}", 1)
            pdf.ln()
        
        # Добавляем информацию о стоимости
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 8, "Total Price:", 0)
        pdf.cell(40, 8, f"{total_price:,.0f} RUB", 0, ln=True)
        
        if discount > 0:
            pdf.set_font("Arial", "", 12)
            pdf.cell(150, 8, f"Discount ({discount}%):", 0)
            discount_amount = total_price - total_after_discount
            pdf.cell(40, 8, f"-{discount_amount:,.0f} RUB", 0, ln=True)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(150, 8, "Final Price:", 0)
            pdf.cell(40, 8, f"{total_after_discount:,.0f} RUB", 0, ln=True)
        
        # Добавляем дату и дисклеймер
        pdf.ln(15)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(190, 6, f"Offer generated on: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
        pdf.cell(190, 6, "This offer is valid for 30 days from the date of issue.", ln=True)
        
        # Сохраняем PDF-файл
        pdf.output(pdf_path)
        logger.info(f"PDF успешно создан по пути: {pdf_path}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {str(e)}", exc_info=True)
        return None