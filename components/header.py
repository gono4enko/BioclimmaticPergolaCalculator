"""
Модуль для отображения заголовка приложения и верхнего меню.
"""
import streamlit as st

def render_header():
    """
    Отображает заголовок приложения и верхнее меню.
    Этот компонент отображается в верхней части страницы.
    """
    st.markdown(
        """
        <div class="header-container" style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="color: #0066cc; font-size: 2.2rem; font-weight: 600;">Калькулятор пергол</h1>
            <p style="font-size: 1.1rem; color: #555;">
                Рассчитайте стоимость перголы с учетом всех опций и дополнительных элементов
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Добавляем меню для выбора языка (в будущем)
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        pass
    with col2:
        st.markdown(
            """
            <div style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 1rem; margin-bottom: 1rem;">
                <span style="margin-right: 1rem; color: #0066cc; font-weight: 500;">Калькулятор</span>
                <span style="margin-right: 1rem; color: #777;">О компании</span>
                <span style="color: #777;">Контакты</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col3:
        pass
        
    return True