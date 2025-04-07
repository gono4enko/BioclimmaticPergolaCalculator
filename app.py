import streamlit as st
import logging
import os
from datetime import datetime

from utils.logger import setup_logger
from utils.calculator import calculate_pergola_cost
from utils.validation import validate_dimensions

from components.header import render_header
from components.dimensions_form import render_dimensions_form
from components.options_form import render_options_form
from components.results import render_results

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = f"{log_dir}/pergola_calculator_{datetime.now().strftime('%Y%m%d')}.log"
logger = setup_logger(log_file)

# Настройка страницы
st.set_page_config(
    page_title="Калькулятор пергол Decolife",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Инициализация состояния сессии при первом запуске
if 'calculation_done' not in st.session_state:
    st.session_state.calculation_done = False
    
if 'calculation_results' not in st.session_state:
    st.session_state.calculation_results = None
    
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

if 'log_info' not in st.session_state:
    st.session_state.log_info = []

def perform_calculation(dimensions, options):
    """Выполнить расчет стоимости перголы"""
    try:
        logger.info(f"Начат расчет: Размеры {dimensions}, Опции {options}")
        
        # Валидация данных
        validation_error = validate_dimensions(dimensions)
        if validation_error:
            st.session_state.error_message = validation_error
            st.session_state.calculation_done = False
            logger.warning(f"Ошибка валидации: {validation_error}")
            return
        
        # Расчет стоимости
        results = calculate_pergola_cost(dimensions, options)
        
        # Сохранение результатов
        st.session_state.calculation_results = results
        st.session_state.calculation_done = True
        st.session_state.error_message = None
        
        # Логирование успешного расчета
        log_entry = f"Расчет выполнен для {options['pergola_type']}, размеры: {dimensions['width']}x{dimensions['length']}x{dimensions['height']}, итоговая стоимость: {results['total_cost']} евро"
        st.session_state.log_info.append(log_entry)
        logger.info(log_entry)
        
    except Exception as e:
        error_msg = f"Ошибка при расчете: {str(e)}"
        st.session_state.error_message = error_msg
        st.session_state.calculation_done = False
        logger.error(error_msg, exc_info=True)

def main():
    """Основная функция приложения"""
    try:
        # Отрисовка заголовка
        render_header()
        
        # Форма размеров
        dimensions = render_dimensions_form()
        
        # Форма опций
        options = render_options_form()
        
        # Кнопка расчета
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Рассчитать стоимость", type="primary", use_container_width=True):
                perform_calculation(dimensions, options)
        
        # Отображение ошибки, если есть
        if st.session_state.error_message:
            st.error(st.session_state.error_message)
        
        # Отображение результатов, если расчет выполнен
        if st.session_state.calculation_done and st.session_state.calculation_results:
            render_results(st.session_state.calculation_results)
        
        # Логи действий пользователя (скрытый раздел для разработчиков)
        with st.expander("Журнал действий", expanded=False):
            for idx, log in enumerate(reversed(st.session_state.log_info)):
                st.text(f"{idx+1}. {log}")
            
            if st.button("Очистить журнал"):
                st.session_state.log_info = []
                st.rerun()
                
    except Exception as e:
        logger.critical(f"Критическая ошибка в приложении: {str(e)}", exc_info=True)
        st.error(f"Произошла непредвиденная ошибка. Пожалуйста, обратитесь к разработчику.")

if __name__ == "__main__":
    main()
