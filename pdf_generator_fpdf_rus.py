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
        
        # Устанавливаем мета-информацию PDF (только латиница)
        self.set_title("Kommercheskoe Predlozhenie")
        self.set_author("Pergola Calculator")
        self.set_creator("Pergola Calculator")
        
        # Устанавливаем отступы
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=20)
        
        # Добавляем шрифт с поддержкой кириллицы
        # Проверяем наличие файла шрифта
        # В Replit используем копирование вместо символьных ссылок
        # и добавляем отладочную информацию
        print("Проверка наличия шрифтов:")
        print(f"DejaVuSans.ttf: {os.path.exists('fonts/DejaVuSans.ttf')}")
        print(f"DejaVuSans-Bold.ttf: {os.path.exists('fonts/DejaVuSans-Bold.ttf')}")
        print(f"DejaVuSansCondensed.ttf: {os.path.exists('fonts/DejaVuSansCondensed.ttf')}")
        
        # Добавляем шрифты с поддержкой кириллицы
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        
        # Устанавливаем шрифт по умолчанию
        self.set_font('DejaVu', '', 12)
        
        # Счетчик страниц для колонтитула
        self.page_count = 0
        
    def header(self):
        """Создает верхний колонтитул на каждой странице"""
        self.page_count += 1
        # Добавляем синюю плашку с текстом
        self.set_fill_color(63, 109, 170)  # Синий цвет #3f6daa
        self.set_text_color(255, 255, 255)  # Белый текст
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 15, "Компания «Комфортный дом»", 0, 1, "C", fill=True)
        
        # Номер страницы
        self.set_text_color(0, 0, 0)  # Черный текст
        self.set_font("DejaVu", "", 10)
        self.cell(0, 5, f"{self.page_count} из 4", 0, 1, "L")
        
    def footer(self):
        """Создает нижний колонтитул на каждой странице"""
        self.set_y(-15)  # 15 мм от нижнего края
        self.set_font("DejaVu", "", 8)
        self.set_text_color(128, 128, 128)  # Серый текст
        self.cell(0, 10, "© 2025 Комфортный дом | Все права защищены", 0, 0, "C")
        
    def chapter_title(self, title):
        """Добавляет заголовок раздела"""
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(0, 0, 0)  # Черный текст
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(1)  # Небольшой отступ после заголовка
        
    def table_header(self, headers, widths):
        """Создает заголовок таблицы"""
        self.set_fill_color(173, 216, 230)  # Светло-голубой цвет
        self.set_text_color(0, 0, 0)  # Черный текст
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
    try:
        # Очищаем временные файлы обработанных изображений
        for file in os.listdir("processed_images"):
            if file.startswith("resized_"):
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
        
        # Добавляем первую страницу
        pdf.add_page()
        
        # Устанавливаем информацию о текущей дате
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 5, f"г. Москва, {current_date}", 0, 1, "L")
        
        # Добавляем номер коммерческого предложения
        pdf.ln(5)
        pdf.cell(0, 5, f"№ {timestamp[:8]}", 0, 1, "L")
        
        # Добавляем заголовок коммерческого предложения
        pdf.ln(10)
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, "C")
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, "на поставку и монтаж биоклиматической перголы", 0, 1, "C")
        
        # Добавляем информацию о клиенте, если она доступна
        if user_data:
            pdf.ln(5)
            pdf.chapter_title("Информация о клиенте:")
            
            pdf.set_font('DejaVu', '', 10)
            if user_data.get('name'):
                pdf.cell(0, 7, f"Имя: {user_data['name']}", 0, 1)
            
            if user_data.get('phone'):
                pdf.cell(0, 7, f"Телефон: {user_data['phone']}", 0, 1)
            
            if user_data.get('email'):
                pdf.cell(0, 7, f"Email: {user_data['email']}", 0, 1)
        
        # Добавляем информацию о выбранной конфигурации перголы
        pdf.ln(10)
        pdf.chapter_title("Параметры перголы:")
        
        # Извлекаем данные о перголе из словаря
        pergola_type = pergola_data.get('pergola_type', '')
        width = pergola_data.get('width', 0)
        length = pergola_data.get('length', 0)
        lamella_type = pergola_data.get('lamella_type', '')
        modules = pergola_data.get('modules', 1)
        
        # Создаем таблицу с основными параметрами перголы
        headers = ["Параметр", "Значение"]
        widths = [80, 80]  # Ширина колонок в мм
        
        pdf.table_header(headers, widths)
        
        pdf.table_row(["Модель перголы", pergola_type], widths)
        pdf.table_row(["Ширина", f"{width} м"], widths)
        pdf.table_row(["Вынос (длина)", f"{length} м"], widths)
        pdf.table_row(["Тип ламелей", lamella_type], widths)
        pdf.table_row(["Количество модулей", str(modules)], widths)
        
        # Если есть опции, добавляем их в таблицу
        options = pergola_data.get('options', {})
        if options:
            if 'lighting_type' in options and options['lighting_type'] != 'none':
                pdf.table_row(["Тип освещения", options['lighting_type']], widths)
            if options.get('installation', False):
                pdf.table_row(["Установка", "Включена"], widths)
            if options.get('delivery', False):
                pdf.table_row(["Доставка", "Включена"], widths)
        
        # Добавляем спецификацию перголы
        pdf.ln(10)
        pdf.chapter_title("Спецификация перголы:")
        
        # Получаем данные о спецификации
        specification = pergola_data.get('specification', [])
        
        if specification:
            headers = ["№", "Наименование", "Количество"]
            widths = [15, 120, 25]  # Ширина колонок в мм
            
            pdf.table_header(headers, widths)
            
            for i, item in enumerate(specification, 1):
                pdf.table_row([str(i), item['name'], str(item['quantity'])], widths, aligns=["C", "L", "C"])
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о спецификации отсутствуют", 0, 1)
        
        # Добавляем информацию о стоимости
        pdf.ln(10)
        pdf.chapter_title("Стоимость:")
        
        # Получаем данные о стоимости
        cost_items = pergola_data.get('cost_items', [])
        total_cost = pergola_data.get('total_cost', 0)
        
        if cost_items:
            headers = ["№", "Наименование", "Стоимость (₽)"]
            widths = [15, 120, 25]  # Ширина колонок в мм
            
            pdf.table_header(headers, widths)
            
            for i, item in enumerate(cost_items, 1):
                price_str = f"{item['price']:,.2f}".replace(',', ' ')
                pdf.table_row([str(i), item['name'], price_str], widths, aligns=["C", "L", "R"])
                
            # Добавляем итоговую строку
            pdf.set_fill_color(211, 211, 211)  # Светло-серый цвет
            pdf.set_font('DejaVu', 'B', 10)
            pdf.set_text_color(0, 0, 0)  # Черный текст
            total_price_str = f"{total_cost:,.2f}".replace(',', ' ')
            
            pdf.cell(15, 8, "", 1, 0, "C", fill=True)
            pdf.cell(120, 8, "ИТОГО:", 1, 0, "R", fill=True)
            pdf.cell(25, 8, total_price_str, 1, 1, "R", fill=True)
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        # Добавляем описание перголы
        pdf.add_page()
        pdf.chapter_title("Описание перголы:")
        
        # Получаем описание перголы
        pergola_description = pergola_data.get('description', '')
        
        # Выводим для отладки
        print(f"Длина HTML-описания: {len(pergola_description)} символов")
        print(f"Содержимое описания: {pergola_description[:100]}...")
        
        # Если описание отсутствует или пустое, добавляем базовое описание
        if not pergola_description or pergola_description == "<p>Описание для данного типа перголы отсутствует.</p>":
            pergola_type = pergola_data.get('pergola_type', 'биоклиматическая')
            print(f"Добавляем базовое описание для перголы типа {pergola_type}")
            
            pergola_description = f"""
            <div style='padding: 0 20px;'>
            <h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Пергола {pergola_type}</h3>
            <p style='margin-bottom: 15px;'>
            Современная биоклиматическая пергола с автоматическим управлением. 
            Изготовлена из высококачественного алюминия с порошковым покрытием.
            </p>
            <div style='margin-bottom: 15px;'>
            <strong>Преимущества:</strong><br/>
            • Защита от осадков и солнца<br/>
            • Регулируемое положение ламелей<br/>
            • Встроенная система отвода воды<br/>
            • Долговечные материалы<br/>
            • Простота управления
            </div>
            <div style='margin-bottom: 15px;'>
            <strong>Технические характеристики:</strong><br/>
            • Алюминиевый профиль: экструдированный алюминий с порошковым покрытием (322х260 мм)<br/>
            • Размеры: 164x164 мм, используется 7 различных типов алюминиевых профилей<br/>
            • Система автоматизации: приводной механизм Bansbach easylift (IP65),<br/>
            дополнительно TANDEM привод доступен опционально
            </div>
            </div>
            """
        
        # HTML-описание нужно преобразовать в чистый текст
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(pergola_description, 'html.parser')
            clean_text = soup.get_text(separator="\n\n")
            
            # Выводим текст в PDF
            pdf.set_font('DejaVu', '', 11)
            
            # Очищаем текст от излишних пробелов и переносов
            clean_text = ' '.join([line.strip() for line in clean_text.split('\n')])
            
            # Разбиваем текст на смысловые блоки
            sections = []
            current_section = []
            
            for line in clean_text.split('\n\n'):
                line = line.strip()
                if line:
                    current_section.append(line)
                elif current_section:
                    sections.append(' '.join(current_section))
                    current_section = []
            
            if current_section:
                sections.append(' '.join(current_section))
            
            # Добавляем блоки в PDF
            for section in sections:
                # Добавляем заголовки с жирным шрифтом
                if "B500NEW" in section or "Серия B500NEW" in section:
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.multi_cell(0, 6, "Серия B500NEW (с поворотными ламелями)")
                    pdf.ln(3)
                    pdf.set_font('DejaVu', '', 11)
                    continue
                    
                if "Ламели:" in section:
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.multi_cell(0, 6, "Ламели:")
                    pdf.ln(3)
                    pdf.set_font('DejaVu', '', 11)
                    continue
                    
                if "Преимущества:" in section:
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.multi_cell(0, 6, "Преимущества:")
                    pdf.ln(3)
                    pdf.set_font('DejaVu', '', 11)
                    continue
                
                if "Узлы:" in section:
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.multi_cell(0, 6, "Узлы:")
                    pdf.ln(3)
                    pdf.set_font('DejaVu', '', 11)
                    continue
                
                # Обрабатываем маркированные списки
                if section.startswith('•'):
                    # Разбираем маркированные пункты
                    items = section.split('•')
                    for item in items:
                        if item.strip():
                            pdf.multi_cell(0, 6, f"• {item.strip()}")
                            pdf.ln(2)
                else:
                    # Обычный текст
                    pdf.multi_cell(0, 6, section)
                    pdf.ln(3)
                
        except Exception as e:
            print(f"Ошибка при обработке HTML-описания: {str(e)}")
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Ошибка при обработке описания перголы", 0, 1)
        
        # Добавляем изображение перголы, если оно есть
        image_path = pergola_data.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                # Обрабатываем изображение перед добавлением
                original_img = Image.open(image_path)
                width, height = original_img.size
                
                # Определяем максимальную ширину для изображения (160 мм, учитывая поля)
                max_width_mm = 160
                max_width_px = int(max_width_mm * 300 / 25.4)  # Преобразуем мм в пиксели при 300 DPI
                
                # Создаем отдельную страницу для изображения
                pdf.add_page()
                
                # Максимальная ширина для изображения в PDF
                max_width_pdf = 160  # максимальная ширина в мм
                
                # Вычисляем отношение сторон
                aspect_ratio = height / width
                
                # Рассчитываем размеры с сохранением пропорций
                img_width_mm = max_width_pdf
                img_height_mm = img_width_mm * aspect_ratio
                
                # Отладочная информация
                print(f"Исходные размеры изображения: {width}x{height}")
                print(f"Отношение сторон: {aspect_ratio:.2f}")
                print(f"Размеры для PDF: {img_width_mm:.1f}x{img_height_mm:.1f} мм")
                
                # Добавляем заголовок изображения
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 10, "Иллюстрация перголы:", 0, 1, "C")
                pdf.ln(5)
                
                # Вставляем изображение с явным указанием ширины и высоты
                # для гарантии сохранения пропорций
                pdf.image(
                    image_path,
                    x=(210 - img_width_mm) / 2,  # центрируем
                    y=pdf.get_y(),  # текущая позиция Y
                    w=img_width_mm,  # ширина
                    h=img_height_mm  # высота, рассчитанная с сохранением пропорций
                )
                print(f"Добавляем изображение в PDF: {image_path}")
            except Exception as e:
                print(f"Ошибка при обработке изображения: {str(e)}")
        
        # Добавляем контактную информацию
        pdf.add_page()
        pdf.chapter_title("Контактная информация:")
        
        pdf.set_font('DejaVu', '', 11)
        pdf.multi_cell(0, 6, "Для получения дополнительной информации или оформления заказа, пожалуйста, свяжитесь с нами:")
        pdf.ln(5)
        
        contact_info = [
            "Телефон: +7 (495) 123-45-67",
            "Email: info@komfortnyj-dom.ru",
            "Веб-сайт: www.komfortnyj-dom.ru",
            "Адрес: г. Москва, ул. Примерная, д. 123"
        ]
        
        for info in contact_info:
            pdf.cell(0, 7, info, 0, 1)
        
        # Создаем директорию для сохранения PDF
        os.makedirs(os.path.dirname(pdf_filename), exist_ok=True)
        
        # Сохраняем PDF
        pdf.output(pdf_filename)
        print(f"PDF успешно создан: {pdf_filename}")
        
        return pdf_filename
        
    except Exception as e:
        print(f"Ошибка при создании PDF: {str(e)}")
        
        try:
            # Создаем упрощенный PDF без кириллицы в случае ошибки
            from fpdf import FPDF
            
            # Получаем данные из словаря
            p_type = pergola_data.get('pergola_type', 'пергола') if pergola_data else 'пергола'
            p_width = pergola_data.get('width', 0) if pergola_data else 0
            p_length = pergola_data.get('length', 0) if pergola_data else 0
            p_cost = pergola_data.get('total_cost', 0) if pergola_data else 0
            
            # Создаем упрощенный PDF
            simple_pdf = FPDF()
            simple_pdf.add_page()
            simple_pdf.set_font('Arial', 'B', 14)
            simple_pdf.cell(0, 10, "Калькулятор пергол", 0, 1, 'C')
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.cell(0, 10, f"Модель: {p_type}", 0, 1)
            simple_pdf.cell(0, 10, f"Размеры: {p_width}x{p_length}м", 0, 1)
            simple_pdf.cell(0, 10, f"Общая стоимость: {p_cost:,.2f} руб", 0, 1)
            
            # Добавляем заметку о проблеме
            simple_pdf.ln(10)
            simple_pdf.set_font('Arial', 'I', 10)
            simple_pdf.cell(0, 10, "Произошла ошибка при создании полного PDF с описанием.", 0, 1)
            simple_pdf.cell(0, 10, "Это упрощенная версия с основной информацией.", 0, 1)
            
            # Сохраняем упрощенный PDF в дефолтную директорию
            backup_filename = f"generated_pdf/KP_Pergola_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
            simple_pdf.output(backup_filename)
            print(f"Упрощенный PDF создан: {backup_filename}")
            
            return backup_filename
            
        except Exception as e2:
            print(f"Ошибка при создании упрощенного PDF: {str(e2)}")
            return None


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