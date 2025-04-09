"""
Модуль для генерации коммерческого предложения в формате PDF
на основе данных из калькулятора перголы.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Создаем директорию для сохранения сгенерированных PDF
os.makedirs("generated_pdf", exist_ok=True)

# Регистрируем шрифты для поддержки кириллицы
# По умолчанию используем стандартный шрифт Helvetica
# В будущем можно добавить поддержку кастомных шрифтов

def generate_commercial_offer(pergola_data, user_data=None):
    """
    Генерирует коммерческое предложение в формате PDF на основе 
    данных о перголе, полученных из калькулятора.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе, ее размерах, конфигурации и стоимости
        user_data (dict, optional): Словарь с данными пользователя (имя, телефон и т.д.)
        
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    # Создаем уникальное имя файла на основе текущей даты и времени
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # Форматируем текущую дату для отображения в документе
    current_date = now.strftime("%d.%m.%Y")
    
    # Определяем путь для сохранения файла
    if user_data and user_data.get('phone'):
        # Если есть телефон, используем его в имени файла (без специальных символов)
        phone = ''.join(filter(str.isdigit, user_data['phone']))
        pdf_filename = f"generated_pdf/KP_Pergola_{phone}_{timestamp}.pdf"
    else:
        pdf_filename = f"generated_pdf/KP_Pergola_{timestamp}.pdf"
    
    # Настройка документа и его размеров
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Получаем базовые стили
    styles = getSampleStyleSheet()
    
    # Создаем пользовательские стили, используя разные имена
    styles.add(ParagraphStyle(
        name='KPTitle', 
        parent=styles['Heading1'], 
        fontSize=16, 
        alignment=1,  # по центру
        spaceAfter=10*mm
    ))
    
    styles.add(ParagraphStyle(
        name='KPSubtitle', 
        parent=styles['Heading2'], 
        fontSize=14, 
        alignment=1,  # по центру
        spaceAfter=6*mm
    ))
    
    styles.add(ParagraphStyle(
        name='SmallText', 
        parent=styles['Normal'], 
        fontSize=8,
        alignment=0  # по левому краю
    ))
    
    styles.add(ParagraphStyle(
        name='TableHeader', 
        parent=styles['Normal'], 
        fontSize=10,
        alignment=1,  # по центру
        textColor=colors.white
    ))
    
    styles.add(ParagraphStyle(
        name='TableCell', 
        parent=styles['Normal'], 
        fontSize=10,
        alignment=0  # по левому краю
    ))
    
    styles.add(ParagraphStyle(
        name='Footer', 
        parent=styles['Normal'], 
        fontSize=9,
        alignment=1,  # по центру
        textColor=colors.gray
    ))
    
    # Список элементов, которые будут добавлены в PDF
    elements = []
    
    # Добавляем шапку с логотипом компании
    # Ключевые реквизиты организации
    try:
        logo_path = "attached_assets/IMG_1030.jpeg"
        logo = Image(logo_path, width=17*cm, height=4*cm)
        elements.append(logo)
    except Exception as e:
        # Если не удалось загрузить логотип, добавляем текстовую шапку
        elements.append(Paragraph("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", styles['KPTitle']))
        elements.append(Paragraph("ООО 'Комфортный дом'", styles['KPSubtitle']))
        elements.append(Paragraph("ИНН/КПП: XXXXXXXXXX / YYYYYYYYY", styles['SmallText']))
        elements.append(Paragraph("Адрес: г. Москва, ул. Примерная, д. 123", styles['SmallText']))
        elements.append(Paragraph("Телефон: +7 (XXX) XXX-XX-XX", styles['SmallText']))
        elements.append(Paragraph("Email: info@example.com", styles['SmallText']))
    
    # Добавляем дату и номер коммерческого предложения
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"Дата: {current_date}", styles['Normal']))
    elements.append(Paragraph(f"Коммерческое предложение № КП-{timestamp[:8]}", styles['Normal']))
    
    # Добавляем информацию о клиенте, если она доступна
    if user_data:
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("Информация о клиенте:", styles['Heading3']))
        
        if user_data.get('name'):
            elements.append(Paragraph(f"Имя: {user_data['name']}", styles['Normal']))
        
        if user_data.get('phone'):
            elements.append(Paragraph(f"Телефон: {user_data['phone']}", styles['Normal']))
        
        if user_data.get('email'):
            elements.append(Paragraph(f"Email: {user_data['email']}", styles['Normal']))
    
    # Добавляем заголовок коммерческого предложения
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", styles['KPTitle']))
    elements.append(Paragraph("на поставку и монтаж биоклиматической перголы", styles['KPSubtitle']))
    
    # Добавляем информацию о выбранной конфигурации перголы
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("Параметры перголы:", styles['Heading3']))
    
    # Извлекаем данные о перголе из словаря
    pergola_type = pergola_data.get('pergola_type', '')
    width = pergola_data.get('width', 0)
    length = pergola_data.get('length', 0)
    lamella_type = pergola_data.get('lamella_type', '')
    modules = pergola_data.get('modules', 1)
    
    # Создаем таблицу с основными параметрами перголы
    data = [
        ["Параметр", "Значение"],
        ["Модель перголы", pergola_type],
        ["Ширина", f"{width} м"],
        ["Вынос (длина)", f"{length} м"],
        ["Тип ламелей", lamella_type],
        ["Количество модулей", str(modules)]
    ]
    
    # Если есть опции, добавляем их в таблицу
    options = pergola_data.get('options', {})
    if options:
        if 'lighting_type' in options and options['lighting_type'] != 'none':
            data.append(["Тип освещения", options['lighting_type']])
        if options.get('installation', False):
            data.append(["Установка", "Включена"])
        if options.get('delivery', False):
            data.append(["Доставка", "Включена"])
    
    # Создаем таблицу с параметрами
    parameters_table = Table(data, colWidths=[8*cm, 8*cm])
    parameters_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, 1), (1, -1), colors.white),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (1, -1), 5),
        ('RIGHTPADDING', (0, 0), (1, -1), 5),
    ]))
    
    elements.append(parameters_table)
    elements.append(Spacer(1, 10*mm))
    
    # Добавляем спецификацию перголы
    elements.append(Paragraph("Спецификация перголы:", styles['Heading3']))
    
    # Получаем данные о спецификации
    specification = pergola_data.get('specification', [])
    
    if specification:
        # Формируем данные для таблицы спецификации
        spec_data = [["№", "Наименование", "Количество"]]
        for i, item in enumerate(specification, 1):
            spec_data.append([str(i), item['name'], str(item['quantity'])])
        
        # Создаем таблицу спецификации
        spec_table = Table(spec_data, colWidths=[1.5*cm, 12*cm, 2.5*cm])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (2, 0), 12),
            ('BOTTOMPADDING', (0, 0), (2, 0), 8),
            ('BACKGROUND', (0, 1), (2, -1), colors.white),
            ('GRID', (0, 0), (2, -1), 1, colors.black),
            ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (2, -1), 5),
            ('RIGHTPADDING', (0, 0), (2, -1), 5),
        ]))
        
        elements.append(spec_table)
    else:
        elements.append(Paragraph("Данные о спецификации отсутствуют", styles['Normal']))
    
    elements.append(Spacer(1, 10*mm))
    
    # Добавляем информацию о стоимости
    elements.append(Paragraph("Стоимость:", styles['Heading3']))
    
    # Получаем данные о стоимости
    cost_items = pergola_data.get('cost_items', [])
    total_cost = pergola_data.get('total_cost', 0)
    
    if cost_items:
        # Формируем данные для таблицы стоимости
        cost_data = [["№", "Наименование", "Стоимость (₽)"]]
        for i, item in enumerate(cost_items, 1):
            cost_data.append([str(i), item['name'], f"{item['price']:,.2f}".replace(',', ' ')])
        
        # Добавляем итоговую строку
        cost_data.append(["", "ИТОГО:", f"{total_cost:,.2f}".replace(',', ' ')])
        
        # Создаем таблицу стоимости
        cost_table = Table(cost_data, colWidths=[1.5*cm, 12*cm, 2.5*cm])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (2, 0), 12),
            ('BOTTOMPADDING', (0, 0), (2, 0), 8),
            ('BACKGROUND', (0, 1), (2, -2), colors.white),
            ('BACKGROUND', (0, -1), (2, -1), colors.lightgrey),
            ('GRID', (0, 0), (2, -1), 1, colors.black),
            ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (2, -1), 'Helvetica-Bold'),
            ('LEFTPADDING', (0, 0), (2, -1), 5),
            ('RIGHTPADDING', (0, 0), (2, -1), 5),
        ]))
        
        elements.append(cost_table)
    else:
        elements.append(Paragraph("Данные о стоимости отсутствуют", styles['Normal']))
    
    # Добавляем описание перголы
    elements.append(PageBreak())  # Переход на новую страницу
    elements.append(Paragraph("Описание перголы:", styles['Heading3']))
    
    # Получаем описание перголы
    pergola_description = pergola_data.get('description', '')
    
    if pergola_description:
        # Добавляем описание перголы с учетом HTML-форматирования
        elements.append(Paragraph(pergola_description, styles['Normal']))
    else:
        elements.append(Paragraph("Описание перголы отсутствует", styles['Normal']))
    
    # Добавляем изображение перголы, если оно доступно
    pergola_image = pergola_data.get('image_path', '')
    if pergola_image and os.path.exists(pergola_image):
        try:
            elements.append(Spacer(1, 10*mm))
            img = Image(pergola_image, width=15*cm, height=10*cm)
            elements.append(img)
        except Exception as e:
            pass
    
    # Добавляем условия коммерческого предложения
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("Условия коммерческого предложения:", styles['Heading3']))
    
    conditions = [
        "Срок действия коммерческого предложения: 14 календарных дней с даты выдачи",
        "Срок изготовления перголы: 30-45 рабочих дней с момента подтверждения заказа",
        "Гарантия на конструкцию и механизмы: 5 лет",
        "Гарантия на комплектующие и электрику: 2 года",
        "Условия оплаты: 70% предоплата, 30% после монтажа"
    ]
    
    list_items = []
    for item in conditions:
        list_items.append(ListItem(Paragraph(item, styles['Normal'])))
    
    elements.append(ListFlowable(list_items, bulletType='bullet', start=None))
    
    # Добавляем контактную информацию
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("Контактная информация:", styles['Heading3']))
    elements.append(Paragraph("Телефон: +7 (XXX) XXX-XX-XX", styles['Normal']))
    elements.append(Paragraph("Email: info@example.com", styles['Normal']))
    elements.append(Paragraph("Сайт: www.example.com", styles['Normal']))
    
    # Добавляем подпись
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph("С уважением,", styles['Normal']))
    elements.append(Paragraph("Генеральный директор ООО 'Комфортный дом'", styles['Normal']))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("________________ / Иванов И.И. /", styles['Normal']))
    
    # Добавляем подвал с информацией о компании
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph("© 2025 Комфортный дом | Все права защищены", styles['Footer']))
    
    # Собираем PDF
    doc.build(elements)
    
    return pdf_filename

