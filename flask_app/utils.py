import os
import json
import uuid
import random
import string
import time
import logging
import tempfile
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

try:
    CALC_MAX_AGE_DAYS = max(1, int(os.environ.get('CALC_RETENTION_DAYS', 30)))
except (ValueError, TypeError):
    CALC_MAX_AGE_DAYS = 30

cleanup_metrics = {
    'last_run_time': None,
    'last_run_dt': None,
    'last_files_removed': 0,
    'total_runs': 0,
    'total_files_removed': 0,
}

try:
    CLEANUP_INTERVAL_HOURS = max(1, int(os.environ.get('CLEANUP_INTERVAL_HOURS', 24)))
except (ValueError, TypeError):
    CLEANUP_INTERVAL_HOURS = 24

HEALTH_CHECK_GRACE_MULTIPLIER = 2


def send_telegram_alert(message):
    """
    Отправляет уведомление администратору через Telegram-бота.

    Использует переменные окружения TG_BOT_TOKEN и TG_ADMIN_CHAT_ID
    (с фолбэком на TG_CHAT_ID). Если конфигурация отсутствует или
    отправка не удалась — пишет в лог и возвращает False.
    """
    token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_ADMIN_CHAT_ID') or os.environ.get('TG_CHAT_ID')
    if not token or not chat_id:
        logger.warning(
            "Telegram alert not sent (TG_BOT_TOKEN/TG_ADMIN_CHAT_ID not configured): %s",
            message,
        )
        return False
    try:
        import urllib.request as ur
        payload = json.dumps({'chat_id': chat_id, 'text': message}).encode()
        req = ur.Request(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data=payload,
            headers={'Content-Type': 'application/json'},
        )
        ur.urlopen(req, timeout=8)
        return True
    except Exception as exc:
        logger.warning("Failed to send Telegram alert: %s | message=%s", exc, message)
        return False


def check_scheduler_health():
    last_dt = cleanup_metrics.get('last_run_dt')
    if last_dt is None:
        return {
            'healthy': False,
            'status': 'never_run',
            'message': 'Cleanup has never run',
            'last_run': None,
            'overdue_seconds': None,
        }

    expected_interval = timedelta(hours=CLEANUP_INTERVAL_HOURS)
    grace_period = expected_interval * HEALTH_CHECK_GRACE_MULTIPLIER
    now = datetime.now()
    elapsed = now - last_dt
    overdue = elapsed - grace_period

    if overdue.total_seconds() > 0:
        return {
            'healthy': False,
            'status': 'stalled',
            'message': f'Cleanup overdue by {int(overdue.total_seconds())}s (last ran {int(elapsed.total_seconds())}s ago, expected every {CLEANUP_INTERVAL_HOURS}h)',
            'last_run': cleanup_metrics['last_run_time'],
            'overdue_seconds': int(overdue.total_seconds()),
        }

    return {
        'healthy': True,
        'status': 'ok',
        'message': f'Cleanup running normally (last ran {int(elapsed.total_seconds())}s ago)',
        'last_run': cleanup_metrics['last_run_time'],
        'overdue_seconds': 0,
    }


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


