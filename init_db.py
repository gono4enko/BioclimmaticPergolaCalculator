"""
Скрипт для инициализации базы данных.

Использование: python init_db.py
"""
import os
import sys
from flask import Flask
from flask_app import db
from flask_app.models.pergola_model import Pergola, PriceData, CalculationHistory

# Создание минимального приложения Flask для контекста
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pergola.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_db():
    """Инициализирует базу данных, создавая все таблицы."""
    with app.app_context():
        print("Создание таблиц базы данных...")
        db.create_all()
        print("База данных успешно инициализирована!")

def drop_db():
    """Удаляет все таблицы из базы данных."""
    with app.app_context():
        print("ВНИМАНИЕ: Будут удалены все таблицы из базы данных!")
        confirm = input("Вы уверены? [y/N]: ")
        if confirm.lower() == 'y':
            print("Удаление таблиц...")
            db.drop_all()
            print("Все таблицы удалены.")
        else:
            print("Операция отменена.")

def reset_db():
    """Сбрасывает базу данных (удаляет и создает заново)."""
    with app.app_context():
        print("ВНИМАНИЕ: База данных будет сброшена (удалена и создана заново)!")
        confirm = input("Вы уверены? [y/N]: ")
        if confirm.lower() == 'y':
            print("Удаление таблиц...")
            db.drop_all()
            print("Создание таблиц...")
            db.create_all()
            print("База данных успешно сброшена!")
        else:
            print("Операция отменена.")

if __name__ == '__main__':
    # Если передан аргумент 'drop', удаляем таблицы
    if len(sys.argv) > 1 and sys.argv[1] == 'drop':
        drop_db()
    # Если передан аргумент 'reset', сбрасываем базу данных
    elif len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_db()
    # Иначе инициализируем базу данных
    else:
        init_db()