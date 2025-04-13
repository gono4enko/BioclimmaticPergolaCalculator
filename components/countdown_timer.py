"""
Надежный компонент таймера обратного отсчета, который работает даже в среде Streamlit+Replit.
Использует комбинацию JS и CSS для реального обновления времени без перезагрузки страницы.
"""
import streamlit as st
import time
import datetime
import uuid

def create_timer(end_time=None, days=0, hours=0, minutes=0, seconds=0, 
                background_color="#4CAF50", text_color="white", timer_color="#FFEB3B"):
    """
    Создает и отображает таймер обратного отсчета, который надежно обновляется в реальном времени.
    
    Args:
        end_time (datetime.datetime, optional): Конечная дата и время таймера
        days (int): Дни (используется, если end_time не указан)
        hours (int): Часы (используется, если end_time не указан)
        minutes (int): Минуты (используется, если end_time не указан)
        seconds (int): Секунды (используется, если end_time не указан)
        background_color (str): Цвет фона контейнера таймера
        text_color (str): Цвет текста внутри контейнера
        timer_color (str): Цвет цифр таймера
    """
    # Генерируем уникальный ID
    timer_id = f"timer_{uuid.uuid4().hex}"
    
    # Определяем конечное время
    if end_time:
        # Если предоставлена конечная дата-время, используем ее
        now = datetime.datetime.now()
        time_left = end_time - now
        
        # Если время уже истекло, выводим сообщение
        if time_left.total_seconds() <= 0:
            st.warning("Указанное время уже истекло")
            return
            
        # Устанавливаем время
        total_seconds = time_left.total_seconds()
        days = time_left.days
        hours = int((time_left.seconds // 3600))
        minutes = int((time_left.seconds % 3600) // 60)
        seconds = int(time_left.seconds % 60)
    else:
        # Если конечное время не указано, вычисляем из предоставленных компонентов
        total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
    
    # Устанавливаем timestamp для JavaScript (текущее время + оставшиеся секунды)
    end_timestamp = int(time.time() * 1000 + total_seconds * 1000)
    
    # Форматируем начальное значение для отображения
    if days > 0:
        display_text = f"{days} дн. {hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        display_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # HTML и CSS для таймера
    st.markdown(f"""
    <style>
    .countdown-panel-{timer_id} {{
        background-color: {background_color};
        color: {text_color};
        border-radius: 8px;
        padding: 12px 15px;
        margin: 10px 0;
        text-align: center;
        width: 100%;
    }}
    .timer-{timer_id} {{
        font-weight: bold;
        font-size: 1.5rem;
        color: {timer_color};
        display: inline-block;
        margin: 5px 0;
        padding: 3px 8px;
        border-radius: 4px;
        background-color: rgba(0,0,0,0.1);
        min-width: 160px;
    }}
    </style>
    <div class="countdown-panel-{timer_id}">
        <div>До окончания акции:</div>
        <div class="timer-{timer_id}" id="{timer_id}">{display_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript для обновления таймера
    js_code = f"""
    <script>
    (function() {{
        // Время окончания в миллисекундах
        const endTime = {end_timestamp};
        
        // Функция форматирования чисел (с ведущим нулем)
        function padZero(num) {{
            return num < 10 ? '0' + num : num;
        }}
        
        // Функция для обновления таймера
        function updateCountdown() {{
            const timerElement = document.getElementById('{timer_id}');
            if (!timerElement) return;
            
            // Текущее время
            const now = new Date().getTime();
            let timeLeft = endTime - now;
            
            if (timeLeft < 0) {{
                // Если время истекло
                timerElement.innerHTML = "ВРЕМЯ ИСТЕКЛО";
                clearInterval(timerInterval);
                return;
            }}
            
            // Вычисляем оставшееся время
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            
            // Форматируем вывод
            let displayText = "";
            if (days > 0) {{
                displayText = days + " дн. " + padZero(hours) + ":" + padZero(minutes) + ":" + padZero(seconds);
            }} else {{
                displayText = padZero(hours) + ":" + padZero(minutes) + ":" + padZero(seconds);
            }}
            
            // Обновляем содержимое таймера
            timerElement.innerHTML = displayText;
        }}
        
        // Немедленно запускаем обновление
        updateCountdown();
        
        // Устанавливаем таймер на каждую секунду
        const timerInterval = setInterval(updateCountdown, 1000);
        
        // Сохраняем ID интервала в атрибуте элемента для возможности очистки
        const timerElement = document.getElementById('{timer_id}');
        if (timerElement) {{
            timerElement.setAttribute('data-interval-id', timerInterval);
        }}
        
        // Запускаем обновление при фокусе окна
        window.addEventListener('focus', updateCountdown);
        
        // Запускаем обновление при видимости страницы
        document.addEventListener('visibilitychange', function() {{
            if (!document.hidden) {{
                updateCountdown();
            }}
        }});
    }})();
    </script>
    """
    
    # Добавляем JavaScript на страницу
    st.markdown(js_code, unsafe_allow_html=True)
    
    return timer_id