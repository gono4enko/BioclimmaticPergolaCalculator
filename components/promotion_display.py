"""
Компонент для отображения акций и скидок в интерфейсе калькулятора пергол.
Включает:
- Отображение значков акций
- Поле для ввода промокода
- Таймер для срочных скидок
- Информацию о примененных скидках
"""
import streamlit as st
import datetime
import time
from typing import Dict, List, Optional

# Импортируем модуль с акциями
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import promotions

def display_promo_badges(applicable_promotions: List[Dict]) -> None:
    """
    Отображает значки активных акций.
    
    Args:
        applicable_promotions: Список применимых акций
    """
    if not applicable_promotions:
        return
    
    badges = []
    
    for promo in applicable_promotions:
        if promo.get("display_badge", True):
            badges.append({
                "text": promo.get("badge_text", promo.get("name", "")),
                "color": promo.get("badge_color", "#4CAF50")
            })
    
    if badges:
        st.markdown("""
        <style>
        .promo-badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }
        .promo-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: bold;
            color: white;
            animation: badge-pulse 2s infinite;
        }
        @keyframes badge-pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        @media (max-width: 768px) {
            .promo-badge {
                font-size: 0.75rem;
                padding: 3px 8px;
            }
        }
        </style>
        <div class="promo-badge-container">
        """, unsafe_allow_html=True)
        
        for badge in badges:
            st.markdown(f"""
            <div class="promo-badge" style="background-color: {badge['color']};">
                {badge['text']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_urgent_discount_panel(urgent_promotion: Optional[Dict] = None) -> bool:
    """
    Отображает панель для активации срочной скидки с обратным отсчетом.
    
    Args:
        urgent_promotion: Информация о срочной скидке
        
    Returns:
        bool: True если скидка активирована
    """
    if not urgent_promotion:
        return False
    
    # Проверяем, активирована ли скидка
    if "urgent_discount_activated" not in st.session_state:
        st.session_state.urgent_discount_activated = False
    
    if "urgent_discount_time" not in st.session_state:
        # Если таймер еще не запущен, устанавливаем его
        hours_limit = 24
        for condition in urgent_promotion.get("conditions", []):
            if condition.get("type") == promotions.CONDITION_QUICK_DECISION:
                hours_limit = condition.get("hours_limit", 24)
        
        # Устанавливаем время окончания скидки (часы * 3600 секунд)
        st.session_state.urgent_discount_time = time.time() + (hours_limit * 3600)
    
    # Если скидка уже активирована, просто возвращаем True
    if st.session_state.urgent_discount_activated:
        return True
    
    # Отображаем панель со срочной скидкой
    with st.container():
        st.markdown(f"""
        <style>
        .urgent-panel {{
            background-color: {urgent_promotion.get('badge_color', '#F44336')};
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
        }}
        .urgent-panel h4 {{
            margin: 0 0 5px 0;
            font-size: 1.1rem;
        }}
        .urgent-panel p {{
            margin: 0 0 10px 0;
            font-size: 0.9rem;
        }}
        .countdown {{
            font-weight: bold;
            font-size: 1.1rem;
            color: #FFEB3B;
        }}
        .pulse-animation {{
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.03); }}
            100% {{ transform: scale(1); }}
        }}
        @media (max-width: 768px) {{
            .urgent-panel h4 {{
                font-size: 0.95rem;
            }}
            .urgent-panel p {{
                font-size: 0.8rem;
            }}
            .countdown {{
                font-size: 0.9rem;
            }}
        }}
        </style>
        <div class="urgent-panel pulse-animation">
            <h4>{urgent_promotion.get('name', 'Срочная скидка')}</h4>
            <p>{urgent_promotion.get('description', 'Активируйте скидку сейчас!')}</p>
            <div class="countdown-container">
                <span>До окончания: </span>
                <span class="countdown" id="countdown">Загрузка...</span>
            </div>
            <div style="text-align: center; margin-top: 10px;">
                <button id="activate-discount" 
                        style="background-color: white; 
                               color: {urgent_promotion.get('badge_color', '#F44336')}; 
                               border: none; 
                               padding: 8px 15px; 
                               border-radius: 4px; 
                               font-weight: bold;
                               cursor: pointer;">
                    Активировать скидку
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Обновляем таймер с помощью JavaScript
        remaining_time = st.session_state.urgent_discount_time - time.time()
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        seconds = int(remaining_time % 60)
        
        # Обратный отсчет с помощью JavaScript
        st.markdown(f"""
        <script>
            // Устанавливаем начальное время
            var countDownDate = new Date().getTime() + {int(remaining_time * 1000)};
            
            // Функция для форматирования чисел с ведущим нулем
            function formatNumber(num) {{
                return num < 10 ? '0' + num : num;
            }}
            
            // Обновляем таймер каждую секунду
            var x = setInterval(function() {{
                var now = new Date().getTime();
                var distance = countDownDate - now;
                
                // Расчеты для часов, минут и секунд
                var hours = Math.floor(distance / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                // Отображаем результат
                document.getElementById("countdown").innerHTML = 
                    formatNumber(hours) + ":" + formatNumber(minutes) + ":" + formatNumber(seconds);
                
                // Если время истекло
                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("countdown").innerHTML = "ВРЕМЯ ИСТЕКЛО";
                    document.getElementById("activate-discount").style.display = "none";
                }}
            }}, 1000);
            
            // Обработчик клика по кнопке активации
            document.getElementById("activate-discount").addEventListener("click", function() {{
                // Отправляем событие активации в Streamlit
                window.parent.postMessage({{
                    type: "streamlit:setComponentValue",
                    value: true
                }}, "*");
                
                // Меняем текст кнопки
                this.innerHTML = "Скидка активирована!";
                this.disabled = true;
                this.style.backgroundColor = "#CCCCCC";
            }});
        </script>
        """, unsafe_allow_html=True)
        
        # Проверяем, была ли нажата кнопка
        if st.button("Активировать скидку", key="urgent_discount_button", type="primary"):
            st.session_state.urgent_discount_activated = True
            return True
    
    return st.session_state.urgent_discount_activated

