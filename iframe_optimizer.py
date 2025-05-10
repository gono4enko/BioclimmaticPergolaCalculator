"""
Модуль для оптимизации приложения Streamlit при встраивании в iframe.
Предоставляет функции для улучшения производительности при использовании
внутри внешних веб-сайтов через iframe.
"""
import streamlit as st
import json
import time

def add_iframe_optimization():
    """
    Добавляет JavaScript-код для оптимизации работы в iframe.
    Улучшает взаимодействие с родительской страницей и оптимизирует высоту iframe.
    
    Returns:
        str: HTML-код с JavaScript-скриптами для оптимизации iframe
    """
    js_code = """
    <script>
        // Функция для оптимизации работы в iframe
        function optimizeIframeIntegration() {
            // Определяем, находится ли приложение в iframe
            const isInIframe = window !== window.parent;
            
            if (isInIframe) {
                // Добавляем класс для специальных оптимизаций
                document.body.classList.add('in-iframe');
                
                // Оптимизированное обновление высоты iframe
                function updateIframeHeight() {
                    // Вычисляем точную высоту содержимого
                    const height = document.documentElement.scrollHeight || document.body.scrollHeight;
                    // Отправляем сообщение родительскому окну с новой высотой
                    window.parent.postMessage({
                        type: 'set-iframe-height',
                        height: height + 20 // Небольшой отступ для предотвращения скролла
                    }, '*');
                }
                
                // Отслеживаем изменения размера окна
                window.addEventListener('resize', updateIframeHeight);
                
                // Отслеживаем изменения DOM
                const observer = new MutationObserver(function(mutations) {
                    // Используем debounce для предотвращения частых обновлений
                    if (window.iframeUpdateTimeout) {
                        clearTimeout(window.iframeUpdateTimeout);
                    }
                    window.iframeUpdateTimeout = setTimeout(updateIframeHeight, 100);
                });
                
                // Запускаем наблюдение за изменениями DOM
                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true
                });
                
                // Разрешаем прокрутку содержимого в iframe, но блокируем прокрутку родительской страницы
                document.addEventListener('wheel', function(e) {
                    // Находимся ли мы внутри iframe
                    if (isInIframe) {
                        // Проверяем, нужно ли блокировать прокрутку родительской страницы
                        const contentHeight = document.body.scrollHeight;
                        const visibleHeight = window.innerHeight;
                        const scrollTop = window.scrollY || document.documentElement.scrollTop;
                        
                        // Если содержимое помещается в видимую область, блокируем прокрутку
                        if (contentHeight <= visibleHeight) {
                            e.preventDefault();
                        }
                        // Если достигли верха или низа и пытаемся прокрутить дальше, блокируем
                        else if ((scrollTop <= 0 && e.deltaY < 0) || 
                                (scrollTop + visibleHeight >= contentHeight && e.deltaY > 0)) {
                            e.preventDefault();
                        }
                    }
                }, { passive: false });
                
                // Начальное обновление высоты
                setTimeout(updateIframeHeight, 100);
                setTimeout(updateIframeHeight, 500);
                setTimeout(updateIframeHeight, 1000);
                
                // Повторное обновление высоты после полной загрузки страницы
                window.addEventListener('load', function() {
                    updateIframeHeight();
                    
                    // Добавляем дополнительные обновления с задержкой для учета асинхронного контента
                    setTimeout(updateIframeHeight, 500);
                    setTimeout(updateIframeHeight, 1000);
                    setTimeout(updateIframeHeight, 2000);
                });
                
                console.log("🖼️ Iframe оптимизации активированы");
            }
        }
        
        // Запускаем оптимизацию для iframe
        document.addEventListener('DOMContentLoaded', optimizeIframeIntegration);
    </script>
    """
    
    return js_code

def add_performance_monitor():
    """
    Добавляет JavaScript-монитор производительности для отладки.
    Полезно для диагностики проблем с производительностью.
    
    Returns:
        str: HTML-код с JavaScript для мониторинга производительности
    """
    js_code = """
    <script>
        // Функция для мониторинга производительности
        function monitorPerformance() {
            if (!window.performance || !window.performance.timing) {
                console.log("Performance API не поддерживается в этом браузере");
                return;
            }
            
            // Отслеживаем загрузку страницы
            window.addEventListener('load', function() {
                // Задержка для завершения всех процессов загрузки
                setTimeout(function() {
                    const perfData = window.performance.timing;
                    
                    // Расчет времени загрузки страницы
                    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                    const domReadyTime = perfData.domComplete - perfData.domLoading;
                    
                    // Записываем в консоль для диагностики
                    console.log("📊 Производительность приложения:");
                    console.log(`  • Полное время загрузки: ${pageLoadTime}ms`);
                    console.log(`  • Время готовности DOM: ${domReadyTime}ms`);
                    
                    // Для отладки записываем детальную информацию
                    const performanceData = {
                        'totalLoad': pageLoadTime,
                        'domReady': domReadyTime,
                        'networkLatency': perfData.responseEnd - perfData.requestStart,
                        'processingTime': perfData.domComplete - perfData.responseEnd,
                        'timestamp': new Date().toISOString()
                    };
                    
                    // Сохраняем статистику в localStorage для анализа
                    try {
                        // Получаем существующие данные
                        let perfHistory = localStorage.getItem('streamlit_perf_stats');
                        let perfStats = perfHistory ? JSON.parse(perfHistory) : [];
                        
                        // Добавляем новые данные
                        perfStats.push(performanceData);
                        
                        // Ограничиваем историю последними 10 загрузками
                        if (perfStats.length > 10) {
                            perfStats = perfStats.slice(-10);
                        }
                        
                        // Сохраняем обратно в localStorage
                        localStorage.setItem('streamlit_perf_stats', JSON.stringify(perfStats));
                    } catch (e) {
                        // Игнорируем ошибки localStorage
                        console.log("Невозможно сохранить статистику производительности");
                    }
                    
                    // Если время загрузки слишком большое, показываем уведомление
                    if (pageLoadTime > 3000) {
                        console.log("⚠️ Время загрузки страницы превышает 3 секунды");
                    }
                }, 0);
            });
        }
        
        // Запускаем мониторинг производительности только в режиме разработки или отладки
        const isDebugMode = window.location.search.includes('debug=1') || 
                           localStorage.getItem('streamlit_debug_mode') === 'true';
        
        if (isDebugMode) {
            monitorPerformance();
            console.log("🔍 Мониторинг производительности активирован (режим отладки)");
        }
    </script>
    """
    
    return js_code

