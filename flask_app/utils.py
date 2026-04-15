import os
import json
import uuid
import random
import string
import tempfile
from datetime import datetime, date, timedelta


def get_pergola_count():
    current_week = datetime.now().isocalendar()[1]
    return max(1, current_week - 6)


def generate_kp_number(pergola_type="B500"):
    short_type = pergola_type.replace("NEW", "")
    date_str = datetime.now().strftime("%d%m%y")
    rand_part = ''.join(random.choices(string.digits, k=4))
    return f"{short_type}-{date_str}-{rand_part}"


def get_deadline_str(calc_date=None):
    if calc_date is None:
        calc_date = date.today()
    return (calc_date + timedelta(days=14)).strftime('%d.%m.%Y')


def generate_calc_id():
    ts = datetime.now().strftime('%y%m%d')
    uid = uuid.uuid4().hex[:8]
    return f"{ts}-{uid}"


def _get_calculations_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calc_dir = os.path.join(base, 'data', 'calculations')
    os.makedirs(calc_dir, exist_ok=True)
    return calc_dir


def save_calculation(calc_id, data):
    calc_dir = _get_calculations_dir()
    filepath = os.path.join(calc_dir, f"{calc_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_calculation(calc_id):
    if not calc_id or '..' in calc_id or '/' in calc_id or '\\' in calc_id:
        return None
    calc_dir = _get_calculations_dir()
    filepath = os.path.join(calc_dir, f"{calc_id}.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def generate_top_view_svg(width, length, modules=1, is_pir=False, lamella_count=None):
    svg_w = 300
    svg_h = 220
    margin = 40
    rect_w = svg_w - 2 * margin
    rect_h = svg_h - 2 * margin
    area = round(width * length, 1)

    arrow_color = '#1a3a6e'
    rect_color = '#e8eef6'
    stroke_color = '#1a3a6e'
    text_color = '#333'
    dim_font = '13px'
    label_font = '10px'

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += '<defs><marker id="ah" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">'
    svg += f'<path d="M0,0 L8,3 L0,6" fill="{arrow_color}"/></marker>'
    svg += '<marker id="aht" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto">'
    svg += f'<path d="M8,0 L0,3 L8,6" fill="{arrow_color}"/></marker></defs>'

    rx = margin
    ry = margin
    svg += f'<rect x="{rx}" y="{ry}" width="{rect_w}" height="{rect_h}" fill="{rect_color}" stroke="{stroke_color}" stroke-width="2" rx="3"/>'

    if is_pir:
        panel_count = max(1, modules)
        for i in range(1, panel_count):
            px = rx + (rect_w / panel_count) * i
            svg += f'<line x1="{px}" y1="{ry}" x2="{px}" y2="{ry + rect_h}" stroke="{stroke_color}" stroke-width="0.8" stroke-dasharray="6,3"/>'
        cx = rx + rect_w / 2
        cy = ry + rect_h / 2
        svg += f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">PIR панели</text>'
        svg += f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">{panel_count} секц.</text>'
    else:
        lam_count = lamella_count or max(4, int(rect_h / 8))
        spacing = rect_h / (lam_count + 1)
        for i in range(1, lam_count + 1):
            ly = ry + spacing * i
            svg += f'<line x1="{rx + 4}" y1="{ly}" x2="{rx + rect_w - 4}" y2="{ly}" stroke="{stroke_color}" stroke-width="0.6" opacity="0.4"/>'
        cx = rx + rect_w / 2
        cy = ry + rect_h / 2
        svg += f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">{lam_count} ламелей</text>'

    if modules > 1:
        for i in range(1, modules):
            mx = rx + (rect_w / modules) * i
            svg += f'<line x1="{mx}" y1="{ry - 2}" x2="{mx}" y2="{ry + rect_h + 2}" stroke="#c00" stroke-width="1.5" stroke-dasharray="4,2"/>'

    arrow_y = ry + rect_h + 25
    svg += f'<line x1="{rx}" y1="{arrow_y}" x2="{rx + rect_w}" y2="{arrow_y}" stroke="{arrow_color}" stroke-width="1.5" marker-start="url(#aht)" marker-end="url(#ah)"/>'
    svg += f'<text x="{rx + rect_w / 2}" y="{arrow_y + 15}" text-anchor="middle" font-size="{dim_font}" font-weight="bold" fill="{arrow_color}">{width} м</text>'

    arrow_x = rx - 20
    svg += f'<line x1="{arrow_x}" y1="{ry}" x2="{arrow_x}" y2="{ry + rect_h}" stroke="{arrow_color}" stroke-width="1.5" marker-start="url(#aht)" marker-end="url(#ah)"/>'
    svg += f'<text x="{arrow_x}" y="{ry + rect_h / 2}" text-anchor="middle" font-size="{dim_font}" font-weight="bold" fill="{arrow_color}" transform="rotate(-90,{arrow_x},{ry + rect_h / 2})">{length} м</text>'

    svg += f'<text x="{rx + rect_w / 2}" y="{ry - 8}" text-anchor="middle" font-size="12px" font-weight="bold" fill="{text_color}">S = {area} м²</text>'

    svg += '</svg>'
    return svg


def svg_to_png_path(svg_content):
    try:
        import cairosvg
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=tmp.name, output_width=600, output_height=440)
        return tmp.name
    except ImportError:
        pass
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (600, 440), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([80, 80, 520, 360], fill='#e8eef6', outline='#1a3a6e', width=2)
        draw.text((300, 400), "Схема размеров", anchor="mm", fill='#1a3a6e')
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(tmp.name, 'PNG')
        return tmp.name
    except Exception:
        return None


def generate_qr_image(url, size=150):
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#1a3a6e', back_color='white')
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(tmp.name)
        return tmp.name
    except Exception:
        return None