def promo_code_input() -> Optional[str]:
    """
    Отображает поле для ввода промокода.
    
    Returns:
        Optional[str]: Введенный промокод или None
    """
    # Состояние для хранения введенного промокода
    if "promo_code" not in st.session_state:
        st.session_state.promo_code = ""
    
    # Состояние для отслеживания, был ли применен промокод
    if "promo_code_applied" not in st.session_state:
        st.session_state.promo_code_applied = False
    
    if st.session_state.promo_code_applied:
        # Если промокод уже применен, показываем информацию о нем
        st.markdown(f"""
        <style>
        .promo-applied {{
            background-color: #E8F5E9;
            color: #388E3C;
            padding: 8px 12px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .promo-applied span {{
            font-weight: bold;
        }}
        .promo-applied button {{
            background: none;
            border: none;
            color: #D32F2F;
            cursor: pointer;
            font-weight: bold;
        }}
        @media (max-width: 768px) {{
            .promo-applied {{
                padding: 6px 10px;
                font-size: 0.8rem;
            }}
        }}
        </style>
        <div class="promo-applied">
            <div>Промокод <span>{st.session_state.promo_code}</span> применен</div>
            <button id="remove-promo" onclick="removePromo()">✕</button>
        </div>
        <script>
        function removePromo() {{
            // Сбрасываем промокод через Streamlit
            window.parent.postMessage({{
                type: "streamlit:setComponentValue",
                value: null
            }}, "*");
            
            // Обновляем страницу
            window.parent.postMessage({{
                type: "streamlit:componentRerun"
            }}, "*");
        }}
        </script>
        """, unsafe_allow_html=True)
        
        # Кнопка для отмены промокода
        if st.button("Отменить промокод", key="cancel_promo", type="secondary"):
            st.session_state.promo_code = ""
            st.session_state.promo_code_applied = False
            st.rerun()
            
        return st.session_state.promo_code
    else:
        # Если промокод еще не применен, показываем форму ввода
        col1, col2 = st.columns([3, 1])
        
        with col1:
            promo_code = st.text_input(
                "Введите промокод",
                key="promo_code_input",
                value=st.session_state.promo_code
            )
        
        with col2:
            apply_button = st.button(
                "Применить",
                key="apply_promo",
                type="primary"
            )
        
        if apply_button and promo_code:
            # Сохраняем введенный промокод
            st.session_state.promo_code = promo_code
            st.session_state.promo_code_applied = True
            return promo_code
        
        return None

