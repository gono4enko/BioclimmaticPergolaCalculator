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

from flask_app.services.calculator import (
    ZIP_COLOR_NAMES_SHORT,
    ZIP_COLOR_HEX,
)

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
        # Позиция на 2 см от нижнего края (увеличено для третьей строки)
        self.set_y(-18)
        self.set_font('DejaVu', '', 7)
        self.cell(0, 4, 'Компания «Комфортный дом» | Комплексные решения для обустройства террас, веранд и беседок.', 0, 1, 'C')
        self.cell(0, 4, 'ИП Гоноченко А.В. ОГРНИП 321619600249231 | Тел.: +7-906-429-74-20 | Сайт: pergolamarket.ru', 0, 1, 'C')
        self.set_font('DejaVu', '', 6)
        self.set_text_color(150, 150, 150)
        self.cell(0, 4, 'Политика конфиденциальности: pergolamarket.ru/soglasie-na-obrabotku-pd  |  Оферта: pergolamarket.ru/soglasie-na-obrabotku-pd', 0, 0, 'C')
        self.set_text_color(0, 0, 0)
    
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

    # Добавляем данные ZIP-маркиз для отдельной секции PDF
    if "zip" in results and results["zip"].get("openings"):
        pergola_data["zip_openings"] = results["zip"]["openings"]
        pergola_data["zip_pult_name"] = results["zip"].get("pult_name")
        pergola_data["zip_pult_eur"] = results["zip"].get("pult_eur", 0)
        pergola_data["zip_price_eur"] = results["zip"].get("price", 0)
        pergola_data["zip_count"] = results["zip"].get("count", 0)
    
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


# ── Color / glass name tables for glazing preview block ──────────────────────
_GLZ_W_COLORS = {
    'ral9016': 'Белый RAL 9016', 'ral8028': 'Коричн. RAL 8028',
    'ral7024': 'Графит RAL 7024', 'ral_special': 'RAL special',
    'ral9t08': 'Антрацит RAL 9T08',
}
_GLZ_W_GLASS = {'transparent': 'Прозрачное', 'multifunctional': 'Мультифункц.'}
_GLZ_S500_COLORS = {
    'ral7016': 'Антрацит RAL 7016', 'ral9016': 'Белый RAL 9016',
    'ral8028': 'Коричн. RAL 8028', 'custom': 'RAL special',
}
_GLZ_S500_GLASS = {'transparent': 'Закалённое', 'tinted': 'Тонированное'}
_GLZ_S100_COLORS = {
    'ral9t08': 'Антрацит RAL 9T08', 'ral7024': 'Графит RAL 7024',
    'ral8028': 'Коричн. RAL 8028', 'ral9016': 'Белый RAL 9016',
    'ral_special': 'RAL special',
}
_GLZ_S100_GLASS = {'transparent': 'Прозрачное', 'tinted_mass': 'Тонированное (масса)'}
_GLZ_DIRS = {'right': '→ вправо', 'left': '← влево', 'center': '← → центр'}
_GLZ_SIDE_LABELS = {
    'front': ('F', 'Фасад'), 'back': ('B', 'Сзади'),
    'left': ('A', 'Слева'), 'right': ('C', 'Справа'),
}


