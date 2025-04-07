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
        // Ищем вкладки с результатами по классу
        const tabElements = document.querySelectorAll('.stTabs');
        if (tabElements.length > 0) {
            // Берем последний элемент вкладок (обычно это результаты)
            const resultsTab = tabElements[tabElements.length - 1];
            resultsTab.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Запускаем функцию с небольшой задержкой для уверенности, что DOM загружен
    setTimeout(scrollToResults, 500);
    </script>
    """
    
    # Вставляем JavaScript-код на страницу
    st.markdown(js_code, unsafe_allow_html=True)