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
    # Добавляем стили для фиксированных кнопок справа
    st.markdown("""
    <style>
    /* Стили для фиксированных кнопок справа по центру */
    .floating-button-right {
        position: fixed;
        right: 20px;
        z-index: 9999 !important;
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 18px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        cursor: pointer;
        text-align: center;
    }
    
    /* Кнопка "Изменить размеры" */
    .edit-dimensions-btn {
        top: 100px;
        background-color: #28a745;
    }
    
    /* Кнопка "К результатам" */
    .go-results-btn {
        top: 160px;
        background-color: #0066cc;
    }
    
    /* Стиль при наведении */
    .floating-button-right:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .floating-button-right {
            padding: 8px 14px;
            font-size: 14px;
            right: 10px;
        }
    }
    </style>
    
    <!-- Добавляем фиксированные кнопки -->
    <button class="floating-button-right edit-dimensions-btn" id="edit-dimensions" onclick="resetForm()">🖋 Изменить размеры</button>
    <button class="floating-button-right go-results-btn" id="go-results" onclick="clickCalculate()">⬇️ К результатам</button>
    
    <script>
    // Функция для сброса формы
    function resetForm() {
        // Находим все поля ввода и сбрасываем их значения
        var inputs = document.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].type === 'text' || inputs[i].type === 'number') {
                inputs[i].value = '';
            } else if (inputs[i].type === 'checkbox' || inputs[i].type === 'radio') {
                inputs[i].checked = false;
            }
        }
        
        // Также сбрасываем select'ы
        var selects = document.querySelectorAll('select');
        for (var i = 0; i < selects.length; i++) {
            selects[i].selectedIndex = 0;
        }
        
        // Перезагружаем страницу
        window.location.reload();
    }
    
    // Функция для клика по кнопке "Рассчитать"
    function clickCalculate() {
        // Находим кнопку расчета
        var buttons = document.querySelectorAll('button');
        var calcButton = null;
        
        for (var i = 0; i < buttons.length; i++) {
            var buttonText = buttons[i].innerText.toLowerCase();
            if (buttonText.includes('рассчитать') || buttonText.includes('расчет')) {
                calcButton = buttons[i];
                break;
            }
        }
        
        if (calcButton) {
            // Прокручиваем к форме, если она не видна
            var form = document.querySelector('form');
            if (form) {
                form.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            // Нажимаем на кнопку расчета
            calcButton.click();
            
            // Если есть результаты, прокручиваем к ним
            setTimeout(function() {
                var results = document.getElementById('results');
                if (results) {
                    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 1000);
        } else {
            // Если кнопка расчета не найдена, пробуем прокрутить к результатам
            var results = document.getElementById('results');
            if (results) {
                results.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }
    </script>
    """, unsafe_allow_html=True)