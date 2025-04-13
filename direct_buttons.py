"""
Модуль для прямого внедрения плавающих кнопок навигации в приложении Streamlit.
Этот метод более надежен, чем использование компонентов, и обеспечивает
постоянное отображение кнопок независимо от состояния приложения.
"""

import streamlit as st

def inject_direct_buttons():
    """
    Внедряет базовые стили для расположения кнопок навигации справа вверху.
    """
    # Добавляем CSS для стилизации кнопок
    st.markdown("""
    <style>
    /* Стилизация встроенных кнопок */
    .stButton {
        position: relative;
        z-index: 1;
    }
    
    /* Контейнер с кнопками навигации */
    .nav-buttons-container {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    /* Стили для кнопки "Изменить размеры" */
    .edit-button button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.5em 1em !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        width: auto !important;
    }
    
    /* Стили для кнопки "К результатам" */
    .results-button button {
        background-color: #0066cc !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.5em 1em !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        width: auto !important;
    }
    
    /* Эффект при наведении */
    .edit-button button:hover, .results-button button:hover {
        opacity: 0.9;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем фиксированные кнопки навигации при помощи обычных контейнеров Streamlit
    edit_button = st.sidebar.button("🖋 Изменить размеры", key="edit_button")
    results_button = st.sidebar.button("⬇️ К результатам", key="results_button")
    
    # Обрабатываем нажатие на кнопку "Изменить размеры"
    if edit_button:
        # Сбрасываем состояние формы
        for key in list(st.session_state.keys()):
            if key.startswith("form_") or key in ["calculation_performed", "results"]:
                if key in st.session_state:
                    del st.session_state[key]
        st.rerun()
    
    # Обрабатываем нажатие на кнопку "К результатам"
    if results_button:
        # Просто устанавливаем флаг для прокрутки
        st.session_state.scroll_to_results = True
        st.rerun()
    
    # Добавляем JavaScript для перемещения кнопок из сайдбара в фиксированный контейнер справа
    st.markdown("""
    <script>
    // Функция для перемещения кнопок из сайдбара в правый верхний угол
    function moveButtons() {
        // Создаем контейнер для кнопок, если его еще нет
        if (!document.querySelector('.nav-buttons-container')) {
            const container = document.createElement('div');
            container.className = 'nav-buttons-container';
            document.body.appendChild(container);
        }
        
        // Контейнер для кнопок
        const container = document.querySelector('.nav-buttons-container');
        
        // Находим кнопки в сайдбаре
        const sidebar = document.querySelector('.stSidebar');
        if (sidebar) {
            // Найдем кнопку "Изменить размеры"
            const editButton = Array.from(sidebar.querySelectorAll('button'))
                .find(btn => btn.innerText.includes('Изменить размеры'));
            
            // Найдем кнопку "К результатам"
            const resultsButton = Array.from(sidebar.querySelectorAll('button'))
                .find(btn => btn.innerText.includes('К результатам'));
            
            // Перемещаем кнопки в контейнер
            if (editButton && !document.querySelector('.edit-button')) {
                const editDiv = document.createElement('div');
                editDiv.className = 'edit-button';
                editDiv.appendChild(editButton.cloneNode(true));
                container.appendChild(editDiv);
                
                // Добавляем обработчик события при клонировании
                const newEditButton = editDiv.querySelector('button');
                if (newEditButton) {
                    newEditButton.addEventListener('click', function() {
                        // Находим оригинальную кнопку и кликаем по ней
                        if (editButton) {
                            editButton.click();
                        }
                    });
                }
            }
            
            if (resultsButton && !document.querySelector('.results-button')) {
                const resultsDiv = document.createElement('div');
                resultsDiv.className = 'results-button';
                resultsDiv.appendChild(resultsButton.cloneNode(true));
                container.appendChild(resultsDiv);
                
                // Добавляем обработчик события при клонировании
                const newResultsButton = resultsDiv.querySelector('button');
                if (newResultsButton) {
                    newResultsButton.addEventListener('click', function() {
                        // Находим оригинальную кнопку и кликаем по ней
                        if (resultsButton) {
                            resultsButton.click();
                        }
                    });
                }
            }
            
            // Скрываем сайдбар
            const sidebarParent = sidebar.parentElement;
            if (sidebarParent) {
                sidebarParent.style.display = 'none';
            }
        }
    }
    
    // Запускаем после загрузки страницы
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(moveButtons, 500);
    });
    
    // Наблюдаем за изменениями в DOM и при необходимости перемещаем кнопки снова
    const observer = new MutationObserver(function(mutations) {
        setTimeout(moveButtons, 500);
    });
    
    // Начинаем наблюдение за изменениями в DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Запускаем сразу и через задержку для надежности
    setTimeout(moveButtons, 100);
    setTimeout(moveButtons, 1000);
    </script>
    """, unsafe_allow_html=True)