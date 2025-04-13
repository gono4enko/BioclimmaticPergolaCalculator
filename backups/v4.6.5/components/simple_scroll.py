"""
Максимально простой механизм скроллинга на базе Streamlit session_state.
Без лишних усложнений, без нескольких этапов - только самое необходимое.
"""
import streamlit as st

def set_scroll_to(section_id):
    """
    Устанавливает целевую секцию для скроллинга
    и перезагружает страницу для применения изменения.
    
    Args:
        section_id (str): ID секции для скроллинга
    """
    # Устанавливаем флаг и значение в session_state
    st.session_state["scroll_to_section"] = section_id
    
    # Перезагружаем страницу
    st.rerun()

def get_scroll_target():
    """
    Возвращает ID целевой секции для скроллинга, если она задана.
    
    Returns:
        str или None: ID целевой секции или None, если не задана
    """
    # Если в текущей сессии есть секция для скроллинга
    if "scroll_to_section" in st.session_state:
        # Запоминаем ID секции
        section_id = st.session_state["scroll_to_section"]
        # Удаляем из session_state, чтобы избежать повторного скроллинга
        del st.session_state["scroll_to_section"]
        # Возвращаем ID секции
        return section_id
    
    # Если секция для скроллинга не задана
    return None

def display_section(section_id, content_function, show_border=True):
    """
    Отображает секцию с уникальным ID. Если секция является целью скроллинга,
    добавляет вокруг нее заметную рамку и отображает сообщение о перемещении.
    
    Args:
        section_id (str): Уникальный ID секции
        content_function (callable): Функция, которая будет вызвана для отображения содержимого
        show_border (bool): Показывать ли рамку вокруг секции при скроллинге
        
    Returns:
        bool: True если эта секция была целью скроллинга, иначе False
    """
    # Получаем ID целевой секции для скроллинга
    target_section = get_scroll_target()
    
    # Если эта секция является целью скроллинга, добавляем рамку и сообщение
    is_target = (target_section == section_id)
    
    # Создаем HTML для контейнера (с рамкой или без)
    if is_target and show_border:
        st.success(f"⬇️ Перемещено к разделу '{section_id}' ⬇️")
    
    # Вызываем функцию для отображения содержимого
    content_function()
    
    # Возвращаем True если эта секция была целью скроллинга
    return is_target