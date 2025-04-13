"""
Модуль для автоматической прокрутки в Streamlit с помощью растущего spacer-элемента.
Этот подход не требует JavaScript и хорошо работает в iframe и ограниченных средах.
"""
import streamlit as st
import time


def create_growing_spacer(trigger=True, max_height=800, step=50, delay=0.01):
    """
    Создает растущий spacer, который заставляет страницу прокручиваться вниз.
    
    Args:
        trigger (bool): Условие для активации прокрутки
        max_height (int): Максимальная высота spacer-а в пикселях
        step (int): Шаг увеличения высоты (влияет на плавность)
        delay (float): Задержка между шагами в секундах
        
    Returns:
        None
    """
    if not trigger:
        return
    
    # Постепенно увеличиваем высоту, чтобы создать эффект плавной прокрутки
    for height in range(0, max_height, step):
        st.markdown(f'<div style="height:{height}px;"></div>', unsafe_allow_html=True)
        time.sleep(delay)
    
    # Добавляем финальный spacer с фиксированной высотой
    st.markdown(f'<div style="height:{max_height}px;"></div>', unsafe_allow_html=True)