"""
Модуль с пользовательскими компонентами интерфейса для калькулятора пергол
"""
import streamlit as st

def fixed_button(label, key=None, help=None, on_click=None, disabled=False, white_background=True):
    """
    Создает кнопку с принудительно белым фоном или другим заданным цветом.
    
    Args:
        label (str): Текст кнопки
        key (str, optional): Уникальный ключ компонента
        help (str, optional): Подсказка при наведении
        on_click (callable, optional): Функция обратного вызова
        disabled (bool, optional): Отключена ли кнопка
        white_background (bool, optional): Принудительно белый фон
    
    Returns:
        bool: True если кнопка была нажата
    """
    # Создаем контейнер для кнопки
    container = st.container()
    
    # Если требуется белый фон, добавляем стиль
    if white_background:
        # Добавляем CSS стили для кнопки
        st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            background-color: white;
            color: black;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        div[data-testid="stButton"] button:hover {
            background-color: #f8f8f8;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Размещаем кнопку в контейнере
    with container:
        return st.button(
            label=label,
            key=key,
            help=help,
            on_click=on_click,
            disabled=disabled
        )

def white_tile(title, subtitle="", key=None, is_selected=False, on_click=None):
    """
    Создает плитку с белым фоном и без синей заливки.
    
    Args:
        title (str): Заголовок плитки
        subtitle (str, optional): Подзаголовок плитки
        key (str, optional): Уникальный ключ компонента
        is_selected (bool, optional): Выбрана ли плитка
        on_click (callable, optional): Функция обратного вызова при клике
    
    Returns:
        bool: True если плитка была нажата
    """
    # Определяем стили для плиток
    st.markdown("""
    <style>
    .tile-container {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .tile-container:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .tile-container.selected {
        border: 2px solid #4CAF50;
        box-shadow: 0 2px 5px rgba(76, 175, 80, 0.3);
    }
    .tile-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .tile-subtitle {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем уникальный ID для обработки кликов
    if key is None:
        key = f"tile_{title}_{subtitle}".replace(" ", "_")
    
    # Определяем класс для плитки (с выделением или без)
    tile_class = "tile-container selected" if is_selected else "tile-container"
    
    # Создаем HTML для плитки
    tile_html = f"""
    <div class="{tile_class}" id="{key}" onclick="handleClick('{key}')">
        <div class="tile-title">{title}</div>
        <div class="tile-subtitle">{subtitle}</div>
    </div>
    
    <script>
    function handleClick(key) {{
        // Отправляем событие клика через Streamlit
        window.parent.postMessage({{
            type: "streamlit:setComponentValue",
            value: key,
            key: "{key}"
        }}, "*");
    }}
    </script>
    """
    
    # Рендерим плитку
    st.markdown(tile_html, unsafe_allow_html=True)
    
    # Ожидаем взаимодействие с плиткой
    clicked = st.session_state.get(key, False)
    
    # Если плитка была нажата и есть функция обратного вызова, вызываем её
    if clicked and on_click:
        on_click()
    
    return clicked

def tile_grid(options, columns=3):
    """
    Создает сетку плиток с заданным количеством колонок.
    
    Args:
        options (list): Список словарей с опциями для плиток
                        Каждый словарь должен содержать 'title', 'subtitle' и 'key'
        columns (int, optional): Количество колонок в сетке
        
    Returns:
        str: Ключ выбранной плитки или None
    """
    # Создаем колонки
    cols = st.columns(columns)
    
    # Переменная для хранения выбранной опции
    selected_option = None
    
    # Распределяем плитки по колонкам
    for i, option in enumerate(options):
        with cols[i % columns]:
            is_selected = st.session_state.get(f"selected_option") == option['key']
            
            if white_tile(
                title=option['title'],
                subtitle=option.get('subtitle', ''),
                key=option['key'],
                is_selected=is_selected
            ):
                selected_option = option['key']
                st.session_state['selected_option'] = selected_option
    
    return selected_option

def create_section(title, content_function):
    """
    Создает секцию с заголовком и сворачиваемым содержимым.
    
    Args:
        title (str): Заголовок секции
        content_function (callable): Функция, которая рендерит содержимое секции
        
    Returns:
        bool: True если секция развернута
    """
    is_expanded = st.expander(title, expanded=True)
    
    with is_expanded:
        content_function()
        
    return is_expanded._expanded

def info_box(message, type="info"):
    """
    Отображает информационный блок с сообщением.
    
    Args:
        message (str): Текст сообщения
        type (str, optional): Тип сообщения (info, success, warning, error)
    """
    if type == "info":
        st.info(message)
    elif type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)
    else:
        st.info(message)

def display_formatted_description(description_text):
    """
    Отображает форматированное описание в стилизованном контейнере,
    избегая проблем с видимостью HTML-тегов.
    
    Args:
        description_text (str): HTML-текст с описанием
    """
    # Создаем стилизованный контейнер
    st.markdown("""
    <style>
    .description-container {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .description-container h2 {
        color: #2c3e50;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .description-container h3 {
        color: #34495e;
        font-size: 1.25rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .description-container p {
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }
    .description-container ul {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    .description-container li {
        margin-bottom: 0.25rem;
    }
    .description-container img {
        max-width: 100%;
        height: auto;
        margin: 1rem 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Преобразуем теги section в div с классом section
    description_text = description_text.replace('<section>', '<div class="section">').replace('</section>', '</div>')
    
    # Отображаем содержимое в контейнере
    st.markdown(f'<div class="description-container">{description_text}</div>', unsafe_allow_html=True)

def display_image_with_padding(image_path, caption=None, padding_percent=5):
    """
    Отображает изображение с отступами по краям и подписью.
    
    Args:
        image_path (str): Путь к изображению
        caption (str, optional): Подпись к изображению
        padding_percent (int, optional): Процент отступа от ширины контейнера (по умолчанию 5%)
    """
    # Создаем контейнер для изображения
    container = st.container()
    
    # Добавляем CSS стили для создания отступов
    css = f"""
    <style>
    .image-container {{
        padding-left: {padding_percent}%;
        padding-right: {padding_percent}%;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
    .image-caption {{
        text-align: center;
        color: #666;
        font-style: italic;
        margin-top: 0.5rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    # Отображаем изображение с отступами
    with container:
        html = f'<div class="image-container"><img src="{image_path}" style="width:100%;" />'
        if caption:
            html += f'<div class="image-caption">{caption}</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

def scroll_to_results():
    """
    Добавляет JavaScript для перехода к якорю результатов при нажатии на скрытую кнопку
    """
    # Создаем якорь для результатов
    st.markdown('<div id="results-section"></div>', unsafe_allow_html=True)
    
    # Добавляем JavaScript для прокрутки к якорю
    js = """
    <script>
    function scrollToResults() {
        const resultsElement = document.getElementById('results-section');
        if (resultsElement) {
            resultsElement.scrollIntoView({ behavior: 'smooth' });
        }
    }
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
    
    # Создаем скрытую кнопку, которая вызовет скролл
    button_html = """
    <div style="display:none;">
        <button onclick="scrollToResults()">Scroll to Results</button>
    </div>
    <script>
    // Автоматически прокручиваем к результатам при загрузке этого элемента
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(scrollToResults, 500);
    });
    </script>
    """
    st.markdown(button_html, unsafe_allow_html=True)