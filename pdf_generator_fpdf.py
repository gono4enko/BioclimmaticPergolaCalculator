"""
Модуль для генерации коммерческого предложения в формате PDF
на основе данных из калькулятора перголы.
Использует библиотеку FPDF для корректной работы с кириллицей.
"""
import os
import io
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# Создаем директорию для сохранения сгенерированных PDF
os.makedirs("generated_pdf", exist_ok=True)

# Создаем директорию для обработанных изображений
os.makedirs("processed_images", exist_ok=True)

class PDF(FPDF):
    """
    Расширенный класс FPDF с поддержкой кириллицы и дополнительными функциями
    """
    def __init__(self):
        # Используем конкретные значения из перечисления литералов
        super().__init__(orientation='P', unit='mm', format='A4')
        
        # Добавляем шрифты с поддержкой кириллицы
        # Используем DejaVu шрифты, которые есть в директории fonts
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        
        # Устанавливаем мета-информацию PDF (только латиница)
        self.set_title("Commercial Offer")
        self.set_author("Pergola Calculator")
        self.set_creator("Pergola Calculator")
        
        # Устанавливаем отступы
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=20)
        
        # Счетчик страниц для колонтитула
        self.page_count = 0
        
    def header(self):
        """Создает верхний колонтитул на каждой странице"""
        self.page_count += 1
        # Добавляем синюю плашку с текстом 
        self.set_fill_color(63, 109, 170)  # Синий цвет #3f6daa
        self.set_text_color(255, 255, 255)  # Белый текст
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 15, "Comfortable Home Company", 0, 1, "C", fill=True)
        
        # Номер страницы
        self.set_text_color(0, 0, 0)  # Черный текст
        self.set_font("DejaVu", "", 10)
        self.cell(0, 5, f"Page {self.page_count} of 4", 0, 1, "L")
        
    def footer(self):
        """Создает нижний колонтитул на каждой странице"""
        self.set_y(-15)  # 15 мм от нижнего края
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(128, 128, 128)  # Серый текст
        self.cell(0, 10, "© 2025 Comfortable Home | All rights reserved", 0, 0, "C")
        
    def chapter_title(self, title):
        """Добавляет заголовок раздела"""
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(0, 0, 0)  # Черный текст
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(1)  # Небольшой отступ после заголовка
        
    def table_header(self, headers, widths):
        """Создает заголовок таблицы"""
        self.set_fill_color(173, 216, 230)  # Светло-голубой цвет
        self.set_text_color(255, 255, 255)  # Белый текст
        self.set_font("DejaVu", "B", 10)
        for i, header in enumerate(headers):
            self.cell(widths[i], 8, header, 1, 0, "C", fill=True)
        self.ln()
        
    def table_row(self, data, widths, aligns=None):
        """Добавляет строку в таблицу"""
        if aligns is None:
            aligns = ["L"] * len(data)
        self.set_text_color(0, 0, 0)  # Черный текст
        self.set_font("DejaVu", "", 10)
        for i, cell in enumerate(data):
            self.cell(widths[i], 8, str(cell), 1, 0, aligns[i])
        self.ln()


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
    # Очищаем временные файлы обработанных изображений
    for file in os.listdir("processed_images"):
        if file.startswith("proc_"):
            try:
                os.remove(os.path.join("processed_images", file))
            except:
                pass
    
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
    
    # Создаем экземпляр PDF с поддержкой кириллицы
    pdf = PDF()
    
    # Создаем директорию для шрифтов (если ее нет)
    os.makedirs('fonts', exist_ok=True)
    
    # Используем встроенные шрифты FPDF
    # DejaVu поддерживает кириллицу и используется вместо Arial
    
    # Указываем, что мы будем использовать шрифт DejaVu с поддержкой кириллицы
    pdf.set_font("DejaVu", '', 12)
    
    # Добавляем первую страницу
    pdf.add_page()
    
    # Устанавливаем информацию о текущей дате
    pdf.set_font("DejaVu", '', 10)
    pdf.cell(0, 5, f"Moscow, {current_date}", 0, 1, "L")
    
    # Добавляем номер коммерческого предложения
    pdf.ln(5)
    pdf.cell(0, 5, f"No. {timestamp[:8]}", 0, 1, "L")
    
    # Добавляем заголовок коммерческого предложения
    pdf.ln(10)
    pdf.set_font("DejaVu", 'B', 16)
    pdf.cell(0, 10, "COMMERCIAL OFFER", 0, 1, "C")
    pdf.set_font("DejaVu", '', 14)
    pdf.cell(0, 10, "for the supply and installation of a bioclimatic pergola", 0, 1, "C")
    
    # Добавляем информацию о клиенте, если она доступна
    if user_data:
        pdf.ln(5)
        pdf.chapter_title("Client Information:")
        
        pdf.set_font("DejaVu", '', 10)
        if user_data.get('name'):
            pdf.cell(0, 7, f"Name: {user_data['name']}", 0, 1)
        
        if user_data.get('phone'):
            pdf.cell(0, 7, f"Phone: {user_data['phone']}", 0, 1)
        
        if user_data.get('email'):
            pdf.cell(0, 7, f"Email: {user_data['email']}", 0, 1)
    
    # Добавляем информацию о выбранной конфигурации перголы
    pdf.ln(10)
    pdf.chapter_title("Pergola Parameters:")
    
    # Извлекаем данные о перголе из словаря
    pergola_type = pergola_data.get('pergola_type', '')
    width = pergola_data.get('width', 0)
    length = pergola_data.get('length', 0)
    lamella_type = pergola_data.get('lamella_type', '')
    modules = pergola_data.get('modules', 1)
    
    # Создаем таблицу с основными параметрами перголы
    headers = ["Parameter", "Value"]
    widths = [80, 80]  # Ширина колонок в мм
    
    pdf.table_header(headers, widths)
    
    pdf.table_row(["Pergola model", pergola_type], widths)
    pdf.table_row(["Width", f"{width} m"], widths)
    pdf.table_row(["Length", f"{length} m"], widths)
    pdf.table_row(["Lamella type", lamella_type], widths)
    pdf.table_row(["Modules count", str(modules)], widths)
    
    # Если есть опции, добавляем их в таблицу
    options = pergola_data.get('options', {})
    if options:
        if 'lighting_type' in options and options['lighting_type'] != 'none':
            pdf.table_row(["Lighting type", options['lighting_type']], widths)
        if options.get('installation', False):
            pdf.table_row(["Installation", "Included"], widths)
        if options.get('delivery', False):
            pdf.table_row(["Delivery", "Included"], widths)
    
    # Добавляем спецификацию перголы
    pdf.ln(10)
    pdf.chapter_title("Pergola Specification:")
    
    # Получаем данные о спецификации
    specification = pergola_data.get('specification', [])
    
    if specification:
        headers = ["#", "Description", "Quantity"]
        widths = [15, 120, 25]  # Ширина колонок в мм
        
        pdf.table_header(headers, widths)
        
        for i, item in enumerate(specification, 1):
            pdf.table_row([str(i), item['name'], str(item['quantity'])], widths, aligns=["C", "L", "C"])
    else:
        pdf.set_font("DejaVu", '', 10)
        pdf.cell(0, 7, "No specification data available", 0, 1)
    
    # Добавляем информацию о стоимости
    pdf.ln(10)
    pdf.chapter_title("Price Information:")
    
    # Получаем данные о стоимости
    cost_items = pergola_data.get('cost_items', [])
    total_cost = pergola_data.get('total_cost', 0)
    
    if cost_items:
        headers = ["#", "Item", "Price (₽)"]
        widths = [15, 120, 25]  # Ширина колонок в мм
        
        pdf.table_header(headers, widths)
        
        for i, item in enumerate(cost_items, 1):
            price_str = f"{item['price']:,.2f}".replace(',', ' ')
            pdf.table_row([str(i), item['name'], price_str], widths, aligns=["C", "L", "R"])
            
        # Добавляем итоговую строку
        pdf.set_fill_color(211, 211, 211)  # Светло-серый цвет
        pdf.set_font("DejaVu", 'B', 10)
        pdf.set_text_color(0, 0, 0)  # Черный текст
        total_price_str = f"{total_cost:,.2f}".replace(',', ' ')
        
        pdf.cell(15, 8, "", 1, 0, "C", fill=True)
        pdf.cell(120, 8, "TOTAL:", 1, 0, "R", fill=True)
        pdf.cell(25, 8, total_price_str, 1, 1, "R", fill=True)
    else:
        pdf.set_font("DejaVu", '', 10)
        pdf.cell(0, 7, "No pricing data available", 0, 1)
    
    # Добавляем описание перголы и дополнительные разделы
    pdf.add_page()
    pdf.chapter_title("Описание перголы:")
    
    # Получаем все описания и изображения
    pergola_description = pergola_data.get('description', '')
    modular_description = pergola_data.get('modular_description', '')
    drainage_description = pergola_data.get('drainage_description', '')
    drive_description = pergola_data.get('drive_description', '')
    
    # Составляем список всех описаний в нужном порядке
    all_descriptions = []
    
    # Сначала основное описание перголы
    if pergola_description:
        all_descriptions.append({
            'title': 'Основное описание',
            'content': pergola_description
        })
    
    # Затем описание модульной системы, если есть
    if modular_description:
        all_descriptions.append({
            'title': 'Модульная система',
            'content': modular_description
        })
    
    # Затем описание системы водоотведения, если есть
    if drainage_description:
        all_descriptions.append({
            'title': 'Система водоотведения',
            'content': drainage_description
        })
    
    # Наконец, описание привода, если есть
    if drive_description:
        drive_title = "Привод Bansbach" if "B500NEW" in pergola_data.get('pergola_type', '') else "Привод Somfy"
        all_descriptions.append({
            'title': drive_title,
            'content': drive_description
        })
    
    # Выводим для отладки
    print(f"Найдено {len(all_descriptions)} разделов описаний для PDF")
    
    # Если нет ни одного описания, добавляем базовое
    if not all_descriptions:
        pergola_type = pergola_data.get('pergola_type', 'биоклиматическая')
        print(f"Добавляем базовое описание для перголы типа {pergola_type}")
        
        basic_description = f"""
        <div style='padding: 0 20px;'>
        <h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Пергола {pergola_type}</h3>
        <p style='margin-bottom: 15px;'>
        Современная биоклиматическая пергола с автоматическим управлением. 
        Изготовлена из высококачественного алюминия с порошковой покраской.
        </p>
        <div style='margin-bottom: 15px;'>
        <strong>Преимущества:</strong><br/>
        • Защита от осадков и солнца<br/>
        • Регулируемое положение ламелей<br/>
        • Встроенная система водоотведения<br/>
        • Долговечные материалы<br/>
        • Простота использования
        </div>
        </div>
        """
        
        all_descriptions.append({
            'title': 'Описание перголы',
            'content': basic_description
        })
    
    # Обрабатываем каждое описание по очереди
    for section_index, section in enumerate(all_descriptions):
        section_title = section.get('title', '')
        section_content = section.get('content', '')
        
        # Пропускаем пустые секции
        if not section_content:
            continue
        
        # Добавляем подзаголовок секции, кроме первой (основной)
        if section_index > 0:
            pdf.ln(10)  # Отступ между секциями
            pdf.set_font("DejaVu", 'B', 12)
            pdf.cell(0, 8, section_title, 0, 1, 'L')
            pdf.ln(2)
        
        # HTML-описание нужно преобразовать в чистый текст
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(section_content, 'html.parser')
            
            # Обрабатываем изображения
            # Находим и удаляем изображения из HTML, они будут добавлены отдельно
            for img in soup.find_all('img'):
                img.extract()
            
            # Обрабатываем заголовки - делаем их крупнее и жирным шрифтом
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                heading_text = heading.get_text().strip()
                
                # Устанавливаем размер шрифта в зависимости от уровня заголовка
                header_size = 14 if heading.name == 'h1' else 12 if heading.name == 'h2' else 11
                
                pdf.set_font("DejaVu", 'B', header_size)
                # Добавляем отступ перед заголовком
                pdf.ln(5)
                # Выводим заголовок
                pdf.cell(0, 8, heading_text, 0, 1, 'C' if heading.name == 'h1' else 'L')
                pdf.ln(2)
                
                # Удаляем заголовок, чтобы не дублировать его в тексте
                heading.extract()
            
            # Обрабатываем параграфы текста
            for paragraph in soup.find_all('p'):
                paragraph_text = paragraph.get_text().strip()
                if paragraph_text:
                    pdf.set_font("DejaVu", '', 11)
                    
                    # Разбиваем текст на части, если он слишком длинный
                    if len(paragraph_text) > 200:
                        # Разбиваем длинные параграфы на части с учетом границ слов
                        parts = []
                        current_pos = 0
                        
                        while current_pos < len(paragraph_text):
                            # Если остался небольшой кусок текста
                            if current_pos + 200 >= len(paragraph_text):
                                parts.append(paragraph_text[current_pos:])
                                break
                            
                            # Ищем последний пробел до 200 символов
                            end_pos = current_pos + 200
                            while end_pos > current_pos and paragraph_text[end_pos] != ' ':
                                end_pos -= 1
                            
                            # Если пробела нет, делим просто по длине
                            if end_pos == current_pos:
                                end_pos = current_pos + 200
                            
                            parts.append(paragraph_text[current_pos:end_pos])
                            current_pos = end_pos + 1
                        
                        # Выводим части
                        for part in parts:
                            if part.strip():
                                pdf.multi_cell(0, 6, part.strip())
                    else:
                        # Короткий параграф выводим целиком
                        pdf.multi_cell(0, 6, paragraph_text)
                    
                    pdf.ln(3)  # Отступ после параграфа
            
            # Обрабатываем списки
            for ul in soup.find_all('ul'):
                pdf.ln(2)
                
                for li in ul.find_all('li'):
                    li_text = li.get_text().strip()
                    if li_text:
                        pdf.set_font("DejaVu", '', 11)
                        # Добавляем маркер списка
                        pdf.multi_cell(0, 6, f"• {li_text}")
                
                pdf.ln(2)
        except Exception as e:
            print(f"Ошибка при обработке HTML-описания секции {section_title}: {str(e)}")
            pdf.set_font("DejaVu", '', 10)
            pdf.multi_cell(0, 6, f"Ошибка при обработке описания. {str(e)}")
    
    # Добавляем страницу с изображениями
    pdf.add_page()
    pdf.chapter_title("Изображения перголы:")
    
    # Получаем список изображений
    images = pergola_data.get('images', [])
    image_captions = pergola_data.get('image_captions', {})
    default_caption = pergola_data.get('image_caption', 'Изображение перголы')
    
    # Проверяем, есть ли изображения в списке
    if images and len(images) > 0:
        # Обрабатываем каждое изображение
        for i, img_path in enumerate(images):
            if os.path.exists(img_path):
                try:
                    # Получаем подпись для этого изображения
                    caption = image_captions.get(img_path, default_caption)
                    if i > 0:
                        pdf.ln(15)  # Отступ между изображениями
                    
                    # Обрабатываем изображение перед добавлением
                    original_img = Image.open(img_path)
                    width, height = original_img.size
                    
                    # Определяем максимальную ширину (150 мм с учетом полей)
                    max_width_mm = 150  
                    # Пересчитываем в пикселях для определения масштаба
                    max_width_px = int(max_width_mm * 300 / 25.4)  # при 300 DPI
                    
                    # Вычисляем коэффициент масштабирования
                    scale = min(max_width_px / width, 1.0)
                    # Вычисляем новые размеры с сохранением пропорций
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    
                    # Проверяем, не слишком ли большое изображение для страницы
                    if pdf.get_y() + (new_height * 25.4 / 300) + 20 > 277:  # 277 мм - высота страницы A4 с отступами
                        pdf.add_page()
                    
                    # Добавляем подпись к изображению
                    pdf.set_font("DejaVu", 'B', 11)
                    pdf.cell(0, 8, f"{caption}", 0, 1, 'C')
                    pdf.ln(5)
                    
                    # Если нужно масштабировать, создаем временную копию
                    if scale < 1.0:
                        # Ресайзим изображение для PDF
                        resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        # Создаем временный файл для изображения
                        tmp_path = os.path.join("processed_images", f"tmp_{i}_{os.path.basename(img_path)}")
                        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                        resized_img.save(tmp_path)
                        
                        # Добавляем изображение в PDF, центрируя по ширине
                        pdf.image(
                            tmp_path, 
                            x=(210 - max_width_mm) / 2,  # центрируем по ширине A4 (210 мм)
                            w=max_width_mm
                        )
                        
                        # Удаляем временный файл
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
                    else:
                        # Добавляем оригинальное изображение, если оно не требует масштабирования
                        img_width_mm = width * 25.4 / 300
                        pdf.image(
                            img_path,
                            x=(210 - img_width_mm) / 2,  # центрируем
                            w=img_width_mm
                        )
                    
                    print(f"Добавлено изображение в PDF: {img_path}")
                except Exception as e:
                    print(f"Ошибка при обработке изображения {img_path}: {str(e)}")
                    pdf.set_font("DejaVu", '', 10)
                    pdf.cell(0, 7, f"Ошибка при добавлении изображения: {str(e)}", 0, 1)
    # Если в списке изображений нет, но есть прямая ссылка на изображение
    elif pergola_data.get('image_path'):
        image_path = pergola_data.get('image_path')
        if os.path.exists(image_path):
            try:
                # Добавляем подпись к изображению
                pdf.set_font("DejaVu", 'B', 11)
                pdf.cell(0, 8, default_caption, 0, 1, 'C')
                pdf.ln(5)
                
                # Обрабатываем изображение перед добавлением
                original_img = Image.open(image_path)
                width, height = original_img.size
                
                # Определяем максимальную ширину для изображения (160 мм, учитывая поля)
                max_width_mm = 160
                max_width_px = int(max_width_mm * 300 / 25.4)  # Преобразуем мм в пиксели при 300 DPI
                
                # Вычисляем новый размер с сохранением пропорций
                ratio = min(max_width_px / width, 1.0)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # Масштабируем изображение, если необходимо
                if ratio < 1.0:
                    resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Сохраняем обработанное изображение
                    img_name = os.path.basename(image_path)
                    processed_image_path = os.path.join("processed_images", f"resized_{img_name}")
                    os.makedirs(os.path.dirname(processed_image_path), exist_ok=True)
                    resized_img.save(processed_image_path)
                    
                    print(f"Размеры оригинального изображения: {width}x{height}")
                    print(f"Новые размеры изображения: {new_width}x{new_height} пикселей")
                    
                    # Центрируем изображение
                    pdf.image(
                        processed_image_path,
                        x=(210 - max_width_mm) / 2,  # центрируем
                        w=max_width_mm
                    )
                    print(f"Добавлено масштабированное изображение в PDF: {processed_image_path}")
                else:
                    # Добавляем оригинальное изображение без масштабирования
                    img_width_mm = width * 25.4 / 300
                    pdf.image(
                        image_path,
                        x=(210 - img_width_mm) / 2,  # центрируем
                        w=img_width_mm
                    )
                    print(f"Добавлено оригинальное изображение в PDF: {image_path}")
            except Exception as e:
                print(f"Ошибка при обработке изображения {image_path}: {str(e)}")
                pdf.set_font("DejaVu", '', 10)
                pdf.cell(0, 7, f"Ошибка при добавлении изображения: {str(e)}", 0, 1)
    else:
        # Если изображений нет вообще
        pdf.set_font("DejaVu", 'I', 10)
        pdf.cell(0, 10, "Изображения для данного типа перголы отсутствуют", 0, 1, 'C')
    
    # Добавляем контактную информацию
    pdf.add_page()
    pdf.chapter_title("Контактная информация:")
    
    pdf.set_font("DejaVu", '', 11)
    pdf.multi_cell(0, 6, "Для получения дополнительной информации или оформления заказа, свяжитесь с нами:")
    pdf.ln(5)
    
    contact_info = [
        "Телефон: +7 (495) 123-45-67",
        "Email: info@komfortnyj-dom.ru",
        "Веб-сайт: www.komfortnyj-dom.ru",
        "Адрес: г. Москва, ул. Примерная, д. 123"
    ]
    
    for info in contact_info:
        pdf.cell(0, 7, info, 0, 1)
    
    # Сохраняем PDF с поддержкой UTF-8
    try:
        # Создаем директорию для сохранения PDF
        os.makedirs(os.path.dirname(pdf_filename), exist_ok=True)
        
        # В FPDF встроенный метод output с dest='F' и кодировкой по умолчанию latin-1
        # Поскольку у нас кириллица, нам нужно создать полностью новый PDF без
        # русских символов, а затем добавить текстовую информацию транслитом
        
        # Try to save full PDF first
        pdf.output(pdf_filename, 'F')
        print(f"PDF successfully created: {pdf_filename}")
    except Exception as e:
        print(f"Ошибка при сохранении PDF: {str(e)}")
        
        try:
            # Создаем упрощенный PDF без кириллицы
            simple_pdf = FPDF()
            simple_pdf.add_page()
            simple_pdf.set_font("DejaVu", 'B', 14)
            simple_pdf.cell(0, 10, "Kalkulyator Pergol", 0, 1, 'C')
            simple_pdf.set_font("DejaVu", '', 12)
            
            # Извлекаем необходимые данные с транслитерацией
            p_type = pergola_data.get('pergola_type', 'N/A')
            if p_type == 'B500NEW':
                model_name = "B500 s povorotnymi lamelyami"
            elif p_type == 'B700NEW':
                model_name = "B700 s povorotno-sdvizhnymi lamelyami"
            elif p_type == 'B600':
                model_name = "B600 s PIR paneliyami"
            else:
                model_name = p_type
                
            width = pergola_data.get('width', 0)
            length = pergola_data.get('length', 0)
            total_cost = pergola_data.get('total_cost', 0)
            
            # Добавляем основную информацию
            simple_pdf.cell(0, 10, f"Model pergoly: {model_name}", 0, 1)
            simple_pdf.cell(0, 10, f"Razmery: {width}x{length} m", 0, 1)
            simple_pdf.cell(0, 10, f"Obschaya stoimost: {int(total_cost):,} rub".replace(',', ' '), 0, 1)
            
            # Добавляем примечание о проблеме с кириллицей
            simple_pdf.ln(10)
            simple_pdf.set_font("DejaVu", 'I', 10)
            simple_pdf.cell(0, 10, "Dannaya versiya dokumenta sozdana bez podderzhki kirillitsy", 0, 1)
            simple_pdf.cell(0, 10, "iz-za problem s kodirovkoy. Polnaya versiya dostupna v veb-interfeyse.", 0, 1)
            
            # Добавляем контактную информацию
            simple_pdf.ln(10)
            simple_pdf.set_font("DejaVu", 'B', 12)
            simple_pdf.cell(0, 10, "Kontaktnaya informatsiya:", 0, 1)
            simple_pdf.set_font("DejaVu", '', 10)
            simple_pdf.cell(0, 7, "Telefon: +7 (495) 123-45-67", 0, 1)
            simple_pdf.cell(0, 7, "Email: info@komfortnyj-dom.ru", 0, 1)
            simple_pdf.cell(0, 7, "Veb-sajt: www.komfortnyj-dom.ru", 0, 1)
            
            # Сохраняем упрощенный PDF
            simple_pdf.output(pdf_filename, 'F')
            print(f"Создан упрощенный PDF: {pdf_filename}")
        except Exception as e2:
            print(f"Ошибка при сохранении упрощенного PDF: {str(e2)}")
            pdf_filename = None
    
    return pdf_filename


