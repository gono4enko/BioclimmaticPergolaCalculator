import os
import json
import base64
import re
import csv
import threading
from functools import wraps
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, current_app

bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            if request.is_json or request.content_type and 'multipart' in request.content_type:
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('admin.login_page'))
        return f(*args, **kwargs)
    return decorated


@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if not ADMIN_PASSWORD:
            error = 'ADMIN_PASSWORD не настроен'
        elif password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.prices_page'))
        else:
            error = 'Неверный пароль'
    return render_template('admin_login.html', error=error)


@bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login_page'))


@bp.route('/prices')
@admin_required
def prices_page():
    return render_template('admin_prices.html')


@bp.route('/get-prices', methods=['GET'])
@admin_required
def get_prices():
    pergola_type = request.args.get('pergola_type', '')
    lamella_size = request.args.get('lamella_size', '')
    if not pergola_type or not lamella_size:
        return jsonify({'error': 'Не указаны параметры'}), 400

    try:
        import psycopg2
        with psycopg2.connect(os.environ.get('DATABASE_URL', '')) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT width, length, price, modules FROM price_data WHERE pergola_type=%s AND lamella_size=%s ORDER BY width, length",
                    (pergola_type, lamella_size)
                )
                rows = cur.fetchall()

        if not rows:
            return jsonify({'ok': True, 'data': None, 'message': 'Нет данных'})

        def fnum(v):
            return f"{float(v):.1f}" if float(v) == int(float(v)) else f"{float(v):.2f}"

        length_module_pairs = {}
        for w, l, p, m in rows:
            lk = fnum(l)
            mi = int(m) if m else 1
            if lk not in length_module_pairs:
                length_module_pairs[lk] = set()
            length_module_pairs[lk].add(mi)

        boundary_lengths = {lk for lk, mods in length_module_pairs.items() if len(mods) > 1}

        depths_set = sorted(set(fnum(r[0]) for r in rows), key=lambda x: float(x))
        widths_keys = []
        seen_width_keys = set()
        modules_map = {}
        prices = {}

        for w, l, p, m in sorted(rows, key=lambda r: (float(r[1]), int(r[3]) if r[3] else 1)):
            dk = fnum(w)
            lk = fnum(l)
            mi = int(m) if m else 1

            if lk in boundary_lengths:
                min_mod = min(length_module_pairs[lk])
                if mi == min_mod:
                    wk = lk
                else:
                    wk = lk + '+'
            else:
                wk = lk

            if wk not in seen_width_keys:
                seen_width_keys.add(wk)
                widths_keys.append(wk)
            modules_map[wk] = mi

            if dk not in prices:
                prices[dk] = {}
            prices[dk][wk] = int(round(float(p))) if p else None

        def width_sort_key(w):
            s = str(w).strip()
            if s.endswith('+'):
                return (float(s[:-1]), 1)
            return (float(s), 0)

        widths_sorted = sorted(widths_keys, key=width_sort_key)

        return jsonify({
            'ok': True,
            'data': {
                'widths': widths_sorted,
                'depths': depths_set,
                'prices': prices,
                'modules': modules_map,
            }
        })
    except Exception:
        return jsonify({'error': 'Ошибка загрузки цен'}), 500


