"""
Скрипт для восстановления функциональности генерации PDF
из опубликованной версии приложения.
"""

import os
import re
import shutil
import logging
from datetime import datetime

# Настраиваем логирование
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join("logs", "pdf_restore.log"),
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("restore_pdf")

def restore_pdf_generator():
    """Восстанавливает генератор PDF из опубликованной версии"""
    logger.info("Начинаем восстановление PDF-генератора")
    
    # Создаем директорию для логов, если она не существует
    os.makedirs("logs", exist_ok=True)
    
    # Создаем директорию для PDF, если она не существует
    os.makedirs("generated_pdf", exist_ok=True)

    # Проверяем, есть ли упрощенный PDF-генератор и создаем его, если нет
    if not os.path.exists("simple_pdf.py"):
        logger.info("Создаем упрощенный генератор PDF...")
        create_simple_pdf_generator()
    
    # Обновляем функцию export_to_pdf в app.py для использования упрощенного генератора
    update_export_function()
    
    # Обновляем кнопку скачивания PDF
    update_download_button()
    
    logger.info("Восстановление PDF-генератора завершено!")
    print("Восстановление PDF-генератора завершено!")
    return True

def create_simple_pdf_generator():
    """Создает простой генератор PDF на основе FPDF"""
    logger.info("Создание файла simple_pdf.py")
    code = '''"""
Простой генератор PDF для перголы с минимальными зависимостями.
Создает простой PDF-документ с информацией о перголе и ее стоимости.
Используется как резервный вариант, если основной генератор PDF не работает.
"""

import os
import datetime
from fpdf import FPDF
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_pdf")

def generate_simple_pdf(pergola_data):
    """
    Создает простой PDF-документ с информацией о перголе.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе
    
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    try:
        # Создаем директорию для PDF, если она не существует
        os.makedirs("generated_pdf", exist_ok=True)
        
        # Получаем данные из pergola_data
        pergola_type = pergola_data.get("pergola_type", "B500NEW")
        width = pergola_data.get("width", 3.0)
        length = pergola_data.get("length", 4.0)
        modules = pergola_data.get("modules", 1)
        items = pergola_data.get("items", [])
        total_price = pergola_data.get("total_price", 0)
        discount = pergola_data.get("discount", 0)
        total_after_discount = pergola_data.get("total_price_after_discount", 0)
        
        # Генерируем имя файла
        today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"КП_пергола_{pergola_type}_{width}x{length}м_{today}.pdf"
        pdf_path = os.path.join("generated_pdf", filename)
        
        # Создаем PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Добавляем заголовок
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Коммерческое предложение", ln=True, align="C")
        pdf.ln(5)
        
        # Добавляем информацию о перголе
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Тип перголы: {pergola_type}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 8, f"Размеры: {width} x {length} м", ln=True)
        pdf.cell(190, 8, f"Модули: {modules}", ln=True)
        pdf.ln(5)
        
        # Добавляем таблицу с опциями
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Выбранные опции:", ln=True)
        pdf.ln(2)
        
        # Заголовки таблицы
        pdf.set_font("Arial", "B", 10)
        pdf.cell(110, 7, "Наименование", 1)
        pdf.cell(40, 7, "Количество", 1)
        pdf.cell(40, 7, "Цена (руб.)", 1)
        pdf.ln()
        
        # Строки таблицы
        pdf.set_font("Arial", "", 10)
        for item in items:
            name = item.get("name", "")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            
            # Добавляем строку в таблицу
            pdf.cell(110, 7, name, 1)
            pdf.cell(40, 7, str(quantity), 1)
            pdf.cell(40, 7, f"{price:,.0f}", 1)
            pdf.ln()
        
        # Добавляем информацию о стоимости
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 8, "Общая стоимость:", 0)
        pdf.cell(40, 8, f"{total_price:,.0f} руб.", 0, ln=True)
        
        if discount > 0:
            pdf.set_font("Arial", "", 12)
            pdf.cell(150, 8, f"Скидка ({discount}%):", 0)
            discount_amount = total_price - total_after_discount
            pdf.cell(40, 8, f"-{discount_amount:,.0f} руб.", 0, ln=True)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(150, 8, "Итоговая стоимость:", 0)
            pdf.cell(40, 8, f"{total_after_discount:,.0f} руб.", 0, ln=True)
        
        # Добавляем дату и дисклеймер
        pdf.ln(15)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(190, 6, f"Предложение сформировано: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
        pdf.cell(190, 6, "Предложение действительно в течение 30 дней.", ln=True)
        
        # Сохраняем PDF-файл
        pdf.output(pdf_path)
        logger.info(f"PDF успешно создан по пути: {pdf_path}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {str(e)}", exc_info=True)
        return None
'''
    
    try:
        with open("simple_pdf.py", "w", encoding="utf-8") as f:
            f.write(code.strip())
        logger.info("Файл simple_pdf.py успешно создан")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании simple_pdf.py: {str(e)}")
        return False