def format_pergola_data_for_pdf(results, options, dimensions, pergola_description):
    """
    Форматирует данные расчета перголы для использования в генерации PDF
    
    Args:
        results (dict): Результаты расчета перголы
        options (dict): Выбранные опции
        dimensions (dict): Размеры перголы
        pergola_description (str): Описание перголы (HTML)
        
    Returns:
        dict: Отформатированные данные для генерации PDF
    """
    # Получаем константы из приложения
    EURO_RATE = 110  # Курс евро
    
    # Извлекаем тип перголы из опций
    pergola_type = options.get('pergola_type', '')
    
    pdf_data = {
        'pergola_type': pergola_type,
        'width': dimensions.get('width', 0),
        'length': dimensions.get('length', 0),
        'lamella_type': options.get('lamella_type', ''),
        'modules': dimensions.get('modules', 1),
        'options': options,
        'total_cost': results.get('total_price', 0) * EURO_RATE,  # Конвертируем в рубли
        'description': pergola_description,
    }
    
    # Форматируем спецификацию
    specification = []
    if 'specification' in results:
        for item in results['specification']:
            specification.append({
                'name': item.get('name', ''),
                'quantity': item.get('count', 0)
            })
    pdf_data['specification'] = specification
    
    # Форматируем стоимость
    cost_items = []
    if 'items' in results:
        for item in results['items']:
            cost_items.append({
                'name': item.get('name', ''),
                'price': item.get('price', 0) * EURO_RATE  # Конвертируем в рубли
            })
    pdf_data['cost_items'] = cost_items
    
    # Добавляем путь к изображению перголы, если такое имеется
    if pergola_type == 'B500NEW':
        pdf_data['image_path'] = "attached_assets/b500_rotation.png"
    elif pergola_type == 'B700NEW':
        pdf_data['image_path'] = "attached_assets/b700_sliding.png"
    elif pergola_type == 'B600':
        pdf_data['image_path'] = "attached_assets/b600_sandwich.png"
    
    return pdf_data