def generate_top_view_svg(width, length, modules=1, is_pir=False, lamella_count=None, max_overhang=None):
    svg_w = 320
    svg_h = 240
    margin = 44
    rect_w = svg_w - 2 * margin
    rect_h = svg_h - 2 * margin
    area = round(width * length, 1)

    arrow_color = '#1a3a6e'
    inner_fill = '#eef3fa'
    beam_color = '#1a3a6e'
    beam_fill = '#9fb8d6'
    column_fill = '#1a3a6e'
    lamella_color = '#5d7da8'
    text_color = '#333'
    dim_font = '13px'
    label_font = '10px'

    BEAM_WIDTH_M = 0.164
    CENTER_BEAM_WIDTH_M = 0.28
    COLUMN_M = 0.164

    px_per_m_x = rect_w / max(width, 0.1) if width else 0
    px_per_m_y = rect_h / max(length, 0.1) if length else 0

    beam_px_x = max(3.0, BEAM_WIDTH_M * px_per_m_x)
    beam_px_y = max(3.0, BEAM_WIDTH_M * px_per_m_y)
    center_beam_px = max(4.0, CENTER_BEAM_WIDTH_M * px_per_m_x)
    col_px_x = max(4.0, COLUMN_M * px_per_m_x)
    col_px_y = max(4.0, COLUMN_M * px_per_m_y)

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += '<defs><marker id="ah" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">'
    svg += f'<path d="M0,0 L8,3 L0,6" fill="{arrow_color}"/></marker>'
    svg += '<marker id="aht" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto">'
    svg += f'<path d="M8,0 L0,3 L8,6" fill="{arrow_color}"/></marker></defs>'

    rx = margin
    ry = margin

    svg += (f'<rect x="{rx}" y="{ry}" width="{rect_w}" height="{rect_h}" '
            f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="1"/>')

    inner_x = rx + beam_px_x
    inner_y = ry + beam_px_y
    inner_w = rect_w - 2 * beam_px_x
    inner_h = rect_h - 2 * beam_px_y

    if is_pir:
        panel_count = max(1, modules)
        for i in range(1, panel_count):
            mx = rx + (rect_w / panel_count) * i
            svg += (f'<rect x="{mx - beam_px_x / 2}" y="{ry}" width="{beam_px_x}" height="{rect_h}" '
                    f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="0.8"/>')

        seg_w = (inner_w - (panel_count - 1) * beam_px_x) / panel_count
        for i in range(panel_count):
            sx = inner_x + i * (seg_w + beam_px_x)
            svg += (f'<rect x="{sx}" y="{inner_y}" width="{seg_w}" height="{inner_h}" '
                    f'fill="{inner_fill}" stroke="none"/>')

        cx = rx + rect_w / 2
        cy = ry + rect_h / 2
        svg += f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">PIR панели</text>'
        svg += f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">{panel_count} секц.</text>'
    else:
        mod_count = max(1, modules)

        for i in range(1, mod_count):
            mx = rx + (rect_w / mod_count) * i
            svg += (f'<rect x="{mx - center_beam_px / 2}" y="{ry}" width="{center_beam_px}" height="{rect_h}" '
                    f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="0.8"/>')

        seg_w = (inner_w - (mod_count - 1) * center_beam_px) / mod_count
        for m in range(mod_count):
            sx = inner_x + m * (seg_w + center_beam_px)
            svg += (f'<rect x="{sx}" y="{inner_y}" width="{seg_w}" height="{inner_h}" '
                    f'fill="{inner_fill}" stroke="none"/>')

            lam_count = lamella_count or max(4, int(inner_h / 7))
            spacing = inner_h / (lam_count + 1)
            for k in range(1, lam_count + 1):
                ly = inner_y + spacing * k
                svg += (f'<line x1="{sx + 1}" y1="{ly}" x2="{sx + seg_w - 1}" y2="{ly}" '
                        f'stroke="{lamella_color}" stroke-width="0.5" opacity="0.55"/>')

        cx = rx + rect_w / 2
        cy = ry + rect_h / 2
        total_lam = lamella_count or max(4, int(inner_h / 7))
        svg += f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">{total_lam} ламелей</text>'

    col_count_x = max(2, modules + 1)
    col_xs = []
    if col_count_x == 2:
        col_xs = [rx + col_px_x / 2, rx + rect_w - col_px_x / 2]
    else:
        col_xs.append(rx + col_px_x / 2)
        for i in range(1, modules):
            col_xs.append(rx + (rect_w / modules) * i)
        col_xs.append(rx + rect_w - col_px_x / 2)

    col_ys = [ry + col_px_y / 2, ry + rect_h - col_px_y / 2]

    needs_extra = (max_overhang is not None and length and length > max_overhang + 0.001)
    if needs_extra:
        col_ys.append(ry + rect_h / 2)

    for cxp in col_xs:
        for cyp in col_ys:
            svg += (f'<rect x="{cxp - col_px_x / 2}" y="{cyp - col_px_y / 2}" '
                    f'width="{col_px_x}" height="{col_px_y}" '
                    f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    if needs_extra:
        note_y = ry + rect_h / 2 - col_px_y - 4
        svg += (f'<text x="{rx + rect_w + 4}" y="{ry + rect_h / 2 + 3}" '
                f'text-anchor="start" font-size="8px" fill="{beam_color}" '
                f'font-style="italic">доп. опора</text>')

    arrow_y = ry + rect_h + 25
    svg += f'<line x1="{rx}" y1="{arrow_y}" x2="{rx + rect_w}" y2="{arrow_y}" stroke="{arrow_color}" stroke-width="1.5" marker-start="url(#aht)" marker-end="url(#ah)"/>'
    svg += f'<text x="{rx + rect_w / 2}" y="{arrow_y + 15}" text-anchor="middle" font-size="{dim_font}" font-weight="bold" fill="{arrow_color}">{width} м</text>'

    arrow_x = rx - 20
    svg += f'<line x1="{arrow_x}" y1="{ry}" x2="{arrow_x}" y2="{ry + rect_h}" stroke="{arrow_color}" stroke-width="1.5" marker-start="url(#aht)" marker-end="url(#ah)"/>'
    svg += f'<text x="{arrow_x}" y="{ry + rect_h / 2}" text-anchor="middle" font-size="{dim_font}" font-weight="bold" fill="{arrow_color}" transform="rotate(-90,{arrow_x},{ry + rect_h / 2})">{length} м</text>'

    svg += f'<text x="{rx + rect_w / 2}" y="{ry - 8}" text-anchor="middle" font-size="12px" font-weight="bold" fill="{text_color}">S = {area} м²</text>'

    svg += '</svg>'
    return svg


def generate_front_view_svg(width, height=3.0, modules=1, max_overhang=None):
    """Front view of pergola (width direction).
    width, height in meters. Standard column 164mm, drainage beam 260mm tall,
    pad overhang 82mm each side, slab thickness ~50mm.
    """
    BEAM_H_M = 0.26
    COLUMN_W_M = 0.164
    PAD_OVERHANG_M = 0.082
    SLAB_H_M = 0.05

    width = max(0.5, float(width))
    height = max(1.5, float(height))
    if height < BEAM_H_M + 0.5:
        height = BEAM_H_M + 0.5

    total_w_m = width + 2 * PAD_OVERHANG_M

    svg_w = 480
    svg_h = 320
    margin_l = 70
    margin_r = 90
    margin_t = 50
    margin_b = 80

    draw_w = svg_w - margin_l - margin_r
    draw_h = svg_h - margin_t - margin_b

    px_per_m_x = draw_w / total_w_m
    px_per_m_y = draw_h / (height + SLAB_H_M)
    scale = min(px_per_m_x, px_per_m_y)

    real_w_px = total_w_m * scale
    real_h_px = (height + SLAB_H_M) * scale

    ox = margin_l + (draw_w - real_w_px) / 2
    oy = margin_t + (draw_h - real_h_px)

    arrow_color = '#1a3a6e'
    beam_color = '#1a3a6e'
    beam_fill = '#9fb8d6'
    column_fill = '#1a3a6e'
    slab_fill = '#d4d4d4'
    slab_stroke = '#666'
    text_color = '#333'
    dim_font = '12px'
    small_font = '10px'

    pad_px = PAD_OVERHANG_M * scale
    col_w_px = COLUMN_W_M * scale
    beam_h_px = BEAM_H_M * scale
    slab_h_px = SLAB_H_M * scale

    pergola_top = oy
    pergola_bottom = oy + height * scale
    slab_top = pergola_bottom
    slab_bottom = slab_top + slab_h_px

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += '<defs><marker id="fah" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">'
    svg += f'<path d="M0,0 L8,3 L0,6" fill="{arrow_color}"/></marker>'
    svg += '<marker id="faht" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto">'
    svg += f'<path d="M8,0 L0,3 L8,6" fill="{arrow_color}"/></marker>'
    svg += '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
    svg += f'<line x1="0" y1="0" x2="0" y2="6" stroke="{slab_stroke}" stroke-width="0.7"/></pattern></defs>'

    col_left_x = ox + pad_px
    col_right_x = ox + real_w_px - pad_px - col_w_px

    beam_x = col_left_x
    beam_w = (col_right_x + col_w_px) - col_left_x
    svg += (f'<rect x="{beam_x}" y="{pergola_top}" width="{beam_w}" height="{beam_h_px}" '
            f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="1"/>')

    col_top_y = pergola_top + beam_h_px
    col_h_px = pergola_bottom - col_top_y

    col_xs = [col_left_x, col_right_x]
    inner_span_m = width - COLUMN_W_M
    needs_extra = (max_overhang is not None and inner_span_m > max_overhang + 0.001)
    mod_count = max(1, int(modules))
    if mod_count > 1:
        for i in range(1, mod_count):
            cxp = ox + pad_px + (width * scale / mod_count) * i - col_w_px / 2
            col_xs.append(cxp)
    elif needs_extra:
        col_xs.append(ox + real_w_px / 2 - col_w_px / 2)

    for cxp in col_xs:
        svg += (f'<rect x="{cxp}" y="{col_top_y}" width="{col_w_px}" height="{col_h_px}" '
                f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    svg += (f'<rect x="{ox}" y="{slab_top}" width="{real_w_px}" height="{slab_h_px}" '
            f'fill="url(#hatch)" stroke="{slab_stroke}" stroke-width="0.8"/>')

    title_y = margin_t - 25
    svg += (f'<text x="{svg_w/2}" y="{title_y}" text-anchor="middle" '
            f'font-size="13px" font-style="italic" fill="{text_color}">Вид спереди</text>')

    h_arrow_x = ox + real_w_px + 30
    svg += (f'<line x1="{h_arrow_x}" y1="{pergola_top}" x2="{h_arrow_x}" y2="{pergola_bottom}" '
            f'stroke="{arrow_color}" stroke-width="1.2" marker-start="url(#faht)" marker-end="url(#fah)"/>')
    svg += (f'<text x="{h_arrow_x + 10}" y="{(pergola_top + pergola_bottom)/2}" '
            f'text-anchor="middle" font-size="{dim_font}" font-weight="bold" fill="{arrow_color}" '
            f'transform="rotate(-90,{h_arrow_x + 10},{(pergola_top + pergola_bottom)/2})">{height:.2f} м</text>')

    beam_arrow_x = col_right_x + col_w_px + 8
    svg += (f'<line x1="{beam_arrow_x}" y1="{pergola_top}" x2="{beam_arrow_x}" y2="{pergola_top + beam_h_px}" '
            f'stroke="{arrow_color}" stroke-width="1" marker-start="url(#faht)" marker-end="url(#fah)"/>')
    svg += (f'<text x="{beam_arrow_x + 4}" y="{pergola_top + beam_h_px/2 + 3}" '
            f'text-anchor="start" font-size="{small_font}" fill="{arrow_color}">260</text>')

    w_arrow_y = slab_bottom + 22
    svg += (f'<line x1="{ox}" y1="{w_arrow_y}" x2="{ox + real_w_px}" y2="{w_arrow_y}" '
            f'stroke="{arrow_color}" stroke-width="1.2" marker-start="url(#faht)" marker-end="url(#fah)"/>')
    svg += (f'<text x="{ox + real_w_px/2}" y="{w_arrow_y + 14}" text-anchor="middle" '
            f'font-size="{dim_font}" font-weight="bold" fill="{arrow_color}">{width:.2f} м (+ 2×82 мм)</text>')

    col_arrow_y = pergola_top - 10
    svg += (f'<line x1="{col_left_x + col_w_px}" y1="{col_arrow_y}" x2="{col_right_x}" y2="{col_arrow_y}" '
            f'stroke="{arrow_color}" stroke-width="1" marker-start="url(#faht)" marker-end="url(#fah)"/>')
    inner_mm = int(round((width - COLUMN_W_M) * 1000))
    svg += (f'<text x="{(col_left_x + col_w_px + col_right_x)/2}" y="{col_arrow_y - 4}" '
            f'text-anchor="middle" font-size="{small_font}" fill="{arrow_color}">{inner_mm} мм</text>')

    svg += (f'<text x="{col_left_x - 4}" y="{col_top_y + col_h_px/2}" text-anchor="end" '
            f'font-size="{small_font}" fill="{arrow_color}">164</text>')

    svg += '</svg>'
    return svg


def generate_isometric_svg(width, length, height=3.0, lamella_count=None, modules=1, lamella_open_deg=55, max_overhang=None):
    """3D isometric view of pergola with tilted/open lamellas.
    Camera looks from front-right-above. X = ширина (вправо-вниз),
    Z = длина (влево-вниз в глубину), Y = высота (вверх).
    """
    import math

    width = max(0.5, float(width))
    length = max(0.5, float(length))
    height = max(1.5, float(height))
    open_deg = min(80, max(0, float(lamella_open_deg)))
    open_rad = math.radians(open_deg)

    BEAM_H = 0.26
    COL_W = 0.164
    CENTER_BEAM_W = 0.28
    LAM_W = 0.25
    LAM_T = 0.04

    svg_w = 560
    svg_h = 400
    pad_x = 40
    pad_top = 36
    pad_bot = 50

    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))

    def project(p):
        x, y, z = p
        sx = (x - z) * cos30
        sy = (x + z) * sin30 - y
        return sx, sy

    test_pts = [
        (0, 0, 0), (width, 0, 0), (width, 0, length), (0, 0, length),
        (0, height, 0), (width, height, 0), (width, height, length), (0, height, length),
    ]
    proj = [project(p) for p in test_pts]
    xs = [p[0] for p in proj]; ys = [p[1] for p in proj]
    span_x = max(xs) - min(xs); span_y = max(ys) - min(ys)
    scale = min((svg_w - 2 * pad_x) / span_x, (svg_h - pad_top - pad_bot) / span_y)
    ox = pad_x - min(xs) * scale + ((svg_w - 2 * pad_x) - span_x * scale) / 2
    oy = pad_top - min(ys) * scale

    def s(p):
        sx, sy = project(p)
        return ox + sx * scale, oy + sy * scale

    def quad(pts, fill, stroke='#1a3a6e', sw=0.8):
        coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in pts))
        return f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'

    def line(p1, p2, stroke='#1a3a6e', sw=0.6, opacity=1.0):
        x1, y1 = s(p1); x2, y2 = s(p2)
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'

    col_dark = '#143055'
    col_med = '#2a4a7e'
    col_light = '#3d6396'
    beam_top = '#b8c8df'
    beam_front = '#7d9bc0'
    beam_side = '#5d7da8'
    lam_top = '#d8e2ef'
    lam_front = '#9fb3cd'
    lam_edge = '#3d6396'
    ground = '#eef2f7'
    text_color = '#333'

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'

    g00 = (-0.4, 0, -0.4); g10 = (width + 0.4, 0, -0.4)
    g11 = (width + 0.4, 0, length + 0.4); g01 = (-0.4, 0, length + 0.4)
    svg += quad([g00, g10, g11, g01], ground, '#cfd6e0', 0.5)

    mod_count = max(1, int(modules))
    if mod_count == 1:
        col_xs = [COL_W / 2, width - COL_W / 2]
    else:
        col_xs = [COL_W / 2]
        for i in range(1, mod_count):
            col_xs.append(width / mod_count * i)
        col_xs.append(width - COL_W / 2)
    col_zs = [COL_W / 2, length - COL_W / 2]
    has_mid_z = max_overhang is not None and length > float(max_overhang) + 0.001
    if has_mid_z:
        col_zs.insert(1, length / 2)

    column_top = height - BEAM_H

    def draw_column(cx, cz, y0, y1):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light)
        return out

    back_cols = [(cx, col_zs[-1]) for cx in col_xs]
    mid_cols = [(cx, col_zs[1]) for cx in col_xs] if has_mid_z else []
    front_cols = [(cx, col_zs[0]) for cx in col_xs]

    back_cols.sort(key=lambda c: -c[0])
    for cx, cz in back_cols:
        svg += draw_column(cx, cz, 0, column_top)

    by0 = column_top
    by1 = height

    def draw_beam(x0, x1, z0, z1, y0, y1, top_c, front_c, side_c):
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], front_c)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], side_c)
        out += quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], top_c)
        return out

    svg += draw_beam(0, width, length - COL_W, length, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(0, COL_W, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    if lamella_count and lamella_count > 0:
        lam_n = int(lamella_count)
        seg_count = mod_count
        lam_per_seg = max(1, lam_n)
        for s_idx in range(seg_count):
            x_left = (width / seg_count) * s_idx + (COL_W if s_idx == 0 else COL_W / 2)
            x_right = (width / seg_count) * (s_idx + 1) - (COL_W if s_idx == seg_count - 1 else COL_W / 2)
            if x_right - x_left < 0.1:
                continue
            z_first = COL_W + 0.05
            z_last = length - COL_W - 0.05
            z_span = z_last - z_first
            spacing = z_span / max(1, lam_per_seg)
            y_center = column_top + 0.06

            half_w = LAM_W / 2
            half_t = LAM_T / 2
            dy_w = math.sin(open_rad) * half_w
            dz_w = math.cos(open_rad) * half_w
            dy_t = math.cos(open_rad) * half_t
            dz_t = math.sin(open_rad) * half_t

            lam_list = []
            for k in range(lam_per_seg):
                cz = z_first + spacing * (k + 0.5)
                lam_list.append(cz)
            for cz in lam_list:
                A = (x_left,  y_center - dy_w - dy_t, cz - dz_w + dz_t)
                B = (x_right, y_center - dy_w - dy_t, cz - dz_w + dz_t)
                C = (x_right, y_center - dy_w + dy_t, cz - dz_w - dz_t)
                D = (x_left,  y_center - dy_w + dy_t, cz - dz_w - dz_t)
                E = (x_left,  y_center + dy_w + dy_t, cz + dz_w - dz_t)
                F = (x_right, y_center + dy_w + dy_t, cz + dz_w - dz_t)
                G = (x_right, y_center + dy_w - dy_t, cz + dz_w + dz_t)
                H = (x_left,  y_center + dy_w - dy_t, cz + dz_w + dz_t)

                svg += quad([D, C, F, E], lam_top, lam_edge, 0.7)
                svg += quad([B, C, F, G], lam_front, lam_edge, 0.7)
                svg += quad([A, B, G, H], '#7a96ba', lam_edge, 0.7)

    if mod_count >= 2:
        for i in range(1, mod_count):
            cx_mid = width / mod_count * i
            svg += draw_beam(cx_mid - CENTER_BEAM_W / 2, cx_mid + CENTER_BEAM_W / 2,
                             COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(width - COL_W, width, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(0, width, 0, COL_W, by0, by1, beam_top, beam_front, beam_side)

    if mid_cols:
        mid_cols.sort(key=lambda c: c[0])
        for cx, cz in mid_cols:
            svg += draw_column(cx, cz, 0, column_top)

    front_cols.sort(key=lambda c: c[0])
    for cx, cz in front_cols:
        svg += draw_column(cx, cz, 0, column_top)

    label_y_top = 22
    svg += (f'<text x="{svg_w/2}" y="{label_y_top}" text-anchor="middle" '
            f'font-size="14px" font-weight="600" fill="#1a3a6e">Изометрия — ламели открыты {int(open_deg)}°</text>')

    info_y = svg_h - 28
    info = f'{width:.2f} (Ш) × {length:.2f} (Д) × {height:.2f} (В) м'
    if lamella_count:
        info += f', {int(lamella_count)} ламелей по {int(LAM_W*1000)} мм'
    svg += (f'<text x="{svg_w/2}" y="{info_y}" text-anchor="middle" '
            f'font-size="11px" fill="{text_color}">{info}</text>')

    svg += (f'<text x="{svg_w/2}" y="{svg_h - 12}" text-anchor="middle" '
            f'font-size="9px" fill="#888" font-style="italic">'
            f'Колонна {int(COL_W*1000)}×{int(COL_W*1000)} мм, лоток {int(BEAM_H*1000)} мм</text>')

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


def cleanup_old_calculations(max_age_days=CALC_MAX_AGE_DAYS):
    calc_dir = _get_calculations_dir()
    cutoff = time.time() - max_age_days * 86400
    removed = 0
    try:
        for fname in os.listdir(calc_dir):
            if not fname.endswith('.json'):
                continue
            fpath = os.path.join(calc_dir, fname)
            try:
                if os.path.getmtime(fpath) < cutoff:
                    os.remove(fpath)
                    removed += 1
            except OSError:
                continue
    except OSError:
        pass
    if removed:
        logger.info("Cleaned up %d old calculation(s) from %s", removed, calc_dir)
    now = datetime.now()
    cleanup_metrics['last_run_time'] = now.isoformat()
    cleanup_metrics['last_run_dt'] = now
    cleanup_metrics['last_files_removed'] = removed
    cleanup_metrics['total_runs'] += 1
    cleanup_metrics['total_files_removed'] += removed
    return removed


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
