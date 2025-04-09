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
# Использование стандартного шрифта Helvetica не подходит для кириллицы
# Необходимо установить и зарегистрировать шрифт с поддержкой кириллицы
import os.path

# Создаем директорию для шрифтов, если не существует
os.makedirs("fonts", exist_ok=True)

# Проверяем доступные шрифты
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Для Linux
    "/usr/share/fonts/TTF/DejaVuSans.ttf",              # Для некоторых дистрибутивов Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Liberation Sans
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",  # FreeSans
    "C:/Windows/Fonts/Arial.ttf",                      # Для Windows
    "/Library/Fonts/Arial Unicode.ttf",                # Для MacOS
    "arial.ttf",                                       # Относительный путь
    "DejaVuSans.ttf",                                  # Относительный путь
]

# Регистрируем основной шрифт и жирный вариант
font_found = False
for font_path in font_paths:
    if os.path.exists(font_path):
        # Копируем шрифт в локальную директорию для надежности
        import shutil
        local_font_path = "fonts/main_font.ttf"
        try:
            shutil.copy(font_path, local_font_path)
            # Регистрируем шрифт с поддержкой кириллицы
            pdfmetrics.registerFont(TTFont('CustomFont', local_font_path))
            # Регистрируем шрифт как семейство для поддержки жирного и наклонного начертания
            pdfmetrics.registerFontFamily(
                'CustomFont',
                normal='CustomFont',
                bold='CustomFont',
                italic='CustomFont',
                boldItalic='CustomFont'
            )
            font_found = True
            print(f"Зарегистрирован шрифт с поддержкой кириллицы из: {font_path}")
            break
        except Exception as e:
            print(f"Ошибка при копировании/регистрации шрифта {font_path}: {str(e)}")

# Если шрифт не найден, пробуем зарегистрировать непосредственно системный шрифт
if not font_found:
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                pdfmetrics.registerFontFamily(
                    'CustomFont',
                    normal='CustomFont',
                    bold='CustomFont',
                    italic='CustomFont',
                    boldItalic='CustomFont'
                )
                font_found = True
                print(f"Зарегистрирован системный шрифт: {font_path}")
                break
            except Exception as e:
                print(f"Ошибка при регистрации шрифта {font_path}: {str(e)}")

