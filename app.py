"""
Основной файл для запуска Flask-приложения калькулятора перголы.

Для разработки:
    $ export FLASK_APP=app.py
    $ export FLASK_ENV=development
    $ flask run

Для продакшена (с Gunicorn):
    $ gunicorn -w 4 'app:app' --bind 0.0.0.0:5000
"""
import os
import logging
from flask import current_app
from flask_app import create_app, db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)

# Создание директории для логов
os.makedirs('logs', exist_ok=True)

# Создание экземпляра приложения
app = create_app()

@app.cli.command('init-db')
def init_db_command():
    """Инициализация базы данных."""
    with app.app_context():
        db.create_all()
        current_app.logger.info('База данных инициализирована.')

@app.cli.command('import-prices')
def import_prices():
    """Импорт цен из CSV-файлов в базу данных."""
    with app.app_context():
        from flask_app.models.pergola_model import PriceData
        import csv
        import os
        
        # Папка с CSV-файлами цен
        prices_dir = os.path.join('data', 'prices')
        if not os.path.exists(prices_dir):
            os.makedirs(prices_dir, exist_ok=True)
            current_app.logger.warning(f'Создана пустая директория для цен: {prices_dir}')
            return
        
        # Поиск CSV-файлов
        count = 0
        for filename in os.listdir(prices_dir):
            if not filename.endswith('.csv'):
                continue
                
            # Парсинг имени файла для получения типа перголы и размера ламели
            parts = filename.split('_')
            if len(parts) < 2:
                current_app.logger.warning(f'Некорректное имя файла: {filename}')
                continue
                
            pergola_type = parts[0]
            lamella_size = parts[1].split('.')[0]
            
            # Путь к файлу
            file_path = os.path.join(prices_dir, filename)
            
            # Чтение и импорт данных
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        width = float(row['width'])
                        length = float(row['length'])
                        price = float(row['price'])
                        modules = int(row.get('modules', 1))
                        
                        # Проверка, существует ли уже такая запись
                        existing = PriceData.query.filter_by(
                            pergola_type=pergola_type,
                            lamella_size=lamella_size,
                            width=width,
                            length=length
                        ).first()
                        
                        if existing:
                            # Обновление существующей записи
                            existing.price = price
                            existing.modules = modules
                        else:
                            # Создание новой записи
                            price_data = PriceData()
                            price_data.pergola_type = pergola_type
                            price_data.lamella_size = lamella_size
                            price_data.width = width
                            price_data.length = length
                            price_data.price = price
                            price_data.modules = modules
                            db.session.add(price_data)
                            
                        count += 1
                    except Exception as e:
                        current_app.logger.error(f'Ошибка при импорте строки из {filename}: {str(e)}')
        
        # Сохранение изменений
        db.session.commit()
        current_app.logger.info(f'Импортировано {count} записей с ценами.')

if __name__ == '__main__':
    # Запуск приложения в режиме отладки
    app.run(host='0.0.0.0', port=5000, debug=True)