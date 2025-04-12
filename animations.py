"""
Модуль для добавления плавных микроанимаций и переходов в приложение Streamlit.
Улучшает пользовательский опыт без перегрузки интерфейса.
"""

import streamlit as st

def add_animations_css():
    """
    Добавляет базовые CSS анимации для всего приложения.
    Должна вызываться один раз в начале приложения.
    """
    st.markdown(
        """
        <style>
        /* Базовые анимации и переходы */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        @keyframes highlight {
            0% { background-color: rgba(0, 102, 204, 0.05); }
            50% { background-color: rgba(0, 102, 204, 0.1); }
            100% { background-color: rgba(0, 102, 204, 0.05); }
        }
        
        /* Классы для применения анимаций */
        .fadeIn {
            animation: fadeIn 0.6s ease-out forwards;
        }
        
        .slideInRight {
            animation: slideInRight 0.5s ease-out forwards;
        }
        
        .slideInLeft {
            animation: slideInLeft 0.5s ease-out forwards;
        }
        
        .pulseAnimation {
            animation: pulse 1.5s infinite ease-in-out;
        }
        
        .highlightAnimation {
            animation: highlight 2s infinite ease-in-out;
        }
        
        /* Плавные переходы для интерактивных элементов */
        .stRadio > label, .stCheckbox > label, .stSelectbox, button,
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            transition: all 0.3s ease !important;
        }
        
        .stRadio > label:hover, .stCheckbox > label:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Стили для разделов */
        .section-transition {
            transition: all 0.5s ease;
            padding: 10px;
            border-radius: 8px;
        }
        
        .section-transition:hover {
            background-color: rgba(0, 102, 204, 0.05);
        }
        
        /* Стиль для активных элементов интерфейса */
        .active-element {
            background-color: rgba(0, 102, 204, 0.07);
            border-left: 3px solid #0066cc;
            padding-left: 8px;
            transition: all 0.3s ease;
        }
        
        /* Плавные переходы контейнеров */
        div.stContainer {
            transition: all 0.4s ease;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def animate_section(html_content, animation_type='fadeIn', delay=0):
    """
    Обертывает HTML-контент в div с выбранной анимацией и задержкой
    
    Args:
        html_content (str): HTML-строка для анимации
        animation_type (str): Тип анимации ('fadeIn', 'slideInRight', 'slideInLeft')
        delay (float): Задержка анимации в секундах
        
    Returns:
        str: HTML с применённой анимацией
    """
    return f"""
    <div class="{animation_type}" style="animation-delay: {delay}s;">
        {html_content}
    </div>
    """

def animated_container(content_function, animation_type='fadeIn', delay=0):
    """
    Создает контейнер с анимацией, в котором будет выполнена функция content_function
    
    Args:
        content_function: Функция, которая будет выполнена внутри анимированного контейнера
        animation_type (str): Тип анимации
        delay (float): Задержка анимации в секундах
    """
    st.markdown(f'<div class="{animation_type}" style="animation-delay: {delay}s;">', 
                unsafe_allow_html=True)
    content_function()
    st.markdown('</div>', unsafe_allow_html=True)

def add_section_separator(height=10, animation=True):
    """
    Добавляет разделитель между секциями с опциональной анимацией
    
    Args:
        height (int): Высота разделителя в пикселях
        animation (bool): Применять ли анимацию к разделителю
    """
    separator = f'<div style="height: {height}px;"></div>'
    if animation:
        separator = f'<div class="fadeIn" style="height: {height}px;"></div>'
    st.markdown(separator, unsafe_allow_html=True)

def animate_text(text, tag='p', css_class='fadeIn', delay=0, 
                additional_style=''):
    """
    Создает анимированный текстовый элемент
    
    Args:
        text (str): Текст для отображения
        tag (str): HTML-тег для обертки текста
        css_class (str): CSS класс для анимации
        delay (int): Задержка анимации в секундах
        additional_style (str): Дополнительные стили
        
    Returns:
        None: Отображает текст через st.markdown
    """
    # Конвертируем float в строку для корректного отображения в CSS
    delay_str = str(delay)
    html = f'<{tag} class="{css_class}" style="animation-delay: {delay_str}s; {additional_style}">{text}</{tag}>'
    st.markdown(html, unsafe_allow_html=True)

def add_section_animation_js():
    """
    Добавляет JavaScript для анимации появления секций при прокрутке
    """
    js = """
    <script>
    // Функция проверки, находится ли элемент в видимой области
    function isElementInViewport(el) {
        var rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Функция добавления класса при появлении элемента в поле зрения
    function animateOnScroll() {
        var sections = document.querySelectorAll('.section-transition:not(.animated)');
        
        sections.forEach(function(section) {
            if (isElementInViewport(section)) {
                section.classList.add('fadeIn');
                section.classList.add('animated');
            }
        });
    }
    
    // Запускаем проверку при прокрутке и при загрузке
    window.addEventListener('scroll', animateOnScroll);
    window.addEventListener('load', animateOnScroll);
    
    // Запускаем также каждые 500мс, чтобы учесть динамически добавленный контент
    setInterval(animateOnScroll, 500);
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def add_scroll_animations():
    """
    Добавляет эффект анимации при прокрутке страницы
    """
    st.markdown(
        """
        <style>
        /* Скрываем элементы до появления в видимой области */
        .reveal {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.8s ease, transform 0.8s ease;
        }
        
        /* Класс, который добавляется JS-скриптом при появлении элемента в видимой области */
        .reveal.visible {
            opacity: 1;
            transform: translateY(0);
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # JavaScript для определения видимости элементов
    st.markdown(
        """
        <script>
        // Функция для определения элементов в видимой области
        function revealElements() {
            var reveals = document.querySelectorAll('.reveal');
            
            for (var i = 0; i < reveals.length; i++) {
                var windowHeight = window.innerHeight;
                var elementTop = reveals[i].getBoundingClientRect().top;
                var elementVisible = 150; // Элемент считается видимым, когда эта часть видна
                
                if (elementTop < windowHeight - elementVisible) {
                    reveals[i].classList.add('visible');
                }
            }
        }
        
        // Добавляем обработчики событий
        window.addEventListener('scroll', revealElements);
        window.addEventListener('load', revealElements);
        
        // Также запускаем периодически для динамически добавленных элементов
        setInterval(revealElements, 300);
        </script>
        """, 
        unsafe_allow_html=True
    )

def add_smooth_transition_js():
    """
    Добавляет JavaScript для плавных переходов при изменении состояния приложения
    """
    js = """
    <script>
    // Функция для плавного затухания страницы перед изменением
    function addSmoothStateTransition() {
        // Находим все элементы формы, которые могут вызвать перезагрузку страницы
        var inputs = document.querySelectorAll('input, select, button');
        
        inputs.forEach(function(input) {
            input.addEventListener('change', function() {
                // Добавляем затухание всему контейнеру приложения
                var appContainer = document.querySelector('.main');
                if (appContainer) {
                    appContainer.style.transition = 'opacity 0.3s ease';
                    appContainer.style.opacity = '0.7';
                    
                    // Возвращаем непрозрачность после небольшой задержки
                    setTimeout(function() {
                        appContainer.style.opacity = '1';
                    }, 400);
                }
            });
        });
    }
    
    // Запускаем после загрузки страницы и периодически для новых элементов
    window.addEventListener('load', addSmoothStateTransition);
    setInterval(addSmoothStateTransition, 1000);
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def animate_button(button_text, key=None, animation_class="pulseAnimation"):
    """
    Создает анимированную кнопку
    
    Args:
        button_text (str): Текст кнопки
        key (str, optional): Ключ для кнопки
        animation_class (str): Класс CSS-анимации
        
    Returns:
        bool: True если кнопка нажата
    """
    # Добавляем дополнительные CSS-стили для анимации
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    
    .pulseAnimation {
        animation: pulse 1.5s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем HTML для анимированной кнопки
    button_html = f"""
    <button class="{animation_class}" 
        style="
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 16px;
            height: 50px;
            line-height: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: block;
            width: 100%;
            margin: 0 auto;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            font-weight: bold;
        "
        onclick="document.getElementById('hidden-button-{key}').click();"
    >
        {button_text}
    </button>
    """
    
    # Отображаем анимированную кнопку
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Создаем скрытую кнопку, которая будет нажиматься из HTML-кнопки
    return st.button("Скрытая кнопка", key=f"hidden-button-{key}", 
                     help="Это скрытая кнопка для анимированного интерфейса", 
                     on_click=None)

def apply_entrance_animation():
    """
    Добавляет анимацию при первой загрузке страницы
    """
    st.markdown(
        """
        <style>
        /* Анимация при первой загрузке */
        @keyframes pageEntrance {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        /* Применяем анимацию к основному контейнеру */
        .main .block-container {
            animation: pageEntrance 0.8s ease-out forwards;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )