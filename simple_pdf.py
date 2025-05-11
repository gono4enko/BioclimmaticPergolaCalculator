"""
Простой генератор PDF без сложных зависимостей
Использует только стандартную библиотеку fpdf
"""
import os
from datetime import datetime
from fpdf import FPDF

def create_simple_pdf(data):
    """
    Создает простой PDF с информацией о перголе.
    
    Args:
        data (dict): Данные о перголе для включения в PDF
        
    Returns:
        str: Путь к сгенерированному PDF-файлу или None в случае ошибки
    """
    try:
        # Имя файла с метками времени для уникальности
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"pergola_quote_{timestamp}.pdf"
        
        # Обеспечиваем существование директории
        output_dir = "generated_pdf"
        os.makedirs(output_dir, exist_ok=True)
        
        # Полный путь к файлу
        pdf_file_path = os.path.join(output_dir, pdf_filename)
        
        # Создаем чистый PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Заголовок
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Pergola Calculation Quote", 0, 1, "C")
        pdf.ln(5)
        
        # Информация о клиенте
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Client Information", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Date: {timestamp[:8]}", 0, 1)
        pdf.ln(5)
        
        # Основная информация
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Pergola Specifications", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        # Извлекаем информацию из словаря data
        pergola_type = data.get('pergola_type', 'B500')
        width = data.get('width', 3)
        length = data.get('length', 4)
        modules = data.get('modules', 1)
        color = data.get('color', 'White')
        
        # Информация о перголе
        pdf.cell(60, 6, "Model:", 0, 0)
        pdf.cell(0, 6, f"{pergola_type}", 0, 1)
        
        pdf.cell(60, 6, "Width:", 0, 0)
        pdf.cell(0, 6, f"{width} m", 0, 1)
        
        pdf.cell(60, 6, "Length:", 0, 0)
        pdf.cell(0, 6, f"{length} m", 0, 1)
        
        pdf.cell(60, 6, "Modules:", 0, 0)
        pdf.cell(0, 6, f"{modules}", 0, 1)
        
        pdf.cell(60, 6, "Color:", 0, 0)
        pdf.cell(0, 6, f"{color}", 0, 1)
        
        pdf.ln(5)
        
        # Цены
        total_price = data.get('total_price', 0)
        discount = data.get('discount', 0)
        price_after_discount = data.get('total_price_after_discount', 0)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Price Information", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        pdf.cell(60, 6, "Base Price:", 0, 0)
        pdf.cell(0, 6, f"{total_price:,.0f} RUB", 0, 1)
        
        pdf.cell(60, 6, "Discount:", 0, 0)
        pdf.cell(0, 6, f"{discount:,.0f} RUB", 0, 1)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(60, 6, "Final Price:", 0, 0)
        pdf.cell(0, 6, f"{price_after_discount:,.0f} RUB", 0, 1)
        
        pdf.ln(10)
        
        # Примечание
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 6, "This quote is valid for 30 days from the date of issue.", 0, 1)
        
        # Сохраняем PDF
        pdf.output(pdf_file_path)
        
        return pdf_file_path
    except Exception as e:
        import traceback
        print(f"Ошибка при создании простого PDF: {e}")
        traceback.print_exc()
        return None

def get_pdf_download_button(pdf_path, pergola_type="B500"):
    """
    Создает HTML кнопку для скачивания PDF.
    Использует прямую ссылку на файл вместо сложных компонентов.
    
    Args:
        pdf_path (str): Путь к PDF файлу
        pergola_type (str): Тип перголы для названия файла
    
    Returns:
        str: HTML-код кнопки скачивания
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return None
    
    # Получаем имя файла
    filename = os.path.basename(pdf_path)
    
    # Создаем HTML-код кнопки
    button_html = f"""
    <div style="margin: 20px 0; text-align: center;">
        <a href="{pdf_path}" 
           download="{filename}" 
           target="_blank" 
           style="display: inline-block; 
                  padding: 10px 20px; 
                  background: #4CAF50; 
                  color: white; 
                  text-decoration: none; 
                  border-radius: 4px; 
                  font-weight: bold;">
            📄 Скачать коммерческое предложение (PDF)
        </a>
    </div>
    """
    
    return button_html