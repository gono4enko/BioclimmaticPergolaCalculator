"""
Компонент для выбора опций перголы
"""
import streamlit as st
from config.pergola_types import (
    PERGOLA_TYPES,
    LAMELLA_TYPES,
    INSTALLATION_TYPES,
    LIGHTING_TYPES,
    ADDITIONAL_SYSTEMS,
    PERGOLA_LAMELLA_COMPATIBILITY
)
from utils.validation import validate_pergola_config
from utils.logger import log_user_action

def get_lamella_options_for_pergola(pergola_type):
    """
    Возвращает список доступных типов ламелей для выбранного типа перголы
    
    Args:
        pergola_type (str): Тип перголы
        
    Returns:
        list: Список доступных типов ламелей
    """
    return PERGOLA_LAMELLA_COMPATIBILITY.get(pergola_type, [])

def render_options_form():
    """
    Отображает форму для выбора опций перголы
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    st.subheader("Шаг 2: Выберите конфигурацию перголы")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Выбор типа перголы
        pergola_options = list(PERGOLA_TYPES.keys())
        pergola_names = [PERGOLA_TYPES[key]['name'] for key in pergola_options]
        pergola_index = 0  # По умолчанию B500NEW
        
        if 'pergola_type' in st.session_state:
            try:
                pergola_index = pergola_options.index(st.session_state['pergola_type'])
            except ValueError:
                pergola_index = 0
        
        pergola_name = st.selectbox(
            "Тип перголы:",
            pergola_names,
            index=pergola_index,
            help="Выберите тип перголы"
        )
        
        # Определяем выбранный ключ типа перголы
        pergola_type = pergola_options[pergola_names.index(pergola_name)]
        
        # Сохраняем выбранный тип перголы в состоянии сессии
        if 'pergola_type' not in st.session_state or st.session_state['pergola_type'] != pergola_type:
            st.session_state['pergola_type'] = pergola_type
            if 'lamella_type' in st.session_state:
                del st.session_state['lamella_type']
        
        # Выбор типа ламелей (зависит от выбранного типа перголы)
        available_lamellas = get_lamella_options_for_pergola(pergola_type)
        lamella_names = [LAMELLA_TYPES[key]['name'] for key in available_lamellas]
        
        lamella_index = 0
        if 'lamella_type' in st.session_state and st.session_state['lamella_type'] in available_lamellas:
            try:
                lamella_index = available_lamellas.index(st.session_state['lamella_type'])
            except ValueError:
                lamella_index = 0
        
        lamella_name = st.selectbox(
            "Тип ламели:",
            lamella_names,
            index=lamella_index,
            help="Выберите тип ламели для перголы"
        )
        
        # Определяем выбранный ключ типа ламели
        lamella_type = available_lamellas[lamella_names.index(lamella_name)]
        
        # Сохраняем выбранный тип ламели в состоянии сессии
        if 'lamella_type' not in st.session_state or st.session_state['lamella_type'] != lamella_type:
            st.session_state['lamella_type'] = lamella_type
        
        # Выбор типа монтажа
        installation_options = list(INSTALLATION_TYPES.keys())
        installation_names = [INSTALLATION_TYPES[key]['name'] for key in installation_options]
        
        installation_name = st.selectbox(
            "Тип монтажа:",
            installation_names,
            index=0,
            help="Выберите тип монтажа перголы"
        )
        
        # Определяем выбранный ключ типа монтажа
        installation_type = installation_options[installation_names.index(installation_name)]
    
    with col2:
        # Выбор типа освещения
        lighting_options = list(LIGHTING_TYPES.keys())
        lighting_names = [LIGHTING_TYPES[key]['name'] for key in lighting_options]
        
        lighting_name = st.selectbox(
            "Освещение:",
            lighting_names,
            index=0,
            help="Выберите тип освещения для перголы"
        )
        
        # Определяем выбранный ключ типа освещения
        lighting_type = lighting_options[lighting_names.index(lighting_name)]
        
        # Выбор типа управления
        control_options = ["manual_control", "motor_control", "smart_control"]
        control_names = {
            "manual_control": "Ручное управление",
            "motor_control": "Моторизованное управление",
            "smart_control": "Умное управление (пульт, датчики)"
        }
        
        control_name = st.selectbox(
            "Тип управления:",
            list(control_names.values()),
            index=1,
            help="Выберите тип управления ламелями"
        )
        
        # Определяем выбранный ключ типа управления
        control_type = [k for k, v in control_names.items() if v == control_name][0]
        
        # Выбор типа окраски
        color_options = ["standard_color", "custom_color"]
        color_names = {
            "standard_color": "Стандартный цвет",
            "custom_color": "Нестандартный цвет (RAL)"
        }
        
        color_name = st.selectbox(
            "Цвет конструкции:",
            list(color_names.values()),
            index=0,
            help="Выберите цвет для конструкции перголы"
        )
        
        # Определяем выбранный ключ типа окраски
        color_type = [k for k, v in color_names.items() if v == color_name][0]

    # Выбор дополнительных систем
    st.subheader("Дополнительные системы")
    
    additional_systems_options = {}
    for key, data in ADDITIONAL_SYSTEMS.items():
        additional_systems_options[key] = data['name']
    
    selected_additional_systems = st.multiselect(
        "Выберите дополнительные системы:",
        options=list(additional_systems_options.keys()),
        format_func=lambda x: additional_systems_options[x],
        help="Выберите дополнительные системы для установки на перголу"
    )
    
    # Проверяем валидность конфигурации
    if 'width' in st.session_state and 'length' in st.session_state:
        width = st.session_state.get('width', 3000)
        length = st.session_state.get('length', 4000)
        validation_error = validate_pergola_config(pergola_type, lamella_type, width, length)
        
        if validation_error:
            st.warning(validation_error)
    
    # Собираем все выбранные опции в словарь
    options = {
        "pergola_type": pergola_type,
        "lamella_type": lamella_type,
        "installation_type": installation_type,
        "lighting_type": lighting_type,
        "control_type": control_type,
        "color_type": color_type,
        "additional_systems": selected_additional_systems
    }
    
    # Логируем действие пользователя
    log_user_action("Выбор опций перголы", options)
    
    return options
