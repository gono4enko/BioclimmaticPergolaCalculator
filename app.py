"""
Калькулятор стоимости пергол с поддержкой различных опций и материалов.
"""
import os
import streamlit as st
from utils.logger import setup_logger, log_user_action, log_calculation
from utils.calculator import calculate_pergola_cost
from components.header import render_header
from components.dimensions_form import render_dimensions_form
from components.options_form import render_options_form
from components.results import render_results
from components.specification import render_specification

# Настраиваем логирование
logger = setup_logger()

def perform_calculation(dimensions, options):
    """Выполнить расчет стоимости перголы"""
    try:
        # Логируем входные данные
        log_calculation(dimensions, options)
        
        # Выполняем расчет
        results = calculate_pergola_cost(dimensions, options)
        
        # Логируем результаты
        if 'error' in results:
            log_calculation(dimensions, options, error=results['error'])
        else:
            log_calculation(dimensions, options, results)
        
        return results
    
    except Exception as e:
        error_msg = f"Ошибка при расчете: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}

def main():
    """Основная функция приложения"""
    # Настраиваем страницу
    st.set_page_config(
        page_title="Калькулятор пергол DecoLife",
        page_icon="🏠",
        layout="wide"
    )
    
    # Отображаем заголовок
    render_header()
    
    # Делим экран на две колонки
    col1, col2 = st.columns([1, 1])
    
    # В левой колонке отображаем формы ввода данных
    with col1:
        # Форма для ввода размеров
        dimensions = render_dimensions_form()
        
        # Форма для выбора опций
        options = render_options_form()
        
        # Кнопка для расчета
        if st.button("Рассчитать стоимость", type="primary"):
            with st.spinner("Выполняется расчет..."):
                # Проверяем, что у нас есть данные для расчета
                if dimensions and options:
                    # Сохраняем предыдущие результаты, если они есть
                    if 'results' in st.session_state:
                        st.session_state.prev_results = st.session_state.results
                    
                    # Выполняем расчет
                    results = perform_calculation(dimensions, options)
                    
                    # Сохраняем результаты и опции в состоянии сессии
                    st.session_state.results = results
                    st.session_state.options = options
                    
                    # Логируем действие пользователя
                    log_user_action("Выполнен расчет стоимости", {
                        "dimensions": dimensions,
                        "options": options
                    })
                    
                    # Перезагружаем страницу для отображения результатов
                    st.rerun()
    
    # В правой колонке отображаем результаты расчета
    with col2:
        if 'results' in st.session_state and 'options' in st.session_state:
            # Создаем вкладки для разных представлений результатов
            tab1, tab2 = st.tabs(["Результаты расчета", "Спецификация перголы"])
            
            with tab1:
                render_results(st.session_state.results)
            
            with tab2:
                render_specification(st.session_state.results, st.session_state.options)
        else:
            st.info("Введите данные и нажмите 'Рассчитать стоимость' для получения результата")
    
    # Добавляем информацию о версии внизу страницы
    st.markdown("---")
    st.caption("© 2025 DecoLife | Калькулятор пергол v1.0")
    
    # Логируем посещение страницы
    if 'page_viewed' not in st.session_state:
        log_user_action("Посещение страницы калькулятора")
        st.session_state.page_viewed = True

if __name__ == "__main__":
    # Создаем директории, если они не существуют
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/price_tables", exist_ok=True)
    
    # Запускаем приложение
    main()