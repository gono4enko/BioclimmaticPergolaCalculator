"""
Основные маршруты веб-приложения.
"""
import os
import datetime
from flask import Blueprint, render_template, current_app, redirect, url_for, request, jsonify
from ..models.pergola_model import Pergola, db
from ..services.cache_service import preload_images, clear_image_cache
from ..services.calculator import get_zip_colors_for_js

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return redirect(url_for('main.calculator'))

@bp.route('/calculator')
def calculator():
    current_year = datetime.datetime.now().year
    return render_template('calculator.html', now={'year': current_year},
                           zip_colors=get_zip_colors_for_js())

@bp.route('/kp/<calc_id>')
def view_kp(calc_id):
    current_year = datetime.datetime.now().year
    return render_template('calculator.html', now={'year': current_year}, calc_id=calc_id,
                           zip_colors=get_zip_colors_for_js())

@bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Очистка кэша изображений."""
    try:
        clear_image_cache()
        return jsonify({'success': True, 'message': 'Кэш успешно очищен'})
    except Exception as e:
        current_app.logger.error(f"Ошибка при очистке кэша: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/ping')
@bp.route('/health')
def health_check():
    """Проверка работоспособности приложения."""
    try:
        # Проверка соединения с базой данных
        from sqlalchemy import text
        db.session.execute(text('SELECT 1')).scalar()
        
        # Проверка доступа к папкам
        folders_to_check = [
            current_app.config['PDF_FOLDER'],
            current_app.config['UPLOAD_FOLDER']
        ]
        
        for folder in folders_to_check:
            if not os.path.exists(folder):
                return jsonify({
                    'status': 'error',
                    'message': f'Папка не существует: {folder}'
                }), 500
        
        return jsonify({'status': 'ok', 'message': 'Приложение работает нормально'})
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при проверке работоспособности: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Ошибка: {str(e)}'
        }), 500