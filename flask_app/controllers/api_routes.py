"""
API маршруты для взаимодействия с клиентским JavaScript.
"""
import os
import json
import datetime
from flask import Blueprint, jsonify, request, current_app, send_file, url_for
from werkzeug.exceptions import BadRequest, NotFound
from ..models.pergola_model import Pergola, db
from ..services.calculator import (CalculationFactory, 
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
        
        # Собираем опции из запроса
        options = {}
        for key in ['led_lighting', 'rain_sensor', 'wind_sensor']:
            options[key] = data.get(key, False)
        
        # Добавляем скидку, если указана
        discount = float(data.get('discount', 0))
        if discount > 0:
            options['discount'] = discount
        
        # Проверка наличия необходимых параметров
        if not pergola_type or width <= 0 or length <= 0 or not lamella_size:
            raise BadRequest("Invalid parameters for calculation")
        
        # Корректировка длины в зависимости от размера ламелей
        adjusted_length = adjust_length_for_lamella_size(length, lamella_size)
        
        # Определение количества модулей
        modules = get_modules_by_dimensions(width, adjusted_length, pergola_type)
        
        # Выполнение расчета с использованием фабрики и стратегии
        calculator = CalculationFactory.get_strategy(pergola_type)
        result = calculator.calculate(
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
            'results': result,
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

@bp.route('/export-pdf', methods=['GET', 'POST'])
def export_pdf():
    """API для экспорта результатов в PDF."""
    try:
        # Получаем данные из POST-запроса или из сессии
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                raise BadRequest("Missing request data")
        else:
            # При GET-запросе используем данные из последнего расчета
            # В реальном приложении здесь можно использовать сессию или ID расчета
            data = {
                'pergola_type': 'B500NEW',
                'width': 4.0,
                'length': 4.0,
                'lamella_size': '250',
                'modules': 1,
                'items': [
                    {'name': 'Пергола B500NEW, ламели 250 мм', 'quantity': '4.0x4.0 м (1 модуль)', 'price': 150000},
                    {'name': 'Привод Somfy WT 40 Нм', 'quantity': 1, 'price': 35000},
                    {'name': 'Пульт управления Somfy Smoove Origin RTS', 'quantity': 1, 'price': 8000}
                ],
                'total_price': 193000,
                'discount': 0,
                'total_price_after_discount': 193000
            }
        
        # Генерация PDF
        pdf_path = generate_pdf(data)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise Exception("Failed to generate PDF")
        
        # Формирование имени файла для скачивания
        filename = os.path.basename(pdf_path)
        
        # Если это GET-запрос, сразу отправляем файл
        if request.method == 'GET':
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"KP_Pergola_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        
        # Если это POST-запрос, возвращаем URL для скачивания
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