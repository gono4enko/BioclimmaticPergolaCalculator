"""
Инициализация Flask-приложения и его зависимостей.
"""
import os
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_compress import Compress

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()

_DEV_KEY_CACHE = None

def _stable_dev_key():
    global _DEV_KEY_CACHE
    if _DEV_KEY_CACHE is None:
        import logging
        logging.getLogger(__name__).warning("SECRET_KEY not set — using deterministic dev key. Set SECRET_KEY env var for production!")
        seed = os.environ.get('REPL_ID', '') + os.environ.get('REPL_SLUG', '') + 'pergola-dev-key'
        _DEV_KEY_CACHE = hashlib.sha256(seed.encode()).hexdigest()
    return _DEV_KEY_CACHE

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
        SECRET_KEY=os.environ.get('SECRET_KEY') or _stable_dev_key(),
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
        
    for folder in ['generated_pdf', 'uploads', 'static/images']:
        os.makedirs(os.path.join(app.root_path, folder), exist_ok=True)

    _deco_missing = False
    for deco_folder in ['b500', 'b700', 'b600']:
        deco_dir = os.path.join(app.root_path, 'static', 'decolife', deco_folder)
        deco_file = os.path.join(deco_dir, 'data.json')
        if not os.path.exists(deco_file):
            _deco_missing = True
            break
    if _deco_missing:
        try:
            import sys
            proj_root = os.path.dirname(app.root_path)
            if proj_root not in sys.path:
                sys.path.insert(0, proj_root)
            from scripts.fetch_decolife import ensure_data_files, fetch_and_parse
            ensure_data_files()
            import threading
            _deco_dir = os.path.join(app.root_path, 'static', 'decolife')
            def _bg_fetch():
                try:
                    results = fetch_and_parse()
                    if results:
                        import json as _json
                        for key, data in results.items():
                            dp = os.path.join(_deco_dir, key, 'data.json')
                            os.makedirs(os.path.dirname(dp), exist_ok=True)
                            with open(dp, 'w', encoding='utf-8') as f:
                                _json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"[decolife] Updated {len(results)} model(s)")
                except Exception as e:
                    print(f"[decolife] Background fetch failed: {e}")
            threading.Thread(target=_bg_fetch, daemon=True).start()
        except Exception:
            pass
    
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