def update_export_function():
    """Обновляет функцию export_to_pdf в app.py для использования упрощенного генератора PDF"""
    logger.info("Обновление функции export_to_pdf в app.py")
    try:
        # Проверяем существование файла
        if not os.path.exists("app.py"):
            logger.error("Файл app.py не найден")
            return False
            
        # Создаем бэкап app.py перед изменением
        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"app.py.backup_pdf_restore_{backup_time}"
        shutil.copy("app.py", backup_path)
        logger.info(f"Создан бэкап app.py: {backup_path}")
        
        # Читаем содержимое файла
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Шаблон для поиска функции export_to_pdf
        export_pattern = r'def export_to_pdf\(\):[^#]*?(?=def |$)'
        match = re.search(export_pattern, content, re.DOTALL)
        
        if not match:
            logger.warning("Не удалось найти функцию export_to_pdf в файле app.py")
            # Ищем другой шаблон
            export_pattern = r'def export_to_pdf\(\):.*?return .*?pdf_path'
            match = re.search(export_pattern, content, re.DOTALL | re.MULTILINE)
            
            if not match:
                logger.error("Не удалось найти функцию export_to_pdf в файле app.py по альтернативному шаблону")
                return False
        
        # Новый код функции
        new_function = '''
def export_to_pdf():
    """
    Формирует данные для экспорта и генерирует PDF-файл с улучшенным скачиванием.
    Использует простую версию PDF-генератора для максимальной надежности.
    
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    import os
    import sys
    import logging
    import time
    
    # Настраиваем логирование для отладки PDF-генерации
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join("logs", "pdf_generation.log"),
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("export_to_pdf")
    
    # Проверяем, были ли выполнены расчеты
    if 'results' not in st.session_state:
        st.error("Сначала нужно выполнить расчет!")
        return None
    
    results = st.session_state.results
    options = results.get("options", {})
    dimensions = results.get("dimensions", {})
    pergola_type = options.get("pergola_type", "")
    
    # Создаем необходимые директории
    os.makedirs("generated_pdf", exist_ok=True)
    
    # Получаем параметры из результатов расчета
    default_width = st.session_state.get('cached_width') or 3.0
    default_length = st.session_state.get('cached_length') or 4.0
    
    # Логируем данные для отладки
    logger.info(f"Экспорт PDF для перголы: {pergola_type}")
    logger.info(f"Размеры из результатов: {dimensions}")
    
    # Формируем данные для PDF
    pdf_data = {
        "pergola_type": pergola_type,
        "width": dimensions.get("width", default_width),
        "length": dimensions.get("length", default_length),
        "modules": dimensions.get("modules", 1),
        "items": results.get("items", []),
        "total_price": results.get("total_price", 0),
        "discount": results.get("discount", 0),
        "total_price_after_discount": results.get("total_price_after_discount", 0)
    }
    
    try:
        # Показываем индикатор загрузки
        with st.spinner("Создание PDF-документа..."):
            # Пробуем использовать простой генератор PDF
            try:
                logger.info("Используем simple_pdf для создания PDF")
                from simple_pdf import generate_simple_pdf
                pdf_file_path = generate_simple_pdf(pdf_data)
                
                if pdf_file_path and os.path.exists(pdf_file_path):
                    # Выводим читаемую для пользователя информацию о созданном PDF
                    logger.info(f"PDF файл успешно создан: {pdf_file_path}")
                    return pdf_file_path
                else:
                    # Пробуем запасной вариант
                    logger.warning("Не удалось создать PDF через simple_pdf, пробуем основной генератор")
                    
                    # Пробуем использовать основной PDF-генератор
                    from pdf_generator_fpdf_rus import generate_commercial_offer, format_pergola_data_for_pdf
                    
                    # Генерируем PDF с полными данными
                    pergola_data = format_pergola_data_for_pdf(results, options, dimensions, "")
                    pdf_file_path = generate_commercial_offer(pergola_data)
                    
                    if pdf_file_path and os.path.exists(pdf_file_path):
                        logger.info(f"PDF успешно создан через основной генератор: {pdf_file_path}")
                        return pdf_file_path
                    else:
                        st.error("Не удалось создать PDF документ")
                        return None
                
            except ImportError as ie:
                logger.error(f"Ошибка импорта модуля для PDF: {str(ie)}")
                st.error(f"Ошибка при создании PDF: модуль не найден")
                return None
                
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при генерации PDF: {str(e)}", exc_info=True)
        st.error(f"Не удалось сгенерировать PDF. Пожалуйста, попробуйте еще раз.")
        return None
'''
        
        # Заменяем функцию в файле
        new_content = content.replace(match.group(0), new_function)
        
        # Проверяем, что замена произошла
        if new_content == content:
            logger.warning("Замена функции export_to_pdf не произведена")
            return False
            
        # Записываем обновленный контент
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        logger.info("Функция export_to_pdf успешно обновлена в app.py")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении функции export_to_pdf: {str(e)}")
        return False

