"""
Основной модуль Flask-приложения калькулятора перголы.
Содержит фабрику приложения и инициализацию расширений.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """
    Фабричная функция для создания экземпляра Flask приложения.
    
    Args:
        test_config (dict, optional): Конфигурация для тестирования
        
    Returns:
        Flask: Экземпляр Flask приложения
    """
    # Создание и настройка приложения
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Загрузка конфигурации
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///pergola.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            UPLOAD_FOLDER=os.path.join(app.root_path, 'uploads'),
            PDF_FOLDER=os.path.join(app.root_path, 'generated_pdf'),
            JSON_AS_ASCII=False  # Для корректной работы с кириллицей
        )
    else:
        app.config.from_mapping(test_config)
    
    # Создание необходимых папок
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .models import pergola_model  # Импорт моделей

    # Регистрация маршрутов
    from .controllers import main_routes, api_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(api_routes.bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        """Простая проверка работоспособности сервера"""
        return {'status': 'healthy'}
    
    return app