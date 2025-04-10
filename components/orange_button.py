"""
Модуль для создания кнопок с оранжевым стилем.
"""
import streamlit as st

def create_orange_button(label, key=None, help=None, on_click=None):
    """
    Создает кнопку с оранжевым стилем для расчета перголы.
    
    Args:
        label (str): Текст кнопки
        key (str, optional): Уникальный ключ компонента
        help (str, optional): Текст подсказки
        on_click (callable, optional): Функция обратного вызова
    
    Returns:
        bool: True если кнопка была нажата
    """
    # Добавляем CSS для оранжевой кнопки
    st.markdown("""
        <style>
        div[data-testid="stButton"] button.orange-button {
            background-color: #ff9c00;
            color: white;
            font-weight: bold;
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: 1.2rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        div[data-testid="stButton"] button.orange-button:hover {
            background-color: #e68a00;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        div[data-testid="stButton"] button.orange-button:active {
            background-color: #cc7a00;
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Добавляем класс к кнопке через HTML
    st.markdown(f"""
        <button 
            class="orange-button" 
            id="orange-button-{key}" 
            onclick="document.getElementById('orange-button-click-{key}').click();"
            title="{help if help else ''}"
        >
            {label}
        </button>
        
        <script>
            // Добавляем класс scroll-trigger для автоматической прокрутки
            document.addEventListener('DOMContentLoaded', function() {{
                const button = document.getElementById('orange-button-{key}');
                if (button) {{
                    button.classList.add('scroll-trigger');
                }}
            }});
        </script>
    """, unsafe_allow_html=True)
    
    # Создаем скрытую кнопку для обработки события
    return st.button("Нажмите для расчета", key=f"orange-button-click-{key}", on_click=on_click, help=help, label_visibility="collapsed")