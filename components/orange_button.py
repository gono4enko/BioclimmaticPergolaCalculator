"""
Компонент для создания оранжевой кнопки "Рассчитать стоимость"
"""
import streamlit as st
import uuid
import time

def create_orange_button(label="Рассчитать стоимость"):
    """
    Создает оранжевую кнопку с принудительной стилизацией через HTML.
    Использует один скрытый элемент Streamlit для отслеживания нажатия.
    
    Args:
        label (str): Текст кнопки, по умолчанию "Рассчитать стоимость"
        
    Returns:
        bool: True если кнопка была нажата
    """
    # Создаем уникальный ID для кнопки, включая временную метку для обхода кэширования
    unique_id = f"orange_btn_{uuid.uuid4()}_{int(time.time())}"
    
    # Создаем скрытую кнопку Streamlit для получения обратной связи
    # Используем container чтобы скрыть эту кнопку
    container = st.container()
    with container:
        clicked = st.button(label, key=unique_id)
    
    # Скрываем контейнер с кнопкой Streamlit и удаляем все остальные primary кнопки
    st.markdown(f"""
    <style>
    /* Полностью скрываем контейнер с нашей скрытой кнопкой */
    div[data-testid="element-container"]:has(button[key="{unique_id}"]) {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
    }}
    
    /* Запрещаем дублированные кнопки с текстом "Рассчитать стоимость" */
    div[data-testid="element-container"]:has(button:not([key="{unique_id}"]):contains("{label}")) {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем свою HTML-кнопку с оранжевым фоном и JavaScript
    button_html = f"""
    <div style="margin-top: 20px; margin-bottom: 20px;">
        <button 
            id="{unique_id}" 
            style="
                background-color: #ff7a2f; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                font-size: 24px; 
                font-weight: 700; 
                padding: 16px 24px; 
                cursor: pointer; 
                width: 100%; 
                height: 80px; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
                transition: all 0.3s;
                display: inline-block;
                text-align: center;
            "
        >{label}</button>
    </div>
    
    <script>
        (function() {{
            // Находим нашу оранжевую кнопку
            var orangeButton = document.getElementById('{unique_id}');
            
            // Находим скрытую кнопку Streamlit
            var hiddenButton = document.querySelector('button[key="{unique_id}"]');
            
            if (orangeButton && hiddenButton) {{
                // Добавляем обработчик клика
                orangeButton.addEventListener('click', function() {{
                    hiddenButton.click();
                }});
                
                // Добавляем эффекты при наведении
                orangeButton.addEventListener('mouseover', function() {{
                    this.style.backgroundColor = '#e06a20';
                    this.style.boxShadow = '0 6px 8px rgba(0, 0, 0, 0.15)';
                }});
                
                orangeButton.addEventListener('mouseout', function() {{
                    this.style.backgroundColor = '#ff7a2f';
                    this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                }});
            }}
        }})();
    </script>
    """
    
    st.markdown(button_html, unsafe_allow_html=True)
    
    return clicked