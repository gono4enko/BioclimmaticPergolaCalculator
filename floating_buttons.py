"""
Модуль для добавления плавающих кнопок навигации в приложении Streamlit.
Позволяет добавлять фиксированные кнопки, которые остаются видимыми при прокрутке страницы
и могут выполнять переход к заданным якорям на странице.
"""
import streamlit as st
from streamlit.components.v1 import html

def add_floating_button(target_id, button_text, position="bottom-right", color="#0066cc", 
                       icon=None, appear_after_scroll=None, id=None):
    """
    Добавляет плавающую кнопку, которая скроллит к указанному якорю на странице.
    
    Args:
        target_id (str): ID элемента, к которому нужно прокрутить при нажатии на кнопку
        button_text (str): Текст на кнопке
        position (str): Позиция кнопки на экране (bottom-right, bottom-left, bottom-center)
        color (str): Цвет кнопки в HEX-формате
        icon (str, optional): Название иконки из Font Awesome (без префикса fa-)
        appear_after_scroll (int, optional): Появляться только после скролла на указанное количество пикселей
        id (str, optional): Уникальный ID для кнопки, если нужно обращаться к ней через JS
    """
    if id is None:
        id = f"floating-btn-{target_id}"
    
    # Определяем позицию кнопки
    position_css = ""
    if position == "bottom-right":
        position_css = "right: 20px; bottom: 20px;"
    elif position == "bottom-left":
        position_css = "left: 20px; bottom: 20px;"
    elif position == "bottom-center":
        position_css = "left: 50%; transform: translateX(-50%); bottom: 20px;"
    
    # Добавляем иконку, если она указана
    icon_html = ""
    if icon:
        icon_html = f'<i class="fas fa-{icon}" style="margin-right: 8px;"></i>'
    
    # CSS для плавающей кнопки
    css = f"""
    <style>
    #{id} {{
        position: fixed;
        {position_css}
        background-color: {color};
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        display: {"none" if appear_after_scroll else "block"};
        transition: all 0.3s ease;
        opacity: 0.9;
    }}
    
    #{id}:hover {{
        transform: {("translateX(-50%) scale(1.05)" if position == "bottom-center" else "scale(1.05)")};
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        opacity: 1;
    }}
    </style>
    """
    
    # JavaScript для функционала кнопки
    js = f"""
    <script>
    (function() {{
        // Добавляем FontAwesome, если нужна иконка
        if ('{icon}' && !document.querySelector('link[href*="fontawesome"]')) {{
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
            document.head.appendChild(link);
        }}
        
        // Создаем кнопку и добавляем ее на страницу
        const button = document.createElement('button');
        button.id = '{id}';
        button.innerHTML = '{icon_html}{button_text}';
        document.body.appendChild(button);
        
        // Обработчик клика для скролла к указанному элементу
        button.addEventListener('click', function() {{
            const targetElement = document.getElementById('{target_id}');
            if (targetElement) {{
                console.log('🔄 Скролл к элементу #{target_id}');
                targetElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }} else {{
                console.error('⚠️ Элемент #{target_id} не найден');
            }}
        }});
        
        // Если задан порог появления после скролла
        {f'''
        const showButtonAfterScroll = () => {{
            if (window.scrollY > {appear_after_scroll}) {{
                document.getElementById('{id}').style.display = 'block';
            }} else {{
                document.getElementById('{id}').style.display = 'none';
            }}
        }};
        window.addEventListener('scroll', showButtonAfterScroll);
        showButtonAfterScroll();
        ''' if appear_after_scroll else ''}
    }})();
    </script>
    """
    
    # Выводим CSS и JavaScript
    html_content = css + js
    html(html_content, height=0)

def add_results_navigation_button():
    """
    Добавляет плавающую кнопку для быстрого перехода к результатам расчета.
    Кнопка появляется только после скролла на 300 пикселей.
    """
    add_floating_button(
        target_id="results", 
        button_text="К результатам расчета", 
        position="bottom-right", 
        color="#0066cc", 
        icon="arrow-down",
        appear_after_scroll=300,
        id="btn-to-results"
    )

def add_dimensions_edit_button():
    """
    Добавляет плавающую зеленую кнопку для возврата к редактированию размеров.
    Появляется всегда на странице.
    """
    add_floating_button(
        target_id="dimensions-form", 
        button_text="Изменить размеры", 
        position="bottom-center", 
        color="#4CAF50", 
        icon="edit",
        id="btn-edit-dimensions"
    )