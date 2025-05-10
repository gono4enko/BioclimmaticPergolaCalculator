"""
Модуль для оптимизации производительности приложения и ускорения загрузки страницы.
Предоставляет функции для оптимизированной загрузки ресурсов и улучшения отзывчивости интерфейса.
"""
import os
import json
import logging
from typing import List, Dict, Tuple

# Настройка логгера
logger = logging.getLogger(__name__)

def optimize_images_loading(critical_images: List[str], secondary_images: List[str] = [], 
                           tertiary_images: List[str] = []):
    """
    Возвращает JavaScript-код для оптимизированной многоуровневой загрузки изображений.
    Критические изображения загружаются немедленно, остальные - с задержкой.
    
    Args:
        critical_images (List[str]): Список путей к критически важным изображениям
        secondary_images (List[str], optional): Список путей к второстепенным изображениям
        tertiary_images (List[str], optional): Список путей к дополнительным изображениям
        
    Returns:
        str: HTML/JavaScript код для оптимизированной загрузки
    """
    if secondary_images is None:
        secondary_images = []
    if tertiary_images is None:
        tertiary_images = []

    # Фильтруем только существующие изображения
    critical_paths = [path for path in critical_images if os.path.exists(path)]
    secondary_paths = [path for path in secondary_images if os.path.exists(path)]
    tertiary_paths = [path for path in tertiary_images if os.path.exists(path)]
    
    # Преобразуем пути в JSON-строки для вставки в JavaScript
    critical_json = json.dumps(critical_paths)
    secondary_json = json.dumps(secondary_paths)
    tertiary_json = json.dumps(tertiary_paths)
    
    # Формируем JavaScript-код с различными приоритетами загрузки
    js_code = f"""
    <script>
        // Функция для предварительной загрузки критически важных изображений (немедленно)
        function preloadCriticalImages() {{
            // Критически важные изображения для немедленной загрузки
            const criticalImages = {critical_json};
            
            if (criticalImages.length === 0) return;
            
            // Загружаем с высоким приоритетом
            criticalImages.forEach(src => {{
                const img = new Image();
                img.src = src;
                img.fetchpriority = 'high';
                img.importance = 'high';
            }});
            
            console.log("🚀 Подготовлено " + criticalImages.length + " критически важных изображений");
        }}
        
        // Функция для загрузки второстепенных изображений (после загрузки страницы)
        function preloadSecondaryImages() {{
            // Второстепенные изображения
            const secondaryImages = {secondary_json};
            
            if (secondaryImages.length === 0) return;
            
            // Загружаем с обычным приоритетом после загрузки страницы
            secondaryImages.forEach(src => {{
                const img = new Image();
                img.src = src;
                img.loading = 'lazy';
            }});
            
            console.log("📦 Подготовлено " + secondaryImages.length + " второстепенных изображений");
        }}
        
        // Функция для отложенной загрузки дополнительных изображений 
        function preloadTertiaryImages() {{
            // Дополнительные изображения
            const tertiaryImages = {tertiary_json};
            
            if (tertiaryImages.length === 0) return;
            
            // Используем requestIdleCallback для загрузки в период простоя
            const loadMethod = window.requestIdleCallback || 
                ((callback) => setTimeout(callback, 2000));
            
            loadMethod(() => {{
                tertiaryImages.forEach((src, index) => {{
                    // Загружаем с задержкой для снижения нагрузки
                    setTimeout(() => {{
                        const img = new Image();
                        img.src = src;
                        img.loading = 'lazy';
                        img.fetchpriority = 'low';
                    }}, index * 100);
                }});
                
                console.log("🔄 Подготовлено " + tertiaryImages.length + " дополнительных изображений");
            }});
        }}
        
        // Запускаем критическую загрузку немедленно
        preloadCriticalImages();
        
        // После загрузки DOM запускаем второстепенную загрузку 
        document.addEventListener('DOMContentLoaded', function() {{
            // Оптимизируем загрузку WebFont
            if ('fonts' in document) {{
                document.fonts.ready.then(function () {{
                    console.log("✅ Шрифты загружены");
                }}).catch(function() {{
                    console.log("⚠️ Не удалось загрузить все шрифты");
                }});
            }}
            
            // Загружаем второстепенные ресурсы
            setTimeout(preloadSecondaryImages, 300);
        }});
        
        // После полной загрузки страницы загружаем дополнительные ресурсы
        window.addEventListener('load', function() {{
            setTimeout(preloadTertiaryImages, 1000);
            
            // Оптимизируем все изображения на странице
            document.querySelectorAll('img').forEach(img => {{
                if (!img.hasAttribute('loading') && !img.complete) {{
                    img.loading = 'lazy';
                }}
            }});
        }});
    </script>
    """
    
    return js_code

