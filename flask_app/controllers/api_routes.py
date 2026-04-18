"""
API маршруты для калькулятора пергол.
"""
import os
import json
import datetime
import threading
import time
from io import BytesIO
from flask import Blueprint, jsonify, request, current_app, send_file
from ..services.calculator import (
    perform_calculation,
    perform_all_variants_calculation,
    get_pergola_types_list,
    get_lamella_sizes_for_type,
    get_max_dimensions,
    adjust_length_for_lamella_size,
    get_modules_by_dimensions
)

bp = Blueprint('api', __name__)


@bp.route('/pergola-scheme.svg', methods=['GET'])
def pergola_scheme_svg():
    from flask import Response
    from ..utils import generate_top_view_svg
    try:
        w = float(request.args.get('w', 0))
        l = float(request.args.get('l', 0))
        m = int(request.args.get('m', 1))
        lc = request.args.get('lc')
        lc = int(lc) if lc and lc.isdigit() else None
        mo = request.args.get('mo')
        mo = float(mo) if mo else None
        pir = request.args.get('pir', '0') == '1'
        if w <= 0 or l <= 0:
            return Response('', status=400)
        ref_raw = request.args.get('ref')
        ref = float(ref_raw) if ref_raw else None
        xc_raw = request.args.get('xc')
        xc = int(xc_raw) if xc_raw and xc_raw.isdigit() else 0
        svg = generate_top_view_svg(width=w, length=l, modules=m,
                                    is_pir=pir, lamella_count=lc, max_overhang=mo, ref=ref,
                                    extra_columns=xc)
        return Response(svg, mimetype='image/svg+xml',
                        headers={'Cache-Control': 'no-cache, must-revalidate'})
    except Exception:
        return Response('', status=400)


@bp.route('/pergola-front.svg', methods=['GET'])
def pergola_front_svg():
    from flask import Response
    from ..utils import generate_front_view_svg
    try:
        w = float(request.args.get('w', 0))
        h = float(request.args.get('h', 3.0))
        m = int(request.args.get('m', 1))
        mo = request.args.get('mo')
        mo = float(mo) if mo else None
        if w <= 0:
            return Response('', status=400)
        ref_raw = request.args.get('ref')
        ref = float(ref_raw) if ref_raw else None
        title = request.args.get('title') or 'Вид спереди'
        xc_raw = request.args.get('xc')
        xc = int(xc_raw) if xc_raw and xc_raw.isdigit() else 0
        cm_raw = request.args.get('col_mm')
        col_mm = int(cm_raw) if cm_raw and cm_raw.isdigit() else 164
        bh_raw = request.args.get('beam_h_mm')
        beam_h_mm = int(bh_raw) if bh_raw and bh_raw.isdigit() else 280
        svg = generate_front_view_svg(width=w, height=h, modules=m, max_overhang=mo, ref=ref,
                                      title=title, extra_columns=xc, col_mm=col_mm, beam_h_mm=beam_h_mm)
        return Response(svg, mimetype='image/svg+xml',
                        headers={'Cache-Control': 'no-cache, must-revalidate'})
    except Exception:
        return Response('', status=400)


@bp.route('/pergola-iso.svg', methods=['GET'])
def pergola_iso_svg():
    from flask import Response
    from ..utils import generate_isometric_svg, generate_pir_iso_svg
    try:
        w = float(request.args.get('w', 0))
        l = float(request.args.get('l', 0))
        h = float(request.args.get('h', 3.0))
        m = int(request.args.get('m', 1))
        lc = request.args.get('lc')
        lc = int(lc) if lc and lc.isdigit() else None
        deg = float(request.args.get('deg', 55))
        mo_raw = request.args.get('mo')
        mo = float(mo_raw) if mo_raw else None
        is_pir = request.args.get('pir', '0') == '1'
        if w <= 0 or l <= 0:
            return Response('', status=400)
        xc_raw = request.args.get('xc')
        xc = int(xc_raw) if xc_raw and xc_raw.isdigit() else 0
        if is_pir:
            svg = generate_pir_iso_svg(width=w, length=l, height=h, modules=m, max_overhang=mo)
        else:
            svg = generate_isometric_svg(width=w, length=l, height=h, lamella_count=lc,
                                         modules=m, lamella_open_deg=deg, max_overhang=mo,
                                         extra_columns=xc)
        return Response(svg, mimetype='image/svg+xml',
                        headers={'Cache-Control': 'no-cache, must-revalidate'})
    except Exception:
        return Response('', status=400)


