"""
Сервис для генерации PDF-документов с использованием ReportLab.
"""
import os
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

# Настройка логирования
logger = logging.getLogger(__name__)

# Регистрация русских шрифтов (при наличии)
try:
    FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts')
    os.makedirs(FONT_DIR, exist_ok=True)
    
    font_files = {
        'Arial': 'DejaVuSans.ttf',
        'ArialBold': 'DejaVuSans-Bold.ttf',
        'ArialItalic': 'DejaVuSansCondensed-Oblique.ttf',
        'ArialBoldItalic': 'DejaVuSansCondensed-Bold.ttf',
    }
    
    fonts_registered = False
    for font_name, font_file in font_files.items():
        font_path = os.path.join(FONT_DIR, font_file)
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            fonts_registered = True
        else:
            logger.warning(f"Шрифт {font_file} не найден по пути {font_path}")
    
    if fonts_registered:
        logger.info("Шрифты для PDF успешно зарегистрированы")
    else:
        logger.warning("Ни один шрифт не был зарегистрирован. PDF будет использовать стандартные шрифты.")
except Exception as e:
    logger.error(f"Ошибка при регистрации шрифтов: {str(e)}")

class PDFGenerator:
    """Базовый класс генератора PDF."""
    
    def generate(self, data):
        """
        Генерирует PDF на основе данных.
        
        Args:
            data (dict): Данные для генерации PDF
            
        Returns:
            str: Путь к сгенерированному PDF-файлу
        """
        raise NotImplementedError("Subclasses must implement generate()")


