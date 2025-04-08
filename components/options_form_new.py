"""
Компонент для выбора опций перголы - НОВАЯ ВЕРСИЯ
Полностью переписан для решения проблем с синей заливкой
"""
import streamlit as st
from utils.logger import log_user_action
from config.pergola_types import PERGOLA_TYPES, LAMELLA_TYPES, LIGHTING_TYPES

def render_options_form():
    """
    Отображает форму для выбора опций перголы с плиточным дизайном
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    # Инициализация состояния сессии при первой загрузке    
    if 'options' not in st.session_state:
        st.session_state.options = {
            'pergola_type': 'b500',
            'lamella_type': '200',
            'lamella_step': 200,
            'lighting_type': 'none',
            'additional_options': []
        }
    
    # ВАЖНО: Исключаем возможность использования любых Streamlit-виджетов с синей заливкой
    # Вместо этого принудительно применяем минимальные отступы
    # Используем жесткие CSS-правила для удаления всех отступов
    st.markdown("""
    <style>
    /* Глобальное обнуление всех отступов */
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Удаляем все синие заливки и индикаторы */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Скрываем скрытые поля ввода полностью */
    [data-testid="stTextInput"] {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        width: 0 !important;
    }
    
    [data-testid="stTextInput"] > div > div > input {
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        position: absolute !important;
    }
    
    /* Скрываем лейблы скрытых полей */
    [data-testid="stTextInput"] label {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # ТИП ПЕРГОЛЫ
    st.subheader("Тип перголы")
    
    # Получаем текущее значение
    pergola_type = st.session_state.options['pergola_type']
    
    # Создаем плитки перголы с помощью HTML
    cols = st.columns(3)
    pergola_options = list(PERGOLA_TYPES.keys())
    
    # Для каждого типа перголы создаем собственный HTML-элемент
    for i, p_type in enumerate(pergola_options):
        with cols[i % 3]:
            # Определяем, выбран ли текущий тип перголы
            is_selected = p_type == pergola_type
            border_style = "1px solid #0066cc" if is_selected else "1px solid #dddddd"
            check_mark = " ✓" if is_selected else ""
            
            # Создаём HTML-кнопку вместо Streamlit-компонента
            st.markdown(f"""
            <div style="border:{border_style}; background-color:white; border-radius:8px; 
                padding:10px; margin:2px 0; cursor:pointer; text-align:center;"
                onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: '{p_type}', dataType: 'string', componentIndex: '_pergola_{p_type}'}},'*')">
                <div style="font-weight:bold; color:#000000; font-size:1rem;">
                    {PERGOLA_TYPES[p_type]['name']}{check_mark}
                </div>
                <div style="color:#000000; font-size:0.8rem; margin-top:2px;">
                    {PERGOLA_TYPES[p_type]['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Добавляем скрытое поле для обработки выбора через JavaScript
            hidden_input = st.text_input("", key=f"_pergola_{p_type}", 
                                      label_visibility="collapsed")
            if hidden_input == p_type:
                st.session_state.options['pergola_type'] = p_type
                # Сбрасываем тип ламелей если сменился тип перголы
                # Просто используем первый доступный тип для нового типа перголы
                if p_type in PERGOLA_TYPES and PERGOLA_TYPES[p_type]['available_lamella']:
                    st.session_state.options['lamella_type'] = PERGOLA_TYPES[p_type]['available_lamella'][0]
                st.rerun()
    
    # ТИП ЛАМЕЛЕЙ
    st.subheader("Тип ламелей")
    
    # Получаем текущий тип ламелей
    lamella_type = st.session_state.options['lamella_type']
    
    # Доступные типы ламелей для выбранного типа перголы
    available_lamella = PERGOLA_TYPES[pergola_type]['available_lamella'] if pergola_type in PERGOLA_TYPES else []
    
    # Создаем колонки для типов ламелей
    cols = st.columns(len(available_lamella))
    
    # Для каждого типа ламели создаем собственный HTML-элемент
    for i, lam_type in enumerate(available_lamella):
        with cols[i]:
            # Определяем, выбран ли текущий тип ламели
            is_selected = lam_type == lamella_type
            border_style = "1px solid #0066cc" if is_selected else "1px solid #dddddd"
            check_mark = " ✓" if is_selected else ""
            
            # Получаем информацию о ламели
            lamella_name = LAMELLA_TYPES[lam_type]['name'] if lam_type in LAMELLA_TYPES else lam_type
            lamella_desc = LAMELLA_TYPES[lam_type]['description'] if lam_type in LAMELLA_TYPES else ""
            
            # Создаём HTML-кнопку вместо Streamlit-компонента
            st.markdown(f"""
            <div style="border:{border_style}; background-color:white; border-radius:5px; 
                padding:5px; margin:2px 0; cursor:pointer; text-align:center;"
                onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: '{lam_type}', dataType: 'string', componentIndex: '_lamella_{lam_type}'}},'*')">
                <div style="font-weight:bold; color:#000000; font-size:0.9rem;">
                    {lamella_name}{check_mark}
                </div>
                <div style="color:#000000; font-size:0.7rem;">
                    {lamella_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Добавляем скрытое поле для обработки выбора через JavaScript
            hidden_input = st.text_input("", key=f"_lamella_{lam_type}", 
                                      label_visibility="collapsed")
            if hidden_input == lam_type:
                st.session_state.options['lamella_type'] = lam_type
                
                # Устанавливаем шаг ламелей в зависимости от типа
                if lam_type == "200":
                    lamella_step = 200  # Для ламелей B500-20NEW и B700-20NEW
                else:
                    lamella_step = 250  # Для ламелей B500-25NEW и B700-25NEW
                
                st.session_state.options['lamella_step'] = lamella_step
                st.rerun()
    
    # ПОДСВЕТКА (LED по периметру)
    st.subheader("Подсветка (LED по периметру)")
    
    # Доступные типы освещения для выбранного типа перголы - убираем 'none'
    lighting_options = [opt for opt in PERGOLA_TYPES[pergola_type]["available_lighting"] if opt != "none"] if pergola_type in PERGOLA_TYPES else []
    selected_lighting = st.session_state.options['lighting_type']
    
    # Создаем колонки для типов освещения
    cols = st.columns(len(lighting_options))
    
    # Для каждого типа освещения создаем собственный HTML-элемент
    for i, light_type in enumerate(lighting_options):
        with cols[i]:
            # Получаем информацию о типе освещения с короткими названиями
            if light_type == "led":
                light_name = "Сверхъяркая LED"
                light_desc = "белый свет"
            elif light_type == "rgb":
                light_name = "RGB подсветка"
                light_desc = "цветная"
            elif light_type == "led_rgb":
                light_name = "LED + RGB"
                light_desc = "2в1"
            else:
                light_name = LIGHTING_TYPES[light_type]['name'] if light_type in LIGHTING_TYPES else light_type
                light_desc = ""
            
            # Определяем, выбран ли текущий тип освещения
            is_selected = light_type == selected_lighting
            border_style = "1px solid #0066cc" if is_selected else "1px solid #dddddd"
            check_mark = " ✓" if is_selected else ""
            
            # Создаём HTML-кнопку вместо Streamlit-компонента
            st.markdown(f"""
            <div style="border:{border_style}; background-color:white; border-radius:5px; 
                padding:5px; margin:2px 0; cursor:pointer; text-align:center;"
                onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: '{light_type}', dataType: 'string', componentIndex: '_lighting_{light_type}'}},'*')">
                <div style="font-weight:bold; color:#000000; font-size:0.9rem;">
                    {light_name}{check_mark}
                </div>
                <div style="color:#000000; font-size:0.7rem;">
                    {light_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Добавляем скрытое поле для обработки выбора через JavaScript
            hidden_input = st.text_input("", key=f"_lighting_{light_type}", 
                                      label_visibility="collapsed")
            if hidden_input == light_type:
                st.session_state.options['lighting_type'] = light_type
                st.rerun()
    
    # УСТАНОВКА
    st.subheader("Установка")
    
    # Создаем колонки для опций установки
    install_cols = st.columns(2)
    
    with install_cols[0]:
        st.markdown(f"""
        <div style="border:1px solid #0066cc; background-color:white; 
             border-radius:5px; padding:5px; margin:0; text-align:center; cursor:default;">
            <div style="font-weight:bold; color:#000000; font-size:1.1rem;">Без установки ✓</div>
            <div style="color:#000000; font-size:0.7rem;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    with install_cols[1]:
        st.markdown(f"""
        <div style="border:1px solid #dddddd; background-color:white; 
             border-radius:5px; padding:5px; margin:0; text-align:center; cursor:not-allowed;">
            <div style="font-weight:bold; color:#000000; font-size:1.1rem;">С установкой</div>
            <div style="color:#000000; font-size:0.7rem;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Собираем опции для возврата
    lamella_step = 200 if lamella_type == "200" else 250  # Шаг ламелей зависит от типа
    lighting_type = selected_lighting
    
    # Дополнительные опции (автоматика) подбираются автоматически
    selected_options = []
    
    # Формируем итоговый словарь с опциями
    options = {
        'pergola_type': pergola_type,
        'lamella_type': lamella_type,
        'lamella_step': lamella_step,
        'lighting_type': lighting_type,
        'additional_options': selected_options
    }
    
    # Обновляем состояние сессии только если опции изменились
    if (st.session_state.options['pergola_type'] != options['pergola_type'] or
        st.session_state.options['lamella_type'] != options['lamella_type'] or
        st.session_state.options['lighting_type'] != options['lighting_type'] or
        set(st.session_state.options['additional_options']) != set(options['additional_options'])):
        
        st.session_state.options = options
        log_user_action("Обновлены опции перголы", options)
    
    # Возвращаем выбранные опции
    return options