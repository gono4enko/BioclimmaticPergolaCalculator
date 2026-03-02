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
        
    def header(self):
        """Создает верхний колонтитул на каждой странице"""
        # Ничего не делаем в хедере для первой страницы
        if self.page_no() > 1:
            # Логотип в верхнем левом углу
            self.set_y(10)
            self.set_font('DejaVu', 'B', 15)
            self.cell(0, 10, 'Биоклиматические перголы', 0, 0, 'L')
            
            # Линия под заголовком
            self.line(20, 20, 190, 20)
            
            # Устанавливаем позицию для начала основного текста
            self.set_y(25)
    
    def footer(self):
        """Создает нижний колонтитул на каждой странице"""
        # Позиция на 1.5 см от нижнего края
        self.set_y(-15)
        self.set_font('DejaVu', '', 7)
        self.cell(0, 4, 'Компания «Комфортный дом» | Комплексные решения для обустройства террас, веранд и беседок.', 0, 1, 'C')
        self.cell(0, 4, 'ИП Гоноченко А.В. ОГРНИП 321619600249231 | Тел.: +7-906-429-74-20 | Сайт: pergolamarket.ru', 0, 0, 'C')
    
    def chapter_title(self, title):
        """Добавляет заголовок раздела"""
        self.set_font('DejaVu', 'B', 14)
        self.set_fill_color(230, 230, 230)  # Светло-серый фон
        self.cell(0, 9, title, 0, 1, 'L', 1)
        self.ln(3)  # Отступ после заголовка
    
    def check_table_fit(self, rows_count, row_height=8):
        """
        Проверяет, поместится ли таблица на текущей странице
        Если не поместится - добавляет новую страницу
        
        Args:
            rows_count (int): Количество строк в таблице
            row_height (int): Высота одной строки в мм
            
        Returns:
            bool: True если таблица помещается, False если добавлена новая страница
        """
        # Примерная высота таблицы: высота строки * кол-во строк + запас 15 мм на заголовки и отступы
        table_height = rows_count * row_height + 15
        
        # Получаем текущую позицию Y (высоту от начала страницы)
        current_y = self.get_y()
        
        # Рассчитываем оставшееся пространство на странице
        page_bottom = 277  # Примерная нижняя граница страницы A4 с учетом полей и футера
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
    
    def table_row(self, data, widths, aligns=None, row_height=7):
        if aligns is None:
            aligns = ['L'] * len(data)

        self.set_font('DejaVu', '', 9)
        self.set_text_color(0, 0, 0)
        lh = row_height

        needs_wrap = False
        for i in range(len(data)):
            text = str(data[i])
            tw = self.get_string_width(text)
            if tw > widths[i] - 4:
                needs_wrap = True
                break

        if not needs_wrap:
            for i in range(len(data)):
                self.cell(widths[i], lh, str(data[i]), 1, 0, aligns[i])
            self.ln()
            return

        x_start = self.get_x()
        y_start = self.get_y()
        max_h = lh

        for i in range(len(data)):
            text = str(data[i])
            tw = self.get_string_width(text)
            if tw > widths[i] - 4:
                lines = self.multi_cell(widths[i] - 2, lh, text, 0, 'L', split_only=True)
                cell_h = len(lines) * lh
                if cell_h > max_h:
                    max_h = cell_h

        for i in range(len(data)):
            text = str(data[i])
            tw = self.get_string_width(text)
            cx = x_start + sum(widths[:i])
            self.rect(cx, y_start, widths[i], max_h)
            if tw > widths[i] - 4:
                self.set_xy(cx + 1, y_start)
                self.multi_cell(widths[i] - 2, lh, text, 0, aligns[i])
            else:
                self.set_xy(cx, y_start + (max_h - lh) / 2)
                self.cell(widths[i], lh, text, 0, 0, aligns[i])

        self.set_xy(x_start, y_start + max_h)

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
    
    if "discount" in results and results["discount"] > 0:
        pergola_data["discount"] = results["discount"]
        pergola_data["total_price_after_discount"] = results.get("total_price_after_discount", 0)
    
    # Добавляем позиции для таблицы стоимости
    if "items" in results:
        pergola_data["items"] = results["items"]
    
    # Добавляем текстовые описания
    pergola_data["description"] = pergola_description
    
    # Дополнительно можно добавить модульное описание и описание системы водоотведения
    from config.pergola_descriptions import (
        get_modular_system_description,
        get_drainage_system_description,
        get_pergola_images,
        get_pergola_image_caption
    )
    
    # Добавляем дополнительные описания
    pergola_data["modular_description"] = get_modular_system_description()
    pergola_data["drainage_description"] = get_drainage_system_description()
    
    # Добавляем пути к изображениям
    pergola_data["image_paths"] = get_pergola_images(options["pergola_type"])
    pergola_data["image_caption"] = get_pergola_image_caption(options["pergola_type"])
    
    return pergola_data


