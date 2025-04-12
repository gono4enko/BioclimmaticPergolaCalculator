"""
Модуль реализует скроллинг на чистом питоне через структурирование приложения
с вариативным рендерингом компонентов в зависимости от состояния приложения.
Это полностью Python-подход без использования JavaScript.
"""
import streamlit as st
import time

def set_scroll_target(target_id):
    """
    Устанавливает целевую секцию для прокрутки и перезагружает страницу.
    
    Args:
        target_id (str): Идентификатор секции для прокрутки
    """
    # Сохраняем ID целевой секции для прокрутки
    st.session_state['_target_section'] = target_id
    
    # Сохраняем текущее время для отслеживания актуальности команды на прокрутку
    st.session_state['_scroll_command_time'] = time.time()
    
    # Устанавливаем флаг первого рендеринга (нужно для multi-step прокрутки)
    st.session_state['_first_render_after_scroll'] = True
    
    # Перезагружаем страницу
    st.rerun()

def should_render_section(section_id, render_function=None, *args, **kwargs):
    """
    Определяет, нужно ли отрендерить секцию, в зависимости от текущего состояния скроллинга.
    Важная часть стратегии - мы рендерим только целевую секцию и секции до неё,
    если находимся в процессе скроллинга.
    
    Args:
        section_id (str): Идентификатор секции
        render_function (callable, optional): Функция для рендеринга секции
        *args, **kwargs: Аргументы для функции рендеринга
        
    Returns:
        bool: True если секция должна быть отрендерена, False в противном случае
    """
    # Если не в режиме скроллинга - рендерим все секции
    if '_target_section' not in st.session_state:
        if render_function:
            render_function(*args, **kwargs)
        return True
    
    # Получаем целевую секцию и проверяем, совпадает ли она с текущей
    target_section = st.session_state.get('_target_section')
    is_target = (section_id == target_section)
    
    # Этот флаг будет отражать, нужно ли рендерить секцию
    should_render = True
    
    # Если мы в режиме первого рендеринга после команды прокрутки, 
    # рендерим только целевую секцию для упрощения DOM
    if st.session_state.get('_first_render_after_scroll', False):
        should_render = is_target
    
    # Если это целевая секция и у нас первый рендеринг после скроллинга,
    # обновляем флаг для следующего рендеринга
    if is_target and st.session_state.get('_first_render_after_scroll', False):
        # Сбрасываем флаг первого рендеринга
        st.session_state['_first_render_after_scroll'] = False
        
        # Отображаем уведомление о перемещении к секции
        st.markdown(f"""
        <div style="padding: 8px; 
                    background-color: #e6f2ff; 
                    border-left: 3px solid #0066cc; 
                    margin-bottom: 10px;
                    border-radius: 4px;">
            <p style="margin: 0; padding: 0; text-align: center; font-weight: bold;">
                ⤵ Результаты расчета ⤵
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # После полного рендеринга текущей секции, 
        # запланируем очистку состояния через 10 секунд
        # Это нужно чтобы не "застрять" в режиме скроллинга навсегда
        st.session_state['_scroll_cleanup_time'] = time.time() + 10
    
    # Проверяем, не пора ли очистить состояние скроллинга
    # (например, если пользователь не взаимодействовал с приложением после скроллинга)
    if '_scroll_cleanup_time' in st.session_state:
        if time.time() > st.session_state['_scroll_cleanup_time']:
            # Очищаем все данные о скроллинге
            st.session_state.pop('_target_section', None)
            st.session_state.pop('_scroll_command_time', None)
            st.session_state.pop('_first_render_after_scroll', None)
            st.session_state.pop('_scroll_cleanup_time', None)
    
    # Рендерим секцию, если нужно
    if should_render and render_function:
        render_function(*args, **kwargs)
    
    return should_render

def create_section_header(section_id, title, highlight=False):
    """
    Создает заголовок для секции с возможностью подсветки.
    
    Args:
        section_id (str): Идентификатор секции
        title (str): Заголовок секции
        highlight (bool): Подсвечивать ли заголовок
    """
    # Определяем стили в зависимости от того, нужно ли подсветить секцию
    bg_color = "#f0f8ff" if highlight else "transparent"
    border = "2px solid #0066cc" if highlight else "1px solid #e6e6e6"
    padding = "12px" if highlight else "8px"
    border_radius = "4px" if highlight else "0"
    
    # Создаем HTML для заголовка секции
    header_html = f"""
    <div id="{section_id}" 
         style="width: 100%; 
                margin-top: 20px;
                margin-bottom: 15px;
                background-color: {bg_color};
                border-top: {border};
                padding: {padding};
                border-radius: {border_radius};">
        <h2 style="margin: 0; 
                   padding: 0; 
                   font-size: 1.5rem; 
                   text-align: center;
                   color: #333;">
            {title}
        </h2>
    </div>
    """
    
    # Отображаем заголовок
    st.markdown(header_html, unsafe_allow_html=True)

def check_scroll_state():
    """
    Проверяет состояние скроллинга и возвращает информацию о целевой секции.
    Должна вызываться в начале приложения.
    
    Returns:
        tuple: (is_scrolling, target_section)
    """
    is_scrolling = False
    target_section = None
    
    # Проверяем, находимся ли мы в режиме скроллинга
    if '_target_section' in st.session_state and '_scroll_command_time' in st.session_state:
        # Проверяем, не устарела ли команда на скроллинг (30 секунд)
        if time.time() - st.session_state['_scroll_command_time'] > 30:
            # Удаляем устаревшие данные
            st.session_state.pop('_target_section', None)
            st.session_state.pop('_scroll_command_time', None)
            st.session_state.pop('_first_render_after_scroll', None)
        else:
            # Мы в режиме скроллинга
            is_scrolling = True
            target_section = st.session_state['_target_section']
    
    return is_scrolling, target_section