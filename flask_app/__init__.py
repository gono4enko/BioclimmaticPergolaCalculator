"""
Инициализация Flask-приложения и его зависимостей.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_compress import Compress

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """
    Создает и настраивает экземпляр Flask-приложения.
    
    Args:
        test_config: Конфигурация для тестирования (если нужна)
        
    Returns:
        Flask: Настроенное Flask-приложение
    """
    # Создаем экземпляр приложения
    app = Flask(__name__, instance_relative_config=True)
    
    # Настройка приложения
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///pergola.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,
        PDF_FOLDER=os.path.join(app.root_path, 'generated_pdf'),
        UPLOAD_FOLDER=os.path.join(app.root_path, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB лимит загрузки
        ALLOWED_SCRAPING_DOMAINS=[
            'pergolamarket.ru', 'pergolas.ru', 'decolife.ru', 'forumhouse.ru', 
            'stroyka.ru', 'wikipedia.org', 'dizainland.ru', 'houzz.ru', 
            'inmyroom.ru', 'ivd.ru', 'elitepergola.ru'
        ]
    )
    
    # Если передан тестовый конфиг, используем его
    if test_config is not None:
        app.config.from_mapping(test_config)
        
    # Создаем необходимые директории
    for folder in ['generated_pdf', 'uploads', 'static/images']:
        os.makedirs(os.path.join(app.root_path, folder), exist_ok=True)
    
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html', 'text/css', 'text/javascript',
        'application/javascript', 'application/json', 'image/svg+xml'
    ]
    app.config['COMPRESS_MIN_SIZE'] = 500

    Compress(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация Blueprints
    from .controllers.main_routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .controllers.api_routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from .controllers.admin_routes import bp as admin_bp
    app.register_blueprint(admin_bp)

    # Регистрация блюпринта для скрапера
    from .controllers.scraper_controller import register_scraper_blueprints
    register_scraper_blueprints(app)
    
    # Регистрация блюпринта для работы с PDF
    from .controllers.pdf_controller import register_pdf_blueprints
    register_pdf_blueprints(app)
    
    @app.after_request
    def set_iframe_headers(response):
        response.headers.pop('X-Frame-Options', None)
        response.headers['Content-Security-Policy'] = response.headers.get('Content-Security-Policy', '').replace('frame-ancestors', '') or "frame-ancestors *"
        return response

    @app.errorhandler(404)
    def page_not_found(error):
        return {'error': 'Страница не найдена'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return {'error': 'Внутренняя ошибка сервера'}, 500
    
    # Возвращаем приложение
    return app