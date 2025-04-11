"""
Модуль для управления сезонными акциями и специальными предложениями.
Содержит конфигурацию скидок, периоды действия и условия применения.
"""
import datetime
from typing import Dict, List, Optional, Union, Tuple

# Типы скидок
DISCOUNT_TYPE_PERCENTAGE = "percentage"  # Скидка в процентах
DISCOUNT_TYPE_FIXED = "fixed"  # Фиксированная скидка в рублях
DISCOUNT_TYPE_FREE_ITEM = "free_item"  # Бесплатный предмет или опция

# Типы условий
CONDITION_DATE_RANGE = "date_range"  # Скидка в определенный период
CONDITION_PERGOLA_TYPE = "pergola_type"  # Скидка на определенный тип перголы
CONDITION_MINIMUM_PRICE = "minimum_price"  # Скидка при минимальной сумме заказа
CONDITION_SIZE_RANGE = "size_range"  # Скидка на определенный размер перголы
CONDITION_QUICK_DECISION = "quick_decision"  # Скидка за быстрое решение
CONDITION_PROMO_CODE = "promo_code"  # Скидка по промокоду

# === Активные акции ===

# Словарь со всеми активными акциями
ACTIVE_PROMOTIONS = {
    # Весенняя акция - 5% на все перголы
    "spring_sale_2025": {
        "name": "Весенняя акция 2025",
        "description": "Скидка 5% на все перголы при заказе до 31 мая",
        "discount_type": DISCOUNT_TYPE_PERCENTAGE,
        "discount_value": 5,  # 5%
        "conditions": [
            {
                "type": CONDITION_DATE_RANGE,
                "start_date": datetime.date(2025, 3, 1),
                "end_date": datetime.date(2025, 5, 31)
            }
        ],
        "display_badge": True,
        "badge_text": "Весенняя скидка 5%",
        "badge_color": "#4CAF50",  # Зеленый цвет
        "apply_to_base_price": True,  # Скидка применяется к базовой стоимости перголы
        "apply_to_options": False,  # Не применяется к опциям
        "priority": 10,  # Приоритет акции (чем выше, тем важнее)
    },
    
    # Акция "Большая скидка на большие размеры"
    "large_size_discount": {
        "name": "Большие размеры - большие скидки",
        "description": "Скидка 7% на перголы размером от 7×7 метров",
        "discount_type": DISCOUNT_TYPE_PERCENTAGE,
        "discount_value": 7,  # 7%
        "conditions": [
            {
                "type": CONDITION_SIZE_RANGE,
                "min_width": 7.0,  # Минимальная ширина 7 метров
                "min_length": 7.0,  # Минимальная длина 7 метров
            }
        ],
        "display_badge": True,
        "badge_text": "Скидка 7% на большие перголы",
        "badge_color": "#2196F3",  # Синий цвет
        "apply_to_base_price": True,
        "apply_to_options": False,
        "priority": 20,
    },
    
    # Акция "Бесплатная доставка"
    "free_delivery": {
        "name": "Бесплатная доставка",
        "description": "Бесплатная доставка при заказе перголы стоимостью от 500 000 ₽",
        "discount_type": DISCOUNT_TYPE_FREE_ITEM,
        "discount_value": "delivery",  # Код опции, которая становится бесплатной
        "conditions": [
            {
                "type": CONDITION_MINIMUM_PRICE,
                "min_price": 500000,  # Минимальная стоимость заказа
            }
        ],
        "display_badge": True,
        "badge_text": "Бесплатная доставка",
        "badge_color": "#9C27B0",  # Фиолетовый цвет
        "apply_to_base_price": False,
        "apply_to_options": True,
        "priority": 5,
    },
    
    # Акция быстрого решения - срочная скидка
    "urgent_discount": {
        "name": "Скидка за быстрое решение",
        "description": "Дополнительная скидка 5% при оформлении заказа в течение 24 часов",
        "discount_type": DISCOUNT_TYPE_PERCENTAGE,
        "discount_value": 5,  # 5%
        "conditions": [
            {
                "type": CONDITION_QUICK_DECISION,
                "hours_limit": 24,  # Лимит времени в часах
            }
        ],
        "display_badge": True,
        "badge_text": "Срочная скидка 5% - только 24 часа!",
        "badge_color": "#F44336",  # Красный цвет для срочности
        "apply_to_base_price": True,
        "apply_to_options": True,  # Применяется ко всему заказу
        "priority": 30,  # Высокий приоритет
        "activation_required": True,  # Требуется активация пользователем
        "show_countdown": True,  # Показывать обратный отсчет
    },
    
    # Промокод на скидку
    "promo_code_spring2025": {
        "name": "Промокод ВЕСНА2025",
        "description": "Скидка 7% при использовании промокода ВЕСНА2025",
        "discount_type": DISCOUNT_TYPE_PERCENTAGE,
        "discount_value": 7,  # 7%
        "conditions": [
            {
                "type": CONDITION_PROMO_CODE,
                "code": "ВЕСНА2025",
            }
        ],
        "display_badge": False,  # Не показывать значок, только после активации
        "badge_text": "Промокод активирован: -7%",
        "badge_color": "#FF9800",  # Оранжевый цвет
        "apply_to_base_price": True,
        "apply_to_options": True,
        "priority": 15,
        "activation_required": True,  # Требуется ввод промокода
    }
}

