"""
Модуль для генерации коммерческого предложения в формате PDF
на основе данных из калькулятора перголы.
Использует библиотеку FPDF для корректной работы с кириллицей.
"""
import os
import io
import re
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


GALLERY_BY_MODEL = {
    'b500': [
        'pergola_b500_led_lighting.jpg',
        'pergola_b500_garden_view.jpg',
        'pergola_evening_lighting.jpg',
        'IMG_0672_2_882acf32.jpg',
        'IMG_5914.jpg',
        'pergola_b700_poolside.jpg',
    ],
    'b700': [
        'IMG_5914.jpg',
        'pergola_b700_poolside.jpg',
        'pergola_panoramic_glass_walls.jpg',
        'pergola_evening_lighting.jpg',
        'IMG_0748_827e14fe.jpg',
        'pergola_b500_garden_view.jpg',
    ],
    'b600': [
        'pergola_panoramic_glass_walls.jpg',
        'IMG_0672_2_882acf32.jpg',
        'IMG_0748_827e14fe.jpg',
        'pergola_evening_lighting.jpg',
        'IMG_5914.jpg',
        'pergola_b700_poolside.jpg',
    ],
}

GALLERY_CAPTIONS = {
    'IMG_5914.jpg':                     'Пергола B700 у бассейна, Крым',
    'pergola_b500_led_lighting.jpg':    'Пергола B500 с LED подсветкой',
    'pergola_b700_poolside.jpg':        'Пергола B700 у бассейна',
    'pergola_b500_garden_view.jpg':     'Пергола B500, вид на сад',
    'pergola_evening_lighting.jpg':     'Вечернее освещение',
    'pergola_panoramic_glass_walls.jpg':'Пергола с раздвижным остеклением',
    'IMG_0672_2_882acf32.jpg':          'Реализованный проект',
    'IMG_0748_827e14fe.jpg':            'Реализованный проект',
}

def _get_gallery_images(max_images=6, model_key='b500'):
    """Возвращает список (путь, подпись) для галереи в PDF по модели."""
    GALLERY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_app', 'static', 'images', 'gallery')
    ASSETS_DIR = "attached_assets"
    model_list = GALLERY_BY_MODEL.get(model_key, GALLERY_BY_MODEL['b500'])
    result = []
    for filename in model_list:
        caption = GALLERY_CAPTIONS.get(filename, 'Реализованный проект')
        path = os.path.join(GALLERY_DIR, filename)
        if not os.path.exists(path):
            path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            result.append((path, caption))
            if len(result) >= max_images:
                break
    return result


