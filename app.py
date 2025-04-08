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
    
    # Задаем стили для компактного и читаемого интерфейса по новому дизайну
    st.markdown("""
    <style>
    .block-container {
        max-width: 800px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        margin: 0 auto;
    }
    /* Глобальные стили для улучшения читаемости */
    .stApp, .stApp p, .stApp div {
        font-size: 1rem;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    /* Заголовки секций */
    .section-header {
        font-size: 1.2rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
    }
    /* Стили для плиточных кнопок */
    .tile-button {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        height: 100%;
        transition: all 0.2s;
    }
    .tile-button:hover {
        border-color: #0066cc;
        box-shadow: 0 2px 5px rgba(0, 0, 102, 0.1);
    }
    .tile-button.selected {
        background-color: #e6f2ff;
        border-color: #0066cc;
        box-shadow: 0 2px 5px rgba(0, 0, 102, 0.1);
    }
    .tile-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #0066cc;
        margin-bottom: 5px;
    }
    .tile-desc {
        font-size: 0.9rem;
        color: #666;
    }
    /* Компактные, но читаемые поля формы */
    div.row-widget.stNumberInput, div.row-widget.stTextInput {
        margin-bottom: 0.8rem !important;
    }
    /* Стили для radio и checkbox групп */
    div.row-widget.stRadio > div {
        flex-direction: row !important;
        gap: 10px;
    }
    /* Стили для основной кнопки расчета */
    .main-button {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    .main-button:hover {
        background-color: #0055aa;
    }
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .block-container {
            max-width: 100%;
            padding: 0.5rem;
        }
        .tile-title {
            font-size: 0.9rem;
        }
        .tile-desc {
            font-size: 0.8rem;
        }
    }
    /* Стили для карточек с результатами */
    .result-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .result-card-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
    }
    /* Устраняем пустые промежутки между компонентами */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 10px !important;
    }
    /* Убираем лишние границы для компактности */
    .element-container {
        margin-top: 0;
        margin-bottom: 0.6rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок калькулятора - крупный и четкий
    st.markdown("<h1 style='text-align: center; margin-top: 20px; margin-bottom: 10px; font-size: 1.8rem; font-weight: 600; color: #0066cc;'>Калькулятор стоимости перголы</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 20px; font-size: 1rem;'>Введите размеры и параметры перголы для расчета стоимости в евро (€)</p>", unsafe_allow_html=True)
    dimensions = render_dimensions_form()
    
    # Убираем заголовок конфигурации для более чистого интерфейса
    options = render_options_form()
    
    # Кнопка для расчета с улучшенным стилем
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #0066cc;
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 6px;
            padding: 12px 0;
            border: none;
            margin-top: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
            transition: all 0.2s;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #0055aa;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("Рассчитать стоимость", type="primary", use_container_width=True):
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