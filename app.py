"""
Калькулятор стоимости пергол с поддержкой различных опций и материалов.
"""
import os
import streamlit as st

# Настраиваем страницу перед выполнением любых других команд Streamlit
st.set_page_config(
    page_title="Калькулятор пергол DecoLife",
    page_icon="🏠",
    layout="centered",  # Центрированный макет для более узкого интерфейса
    initial_sidebar_state="collapsed" # Скрываем сайдбар по умолчанию
)

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

# Второй вызов set_page_config удаляем, т.к. он уже вызван выше

def main():
    """Основная функция приложения"""
    
    # Добавляем CSS для увеличения кнопки сразу после загрузки страницы
    st.markdown("""
    <style>
    /* Глобальные стили для кнопки расчета - управление размером */
    .stButton button {
        font-size: 2rem !important;
        padding: 25px 25px !important;
        min-height: 80px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Принудительно устанавливаем светлую тему независимо от предпочтений пользователя
    st.markdown("""
    <script>
    // Принудительно устанавливаем светлую тему при загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        // Устанавливаем светлую тему в localStorage
        localStorage.setItem('userPrefersDark', false);
        
        // Принудительно добавляем класс light-mode для тела документа
        document.body.classList.add('light-mode');
        document.body.classList.remove('dark-mode');
        document.documentElement.classList.remove('dark');
        document.documentElement.setAttribute('data-theme', 'light');
        
        // Принудительно устанавливаем черный цвет для текста заголовков
        document.querySelectorAll('.section-header').forEach(function(el) {
            el.style.color = '#000000';
            el.style.backgroundColor = '#FFFFFF';
        });
        
        // Отключаем слушатель события для изменений темы - всегда светлая тема
        if (window.matchMedia) {
            var darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            darkModeMediaQuery.removeEventListener('change', function() {});
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
        --text-color: #ffffff;  /* Изменено с #e0e0e0 на #ffffff для лучшей видимости */
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
    
    /* Принудительно делаем весь текст белым в темном режиме - глобально */
    .stApp.dark div, 
    .stApp.dark p, 
    .stApp.dark span, 
    .stApp.dark label, 
    .stApp.dark .section-header, 
    .stApp.dark .streamlit-expanderHeader,
    .stApp.dark [data-testid="stMarkdown"] p,
    .stApp.dark [data-testid="stText"] p,
    .stApp.dark [data-testid="stHeader"] h1,
    .stApp.dark [data-testid="stHeader"] h2,
    .stApp.dark [data-testid="stHeader"] h3,
    .stApp.dark [data-testid="stSubheader"] h1, 
    .stApp.dark [data-testid="stSubheader"] h2, 
    .stApp.dark [data-testid="stSubheader"] h3, 
    .stApp.dark [data-testid="stExpander"] .streamlit-expanderHeader,
    .stApp.dark [data-testid="stVerticalBlock"] div,
    .stApp.dark [data-testid="stForm"] div,
    .stApp.dark [data-testid="stFormSubmitButton"] button,
    .stApp.dark .stHeadingContainer h1,
    .stApp.dark .stHeadingContainer h2,
    .stApp.dark .stHeadingContainer h3,
    .stApp.dark .stMarkdown p,
    .stApp.dark .stButton button,
    .stApp.dark .stNumberInput div,
    .stApp.dark .stTextInput div,
    .stApp.dark .stTextArea div,
    .dark-mode div,
    .dark-mode p,
    .dark-mode h1,
    .dark-mode h2,
    .dark-mode h3 {
        color: #FFFFFF !important;
    }
    
    /* Дополнительный селектор для любых типов заголовков с высоким приоритетом */
    [data-theme="dark"] [data-testid*="stVerticalBlock"] div.section-header,
    [data-theme="dark"] div.section-header,
    .dark div.section-header {
        color: #FFFFFF !important;
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
    
    /* Стили для плиточных кнопок - БЕЛЫЙ ФОН для невыбранных */
    .tile-button {
        background-color: #FFFFFF !important; /* Всегда белый фон */
        border: 1px solid #dddddd !important; /* Светлая рамка */
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        height: 100%;
        transition: all 0.2s;
    }
    
    .tile-button:hover {
        border-color: #0066cc !important; /* Синяя рамка при наведении */
        box-shadow: 0 2px 5px rgba(0, 0, 102, 0.1);
    }
    
    /* Выбранная плитка с МАЛЕНЬКИМ синим индикатором */
    .tile-button.selected {
        background-color: #FFFFFF !important; /* Белый фон */
        border-color: #0066cc !important; /* Синяя рамка */
        box-shadow: 0 2px 5px rgba(0, 0, 102, 0.1);
        position: relative; /* Для позиционирования индикатора */
    }
    
    /* Добавляем маленький синий индикатор выбора внизу плитки */
    .tile-button.selected::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px; /* В 5 раз меньше по высоте */
        background-color: #0066cc !important;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
    }
    
    .tile-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #0066cc !important; /* Всегда синий цвет */
        margin-bottom: 5px;
    }
    
    .tile-desc {
        font-size: 0.9rem;
        color: #000000 !important; /* Всегда черный текст */
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
        margin-top: 0 !important;
        padding: 3px 10px !important;
    }
    
    /* Минимальные отступы для блока подсветки */
    div:has(> div.section-header:contains("Подсветка")) {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Уменьшение интервалов между кнопками подсветки */
    [data-testid="column"]:has([data-testid="stButton"] > button) {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Уменьшаем высоту строк в кнопках, исключая основную кнопку расчета */
    [data-testid="stButton"]:not(:has(> button[data-testid="baseButton-primary"])) > button {
        line-height: 1 !important;
        padding-top: 2px !important;
        padding-bottom: 2px !important;
        font-size: 0.8rem !important;
        margin-bottom: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Принудительно устанавливаем минимальные отступы для блока подсветки */
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stVerticalBlock"] > div > div > [data-testid="column"]) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Максимально уменьшаем отступы между вариантами освещения (всего 1-2px) */
    [data-testid="column"] > div {
        margin-top: 0 !important;
        margin-bottom: 1px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Уменьшаем вертикальное расстояние между блоками подсветки в 5 раз */
    [data-testid="stHorizontalBlock"] div[data-testid="column"] {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Специфично для блоков подсветки - делаем минимальный отступ */
    [data-testid="stVerticalBlock"] div:has(> .section-header:contains("Подсветка")),
    [data-testid="stVerticalBlock"] div:has(> .section-header:contains("Подсветка")) + div {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* ВАЖНО: ВСЕ ТЕКСТЫ ВСЕГДА ЧЕРНЫЕ - ОТКЛЮЧЕН НОЧНОЙ РЕЖИМ */
    div, p, span, h1, h2, h3, h4, h5, h6,
    .stApp div, .stApp p, .stApp span, 
    .stApp h1, .stApp h2, .stApp h3, 
    .stApp h4, .stApp h5, .stApp h6,
    .stApp.dark div, .stApp.dark p, .stApp.dark span, 
    .stApp.dark h1, .stApp.dark h2, .stApp.dark h3, 
    .stApp.dark h4, .stApp.dark h5, .stApp.dark h6 {
        color: #000000 !important;
    }
    
    /* Фиксируем светлый фон */
    body, .stApp, .stApp.dark {
        background-color: #FFFFFF !important;
    }
    
    /* Заголовки всегда на светлом фоне с черным текстом */
    .section-header, .stApp .section-header, .stApp.dark .section-header {
        color: #000000 !important;
        border-bottom-color: #dddddd !important;
        background-color: #FFFFFF !important;
    }
    
    /* Устанавливаем минимальный отступ между блоками формы */
    .stMarkdown {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Уменьшаем отступы между блоками формы */
    .result-card {
        margin-top: 0 !important;
        margin-bottom: 2px !important;
        padding-top: 1px !important;
        padding-bottom: 1px !important;
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
    _, center_col, _ = st.columns([1, 3, 1]) # Делаем кнопку шире, увеличивая относительный размер колонки
    with center_col:
        st.markdown("""
        <style>
        /* Глобальные стили для кнопки расчета - применяются с наивысшим приоритетом */
        div[data-testid="stButton"] > button,
        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="column"] > div[data-testid="stButton"] > button,
        button[data-testid="baseButton-primary"],
        .element-container div[data-testid="stButton"] button,
        .stButton > button {
            background-color: var(--button-bg) !important;
            color: var(--button-text) !important;
            font-size: 2rem !important; /* Сделаем еще больше */
            font-weight: 700 !important; /* Жирный шрифт */
            border-radius: 8px !important;
            padding: 25px 25px !important; /* Увеличиваем отступы со всех сторон */
            border: none !important;
            margin-top: 25px !important;
            margin-bottom: 25px !important;
            box-shadow: 0 3px 7px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.2s !important;
            height: auto !important; /* Убедимся, что высота определяется контентом */
            min-height: 80px !important; /* Минимальная высота */
            letter-spacing: 0.5px !important; /* Улучшаем читаемость */
            width: 100% !important; /* Убеждаемся, что кнопка занимает всю ширину */
        }
        /* Стиль для кнопки при наведении */
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        div[data-testid="stButton"] > button:hover,
        button[data-testid="baseButton-primary"]:hover,
        .element-container div[data-testid="stButton"] button:hover,
        .stButton > button:hover {
            background-color: var(--highlight-hover) !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Стили для полей ввода и меток - абсолютный белый цвет в темном режиме */
        .stTextInput label, .stNumberInput label, .stSelectbox label,
        .stCheckbox label, .stRadio label, .stSlider label {
            color: var(--label-color) !important;
        }
        
        /* КРИТИЧНО: ОТКЛЮЧЕН ТЕМНЫЙ РЕЖИМ - ВСЕГДА БЕЛЫЙ ФОН И ЧЕРНЫЙ ТЕКСТ */
        /* ВСЕ ВСЕГДА ЧЕРНЫМ ЦВЕТОМ (кроме специальных элементов с белым текстом, например кнопок) */
        .stApp *, .stApp.dark *, .dark-mode * {
            color: #000000 !important;
        }
        
        /* Принудительно светлый фон для всего приложения */
        body, .stApp, .stApp.dark, [data-theme="dark"], .dark-mode {
            background-color: #FFFFFF !important;
        }
        
        /* Принудительно черный текст для всех элементов интерфейса */
        label, .stTextInput label, p, span, div:not(.stButton *),
        h1, h2, h3, h4, h5, h6, .section-header, [data-testid="stMarkdown"] p,
        .stApp label, .stApp .stTextInput label, .stApp p, .stApp span, .stApp div:not(.stButton *),
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp .section-header,
        .stApp [data-testid="stMarkdown"] p,
        .stApp.dark label, .stApp.dark .stTextInput label, .stApp.dark p, .stApp.dark span,
        .stApp.dark div:not(.stButton *), .stApp.dark h1, .stApp.dark h2, .stApp.dark h3,
        .stApp.dark h4, .stApp.dark h5, .stApp.dark h6, .stApp.dark .section-header,
        .stApp.dark [data-testid="stMarkdown"] p {
            color: #000000 !important;
        }
        
        /* Белый текст только для кнопок */
        [data-testid="stButton"] button[data-testid="baseButton-primary"] {
            color: #FFFFFF !important;
        }
        
        /* Заголовки секций - общие стили - ТЕПЕРЬ ВСЕГДА ЧЕРНЫЙ ТЕКСТ */
        .section-header {
            font-weight: bold;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 10px;
            font-size: 1.1rem;
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }
        
        /* Заголовки секций с высшим приоритетом - всегда черный текст */
        .section-header,
        .stApp .section-header,
        .stApp.dark .section-header,
        .dark-mode .section-header,
        body.dark-mode .section-header,
        [data-theme="dark"] .section-header {
            color: #000000 !important;
            border-bottom-color: #dddddd !important;
            background-color: #FFFFFF !important;
        }
        
        /* Делаем текст в таблицах всегда черным, независимо от режима */
        table td, table th {
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        # Создаем кнопку с усиленным стилем через атрибут style
        if st.button("Рассчитать стоимость", type="primary", use_container_width=True, help="Нажмите для расчета стоимости перголы"):
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