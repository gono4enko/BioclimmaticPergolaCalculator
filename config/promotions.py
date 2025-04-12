"""
Модуль для управления сезонными акциями и специальными предложениями.
Содержит конфигурацию скидок, периоды действия и условия применения.
Автоматически определяет текущий сезон и применяет соответствующую акцию.
"""
import datetime
import calendar
from typing import Dict, List, Optional, Union, Tuple, Any

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

# Константы для сезонов
SEASON_SPRING = "spring"
SEASON_SUMMER = "summer"
SEASON_AUTUMN = "autumn"
SEASON_WINTER = "winter"

# Цвета для сезонных акций
SEASON_COLORS = {
    SEASON_SPRING: "#4CAF50",  # Зеленый
    SEASON_SUMMER: "#FFA000",  # Оранжевый
    SEASON_AUTUMN: "#BF360C",  # Темно-оранжевый
    SEASON_WINTER: "#1565C0",  # Синий
}

def get_current_season() -> str:
    """
    Определяет текущий сезон на основе текущей даты
    
    Returns:
        str: Код сезона (spring, summer, autumn, winter)
    """
    today = datetime.date.today()
    month = today.month
    
    if 3 <= month <= 5:
        return SEASON_SPRING
    elif 6 <= month <= 8:
        return SEASON_SUMMER
    elif 9 <= month <= 11:
        return SEASON_AUTUMN
    else:  # month == 12 or month <= 2
        return SEASON_WINTER

def get_season_date_range(season: str, year: Optional[int] = None) -> tuple:
    """
    Возвращает даты начала и окончания указанного сезона
    
    Args:
        season: Код сезона (spring, summer, autumn, winter)
        year: Год (если не указан, используется текущий)
        
    Returns:
        tuple: (дата начала, дата окончания)
    """
    if year is None:
        year = datetime.date.today().year
    
    if season == SEASON_SPRING:
        start_date = datetime.date(year, 3, 1)
        end_date = datetime.date(year, 5, 31)
    elif season == SEASON_SUMMER:
        start_date = datetime.date(year, 6, 1)
        end_date = datetime.date(year, 8, 31)
    elif season == SEASON_AUTUMN:
        start_date = datetime.date(year, 9, 1)
        end_date = datetime.date(year, 11, 30)
    elif season == SEASON_WINTER:
        # Зима может охватывать два года
        if datetime.date.today().month == 12:
            # Если сейчас декабрь, то зима начинается в этом году и заканчивается в следующем
            start_date = datetime.date(year, 12, 1)
            end_date = datetime.date(year + 1, 2, calendar.monthrange(year + 1, 2)[1])
        else:
            # Если сейчас январь или февраль, то зима началась в прошлом году
            start_date = datetime.date(year - 1, 12, 1)
            end_date = datetime.date(year, 2, calendar.monthrange(year, 2)[1])
    else:
        raise ValueError(f"Неизвестный сезон: {season}")
    
    return start_date, end_date

def get_season_name_in_russian(season: str) -> str:
    """
    Возвращает название сезона на русском языке
    
    Args:
        season: Код сезона (spring, summer, autumn, winter)
        
    Returns:
        str: Название сезона на русском
    """
    season_names = {
        SEASON_SPRING: "Весенняя",
        SEASON_SUMMER: "Летняя",
        SEASON_AUTUMN: "Осенняя",
        SEASON_WINTER: "Зимняя"
    }
    return season_names.get(season, "Сезонная")

def generate_seasonal_promotion(discount_value: int = 5) -> Dict:
    """
    Генерирует настройки акции для текущего сезона
    
    Args:
        discount_value: Размер скидки в процентах
        
    Returns:
        Dict: Настройки сезонной акции
    """
    current_season = get_current_season()
    current_year = datetime.date.today().year
    start_date, end_date = get_season_date_range(current_season, current_year)
    season_name_ru = get_season_name_in_russian(current_season)
    
    return {
        "name": f"{season_name_ru} акция {current_year}",
        "description": f"Скидка {discount_value}% на все перголы до {end_date.strftime('%d.%m.%Y')}",
        "discount_type": DISCOUNT_TYPE_PERCENTAGE,
        "discount_value": discount_value,
        "conditions": [
            {
                "type": CONDITION_DATE_RANGE,
                "start_date": start_date,
                "end_date": end_date
            }
        ],
        "display_badge": True,
        "badge_text": f"{season_name_ru} акция {discount_value}%",
        "badge_color": SEASON_COLORS[current_season],
        "apply_to_base_price": True,
        "apply_to_options": True,
        "priority": 10,
        "show_countdown": True,
    }

