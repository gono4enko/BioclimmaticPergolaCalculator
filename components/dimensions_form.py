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
            'width': 3000,
            'length': 4000,
            'height': 3000  # Стандартная высота 3000 мм
        }
    
    # Фиксированная высота 3000 мм
    if st.session_state.dimensions['height'] != 3000:
        st.session_state.dimensions['height'] = 3000
    
    # Создаем форму для ввода размеров
    with st.form(key="dimensions_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            width = st.number_input(
                "Ширина (мм):", 
                min_value=1000, 
                max_value=7000, 
                value=st.session_state.dimensions['width'],
                step=100, 
                help="Ширина перголы в миллиметрах (от 1000 до 7000 мм)"
            )
            
            # Отображаем информацию о фиксированной высоте
            st.info("Высота: 3000 мм (стандартная)")
            # Сохраняем фиксированную высоту
            height = 3000
        
        with col2:
            length = st.number_input(
                "Длина (мм):", 
                min_value=1000, 
                max_value=7000, 
                value=st.session_state.dimensions['length'],
                step=100, 
                help="Длина перголы в миллиметрах (от 1000 до 7000 мм)"
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