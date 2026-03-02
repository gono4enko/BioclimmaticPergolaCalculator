"""
Сервис для генерации PDF-документов с использованием ReportLab.
"""
import os
import io
import time
import datetime
import logging
from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

try:
    FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts')
    os.makedirs(FONT_DIR, exist_ok=True)
    
    font_files = {
        'Arial': 'DejaVuSans.ttf',
        'ArialBold': 'DejaVuSans-Bold.ttf',
    }
    
    fonts_registered = False
    for font_name, font_file in font_files.items():
        font_path = os.path.join(FONT_DIR, font_file)
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            fonts_registered = True
    
    if fonts_registered:
        logger.info("Шрифты для PDF успешно зарегистрированы")
except Exception as e:
    logger.error(f"Ошибка при регистрации шрифтов: {str(e)}")


def generate_pdf(data):
    """
    Генерирует PDF коммерческого предложения и возвращает байты.
    
    Args:
        data (dict): Данные для генерации PDF
        
    Returns:
        bytes: PDF-документ в виде байтов (или None при ошибке)
    """
    try:
        pergola_type = data.get('pergola_type', 'B500NEW')
        width = data.get('width', 3.0)
        length = data.get('length', 4.0)
        modules = data.get('modules', 1)
        items = data.get('items', [])
        total_price = data.get('total_price', 0)
        discount = data.get('discount', 0)
        total_after_discount = data.get('total_price_after_discount', 0)
        
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        page_w, page_h = A4
        
        font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'ArialBold' if 'ArialBold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        
        c.setFont(font_bold, 16)
        c.drawCentredString(page_w / 2, page_h - 30, "Коммерческое предложение")
        c.drawCentredString(page_w / 2, page_h - 50, f"Пергола {pergola_type}")
        
        c.setFont(font_name, 12)
        y = page_h - 80
        c.drawString(30, y, f"Размеры: {width} x {length} м")
        y -= 20
        c.drawString(30, y, f"Количество модулей: {modules}")
        y -= 40
        
        c.setFont(font_bold, 14)
        c.drawString(30, y, "Комплектация:")
        y -= 30
        
        table_data = [['Наименование', 'Количество', 'Цена, руб.']]
        for item in items:
            name = item.get('name', '')
            quantity = item.get('quantity', '')
            price = item.get('price', 0)
            table_data.append([name, str(quantity), f"{price:,.0f}".replace(',', ' ')])
        
        table_data.append(['', '', ''])
        table_data.append(['', 'Итого:', f"{total_price:,.0f}".replace(',', ' ')])
        
        if discount > 0:
            discount_amount = total_price - total_after_discount
            table_data.append(['', f'Скидка {discount}%:', f"-{discount_amount:,.0f}".replace(',', ' ')])
            table_data.append(['', 'Итого со скидкой:', f"{total_after_discount:,.0f}".replace(',', ' ')])
        
        col_widths = [270, 100, 100]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), font_bold, 12),
            ('FONT', (0, 1), (-1, -1), font_name, 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        table.wrapOn(c, 30, 0)
        table.drawOn(c, 30, y - 20 * len(table_data))
        
        y = 80
        c.setFont(font_name, 10)
        c.drawString(30, y, "Коммерческое предложение действительно в течение 30 дней.")
        y -= 20
        c.drawString(30, y, f"Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        c.save()
        pdf_bytes = buf.getvalue()
        logger.info(f"PDF создан в памяти ({len(pdf_bytes)} байт)")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {str(e)}", exc_info=True)
        return None
