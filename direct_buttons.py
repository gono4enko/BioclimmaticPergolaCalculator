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
    # Добавляем HTML и CSS для фиксированных кнопок
    st.markdown("""
    <style>
    /* Скрываем кнопки, создаваемые в контейнере */
    #button-container {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    /* Стили для плавающих кнопок */
    .right-floating-btn {
        position: fixed !important;
        right: 20px !important;
        z-index: 9999 !important;
        padding: 10px 15px !important;
        border-radius: 30px !important;
        color: white !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3) !important;
        cursor: pointer !important;
        text-align: center !important;
        max-width: 180px !important;
        border: none !important;
        transition: transform 0.2s ease-in-out !important;
        font-size: 14px !important;
    }
    
    .edit-btn {
        top: 100px !important;
        background-color: #28a745 !important;
    }
    
    .results-btn {
        top: 160px !important;
        background-color: #0066cc !important;
    }
    
    .right-floating-btn:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .right-floating-btn {
            padding: 8px 12px !important;
            font-size: 12px !important;
            right: 10px !important;
        }
    }
    </style>
    
    <!-- Фиксированные кнопки навигации -->
    <button id="edit-btn" class="right-floating-btn edit-btn">🖋 Изменить размеры</button>
    <button id="results-btn" class="right-floating-btn results-btn">⬇️ К результатам</button>
    
    <script>
    // Функционал кнопки сброса формы
    document.getElementById('edit-btn').addEventListener('click', function() {
        // Перезагрузка страницы
        window.location.reload();
    });
    
    // Функционал кнопки прокрутки к результатам
    document.getElementById('results-btn').addEventListener('click', function() {
        // Ищем элемент с ID results
        var resultsElem = document.getElementById('results');
        if (resultsElem) {
            // Если элемент найден, прокручиваем к нему
            resultsElem.scrollIntoView({behavior: 'smooth', block: 'start'});
        } else {
            // Если элемент не найден, ищем кнопку расчета и нажимаем на нее
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].innerText && 
                    (buttons[i].innerText.toLowerCase().includes('рассчитать') || 
                    buttons[i].innerText.toLowerCase().includes('расчет'))) {
                    // Нажимаем на кнопку расчета
                    buttons[i].click();
                    
                    // Через секунду пробуем прокрутить к результатам
                    setTimeout(function() {
                        var results = document.getElementById('results');
                        if (results) {
                            results.scrollIntoView({behavior: 'smooth', block: 'start'});
                        }
                    }, 1000);
                    
                    break;
                }
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)