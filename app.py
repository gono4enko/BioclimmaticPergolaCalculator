"""
Калькулятор стоимости пергол с поддержкой различных опций и материалов.
"""
import os
import streamlit as st
from utils.logger import setup_logger, log_user_action, log_calculation
from utils.calculator import calculate_pergola_cost
from components.header import render_header
from components.dimensions_form import render_dimensions_form
from components.scroll_helper import scroll_to_results, add_button_animation
from components.options_form import render_options_form
from components.results_new import render_results

# Обновляем освещение напрямую в конфигурации
from config.pergola_types import LIGHTING_TYPES
LIGHTING_TYPES["none"]["description"] = ""  # Убираем описание для опции "Без освещения"
LIGHTING_TYPES["led"]["name"] = "Сверхъяркая LED подсветка"
LIGHTING_TYPES["led"]["description"] = "Яркая LED лента по периметру перголы"
LIGHTING_TYPES["rgb"]["name"] = "Светодиодная RGB подсветка"
LIGHTING_TYPES["rgb"]["description"] = "Яркая RGB лента со сменой цвета по периметру перголы"
LIGHTING_TYPES["led_rgb"]["name"] = "Комбинированное LED + RGB освещение"
LIGHTING_TYPES["led_rgb"]["description"] = "Позволяет выбрать между белым и цветным освещением"

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
    
    # Добавляем JavaScript для определения темы пользователя
    st.markdown("""
    <script>
    function detectUserTheme() {
        // Проверяем, поддерживает ли браузер определение темы
        if (window.matchMedia) {
            // Проверяем предпочтительную тему пользователя
            var darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            // Устанавливаем переменную с информацией о теме
            localStorage.setItem('userPrefersDark', darkMode);
            
            // Возвращаем выбранную тему для дальнейшего использования
            return darkMode;
        } else {
            // Если браузер не поддерживает определение темы, устанавливаем светлую по умолчанию
            localStorage.setItem('userPrefersDark', false);
            return false;
        }
    }
    
    // Вызываем функцию определения темы при загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        var isDarkMode = detectUserTheme();
        
        // Применяем соответствующие стили для темного режима
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.add('light-mode');
        }
        
        // Добавляем слушатель события для отслеживания изменений темы
        if (window.matchMedia) {
            var darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            darkModeMediaQuery.addEventListener('change', function(e) {
                var isDarkMode = e.matches;
                localStorage.setItem('userPrefersDark', isDarkMode);
                
                // Обновляем классы
                document.body.classList.remove('light-mode', 'dark-mode');
                document.body.classList.add(isDarkMode ? 'dark-mode' : 'light-mode');
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Задаем стили для компактного и читаемого интерфейса по новому дизайну
    st.markdown("""
    <style>
    /* Базовые стили для светлой темы (по умолчанию) */
    :root {
        --background-color: #ffffff;
        --text-color: #333333;
        --label-color: #333333;
        --border-color: #dddddd;
        --highlight-color: #0066cc;
        --highlight-bg: #e6f2ff;
        --highlight-hover: #0055aa;
        --card-bg: #f8f9fa;
        --card-border: #eeeeee;
        --button-bg: #0066cc;
        --button-text: white;
        --tile-bg: white;
        --tile-border: #dddddd;
        --header-color: #0066cc;
        --section-border: #eeeeee;
    }
    
    /* Стили для темной темы */
    body.dark-mode {
        --background-color: #121212;
        --text-color: #e0e0e0;
        --label-color: #ffffff;
        --border-color: #444444;
        --highlight-color: #4d94ff;
        --highlight-bg: #1a3d66;
        --highlight-hover: #66a3ff;
        --card-bg: #1e1e1e;
        --card-border: #333333;
        --button-bg: #1a73e8;
        --button-text: white;
        --tile-bg: #1e1e1e;
        --tile-border: #444444;
        --header-color: #4d94ff;
        --section-border: #333333;
    }
    
    /* Применяем переменные к элементам */
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
        color: var(--text-color);
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--text-color);
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid var(--section-border);
    }
    
    /* Стили для плиточных кнопок */
    .tile-button {
        background-color: var(--tile-bg);
        border: 1px solid var(--tile-border);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        height: 100%;
        transition: all 0.2s;
    }
    
    .tile-button:hover {
        border-color: var(--highlight-color);
        box-shadow: 0 2px 5px rgba(0, 0, 102, 0.1);
    }
    
    .tile-button.selected {
        background-color: var(--highlight-bg);
        border-color: var(--highlight-color);
        box-shadow: 0 2px 5px rgba(0, 0, 102, 0.1);
    }
    
    .tile-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--highlight-color);
        margin-bottom: 5px;
    }
    
    .tile-desc {
        font-size: 0.9rem;
        color: var(--text-color);
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
        background-color: var(--button-bg);
        color: var(--button-text);
        font-weight: bold;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    
    .main-button:hover {
        background-color: var(--highlight-hover);
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
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .result-card-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--text-color);
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid var(--card-border);
    }
    
    /* Устраняем пустые промежутки между компонентами */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Убираем лишние границы для компактности */
    .element-container {
        margin-top: 0;
        margin-bottom: 0;
    }
    
    /* Уменьшаем отступы у карточек результатов */
    .result-card {
        margin-bottom: 0 !important;
        padding: 5px 10px !important;
    }
    
    /* Устанавливаем минимальный отступ между блоками формы */
    .stMarkdown {
        margin-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок калькулятора - крупный и четкий
    st.markdown("<h1 style='text-align: center; margin-top: 20px; margin-bottom: 10px; font-size: 1.8rem; font-weight: 600; color: var(--header-color);'>Калькулятор стоимости перголы</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 20px; font-size: 1rem; color: var(--text-color);'>Введите размеры и параметры перголы для расчета стоимости в евро (€)</p>", unsafe_allow_html=True)
    dimensions = render_dimensions_form()
    
    # Убираем заголовок конфигурации для более чистого интерфейса
    options = render_options_form()
    
    # Кнопка для расчета с улучшенным стилем
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: var(--button-bg);
            color: var(--button-text);
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
            background-color: var(--highlight-hover);
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }
        
        /* Стили для полей ввода и меток */
        .stTextInput label, .stNumberInput label, .stSelectbox label {
            color: var(--label-color) !important;
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
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.5rem; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
    
    # Отображаем результаты расчета под формами ввода
    if 'results' in st.session_state and 'options' in st.session_state:
        # Показываем общий результат и детальную информацию
        render_results(st.session_state.results)
        
        # Добавляем скрипт для автоматического скролла к результатам
        scroll_to_results()
    
    # Добавляем информацию о версии внизу страницы (компактно)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.3rem; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: var(--text-color);'>© 2025 DecoLife | Калькулятор пергол v1.0</div>", unsafe_allow_html=True)
    
    # Добавляем анимацию нажатия кнопки
    add_button_animation()
    
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