def display_applied_discounts(applied_promotions: List[Dict], total_discount: float) -> None:
    """
    Отображает информацию о примененных скидках.
    
    Args:
        applied_promotions: Список примененных акций
        total_discount: Общая сумма скидки
    """
    if not applied_promotions:
        return
    
    st.markdown("""
    <style>
    .discounts-container {
        margin-top: 15px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        overflow: hidden;
    }
    .discounts-header {
        background-color: #F5F5F5;
        padding: 10px 15px;
        font-weight: bold;
        border-bottom: 1px solid #E0E0E0;
    }
    .discount-item {
        padding: 10px 15px;
        border-bottom: 1px solid #E0E0E0;
        display: flex;
        justify-content: space-between;
    }
    .discount-item:last-child {
        border-bottom: none;
    }
    .discount-name {
        font-weight: 500;
    }
    .discount-amount {
        font-weight: bold;
    }
    .discount-total {
        background-color: #FFFDE7;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        font-weight: bold;
    }
    @media (max-width: 768px) {
        .discounts-header, .discount-item, .discount-total {
            padding: 8px 10px;
            font-size: 0.8rem;
        }
    }
    </style>
    <div class="discounts-container">
        <div class="discounts-header">Примененные скидки</div>
    """, unsafe_allow_html=True)
    
    for promo in applied_promotions:
        discount_display = promo.get("discount_display", "")
        discount_amount = promo.get("discount_amount", 0)
        
        st.markdown(f"""
        <div class="discount-item">
            <div class="discount-name">{promo.get('name', 'Скидка')} ({discount_display})</div>
            <div class="discount-amount">-{discount_amount:,.0f} ₽</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="discount-total">
            <div>Общая скидка:</div>
            <div>-{total_discount:,.0f} ₽</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def promotions_section(pergola_type: str, width: float, length: float, 
                      base_price: float, options_price: float, options: Dict) -> float:
    """
    Отображает секцию с акциями и скидками и возвращает сумму скидки.
    
    Args:
        pergola_type: Тип перголы
        width: Ширина перголы
        length: Длина перголы
        base_price: Базовая стоимость перголы
        options_price: Стоимость опций
        options: Словарь с опциями
        
    Returns:
        float: Сумма скидки
    """
    # Получаем промокод, если введен
    promo_code = None
    if "promo_code_applied" in st.session_state and st.session_state.promo_code_applied:
        promo_code = st.session_state.promo_code
    
    # Проверяем активацию срочной скидки
    quick_decision_activated = False
    if "urgent_discount_activated" in st.session_state:
        quick_decision_activated = st.session_state.urgent_discount_activated
    
    # Получаем список применимых акций
    applicable_promotions = promotions.get_applicable_promotions(
        pergola_type=pergola_type,
        width=width,
        length=length,
        base_price=base_price,
        options=options,
        promo_code=promo_code,
        quick_decision_activated=quick_decision_activated
    )
    
    # Отображаем значки акций
    display_promo_badges(applicable_promotions)
    
    # Ищем срочную скидку
    urgent_promotion = None
    for promo in applicable_promotions:
        if any(c.get("type") == promotions.CONDITION_QUICK_DECISION 
               for c in promo.get("conditions", [])):
            # Если есть условие срочной скидки
            if promo.get("activation_required", False) and not quick_decision_activated:
                # Если требуется активация и скидка еще не активирована
                urgent_promotion = promo
                break
    
    # Показываем панель срочной скидки, если она есть
    if urgent_promotion:
        display_urgent_discount_panel(urgent_promotion)
    
    # Отображаем поле для ввода промокода
    entered_promo_code = promo_code_input()
    if entered_promo_code and entered_promo_code != promo_code:
        # Если пользователь ввел новый промокод, обновляем список акций
        st.rerun()
    
    # Рассчитываем скидку на основе применимых акций
    total_discount, applied_promotions = promotions.calculate_discount(
        applicable_promotions=applicable_promotions,
        base_price=base_price,
        options_price=options_price
    )
    
    # Отображаем информацию о примененных скидках, если они есть
    if applied_promotions:
        display_applied_discounts(applied_promotions, total_discount)
    
    return total_discount