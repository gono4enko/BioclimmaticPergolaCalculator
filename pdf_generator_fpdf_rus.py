"""
Модуль для генерации коммерческого предложения в формате PDF
на основе данных из калькулятора перголы.
Использует библиотеку FPDF для корректной работы с кириллицей.
"""
import os
import io
from datetime import datetime
import pytz
from fpdf import FPDF
from PIL import Image

# Определяем временную зону для Ростова-на-Дону (также использует Europe/Moscow)
ROSTOV_TZ = pytz.timezone('Europe/Moscow')

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
        
        # Устанавливаем отступы (верхний отступ увеличиваем для шапки)
        self.set_margins(20, 35, 20)
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
        
    def header(self):
        """
        Добавляет шапку в PDF с информацией о компании.
        Шапка содержит название компании, адрес, телефон и другие контактные данные.
        Версия без логотипа, только с текстом на синем фоне.
        """
        # Устанавливаем координаты для шапки
        self.set_y(0)
        
        # Синий цвет фона шапки (#2A4C7F - темно-синий)
        self.set_fill_color(42, 76, 127)
        
        # Белый цвет текста
        self.set_text_color(255, 255, 255)
        
        # Рисуем прямоугольник по всей ширине страницы
        self.set_draw_color(42, 76, 127)  # Устанавливаем цвет рамки как фон
        self.rect(0, 0, 210, 30, style='F')
        
        # Добавляем название компании (слева) 
        self.set_font('DejaVu', 'B', 16)  # Увеличиваем размер шрифта
        self.set_xy(10, 5)
        self.cell(100, 10, 'Компания «Комфортный дом»', 0, 1, 'L')
        
        # Добавляем слоган или подзаголовок (используем обычный шрифт вместо курсива)
        self.set_font('DejaVu', '', 10)
        self.cell(100, 5, 'Биоклиматические перголы премиум-класса', 0, 1, 'L')
        
        # Добавляем контактную информацию (справа)
        self.set_font('DejaVu', '', 9)
        self.set_xy(120, 5)
        self.cell(80, 5, 'г.Ростов-на-Дону, ул.Орская, 27\\1', 0, 2, 'R')
        self.cell(80, 5, 'моб. +7 (906) 429-74-20', 0, 2, 'R')
        self.cell(80, 5, 'E-mail: zakaz@infopergola.ru', 0, 2, 'R')
        self.cell(80, 5, 'Сайт: https://pergolamarket.ru/', 0, 2, 'R')
        
        # Добавляем разделительную линию под шапкой
        self.set_draw_color(255, 255, 255)  # Белый цвет линии
        self.line(10, 28, 200, 28)
        
        # Сбрасываем цвет текста на черный для основного содержимого
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)  # Восстанавливаем черный цвет линий
        
        # Устанавливаем позицию для начала основного содержимого
        self.set_xy(20, 35)
    
    def footer(self):
        """Создает нижний колонтитул на каждой странице"""
        # Позиция на 1.5 см от нижнего края
        self.set_y(-15)
        
        # Тонкая линия над футером (светло-серая)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(self.get_y() + 2)  # Небольшой отступ после линии
        
        # Устанавливаем шрифт для футера
        self.set_font('DejaVu', '', 8)
        self.set_text_color(80, 80, 80)  # Серый цвет текста для футера
        
        # Текст сайта слева
        self.cell(100, 10, 'https://pergolamarket.ru/calculator_bioclimatic_pergola', 0, 0, 'L')
        
        # Номер страницы справа
        self.cell(0, 10, f'Страница {self.page_no()}', 0, 0, 'R')
        
        # Восстанавливаем цвета по умолчанию
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
    
    def chapter_title(self, title):
        """Добавляет заголовок раздела"""
        self.set_font('DejaVu', 'B', 14)
        self.set_fill_color(230, 230, 230)  # Светло-серый фон
        self.cell(0, 9, title, 0, 1, 'L', 1)
        self.ln(3)  # Отступ после заголовка
    
    def check_table_fit(self, rows_count, row_height=8, additional_height=0):
        """
        Проверяет, поместится ли таблица на текущей странице
        Если не поместится - добавляет новую страницу
        
        Args:
            rows_count (int): Количество строк в таблице
            row_height (int): Высота одной строки в мм
            additional_height (int): Дополнительная высота (для учета многострочных ячеек)
            
        Returns:
            bool: True если таблица помещается, False если добавлена новая страница
        """
        # Примерная высота таблицы: высота строки * кол-во строк + запас 15 мм на заголовки и отступы
        # Добавляем additional_height для учета многострочных ячеек
        table_height = rows_count * row_height + 15 + additional_height
        
        # Получаем текущую позицию Y (высоту от начала страницы)
        current_y = self.get_y()
        
        # Рассчитываем оставшееся пространство на странице
        # Увеличим отступ от нижней границы для надежности
        page_bottom = 272  # Уменьшаем нижнюю границу для большего запаса от футера
        available_space = page_bottom - current_y
        
        # Если таблица не помещается, добавляем новую страницу
        if table_height > available_space:
            self.add_page()
            return False
        
        return True
    
    def table_header(self, headers, widths):
        """Создает заголовок таблицы"""
        # Устанавливаем шрифт и цвет для заголовков
        self.set_font('DejaVu', 'B', 10)
        self.set_fill_color(240, 240, 240)  # Светло-серый фон
        self.set_text_color(0, 0, 0)  # Черный текст
        
        # Выводим заголовки таблицы
        for i in range(len(headers)):
            self.cell(widths[i], 10, headers[i], 1, 0, 'C', 1)
        self.ln()  # Переход на новую строку
    
    def multi_cell_row(self, data, widths, aligns=None, min_row_height=7):
        """
        Добавляет строку в таблицу с поддержкой многострочного текста в ячейках
        
        Args:
            data (list): Данные для ячеек
            widths (list): Ширина каждой ячейки
            aligns (list, optional): Выравнивание для каждой ячейки (L, C, R)
            min_row_height (int, optional): Минимальная высота строки в мм
        """
        # Если выравнивание не указано, используем левое для всех ячеек
        if aligns is None:
            aligns = ['L'] * len(data)
            
        # Устанавливаем шрифт
        self.set_font('DejaVu', '', 10)
        
        # Преобразуем все элементы данных в строки
        data = [str(item) for item in data]
        
        # Сохраняем текущую позицию
        x_start = self.get_x()
        y_start = self.get_y()
        
        # Вычисляем height для каждой ячейки
        heights = []
        line_counts = []
        
        # Сначала вычислим высоту для каждой ячейки,
        # разбивая текст на строки соответствующей ширины
        for i, text in enumerate(data):
            lines = self.get_multi_cell_lines(text, widths[i] - 4)  # Отступ 4 мм
            line_count = len(lines)
            line_counts.append(line_count)
            
            # Вычисляем высоту ячейки (количество строк * высота строки)
            cell_height = line_count * min_row_height
            heights.append(cell_height)
        
        # Определяем максимальную высоту строки таблицы
        max_height = max(heights)
        max_height = max(max_height, min_row_height)  # Минимальная высота
        
        # Теперь рисуем ячейки с одинаковой высотой
        for i, text in enumerate(data):
            current_x = x_start
            for j in range(i):
                current_x += widths[j]
            
            # Рисуем границу ячейки
            self.rect(current_x, y_start, widths[i], max_height)
            
            # Если текст состоит из нескольких строк
            lines = self.get_multi_cell_lines(text, widths[i] - 4)
            
            if len(lines) > 1:
                # Для многострочного текста используем multi_cell
                self.set_xy(current_x, y_start)
                
                # Вычисляем высоту одной строки с учетом равномерного распределения всего текста
                line_height = max_height / len(lines)
                
                # Выводим текст построчно с учетом выравнивания
                for line in lines:
                    # Вычисляем x-позицию в зависимости от выравнивания
                    if aligns[i] == 'C':  # По центру
                        line_width = self.get_string_width(line)
                        text_x = current_x + (widths[i] - line_width) / 2
                    elif aligns[i] == 'R':  # По правому краю
                        line_width = self.get_string_width(line)
                        text_x = current_x + widths[i] - line_width - 2
                    else:  # По левому краю (L)
                        text_x = current_x + 2
                    
                    self.set_xy(text_x, self.get_y())
                    self.cell(0, line_height, line, 0, 2, '')
            else:
                # Для однострочного текста центрируем по вертикали
                line_height = max_height
                
                # Определяем вертикальное положение (по центру ячейки)
                text_y = y_start + (max_height - min_row_height) / 2
                
                self.set_xy(current_x + 2, text_y)
                self.cell(widths[i] - 4, min_row_height, text, 0, 0, aligns[i])
        
        # Переходим на следующую строку
        self.set_xy(x_start, y_start + max_height)

    def get_multi_cell_lines(self, text, width):
        """
        Возвращает список строк, на которые разбивается текст,
        чтобы поместиться в указанную ширину.
        
        Args:
            text (str): Текст для отображения
            width (float): Доступная ширина в мм
            
        Returns:
            list: Список строк после разбиения
        """
        # Предварительная обработка текста
        if not text:
            return [""]
            
        # Разбиваем текст по явным переносам строк
        text_array = text.split('\n')
        lines = []
        
        # Корректируем ширину, добавляя небольшой запас
        # (это нужно для надежности, чтобы избежать обрезания текста)
        effective_width = width - 2
        
        for text_line in text_array:
            # Если строка короткая, просто добавляем её
            if self.get_string_width(text_line) <= effective_width:
                lines.append(text_line)
                continue
                
            # Разбиваем строку на слова
            words = text_line.split(' ')
            current_line = ''
            
            for word in words:
                # Проверяем, поместится ли слово в текущую строку
                test_line = current_line + (' ' if current_line else '') + word
                if self.get_string_width(test_line) <= effective_width:
                    # Слово помещается - добавляем его к текущей строке
                    current_line = test_line
                else:
                    # Слово не помещается - начинаем новую строку
                    
                    # Сначала сохраняем текущую строку
                    if current_line:
                        lines.append(current_line)
                    
                    # Проверяем, поместится ли само слово в строку
                    if self.get_string_width(word) <= effective_width:
                        # Слово помещается в новую строку
                        current_line = word
                    else:
                        # Слово слишком длинное - разбиваем его на части
                        parts = []
                        current_part = ''
                        
                        for char in word:
                            test_part = current_part + char
                            if self.get_string_width(test_part) <= effective_width:
                                current_part = test_part
                            else:
                                parts.append(current_part)
                                current_part = char
                        
                        # Добавляем последнюю часть
                        if current_part:
                            parts.append(current_part)
                        
                        # Первую часть используем для текущей строки
                        if parts:
                            current_line = parts[0]
                            # Остальные части сразу добавляем в список строк
                            for i in range(1, len(parts)):
                                lines.append(parts[i])
            
            # Добавляем последнюю строку
            if current_line:
                lines.append(current_line)
        
        # Если ни одной строки не получилось, добавляем пустую
        if not lines:
            lines = [""]
            
        return lines
    
    def table_row(self, data, widths, aligns=None, row_height=7):
        """
        Добавляет строку в таблицу с адаптивным размером шрифта
        
        Args:
            data (list): Данные для ячеек
            widths (list): Ширина каждой ячейки
            aligns (list, optional): Выравнивание для каждой ячейки (L, C, R)
            row_height (int, optional): Высота строки в мм
        """
        # Если выравнивание не указано, используем левое для всех ячеек
        if aligns is None:
            aligns = ['L'] * len(data)
        
        # Устанавливаем шрифт для данных таблицы
        self.set_font('DejaVu', '', 10)
        
        # Восстанавливаем цвет текста (черный)
        self.set_text_color(0, 0, 0)
        
        # Устанавливаем высоту строки
        line_height = row_height
        
        # Рассчитываем максимальную длину текста для ячейки
        # Примерно 15-20 символов на 1 см ширины ячейки с учетом шрифта размером 10
        for i in range(len(data)):
            # Проверяем, что длина текста не превышает возможности ячейки
            text = str(data[i])
            text_width = self.get_string_width(text)
            
            # Если текст не помещается, уменьшаем шрифт
            if text_width > widths[i] - 4:  # 4 мм - отступы внутри ячейки
                self.set_font_size(9)  # Уменьшаем размер шрифта для компактности
                
                # Если даже уменьшенный шрифт не помещается, увеличиваем высоту строки
                text_width = self.get_string_width(text)
                if text_width > widths[i] - 4:
                    line_height = max(line_height, 10)  # Увеличиваем высоту строки
            
            self.cell(widths[i], line_height, text, 1, 0, aligns[i])
        
        self.ln()  # Переход на новую строку

