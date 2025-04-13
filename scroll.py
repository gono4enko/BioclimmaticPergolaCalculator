"""
Модуль для плавного скроллинга к элементам страницы с использованием кастомных компонентов
"""
import streamlit as st 
from streamlit.components.v1 import html

def smooth_scroll_to(target_id):
    """
    Выполняет плавный скролл к элементу с указанным ID
    
    Args:
        target_id (str): ID элемента для скролла
        
    Returns:
        None: Вставляет JS-скрипт непосредственно в страницу
    """
    scroll_code = f"""
    <script type="text/javascript">
        (function() {{
            // Выводим подробные логи для отладки
            console.log("🎯 SCROLL: Компонент smooth_scroll_to запущен, цель #{target_id}");
            
            // Константы
            const MAX_ATTEMPTS = 20; // максимум попыток
            const TARGET_ID = "{target_id}";
            
            // Функция для проверки наличия элемента и выполнения скролла
            const tryScrollToElement = (currentAttempt) => {{
                
                if (currentAttempt > MAX_ATTEMPTS) {{
                    console.log(`🎯 SCROLL: Превышено максимальное количество попыток (${{MAX_ATTEMPTS}}), прекращаю поиск элемента`);
                    return;
                }}
                
                console.log(`🎯 SCROLL: Попытка #${{currentAttempt}} найти элемент #${{TARGET_ID}}`);
                
                const targetElement = document.getElementById(TARGET_ID);
                if (targetElement) {{
                    console.log(`🎯 SCROLL: ✅ Элемент #${{TARGET_ID}} найден на попытке #${{currentAttempt}}`);
                    
                    // Добавим подсветку для наглядности (только для отладки)
                    targetElement.style.backgroundColor = "#e6f2ff";
                    targetElement.style.transition = "background-color 2s";
                    
                    // Используем оба метода для скролла с разной задержкой для надежности
                    setTimeout(() => {{
                        try {{
                            // Метод 1: scrollIntoView
                            targetElement.scrollIntoView({{ behavior: "smooth", block: "start" }});
                            console.log("🎯 SCROLL: scrollIntoView выполнен");
                            
                            // Дублируем скролл через window.scrollTo для надежности
                            setTimeout(() => {{
                                try {{
                                    // Метод 2: window.scrollTo
                                    const yOffset = -20; // немного выше, чем сам элемент для лучшей видимости
                                    const elementY = targetElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
                                    
                                    window.scrollTo({{
                                        top: elementY,
                                        behavior: 'smooth'
                                    }});
                                    console.log(`🎯 SCROLL: window.scrollTo выполнен на позицию ${{elementY}}px`);
                                    
                                    // Последняя попытка с прямым присвоением (для старых браузеров)
                                    setTimeout(() => {{
                                        try {{
                                            const finalY = targetElement.getBoundingClientRect().top + window.pageYOffset - 30;
                                            window.scrollTo(0, finalY);
                                            console.log(`🎯 SCROLL: Финальный скролл на ${{finalY}}px выполнен`);
                                        }} catch (finalErr) {{
                                            console.error("Ошибка финального скролла:", finalErr);
                                        }}
                                    }}, 300);
                                    
                                }} catch (scrollError) {{
                                    console.error(`🎯 SCROLL: Ошибка в window.scrollTo: ${{scrollError.message}}`);
                                }}
                            }}, 200);
                            
                        }} catch (viewError) {{
                            console.error(`🎯 SCROLL: Ошибка в scrollIntoView: ${{viewError.message}}`);
                        }}
                        
                        // Через 2 секунды убираем подсветку
                        setTimeout(() => {{
                            targetElement.style.backgroundColor = "transparent";
                        }}, 2000);
                        
                    }}, 150);
                    
                }} else {{
                    console.log(`🎯 SCROLL: Элемент #${{TARGET_ID}} не найден на попытке #${{currentAttempt}}, повторю попытку...`);
                    // Рекурсивно пробуем снова с увеличенным счетчиком
                    setTimeout(() => {{
                        tryScrollToElement(currentAttempt + 1);
                    }}, 200); // Интервал между попытками
                }}
            }};
            
            // Запускаем первую попытку с небольшой задержкой
            setTimeout(() => {{
                tryScrollToElement(1);
            }}, 700); // Увеличенная задержка для полной загрузки DOM
        }})();
    </script>
    """
    
    # Используем height=10, чтобы убедиться, что компонент не будет удален garbage collector'ом
    html(scroll_code, height=10)