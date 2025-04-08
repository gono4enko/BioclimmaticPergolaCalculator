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
    # Добавляем CSS для стилизации формы размеров
    st.markdown("""
    <style>
    .dimension-input {
        margin-bottom: 0.5rem;
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    .dimension-input label {
        font-weight: bold;
        font-size: 1.1rem;
        color: #333;
    }
    .dimension-input input {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.5rem;
        font-size: 1.1rem;
    }
    .dimension-unit {
        background-color: #f0f2f6;
        color: #333;
        padding: 0.3rem 0.6rem;
        border-radius: 5px;
        margin-left: 0.5rem;
        font-weight: bold;
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
    
    # Основные размеры - без использования формы для мгновенного обновления
    # Используем более узкий контейнер с центрированием
    _, center_container, _ = st.columns([1, 6, 1])
    with center_container:
        col1, col2 = st.columns(2)
    
    with center_container:
        with col1:
            width = st.number_input(
                "Ширина (м):", 
                min_value=1.5, 
                max_value=13.5, 
                value=st.session_state.dimensions['width'],
                step=0.1, 
                format="%.1f",
                key="width_input",
                help="Ширина перголы в метрах (от 1.5 до 13.5 м)"
            )
        
        with col2:
            length = st.number_input(
                "Вынос (м):", 
                min_value=1.0, 
                max_value=8.0, 
                value=st.session_state.dimensions['length'],
                step=0.1, 
                format="%.1f",
                key="length_input",
                help="Вынос перголы в метрах (от 1.0 до 8.0 м)"
            )
        
        # Фиксированная высота
        st.markdown("<div style='background-color: #e6f3ff; border-radius: 5px; padding: 0.7rem; margin-top: 0.5rem;'><b>Высота:</b> 3.0 м (стандартная)</div>", unsafe_allow_html=True)
        
        # Площадь перголы (информационно)
        area = round(width * length, 2)
        st.markdown(f"<div style='background-color: #f0f0f0; border-radius: 5px; padding: 0.7rem; margin-top: 0.5rem;'><b>Площадь перголы:</b> {area} м²</div>", unsafe_allow_html=True)
    
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