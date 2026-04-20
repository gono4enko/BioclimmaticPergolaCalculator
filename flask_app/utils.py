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


def get_cleanup_history(limit=50, trigger=None, date_from=None, date_to=None,
                        include_total=False, offset=0):
    """Return up to `limit` cleanup history entries, newest first.

    Optional filters:
      trigger   – exact match on entry['trigger'] (e.g. 'manual', 'scheduled', 'startup')
      date_from – inclusive lower bound, 'YYYY-MM-DD' string or datetime.date / datetime.datetime
      date_to   – inclusive upper bound, same format
      offset    – number of newest (post-filter) entries to skip before slicing,
                  enabling pagination through older records. Must be >= 0.

    If `include_total` is True, returns a tuple
    `(entries, total_count, filtered_count)` where `total_count` is the number
    of entries in storage before any filtering and `filtered_count` is the
    number of entries that matched the active filters (before offset/limit
    were applied).
    """
    history = _load_cleanup_history_raw()
    total_count = len(history)

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

    filtered_count = len(history)

    result = list(reversed(history))
    if offset and offset > 0:
        result = result[offset:]
    if limit and limit > 0:
        result = result[:limit]
    if include_total:
        return result, total_count, filtered_count
    return result


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


def generate_top_view_svg(width, length, modules=1, is_pir=False, lamella_count=None, max_overhang=None, ref=None, extra_columns=0, xc_left=0, xc_right=0, xc_front=0, xc_back=0):
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

    col_ys_base = [ry + col_px / 2, ry + rect_h - col_px / 2]

    needs_extra = (max_overhang is not None and length and length > max_overhang + 0.001)
    reinf_rows = max(int(extra_columns or 0), 1 if needs_extra else 0)

    xc_l = max(int(xc_left or 0), 0)
    xc_r = max(int(xc_right or 0), 0)
    xc_f = max(int(xc_front or 0), 0)
    xc_bk = max(int(xc_back or 0), 0)

    left_x = col_xs[0]
    right_x = col_xs[-1]

    def _extra_ys(n):
        return [ry + (rect_h / (n + 1)) * i for i in range(1, n + 1)]

    def _extra_xs(n):
        return [rx + (rect_w / (n + 1)) * i for i in range(1, n + 1)]

    for cxp in col_xs:
        is_left = abs(cxp - left_x) < 2
        is_right = abs(cxp - right_x) < 2
        n_side = max(reinf_rows, xc_l if is_left else (xc_r if is_right else 0))
        ys = col_ys_base + _extra_ys(n_side) if n_side > 0 else col_ys_base
        for cyp in ys:
            svg += (f'<rect x="{cxp - col_px / 2}" y="{cyp - col_px / 2}" '
                    f'width="{col_px}" height="{col_px}" '
                    f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    top_y = col_ys_base[0]
    bot_y = col_ys_base[1]
    for n_fb, y_pos in ((xc_f, top_y), (xc_bk, bot_y)):
        if n_fb > 0:
            for ex in _extra_xs(n_fb):
                svg += (f'<rect x="{ex - col_px / 2}" y="{y_pos - col_px / 2}" '
                        f'width="{col_px}" height="{col_px}" '
                        f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    arrow_y = ry + rect_h + DIM_OFFSET
    svg += _dim_h(rx, rx + rect_w, arrow_y, f'{width:.2f} м', prefix='t', below=True)

    arrow_x = rx - DIM_OFFSET
    svg += _dim_v(arrow_x, ry, ry + rect_h, f'{length:.2f} м', prefix='t', side='left')

    svg += (f'<text x="{rx + rect_w / 2}" y="{ry - 14}" text-anchor="middle" '
            f'font-size="13px" font-weight="bold" fill="{text_color}">Вид сверху · S = {area} м²</text>')

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg


def _draw_zip_fill(x, y, w, h):
    """Draw a vertical ZIP roller awning in elevation view.
    Structure: cassette box (top) → side guide rails → fabric panel → bottom bar.
    Matches the appearance of Decolife/SIMU ZIP100/ZIP130 technical drawings.
    """
    if w < 2 or h < 2:
        return ''
    cassette_c = '#1e2d3a'   # dark aluminium cassette / rails
    rail_c     = '#253545'
    fabric_c   = '#c8d8e8'   # light grey-blue, typical solar-screen tone
    stripe_c   = '#8aa0b2'   # horizontal weft lines
    bottom_c   = '#1e2d3a'   # weighted hem bar

    cassette_h = max(3.5, min(h * 0.07, 11))
    rail_w     = max(2.0, w * 0.04)
    bottom_h   = max(2.0, h * 0.04)

    fy = y + cassette_h                     # fabric top edge
    fh = max(1.0, h - cassette_h - bottom_h)  # fabric height
    fx = x + rail_w                         # fabric left edge
    fw = max(1.0, w - 2 * rail_w)           # fabric width

    out = ''
    # 1. Top cassette housing (where the roller and fabric reel live)
    out += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{cassette_h:.1f}" '
            f'fill="{cassette_c}" rx="1" opacity="0.92"/>')
    # Small drum-circle hint inside the cassette
    dr = max(1.0, cassette_h * 0.30)
    dcx, dcy = x + w / 2, y + cassette_h / 2
    out += (f'<circle cx="{dcx:.1f}" cy="{dcy:.1f}" r="{dr:.1f}" '
            f'fill="none" stroke="#7090a8" stroke-width="0.7" opacity="0.55"/>')

    # 2. Left guide rail
    out += (f'<rect x="{x:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bottom_h:.1f}" fill="{rail_c}" opacity="0.88"/>')
    # 3. Right guide rail
    out += (f'<rect x="{x + w - rail_w:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bottom_h:.1f}" fill="{rail_c}" opacity="0.88"/>')

    # 4. Fabric panel (solar screen)
    out += (f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" '
            f'fill="{fabric_c}" opacity="0.72"/>')
    # 5. Horizontal weft lines (woven screen texture)
    n_lines = max(4, int(fh / 7))
    for i in range(1, n_lines + 1):
        ly = fy + i * fh / (n_lines + 1)
        out += (f'<line x1="{fx:.1f}" y1="{ly:.1f}" x2="{fx + fw:.1f}" y2="{ly:.1f}" '
                f'stroke="{stripe_c}" stroke-width="0.55" opacity="0.55"/>')

    # 6. Bottom weighted bar
    out += (f'<rect x="{fx:.1f}" y="{fy + fh:.1f}" width="{fw:.1f}" height="{bottom_h:.1f}" '
            f'fill="{bottom_c}" opacity="0.88"/>')

    # 7. "ZIP" label centred on fabric
    out += (f'<text x="{x + w / 2:.1f}" y="{fy + fh / 2:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="9px" font-weight="bold" '
            f'fill="#1e2d3a" opacity="0.65">ZIP</text>')
    return out


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


def _draw_s100_glazing_fill(pc, direction, color, glass, x, y, w, h):
    """Frameless S100: thin top + bottom rails (no side frame), thin vertical mullions
    between glass panels. Center-split for 3+3/4+4/6+6 (pc 6 with center, 8, 12)."""
    if w < 4 or h < 4:
        return ''
    pc = max(3, min(12, int(pc)))
    is_center = (direction == 'center') or pc in (8, 12) or (pc == 6 and direction == 'center')
    if color == 'ral9016':
        pC = '#d8d8d8'
    elif color == 'ral8028':
        pC = '#5c3d1e'
    elif color == 'ral7024':
        pC = '#3a4148'
    elif color == 'ral_special':
        pC = '#7a7a7a'
    else:  # ral9t08 default — текст. графит
        pC = '#2e3338'
    is_tinted = (glass == 'tinted_mass')
    if is_tinted:
        cG1, cG2 = '#7d8e96', '#5d7078'
    else:
        cG1, cG2 = '#d8e8f0', '#b8d4e6'
    # Profile heights from spec: top 50mm (3p) / 46mm (4/6p), bottom 20mm
    top_mm = 50 if pc == 3 else 46
    bot_mm = 20
    top_px = max(2.5, min(8, h * (top_mm / 3000.0) * 1.6 + 2.5))
    bot_px = max(1.8, min(5, h * (bot_mm / 3000.0) * 1.6 + 1.5))
    mid_px = max(0.6, min(1.6, w * 0.0035))
    center_px = max(1.2, min(3, w * 0.006))
    # Thin vertical side jambs (frameless still has L/R end profiles per spec photos)
    side_px = max(1.2, min(3.5, w * 0.005))
    out = []
    inner_x = x + side_px
    inner_y = y + top_px
    inner_w = w - 2 * side_px
    inner_h = h - top_px - bot_px
    if inner_w < 4 or inner_h < 4:
        return ''
    if is_center:
        cx = inner_x + inner_w / 2
        out.append(f'<rect x="{cx - center_px / 2:.1f}" y="{inner_y:.1f}" width="{center_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
    half_n = pc / 2 if is_center else pc
    if is_center:
        usable = (inner_w - center_px) / 2
        panel_w = (usable - (half_n - 1) * mid_px) / half_n
    else:
        panel_w = (inner_w - (pc - 1) * mid_px) / pc
    for i in range(pc):
        if is_center:
            section_idx = i % (pc // 2)
            section_off = (inner_w - center_px) / 2 + center_px if i >= pc // 2 else 0
        else:
            section_idx = i
            section_off = 0
        px = inner_x + section_off + section_idx * (panel_w + mid_px)
        if section_idx > 0:
            out.append(f'<rect x="{px - mid_px:.1f}" y="{inner_y:.1f}" width="{mid_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
        out.append(f'<rect x="{px:.1f}" y="{inner_y:.1f}" width="{panel_w:.1f}" height="{inner_h:.1f}" fill="{cG1}" opacity="0.92"/>')
        out.append(f'<rect x="{px + panel_w * 0.55:.1f}" y="{inner_y:.1f}" width="{panel_w * 0.45:.1f}" height="{inner_h:.1f}" fill="{cG2}" opacity="0.35"/>')
    # Top + bottom thin rails
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{top_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y + h - bot_px:.1f}" width="{w:.1f}" height="{bot_px:.1f}" fill="{pC}"/>')
    return ''.join(out)


def _w_color_hex(color):
    if color == 'ral9016':     return '#d8d8d8'
    if color == 'ral8028':     return '#5c3d1e'
    if color == 'ral7024':     return '#3a4148'
    if color == 'ral_special': return '#7a7a7a'
    return '#2e3338'  # ral9t08 default


def _draw_w_glazing_fill(series, sashes, color, glass, x, y, w, h):
    """W500/W600/W700 guillotine: top/middle/bottom horizontal rails,
    no vertical mullions, chain marker on top rail. 2 or 3 sashes."""
    if w < 4 or h < 4:
        return ''
    try:
        sashes = max(2, min(3, int(sashes)))
    except Exception:
        sashes = 2
    pC = _w_color_hex(color)
    is_multi = (glass == 'multifunctional')
    cG1 = '#a8c0d0' if is_multi else '#cce0f0'
    cG2 = '#7d97a8' if is_multi else '#a8c8e0'
    top_px = max(4, min(11, h * 0.06))
    bot_px = max(3, min(7, h * 0.035))
    mid_px = max(2, min(5, h * 0.022))
    side_px = max(2, min(7, w * 0.018))
    out = []
    # Glass background panels (split into N horizontal sashes)
    inner_x = x + side_px
    inner_y = y + top_px
    inner_w = w - 2 * side_px
    inner_h = h - top_px - bot_px
    if inner_w < 4 or inner_h < 4:
        return ''
    sash_h = (inner_h - (sashes - 1) * mid_px) / sashes
    for i in range(sashes):
        sy = inner_y + i * (sash_h + mid_px)
        out.append(f'<rect x="{inner_x:.1f}" y="{sy:.1f}" width="{inner_w:.1f}" height="{sash_h:.1f}" fill="{cG1}"/>')
        out.append(f'<rect x="{inner_x + inner_w * 0.55:.1f}" y="{sy:.1f}" width="{inner_w * 0.4:.1f}" height="{sash_h:.1f}" fill="{cG2}" opacity="0.35"/>')
        if i < sashes - 1:
            out.append(f'<rect x="{inner_x:.1f}" y="{sy + sash_h:.1f}" width="{inner_w:.1f}" height="{mid_px:.1f}" fill="{pC}"/>')
    # Side jambs
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x + w - side_px:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    # Top rail with chain marker
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{top_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y + h - bot_px:.1f}" width="{w:.1f}" height="{bot_px:.1f}" fill="{pC}"/>')
    # Chain marker (small lift indicator) on top rail
    cmx = x + w * 0.5
    cmy = y + top_px * 0.5
    out.append(f'<circle cx="{cmx:.1f}" cy="{cmy:.1f}" r="{min(3, top_px*0.35):.1f}" fill="#dfe7ef" stroke="#1a3a6e" stroke-width="0.6"/>')
    # Series label on bottom rail
    label_y = y + h - bot_px * 0.25
    out.append(f'<text x="{x + w*0.5:.1f}" y="{label_y:.1f}" text-anchor="middle" font-size="6" fill="#dfe7ef" font-family="Arial,sans-serif">{series}</text>')
    return ''.join(out)


def _draw_glazing_fill(spec, x, y, w, h):
    """Render a sliding/guillotine schematic into the elevation opening.
    spec formats:
      S500: 'pc:direction:color:glass'
      S100: 'S100:pc:direction:color:glass'
      W:    'W500|W600|W700:sashes:color:glass'
    """
    if not spec or w < 4 or h < 4:
        return ''
    try:
        parts = (spec or '').split(':')
        head = parts[0].upper() if parts else ''
        if head in ('W500', 'W600', 'W700'):
            sashes = int(parts[1]) if len(parts) >= 2 else 2
            color = parts[2] if len(parts) >= 3 else 'ral9t08'
            glass = parts[3] if len(parts) >= 4 else 'transparent'
            return _draw_w_glazing_fill(head, sashes, color, glass, x, y, w, h)
        series = 'S500'
        if head == 'S100':
            series = 'S100'
            parts = parts[1:]
        if parts and parts[0].upper() == 'S500':
            parts = parts[1:]
        if series == 'S100':
            pc = max(3, min(12, int(parts[0]))) if len(parts) >= 1 else 4
        else:
            pc = max(2, min(10, int(parts[0]))) if len(parts) >= 1 else 4
        direction = parts[1] if len(parts) >= 2 else 'right'
        color = parts[2] if len(parts) >= 3 else ('ral9t08' if series == 'S100' else 'ral7016')
        glass = parts[3] if len(parts) >= 4 else 'transparent'
    except Exception:
        return ''
    if series == 'S100':
        return _draw_s100_glazing_fill(pc, direction, color, glass, x, y, w, h)
    is_center = direction == 'center' or pc in (6, 8, 10)
    if color == 'ral9016':
        pC, pD = '#d0d0d0', '#909090'
    elif color == 'ral8028':
        pC, pD = '#5c3d1e', '#3a2410'
    elif color == 'custom':
        pC, pD = '#777', '#111'
    else:
        pC, pD = '#3a4048', '#111'
    is_tinted = (glass == 'tinted')
    is_bronze = is_tinted and color == 'ral8028'
    if is_bronze:
        cG1, cG2 = '#b8956a', '#9a7548'
    elif is_tinted:
        cG1, cG2 = '#8a9ea8', '#6a8088'
    else:
        cG1, cG2 = '#cce0f0', '#a8c8e0'
    top_px = max(3, min(10, h * 0.05))
    bot_px = max(2, min(6, h * 0.025))
    side_px = max(3, min(10, w * 0.025))
    mid_px = max(1.2, min(3, w * 0.005))
    center_px = max(2, min(6, w * 0.01))
    out = []
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{top_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y + h - bot_px:.1f}" width="{w:.1f}" height="{bot_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x + w - side_px:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    inner_x = x + side_px
    inner_y = y + top_px
    inner_w = w - 2 * side_px
    inner_h = h - top_px - bot_px
    if inner_w < 4 or inner_h < 4:
        return ''.join(out)
    if is_center:
        cx = inner_x + inner_w / 2
        out.append(f'<rect x="{cx - center_px / 2:.1f}" y="{inner_y:.1f}" width="{center_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
    half_n = pc / 2 if is_center else pc
    if is_center:
        usable = (inner_w - center_px) / 2
        panel_w = (usable - (half_n - 1) * mid_px) / half_n
    else:
        panel_w = (inner_w - (pc - 1) * mid_px) / pc
    for i in range(pc):
        if is_center:
            section_idx = i % (pc // 2)
            section_off = (inner_w - center_px) / 2 + center_px if i >= pc // 2 else 0
        else:
            section_idx = i
            section_off = 0
        px = inner_x + section_off + section_idx * (panel_w + mid_px)
        if section_idx > 0:
            out.append(f'<rect x="{px - mid_px:.1f}" y="{inner_y:.1f}" width="{mid_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
        out.append(f'<rect x="{px:.1f}" y="{inner_y:.1f}" width="{panel_w:.1f}" height="{inner_h:.1f}" fill="{cG1}"/>')
        out.append(f'<rect x="{px + panel_w * 0.5:.1f}" y="{inner_y:.1f}" width="{panel_w * 0.5:.1f}" height="{inner_h:.1f}" fill="{cG2}" opacity="0.3"/>')
    rail_y = y + h - bot_px
    out.append(f'<rect x="{x:.1f}" y="{rail_y - 1:.1f}" width="{w:.1f}" height="2" fill="#b8c4cc"/>')
    return ''.join(out)


def generate_front_view_svg(width, height=3.0, modules=1, max_overhang=None, ref=None, title='Вид спереди', extra_columns=0, col_mm=164, beam_h_mm=280, fill_type=None, fills_per_bay=None, glazings_per_bay=None, zips_per_bay=None):
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

    if fills_per_bay or (fill_type and fill_type.strip()) or glazings_per_bay or zips_per_bay:
        fill_y0 = pergola_top + beam_h_px
        fill_h_px = pergola_bottom - fill_y0
        sorted_xs = sorted(col_xs)
        for _bi in range(len(sorted_xs) - 1):
            _fx0 = sorted_xs[_bi] + col_w_px
            _fx1 = sorted_xs[_bi + 1]
            if _fx1 - _fx0 > 2:
                has_zip = bool(zips_per_bay and _bi < len(zips_per_bay) and zips_per_bay[_bi])
                glz_spec = None
                if glazings_per_bay and _bi < len(glazings_per_bay):
                    glz_spec = glazings_per_bay[_bi]
                if glz_spec:
                    svg += _draw_glazing_fill(glz_spec, _fx0, fill_y0, _fx1 - _fx0, fill_h_px)
                else:
                    if fills_per_bay and _bi < len(fills_per_bay) and fills_per_bay[_bi]:
                        bay_fill = fills_per_bay[_bi]
                    else:
                        bay_fill = fill_type
                    svg += _draw_facade_fill(bay_fill, _fx0, fill_y0, _fx1 - _fx0, fill_h_px)
                if has_zip:
                    svg += _draw_zip_fill(_fx0, fill_y0, _fx1 - _fx0, fill_h_px)

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg


def generate_isometric_svg(width, length, height=3.0, lamella_count=None, modules=1, lamella_open_deg=55, max_overhang=None, extra_columns=0, fill_front=None, fill_right=None, fill_left=None, fill_back=None, fills_front_per_bay=None, fills_back_per_bay=None, fills_left_per_bay=None, fills_right_per_bay=None):
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
            line_c = '#1f2a35'
            edge_c = '#26323f'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], bg, edge_c, 1.2)
            n_v_lines = 10
            for _li in range(1, n_v_lines):
                _t = _li / n_v_lines
                def _lerp(a, b, __t=_t):
                    return (a[0]+__t*(b[0]-a[0]), a[1]+__t*(b[1]-a[1]), a[2]+__t*(b[2]-a[2]))
                _out += line(_lerp(pts_bot_left, pts_bot_right), _lerp(pts_top_left, pts_top_right), line_c, 0.6, 0.85)
        elif ft == 'S500':
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.2)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.0),
                          _lerpS(pts_bot_left, pts_bot_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.0)], '#dde8ee', frame_c, 0.4)
            n_panels = 4
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.9, 0.95)
            _out += line(pts_top_left, pts_top_right, frame_c, 1.4, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.4, 1.0)
        elif ft == 'S100':
            # Frameless: lighter, more transparent glass; thin top + bottom rails; thin mullions
            frame_c = '#2e3338'
            glass_c = '#cfe0ea'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 0.5)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            # Subtle slide-stack hint
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.55),
                          _lerpS(pts_bot_left, pts_bot_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 0.55)], '#e6f0f6', frame_c, 0.3)
            n_panels = 6
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.5, 0.7)
            # Heavier top + bottom rails (frameless = no side frame)
            _out += line(pts_top_left, pts_top_right, frame_c, 1.6, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.2, 1.0)
        elif ft.split(':')[0] in ('W500', 'W600', 'W700'):
            # Guillotine: glass panel + thick top/bottom rails + (sashes-1) horizontal mid-rails.
            _wparts = ft.split(':')
            _wseries = _wparts[0]
            try:
                _wsashes = max(2, min(3, int(_wparts[1])))
            except Exception:
                _wsashes = 2
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0' if _wseries == 'W500' else ('#aac7d8' if _wseries == 'W600' else '#9bbacd')
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.0)
            def _lerpW(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            # Draw (sashes-1) horizontal mid-rails evenly spaced between top and bottom
            for _ri in range(1, _wsashes):
                _t = _ri / _wsashes
                _ml = _lerpW(pts_bot_left,  pts_top_left,  _t)
                _mr = _lerpW(pts_bot_right, pts_top_right, _t)
                _out += line(_ml, _mr, frame_c, 1.4, 1.0)
            # Heavy top + bottom rails
            _out += line(pts_top_left, pts_top_right, frame_c, 1.8, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.6, 1.0)
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
        elif ft == 'ZIP':
            def _lz(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            cas_t = 0.07
            bot_t = 0.04
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left],
                         '#c8d8e8', '#1a3a6e', 0.6)
            _cas_bl = _lz(pts_top_left,  pts_bot_left,  cas_t)
            _cas_br = _lz(pts_top_right, pts_bot_right, cas_t)
            _out += quad([_cas_bl, _cas_br, pts_top_right, pts_top_left], '#1e2d3a', '#1e2d3a', 0.3)
            _bot_tl = _lz(pts_bot_left,  pts_top_left,  bot_t)
            _bot_tr = _lz(pts_bot_right, pts_top_right, bot_t)
            _out += quad([pts_bot_left, pts_bot_right, _bot_tr, _bot_tl], '#1e2d3a', '#1e2d3a', 0.3)
            for _li in range(1, 10):
                _t = cas_t + _li * (1.0 - cas_t - bot_t) / 10
                _out += line(_lz(pts_top_left, pts_bot_left, _t), _lz(pts_top_right, pts_bot_right, _t),
                             '#8aa0b2', 0.7, 0.65)
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

    def _front_bay_bounds(_mi):
        _bx0 = col_xs[0] if _mi == 0 else width / mod_count * _mi + COL_W / 2
        _bx1 = col_xs[-1] if _mi == mod_count - 1 else width / mod_count * (_mi + 1) - COL_W / 2
        return _bx0, _bx1

    _sorted_zs = sorted(col_zs)
    _n_lr_bays = max(1, len(_sorted_zs) - 1)

    def _side_bay_bounds(_bi):
        z0 = _sorted_zs[_bi] + COL_W / 2
        z1 = _sorted_zs[_bi + 1] - COL_W / 2
        return z0, z1

    def _bay_specs(side, single, per_bay, n_bays):
        out = []
        for _bi in range(n_bays):
            v = None
            if per_bay is not None and _bi < len(per_bay):
                v = per_bay[_bi]
            elif single and str(single).strip():
                v = single
            out.append(v if (v and str(v).strip()) else None)
        return out

    _front_specs = _bay_specs('front', fill_front, fills_front_per_bay, mod_count)
    _back_specs  = _bay_specs('back',  fill_back,  fills_back_per_bay,  mod_count)
    _left_specs  = _bay_specs('left',  fill_left,  fills_left_per_bay,  _n_lr_bays)
    _right_specs = _bay_specs('right', fill_right, fills_right_per_bay, _n_lr_bays)

    fill_back_svg = ''
    for _mi in range(mod_count):
        _spec = _back_specs[_mi]
        if not _spec: continue
        _bx0, _bx1 = _front_bay_bounds(_mi)
        fill_back_svg += _iso_fill_face(_spec, (_bx0, 0, length), (_bx1, 0, length),
                                        (_bx0, column_top, length), (_bx1, column_top, length))

    fill_left_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _left_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_left_svg += _iso_fill_face(_spec, (0, 0, _z0), (0, 0, _z1),
                                        (0, column_top, _z0), (0, column_top, _z1))

    fill_right_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _right_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_right_svg += _iso_fill_face(_spec, (width, 0, _z0), (width, 0, _z1),
                                         (width, column_top, _z0), (width, column_top, _z1))

    fill_front_svg = ''
    any_other_fill = any(_back_specs) or any(_left_specs) or any(_right_specs)
    for _mi in range(mod_count):
        _fx0, _fx1 = _front_bay_bounds(_mi)
        _pbl = (_fx0, 0, 0); _pbr = (_fx1, 0, 0)
        _ptl = (_fx0, column_top, 0); _ptr = (_fx1, column_top, 0)
        _spec = _front_specs[_mi]
        if _spec:
            fill_front_svg += _iso_fill_face(_spec, _pbl, _pbr, _ptl, _ptr)
        elif any_other_fill:
            coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in [_pbl, _pbr, _ptr, _ptl]))
            fill_front_svg += f'<polygon points="{coords}" fill="#eef2f7" fill-opacity="0.78" stroke="#2a4a7e" stroke-width="1.0" stroke-dasharray="6,3" stroke-linejoin="round"/>'

    SW_SIL = 1.2

    def draw_column(cx, cz, y0, y1, sw=SW_SIL):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark, '#1a3a6e', sw)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light, '#1a3a6e', sw)
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

    def draw_beam(x0, x1, z0, z1, y0, y1, top_c, front_c, side_c, sw=SW_SIL):
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], front_c, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], side_c, '#1a3a6e', sw)
        out += quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], top_c, '#1a3a6e', sw)
        return out

    svg += fill_left_svg
    svg += fill_right_svg
    svg += fill_front_svg

    svg += draw_beam(0, width, length - COL_W, length, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, COL_W, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(width - COL_W, width, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, width, 0, COL_W, by0, by1, beam_top, beam_front, beam_side)

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

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg


def generate_pir_iso_svg(width, length, height=3.0, modules=1, max_overhang=None, extra_columns=0, fill_front=None, fill_right=None, fill_left=None, fill_back=None, fills_front_per_bay=None, fills_back_per_bay=None, fills_left_per_bay=None, fills_right_per_bay=None):
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

    def line(p1, p2, stroke='#1a3a6e', sw=0.6, opacity=1.0):
        x1, y1 = s(p1); x2, y2 = s(p2)
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'

    col_dark = '#143055'; col_med = '#2a4a7e'; col_light = '#3d6396'
    beam_top = '#b8c8df'; beam_front = '#7d9bc0'; beam_side = '#5d7da8'
    pir_top = '#c8d8eb'; pir_front = '#8fafc8'; pir_joint = '#6a87a8'
    ground = '#eef2f7'

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
                _out += seg(_lerp(pts_bot_left, pts_top_left), _lerp(pts_bot_right, pts_top_right), line_c, 0.7)
        elif ft == 'S500':
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.2)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.0),
                          _lerpS(pts_bot_left, pts_bot_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.0)], '#dde8ee', frame_c, 0.4)
            n_panels = 4
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.9, 0.95)
            _out += line(pts_top_left, pts_top_right, frame_c, 1.4, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.4, 1.0)
        elif ft == 'S100':
            frame_c = '#2e3338'
            glass_c = '#cfe0ea'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 0.5)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.55),
                          _lerpS(pts_bot_left, pts_bot_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 0.55)], '#e6f0f6', frame_c, 0.3)
            n_panels = 6
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.5, 0.7)
            _out += seg(pts_top_left, pts_top_right, frame_c, 1.6)
            _out += seg(pts_bot_left, pts_bot_right, frame_c, 1.2)
        elif ft.split(':')[0] in ('W500', 'W600', 'W700'):
            _wparts = ft.split(':')
            _wseries = _wparts[0]
            try:
                _wsashes = max(2, min(3, int(_wparts[1])))
            except Exception:
                _wsashes = 2
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0' if _wseries == 'W500' else ('#aac7d8' if _wseries == 'W600' else '#9bbacd')
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.0)
            def _lerpW(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            for _ri in range(1, _wsashes):
                _t = _ri / _wsashes
                _ml = _lerpW(pts_bot_left,  pts_top_left,  _t)
                _mr = _lerpW(pts_bot_right, pts_top_right, _t)
                _out += seg(_ml, _mr, frame_c, 1.4)
            _out += seg(pts_top_left, pts_top_right, frame_c, 1.8)
            _out += seg(pts_bot_left, pts_bot_right, frame_c, 1.6)
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
        elif ft == 'ZIP':
            def _lz(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            cas_t = 0.07
            bot_t = 0.04
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left],
                         '#c8d8e8', '#1a3a6e', 0.6)
            _cas_bl = _lz(pts_top_left,  pts_bot_left,  cas_t)
            _cas_br = _lz(pts_top_right, pts_bot_right, cas_t)
            _out += quad([_cas_bl, _cas_br, pts_top_right, pts_top_left], '#1e2d3a', '#1e2d3a', 0.3)
            _bot_tl = _lz(pts_bot_left,  pts_top_left,  bot_t)
            _bot_tr = _lz(pts_bot_right, pts_top_right, bot_t)
            _out += quad([pts_bot_left, pts_bot_right, _bot_tr, _bot_tl], '#1e2d3a', '#1e2d3a', 0.3)
            for _li in range(1, 10):
                _t = cas_t + _li * (1.0 - cas_t - bot_t) / 10
                _out += seg(_lz(pts_top_left, pts_bot_left, _t), _lz(pts_top_right, pts_bot_right, _t),
                            '#8aa0b2', 0.7)
        return _out

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

    SW_SIL = 1.2

    def draw_column(cx, cz, y0, y1, sw=SW_SIL):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark, '#1a3a6e', sw)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light, '#1a3a6e', sw)
        return out

    def draw_beam(x0, x1, z0, z1, y0, y1, tc, fc, sc, sw=SW_SIL):
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], fc, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], sc, '#1a3a6e', sw)
        out += quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], tc, '#1a3a6e', sw)
        return out

    by0 = column_top; by1 = height

    def _front_bay_bounds(_mi):
        _bx0 = col_xs[0] if _mi == 0 else width / mod_count * _mi + COL_W / 2
        _bx1 = col_xs[-1] if _mi == mod_count - 1 else width / mod_count * (_mi + 1) - COL_W / 2
        return _bx0, _bx1

    _sorted_zs = sorted(col_zs)
    _n_lr_bays = max(1, len(_sorted_zs) - 1)

    def _side_bay_bounds(_bi):
        z0 = _sorted_zs[_bi] + COL_W / 2
        z1 = _sorted_zs[_bi + 1] - COL_W / 2
        return z0, z1

    def _bay_specs(single, per_bay, n_bays):
        out = []
        for _bi in range(n_bays):
            v = None
            if per_bay is not None and _bi < len(per_bay):
                v = per_bay[_bi]
            elif single and str(single).strip():
                v = single
            out.append(v if (v and str(v).strip()) else None)
        return out

    _front_specs = _bay_specs(fill_front, fills_front_per_bay, mod_count)
    _back_specs  = _bay_specs(fill_back,  fills_back_per_bay,  mod_count)
    _left_specs  = _bay_specs(fill_left,  fills_left_per_bay,  _n_lr_bays)
    _right_specs = _bay_specs(fill_right, fills_right_per_bay, _n_lr_bays)

    fill_back_svg = ''
    for _mi in range(mod_count):
        _spec = _back_specs[_mi]
        if not _spec: continue
        _bx0, _bx1 = _front_bay_bounds(_mi)
        fill_back_svg += _iso_fill_face(_spec, (_bx0, 0, length), (_bx1, 0, length),
                                        (_bx0, column_top, length), (_bx1, column_top, length))
    fill_left_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _left_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_left_svg += _iso_fill_face(_spec, (0, 0, _z0), (0, 0, _z1),
                                        (0, column_top, _z0), (0, column_top, _z1))
    fill_right_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _right_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_right_svg += _iso_fill_face(_spec, (width, 0, _z0), (width, 0, _z1),
                                         (width, column_top, _z0), (width, column_top, _z1))
    fill_front_svg = ''
    any_other_fill = any(_back_specs) or any(_left_specs) or any(_right_specs)
    for _mi in range(mod_count):
        _fx0, _fx1 = _front_bay_bounds(_mi)
        _pbl = (_fx0, 0, 0); _pbr = (_fx1, 0, 0)
        _ptl = (_fx0, column_top, 0); _ptr = (_fx1, column_top, 0)
        _spec = _front_specs[_mi]
        if _spec:
            fill_front_svg += _iso_fill_face(_spec, _pbl, _pbr, _ptl, _ptr)
        elif any_other_fill:
            coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in [_pbl, _pbr, _ptr, _ptl]))
            fill_front_svg += f'<polygon points="{coords}" fill="#eef2f7" fill-opacity="0.78" stroke="#2a4a7e" stroke-width="1.0" stroke-dasharray="6,3" stroke-linejoin="round"/>'

    svg += fill_back_svg

    back_cols = [(cx, col_zs[-1]) for cx in col_xs]
    back_cols.sort(key=lambda c: -c[0])
    for cx, cz in back_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += fill_left_svg
    svg += fill_right_svg
    svg += fill_front_svg

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

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
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


