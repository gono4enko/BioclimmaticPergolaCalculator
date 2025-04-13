"""
Модуль для добавления плавающих кнопок навигации в приложении Streamlit.
Позволяет добавлять фиксированные кнопки, которые остаются видимыми при прокрутке страницы
и могут выполнять переход к заданным якорям на странице.
"""

import streamlit as st
import streamlit.components.v1 as components

# Глобальная переменная для отслеживания загрузки Font Awesome
_font_awesome_loaded = False

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
    # Добавляем отладочное сообщение для проверки переданных параметров
    st.markdown(f"""
    <script>
        console.log("🔧 DEBUG: add_floating_button вызван с параметрами:");
        console.log("  target_id: {target_id}");
        console.log("  button_text: {button_text}");
        console.log("  position: {position}");
        console.log("  appear_after_scroll: {appear_after_scroll}");
        console.log("  id: {id}");
    </script>
    """, unsafe_allow_html=True)
    # Добавляем загрузку Font Awesome при первом вызове функции
    global _font_awesome_loaded
    if not _font_awesome_loaded:
        st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        """, unsafe_allow_html=True)
        # Отмечаем, что уже загрузили Font Awesome
        _font_awesome_loaded = True
    # Генерируем уникальный ID, если не предоставлен
    if id is None:
        import hashlib
        id = f"floating-btn-{hashlib.md5(button_text.encode()).hexdigest()[:8]}"
    
    # Определяем позицию кнопки в CSS
    position_css = ""
    if position == "bottom-right":
        position_css = "right: 20px; bottom: 20px;"
    elif position == "bottom-left":
        position_css = "left: 20px; bottom: 20px;"
    elif position == "bottom-center":
        position_css = "left: 50%; bottom: 20px; transform: translateX(-50%);"
    elif position == "middle-right":
        position_css = "right: 20px; top: 50%; transform: translateY(-50%);"
    
    # Добавляем иконку, если указана
    icon_html = ""
    if icon:
        icon_html = f'<i class="fas fa-{icon}" style="margin-right: 5px;"></i>'
    
    # Добавляем условие появления после скролла
    scroll_js = ""
    display_style = "display: block;"
    if appear_after_scroll is not None:
        display_style = "display: none;"
        scroll_js = f"""
        window.addEventListener('scroll', function() {{
            const button = document.getElementById('{id}');
            if (window.scrollY > {appear_after_scroll}) {{
                button.style.display = 'block';
            }} else {{
                button.style.display = 'none';
            }}
        }});
        """
    
    # Формируем HTML и CSS для кнопки
    html = f"""
    <div id="{id}" class="floating-button" 
         style="position: fixed; {position_css} z-index: 1000; {display_style} 
                cursor: pointer; padding: 12px 20px; border-radius: 50px; 
                background-color: {color}; color: white; font-weight: 600;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); 
                transition: all 0.3s ease;">
        {icon_html}{button_text}
    </div>
    
    <script>
    document.getElementById('{id}').addEventListener('click', function() {{
        const targetElement = document.getElementById('{target_id}');
        if (targetElement) {{
            // Плавная прокрутка к элементу
            targetElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            
            // Добавляем выделение для элемента
            targetElement.style.transition = 'background-color 0.5s ease';
            targetElement.style.backgroundColor = '#f0f7ff';
            setTimeout(function() {{
                targetElement.style.backgroundColor = '';
            }}, 1500);
        }}
    }});
    
    // Эффект при наведении и нажатии
    document.getElementById('{id}').addEventListener('mouseover', function() {{
        this.style.boxShadow = '0 6px 15px rgba(0, 0, 0, 0.25)';
        this.style.transform = this.style.transform.includes('translateX') ? 
            'translateX(-50%) scale(1.05)' : 
            (this.style.transform.includes('translateY') ? 
                'translateY(-50%) scale(1.05)' : 'scale(1.05)');
    }});
    
    document.getElementById('{id}').addEventListener('mouseout', function() {{
        this.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.2)';
        this.style.transform = this.style.transform.includes('translateX') ? 
            'translateX(-50%)' : 
            (this.style.transform.includes('translateY') ? 
                'translateY(-50%)' : 'none');
    }});
    
    document.getElementById('{id}').addEventListener('mousedown', function() {{
        this.style.transform = this.style.transform.includes('translateX') ? 
            'translateX(-50%) scale(0.95)' : 
            (this.style.transform.includes('translateY') ? 
                'translateY(-50%) scale(0.95)' : 'scale(0.95)');
    }});
    
    document.getElementById('{id}').addEventListener('mouseup', function() {{
        this.style.transform = this.style.transform.includes('translateX') ? 
            'translateX(-50%) scale(1.05)' : 
            (this.style.transform.includes('translateY') ? 
                'translateY(-50%) scale(1.05)' : 'scale(1.05)');
    }});
    
    // Адаптация для мобильных устройств
    if (window.innerWidth < 768) {{
        document.getElementById('{id}').style.padding = '8px 15px';
        document.getElementById('{id}').style.fontSize = '14px';
    }}
    
    {scroll_js}
    </script>
    """
    
    # Добавляем кнопку на страницу
    components.html(html, height=0)

def add_results_navigation_button():
    """
    Добавляет плавающую кнопку для быстрого перехода к результатам расчета.
    Кнопка появляется только после скролла на 300 пикселей.
    """
    # Добавляем отладочное сообщение для проверки вызова функции
    st.markdown("""
    <script>
        console.log("🚀 DEBUG: Вызвана функция add_results_navigation_button()");
    </script>
    """, unsafe_allow_html=True)
    
    # Загружаем компонент для обнаружения мобильных устройств
    mobile_css = """
    <style>
    @media (max-width: 768px) {
        #results-nav-button {
            padding: 10px 15px !important;
            font-size: 14px !important;
            bottom: 15px !important;
        }
    }
    </style>
    """
    st.markdown(mobile_css, unsafe_allow_html=True)
    
    # Добавляем принудительное отображение кнопки (без условия скролла)
    add_floating_button(
        target_id="results",
        button_text="К результатам",
        position="bottom-center",
        color="#0066cc",
        icon="arrow-down",
        appear_after_scroll=None,  # Убираем условие скролла
        id="results-nav-button"
    )

def add_dimensions_edit_button():
    """
    Добавляет плавающую зеленую кнопку для возврата к редактированию размеров.
    Появляется всегда на странице.
    """
    # Добавляем отладочное сообщение для проверки вызова функции
    st.markdown("""
    <script>
        console.log("🚀 DEBUG: Вызвана функция add_dimensions_edit_button()");
    </script>
    """, unsafe_allow_html=True)
    
    # Загружаем CSS для мобильных устройств
    mobile_css = """
    <style>
    @media (max-width: 768px) {
        #dimensions-edit-button {
            padding: 10px 15px !important;
            font-size: 14px !important;
            bottom: 15px !important;
            left: 15px !important;
        }
    }
    </style>
    """
    st.markdown(mobile_css, unsafe_allow_html=True)
    
    add_floating_button(
        target_id="dimensions-form",
        button_text="Изменить размеры",
        position="bottom-left",
        color="#28a745",
        icon="edit",
        id="dimensions-edit-button"
    )