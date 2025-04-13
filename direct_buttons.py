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
        top: calc(50% - 30px);
        background-color: #28a745;
    }
    
    /* Кнопка "К результатам" */
    .go-results-btn {
        top: calc(50% + 30px);
        background-color: #0066cc;
    }
    
    /* Скрываем все стандартные кнопки */
    div[data-testid="stHorizontalBlock"] button {
        display: none !important;
    }
    
    /* Скрываем верхние кнопки с эмодзи */
    button:has(div:contains("✏️")), 
    button:has(div:contains("⬇️")) {
        display: none !important;
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
    <button class="floating-button-right edit-dimensions-btn" id="edit-dimensions">🖋 Изменить размеры</button>
    <button class="floating-button-right go-results-btn" id="go-results">⬇️ К результатам</button>
    
    <script>
    // Функция для обработки событий кнопок
    function setupButtons() {
        // Кнопка для сброса/возврата к форме размеров
        const editButton = document.getElementById('edit-dimensions');
        if (editButton) {
            editButton.addEventListener('click', function() {
                console.log('Клик по кнопке "Изменить размеры"');
                
                // Находим кнопку "Сбросить"/"Назад"
                const resetButtons = Array.from(document.querySelectorAll('button'));
                let resetButton = null;
                
                for (const btn of resetButtons) {
                    if (btn.innerText && (
                        btn.innerText.includes('Сбросить') || 
                        btn.innerText.includes('Назад') || 
                        btn.innerText.includes('Изменить')
                    )) {
                        resetButton = btn;
                        break;
                    }
                }
                
                if (resetButton) {
                    console.log('Нажимаем кнопку сброса/возврата');
                    resetButton.click();
                } else {
                    // Если не нашли подходящую кнопку - перезагружаем страницу
                    console.log('Кнопка сброса не найдена, перезагружаем страницу');
                    window.location.reload();
                }
            });
            console.log('Обработчик кнопки "Изменить размеры" настроен');
        }
        
        // Кнопка для перехода к результатам/расчета
        const resultsButton = document.getElementById('go-results');
        if (resultsButton) {
            resultsButton.addEventListener('click', function() {
                console.log('Клик по кнопке "К результатам"');
                
                // Находим кнопку расчета (зеленую/синюю)
                const calcButtons = Array.from(document.querySelectorAll('button'));
                let calcButton = null;
                
                for (const btn of calcButtons) {
                    if (btn.innerText && (
                        btn.innerText.includes('Рассчитать') || 
                        btn.innerText.includes('Расчет')
                    )) {
                        calcButton = btn;
                        break;
                    }
                }
                
                if (calcButton) {
                    console.log('Нажимаем кнопку расчета');
                    calcButton.click();
                } else {
                    console.log('Кнопка расчета не найдена');
                }
            });
            console.log('Обработчик кнопки "К результатам" настроен');
        }
    }
    
    // Запускаем настройку кнопок при загрузке страницы
    document.addEventListener('DOMContentLoaded', setupButtons);
    
    // Повторяем настройку через таймаут для надежности
    setTimeout(setupButtons, 1000);
    </script>
    """, unsafe_allow_html=True)