def optimize_form_rendering():
    """
    Предоставляет JavaScript код для ускорения отображения формы ввода.
    Особенно полезно при отображении в iframe.
    
    Returns:
        str: JavaScript код для оптимизации форм
    """
    
    js_code = """
    <script>
        // Функция для оптимизации загрузки и отображения форм
        function optimizeFormRendering() {
            // Создаем обертку для отслеживания загрузки и настройки производительности
            const perfObserver = window.PerformanceObserver 
                ? new PerformanceObserver((list) => {
                      // Анализ метрик для оптимизации
                      const entries = list.getEntries();
                      if (entries.length > 0) {
                          console.log("📊 Форма отрисована за", 
                              entries[0].startTime.toFixed(2) + "ms");
                      }
                  }) 
                : null;
            
            // Начинаем измерение, если доступно
            if (perfObserver) {
                perfObserver.observe({type: 'paint', buffered: true});
            }
            
            // Функция для автоматического обновления высоты iframe
            function updateIframeHeight() {
                // Если приложение в iframe, сообщаем родителю новую высоту
                if (window.parent && window !== window.parent) {
                    const height = document.body.scrollHeight;
                    window.parent.postMessage({
                        type: 'set-iframe-height',
                        height: height + 20
                    }, '*');
                }
            }
            
            // Оптимизация критических элементов формы
            function optimizeCriticalFormElements() {
                // Находим критические элементы
                const formElements = document.querySelectorAll('input, select, button');
                
                // Устанавливаем высокий приоритет рендеринга для них
                formElements.forEach(elem => {
                    elem.style.containIntrinsicSize = 'auto';
                    if (elem.tagName === 'BUTTON' 
                        && (elem.innerText.includes('Рассчитать') || elem.innerText.includes('Расчёт'))) {
                        // Выделяем кнопку расчета
                        elem.style.boxShadow = '0 0 8px rgba(63, 109, 170, 0.6)';
                        elem.style.transform = 'scale(1.02)';
                    }
                });
                
                // Добавляем визуальные подсказки
                const hintElement = document.createElement('div');
                hintElement.innerHTML = '<small style="color:#777">Нажмите Tab для быстрой навигации</small>';
                hintElement.style.textAlign = 'center';
                hintElement.style.marginTop = '5px';
                hintElement.style.opacity = '0';
                document.body.appendChild(hintElement);
                
                // Плавно показываем подсказку через 2 секунды
                setTimeout(() => {
                    hintElement.style.transition = 'opacity 0.5s';
                    hintElement.style.opacity = '1';
                    
                    // Скрываем через 5 секунд
                    setTimeout(() => {
                        hintElement.style.opacity = '0';
                    }, 5000);
                }, 2000);
            }
            
            // Запускаем оптимизацию форм после загрузки DOM
            document.addEventListener('DOMContentLoaded', function() {
                // Запускаем оптимизацию формы с небольшой задержкой
                setTimeout(optimizeCriticalFormElements, 100);
                
                // Обновляем высоту iframe
                setTimeout(updateIframeHeight, 300);
            });
            
            // Обновляем высоту при изменении размеров окна
            window.addEventListener('resize', updateIframeHeight);
            
            // Отслеживаем изменения DOM и обновляем высоту iframe
            const observer = new MutationObserver(function() {
                updateIframeHeight();
            });
            
            // Запускаем наблюдение за изменениями DOM
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            });
        }
        
        // Запускаем функцию оптимизации загрузки формы
        optimizeFormRendering();
    </script>
    """
    
    return js_code

def add_page_speed_optimizations():
    """
    Добавляет комплексные оптимизации для ускорения загрузки страницы.
    
    Returns:
        str: HTML-код с оптимизациями для добавления в страницу
    """
    
    optimization_js = """
    <script>
        // Отключаем все неиспользуемые анимации на загрузке
        document.documentElement.classList.add('streamlit-loading-optimization');
        
        // Устанавливаем критический CSS напрямую для ускорения рендеринга
        const criticalCSS = `
            .stApp {
                opacity: 1 !important;
                animation: none !important;
            }
            .streamlit-loading-optimization * {
                transition: none !important;
                animation-duration: 0ms !important;
            }
            .stButton button {
                transition: transform 0.2s, box-shadow 0.2s !important;
            }
            @media (max-width: 768px) {
                .stNumberInput input {
                    font-size: 16px !important; /* Предотвращает зум на мобильных */
                }
            }
        `;
        
        // Добавляем критический CSS в head
        const style = document.createElement('style');
        style.textContent = criticalCSS;
        document.head.appendChild(style);
        
        // Убираем класс оптимизации после полной загрузки
        window.addEventListener('load', function() {
            setTimeout(() => {
                document.documentElement.classList.remove('streamlit-loading-optimization');
            }, 500);
        });
        
        // Оптимизация взаимодействия
        document.addEventListener('DOMContentLoaded', function() {
            // Предотвращаем ненужные перерисовки
            const debounce = (fn, delay) => {
                let timer;
                return function(...args) {
                    clearTimeout(timer);
                    timer = setTimeout(() => fn.apply(this, args), delay);
                };
            };
            
            // Оптимизация для iFrame
            if (window.parent && window !== window.parent) {
                // Отключаем сложные анимации в iframe
                document.body.classList.add('in-iframe');
            }
        });
    </script>
    """
    
    # Объединяем все оптимизации
    meta_tags = """
    <meta http-equiv="Cache-Control" content="max-age=86400, must-revalidate">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    """
    
    return meta_tags + optimization_js