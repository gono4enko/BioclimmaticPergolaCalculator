"""
Компонент для создания оранжевой кнопки "Рассчитать стоимость"
"""
import streamlit as st

def create_orange_button(label="Рассчитать стоимость"):
    """
    Создает оранжевую кнопку с принудительной стилизацией через HTML и CSS.
    
    Args:
        label (str): Текст кнопки, по умолчанию "Рассчитать стоимость"
        
    Returns:
        bool: True если кнопка была нажата
    """
    # Скрываем стандартную кнопку Streamlit, чтобы не было дублирования
    st.markdown("""
    <style>
    /* Скрываем стандартные кнопки Streamlit с текстом "Рассчитать стоимость" */
    div[data-testid="stButton"] > button:contains("Рассчитать стоимость") {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем обычную скрытую кнопку Streamlit для отслеживания нажатия
    button_key = f"orange_button_{st.session_state.get('button_counter', 0)}"
    button_clicked = st.button(label, key=button_key, type="primary")
    
    # Генерируем ID для кнопки
    button_id = f"custom_button_{st.session_state.get('button_counter', 0)}"
    
    # Создаем кастомную HTML кнопку в оранжевом цвете и добавляем обработчик кликов
    st.markdown(f"""
    <button 
        id="{button_id}"
        style="
            background-color: #ff7a2f; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            font-size: 24px; 
            font-weight: 700; 
            padding: 16px 24px; 
            margin: 20px 0; 
            cursor: pointer; 
            width: 100%; 
            height: 80px; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
            transition: all 0.3s;
        "
        onmouseover="this.style.backgroundColor='#e06a20'; this.style.boxShadow='0 6px 8px rgba(0, 0, 0, 0.15)';"
        onmouseout="this.style.backgroundColor='#ff7a2f'; this.style.boxShadow='0 4px 6px rgba(0, 0, 0, 0.1)';"
    >{label}</button>
    <script>
        // Находим нашу кнопку и добавляем обработчик клика
        document.getElementById("{button_id}").addEventListener("click", function() {{
            // Программно нажимаем на скрытую кнопку Streamlit
            const buttons = Array.from(document.querySelectorAll('button[kind="primary"]'));
            for (const btn of buttons) {{
                if (btn.innerText.includes("{label}")) {{
                    btn.click();
                    break;
                }}
            }}
        }});
    </script>
    """, unsafe_allow_html=True)
    
    # Увеличиваем счетчик для обхода кэширования
    if 'button_counter' not in st.session_state:
        st.session_state.button_counter = 0
    else:
        st.session_state.button_counter += 1
    
    return button_clicked