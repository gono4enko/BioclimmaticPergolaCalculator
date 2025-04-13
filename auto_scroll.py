"""
Модуль для автоматической прокрутки в Streamlit с помощью растущего spacer-элемента.
Этот подход не требует JavaScript и хорошо работает в iframe и ограниченных средах.
"""
import streamlit as st


def create_growing_spacer(trigger=True, max_height=800, step=None, delay=None):
    """
    Создает пространство между элементами для автоматической прокрутки страницы
    к результатам расчета.
    
    Args:
        trigger (bool): Условие для активации прокрутки
        max_height (int): Высота spacer-а в пикселях
        step (int, optional): Не используется в этой версии, оставлен для совместимости
        delay (float, optional): Не используется в этой версии, оставлен для совместимости
        
    Returns:
        None
    """
    if not trigger:
        return
    
    # Создаем отступ для прокрутки (упрощенная версия без циклов и задержек)
    st.markdown(f"""
    <div style="height:{max_height}px; 
                width:100%; 
                margin-top:10px;
                margin-bottom:10px;">
    </div>
    """, unsafe_allow_html=True)
    
    # Добавляем скрытое сообщение для отладки
    st.markdown("""
    <div style="display:none;">Автоматическая прокрутка без JavaScript</div>
    """, unsafe_allow_html=True)