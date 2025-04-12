"""
Модуль для управления скроллингом в Streamlit приложении
Решает проблему автоматического скроллинга к результатам после расчета
"""
import streamlit as st
import time

def setup_scroll_functionality():
    """
    Настраивает базовые функции для скроллинга.
    Вызывается один раз при инициализации приложения.
    """
    # Глобальные стили и скрипты для скроллинга
    st.markdown("""
    <style>
    /* Обеспечиваем плавный скроллинг на всей странице */
    html {
        scroll-behavior: smooth;
    }
    
    /* Стили для якорей скроллинга */
    .scroll-target {
        scroll-margin-top: 70px;
        position: relative;
    }
    
    /* Класс для интерфейса с анимацией появления */
    .scroll-appear {
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate3d(0, 30px, 0);
        }
        to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
    }
    </style>
    
    <script>
    // Функция для программного скроллинга
    function scrollToElementById(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            return true;
        }
        return false;
    }
    </script>
    """, unsafe_allow_html=True)

def create_scroll_target(target_id, label=None, height_px=20):
    """
    Создает цель для скроллинга с поддержкой Python-механизма скроллинга.
    
    Args:
        target_id (str): Идентификатор якоря
        label (str, optional): Дополнительный текст для отладки
        height_px (int): Высота якоря в пикселях
    """
    display_text = ""
    if label:
        display_text = f"<span style='display:none;'>{label}</span>"
    
    # Создаем якорь для скроллинга
    st.markdown(
        f"""<div id="{target_id}" 
             class="scroll-target" 
             style="height:{height_px}px; visibility:hidden; margin-top:-60px; position:relative">
             {display_text}
        </div>""", 
        unsafe_allow_html=True
    )
    
    # Проверяем, нужно ли скроллить к этому элементу сразу
    if '_scroll_to' in st.session_state and st.session_state['_scroll_to'] == target_id:
        print(f"*** create_scroll_target: Найдена цель для автоматического скролла: {target_id}")
        
        # Удаляем флаг скроллинга
        del st.session_state['_scroll_to']
        
        # Добавляем JavaScript для программного скролла
        st.markdown(
            f"""
            <script>
                (function() {{
                    function scrollToTarget() {{
                        try {{
                            const element = document.getElementById("{target_id}");
                            if (element) {{
                                console.log("Python triggered scroll to {target_id}");
                                element.scrollIntoView({{
                                    behavior: 'smooth',
                                    block: 'start'
                                }});
                                return true;
                            }}
                            console.log("Element {target_id} not found for scrolling");
                            return false;
                        }} catch(e) {{
                            console.error("Error scrolling to {target_id}:", e);
                            return false;
                        }}
                    }}
                    
                    // Попытка прокрутки с разной задержкой для надежности
                    setTimeout(scrollToTarget, 100);
                    setTimeout(scrollToTarget, 500);
                    setTimeout(scrollToTarget, 1000);
                }})();
            </script>
            """,
            unsafe_allow_html=True
        )

def create_scroll_button(text, target_id, variant="primary", use_container_width=True):
    """
    Создает кнопку для скроллинга к указанному якорю.
    Возвращает True если кнопка нажата.
    
    Args:
        text (str): Текст кнопки
        target_id (str): ID якоря для скролла
        variant (str): Вариант кнопки ('primary', 'secondary', etc.)
        use_container_width (bool): Растягивать по ширине контейнера
        
    Returns:
        bool: True если кнопка нажата
    """
    # Создаем обычную кнопку Streamlit
    button_key = f"scroll_btn_{target_id}_{int(time.time() * 1000)}"
    clicked = st.button(
        text, 
        key=button_key,
        type=variant,
        use_container_width=use_container_width
    )
    
    # Если кнопка нажата, добавляем JS для скроллинга
    if clicked:
        trigger_scroll_to(target_id)
        
    return clicked

def trigger_scroll_to(target_id):
    """
    Выполняет программный скролл к указанному якорю
    
    Args:
        target_id (str): ID якоря для скролла
    """
    # Вставляем JavaScript для выполнения скролла
    st.markdown(
        f"""
        <script>
            // Используем setTimeout для гарантии, что DOM загружен
            setTimeout(function() {{
                scrollToElementById("{target_id}");
            }}, 100);
            
            // Резервный вариант с большей задержкой
            setTimeout(function() {{
                scrollToElementById("{target_id}");
            }}, 500);
            
            // Еще один резервный вариант
            setTimeout(function() {{
                const element = document.getElementById("{target_id}");
                if (element) {{
                    const rect = element.getBoundingClientRect();
                    const absoluteElementTop = rect.top + window.pageYOffset;
                    window.scrollTo({{
                        top: absoluteElementTop - 70,
                        behavior: 'smooth'
                    }});
                }}
            }}, 800);
        </script>
        """, 
        unsafe_allow_html=True
    )

def auto_scroll_on_load(target_id):
    """
    Выполняет автоматический скролл сразу после загрузки страницы.
    Используется, когда страница перезагружается после расчета.
    
    Args:
        target_id (str): ID якоря для скролла
    
    Note:
        Реализует скроллинг с помощью Python-механизма,
        используя session_state для отслеживания состояния.
    """
    # Добавляем маркер в session_state
    st.session_state['_scroll_to'] = target_id
    
    # Выводим информационное сообщение в лог для отладки
    print(f"*** auto_scroll_on_load: Установлен флаг _scroll_to для {target_id}")
    
    # Создаем минимальную JavaScript-функцию для логирования (без скролла)
    st.markdown(
        f"""
        <script>
            console.log("Python-based scroll targeting {target_id} is ready");
        </script>
        """, 
        unsafe_allow_html=True
    )
    
    # Добавляем отметку на странице, чтобы знать, что скролл должен сработать
    st.markdown(
        f"""
        <div id="scroll-marker-{target_id}" 
             style="position: absolute; width: 1px; height: 1px; 
                   pointer-events: none; opacity: 0;"
             data-target="{target_id}" data-scroll-ready="true">
        </div>
        """,
        unsafe_allow_html=True
    )

def handle_calculation_scroll():
    """
    Проверяет, нужно ли выполнить скролл к результатам.
    Вызывается в начале приложения.
    
    Returns:
        bool: True если скролл был выполнен
    """
    if 'results' in st.session_state and st.session_state.get('need_scroll_to_results', False):
        # Сбрасываем флаг
        st.session_state.need_scroll_to_results = False
        # Выполняем автоматический скролл
        auto_scroll_on_load('calculation-results')
        return True
        
    return False