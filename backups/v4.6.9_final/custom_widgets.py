"""
Модуль с пользовательскими виджетами для замены стандартных компонентов Streamlit,
чтобы предотвратить появление синей заливки.
"""
import streamlit as st

def fixed_button(label, key=None, help=None, on_click=None, disabled=False, white_background=True):
    """
    Создает кнопку с принудительно белым фоном или другим заданным цветом.
    
    Args:
        label (str): Текст кнопки
        key (str, optional): Уникальный ключ компонента
        help (str, optional): Подсказка при наведении
        on_click (callable, optional): Функция обратного вызова
        disabled (bool, optional): Отключена ли кнопка
        white_background (bool, optional): Принудительно белый фон
    
    Returns:
        bool: True если кнопка была нажата
    """
    # Добавляем CSS для изменения стиля этой конкретной кнопки
    button_id = f"fixed_button_{key}" if key else f"fixed_button_{label.replace(' ', '_').lower()}"
    bg_color = "#FFFFFF" if white_background else "#0066cc"
    text_color = "#000000" if white_background else "#FFFFFF"
    border_color = "#dddddd" if white_background else "#0066cc"
    
    st.markdown(f"""
    <style>
    div[data-testid="element-container"] div[data-testid="stButton"] button[kind="{button_id}"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    div[data-testid="element-container"] div[data-testid="stButton"] button[kind="{button_id}"]:hover {{
        background-color: {bg_color} !important;
        border-color: #0066cc !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Используем атрибут kind для идентификации кнопки в CSS
    return st.button(label, key=key, help=help, on_click=on_click, disabled=disabled, type=button_id)

def white_tile(title, subtitle="", key=None, is_selected=False, on_click=None):
    """
    Создает плитку с белым фоном и без синей заливки.
    
    Args:
        title (str): Заголовок плитки
        subtitle (str, optional): Подзаголовок плитки
        key (str, optional): Уникальный ключ компонента
        is_selected (bool, optional): Выбрана ли плитка
        on_click (callable, optional): Функция обратного вызова при клике
    
    Returns:
        bool: True если плитка была нажата
    """
    # Создаем уникальный ключ
    if key is None:
        key = f"tile_{title.replace(' ', '_').lower()}"
    
    # Создаем стили для плитки
    border = "2px solid #0066cc" if is_selected else "1px solid #dddddd"
    check_mark = "✓ " if is_selected else ""
    font_weight = "bold" if is_selected else "normal"
    
    # Создаем HTML-контейнер для плитки
    st.markdown(f"""
    <div style="background-color:#FFFFFF; border:{border}; border-radius:8px; padding:10px; 
         margin-bottom:10px; text-align:center; cursor:pointer;">
        <div style="font-size:1.1rem; font-weight:{font_weight}; color:#000000;">{check_mark}{title}</div>
        <div style="font-size:0.9rem; color:#555555; margin-top:5px;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Создаем скрытую кнопку, которая будет занимать то же место, но будет прозрачной
    st.markdown("""
    <style>
    div.stButton > button:last-child {
        position: relative;
        top: -60px;  /* Подвигаем кнопку вверх, чтобы она перекрывала наш HTML-контейнер */
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        height: 40px;  /* Высота достаточная для перекрытия нашего контейнера */
        width: 100%;
        padding: 0;
        margin: 0;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Возвращаем результат клика
    clicked = st.button("", key=key)
    if clicked and on_click:
        on_click()
    
    return clicked