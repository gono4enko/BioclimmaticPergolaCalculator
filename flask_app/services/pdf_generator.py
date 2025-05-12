"""
Сервис для генерации PDF файлов с коммерческими предложениями.
"""
import os
import time
import datetime
from flask import current_app
from fpdf import FPDF


class PergolaQuotePDF(FPDF):
    """
    Класс для создания PDF с коммерческим предложением на перголу.
    Расширяет базовый класс FPDF.
    """
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        # Приводим параметры к требуемым типам для FPDF
        super().__init__(orientation=('P' if orientation == 'P' else 'L'), 
                         unit=('mm' if unit == 'mm' else 'pt'), 
                         format=('A4' if format == 'A4' else 'A3'))
        # Используем стандартные шрифты вместо кастомных
        self.set_font('Helvetica')
        
    def header(self):
        """Верхний колонтитул с логотипом и заголовком."""
        # Логотип компании
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 50)
        
        # Заголовок
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, 'Коммерческое предложение', 0, 1, 'R')
        
        # Дата
        self.set_font('Helvetica', '', 10)
        today = datetime.datetime.now().strftime('%d.%m.%Y')
        self.cell(0, 10, f'Дата: {today}', 0, 1, 'R')
        
        # Линия под заголовком
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, 30, 200, 30)
        self.ln(10)
    
    def footer(self):
        """Нижний колонтитул с номером страницы."""
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(128, 128, 128)
        
        # Номер страницы
        self.cell(0, 10, f'Страница {self.page_no()}', 0, 0, 'C')
        
        # Контактная информация
        self.set_y(-10)
        self.cell(0, 10, 'Телефон: +7 (495) 123-45-67 | Email: info@pergola-calc.ru', 0, 0, 'C')


def generate_pdf(data):
    """
    Генерирует PDF файл с коммерческим предложением.
    
    Args:
        data (dict): Данные для генерации PDF
    
    Returns:
        str: Путь к сгенерированному PDF файлу
    """
    try:
        # Создаем экземпляр PDF
        pdf = PergolaQuotePDF()
        pdf.add_page()
        
        # Информация о клиенте (если есть)
        client_info = data.get('client_info', {})
        if client_info:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Данные клиента:', 0, 1)
            
            pdf.set_font('Helvetica', '', 10)
            for key, value in client_info.items():
                pdf.cell(0, 6, f'{key}: {value}', 0, 1)
            
            pdf.ln(5)
        
        # Информация о перголе
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Параметры перголы:', 0, 1)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, f'Тип перголы: {data.get("pergola_type", "")}', 0, 1)
        pdf.cell(0, 6, f'Размеры: {data.get("width", 0)} x {data.get("length", 0)} м', 0, 1)
        pdf.cell(0, 6, f'Количество модулей: {data.get("modules", 1)}', 0, 1)
        pdf.cell(0, 6, f'Размер ламелей: {data.get("lamella_size", "")} мм', 0, 1)
        
        # Опции
        options = data.get('options', {})
        if options:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Дополнительные опции:', 0, 1)
            
            pdf.set_font('Helvetica', '', 10)
            for key, value in options.items():
                if value:
                    pdf.cell(0, 6, f'✓ {key}', 0, 1)
        
        # Таблица с позициями и ценами
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Спецификация:', 0, 1)
        
        # Заголовки таблицы
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        
        col_width = [100, 30, 30]
        pdf.cell(col_width[0], 10, 'Наименование', 1, 0, 'C', True)
        pdf.cell(col_width[1], 10, 'Кол-во', 1, 0, 'C', True)
        pdf.cell(col_width[2], 10, 'Цена, ₽', 1, 1, 'C', True)
        
        # Строки таблицы
        pdf.set_font('Helvetica', '', 10)
        
        items = data.get('items', [])
        for item in items:
            # Разбиваем длинные названия на несколько строк
            name = item.get('name', '')
            quantity = item.get('quantity', '')
            price = item.get('price', 0)
            
            # Форматирование цены
            formatted_price = f"{int(price):,}".replace(',', ' ')
            
            pdf.cell(col_width[0], 8, name, 1, 0)
            pdf.cell(col_width[1], 8, str(quantity), 1, 0, 'C')
            pdf.cell(col_width[2], 8, formatted_price, 1, 1, 'R')
        
        # Итоговая стоимость
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        total_price = data.get('total_price', 0)
        formatted_total = f"{int(total_price):,}".replace(',', ' ')
        pdf.cell(130, 10, 'Итого:', 0, 0, 'R')
        pdf.cell(30, 10, f'{formatted_total} ₽', 0, 1, 'R')
        
        # Скидка
        discount = data.get('discount', 0)
        if discount > 0:
            # Если применена акция, выводим информацию о ней
            if data.get('promotion_applied', False):
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_text_color(255, 107, 0)  # Оранжевый цвет для акции
                pdf.cell(0, 8, f'Акция: {data.get("promotion_name", "Специальное предложение")}', 0, 1, 'R')
                pdf.set_text_color(0, 0, 0)  # Возвращаем черный цвет
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(130, 8, f'Скидка {discount}%:', 0, 0, 'R')
            
            total_after_discount = data.get('total_price_after_discount', 0)
            formatted_discount_price = f"{int(total_after_discount):,}".replace(',', ' ')
            pdf.cell(30, 8, f'{formatted_discount_price} ₽', 0, 1, 'R')
        
        # Условия и сроки
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Условия:', 0, 1)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, 'Срок изготовления: 4-6 недель с момента предоплаты\n'
                           'Гарантия: 3 года на конструкцию, 1 год на электронику\n'
                           'Условия оплаты: 70% предоплата, 30% по готовности к монтажу')
        
        # Генерация имени файла
        timestamp = int(time.time())
        filename = f"KP_Pergola_{timestamp}.pdf"
        
        # Сохранение PDF
        pdf_path = os.path.join(current_app.config['PDF_FOLDER'], filename)
        pdf.output(pdf_path)
        
        return pdf_path
    
    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        return None