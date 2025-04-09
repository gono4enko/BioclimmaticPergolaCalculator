"""
Компонент для создания плиток без синей заливки Streamlit
"""
import streamlit as st

def custom_tile_button(title, subtitle="", key=None, is_selected=False, callback=None):
    """
    Создает плитку с белым фоном и синей рамкой без использования компонентов Streamlit
    
    Args:
        title (str): Заголовок плитки
        subtitle (str, optional): Подзаголовок плитки
        key (str, optional): Ключ для компонента
        is_selected (bool, optional): Выбрана ли плитка
        callback (callable, optional): Функция обратного вызова при клике
        
    Returns:
        bool: True если плитка была нажата
    """
    # Создаем стили для плиток
    st.markdown("""
    <style>
    .custom-tile {
        background-color: white !important;
        border-radius: 8px;
        margin-bottom: 10px;
        padding: 12px 10px;
        cursor: pointer;
        text-align: center;
        transition: all 0.2s;
    }
    .tile-selected {
        border: 2px solid #0066cc;
        font-weight: bold;
    }
    .tile-unselected {
        border: 1px solid #dddddd;
    }
    .tile-title {
        font-size: 1.1rem;
        color: black !important;
    }
    .tile-subtitle {
        font-size: 0.9rem;
        margin-top: 5px;
        color: #555555 !important;
    }
    .tile-unselected:hover {
        border-color: #0066cc;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Определяем стиль на основе выбора
    tile_class = "tile-selected" if is_selected else "tile-unselected"
    checkmark = "✓ " if is_selected else ""
    
    # Создаем уникальный ключ для кнопки если не указан
    if key is None:
        key = f"tile_{title.replace(' ', '_').lower()}"
    
    # Создаем невидимую кнопку (скрыта, но функциональна)
    st.markdown(f"""
    <div style="position: relative;">
        <div class="custom-tile {tile_class}">
            <div class="tile-title">{checkmark}{title}</div>
            <div class="tile-subtitle">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Создаем прозрачную кнопку поверх HTML-разметки
    clicked = st.button("***", key=key, help=title)
    
    if clicked and callback:
        callback()
    
    return clicked

def render_tile_group(items, key_prefix, selected_value, on_change=None):
    """
    Рендерит группу плиток и возвращает выбранное значение
    
    Args:
        items (dict): Словарь где ключи - это значения, а значения - это словари с title и subtitle
        key_prefix (str): Префикс для ключей кнопок
        selected_value (str): Текущее выбранное значение
        on_change (callable, optional): Функция, вызываемая при изменении выбора
        
    Returns:
        str: Выбранное значение
    """
    cols = st.columns(len(items))
    
    # Для каждого элемента создаем плитку
    for i, (value, properties) in enumerate(items.items()):
        with cols[i]:
            title = properties["title"] if isinstance(properties, dict) else properties
            subtitle = properties.get("subtitle", "") if isinstance(properties, dict) else ""
            
            # Определяем, выбрана ли текущая плитка
            is_selected = value == selected_value
            
            # Создаем функцию обратного вызова для обновления значения
            def make_callback(val=value):
                def callback():
                    if on_change:
                        on_change(val)
                return callback
            
            # Отображаем плитку
            if custom_tile_button(
                title=title,
                subtitle=subtitle,
                key=f"{key_prefix}_{value}",
                is_selected=is_selected,
                callback=make_callback()
            ):
                return value
    
    return selected_value