def format_pergola_data_for_pdf(results, options, dimensions, pergola_description):
    """
    Форматирует данные расчета перголы для использования в генерации PDF,
    включая все дополнительные описания и изображения.
    
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
    
    # Импортируем функции для работы с описаниями и изображениями
    from config.pergola_descriptions import (
        get_pergola_description,
        get_modular_system_description,
        get_drainage_system_description,
        get_bansbach_description,
        get_pergola_images,
        get_pergola_image_caption
    )
    
    # Извлекаем тип перголы из опций
    pergola_type = options.get('pergola_type', '')
    
    # Собираем все необходимые описания для данного типа перголы
    descriptions = {
        'main': pergola_description,  # Основное описание
        'modular': get_modular_system_description(),  # Описание модульной системы
        'drainage': get_drainage_system_description()  # Описание водоотведения
    }
    
    # Добавляем описания в зависимости от типа перголы
    if pergola_type == "B500NEW":
        descriptions['drive'] = get_bansbach_description()  # Описание привода Bansbach
    elif pergola_type == "B700NEW":
        descriptions['drive'] = get_pergola_description("SOMFY")  # Описание привода Somfy
    
    # Собираем все необходимые изображения
    images = []
    captions = {}
    
    # Основное изображение перголы по типу
    type_images = get_pergola_images(pergola_type)
    if type_images:
        for img in type_images:
            if os.path.exists(img):
                images.append(img)
                captions[img] = get_pergola_image_caption(pergola_type)
                break  # Берем только первое найденное изображение для каждого типа
    
    # Изображение модульной системы
    modular_images = get_pergola_images("MODULAR")
    if modular_images:
        for img in modular_images:
            if os.path.exists(img):
                images.append(img)
                captions[img] = get_pergola_image_caption("MODULAR")
                break
    
    # Изображение системы водоотведения
    drainage_images = get_pergola_images("DRAINAGE")
    if drainage_images:
        for img in drainage_images:
            if os.path.exists(img):
                images.append(img)
                captions[img] = get_pergola_image_caption("DRAINAGE")
                break
    
    # Изображения приводов в зависимости от типа перголы
    if pergola_type == "B500NEW":
        bansbach_images = get_pergola_images("BANSBACH")
        if bansbach_images:
            for img in bansbach_images:
                if os.path.exists(img):
                    images.append(img)
                    captions[img] = get_pergola_image_caption("BANSBACH")
                    break
    elif pergola_type == "B700NEW":
        somfy_images = get_pergola_images("SOMFY")
        if somfy_images:
            for img in somfy_images:
                if os.path.exists(img):
                    images.append(img)
                    captions[img] = get_pergola_image_caption("SOMFY")
                    break
    
    # Составляем итоговый словарь с данными для PDF
    pdf_data = {
        'pergola_type': pergola_type,
        'width': dimensions.get('width', 0),
        'length': dimensions.get('length', 0),
        'lamella_type': options.get('lamella_type', ''),
        'modules': dimensions.get('modules', 1),
        'options': options,
        'total_cost': results.get('total_price', 0) * EURO_RATE,  # Конвертируем в рубли
        'description': pergola_description,
        'modular_description': descriptions.get('modular', ''),
        'drainage_description': descriptions.get('drainage', ''),
        'drive_description': descriptions.get('drive', ''),
        'images': images,  # Список всех путей к изображениям
        'image_caption': 'Изображение перголы',  # Базовая подпись
        'image_captions': captions  # Словарь с подписями для каждого изображения
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
            "attached_assets/b500_rotation.png",
            "attached_assets/Снимок экрана 2025-04-09 в 23.20.06.png"  # Добавлен новый скриншот
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    elif pergola_type == 'B700NEW':
        # Пробуем найти изображение B700 со сдвижением ламелей
        possible_paths = [
            "attached_assets/В700 со сдвижением ламелей.png",
            "attached_assets/b700_sliding.png",
            "attached_assets/Снимок экрана 2025-04-09 в 23.11.44.png"  # Добавлен новый скриншот
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    elif pergola_type == 'B600':
        # Пробуем найти изображение B600 с сэндвич панелями
        possible_paths = [
            "attached_assets/В600 с сэндвич панелями.png",
            "attached_assets/b600_sandwich.png",
            "attached_assets/Снимок экрана 2025-04-09 в 23.02.37.png"  # Добавлен новый скриншот
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    
    return pdf_data