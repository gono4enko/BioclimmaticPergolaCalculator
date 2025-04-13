"""
Модуль для плавного скроллинга к элементам страницы с использованием кастомных компонентов
"""
import streamlit as st 
from streamlit.components.v1 import html

def smooth_scroll_to(target_id):
    """
    Выполняет плавный скролл к элементу с указанным ID
    
    Args:
        target_id (str): ID элемента для скролла
        
    Returns:
        None: Вставляет JS-скрипт непосредственно в страницу
    """
    scroll_code = f"""
    <script>
        console.log("🎯 SCROLL: Компонент smooth_scroll_to запущен, цель #{target_id}");
        // Даем странице немного времени для рендеринга
        setTimeout(function() {{
            const target = document.getElementById("{target_id}");
            if (target) {{
                console.log("🎯 SCROLL: Элемент #{target_id} найден, выполняю scrollIntoView");
                
                // Добавим подсветку для наглядности (только для отладки)
                target.style.backgroundColor = "#f0f8ff";
                target.style.transition = "background-color 2s";
                
                // Выполняем скролл
                target.scrollIntoView({{ behavior: "smooth", block: "start" }});
                
                // Через 2 секунды убираем подсветку
                setTimeout(function() {{
                    target.style.backgroundColor = "transparent";
                }}, 2000);
                
                console.log("🎯 SCROLL: scrollIntoView выполнен");
            }} else {{
                console.log("🎯 SCROLL: Элемент #{target_id} не найден");
            }}
        }}, 300); // Задержка перед скроллом для надежности
    </script>
    """
    html(scroll_code, height=0)