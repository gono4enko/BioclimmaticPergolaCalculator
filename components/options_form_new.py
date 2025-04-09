"""
Компонент для выбора опций перголы - НОВАЯ ВЕРСИЯ
Полностью переписан для решения проблем с синей заливкой
"""
import streamlit as st
from config.pergola_types import PERGOLA_TYPES, LAMELLA_TYPES, LIGHTING_TYPES
from force_white_background import fix_blue_tiles

def render_options_form():
    """
    Отображает форму для выбора опций перголы с плиточным дизайном
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    # Применяем фикс для удаления синей заливки
    fix_blue_tiles()
    
    # Инициализируем состояние опций, если оно не существует
    if 'options' not in st.session_state:
        st.session_state.options = {
            'pergola_type': 'B500NEW',  # По умолчанию
            'lamella_type': 'standard_200',  # По умолчанию
            'lighting': 'none',  # По умолчанию без подсветки
            'drive_type': 'auto',  # Автоматический выбор привода
            'additional_options': [],  # Без доп. опций по умолчанию
        }
    
    # Создаем словарь для хранения выбранных опций
    options = st.session_state.options.copy()
    
    # Отображаем заголовок секции
    st.markdown('<div class="section-header">Тип перголы</div>', unsafe_allow_html=True)
    
    # Получаем текущие значения из состояния
    pergola_type = options.get('pergola_type', 'B500NEW')
    
    # Отображаем плитки для выбора типа перголы в 3 колонки
    pergola_options = list(PERGOLA_TYPES.keys())
    cols = st.columns(3)
    
    # Для каждого типа перголы создаем собственный HTML-элемент с белой заливкой
    for i, p_type in enumerate(pergola_options):
        with cols[i % 3]:
            # Получаем информацию о типе перголы
            pergola_name = PERGOLA_TYPES[p_type]['name']
            pergola_desc = PERGOLA_TYPES[p_type].get('short_description', 'Стандартная пергола')
            
            # Определяем, выбран ли текущий тип перголы
            is_selected = p_type == pergola_type
            
            # Создаем HTML-кнопку с контролем стиля
            if is_selected:
                # Для выбранной опции с галочкой и синей рамкой
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:2px solid #0066cc; border-radius:8px; 
                    padding:12px 8px; margin:5px 0; text-align:center;">
                    <div style="font-weight:bold; color:#000000; font-size:1.1rem;">{pergola_name} ✓</div>
                    <div style="color:#000000; font-size:0.9rem; margin-top:5px;">{pergola_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Для невыбранной опции
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:1px solid #dddddd; border-radius:8px; 
                    padding:12px 8px; margin:5px 0; text-align:center;">
                    <div style="font-weight:500; color:#000000; font-size:1.1rem;">{pergola_name}</div>
                    <div style="color:#555555; font-size:0.9rem; margin-top:5px;">{pergola_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Добавляем прозрачную кнопку поверх HTML-контента
                # Используем unique_key для предотвращения конфликтов ключей
                unique_key = f"btn_pergola_{p_type}_{i}"
                if st.button(f"Выбрать {pergola_name}", key=unique_key, 
                             help=f"{pergola_desc}"):
                    options['pergola_type'] = p_type
                    
                    # Обновляем тип ламелей в зависимости от типа перголы
                    if p_type == 'B600':
                        options['lamella_type'] = 'pir_sandwich'
                    elif p_type == 'B500NEW' and options['lamella_type'] not in ['standard_200', 'standard_250']:
                        options['lamella_type'] = 'standard_200'
                    elif p_type == 'B700NEW' and options['lamella_type'] not in ['movable_200', 'movable_250']:
                        options['lamella_type'] = 'movable_250'
                    
                    # Сохраняем обновленные опции
                    st.session_state.options = options
                    st.rerun()
    
    # Отображаем заголовок секции ламелей
    st.markdown('<div class="section-header">Тип ламелей</div>', unsafe_allow_html=True)
    
    # Получаем текущие значения
    lamella_type = options.get('lamella_type', 'standard_200')
    
    # Определяем доступные типы ламелей в зависимости от выбранного типа перголы
    if pergola_type == 'B500NEW':
        lamella_options = ['standard_200', 'standard_250']
    elif pergola_type == 'B700NEW':
        lamella_options = ['movable_200', 'movable_250']
    else:  # B600
        lamella_options = ['pir_sandwich']
    
    # Отображаем плитки для выбора типа ламелей
    cols = st.columns(len(lamella_options))
    
    # Для каждого типа ламелей создаем собственный HTML-элемент с белой заливкой
    for i, l_type in enumerate(lamella_options):
        with cols[i]:
            # Получаем информацию о типе ламелей
            lamella_name = LAMELLA_TYPES[l_type]['name']
            lamella_desc = LAMELLA_TYPES[l_type].get('description', '')
            
            # Определяем, выбран ли текущий тип ламелей
            is_selected = l_type == lamella_type
            
            # Создаем HTML-кнопку с контролем стиля
            if is_selected:
                # Для выбранной опции с галочкой и синей рамкой
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:2px solid #0066cc; border-radius:8px; 
                    padding:12px 8px; margin:5px 0; text-align:center;">
                    <div style="font-weight:bold; color:#000000; font-size:1.1rem;">{lamella_name} ✓</div>
                    <div style="color:#000000; font-size:0.9rem; margin-top:5px;">{lamella_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Для невыбранной опции
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:1px solid #dddddd; border-radius:8px; 
                    padding:12px 8px; margin:5px 0; text-align:center;">
                    <div style="font-weight:500; color:#000000; font-size:1.1rem;">{lamella_name}</div>
                    <div style="color:#555555; font-size:0.9rem; margin-top:5px;">{lamella_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Добавляем прозрачную кнопку поверх HTML-контента
                # Используем unique_key для предотвращения конфликтов ключей
                unique_key = f"btn_lamella_{l_type}_{i}"
                if st.button(f"Выбрать {lamella_name}", key=unique_key, 
                            help=f"{lamella_desc}"):
                    options['lamella_type'] = l_type
                    st.session_state.options = options
                    st.rerun()
    
    # Отображаем заголовок секции освещения (единая строка заголовка на всю ширину)
    st.markdown('<div class="section-header">Подсветка</div>', unsafe_allow_html=True)
    
    # Получаем текущее значение освещения
    lighting = options.get('lighting', 'none')
    
    # Отображаем плитки для выбора типа освещения в 4 колонки
    lighting_options = list(LIGHTING_TYPES.keys())
    cols = st.columns(len(lighting_options))
    
    # Для каждого типа освещения создаем собственный HTML-элемент
    for i, l_type in enumerate(lighting_options):
        with cols[i]:
            # Получаем информацию о типе освещения
            light_name = LIGHTING_TYPES[l_type]['name']
            light_desc = LIGHTING_TYPES[l_type].get('description', '')
            
            # Определяем, выбран ли текущий тип освещения
            is_selected = l_type == lighting
            
            # Создаем HTML-кнопку с контролем стиля
            if is_selected:
                # Для выбранной опции с галочкой и синей рамкой
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:2px solid #0066cc; border-radius:8px; 
                    padding:12px 8px; margin:2px 0; text-align:center;">
                    <div style="font-weight:bold; color:#000000; font-size:1.0rem;">{light_name} ✓</div>
                    <div style="color:#000000; font-size:0.8rem; margin-top:5px;">{light_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Для невыбранной опции
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:1px solid #dddddd; border-radius:8px; 
                    padding:12px 8px; margin:2px 0; text-align:center;">
                    <div style="font-weight:500; color:#000000; font-size:1.0rem;">{light_name}</div>
                    <div style="color:#555555; font-size:0.8rem; margin-top:5px;">{light_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Добавляем прозрачную кнопку поверх HTML-контента
                if st.button(f"Выбрать {light_name}", key=f"btn_light_{l_type}", 
                            help=f"{light_desc}"):
                    options['lighting'] = l_type
                    st.session_state.options = options
                    st.rerun()
    
    # Добавляем скрытое поле для автоматического выбора типа привода
    options['drive_type'] = 'auto'  # Всегда автоматический выбор
    
    # Возвращаем обновленные опции
    return options