@bp.route('/promotions', methods=['GET'])
def get_promotions():
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from config.promotions import get_active_promotions, get_current_season, SEASON_COLORS
        from datetime import datetime as dt
        from ..utils import get_pergola_count

        promos = get_active_promotions()
        current_season = get_current_season()
        bg_color = SEASON_COLORS.get(current_season, "#004B9A")

        install_count = get_pergola_count()

        badges = []
        for p in promos.values():
            if p.get("display_badge", True):
                badges.append({
                    "text": p.get("badge_text", p.get("name", "")),
                    "color": p.get("badge_color", bg_color)
                })

        return jsonify({
            'success': True,
            'badges': badges,
            'install_count': install_count,
            'year': dt.now().year,
            'counter_color': bg_color
        })
    except Exception as e:
        current_app.logger.error(f"Promotions error: {e}")
        return jsonify({'success': True, 'badges': [], 'install_count': 0, 'year': 2025, 'counter_color': '#004B9A'})


@bp.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Отсутствуют данные запроса'}), 400

        pergola_type = data.get('pergola_type', '')
        width = float(data.get('width', 0))
        length = float(data.get('length', 0))
        lamella_size = data.get('lamella_size', '250')
        lamella_type = data.get('lamella_type', '')
        lighting = data.get('lighting', [])
        installation = data.get('installation', False)
        selected_variant = data.get('selected_variant', '')

        if not pergola_type or width <= 0 or length <= 0:
            return jsonify({'success': False, 'error': 'Некорректные параметры'}), 400

        facade_type = data.get('facade_type', '')
        facade_sides = data.get('facade_sides', [])

        dimensions = {"width": width, "length": length}
        options = {
            "pergola_type": pergola_type,
            "lamella_type": lamella_type,
            "lamella_size": lamella_size,
            "lighting": lighting,
            "installation": installation,
            "selected_variant": selected_variant,
            "facade_type": facade_type,
            "facade_sides": facade_sides
        }

        from ..utils import generate_kp_number, get_pergola_count, get_deadline_str, generate_calc_id, save_calculation

        kp_number = generate_kp_number(pergola_type)
        pergola_count = get_pergola_count()
        deadline = get_deadline_str()
        calc_id = generate_calc_id()

        if selected_variant == 'all':
            all_results = perform_all_variants_calculation(dimensions, options)
            if not all_results:
                return jsonify({'success': False, 'error': 'Нет доступных вариантов для данных размеров'}), 400
            resp = {'success': True, 'mode': 'all', 'results': all_results, 'kp_number': kp_number, 'pergola_count': pergola_count, 'deadline': deadline, 'calc_id': calc_id}
            try:
                save_calculation(calc_id, {
                    'mode': 'all', 'results': all_results,
                    'kp_number': kp_number, 'deadline': deadline,
                    'client_name': data.get('client_name', ''),
                    'created_at': datetime.datetime.now().isoformat(),
                    'request': {'pergola_type': pergola_type, 'width': width, 'length': length,
                                'lamella_size': lamella_size, 'selected_variant': selected_variant}
                })
            except Exception as save_err:
                current_app.logger.warning(f"Failed to save calculation {calc_id}: {save_err}")
                resp['calc_id'] = ''
            return jsonify(resp)

        if selected_variant == 'auto':
            options['selected_variant'] = ''

        result = perform_calculation(dimensions, options)

        if "error" in result:
            return jsonify({'success': False, 'error': result['error']}), 400

        resp = {'success': True, 'mode': 'single', 'result': result, 'kp_number': kp_number, 'pergola_count': pergola_count, 'deadline': deadline, 'calc_id': calc_id}
        try:
            save_calculation(calc_id, {
                'mode': 'single', 'result': result,
                'kp_number': kp_number, 'deadline': deadline,
                'client_name': data.get('client_name', ''),
                'created_at': datetime.datetime.now().isoformat(),
                'request': {'pergola_type': pergola_type, 'width': width, 'length': length,
                            'lamella_size': lamella_size, 'selected_variant': selected_variant}
            })
        except Exception as save_err:
            current_app.logger.warning(f"Failed to save calculation {calc_id}: {save_err}")
            resp['calc_id'] = ''
        return jsonify(resp)

    except Exception as e:
        current_app.logger.error(f"Calculate error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@bp.route('/kp/<calc_id>', methods=['GET'])
def get_saved_kp(calc_id):
    from ..utils import load_calculation
    data = load_calculation(calc_id)
    if not data:
        return jsonify({'success': False, 'error': 'КП не найдено'}), 404
    return jsonify({'success': True, 'data': data})


@bp.route('/pergola-types', methods=['GET'])
def pergola_types():
    return jsonify({'success': True, 'types': get_pergola_types_list()})


@bp.route('/lamella-sizes/<pergola_type>', methods=['GET'])
def lamella_sizes(pergola_type):
    sizes = get_lamella_sizes_for_type(pergola_type)
    max_dims = get_max_dimensions(pergola_type, sizes[0]['id'] if sizes else '250')
    return jsonify({'success': True, 'sizes': sizes, 'max_dimensions': max_dims})


@bp.route('/decolife-data/<pergola_type>', methods=['GET'])
def decolife_data(pergola_type):
    type_map = {'B500NEW': 'b500', 'B700NEW': 'b700', 'B600': 'b600', 'B200': 'b200'}
    folder = type_map.get(pergola_type, 'b500')
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'decolife', folder, 'data.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/variant-options/<pergola_type>', methods=['GET'])
def variant_options(pergola_type):
    from config.variant_specs import get_variant_options
    options = get_variant_options(pergola_type)
    return jsonify({'success': True, 'variants': options})