@bp.route('/parse-price-image', methods=['POST'])
@admin_required
def parse_price_image():
    import anthropic

    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'ANTHROPIC_API_KEY не настроен'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'Файл не прикреплён'}), 400

    img_file = request.files['image']
    ext = img_file.filename.rsplit('.', 1)[-1].lower()
    if ext not in {'png', 'jpg', 'jpeg', 'webp'}:
        return jsonify({'error': f'Формат {ext} не поддерживается'}), 400

    img_bytes = img_file.read()
    b64 = base64.b64encode(img_bytes).decode()
    media_type = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'

    prompt = """You are a precise OCR engine for price tables of bioclimatic pergolas.
TASK: Extract ALL prices from this price table image.
TABLE STRUCTURE:
- LEFT column: вынос/вылет (depth/projection) values in meters (rows)
- TOP row: ширина (width) values in meters (columns)
- Columns are organized by module groups: 1 модуль, 2 модуля, 3 модуля
- Each cell may contain TWO numbers:
  * MAIN price (larger number) — extract this
  * Secondary price with asterisk *NNN (price per m²) — IGNORE completely
DUPLICATE WIDTH COLUMNS AT MODULE BOUNDARIES:
- Some widths appear TWICE at module boundaries (e.g. 4.5m, 9.0m)
- First occurrence: key as-is (e.g. "4.5") — belongs to lower module group
- Second occurrence: key with "+" suffix (e.g. "4.5+") — belongs to higher module group
- Extract BOTH prices separately
MODULE INFORMATION:
- For each width column, note which module group it belongs to (1, 2, or 3)
- Include this in the output
GENERAL RULES:
1. Numbers use space as thousand separator: "4 512" = 4512
2. All prices are positive integers in EUR
3. If a cell is empty, use null
4. Decimal separators in row/column headers may be "." or ","
OUTPUT FORMAT — return ONLY valid JSON, no markdown:
{
  "widths": ["2.5","3.0","3.5","4.0","4.5","5.0","6.0",...],
  "depths": ["2.5","3.0","3.5","4.0","4.5","5.0",...],
  "modules": {"2.5": 1, "3.0": 1, "4.5": 1, "4.5+": 2, "5.0": 2, ...},
  "prices": {
    "2.5": {"2.5": 5431, "3.0": 5945, "4.5": 7488, "4.5+": 10289, ...},
    "3.0": {...}
  }
}
Outer key of "prices" = depth/вынос row. Inner key = width/ширина column."""

    try:
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=8192,
            messages=[{
                'role': 'user',
                'content': [
                    {'type': 'image', 'source': {'type': 'base64', 'media_type': media_type, 'data': b64}},
                    {'type': 'text', 'text': prompt}
                ]
            }]
        )

        raw = response.content[0].text.strip()
        if raw.startswith('```'):
            raw = re.sub(r'^```[a-z]*\n?', '', raw)
            raw = re.sub(r'\n?```$', '', raw.strip())

        parsed = json.loads(raw)
        if 'prices' not in parsed or 'widths' not in parsed or 'depths' not in parsed:
            return jsonify({'error': 'Неожиданный формат ответа', 'raw': raw[:600]}), 422

        def fmt_depth(v):
            try:
                return f"{float(str(v).replace(',', '.')):.2f}"
            except:
                return str(v)

        def fmt_width(v):
            s = str(v).strip()
            if s.endswith('+'):
                try:
                    return f"{float(s[:-1].replace(',', '.')):.1f}+"
                except:
                    return s
            try:
                return f"{float(s.replace(',', '.')):.1f}"
            except:
                return s

        def width_sort_key(w):
            s = str(w).strip()
            if s.endswith('+'):
                return (float(s[:-1]), 1)
            try:
                return (float(s), 0)
            except:
                return (999, 0)

        widths_sorted = sorted([fmt_width(w) for w in parsed['widths']], key=width_sort_key)
        depths_sorted = sorted([fmt_depth(d) for d in parsed['depths']], key=lambda d: float(d))

        modules = {}
        if 'modules' in parsed:
            for w, m in parsed['modules'].items():
                modules[fmt_width(w)] = int(m)

        normalized = {}
        for d_raw, row in parsed['prices'].items():
            d_key = fmt_depth(d_raw)
            normalized[d_key] = {}
            for w_raw, price in row.items():
                w_key = fmt_width(w_raw)
                if price is not None:
                    try:
                        normalized[d_key][w_key] = int(float(
                            str(price).replace(' ', '').replace('\u00a0', '')
                        ))
                    except:
                        normalized[d_key][w_key] = None
                else:
                    normalized[d_key][w_key] = None

        boundary_widths = [w for w in widths_sorted if w.endswith('+')]
        if boundary_widths:
            verify_prompt = f"""You are verifying OCR results for a price table. Look at the image again.
BOUNDARY COLUMNS to verify: {', '.join(boundary_widths)}
These are duplicate width columns at module boundaries (e.g. 4.5 appears in both 1-module and 2-module groups).
The "+" suffix means the column belongs to the HIGHER module group.

For each boundary width, verify the prices in the FIRST 3 depth rows.
First-pass extracted these values:
"""
            for bw in boundary_widths[:4]:
                bw_base = bw.rstrip('+')
                verify_prompt += f"\nWidth {bw_base} (lower module) vs {bw} (higher module):\n"
                for d in depths_sorted[:3]:
                    p_base = normalized.get(d, {}).get(bw_base, 'null')
                    p_plus = normalized.get(d, {}).get(bw, 'null')
                    verify_prompt += f"  depth {d}: base={p_base}, plus={p_plus}\n"

            verify_prompt += """
Return ONLY valid JSON with corrections (or empty corrections if all correct):
{"corrections": {"depth_key": {"width_key": corrected_price, ...}, ...}}
Only include cells that need correction. Return {"corrections": {}} if all values are correct."""

            try:
                verify_resp = client.messages.create(
                    model='claude-sonnet-4-20250514',
                    max_tokens=2048,
                    messages=[{
                        'role': 'user',
                        'content': [
                            {'type': 'image', 'source': {'type': 'base64', 'media_type': media_type, 'data': b64}},
                            {'type': 'text', 'text': verify_prompt}
                        ]
                    }]
                )
                vraw = verify_resp.content[0].text.strip()
                if vraw.startswith('```'):
                    vraw = re.sub(r'^```[a-z]*\n?', '', vraw)
                    vraw = re.sub(r'\n?```$', '', vraw.strip())
                corrections = json.loads(vraw).get('corrections', {})
                applied_corrections = 0
                for d_key, row_corr in corrections.items():
                    fd = fmt_depth(d_key)
                    if fd in normalized:
                        for w_key, new_price in row_corr.items():
                            fw = fmt_width(w_key)
                            if new_price is not None:
                                normalized[fd][fw] = int(float(str(new_price).replace(' ', '')))
                                applied_corrections += 1
            except Exception:
                pass

        filled = sum(1 for row in normalized.values() for v in row.values() if v is not None)
        total = len(depths_sorted) * len(widths_sorted)

        return jsonify({
            'ok': True,
            'data': {
                'widths': widths_sorted,
                'depths': depths_sorted,
                'prices': normalized,
                'modules': modules,
            },
            'filled': filled,
            'total': total,
        })

    except json.JSONDecodeError:
        return jsonify({'error': 'Ошибка разбора ответа ИИ'}), 422
    except Exception:
        return jsonify({'error': 'Ошибка обработки изображения'}), 500


