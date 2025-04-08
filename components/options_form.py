"""
Компонент для выбора опций перголы
"""
import streamlit as st
from config.pergola_types import PERGOLA_TYPES, LIGHTING_TYPES, ADDITIONAL_OPTIONS, LAMELLA_TYPES
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
    Отображает форму для выбора опций перголы в плиточном дизайне
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    # Добавляем CSS для стилизации плиток опций с адаптивностью
    st.markdown("""
    <style>
    /* Адаптивные стили для мобильных устройств */
    @media (max-width: 768px) {
        .pergola-option-container {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }
        .option-title {
            font-size: 1.1rem;
            margin-bottom: 0.7rem;
        }
        .option-tile {
            padding: 0.7rem;
        }
        .option-name {
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
        }
        .option-description {
            font-size: 0.75rem;
        }
    }
    
    /* Универсальные стили (более компактные) */
    .pergola-option-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 0.6rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .option-title {
        font-size: 0.95rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .option-tile {
        background-color: #f0f2f6;
        border: 1px solid #e0e4e8;
        border-radius: 6px;
        padding: 0.3rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        height: 100%;
        margin: 0;
    }
    .option-tile:hover {
        border-color: #4a69bd;
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.05);
    }
    .option-tile.selected {
        background-color: #e6f2ff;
        border-color: #4a69bd;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .option-name {
        font-weight: bold;
        font-size: 0.8rem;
        margin: 0;
        padding: 0;
        color: #333;
    }
    .option-desc {
        font-size: 0.7rem;
        color: #666;
        line-height: 1.2;
        margin: 0;
        padding: 0;
    }
    .lamella-image {
        max-width: 100%;
        height: 70px;
        object-fit: contain;
        margin-bottom: 0.5rem;
    }
    .additional-options-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Получаем сохраненные значения из состояния сессии, если они есть
    if 'options' not in st.session_state:
        st.session_state.options = {
            'pergola_type': 'B500NEW',
            'lamella_type': 'B500-20NEW',
            'lamella_step': 200,
            'lighting_type': 'none',
            'additional_options': []
        }
    
    # Контейнер для опций перголы (мобильный стиль, максимально компактный)
    st.markdown("<div class='pergola-option-container' style='margin: 0; padding: 0.2rem;'>", unsafe_allow_html=True)
    
    # Заголовок блока (максимально компактный)
    st.markdown("<h3 style='margin: 0; padding: 0 0 0.1rem 0; color: #333; font-size: 0.85rem; line-height: 1.1;'>Конфигурация перголы</h3>", unsafe_allow_html=True)
    
    # Блок выбора типа перголы (максимально компактный)
    st.markdown("<div class='option-title' style='margin:0; padding:0; font-size:0.75rem;'>Тип перголы:</div>", unsafe_allow_html=True)
    # Создаем плитки для выбора типа перголы
    pergola_options = list(PERGOLA_TYPES.keys())
    pergola_cols = st.columns(len(pergola_options))
    selected_pergola_type = st.session_state.options['pergola_type']
    
    # Отображаем плитки с типами пергол
    for i, pergola_type in enumerate(pergola_options):
        with pergola_cols[i]:
            # Определяем, выбрана ли текущая опция
            is_selected = pergola_type == selected_pergola_type
            selected_class = "selected" if is_selected else ""
            
            # Получаем название и описание типа перголы
            pergola_name = PERGOLA_TYPES[pergola_type]['name']
            pergola_short_desc = PERGOLA_TYPES[pergola_type].get('short_description', '')
            if not pergola_short_desc:
                if "B500" in pergola_type:
                    pergola_short_desc = "поворотные ламели"
                elif "B700" in pergola_type:
                    pergola_short_desc = "сдвижные ламели"
                elif "B600" in pergola_type:
                    pergola_short_desc = "стационарная"
                
            # Создаем кнопки с более заметным выделением при выборе (ультра-компактные)
            button_style = """ 
            <style>
            div[data-testid*="stButton"] > button {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                color: #333;
                font-weight: bold;
                text-align: center;
                border-radius: 6px;
                height: auto;
                padding: 5px;
                margin-bottom: 3px;
                transition: all 0.3s;
                font-size: 0.75rem;
                min-height: 0;
                line-height: 1.2;
            }
            div[data-testid*="stButton"] > button:hover {
                background-color: #e6f3ff;
                border-color: #0066cc;
                color: #0066cc;
            }
            </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            
            # Отображаем состояние выбора визуально (ультра-компактно)
            if is_selected:
                st.markdown(f"""
                <div style="background-color: #e6f3ff; border: 1px solid #0066cc; color: #0066cc; 
                     font-weight: bold; text-align: center; border-radius: 6px; padding: 4px; margin-bottom: 3px;">
                    <div style="font-size: 13px;">{pergola_name.split()[-1]} ✓</div>
                    <div style="font-size: 9px; margin-top: 1px;">{pergola_short_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Пустая кнопка для сохранения структуры (скрытая)
                if st.button("", key=f"no_action_{pergola_type}", use_container_width=True, disabled=True):
                    pass
            else:
                # Видимая кнопка для выбора перголы (ультра-компактная)
                if st.button(f"{pergola_name.split()[-1]}\n{pergola_short_desc}", key=f"btn_pergola_{pergola_type}", use_container_width=True):
                    selected_pergola_type = pergola_type
                
                    # Обновляем тип ламелей при смене типа перголы
                    lamella_options = get_lamella_options_for_pergola(pergola_type)
                    if lamella_options and st.session_state.options['lamella_type'] not in lamella_options:
                        st.session_state.options['lamella_type'] = lamella_options[0]
                    
                    # При выборе B600 устанавливаем фиксированный тип ламелей
                    if pergola_type == "B600":
                        st.session_state.options['lamella_type'] = "B600"
                    
                    # Обновляем тип освещения при смене типа перголы
                    lighting_options = PERGOLA_TYPES[pergola_type]["available_lighting"]
                    if st.session_state.options['lighting_type'] not in lighting_options:
                        st.session_state.options['lighting_type'] = lighting_options[0]
                    
                    # Обновляем дополнительные опции при смене типа перголы
                    available_options = PERGOLA_TYPES[pergola_type]["additional_options"]
                    st.session_state.options['additional_options'] = [
                        opt for opt in st.session_state.options['additional_options']
                        if opt in available_options
                    ]
                    
                    # Обновляем тип перголы в состоянии сессии
                    st.session_state.options['pergola_type'] = pergola_type
                    st.rerun()
    
    # Удаляем информационную строку о перголе
    
    # Устанавливаем значения для текущего типа перголы
    pergola_type = selected_pergola_type
    # Получаем доступные типы ламелей для выбранного типа перголы
    lamella_options = get_lamella_options_for_pergola(pergola_type)
    
    # Блок выбора типа ламелей и отображения типа крыши для всех типов пергол (ультра-компактно)
    if pergola_type == "B600":
        # Для B600 нет выбора ламелей - используются PIR-панели (максимально компактно)
        st.markdown("""
        <div style='background-color: #fff8e6; border-radius: 4px; padding: 0.1rem; margin:0; font-size: 0.7rem;'>
            <b>Тип крыши:</b> Стационарные PIR-панели
        </div>
        """, unsafe_allow_html=True)
        lamella_type = "B600"  # Для перголы B600 используем фиксированный тип ламелей
        selected_lamella_type = lamella_type
    elif "B500" in pergola_type:
        # Для B500 - отображаем информацию о поворотных ламелях (максимально компактно)
        st.markdown("""
        <div style='background-color: #fff8e6; border-radius: 4px; padding: 0.1rem; margin:0; font-size: 0.7rem;'>
            <b>Тип крыши:</b> Поворотные ламели
        </div>
        """, unsafe_allow_html=True)
        # Для выбора ламелей - заголовок (максимально компактно)
        st.markdown("<div class='option-title' style='margin:0; padding:0; font-size:0.75rem;'>Тип ламелей:</div>", unsafe_allow_html=True)
        
        # Создаем плитки для выбора типа ламелей
        lamella_cols = st.columns(len(lamella_options))
        selected_lamella_type = st.session_state.options['lamella_type']
        lamella_type = selected_lamella_type
    else:  # B700
        # Для B700 - отображаем информацию о сдвижных ламелях (максимально компактно)
        st.markdown("""
        <div style='background-color: #fff8e6; border-radius: 4px; padding: 0.1rem; margin:0; font-size: 0.7rem;'>
            <b>Тип крыши:</b> Сдвижные ламели
        </div>
        """, unsafe_allow_html=True)
        # Для выбора ламелей - заголовок (максимально компактно)
        st.markdown("<div class='option-title' style='margin:0; padding:0; font-size:0.75rem;'>Тип ламелей:</div>", unsafe_allow_html=True)
        
        # Создаем плитки для выбора типа ламелей
        lamella_cols = st.columns(len(lamella_options))
        selected_lamella_type = st.session_state.options['lamella_type']
        lamella_type = selected_lamella_type
        
        # Только для B500 и B700 показываем плитки для выбора типа ламелей
    if 'B500' in pergola_type or 'B700' in pergola_type:
        # Отображаем плитки с типами ламелей
        for i, lam_type in enumerate(lamella_options):
            with lamella_cols[i]:
                # Определяем, выбрана ли текущая опция
                is_selected = lam_type == selected_lamella_type
                selected_class = "selected" if is_selected else ""
                
                # Получаем название и описание типа ламелей
                if lam_type in LAMELLA_TYPES:
                    lamella_name = LAMELLA_TYPES[lam_type]['name']
                    lamella_short_desc = LAMELLA_TYPES[lam_type].get('short_description', '')
                    lamella_width = LAMELLA_TYPES[lam_type].get('width', 0)
                    
                    # Если нет короткого описания, создаем его из размеров
                    if not lamella_short_desc:
                        if "20" in lam_type:
                            lamella_short_desc = "Ламель 200 х 56 мм NEW, Усиленная"
                        else:
                            lamella_short_desc = "Ламель 250 х 53 мм NEW, Стандартная"
                    
                    # Определяем размер ламелей для отображения
                    size_display = ""
                    if "20" in lam_type:
                        size_display = "200мм"
                    else:
                        size_display = "250мм"
                    
                    # Переиспользуем стиль кнопок для ламелей (ультра-компактные)
                    if is_selected:
                        st.markdown(f"""
                        <div style="background-color: #e6f3ff; border: 1px solid #0066cc; color: #0066cc; 
                             font-weight: bold; text-align: center; border-radius: 6px; padding: 3px; margin-bottom: 2px;">
                            <div style="font-size: 12px;">{size_display} ✓</div>
                            <div style="font-size: 9px; margin-top: 1px;">{lamella_short_desc.split(',')[-1].strip()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Пустая кнопка для сохранения структуры (скрытая)
                        if st.button("", key=f"no_action_{lam_type}", use_container_width=True, disabled=True):
                            pass
                    else:
                        # Видимая кнопка для выбора ламели (ультра-компактная)
                        if st.button(f"{size_display}\n{lamella_short_desc.split(',')[-1].strip()}", key=f"btn_lamella_{lam_type}", use_container_width=True):
                            st.session_state.options['lamella_type'] = lam_type
                            st.rerun()
    
    # Устанавливаем значение шага ламелей по умолчанию без отображения в интерфейсе
    if "20" in lamella_type:
        lamella_step = 200  # Для ламелей B500-20NEW и B700-20NEW
    else:
        lamella_step = 250  # Для ламелей B500-25NEW и B700-25NEW
    
    # Блок выбора освещения на полную ширину (максимально компактно)
    st.markdown("<div class='option-title' style='margin:0; padding:0; font-size:0.75rem;'>Освещение:</div>", unsafe_allow_html=True)
    
    # Доступные типы освещения для выбранного типа перголы
    lighting_options = PERGOLA_TYPES[pergola_type]["available_lighting"] if pergola_type in PERGOLA_TYPES else ["none"]
    
    # Стиль для уменьшения размера радиокнопок
    st.markdown("""
    <style>
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: center;
    }
    div.row-widget.stRadio > div label {
        font-size: 0.7rem !important;
        padding: 0.1rem 0.3rem;
        margin: 0.1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Радиокнопки для выбора освещения (компактные)
    lighting_type = st.radio(
        "Тип освещения:",
        options=lighting_options,
        format_func=lambda x: LIGHTING_TYPES[x]['name'] if x in LIGHTING_TYPES else x,
        index=lighting_options.index(st.session_state.options['lighting_type']) if st.session_state.options['lighting_type'] in lighting_options else 0,
        key="lighting_radio",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Удаляем информационную строку об освещении
    
    # Инициализируем пустой список выбранных опций
    # Дополнительные опции (автоматика) подбираются автоматически
    selected_options = []
    
    # Закрываем контейнер для опций перголы
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Применяем все опции и обновляем состояние
        
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