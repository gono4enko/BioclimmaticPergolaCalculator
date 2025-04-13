"""
Модуль для скроллинга в Streamlit.
Максимально простой, без усложнений, на чистом Python.
Использует только те функции, которые точно работают.
"""

import streamlit as st


def scroll_to_element(element_id):
    """
    Добавляет минимальный JavaScript для скролла к элементу с указанным ID.
    
    Args:
        element_id (str): ID элемента для скролла
    """
    # Добавляем маленький JS-скрипт, который скроллит к нужному элементу
    js = f"""
    <script>
    // Функция для скролла к элементу
    function scrollToElement() {{
        const element = document.getElementById("{element_id}");
        if (element) {{
            // Используем scrollIntoView, который гарантированно работает во всех браузерах
            element.scrollIntoView({{
                behavior: 'smooth',
                block: 'start'
            }});
            console.log("Прокрутка к элементу {element_id} выполнена");
        }} else {{
            console.log("Элемент {element_id} не найден");
        }}
    }}
    
    // Вызываем с небольшой задержкой, чтобы элемент успел отрендериться
    setTimeout(scrollToElement, 300);
    </script>
    """
    
    # Добавляем скрипт на страницу
    st.markdown(js, unsafe_allow_html=True)


def create_anchor(anchor_id, content=None, show_border=False):
    """
    Создает HTML-якорь с указанным ID и опциональным контентом.
    
    Args:
        anchor_id (str): ID якоря для скролла
        content (str, optional): HTML-контент для отображения
        show_border (bool): Показывать ли рамку вокруг якоря (для отладки)
        
    Returns:
        None: Якорь отображается с помощью st.markdown
    """
    # Создаем стили для якоря
    style = ""
    if show_border:
        style = "border: 1px solid red; padding: 10px; margin: 5px 0; display: block;"
    
    # Формируем HTML для якоря
    html = f'<div id="{anchor_id}" style="{style}"></div>'
    
    # Если есть контент, добавляем его после якоря
    if content:
        html += content
    
    # Отображаем якорь
    st.markdown(html, unsafe_allow_html=True)


def scroll_on_page_load(target_id=None):
    """
    Проверяет, нужен ли скролл при загрузке страницы.
    Должна вызываться в начале приложения.
    
    Args:
        target_id (str, optional): ID элемента для скролла или None, 
                                  чтобы использовать значение из session_state
    """
    # Если явно указан target_id, используем его
    if target_id:
        scroll_target = target_id
    # Иначе проверяем session_state
    elif "scroll_target" in st.session_state:
        scroll_target = st.session_state.pop("scroll_target")
    else:
        # Если нет цели для скролла, ничего не делаем
        return
    
    # Выполняем скролл
    scroll_to_element(scroll_target)


def set_scroll_target(target_id):
    """
    Устанавливает цель для скролла и перезагружает страницу.
    
    Args:
        target_id (str): ID элемента для скролла
    """
    # Устанавливаем цель для скролла в session_state
    st.session_state.scroll_target = target_id
    
    # Перезагружаем страницу
    st.rerun()