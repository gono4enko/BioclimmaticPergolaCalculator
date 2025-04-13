"""
Модуль для прямого внедрения плавающих кнопок навигации в приложении Streamlit.
Этот метод более надежен, чем использование компонентов, и обеспечивает
постоянное отображение кнопок независимо от состояния приложения.
"""

import streamlit as st

def inject_direct_buttons():
    """
    Внедряет плавающие кнопки навигации с использованием нативных элементов Streamlit
    и JavaScript для их правильного позиционирования и функциональности.
    """
    # Добавляем стили для позиционирования кнопок
    st.markdown("""
    <style>
    /* Стиль для скрытого контейнера кнопок */
    #fixed-button-container {
        display: none !important;
    }
    
    /* Стили для создания плавающих кнопок из обычных кнопок Streamlit */
    .fixed-button-edit {
        position: fixed !important;
        top: 100px !important;
        right: 20px !important;
        z-index: 9999 !important;
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 5px 15px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .fixed-button-calc {
        position: fixed !important;
        top: 160px !important;
        right: 20px !important;
        z-index: 9999 !important;
        background-color: #0066cc !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 5px 15px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .fixed-button-edit:hover, .fixed-button-calc:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .fixed-button-edit, .fixed-button-calc {
            padding: 3px 10px !important;
            font-size: 0.8rem !important;
            right: 10px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Добавляем JavaScript для нахождения кнопок по их содержимому и применения стилей
    st.markdown("""
    <script>
    // Функция для позиционирования кнопок
    function setupButtonStyles() {
        // Ищем все кнопки на странице
        const buttons = document.querySelectorAll('button');
        
        // Для каждой кнопки проверяем ее текст
        for (let i = 0; i < buttons.length; i++) {
            const button = buttons[i];
            const buttonText = (button.innerText || '').toLowerCase();
            
            // Если это кнопка "Сбросить форму"
            if (buttonText.includes('сбросить форму')) {
                // Добавляем стиль для кнопки "Изменить размеры"
                button.classList.add('fixed-button-edit');
                button.innerText = '🖋 Изменить размеры';
                
                // Предотвращаем дублирование обработчиков событий
                button.onclick = function() {
                    // Перезагружаем страницу, чтобы сбросить форму
                    window.location.reload();
                    return false;
                };
            }
            
            // Если это кнопка "К результатам"
            if (buttonText.includes('к результатам')) {
                // Добавляем стиль для кнопки "К результатам"
                button.classList.add('fixed-button-calc');
                
                // Предотвращаем дублирование обработчиков событий
                button.onclick = function() {
                    // Находим результаты и прокручиваем к ним
                    const resultsSection = document.getElementById('results');
                    if (resultsSection) {
                        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } else {
                        // Если нет результатов, то пробуем найти кнопку расчета и нажать на нее
                        const calcButton = findCalculateButton();
                        if (calcButton) {
                            calcButton.click();
                            // После нажатия ждем появления результатов
                            setTimeout(function() {
                                const results = document.getElementById('results');
                                if (results) {
                                    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                }
                            }, 1000);
                        }
                    }
                    return false;
                };
            }
        }
    }
    
    // Функция для поиска кнопки расчета стоимости
    function findCalculateButton() {
        const buttons = document.querySelectorAll('button');
        
        for (let i = 0; i < buttons.length; i++) {
            const buttonText = (buttons[i].innerText || '').toLowerCase();
            if (buttonText.includes('рассчитать') || buttonText.includes('расчет')) {
                return buttons[i];
            }
        }
        
        return null;
    }
    
    // Функция для прокрутки к результатам
    function scrollToResults() {
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Запускаем первую настройку кнопок после загрузки страницы
    window.addEventListener('DOMContentLoaded', function() {
        // Ждем 500мс, чтобы DOM полностью сформировался
        setTimeout(setupButtonStyles, 500);
    });
    
    // Также запускаем настройку после полной загрузки страницы
    window.addEventListener('load', function() {
        // Ждем 1000мс после полной загрузки
        setTimeout(setupButtonStyles, 1000);
    });
    
    // Обновляем стили при изменении DOM
    const observer = new MutationObserver(function(mutations) {
        // При каждом значительном изменении DOM пробуем обновить стили кнопок
        setTimeout(setupButtonStyles, 500);
    });
    
    // Начинаем наблюдение за изменениями в DOM
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
    
    // Запускаем настройку сразу для случаев, когда DOM уже загружен
    setTimeout(setupButtonStyles, 100);
    setTimeout(setupButtonStyles, 1000);
    setTimeout(setupButtonStyles, 2000);
    </script>
    """, unsafe_allow_html=True)
    
    # Создаем настоящие кнопки Streamlit, которые будут стилизованы через JavaScript
    with st.container():
        st.button("Сбросить форму", key="reset_form_button", on_click=reset_form)
        st.button("К результатам", key="go_to_results_button", on_click=scroll_to_results)

def reset_form():
    """
    Сбрасывает состояние формы и перезагружает страницу
    """
    # Сбрасываем все состояния формы
    for key in list(st.session_state.keys()):
        if key.startswith("form_") or key == "calculation_performed" or key == "results":
            if key in st.session_state:
                del st.session_state[key]
    
    # Перезагружаем страницу
    st.rerun()

def scroll_to_results():
    """
    Прокручивает страницу к результатам
    """
    # Добавляем JavaScript для прокрутки к якорю #results
    st.markdown("""
    <script>
    const resultsElement = document.getElementById('results');
    if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    </script>
    """, unsafe_allow_html=True)