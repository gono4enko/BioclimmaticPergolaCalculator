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

def create_scroll_target(target_id, label=None, height_px=1):
    """
    Создает невидимую цель для скроллинга.
    
    Args:
        target_id (str): Идентификатор якоря
        label (str, optional): Дополнительный текст для отладки
        height_px (int): Высота якоря в пикселях
    """
    display_text = ""
    if label:
        display_text = f"<span style='display:none;'>{label}</span>"
        
    st.markdown(
        f"""<div id="{target_id}" 
             class="scroll-target" 
             style="height:{height_px}px; visibility:hidden; margin-top:-70px;">
             {display_text}
        </div>""", 
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
    """
    trigger_scroll_to(target_id)

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