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

def create_scroll_target(target_id, label=None, height_px=80):
    """
    Создает цель для скроллинга с поддержкой Python-механизма скроллинга.
    
    Args:
        target_id (str): Идентификатор якоря
        label (str, optional): Дополнительный текст для отладки
        height_px (int): Высота якоря в пикселях
    """
    # Создаем очень простой якорь, но с явной видимостью для отладки
    st.markdown(
        f"""
        <div id="{target_id}" 
             class="streamlit-scroll-target"
             style="position: relative; 
                    display: block; 
                    width: 100%; 
                    height: {height_px}px; 
                    border-top: 2px solid #e0e0e0;
                    margin-top: 5px;
                    margin-bottom: 5px;
                    padding-top: 5px;
                    scroll-margin-top: 100px;">
            <span style="position: absolute; 
                         left: 0; right: 0; 
                         text-align: center; 
                         font-size: 0.7rem; 
                         color: #888;
                         padding: 2px;
                         user-select: none;">
                {label if label else f"Раздел: {target_id}"}
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Проверяем наличие флага скроллинга именно для этого якоря
    need_scroll = (
        '_scroll_to_target' in st.session_state and 
        st.session_state['_scroll_to_target'] == target_id
    )
    
    if need_scroll:
        # Очищаем флаг
        if '_scroll_to_target' in st.session_state:
            del st.session_state['_scroll_to_target']
        
        print(f">>> [PYTHON_SCROLL] Активирован скроллинг к цели {target_id}")
        
        # Создаем улучшенную функцию для гарантированного скроллинга
        st.markdown(f"""
        <script>
            (function() {{
                // Функция для надежного скроллинга
                function reliableScrollTo(elementId) {{
                    try {{
                        const targetElement = document.getElementById('{target_id}');
                        if (!targetElement) {{
                            console.error('Элемент {target_id} не найден!');
                            return false;
                        }}
                        
                        // Получаем координаты элемента
                        const rect = targetElement.getBoundingClientRect();
                        const absoluteY = rect.top + window.pageYOffset;
                        
                        // Скроллим с небольшим отступом сверху
                        window.scrollTo({{
                            top: absoluteY - 100,
                            behavior: 'smooth'
                        }});
                        
                        console.log('ВЫПОЛНЕН СКРОЛЛ К ЭЛЕМЕНТУ {target_id}:', absoluteY);
                        
                        // Добавляем подсветку на время, чтобы пользователь увидел якорь
                        targetElement.style.borderTop = '2px solid #0066cc';
                        targetElement.style.backgroundColor = 'rgba(0, 102, 204, 0.1)';
                        
                        // Через 2 секунды убираем подсветку
                        setTimeout(() => {{
                            targetElement.style.borderTop = '2px solid #e0e0e0';
                            targetElement.style.backgroundColor = 'transparent';
                        }}, 2000);
                        
                        return true;
                    }} catch (error) {{
                        console.error('Ошибка при скроллинге:', error);
                        return false;
                    }}
                }}
                
                // Запускаем скроллинг несколько раз для надежности
                console.log('Запланирован скроллинг к элементу {target_id}');
                setTimeout(() => reliableScrollTo('{target_id}'), 300);
                setTimeout(() => reliableScrollTo('{target_id}'), 700);
                setTimeout(() => reliableScrollTo('{target_id}'), 1200);
                setTimeout(() => reliableScrollTo('{target_id}'), 2000);
            }})();
        </script>
        """, unsafe_allow_html=True)
        
        # Добавляем заметное уведомление
        st.markdown(f"""
        <div style="margin: 10px 0; padding: 10px; 
                    background-color: rgba(0, 102, 204, 0.1); 
                    border-left: 3px solid #0066cc; 
                    font-weight: bold; 
                    text-align: center;">
            {label if label else "Результаты расчета готовы"}
        </div>
        """, unsafe_allow_html=True)

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
    # Задаем специальный идентификатор target_id для якоря в session_state
    st.session_state['_scroll_to_target'] = target_id
    
    # Добавляем метку времени для проверки актуальности
    st.session_state['_scroll_timestamp'] = time.time()
    
    # Выводим специальный маркер для отладки
    print(f">>> [AUTO_SCROLL] Включен автоматический скроллинг к якорю {target_id}")
    
    # Используем более мощный JavaScript для надежного скроллинга
    st.markdown(f"""
    <div id="auto-scroll-marker-{int(time.time() * 1000)}" 
         data-target="{target_id}"
         style="display:none;">
    </div>
    
    <script>
        // Функция для гарантированного скроллинга
        function smoothScrollToTarget(targetId, attempts = 0) {{
            const target = document.getElementById(targetId);
            if (target) {{
                console.log('Найден элемент для скроллинга:', targetId);
                const rect = target.getBoundingClientRect();
                const targetTop = rect.top + window.pageYOffset;
                
                window.scrollTo({{
                    top: targetTop - 100,
                    behavior: 'smooth'
                }});
                
                console.log('Выполнен скролл к якорю ' + targetId + ' на позицию ' + targetTop);
                return true;
            }} else if (attempts < 10) {{
                console.log('Элемент ' + targetId + ' еще не найден, повторная попытка...');
                setTimeout(() => smoothScrollToTarget(targetId, attempts + 1), 200);
            }} else {{
                console.error('Не удалось найти элемент ' + targetId + ' после 10 попыток');
            }}
        }}
            
        // Запуск скроллинга с задержкой
        console.log('Запланирован скроллинг к элементу {target_id}');
        setTimeout(() => smoothScrollToTarget('{target_id}'), 300);
        setTimeout(() => smoothScrollToTarget('{target_id}'), 800);
        setTimeout(() => smoothScrollToTarget('{target_id}'), 1500);
    </script>
    """, unsafe_allow_html=True)

def handle_calculation_scroll():
    """
    Проверяет, нужно ли выполнить скролл к результатам.
    Вызывается в начале приложения.
    
    Returns:
        bool: True если скролл был выполнен
    """
    # Проверяем наличие результатов и флага для скролла
    has_results = 'results' in st.session_state
    needs_scroll = st.session_state.get('need_scroll_to_results', False)
    
    print(f">>> handle_calculation_scroll: has_results={has_results}, needs_scroll={needs_scroll}")
    
    if has_results and needs_scroll:
        # Сбрасываем флаг скролла
        st.session_state.need_scroll_to_results = False
        
        # Устанавливаем флаг для скролла к якорю
        print(">>> Установка флага для скролла к результатам...")
        
        # Выводим отладочное сообщение
        st.info("Выполняется автоматический скролл к результатам...")
        
        # Устанавливаем флаг для скролла через механизм Python
        auto_scroll_on_load('calculation-results')
        
        # Сохраняем информацию, что скролл был выполнен
        st.session_state['_scroll_performed'] = True
        st.session_state['_scroll_timestamp'] = time.time()
        
        return True
    
    # Проверяем, был ли выполнен скролл в последние 5 секунд
    if has_results and st.session_state.get('_scroll_performed', False):
        # Проверяем, не истекло ли время
        timestamp = st.session_state.get('_scroll_timestamp', 0)
        if time.time() - timestamp < 5:  # Если прошло менее 5 секунд
            print(">>> Повторная попытка скролла (в течение 5 сек после первой)")
            auto_scroll_on_load('calculation-results')
            return True
        else:
            # Сбрасываем флаг, если прошло более 5 секунд
            st.session_state['_scroll_performed'] = False
            
    return False