# === Функции для работы с акциями ===

def get_active_promotions() -> Dict:
    """
    Возвращает все активные акции с учетом текущей даты.
    
    Returns:
        Dict: Словарь с активными акциями
    """
    current_date = datetime.date.today()
    active_promotions = {}
    
    for promo_id, promotion in ACTIVE_PROMOTIONS.items():
        is_active = True
        
        # Проверяем условия по датам
        for condition in promotion.get("conditions", []):
            if condition["type"] == CONDITION_DATE_RANGE:
                start_date = condition.get("start_date")
                end_date = condition.get("end_date")
                
                if start_date and current_date < start_date:
                    is_active = False
                    break
                    
                if end_date and current_date > end_date:
                    is_active = False
                    break
        
        if is_active:
            active_promotions[promo_id] = promotion
            
    return active_promotions

def get_applicable_promotions(
    pergola_type: str, 
    width: float, 
    length: float, 
    base_price: float, 
    options: Dict,
    promo_code: Optional[str] = None,
    quick_decision_activated: bool = False
) -> List[Dict]:
    """
    Определяет, какие акции применимы к конкретной конфигурации перголы.
    
    Args:
        pergola_type: Тип перголы (B500NEW, B700NEW, B600)
        width: Ширина перголы в метрах
        length: Длина (вынос) перголы в метрах
        base_price: Базовая стоимость перголы
        options: Словарь с выбранными опциями
        promo_code: Введенный промокод (если есть)
        quick_decision_activated: Активирована ли акция быстрого решения
        
    Returns:
        List[Dict]: Список применимых акций
    """
    active_promotions = get_active_promotions()
    applicable_promotions = []
    
    for promo_id, promotion in active_promotions.items():
        is_applicable = True
        conditions = promotion.get("conditions", [])
        
        # Проверяем требуется ли активация
        if promotion.get("activation_required", False):
            # Для промокода
            if any(c["type"] == CONDITION_PROMO_CODE for c in conditions) and not promo_code:
                is_applicable = False
            # Для быстрого решения
            elif any(c["type"] == CONDITION_QUICK_DECISION for c in conditions) and not quick_decision_activated:
                is_applicable = False
        
        # Проверяем остальные условия
        for condition in conditions:
            # Проверка типа перголы
            if condition["type"] == CONDITION_PERGOLA_TYPE:
                if pergola_type not in condition.get("pergola_types", []):
                    is_applicable = False
                    break
            
            # Проверка диапазона размеров
            elif condition["type"] == CONDITION_SIZE_RANGE:
                min_width = condition.get("min_width")
                max_width = condition.get("max_width")
                min_length = condition.get("min_length")
                max_length = condition.get("max_length")
                
                if min_width is not None and width < min_width:
                    is_applicable = False
                    break
                if max_width is not None and width > max_width:
                    is_applicable = False
                    break
                if min_length is not None and length < min_length:
                    is_applicable = False
                    break
                if max_length is not None and length > max_length:
                    is_applicable = False
                    break
            
            # Проверка минимальной цены
            elif condition["type"] == CONDITION_MINIMUM_PRICE:
                if base_price < condition.get("min_price", 0):
                    is_applicable = False
                    break
            
            # Проверка промокода
            elif condition["type"] == CONDITION_PROMO_CODE:
                if promo_code != condition.get("code"):
                    is_applicable = False
                    break
        
        # Если все условия выполнены, добавляем акцию в список применимых
        if is_applicable:
            applicable_promotions.append({
                "id": promo_id,
                **promotion
            })
    
    # Сортируем акции по приоритету (от высокого к низкому)
    return sorted(applicable_promotions, key=lambda p: p.get("priority", 0), reverse=True)

