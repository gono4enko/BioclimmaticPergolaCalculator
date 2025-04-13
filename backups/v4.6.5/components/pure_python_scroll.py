"""
Максимально простой и гарантированно работающий механизм скроллинга на чистом Python.
Использует только базовое API Streamlit без каких-либо хитростей.
"""
import streamlit as st

def set_target_section(section_name):
    """
    Устанавливает целевую секцию для перехода.
    Будет перерисовывать приложение до тех пор, пока не дойдет до нужной секции.
    
    Args:
        section_name (str): Имя секции, к которой нужно перейти
    """
    # Отключаем показ всех секций, кроме результатов
    st.session_state['skip_sections'] = True
    # Устанавливаем целевую секцию
    st.session_state['target_section'] = section_name
    
    # Перезагружаем страницу
    st.rerun()

def is_target_section(section_name):
    """
    Проверяет, является ли текущая секция целевой для скроллинга.
    
    Args:
        section_name (str): Имя секции для проверки
        
    Returns:
        bool: True если секция является целевой, иначе False
    """
    return st.session_state.get('target_section') == section_name

def should_show_section(section_name):
    """
    Определяет, нужно ли показывать секцию в текущем состоянии.
    
    Args:
        section_name (str): Имя секции
        
    Returns:
        bool: True если секцию нужно показать, иначе False
    """
    # Если нет активного скроллинга, показываем все секции
    if 'target_section' not in st.session_state:
        return True
    
    # Если есть активный скроллинг, показываем только целевую секцию
    if st.session_state.get('skip_sections', False):
        # Показываем только целевую секцию
        return is_target_section(section_name)
    
    # Когда секции уже показаны, разрешаем показывать все
    return True

def finalize_scroll():
    """
    Финализирует скроллинг, позволяя отображать все секции.
    """
    if 'skip_sections' in st.session_state:
        # Показываем все секции после нахождения целевой
        st.session_state['skip_sections'] = False
        
        # Отображаем уведомление о перемещении
        st.success(f"⬇️ Перемещено к разделу «{st.session_state.get('target_section')}» ⬇️")
        
        # Перезагружаем страницу, чтобы отобразить все секции
        st.rerun()

def create_section(section_name, section_title=None):
    """
    Создает маркированную секцию, которая может быть целью скроллинга.
    
    Args:
        section_name (str): Уникальное имя секции
        section_title (str, optional): Заголовок секции для отображения
    
    Returns:
        bool: True если секцию нужно показать, иначе False
    """
    # Проверяем, нужно ли показывать эту секцию
    show_section = should_show_section(section_name)
    
    # Если это целевая секция, финализируем скроллинг
    if show_section and is_target_section(section_name):
        finalize_scroll()
    
    # Если нужно отобразить заголовок секции
    if show_section and section_title:
        st.markdown(f"""
        <div style="width: 100%; 
                    background-color: #f0f8ff; 
                    padding: 10px;
                    margin-top: 20px;
                    margin-bottom: 15px;
                    border-top: 2px solid #0066cc;
                    border-radius: 4px;">
            <h2 style="margin: 0; 
                       padding: 0; 
                       font-size: 1.5rem; 
                       text-align: center;
                       color: #333;">
                {section_title}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    return show_section