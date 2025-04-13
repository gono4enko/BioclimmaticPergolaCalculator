"""
Модуль для добавления функций автоматической прокрутки и анимаций к интерфейсу.
"""
import streamlit as st

def scroll_to_results():
    """
    Добавляет JavaScript для перехода к якорю результатов при нажатии на скрытую кнопку
    """
    st.markdown("""
    <script>
        // Функция для прокрутки к результатам
        function scrollToResults() {
            // Находим элемент с id "calculation-results"
            const resultsElement = document.getElementById("calculation-results");
            if (resultsElement) {
                // Плавно прокручиваем к элементу
                resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
        
        // Ищем все кнопки с классом scroll-trigger
        document.addEventListener('DOMContentLoaded', function() {
            const scrollButtons = document.querySelectorAll('.scroll-trigger');
            scrollButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Даем немного времени, чтобы результаты отрисовались
                    setTimeout(scrollToResults, 300);
                });
            });
        });
    </script>
    """, unsafe_allow_html=True)

def add_button_animation():
    """
    Добавляет анимацию кнопок при наведении и нажатии
    """
    st.markdown("""
    <style>
        /* Анимация для кнопок */
        .stButton button {
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .stButton button:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Анимация для кнопки расчета */
        .stButton.calculate-button button {
            position: relative;
            overflow: hidden;
        }
        
        .stButton.calculate-button button:after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.5);
            opacity: 0;
            border-radius: 100%;
            transform: scale(1, 1) translate(-50%, -50%);
            transform-origin: 50% 50%;
        }
        
        .stButton.calculate-button button:focus:after {
            animation: ripple 1s ease-out;
        }
        
        @keyframes ripple {
            0% {
                transform: scale(0, 0);
                opacity: 0.5;
            }
            20% {
                transform: scale(25, 25);
                opacity: 0.3;
            }
            100% {
                opacity: 0;
                transform: scale(40, 40);
            }
        }
    </style>
    """, unsafe_allow_html=True)