def calculate_discount(
    applicable_promotions: List[Dict],
    base_price: float,
    options_price: float
) -> Tuple[float, List[Dict]]:
    """
    Рассчитывает общую скидку на основе применимых акций.
    
    Args:
        applicable_promotions: Список применимых акций
        base_price: Базовая стоимость перголы
        options_price: Стоимость дополнительных опций
        
    Returns:
        Tuple[float, List[Dict]]: Общая сумма скидки и список примененных акций с деталями
    """
    total_discount = 0
    applied_promotions = []
    
    # Для каждой акции рассчитываем скидку
    for promotion in applicable_promotions:
        discount_type = promotion.get("discount_type")
        discount_value = promotion.get("discount_value", 0)
        apply_to_base = promotion.get("apply_to_base_price", True)
        apply_to_options = promotion.get("apply_to_options", False)
        
        discount_amount = 0
        discount_details = {
            "id": promotion.get("id"),
            "name": promotion.get("name"),
            "description": promotion.get("description"),
            "badge_text": promotion.get("badge_text"),
            "badge_color": promotion.get("badge_color")
        }
        
        # Вычисляем сумму для скидки
        applicable_amount = 0
        if apply_to_base:
            applicable_amount += base_price
        if apply_to_options:
            applicable_amount += options_price
        
        # Рассчитываем скидку в зависимости от типа
        if discount_type == DISCOUNT_TYPE_PERCENTAGE:
            discount_amount = applicable_amount * (discount_value / 100)
            discount_details["discount_display"] = f"{discount_value}%"
        
        elif discount_type == DISCOUNT_TYPE_FIXED:
            discount_amount = min(discount_value, applicable_amount)  # Не больше суммы заказа
            discount_details["discount_display"] = f"{discount_value:,.0f} ₽"
        
        # Для бесплатных опций - логика обрабатывается отдельно
        elif discount_type == DISCOUNT_TYPE_FREE_ITEM:
            # Здесь особая логика в зависимости от типа бесплатной опции
            if discount_value == "delivery":
                # Ищем стоимость доставки среди опций
                if options_price > 0 and 'delivery' in options:
                    discount_amount = options.get('delivery', {}).get('price', 0)
            discount_details["discount_display"] = "Бесплатно"
        
        # Добавляем детали скидки
        discount_details["discount_amount"] = discount_amount
        applied_promotions.append(discount_details)
        
        # Суммируем общую скидку
        total_discount += discount_amount
    
    return total_discount, applied_promotions

def format_countdown_time(hours: int = 24) -> str:
    """
    Форматирует оставшееся время для акции с обратным отсчетом.
    
    Args:
        hours: Количество часов для обратного отсчета
        
    Returns:
        str: Форматированная строка с оставшимся временем
    """
    # В реальном приложении здесь будет логика для сохранения
    # времени начала отсчета в сессии или cookies
    return f"{hours}:00:00"