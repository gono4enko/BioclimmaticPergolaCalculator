"""
API маршруты для калькулятора пергол.
"""
import os
import json
import datetime
from io import BytesIO
from flask import Blueprint, jsonify, request, current_app, send_file
from ..services.calculator import (
    perform_calculation,
    get_pergola_types_list,
    get_lamella_sizes_for_type,
    get_max_dimensions,
    adjust_length_for_lamella_size,
    get_modules_by_dimensions
)

bp = Blueprint('api', __name__)


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

        if not pergola_type or width <= 0 or length <= 0:
            return jsonify({'success': False, 'error': 'Некорректные параметры'}), 400

        dimensions = {"width": width, "length": length}
        options = {
            "pergola_type": pergola_type,
            "lamella_type": lamella_type,
            "lamella_size": lamella_size,
            "lighting": lighting,
            "installation": installation
        }

        result = perform_calculation(dimensions, options)

        if "error" in result:
            return jsonify({'success': False, 'error': result['error']}), 400

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        current_app.logger.error(f"Calculate error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@bp.route('/pergola-types', methods=['GET'])
def pergola_types():
    return jsonify({'success': True, 'types': get_pergola_types_list()})


@bp.route('/lamella-sizes/<pergola_type>', methods=['GET'])
def lamella_sizes(pergola_type):
    sizes = get_lamella_sizes_for_type(pergola_type)
    max_dims = get_max_dimensions(pergola_type, sizes[0]['id'] if sizes else '250')
    return jsonify({'success': True, 'sizes': sizes, 'max_dimensions': max_dims})


@bp.route('/max-dimensions', methods=['GET'])
def max_dimensions():
    pergola_type = request.args.get('pergola_type', 'B500NEW')
    lamella_size = request.args.get('lamella_size', '250')
    dims = get_max_dimensions(pergola_type, lamella_size)
    return jsonify({'success': True, 'max_dimensions': dims})


@bp.route('/export-pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Отсутствуют данные'}), 400

        from pdf_generator_fpdf_rus import generate_commercial_offer
        from config.pergola_descriptions import (
            get_modular_system_description,
            get_drainage_system_description,
            get_pergola_images,
            get_pergola_image_caption
        )

        result = data.get('result', {})
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

        pergola_data = {
            'pergola_type': options.get('pergola_type', ''),
            'lamella_type': options.get('lamella_type', ''),
            'width': dimensions.get('width', 0),
            'length': dimensions.get('length', 0),
            'modules': dimensions.get('modules', 1),
            'euro_rate': 1,
            'items': rub_items,
            'specification': result.get('specification', []),
            'base_price': totals.get('cash', 0),
            'total_cost': totals.get('cash', 0),
            'cash_total': totals.get('cash', 0),
            'noncash_total': totals.get('non_cash', 0),
            'vat_total': totals.get('with_vat', 0),
            'description': '',
            'modular_description': get_modular_system_description(),
            'drainage_description': get_drainage_system_description(),
            'image_paths': get_pergola_images(options.get('pergola_type', '')),
            'image_caption': get_pergola_image_caption(options.get('pergola_type', ''))
        }

        pdf_bytes = generate_commercial_offer(pergola_data)

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

        filename = f"КП_пергола_{pergola_type}_{width}x{length}м_{current_date}.pdf"

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"PDF export error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