def _compress_image_for_pdf(img_path, max_width=800, quality=60, crop_ratio=None):
    """Сжимает изображение для PDF, возвращает путь к сжатому файлу.
    crop_ratio: если задан (w/h), обрезает изображение до этого соотношения сторон."""
    try:
        from PIL import Image as PILImage
        img = PILImage.open(img_path)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        w, h = img.size
        if crop_ratio:
            target_h = int(w / crop_ratio)
            if target_h > h:
                target_w = int(h * crop_ratio)
                left = (w - target_w) // 2
                img = img.crop((left, 0, left + target_w, h))
            else:
                top = (h - target_h) // 2
                img = img.crop((0, top, w, top + target_h))
            w, h = img.size
        if w > max_width:
            ratio = max_width / w
            img = img.resize((max_width, int(h * ratio)), PILImage.LANCZOS)
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(tmp.name, 'JPEG', quality=quality, optimize=True)
        return tmp.name
    except Exception:
        return img_path


def _add_section_images_grid(pdf, image_paths):
    from PIL import Image as PILImage
    valid = []
    for p in image_paths:
        if os.path.exists(p):
            valid.append(p)
        else:
            print(f"Изображение секции не найдено: {p}")
    if not valid:
        return

    page_w = 190
    page_bottom = 245
    gap = 4
    start_y = pdf.get_y() + 2
    available_h = page_bottom - start_y

    layout = []
    for img_path in valid:
        try:
            img_obj = PILImage.open(img_path)
            w, h = img_obj.size
            layout.append((img_path, w / h))
        except Exception:
            layout.append((img_path, 1.5))

    row1_h = 70
    row2_h = 55
    total_needed = row1_h + row2_h + gap

    if total_needed > available_h:
        scale = available_h / total_needed
        row1_h *= scale
        row2_h *= scale

    if row1_h < 15:
        pdf.add_page()
        start_y = pdf.get_y() + 2
        available_h = page_bottom - start_y
        scale = min(1.0, available_h / (70 + 55 + gap))
        row1_h = 70 * scale
        row2_h = 55 * scale

    cur_y = start_y

    if len(layout) >= 1:
        path0, ratio0 = layout[0]
        w0 = min(row1_h * ratio0, page_w * 0.55)
        compressed = _compress_image_for_pdf(path0, max_width=1000, quality=70)
        x0 = 10 + (page_w * 0.55 - w0) / 2
        pdf.image(compressed, x=x0, y=cur_y, w=w0, h=row1_h)

    if len(layout) >= 2:
        path1, ratio1 = layout[1]
        w1 = min(row1_h * ratio1, page_w * 0.42)
        compressed = _compress_image_for_pdf(path1, max_width=1000, quality=70)
        x1 = 10 + page_w * 0.58 + (page_w * 0.42 - w1) / 2
        pdf.image(compressed, x=x1, y=cur_y, w=w1, h=row1_h)

    cur_y += row1_h + gap

    if len(layout) >= 3:
        path2, ratio2 = layout[2]
        w2 = min(row2_h * ratio2, page_w * 0.48)
        compressed = _compress_image_for_pdf(path2, max_width=1000, quality=70)
        pdf.image(compressed, x=10, y=cur_y, w=w2, h=row2_h)

    if len(layout) >= 4:
        path3, ratio3 = layout[3]
        w3 = min(row2_h * ratio3, page_w * 0.48)
        compressed = _compress_image_for_pdf(path3, max_width=1000, quality=70)
        x3 = 10 + page_w - w3
        pdf.image(compressed, x=x3, y=cur_y, w=w3, h=row2_h)

    cur_y += row2_h + gap
    pdf.set_y(cur_y)


