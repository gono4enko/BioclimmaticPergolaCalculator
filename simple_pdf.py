"""
Модуль для максимально простой генерации PDF с коммерческим предложением.
Реализует минимальную функциональность без зависимости от сложных шрифтов.
"""
import os
import time
from datetime import datetime
import pytz
from fpdf import FPDF
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join("logs", "pdf_generation.log"),
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("simple_pdf")

# Создаем директорию для PDF
os.makedirs("generated_pdf", exist_ok=True)

class SimplePDF(FPDF):
    """
    Максимально простой класс для генерации PDF без сложных требований к шрифтам.
    Использует только встроенные шрифты FPDF.
    """
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(True, margin=15)
        
        # Базовые метаданные PDF
        self.set_title("Kommercheskoe Predlozhenie")
        self.set_author("Pergola Calculator")
        self.set_creator("Pergola Calculator")
    
    def header(self):
        """Простой заголовок без использования внешних шрифтов или изображений"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 150)  # Темно-синий цвет
        self.cell(0, 10, 'Kommercheskoe Predlozhenie', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)  # Серый цвет
        self.cell(0, 5, 'Raschet stoimosti pergoly na ' + datetime.now().strftime('%d.%m.%Y'), 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        """Простой нижний колонтитул"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Stranitsa {self.page_no()}', 0, 0, 'C')

def generate_simple_pdf(pergola_data):
    """
    Создает простой PDF-файл с данными о перголе
    
    Args:
        pergola_data (dict): Данные о перголе
        
    Returns:
        str: Путь к сохраненному PDF-файлу
    """
    try:
        logger.info("Начало создания простого PDF")
        pdf = SimplePDF()
        pdf.add_page()
        
        # Извлекаем данные
        pergola_type = pergola_data.get("pergola_type", "")
        width = pergola_data.get("width", 0)
        length = pergola_data.get("length", 0)
        total_price = pergola_data.get("total_price", 0)
        
        # Заголовок документа
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Pergola {pergola_type}", 0, 1, "C")
        pdf.ln(5)
        
        # Основные данные о перголе
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Tehnicheskie parametry:", 0, 1)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(80, 8, "Tip konstrukcii:", 0, 0)
        pdf.cell(0, 8, pergola_type, 0, 1)
        
        pdf.cell(80, 8, "Shirina:", 0, 0)
        pdf.cell(0, 8, f"{width} m", 0, 1)
        
        pdf.cell(80, 8, "Dlina (vynos):", 0, 0)
        pdf.cell(0, 8, f"{length} m", 0, 1)
        
        # Информация о цене
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        
        # Форматирование стоимости
        formatted_price = f"{int(total_price):,}".replace(",", " ")
        pdf.cell(0, 10, f"Itogo: {formatted_price} rub.", 1, 1, "C", fill=True)
        
        # Добавляем спецификацию
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Specifikaciya:", 0, 1)
        
        # Заголовки таблицы
        headers = ["Naimenovanie", "Kol-vo", "Stoimost'"]
        col_widths = [100, 30, 40]
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(220, 220, 220)
        
        # Строка заголовков
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, "C", fill=True)
        pdf.ln()
        
        # Данные спецификации
        pdf.set_font("Arial", "", 10)
        items = pergola_data.get("items", [])
        
        for item in items:
            name = item.get("name", "")
            quantity = item.get("quantity", 0)
            price = item.get("price", 0)
            
            # Ограничиваем длину имени
            if len(name) > 40:
                name = name[:37] + "..."
                
            # Форматируем цену
            formatted_item_price = f"{int(price):,}".replace(",", " ")
            
            pdf.cell(col_widths[0], 8, name, 1, 0)
            pdf.cell(col_widths[1], 8, str(quantity), 1, 0, "C")
            pdf.cell(col_widths[2], 8, formatted_item_price, 1, 0, "R")
            pdf.ln()
        
        # Контактная информация
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Kontaktnaya informaciya:", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, "Telefon: +7 (906) 429-74-20", 0, 1)
        pdf.cell(0, 6, "Email: zakaz@infopergola.ru", 0, 1)
        pdf.cell(0, 6, "Veb-sajt: https://pergolamarket.ru", 0, 1)
        pdf.cell(0, 6, "Adres: g.Rostov-na-Donu, ul.Orskaya, 27/1", 0, 1)
        
        # Создаем информативное имя файла
        rostov_tz = pytz.timezone('Europe/Moscow')
        now_utc = datetime.now(pytz.utc)
        now_rostov = now_utc.astimezone(rostov_tz)
        current_date = now_rostov.strftime("%d.%m.%Y")
        
        file_name = f"KP_pergola_{pergola_type}_{width}x{length}м_{current_date}.pdf"
        safe_filename = file_name.replace(" ", "_").replace("/", "_")
        file_path = os.path.join("generated_pdf", safe_filename)
        
        # Сохраняем PDF
        pdf.output(file_path)
        logger.info(f"PDF успешно создан: {file_path}")
        
        return file_path
        
    except Exception as e:
        error_msg = f"Ошибка при создании PDF: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(error_msg)
        return None

if __name__ == "__main__":
    # Тестовые данные
    test_data = {
        "pergola_type": "B500NEW",
        "width": 3.0,
        "length": 4.0,
        "total_price": 1250000,
        "items": [
            {"name": "Pergola B500", "quantity": 1, "price": 1000000},
            {"name": "Montazh", "quantity": 1, "price": 250000},
        ]
    }
    
    # Тестируем создание PDF
    pdf_path = generate_simple_pdf(test_data)
    if pdf_path:
        print(f"Тестовый PDF создан успешно: {pdf_path}")
    else:
        print("Ошибка при создании тестового PDF")