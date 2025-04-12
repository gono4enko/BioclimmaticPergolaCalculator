"""
Модуль реализует скроллинг на чистом питоне через хранение состояний
и перезагрузку страницы с передачей якоря.
"""
import streamlit as st
import time

def set_page_anchor(anchor_id):
    """
    Устанавливает якорь для текущей страницы.
    После этого страница будет перезагружена и прокручена к указанному якорю.
    
    Args:
        anchor_id (str): Идентификатор якоря, к которому нужно прокрутить страницу
    """
    # Сохраняем ID якоря в session_state
    st.session_state['_scroll_anchor'] = anchor_id
    st.session_state['_scroll_timestamp'] = time.time()
    
    # Используем встроенную функцию перезагрузки Streamlit
    st.rerun()

def create_anchor_element(anchor_id, label=None, show_border=True):
    """
    Создает HTML-элемент якоря, к которому можно прокрутить страницу.
    
    Args:
        anchor_id (str): Идентификатор якоря
        label (str, optional): Текст метки для якоря
        show_border (bool): Показывать ли границу якоря
    """
    border_style = "border-top: 2px solid #0066cc;" if show_border else ""
    bg_color = "background-color: rgba(0, 102, 204, 0.05);" if show_border else ""
    
    anchor_html = f"""
    <div id="{anchor_id}" 
         style="position: relative; 
                width: 100%; 
                height: 40px;
                margin-top: 15px;
                {border_style}
                {bg_color}
                padding-top: 5px;">
    """
    
    if label:
        anchor_html += f"""
        <span style="position: absolute; 
                     top: 5px;
                     left: 0; right: 0; 
                     text-align: center; 
                     font-size: 0.75rem; 
                     color: #555;
                     padding: 2px;">
            {label}
        </span>
        """
    
    anchor_html += "</div>"
    
    # Отображаем якорь
    st.markdown(anchor_html, unsafe_allow_html=True)

def check_scroll_anchor():
    """
    Проверяет, нужно ли прокрутить страницу к якорю.
    Должна вызываться в начале приложения.
    
    Returns:
        bool: True если был выполнен скролл, иначе False
    """
    if '_scroll_anchor' in st.session_state and '_scroll_timestamp' in st.session_state:
        anchor_id = st.session_state['_scroll_anchor']
        timestamp = st.session_state['_scroll_timestamp']
        
        # Проверяем, не устарел ли якорь (5 секунд)
        if time.time() - timestamp > 5:
            # Удаляем устаревший якорь
            del st.session_state['_scroll_anchor']
            del st.session_state['_scroll_timestamp']
            return False
        
        # Добавляем уведомление для пользователя
        st.markdown(f"""
        <div style="padding: 10px; 
                    background-color: #e6f2ff; 
                    border-left: 3px solid #0066cc; 
                    margin-bottom: 15px;">
            <p style="margin: 0; padding: 0; text-align: center;">
                <b>Перемещение к разделу</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Добавляем JavaScript для прокрутки к якорю
        scroll_script = f"""
        <script>
            function scrollToAnchor() {{
                try {{
                    const element = document.getElementById('{anchor_id}');
                    if (element) {{
                        // Прокручиваем к элементу
                        element.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                        
                        // Добавляем подсветку
                        element.style.backgroundColor = 'rgba(0, 102, 204, 0.1)';
                        element.style.borderTop = '2px solid #0066cc';
                        
                        // Через 3 секунды убираем подсветку
                        setTimeout(function() {{
                            element.style.backgroundColor = '';
                            element.style.borderTop = '';
                        }}, 3000);
                        
                        console.log('Прокрутка к якорю {anchor_id} выполнена успешно');
                        return true;
                    }}
                    console.error('Якорь {anchor_id} не найден');
                }} catch (error) {{
                    console.error('Ошибка при прокрутке к якорю {anchor_id}:', error);
                }}
                return false;
            }}
            
            // Запускаем с задержкой для гарантии загрузки DOM
            setTimeout(scrollToAnchor, 300);
            setTimeout(scrollToAnchor, 800);
            setTimeout(scrollToAnchor, 1500);
        </script>
        """
        st.markdown(scroll_script, unsafe_allow_html=True)
        
        # Удаляем якорь из session_state, чтобы не скроллить при следующей перезагрузке
        del st.session_state['_scroll_anchor']
        
        return True
    
    return False