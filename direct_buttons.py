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
    
    /* Контейнер для кнопок - справа по центру вертикально */
    .floating-buttons-container {
        position: fixed;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 9999 !important;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    /* Стиль для кнопки перехода к результатам - справа по центру */
    #results-button {
        background-color: #0066cc;
        right: 20px;
        margin-bottom: 10px;
    }
    
    /* Стиль для кнопки возврата к форме размеров - справа по центру */
    #dimensions-button {
        background-color: #28a745;
        right: 20px;
    }
    
    /* Анимация при наведении */
    .floating-nav-button:hover {
        box-shadow: 0 6px 15px rgba(0,0,0,0.25);
        transform: scale(1.05);
    }
    
    /* Стили для мобильных устройств */
    @media (max-width: 768px) {
        .floating-nav-button {
            padding: 10px 15px !important;
            font-size: 14px !important;
        }
        .floating-buttons-container {
            right: 10px;
        }
    }
    </style>
    
    <div class="floating-buttons-container">
        <button id="dimensions-button" class="floating-nav-button">
            <i class="fas fa-edit" style="margin-right: 5px;"></i> Изменить размеры
        </button>
        
        <button id="results-button" class="floating-nav-button">
            <i class="fas fa-arrow-down" style="margin-right: 5px;"></i> К результатам
        </button>
    </div>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script>
    // Функция для инициализации кнопок
    function initializeButtons() {
        console.log("Инициализация прямых плавающих кнопок...");
        
        // Кнопка для перехода к результатам
        var resultsButton = document.getElementById('results-button');
        if (resultsButton) {
            resultsButton.addEventListener('click', function(e) {
                e.preventDefault(); // Предотвращаем стандартное поведение
                console.log('Клик по кнопке "К результатам"');
                
                // Кликаем на существующую кнопку расчета
                var calculateButton = document.querySelector('button[kind="primary"]');
                if (calculateButton) {
                    console.log('Нажатие на кнопку расчета');
                    calculateButton.click();
                } else {
                    console.log('Кнопка расчета не найдена, ищем альтернативную');
                    
                    // Вторая попытка - по атрибуту data-testid
                    var altCalculateButton = document.querySelector('button[data-testid="stButton"]');
                    if (altCalculateButton) {
                        console.log('Нажатие на альтернативную кнопку расчета');
                        altCalculateButton.click();
                    } else {
                        console.error('Ни одна кнопка расчета не найдена');
                    }
                }
            });
            console.log('Обработчик для кнопки результатов добавлен');
        } else {
            console.error('Кнопка #results-button не найдена');
        }
        
        // Кнопка для возврата к форме размеров
        var dimensionsButton = document.getElementById('dimensions-button');
        if (dimensionsButton) {
            dimensionsButton.addEventListener('click', function(e) {
                e.preventDefault(); // Предотвращаем стандартное поведение
                console.log('Клик по кнопке "Изменить размеры"');
                
                // Пытаемся найти кнопку сброса или форму размеров
                var resetStateButton = document.querySelector('button[data-testid="stButton"]');
                if (resetStateButton) {
                    // Находим все кнопки и ищем кнопку с текстом "Сбросить" или "Изменить размеры"
                    var allButtons = document.querySelectorAll('button');
                    var targetButton = null;
                    
                    allButtons.forEach(function(btn) {
                        if (btn.innerText.includes('Изменить размеры') || 
                            btn.innerText.includes('Сбросить') || 
                            btn.innerText.includes('Назад')) {
                            targetButton = btn;
                        }
                    });
                    
                    if (targetButton) {
                        console.log('Нажатие на кнопку изменения размеров/сброса');
                        targetButton.click();
                    } else {
                        // Если не нашли кнопку, перезагрузим страницу
                        console.log('Кнопка изменения размеров не найдена, перезагрузка');
                        window.location.reload();
                    }
                } else {
                    console.log('Элементы управления не найдены, перезагрузка');
                    window.location.reload();
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