"""
API маршруты для взаимодействия с клиентским JavaScript.
"""
import os
import json
import datetime
from io import BytesIO
from flask import Blueprint, jsonify, request, current_app, send_file, url_for
from werkzeug.exceptions import BadRequest, NotFound
from ..models.pergola_model import Pergola, db
from ..services.calculator import (calculate_pergola_price, 
                                  get_modules_by_dimensions, 
                                  adjust_length_for_lamella_size)
from ..services.pdf_generator import generate_pdf

bp = Blueprint('api', __name__)

@bp.route('/calculate', methods=['POST'])
def calculate():
    """API для расчета стоимости перголы."""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Missing request data")
        
        # Получение параметров из запроса
        pergola_type = data.get('pergola_type')
        width = float(data.get('width', 0))
        length = float(data.get('length', 0))
        lamella_size = data.get('lamella_size')
        options = data.get('options', {})
        
        # Проверка наличия необходимых параметров
        if not pergola_type or width <= 0 or length <= 0 or not lamella_size:
            raise BadRequest("Invalid parameters for calculation")
        
        # Корректировка длины в зависимости от размера ламелей
        adjusted_length = adjust_length_for_lamella_size(length, lamella_size)
        
        # Определение количества модулей
        modules = get_modules_by_dimensions(width, adjusted_length, pergola_type)
        
        # Выполнение расчета
        result = calculate_pergola_price(
            pergola_type=pergola_type,
            width=width,
            length=adjusted_length,
            modules=modules,
            lamella_size=lamella_size,
            options=options
        )
        
        # Формирование ответа
        response = {
            'success': True,
            'result': result,
            'adjusted_length': adjusted_length,
            'modules': modules
        }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error in calculate API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/save', methods=['POST'])
def save_calculation():
    """API для сохранения результатов расчета."""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Missing request data")
        
        # Создание новой записи для перголы
        new_pergola = Pergola()
        new_pergola.type = data.get('pergola_type')
        new_pergola.width = float(data.get('width'))
        new_pergola.length = float(data.get('length'))
        new_pergola.modules = int(data.get('modules'))
        new_pergola.lamella_size = data.get('lamella_size')
        new_pergola.options = data.get('options', {})
        new_pergola.total_price = float(data.get('total_price'))
        new_pergola.discount = float(data.get('discount', 0))
        new_pergola.total_price_after_discount = float(data.get('total_price_after_discount', 0))
        
        # Сохранение в базу данных
        db.session.add(new_pergola)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pergola_id': new_pergola.id,
            'message': 'Расчет успешно сохранен'
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in save calculation API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/export-pdf', methods=['POST'])
def export_pdf():
    """API для экспорта результатов в PDF. Возвращает PDF-файл напрямую."""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Missing request data")
        
        pdf_bytes = generate_pdf(data)
        
        if not pdf_bytes:
            raise Exception("Failed to generate PDF")
        
        filename = data.get('filename', 'КП_пергола.pdf')
        
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        current_app.logger.error(f"Error in export PDF API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400