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
    # Уникальный ключ для кнопки и обхода кэширования
    button_key = f"orange_button_{label.replace(' ', '_')}_{st.session_state.get('button_counter', 0)}"
    
    # Создаем обычную кнопку Streamlit, которая будет "отслеживаться"
    button_clicked = st.button(
        label, 
        key=button_key,
        type="primary",
        use_container_width=True
    )
    
    # Создаем HTML и JS для стилизации кнопки
    # Делаем реализацию максимально надежной и прямую
    custom_html = f"""
    <style>
    /* Прямое и очень специфичное применение стилей к кнопке */
    button[kind="primary"][data-testid="baseButton-primary"]:contains("{label}"),
    div[data-testid="stButton"] > button:contains("{label}"),
    .stButton > button:contains("{label}") {{
        background-color: #ff7a2f !important;
        background: #ff7a2f !important;
        color: white !important;
        border-color: #ff7a2f !important;
        font-size: 2rem !important;
        padding: 25px 25px !important;
        min-height: 80px !important;
        font-weight: 700 !important;
    }}
    </style>
    
    <script>
    // Функция для найма именно этой кнопки
    function findAndStyleButton() {{
        // Используем множественные селекторы для поиска кнопки
        const buttons = Array.from(document.querySelectorAll('button'));
        buttons.forEach(btn => {{
            if (btn.innerText.includes("{label}")) {{
                // Мощное переопределение стилей напрямую
                btn.style.cssText = `
                    background-color: #ff7a2f !important;
                    background: #ff7a2f !important;
                    color: white !important;
                    border-color: #ff7a2f !important;
                    font-size: 2rem !important;
                    padding: 25px 25px !important;
                    min-height: 80px !important;
                    font-weight: 700 !important;
                `;
                
                // Для полной надежности добавляем атрибут, который переопределит стили
                btn.setAttribute('style-version', 'orange-{st.session_state.get("button_counter", 0)}');
                
                // Создаем CSS-класс если его нет
                if (!document.getElementById('orange-button-style')) {{
                    const style = document.createElement('style');
                    style.id = 'orange-button-style';
                    style.innerHTML = `
                        button[style-version^="orange-"] {{
                            background-color: #ff7a2f !important;
                            color: white !important;
                        }}
                    `;
                    document.head.appendChild(style);
                }}
            }}
        }});
    }}
    
    // Вызываем функцию сразу и после загрузки DOM
    document.addEventListener('DOMContentLoaded', findAndStyleButton);
    findAndStyleButton();
    
    // Вызываем функцию снова после изменений в DOM
    const observer = new MutationObserver(findAndStyleButton);
    observer.observe(document.body, {{ childList: true, subtree: true }});
    
    // Дополнительно вызываем стилизацию через таймер
    setInterval(findAndStyleButton, 100);
    </script>
    """
    
    # Вставляем HTML и JS на страницу напрямую
    st.markdown(custom_html, unsafe_allow_html=True)
    
    # Обновляем счетчик для обхода кэширования
    if 'button_counter' not in st.session_state:
        st.session_state.button_counter = 0
    else:
        st.session_state.button_counter += 1
    
    return button_clicked