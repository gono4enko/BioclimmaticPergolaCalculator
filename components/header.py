"""
Компонент для отображения заголовка приложения
"""
import streamlit as st

def render_header():
    """
    Отображает заголовок и описание калькулятора пергол
    """
    # Добавляем CSS для стилизации заголовка (ультра-компактная версия в стиле pergolamarket.ru)
    st.markdown("""
    <style>
    .header-container {
        background-color: #3f6daa;
        padding: 0.6rem;
        border-radius: 8px;
        margin-bottom: 0.7rem;
        color: white;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
    }
    .header-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 0.1rem;
        text-align: center;
    }
    .header-subtitle {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .header-desc {
        font-size: 0.7rem;
        opacity: 0.8;
        text-align: center;
        margin-bottom: 0;
    }
    /* Добавляем акцентный оранжевый элемент */
    .accent-bar {
        height: 3px;
        width: 50px;
        background-color: #ff9c00;
        margin: 5px auto;
    }
    </style>
    
    <div class="header-container">
        <div class="header-title">Калькулятор пергол DecoLife</div>
        <div class="accent-bar"></div>
        <div class="header-subtitle">Конфигуратор для расчета стоимости перголы</div>
        <div class="header-desc">Цены указаны в евро (€). Все расчеты выполняются автоматически.</div>
    </div>
    """, unsafe_allow_html=True)