"""
Инициализация Flask-приложения и его зависимостей.
"""
import os

# Загрузка переменных окружения из .env файла (для production VPS-сервера).
# В Replit переменные приходят через встроенные Secrets — load_dotenv() ничего
# не сделает (если .env нет — просто молча пропустит). По умолчанию реальные env-vars
# имеют приоритет над .env (override=False), так что Replit Secrets не перезатираются.
# ВАЖНО: load_dotenv() должен вызываться ДО любых импортов модулей, читающих os.environ
# на module-level (например, flask_app/controllers/api_routes.py читает GMAIL_USER и др.
# при импорте — он импортируется внутри create_app(), так что вызов здесь срабатывает вовремя).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv не установлен. На Replit это нормально (Secrets подгружаются платформой),
    # но на VPS без dotenv .env файл загружен НЕ БУДЕТ — выводим предупреждение, чтобы
    # ops-инженер сразу заметил проблему. На Replit (REPL_ID задан) предупреждение скрываем.
    if not os.environ.get('REPL_ID'):
        import sys
        print(
            "[startup] WARNING: python-dotenv не установлен. Если на этом сервере используется "
            ".env файл — переменные из него НЕ будут загружены. Установите: pip install python-dotenv",
            file=sys.stderr, flush=True
        )

# Диагностическое логирование переменных окружения при каждом старте.
# Позволяет сразу увидеть в логах gunicorn какие переменные найдены, а каких нет.
print("=" * 50, flush=True)
print("[ENV] Проверка переменных окружения:", flush=True)
print("=" * 50, flush=True)
for _var in ['GMAIL_USER', 'GMAIL_PASSWORD', 'RECIPIENT_EMAIL',
             'SECRET_KEY', 'ADMIN_PASSWORD', 'DATABASE_URL']:
    _val = os.environ.get(_var)
    if _val:
        if 'PASSWORD' in _var or 'KEY' in _var or 'URL' in _var:
            print(f"  [OK] {_var}: ***скрыт***", flush=True)
        else:
            print(f"  [OK] {_var}: {_val}", flush=True)
    else:
        print(f"  [!!] {_var}: НЕ НАЙДЕН", flush=True)
print("=" * 50, flush=True)

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

def _start_cleanup_scheduler(app, cleanup_fn):
    import logging
    _logger = logging.getLogger(__name__)

    if app.config.get('TESTING'):
        return

    try:
        hours = max(1, int(os.environ.get('CLEANUP_INTERVAL_HOURS', 24)))
    except (ValueError, TypeError):
        hours = 24

    watchdog_minutes = max(10, (hours * 60) // 4)

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        import threading as _threading
        import time as _time
        scheduler = BackgroundScheduler(daemon=True)

        alert_state = {'last_sent': 0.0, 'last_status': None, 'was_unhealthy': False}

        def _run_cleanup():
            with app.app_context():
                cleanup_fn(trigger='scheduled')

        def _watchdog_check():
            from flask_app.utils import (
                check_scheduler_health, send_telegram_alert, get_scheduler_settings,
            )
            health = check_scheduler_health()
            alert_cooldown_seconds = get_scheduler_settings()['alert_cooldown_seconds']
            if not health['healthy']:
                _logger.warning(
                    "SCHEDULER ALERT: %s (status=%s)",
                    health['message'], health['status']
                )

                now_ts = _time.time()
                status_changed = alert_state['last_status'] != health['status']
                cooldown_elapsed = (
                    now_ts - alert_state['last_sent']
                ) >= alert_cooldown_seconds
                if status_changed or cooldown_elapsed:
                    alert_text = (
                        "⚠️ Pergola: cleanup scheduler stalled\n"
                        f"Status: {health['status']}\n"
                        f"Details: {health['message']}\n"
                        f"Last run: {health.get('last_run') or 'never'}"
                    )
                    _threading.Thread(
                        target=send_telegram_alert,
                        args=(alert_text,),
                        daemon=True,
                    ).start()
                    alert_state['last_sent'] = now_ts
                    alert_state['last_status'] = health['status']
                alert_state['was_unhealthy'] = True

                job = scheduler.get_job('cleanup_old_calculations')
                if job is None or not scheduler.running:
                    _logger.error(
                        "SCHEDULER ALERT: Cleanup job missing or scheduler stopped. "
                        "Attempting recovery..."
                    )
                    try:
                        if not scheduler.running:
                            scheduler.start()
                        if scheduler.get_job('cleanup_old_calculations') is None:
                            scheduler.add_job(
                                _run_cleanup, 'interval', hours=hours,
                                id='cleanup_old_calculations'
                            )
                        _logger.info("Scheduler recovery attempted successfully")
                    except Exception as recover_exc:
                        _logger.error("Scheduler recovery failed: %s", recover_exc)
            else:
                if alert_state['was_unhealthy']:
                    recovery_text = (
                        "✅ Pergola: cleanup scheduler recovered\n"
                        f"Status: {health['status']}\n"
                        f"Details: {health['message']}"
                    )
                    _threading.Thread(
                        target=send_telegram_alert,
                        args=(recovery_text,),
                        daemon=True,
                    ).start()
                alert_state['was_unhealthy'] = False
                alert_state['last_status'] = health['status']

        scheduler.add_job(_run_cleanup, 'interval', hours=hours, id='cleanup_old_calculations')
        scheduler.add_job(
            _watchdog_check, 'interval', minutes=watchdog_minutes,
            id='cleanup_watchdog'
        )
        scheduler.start()
        app.extensions['cleanup_scheduler'] = scheduler
        _logger.info(
            "Cleanup scheduler started (every %d hour(s), watchdog every %d min)",
            hours, watchdog_minutes
        )
    except Exception as exc:
        _logger.warning("Failed to start cleanup scheduler: %s", exc)


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
    
    from .utils import cleanup_old_calculations
    cleanup_old_calculations(trigger='startup')

    _start_cleanup_scheduler(app, cleanup_old_calculations)

    @app.after_request
    def set_iframe_headers(response):
        from flask import request as _req
        # /api/health-probe сам управляет своими заголовками (CORS, Cache-Control,
        # Content-Length, X-Probe-Size). Не трогаем его, чтобы не было дублирующих
        # или лишних заголовков, которые могут сбить DPI-мониторинг по точному размеру.
        if _req.path == '/api/health-probe':
            return response
        response.headers.pop('X-Frame-Options', None)
        csp = response.headers.get('Content-Security-Policy', '').replace('frame-ancestors', '') or "frame-ancestors *"
        if 'frame-src' not in csp:
            csp += "; frame-src 'self' https://rutube.ru https://*.rutube.ru"
        response.headers['Content-Security-Policy'] = csp
        if _req.path.startswith('/static/') and (_req.path.endswith('.js') or _req.path.endswith('.css')):
            response.headers['Cache-Control'] = 'no-cache, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
        return response

    @app.errorhandler(404)
    def page_not_found(error):
        return {'error': 'Страница не найдена'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return {'error': 'Внутренняя ошибка сервера'}, 500
    
    # Возвращаем приложение
    return app