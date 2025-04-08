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
    st.markdown("""
    <style>
    .dimension-form {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .dimension-label {
        font-weight: bold;
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .dimension-input-container {
        position: relative;
        margin-bottom: 1.5rem;
    }
    .dimension-input {
        width: 100%;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.75rem;
        font-size: 1.2rem;
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
        padding: 1rem;
        font-size: 0.9rem;
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
        font-size: 1.1rem;
        border-radius: 5px;
        padding: 0.75rem;
        border: none;
        width: 100%;
        margin-top: 1rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    .calculate-button:hover {
        background-color: #0055aa;
    }
    .result-block {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .result-label {
        font-weight: bold;
        font-size: 1.2rem;
        color: #333;
    }
    .result-value {
        font-weight: bold;
        font-size: 1.5rem;
        color: #0066cc;
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
    
    # Создаем блок для размеров
    st.markdown("<div style='background-color: #f8f9fa; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>", unsafe_allow_html=True)
    
    # Заголовок блока
    st.markdown("<h3 style='margin-top: 0; margin-bottom: 1rem; color: #333;'>Размеры перголы</h3>", unsafe_allow_html=True)
    
    # Используем новый дизайн формы ввода размеров
    st.markdown('<div class="dimension-form">', unsafe_allow_html=True)
    
    # Ширина
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
    
    # Вынос
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
    
    # Высота
    st.markdown('<div class="dimension-label">Высота</div>', unsafe_allow_html=True)
    st.markdown('<div class="dimension-input-container">', unsafe_allow_html=True)
    st.text_input(
        "Высота перголы",
        value="3,0 м (по умолчанию)",
        disabled=True,
        key="height_input",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Конфигурация - добавляем кнопки выбора типа перголы
    st.markdown('<div class="dimension-label">Конфигурация</div>', unsafe_allow_html=True)
    
    # Используем колонки для ровного расположения кнопок
    conf_cols = st.columns(3)
    with conf_cols[0]:
        st.button("Поворотные\nламели", key="btn_config_b500", use_container_width=True)
    with conf_cols[1]:
        st.button("Сдвижные\nламели", key="btn_config_b700", use_container_width=True)
    with conf_cols[2]:
        st.button("Стационарные\nпанели", key="btn_config_b600", use_container_width=True)
    
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