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
            if mod_count > 1 and lamella_count:
                lam_count = max(2, int(round(lamella_count / mod_count)))
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
