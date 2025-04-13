"""
Модуль для прямого внедрения плавающих кнопок навигации в приложении Streamlit.
Этот метод более надежен, чем использование компонентов, и обеспечивает
постоянное отображение кнопок независимо от состояния приложения.
"""

import streamlit as st

def inject_direct_buttons():
    """
    Внедряет кнопки навигации в правом верхнем углу экрана.
    Использует простой подход с формами для гарантированной работы кнопок.
    """
    # Добавляем только CSS-стили для кнопок, не добавляя сами кнопки через HTML
    st.markdown("""
    <style>
    /* Стилизуем кнопку "Изменить размеры" */
    div[data-testid="element-container"]:has(button:contains("📝 Сброс формы")) button {
        position: fixed !important;
        right: 20px !important;
        top: 100px !important;
        z-index: 9999 !important;
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 30px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        padding: 10px 18px !important;
        width: auto !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    
    /* Стилизуем кнопку "К результатам" */
    div[data-testid="element-container"]:has(button:contains("🔄 Рассчитать")) button {
        position: fixed !important;
        right: 20px !important;
        top: 150px !important;
        z-index: 9999 !important;
        background-color: #0066cc !important;
        color: white !important;
        border-radius: 30px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        padding: 10px 18px !important;
        width: auto !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    
    /* Анимация при наведении */
    div[data-testid="element-container"]:has(button:contains("📝 Сброс формы")) button:hover,
    div[data-testid="element-container"]:has(button:contains("🔄 Рассчитать")) button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.25) !important;
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        div[data-testid="element-container"]:has(button:contains("📝 Сброс формы")) button,
        div[data-testid="element-container"]:has(button:contains("🔄 Рассчитать")) button {
            padding: 8px 14px !important;
            font-size: 14px !important;
            right: 10px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем невидимые контейнеры для кнопок
    col1, col2, col3 = st.columns([1, 1, 20])
    
    # Кнопка "Изменить размеры" (клонируем существующую кнопку сброса)
    with col3:
        dimensions_reset = st.button("📝 Сброс формы", key="dimensions_reset_button")
        if dimensions_reset:
            # Сбрасываем состояние формы
            for key in st.session_state.keys():
                if key.startswith("form_") or key == "calculation_performed":
                    del st.session_state[key]
            st.rerun()
    
    # Кнопка "К результатам" (клонируем существующую кнопку расчета)
    with col3:
        calculate_button = st.button("🔄 Рассчитать", key="calculate_button_fixed")
        if calculate_button:
            # Устанавливаем флаг для расчета
            st.session_state["calculation_requested"] = True
            st.rerun()