def update_download_button():
    """Обновляет код кнопки скачивания PDF в app.py"""
    logger.info("Обновление кнопки скачивания PDF")
    try:
        # Читаем содержимое файла
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ищем паттерны для кнопки скачивания PDF
        download_patterns = [
            r'# Получаем улучшенный компонент для скачивания PDF.*?get_streamlit_download_component\(pdf_path\)',
            r'from improved_pdf_export import get_streamlit_download_component.*?get_streamlit_download_component\(pdf_path\)',
            r'# Отображаем кнопку скачивания.*?st\.download_button\('
        ]
        
        found = False
        for pattern in download_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                found = True
                download_code = '''
                    # Читаем PDF-файл для скачивания
                    import time
                    try:
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            
                        # Отображаем кнопку скачивания с уникальным ключом, чтобы избежать дублирования
                        st.download_button(
                            label="📥 Скачать PDF",
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            key=f"download_pdf_{int(time.time())}",  # Генерируем уникальный ключ на основе времени
                            help="Скачать PDF-файл на компьютер",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Ошибка при подготовке файла для скачивания: {str(e)}")'''
                
                # Заменяем код кнопки скачивания
                new_content = content.replace(match.group(0), download_code)
                
                # Проверяем, произошла ли замена
                if new_content == content:
                    logger.warning(f"Замена кнопки скачивания PDF по шаблону '{pattern}' не произведена")
                    continue
                
                # Записываем обновленный контент
                with open("app.py", "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                logger.info("Кнопка скачивания PDF успешно обновлена")
                return True
        
        if not found:
            logger.warning("Не удалось найти код кнопки скачивания PDF в app.py")
            # Ищем место, где отображается успешное создание PDF
            success_pattern = r'st\.success\(f"PDF файл успешно создан"\)'
            match = re.search(success_pattern, content)
            
            if match:
                # Добавляем код кнопки скачивания после сообщения об успехе
                insert_position = match.end()
                download_code = '''
                    
                    # Читаем PDF-файл для скачивания
                    import time
                    try:
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            
                        # Отображаем кнопку скачивания с уникальным ключом
                        st.download_button(
                            label="📥 Скачать PDF",
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            key=f"download_pdf_{int(time.time())}",
                            help="Скачать PDF-файл на компьютер",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Ошибка при подготовке файла для скачивания: {str(e)}")'''
                
                new_content = content[:insert_position] + download_code + content[insert_position:]
                
                # Записываем обновленный контент
                with open("app.py", "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                logger.info("Добавлена новая кнопка скачивания PDF после сообщения об успехе")
                return True
                
            logger.error("Не удалось найти место для вставки кнопки скачивания PDF")
            return False
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении кнопки скачивания PDF: {str(e)}")
        return False

if __name__ == "__main__":
    # Запускаем восстановление
    restore_pdf_generator()