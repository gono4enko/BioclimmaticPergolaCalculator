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
    
    # Создаем компактный блок для размеров
    st.markdown("<div style='background-color: #f8f9fa; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.6rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);'>", unsafe_allow_html=True)
    
    # Заголовок блока (ещё более компактный)
    st.markdown("<h3 style='margin-top: 0; margin-bottom: 0.3rem; color: #333; font-size: 1.1rem;'>Размеры перголы</h3>", unsafe_allow_html=True)
    
    # Используем более компактный дизайн формы ввода размеров
    st.markdown('<div class="dimension-form" style="padding: 0.4rem;">', unsafe_allow_html=True)
    
    # Создаем два ряда по два элемента для более компактного отображения
    row1_cols = st.columns(2)
    
    # Первый ряд: Ширина и Вынос
    with row1_cols[0]:
        st.markdown('<div class="dimension-label">Ширина</div>', unsafe_allow_html=True)
        st.markdown('<div class="dimension-input-container">', unsafe_allow_html=True)
        width = st.number_input(
            "Ширина перголы", 
            min_value=1.5, 
            max_value=13.5, 
            value=st.session_state.dimensions['width'],
            step=0.1, 
            format="%.1f",
            key="width_input",
            label_visibility="collapsed"
        )
        st.markdown(f'<div class="dimension-unit">м</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row1_cols[1]:
        st.markdown('<div class="dimension-label">Вынос</div>', unsafe_allow_html=True)
        st.markdown('<div class="dimension-input-container">', unsafe_allow_html=True)
        length = st.number_input(
            "Вынос перголы", 
            min_value=1.0, 
            max_value=8.0, 
            value=st.session_state.dimensions['length'],
            step=0.1, 
            format="%.1f",
            key="length_input",
            label_visibility="collapsed"
        )
        st.markdown(f'<div class="dimension-unit">м</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Только высота, убираем дублирующуюся конфигурацию
    st.markdown('<div class="dimension-label">Высота</div>', unsafe_allow_html=True)
    st.markdown('<div class="dimension-input-container">', unsafe_allow_html=True)
    st.text_input(
        "Высота перголы",
        value="3,0 м",
        disabled=True,
        key="height_input",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Закрываем блок размеров
    st.markdown("</div>", unsafe_allow_html=True)
    
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