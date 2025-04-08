"""
Компонент для выбора опций перголы
"""
import streamlit as st
from config.pergola_types import PERGOLA_TYPES, LIGHTING_TYPES, ADDITIONAL_OPTIONS, LAMELLA_TYPES
from utils.logger import log_user_action

# Добавляем CSS для правильного отображения цвета в темном режиме и уменьшения пространства между опциями
st.markdown("""
<style>
/* Форсированный белый цвет для всех заголовков секций в темном режиме */
body.dark-mode .section-header, 
.dark-mode .section-header,
.stApp.dark .section-header {
    color: white !important;
}

/* Максимальное уменьшение отступов между элементами подсветки */
div[data-testid*="column"] > div {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

/* Минимальные отступы у кнопок в блоке подсветки */
div[data-testid*="stButton"] > button {
    padding: 5px 3px !important;
    margin: 0 !important;
    line-height: 1 !important;
}

/* Дополнительное уменьшение вертикальных отступов в блоке подсветки */
[data-testid="stVerticalBlock"] > div:has(div.section-header:contains("Подсветка")) > div {
    margin: 0 !important;
    padding: 0 !important;
}

/* Уменьшаем размер текста в кнопках подсветки */
div[data-testid*="stButton"] > button[kind="secondary"] {
    font-size: 0.9rem !important;
}
</style>
""", unsafe_allow_html=True)

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
        background-color: var(--card-bg, #f8f9fa);
        border-radius: 8px;
        padding: 0.4rem;
        margin-bottom: 0.1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .option-title, .section-header {
        font-size: 0.95rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: var(--text-color, #333);
    }
    .option-tile {
        background-color: #FFFFFF !important; /* Всегда белый фон */
        border: 1px solid #dddddd !important;
        border-radius: 6px;
        padding: 0.3rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        height: 100%;
        margin: 0;
        position: relative; /* Для индикатора */
    }
    .option-tile:hover {
        border-color: #0066cc !important;
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.05);
    }
    .option-tile.selected {
        background-color: #FFFFFF !important; /* Белый фон */
        border-color: #0066cc !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
    }
    /* Маленький синий индикатор внизу выбранной плитки */
    .option-tile.selected::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px; /* Тонкая линия */
        background-color: #0066cc !important;
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    .option-name {
        font-weight: bold;
        font-size: 0.8rem;
        margin: 0;
        padding: 0;
        color: var(--text-color, #333);
    }
    .option-desc {
        font-size: 0.7rem;
        color: var(--desc-color, #666);
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
        background-color: var(--card-bg, white);
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
    
    # Контейнер для опций перголы в новом стиле с минимальными отступами
    st.markdown('<div class="result-card" style="margin-bottom: 0px; margin-top: 0px; padding-top: 2px; padding-bottom: 2px;">', unsafe_allow_html=True)
    
    # Заголовок блока - более четкий и читаемый
    st.markdown('<div class="section-header" style="color: #FFFFFF !important;">Тип перголы</div>', unsafe_allow_html=True)
    
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
                    pergola_short_desc = "С поворотными ламелями"
                elif "B700" in pergola_type:
                    pergola_short_desc = "С поворотно-сдвижными ламелями"
                elif "B600" in pergola_type:
                    pergola_short_desc = "Со стационарными сэндвич-панелями"
                
            # Используем новый стиль кнопок с более читаемыми элементами
            button_style = """ 
            <style>
            div[data-testid*="stButton"] > button {
                background-color: var(--tile-bg, white);
                border: 1px solid var(--tile-border, #ddd);
                color: var(--text-color, #333);
                font-weight: 500;
                text-align: center;
                border-radius: 8px;
                height: auto;
                padding: 12px 8px;
                margin-bottom: 5px;
                transition: all 0.2s;
                font-size: 1rem;
                line-height: 1.3;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            div[data-testid*="stButton"] > button:hover {
                background-color: #e6f3ff;
                border-color: #0066cc;
                color: #0066cc;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            
            # Отображаем состояние выбора визуально с улучшенной читаемостью
            if is_selected:
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #0066cc; color: #000000; 
                     font-weight: bold; text-align: center; border-radius: 8px; padding: 12px 8px; 
                     margin-bottom: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: relative;">
                    <div style="font-size: 1.1rem;">{pergola_name} ✓</div>
                    <div style="font-size: 0.9rem; margin-top: 5px;">{pergola_short_desc}</div>
                    <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #0066cc;
                         border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Пустая кнопка для сохранения структуры (скрытая)
                if st.button("", key=f"no_action_{pergola_type}", use_container_width=True, disabled=True):
                    pass
            else:
                # Видимая кнопка для выбора перголы в новом стиле
                if st.button(f"{pergola_name}\n{pergola_short_desc}", key=f"btn_pergola_{pergola_type}", use_container_width=True):
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
    # Инициализируем значения по умолчанию для избежания ошибок
    lamella_type = st.session_state.options['lamella_type']
    selected_lamella_type = lamella_type
    # Инициализируем начальное значение для lamella_cols как пустой список колонок
    if lamella_options:
        lamella_cols = st.columns(len(lamella_options))
    else:
        lamella_cols = st.columns(1)  # Минимум одна колонка, даже если нет опций
    
    # Блок для ламелей - в новом стиле отдельным блоком
    if pergola_type == "B600":
        # Для B600 создаем информационный блок без выбора (стационарные PIR сэндвич-панели)
        st.markdown('</div>', unsafe_allow_html=True)  # Закрываем предыдущий блок
        
        st.markdown('<div class="result-card" style="margin-bottom: 0px; margin-top: 0px; padding-top: 2px; padding-bottom: 2px;">', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="color: #FFFFFF !important;">Тип кровли</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding: 15px; text-align: center; font-size: 1rem;">Для перголы В600 PIR используются стационарные PIR сэндвич-панели</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        lamella_type = "B600"  # Для перголы B600 используем фиксированный тип ламелей
        selected_lamella_type = lamella_type
        
    elif "B500" in pergola_type or "B700" in pergola_type:
        # Закрываем блок с типом перголы и открываем новый блок для ламелей
        st.markdown('</div>', unsafe_allow_html=True)  # Закрываем предыдущий блок
        
        st.markdown('<div class="result-card" style="margin-bottom: 0px; margin-top: 0px; padding-top: 2px; padding-bottom: 2px;">', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="color: #FFFFFF !important;">Тип ламелей</div>', unsafe_allow_html=True)
        
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
                            lamella_short_desc = "Ламель 200 х 56 мм NEW, (Усиленная)"
                        else:
                            lamella_short_desc = "Ламель 250 х 53 мм NEW, (Стандартная)"
                    
                    # Определяем размер ламелей для отображения
                    size_display = ""
                    if "20" in lam_type:
                        size_display = "200*56 мм NEW"
                    else:
                        size_display = "250*53 мм NEW"
                    
                    # Используем улучшенный стиль кнопок для ламелей (как для типа перголы)
                    if is_selected:
                        st.markdown(f"""
                        <div style="background-color: #FFFFFF; border: 1px solid #0066cc; color: #000000; 
                             font-weight: bold; text-align: center; border-radius: 8px; padding: 12px 8px; 
                             margin-bottom: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: relative;">
                            <div style="font-size: 1.1rem;">{size_display} ✓</div>
                            <div style="font-size: 0.9rem; margin-top: 5px;">{lamella_short_desc.split(',')[-1].strip()}</div>
                            <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #0066cc;
                                 border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Пустая кнопка для сохранения структуры (скрытая)
                        if st.button("", key=f"no_action_{lam_type}", use_container_width=True, disabled=True):
                            pass
                    else:
                        # Видимая кнопка для выбора ламели с улучшенным стилем
                        if st.button(f"{size_display}\n{lamella_short_desc.split(',')[-1].strip()}", key=f"btn_lamella_{lam_type}", use_container_width=True):
                            st.session_state.options['lamella_type'] = lam_type
                            st.rerun()
    
    # Устанавливаем значение шага ламелей по умолчанию без отображения в интерфейсе
    if "20" in lamella_type:
        lamella_step = 200  # Для ламелей B500-20NEW и B700-20NEW
    else:
        lamella_step = 250  # Для ламелей B500-25NEW и B700-25NEW
    
    # Использовать ТОЛЬКО СТАНДАРТНЫЕ функции Streamlit для заголовка - никакого HTML, CSS или JS
    st.subheader("Подсветка (LED по периметру)")
    
    # Доступные типы освещения для выбранного типа перголы - убираем 'none'
    lighting_options = [opt for opt in PERGOLA_TYPES[pergola_type]["available_lighting"] if opt != "none"] if pergola_type in PERGOLA_TYPES else []
    selected_lighting = st.session_state.options['lighting_type']
    lighting_type = selected_lighting
    
    # Добавляем очень агрессивный CSS для принудительного уменьшения отступов и изменения дизайна
    st.markdown("""
    <style>
    /* Максимальная компактность карточек подсветки */
    div.stButton > button {
        margin: 0px !important;
        padding: 2px !important;
        height: auto !important;
        line-height: 1 !important;
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
        box-shadow: none !important;
    }
    
    /* Делаем кнопки подсветки максимально компактными */
    div.stButton > button > div {
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Принудительно убираем все цвета и стили Streamlit */
    div.stButton > button:hover {
        background-color: white !important;
        color: black !important;
        border: 1px solid #0066cc !important;
        box-shadow: none !important;
    }
    
    /* Уменьшаем расстояние между колонками */
    div.row-widget.stHorizontal {
        gap: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем одну строку, где все элементы будут плотно друг к другу
    cols = st.columns(len(lighting_options), gap="small")
    
    # Для каждого варианта подсветки создаем кнопку с минимальными размерами
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
            
            # Определяем, выбрана ли текущая опция
            is_selected = light_type == selected_lighting
            
            # Если опция выбрана, показываем карточку белого цвета с галочкой
            if is_selected:
                # Используем максимально компактный div вместо стандартного элемента Streamlit - БЕЗ синего индикатора
                st.markdown(f"""
                <div style="border:1px solid #0066cc; background-color:white; 
                     border-radius:5px; padding:5px; margin:0; text-align:center;">
                    <p style="margin:0; padding:0; font-size:0.9rem; font-weight:bold; color:#000000;">{light_name} ✓</p>
                    <p style="margin:0; padding:0; font-size:0.7rem; color:#000000;">{light_desc}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # НЕ используем элемент st.button, а вместо этого используем собственную разметку HTML
                st.markdown(f"""
                <div style="border:1px solid #dddddd; background-color:white; 
                     border-radius:5px; padding:5px; margin:0; text-align:center; cursor:pointer;"
                     onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: '{light_type}', dataType: 'string', componentIndex: '_lighting_{light_type}'}},'*')">
                    <p style="margin:0; padding:0; font-size:0.9rem; font-weight:bold; color:#000000;">{light_name}</p>
                    <p style="margin:0; padding:0; font-size:0.7rem; color:#000000;">{light_desc}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Скрытое поле ввода для приема выбора через JavaScript
                hidden_input = st.text_input(f"Скрытый выбор освещения {light_type}", "", 
                                          key=f"_lighting_{light_type}", 
                                          label_visibility="collapsed")
                if hidden_input == light_type:
                    st.session_state.options['lighting_type'] = light_type
                    st.rerun()
    
    # Нет необходимости закрывать контейнер, так как мы используем встроенные компоненты Streamlit
    
    # Используем стандартный компонент подзаголовка Streamlit для установки
    st.subheader("Установка")
    
    # Создаем колонки для опций установки
    install_cols = st.columns([1, 1])
    
    with install_cols[0]:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #0066cc; color: #000000; 
             font-weight: bold; text-align: left; border-radius: 8px; padding: 12px 8px; 
             margin-bottom: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 1.1rem;">Без установки ✓</div>
            <div style="font-size: 0.9rem; margin-top: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    with install_cols[1]:
        st.markdown(f"""
        <div style="background-color: var(--tile-bg, white); border: 1px solid var(--tile-border, #ddd); color: var(--text-color, #333); 
             text-align: left; border-radius: 8px; padding: 12px 8px; margin-bottom: 5px;">
            <div style="font-size: 1.1rem;">С установкой</div>
            <div style="font-size: 0.9rem; margin-top: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Нет необходимости закрывать блок, так как мы используем встроенные компоненты Streamlit
    
    # Инициализируем пустой список выбранных опций
    # Дополнительные опции (автоматика) подбираются автоматически
    selected_options = []
    
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