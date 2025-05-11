"""
Контроллер для работы с PDF-файлами - парсинг, анализ и управление.
"""

import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app, send_from_directory
from werkzeug.utils import secure_filename

from ..services.pdf_parser import parse_pdf

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание блюпринта
pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdf')
api_pdf_bp = Blueprint('api_pdf', __name__, url_prefix='/api/pdf')

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """
    Проверяет, разрешено ли загружать файл с данным расширением.
    
    Args:
        filename (str): Имя файла
        
    Returns:
        bool: True, если расширение файла разрешено
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@pdf_bp.route('/', methods=['GET'])
def pdf_manager():
    """Отображает страницу управления PDF-файлами."""
    # Получаем список всех PDF-файлов в директории
    pdf_folder = current_app.config['PDF_FOLDER']
    all_pdfs = []
    
    if os.path.exists(pdf_folder):
        for filename in os.listdir(pdf_folder):
            if filename.endswith('.pdf'):
                file_path = os.path.join(pdf_folder, filename)
                file_info = {
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d.%m.%Y %H:%M')
                }
                all_pdfs.append(file_info)
    
    # Сортируем по дате изменения (новые в начале)
    all_pdfs.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('pdf_manager.html', pdfs=all_pdfs)


@pdf_bp.route('/view/<filename>', methods=['GET'])
def view_pdf(filename):
    """
    Отображает PDF-файл в браузере.
    
    Args:
        filename (str): Имя файла
    """
    pdf_folder = current_app.config['PDF_FOLDER']
    return send_from_directory(pdf_folder, filename)


@api_pdf_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """API-метод для загрузки PDF-файла."""
    try:
        # Проверяем, что файл был отправлен
        if 'file' not in request.files:
            return jsonify({'error': 'Не найден файл в запросе'}), 400
        
        file = request.files['file']
        
        # Проверяем, что имя файла не пустое
        if file.filename == '':
            return jsonify({'error': 'Не выбран файл'}), 400
        
        # Проверяем, что есть имя файла
        if not file.filename:
            return jsonify({'error': 'Файл не имеет имени'}), 400
            
        # Проверяем расширение файла
        if not allowed_file(file.filename):
            return jsonify({'error': 'Недопустимый тип файла. Разрешены только PDF-файлы'}), 400
        
        # Сохраняем файл
        filename = secure_filename(file.filename)
        pdf_folder = current_app.config['PDF_FOLDER']
        
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder, exist_ok=True)
        
        file_path = os.path.join(pdf_folder, filename)
        file.save(file_path)
        
        logger.info(f"Файл {filename} успешно загружен в {pdf_folder}")
        
        # Возвращаем успешный ответ
        return jsonify({
            'success': True,
            'message': 'Файл успешно загружен',
            'filename': filename,
            'path': file_path
        })
    
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {str(e)}")
        return jsonify({'error': f'Ошибка при загрузке файла: {str(e)}'}), 500


@api_pdf_bp.route('/parse/<filename>', methods=['GET'])
def parse_pdf_file(filename):
    """
    API-метод для парсинга PDF-файла.
    
    Args:
        filename (str): Имя файла
    """
    try:
        pdf_folder = current_app.config['PDF_FOLDER']
        file_path = os.path.join(pdf_folder, filename)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Парсим PDF-файл
        result = parse_pdf(file_path)
        
        # Логируем результат
        logger.info(f"Файл {filename} успешно проанализирован")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Ошибка при парсинге файла {filename}: {str(e)}")
        return jsonify({'error': f'Ошибка при анализе файла: {str(e)}'}), 500


@api_pdf_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_pdf(filename):
    """
    API-метод для удаления PDF-файла.
    
    Args:
        filename (str): Имя файла
    """
    try:
        pdf_folder = current_app.config['PDF_FOLDER']
        file_path = os.path.join(pdf_folder, filename)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Удаляем файл
        os.remove(file_path)
        
        logger.info(f"Файл {filename} успешно удален")
        
        return jsonify({
            'success': True,
            'message': f'Файл {filename} успешно удален'
        })
    
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {filename}: {str(e)}")
        return jsonify({'error': f'Ошибка при удалении файла: {str(e)}'}), 500


@api_pdf_bp.route('/list', methods=['GET'])
def list_pdfs():
    """API-метод для получения списка PDF-файлов."""
    try:
        pdf_folder = current_app.config['PDF_FOLDER']
        all_pdfs = []
        
        if os.path.exists(pdf_folder):
            for filename in os.listdir(pdf_folder):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(pdf_folder, filename)
                    file_info = {
                        'name': filename,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d.%m.%Y %H:%M')
                    }
                    all_pdfs.append(file_info)
        
        # Сортируем по дате изменения (новые в начале)
        all_pdfs.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify(all_pdfs)
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка файлов: {str(e)}")
        return jsonify({'error': f'Ошибка при получении списка файлов: {str(e)}'}), 500


# Функция для регистрации блюпринтов
def register_pdf_blueprints(app):
    """
    Регистрирует блюпринты для работы с PDF.
    
    Args:
        app: Экземпляр приложения Flask
    """
    app.register_blueprint(pdf_bp)
    app.register_blueprint(api_pdf_bp)