"""
Вспомогательные инструменты для работы с интерфейсом Streamlit
"""
import streamlit as st

def create_custom_tiles(items, key_prefix, selected_value, callback_fn=None):
    """
    Создает горизонтальные плитки с белым фоном (без синей заливки)
    
    Args:
        items (dict): Словарь, где ключи - значения плиток, значения - их названия
        key_prefix (str): Префикс для ключей кнопок
        selected_value (str): Текущее выбранное значение
        callback_fn (callable, optional): Функция, вызываемая при клике
        
    Returns:
        str: Выбранное значение (может измениться при клике)
    """
    # Создаем колонки для каждого элемента
    cols = st.columns(len(items))
    
    # Устанавливаем общие стили для плиток
    st.markdown("""
    <style>
    .tile-container {
        border-radius: 8px;
        padding: 10px;
        margin: 2px 0;
        text-align: center;
        transition: all 0.2s;
        cursor: pointer;
        background-color: white !important;
    }
    .tile-selected {
        border: 2px solid #0066cc;
        color: black;
        font-weight: bold;
    }
    .tile-unselected {
        border: 1px solid #dddddd;
        color: #333333;
    }
    .tile-title {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .tile-subtitle {
        font-size: 0.9rem;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Отображаем каждую плитку
    for i, (value, info) in enumerate(items.items()):
        with cols[i]:
            # Определяем, выбрана ли текущая плитка
            is_selected = value == selected_value
            
            # Создаем HTML-разметку для плитки вместо кнопки
            title = info["title"] if isinstance(info, dict) else info
            subtitle = info.get("subtitle", "") if isinstance(info, dict) else ""
            
            # Класс в зависимости от выбора
            tile_class = "tile-selected" if is_selected else "tile-unselected"
            check_mark = "✓ " if is_selected else ""
            
            # Создаем кликабельный элемент
            clicked = st.container()
            with clicked:
                st.markdown(f"""
                <div class="tile-container {tile_class}" 
                     onclick="alert('This feature requires JavaScript interaction')">
                    <div class="tile-title">{check_mark}{title}</div>
                    <div class="tile-subtitle">{subtitle}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Добавляем невидимую кнопку для функциональности клика
                if st.button("", key=f"{key_prefix}_{value}", help=title):
                    selected_value = value
                    if callback_fn:
                        callback_fn(value)
    
    return selected_value