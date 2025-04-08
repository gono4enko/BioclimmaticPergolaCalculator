"""
Компонент для автоматического прокручивания страницы к результатам
"""
import streamlit as st

def scroll_to_results():
    """
    Добавляет JavaScript-код для автоматического скролла к результатам
    """
    js_code = """
    <script>
    // Функция для скролла к определенному элементу на странице
    function scrollToResults() {
        // Ищем элемент заголовка "Результаты расчета"
        const headers = Array.from(document.querySelectorAll('h2, h3'));
        const resultHeader = headers.find(h => h.innerText.includes('Результаты расчета') || h.innerText.includes('Спецификация перголы'));
        
        if (resultHeader) {
            // Если нашли заголовок "Результаты расчета" или "Спецификация перголы", скроллим к нему
            resultHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
            console.log('Scrolled to results section');
        } else {
            // Альтернативный вариант - ищем контейнеры с возможными результатами
            const containers = document.querySelectorAll('.stContainer');
            if (containers.length > 1) {
                // Берем второй (или последний) контейнер, который обычно содержит результаты
                const resultContainer = containers[containers.length > 1 ? 1 : 0];
                resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                console.log('Scrolled to result container');
            }
        }
    }
    
    // Запускаем функцию с задержкой для уверенности, что DOM загружен
    setTimeout(scrollToResults, 800);
    </script>
    """
    
    # Вставляем JavaScript-код на страницу
    st.markdown(js_code, unsafe_allow_html=True)