@bp.route('/max-dimensions', methods=['GET'])
def max_dimensions():
    pergola_type = request.args.get('pergola_type', 'B500NEW')
    lamella_size = request.args.get('lamella_size', '250')
    dims = get_max_dimensions(pergola_type, lamella_size)
    return jsonify({'success': True, 'max_dimensions': dims})


def _build_pergola_data(result):
    from config.pergola_descriptions import (
        get_modular_system_description,
        get_drainage_system_description,
        get_pergola_images,
        get_pergola_image_caption
    )
    options = result.get('options', {})
    dimensions = result.get('dimensions', {})
    totals = result.get('totals', {})
    euro_rate = result.get('euro_rate', 110)

    rub_items = []
    for item in result.get('items', []):
        rub_items.append({
            'name': item['name'],
            'price': round(item['price'] * euro_rate)
        })

    from config.pergola_descriptions import get_pergola_description
    ptype = options.get('pergola_type', '')
    return {
        'pergola_type': ptype,
        'lamella_type': options.get('lamella_type', ''),
        'width': dimensions.get('width', 0),
        'length': dimensions.get('length', 0),
        'height': dimensions.get('height', 3.0),
        'modules': dimensions.get('modules', 1),
        'max_overhang': result.get('max_overhang'),
        'lamellas_count': result.get('lamellas_count') or result.get('lamella_count'),
        'euro_rate': 1,
        'items': rub_items,
        'specification': result.get('specification', []),
        'base_price': totals.get('cash', 0),
        'total_cost': totals.get('cash', 0),
        'cash_total': totals.get('cash', 0),
        'noncash_total': totals.get('non_cash', 0),
        'vat_total': totals.get('with_vat', 0),
        'selected_variant': result.get('selected_variant', ''),
        'variant_label': result.get('variant_label', ''),
        'lamella_size': options.get('lamella_size', ''),
        'description': get_pergola_description(ptype) or '',
        'modular_description': get_modular_system_description(),
        'drainage_description': get_drainage_system_description(),
        'image_paths': get_pergola_images(ptype),
        'image_caption': get_pergola_image_caption(ptype)
    }


