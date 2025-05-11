"""
Основные маршруты веб-приложения.
"""
import os
from flask import Blueprint, render_template, current_app, redirect, url_for, request, jsonify
from ..models.pergola_model import Pergola, db
from ..services.cache_service import preload_images, clear_image_cache

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Главная страница приложения."""
    return render_template('index.html', preload_images=preload_images())

@bp.route('/calculator')
def calculator():
    """Страница калькулятора перголы."""
    return render_template('calculator.html', preload_images=preload_images())

@bp.route('/catalog')
def catalog():
    """Страница каталога пергол."""
    return render_template('catalog.html')

@bp.route('/pergolas/<int:pergola_id>')
def pergola_details(pergola_id):
    """Страница с деталями конкретной перголы."""
    pergola = Pergola.query.get_or_404(pergola_id)
    return render_template('pergola_details.html', pergola=pergola)

@bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Очистка кэша изображений."""
    try:
        clear_image_cache()
        return jsonify({'success': True, 'message': 'Кэш успешно очищен'})
    except Exception as e:
        current_app.logger.error(f"Ошибка при очистке кэша: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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