def optimize_for_iframe():
    """
    Основная функция для применения всех оптимизаций для iframe.
    Вызывается в main() перед отображением основного контента.
    """
    # Добавляем оптимизацию для iframe
    st.markdown(add_iframe_optimization(), unsafe_allow_html=True)
    
    # Добавляем мониторинг производительности (активируется только в режиме отладки)
    if st.session_state.get('debug_mode', False) or 'debug' in st.experimental_get_query_params():
        st.markdown(add_performance_monitor(), unsafe_allow_html=True)
    
    # Базовые CSS-оптимизации для iframe
    st.markdown("""
    <style>
    /* Стили для оптимизации в iframe */
    body.in-iframe {
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }
    
    body.in-iframe .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
    }
    
    body.in-iframe .stApp {
        margin: 0 !important;
    }
    
    /* Предотвращаем конфликты с родительской страницей */
    body.in-iframe * {
        box-sizing: border-box !important;
    }
    
    /* Оптимизация для устранения мерцаний при загрузке */
    .element-container:empty {
        min-height: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

def add_content_visibility_optimizations():
    """
    Добавляет CSS-оптимизации с использованием content-visibility
    для более быстрой загрузки контента, особенно на мобильных устройствах.
    
    Returns:
        str: HTML-код с CSS-оптимизациями
    """
    css_code = """
    <style>
    /* Используем content-visibility для отложенного рендеринга несрочного контента */
    .stButton, .stDownloadButton {
        content-visibility: auto;
    }
    
    /* Ускоряем отрисовку таблиц */
    .stTable {
        content-visibility: auto;
        contain-intrinsic-size: 1px 500px; /* Примерный размер для выделения памяти */
    }
    
    /* Оптимизируем загрузку второстепенных изображений */
    img:not([loading]) {
        loading: lazy;
    }
    
    /* Предварительно выделяем размеры для наиболее важных элементов */
    .stForm {
        min-height: 50px;
    }
    
    /* Предотвращаем мерцание при изменении расположения элементов */
    .stMarkdown, .stText {
        min-height: 1.5em;
    }
    
    /* Ускоряем отрисовку форм и инпутов */
    input, select {
        -webkit-font-smoothing: antialiased;
        font-smooth: always;
    }
    </style>
    """
    
    return css_code

def optimize_startup_sequence():
    """
    Оптимизирует последовательность загрузки приложения,
    приоритизируя отображение формы ввода данных.
    
    Returns:
        str: HTML-код с JavaScript для оптимизации загрузки
    """
    js_code = """
    <script>
        // Функция для приоритизации ключевых компонентов при загрузке
        function prioritizeStartupSequence() {
            // Ускоряем появление основной формы для быстрого взаимодействия
            function prioritizeForm() {
                // Находим все формы
                const forms = document.querySelectorAll('.stForm, form, .dimensions-form');
                if (forms.length === 0) return;
                
                // Применяем высокий приоритет к формам
                forms.forEach(form => {
                    // Устанавливаем CSS-приоритет для быстрой отрисовки
                    form.style.contentVisibility = 'visible';
                    form.style.contain = 'none';
                    
                    // Изменяем opacity для эффекта быстрой отрисовки
                    const initialOpacity = getComputedStyle(form).opacity;
                    form.style.opacity = '0.01';
                    
                    // Быстро показываем форму
                    setTimeout(() => {
                        form.style.transition = 'opacity 0.3s ease';
                        form.style.opacity = initialOpacity || '1';
                    }, 10);
                    
                    // Находим инпуты и фокусируемся на первом числовом инпуте
                    const inputs = form.querySelectorAll('input[type="number"]');
                    if (inputs.length > 0) {
                        // Задержка для стабильного фокуса
                        setTimeout(() => {
                            inputs[0].focus();
                        }, 500);
                    }
                });
                
                console.log("✅ Формы приоритизированы для быстрого взаимодействия");
            }
            
            // Запускаем приоритизацию после загрузки DOM
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', prioritizeForm);
            } else {
                prioritizeForm();
            }
            
            // Дополнительная проверка для случаев, когда DOM готов, но формы еще не созданы
            setTimeout(prioritizeForm, 300);
            setTimeout(prioritizeForm, 800);
        }
        
        // Запускаем оптимизацию последовательности загрузки
        prioritizeStartupSequence();
    </script>
    """
    
    return js_code