@bp.route('/export-pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Отсутствуют данные'}), 400

        from pdf_generator_fpdf_rus import generate_commercial_offer
        from ..utils import generate_kp_number

        mode = data.get('mode', 'single')
        client_name = data.get('client_name', '')
        user_data = None
        if client_name:
            user_data = {'name': client_name}

        def _load_decolife(ptype):
            key = ptype.replace('NEW', '').lower()
            deco_map = {'b500': 'b500', 'b700': 'b700', 'b600': 'b600', 'b200': 'b200'}
            folder = deco_map.get(key, key)
            deco_path = os.path.join(current_app.static_folder, 'decolife', folder, 'data.json')
            try:
                with open(deco_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}

        kp_number_from_web = data.get('kp_number', '')
        deadline_from_web = data.get('deadline', '')
        calc_id_from_web = data.get('calc_id', '')

        if mode == 'all':
            results_list = data.get('results', [])
            if not results_list:
                return jsonify({'success': False, 'error': 'Нет данных для PDF'}), 400
            all_pergola_data = [_build_pergola_data(r) for r in results_list]
            pt = results_list[0].get('options', {}).get('pergola_type', 'B500')
            kp_number = kp_number_from_web or generate_kp_number(pt)
            all_pergola_data[0]['kp_number'] = kp_number
            all_pergola_data[0]['deadline'] = deadline_from_web
            all_pergola_data[0]['calc_id'] = calc_id_from_web
            decolife_data = _load_decolife(pt)
            all_pergola_data[0]['decolife'] = decolife_data
            pdf_bytes = generate_commercial_offer(all_pergola_data[0], user_data=user_data, all_variants=all_pergola_data)
            first = results_list[0]
            options = first.get('options', {})
            dimensions = first.get('dimensions', {})
        else:
            result = data.get('result', {})
            pergola_data = _build_pergola_data(result)
            pt = result.get('options', {}).get('pergola_type', 'B500')
            kp_number = kp_number_from_web or generate_kp_number(pt)
            pergola_data['kp_number'] = kp_number
            pergola_data['deadline'] = deadline_from_web
            pergola_data['calc_id'] = calc_id_from_web
            decolife_data = _load_decolife(pt)
            pergola_data['decolife'] = decolife_data
            pdf_bytes = generate_commercial_offer(pergola_data, user_data=user_data)
            options = result.get('options', {})
            dimensions = result.get('dimensions', {})

        if not pdf_bytes:
            return jsonify({'success': False, 'error': 'Ошибка генерации PDF'}), 500

        pergola_type = options.get("pergola_type", "pergola")
        width = round(float(dimensions.get("width", 0)), 1)
        length = round(float(dimensions.get("length", 0)), 1)

        try:
            import pytz
            current_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%d.%m.%Y")
        except ImportError:
            current_date = datetime.datetime.now().strftime("%d.%m.%Y")

        suffix = "_сравнение" if mode == 'all' else ""
        filename = f"КП_пергола_{pergola_type}_{width}x{length}м{suffix}_{current_date}.pdf"

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"PDF export error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Rate-limit: {ip: [timestamp, ...]}
_lead_rate = {}
_lead_rate_lock = threading.Lock()

TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN', '8658950389:AAGmL1Ii4BFzce0EpYuhQHEY0V-hCBSkGgE')
TG_CHAT_ID   = os.environ.get('TG_CHAT_ID',   '-5258227787')


def _send_telegram_lead(text):
    try:
        import urllib.request as ur
        payload = json.dumps({'chat_id': TG_CHAT_ID, 'text': text}).encode()
        req = ur.Request(
            f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        ur.urlopen(req, timeout=8)
    except Exception as e:
        pass


def _save_lead_db(phone, city, calc_text, channel, ip):
    try:
        import psycopg2
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            return
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO leads (phone, city, calc_text, channel, ip) VALUES (%s, %s, %s, %s, %s)",
            (phone, city, calc_text, channel, ip)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        pass


@bp.route('/submit-lead', methods=['POST'])
def submit_lead():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()

    # Rate-limit: 5 заявок / IP / 10 минут
    now = time.time()
    with _lead_rate_lock:
        times = [t for t in _lead_rate.get(ip, []) if now - t < 600]
        if len(times) >= 5:
            return jsonify({'success': False, 'error': 'rate_limit'}), 429
        times.append(now)
        _lead_rate[ip] = times

    data = request.get_json(silent=True) or {}
    phone     = str(data.get('phone', ''))[:30]
    city      = str(data.get('city', 'Не определён'))[:100]
    calc_text = str(data.get('calc_text', ''))[:4000]
    channel   = str(data.get('channel', 'callback'))[:20]

    channel_label = {'telegram': 'Telegram', 'max': 'Max', 'callback': '📞 Звонок'}.get(channel, channel)
    tg_text = (
        f"🏗 Заявка — Биоклиматическая пергола\n"
        f"Канал: {channel_label}\n"
        f"Телефон: {phone}\n"
        f"Город: {city}\n\n"
        f"{calc_text}"
    )

    threading.Thread(target=_send_telegram_lead, args=(tg_text,), daemon=True).start()
    threading.Thread(target=_save_lead_db, args=(phone, city, calc_text, channel, ip), daemon=True).start()

    return jsonify({'success': True})
