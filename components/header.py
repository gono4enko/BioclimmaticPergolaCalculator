"""
Модуль для отображения заголовка и описания калькулятора пергол.
"""
import streamlit as st

def render_header():
    """
    Отображает заголовок и описание калькулятора пергол
    """
    # Заголовок с увеличенным размером шрифта
    st.markdown("""
        <h1 style="color: #0066cc; font-size: 2.2rem; font-weight: 600; text-align: center; margin-bottom: 1rem;">
            Калькулятор стоимости пергол
        </h1>
    """, unsafe_allow_html=True)
    
    # Описание калькулятора
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;">
            <p style="margin-bottom: 0.5rem;">
                Данный калькулятор поможет вам рассчитать стоимость перголы в зависимости от выбранных параметров.
            </p>
            <p style="margin-bottom: 0.5rem;">
                Выберите размеры перголы, тип конструкции, тип ламелей и дополнительные опции, 
                чтобы получить точный расчет стоимости с учетом всех выбранных параметров.
            </p>
            <p style="margin-bottom: 0;">
                Цены указаны в евро и рублях. Расчет в рублях производится по текущему курсу.
            </p>
        </div>
    """, unsafe_allow_html=True)