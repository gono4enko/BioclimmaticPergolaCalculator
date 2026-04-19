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

try:
    CLEANUP_HISTORY_MAX_ENTRIES = max(10, int(os.environ.get('CLEANUP_HISTORY_MAX_ENTRIES', 200)))
except (ValueError, TypeError):
    CLEANUP_HISTORY_MAX_ENTRIES = 200

_cleanup_history_lock = None


def _get_cleanup_history_lock():
    global _cleanup_history_lock
    if _cleanup_history_lock is None:
        import threading
        _cleanup_history_lock = threading.Lock()
    return _cleanup_history_lock


def _get_cleanup_history_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'cleanup_history.json')


def _load_cleanup_history_raw():
    path = _get_cleanup_history_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        logger.warning("Cleanup history file is corrupted; starting fresh")
    return []


def append_cleanup_history(entry, max_entries=None):
    """Append a cleanup run entry to the persistent history log (JSON file)."""
    if max_entries is None:
        max_entries = CLEANUP_HISTORY_MAX_ENTRIES
    path = _get_cleanup_history_path()
    lock = _get_cleanup_history_lock()
    with lock:
        history = _load_cleanup_history_raw()
        history.append(entry)
        if len(history) > max_entries:
            history = history[-max_entries:]
        tmp_path = path + '.tmp'
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except OSError as exc:
            logger.warning("Failed to write cleanup history: %s", exc)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass


def get_cleanup_history(limit=50, trigger=None, date_from=None, date_to=None):
    """Return up to `limit` most recent cleanup history entries, newest first.

    Optional filters:
      trigger   – exact match on entry['trigger'] (e.g. 'manual', 'scheduled', 'startup')
      date_from – inclusive lower bound, 'YYYY-MM-DD' string or datetime.date / datetime.datetime
      date_to   – inclusive upper bound, same format
    """
    history = _load_cleanup_history_raw()

    if trigger:
        history = [e for e in history if e.get('trigger') == trigger]

    if date_from or date_to:
        from datetime import datetime as _dt, date as _date

        def _parse_bound(val):
            if isinstance(val, _dt):
                return val.date()
            if isinstance(val, _date):
                return val
            try:
                return _dt.strptime(str(val)[:10], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None

        df = _parse_bound(date_from)
        dt = _parse_bound(date_to)

        filtered = []
        for e in history:
            ts_raw = e.get('timestamp', '')
            try:
                entry_date = _dt.fromisoformat(str(ts_raw)[:19]).date()
            except (ValueError, TypeError):
                filtered.append(e)
                continue
            if df and entry_date < df:
                continue
            if dt and entry_date > dt:
                continue
            filtered.append(e)
        history = filtered

    if limit and limit > 0:
        history = history[-limit:]
    return list(reversed(history))


def clear_cleanup_history():
    """Wipe the entire cleanup history log. Returns True on success, False on error."""
    path = _get_cleanup_history_path()
    lock = _get_cleanup_history_lock()
    with lock:
        tmp_path = path + '.tmp'
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            os.replace(tmp_path, path)
            return True
        except OSError as exc:
            logger.warning("Failed to clear cleanup history: %s", exc)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            return False

HEALTH_CHECK_GRACE_MULTIPLIER = 2

GRACE_MULTIPLIER_MIN = 1.0
GRACE_MULTIPLIER_MAX = 100.0
ALERT_COOLDOWN_MIN = 60
ALERT_COOLDOWN_MAX = 86400


def _scheduler_settings_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'scheduler_settings.json')


def _env_default_grace_multiplier():
    try:
        v = float(os.environ.get('SCHEDULER_GRACE_MULTIPLIER', HEALTH_CHECK_GRACE_MULTIPLIER))
    except (ValueError, TypeError):
        v = float(HEALTH_CHECK_GRACE_MULTIPLIER)
    return max(GRACE_MULTIPLIER_MIN, min(GRACE_MULTIPLIER_MAX, v))


def _env_default_alert_cooldown():
    try:
        v = int(os.environ.get('SCHEDULER_ALERT_COOLDOWN_SECONDS', 3600))
    except (ValueError, TypeError):
        v = 3600
    return max(ALERT_COOLDOWN_MIN, min(ALERT_COOLDOWN_MAX, v))


def get_scheduler_settings():
    """Returns current scheduler alert settings.

    Reads from data/scheduler_settings.json (if present), otherwise falls back
    to env defaults. Result is always clamped to valid bounds.
    """
    grace = _env_default_grace_multiplier()
    cooldown = _env_default_alert_cooldown()
    source = 'env'
    path = _scheduler_settings_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                if 'grace_multiplier' in data:
                    try:
                        grace = max(GRACE_MULTIPLIER_MIN, min(
                            GRACE_MULTIPLIER_MAX, float(data['grace_multiplier'])))
                    except (ValueError, TypeError):
                        pass
                if 'alert_cooldown_seconds' in data:
                    try:
                        cooldown = max(ALERT_COOLDOWN_MIN, min(
                            ALERT_COOLDOWN_MAX, int(data['alert_cooldown_seconds'])))
                    except (ValueError, TypeError):
                        pass
                source = 'file'
        except Exception as exc:
            logger.warning("Failed to read scheduler settings: %s", exc)
    return {
        'grace_multiplier': grace,
        'alert_cooldown_seconds': cooldown,
        'source': source,
    }


