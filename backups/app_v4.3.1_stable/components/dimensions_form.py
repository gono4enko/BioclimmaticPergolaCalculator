"""
Модуль для отображения формы ввода размеров перголы.
"""
import streamlit as st

def render_dimensions_form():
    """
    Отображает форму для ввода размеров перголы
    
    Returns:
        dict: Словарь с введенными размерами
    """
    st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: #0066cc; font-size: 2.0rem; font-weight: 600; margin-bottom: 1rem;">Размеры перголы</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Создаем два колонки для размеров
    col1, col2 = st.columns(2)
    
    with col1:
        width = st.number_input(
            "Ширина перголы (метры):",
            min_value=2.5,
            max_value=8.0,
            value=3.0,
            step=0.5,
            format="%.1f",
            help="Ширина перголы в метрах (от 2.5 до 8.0 метров)"
        )
    
    with col2:
        length = st.number_input(
            "Вынос перголы (метры):",
            min_value=2.5,
            max_value=13.5,
            value=4.0,
            step=0.5,
            format="%.1f",
            help="Вынос (длина) перголы в метрах (от 2.5 до 13.5 метров)"
        )
    
    # Возвращаем введенные размеры как словарь
    return {
        "width": width,
        "length": length
    }