"""
Основной модуль запуска Flask-приложения калькулятора перголы.
"""
from flask_app import create_app

# Создаем экземпляр приложения
app = create_app()

if __name__ == '__main__':
    # Запускаем приложение в режиме разработки
    app.run(host='0.0.0.0', port=5000, debug=True)