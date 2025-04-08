"""
Компонент для автоматического прокручивания страницы к результатам
и добавления анимации нажатия кнопки
"""
import streamlit as st

def scroll_to_results():
    """
    Добавляет JavaScript-код для автоматического скролла к результатам
    и анимации нажатия кнопки
    """
    js_code = """
    <script>
    // Функция для скролла к определенному элементу на странице
    function scrollToResults() {
        // Получаем заголовок результатов расчета
        const resultHeading = document.querySelector('.result-heading');
        
        if (resultHeading) {
            // Если нашли заголовок, скроллим к нему
            resultHeading.scrollIntoView({ behavior: 'smooth', block: 'start' });
            console.log('Scrolled to results heading');
        } else {
            // Ищем элемент заголовка "Результаты расчета" или "Спецификация перголы"
            const headers = Array.from(document.querySelectorAll('h2, h3'));
            const resultHeader = headers.find(h => 
                h.innerText.includes('Результаты расчета') || 
                h.innerText.includes('Спецификация перголы')
            );
            
            if (resultHeader) {
                // Скроллим к найденному заголовку
                resultHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
                console.log('Scrolled to results section');
            } else {
                // Альтернативный вариант - ищем div с blue header (заголовки таблиц)
                const blueHeaders = document.querySelectorAll('div[style*="background-color: #4a75e2"]');
                if (blueHeaders.length > 0) {
                    const firstBlueHeader = blueHeaders[0];
                    firstBlueHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    console.log('Scrolled to table header');
                } else {
                    // Последний вариант - ищем контейнеры с возможными результатами
                    const containers = document.querySelectorAll('.stContainer');
                    if (containers.length > 1) {
                        // Берем второй (или последний) контейнер, который обычно содержит результаты
                        const resultContainer = containers[containers.length > 1 ? 1 : 0];
                        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        console.log('Scrolled to result container');
                    }
                }
            }
        }
    }
    
    // Запускаем функцию с задержкой для уверенности, что DOM загружен
    setTimeout(scrollToResults, 800);
    </script>
    """
    
    # Вставляем JavaScript-код на страницу
    st.markdown(js_code, unsafe_allow_html=True)

def add_button_animation():
    """
    Добавляет CSS и JavaScript-код для анимации нажатия кнопки "Рассчитать стоимость"
    """
    css_and_js_code = """
    <style>
    /* Стили для анимации кнопки и увеличения размера */
    .stButton button {
        position: relative;
        overflow: hidden;
        transition: background-color 0.3s ease, transform 0.2s ease;
        font-size: 2rem !important; /* Большой размер шрифта */
        padding: 25px 25px !important; /* Большие отступы */
        min-height: 80px !important; /* Минимальная высота */
        width: 100% !important; /* Полная ширина */
        font-weight: 700 !important; /* Жирный шрифт */
    }
    
    .stButton button:active {
        transform: scale(0.97);
    }
    
    /* Дополнительные стили для более агрессивного изменения размера кнопки */
    div[data-testid="stButton"] > button,
    div[data-testid="stButton"] > button[kind="primary"],
    button[data-testid="baseButton-primary"],
    .element-container div[data-testid="stButton"] button {
        font-size: 2rem !important; /* Большой размер шрифта */
        padding: 25px 25px !important; /* Большие отступы */
        min-height: 80px !important; /* Минимальная высота */
        width: 100% !important; /* Полная ширина */
        font-weight: 700 !important; /* Жирный шрифт */
    }
    
    /* Эффект пульсации при нажатии */
    .button-pulse {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: pulse 0.6s ease-out;
    }
    
    @keyframes pulse {
        0% {
            width: 0;
            height: 0;
            opacity: 0.5;
        }
        100% {
            width: 300px;
            height: 300px;
            opacity: 0;
        }
    }
    </style>
    
    <script>
    // Функция для добавления анимации нажатия на кнопку и применения стилей
    function addButtonAnimation() {
        // Находим кнопку "Рассчитать стоимость"
        const buttons = Array.from(document.querySelectorAll('.stButton button, div[data-testid="stButton"] button, button[data-testid="baseButton-primary"]'));
        const calculateButton = buttons.find(btn => 
            btn.innerText.includes('Рассчитать стоимость')
        );
        
        // Примененяем стили напрямую через JavaScript
        if (calculateButton) {
            calculateButton.style.fontSize = '2rem';
            calculateButton.style.padding = '25px';
            calculateButton.style.minHeight = '80px';
            calculateButton.style.fontWeight = '700';
        }
        
        if (calculateButton) {
            calculateButton.addEventListener('click', function(e) {
                // Создаем эффект пульсации
                const pulse = document.createElement('span');
                pulse.classList.add('button-pulse');
                this.appendChild(pulse);
                
                // Удаляем эффект пульсации после завершения анимации
                setTimeout(() => {
                    pulse.remove();
                }, 600);
            });
            
            console.log('Button animation added');
        }
    }
    
    // Запускаем функцию с задержкой
    setTimeout(addButtonAnimation, 500);
    
    // Повторно добавляем обработчик при обновлении DOM
    const observer = new MutationObserver(() => {
        setTimeout(addButtonAnimation, 500);
    });
    
    // Наблюдаем за изменениями в DOM
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """
    
    # Вставляем CSS и JavaScript-код на страницу
    st.markdown(css_and_js_code, unsafe_allow_html=True)