# Если всё еще не найден шрифт, выводим предупреждение
if not font_found:
    print("ВНИМАНИЕ: Не найден подходящий шрифт с поддержкой кириллицы!")
    print("Будет использован запасной вариант, но возможны проблемы с отображением.")
    
    # Создаем фиктивный шрифт в качестве запасного варианта
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    pdfmetrics.registerFont(TTFont('CustomFont', "Helvetica"))
    pdfmetrics.registerFontFamily(
        'CustomFont',
        normal='Helvetica',
        bold='Helvetica-Bold',
        italic='Helvetica-Oblique',
        boldItalic='Helvetica-BoldOblique'
    )

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
    
    # Получаем базовые стили и переопределяем их для поддержки кириллицы
    styles = getSampleStyleSheet()
    
    # Переопределяем базовые стили для использования нашего шрифта
    for style_name in styles.byName:
        style = styles[style_name]
        style.fontName = 'CustomFont'
    
    # Создаем пользовательские стили, используя разные имена
    styles.add(ParagraphStyle(
        name='KPTitle', 
        parent=styles['Heading1'],
        fontName='CustomFont', 
        fontSize=16, 
        alignment=1,  # по центру
        spaceAfter=10*mm
    ))
    
    styles.add(ParagraphStyle(
        name='KPSubtitle', 
        parent=styles['Heading2'],
        fontName='CustomFont', 
        fontSize=14, 
        alignment=1,  # по центру
        spaceAfter=6*mm
    ))
    
    styles.add(ParagraphStyle(
        name='SmallText', 
        parent=styles['Normal'],
        fontName='CustomFont', 
        fontSize=8,
        alignment=0  # по левому краю
    ))
    
    styles.add(ParagraphStyle(
        name='TableHeader', 
        parent=styles['Normal'],
        fontName='CustomFont', 
        fontSize=10,
        alignment=1,  # по центру
        textColor=colors.white
    ))
    
    styles.add(ParagraphStyle(
        name='TableCell', 
        parent=styles['Normal'],
        fontName='CustomFont', 
        fontSize=10,
        alignment=0  # по левому краю
    ))
    
    styles.add(ParagraphStyle(
        name='Footer', 
        parent=styles['Normal'],
        fontName='CustomFont', 
        fontSize=9,
        alignment=1,  # по центру
        textColor=colors.gray
    ))
    
    # Добавляем стиль для подзаголовков 4 уровня
    styles.add(ParagraphStyle(
        name='Heading4', 
        parent=styles['Heading3'],
        fontName='CustomFont', 
        fontSize=11,
        alignment=0,  # по левому краю
        textColor=colors.black
    ))
    
    # Список элементов, которые будут добавлены в PDF
    elements = []
    
    # Создаем текстовую шапку как в представленном скриншоте
    # Добавляем синюю плашку с текстом "Компания «Комфортный дом»"
    header_table = Table([["Компания «Комфортный дом»"]], colWidths=[18*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('ALIGNMENT', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'CustomFont'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('PADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('TOPPADDING', (0, 0), (0, 0), 10),
    ]))
    elements.append(header_table)
    
    # Добавляем счетчик страниц и другую информацию
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(f"1 из 4", styles['Normal']))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(f"г. Москва, {current_date}", styles['Normal']))
    
    # Добавляем номер коммерческого предложения
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"№ {timestamp[:8]}", styles['Normal']))
    
    # Добавляем заголовок коммерческого предложения
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", styles['KPTitle']))
    elements.append(Paragraph("на поставку и монтаж биоклиматической перголы", styles['KPSubtitle']))
    
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
        ('FONTNAME', (0, 0), (1, 0), 'CustomFont'),
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
            ('FONTNAME', (0, 0), (2, 0), 'CustomFont'),
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
            ('FONTNAME', (0, 0), (2, 0), 'CustomFont'),
            ('FONTSIZE', (0, 0), (2, 0), 12),
            ('BOTTOMPADDING', (0, 0), (2, 0), 8),
            ('BACKGROUND', (0, 1), (2, -2), colors.white),
            ('BACKGROUND', (0, -1), (2, -1), colors.lightgrey),
            ('GRID', (0, 0), (2, -1), 1, colors.black),
            ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (2, -1), 'CustomFont'),
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
    
    # Выводим для отладки
    print(f"Длина HTML-описания: {len(pergola_description)} символов")
    
    if pergola_description:
        # Улучшенная обработка HTML для корректного отображения всего текста
        import re
        from bs4 import BeautifulSoup
        
        # Добавляем серию заголовков о типах пергол для диагностики
        elements.append(Paragraph(f"Тип перголы: {pergola_data.get('pergola_type', 'Не указан')}", styles['Heading3']))
        
        # Используем комбинированный подход для максимальной надежности
        try:
            # Проверка и предварительная обработка HTML
            if not pergola_description.strip().startswith('<'):
                # Если это не HTML, просто добавляем как текст
                paragraphs = pergola_description.split('\n')
                for p in paragraphs:
                    if p.strip():
                        elements.append(Paragraph(p.strip(), styles['Normal']))
                        elements.append(Spacer(1, 3*mm))
            else:
                # Это HTML, используем BeautifulSoup
                soup = BeautifulSoup(pergola_description, 'html.parser')
                print(f"HTML-структура: {soup.prettify()[:200]}...")  # Печатаем начало структуры для диагностики
                
                # Извлекаем текст из всех заголовков (h1-h6)
                all_headers = []
                for i in range(1, 7):
                    headers = soup.find_all(f'h{i}')
                    for header in headers:
                        header_text = header.get_text().strip()
                        if header_text:
                            all_headers.append((i, header_text))  # Сохраняем уровень и текст
                
                # Извлекаем все блоки параграфов
                all_paragraphs = []
                paragraphs = soup.find_all(['p', 'div', 'span', 'li'])
                for p in paragraphs:
                    # Проверяем, что это не внутри заголовка
                    if not p.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        paragraph_text = p.get_text().strip()
                        if paragraph_text:
                            all_paragraphs.append(paragraph_text)
                
                # Выводим для отладки результаты парсинга
                print(f"Найдено заголовков: {len(all_headers)}")
                print(f"Найдено параграфов: {len(all_paragraphs)}")
                
                # Добавляем заголовки и параграфы в PDF
                if all_headers:
                    for level, header_text in all_headers:
                        style_name = 'Heading3' if level <= 3 else 'Heading4'
                        elements.append(Paragraph(header_text, styles[style_name]))
                        elements.append(Spacer(1, 3*mm))
                
                if all_paragraphs:
                    for paragraph_text in all_paragraphs:
                        elements.append(Paragraph(paragraph_text, styles['Normal']))
                        elements.append(Spacer(1, 3*mm))
                        
                # Если ничего не найдено, пробуем разобрать весь текст
                if not all_headers and not all_paragraphs:
                    full_text = soup.get_text().strip()
                    paragraphs = full_text.split('\n')
                    for p in paragraphs:
                        if p.strip():
                            elements.append(Paragraph(p.strip(), styles['Normal']))
                            elements.append(Spacer(1, 3*mm))
                
        except Exception as e:
            # Если произошла ошибка, используем простой метод разбора текста
            print(f"Ошибка при парсинге HTML: {str(e)}")
            
            # Просто разделяем текст по абзацам и добавляем каждый абзац
            try:
                # Удаляем все HTML-теги
                text_only = re.sub(r'<.*?>', ' ', pergola_description)
                # Нормализуем пробелы
                text_only = re.sub(r'\s+', ' ', text_only).strip()
                # Разбиваем на абзацы по точке или двойным пробелам
                paragraphs = re.split(r'\.(?:\s{2,}|\n+)', text_only)
                
                for p in paragraphs:
                    if p.strip():
                        elements.append(Paragraph(p.strip() + '.', styles['Normal']))
                        elements.append(Spacer(1, 3*mm))
            except Exception as e2:
                # В случае полного отказа, просто добавляем весь текст как есть
                print(f"Ошибка при простом парсинге: {str(e2)}")
                elements.append(Paragraph(pergola_description[:1000], styles['Normal']))
                if len(pergola_description) > 1000:
                    elements.append(Paragraph("...(текст слишком длинный)", styles['Normal']))
    else:
        elements.append(Paragraph("Описание перголы отсутствует", styles['Normal']))
    
    # Добавляем изображение перголы, если оно доступно
    pergola_image = pergola_data.get('image_path', '')
    if pergola_image and os.path.exists(pergola_image):
        try:
            elements.append(Spacer(1, 10*mm))
            
            # Вместо фиксированных размеров, сохраняем пропорции изображения
            # Получаем размеры изображения
            from PIL import Image as PILImage
            img_pil = PILImage.open(pergola_image)
            img_width, img_height = img_pil.size
            
            # Рассчитываем размеры с сохранением пропорций
            # Ограничиваем по ширине страницы (17 см), высота рассчитывается пропорционально
            max_width = 16*cm  # Немного уменьшим максимальную ширину
            
            # Важно: сначала вычисляем соотношение сторон
            aspect_ratio = img_height / float(img_width)
            
            # Устанавливаем ширину изображения
            width = max_width
            
            # Вычисляем высоту с учетом соотношения сторон
            height = width * aspect_ratio
            
            print(f"Размеры изображения: {img_width}x{img_height}, соотношение сторон: {aspect_ratio}")
            print(f"Размеры в PDF: {width/cm}x{height/cm} см")
            
            # Добавляем изображение с сохранением пропорций
            # Используем явно указанные width и height для гарантии сохранения пропорций
            img = Image(pergola_image)
            img.drawWidth = width
            img.drawHeight = height
            elements.append(img)
        except Exception as e:
            # Если не удалось обработать изображение через PIL, используем стандартный подход
            try:
                img = Image(pergola_image, width=15*cm)  # Указываем только ширину, высота будет пропорциональной
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(f"Не удалось загрузить изображение: {str(e)}", styles['Normal']))
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
    
    # Добавляем пути к изображениям перголы, использующиеся в UI
    # Проверяем наличие файлов из скриншотов в attached_assets
    if pergola_type == 'B500NEW':
        # Пробуем найти изображение B500 с вращением ламелей
        possible_paths = [
            "attached_assets/Снимок экрана 2025-04-09 в 22.44.59.png",
            "attached_assets/aluminum slats.png",
            "attached_assets/В500 со вращением ламелей.png",
            "attached_assets/b500_rotation.png"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    elif pergola_type == 'B700NEW':
        # Пробуем найти изображение B700 со сдвижением ламелей
        possible_paths = [
            "attached_assets/В700 со сдвижением ламелей.png",
            "attached_assets/b700_sliding.png"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    elif pergola_type == 'B600':
        # Пробуем найти изображение B600 с сэндвич панелями
        possible_paths = [
            "attached_assets/В600 с сэндвич панелями.png",
            "attached_assets/b600_sandwich.png"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    
    return pdf_data