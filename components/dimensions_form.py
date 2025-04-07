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
    st.subheader("Шаг 1: Укажите размеры перголы")
    
    col1, col2 = st.columns(2)
    
    with col1:
        width = st.number_input(
            "Ширина (мм):",
            min_value=2000,
            max_value=7000,
            value=3000,
            step=100,
            help="Минимально: 2000 мм, максимально: 7000 мм"
        )
        
        length = st.number_input(
            "Длина (мм):",
            min_value=2000,
            max_value=8000,
            value=4000,
            step=100,
            help="Минимально: 2000 мм, максимально: 8000 мм"
        )
        
        height = st.number_input(
            "Высота колонн (мм):",
            min_value=2000,
            max_value=7000,
            value=2400,
            step=100,
            help="Минимально: 2000 мм, максимально: 7000 мм"
        )
    
    with col2:
        # Отображаем информацию о текущей площади
        area = (width / 1000) * (length / 1000)
        perimeter = 2 * ((width / 1000) + (length / 1000))
        
        st.info(f"""
        **Параметры конструкции:**
        - Площадь: **{area:.2f} м²**
        - Периметр: **{perimeter:.2f} м**
        
        **Рекомендации:**
        - Максимальный пролет между колоннами: до 7 м
        - Максимальный вынос: до 8 м
        - Максимальная высота колонн: до 7 м
        """)
        
        # Визуализация перголы (простая схема)
        st.markdown("""
        **Схема перголы:**
        ```
        ┌───────────────┐
        │               │
        │               │ 
        │      ↑        │
        │      │        │
        │    Длина      │
        │      │        │
        │      ↓        │
        │               │
        │               │
        └───────────────┘
          ←  Ширина  →
        ```
        """)
    
    dimensions = {
        "width": width,
        "length": length,
        "height": height
    }
    
    # Валидируем размеры и выводим предупреждение при необходимости
    validation_error = validate_dimensions(dimensions)
    if validation_error:
        st.warning(validation_error)
    
    # Логируем действие пользователя
    log_user_action("Ввод размеров перголы", dimensions)
    
    return dimensions
