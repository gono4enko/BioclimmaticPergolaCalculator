"""
Модуль для генерации коммерческого предложения в формате PDF
на основе данных из калькулятора перголы.
Использует библиотеку FPDF с поддержкой шрифта DejaVu для корректной работы с кириллицей.
"""
import os
import io
import re
import time
import glob
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from bs4 import BeautifulSoup

# Создаем директории для сохранения файлов, если их нет
os.makedirs("generated_pdf", exist_ok=True)
os.makedirs("processed_images", exist_ok=True)

# Постоянные параметры для PDF
PAGE_WIDTH = 210  # A4 ширина в мм
PAGE_HEIGHT = 297  # A4 высота в мм
MARGIN = 20  # Отступы в мм

# Определяем пути к шрифтам
FONT_PATH = "fonts"
REGULAR_FONT = os.path.join(FONT_PATH, "DejaVuSans.ttf")
BOLD_FONT = os.path.join(FONT_PATH, "DejaVuSans-Bold.ttf")

class PDF(FPDF):
    """
    Расширенный класс FPDF с поддержкой кириллицы через шрифты DejaVu
    и дополнительными функциями для создания коммерческого предложения
    """
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        
        # Добавляем шрифты с поддержкой кириллицы
        self.add_font('DejaVu', '', REGULAR_FONT, uni=True)
        self.add_font('DejaVu', 'B', BOLD_FONT, uni=True)
        
        # Устанавливаем метаданные PDF
        self.set_title("Коммерческое предложение")
        self.set_author("Pergola Calculator")
        self.set_creator("Pergola Calculator")
        
        # Устанавливаем отступы
        self.set_margins(MARGIN, MARGIN, MARGIN)
        self.set_auto_page_break(True, margin=MARGIN)
        
        # Счетчик страниц для колонтитула
        self.alias_nb_pages()  # Добавляем поддержку общего числа страниц
        
    def header(self):
        """Создает верхний колонтитул на каждой странице"""
        # Логотип компании
        self.set_fill_color(63, 109, 170)  # Синий цвет #3f6daa
        self.set_text_color(255, 255, 255)  # Белый текст
        self.set_font('DejaVu', 'B', 14)
        self.cell(0, 15, "Комфортный Дом", 0, 1, 'C', fill=True)
        
        # Возвращаем цвет текста к черному
        self.set_text_color(0, 0, 0)
        self.ln(5)  # Добавляем отступ после заголовка
        
    def footer(self):
        """Создает нижний колонтитул на каждой странице"""
        self.set_y(-20)  # Позиционируемся в 20 мм от нижнего края
        self.set_font('DejaVu', '', 8)
        
        # Добавляем информацию о компании
        self.cell(0, 5, "Телефон: +7 (495) 123-45-67 | Email: info@komfortnyj-dom.ru | www.komfortnyj-dom.ru", 0, 1, 'C')
        
        # Добавляем номер страницы
        self.cell(0, 5, f"Страница {self.page_no()}/{'{nb}'}", 0, 0, 'C')
        
    def add_title(self, title):
        """Добавляет заголовок с синей плашкой"""
        self.set_font('DejaVu', 'B', 16)
        self.set_fill_color(63, 109, 170)  # Синий цвет #3f6daa
        self.set_text_color(255, 255, 255)  # Белый текст
        self.cell(0, 10, title, 0, 1, 'C', fill=True)
        self.set_text_color(0, 0, 0)  # Возвращаем черный цвет
        self.ln(5)
        
    def add_subtitle(self, subtitle):
        """Добавляет подзаголовок"""
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.ln(2)
        
    def add_paragraph(self, text):
        """Добавляет абзац с форматированным текстом"""
        self.set_font('DejaVu', '', 10)
        
        # Разбиваем текст на строки с учетом ширины страницы
        text_width = self.w - 2 * MARGIN
        lines = self.multi_cell(0, 5, text, 0, 'L', False, True)
        self.ln(3)
        
    def add_html_text(self, html_text):
        """
        Обрабатывает HTML текст и добавляет его в PDF с поддержкой
        базовых тегов (b, strong, i, em, br, p)
        """
        if not html_text:
            return
            
        # Очищаем текст от лишних пробелов, табуляций и переносов строк
        html_text = re.sub(r'\s+', ' ', html_text)
        
        # Парсим HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Преобразуем HTML в текст с сохранением базового форматирования
        text = ""
        for element in soup.recursiveChildGenerator():
            if element.name == 'p':
                text += "\n\n"
            elif element.name == 'br':
                text += "\n"
            elif element.name in ['b', 'strong']:
                # Обрабатываем жирный текст отдельно
                self.set_font('DejaVu', 'B', 10)
                self.multi_cell(0, 5, element.get_text(), 0, 'L')
                self.set_font('DejaVu', '', 10)
                continue
            elif element.name in ['i', 'em']:
                # Обрабатываем курсивный текст (используем обычный шрифт, т.к. курсивного нет)
                self.set_font('DejaVu', '', 10)
                self.multi_cell(0, 5, element.get_text(), 0, 'L')
                continue
            elif element.string:
                text += element.string
        
        # Добавляем текст в PDF
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 5, text, 0, 'L')
        self.ln(3)
    
    def add_list(self, items, bullet="•"):
        """Добавляет маркированный список"""
        self.set_font('DejaVu', '', 10)
        for item in items:
            self.cell(5, 5, bullet, 0, 0, 'L')
            self.multi_cell(0, 5, item, 0, 'L')
            self.ln(2)
        self.ln(3)
            
    def add_table(self, headers, data, col_widths=None):
        """
        Добавляет таблицу с заголовками и данными
        
        Args:
            headers (list): Список заголовков столбцов
            data (list): Список строк с данными (каждая строка - список ячеек)
            col_widths (list, optional): Список ширин столбцов в мм
        """
        # Проверка, поместится ли таблица на текущей странице
        table_height = 10  # Высота заголовка
        
        # Расчет примерной высоты таблицы
        for row in data:
            row_height = 8  # Минимальная высота строки
            table_height += row_height
        
        # Если таблица не помещается, добавляем новую страницу
        if self.get_y() + table_height > PAGE_HEIGHT - MARGIN:
            self.add_page()
        
        # Определяем ширину столбцов, если не задана
        if col_widths is None:
            available_width = PAGE_WIDTH - 2 * MARGIN
            col_widths = [available_width / len(headers)] * len(headers)
            
        # Заголовки таблицы
        self.set_font('DejaVu', 'B', 10)
        self.set_fill_color(240, 240, 240)  # Светло-серый фон
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C', True)
        self.ln()
        
        # Данные таблицы
        self.set_font('DejaVu', '', 10)
        self.set_fill_color(255, 255, 255)  # Белый фон
        
        for row in data:
            # Находим максимальное количество строк в ячейке
            max_lines = 1
            for i, cell in enumerate(row):
                # Расчет количества строк в ячейке
                cell_lines = len(self.multi_cell(col_widths[i], 5, str(cell), 0, 'L', False, True))
                max_lines = max(max_lines, cell_lines)
            
            # Высота строки = высота одной строки текста * количество строк + отступы
            row_height = max_lines * 5 + 2
            
            # Запоминаем начальную позицию X
            x_pos = self.get_x()
            y_pos = self.get_y()
            
            # Рисуем ячейки строки с одинаковой высотой
            for i, cell in enumerate(row):
                self.set_xy(x_pos, y_pos)
                self.multi_cell(col_widths[i], row_height / max_lines, str(cell), 1, 'L', False)
                x_pos += col_widths[i]
            
            # Переходим на позицию начала следующей строки
            self.set_y(y_pos + row_height)
        
        self.ln(5)
    
    def add_image(self, image_path, caption=None, width=None, height=None):
        """
        Добавляет изображение с подписью, сохраняя пропорции
        
        Args:
            image_path (str): Путь к изображению
            caption (str, optional): Подпись к изображению
            width (int, optional): Желаемая ширина изображения в мм
            height (int, optional): Желаемая высота изображения в мм
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(image_path):
                print(f"Файл не найден: {image_path}")
                return
                
            # Создаем уникальное имя для обработанного изображения
            image_name = os.path.basename(image_path)
            processed_path = os.path.join("processed_images", f"proc_{int(time.time())}_{image_name}")
            
            # Открываем и обрабатываем изображение через Pillow
            with Image.open(image_path) as img:
                # Получаем оригинальные размеры
                orig_width, orig_height = img.size
                
                # Если размеры не указаны, используем размер, чтобы изображение
                # занимало 80% ширины страницы
                available_width = PAGE_WIDTH - 2 * MARGIN
                if width is None and height is None:
                    width = available_width * 0.8
                
                # Вычисляем высоту с сохранением пропорций
                if width is not None and height is None:
                    height = width * orig_height / orig_width
                elif height is not None and width is None:
                    width = height * orig_width / orig_height
                
                # Проверяем, поместится ли изображение на текущей странице
                if self.get_y() + height + (15 if caption else 5) > PAGE_HEIGHT - MARGIN:
                    self.add_page()
                
                # Центрируем изображение
                x_pos = (PAGE_WIDTH - width) / 2
                
                # Добавляем изображение
                self.image(image_path, x=x_pos, y=self.get_y(), w=width, h=height)
                self.ln(height + 5)
                
                # Добавляем подпись, если указана
                if caption:
                    self.set_font('DejaVu', '', 9)
                    self.set_text_color(90, 90, 90)  # Серый цвет для подписи
                    self.multi_cell(0, 5, caption, 0, 'C')
                    self.set_text_color(0, 0, 0)  # Возвращаем черный цвет
                    self.ln(5)
                    
        except Exception as e:
            print(f"Ошибка при добавлении изображения {image_path}: {str(e)}")
            self.add_paragraph(f"[Ошибка загрузки изображения: {os.path.basename(image_path)}]")


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
        # Создаем PDF документ
        pdf = PDF()
        pdf.add_page()
        
        # Добавляем информацию о пользователе, если она предоставлена
        if user_data:
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 10, f"Клиент: {user_data.get('name', 'Не указан')}", 0, 1, 'L')
            
            if 'contact' in user_data and user_data['contact']:
                pdf.set_font('DejaVu', '', 10)
                pdf.cell(0, 6, f"Контактная информация: {user_data['contact']}", 0, 1, 'L')
            
            if 'delivery_address' in user_data and user_data['delivery_address']:
                pdf.set_font('DejaVu', '', 10)
                pdf.cell(0, 6, f"Адрес доставки: {user_data['delivery_address']}", 0, 1, 'L')
            
            pdf.ln(5)
        
        # Добавляем дату создания коммерческого предложения
        current_date = datetime.now().strftime("%d.%m.%Y")
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, f"Коммерческое предложение от {current_date}", 0, 1, 'L')
        pdf.ln(5)
        
        # Добавляем название и общее описание проекта
        pdf.add_title("Калькулятор Пергол")
        
        # Основная информация о перголе
        pergola_type = pergola_data["options"]["pergola_type"]
        pergola_type_name = {
            "B500NEW": "Пергола B500 с поворотными ламелями",
            "B700NEW": "Пергола B700 со сдвижными ламелями",
            "B600": "Пергола B600 с сэндвич панелями"
        }.get(pergola_type, pergola_type)
        
        width = pergola_data["dimensions"]["width"]
        length = pergola_data["dimensions"]["length"]
        modules = pergola_data["dimensions"]["modules"]
        
        # Добавляем основную информацию о перголе
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, f"Модель перголы: {pergola_type_name}", 0, 1, 'L')
        pdf.cell(0, 8, f"Размеры: {width:.1f}x{length:.1f} м", 0, 1, 'L')
        
        # Добавляем количество модулей, если больше 1
        if modules > 1:
            pdf.cell(0, 8, f"Количество модулей: {modules}", 0, 1, 'L')
        
        # Добавляем описание перголы, если оно есть
        if "pergola_description" in pergola_data and pergola_data["pergola_description"]:
            pdf.ln(5)
            pdf.add_subtitle("Описание перголы")
            pdf.add_html_text(pergola_data["pergola_description"])
        
        # Добавляем изображения перголы, если они есть
        if "pergola_images" in pergola_data and pergola_data["pergola_images"]:
            pdf.ln(5)
            pdf.add_subtitle("Изображения")
            
            # Проходим по всем изображениям, но не более 3-х
            for i, image_path in enumerate(pergola_data["pergola_images"][:3]):
                caption = pergola_data.get("pergola_image_caption", f"Изображение {i+1}")
                # Если изображение слишком большое по высоте, добавляем его на отдельной странице
                if i > 0:  # Пропускаем проверку для первого изображения
                    pdf.add_page()
                pdf.add_image(image_path, caption, width=None)
        
        # Добавляем дополнительные описания, если они есть
        if "additional_descriptions" in pergola_data:
            for desc_title, desc_html in pergola_data["additional_descriptions"].items():
                if desc_html:
                    pdf.add_page()
                    pdf.add_subtitle(desc_title)
                    pdf.add_html_text(desc_html)
        
        # Добавляем спецификацию перголы
        if "specification" in pergola_data and pergola_data["specification"]:
            pdf.add_page()
            pdf.add_subtitle("Спецификация перголы")
            
            # Подготавливаем данные для таблицы
            spec_data = []
            for item in pergola_data["specification"]:
                spec_data.append([item["name"], item["count"]])
            
            # Добавляем таблицу спецификации
            pdf.add_table(
                headers=["Наименование", "Количество"],
                data=spec_data,
                col_widths=[120, 50]
            )
        
        # Добавляем стоимость перголы
        pdf.add_page()
        pdf.add_subtitle("Стоимость")
        
        # Подготавливаем данные о стоимости
        price_data = []
        total_price = pergola_data["total_price"]
        euro_rate = pergola_data.get("euro_rate", 100)  # Курс евро по умолчанию
        
        # Функция для форматирования цен
        def format_price(price_eur):
            price_rub = price_eur * euro_rate
            return f"{price_eur:.2f} € ({price_rub:,.0f} ₽)".replace(",", " ")
        
        # Добавляем строки с ценами из items, если они есть
        if "items" in pergola_data:
            for item in pergola_data["items"]:
                price_data.append([item["name"], format_price(item["price"])])
        
        # Добавляем таблицу с ценами
        pdf.add_table(
            headers=["Наименование", "Стоимость"],
            data=price_data,
            col_widths=[120, 50]
        )
        
        # Добавляем итоговую стоимость
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, f"Общая стоимость: {format_price(total_price)}", 0, 1, 'R')
        
        # Добавляем информацию об установке, если она выбрана
        if pergola_data["options"].get("installation", False):
            pdf.add_page()
            pdf.add_subtitle("Установка")
            
            # Если есть описание установки, добавляем его
            if "installation_description" in pergola_data and pergola_data["installation_description"]:
                pdf.add_html_text(pergola_data["installation_description"])
            else:
                # Иначе добавляем стандартное описание
                pdf.add_paragraph(
                    "Стоимость установки включает все необходимые работы по монтажу перголы, "
                    "подключению автоматики и настройке системы."
                )
                
                # Стандартный список работ по установке
                install_items = [
                    "Доставка комплектующих на объект",
                    "Сборка каркаса перголы",
                    "Монтаж ламелей и механизмов",
                    "Установка системы управления",
                    "Настройка и тестирование",
                    "Инструктаж по эксплуатации"
                ]
                
                pdf.add_list(install_items)
        
        # Сохраняем PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"generated_pdf/KP_Pergola_{timestamp}.pdf"
        
        try:
            pdf.output(pdf_filename)
            print(f"PDF успешно сохранен: {pdf_filename}")
            return pdf_filename
        except Exception as e:
            print(f"Ошибка при сохранении PDF: {str(e)}")
            # Создаем упрощенную версию без кириллицы для отладки
            try:
                pdf_backup = FPDF()
                pdf_backup.add_page()
                pdf_backup.set_font("Arial", "B", 16)
                pdf_backup.cell(0, 10, "Kalkulyator Pergol", ln=True)
                pdf_backup.set_font("Arial", "", 12)
                pdf_backup.cell(0, 10, f"Model pergoly: {pergola_type_name}", ln=True)
                pdf_backup.cell(0, 10, f"Razmery: {width:.1f}x{length:.1f} m", ln=True)
                pdf_backup.cell(0, 10, f"Obschaya stoimost: {total_price*euro_rate:,.0f} rub", ln=True)
                pdf_backup.ln(20)
                pdf_backup.cell(0, 10, "Dannaya versiya dokumenta sozdana bez podderzhki kirillitsy", ln=True)
                pdf_backup.cell(0, 10, "iz-za problem s kodirovkoy. Polnaya versiya dostupna v veb-interfeyse.", ln=True)
                pdf_backup.ln(40)
                pdf_backup.cell(0, 10, "Kontaktnaya informatsiya:", ln=True)
                pdf_backup.ln(5)
                pdf_backup.cell(0, 10, "Telefon: +7 (495) 123-45-67", ln=True)
                pdf_backup.cell(0, 10, "Email: info@komfortnyj-dom.ru", ln=True) 
                pdf_backup.cell(0, 10, "Veb-sajt: www.komfortnyj-dom.ru", ln=True)
                backup_filename = pdf_filename
                pdf_backup.output(backup_filename)
                print(f"Создан упрощенный PDF: {backup_filename}")
                return backup_filename
            except Exception as backup_error:
                print(f"Ошибка при создании упрощенного PDF: {str(backup_error)}")
                return None
    
    except Exception as e:
        print(f"Ошибка при генерации PDF: {str(e)}")
        return None


def format_pergola_data_for_pdf(results, options, dimensions, pergola_description=""):
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
    from config.pergola_descriptions import (
        get_pergola_description, 
        get_modular_system_description,
        get_drainage_system_description,
        get_bansbach_description,
        get_bioclimatic_install_description,
        get_lamella_engineering_description,
        get_pergola_images,
        get_pergola_image_caption
    )
    
    # Получаем тип перголы и другие параметры
    pergola_type = options.get("pergola_type", "")
    modules = dimensions.get("modules", 1)
    
    # Если описание перголы не указано, используем стандартное из модуля descriptions
    if not pergola_description:
        pergola_description = get_pergola_description(pergola_type)
    
    # Формируем словарь с данными для PDF
    pdf_data = {
        "options": options,
        "dimensions": dimensions,
        "total_price": results.get("total_price", 0),
        "euro_rate": 110,  # Актуальный курс евро (из константы в app_basic.py)
        "items": results.get("items", []),
        "specification": results.get("specification", []),
        "pergola_description": pergola_description,
        "pergola_image_caption": get_pergola_image_caption(pergola_type),
    }
    
    # Получаем изображения для перголы
    pdf_data["pergola_images"] = get_pergola_images(pergola_type)
    
    # Добавляем дополнительные описания
    pdf_data["additional_descriptions"] = {
        "Описание модульной системы": get_modular_system_description() if modules > 1 else "",
        "Система водоотведения": get_drainage_system_description(),
        "Технические характеристики ламелей": get_lamella_engineering_description(),
    }
    
    # Добавляем описание привода в зависимости от типа перголы
    if pergola_type == "B500NEW":
        pdf_data["additional_descriptions"]["Автоматика Bansbach"] = get_bansbach_description()
    
    # Добавляем описание установки, если она выбрана
    if options.get("installation", False):
        pdf_data["installation_description"] = get_bioclimatic_install_description()
    
    return pdf_data