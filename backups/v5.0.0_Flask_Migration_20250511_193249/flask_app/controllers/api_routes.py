"""
API маршруты для взаимодействия с клиентским JavaScript.
"""
import os
import json
import datetime
from flask import Blueprint, jsonify, request, current_app, send_file
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
        new_pergola = Pergola(
            type=data.get('pergola_type'),
            width=float(data.get('width')),
            length=float(data.get('length')),
            modules=int(data.get('modules')),
            lamella_size=data.get('lamella_size'),
            options=data.get('options', {}),
            total_price=float(data.get('total_price')),
            discount=float(data.get('discount', 0)),
            total_price_after_discount=float(data.get('total_price_after_discount', 0))
        )
        
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
    """API для экспорта результатов в PDF."""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Missing request data")
        
        # Генерация PDF
        pdf_path = generate_pdf(data)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise Exception("Failed to generate PDF")
        
        # Сохранение пути к PDF в базу данных, если есть ID перголы
        pergola_id = data.get('pergola_id')
        if pergola_id:
            pergola = Pergola.query.get(pergola_id)
            if pergola:
                pergola.pdf_path = pdf_path
                db.session.commit()
        
        # Формирование имени файла для скачивания
        filename = os.path.basename(pdf_path)
        
        return jsonify({
            'success': True,
            'pdf_url': url_for('api.download_pdf', filename=filename),
            'filename': filename
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in export PDF API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/download-pdf/<filename>')
def download_pdf(filename):
    """API для скачивания сгенерированного PDF."""
    try:
        pdf_path = os.path.join(current_app.config['PDF_FOLDER'], filename)
        
        if not os.path.exists(pdf_path):
            raise NotFound("PDF файл не найден")
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        current_app.logger.error(f"Error in download PDF API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404