def get_pergola_images(pergola_type):
    """
    Возвращает список путей к изображениям перголы указанного типа для использования в PDF
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B600, B700NEW)
        
    Returns:
        list: Список путей к изображениям перголы
    """
    # Создаем список для хранения путей к изображениям
    image_paths = []
    
    # Определяем базовый путь к изображениям в зависимости от типа перголы
    pergola_lower = pergola_type.lower().replace("new", "")
    base_image_dir = "assets"
    
    # Проверяем существование директории с изображениями
    if not os.path.exists(base_image_dir):
        print(f"Директория {base_image_dir} не найдена")
        return image_paths
    
    # Ищем изображения в директории assets, которые соответствуют типу перголы
    for filename in os.listdir(base_image_dir):
        filepath = os.path.join(base_image_dir, filename)
        # Ищем подходящие изображения по имени файла (содержит тип перголы)
        if os.path.isfile(filepath) and (pergola_lower in filename.lower() or pergola_type in filename):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                image_paths.append(filepath)
                print(f"Найдено изображение для PDF: {filepath}")
    
    # Если не нашли конкретные изображения для этого типа перголы, используем общие изображения
    if not image_paths:
        # Ищем общие изображения пергол
        for filename in os.listdir(base_image_dir):
            filepath = os.path.join(base_image_dir, filename)
            if os.path.isfile(filepath) and 'pergola' in filename.lower():
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    image_paths.append(filepath)
                    print(f"Найдено общее изображение перголы для PDF: {filepath}")
    
    # Если все еще нет изображений, проверяем в attached_assets
    if not image_paths and os.path.exists('attached_assets'):
        for filename in os.listdir('attached_assets'):
            filepath = os.path.join('attached_assets', filename)
            if os.path.isfile(filepath) and (pergola_lower in filename.lower() or 
                                            pergola_type in filename or 
                                            'pergola' in filename.lower()):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    image_paths.append(filepath)
                    print(f"Найдено изображение в attached_assets для PDF: {filepath}")
    
    return image_paths

