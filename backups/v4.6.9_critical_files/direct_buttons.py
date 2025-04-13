"""
Модуль для прямого внедрения плавающих кнопок навигации в приложении Streamlit.
Этот метод более надежен, чем использование компонентов, и обеспечивает
постоянное отображение кнопок независимо от состояния приложения.
"""

import streamlit as st

def is_admin_page():
    """
    Проверяет, является ли текущая страница страницей администрирования.
    
    Returns:
        bool: True если текущая страница относится к администрированию
    """
    # Получаем URL текущей страницы
    page_url = st.query_params.get("_stcore_page_id", [""])[0]
    page_name = page_url.lower()
    
    # Более строгие проверки для определения страниц администрирования
    admin_terms = ["admin", "prices_admin", "promotions_admin", "content_admin", "gallery_admin"]
    
    # Проверяем через регулярное выражение наличие админ-терминов
    import re
    for admin_term in admin_terms:
        if re.search(f'\\b{admin_term}\\b', page_name):
            return True
    
    # Проверяем любые дополнительные признаки админской страницы
    # Например, параметры URL
    if 'admin' in str(st.query_params).lower():
        return True
        
    # Проверка на страницу с паролем (тоже является админской)
    if st.session_state.get('admin_login_attempted', False):
        return True
    
    # Обычная проверка
    return any(admin_term in page_name for admin_term in admin_terms)