# === Активные акции ===

# Сезонная акция с автоматическим определением текущего сезона
current_season = get_current_season()
season_key = f"{current_season}_sale_{datetime.date.today().year}"

# Словарь со всеми активными акциями
ACTIVE_PROMOTIONS = {
    # Сезонная акция - 5% на все перголы
    season_key: generate_seasonal_promotion(5),
    
    # Акция "Скидка на большие размеры"
    "large_size_discount": {
        "name": "Большие размеры -\nдополнительная скидка",
        "description": "Дополнительная скидка 2% на перголы размером от 7×7 метров",
        "discount_type": DISCOUNT_TYPE_PERCENTAGE,
        "discount_value": 2,  # 2%
        "conditions": [
            {
                "type": CONDITION_SIZE_RANGE,
                "min_width": 7.0,  # Минимальная ширина 7 метров
                "min_length": 7.0,  # Минимальная длина 7 метров
            }
        ],
        "display_badge": True,
        "badge_text": "Дополнительно +2% на большие перголы",
        "badge_color": "#2196F3",  # Синий цвет
        "apply_to_base_price": True,
        "apply_to_options": True,   # Применяется и к опциям тоже
        "priority": 20,
        "stackable": True,          # Суммируется с другими акциями
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
            # Проверяем, что акции с таким ID еще нет в списке
            if not any(p.get("id") == promo_id for p in applicable_promotions):
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
    
    # Разделяем акции на суммируемые и несуммируемые
    stackable_promotions = []
    non_stackable_promotions = []
    
    for promotion in applicable_promotions:
        if promotion.get("stackable", False):
            stackable_promotions.append(promotion)
        else:
            non_stackable_promotions.append(promotion)
    
    # Обрабатываем несуммируемые акции
    # Применяется только самая выгодная (с наивысшим приоритетом)
    if non_stackable_promotions:
        # Берем акцию с самым высоким приоритетом
        promotion = non_stackable_promotions[0]
        
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
            # В данной версии акции бесплатных опций отключены
            discount_amount = 0
            discount_details["discount_display"] = "Бесплатно"
        
        # Добавляем детали скидки
        discount_details["discount_amount"] = discount_amount
        applied_promotions.append(discount_details)
        
        # Суммируем общую скидку
        total_discount += discount_amount
    
    # Обрабатываем суммируемые акции (они добавляются к основной скидке)
    for promotion in stackable_promotions:
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
            discount_details["discount_display"] = f"+{discount_value}%"
        
        elif discount_type == DISCOUNT_TYPE_FIXED:
            discount_amount = min(discount_value, applicable_amount)  # Не больше суммы заказа
            discount_details["discount_display"] = f"+{discount_value:,.0f} ₽"
        
        # Добавляем детали скидки
        discount_details["discount_amount"] = discount_amount
        applied_promotions.append(discount_details)
        
        # Суммируем общую скидку
        total_discount += discount_amount
    
    return total_discount, applied_promotions

def format_countdown_time(end_date=None) -> str:
    """
    Форматирует оставшееся время до окончания акции.
    
    Args:
        end_date: Дата окончания акции, если None, используется стандартный таймер в 24 часа
        
    Returns:
        str: Форматированная строка с оставшимся временем "DD:HH:MM:SS"
    """
    import datetime
    
    if end_date:
        # Рассчитываем оставшееся время до указанной даты
        now = datetime.datetime.now()
        target_date = datetime.datetime.combine(end_date, datetime.time.min)
        
        # Если дата уже прошла, возвращаем нули
        if now >= target_date:
            return "00:00:00:00"
        
        # Рассчитываем разницу во времени
        time_delta = target_date - now
        
        # Рассчитываем дни, часы, минуты и секунды
        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Форматируем строку с обратным отсчетом
        return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        # Для стандартного таймера (24 часа)
        return "00:24:00:00"