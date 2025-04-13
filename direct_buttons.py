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
    st.markdown("""
    <style>
    /* Базовые стили для плавающих кнопок */
    .floating-nav-button {
        position: fixed;
        z-index: 9999 !important;
        padding: 12px 20px;
        border-radius: 50px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        display: block !important;
        border: none;
        outline: none;
        color: white;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Стиль для кнопки перехода к результатам - внизу по центру */
    #results-button {
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #0066cc;
    }
    
    /* Стиль для кнопки возврата к форме размеров - над кнопкой результатов по центру */
    #dimensions-button {
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #28a745;
    }
    
    /* Анимация при наведении */
    .floating-nav-button:hover {
        box-shadow: 0 6px 15px rgba(0,0,0,0.25);
    }
    #results-button:hover {
        transform: translateX(-50%) scale(1.05);
    }
    #dimensions-button:hover {
        transform: translateX(-50%) scale(1.05);
    }
    
    /* Стили для мобильных устройств */
    @media (max-width: 768px) {
        .floating-nav-button {
            padding: 10px 15px !important;
            font-size: 14px !important;
        }
        #results-button {
            bottom: 15px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
        }
        #dimensions-button {
            bottom: 65px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
        }
    }
    </style>
    
    <button id="results-button" class="floating-nav-button">
        <i class="fas fa-arrow-down" style="margin-right: 5px;"></i> К результатам
    </button>
    
    <button id="dimensions-button" class="floating-nav-button">
        <i class="fas fa-edit" style="margin-right: 5px;"></i> Изменить размеры
    </button>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script>
    // Функция для инициализации кнопок
    function initializeButtons() {
        console.log("Инициализация прямых плавающих кнопок...");
        
        // Кнопка для перехода к результатам
        var resultsButton = document.getElementById('results-button');
        if (resultsButton) {
            resultsButton.addEventListener('click', function() {
                console.log('Клик по кнопке "К результатам"');
                var resultsElement = document.getElementById('results');
                if (resultsElement) {
                    resultsElement.scrollIntoView({behavior: 'smooth', block: 'start'});
                } else {
                    console.error('Элемент #results не найден');
                }
            });
            console.log('Обработчик для кнопки результатов добавлен');
        } else {
            console.error('Кнопка #results-button не найдена');
        }
        
        // Кнопка для возврата к форме размеров
        var dimensionsButton = document.getElementById('dimensions-button');
        if (dimensionsButton) {
            dimensionsButton.addEventListener('click', function() {
                console.log('Клик по кнопке "Изменить размеры"');
                var dimensionsElement = document.getElementById('dimensions-form');
                if (dimensionsElement) {
                    dimensionsElement.scrollIntoView({behavior: 'smooth', block: 'start'});
                } else {
                    console.error('Элемент #dimensions-form не найден');
                }
            });
            console.log('Обработчик для кнопки изменения размеров добавлен');
        } else {
            console.error('Кнопка #dimensions-button не найдена');
        }
    }
    
    // Инициализация при загрузке DOM
    document.addEventListener('DOMContentLoaded', initializeButtons);
    
    // Повторная инициализация через таймаут для надежности
    setTimeout(initializeButtons, 1000);
    
    // Еще одна инициализация с большим таймаутом
    setTimeout(initializeButtons, 2500);
    </script>
    """, unsafe_allow_html=True)