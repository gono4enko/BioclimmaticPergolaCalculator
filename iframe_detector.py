"""
Модуль для определения, запущено ли приложение в iframe,
и адаптации интерфейса соответствующим образом.
"""
import streamlit as st

def is_in_iframe():
    """
    Определяет, запущено ли приложение в iframe на основе URL-параметров.
    
    Returns:
        bool: True если приложение запущено в iframe, иначе False
    """
    # Используем новый API для работы с параметрами запроса
    return 'embedded' in st.query_params or 'iframe' in st.query_params

def add_iframe_detector_script():
    """
    Добавляет JavaScript-код для определения, запущено ли приложение в iframe,
    и адаптации интерфейса соответствующим образом.
    
    Returns:
        str: HTML-код с JavaScript-скриптом
    """
    script = """
    <script>
    // Функция для определения, запущено ли приложение в iframe
    function detectIframe() {
        // Проверяем, запущено ли приложение в iframe
        const isInIframe = window !== window.parent;
        
        // Сохраняем результат в sessionStorage
        sessionStorage.setItem('in_iframe', isInIframe ? 'true' : 'false');
        
        // Если в iframe, добавляем параметр iframe=true к URL
        if (isInIframe && !window.location.href.includes('iframe=true')) {
            // Проверяем, существуют ли уже параметры в URL
            const separator = window.location.href.includes('?') ? '&' : '?';
            
            // Добавляем параметр iframe=true
            const newUrl = window.location.href + separator + 'iframe=true';
            
            // Обновляем URL без перезагрузки страницы
            window.history.replaceState({}, document.title, newUrl);
        }
        
        return isInIframe;
    }
    
    // Запускаем определение iframe при загрузке страницы
    const isInIframe = detectIframe();
    
    // Если в iframe, добавляем класс к body
    if (isInIframe) {
        document.documentElement.classList.add('in-iframe');
        
        // Подготавливаем дополнительные стили для iframe
        const iframeStyles = document.createElement('style');
        iframeStyles.textContent = `
            body.stApp {
                padding: 0 !important;
                margin: 0 !important;
                background: transparent !important;
            }
            
            .block-container {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                max-width: 100% !important;
            }
            
            .stApp header {
                display: none !important;
            }
            
            /* Скрываем нижний колонтитул с информацией о Streamlit */
            footer {
                display: none !important;
            }
            
            /* Уменьшаем отступы вокруг форм */
            .stForm {
                padding: 5px !important;
            }
            
            /* Уменьшаем отступы между элементами формы */
            .stVerticalBlock > div {
                margin-bottom: 5px !important;
            }
        `;
        
        // Добавляем стили в head документа
        document.head.appendChild(iframeStyles);
        
        console.log("🖼️ Приложение запущено в iframe, применены оптимизации интерфейса");
    }
    </script>
    """
    
    return script

def adapt_for_iframe():
    """
    Адаптирует интерфейс для работы в iframe.
    
    Returns:
        bool: True если приложение запущено в iframe, иначе False
    """
    # Добавляем JavaScript-код для определения iframe
    st.markdown(add_iframe_detector_script(), unsafe_allow_html=True)
    
    # Определяем, запущено ли приложение в iframe
    in_iframe = is_in_iframe()
    
    # Если приложение запущено в iframe, адаптируем интерфейс
    if in_iframe:
        # Добавляем стили для оптимизации интерфейса
        st.markdown("""
        <style>
        /* Стили для оптимизации в iframe */
        .stApp {
            background-color: transparent !important;
        }
        
        /* Убираем отступы */
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
        }
        
        /* Скрываем заголовок */
        header {
            display: none !important;
        }
        
        /* Скрываем нижний колонтитул */
        footer {
            display: none !important;
        }
        
        /* Уменьшаем отступы между секциями */
        .stForm, .stButton, .stMarkdown {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Ускоряем рендеринг интерфейса */
        .stMarkdown, .stForm, .stButton {
            animation: none !important;
            transition: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Сохраняем информацию в session_state
        st.session_state['in_iframe'] = True
    
    return in_iframe