def save_scheduler_settings(grace_multiplier, alert_cooldown_seconds):
    """Validates and persists scheduler alert settings.

    Returns (ok, error_message). Raises nothing.
    """
    try:
        gm = float(grace_multiplier)
    except (ValueError, TypeError):
        return False, 'Grace multiplier должен быть числом'
    try:
        cd = int(alert_cooldown_seconds)
    except (ValueError, TypeError):
        return False, 'Alert cooldown должен быть целым числом'

    if not (GRACE_MULTIPLIER_MIN <= gm <= GRACE_MULTIPLIER_MAX):
        return False, (
            f'Grace multiplier должен быть в диапазоне '
            f'{GRACE_MULTIPLIER_MIN}–{GRACE_MULTIPLIER_MAX}'
        )
    if not (ALERT_COOLDOWN_MIN <= cd <= ALERT_COOLDOWN_MAX):
        return False, (
            f'Alert cooldown должен быть в диапазоне '
            f'{ALERT_COOLDOWN_MIN}–{ALERT_COOLDOWN_MAX} сек'
        )

    path = _scheduler_settings_path()
    try:
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({
                'grace_multiplier': gm,
                'alert_cooldown_seconds': cd,
            }, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True, None
    except Exception as exc:
        logger.warning("Failed to save scheduler settings: %s", exc)
        return False, 'Не удалось сохранить настройки'


def send_telegram_alert_detailed(message):
    """
    Отправляет уведомление через Telegram-бота и возвращает подробный результат.

    Возвращает dict: {'ok': bool, 'error': str|None, 'reason': str|None},
    где `reason` — машиночитаемый код ('missing_config', 'http_error',
    'network_error', 'unexpected_error'), а `error` — человекочитаемое
    описание (включая HTTP-код и тело ответа Telegram при наличии).
    """
    token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_ADMIN_CHAT_ID') or os.environ.get('TG_CHAT_ID')
    if not token or not chat_id:
        missing = []
        if not token:
            missing.append('TG_BOT_TOKEN')
        if not chat_id:
            missing.append('TG_ADMIN_CHAT_ID/TG_CHAT_ID')
        err = 'Не настроены переменные окружения: ' + ', '.join(missing)
        logger.warning("Telegram alert not sent (%s): %s", err, message)
        return {'ok': False, 'error': err, 'reason': 'missing_config'}

    import urllib.request as ur
    import urllib.error as ue
    payload = json.dumps({'chat_id': chat_id, 'text': message}).encode()
    req = ur.Request(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=payload,
        headers={'Content-Type': 'application/json'},
    )
    try:
        ur.urlopen(req, timeout=8)
        return {'ok': True, 'error': None, 'reason': None}
    except ue.HTTPError as exc:
        body = ''
        try:
            raw = exc.read()
            if raw:
                body = raw.decode('utf-8', errors='replace')[:300]
        except Exception:
            pass
        try:
            body_json = json.loads(body) if body else {}
            description = body_json.get('description') if isinstance(body_json, dict) else None
        except Exception:
            description = None
        err = f'Telegram API HTTP {exc.code}'
        if description:
            err += f': {description}'
        elif body:
            err += f': {body}'
        logger.warning("Failed to send Telegram alert: %s | message=%s", err, message)
        return {'ok': False, 'error': err, 'reason': 'http_error'}
    except ue.URLError as exc:
        err = f'Сетевая ошибка: {exc.reason}'
        logger.warning("Failed to send Telegram alert: %s | message=%s", err, message)
        return {'ok': False, 'error': err, 'reason': 'network_error'}
    except Exception as exc:
        err = f'{type(exc).__name__}: {exc}'
        logger.warning("Failed to send Telegram alert: %s | message=%s", err, message)
        return {'ok': False, 'error': err, 'reason': 'unexpected_error'}


def send_telegram_alert(message):
    """
    Backwards-compatible wrapper around send_telegram_alert_detailed.
    Returns True on success, False otherwise.
    """
    return bool(send_telegram_alert_detailed(message).get('ok'))


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
    grace_multiplier = get_scheduler_settings()['grace_multiplier']
    grace_period = expected_interval * grace_multiplier
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


DIM_COLOR = '#1a3a6e'
DIM_FONT = '13px'
DIM_SMALL_FONT = '10px'
DIM_OFFSET = 26
DIM_TEXT_GAP = 14
DIM_EXT_LEN = 6
DIM_TARGET_PX = 280
DIM_MARGIN_L = 110
DIM_MARGIN_R = 64
DIM_MARGIN_T = 46
DIM_MARGIN_B = 64


def _scale_from_ref(ref):
    if not ref or ref <= 0:
        ref = 5.0
    return DIM_TARGET_PX / float(ref)


def _dim_defs(prefix='d'):
    return (
        f'<defs><marker id="{prefix}-ah" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">'
        f'<path d="M0,0 L8,3.5 L0,7" fill="{DIM_COLOR}"/></marker>'
        f'<marker id="{prefix}-aht" markerWidth="9" markerHeight="7" refX="0" refY="3.5" orient="auto">'
        f'<path d="M8,0 L0,3.5 L8,7" fill="{DIM_COLOR}"/></marker>'
        f'<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="6" stroke="#666" stroke-width="0.7"/></pattern></defs>'
    )


def _dim_h(x1, x2, y, label, prefix='d', below=True, font=None):
    f = font or DIM_FONT
    ext1_y0 = y - DIM_EXT_LEN if below else y + DIM_EXT_LEN
    ext1_y1 = y + 2 if below else y - 2
    text_y = y + DIM_TEXT_GAP if below else y - DIM_TEXT_GAP + 4
    return (
        f'<line x1="{x1}" y1="{ext1_y0}" x2="{x1}" y2="{ext1_y1}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{x2}" y1="{ext1_y0}" x2="{x2}" y2="{ext1_y1}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{DIM_COLOR}" stroke-width="1.2" '
        f'marker-start="url(#{prefix}-aht)" marker-end="url(#{prefix}-ah)"/>'
        f'<text x="{(x1+x2)/2}" y="{text_y}" text-anchor="middle" '
        f'font-size="{f}" font-weight="bold" fill="{DIM_COLOR}">{label}</text>'
    )


def _dim_v(x, y1, y2, label, prefix='d', side='left', font=None):
    f = font or DIM_FONT
    ext_x0 = x + DIM_EXT_LEN if side == 'left' else x - DIM_EXT_LEN
    ext_x1 = x - 2 if side == 'left' else x + 2
    text_x = x - DIM_TEXT_GAP if side == 'left' else x + DIM_TEXT_GAP
    return (
        f'<line x1="{ext_x0}" y1="{y1}" x2="{ext_x1}" y2="{y1}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{ext_x0}" y1="{y2}" x2="{ext_x1}" y2="{y2}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{DIM_COLOR}" stroke-width="1.2" '
        f'marker-start="url(#{prefix}-aht)" marker-end="url(#{prefix}-ah)"/>'
        f'<text x="{text_x}" y="{(y1+y2)/2}" text-anchor="middle" '
        f'font-size="{f}" font-weight="bold" fill="{DIM_COLOR}" '
        f'transform="rotate(-90,{text_x},{(y1+y2)/2})">{label}</text>'
    )


def generate_top_view_svg(width, length, modules=1, is_pir=False, lamella_count=None, max_overhang=None, ref=None, extra_columns=0):
    inner_fill = '#eef3fa'
    beam_color = '#1a3a6e'
    beam_fill = '#9fb8d6'
    column_fill = '#1a3a6e'
    lamella_color = '#5d7da8'
    text_color = '#333'
    label_font = '10px'

    BEAM_WIDTH_M = 0.164
    CENTER_BEAM_WIDTH_M = 0.28
    COLUMN_M = 0.164

    if not ref:
        ref = max(width, length, 0.5)
    scale = _scale_from_ref(ref)

    rect_w = max(60.0, width * scale)
    rect_h = max(60.0, length * scale)
    svg_w = int(DIM_MARGIN_L + rect_w + DIM_MARGIN_R)
    svg_h = int(DIM_MARGIN_T + rect_h + DIM_MARGIN_B)
    area = round(width * length, 1)

    beam_px_x = max(2.5, BEAM_WIDTH_M * scale)
    beam_px_y = max(2.5, BEAM_WIDTH_M * scale)
    center_beam_px = max(3.5, CENTER_BEAM_WIDTH_M * scale)
    col_px = max(3.5, COLUMN_M * scale)

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += _dim_defs('t')

    rx = DIM_MARGIN_L
    ry = DIM_MARGIN_T

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
        col_xs = [rx + col_px / 2, rx + rect_w - col_px / 2]
    else:
        col_xs.append(rx + col_px / 2)
        for i in range(1, modules):
            col_xs.append(rx + (rect_w / modules) * i)
        col_xs.append(rx + rect_w - col_px / 2)

    col_ys = [ry + col_px / 2, ry + rect_h - col_px / 2]

    needs_extra = (max_overhang is not None and length and length > max_overhang + 0.001)
    extra_rows = max(int(extra_columns or 0), 1 if needs_extra else 0)
    if extra_rows > 0:
        for i in range(1, extra_rows + 1):
            col_ys.append(ry + (rect_h / (extra_rows + 1)) * i)

    for cxp in col_xs:
        for cyp in col_ys:
            svg += (f'<rect x="{cxp - col_px / 2}" y="{cyp - col_px / 2}" '
                    f'width="{col_px}" height="{col_px}" '
                    f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    arrow_y = ry + rect_h + DIM_OFFSET
    svg += _dim_h(rx, rx + rect_w, arrow_y, f'{width:.2f} м', prefix='t', below=True)

    arrow_x = rx - DIM_OFFSET
    svg += _dim_v(arrow_x, ry, ry + rect_h, f'{length:.2f} м', prefix='t', side='left')

    svg += (f'<text x="{rx + rect_w / 2}" y="{ry - 14}" text-anchor="middle" '
            f'font-size="13px" font-weight="bold" fill="{text_color}">Вид сверху · S = {area} м²</text>')

    svg += '</svg>'
    return svg


def _draw_facade_fill(fill_type, x, y, w, h):
    """Return SVG string for facade opening fill in flat elevation views."""
    out = ''
    ft = (fill_type or '').strip()
    if not ft or w < 2 or h < 2:
        return out
    if ft in ('FP-20', 'FP-PIR'):
        bg = '#4e6070' if ft == 'FP-PIR' else '#5d7080'
        line_c = '#3b4e5e' if ft == 'FP-PIR' else '#4a5e6e'
        out += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{bg}" opacity="0.80"/>'
        n = max(3, int(h / 18))
        for i in range(1, n + 1):
            ly = y + i * h / (n + 1)
            out += (f'<line x1="{x:.1f}" y1="{ly:.1f}" x2="{x + w:.1f}" y2="{ly:.1f}" '
                    f'stroke="{line_c}" stroke-width="0.9" opacity="0.55"/>')
    elif ft.startswith('FZ-44'):
        slat_c = '#4d6578'
        gap_r = 0.08 if '-100' in ft else (0.30 if '-70' in ft else 0.52)
        n_slats = max(4, int(h / 13))
        sh = h / n_slats
        sfh = max(1.0, sh * (1.0 - gap_r))
        for i in range(n_slats):
            sy = y + i * sh
            out += f'<rect x="{x:.1f}" y="{sy:.1f}" width="{w:.1f}" height="{sfh:.1f}" fill="{slat_c}" opacity="0.80"/>'
    return out


def generate_front_view_svg(width, height=3.0, modules=1, max_overhang=None, ref=None, title='Вид спереди', extra_columns=0, col_mm=164, beam_h_mm=280, fill_type=None, fills_per_bay=None):
    """Front/side elevation. width = horizontal dimension (m), height in m.
    Uses shared scale (DIM_TARGET_PX/ref) so views align with top view.
    """
    COLUMN_W_M = max(0.05, float(col_mm or 164) / 1000)
    BEAM_H_M = max(0.10, float(beam_h_mm or 280) / 1000)
    PAD_OVERHANG_M = 0.082
    SLAB_H_M = 0.05

    width = max(0.5, float(width))
    height = max(1.5, float(height))
    if height < BEAM_H_M + 0.5:
        height = BEAM_H_M + 0.5

    total_w_m = width + 2 * PAD_OVERHANG_M
    total_h_m = height + SLAB_H_M

    if not ref:
        ref = max(width, height, 0.5)
    scale = _scale_from_ref(ref)

    real_w_px = max(60.0, total_w_m * scale)
    real_h_px = max(60.0, total_h_m * scale)

    svg_w = int(DIM_MARGIN_L + real_w_px + DIM_MARGIN_R)
    svg_h = int(DIM_MARGIN_T + real_h_px + DIM_MARGIN_B)

    ox = DIM_MARGIN_L
    oy = DIM_MARGIN_T

    beam_color = '#1a3a6e'
    beam_fill = '#9fb8d6'
    column_fill = '#1a3a6e'
    slab_stroke = '#666'
    text_color = '#333'
    small_font = '10px'

    pad_px = PAD_OVERHANG_M * scale
    col_w_px = max(2.5, COLUMN_W_M * scale)
    beam_h_px = max(3.0, BEAM_H_M * scale)
    slab_h_px = max(2.5, SLAB_H_M * scale)

    pergola_top = oy
    pergola_bottom = oy + height * scale
    slab_top = pergola_bottom
    slab_bottom = slab_top + slab_h_px

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += _dim_defs('f')

    col_left_x = ox + pad_px
    col_right_x = ox + real_w_px - pad_px - col_w_px

    col_xs = [col_left_x, col_right_x]
    inner_span_m = width - COLUMN_W_M
    needs_extra = (max_overhang is not None and inner_span_m > max_overhang + 0.001)
    mod_count = max(1, int(modules))
    extra_col_xs = []
    if mod_count > 1:
        for i in range(1, mod_count):
            cxp = ox + pad_px + (width * scale / mod_count) * i - col_w_px / 2
            col_xs.append(cxp)
    elif needs_extra:
        cxp = ox + real_w_px / 2 - col_w_px / 2
        col_xs.append(cxp)
        extra_col_xs.append(cxp)
    extra_n = max(int(extra_columns or 0), 0)
    if extra_n > 0:
        for i in range(1, extra_n + 1):
            cxp = ox + pad_px + (width * scale / (extra_n + 1)) * i - col_w_px / 2
            col_xs.append(cxp)
            extra_col_xs.append(cxp)

    col_top_y = pergola_top
    col_h_px = pergola_bottom - pergola_top

    for cxp in col_xs:
        svg += (f'<rect x="{cxp}" y="{col_top_y}" width="{col_w_px}" height="{col_h_px}" '
                f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    beam_x = col_left_x
    beam_w = (col_right_x + col_w_px) - col_left_x
    svg += (f'<rect x="{beam_x}" y="{pergola_top}" width="{beam_w}" height="{beam_h_px}" '
            f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="1"/>')

    svg += (f'<rect x="{ox}" y="{slab_top}" width="{real_w_px}" height="{slab_h_px}" '
            f'fill="url(#hatch)" stroke="{slab_stroke}" stroke-width="0.8"/>')

    svg += (f'<text x="{svg_w/2}" y="{oy - 14}" text-anchor="middle" '
            f'font-size="13px" font-weight="bold" fill="{text_color}">{title}</text>')

    h_dim_x = ox + real_w_px + DIM_OFFSET
    svg += _dim_v(h_dim_x, pergola_top, pergola_bottom, f'{height:.2f} м', prefix='f', side='right')

    w_dim_y = slab_bottom + DIM_OFFSET
    svg += _dim_h(ox, ox + real_w_px, w_dim_y, f'{width:.2f} м', prefix='f', below=True)

    beam_h_label = int(round(float(beam_h_mm or 280)))
    svg += (f'<text x="{col_right_x + col_w_px + 4}" y="{pergola_top + beam_h_px/2 + 3}" '
            f'text-anchor="start" font-size="{small_font}" fill="{DIM_COLOR}">{beam_h_label}</text>')

    _ldr_attach_x = col_left_x
    _ldr_attach_y = col_top_y + beam_h_px + (col_h_px - beam_h_px) * 0.38
    _ldr_elbow_x = col_left_x - 10
    _ldr_elbow_y = _ldr_attach_y - 18
    _ldr_shelf_end_x = max(4.0, _ldr_elbow_x - 52)
    svg += (f'<defs><marker id="f-dot" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5">'
            f'<circle cx="2.5" cy="2.5" r="2" fill="{DIM_COLOR}"/></marker></defs>')
    svg += (f'<polyline points="{_ldr_attach_x:.1f},{_ldr_attach_y:.1f} '
            f'{_ldr_elbow_x:.1f},{_ldr_elbow_y:.1f} '
            f'{_ldr_shelf_end_x:.1f},{_ldr_elbow_y:.1f}" '
            f'fill="none" stroke="{DIM_COLOR}" stroke-width="0.8" '
            f'marker-start="url(#f-dot)"/>')
    col_mm_label = int(col_mm) if col_mm else 164
    svg += (f'<text x="{_ldr_elbow_x:.1f}" y="{_ldr_elbow_y - 3:.1f}" '
            f'text-anchor="end" font-size="{small_font}" fill="{DIM_COLOR}">□ {col_mm_label}×{col_mm_label} мм</text>')

    if fills_per_bay or (fill_type and fill_type.strip()):
        fill_y0 = pergola_top + beam_h_px
        fill_h_px = pergola_bottom - fill_y0
        sorted_xs = sorted(col_xs)
        for _bi in range(len(sorted_xs) - 1):
            _fx0 = sorted_xs[_bi] + col_w_px
            _fx1 = sorted_xs[_bi + 1]
            if _fx1 - _fx0 > 2:
                if fills_per_bay and _bi < len(fills_per_bay) and fills_per_bay[_bi]:
                    bay_fill = fills_per_bay[_bi]
                else:
                    bay_fill = fill_type
                svg += _draw_facade_fill(bay_fill, _fx0, fill_y0, _fx1 - _fx0, fill_h_px)

    svg += '</svg>'
    return svg


def generate_isometric_svg(width, length, height=3.0, lamella_count=None, modules=1, lamella_open_deg=55, max_overhang=None, extra_columns=0, fill_front=None, fill_right=None, fill_left=None, fill_back=None):
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

    BEAM_H = 0.28
    COL_W = 0.164
    CENTER_BEAM_W = 0.28
    LAM_W = 0.25
    LAM_T = 0.04

    svg_w = 620
    svg_h = 460
    pad_x = 80
    pad_top = 40
    pad_bot = 80

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
    lam_top = '#daeaf8'
    lam_front = '#7ab4d4'
    lam_edge = '#0d2550'
    ground = '#eef2f7'
    text_color = '#333'

    def _iso_fill_face(ft, pts_bot_left, pts_bot_right, pts_top_left, pts_top_right, n_h_lines=8):
        _out = ''
        if not ft or not ft.strip():
            return _out
        ft = ft.strip()
        if ft in ('FP-20', 'FP-PIR'):
            bg = '#455a6a' if ft == 'FP-PIR' else '#527080'
            line_c = '#334455'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], bg, bg, 0.0)
            for _li in range(1, n_h_lines + 1):
                _t = _li / (n_h_lines + 1)
                def _lerp(a, b, __t=_t):
                    return (a[0]+__t*(b[0]-a[0]), a[1]+__t*(b[1]-a[1]), a[2]+__t*(b[2]-a[2]))
                _out += line(_lerp(pts_bot_left, pts_top_left), _lerp(pts_bot_right, pts_top_right), line_c, 0.7)
        elif ft.startswith('FZ-44'):
            slat_c = '#415568'
            gap_r = 0.08 if '-100' in ft else (0.30 if '-70' in ft else 0.52)
            n_slats = 8
            for _si in range(n_slats):
                t0 = _si / n_slats
                t1 = t0 + (1.0 - gap_r) / n_slats
                def _lp(a, b, _t):
                    return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
                _out += quad([_lp(pts_bot_left, pts_top_left, t0),
                              _lp(pts_bot_right, pts_top_right, t0),
                              _lp(pts_bot_right, pts_top_right, t1),
                              _lp(pts_bot_left, pts_top_left, t1)], slat_c, slat_c, 0.3)
        return _out

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
    extra_n = max(int(extra_columns or 0), 0)
    mid_z_positions = []
    if extra_n > 0:
        for i in range(1, extra_n + 1):
            mid_z_positions.append(length / (extra_n + 1) * i)
    elif has_mid_z:
        mid_z_positions.append(length / 2)
    for mz in mid_z_positions:
        col_zs.insert(-1, mz)
    has_mid_z = bool(mid_z_positions)

    column_top = height - BEAM_H

    fill_back_svg = ''
    if fill_back and fill_back.strip():
        for _mi in range(mod_count):
            _bx0 = col_xs[0] if _mi == 0 else width / mod_count * _mi + COL_W / 2
            _bx1 = col_xs[-1] if _mi == mod_count - 1 else width / mod_count * (_mi + 1) - COL_W / 2
            fill_back_svg += _iso_fill_face(fill_back, (_bx0, 0, length), (_bx1, 0, length),
                                            (_bx0, column_top, length), (_bx1, column_top, length))
    fill_left_svg = ''
    if fill_left and fill_left.strip():
        fill_left_svg = _iso_fill_face(fill_left, (0, 0, COL_W), (0, 0, length - COL_W),
                                       (0, column_top, COL_W), (0, column_top, length - COL_W))

    def draw_column(cx, cz, y0, y1):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light)
        return out

    back_cols = [(cx, col_zs[-1]) for cx in col_xs]
    mid_cols = []
    for mz in mid_z_positions:
        for cx in col_xs:
            mid_cols.append((cx, mz))
    front_cols = [(cx, col_zs[0]) for cx in col_xs]

    svg += fill_back_svg

    back_cols.sort(key=lambda c: -c[0])
    for cx, cz in back_cols:
        svg += draw_column(cx, cz, 0, height)

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

    svg += fill_left_svg

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

                svg += quad([D, C, F, E], lam_top, lam_edge, 1.0)
                svg += quad([B, C, F, G], lam_front, lam_edge, 1.0)
                svg += quad([A, B, G, H], '#5a90b8', lam_edge, 1.0)

    if mod_count >= 2:
        for i in range(1, mod_count):
            cx_mid = width / mod_count * i
            svg += draw_beam(cx_mid - CENTER_BEAM_W / 2, cx_mid + CENTER_BEAM_W / 2,
                             COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(width - COL_W, width, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(0, width, 0, COL_W, by0, by1, beam_top, beam_front, beam_side)

    if fill_right and fill_right.strip():
        _pbl = (width, 0, COL_W)
        _pbr = (width, 0, length - COL_W)
        _ptl = (width, column_top, COL_W)
        _ptr = (width, column_top, length - COL_W)
        svg += _iso_fill_face(fill_right, _pbl, _pbr, _ptl, _ptr)

    any_other_fill = any([fill_right, fill_left, fill_back])
    for _mi in range(mod_count):
        _fx0 = col_xs[0] if _mi == 0 else width / mod_count * _mi + COL_W / 2
        _fx1 = col_xs[-1] if _mi == mod_count - 1 else width / mod_count * (_mi + 1) - COL_W / 2
        _pbl = (_fx0, 0, 0)
        _pbr = (_fx1, 0, 0)
        _ptl = (_fx0, column_top, 0)
        _ptr = (_fx1, column_top, 0)
        if fill_front and fill_front.strip():
            svg += _iso_fill_face(fill_front, _pbl, _pbr, _ptl, _ptr)
        elif any_other_fill:
            coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in [_pbl, _pbr, _ptr, _ptl]))
            svg += f'<polygon points="{coords}" fill="#eef2f7" fill-opacity="0.78" stroke="#2a4a7e" stroke-width="1.0" stroke-dasharray="6,3" stroke-linejoin="round"/>'

    if mid_cols:
        mid_cols.sort(key=lambda c: c[0])
        for cx, cz in mid_cols:
            svg += draw_column(cx, cz, 0, height)

    front_cols.sort(key=lambda c: c[0])
    for cx, cz in front_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += _dim_defs('i')

    def _iso_dim(p1, p2, nx, ny, label, off=28, text_off=14):
        d1x = p1[0] + nx * off
        d1y = p1[1] + ny * off
        d2x = p2[0] + nx * off
        d2y = p2[1] + ny * off
        ang = math.degrees(math.atan2(d2y - d1y, d2x - d1x))
        if ang > 90 or ang < -90:
            ang -= 180
            d1x, d2x = d2x, d1x
            d1y, d2y = d2y, d1y
        midx = (d1x + d2x) / 2
        midy = (d1y + d2y) / 2
        tnx, tny = nx, ny
        if (tnx * math.cos(math.radians(ang)) + tny * math.sin(math.radians(ang))) > 0:
            pass
        tx = midx + nx * text_off
        ty = midy + ny * text_off
        return (
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p1[0] + nx*off:.1f}" y2="{p1[1] + ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{p2[0]:.1f}" y1="{p2[1]:.1f}" x2="{p2[0] + nx*off:.1f}" y2="{p2[1] + ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{d1x:.1f}" y1="{d1y:.1f}" x2="{d2x:.1f}" y2="{d2y:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" '
            f'marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" '
            f'fill="{DIM_COLOR}" transform="rotate({ang:.1f},{tx:.1f},{ty:.1f})">{label}</text>'
        )

    p_bl_floor = s((0, 0, length))
    p_br_floor = s((width, 0, length))
    nx_w_back = -math.cos(math.radians(30))
    ny_w_back = math.sin(math.radians(30))
    svg += _iso_dim(p_bl_floor, p_br_floor, nx_w_back, ny_w_back, f'{width:.2f} м (Ш)')

    p_fr_floor = s((width, 0, 0))
    nx_l_right = math.cos(math.radians(30))
    ny_l_right = math.sin(math.radians(30))
    svg += _iso_dim(p_fr_floor, p_br_floor, nx_l_right, ny_l_right, f'{length:.2f} м (Д)')

    p_btr = s((width, 0, 0))
    p_ttr = s((width, height, 0))
    hd_x = max(p_btr[0], p_ttr[0]) + 32
    svg += (f'<line x1="{p_btr[0]:.1f}" y1="{p_btr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{p_ttr[0]:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_ttr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{hd_x:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" '
            f'marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
            f'<text x="{hd_x + 14:.1f}" y="{(p_btr[1]+p_ttr[1])/2:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" '
            f'fill="{DIM_COLOR}" transform="rotate(-90,{hd_x + 14:.1f},{(p_btr[1]+p_ttr[1])/2:.1f})">{height:.2f} м (В)</text>')

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


def generate_pir_iso_svg(width, length, height=3.0, modules=1, max_overhang=None, extra_columns=0):
    """Isometric view for B600 pergola with PIR sandwich-panel roof.
    Panel joints spaced proportionally to actual panel width (~0.9 m).
    """
    import math

    width = max(0.5, float(width))
    length = max(0.5, float(length))
    height = max(1.5, float(height))

    BEAM_H = 0.28
    COL_W = 0.164
    CENTER_BEAM_W = 0.28
    PANEL_W_NOM = 0.9

    svg_w = 620
    svg_h = 460
    pad_x = 80
    pad_top = 40
    pad_bot = 80

    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))

    def project(p):
        x, y, z = p
        return (x - z) * cos30, (x + z) * sin30 - y

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

    def seg(p1, p2, stroke='#1a3a6e', sw=0.7):
        x1, y1 = s(p1); x2, y2 = s(p2)
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"/>'

    col_dark = '#143055'; col_med = '#2a4a7e'; col_light = '#3d6396'
    beam_top = '#b8c8df'; beam_front = '#7d9bc0'; beam_side = '#5d7da8'
    pir_top = '#c8d8eb'; pir_front = '#8fafc8'; pir_joint = '#6a87a8'
    ground = '#eef2f7'

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'

    g00 = (-0.4, 0, -0.4); g10 = (width + 0.4, 0, -0.4)
    g11 = (width + 0.4, 0, length + 0.4); g01 = (-0.4, 0, length + 0.4)
    svg += quad([g00, g10, g11, g01], ground, '#cfd6e0', 0.5)

    mod_count = max(1, int(modules))
    col_xs = [COL_W / 2]
    for i in range(1, mod_count):
        col_xs.append(width / mod_count * i)
    col_xs.append(width - COL_W / 2)
    col_zs = [COL_W / 2, length - COL_W / 2]
    has_mid_z = max_overhang is not None and length > float(max_overhang) + 0.001
    extra_n = max(int(extra_columns or 0), 0)
    mid_z_positions = []
    if extra_n > 0:
        for i in range(1, extra_n + 1):
            mid_z_positions.append(length / (extra_n + 1) * i)
    elif has_mid_z:
        mid_z_positions.append(length / 2)
    for mz in mid_z_positions:
        col_zs.insert(-1, mz)
    has_mid_z = bool(mid_z_positions)

    column_top = height - BEAM_H

    def draw_column(cx, cz, y0, y1):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light)
        return out

    def draw_beam(x0, x1, z0, z1, y0, y1, tc, fc, sc):
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], fc)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], sc)
        out += quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], tc)
        return out

    by0 = column_top; by1 = height

    back_cols = [(cx, col_zs[-1]) for cx in col_xs]
    back_cols.sort(key=lambda c: -c[0])
    for cx, cz in back_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += draw_beam(0, width, length - COL_W, length, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, COL_W, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    inner_x0 = COL_W
    inner_x1 = width - COL_W
    z_near = COL_W
    z_far = length - COL_W
    z_span = z_far - z_near

    n_panels = max(1, round(z_span / PANEL_W_NOM))
    panel_depth = z_span / n_panels

    RIB_PITCH = 0.075
    pir_shadow = '#7a94b2'
    pir_highlight = '#ddeef8'

    for i in range(n_panels):
        pz0 = z_near + i * panel_depth
        pz1 = z_near + (i + 1) * panel_depth
        svg += quad([(inner_x0, height, pz0), (inner_x0, height, pz1),
                     (inner_x1, height, pz1), (inner_x1, height, pz0)], pir_top, pir_joint, 0.4)
        if i == 0:
            svg += quad([(inner_x0, column_top, pz0), (inner_x0, height, pz0),
                         (inner_x1, height, pz0), (inner_x1, column_top, pz0)], pir_front, pir_joint, 0.4)
        n_ribs = max(1, int(panel_depth / RIB_PITCH))
        actual_pitch = panel_depth / n_ribs
        for k in range(n_ribs + 1):
            rz = pz0 + k * actual_pitch
            if rz > pz1 + 1e-6:
                break
            rz = min(rz, pz1)
            svg += seg((inner_x0, height, rz), (inner_x1, height, rz), pir_shadow, 0.55)
            hlz = rz + actual_pitch * 0.35
            if hlz < pz1 - 1e-6:
                svg += seg((inner_x0, height, hlz), (inner_x1, height, hlz), pir_highlight, 0.5)

    for i in range(1, n_panels):
        jz = z_near + i * panel_depth
        svg += seg((inner_x0, height, jz), (inner_x1, height, jz), pir_joint, 1.2)

    if mod_count >= 2:
        for i in range(1, mod_count):
            cx_mid = width / mod_count * i
            svg += draw_beam(cx_mid - CENTER_BEAM_W / 2, cx_mid + CENTER_BEAM_W / 2,
                             COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(width - COL_W, width, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, width, 0, COL_W, by0, by1, beam_top, beam_front, beam_side)

    if has_mid_z:
        mid_cols = [(cx, col_zs[1]) for cx in col_xs]
        mid_cols.sort(key=lambda c: c[0])
        for cx, cz in mid_cols:
            svg += draw_column(cx, cz, 0, height)

    front_cols = [(cx, col_zs[0]) for cx in col_xs]
    front_cols.sort(key=lambda c: c[0])
    for cx, cz in front_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += _dim_defs('i')

    def _iso_dim(p1, p2, nx, ny, label, off=28, text_off=14):
        d1x = p1[0] + nx * off; d1y = p1[1] + ny * off
        d2x = p2[0] + nx * off; d2y = p2[1] + ny * off
        ang = math.degrees(math.atan2(d2y - d1y, d2x - d1x))
        if ang > 90 or ang < -90:
            ang -= 180
            d1x, d2x = d2x, d1x
            d1y, d2y = d2y, d1y
        midx = (d1x + d2x) / 2; midy = (d1y + d2y) / 2
        tx = midx + nx * text_off; ty = midy + ny * text_off
        return (
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p1[0]+nx*off:.1f}" y2="{p1[1]+ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{p2[0]:.1f}" y1="{p2[1]:.1f}" x2="{p2[0]+nx*off:.1f}" y2="{p2[1]+ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{d1x:.1f}" y1="{d1y:.1f}" x2="{d2x:.1f}" y2="{d2y:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" fill="{DIM_COLOR}" transform="rotate({ang:.1f},{tx:.1f},{ty:.1f})">{label}</text>'
        )

    p_bl = s((0, 0, length)); p_br = s((width, 0, length))
    nx_w = -cos30; ny_w = sin30
    svg += _iso_dim(p_bl, p_br, nx_w, ny_w, f'{width:.2f} м (Ш)')

    p_fr = s((width, 0, 0))
    nx_l = cos30; ny_l = sin30
    svg += _iso_dim(p_fr, p_br, nx_l, ny_l, f'{length:.2f} м (Д)')

    p_btr = s((width, 0, 0)); p_ttr = s((width, height, 0))
    hd_x = max(p_btr[0], p_ttr[0]) + 32
    svg += (
        f'<line x1="{p_btr[0]:.1f}" y1="{p_btr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
        f'<line x1="{p_ttr[0]:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_ttr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
        f'<line x1="{hd_x:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
        f'<text x="{hd_x+14:.1f}" y="{(p_btr[1]+p_ttr[1])/2:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" fill="{DIM_COLOR}" transform="rotate(-90,{hd_x+14:.1f},{(p_btr[1]+p_ttr[1])/2:.1f})">{height:.2f} м (В)</text>'
    )

    svg += (f'<text x="{svg_w/2}" y="22" text-anchor="middle" '
            f'font-size="14px" font-weight="600" fill="#1a3a6e">Изометрия — PIR панели</text>')
    panel_mm = int(round(panel_depth * 1000))
    _psuffix = 'и' if 2 <= n_panels <= 4 else ('ей' if n_panels >= 5 else 'ь')
    svg += (f'<text x="{svg_w/2}" y="{svg_h - 28}" text-anchor="middle" '
            f'font-size="11px" fill="#333">{width:.2f} (Ш) × {length:.2f} (Д) × {height:.2f} (В) м, '
            f'{n_panels} панел{_psuffix} ~{panel_mm} мм</text>')
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


def cleanup_old_calculations(max_age_days=CALC_MAX_AGE_DAYS, trigger='scheduled'):
    calc_dir = _get_calculations_dir()
    cutoff = time.time() - max_age_days * 86400
    removed = 0
    error_msg = None
    try:
        for fname in os.listdir(calc_dir):
            if not fname.endswith('.json'):
                continue
            fpath = os.path.join(calc_dir, fname)
            try:
                if os.path.getmtime(fpath) < cutoff:
                    os.remove(fpath)
                    removed += 1
            except OSError as exc:
                error_msg = str(exc)
                continue
    except OSError as exc:
        error_msg = str(exc)
    if removed:
        logger.info("Cleaned up %d old calculation(s) from %s", removed, calc_dir)
    now = datetime.now()
    cleanup_metrics['last_run_time'] = now.isoformat()
    cleanup_metrics['last_run_dt'] = now
    cleanup_metrics['last_files_removed'] = removed
    cleanup_metrics['total_runs'] += 1
    cleanup_metrics['total_files_removed'] += removed

    entry = {
        'timestamp': now.isoformat(),
        'files_removed': removed,
        'trigger': trigger if trigger in ('manual', 'scheduled', 'startup') else 'scheduled',
        'max_age_days': max_age_days,
    }
    if error_msg:
        entry['error'] = error_msg
    try:
        append_cleanup_history(entry)
    except Exception as exc:
        logger.warning("Failed to append cleanup history entry: %s", exc)
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
