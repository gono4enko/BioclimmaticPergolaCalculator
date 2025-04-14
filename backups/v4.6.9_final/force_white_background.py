"""
Модуль для решения проблемы с синей заливкой кнопок Streamlit
"""
import streamlit as st

def fix_blue_tiles():
    """
    Применяет CSS стили для удаления синей заливки в кнопках Streamlit
    """
    st.markdown("""
    <style>
    /* Принудительно делаем белыми АБСОЛЮТНО ЛЮБЫЕ кнопки в Streamlit с максимальным приоритетом */
    button:not([data-testid="baseButton-primary"]), 
    button:not([data-testid="baseButton-primary"]):hover, 
    button:not([data-testid="baseButton-primary"]):active, 
    button:not([data-testid="baseButton-primary"]):focus,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]),
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):hover,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):active,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):focus,
    .stButton > button:not([data-testid="baseButton-primary"]),
    div[data-testid="column"] div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]),
    div[data-testid*="stButton"] button:not([data-testid="baseButton-primary"]), 
    div[data-testid*="stButton"] button:not([data-testid="baseButton-primary"]):hover,
    div[data-testid*="stButton"] button:not([data-testid="baseButton-primary"]):active,
    div[data-testid*="stButton"] button:not([data-testid="baseButton-primary"]):focus,
    .streamlit-button:not([data-testid="baseButton-primary"]),
    .streamlit-button:not([data-testid="baseButton-primary"]):hover,
    .streamlit-button:not([data-testid="baseButton-primary"]):active,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-secondary"]:hover,
    [data-testid="baseButton-secondary"]:active,
    [data-testid="baseButton-secondary"]:focus {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #dddddd !important;
        box-shadow: none !important;
    }
    
    /* ВАЖНО: Отдельный селектор для "плиток" выбора */
    /* Это должно принудительно сделать все плитки белыми! */
    .row-widget.stButton > button:not([data-testid="baseButton-primary"]),
    .row-widget button:not([data-testid="baseButton-primary"]) {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #dddddd !important;
        box-shadow: none !important;
    }
    
    /* Скрываем все кнопки "Рассчитать стоимость" type="primary" */
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-primary"],
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"],
    div[data-testid="stButton"] button[data-testid="baseButton-primary"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        visibility: hidden !important;
        position: absolute !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }
    
    /* Изменяем радиокнопки на квадратные чекбоксы с галочками */
    div[data-testid="stRadio"] > div:first-child > div:first-child {
        display: flex !important;
        flex-direction: column !important;
    }
    
    div[data-testid="stRadio"] input[type="radio"] {
        appearance: none !important;
        -webkit-appearance: none !important;
        width: 20px !important;
        height: 20px !important;
        border: 2px solid #3f6daa !important;
        border-radius: 4px !important; /* Квадратные углы */
        margin-right: 10px !important;
        position: relative !important;
        cursor: pointer !important;
        background-color: white !important;
    }
    
    div[data-testid="stRadio"] input[type="radio"]:checked {
        background-color: white !important;
    }
    
    div[data-testid="stRadio"] input[type="radio"]:checked::before {
        content: "✓" !important;
        position: absolute !important;
        top: -2px !important;
        left: 2px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        color: #3f6daa !important;
    }
    
    /* Увеличиваем отступ для элементов */
    div[data-testid="stRadio"] > div:first-child > div:first-child > div {
        margin-bottom: 10px !important;
        padding: 10px !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        background-color: white !important;
    }
    
    /* Выделяем активный элемент */
    div[data-testid="stRadio"] > div:first-child > div:first-child > div:has(input[type="radio"]:checked) {
        border: 3px solid #3f6daa !important;
    }
    
    /* Стиль для текста опции */
    div[data-testid="stRadio"] label {
        font-size: 1.1rem !important;
        color: #000000 !important;
    }
    
    /* Убираем круги у радиокнопок */
    div[data-testid="stRadio"] input[type="radio"] + div {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)