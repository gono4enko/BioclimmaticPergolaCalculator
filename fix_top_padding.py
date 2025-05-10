"""
Модуль для исправления проблемы с большими отступами вверху страницы.
Обеспечивает минимальный отступ для заголовка, чтобы вся важная информация
была видна без необходимости прокрутки страницы.
"""
import streamlit as st

def remove_padding_top():
    """
    Удаляет лишние отступы вверху страницы путем инъекции CSS и JavaScript.
    Использует JavaScript для более агрессивного изменения стилей, 
    чтобы обойти ограничения Streamlit CSS.
    """
    # CSS для удаления отступов
    st.markdown("""
    <style>
    /* Удаляем отступы в блок-контейнере */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Удаляем отступы в контейнере для заголовков */
    .stHeadingContainer {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Убираем отступы заголовков всех уровней */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Убираем отступ для элементов streamlit */
    .css-1d391kg, .css-1v3fvcr, .css-f45fvc {
        padding-top: 0 !important;
    }
    
    /* Минимизируем отступ для appview-container */
    [data-testid="stAppViewContainer"] {
        padding-top: 0.5rem !important;
    }
    
    /* Минимизируем отступ для заголовка */
    header[data-testid="stHeader"] {
        height: auto !important;
        min-height: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript для динамического изменения отступов после загрузки страницы
    # Более радикальный подход с инъекцией в <head>
    st.markdown("""
    <script>
    // Функция для применения нулевых отступов ко всем контейнерам верхнего уровня
    function removeTopPadding() {
        // Находим все основные контейнеры
        const containers = document.querySelectorAll('.main .block-container, .stHeadingContainer, [data-testid="stAppViewContainer"]');
        
        // Применяем нулевые отступы
        containers.forEach(container => {
            container.style.paddingTop = '0';
            container.style.marginTop = '0';
        });
        
        // Добавляем минимальный отступ для верхнего контейнера
        const appContainer = document.querySelector('[data-testid="stAppViewContainer"]');
        if (appContainer) {
            appContainer.style.paddingTop = '0.2rem';
        }
        
        // Уменьшаем высоту хедера
        const header = document.querySelector('header[data-testid="stHeader"]');
        if (header) {
            header.style.height = 'auto';
            header.style.minHeight = '0';
        }
        
        // Удаляем отступы для всех элементов streamlit
        const allStreamlitElements = document.querySelectorAll('.stHeadingContainer, .main, .element-container');
        allStreamlitElements.forEach(el => {
            el.style.marginTop = '0';
            el.style.paddingTop = '0';
        });
    }
    
    // Создаем и добавляем стили прямо в head
    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .main .block-container { padding-top: 0 !important; margin-top: 0 !important; }
            .stHeadingContainer { margin-top: 0 !important; padding-top: 0 !important; }
            h1, h2, h3, h4, h5, h6 { margin-top: 0 !important; padding-top: 0 !important; }
            header[data-testid="stHeader"] { height: auto !important; min-height: 0 !important; }
            [data-testid="stAppViewContainer"] { padding-top: 0.2rem !important; }
            .main { margin-top: 0 !important; padding-top: 0 !important; }
            .element-container { margin-top: 0 !important; padding-top: 0 !important; }
            div.css-1544g2n.e1fqkh3o4 { padding-top: 0 !important; }
            stHeadingContainer { margin-top: 0 !important; padding-top: 0 !important; }
        `;
        document.head.appendChild(style);
    }
    
    // Запускаем функции сразу и после загрузки страницы
    injectStyles();
    removeTopPadding();
    window.addEventListener('load', () => {
        injectStyles();
        removeTopPadding();
    });
    
    // Запускаем функцию при изменении DOM
    const observer = new MutationObserver(() => {
        removeTopPadding();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)