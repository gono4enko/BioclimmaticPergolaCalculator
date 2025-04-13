"""
Модуль для плавного скроллинга к элементам страницы с использованием кастомных компонентов
и альтернативных методов с прямыми координатами для критических случаев
"""
import streamlit as st 
from streamlit.components.v1 import html

def smooth_scroll_to(target_id, fixed_y_position=None):
    """
    Выполняет плавный скролл к элементу с указанным ID
    или к фиксированной Y-координате, если указана
    
    Args:
        target_id (str): ID элемента для скролла
        fixed_y_position (int, optional): Фиксированная Y-координата для скролла,
                                         игнорирует target_id если указана
        
    Returns:
        None: Вставляет JS-скрипт непосредственно в страницу
    """
    # Если указана фиксированная позиция, используем прямое указание координат
    if fixed_y_position is not None:
        fixed_y_scroll_code = f"""
        <script type="text/javascript">
            (function() {{
                console.log("🎯 SCROLL: Выполняется скролл к фиксированной позиции Y={fixed_y_position}px");
                
                // Серия попыток скролла к фиксированной позиции
                const scrollAttempts = [200, 500, 1000, 1500, 2000];
                
                // Функция скролла с минимальной анимацией для надежности
                const scrollToFixedY = (delay) => {{
                    setTimeout(() => {{
                        try {{
                            window.scrollTo({{
                                top: {fixed_y_position},
                                behavior: 'smooth'
                            }});
                            console.log(`🎯 SCROLL: Выполнен скролл к Y={fixed_y_position}px (задержка ${delay}мс)`);
                        }} catch(e) {{
                            console.error(`🎯 SCROLL: Ошибка при скролле к Y={fixed_y_position}px:`, e);
                            
                            // Запасной вариант для старых браузеров
                            try {{
                                window.scrollTo(0, {fixed_y_position});
                                console.log(`🎯 SCROLL: Выполнен прямой скролл к Y={fixed_y_position}px`);
                            }} catch(e2) {{
                                console.error(`🎯 SCROLL: Ошибка при прямом скролле:`, e2);
                            }}
                        }}
                    }}, delay);
                }};
                
                // Запускаем несколько попыток скролла с разными задержками
                scrollAttempts.forEach(delay => scrollToFixedY(delay));
                
                // Создаем мигающий маркер для визуальной индикации
                setTimeout(() => {{
                    const marker = document.createElement('div');
                    marker.style.position = 'absolute';
                    marker.style.left = '0';
                    marker.style.top = `${{{fixed_y_position}}}px`;
                    marker.style.width = '100%';
                    marker.style.height = '5px';
                    marker.style.backgroundColor = '#0066cc';
                    marker.style.zIndex = '9999';
                    marker.style.opacity = '0.7';
                    marker.style.animation = 'pulse 1.5s infinite';
                    
                    // Добавляем стиль анимации
                    const style = document.createElement('style');
                    style.textContent = `
                        @keyframes pulse {{
                            0% {{ opacity: 0.7; }}
                            50% {{ opacity: 0.3; }}
                            100% {{ opacity: 0.7; }}
                        }}
                    `;
                    
                    document.head.appendChild(style);
                    document.body.appendChild(marker);
                    
                    // Удаляем маркер через 5 секунд
                    setTimeout(() => {{
                        marker.remove();
                        style.remove();
                    }}, 5000);
                }}, 500);
            }})();
        </script>
        """
        html(fixed_y_scroll_code, height=10)
        return
    
    # Обычный скролл по ID элемента (модифицированный для повышенной надежности)
    scroll_code = f"""
    <script type="text/javascript">
        (function() {{
            // Выводим подробные логи для отладки
            console.log("🎯 SCROLL: Компонент smooth_scroll_to запущен (новая версия), цель #{target_id}");
            
            // Константы
            const MAX_ATTEMPTS = 25; // увеличили максимум попыток
            const TARGET_ID = "{target_id}";
            const RETRY_INTERVAL = 200; // интервал между попытками, мс
            
            // Функция для скролла по имени класса (запасной вариант)
            const tryScrollByClassName = (className) => {{
                const elements = document.getElementsByClassName(className);
                if (elements && elements.length > 0) {{
                    const element = elements[0];
                    console.log(`🎯 SCROLL: Найден элемент по классу ${{className}}`);
                    
                    try {{
                        const y = element.getBoundingClientRect().top + window.pageYOffset - 30;
                        window.scrollTo({{top: y, behavior: 'smooth'}});
                        console.log(`🎯 SCROLL: Выполнен скролл к элементу по классу ${{className}}`);
                        return true;
                    }} catch(e) {{
                        console.error(`🎯 SCROLL: Ошибка при скролле к элементу по классу:`, e);
                    }}
                }}
                return false;
            }};
            
            // Функция прямого скролла к фиксированной позиции (еще один запасной вариант)
            const directScrollToPosition = (yPos) => {{
                try {{
                    window.scrollTo({{top: yPos, behavior: 'smooth'}});
                    console.log(`🎯 SCROLL: Выполнен прямой скролл к позиции ${{yPos}}px`);
                    return true;
                }} catch(e) {{
                    console.error(`🎯 SCROLL: Ошибка при прямом скролле:`, e);
                    return false;
                }}
            }};
            
            // Функция для проверки наличия элемента и выполнения скролла
            const tryScrollToElement = (currentAttempt) => {{
                
                if (currentAttempt > MAX_ATTEMPTS) {{
                    console.log(`🎯 SCROLL: Превышено максимальное количество попыток (${{MAX_ATTEMPTS}}), переход к запасным вариантам`);
                    
                    // Запасной вариант 1: поиск по классу results-marker
                    if (tryScrollByClassName('results-marker')) return;
                    
                    // Запасной вариант 2: поиск заголовка "Результаты расчета"
                    const headers = document.querySelectorAll('h2, h3');
                    for (let i = 0; i < headers.length; i++) {{
                        if (headers[i].textContent.includes('Результаты расчета')) {{
                            try {{
                                const y = headers[i].getBoundingClientRect().top + window.pageYOffset - 50;
                                directScrollToPosition(y);
                                return;
                            }} catch(e) {{
                                console.error(`🎯 SCROLL: Ошибка при скролле к заголовку:`, e);
                            }}
                        }}
                    }}
                    
                    // Запасной вариант 3: скролл к фиксированной позиции
                    directScrollToPosition(800); // Примерная позиция блока результатов
                    
                    return;
                }}
                
                console.log(`🎯 SCROLL: Попытка #${{currentAttempt}} найти элемент #${{TARGET_ID}}`);
                
                const targetElement = document.getElementById(TARGET_ID);
                if (targetElement) {{
                    console.log(`🎯 SCROLL: ✅ Элемент #${{TARGET_ID}} найден на попытке #${{currentAttempt}}`);
                    
                    // Улучшенное визуальное выделение элемента
                    targetElement.style.backgroundColor = "#e6f2ff";
                    targetElement.style.transition = "all 1s ease";
                    targetElement.style.boxShadow = "0 0 15px rgba(0, 102, 204, 0.7)";
                    targetElement.style.borderRadius = "5px";
                    
                    // Используем несколько методов для скролла с разной задержкой
                    const scrollMethods = [
                        // Метод 1: scrollIntoView
                        () => {{
                            try {{
                                targetElement.scrollIntoView({{ behavior: "smooth", block: "start" }});
                                console.log(`🎯 SCROLL: scrollIntoView выполнен`);
                            }} catch (e) {{
                                console.error(`🎯 SCROLL: Ошибка scrollIntoView:`, e);
                            }}
                        }},
                        
                        // Метод 2: window.scrollTo с координатами элемента
                        () => {{
                            try {{
                                const y = targetElement.getBoundingClientRect().top + window.pageYOffset - 20;
                                window.scrollTo({{ top: y, behavior: 'smooth' }});
                                console.log(`🎯 SCROLL: scrollTo(${{y}}) выполнен`);
                            }} catch (e) {{
                                console.error(`🎯 SCROLL: Ошибка scrollTo:`, e);
                            }}
                        }},
                        
                        // Метод 3: прямое присвоение scrollTop
                        () => {{
                            try {{
                                const y = targetElement.getBoundingClientRect().top + window.pageYOffset - 20;
                                document.documentElement.scrollTop = y;
                                document.body.scrollTop = y; // Для старых браузеров
                                console.log(`🎯 SCROLL: document.body.scrollTop = ${{y}} выполнен`);
                            }} catch (e) {{
                                console.error(`🎯 SCROLL: Ошибка scrollTop:`, e);
                            }}
                        }}
                    ];
                    
                    // Запускаем методы с разной задержкой
                    scrollMethods.forEach((method, index) => {{
                        setTimeout(method, 300 * (index + 1));
                    }});
                    
                    // Удаляем подсветку через 5 секунд
                    setTimeout(() => {{
                        targetElement.style.backgroundColor = "transparent";
                        targetElement.style.boxShadow = "none";
                    }}, 5000);
                    
                }} else {{
                    console.log(`🎯 SCROLL: Элемент #${{TARGET_ID}} не найден на попытке #${{currentAttempt}}, повторяю...`);
                    // Повторяем поиск элемента
                    setTimeout(() => {{
                        tryScrollToElement(currentAttempt + 1);
                    }}, RETRY_INTERVAL);
                }}
            }};
            
            // Запускаем первую попытку с большей задержкой для полной загрузки DOM
            setTimeout(() => {{
                tryScrollToElement(1);
            }}, 1000);
        }})();
    </script>
    """
    
    # Используем height=20, чтобы компонент гарантированно не был удален
    html(scroll_code, height=20)