def _glz_mini_svg_str(w, h, pc, direction, color, glass, series, sashes):
    """
    Generate a mini SVG string for a glazed opening — Python port of
    the JS _drawGlazingMiniSvg function in calculator.js.
    """
    series = (series or 'S500').upper()
    is_w = series in ('W500', 'W600', 'W700')

    if is_w:
        sN = int(sashes) if sashes in (2, 3) else 2
        pCw = ({'ral9016': '#d8d8d8', 'ral8028': '#5c3d1e',
                'ral7024': '#3a4148', 'ral_special': '#7a7a7a'}.get(color, '#2e3338'))
        is_multi = (glass == 'multifunctional')
        cG1w = '#a8c0d0' if is_multi else '#cce0f0'
        cG2w = '#7d97a8' if is_multi else '#a8c8e0'
        fW = 200
        asp = h / w if w > 0 else 1
        fH = max(60, min(190, round(fW * asp)))
        fxw, fyw = 8, 8
        VWw, VHw = fW + 16, fH + 22
        topPxw, botPxw, sidePxw, midPxw = 9, 5, 4, 3
        iXw = fxw + sidePxw
        iYw = fyw + topPxw
        iWw = fW - 2 * sidePxw
        iHw = fH - topPxw - botPxw
        sashHpx = (iHw - (sN - 1) * midPxw) / sN
        sw = ''
        for iw in range(sN):
            syw = iYw + iw * (sashHpx + midPxw)
            sw += (f'<rect x="{iXw}" y="{syw:.2f}" width="{iWw}"'
                   f' height="{sashHpx:.2f}" fill="{cG1w}"/>')
            sw += (f'<rect x="{iXw + iWw * 0.55:.2f}" y="{syw:.2f}"'
                   f' width="{iWw * 0.4:.2f}" height="{sashHpx:.2f}"'
                   f' fill="{cG2w}" opacity="0.35"/>')
            if iw < sN - 1:
                sw += (f'<rect x="{iXw}" y="{syw + sashHpx:.2f}"'
                       f' width="{iWw}" height="{midPxw}" fill="{pCw}"/>')
        sw += f'<rect x="{fxw}" y="{fyw}" width="{sidePxw}" height="{fH}" fill="{pCw}"/>'
        sw += (f'<rect x="{fxw + fW - sidePxw}" y="{fyw}" width="{sidePxw}"'
               f' height="{fH}" fill="{pCw}"/>')
        sw += f'<rect x="{fxw}" y="{fyw}" width="{fW}" height="{topPxw}" fill="{pCw}"/>'
        sw += (f'<rect x="{fxw}" y="{fyw + fH - botPxw}" width="{fW}"'
               f' height="{botPxw}" fill="{pCw}"/>')
        sw += (f'<circle cx="{fxw + fW * 0.5:.2f}" cy="{fyw + topPxw * 0.5:.2f}"'
               f' r="2.5" fill="#dfe7ef" stroke="#1a3a6e" stroke-width="0.6"/>')
        sw += (f'<text x="{fxw + fW * 0.5:.2f}" y="{fyw + fH - botPxw * 0.25:.2f}"'
               f' text-anchor="middle" font-size="6" fill="#dfe7ef"'
               f' font-family="Arial,sans-serif">{series}</text>')
        dimYw = fyw + fH + 8
        sw += (f'<line x1="{fxw}" y1="{dimYw}" x2="{fxw + fW}" y2="{dimYw}"'
               f' stroke="#8a9bbf" stroke-width="0.6"/>')
        sw += (f'<text x="{fxw + fW / 2:.2f}" y="{dimYw + 8}"'
               f' text-anchor="middle" font-size="8" fill="#8a9bbf"'
               f' font-family="Arial,sans-serif">'
               f'{round(w * 1000)}\u00d7{round(h * 1000)} \u043c\u043c</text>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg"'
                f' viewBox="0 0 {VWw} {VHw}" width="{VWw}" height="{VHw}">{sw}</svg>')

    # S-series (S500 / S100)
    n = int(pc) if pc else 3
    is_s100 = (series == 'S100')
    if is_s100:
        is_center = (direction == 'center') or n in (8, 12)
        pC = ({'ral9016': '#d8d8d8', 'ral8028': '#5c3d1e',
               'ral7024': '#3a4148', 'ral_special': '#7a7a7a'}.get(color, '#2e3338'))
        is_tinted = (glass == 'tinted_mass')
        cG1 = '#7d8e96' if is_tinted else '#d8e8f0'
        cG2 = '#5d7078' if is_tinted else '#b8d4e6'
        topPx, botPx = (6 if n == 3 else 5.5), 3
        sidePx, midPx, centerPx = 3.5, 1.6, 3
    else:
        is_center = (direction in ('center',)) or n in (6, 8, 10)
        pC = ({'ral9016': '#d0d0d0', 'ral8028': '#5c3d1e',
               'custom': '#777'}.get(color, '#3a4048'))
        is_tinted = (glass == 'tinted')
        is_bronze = is_tinted and color == 'ral8028'
        cG1 = '#b8956a' if is_bronze else ('#8a9ea8' if is_tinted else '#cce0f0')
        cG2 = '#9a7548' if is_bronze else ('#6a8088' if is_tinted else '#a8c8e0')
        topPx, botPx = 8, 4
        sidePx, midPx, centerPx = 6, 2.4, 4

    frameW = 200
    aspect = h / w if w > 0 else 1
    frameH = round(frameW * aspect)
    frameH = max(50, min(180, frameH))
    fx, fy = 8, 8
    VW, VH = frameW + 16, frameH + 22

    s = ''
    s += f'<rect x="{fx}" y="{fy}" width="{frameW}" height="{topPx}" fill="{pC}"/>'
    s += (f'<rect x="{fx}" y="{fy + frameH - botPx:.2f}" width="{frameW}"'
          f' height="{botPx}" fill="{pC}"/>')
    s += f'<rect x="{fx}" y="{fy}" width="{sidePx}" height="{frameH}" fill="{pC}"/>'
    s += (f'<rect x="{fx + frameW - sidePx:.2f}" y="{fy}" width="{sidePx}"'
          f' height="{frameH}" fill="{pC}"/>')
    iX = fx + sidePx
    iY = fy + topPx
    iW = frameW - 2 * sidePx
    iH = frameH - topPx - botPx
    if is_center:
        cx = iX + iW / 2
        s += (f'<rect x="{cx - centerPx / 2:.2f}" y="{iY:.2f}"'
              f' width="{centerPx}" height="{iH:.2f}" fill="{pC}"/>')
    halfN = n // 2 if is_center else n
    if is_center:
        panelW = ((iW - centerPx) / 2 - (halfN - 1) * midPx) / halfN
    else:
        panelW = (iW - (n - 1) * midPx) / n
    for i in range(n):
        sIdx = (i % (n // 2)) if is_center else i
        sOff = ((iW - centerPx) / 2 + centerPx) if (is_center and i >= n // 2) else 0
        px = iX + sOff + sIdx * (panelW + midPx)
        if sIdx > 0:
            s += (f'<rect x="{px - midPx:.2f}" y="{iY:.2f}" width="{midPx}"'
                  f' height="{iH:.2f}" fill="{pC}"/>')
        s += (f'<rect x="{px:.2f}" y="{iY:.2f}" width="{panelW:.2f}"'
              f' height="{iH:.2f}" fill="{cG1}"/>')
        s += (f'<rect x="{px + panelW * 0.5:.2f}" y="{iY:.2f}"'
              f' width="{panelW * 0.5:.2f}" height="{iH:.2f}"'
              f' fill="{cG2}" opacity="0.3"/>')
    dimY = fy + frameH + 8
    s += (f'<line x1="{fx}" y1="{dimY}" x2="{fx + frameW}" y2="{dimY}"'
          f' stroke="#8a9bbf" stroke-width="0.6"/>')
    s += (f'<text x="{fx + frameW / 2:.2f}" y="{dimY + 8}"'
          f' text-anchor="middle" font-size="8" fill="#8a9bbf"'
          f' font-family="Arial,sans-serif">'
          f'{round(w * 1000)}\u00d7{round(h * 1000)} \u043c\u043c</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg"'
            f' viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}">{s}</svg>')


def _glz_svg_to_png(svg_str):
    """Convert a glazing mini-SVG string to a temp PNG file path."""
    import tempfile
    try:
        import cairosvg
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=tmp.name,
                         output_width=432, output_height=360)
        return tmp.name
    except ImportError:
        pass
    except Exception:
        pass
    # Fallback: draw a simple placeholder rectangle via PIL
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (432, 360), '#f8fafd')
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 412, 340], outline='#c8d4e8', width=2)
        draw.rectangle([40, 40, 392, 320], fill='#dce8f4', outline='#8aaad0', width=1)
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(tmp.name, 'PNG')
        return tmp.name
    except Exception:
        return None


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
            'b200': [
                os.path.join(base_img_dir, 'b200.jpg'),
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
                with Image.open(compressed) as _img:
                    orig_w, orig_h = _img.size
                img_w = 170
                img_h = img_w * orig_h / orig_w
                max_h = 110
                if img_h > max_h:
                    img_h = max_h
                    img_w = img_h * orig_w / orig_h
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

        variant_label = pergola_data.get('variant_label', '') or pergola_data.get('selected_variant', '')
        if variant_label:
            pdf.set_font('DejaVu', '', 11)
            pdf.cell(0, 7, f"Модификация: {variant_label}", 0, 1, "C")

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
                        with Image.open(compressed) as _dimg:
                            _dw, _dh = _dimg.size
                        deco_w = 80
                        deco_h = deco_w * _dh / _dw
                        if deco_h > 60:
                            deco_h = 60
                            deco_w = deco_h * _dw / _dh
                        pdf.image(compressed, x=20, y=pdf.get_y(), w=deco_w, h=deco_h)
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
        variant_label_p2 = pergola_data.get('variant_label', '') or pergola_data.get('selected_variant', '')
        if variant_label_p2:
            pdf.cell(50, 6, "Модификация:", 0, 0, "L"); pdf.cell(0, 6, variant_label_p2, 0, 1, "L")
        pdf.cell(50, 6, "Ширина:", 0, 0, "L"); pdf.cell(0, 6, f"{width} м", 0, 1, "L")
        pdf.cell(50, 6, "Вынос (длина):", 0, 0, "L"); pdf.cell(0, 6, f"{length} м", 0, 1, "L")
        pdf.cell(50, 6, "Модулей:", 0, 0, "L"); pdf.cell(0, 6, f"{modules}", 0, 1, "L")
        if hero_img_key == 'b600':
            pdf.cell(50, 6, "Тип кровли:", 0, 0, "L"); pdf.cell(0, 6, "PIR сэндвич-панели, 100 мм", 0, 1, "L")
        elif hero_img_key == 'b200':
            pdf.cell(50, 6, "Тип ламелей:", 0, 0, "L"); pdf.cell(0, 6, "Стационарные, 200×50 мм", 0, 1, "L")
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

        try:
            from flask_app.utils import (generate_top_view_svg, generate_front_view_svg,
                                          generate_isometric_svg, generate_pir_iso_svg,
                                          svg_to_png_path)
            _is_pir = (hero_img_key == 'b600')
            _lc = pergola_data.get('lamellas_count') or pergola_data.get('lamella_count')
            _h = float(pergola_data.get('height', 3.0) or 3.0)
            _mo = pergola_data.get('max_overhang')
            if _mo is None:
                try:
                    from config.variant_specs import get_variant_options as _gvo
                    _opts = _gvo(pergola_data.get('pergola_type', '')) or []
                    _sel_var = (pergola_data.get('selected_variant') or pergola_data.get('variant') or '').strip().lower()
                    _sel_lam = str(pergola_data.get('lamella_size') or '').strip()
                    _spec = None
                    for _o in (_opts if isinstance(_opts, list) else []):
                        if not isinstance(_o, dict):
                            continue
                        if _sel_var and str(_o.get('variant', '')).lower() != _sel_var:
                            continue
                        if _sel_lam and str(_o.get('lamella_size', '')) != _sel_lam:
                            continue
                        _spec = _o
                        break
                    if _spec is None and isinstance(_opts, list) and _opts:
                        _spec = _opts[0] if isinstance(_opts[0], dict) else None
                    if _spec is None and isinstance(_opts, dict):
                        _spec = _opts
                    _mo = (_spec or {}).get('max_overhang')
                except Exception:
                    _mo = None

            _ref = max(width, length, _h)

            _facade_ops = pergola_data.get('facade_openings') or []
            _glz_ops = pergola_data.get('glazing_openings') or []
            _xc_f = int(pergola_data.get('extra_cols_f', 0) or 0)
            _xc_b = int(pergola_data.get('extra_cols_b', 0) or 0)
            _xc_a = int(pergola_data.get('extra_cols_a', 0) or 0)
            _xc_c = int(pergola_data.get('extra_cols_c', 0) or 0)

            def _bays_for(side):
                if side in ('front', 'back'):
                    return max(1, int(modules))
                # left / right side bays follow max_overhang rule used by JS
                if not _mo or float(length) <= float(_mo) + 0.001:
                    return 1
                import math as _m
                return max(2, _m.ceil(float(length) / float(_mo)))

            def _fills_for(side):
                bays = _bays_for(side)
                arr = [None] * bays
                for op in _facade_ops:
                    if op.get('side') != side:
                        continue
                    bay = int(op.get('bay', 0) or 0)
                    if 0 <= bay < bays:
                        arr[bay] = op.get('type') or None
                return arr if any(arr) else None

            def _glz_for(side):
                bays = _bays_for(side)
                arr = [None] * bays
                for op in _glz_ops:
                    if op.get('side') != side:
                        continue
                    bay = int(op.get('bay', 0) or 0)
                    if not (0 <= bay < bays):
                        continue
                    series = (op.get('series') or 'S500').upper()
                    if series in ('W500', 'W600', 'W700'):
                        sashes = int(op.get('sashes') or 2)
                        if sashes not in (2, 3):
                            sashes = 2
                        color = op.get('color') or 'ral9t08'
                        glass = op.get('glass') or 'transparent'
                        spec = f'{series}:{sashes}:{color}:{glass}'
                    else:
                        pc = int(op.get('pc') or (3 if series == 'S100' else 4))
                        direction = op.get('direction') or 'right'
                        color = op.get('color') or ('ral9t08' if series == 'S100' else 'ral7016')
                        glass = op.get('glass') or 'transparent'
                        if series == 'S100':
                            spec = f'S100:{pc}:{direction}:{color}:{glass}'
                        else:
                            spec = f'{pc}:{direction}:{color}:{glass}'
                    arr[bay] = spec
                return arr if any(arr) else None

            _front_fills = _fills_for('front')
            _back_fills = _fills_for('back')
            _left_fills = _fills_for('left')
            _right_fills = _fills_for('right')
            _front_glz = _glz_for('front')
            _back_glz = _glz_for('back')
            _left_glz = _glz_for('left')
            _right_glz = _glz_for('right')

            # iso fills per bay: prefer facade type, else "S500"/"S100" marker (W-series keeps full spec)
            def _iso_bay_specs(fills, glazings, bays):
                arr = [None] * bays
                for i in range(bays):
                    f = fills[i] if (fills and i < len(fills)) else None
                    g = glazings[i] if (glazings and i < len(glazings)) else None
                    spec = None
                    if f:
                        spec = f
                    elif g:
                        gu = g.upper()
                        if gu.startswith(('W500', 'W600', 'W700')):
                            spec = g
                        elif gu.startswith(('ZIP100', 'ZIP130')):
                            spec = None
                        elif gu.startswith('S100'):
                            spec = 'S100'
                        else:
                            spec = 'S500'
                    arr[i] = spec
                return arr if any(arr) else None

            _iso_front_per_bay = _iso_bay_specs(_front_fills, _front_glz, _bays_for('front'))
            _iso_back_per_bay  = _iso_bay_specs(_back_fills,  _back_glz,  _bays_for('back'))
            _iso_left_per_bay  = _iso_bay_specs(_left_fills,  _left_glz,  _bays_for('left'))
            _iso_right_per_bay = _iso_bay_specs(_right_fills, _right_glz, _bays_for('right'))
            _iso_xc_lr = max(0, _bays_for('left') - 1, _bays_for('right') - 1)

            _svgs = [
                generate_top_view_svg(width=width, length=length, modules=modules,
                                      is_pir=_is_pir, lamella_count=_lc,
                                      max_overhang=_mo, ref=_ref,
                                      xc_left=_xc_a, xc_right=_xc_c,
                                      xc_front=_xc_f, xc_back=_xc_b),
                generate_front_view_svg(width=width, height=_h, modules=modules,
                                        max_overhang=_mo, ref=_ref, title='Вид спереди',
                                        extra_columns=_xc_f,
                                        fills_per_bay=_front_fills,
                                        glazings_per_bay=_front_glz),
                generate_front_view_svg(width=width, height=_h, modules=modules,
                                        max_overhang=_mo, ref=_ref, title='Вид сзади',
                                        extra_columns=_xc_b,
                                        fills_per_bay=_back_fills,
                                        glazings_per_bay=_back_glz),
                generate_front_view_svg(width=length, height=_h, modules=1,
                                        max_overhang=_mo, ref=_ref, title='Вид слева',
                                        extra_columns=max(_bays_for('left') - 1, 0) + _xc_a,
                                        fills_per_bay=_left_fills,
                                        glazings_per_bay=_left_glz),
                generate_front_view_svg(width=length, height=_h, modules=1,
                                        max_overhang=_mo, ref=_ref, title='Вид справа',
                                        extra_columns=max(_bays_for('right') - 1, 0) + _xc_c,
                                        fills_per_bay=_right_fills,
                                        glazings_per_bay=_right_glz),
            ]
            if _is_pir:
                _svgs.append(generate_pir_iso_svg(width=width, length=length,
                                                   height=_h, modules=modules,
                                                   max_overhang=_mo, extra_columns=_iso_xc_lr,
                                                   fills_front_per_bay=_iso_front_per_bay,
                                                   fills_back_per_bay=_iso_back_per_bay,
                                                   fills_left_per_bay=_iso_left_per_bay,
                                                   fills_right_per_bay=_iso_right_per_bay))
            else:
                _svgs.append(generate_isometric_svg(width=width, length=length,
                                                     height=_h, lamella_count=_lc,
                                                     modules=modules, max_overhang=_mo,
                                                     extra_columns=_iso_xc_lr,
                                                     fills_front_per_bay=_iso_front_per_bay,
                                                     fills_back_per_bay=_iso_back_per_bay,
                                                     fills_left_per_bay=_iso_left_per_bay,
                                                     fills_right_per_bay=_iso_right_per_bay))

            _pngs = [svg_to_png_path(s) for s in _svgs]
            _iso_lbl = ('Изометрия (PIR панели)' if _is_pir
                        else ('Изометрия (стационарные)' if hero_img_key == 'b200'
                              else 'Изометрия (ламели открыты)'))
            _labels = ['Вид сверху', 'Вид спереди', 'Вид сзади',
                       'Вид слева', 'Вид справа', _iso_lbl]

            if any(p and os.path.exists(p) for p in _pngs):
                pdf.add_page()
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 8, "Схема перголы:", 0, 1, "L")
                pdf.ln(2)

                _iw = 88
                _gap = 5
                _x_left = 12
                _x_right = _x_left + _iw + _gap
                _row_h = 60
                _start_y = pdf.get_y()
                _y_rows = [_start_y, _start_y + _row_h + 6,
                           _start_y + 2 * (_row_h + 6)]

                # Layout: row 0 = top + iso, row 1 = front + back, row 2 = left + right
                _layout = [
                    (0, 0, 0),  # top  (idx, row, col)
                    (5, 0, 1),  # iso
                    (1, 1, 0),  # front
                    (2, 1, 1),  # back
                    (3, 2, 0),  # left
                    (4, 2, 1),  # right
                ]
                for (idx, _row, _col) in _layout:
                    p = _pngs[idx] if idx < len(_pngs) else None
                    lbl = _labels[idx] if idx < len(_labels) else ''
                    if not p or not os.path.exists(p):
                        continue
                    _x = _x_left if _col == 0 else _x_right
                    _y = _y_rows[_row]
                    pdf.set_font('DejaVu', 'B', 8)
                    pdf.set_xy(_x, _y)
                    pdf.cell(_iw, 5, lbl, 0, 0, 'C')
                    pdf.image(p, x=_x, y=_y + 5, w=_iw)

                for p in _pngs:
                    try:
                        if p:
                            os.unlink(p)
                    except Exception:
                        pass
        except Exception as _e:
            try:
                import logging as _lg
                _lg.getLogger(__name__).warning("Schema page render failed: %s", _e)
            except Exception:
                pass

        # ===== GLAZING PREVIEW SECTION =====
        try:
            _glz_preview_ops = pergola_data.get('glazing_openings') or []
            if _glz_preview_ops:
                import math as _math_glz
                _mo_glz = pergola_data.get('max_overhang')
                _mods_glz = max(1, int(modules or 1))
                if not _mo_glz or float(length) <= float(_mo_glz) + 0.001:
                    _lmods_glz = 1
                else:
                    _lmods_glz = max(2, _math_glz.ceil(float(length) / float(_mo_glz)))

                pdf.add_page()
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 8, "\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 \u043f\u043e \u043f\u0440\u043e\u0451\u043c\u0430\u043c:", 0, 1, "L")
                pdf.ln(2)

                _n_cols = 3 if len(_glz_preview_ops) >= 3 else 2
                if _n_cols == 3:
                    _card_w = 57.0
                    _card_gap = 4.5
                    _img_w = 46.0
                    _card_h = 63.0
                    _img_max_h = 33.0
                    _summary_y_off = 43.0
                    _dims_y_off = 48.5
                    _price_y_off = 53.5
                    _font_badge = 7
                    _font_desc = 6
                    _font_summary = 5
                    _font_dims = 5
                    _font_price = 6
                else:
                    _card_w = 82.0
                    _card_gap = 6.0
                    _img_w = 68.0
                    _card_h = 70.0
                    _img_max_h = 40.0
                    _summary_y_off = 50.0
                    _dims_y_off = 56.0
                    _price_y_off = 62.0
                    _font_badge = 8
                    _font_desc = 7
                    _font_summary = 6
                    _font_dims = 6
                    _font_price = 7
                _left_margin = 20.0
                _col = 0
                _row_start_y = pdf.get_y()
                _last_card_bottom = _row_start_y + _card_h

                _glz_pngs = []
                for _gop in _glz_preview_ops:
                    _gw = float(_gop.get('w', 0) or 0)
                    _gh = float(_gop.get('h', 0) or 0)
                    if _gw <= 0 or _gh <= 0:
                        _glz_pngs.append((None, _gop))
                        continue
                    _gseries = (_gop.get('series') or 'S500').upper()
                    _gpc = int(_gop.get('pc', 3) or 3)
                    _gdir = _gop.get('direction') or 'right'
                    _gcolor = _gop.get('color') or 'ral7016'
                    _gglass = _gop.get('glass') or 'transparent'
                    _gsashes = int(_gop.get('sashes', 2) or 2)
                    _svg_str = _glz_mini_svg_str(_gw, _gh, _gpc, _gdir, _gcolor, _gglass,
                                                 _gseries, _gsashes)
                    _png_path = _glz_svg_to_png(_svg_str)
                    _glz_pngs.append((_png_path, _gop))

                for _pi, (_png_path, _gop) in enumerate(_glz_pngs):
                    _side = _gop.get('side', 'front')
                    _bay = int(_gop.get('bay', 0) or 0)
                    _side_prefix, _side_name = _GLZ_SIDE_LABELS.get(_side, ('?', _side))
                    _side_bays = _mods_glz if _side in ('front', 'back') else _lmods_glz
                    if _side_bays > 1:
                        _label = f'{_side_prefix}{_bay + 1}'
                        _desc = f'{_side_name} \u00b7 \u041f\u0440\u043e\u0451\u043c {_bay + 1}'
                    else:
                        _label = _side_prefix
                        _desc = _side_name

                    _gseries = (_gop.get('series') or 'S500').upper()
                    if _gseries in ('W500', 'W600', 'W700'):
                        _cname = _GLZ_W_COLORS.get(_gop.get('color', ''), _gop.get('color', ''))
                        _gname = _GLZ_W_GLASS.get(_gop.get('glass', ''), _gop.get('glass', ''))
                        _sashes_c = int(_gop.get('sashes', 2) or 2)
                        _plavnik = ' \u00b7 +\u043f\u043b\u0430\u0432\u043d\u0438\u043a' if _gop.get('plavnik') else ''
                        _summary = f'{_gseries} \u00b7 {_sashes_c} \u0441\u0442\u0432. \u00b7 {_cname} \u00b7 {_gname}{_plavnik}'
                    elif _gseries == 'S100':
                        _cname = _GLZ_S100_COLORS.get(_gop.get('color', ''), _gop.get('color', ''))
                        _gname = _GLZ_S100_GLASS.get(_gop.get('glass', ''), _gop.get('glass', ''))
                        _dname = _GLZ_DIRS.get(_gop.get('direction', 'right'), _gop.get('direction', 'right'))
                        _pc_c = int(_gop.get('pc', 3) or 3)
                        _summary = f'{_gseries} \u00b7 {_pc_c} \u043f\u0430\u043d. \u00b7 {_dname} \u00b7 {_cname} \u00b7 {_gname}'
                    else:
                        _cname = _GLZ_S500_COLORS.get(_gop.get('color', ''), _gop.get('color', ''))
                        _gname = _GLZ_S500_GLASS.get(_gop.get('glass', ''), _gop.get('glass', ''))
                        _dname = _GLZ_DIRS.get(_gop.get('direction', 'right'), _gop.get('direction', 'right'))
                        _pc_c = int(_gop.get('pc', 3) or 3)
                        _summary = f'{_gseries} \u00b7 {_pc_c} \u0441\u0442\u0432. \u00b7 {_dname} \u00b7 {_cname} \u00b7 {_gname}'

                    _gw = float(_gop.get('w', 0) or 0)
                    _gh = float(_gop.get('h', 0) or 0)
                    _dims_str = (f'{round(_gw * 1000)}\u00d7{round(_gh * 1000)} '
                                 f'\u043c\u043c \u00b7 {_gw * _gh:.2f} \u043c\u00b2')

                    _card_x = _left_margin + _col * (_card_w + _card_gap)
                    _card_y = _row_start_y

                    # Card border
                    pdf.set_draw_color(200, 210, 230)
                    pdf.rect(_card_x, _card_y, _card_w, _card_h)
                    pdf.set_draw_color(0, 0, 0)

                    # Label badge
                    pdf.set_fill_color(26, 58, 110)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font('DejaVu', 'B', _font_badge)
                    pdf.set_xy(_card_x + 3, _card_y + 3)
                    _badge_w = max(10, len(_label) * 4.5)
                    pdf.cell(_badge_w, 5, _label, 0, 0, 'C', fill=True)

                    # Description text
                    pdf.set_text_color(26, 58, 110)
                    pdf.set_font('DejaVu', 'B', _font_desc)
                    pdf.set_xy(_card_x + 4 + _badge_w, _card_y + 3.5)
                    pdf.cell(_card_w - 6 - _badge_w, 4, _desc, 0, 0, 'L')

                    # SVG PNG image
                    if _png_path and os.path.exists(_png_path):
                        try:
                            with Image.open(_png_path) as _gi:
                                _gi_w_px, _gi_h_px = _gi.size
                            _gi_aspect = _gi_h_px / _gi_w_px if _gi_w_px > 0 else 1
                            _img_w_actual = _img_w
                            _gi_pdf_h = _img_w_actual * _gi_aspect
                            if _gi_pdf_h > _img_max_h:
                                _gi_pdf_h = _img_max_h
                                _img_w_actual = _gi_pdf_h / _gi_aspect
                            _img_x = _card_x + (_card_w - _img_w_actual) / 2
                            pdf.image(_png_path, x=_img_x, y=_card_y + 9, w=_img_w_actual)
                        except Exception:
                            pass

                    # Summary line
                    pdf.set_text_color(26, 58, 110)
                    pdf.set_font('DejaVu', 'B', _font_summary)
                    pdf.set_xy(_card_x + 2, _card_y + _summary_y_off)
                    pdf.cell(_card_w - 4, 5, _summary, 0, 0, 'C')

                    # Dimensions line
                    pdf.set_text_color(100, 100, 100)
                    pdf.set_font('DejaVu', '', _font_dims)
                    pdf.set_xy(_card_x + 2, _card_y + _dims_y_off)
                    pdf.cell(_card_w - 4, 4, _dims_str, 0, 0, 'C')

                    # Price line (W-series only)
                    if _gseries in ('W500', 'W600', 'W700'):
                        _glz_rate = pergola_data.get('glz_euro_rate', 110) or 110
                        _glz_price_rub = round((_gop.get('price_eur', 0) or 0) * _glz_rate)
                        _drv_price_rub = round((_gop.get('drive_price_eur', 0) or 0) * _glz_rate)
                        _total_price_rub = _glz_price_rub + _drv_price_rub
                        if _total_price_rub > 0:
                            _price_str = f"{_total_price_rub:,d}".replace(',', '\u00a0') + "\u00a0\u20bd"
                            pdf.set_fill_color(235, 245, 255)
                            pdf.rect(_card_x + 2, _card_y + _price_y_off, _card_w - 4, 6, 'F')
                            pdf.set_text_color(26, 58, 110)
                            pdf.set_font('DejaVu', 'B', _font_price)
                            pdf.set_xy(_card_x + 2, _card_y + _price_y_off)
                            pdf.cell(_card_w - 4, 6,
                                     f"\u0426\u0435\u043d\u0430: {_price_str}", 0, 0, 'C')

                    pdf.set_text_color(0, 0, 0)

                    _last_card_bottom = _card_y + _card_h

                    _col += 1
                    if _col >= _n_cols:
                        _col = 0
                        _row_start_y += _card_h + 4
                        if _row_start_y + _card_h > 265:
                            pdf.add_page()
                            pdf.set_font('DejaVu', 'B', 12)
                            pdf.cell(0, 8, "\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 "
                                     "\u043f\u043e \u043f\u0440\u043e\u0451\u043c\u0430\u043c "
                                     "(\u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0435\u043d\u0438\u0435):",
                                     0, 1, "L")
                            pdf.ln(2)
                            _row_start_y = pdf.get_y()

                for _png_path, _ in _glz_pngs:
                    try:
                        if _png_path:
                            os.unlink(_png_path)
                    except Exception:
                        pass

                pdf.set_y(_last_card_bottom + 5)
        except Exception as _glz_err:
            try:
                import logging as _lg
                _lg.getLogger(__name__).warning("Glazing preview render failed: %s", _glz_err)
            except Exception:
                pass

        # ===== ZIP AWNING SECTION (before pricing) =====
        _zip_ops_pdf = pergola_data.get('zip_openings', [])
        if _zip_ops_pdf:
            pdf.add_page()
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 8, "ZIP-маркизы:", 0, 1, "L")
            pdf.ln(2)

            # Product photos for each ZIP type used in this order
            _zip_types_used = list(dict.fromkeys(_zo.get('zip_type', 'ZIP100') for _zo in _zip_ops_pdf))
            _facade_img_dir = os.path.join(base_img_dir, 'facade')
            _zip_img_map = {
                'ZIP100': os.path.join(_facade_img_dir, 'zip100.png'),
                'ZIP130': os.path.join(_facade_img_dir, 'zip130.png'),
            }
            _zip_imgs_to_show = [
                (t, _zip_img_map[t]) for t in _zip_types_used
                if t in _zip_img_map and os.path.exists(_zip_img_map[t])
            ]
            if _zip_imgs_to_show:
                _n_imgs = len(_zip_imgs_to_show)
                _img_block_w = 85.0
                _img_h_max = 55.0
                _total_block = _n_imgs * _img_block_w
                _start_x_zip = (210 - _total_block) / 2
                _cur_y_zip = pdf.get_y()
                _max_img_bottom = _cur_y_zip
                for _iti, (_itype, _ipath) in enumerate(_zip_imgs_to_show):
                    try:
                        _compressed_z = _compress_image_for_pdf(_ipath, max_width=500, quality=72)
                        with Image.open(_compressed_z) as _ii:
                            _iw, _ih = _ii.size
                        _disp_w = _img_block_w - 10
                        _disp_h = _disp_w * _ih / _iw
                        if _disp_h > _img_h_max:
                            _disp_h = _img_h_max
                            _disp_w = _disp_h * _iw / _ih
                        _ix = _start_x_zip + _iti * _img_block_w + (_img_block_w - _disp_w) / 2
                        pdf.image(_compressed_z, x=_ix, y=_cur_y_zip, w=_disp_w, h=_disp_h)
                        _cap_y = _cur_y_zip + _disp_h + 1
                        pdf.set_xy(_start_x_zip + _iti * _img_block_w, _cap_y)
                        pdf.set_font('DejaVu', 'B', 10)
                        pdf.set_text_color(26, 58, 110)
                        pdf.cell(_img_block_w, 5, _itype, 0, 0, 'C')
                        pdf.set_text_color(0, 0, 0)
                        _max_img_bottom = max(_max_img_bottom, _cap_y + 5)
                    except Exception:
                        pass
                pdf.set_y(_max_img_bottom + 4)

            _zip_side_names = {'front': 'Фасад', 'back': 'Сзади', 'left': 'Слева', 'right': 'Справа'}
            _zip_fab_names = {'veozip': 'Veozip', 'soltis': 'Soltis W96', 'copaco': 'Copaco Blackout'}
            _zip_drv_names = {'manual': 'Ручное', 'simu': 'SIMU', 'somfy': 'Somfy', 'decolife': 'Decolife'}
            _zip_hdrs = ["\u2116", "Расположение", "Тип", "Размер (мм)", "Ткань/Цвет", "Привод", "Стоимость"]
            _zip_ws = [8, 33, 15, 26, 45, 20, 23]
            _euro_r_z = pergola_data.get('euro_rate', 110)
            pdf.table_header(_zip_hdrs, _zip_ws)
            for _zi, _zo in enumerate(_zip_ops_pdf, 1):
                _side_lbl = _zip_side_names.get(_zo.get('side', ''), _zo.get('side', ''))
                _bay_n = int(_zo.get('bay', 0) or 0) + 1
                _loc = _side_lbl + ((' · П' + str(_bay_n)) if _bay_n > 1 else '')
                _typ = _zo.get('zip_type', 'ZIP100')
                _wm = round((_zo.get('adj_w') or 0) * 1000)
                _hm = round((_zo.get('adj_h') or 0) * 1000)
                _dims = f"{_wm}\u00d7{_hm}"
                _fab = _zip_fab_names.get(_zo.get('fabric', ''), _zo.get('fabric', ''))
                _drv = _zip_drv_names.get(_zo.get('drive', ''), _zo.get('drive', ''))
                _cnt = int(_zo.get('count', 1) or 1)
                _nsec = int(_zo.get('sections', 1) or 1)
                # total_eur already includes count×sections multiplication from backend
                _tot_rub = round((_zo.get('total_eur', 0) or 0) * _euro_r_z)
                _price_s = f"{_tot_rub:,d}".replace(',', ' ') + " ₽"
                _overlay_note = ' (накл.)' if _zo.get('has_glazing') else ''
                _sec_note = f' ×{_nsec}сек.' if _nsec > 1 else ''
                _zip_col_names = ZIP_COLOR_NAMES_SHORT
                _zip_color_hex = ZIP_COLOR_HEX
                _col = _zip_col_names.get(_zo.get('color', ''), _zo.get('color', ''))
                _total_units = _cnt * _nsec
                _row_h_z = 6
                _row_aligns_z = ["C", "L", "C", "C", "L", "L", "L"]
                pdf.set_font('DejaVu', '', 9)
                pdf.set_text_color(0, 0, 0)
                # Draw columns 0-3 using normal cell() calls so FPDF handles
                # any page break naturally before we touch the swatch cell.
                for _ci_z, (_wd_z, _txt_z, _al_z) in enumerate(zip(
                        _zip_ws[:4],
                        [str(_zi), _loc + _overlay_note + _sec_note, _typ, _dims],
                        _row_aligns_z[:4])):
                    pdf.cell(_wd_z, _row_h_z, _txt_z, 1, 0, _al_z)
                # After the first 4 cells any page break has already occurred.
                # Read the live position so the swatch cell is placed correctly.
                _fc_x = pdf.get_x()
                _fc_y = pdf.get_y()
                _fc_w = _zip_ws[4]
                pdf.rect(_fc_x, _fc_y, _fc_w, _row_h_z)
                _swatch_rgb = _zip_color_hex.get(_zo.get('color', ''))
                _text_offset = 1.5
                if _swatch_rgb:
                    _sw = 3.5
                    _sw_x = _fc_x + 1.5
                    _sw_y = _fc_y + (_row_h_z - _sw) / 2
                    pdf.set_fill_color(*_swatch_rgb)
                    pdf.set_draw_color(120, 120, 120)
                    pdf.rect(_sw_x, _sw_y, _sw, _sw, 'FD')
                    pdf.set_draw_color(0, 0, 0)
                    _text_offset = 1.5 + _sw + 1.0
                pdf.set_xy(_fc_x + _text_offset, _fc_y)
                pdf.cell(_fc_w - _text_offset, _row_h_z, _fab + ' / ' + _col, 0, 0, 'L')
                # Continue at the cell after the swatch column and draw remaining cells
                pdf.set_xy(_fc_x + _fc_w, _fc_y)
                for _wd_z, _txt_z, _al_z in zip(
                        _zip_ws[5:],
                        [_drv + (f' ×{_total_units}' if _total_units > 1 else ''), _price_s],
                        _row_aligns_z[5:]):
                    pdf.cell(_wd_z, _row_h_z, _txt_z, 1, 0, _al_z)
                pdf.ln()
            _zip_tot_rub = round(((pergola_data.get('zip_price_eur', 0) or 0) - (pergola_data.get('zip_pult_eur', 0) or 0)) * _euro_r_z)
            pdf.set_font('DejaVu', 'B', 9)
            pdf.cell(sum(_zip_ws[:6]), 6, "ИТОГО ZIP-маркизы:", 1, 0, "L")
            pdf.cell(_zip_ws[6], 6, f"{_zip_tot_rub:,d}".replace(',', ' ') + " ₽", 1, 1, "L")
            pdf.set_font('DejaVu', '', 9)
            pdf.ln(3)

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

            min_cash = min(v.get('cash_total', 0) for v in all_variants)
            min_noncash = min(v.get('noncash_total', 0) for v in all_variants)
            min_vat = min(v.get('vat_total', 0) for v in all_variants)

            def _pct_diff(val, base):
                if not base or val <= base:
                    return ""
                pct = (val - base) / base * 100
                return f" (+{pct:.0f}%)"

            def _abs_diff(val, base):
                if not base or val <= base:
                    return ""
                diff = round(val - base)
                return f"+{diff:,d}".replace(',', ' ') + " ₽"

            for idx, v in enumerate(all_variants):
                v_cash = v.get('cash_total', 0)
                v_noncash = v.get('noncash_total', 0)
                v_vat = v.get('vat_total', 0)
                v_label = v.get('variant_label', '') or v.get('selected_variant', '') or f"Вариант {idx+1}"

                is_cheapest = (v_cash == min_cash)

                if is_cheapest:
                    pdf.set_fill_color(240, 248, 232)
                else:
                    pdf.set_fill_color(240, 244, 255)

                cash_pct = _pct_diff(v_cash, min_cash)
                noncash_pct = _pct_diff(v_noncash, min_noncash)
                vat_pct = _pct_diff(v_vat, min_vat)

                cash_abs = _abs_diff(v_cash, min_cash)
                noncash_abs = _abs_diff(v_noncash, min_noncash)
                vat_abs = _abs_diff(v_vat, min_vat)

                has_diff = bool(cash_pct or noncash_pct or vat_pct)

                if has_diff:
                    diff_row_h = 5
                    main_row_h = row_h - diff_row_h
                    x_start = pdf.get_x()
                    y_start = pdf.get_y()

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('DejaVu', '', 8)
                    pdf.cell(col_label, main_row_h, "  " + v_label, 'LTR', 0, 'L', fill=True)
                    pdf.set_font('DejaVu', '', 8)
                    pdf.cell(col_price, main_row_h, _format_total(v_cash) + cash_pct, 'LTR', 0, 'C', fill=True)
                    pdf.cell(col_price, main_row_h, _format_total(v_noncash) + noncash_pct, 'LTR', 0, 'C', fill=True)
                    pdf.cell(col_price, main_row_h, _format_total(v_vat) + vat_pct, 'LTR', 1, 'C', fill=True)

                    pdf.set_x(x_start)
                    pdf.set_font('DejaVu', '', 6)
                    pdf.set_text_color(130, 130, 130)
                    pdf.cell(col_label, diff_row_h, "", 'LBR', 0, 'L', fill=True)
                    pdf.cell(col_price, diff_row_h, cash_abs, 'LBR', 0, 'C', fill=True)
                    pdf.cell(col_price, diff_row_h, noncash_abs, 'LBR', 0, 'C', fill=True)
                    pdf.cell(col_price, diff_row_h, vat_abs, 'LBR', 1, 'C', fill=True)
                else:
                    pdf.set_text_color(0, 0, 0)
                    if is_cheapest and len(all_variants) > 1:
                        pdf.set_font('DejaVu', 'B', 8)
                        label_text = "  " + v_label
                        badge_text = "  ✓ лучшая цена"
                        label_w = pdf.get_string_width(label_text)
                        pdf.set_font('DejaVu', '', 6)
                        badge_w = pdf.get_string_width(badge_text)
                        remaining = col_label - label_w - 2
                        show_badge = remaining >= badge_w
                        pdf.set_font('DejaVu', 'B', 8)
                        x_before = pdf.get_x()
                        y_before = pdf.get_y()
                        pdf.cell(col_label, row_h, "", 1, 0, 'L', fill=True)
                        pdf.set_xy(x_before, y_before)
                        pdf.cell(label_w + 1, row_h, label_text, 0, 0, 'L')
                        if show_badge:
                            pdf.set_font('DejaVu', '', 6)
                            pdf.set_text_color(56, 118, 29)
                            pdf.cell(remaining, row_h, badge_text, 0, 0, 'L')
                            pdf.set_text_color(0, 0, 0)
                        pdf.set_xy(x_before + col_label, y_before)
                    else:
                        pdf.set_font('DejaVu', 'B' if is_cheapest else '', 8)
                        pdf.cell(col_label, row_h, "  " + v_label, 1, 0, 'L', fill=True)
                    pdf.cell(col_price, row_h, _format_total(v_cash), 1, 0, 'C', fill=True)
                    pdf.cell(col_price, row_h, _format_total(v_noncash), 1, 0, 'C', fill=True)
                    pdf.cell(col_price, row_h, _format_total(v_vat), 1, 1, 'C', fill=True)

            pdf.set_text_color(0, 0, 0)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)

            try:
                from config.variant_specs import VARIANT_SPECS, VARIANT_DISPLAY_ORDER
                pt = pergola_data.get('pergola_type', '')
                type_specs = VARIANT_SPECS.get(pt, {})
                display_order = VARIANT_DISPLAY_ORDER.get(pt, [])
                if type_specs:
                    pdf.ln(3)
                    pdf.set_font('DejaVu', 'I', 7)
                    pdf.set_text_color(80, 80, 80)
                    for idx, v in enumerate(all_variants):
                        v_label = v.get('variant_label', '') or v.get('selected_variant', '') or f"Вариант {idx+1}"
                        v_variant = v.get('selected_variant', '')
                        v_ls = v.get('lamella_size', '')
                        if not v_ls:
                            for do in display_order:
                                if do['variant'] == v_variant and do.get('label', '') == v_label:
                                    v_ls = do['lamella_size']
                                    break
                            if not v_ls:
                                for do in display_order:
                                    if do['variant'] == v_variant:
                                        v_ls = do['lamella_size']
                                        break
                        spec = type_specs.get(v_variant, {}).get(v_ls, {})
                        if spec:
                            details = []
                            if spec.get('lamella'):
                                details.append(f"ламель {spec['lamella']}")
                            if spec.get('column'):
                                details.append(f"колонна {spec['column']}")
                            if spec.get('beam'):
                                details.append(f"балка {spec['beam']}")
                            weight_str = spec.get('weight', '')
                            weight_suffix = ''
                            if weight_str:
                                try:
                                    w_num = float(weight_str.split('кг')[0].strip().replace(',', '.'))
                                    p_w = float(pergola_data.get('width', 0) or 0)
                                    p_l = float(pergola_data.get('length', 0) or 0)
                                    p_area = p_w * p_l
                                    if p_area > 0:
                                        total_weight = w_num * p_area
                                        weight_suffix = f", ~{total_weight:.0f} кг"
                                except (ValueError, IndexError, TypeError):
                                    pass
                            if details:
                                footnote = f"{v_label}: {', '.join(details)}{weight_suffix}"
                                pdf.cell(0, 4, footnote, 0, 1, 'L')
                    pdf.set_text_color(0, 0, 0)
            except Exception as e:
                print(f"[PDF] Ошибка генерации сносок модификаций: {e}")

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
                        with Image.open(compressed) as _cimg:
                            _cw, _ch = _cimg.size
                        img_w = 150
                        img_h = img_w * _ch / _cw
                        if img_h > space_left - 5:
                            img_h = space_left - 5
                            img_w = img_h * _cw / _ch
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
                'b200': os.path.join(base_img_dir, 'b200.jpg'),
            }
            model_photo = model_photo_map.get(hero_img_key)
            if model_photo and os.path.exists(model_photo):
                try:
                    space_left = 260 - pdf.get_y()
                    if space_left > 50:
                        compressed = _compress_image_for_pdf(model_photo, max_width=1000, quality=70)
                        with Image.open(compressed) as _mimg:
                            _mw, _mh = _mimg.size
                        img_w = 150
                        img_h = img_w * _mh / _mw
                        if img_h > space_left - 5:
                            img_h = space_left - 5
                            img_w = img_h * _mw / _mh
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
        for ui in [
            "Остекление: раздвижное, распашное, складное, гильотинное, стационарное",
            "Москитные сетки",
            "Вертикальные ZIP маркизы",
            "Фасадные панели: сплошные и жалюзи",
            "Инфракрасные обогреватели — комфорт в прохладные вечера",
            "LED-подсветка (белая / RGB)",
        ]:
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
        pdf.chapter_title("Как оформить заказ:")
        pdf.set_font('DejaVu', '', 9)
        order_steps = [
            ("1.", "Позвоните или напишите нам для подтверждения расчёта: +7-906-429-74-20"),
            ("2.", "Согласуйте итоговую конфигурацию и подпишите договор"),
            ("3.", "Внесите предоплату 80% — запускаем производство (срок 6 недель)"),
            ("4.", "После монтажа и приёмки оплатите оставшиеся 20%"),
        ]
        for num, text in order_steps:
            pdf.set_font('DejaVu', 'B', 9)
            pdf.cell(8, 5.5, num, 0, 0, "L")
            pdf.set_font('DejaVu', '', 9)
            pdf.multi_cell(0, 5.5, text, 0, "L")

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

        try:
            from flask_app.utils import generate_qr_image
            calc_id = pergola_data.get('calc_id', '')
            qr_url = f'https://pergolamarket.ru/kp/{calc_id}' if calc_id else 'https://pergolamarket.ru'
            qr_path = generate_qr_image(qr_url, size=150)
            if qr_path and os.path.exists(qr_path):
                qr_size = 30
                qr_x = 160
                qr_y = pdf.get_y() + 2
                if qr_y + qr_size + 10 > 280:
                    qr_y = pdf.get_y() - 40
                pdf.image(qr_path, x=qr_x, y=qr_y, w=qr_size, h=qr_size)
                pdf.set_xy(qr_x - 5, qr_y + qr_size + 1)
                pdf.set_font('DejaVu', '', 6)
                qr_label = 'Сканируйте для перехода на сайт'
                pdf.cell(qr_size + 10, 4, qr_label, 0, 1, 'C')
                try:
                    os.unlink(qr_path)
                except Exception:
                    pass
        except Exception:
            pass

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

