"""
Компонент для создания оранжевой кнопки "Рассчитать стоимость"
"""
import streamlit as st

def create_orange_button(label="Рассчитать стоимость"):
    """
    Создает оранжевую кнопку с принудительной стилизацией через HTML и JS.
    
    Args:
        label (str): Текст кнопки, по умолчанию "Рассчитать стоимость"
        
    Returns:
        bool: True если кнопка была нажата
    """
    # Не блокируем стандартную кнопку, а просто создаем свою
    
    # Создаем невидимую стандартную кнопку для отслеживания нажатия
    button_key = f"orange_button_{label.replace(' ', '_')}_{st.session_state.get('button_counter', 0)}"
    button_clicked = st.button(label, key=button_key, type="primary")
    
    # Создаем полностью кастомную кнопку через HTML
    button_html = f"""
    <div class="custom-button-container" data-button-target="{button_key}">
        <button 
            id="custom_orange_button_{st.session_state.get('button_counter', 0)}" 
            class="custom-orange-button"
            style="
                background-color: #ff7a2f !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
                padding: 25px 25px !important;
                min-height: 80px !important;
                width: 100% !important;
                cursor: pointer !important;
                display: block !important;
                text-align: center !important;
                margin: 20px 0 !important;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1) !important;
                transition: all 0.3s ease !important;
            "
            onmouseover="this.style.backgroundColor='#e56a20 !important'"
            onmouseout="this.style.backgroundColor='#ff7a2f !important'"
        >
            {label}
        </button>
    </div>

    <style>
    /* Гарантированно применяем стили к кнопке */
    #custom_orange_button_{st.session_state.get('button_counter', 0)}, 
    .custom-orange-button {{
        background-color: #ff7a2f !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        padding: 25px 25px !important;
        min-height: 80px !important;
        width: 100% !important;
        cursor: pointer !important;
        display: block !important;
        text-align: center !important;
        margin: 20px 0 !important;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }}

    .custom-orange-button:hover {{
        background-color: #e56a20 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15) !important;
    }}

    .custom-orange-button:active {{
        transform: translateY(1px) !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1) !important;
    }}
    </style>

    <script>
    // Функция для имитации нажатия скрытой кнопки Streamlit при нажатии на нашу кастомную
    document.addEventListener('DOMContentLoaded', function() {{
        const customButton = document.getElementById('custom_orange_button_{st.session_state.get('button_counter', 0)}');
        if (customButton) {{
            customButton.addEventListener('click', function() {{
                // Ищем скрытую кнопку Streamlit и кликаем по ней
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (const btn of allButtons) {{
                    if (btn.innerText.includes('{label}')) {{
                        btn.click();
                        break;
                    }}
                }}
            }});
        }}
    }});

    // Если DOM уже загружен, выполняем сразу
    if (document.readyState === 'complete' || document.readyState === 'interactive') {{
        const customButton = document.getElementById('custom_orange_button_{st.session_state.get('button_counter', 0)}');
        if (customButton) {{
            customButton.addEventListener('click', function() {{
                // Ищем скрытую кнопку Streamlit и кликаем по ней
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (const btn of allButtons) {{
                    if (btn.innerText.includes('{label}')) {{
                        btn.click();
                        break;
                    }}
                }}
            }});
        }}
    }}
    </script>
    """
    
    # Отображаем нашу кнопку
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Увеличиваем счетчик для обхода кэширования
    if 'button_counter' not in st.session_state:
        st.session_state.button_counter = 0
    else:
        st.session_state.button_counter += 1
    
    return button_clicked