"""
Компонент для сбора информации о размерах перголы
"""
import streamlit as st
from utils.validation import validate_dimensions
from utils.logger import log_user_action

def render_dimensions_form():
    """
    Отображает форму для ввода размеров перголы
    
    Returns:
        dict: Словарь с введенными размерами
    """
    # Добавляем CSS для стилизации формы размеров в соответствии с предоставленным дизайном
    # Адаптивная и компактная версия
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Мобильные устройства */
        .dimension-form {
            padding: 0.8rem;
        }
        .dimension-input-container {
            margin-bottom: 0.8rem;
        }
        .dimension-label {
            font-size: 0.9rem;
            margin-bottom: 0.3rem;
        }
        input[type="number"] {
            padding: 0.4rem !important;
            font-size: 0.9rem !important;
        }
        button {
            padding: 0.4rem !important;
            font-size: 0.8rem !important;
        }
        .stButton button {
            min-height: auto !important;
            line-height: 1.2 !important;
        }
    }
    
    /* Универсальные стили */
    .dimension-form {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .dimension-label {
        font-weight: 600;
        font-size: 0.95rem;
        color: #333;
        margin-bottom: 0.3rem;
    }
    .dimension-input-container {
        position: relative;
        margin-bottom: 0.8rem;
    }
    .dimension-input {
        width: 100%;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.5rem;
        font-size: 1rem;
        background-color: white;
    }
    .dimension-unit {
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: #333;
        font-weight: bold;
    }
    .config-button {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.6rem;
        font-size: 0.85rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        height: 100%;
    }
    .config-button:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }
    .config-button.selected {
        background-color: #e6f3ff;
        border-color: #0066cc;
        color: #0066cc;
        font-weight: bold;
    }
    .calculate-button {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        font-size: 1rem;
        border-radius: 5px;
        padding: 0.6rem;
        border: none;
        width: 100%;
        margin-top: 0.8rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    .calculate-button:hover {
        background-color: #0055aa;
    }
    .result-block {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .result-label {
        font-weight: bold;
        font-size: 1.1rem;
        color: #333;
    }
    .result-value {
        font-weight: bold;
        font-size: 1.3rem;
        color: #0066cc;
    }
    .stButton button {
        min-height: 0 !important;
        line-height: 1.2 !important;
        padding: 8px 4px !important;
        white-space: pre-wrap !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Получаем сохраненные значения из состояния сессии, если они есть
    if 'dimensions' not in st.session_state:
        st.session_state.dimensions = {
            'width': 3.0,    # 3 метра
            'length': 4.0,   # 4 метра
            'height': 3.0    # Стандартная высота 3 метра
        }
    
    # Фиксированная высота 3 метра
    if st.session_state.dimensions['height'] != 3.0:
        st.session_state.dimensions['height'] = 3.0
    
    # Создаем блок для размеров в новом дизайне с минимальными отступами
    st.markdown('<div class="result-card" style="margin-bottom: 0px; margin-top: 0px; padding-top: 2px; padding-bottom: 2px;">', unsafe_allow_html=True)
    
    # Заголовок блока (четкий и читаемый)
    st.markdown('<div class="section-header" style="color: #FFFFFF !important;">Размеры перголы</div>', unsafe_allow_html=True)
    
    # Используем форму ввода размеров с более крупными элементами
    row_cols = st.columns([1, 1, 1])
    
    # Ширина
    with row_cols[0]:
        st.markdown('<div style="font-weight:500; margin-bottom:5px; font-size:1rem; text-align:center; color: #FFFFFF !important;">Ширина</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            width = st.number_input(
                "Ширина перголы", 
                min_value=1.5, 
                max_value=13.5, 
                value=st.session_state.dimensions['width'],
                step=0.5, 
                format="%.1f",
                key="width_input",
                label_visibility="collapsed"
            )
            # Добавляем CSS для центрирования текста в поле ввода
            st.markdown("""
            <style>
            div[data-testid="stNumberInput"] input {
                text-align: center !important;
            }
            </style>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="padding-top:8px; font-size:0.9rem;">м</div>', unsafe_allow_html=True)
    
    # Вынос (длина)
    with row_cols[1]:
        st.markdown('<div style="font-weight:500; margin-bottom:5px; font-size:1rem; text-align:center; color: #FFFFFF !important;">Вынос</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            length = st.number_input(
                "Вынос перголы", 
                min_value=1.0, 
                max_value=8.0, 
                value=st.session_state.dimensions['length'],
                step=0.5, 
                format="%.1f",
                key="length_input",
                label_visibility="collapsed"
            )
        with col2:
            st.markdown('<div style="padding-top:8px; font-size:0.9rem;">м</div>', unsafe_allow_html=True)
    
    # Высота (фиксированная)
    with row_cols[2]:
        st.markdown('<div style="font-weight:500; margin-bottom:5px; font-size:1rem; text-align:center; color: #FFFFFF !important;">Высота (фикс.)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text_input(
                "Высота перголы",
                value="3,0",
                disabled=True,
                key="height_input",
                label_visibility="collapsed"
            )
            # Добавляем CSS для центрирования текста в поле ввода
            st.markdown("""
            <style>
            div[data-testid="stTextInput"] input {
                text-align: center !important;
            }
            </style>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="padding-top:8px; font-size:0.9rem;">м</div>', unsafe_allow_html=True)
    
    # Закрываем блок размеров
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Сохраняем фиксированную высоту
    height = 3.0
    
    # Обновляем размеры при изменении входных данных (без кнопки)
    dimensions = {
        'width': width,
        'length': length,
        'height': height
    }
    
    # Валидация размеров
    error = validate_dimensions(dimensions)
    if error:
        st.error(error)
        log_user_action("Ошибка валидации размеров", dimensions)
        return None
    
    # Обновляем состояние сессии только если размеры изменились
    if (st.session_state.dimensions['width'] != width or 
        st.session_state.dimensions['length'] != length):
        st.session_state.dimensions = dimensions
        log_user_action("Обновлены размеры перголы", dimensions)
    
    # Возвращаем введенные размеры
    return st.session_state.dimensions