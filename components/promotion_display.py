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
            width: 85%;
            margin-left: auto;
            margin-right: auto;
            justify-content: center;
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
    С автоматическим определением сезонной акции.
    
    Args:
        urgent_promotion: Информация о срочной скидке
        
    Returns:
        bool: True если скидка активирована
    """
    # Обновляем информацию о сезонной акции
    current_season = promotions.get_current_season()
    season_key = f"{current_season}_sale_{datetime.datetime.now().year}"
    
    # Проверяем, что предоставленная акция актуальна для текущего сезона
    # Если нет, генерируем новую сезонную акцию
    promo_id = urgent_promotion.get("id") if urgent_promotion else None
    if not urgent_promotion or (
        isinstance(promo_id, str) and 
        not promo_id.startswith(current_season)
    ):
        # Создаем актуальную сезонную акцию
        urgent_promotion = {
            "id": season_key,
            **promotions.generate_seasonal_promotion(5)
        }
    
    if not urgent_promotion:
        return False
    
    # Проверяем, активирована ли скидка
    if "urgent_discount_activated" not in st.session_state:
        st.session_state.urgent_discount_activated = False
    
    # Находим дату окончания акции из условий
    end_date = None
    for condition in urgent_promotion.get("conditions", []):
        if condition.get("type") == promotions.CONDITION_DATE_RANGE and "end_date" in condition:
            end_date = condition["end_date"]
            break
    
    # Если нет даты окончания, используем стандартный таймер
    if "urgent_discount_time" not in st.session_state and not end_date:
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
    
    # Получаем форматированное время до окончания акции
    if end_date:
        countdown_str = promotions.format_countdown_time(end_date)
        # Разбиваем строку на компоненты (ДД:ЧЧ:ММ:СС)
        parts = countdown_str.split(":")
        days = int(parts[0])
        hours = int(parts[1])
        minutes = int(parts[2])
        seconds = int(parts[3])
        
        # Вычисляем общее время в миллисекундах для JavaScript
        total_ms = ((days * 24 + hours) * 60 + minutes) * 60 + seconds
        total_ms = total_ms * 1000
        
        # Форматируем для отображения
        if days > 0:
            display_text = f"{days} дн. {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            display_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        # Используем стандартный таймер
        remaining_time = st.session_state.urgent_discount_time - time.time()
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        seconds = int(remaining_time % 60)
        total_ms = int(remaining_time * 1000)
        display_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Получаем информацию о текущем сезоне для панели
    season_name_ru = promotions.get_season_name_in_russian(current_season)
    season_color = promotions.SEASON_COLORS.get(current_season, '#4CAF50')  # Зеленый цвет по умолчанию
    
    # Отображаем панель со срочной скидкой
    with st.container():
        season_name_ru = promotions.get_season_name_in_russian(current_season)
        promo_title = urgent_promotion.get('name', f'{season_name_ru} акция {datetime.datetime.now().year}')
        promo_description = urgent_promotion.get('description', f'Скидка {urgent_promotion.get("discount_value", 5)}% до конца сезона!')
        
        # Добавляем стили для заголовка и описания
        st.markdown(f"""
        <style>
        .urgent-panel {{
            background-color: {urgent_promotion.get('badge_color', season_color)};
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            margin-top: -5px;
            position: relative;
            overflow: hidden;
            width: 85%;
            margin-left: auto;
            margin-right: auto;
        }}
        .urgent-panel h4 {{
            margin: 0 0 2px 0;
            font-size: 1.1rem;
            text-align: center;
        }}
        .urgent-panel p {{
            margin: 0 0 10px 0;
            font-size: 1.25rem;
            text-align: center;
            font-weight: 500;
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
                font-size: 1rem;
            }}
            .countdown {{
                font-size: 0.9rem;
            }}
        }}
        </style>
        <div class="urgent-panel pulse-animation">
            <h4>{promo_title}</h4>
            <p>{promo_description}</p>
            <div class="countdown-container" style="text-align: center;">
                <span>До окончания акции: </span>
                <span class="countdown" id="countdown">{display_text}</span>
            </div>
            <!-- Кнопка активации скидки удалена, скидка применяется автоматически -->
        </div>
        """, unsafe_allow_html=True)
        
        # Обратный отсчет с помощью JavaScript
        st.markdown(f"""
        <script>
            // Устанавливаем начальное время
            var countDownDate = new Date().getTime() + {total_ms};
            
            // Функция для форматирования чисел с ведущим нулем
            function formatNumber(num) {{
                return num < 10 ? '0' + num : num;
            }}
            
            // Обновляем таймер каждую секунду
            var x = setInterval(function() {{
                var now = new Date().getTime();
                var distance = countDownDate - now;
                
                // Расчеты для дней, часов, минут и секунд
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                // Отображаем результат
                var displayText = "";
                if (days > 0) {{
                    displayText = days + " дн. " + formatNumber(hours) + ":" + formatNumber(minutes) + ":" + formatNumber(seconds);
                }} else {{
                    displayText = formatNumber(hours) + ":" + formatNumber(minutes) + ":" + formatNumber(seconds);
                }}
                
                document.getElementById("countdown").innerHTML = displayText;
                
                // Если время истекло
                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("countdown").innerHTML = "ВРЕМЯ ИСТЕКЛО";
                }}
            }}, 1000);
        </script>
        """, unsafe_allow_html=True)
        
        # Устанавливаем автоматическое применение скидки
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
        margin-top: 5px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        overflow: hidden;
        width: 100%;
    }
    .discounts-header {
        background-color: #F5F5F5;
        padding: 10px 15px;
        font-weight: bold;
        border-bottom: 1px solid #E0E0E0;
        text-align: center;
    }
    .discount-item {
        padding: 10px 15px;
        border-bottom: 1px solid #E0E0E0;
        display: flex;
        justify-content: space-between;
        padding-left: 25px;
        padding-right: 25px;
    }
    .discount-item:first-child {
        margin-top: 10px;
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
        padding-left: 25px;
        padding-right: 25px;
    }
    @media (max-width: 768px) {
        .discounts-header, .discount-item, .discount-total {
            padding: 8px 10px;
            font-size: 0.8rem;
        }
    }
    </style>
    <div style="width:85%; margin:0 auto; padding-left:25px; padding-right:25px;">
        <div class="discounts-container">
            <div class="discounts-header">Примененные скидки</div>
    """, unsafe_allow_html=True)
    
    for promo in applied_promotions:
        discount_display = promo.get("discount_display", "")
        discount_amount = promo.get("discount_amount", 0)
        
        # Проверяем, содержит ли имя акции символ новой строки
        promo_name = promo.get('name', 'Скидка')
        name_with_discount = f"{promo_name} ({discount_display})"
        
        # Если это акция про большие размеры, перестраиваем текст
        if "Большие размеры" in promo_name:
            name_with_discount = f"Большие размеры<br>дополнительная скидка ({discount_display})"
        
        st.markdown(f"""
        <div class="discount-item">
            <div class="discount-name">{name_with_discount}</div>
            <div class="discount-amount">-{discount_amount:,.0f} ₽</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="discount-total">
            <div>Общая скидка:</div>
            <div>-{total_discount:,.0f} ₽</div>
        </div>
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
    # Промокоды отключены
    promo_code = None
    
    # Акция быстрого решения отключена
    quick_decision_activated = False
    # Эта функциональность отключена
    if "urgent_discount_activated" not in st.session_state:
        st.session_state.urgent_discount_activated = False
    
    # Получаем список применимых акций и скидок
    applicable_promotions = promotions.get_applicable_promotions(
        pergola_type, width, length, base_price, 
        options, promo_code, quick_decision_activated
    )
    
    # Отображаем бейджи акций
    display_promo_badges(applicable_promotions)
    
    # Отображаем сезонную акцию, если она есть в списке
    season_promo = None
    # Список сезонов для поиска в ID акции
    seasons = [promotions.SEASON_SPRING, promotions.SEASON_SUMMER, 
               promotions.SEASON_AUTUMN, promotions.SEASON_WINTER]
    for promo in applicable_promotions:
        promo_id = promo.get("id", "")
        if isinstance(promo_id, str) and any(season in promo_id for season in seasons):
            season_promo = promo
            break
    
    if season_promo:
        display_urgent_discount_panel(season_promo)
    
    # Поле для ввода промокода отключено
    
    # Рассчитываем итоговую скидку на основе применимых акций
    total_discount, applied_promotions_list = promotions.calculate_discount(applicable_promotions, base_price, options_price)
    
    # Если есть применимые акции, отображаем их
    if len(applied_promotions_list) > 0:
        display_applied_discounts(
            applied_promotions_list,
            total_discount
        )
    
    return total_discount