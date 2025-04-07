"""
Компонент для выбора опций перголы
"""
import streamlit as st
from config.pergola_types import PERGOLA_TYPES, LIGHTING_TYPES, ADDITIONAL_OPTIONS
from utils.logger import log_user_action

def get_lamella_options_for_pergola(pergola_type):
    """
    Возвращает список доступных типов ламелей для выбранного типа перголы
    
    Args:
        pergola_type (str): Тип перголы
        
    Returns:
        list: Список доступных типов ламелей
    """
    if pergola_type in PERGOLA_TYPES:
        return PERGOLA_TYPES[pergola_type]["lamella_types"]
    return []

def render_options_form():
    """
    Отображает форму для выбора опций перголы
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    st.subheader("Тип перголы")
    
    # Получаем сохраненные значения из состояния сессии, если они есть
    if 'options' not in st.session_state:
        st.session_state.options = {
            'pergola_type': 'B500NEW',
            'lamella_type': 'B500-20NEW',
            'lamella_step': 200,
            'lighting_type': 'none',
            'additional_options': []
        }
    
    # Создаем форму для выбора опций
    with st.form(key="options_form"):
        # Выбор типа перголы
        pergola_options = list(PERGOLA_TYPES.keys())
        pergola_type = st.selectbox(
            "Тип перголы:", 
            options=pergola_options,
            index=pergola_options.index(st.session_state.options['pergola_type']) if st.session_state.options['pergola_type'] in pergola_options else 0,
            format_func=lambda x: PERGOLA_TYPES[x]['name'],
            help="Выберите тип перголы"
        )
        
        # Отображаем описание выбранного типа перголы
        if pergola_type in PERGOLA_TYPES:
            st.info(PERGOLA_TYPES[pergola_type]['description'])
        
        # Получаем доступные типы ламелей для выбранного типа перголы
        lamella_options = get_lamella_options_for_pergola(pergola_type)
        
        # Выбор типа ламелей
        lamella_type = None
        if pergola_type == "B600":
            st.warning("Для перголы B600 используются стационарные PIR-панели вместо ламелей")
            lamella_type = "B600"  # Для перголы B600 используем фиксированный тип ламелей
        else:
            from config.pergola_types import LAMELLA_TYPES
            lamella_type = st.selectbox(
                "Тип ламелей:", 
                options=lamella_options,
                index=lamella_options.index(st.session_state.options['lamella_type']) if st.session_state.options['lamella_type'] in lamella_options else 0,
                format_func=lambda x: LAMELLA_TYPES[x]['name'] if x in LAMELLA_TYPES else x,
                help="Выберите тип ламелей"
            )
            
            # Отображаем описание выбранного типа ламелей
            if lamella_type in LAMELLA_TYPES:
                st.info(LAMELLA_TYPES[lamella_type]['description'])
        
        # Устанавливаем значение шага ламелей по умолчанию без отображения в интерфейсе
        lamella_step = 200  # значение по умолчанию
        
        # Разделим форму на две колонки для более компактного отображения
        col1, col2 = st.columns(2)
        
        with col1:
            # Выбор типа освещения
            lighting_options = PERGOLA_TYPES[pergola_type]["available_lighting"] if pergola_type in PERGOLA_TYPES else ["none"]
            lighting_type = st.selectbox(
                "Освещение:", 
                options=lighting_options,
                index=lighting_options.index(st.session_state.options['lighting_type']) if st.session_state.options['lighting_type'] in lighting_options else 0,
                format_func=lambda x: LIGHTING_TYPES[x]['name'] if x in LIGHTING_TYPES else x,
                help="Выберите тип освещения"
            )
            
            # Отображаем описание выбранного типа освещения
            if lighting_type in LIGHTING_TYPES:
                st.info(LIGHTING_TYPES[lighting_type]['description'])
        
        with col2:
            # Выбор дополнительных опций
            available_options = PERGOLA_TYPES[pergola_type]["additional_options"] if pergola_type in PERGOLA_TYPES else []
            
            selected_options = []
            for option in available_options:
                if option in ADDITIONAL_OPTIONS:
                    is_selected = st.checkbox(
                        ADDITIONAL_OPTIONS[option]['name'], 
                        value=option in st.session_state.options['additional_options'],
                        help=ADDITIONAL_OPTIONS[option]['description']
                    )
                    if is_selected:
                        selected_options.append(option)
        
        # Кнопка отправки формы
        submit_button = st.form_submit_button(label="Применить опции")
        
        # Если кнопка нажата, обновляем опции
        if submit_button:
            options = {
                'pergola_type': pergola_type,
                'lamella_type': lamella_type,
                'lamella_step': lamella_step,
                'lighting_type': lighting_type,
                'additional_options': selected_options
            }
            
            # Обновляем состояние сессии
            st.session_state.options = options
            
            # Логируем действие пользователя
            log_user_action("Обновлены опции перголы", options)
            
            # Возвращаем выбранные опции
            return options
    
    # Если форма не была отправлена, возвращаем текущие значения
    return st.session_state.options