def _get_gallery_images(max_images=8):
    """Возвращает список (путь, подпись) для галереи в PDF."""
    IMAGES_DIR = "attached_assets"
    gallery_list = [
        ("IMG_5914.jpg", "Пергола B700 у бассейна, Крым"),
        ("pergola_b500_led_lighting.jpg", "Пергола B500 с LED подсветкой"),
        ("pergola_b700_poolside.jpg", "Пергола B700 у бассейна"),
        ("pergola_b500_garden_view.jpg", "Пергола B500 с видом на сад"),
        ("pergola_evening_lighting.jpg", "Пергола с вечерним освещением"),
        ("07dbd8458c61f3f439f3722e558aa6ee.jpg", "Пергола B700, загородный дом"),
        ("5bb7bcac6f5c8462c9cf10d78d650e57.jpg", "Пергола B600 с остеклением"),
        ("dji_fly_20230928_141856_69_1695900255932_photo_optimized_7813c639.jpg", "Аэрофотосъемка проекта"),
        ("IMG_0672_2_882acf32.jpg", "Проект перголы B500"),
        ("IMG_0676_52ddd353.jpg", "Проект перголы B700"),
        ("IMG_0748_827e14fe.jpg", "Проект перголы B700"),
        ("IMG_0782_da126d8f.jpg", "Проект перголы B600"),
    ]
    result = []
    for filename, caption in gallery_list:
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            result.append((path, caption))
            if len(result) >= max_images:
                break
    return result