@bp.route('/apply-parsed-prices', methods=['POST'])
@admin_required
def apply_parsed_prices():
    body = request.get_json(silent=True) or {}
    pergola_type = body.get('pergola_type', '').strip()
    lamella_size = body.get('lamella_size', '').strip()
    widths_in = body.get('widths', [])
    depths_in = body.get('depths', [])
    prices_in = body.get('prices', {})
    modules_in = body.get('modules', {})

    if not pergola_type or not lamella_size or not widths_in or not depths_in or not prices_in:
        return jsonify({'error': 'Недостаточно данных'}), 400

    try:
        import psycopg2
        with psycopg2.connect(os.environ.get('DATABASE_URL', '')) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM price_data WHERE pergola_type=%s AND lamella_size=%s",
                            (pergola_type, lamella_size))

                inserted = 0
                for d_str in depths_in:
                    d_val = float(str(d_str).replace(',', '.').rstrip('+'))
                    row = prices_in.get(str(d_str), {})
                    for w_str in widths_in:
                        price = row.get(str(w_str))
                        if price is None:
                            continue
                        try:
                            price_val = float(str(price).replace(' ', ''))
                        except:
                            continue

                        w_val = float(str(w_str).replace(',', '.').rstrip('+'))
                        mod = modules_in.get(str(w_str), 1)

                        cur.execute(
                            "INSERT INTO price_data (pergola_type, lamella_size, width, length, price, modules, updated_at) VALUES (%s,%s,%s,%s,%s,%s,NOW())",
                            (pergola_type, lamella_size, d_val, w_val, price_val, mod)
                        )
                        inserted += 1

            conn.commit()

        from ..services.calculator import clear_price_cache
        clear_price_cache()

        return jsonify({'ok': True, 'inserted': inserted})

    except Exception:
        return jsonify({'error': 'Ошибка сохранения цен'}), 500


