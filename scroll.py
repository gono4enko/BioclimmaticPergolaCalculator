"""
Максимально упрощенный модуль для scroll в Streamlit.
Никаких лишних шагов, только самое необходимое.
"""

import streamlit as st

def scroll_to(target_id):
    """
    Добавляет JavaScript для скролла к указанному ID.
    Это базовое решение использует window.location.hash, что является стандартным
    и очень надежным способом скролла в браузере.
    
    Args:
        target_id (str): ID элемента для скролла
    """
    # Формируем JavaScript код для скролла
    js = f"""
    <script>
    // Устанавливаем хэш в URL для скролла
    window.location.hash = "#{target_id}";
    
    // Для более надежной работы также используем scrollIntoView
    setTimeout(function() {{
        try {{
            const element = document.getElementById("{target_id}");
            if (element) {{
                element.scrollIntoView({{ behavior: "smooth", block: "start" }});
                console.log("Прокрутка к элементу {target_id} выполнена");
            }} else {{
                console.log("Элемент {target_id} не найден");
            }}
        }} catch (e) {{
            console.error("Ошибка при прокрутке:", e);
        }}
    }}, 100); // Небольшая задержка для надежности
    </script>
    """
    
    # Добавляем JavaScript на страницу
    st.markdown(js, unsafe_allow_html=True)

def create_anchor(anchor_id, text=None):
    """
    Создает якорь для скролла и опционально добавляет текст.
    
    Args:
        anchor_id (str): ID якоря
        text (str, optional): Текст, который будет отображаться рядом с якорем
    """
    # Формируем HTML для якоря
    html = f'<div id="{anchor_id}" style="height:1px;"></div>'
    
    # Если текст передан, добавляем его
    if text:
        html += f'<h2 style="text-align:center; color:#0066cc; margin-top:20px; margin-bottom:20px;">{text}</h2>'
    
    # Отображаем якорь
    st.markdown(html, unsafe_allow_html=True)