"""
Компонент для отображения заголовка приложения
"""
import streamlit as st

def render_header():
    """
    Отображает заголовок и описание калькулятора пергол
    """
    # Добавляем CSS для стилизации заголовка
    st.markdown("""
    <style>
    .header-container {
        background-color: #4a69bd;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0.8rem;
        text-align: center;
    }
    .header-desc {
        font-size: 0.95rem;
        opacity: 0.8;
        text-align: center;
        margin-bottom: 0;
    }
    </style>
    
    <div class="header-container">
        <div class="header-title">Калькулятор пергол DecoLife</div>
        <div class="header-subtitle">Конфигуратор для расчета стоимости перголы</div>
        <div class="header-desc">Цены указаны в евро (€). Все расчеты выполняются автоматически.</div>
    </div>
    """, unsafe_allow_html=True)