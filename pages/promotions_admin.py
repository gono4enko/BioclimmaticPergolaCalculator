"""
Страница администрирования акций и скидок

Функциональность:
- Просмотр активных и неактивных акций
- Редактирование параметров акций
- Создание новых акций и промокодов
- Статистика по использованию акций
"""
import streamlit as st
import pandas as pd
import os
import json
import datetime
import sys
from typing import Dict, List, Optional

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модуль с акциями
from config import promotions
from components.admin_auth import admin_required, check_admin_auth, admin_login_form

# Константы
PROMOTIONS_DATA_FILE = "data/promotions_data.json"
PROMOTIONS_STATS_FILE = "data/promotions_stats.json"

# Функции для работы с данными
def load_promotions_data() -> Dict:
    """Загружает данные о настройках акций"""
    if not os.path.exists(PROMOTIONS_DATA_FILE):
        # Если файл не существует, используем данные из модуля
        return promotions.ACTIVE_PROMOTIONS
    
    try:
        with open(PROMOTIONS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Преобразуем строковые даты в объекты datetime.date
        for promo_id, promo in data.items():
            for condition in promo.get("conditions", []):
                if condition.get("type") == promotions.CONDITION_DATE_RANGE:
                    if condition.get("start_date"):
                        start_date = datetime.datetime.strptime(
                            condition["start_date"], "%Y-%m-%d").date()
                        condition["start_date"] = start_date
                    if condition.get("end_date"):
                        end_date = datetime.datetime.strptime(
                            condition["end_date"], "%Y-%m-%d").date()
                        condition["end_date"] = end_date
                        
        return data
    except Exception as e:
        st.error(f"Ошибка загрузки данных об акциях: {e}")
        return promotions.ACTIVE_PROMOTIONS

def save_promotions_data(data: Dict) -> None:
    """Сохраняет данные о настройках акций"""
    try:
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(PROMOTIONS_DATA_FILE), exist_ok=True)
        
        # Преобразуем объекты datetime.date в строки для JSON
        data_copy = {}
        for promo_id, promo in data.items():
            promo_copy = promo.copy()
            conditions_copy = []
            
            for condition in promo.get("conditions", []):
                condition_copy = condition.copy()
                if condition.get("type") == promotions.CONDITION_DATE_RANGE:
                    if isinstance(condition.get("start_date"), datetime.date):
                        condition_copy["start_date"] = condition["start_date"].isoformat()
                    if isinstance(condition.get("end_date"), datetime.date):
                        condition_copy["end_date"] = condition["end_date"].isoformat()
                conditions_copy.append(condition_copy)
            
            promo_copy["conditions"] = conditions_copy
            data_copy[promo_id] = promo_copy
        
        with open(PROMOTIONS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_copy, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения данных об акциях: {e}")

def load_promotions_stats() -> Dict:
    """Загружает статистику по использованию акций"""
    if not os.path.exists(PROMOTIONS_STATS_FILE):
        return {}
    
    try:
        with open(PROMOTIONS_STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки статистики акций: {e}")
        return {}

def save_promotions_stats(data: Dict) -> None:
    """Сохраняет статистику по использованию акций"""
    try:
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(PROMOTIONS_STATS_FILE), exist_ok=True)
        
        with open(PROMOTIONS_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения статистики акций: {e}")

def update_promotion(promo_id: str, promo_data: Dict) -> None:
    """Обновляет настройки акции"""
    all_promotions = load_promotions_data()
    all_promotions[promo_id] = promo_data
    save_promotions_data(all_promotions)

def delete_promotion(promo_id: str) -> None:
    """Удаляет акцию"""
    all_promotions = load_promotions_data()
    if promo_id in all_promotions:
        del all_promotions[promo_id]
        save_promotions_data(all_promotions)

def is_promotion_active(promotion: Dict) -> bool:
    """Проверяет, активна ли акция по датам"""
    current_date = datetime.date.today()
    
    for condition in promotion.get("conditions", []):
        if condition.get("type") == promotions.CONDITION_DATE_RANGE:
            start_date = condition.get("start_date")
            end_date = condition.get("end_date")
            
            if start_date and current_date < start_date:
                return False
                
            if end_date and current_date > end_date:
                return False
    
    return True

def format_condition(condition: Dict) -> str:
    """Форматирует условие акции для отображения"""
    cond_type = condition.get("type")
    
    if cond_type == promotions.CONDITION_DATE_RANGE:
        start_date = condition.get("start_date")
        end_date = condition.get("end_date")
        
        if start_date and end_date:
            return f"Действует с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}"
        elif start_date:
            return f"Действует с {start_date.strftime('%d.%m.%Y')}"
        elif end_date:
            return f"Действует до {end_date.strftime('%d.%m.%Y')}"
        
    elif cond_type == promotions.CONDITION_PERGOLA_TYPE:
        types = condition.get("pergola_types", [])
        if types:
            return f"Для типов пергол: {', '.join(types)}"
        
    elif cond_type == promotions.CONDITION_MINIMUM_PRICE:
        min_price = condition.get("min_price", 0)
        return f"При заказе от {min_price:,.0f} ₽"
        
    elif cond_type == promotions.CONDITION_SIZE_RANGE:
        min_width = condition.get("min_width")
        max_width = condition.get("max_width")
        min_length = condition.get("min_length")
        max_length = condition.get("max_length")
        
        size_conditions = []
        if min_width is not None:
            size_conditions.append(f"ширина от {min_width} м")
        if max_width is not None:
            size_conditions.append(f"ширина до {max_width} м")
        if min_length is not None:
            size_conditions.append(f"длина от {min_length} м")
        if max_length is not None:
            size_conditions.append(f"длина до {max_length} м")
            
        return f"Размеры: {', '.join(size_conditions)}"
        
    elif cond_type == promotions.CONDITION_QUICK_DECISION:
        hours = condition.get("hours_limit", 24)
        return f"При оформлении заказа в течение {hours} часов"
        
    elif cond_type == promotions.CONDITION_PROMO_CODE:
        code = condition.get("code", "")
        return f"По промокоду: {code}"
        
    return "Неизвестное условие"

def format_discount(promotion: Dict) -> str:
    """Форматирует скидку для отображения"""
    discount_type = promotion.get("discount_type")
    discount_value = promotion.get("discount_value", 0)
    
    if discount_type == promotions.DISCOUNT_TYPE_PERCENTAGE:
        return f"{discount_value}%"
    elif discount_type == promotions.DISCOUNT_TYPE_FIXED:
        return f"{discount_value:,.0f} ₽"
    elif discount_type == promotions.DISCOUNT_TYPE_FREE_ITEM:
        if discount_value == "delivery":
            return "Бесплатная доставка"
        return "Бесплатная опция"
        
    return "Неизвестный тип скидки"

def edit_promotion_form(promo_id: str = None, promo_data: Dict = None) -> Dict:
    """Форма для создания или редактирования акции"""
    all_promotions = load_promotions_data()
    is_new = promo_id is None
    
    if is_new:
        st.header("Создание новой акции")
        if promo_data is None:
            promo_data = {
                "name": "",
                "description": "",
                "discount_type": promotions.DISCOUNT_TYPE_PERCENTAGE,
                "discount_value": 10,
                "conditions": [
                    {
                        "type": promotions.CONDITION_DATE_RANGE,
                        "start_date": datetime.date.today(),
                        "end_date": (datetime.date.today() + datetime.timedelta(days=30))
                    }
                ],
                "display_badge": True,
                "badge_text": "",
                "badge_color": "#4CAF50",
                "apply_to_base_price": True,
                "apply_to_options": False,
                "priority": 10
            }
    else:
        st.header(f"Редактирование акции '{promo_data['name']}'")
    
    # ID акции (для новых генерируем на основе названия)
    if is_new:
        # ID будет сгенерирован на основе названия
        temp_id = "new_promotion"
    else:
        temp_id = promo_id
    
    # Основные параметры акции
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Название акции", promo_data["name"])
    with col2:
        if is_new:
            suggested_id = name.lower().replace(" ", "_")
            new_promo_id = st.text_input("ID акции (латиницей, без пробелов)", 
                                         suggested_id)
            if new_promo_id in all_promotions:
                st.error("Акция с таким ID уже существует!")
        else:
            st.text_input("ID акции", temp_id, disabled=True)
            new_promo_id = promo_id
    
    description = st.text_area("Описание акции", promo_data["description"])
    
    # Настройки скидки
    discount_type = st.selectbox(
        "Тип скидки",
        [promotions.DISCOUNT_TYPE_PERCENTAGE, 
         promotions.DISCOUNT_TYPE_FIXED,
         promotions.DISCOUNT_TYPE_FREE_ITEM],
        index=[promotions.DISCOUNT_TYPE_PERCENTAGE, 
               promotions.DISCOUNT_TYPE_FIXED,
               promotions.DISCOUNT_TYPE_FREE_ITEM].index(promo_data["discount_type"])
    )
    
    if discount_type == promotions.DISCOUNT_TYPE_PERCENTAGE:
        discount_value = st.slider("Размер скидки (%)", 1, 100, 
                                  int(promo_data["discount_value"]) 
                                  if isinstance(promo_data["discount_value"], (int, float)) else 10)
    elif discount_type == promotions.DISCOUNT_TYPE_FIXED:
        discount_value = st.number_input("Размер скидки (руб.)", 1000, 1000000, 
                                        int(promo_data["discount_value"])
                                        if isinstance(promo_data["discount_value"], (int, float)) else 10000,
                                        step=1000)
    elif discount_type == promotions.DISCOUNT_TYPE_FREE_ITEM:
        discount_value = st.selectbox("Бесплатная опция", 
                                     ["delivery"],
                                     index=0 if promo_data["discount_value"] == "delivery" else 0)
    
    # Условия применения
    st.subheader("Условия применения")
    
    conditions = []
    condition_types = [
        promotions.CONDITION_DATE_RANGE,
        promotions.CONDITION_PERGOLA_TYPE,
        promotions.CONDITION_MINIMUM_PRICE,
        promotions.CONDITION_SIZE_RANGE,
        promotions.CONDITION_QUICK_DECISION,
        promotions.CONDITION_PROMO_CODE
    ]
    
    # Группируем существующие условия по типам
    existing_conditions = {cond["type"]: cond for cond in promo_data["conditions"]}
    
    # Период действия акции
    if st.checkbox("Ограничить период действия", 
                  promotions.CONDITION_DATE_RANGE in existing_conditions):
        date_condition = existing_conditions.get(
            promotions.CONDITION_DATE_RANGE,
            {"type": promotions.CONDITION_DATE_RANGE}
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Дата начала",
                date_condition.get("start_date", datetime.date.today())
            )
        with col2:
            end_date = st.date_input(
                "Дата окончания",
                date_condition.get("end_date", 
                                  datetime.date.today() + datetime.timedelta(days=30))
            )
        
        conditions.append({
            "type": promotions.CONDITION_DATE_RANGE,
            "start_date": start_date,
            "end_date": end_date
        })
    
    # Тип перголы
    if st.checkbox("Только для определенных типов пергол", 
                  promotions.CONDITION_PERGOLA_TYPE in existing_conditions):
        pergola_condition = existing_conditions.get(
            promotions.CONDITION_PERGOLA_TYPE,
            {"type": promotions.CONDITION_PERGOLA_TYPE, "pergola_types": []}
        )
        
        pergola_types = st.multiselect(
            "Выберите типы пергол",
            ["B500NEW", "B700NEW", "B600"],
            pergola_condition.get("pergola_types", [])
        )
        
        conditions.append({
            "type": promotions.CONDITION_PERGOLA_TYPE,
            "pergola_types": pergola_types
        })
    
    # Минимальная сумма
    if st.checkbox("Минимальная сумма заказа", 
                  promotions.CONDITION_MINIMUM_PRICE in existing_conditions):
        price_condition = existing_conditions.get(
            promotions.CONDITION_MINIMUM_PRICE,
            {"type": promotions.CONDITION_MINIMUM_PRICE, "min_price": 100000}
        )
        
        min_price = st.number_input(
            "Минимальная сумма заказа (руб.)",
            10000, 10000000, 
            int(price_condition.get("min_price", 100000)),
            step=10000
        )
        
        conditions.append({
            "type": promotions.CONDITION_MINIMUM_PRICE,
            "min_price": min_price
        })
    
    # Диапазон размеров
    if st.checkbox("Ограничить по размерам", 
                  promotions.CONDITION_SIZE_RANGE in existing_conditions):
        size_condition = existing_conditions.get(
            promotions.CONDITION_SIZE_RANGE,
            {"type": promotions.CONDITION_SIZE_RANGE}
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Ширина")
            use_min_width = st.checkbox("Минимальная ширина", 
                                       size_condition.get("min_width") is not None)
            if use_min_width:
                min_width = st.number_input(
                    "Минимальная ширина (м)",
                    1.0, 20.0, 
                    float(size_condition.get("min_width", 6.0)),
                    step=0.5
                )
            else:
                min_width = None
            
            use_max_width = st.checkbox("Максимальная ширина", 
                                       size_condition.get("max_width") is not None)
            if use_max_width:
                max_width = st.number_input(
                    "Максимальная ширина (м)",
                    1.0, 20.0, 
                    float(size_condition.get("max_width", 10.0)),
                    step=0.5
                )
            else:
                max_width = None
        
        with col2:
            st.subheader("Длина (вынос)")
            use_min_length = st.checkbox("Минимальная длина", 
                                        size_condition.get("min_length") is not None)
            if use_min_length:
                min_length = st.number_input(
                    "Минимальная длина (м)",
                    1.0, 20.0, 
                    float(size_condition.get("min_length", 3.0)),
                    step=0.5
                )
            else:
                min_length = None
            
            use_max_length = st.checkbox("Максимальная длина", 
                                        size_condition.get("max_length") is not None)
            if use_max_length:
                max_length = st.number_input(
                    "Максимальная длина (м)",
                    1.0, 20.0, 
                    float(size_condition.get("max_length", 7.0)),
                    step=0.5
                )
            else:
                max_length = None
        
        conditions.append({
            "type": promotions.CONDITION_SIZE_RANGE,
            "min_width": min_width,
            "max_width": max_width,
            "min_length": min_length,
            "max_length": max_length
        })
    
    # Акция за быстрое решение
    if st.checkbox("Скидка за быстрое решение", 
                  promotions.CONDITION_QUICK_DECISION in existing_conditions):
        quick_condition = existing_conditions.get(
            promotions.CONDITION_QUICK_DECISION,
            {"type": promotions.CONDITION_QUICK_DECISION, "hours_limit": 24}
        )
        
        hours_limit = st.number_input(
            "Лимит времени (часов)",
            1, 72, 
            int(quick_condition.get("hours_limit", 24))
        )
        
        conditions.append({
            "type": promotions.CONDITION_QUICK_DECISION,
            "hours_limit": hours_limit
        })
    
    # Промокод
    if st.checkbox("Активация по промокоду", 
                  promotions.CONDITION_PROMO_CODE in existing_conditions):
        promo_condition = existing_conditions.get(
            promotions.CONDITION_PROMO_CODE,
            {"type": promotions.CONDITION_PROMO_CODE, "code": ""}
        )
        
        promo_code = st.text_input(
            "Промокод",
            promo_condition.get("code", "")
        )
        
        conditions.append({
            "type": promotions.CONDITION_PROMO_CODE,
            "code": promo_code
        })
    
    # Настройки применения скидки
    st.subheader("Настройки применения")
    
    col1, col2 = st.columns(2)
    with col1:
        apply_to_base = st.checkbox(
            "Применять к базовой стоимости",
            promo_data.get("apply_to_base_price", True)
        )
    with col2:
        apply_to_options = st.checkbox(
            "Применять к опциям",
            promo_data.get("apply_to_options", False)
        )
    
    # Настройки отображения
    st.subheader("Настройки отображения")
    
    display_badge = st.checkbox(
        "Показывать значок акции",
        promo_data.get("display_badge", True)
    )
    
    if display_badge:
        badge_text = st.text_input(
            "Текст значка акции",
            promo_data.get("badge_text", name)
        )
        
        badge_color = st.color_picker(
            "Цвет значка акции",
            promo_data.get("badge_color", "#4CAF50")
        )
    else:
        badge_text = ""
        badge_color = "#4CAF50"
    
    # Другие настройки
    st.subheader("Другие настройки")
    
    priority = st.slider(
        "Приоритет акции (выше = важнее)",
        1, 100,
        promo_data.get("priority", 10)
    )
    
    activation_required = st.checkbox(
        "Требуется активация пользователем",
        promo_data.get("activation_required", False)
    )
    
    show_countdown = st.checkbox(
        "Показывать обратный отсчет",
        promo_data.get("show_countdown", False)
    )
    
    # Кнопки действий
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Отмена", type="secondary"):
            st.session_state["show_edit_form"] = False
            st.rerun()
    
    with col2:
        save_button = st.button("Сохранить", type="primary")
    
    if save_button:
        # Формируем обновленную акцию
        updated_promotion = {
            "name": name,
            "description": description,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "conditions": conditions,
            "display_badge": display_badge,
            "badge_text": badge_text,
            "badge_color": badge_color,
            "apply_to_base_price": apply_to_base,
            "apply_to_options": apply_to_options,
            "priority": priority,
            "activation_required": activation_required,
            "show_countdown": show_countdown
        }
        
        # Сохраняем
        if is_new:
            if not new_promo_id:
                st.error("Введите ID акции!")
                return None
            if new_promo_id in all_promotions:
                st.error("Акция с таким ID уже существует!")
                return None
            update_promotion(new_promo_id, updated_promotion)
            st.success(f"Акция '{name}' успешно создана")
        else:
            update_promotion(new_promo_id, updated_promotion)
            st.success(f"Акция '{name}' успешно обновлена")
        
        st.session_state["show_edit_form"] = False
        st.rerun()
    
    return updated_promotion

def main():
    st.set_page_config(
        page_title="Управление акциями и скидками",
        page_icon="🏷️",
        layout="wide"
    )
    
    st.title("Управление акциями и скидками")
    
    # Получаем список всех акций
    all_promotions = load_promotions_data()
    
    # Инициализируем состояние сессии
    if "show_edit_form" not in st.session_state:
        st.session_state["show_edit_form"] = False
    if "edit_promo_id" not in st.session_state:
        st.session_state["edit_promo_id"] = None
    
    # Обработка действий
    if "action" in st.session_state:
        if st.session_state["action"] == "edit" and "promo_id" in st.session_state:
            st.session_state["show_edit_form"] = True
            st.session_state["edit_promo_id"] = st.session_state["promo_id"]
        elif st.session_state["action"] == "delete" and "promo_id" in st.session_state:
            delete_promotion(st.session_state["promo_id"])
            st.success(f"Акция удалена")
            st.session_state.pop("action")
            st.session_state.pop("promo_id")
            st.rerun()
        elif st.session_state["action"] == "new":
            st.session_state["show_edit_form"] = True
            st.session_state["edit_promo_id"] = None
        
        # Сбрасываем действие
        st.session_state.pop("action", None)
    
    # Показываем форму редактирования или основной интерфейс
    if st.session_state["show_edit_form"]:
        if st.session_state["edit_promo_id"] is None:
            edit_promotion_form()
        else:
            promo_id = st.session_state["edit_promo_id"]
            if promo_id in all_promotions:
                edit_promotion_form(promo_id, all_promotions[promo_id])
            else:
                st.error(f"Акция с ID '{promo_id}' не найдена")
                st.session_state["show_edit_form"] = False
                st.rerun()
    else:
        # Кнопка для создания новой акции
        if st.button("Создать новую акцию", type="primary"):
            st.session_state["action"] = "new"
            st.rerun()
        
        # Разделяем акции на активные и неактивные
        active_promotions = {}
        inactive_promotions = {}
        
        for promo_id, promotion in all_promotions.items():
            if is_promotion_active(promotion):
                active_promotions[promo_id] = promotion
            else:
                inactive_promotions[promo_id] = promotion
        
        # Отображаем активные акции
        st.header("Активные акции")
        if not active_promotions:
            st.info("Активные акции отсутствуют")
        else:
            for promo_id, promotion in active_promotions.items():
                with st.expander(f"{promotion['name']} ({format_discount(promotion)})", expanded=True):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Описание:** {promotion['description']}")
                        
                        # Отображаем условия
                        for condition in promotion.get("conditions", []):
                            st.markdown(f"- {format_condition(condition)}")
                    
                    with col2:
                        if promotion.get("display_badge"):
                            st.markdown(f"""
                            <div style="background-color: {promotion['badge_color']}; 
                                       color: white; 
                                       padding: 5px 10px; 
                                       border-radius: 4px; 
                                       display: inline-block;
                                       font-weight: bold;">
                                {promotion.get('badge_text', promotion['name'])}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col3:
                        if st.button("Редактировать", key=f"edit_{promo_id}"):
                            st.session_state["action"] = "edit"
                            st.session_state["promo_id"] = promo_id
                            st.rerun()
                    
                    with col4:
                        if st.button("Удалить", key=f"delete_{promo_id}"):
                            if st.session_state.get("confirm_delete") == promo_id:
                                st.session_state["action"] = "delete"
                                st.session_state["promo_id"] = promo_id
                                st.rerun()
                            else:
                                st.session_state["confirm_delete"] = promo_id
                                st.warning("Нажмите еще раз для подтверждения")
        
        # Отображаем неактивные акции
        st.header("Неактивные акции")
        if not inactive_promotions:
            st.info("Неактивные акции отсутствуют")
        else:
            for promo_id, promotion in inactive_promotions.items():
                with st.expander(f"{promotion['name']} ({format_discount(promotion)})"):
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Описание:** {promotion['description']}")
                        
                        # Отображаем условия
                        for condition in promotion.get("conditions", []):
                            st.markdown(f"- {format_condition(condition)}")
                    
                    with col2:
                        if st.button("Редактировать", key=f"edit_{promo_id}"):
                            st.session_state["action"] = "edit"
                            st.session_state["promo_id"] = promo_id
                            st.rerun()
                    
                    with col3:
                        if st.button("Удалить", key=f"delete_{promo_id}"):
                            if st.session_state.get("confirm_delete") == promo_id:
                                st.session_state["action"] = "delete"
                                st.session_state["promo_id"] = promo_id
                                st.rerun()
                            else:
                                st.session_state["confirm_delete"] = promo_id
                                st.warning("Нажмите еще раз для подтверждения")
        
        # Статистика по использованию акций
        st.header("Статистика использования")
        st.info("Эта функция в разработке. Здесь будет отображаться статистика по использованию акций.")

if __name__ == "__main__":
    main()