def generate_commercial_offer(pergola_data, user_data=None):
    """
    Генерирует коммерческое предложение в формате PDF на основе 
    данных о перголе, полученных из калькулятора.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе, ее размерах, конфигурации и стоимости
        user_data (dict, optional): Словарь с данными пользователя (имя, телефон и т.д.)
        
    Returns:
        bytes: Байты PDF-документа (или None при ошибке)
    """
    try:
        for f in os.listdir("processed_images"):
            if f.startswith("proc_"):
                try:
                    os.remove(os.path.join("processed_images", f))
                except:
                    pass
        
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        current_date = now.strftime("%d.%m.%Y")
        
        # Создаем экземпляр PDF с поддержкой кириллицы
        pdf = PDF()
        
        # Добавляем первую страницу
        pdf.add_page()
        
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(95, 5, '', 0, 0, 'L')
        pdf.cell(0, 5, 'г.Ростов-на-Дону, ул.Орская, 27/1', 0, 1, 'R')
        pdf.cell(95, 5, '', 0, 0, 'L')
        pdf.cell(0, 5, 'моб. +7 (906) 429-74-20', 0, 1, 'R')
        
        pdf.set_font('DejaVu', 'B', 11)
        pdf.cell(95, 5, 'Компания «Комфортный дом»', 0, 0, 'L')
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(0, 5, 'E-mail: zakaz@infopergola.ru', 0, 1, 'R')
        pdf.cell(95, 5, '', 0, 0, 'L')
        pdf.cell(0, 5, 'Сайт: https://pergolamarket.ru/', 0, 1, 'R')
        
        pdf.ln(8)
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, "Коммерческое предложение о поставке", 0, 1, "C")
        pdf.cell(0, 8, "биоклиматической перголы", 0, 1, "C")
        
        pdf.ln(3)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 5, f"Дата расчета: {current_date}", 0, 1, "R")
        
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
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 8, "Спецификация:", 0, 1, "L")
            
            # Проверяем, поместится ли таблица на текущей странице
            # В среднем строка занимает 6-7 мм, заголовок и отступы - ещё 20 мм
            table_height = len(specification) * 6 + 20
            
            # Если таблица не помещается, добавляем новую страницу
            if pdf.check_table_fit(len(specification) + 3):
                # Таблица поместится (функция возвращает True) - ничего не делаем
                pass
            
            # Заголовки таблицы
            table_headers = ["№", "Наименование", "Количество"]
            widths = [10, 100, 60]  # Ширины колонок в мм
            
            pdf.table_header(table_headers, widths)
            
            # Данные таблицы
            for i, item in enumerate(specification, 1):
                name = item.get('name', '')
                count = item.get('count', '')
                pdf.table_row([str(i), name, str(count)], widths, aligns=["C", "L", "C"])
            
        # Добавляем стоимость, если она есть
        items = pergola_data.get('items', [])
        if items:
            pdf.add_page()
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 8, "Стоимость:", 0, 1, "L")
            
            # Проверяем, поместится ли таблица на текущей странице
            table_height = len(items) * 6 + 20
            
            # Если таблица не помещается, добавляем новую страницу
            if pdf.check_table_fit(len(items) + 3):
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
                
                # Используем уменьшенную высоту строки (6 мм вместо 8 мм)
                # Меняем выравнивание с R (правого) на L (левое) для соответствия таблице спецификации
                pdf.table_row([str(i), item['name'], price_str], widths, aligns=["C", "L", "L"], row_height=6)
                
            def _format_total(val):
                v = round(val)
                return f"{v:,d}".replace(',', ' ') + " ₽"
            
            discount = pergola_data.get('discount', 0)
            
            pdf.set_fill_color(211, 211, 211)
            pdf.set_font('DejaVu', 'B', 10)
            pdf.set_text_color(0, 0, 0)
            
            if discount and discount > 0:
                pdf.cell(10, 10, "", 1, 0, "C", fill=True)
                pdf.cell(83, 10, "ИТОГО:", 1, 0, "R", fill=True)
                pdf.cell(67, 10, _format_total(total_cost), 1, 1, "L", fill=True)
                
                pdf.set_font('DejaVu', 'B', 9)
                pdf.cell(10, 10, "", 1, 0, "C", fill=True)
                pdf.cell(83, 10, "Скидка по акции:", 1, 0, "R", fill=True)
                pdf.cell(67, 10, "-" + _format_total(discount), 1, 1, "L", fill=True)
                pdf.set_font('DejaVu', 'B', 10)
                
                cash_total = pergola_data.get('total_price_after_discount', total_cost - discount)
            else:
                cash_total = total_cost
            
            noncash_total = cash_total * 1.08
            vat_total = cash_total * 1.15
            
            pdf.cell(10, 10, "", 1, 0, "C", fill=True)
            pdf.cell(83, 10, "ИТОГО (Наличный расчёт):", 1, 0, "R", fill=True)
            pdf.cell(67, 10, _format_total(cash_total), 1, 1, "L", fill=True)
            
            pdf.cell(10, 10, "", 1, 0, "C", fill=True)
            pdf.cell(83, 10, "ИТОГО (Безналичный расчёт):", 1, 0, "R", fill=True)
            pdf.cell(67, 10, _format_total(noncash_total), 1, 1, "L", fill=True)
            
            pdf.cell(10, 10, "", 1, 0, "C", fill=True)
            pdf.cell(83, 10, "ИТОГО (С НДС 22%):", 1, 0, "R", fill=True)
            pdf.cell(67, 10, _format_total(vat_total), 1, 1, "L", fill=True)
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        # Добавляем описание перголы и дополнительные разделы
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
            
        bansbach_description = pergola_data.get('bansbach_description', '')
        if bansbach_description:
            descriptions.append(bansbach_description)
            
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
                if section_index == 1:
                    pdf.chapter_title("Модульная система пергол:")
                elif section_index == 2:
                    pdf.chapter_title("Система водоотведения:")
            
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
                            compressed = _compress_image_for_pdf(img_path, max_width=1000, quality=65)
                            pdf.image(
                                compressed,
                                x=(210 - img_width_mm) / 2,
                                y=pdf.get_y(),
                                w=img_width_mm,
                                h=img_height_mm
                            )
                            print(f"Добавлено изображение в PDF: {img_path}")
                        except Exception as e:
                            print(f"Ошибка при обработке изображения {img_path}: {str(e)}")
                    else:
                        print(f"Изображение не найдено: {img_path}")
                
                if section_index == 1:
                    all_section_imgs = [
                        "attached_assets/Modular_Design_1772474386813.png",
                        "attached_assets/Skyroof_Module_Connectors_1772474386813.jpg",
                        "attached_assets/Drainage_1772474555236.png",
                        "attached_assets/Skyroof_Drainage_1772474555236.png",
                    ]
                    _add_section_images_grid(pdf, all_section_imgs)
                    
            except Exception as e:
                print(f"Ошибка при обработке HTML: {str(e)}")
        
        gallery_images = _get_gallery_images()
        if gallery_images:
            pdf.add_page()
            pdf.chapter_title("Галерея наших работ:")
            pdf.ln(3)
            
            for i in range(0, len(gallery_images), 2):
                if pdf.get_y() + 75 > 277:
                    pdf.add_page()
                
                batch = gallery_images[i:i+2]
                
                if len(batch) == 2:
                    x_left = 15
                    x_right = 108
                    img_w = 85
                    y_start = pdf.get_y()
                    
                    gallery_img_w = 85
                    gallery_img_h = 60
                    gallery_crop = gallery_img_w / gallery_img_h
                    
                    for j, (img_path, caption) in enumerate(batch):
                        x = x_left if j == 0 else x_right
                        try:
                            compressed = _compress_image_for_pdf(img_path, max_width=600, quality=55, crop_ratio=gallery_crop)
                            pdf.image(compressed, x=x, y=y_start, w=gallery_img_w, h=gallery_img_h)
                            pdf.set_xy(x, y_start + gallery_img_h + 1)
                            pdf.set_font('DejaVu', '', 7)
                            pdf.cell(gallery_img_w, 4, caption[:60], 0, 0, 'C')
                        except Exception as e:
                            print(f"Ошибка добавления фото {img_path}: {e}")
                    
                    pdf.set_y(y_start + gallery_img_h + 10)
                else:
                    img_path, caption = batch[0]
                    try:
                        gallery_img_w = 85
                        gallery_img_h = 60
                        gallery_crop = gallery_img_w / gallery_img_h
                        compressed = _compress_image_for_pdf(img_path, max_width=600, quality=55, crop_ratio=gallery_crop)
                        x = (210 - gallery_img_w) / 2
                        pdf.image(compressed, x=x, y=pdf.get_y(), w=gallery_img_w, h=gallery_img_h)
                        pdf.set_y(pdf.get_y() + gallery_img_h + 1)
                        pdf.set_font('DejaVu', '', 7)
                        pdf.cell(0, 4, caption[:60], 0, 1, 'C')
                        pdf.ln(5)
                    except Exception as e:
                        print(f"Ошибка добавления фото {img_path}: {e}")
        
        contact_info_height = 80
        
        if 297 - pdf.get_y() < contact_info_height:
            pdf.add_page()
        else:
            pdf.ln(10)
            
        pdf.chapter_title("Примечания:")
        
        pdf.set_font('DejaVu', '', 10)
        notes = [
            "1. Расчет является предварительным и может быть уточнен при обращении в компанию.",
            "2. Срок действия предложения: 14 дней с даты расчета.",
            "3. Срок поставки: 6 недель с момента подтверждения заказа.",
            "4. Условия оплаты: 80% предоплата, 20% после монтажа.",
        ]
        for note in notes:
            pdf.cell(0, 6, note, 0, 1)
        
        pdf.ln(10)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('DejaVu', 'B', 11)
        pdf.cell(0, 6, 'Компания «Комфортный дом»', 0, 1, 'L')
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(0, 5, 'Комплексные решения для обустройства террас, веранд и беседок.', 0, 1, 'L')
        pdf.cell(0, 5, 'ИП Гоноченко А.В. ОГРНИП 321619600249231', 0, 1, 'L')
        pdf.cell(0, 5, 'Тел.: +7-906-429-74-20   Сайт: pergolamarket.ru', 0, 1, 'L')
        
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
        print(f"PDF успешно создан в памяти ({len(pdf_bytes)} байт)")
        return pdf_bytes
        
    except Exception as e:
        print(f"Ошибка при создании PDF: {str(e)}")
        
        try:
            from fpdf import FPDF
            
            p_type = pergola_data.get('pergola_type', '') if pergola_data else ''
            p_width = pergola_data.get('width', 0) if pergola_data else 0
            p_length = pergola_data.get('length', 0) if pergola_data else 0
            p_cost = pergola_data.get('total_cost', 0) if pergola_data else 0
            
            simple_pdf = FPDF()
            simple_pdf.add_page()
            simple_pdf.set_font('Arial', 'B', 16)
            simple_pdf.cell(0, 10, "Commercial Proposal - Pergola", 0, 1, 'C')
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.ln(10)
            simple_pdf.cell(70, 10, "Model:", 0, 0)
            simple_pdf.cell(0, 10, str(p_type), 0, 1)
            simple_pdf.cell(70, 10, "Width:", 0, 0)
            simple_pdf.cell(0, 10, f"{p_width} m", 0, 1)
            simple_pdf.cell(70, 10, "Length:", 0, 0)
            simple_pdf.cell(0, 10, f"{p_length} m", 0, 1)
            simple_pdf.ln(5)
            simple_pdf.set_font('Arial', 'B', 14)
            price_str = f"{int(p_cost):,d}".replace(',', ' ')
            simple_pdf.cell(0, 10, f"Total: {price_str} RUB", 1, 1, 'C', fill=True)
            
            fallback_bytes = simple_pdf.output(dest='S')
            if isinstance(fallback_bytes, str):
                fallback_bytes = fallback_bytes.encode('latin-1')
            print(f"Упрощенный PDF создан в памяти ({len(fallback_bytes)} байт)")
            return fallback_bytes
            
        except Exception as e2:
            print(f"Ошибка при создании упрощенного PDF: {str(e2)}")
            return None