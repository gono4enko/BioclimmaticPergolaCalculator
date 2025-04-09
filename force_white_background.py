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
    
    /* Исключение для основной кнопки расчета - только она синяя с белым текстом */
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:active,
    button[data-testid="baseButton-primary"]:focus,
    div[data-testid*="stButton"] button[data-testid="baseButton-primary"],
    div[data-testid*="stButton"] button[data-testid="baseButton-primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #0066cc !important;
        color: white !important;
        border: none !important;
    }
    
    /* Удаление синей заливки в выбранных элементах интерфейса */
    .css-12w0qpk, .css-1d391kg, .stRadio > div[role="radiogroup"] div[data-checked="true"],
    div[data-testid="stVerticalBlock"] div[data-checked="true"] {
        background-color: #FFFFFF !important;
    }
    
    /* Радиокнопки - стандартный синий цвет для галки, но белый фон */
    .stRadio div[role="radiogroup"] label span {
        background-color: #FFFFFF !important;
    }
    
    /* Цвет рамки для выбранных опций */
    .stRadio div[role="radiogroup"] div[data-checked="true"] {
        border: 2px solid #0066cc !important;
        border-radius: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)