@bp.route('/save-cell', methods=['POST'])
@admin_required
def save_cell():
    body = request.get_json(silent=True) or {}
    pergola_type = body.get('pergola_type', '').strip()
    lamella_size = body.get('lamella_size', '').strip()
    depth = body.get('depth')
    width = body.get('width')
    price = body.get('price')

    if not all([pergola_type, lamella_size, depth is not None, width is not None, price is not None]):
        return jsonify({'error': 'Недостаточно данных'}), 400

    try:
        import psycopg2
        d_val = float(str(depth).replace(',', '.'))

        w_str = str(width).strip()
        is_boundary_plus = w_str.endswith('+')
        w_val = float(w_str.rstrip('+').replace(',', '.'))
        p_val = float(str(price).replace(' ', ''))

        from ..services.calculator import get_modules_by_dimensions
        base_mod = get_modules_by_dimensions(w_val, None)
        if is_boundary_plus:
            target_mod = base_mod + 1 if base_mod < 3 else 3
        else:
            target_mod = base_mod

        with psycopg2.connect(os.environ.get('DATABASE_URL', '')) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE price_data SET price=%s, updated_at=NOW() WHERE pergola_type=%s AND lamella_size=%s AND width=%s AND length=%s AND modules=%s",
                    (p_val, pergola_type, lamella_size, d_val, w_val, target_mod)
                )
                if cur.rowcount == 0:
                    cur.execute(
                        "INSERT INTO price_data (pergola_type, lamella_size, width, length, price, modules, updated_at) VALUES (%s,%s,%s,%s,%s,%s,NOW())",
                        (pergola_type, lamella_size, d_val, w_val, p_val, target_mod)
                    )
            conn.commit()

        from ..services.calculator import clear_price_cache
        clear_price_cache()

        return jsonify({'ok': True})
    except Exception:
        return jsonify({'error': 'Ошибка сохранения'}), 500


@bp.route('/scheduler-status')
@admin_required
def scheduler_status():
    from ..utils import cleanup_metrics, CALC_MAX_AGE_DAYS

    scheduler = current_app.extensions.get('cleanup_scheduler')

    next_run = None
    scheduler_running = False
    interval_hours = None

    if scheduler:
        scheduler_running = scheduler.running
        job = scheduler.get_job('cleanup_old_calculations')
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()
        if job and job.trigger:
            try:
                interval_hours = job.trigger.interval.total_seconds() / 3600
            except Exception:
                pass

    return jsonify({
        'ok': True,
        'scheduler_running': scheduler_running,
        'interval_hours': interval_hours,
        'retention_days': CALC_MAX_AGE_DAYS,
        'next_run': next_run,
        'last_run_time': cleanup_metrics['last_run_time'],
        'last_files_removed': cleanup_metrics['last_files_removed'],
        'total_runs': cleanup_metrics['total_runs'],
        'total_files_removed': cleanup_metrics['total_files_removed'],
    })
