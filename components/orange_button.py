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
    # Скрываем только станадартную кнопку в основной форме
    # Используем более точный селектор для кнопки с нужным label
    st.markdown(f"""
    <style>
    /* Скрываем стандартные кнопки Streamlit с текстом "Рассчитать стоимость" */
    div[data-testid="stButton"] > button:contains("{label}") {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем обычную скрытую кнопку Streamlit для отслеживания нажатия
    # Помещаем кнопку в контейнер, чтобы легче было выбрать её с помощью CSS
    container = st.container()
    with container:
        button_key = f"orange_button_{st.session_state.get('button_counter', 0)}"
        button_clicked = st.button(label, key=button_key, type="primary")
    
    # Дополнительный CSS для скрытия именно этой кнопки
    st.markdown(f"""
    <style>
    /* Дополнительное скрытие кнопки по специфическому ключу */
    div[data-testid="element-container"]:has(button[kind="primary"][data-testid*="{button_key}"]) {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Генерируем ID для кнопки
    button_id = f"custom_button_{st.session_state.get('button_counter', 0)}"
    
    # Создаем кастомную HTML кнопку в оранжевом цвете и добавляем обработчик кликов
    button_html = f"""
    <div style="margin-top: 20px;">
        <button 
            id="{button_id}"
            type="button"
            style="
                background-color: #ff7a2f !important; 
                color: white !important; 
                border: none !important; 
                border-radius: 8px !important; 
                font-size: 24px !important; 
                font-weight: 700 !important; 
                padding: 16px 24px !important; 
                cursor: pointer !important; 
                width: 100% !important; 
                height: 80px !important; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important; 
                transition: all 0.3s !important;
                display: inline-block !important;
                text-align: center !important;
            "
        >{label}</button>
    </div>
    
    <script>
        (function() {{
            var button = document.getElementById("{button_id}");
            if (button) {{
                button.addEventListener("click", function() {{
                    // Находим скрытую кнопку Streamlit
                    var streamlitButtons = Array.from(document.querySelectorAll('div[data-testid="stButton"] button'));
                    for (var i = 0; i < streamlitButtons.length; i++) {{
                        if (streamlitButtons[i].textContent.includes("{label}")) {{
                            streamlitButtons[i].click();
                            break;
                        }}
                    }}
                }});
                
                // Добавляем эффекты при наведении
                button.addEventListener("mouseover", function() {{
                    this.style.backgroundColor = "#e06a20 !important";
                    this.style.boxShadow = "0 6px 8px rgba(0, 0, 0, 0.15) !important";
                }});
                
                button.addEventListener("mouseout", function() {{
                    this.style.backgroundColor = "#ff7a2f !important";
                    this.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.1) !important";
                }});
            }}
        }})();
    </script>
    """
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Увеличиваем счетчик для обхода кэширования
    if 'button_counter' not in st.session_state:
        st.session_state.button_counter = 0
    else:
        st.session_state.button_counter += 1
    
    return button_clicked