def get_pergola_image_caption(pergola_type):
    """
    Возвращает подпись для галереи изображений в PDF
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B600, B700NEW)
        
    Returns:
        str: Подпись для галереи изображений
    """
    captions = {
        "B500NEW": "Биоклиматическая пергола серии B500 с поворотными ламелями",
        "B600": "Биоклиматическая пергола серии B600 со сдвижной крышей",
        "B700NEW": "Биоклиматическая пергола премиум-класса серии B700 с поворотными ламелями"
    }
    
    return captions.get(pergola_type, "Биоклиматическая пергола")

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
    # Добавляем логирование для отладки
    import logging
    logging.info(f"[format_pergola_data_for_pdf] Received dimensions: {dimensions}")
    logging.info(f"[format_pergola_data_for_pdf] Width from dimensions: {dimensions.get('width', 'No width')}")
    logging.info(f"[format_pergola_data_for_pdf] Length from dimensions: {dimensions.get('length', 'No length')}")
    pergola_data = {}
    
    # Базовая информация о перголе
    pergola_data["pergola_type"] = options["pergola_type"]
    pergola_data["lamella_type"] = options["lamella_type"]
    pergola_data["width"] = dimensions["width"]
    pergola_data["length"] = dimensions["length"]
    pergola_data["modules"] = dimensions["modules"]
    
    # Стоимость перголы
    pergola_data["base_price"] = results["base_price"]
    pergola_data["total_cost"] = results["total_price"]
    pergola_data["euro_rate"] = 110  # Хардкодим для простоты
    
    # Добавляем спецификацию перголы
    if "specification" in results:
        specification = []
        for item in results["specification"]:
            specification.append({
                "name": item["name"],
                "count": item["count"]
            })
        pergola_data["specification"] = specification
    
    # Добавляем позиции для таблицы стоимости
    if "items" in results:
        # Добавляем подробное логирование для понимания проблемы с разными суммами
        logging.info(f"[format_pergola_data_for_pdf] Items count: {len(results['items'])}")
        for i, item in enumerate(results['items']):
            logging.info(f"[format_pergola_data_for_pdf] Item {i+1}: {item.get('name', 'No name')} - {item.get('price', 0)}")
        
        # Получаем все существующие ключи для основного элемента (перголы)
        if len(results['items']) > 0:
            base_item = results['items'][0]  # Первый элемент обычно сама пергола
            logging.info(f"[format_pergola_data_for_pdf] Base item keys: {base_item.keys()}")
        
        # Проверяем, есть ли скидка
        discount = results.get('discount', 0)
        logging.info(f"[format_pergola_data_for_pdf] Discount: {discount}")
        
        # Проверяем итоговую стоимость
        total_price = results.get('total_price', 0)
        total_price_after_discount = results.get('total_price_after_discount', 0)
        logging.info(f"[format_pergola_data_for_pdf] Total price: {total_price}")
        logging.info(f"[format_pergola_data_for_pdf] Total price after discount: {total_price_after_discount}")
        
        # Теперь передаем элементы для PDF
        pergola_data["items"] = results["items"]
        
        # Добавляем информацию о скидке, если она есть
        pergola_data["discount"] = discount
        pergola_data["total_price_after_discount"] = total_price_after_discount
    
    # Добавляем текстовые описания
    pergola_data["description"] = pergola_description
    
    # Добавляем все описания для PDF
    from config.pergola_descriptions import (
        get_modular_system_description,
        get_drainage_system_description,
        get_bansbach_description,
        get_somfy_description,
        get_lamella_engineering_description,
        get_installation_system_description
    )
    
    # Добавляем дополнительные описания
    pergola_data["modular_description"] = get_modular_system_description()
    pergola_data["drainage_description"] = get_drainage_system_description()
    
    # Добавляем описания технических характеристик
    pergola_data["lamella_engineering_description"] = get_lamella_engineering_description()
    pergola_data["installation_system_description"] = get_installation_system_description()
    
    # Добавляем описания приводов в зависимости от типа перголы
    if options["pergola_type"] == "B500NEW":
        pergola_data["drive_description"] = get_bansbach_description()
    elif options["pergola_type"] == "B700NEW":
        pergola_data["drive_description"] = get_somfy_description()
    
    # Добавляем пути к изображениям
    pergola_data["image_paths"] = get_pergola_images(options["pergola_type"])
    pergola_data["image_caption"] = get_pergola_image_caption(options["pergola_type"])
    
    return pergola_data

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
    # Добавляем логирование для отладки
    import logging
    logging.info(f"[generate_commercial_offer] Received pergola_data: {pergola_data}")
    logging.info(f"[generate_commercial_offer] Width from pergola_data: {pergola_data.get('width', 'No width')}")
    logging.info(f"[generate_commercial_offer] Length from pergola_data: {pergola_data.get('length', 'No length')}")
    try:
        # Очищаем временные файлы обработанных изображений
        for file in os.listdir("processed_images"):
            if file.startswith("proc_"):
                try:
                    os.remove(os.path.join("processed_images", file))
                except:
                    pass
        
        # Создаем уникальное имя файла на основе текущей даты и времени
        now_utc = datetime.now(pytz.utc)
        now_rostov = now_utc.astimezone(ROSTOV_TZ)
        timestamp = now_rostov.strftime("%Y%m%d_%H%M%S")
        
        # Форматируем текущую дату для отображения в документе
        current_date = now_rostov.strftime("%d.%m.%Y")
        
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
        pdf.cell(0, 5, f"г.Ростов-на-Дону, {current_date}", 0, 1, "L")
        
        # Добавляем номер коммерческого предложения
        pdf.ln(5)
        pdf.cell(0, 5, f"№ {timestamp[:8]}", 0, 1, "L")
        
        # Добавляем заголовок коммерческого предложения
        pdf.ln(10)
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, "C")
        
        # Добавляем подзаголовок
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 8, "на поставку и монтаж биоклиматической перголы", 0, 1, "C")
        
        # Добавляем информацию о заказчике, если она предоставлена
        if user_data:
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', 11)
            pdf.cell(0, 7, "Данные заказчика:", 0, 1, "L")
            
            pdf.set_font('DejaVu', '', 10)
            if user_data.get('name'):
                pdf.cell(0, 5, f"ФИО: {user_data['name']}", 0, 1, "L")
            if user_data.get('phone'):
                pdf.cell(0, 5, f"Телефон: {user_data['phone']}", 0, 1, "L")
            if user_data.get('email'):
                pdf.cell(0, 5, f"Email: {user_data['email']}", 0, 1, "L")
            if user_data.get('address'):
                pdf.cell(0, 5, f"Адрес: {user_data['address']}", 0, 1, "L")
                
        # Добавляем основную информацию о перголе
        pdf.ln(10)
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 8, "Параметры перголы:", 0, 1, "L")
        
        pergola_type = pergola_data.get('pergola_type', 'Биоклиматическая пергола')
        width = pergola_data.get('width', 0)
        length = pergola_data.get('length', 0)
        
        pdf.set_font('DejaVu', '', 11)
        pdf.cell(50, 7, "Модель:", 0, 0, "L")
        pdf.cell(0, 7, pergola_type, 0, 1, "L")
        
        pdf.cell(50, 7, "Ширина:", 0, 0, "L")
        pdf.cell(0, 7, f"{width} м", 0, 1, "L")
        
        pdf.cell(50, 7, "Вынос (длина):", 0, 0, "L")
        pdf.cell(0, 7, f"{length} м", 0, 1, "L")
        
        modules = pergola_data.get('modules', 1)
        lamella_type = pergola_data.get('lamella_type', 'стандартные')
        
        pdf.cell(50, 7, "Количество модулей:", 0, 0, "L")
        pdf.cell(0, 7, f"{modules}", 0, 1, "L")
        
        pdf.cell(50, 7, "Тип ламелей:", 0, 0, "L")
        pdf.cell(0, 7, lamella_type, 0, 1, "L")
        
        # Добавляем специификацию, если она есть
        specification = pergola_data.get('specification', [])
        if specification:
            # Добавляем отступ перед спецификацией (без разрыва страницы)
            pdf.ln(10)
            
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 8, "Спецификация:", 0, 1, "L")
            
            # Проверяем, поместится ли таблица на текущей странице
            # Предварительно оцениваем возможную дополнительную высоту из-за многострочного текста
            # Для длинных названий компонентов (длиннее 80 символов) добавляем дополнительную высоту
            
            additional_height = 0
            for item in specification:
                name = item.get('name', '')
                # Если название длинное, добавляем дополнительную высоту
                if len(name) > 80:
                    # Примерно +6мм на каждые дополнительные 40 символов
                    additional_lines = len(name) // 40
                    additional_height += additional_lines * 6
            
            # Если таблица не помещается, добавляем новую страницу
            # Передаем дополнительную высоту в качестве параметра
            if pdf.check_table_fit(len(specification) + 3, additional_height=additional_height):
                # Таблица поместится (функция возвращает True) - ничего не делаем
                pass
            
            # Заголовки таблицы
            table_headers = ["№", "Наименование", "Количество"]
            widths = [10, 100, 60]  # Ширины колонок в мм
            
            pdf.table_header(table_headers, widths)
            
            # Данные таблицы с улучшенной поддержкой переноса текста
            for i, item in enumerate(specification, 1):
                name = item.get('name', '')
                count = item.get('count', '')
                # Используем multi_cell_row вместо table_row для лучшего переноса текста
                pdf.multi_cell_row([str(i), name, str(count)], widths, aligns=["C", "L", "C"], min_row_height=8)
            
        # Добавляем стоимость, если она есть
        items = pergola_data.get('items', [])
        if items:
            # Проверяем, достаточно ли места для раздела "Стоимость" на текущей странице
            # Оцениваем необходимое пространство: заголовок (8мм) + отступ (10мм) + 
            # таблица (высота строки * количество строк + заголовок таблицы)
            needed_space = 8 + 10 + (len(items) * 8) + 10
            
            # Получаем текущую позицию Y и оцениваем оставшееся пространство
            current_y = pdf.get_y()
            remaining_space = 272 - current_y  # 272мм - примерная нижняя граница страницы
            
            # Если места достаточно, добавляем отступ перед новым разделом
            # иначе - добавляем новую страницу
            if remaining_space >= needed_space:
                pdf.ln(10)  # Отступ перед разделом "Стоимость"
            else:
                pdf.add_page()
            
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 8, "Стоимость:", 0, 1, "L")
            
            # Проверяем, поместится ли таблица на текущей странице
            # В среднем строка занимает 8 мм, заголовок и отступы - ещё 20 мм
            
            # Оцениваем дополнительную высоту для длинных названий
            additional_height = 0
            for item in items:
                name = item.get('name', '')
                # Если название длинное, добавляем дополнительную высоту
                if len(name) > 80:
                    # Примерно +6мм на каждые дополнительные 40 символов
                    additional_lines = len(name) // 40
                    additional_height += additional_lines * 6
                    
            # Если таблица не помещается, добавляем новую страницу
            if pdf.check_table_fit(len(items) + 2, additional_height=additional_height):
                # Таблица поместится (функция возвращает True) - ничего не делаем
                pass
            
            # Заголовки таблицы
            table_headers = ["№", "Наименование", "Стоимость"]
            widths = [10, 110, 50]  # Ширины колонок в мм
            
            pdf.table_header(table_headers, widths)
            
            # Данные таблицы
            total_cost = 0
            for i, item in enumerate(items, 1):
                name = item.get('name', '')
                price = item.get('price', 0)
                price_value = int(price * pergola_data.get('euro_rate', 110))
                total_cost += price_value
                
                # Форматируем цену в зависимости от ее размера для лучшей читаемости
                if price_value >= 1000000:
                    # Для миллионов: 1 000 000 ₽
                    price_str = f"{price_value:,d}".replace(',', ' ') + " ₽"
                elif price_value >= 1000:
                    # Для тысяч: 100 000 ₽
                    price_str = f"{price_value:,d}".replace(',', ' ') + " ₽"
                else:
                    # Для сотен: 100 ₽
                    price_str = f"{price_value} ₽"
                
                # Используем многострочную ячейку вместо обычной для лучшего переноса длинных текстов
                # Выравниваем текст по левому краю для удобства чтения
                pdf.multi_cell_row([str(i), name, price_str], widths, aligns=["C", "L", "R"], min_row_height=7)
                
            # Проверяем есть ли в данных скидка
            discount = pergola_data.get('discount', 0)
            total_price_after_discount = pergola_data.get('total_price_after_discount', 0)
            
            # Логируем для отладки
            logging.info(f"[generate_commercial_offer] Discount: {discount}")
            logging.info(f"[generate_commercial_offer] Total price after discount: {total_price_after_discount}")
            
            # 1. Сначала добавляем промежуточный итог (без скидки)
            pdf.set_fill_color(211, 211, 211)  # Светло-серый цвет
            pdf.set_font('DejaVu', 'B', 11)  # Увеличиваем шрифт для итоговой суммы
            pdf.set_text_color(0, 0, 0)  # Черный текст
            
            # Форматируем промежуточную итоговую цену
            total_price_value = int(total_cost)
            if total_price_value >= 1000000:
                # Для миллионов форматируем как "1 234 567 ₽"
                total_price_str = f"{total_price_value:,d}".replace(',', ' ') + " ₽"
            else:
                # Для других значений так же
                total_price_str = f"{total_price_value:,d}".replace(',', ' ') + " ₽"
            
            # Строка ИТОГО должна выглядеть как обычная строка, но с другим содержимым
            # Используем те же ширины столбцов, что и в основной таблице для единообразия
            pdf.cell(10, 10, "", 1, 0, "C", fill=True)  # Первая колонка - пустая
            pdf.cell(110, 10, "Итого:", 1, 0, "L", fill=True)  # Вторая колонка - "Итого:" с левым выравниванием
            pdf.cell(50, 10, total_price_str, 1, 1, "R", fill=True)  # Третья колонка - сумма с правым выравниванием
            
            # 2. Если есть скидка, добавляем строку со скидкой
            if discount > 0:
                # Форматируем скидку
                discount_value = int(discount)
                if discount_value >= 1000000:
                    discount_str = f"-{discount_value:,d}".replace(',', ' ') + " ₽"
                else:
                    discount_str = f"-{discount_value:,d}".replace(',', ' ') + " ₽"
                
                # Задаем светло-зеленый цвет для строки скидки
                pdf.set_fill_color(200, 255, 200)  # Светло-зеленый
                
                # Строка СКИДКА
                pdf.cell(10, 10, "", 1, 0, "C", fill=True)  # Первая колонка - пустая
                pdf.cell(110, 10, "Скидка по акции:", 1, 0, "L", fill=True)
                pdf.cell(50, 10, discount_str, 1, 1, "R", fill=True)
                
                # 3. Добавляем строку ИТОГО со скидкой жирным шрифтом
                pdf.set_fill_color(200, 255, 200)  # Сохраняем тот же цвет
                pdf.set_font('DejaVu', 'B', 12)  # Увеличиваем шрифт для финальной суммы
                
                # Форматируем конечную цену со скидкой
                final_price_value = int(total_price_after_discount) if total_price_after_discount else total_price_value - discount_value
                if final_price_value >= 1000000:
                    final_price_str = f"{final_price_value:,d}".replace(',', ' ') + " ₽"
                else:
                    final_price_str = f"{final_price_value:,d}".replace(',', ' ') + " ₽"
                
                # Строка финального ИТОГО
                pdf.cell(10, 10, "", 1, 0, "C", fill=True)  # Первая колонка - пустая
                pdf.cell(110, 10, "ИТОГО:", 1, 0, "L", fill=True)  # Вторая колонка - "ИТОГО:" с левым выравниванием
                pdf.cell(50, 10, final_price_str, 1, 1, "R", fill=True)  # Третья колонка - сумма с правым выравниванием
            
            # Сброс цвета текста и заливки
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        # Добавляем примечания после таблицы стоимости
        pdf.ln(10)  # Отступ перед примечаниями
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, "Примечания:", 0, 1, "L")
        
        # Настраиваем шрифт для текста примечаний
        pdf.set_font('DejaVu', '', 10)
        
        # Добавляем каждое примечание отдельной строкой с нумерацией
        remarks = [
            "Расчет является предварительным и может быть уточнен при обращении в компанию.",
            "Срок действия предложения: 14 дней с даты расчета.",
            "Срок поставки: 6 недель с момента подтверждения заказа.",
            "Условия оплаты: 80% предоплата, 20% после монтажа."
        ]
        
        for i, remark in enumerate(remarks, 1):
            pdf.cell(0, 7, f"{i}. {remark}", 0, 1, "L")
        
        # Добавляем описание перголы и дополнительные разделы на новой странице
        pdf.add_page()
        pdf.chapter_title("Описание перголы:")
        
        # Собираем все типы описаний
        descriptions = []
        
        # Основное описание перголы
        pergola_description = pergola_data.get('description', '')
        pergola_type = pergola_data.get('pergola_type', 'биоклиматическая')
        if pergola_description:
            descriptions.append(pergola_description)
            
        # Дополнительные описания
        modular_description = pergola_data.get('modular_description', '')
        if modular_description:
            descriptions.append(modular_description)
            
        drainage_description = pergola_data.get('drainage_description', '')
        if drainage_description:
            descriptions.append(drainage_description)
            
        # Технические описания ламелей и системы установки
        lamella_engineering_description = pergola_data.get('lamella_engineering_description', '')
        if lamella_engineering_description:
            descriptions.append(lamella_engineering_description)
            
        installation_system_description = pergola_data.get('installation_system_description', '')
        if installation_system_description:
            descriptions.append(installation_system_description)
            
        # Описания приводов (зависят от типа перголы)
        drive_description = pergola_data.get('drive_description', '')
        if drive_description:
            descriptions.append(drive_description)
            
        # Если описаний не нашлось, создаем базовое описание по умолчанию
        if not descriptions:
            pergola_description = """
            <div style='margin-top: 10px;'>
            <h2 style='font-size: 1.2rem;'>Биоклиматические перголы премиум-качества</h2>
            <div>
                <p>
                Биоклиматическая пергола представляет собой современное решение для обустройства открытых пространств, 
                сочетающее в себе элегантный дизайн и практичную функциональность. Ключевой элемент перголы - поворотные 
                алюминиевые ламели, которые позволяют регулировать поступление солнечного света и воздуха, создавая 
                комфортный микроклимат в любое время года.
                </p>
                <p>
                Конструкция перголы выполнена из высококачественного экструдированного алюминия с порошковым покрытием, 
                что обеспечивает долговечность и устойчивость к коррозии. Система оснащена автоматическим приводом, который 
                позволяет управлять положением ламелей с помощью пульта дистанционного управления.
                </p>
                <div>
                <strong>Технические характеристики:</strong><br/>
                • Алюминиевый профиль: экструдированный алюминий с порошковым покрытием (322х260 мм)<br/>
                • Размеры колонны: 164x164 мм, используется 7 различных типов алюминиевых профилей<br/>
                • Система автоматизации: приводной механизм высокого качества, работающий от электросети
                </div>
                </div>
                </div>
                """
        
        # Печатаем весь HTML-текст для отладки
        print("ПОЛНОЕ ОПИСАНИЕ ПЕРГОЛЫ:")
        print(pergola_description)
        
        # Обрабатываем все блоки описаний последовательно
        for section_index, html_description in enumerate(descriptions):
            # Добавляем разрыв страницы между разными описаниями (кроме первого)
            if section_index > 0:
                pdf.add_page()
                # Если у нас более одного раздела, добавляем заголовки для дополнительных
                section_titles = {
                    1: "Модульная система пергол:",
                    2: "Система водоотведения:",
                    3: "Инженерные характеристики ламелей:",
                    4: "Система установки и проектирования:",
                    5: "Привод и автоматика:"
                }
                if section_index in section_titles:
                    pdf.chapter_title(section_titles[section_index])
            
            # HTML-описание нужно преобразовать в чистый текст более эффективным способом
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_description, 'html.parser')
                
                # Сначала обрабатываем заголовок и печатаем его для отладки
                pdf.set_font('DejaVu', 'B', 12)  # Больший размер шрифта для заголовка
                
                # Проверяем, есть ли заголовок h2 или h3 в описании
                title_tag = soup.find(['h2', 'h3'])
                if title_tag:
                    title_text = title_tag.get_text().strip()
                    print(f"Заголовок описания: {title_text}")
                    pdf.multi_cell(0, 5, title_text)
                    pdf.ln(3)
                elif section_index == 0:  # Только для первого раздела используем тип перголы
                    # Если заголовка нет, используем тип перголы как заголовок
                    if "B500" in pergola_type:
                        title_text = "Серия B500NEW (с поворотными ламелями)"
                    elif "B700" in pergola_type:
                        title_text = "Серия B700NEW (со сдвижными ламелями)"
                    elif "B600" in pergola_type:
                        title_text = "Серия B600 (с PIR-панелями)"
                    else:
                        title_text = f"Пергола {pergola_type}"
                    
                    pdf.multi_cell(0, 5, title_text)
                    pdf.ln(3)
                
                # Перерабатываем обычный текст
                pdf.set_font('DejaVu', '', 10)  # Обычный размер для основного текста
                
                # Получаем все параграфы
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text:  # Проверяем, что текст не пустой
                        # Разбиваем длинные параграфы на части для лучшей обработки
                        while len(text) > 0:
                            chunk = text[:400]  # Берем часть текста
                            text = text[400:]   # Оставшийся текст
                            pdf.multi_cell(0, 5, chunk)
                        pdf.ln(3)  # Отступ после параграфа
                
                # Получаем все списки
                lists = soup.find_all(['ul', 'ol'])
                for lst in lists:
                    pdf.ln(2)  # Небольшой отступ перед списком
                    
                    # Определяем тип списка
                    is_ordered = lst.name == 'ol'
                    
                    # Получаем все элементы списка
                    list_items = lst.find_all('li')
                    for i, li in enumerate(list_items, 1):
                        text = li.get_text().strip()
                        if is_ordered:
                            text = f"{i}. {text}"
                        else:
                            text = f"• {text}"
                            
                        # Разбиваем длинные элементы списка на части
                        first_line = True
                        while len(text) > 0:
                            chunk = text[:400]  # Берем часть текста
                            text = text[400:]   # Оставшийся текст
                            
                            if first_line:
                                pdf.multi_cell(0, 5, chunk)
                                first_line = False
                            else:
                                # Для второй и последующих строк делаем отступ
                                pdf.multi_cell(0, 5, f"  {chunk}")
                        
                    pdf.ln(3)  # Отступ после списка
                
                # Обрабатываем изображения
                images = soup.find_all('img')
                for img in images:
                    img_path = img.get('src', '')
                    # Проверяем, существует ли путь и доступен ли он
                    if img_path and os.path.exists(img_path):
                        # Получаем подпись к изображению из атрибута alt
                        caption = img.get('alt', '')
                        
                        # Обрабатываем изображение
                        try:
                            from PIL import Image
                            
                            # Открываем изображение и определяем его размеры
                            img_obj = Image.open(img_path)
                            width, height = img_obj.size
                            
                            # Вычисляем размеры для PDF (в мм)
                            max_width_mm = 170  # Максимальная ширина изображения в PDF (A4 - поля)
                            ratio = height / width
                            
                            # Если изображение шире максимума, масштабируем
                            if width > max_width_mm * 3:  # Умножаем на 3 для примерного перевода из мм в пиксели
                                img_width_mm = max_width_mm
                                img_height_mm = max_width_mm * ratio
                            else:
                                # Используем реальные размеры, переведенные в мм (примерно)
                                img_width_mm = width / 3
                                img_height_mm = height / 3
                            
                            # Проверяем, поместится ли изображение на текущей странице
                            if pdf.get_y() + img_height_mm + 20 > 277:  # 277 мм - высота страницы A4 с учетом полей
                                pdf.add_page()
                            
                            # Добавляем отступ перед изображением
                            pdf.ln(5)
                            
                            # Добавляем подпись к изображению
                            if caption:
                                pdf.set_font('DejaVu', 'B', 11)
                                pdf.cell(0, 8, caption, 0, 1, "C")
                                pdf.ln(5)
                            
                            # Вставляем изображение с явным указанием ширины и высоты
                            # для гарантии сохранения пропорций
                            pdf.image(
                                img_path,
                                x=(210 - img_width_mm) / 2,  # центрируем
                                y=pdf.get_y(),  # текущая позиция Y
                                w=img_width_mm,  # ширина
                                h=img_height_mm  # высота, рассчитанная с сохранением пропорций
                            )
                            print(f"Добавлено изображение в PDF: {img_path}")
                        except Exception as e:
                            print(f"Ошибка при обработке изображения {img_path}: {str(e)}")
                    else:
                        print(f"Изображение не найдено: {img_path}")
            except Exception as e:
                print(f"Ошибка при обработке HTML: {str(e)}")
        
        # Добавляем отдельный раздел с изображениями перголы из pergola_data
        image_paths = pergola_data.get('image_paths', [])
        image_caption = pergola_data.get('image_caption', '')
        
        if image_paths:
            # Начинаем новую страницу для галереи изображений
            pdf.add_page()
            pdf.chapter_title("Галерея изображений:")
            
            # Добавляем пояснение с типом перголы
            if image_caption:
                pdf.set_font('DejaVu', 'I', 11)
                pdf.cell(0, 8, image_caption, 0, 1, "C")
                pdf.ln(5)
            
            # Обрабатываем все изображения из списка
            for img_path in image_paths:
                if os.path.exists(img_path):
                    try:
                        from PIL import Image
                        
                        # Открываем изображение и определяем его размеры
                        img_obj = Image.open(img_path)
                        width, height = img_obj.size
                        
                        # Определяем ширину в миллиметрах для PDF (A4: 210x297 мм)
                        max_width_mm = 170  # Максимальная ширина в мм (с учетом полей)
                        max_height_mm = 240  # Максимальная высота в мм (с учетом полей)
                        
                        # Рассчитываем размеры с сохранением пропорций
                        img_width_mm = max_width_mm
                        img_height_mm = height * (img_width_mm / width)
                        
                        # Если высота слишком большая, пересчитываем размеры
                        if img_height_mm > max_height_mm:
                            img_height_mm = max_height_mm
                            img_width_mm = width * (img_height_mm / height)
                        
                        # Добавляем отступ перед изображением
                        pdf.ln(5)
                        
                        # Проверяем, поместится ли изображение на текущей странице
                        if pdf.get_y() + img_height_mm + 10 > 270:  # 270 = 297 - нижнее поле
                            pdf.add_page()
                        
                        # Вставляем изображение с явным указанием ширины и высоты
                        pdf.image(
                            img_path,
                            x=(210 - img_width_mm) / 2,  # центрируем
                            y=pdf.get_y(),  # текущая позиция Y
                            w=img_width_mm,  # ширина
                            h=img_height_mm  # высота, рассчитанная с сохранением пропорций
                        )
                        
                        # Добавляем отступ после изображения
                        pdf.ln(10)
                        print(f"Добавлено изображение в PDF: {img_path}")
                    except Exception as e:
                        print(f"Ошибка при обработке изображения {img_path}: {str(e)}")
                else:
                    print(f"Изображение не найдено: {img_path}")
        
        # Добавляем контактную информацию - проверяем, может ли она поместиться на текущей странице
        # Примерный размер для контактной информации (6 строк по 7 мм + заголовок и отступы)
        contact_info_height = 60
        
        # Проверяем, поместится ли контактная информация на текущей странице
        if 297 - pdf.get_y() < contact_info_height:
            pdf.add_page()
        else:
            pdf.ln(15)  # Добавляем отступ перед контактной информацией
            
        pdf.chapter_title("Контактная информация:")
        
        pdf.set_font('DejaVu', '', 10)  # Уменьшаем размер шрифта для экономии места
        pdf.multi_cell(0, 5, "Для получения дополнительной информации или оформления заказа, пожалуйста, свяжитесь с нами:")
        pdf.ln(3)
        
        contact_info = [
            "Телефон: +7 (906) 429-74-20",
            "Email: zakaz@infopergola.ru",
            "Веб-сайт: https://pergolamarket.ru",
            "Адрес: г.Ростов-на-Дону, ул.Орская, 27\\1"
        ]
        
        for info in contact_info:
            pdf.cell(0, 6, info, 0, 1)  # Уменьшаем высоту строк с 7 до 6 мм
        
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
            
            # Заголовок документа
            simple_pdf.set_font('Arial', 'B', 16)
            simple_pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, 'C')
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.cell(0, 10, "на поставку и монтаж биоклиматической перголы", 0, 1, 'C')
            simple_pdf.ln(10)
            
            # Основная информация
            simple_pdf.set_font('Arial', 'B', 14)
            simple_pdf.cell(0, 10, "Параметры перголы:", 0, 1, 'L')
            
            # Таблица параметров
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.cell(70, 10, "Модель:", 0, 0)
            simple_pdf.cell(0, 10, p_type, 0, 1)
            
            simple_pdf.cell(70, 10, "Ширина:", 0, 0)
            simple_pdf.cell(0, 10, f"{p_width} м", 0, 1)
            
            simple_pdf.cell(70, 10, "Вынос (длина):", 0, 0)
            simple_pdf.cell(0, 10, f"{p_length} м", 0, 1)
            
            # Стоимость
            simple_pdf.ln(5)
            simple_pdf.set_fill_color(240, 240, 240)
            simple_pdf.set_font('Arial', 'B', 14)
            
            # Форматируем стоимость в полном формате
            price_value = int(p_cost)
            if price_value >= 1000000:
                # Для миллионов форматируем как "1 234 567 рублей"
                price_str = f"{price_value:,d}".replace(',', ' ') + " рублей"
            else:
                # Для других значений так же
                price_str = f"{price_value:,d}".replace(',', ' ') + " рублей"
                
            simple_pdf.cell(0, 10, f"Общая стоимость: {price_str}", 1, 1, 'C', fill=True)
            
            # Заметка о версии документа
            simple_pdf.ln(15)
            simple_pdf.set_font('Arial', 'I', 10)
            simple_pdf.cell(0, 10, "Данный документ является упрощенной версией коммерческого предложения.", 0, 1)
            simple_pdf.cell(0, 10, "Для получения полного предложения с детальным описанием, пожалуйста, свяжитесь с нами.", 0, 1)
            
            # Контактная информация
            simple_pdf.ln(10)
            simple_pdf.set_font('Arial', 'B', 12)
            simple_pdf.cell(0, 10, "Контактная информация:", 0, 1)
            
            simple_pdf.set_font('Arial', '', 10)
            simple_pdf.cell(0, 7, "Телефон: +7 (906) 429-74-20", 0, 1)
            simple_pdf.cell(0, 7, "Email: zakaz@infopergola.ru", 0, 1)
            simple_pdf.cell(0, 7, "Веб-сайт: https://pergolamarket.ru", 0, 1)
            simple_pdf.cell(0, 7, "Адрес: г.Ростов-на-Дону, ул.Орская, 27\\1", 0, 1)
            
            # Сохраняем упрощенный PDF в дефолтную директорию
            backup_filename = f"generated_pdf/KP_Pergola_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
            simple_pdf.output(backup_filename)
            print(f"Упрощенный PDF создан: {backup_filename}")
            
            return backup_filename
            
        except Exception as e2:
            print(f"Ошибка при создании упрощенного PDF: {str(e2)}")
            return None