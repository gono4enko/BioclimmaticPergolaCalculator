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
from components.results_new import render_results
# Удалено: from components.specification import render_specification
from components.scroll_helper import scroll_to_results

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
        layout="centered"  # Изменено с "wide" на "centered" для более узкого интерфейса
    )
    
    # Задаем стили для максимально компактного основного контейнера, ориентируясь на мобильный интерфейс
    st.markdown("""
    <style>
    .block-container {
        max-width: 450px;
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
        margin: 0 auto;
    }
    /* Радикально уменьшаем отступы между элементами */
    div.row-widget.stButton {
        margin-bottom: 0 !important;
    }
    /* Уменьшаем размер шрифта для всего интерфейса */
    .stApp, .stApp p, .stApp div {
        font-size: 0.8rem;
    }
    /* Делаем основной контейнер максимально плотным */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        padding-top: 0 !important;
    }
    /* Убираем лишние отступы для формы */
    div[data-testid="stForm"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Уменьшаем отступы у всех элементов ввода */
    div.row-widget.stNumberInput, div.row-widget.stTextInput, div.row-widget.stTextArea,
    div.row-widget.stRadio, div.row-widget.stCheckbox {
        margin-top: 0 !important;
        margin-bottom: 0.1rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Уменьшаем отступы между заголовками и контентом */
    h1, h2, h3, p, .stMarkdown {
        margin-top: 0 !important;
        margin-bottom: 0.2rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        line-height: 1.1 !important;
    }
    /* Удаляем лишние границы и отступы */
    .element-container {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    /* Убираем лишние отступы у кнопок +/- в числовых полях */
    button.step-down, button.step-up {
        padding: 0 !important;
        min-height: 0 !important;
        line-height: 1 !important;
    }
    /* Убираем лишние белые пространства в форме */
    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Делаем number input более компактным */
    input[type="number"] {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
        min-height: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок калькулятора в ультра-компактном стиле
    st.markdown("<h1 style='text-align: center; margin-top: 10px; margin-bottom: 5px; font-size: 1.3rem;'>Калькулятор стоимости перголы</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 10px; font-size: 0.8rem;'>Введите размеры и параметры перголы для расчета стоимости в евро (€).</p>", unsafe_allow_html=True)
    dimensions = render_dimensions_form()
    
    # Убираем заголовок конфигурации для более чистого интерфейса
    options = render_options_form()
    
    # Кнопка для расчета в ультра-компактном стиле
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #0066cc;
            color: white;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px;
            padding: 8px 0;
            border: none;
            margin-top: 10px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #0055aa;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("Рассчитать", type="primary", use_container_width=True):
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
    
    # Добавляем разделитель (компактный)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.5rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    
    # Отображаем результаты расчета под формами ввода
    if 'results' in st.session_state and 'options' in st.session_state:
        # Заголовок для секции результатов (компактный)
        st.markdown("<h3 style='text-align: center; margin-top: 10px; margin-bottom: 10px; font-size: 1.1rem;'>Результаты расчета</h3>", unsafe_allow_html=True)
        
        # Показываем общий результат и детальную информацию
        render_results(st.session_state.results)
        
        # Добавляем скрипт для автоматического скролла к результатам
        scroll_to_results()
    
    # Добавляем информацию о версии внизу страницы (компактно)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.3rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #999;'>© 2025 DecoLife | Калькулятор пергол v1.0</div>", unsafe_allow_html=True)
    
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