def _generate_multi_summary_cover(pergolas_data_list, user_data=None):
    """Generates a single-page cover summarizing N pergolas with grand totals."""
    pdf = PDF()
    pdf.add_page()

    pdf.set_fill_color(26, 58, 110)
    pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('DejaVu', 'B', 20)
    pdf.set_y(15)
    pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, "C")
    pdf.set_font('DejaVu', '', 12)
    n = len(pergolas_data_list)
    pdf.cell(0, 8, f"Комплекс из {n} перголы", 0, 1, "C")

    kp_number = pergolas_data_list[0].get('kp_number', '') if pergolas_data_list else ''
    if kp_number:
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(0, 6, f"КП № {kp_number}", 0, 1, "C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_y(70)

    if user_data and user_data.get('name'):
        pdf.set_font('DejaVu', '', 11)
        pdf.cell(0, 7, f"Для: {user_data['name']}", 0, 1, "L")
        pdf.ln(3)

    pdf.set_font('DejaVu', 'B', 13)
    pdf.cell(0, 8, "Состав предложения:", 0, 1, "L")
    pdf.ln(2)

    pdf.set_fill_color(230, 235, 245)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('DejaVu', 'B', 9)
    pdf.cell(10, 8, "№", 1, 0, "C", fill=True)
    pdf.cell(58, 8, "Модель", 1, 0, "C", fill=True)
    pdf.cell(32, 8, "Размер, м", 1, 0, "C", fill=True)
    pdf.cell(30, 8, "Наличные, ₽", 1, 0, "C", fill=True)
    pdf.cell(30, 8, "Безнал, ₽", 1, 0, "C", fill=True)
    pdf.cell(30, 8, "с НДС, ₽", 1, 1, "C", fill=True)

    grand_cash = grand_nc = grand_vat = 0
    pdf.set_font('DejaVu', '', 9)
    for i, p in enumerate(pergolas_data_list):
        cash = int(p.get('cash_total', 0) or p.get('total_cost', 0) or 0)
        nc = int(p.get('noncash_total', 0) or p.get('non_cash_total', 0) or 0)
        vat = int(p.get('vat_total', 0) or 0)
        grand_cash += cash
        grand_nc += nc
        grand_vat += vat

        ptype = str(p.get('pergola_type', ''))
        variant = str(p.get('variant_label', '') or p.get('selected_variant', ''))
        if variant and variant.lower() not in ('auto', 'all'):
            model_str = f"{ptype} {variant}"
        else:
            model_str = ptype
        if len(model_str) > 30:
            model_str = model_str[:29] + '…'

        try:
            w_str = f"{float(p.get('width', 0)):.2f}".rstrip('0').rstrip('.')
            l_str = f"{float(p.get('length', 0)):.2f}".rstrip('0').rstrip('.')
        except (TypeError, ValueError):
            w_str = str(p.get('width', ''))
            l_str = str(p.get('length', ''))
        size_str = f"{w_str}×{l_str}"

        pdf.cell(10, 7, str(i + 1), 1, 0, "C")
        pdf.cell(58, 7, model_str, 1, 0, "L")
        pdf.cell(32, 7, size_str, 1, 0, "C")
        pdf.cell(30, 7, f"{cash:,}".replace(',', ' '), 1, 0, "R")
        pdf.cell(30, 7, f"{nc:,}".replace(',', ' '), 1, 0, "R")
        pdf.cell(30, 7, f"{vat:,}".replace(',', ' '), 1, 1, "R")

    pdf.set_fill_color(26, 58, 110)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('DejaVu', 'B', 10)
    pdf.cell(100, 9, "ИТОГО ПО ВСЕМ ПЕРГОЛАМ", 1, 0, "R", fill=True)
    pdf.cell(30, 9, f"{int(grand_cash):,}".replace(',', ' '), 1, 0, "R", fill=True)
    pdf.cell(30, 9, f"{int(grand_nc):,}".replace(',', ' '), 1, 0, "R", fill=True)
    pdf.cell(30, 9, f"{int(grand_vat):,}".replace(',', ' '), 1, 1, "R", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    pdf.set_font('DejaVu', '', 10)
    pdf.multi_cell(0, 6, "Подробное описание, спецификация и стоимость каждой перголы — на следующих страницах.")

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 9)
    pdf.set_text_color(100, 100, 100)
    current_date = datetime.now().strftime("%d.%m.%Y")
    pdf.cell(0, 5, f"Дата расчёта: {current_date}", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)

    out = pdf.output(dest='S')
    if isinstance(out, str):
        out = out.encode('latin-1')
    return bytes(out)


def generate_multi_pergola_offer(pergolas_data_list, user_data=None):
    """Generates a single PDF combining N pergolas: a summary cover + each
    pergola's full commercial offer concatenated together."""
    if not pergolas_data_list:
        return None

    if len(pergolas_data_list) == 1:
        return generate_commercial_offer(pergolas_data_list[0], user_data=user_data)

    try:
        summary_bytes = _generate_multi_summary_cover(pergolas_data_list, user_data)
    except Exception as e:
        print(f"Ошибка генерации сводной обложки: {e}")
        summary_bytes = None

    individual = []
    n = len(pergolas_data_list)
    for i, p in enumerate(pergolas_data_list):
        p_copy = dict(p)
        if i > 0:
            p_copy['kp_number'] = ''
        try:
            b = generate_commercial_offer(p_copy, user_data=user_data)
            if b:
                individual.append(b)
        except Exception as e:
            print(f"Ошибка генерации PDF для перголы {i+1}: {e}")

    if not individual:
        return summary_bytes

    try:
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        if summary_bytes:
            merger.append(io.BytesIO(summary_bytes))
        for b in individual:
            merger.append(io.BytesIO(b))
        out = io.BytesIO()
        merger.write(out)
        merger.close()
        return out.getvalue()
    except Exception as e:
        print(f"Ошибка объединения PDF: {e}")
        return individual[0] if individual else summary_bytes
