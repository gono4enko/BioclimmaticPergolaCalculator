"""
Модуль для прямого внедрения плавающих кнопок навигации в приложении Streamlit.
Этот метод более надежен, чем использование компонентов, и обеспечивает
постоянное отображение кнопок независимо от состояния приложения.
"""

import streamlit as st

def inject_direct_buttons():
    """
    Внедряет плавающие кнопки навигации напрямую в HTML-код Streamlit
    без использования компонентов и зависимости от состояния приложения.
    """
    # Добавляем стили напрямую
    st.markdown("""
    <style>
    .dimension-button {
        position: fixed;
        right: 20px;
        top: calc(50% - 30px);
        z-index: 9999;
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 15px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    
    .result-button {
        position: fixed;
        right: 20px;
        top: calc(50% + 30px);
        z-index: 9999;
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 15px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    
    .dimension-button:hover, .result-button:hover {
        transform: scale(1.05);
    }
    
    @media (max-width: 768px) {
        .dimension-button, .result-button {
            padding: 8px 12px;
            font-size: 14px;
            right: 10px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем кнопки напрямую через компоненты Streamlit
    col1, col2, col3 = st.columns([1, 1, 20])
    
    # Кнопка "Изменить размеры"
    with col3:
        dimensions_button = st.button("✏️ Изменить размеры", key="dimensions_button")
        if dimensions_button:
            st.rerun()
    
    # Кнопка "К результатам"
    with col3:
        results_button = st.button("⬇️ К результатам", key="results_button")
        
    # Скрываем стандартный вид кнопок и применяем собственные стили
    st.markdown("""
    <style>
    /* Скрываем оригинальные кнопки */
    button[data-testid="baseButton-secondary"]:has(div:contains("✏️ Изменить размеры")) {
        visibility: hidden !important;
    }
    
    button[data-testid="baseButton-secondary"]:has(div:contains("⬇️ К результатам")) {
        visibility: hidden !important;
    }
    
    /* Создаем пользовательские кнопки */
    [data-testid="column"]:last-child::before {
        content: "✏️ Изменить размеры";
        display: block;
        position: fixed;
        right: 20px;
        top: calc(50% - 30px);
        background-color: #28a745;
        color: white;
        border-radius: 30px;
        padding: 10px 15px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 9999;
        transition: transform 0.3s ease;
    }
    
    [data-testid="column"]:last-child::after {
        content: "⬇️ К результатам";
        display: block;
        position: fixed;
        right: 20px;
        top: calc(50% + 30px);
        background-color: #0066cc;
        color: white;
        border-radius: 30px;
        padding: 10px 15px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 9999;
        transition: transform 0.3s ease;
    }
    
    [data-testid="column"]:last-child::before:hover,
    [data-testid="column"]:last-child::after:hover {
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Добавляем JavaScript для перехвата кликов
    st.markdown("""
    <script>
        // Функция для имитации клика по скрытой кнопке
        document.addEventListener('click', function(e) {
            // Проверяем, был ли клик по нашей кнопке "Изменить размеры"
            if (e.target.textContent.includes('✏️ Изменить размеры') || 
                (e.target.parentNode && e.target.parentNode.textContent.includes('✏️ Изменить размеры'))) {
                // Находим оригинальную кнопку и кликаем по ней
                document.querySelector('button[data-testid="baseButton-secondary"]:has(div:contains("✏️ Изменить размеры"))').click();
            }
            
            // Проверяем, был ли клик по нашей кнопке "К результатам"
            if (e.target.textContent.includes('⬇️ К результатам') || 
                (e.target.parentNode && e.target.parentNode.textContent.includes('⬇️ К результатам'))) {
                // Находим оригинальную кнопку и кликаем по ней
                document.querySelector('button[data-testid="baseButton-secondary"]:has(div:contains("⬇️ К результатам"))').click();
            }
        });
    </script>
    """, unsafe_allow_html=True)