class StandardPDFGenerator(PDFGenerator):
    """Стандартный генератор PDF для коммерческих предложений по перголам."""
    
    def generate(self, data):
        """
        Генерирует PDF с коммерческим предложением по перголе.
        
        Args:
            data (dict): Данные для генерации PDF
            
        Returns:
            str: Путь к сгенерированному PDF-файлу
        """
        try:
            # Получение данных
            pergola_type = data.get('pergola_type', 'B500NEW')
            width = data.get('width', 3.0)
            length = data.get('length', 4.0)
            modules = data.get('modules', 1)
            items = data.get('items', [])
            total_price = data.get('total_price', 0)
            discount = data.get('discount', 0)
            total_after_discount = data.get('total_price_after_discount', 0)
            
            # Генерация имени файла
            today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"КП_пергола_{pergola_type}_{width}x{length}м_{today}.pdf"
            pdf_dir = current_app.config['PDF_FOLDER']
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Создание PDF
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width_mm, height_mm = A4[0] / mm, A4[1] / mm
            
            # Добавление заголовка
            font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            font_name_bold = 'ArialBold' if 'ArialBold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
            
            c.setFont(font_name_bold, 16)
            c.drawCentredString(width_mm * mm / 2, height_mm * mm - 30, "Коммерческое предложение")
            c.drawCentredString(width_mm * mm / 2, height_mm * mm - 50, f"Пергола {pergola_type}")
            
            # Добавление информации о перголе
            c.setFont(font_name, 12)
            y_position = height_mm * mm - 80
            
            c.drawString(30, y_position, f"Размеры: {width} x {length} м")
            y_position -= 20
            c.drawString(30, y_position, f"Количество модулей: {modules}")
            y_position -= 40
            
            # Добавление таблицы с опциями
            c.setFont(font_name_bold, 14)
            c.drawString(30, y_position, "Комплектация:")
            y_position -= 30
            
            # Создание данных для таблицы
            table_data = [['Наименование', 'Количество', 'Цена, руб.']]
            for item in items:
                name = item.get('name', '')
                quantity = item.get('quantity', '')
                price = item.get('price', 0)
                table_data.append([name, str(quantity), f"{price:,.0f}".replace(',', ' ')])
            
            # Добавление итогов
            table_data.append(['', '', ''])
            table_data.append(['', 'Итого:', f"{total_price:,.0f}".replace(',', ' ')])
            
            if discount > 0:
                discount_amount = total_price - total_after_discount
                table_data.append(['', f'Скидка {discount}%:', f"-{discount_amount:,.0f}".replace(',', ' ')])
                table_data.append(['', 'Итого со скидкой:', f"{total_after_discount:,.0f}".replace(',', ' ')])
            
            # Создание и стилизация таблицы
            col_widths = [270, 100, 100]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), font_name_bold, 12),
                ('FONT', (0, 1), (-1, -1), font_name, 11),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
                ('FONT', (1, -3), (-1, -1), font_name_bold, 11),
            ]))
            
            # Отрисовка таблицы
            table.wrapOn(c, 30, 0)
            table.drawOn(c, 30, y_position - 20 * len(table_data))
            
            # Добавление даты и комментария
            y_position = 80
            c.setFont(font_name, 10)
            c.drawString(30, y_position, f"Коммерческое предложение действительно в течение 30 дней.")
            y_position -= 20
            c.drawString(30, y_position, f"Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
            y_position -= 20
            c.drawString(30, y_position, "Для уточнения деталей и оформления заказа свяжитесь с нами.")
            
            # Сохранение PDF
            c.save()
            logger.info(f"PDF успешно создан по пути: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании PDF: {str(e)}", exc_info=True)
            return None


class SimplePDFGenerator(PDFGenerator):
    """Упрощенный генератор PDF без поддержки кириллицы."""
    
    def generate(self, data):
        """
        Генерирует упрощенный PDF с коммерческим предложением на латинице.
        
        Args:
            data (dict): Данные для генерации PDF
            
        Returns:
            str: Путь к сгенерированному PDF-файлу
        """
        try:
            # Получение данных
            pergola_type = data.get('pergola_type', 'B500NEW')
            width = data.get('width', 3.0)
            length = data.get('length', 4.0)
            modules = data.get('modules', 1)
            items = data.get('items', [])
            total_price = data.get('total_price', 0)
            discount = data.get('discount', 0)
            total_after_discount = data.get('total_price_after_discount', 0)
            
            # Генерация имени файла
            today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"KP_pergola_{pergola_type}_{width}x{length}m_{today}.pdf"
            pdf_dir = current_app.config['PDF_FOLDER']
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Создание PDF
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width_mm, height_mm = A4[0] / mm, A4[1] / mm
            
            # Добавление заголовка
            c.setFont('Helvetica-Bold', 16)
            c.drawCentredString(width_mm * mm / 2, height_mm * mm - 30, "Commercial Offer")
            c.drawCentredString(width_mm * mm / 2, height_mm * mm - 50, f"Pergola {pergola_type}")
            
            # Добавление информации о перголе
            c.setFont('Helvetica', 12)
            y_position = height_mm * mm - 80
            
            c.drawString(30, y_position, f"Dimensions: {width} x {length} m")
            y_position -= 20
            c.drawString(30, y_position, f"Modules: {modules}")
            y_position -= 40
            
            # Добавление таблицы с опциями
            c.setFont('Helvetica-Bold', 14)
            c.drawString(30, y_position, "Options:")
            y_position -= 30
            
            # Создание данных для таблицы
            table_data = [['Item', 'Quantity', 'Price, RUB']]
            for item in items:
                name = item.get('name', '').replace('Пергола', 'Pergola').replace('Привод', 'Drive')
                name = name.replace('Пульт управления', 'Remote Control')
                name = name.replace('Датчик дождя', 'Rain Sensor').replace('Датчик ветра', 'Wind Sensor')
                name = name.replace('Дополнительные колонны', 'Additional Columns')
                name = name.replace('Усилитель лотка', 'Gutter Reinforcement')
                name = name.replace('Светодиодная подсветка', 'LED Lighting')
                name = name.replace('ламели', 'lamellas').replace('лотка', 'gutters').replace('модуль/-я/-ей', 'modules')
                
                quantity = item.get('quantity', '')
                if isinstance(quantity, str):
                    quantity = quantity.replace('м', 'm').replace('шт', 'pcs')
                
                price = item.get('price', 0)
                table_data.append([name, str(quantity), f"{price:,.0f}".replace(',', ' ')])
            
            # Добавление итогов
            table_data.append(['', '', ''])
            table_data.append(['', 'Total:', f"{total_price:,.0f}".replace(',', ' ')])
            
            if discount > 0:
                discount_amount = total_price - total_after_discount
                table_data.append(['', f'Discount {discount}%:', f"-{discount_amount:,.0f}".replace(',', ' ')])
                table_data.append(['', 'Final price:', f"{total_after_discount:,.0f}".replace(',', ' ')])
            
            # Создание и стилизация таблицы
            col_widths = [270, 100, 100]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 11),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
                ('FONT', (1, -3), (-1, -1), 'Helvetica-Bold', 11),
            ]))
            
            # Отрисовка таблицы
            table.wrapOn(c, 30, 0)
            table.drawOn(c, 30, y_position - 20 * len(table_data))
            
            # Добавление даты и комментария
            y_position = 80
            c.setFont('Helvetica', 10)
            c.drawString(30, y_position, f"This offer is valid for 30 days.")
            y_position -= 20
            c.drawString(30, y_position, f"Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
            y_position -= 20
            c.drawString(30, y_position, "Contact us for details and ordering.")
            
            # Сохранение PDF
            c.save()
            logger.info(f"Simple PDF created successfully at: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error creating simple PDF: {str(e)}", exc_info=True)
            return None


class PDFGeneratorFactory:
    """Фабрика для создания генераторов PDF."""
    
    @staticmethod
    def get_generator(generator_type='standard'):
        """
        Возвращает подходящий генератор PDF.
        
        Args:
            generator_type (str): Тип генератора ('standard', 'simple')
            
        Returns:
            PDFGenerator: Генератор PDF
        """
        if generator_type == 'simple':
            return SimplePDFGenerator()
        else:
            return StandardPDFGenerator()


def generate_pdf(data, generator_type='standard', fallback=True):
    """
    Основная функция для генерации PDF с резервным генератором.
    
    Args:
        data (dict): Данные для генерации PDF
        generator_type (str): Тип генератора ('standard', 'simple')
        fallback (bool): Использовать запасной генератор при ошибке
        
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    try:
        # Получение основного генератора
        generator = PDFGeneratorFactory.get_generator(generator_type)
        
        # Попытка создания PDF
        start_time = time.time()
        pdf_path = generator.generate(data)
        elapsed_time = time.time() - start_time
        
        # Проверка результата
        if pdf_path and os.path.exists(pdf_path):
            logger.info(f"PDF успешно создан за {elapsed_time:.2f} сек: {pdf_path}")
            return pdf_path
        else:
            logger.error(f"Не удалось создать PDF с помощью {generator_type} генератора")
            
            # Использование запасного генератора, если разрешено
            if fallback and generator_type != 'simple':
                logger.info("Попытка создания PDF с помощью запасного (simple) генератора")
                return generate_pdf(data, generator_type='simple', fallback=False)
            
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: {str(e)}", exc_info=True)
        
        # Использование запасного генератора, если разрешено
        if fallback and generator_type != 'simple':
            logger.info("Попытка создания PDF с помощью запасного (simple) генератора")
            return generate_pdf(data, generator_type='simple', fallback=False)
        
        return None