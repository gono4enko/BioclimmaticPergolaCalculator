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
    st.subheader("Размеры перголы")
    
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
    
    # Создаем форму для ввода размеров
    with st.form(key="dimensions_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            width = st.number_input(
                "Ширина (м):", 
                min_value=1.5, 
                max_value=13.5, 
                value=st.session_state.dimensions['width'],
                step=0.1, 
                format="%.3f",
                help="Ширина перголы в метрах (от 1.5 до 13.5 м)"
            )
            
            # Отображаем информацию о фиксированной высоте
            st.info("Высота: 3.0 м (стандартная)")
            # Сохраняем фиксированную высоту
            height = 3.0
        
        with col2:
            length = st.number_input(
                "Вынос (м):", 
                min_value=1.0, 
                max_value=8.0, 
                value=st.session_state.dimensions['length'],
                step=0.1, 
                format="%.3f",
                help="Вынос перголы в метрах (от 1.0 до 8.0 м)"
            )
            
            # Добавим пустое место для выравнивания с левой колонкой
            st.text("")
        
        # Кнопка отправки формы
        submit_button = st.form_submit_button(label="Применить размеры")
        
        # Если кнопка нажата, обновляем размеры
        if submit_button:
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
            
            # Обновляем состояние сессии
            st.session_state.dimensions = dimensions
            
            # Логируем действие пользователя
            log_user_action("Обновлены размеры перголы", dimensions)
            
            # Возвращаем введенные размеры
            return dimensions
    
    # Если форма не была отправлена, возвращаем текущие значения
    return st.session_state.dimensions