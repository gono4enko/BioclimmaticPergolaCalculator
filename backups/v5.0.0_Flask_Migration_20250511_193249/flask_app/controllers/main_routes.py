"""
Основные маршруты приложения.
"""
from flask import Blueprint, render_template, current_app, redirect, url_for, request, flash
from ..services.calculator import get_pergola_types, get_lamella_sizes, load_price_data
from ..services.cache_service import get_cached_images

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Главная страница с калькулятором."""
    pergola_types = get_pergola_types()
    lamella_sizes = get_lamella_sizes()
    
    # Предзагрузка изображений для быстрой работы UI
    cached_images = get_cached_images()
    
    return render_template('index.html', 
                           pergola_types=pergola_types,
                           lamella_sizes=lamella_sizes,
                           cached_images=cached_images)

@bp.route('/about')
def about():
    """Страница о перголах."""
    return render_template('about.html')

@bp.route('/gallery')
def gallery():
    """Галерея установленных пергол."""
    return render_template('gallery.html')

@bp.route('/contacts')
def contacts():
    """Контактная информация."""
    return render_template('contacts.html')

@bp.route('/iframe')
def iframe():
    """Версия калькулятора для встраивания в iframe."""
    pergola_types = get_pergola_types()
    lamella_sizes = get_lamella_sizes()
    
    return render_template('iframe.html', 
                           pergola_types=pergola_types,
                           lamella_sizes=lamella_sizes,
                           iframe_mode=True)

@bp.errorhandler(404)
def page_not_found(e):
    """Обработчик ошибки 404."""
    return render_template('errors/404.html'), 404

@bp.errorhandler(500)
def server_error(e):
    """Обработчик ошибки 500."""
    current_app.logger.error(f'Server error: {e}')
    return render_template('errors/500.html'), 500