def generate_zip_detail_svg(zip_type='ZIP100', w_m=2.0, h_m=2.7, fabric='Veozip (Screen Veosol)'):
    """Generate a labeled technical elevation sketch of a ZIP roller awning.

    Shows cassette housing, guide rails, fabric panel, bottom bar, and
    annotation callouts — suitable for embedding in the КП scheme section.
    """
    vw, vh = 620, 400
    dark  = '#1e2d3a'
    mid   = '#253545'
    fab_c = '#c8d8e8'
    str_c = '#8aa0b2'
    ann   = '#1a3a6e'

    cassette_mm = 100 if zip_type == 'ZIP100' else 130
    max_area    = '≈ 14 м²' if zip_type == 'ZIP100' else '≤ 25 м²'

    lbl_w   = 175
    rpad    = 60   # extra right margin to fit height dimension
    drw_x0  = lbl_w + 10
    drw_x1  = vw - rpad
    drw_y0  = 55
    drw_y1  = vh - 48
    drw_w   = drw_x1 - drw_x0
    drw_h   = drw_y1 - drw_y0

    h_mm    = h_m * 1000
    w_mm    = w_m * 1000
    cas_h   = max(8, min(22, cassette_mm / h_mm * drw_h))
    rail_w  = max(4, min(14, 50 / w_mm * drw_w))
    bot_h   = max(4, min(14, 40 / h_mm * drw_h))

    fy      = drw_y0 + cas_h
    fh      = max(10, drw_h - cas_h - bot_h)
    fx      = drw_x0 + rail_w
    fw      = max(10, drw_w - 2 * rail_w)

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" '
           f'width="{vw}" height="{vh}" font-family="Arial, sans-serif">')

    svg += (f'<rect width="{vw}" height="{vh}" fill="#f7f9fc" rx="8"/>')

    title_text = f'{zip_type} — Вертикальная ZIP-маркиза'
    svg += (f'<text x="{vw/2:.1f}" y="28" text-anchor="middle" font-size="14px" '
            f'font-weight="bold" fill="{ann}">{title_text}</text>')
    svg += (f'<text x="{vw/2:.1f}" y="45" text-anchor="middle" font-size="11px" '
            f'fill="#555">Короб {cassette_mm}×{cassette_mm} мм · max {max_area} · {w_m:.2f}×{h_m:.2f} м</text>')

    svg += (f'<rect x="{drw_x0}" y="{drw_y0}" width="{drw_w}" height="{cas_h:.1f}" '
            f'fill="{dark}" rx="2" opacity="0.93"/>')
    dr_r = max(4.0, cas_h * 0.28)
    svg += (f'<circle cx="{drw_x0 + drw_w/2:.1f}" cy="{drw_y0 + cas_h/2:.1f}" r="{dr_r:.1f}" '
            f'fill="none" stroke="#6a8fa8" stroke-width="1.2" opacity="0.6"/>')

    svg += (f'<rect x="{drw_x0:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bot_h:.1f}" fill="{mid}" opacity="0.90"/>')
    svg += (f'<rect x="{drw_x0 + drw_w - rail_w:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bot_h:.1f}" fill="{mid}" opacity="0.90"/>')

    svg += (f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" '
            f'fill="{fab_c}" opacity="0.75"/>')
    n_lines = max(12, int(fh / 8))
    for i in range(1, n_lines + 1):
        ly = fy + i * fh / (n_lines + 1)
        svg += (f'<line x1="{fx:.1f}" y1="{ly:.1f}" x2="{fx + fw:.1f}" y2="{ly:.1f}" '
                f'stroke="{str_c}" stroke-width="0.8" opacity="0.65"/>')

    svg += (f'<rect x="{fx:.1f}" y="{fy + fh:.1f}" width="{fw:.1f}" height="{bot_h:.1f}" '
            f'fill="{dark}" opacity="0.90"/>')

    def ann_line(label1, label2, ty, target_x, target_y, anchor='end'):
        lx = lbl_w - 4
        svg_l = ''
        svg_l += (f'<text x="{lx}" y="{ty}" text-anchor="{anchor}" font-size="10.5px" '
                  f'fill="{ann}" font-weight="600">{label1}</text>')
        if label2:
            svg_l += (f'<text x="{lx}" y="{ty+14}" text-anchor="{anchor}" font-size="9.5px" '
                      f'fill="#555">{label2}</text>')
        arrow_start_x = lx + 2
        svg_l += (f'<line x1="{arrow_start_x}" y1="{ty - 4}" x2="{target_x}" y2="{target_y}" '
                  f'stroke="{ann}" stroke-width="0.9" stroke-dasharray="3,2"/>')
        svg_l += (f'<circle cx="{target_x}" cy="{target_y}" r="2.5" fill="{ann}"/>')
        return svg_l

    cas_y_mid = drw_y0 + cas_h / 2
    rail_mid_y = fy + fh * 0.38
    fab_mid_y  = fy + fh * 0.55
    bot_mid_y  = fy + fh + bot_h / 2

    svg += ann_line('Кассета (короб)', f'{cassette_mm}×{cassette_mm} мм · Ø{78 if cassette_mm==130 else 55} мм вал',
                    int(cas_y_mid), drw_x0 + drw_w * 0.4, cas_y_mid)
    svg += ann_line('Боковые направляющие', 'ZIP-канал (zip-замок)', int(rail_mid_y), drw_x0 + rail_w / 2, rail_mid_y)
    svg += ann_line('Полотно', fabric, int(fab_mid_y), fx + fw * 0.35, fab_mid_y)
    svg += ann_line('Нижняя планка', '(утяжелитель)', int(bot_mid_y), fx + fw * 0.3, bot_mid_y)

    hline_x = drw_x1 + 16
    svg += (f'<line x1="{hline_x}" y1="{drw_y0}" x2="{hline_x + 6}" y2="{drw_y0}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{hline_x}" y1="{drw_y1}" x2="{hline_x + 6}" y2="{drw_y1}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{hline_x + 3}" y1="{drw_y0}" x2="{hline_x + 3}" y2="{drw_y1}" '
            f'stroke="{ann}" stroke-width="0.9" marker-start="url(#dah)" marker-end="url(#dah2)"/>')
    svg += (f'<defs><marker id="dah" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">'
            f'<path d="M6,0 L0,3 L6,6" stroke="{ann}" stroke-width="0.8" fill="none"/></marker>'
            f'<marker id="dah2" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse">'
            f'<path d="M6,0 L0,3 L6,6" stroke="{ann}" stroke-width="0.8" fill="none"/></marker>'
            f'</defs>')
    svg += (f'<text x="{hline_x + 14}" y="{(drw_y0 + drw_y1)/2:.1f}" text-anchor="middle" '
            f'font-size="10px" fill="{ann}" font-weight="600" '
            f'transform="rotate(-90,{hline_x + 14},{(drw_y0 + drw_y1)/2:.1f})">{h_m:.2f} м</text>')

    wline_y = drw_y1 + 22
    svg += (f'<line x1="{drw_x0}" y1="{wline_y}" x2="{drw_x0}" y2="{wline_y + 5}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{drw_x1}" y1="{wline_y}" x2="{drw_x1}" y2="{wline_y + 5}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{drw_x0}" y1="{wline_y + 3}" x2="{drw_x1}" y2="{wline_y + 3}" '
            f'stroke="{ann}" stroke-width="0.9" marker-start="url(#dah)" marker-end="url(#dah2)"/>')
    svg += (f'<text x="{(drw_x0 + drw_x1)/2:.1f}" y="{wline_y + 17}" text-anchor="middle" '
            f'font-size="10px" fill="{ann}" font-weight="600">{w_m:.2f} м</text>')

    zip_mech_y = fy + fh * 0.18
    zip_mech_x = fx - 1
    svg += (f'<rect x="{zip_mech_x - 3:.1f}" y="{zip_mech_y - 5:.1f}" width="5" height="10" '
            f'fill="#a0b8c8" rx="1" opacity="0.75"/>')

    svg += '</svg>'
    return svg