def generate_commercial_offer(pergola_data, user_data=None, all_variants=None):
    """
    Генерирует коммерческое предложение в формате PDF на основе 
    данных о перголе, полученных из калькулятора.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе, ее размерах, конфигурации и стоимости
        user_data (dict, optional): Словарь с данными пользователя (имя, телефон и т.д.)
        all_variants (list, optional): Список dict-ов для режима "Все варианты"
        
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
        
        pdf = PDF()

        # ===== PAGE 1: HERO COVER =====
        pdf.add_page()

        pdf.set_fill_color(26, 58, 110)
        pdf.rect(0, 0, 210, 55, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('DejaVu', 'B', 20)
        pdf.set_y(15)
        pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, "C")
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 8, "о поставке биоклиматической перголы", 0, 1, "C")

        kp_number = pergola_data.get('kp_number', '')
        if kp_number:
            pdf.set_font('DejaVu', '', 9)
            pdf.cell(0, 6, f"КП № {kp_number}", 0, 1, "C")

        pdf.set_text_color(0, 0, 0)
        pdf.set_y(60)

        pergola_type_name = pergola_data.get('pergola_type', 'Биоклиматическая пергола')
        p_w = pergola_data.get('width', 0)
        p_l = pergola_data.get('length', 0)
        hero_img_key = pergola_type_name.lower().replace(' new', '').replace(' basic', '').replace(' light', '').replace(' pro', '').strip()
        base_img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_app', 'static', 'images')
        gallery_img_dir = os.path.join(base_img_dir, 'gallery')
        COVER_IMAGES = {
            'b500': [
                os.path.join(gallery_img_dir, 'pergola_b500_led_lighting.jpg'),
                os.path.join(gallery_img_dir, 'pergola_b500_garden_view.jpg'),
                os.path.join(base_img_dir, 'b500.jpg'),
            ],
            'b700': [
                os.path.join(gallery_img_dir, 'IMG_5914.jpg'),
                os.path.join(gallery_img_dir, 'pergola_b700_poolside.jpg'),
                os.path.join(base_img_dir, 'b700.jpg'),
            ],
            'b600': [
                os.path.join(base_img_dir, 'b600_sandwich.jpg'),
                os.path.join(base_img_dir, 'b600.jpg'),
            ],
        }
        hero_img_path = None
        for candidate in COVER_IMAGES.get(hero_img_key, []):
            if os.path.exists(candidate):
                hero_img_path = candidate
                break
        if not hero_img_path:
            hero_img_path = os.path.join(base_img_dir, 'hero_pergola.jpg')

        if os.path.exists(hero_img_path):
            try:
                compressed = _compress_image_for_pdf(hero_img_path, max_width=1000, quality=70)
                img_w = 170
                img_h = 90
                x_pos = (210 - img_w) / 2
                pdf.image(compressed, x=x_pos, y=pdf.get_y(), w=img_w, h=img_h)
                pdf.set_y(pdf.get_y() + img_h + 5)
            except Exception:
                pdf.ln(10)

        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, pergola_type_name, 0, 1, "C")

        if p_w and p_l:
            pdf.set_font('DejaVu', '', 11)
            area = round(p_w * p_l, 1)
            pdf.cell(0, 7, f"Размер: {p_w} × {p_l} м ({area} м²)", 0, 1, "C")

        cash_total = pergola_data.get('cash_total', 0) or pergola_data.get('total_cost', 0) or 0
        if cash_total:
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', 14)
            price_str = f"{int(cash_total):,d}".replace(',', ' ')
            pdf.cell(0, 10, f"от {price_str} ₽", 0, 1, "C")

        pdf.ln(5)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 5, f"Дата расчёта: {current_date}", 0, 1, "C")
        pdf.set_font('DejaVu', '', 9)
        deadline_str = pergola_data.get('deadline', '')
        if deadline_str:
            pdf.cell(0, 5, f"Действительно до {deadline_str}", 0, 1, "C")
        else:
            pdf.cell(0, 5, "Действительно 14 дней с даты формирования", 0, 1, "C")

        pdf.ln(8)
        pdf.set_font('DejaVu', 'B', 11)
        pdf.cell(0, 6, 'Компания «Комфортный дом»', 0, 1, 'C')
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(0, 5, 'г.Ростов-на-Дону | +7 (906) 429-74-20 | pergolamarket.ru', 0, 1, 'C')

        if user_data and user_data.get('name'):
            pdf.ln(5)
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 5, f"Подготовлено для: {user_data['name']}", 0, 1, "C")

        # ===== PAGE 2: PRODUCT + FEATURES (Decolife) + SPEC =====
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
        pdf.ln(5)

        decolife = pergola_data.get('decolife', {})
        if decolife and decolife.get('description'):
            pdf.set_font('DejaVu', 'B', 12)
            model_title = decolife.get('title', decolife.get('model', 'О модели'))
            pdf.cell(0, 7, model_title, 0, 1, "L")

            deco_key = pergola_type_name.lower().replace(' new', '').replace(' basic', '').replace(' light', '').replace(' pro', '').strip()
            deco_img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_app', 'static', 'decolife', deco_key, 'images')
            deco_img_placed = False
            if os.path.isdir(deco_img_dir):
                deco_imgs = [f for f in os.listdir(deco_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                if deco_imgs:
                    deco_img_path = os.path.join(deco_img_dir, deco_imgs[0])
                    try:
                        compressed = _compress_image_for_pdf(deco_img_path, max_width=600, quality=55)
                        pdf.image(compressed, x=20, y=pdf.get_y(), w=80, h=50)
                        pdf.set_xy(105, pdf.get_y())
                        deco_img_placed = True
                    except Exception:
                        pass

            pdf.set_font('DejaVu', '', 9)
            desc = decolife.get('description', '')[:500]
            if deco_img_placed:
                pdf.set_xy(105, pdf.get_y())
                pdf.multi_cell(85, 4.5, desc)
            else:
                pdf.multi_cell(0, 5, desc)

            if deco_img_placed:
                pdf.set_y(max(pdf.get_y(), 95))

            if decolife.get('features'):
                pdf.ln(2)
                pdf.set_font('DejaVu', 'B', 10)
                pdf.cell(0, 6, "Ключевые особенности:", 0, 1, "L")
                pdf.set_font('DejaVu', '', 8)
                for feat in decolife['features'][:6]:
                    ftitle = feat.get('title', '')
                    ftext = feat.get('text', '')
                    pdf.cell(5, 4.5, "\u2022", 0, 0, "L")
                    pdf.cell(0, 4.5, f"{ftitle} — {ftext}"[:90], 0, 1, "L")
            if decolife.get('production'):
                pdf.ln(1)
                pdf.set_font('DejaVu', '', 8)
                pdf.cell(0, 4, decolife['production'][:120], 0, 1, "L")

        pergola_type = pergola_data.get('pergola_type', 'Биоклиматическая пергола')
        width = pergola_data.get('width', 0)
        length = pergola_data.get('length', 0)
        modules = pergola_data.get('modules', 1)
        lamella_type = pergola_data.get('lamella_type', 'стандартные')

        pdf.ln(5)
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 7, "Параметры перголы:", 0, 1, "L")
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(50, 6, "Модель:", 0, 0, "L"); pdf.cell(0, 6, pergola_type, 0, 1, "L")
        pdf.cell(50, 6, "Ширина:", 0, 0, "L"); pdf.cell(0, 6, f"{width} м", 0, 1, "L")
        pdf.cell(50, 6, "Вынос (длина):", 0, 0, "L"); pdf.cell(0, 6, f"{length} м", 0, 1, "L")
        pdf.cell(50, 6, "Модулей:", 0, 0, "L"); pdf.cell(0, 6, f"{modules}", 0, 1, "L")
        if hero_img_key == 'b600':
            pdf.cell(50, 6, "Тип кровли:", 0, 0, "L"); pdf.cell(0, 6, "PIR сэндвич-панели, 100 мм", 0, 1, "L")
        else:
            pdf.cell(50, 6, "Тип ламелей:", 0, 0, "L"); pdf.cell(0, 6, lamella_type, 0, 1, "L")

        specification = pergola_data.get('specification', [])
        spec_hints = {
            'Колонна': 'Несущие опоры из алюминия, окрашенные порошковым методом',
            'Балка': 'Основной несущий элемент с интегрированным водоотводом',
            'Ламел': 'Поворотные элементы крыши для регулировки света и вентиляции',
            'Лоток': 'Элемент системы водоотведения между модулями',
            'Привод': 'Электромотор для автоматического управления ламелями',
            'Пульт': 'Беспроводное дистанционное управление',
            'Подсветка': 'Встроенные LED-ленты в профилях балок',
            'Усилитель': 'Дополнительное усиление для больших пролётов',
            'Bansbach': 'Газовые пружины Bansbach (Германия)',
            'Somfy': 'Электропривод Somfy (Франция) — мировой лидер автоматики',
            'Simu': 'Электропривод Simu (Франция) — надёжная автоматика',
            'Диммер': 'Регулировка яркости LED-подсветки пультом',
            'лента': 'LED-лента IP65 с защитой от влаги',
            'Доставка': 'Доставка до объекта в пределах РФ',
            'Монтаж': 'Профессиональная установка бригадой Decolife',
        }
        if specification:
            pdf.ln(4)
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 7, "Спецификация:", 0, 1, "L")
            table_headers = ["№", "Наименование", "Количество"]
            widths = [10, 100, 60]
            pdf.table_header(table_headers, widths)
            for i, item in enumerate(specification, 1):
                name = item.get('name', '')
                count = item.get('count', '')
                hint = ''
                for k, v in spec_hints.items():
                    if k in name:
                        hint = v
                        break
                if hint:
                    pdf.table_row([str(i), name, str(count)], widths, aligns=["C", "L", "C"])
                    pdf.set_font('DejaVu', '', 7)
                    pdf.set_text_color(140, 140, 140)
                    pdf.cell(widths[0], 4, '', 0, 0)
                    pdf.cell(widths[1], 4, hint, 0, 1)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('DejaVu', '', 10)
                else:
                    pdf.table_row([str(i), name, str(count)], widths, aligns=["C", "L", "C"])

        # ===== PAGE 3: PRICING + PAYMENT VARIANTS =====
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
            
            if 'cash_total' in pergola_data:
                cash_total = pergola_data['cash_total']
            if 'noncash_total' in pergola_data:
                noncash_total = pergola_data['noncash_total']
            else:
                noncash_total = round(cash_total / 0.92)
            if 'vat_total' in pergola_data:
                vat_total = pergola_data['vat_total']
            else:
                vat_total = round(cash_total / 0.85)
            
            # --- Стилизованный блок «Стоимость по вариантам оплаты» ---
            pdf.ln(4)
            block_x = pdf.get_x()
            block_w = 170  # ширина блока (A4 минус поля)
            label_w = 120
            price_w = 50
            row_h = 10

            # Заголовок: тёмно-синий фон, белый текст
            pdf.set_fill_color(26, 58, 107)   # #1a3a6b
            pdf.set_text_color(255, 255, 255)
            pdf.set_draw_color(199, 212, 245)  # #c7d4f5
            pdf.set_font('DejaVu', 'B', 10)
            pdf.cell(block_w, row_h, "  Стоимость по вариантам оплаты:", border=1, ln=1, align='L', fill=True)

            # Строки с ценами: голубой фон
            pay_rows = [
                ("Наличные",                 "для физических лиц",               _format_total(cash_total),    True),
                ("Безналичный расчёт",       "для ИП и ООО без НДС",             _format_total(noncash_total), False),
                ("Безналичный с НДС 22%",    "для ООО — плательщиков НДС",       _format_total(vat_total),     False),
            ]
            pdf.set_fill_color(240, 244, 255)
            for label, sublabel, price, is_cash in pay_rows:
                y_before = pdf.get_y()
                pdf.set_text_color(80, 80, 80)
                pdf.set_font('DejaVu', '', 10)
                pdf.cell(label_w, row_h, "  " + label, border='LBR', ln=0, align='L', fill=True)
                if is_cash:
                    pdf.set_text_color(40, 167, 69)
                else:
                    pdf.set_text_color(26, 58, 107)
                pdf.set_font('DejaVu', 'B', 10)
                pdf.cell(price_w, row_h, price + "  ", border='LBR', ln=1, align='R', fill=True)
                pdf.set_text_color(140, 140, 140)
                pdf.set_font('DejaVu', '', 7)
                pdf.cell(label_w, 4, "    " + sublabel, border=0, ln=1, align='L')

            # Восстанавливаем цвета
            pdf.set_text_color(0, 0, 0)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_font('DejaVu', '', 10)
            pdf.ln(2)
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        if all_variants and len(all_variants) > 1:
            pdf.ln(6)
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 8, "Сравнение модификаций:", 0, 1, "L")
            pdf.ln(2)

            block_w = 170
            col_label = 52
            col_price = (block_w - col_label) / 3
            row_h = 9

            pdf.set_fill_color(26, 58, 107)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('DejaVu', 'B', 8)
            pdf.cell(col_label, row_h, "  Модификация", 1, 0, 'L', fill=True)
            pdf.cell(col_price, row_h, "Наличные", 1, 0, 'C', fill=True)
            pdf.cell(col_price, row_h, "Безналичный", 1, 0, 'C', fill=True)
            pdf.cell(col_price, row_h, "С НДС 22%", 1, 1, 'C', fill=True)

            for idx, v in enumerate(all_variants):
                v_cash = v.get('cash_total', 0)
                v_noncash = v.get('noncash_total', 0)
                v_vat = v.get('vat_total', 0)
                v_label = v.get('variant_label', '') or v.get('selected_variant', '') or f"Вариант {idx+1}"

                if idx == 0:
                    pdf.set_fill_color(240, 248, 232)
                else:
                    pdf.set_fill_color(240, 244, 255)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font('DejaVu', 'B' if idx == 0 else '', 8)
                pdf.cell(col_label, row_h, "  " + v_label, 1, 0, 'L', fill=True)
                pdf.set_font('DejaVu', 'B' if idx == 0 else '', 8)
                pdf.cell(col_price, row_h, _format_total(v_cash), 1, 0, 'C', fill=True)
                pdf.cell(col_price, row_h, _format_total(v_noncash), 1, 0, 'C', fill=True)
                pdf.cell(col_price, row_h, _format_total(v_vat), 1, 1, 'C', fill=True)

            pdf.set_text_color(0, 0, 0)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)

            try:
                from config.variant_specs import get_variant_options
                pt = pergola_data.get('pergola_type', '')
                specs = get_variant_options(pt)
                if specs:
                    pdf.ln(4)
                    pdf.set_font('DejaVu', 'B', 10)
                    pdf.cell(0, 7, "Технические характеристики модификаций:", 0, 1, "L")
                    pdf.ln(1)

                    p_w = pergola_data.get('width', 0)
                    p_l = pergola_data.get('length', 0)
                    p_area = p_w * p_l if p_w and p_l else 0

                    spec_params = [
                        ('lamella', 'Ламель'),
                        ('column', 'Колонна'),
                        ('beam', 'Балка'),
                        ('beam_double', 'Балка двухст.'),
                        ('max_overhang', 'Макс. вылет'),
                        ('max_module_width', 'Макс. шир. модуля'),
                        ('weight', 'Вес (кг/м²)'),
                        ('_total_weight', 'Вес модели'),
                        ('snow_wind_load', 'Снег./ветр. нагр.'),
                        ('hermiticity', 'Герметичность'),
                        ('heat_protection', 'Защита от нагрева'),
                    ]
                    n_cols = len(specs)
                    param_w = 30
                    val_w = (block_w - param_w) / n_cols

                    pdf.set_fill_color(26, 58, 107)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font('DejaVu', 'B', 7)
                    pdf.cell(param_w, row_h, "  Параметр", 1, 0, 'L', fill=True)
                    for s in specs:
                        pdf.cell(val_w, row_h, s.get('label', ''), 1, 0, 'C', fill=True)
                    pdf.ln()

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_fill_color(248, 251, 255)
                    pdf.set_font('DejaVu', '', 7)
                    for key, label in spec_params:
                        pdf.set_font('DejaVu', 'B', 7)
                        pdf.cell(param_w, row_h, "  " + label, 1, 0, 'L', fill=True)
                        pdf.set_font('DejaVu', '', 7)
                        for s in specs:
                            if key == '_total_weight':
                                w_str = s.get('weight', '')
                                m = re.search(r'([\d.,]+)', w_str) if w_str else None
                                if m and p_area > 0:
                                    kg_m2 = float(m.group(1).replace(',', '.'))
                                    val = f"{round(kg_m2 * p_area)} кг"
                                else:
                                    val = ''
                            else:
                                val = s.get(key, '')
                                if key in ('max_overhang', 'max_module_width'):
                                    val = f"{val} м" if val else "—"
                            pdf.cell(val_w, row_h, str(val) if val else "—", 1, 0, 'C', fill=True)
                        pdf.ln()

                    pdf.set_fill_color(255, 255, 255)
            except Exception:
                pass

            pdf.ln(3)

        # ===== PAGE 4: PRODUCT DESCRIPTION (condensed, single page) =====
        pdf.add_page()

        if hero_img_key == 'b600':
            pdf.chapter_title("B600 — всесезонная терраса с PIR-кровлей")
            pdf.set_font('DejaVu', '', 10)
            pdf.multi_cell(0, 5,
                "Пергола B600 со стационарной крышей из PIR сэндвич-панелей "
                "толщиной 100 мм обеспечивает полную защиту от осадков, ветра и "
                "холода круглый год. Снеговая нагрузка до 200 кг/м² — подходит "
                "для любого региона России."
            )
            pdf.ln(3)
            pdf.multi_cell(0, 5,
                "Интегрированная система водоотведения скрыта внутри колонн. "
                "Конструкция из экструдированного алюминия с порошковым покрытием "
                "обеспечивает долговечность и минимальное обслуживание."
            )
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', 11)
            pdf.cell(0, 6, "Преимущества B600:", 0, 1, "L")
            pdf.set_font('DejaVu', '', 10)
            b600_features = [
                "100% герметичность — защита даже при сильном ливне",
                "Теплоизоляция PIR — снижает затраты на обогрев",
                "Снеговая нагрузка 200 кг/м² — надёжнее обычных навесов",
                "Водоотвод внутри колонн — без внешних труб, эстетично",
                "До 15 м в ширину без центральных опор (модуль Standard)",
            ]
            for feat in b600_features:
                pdf.cell(5, 5, "\u2022", 0, 0, "L")
                pdf.multi_cell(0, 5, f" {feat}")
                pdf.ln(1)

            cover_photo = os.path.join(base_img_dir, 'b600_sandwich.jpg')
            if os.path.exists(cover_photo):
                try:
                    space_left = 260 - pdf.get_y()
                    if space_left > 50:
                        compressed = _compress_image_for_pdf(cover_photo, max_width=1000, quality=70)
                        img_w = 150
                        img_h = 80
                        if img_h > space_left - 5:
                            img_h = space_left - 5
                            img_w = img_h * 1.875
                        pdf.ln(5)
                        pdf.image(compressed, x=(210 - img_w) / 2, y=pdf.get_y(), w=img_w, h=img_h)
                except Exception:
                    pass
        else:
            if hero_img_key == 'b700':
                pdf.chapter_title("Модульная система — масштаб без ограничений")
            else:
                pdf.chapter_title("Модульная система — масштаб без ограничений")

            descriptions = []
            pergola_description = pergola_data.get('description', '')
            if pergola_description:
                descriptions.append(pergola_description)
            modular_description = pergola_data.get('modular_description', '')
            if modular_description:
                descriptions.append(modular_description)

            if not descriptions:
                descriptions.append(
                    "<p>Биоклиматическая пергола — современное решение для обустройства открытых пространств. "
                    "Поворотные алюминиевые ламели регулируют свет и вентиляцию, создавая комфортный микроклимат.</p>"
                    "<p>Конструкция из экструдированного алюминия с порошковым покрытием обеспечивает долговечность. "
                    "Автоматический привод управляется с пульта ДУ.</p>"
                )

            try:
                from bs4 import BeautifulSoup
                combined_html = ' '.join(descriptions[:2])
                soup = BeautifulSoup(combined_html, 'html.parser')
                title_tag = soup.find(['h2', 'h3'])
                if title_tag:
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.multi_cell(0, 5, title_tag.get_text().strip())
                    pdf.ln(3)
                pdf.set_font('DejaVu', '', 10)
                for p in soup.find_all('p'):
                    text = p.get_text().strip()[:400]
                    if text:
                        pdf.multi_cell(0, 5, text)
                        pdf.ln(2)
                for lst in soup.find_all(['ul', 'ol']):
                    for li in lst.find_all('li'):
                        text = li.get_text().strip()[:200]
                        if text:
                            pdf.cell(5, 5, "\u2022", 0, 0, "L")
                            pdf.multi_cell(0, 5, text)
            except Exception:
                pass

            model_photo_map = {
                'b500': os.path.join(gallery_img_dir, 'pergola_b500_garden_view.jpg'),
                'b700': os.path.join(gallery_img_dir, 'pergola_b700_poolside.jpg'),
            }
            model_photo = model_photo_map.get(hero_img_key)
            if model_photo and os.path.exists(model_photo):
                try:
                    space_left = 260 - pdf.get_y()
                    if space_left > 50:
                        compressed = _compress_image_for_pdf(model_photo, max_width=1000, quality=70)
                        img_w = 150
                        img_h = 80
                        if img_h > space_left - 5:
                            img_h = space_left - 5
                            img_w = img_h * 1.875
                        pdf.ln(5)
                        pdf.image(compressed, x=(210 - img_w) / 2, y=pdf.get_y(), w=img_w, h=img_h)
                except Exception:
                    pass

        # ===== PAGE 5: GALLERY (single page, no pagination) =====
        pdf.add_page()
        pdf.chapter_title("Галерея наших работ:")
        pdf.ln(3)

        gallery_images = _get_gallery_images(max_images=6, model_key=hero_img_key)
        if gallery_images:
            for i in range(0, min(len(gallery_images), 6), 2):
                batch = gallery_images[i:i+2]
                y_start = pdf.get_y()
                gallery_img_w = 85
                gallery_img_h = 60
                gallery_crop = gallery_img_w / gallery_img_h
                for j, (img_path, caption) in enumerate(batch):
                    x = 15 if j == 0 else 108
                    try:
                        compressed = _compress_image_for_pdf(img_path, max_width=600, quality=55, crop_ratio=gallery_crop)
                        pdf.image(compressed, x=x, y=y_start, w=gallery_img_w, h=gallery_img_h)
                        pdf.set_xy(x, y_start + gallery_img_h + 1)
                        pdf.set_font('DejaVu', '', 7)
                        pdf.cell(gallery_img_w, 4, caption[:60], 0, 0, 'C')
                    except Exception:
                        pass
                pdf.set_y(y_start + gallery_img_h + 10)

        # ===== PAGE 6: GUARANTEES + UPSELL + URGENCY + NOTES + CONTACTS =====
        pdf.add_page()
        pdf.chapter_title("Гарантии и преимущества:")
        pdf.ln(3)

        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(0, 7, "Гарантийные обязательства:", 0, 1, "L")
        pdf.set_font('DejaVu', '', 9)
        for wi in ["5 лет гарантии на конструкцию перголы", "2 года гарантии на автоматику и моторы", "Сервисное обслуживание на весь срок эксплуатации"]:
            pdf.cell(5, 5, "\u2022", 0, 0, "L")
            pdf.cell(0, 5, wi, 0, 1, "L")

        pdf.ln(4)
        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(0, 7, "Дополнительные опции:", 0, 1, "L")
        pdf.set_font('DejaVu', '', 9)
        for ui in ["Инфракрасные обогреватели — комфорт в прохладные вечера", "Раздвижное остекление — защита от ветра", "LED-подсветка (белая / RGB)", "Акустическая система с Bluetooth"]:
            pdf.cell(5, 5, "\u2022", 0, 0, "L")
            pdf.cell(0, 5, ui, 0, 1, "L")

        pdf.ln(4)
        pdf.set_fill_color(255, 243, 224)
        pdf.set_font('DejaVu', 'B', 10)
        if deadline_str:
            pdf.cell(170, 8, f"  \u23F0 Цены действительны до {deadline_str}", 1, 1, "L", fill=True)
        else:
            pdf.cell(170, 8, "  \u23F0 Цены действительны 14 дней с даты расчёта", 1, 1, "L", fill=True)
        pdf.set_fill_color(255, 255, 255)

        pdf.ln(4)
        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(0, 7, "О компании «Комфортный дом»:", 0, 1, "L")
        pdf.set_font('DejaVu', '', 9)
        for ci in ["Более 8 лет на рынке биоклиматических пергол", "Официальный дилер Decolife в России", "Работаем в 12 регионах РФ", "Комплексные решения: проект, поставка, монтаж"]:
            pdf.cell(5, 5, "\u2022", 0, 0, "L")
            pdf.cell(0, 5, ci, 0, 1, "L")

        pdf.ln(6)
        pdf.chapter_title("Примечания:")
        pdf.set_font('DejaVu', '', 9)
        deadline_note = f"2. Срок действия: до {deadline_str}." if deadline_str else "2. Срок действия: 14 дней."
        for note in ["1. Расчет предварительный, уточняется при обращении.", deadline_note, "3. Срок поставки: 6 недель.", "4. Оплата: 80% после подтверждения заказа, 20% после монтажа и приёмки."]:
            pdf.cell(0, 5, note, 0, 1)

        pdf.ln(6)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)
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