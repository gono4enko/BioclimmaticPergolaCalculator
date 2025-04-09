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
    /* Принудительно делаем белыми ЛЮБЫЕ кнопки в Streamlit */
    button, button:hover, button:active, button:focus,
    div[data-testid*="stButton"] > button,
    div[data-testid*="stButton"] > button:hover,
    div[data-testid*="stButton"] > button:active,
    div[data-testid*="stButton"] > button:focus,
    div[data-testid*="stButton"] button, 
    div[data-testid*="stButton"] button:hover,
    div[data-testid*="stButton"] button:active,
    div[data-testid*="stButton"] button:focus,
    .streamlit-button,
    .streamlit-button:hover,
    .streamlit-button:active,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-secondary"]:hover,
    [data-testid="baseButton-secondary"]:active,
    [data-testid="baseButton-secondary"]:focus {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
    /* Исключение для основной кнопки расчета */
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:active,
    button[data-testid="baseButton-primary"]:focus,
    div[data-testid*="stButton"] button[data-testid="baseButton-primary"],
    div[data-testid*="stButton"] button[data-testid="baseButton-primary"]:hover {
        background-color: #0066cc !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)