def inject_direct_buttons():
    """
    Внедряет базовые стили для расположения кнопок навигации справа вверху.
    Не добавляет кнопки на страницах администрирования.
    """
    # Проверяем, находимся ли мы на странице администрирования
    if is_admin_page():
        return  # Не добавляем кнопки на админ-страницах
    # Добавляем CSS для стилизации кнопок
    st.markdown("""
    <style>
    /* Стилизация встроенных кнопок */
    .stButton {
        position: relative;
        z-index: 1;
    }
    
    /* Контейнер с кнопками навигации */
    .nav-buttons-container {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    /* Стили для кнопки "Изменить размеры" */
    .edit-button button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.5em 1em !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        width: auto !important;
    }
    
    /* Стили для кнопки "К результатам" */
    .results-button button {
        background-color: #0066cc !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.5em 1em !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        width: auto !important;
    }
    
    /* Эффект при наведении */
    .edit-button button:hover, .results-button button:hover {
        opacity: 0.9;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем фиксированные кнопки навигации при помощи обычных контейнеров Streamlit
    edit_button = st.sidebar.button("🖋 Изменить размеры", key="edit_button")
    results_button = st.sidebar.button("⬇️ К результатам", key="results_button")
    
    # Обрабатываем нажатие на кнопку "Изменить размеры"
    if edit_button:
        # Сбрасываем состояние формы
        for key in list(st.session_state.keys()):
            if key.startswith("form_") or key in ["calculation_performed", "results"]:
                if key in st.session_state:
                    del st.session_state[key]
        st.rerun()
    
    # Обрабатываем нажатие на кнопку "К результатам"
    if results_button:
        # Просто устанавливаем флаг для прокрутки
        st.session_state.scroll_to_results = True
        st.rerun()
    
    # Добавляем JavaScript для перемещения кнопок из сайдбара в фиксированный контейнер справа
    st.markdown("""
    <script>
    // Функция для перемещения кнопок из сайдбара в правый верхний угол
    function moveButtons() {
        // Проверяем, находимся ли мы на странице администрирования
        // Проверяем URL, заголовок страницы и параметры URL для определения админ-страницы
        const currentPath = window.location.pathname;
        const currentSearch = window.location.search;
        const pageTitle = document.title || '';
        
        // Проверяем различные признаки админ-страницы
        const isAdminPage = currentPath.includes('admin') || 
                           currentPath.includes('prices_admin') || 
                           currentSearch.includes('admin') ||
                           pageTitle.includes('Администрирование') ||
                           (document.querySelector('h1') && document.querySelector('h1').innerText.includes('Администрирование'));
        
        console.log('Текущий путь:', currentPath);
        console.log('Это админ-страница:', isAdminPage);
        
        // Если мы находимся на странице администрирования - удаляем кнопки
        if (isAdminPage) {
            // Находим и удаляем контейнер с кнопками, если он существует
            const existingContainer = document.querySelector('.nav-buttons-container');
            if (existingContainer) {
                existingContainer.remove();
            }
            
            // Также находим и удаляем кнопки из сайдбара, чтобы предотвратить их перенос
            const sidebar = document.querySelector('.stSidebar');
            if (sidebar) {
                const editButton = Array.from(sidebar.querySelectorAll('button'))
                    .find(btn => btn.innerText.includes('Изменить размеры'));
                const resultsButton = Array.from(sidebar.querySelectorAll('button'))
                    .find(btn => btn.innerText.includes('К результатам'));
                
                if (editButton) {
                    editButton.style.display = 'none';
                }
                if (resultsButton) {
                    resultsButton.style.display = 'none';
                }
            }
            
            return; // Прекращаем выполнение функции
        }
        
        // Создаем контейнер для кнопок, если его еще нет
        if (!document.querySelector('.nav-buttons-container')) {
            const container = document.createElement('div');
            container.className = 'nav-buttons-container';
            document.body.appendChild(container);
        }
        
        // Контейнер для кнопок
        const container = document.querySelector('.nav-buttons-container');
        
        // Находим кнопки в сайдбаре
        const sidebar = document.querySelector('.stSidebar');
        if (sidebar) {
            // Найдем кнопку "Изменить размеры"
            const editButton = Array.from(sidebar.querySelectorAll('button'))
                .find(btn => btn.innerText.includes('Изменить размеры'));
            
            // Найдем кнопку "К результатам"
            const resultsButton = Array.from(sidebar.querySelectorAll('button'))
                .find(btn => btn.innerText.includes('К результатам'));
            
            // Перемещаем кнопки в контейнер
            if (editButton && !document.querySelector('.edit-button')) {
                const editDiv = document.createElement('div');
                editDiv.className = 'edit-button';
                editDiv.appendChild(editButton.cloneNode(true));
                container.appendChild(editDiv);
                
                // Добавляем обработчик события при клонировании
                const newEditButton = editDiv.querySelector('button');
                if (newEditButton) {
                    newEditButton.addEventListener('click', function() {
                        // Находим оригинальную кнопку и кликаем по ней
                        if (editButton) {
                            editButton.click();
                        }
                    });
                }
            }
            
            if (resultsButton && !document.querySelector('.results-button')) {
                const resultsDiv = document.createElement('div');
                resultsDiv.className = 'results-button';
                resultsDiv.appendChild(resultsButton.cloneNode(true));
                container.appendChild(resultsDiv);
                
                // Добавляем обработчик события при клонировании
                const newResultsButton = resultsDiv.querySelector('button');
                if (newResultsButton) {
                    newResultsButton.addEventListener('click', function() {
                        // Находим оригинальную кнопку и кликаем по ней
                        if (resultsButton) {
                            resultsButton.click();
                        }
                    });
                }
            }
            
            // Скрываем сайдбар только на основных страницах
            const sidebarParent = sidebar.parentElement;
            if (sidebarParent && !isAdminPage) {
                sidebarParent.style.display = 'none';
            }
        }
    }
    
    // Запускаем после загрузки страницы
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(moveButtons, 500);
    });
    
    // Наблюдаем за изменениями в DOM и при необходимости перемещаем кнопки снова
    const observer = new MutationObserver(function(mutations) {
        setTimeout(moveButtons, 500);
    });
    
    // Начинаем наблюдение за изменениями в DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Запускаем сразу и через задержку для надежности
    setTimeout(moveButtons, 100);
    setTimeout(moveButtons, 1000);
    </script>
    """, unsafe_allow_html=True)