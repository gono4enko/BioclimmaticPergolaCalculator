"""
Модуль для расчета стоимости пергол на основе введенных данных
"""
import logging
from config.pergola_types import (
    PERGOLA_TYPES, 
    LAMELLA_TYPES, 
    INSTALLATION_TYPES,
    LIGHTING_TYPES,
    ADDITIONAL_SYSTEMS
)
from config.price_data import (
    BASE_PRICE_PER_M2,
    COMPONENT_PRICES,
    AREA_DISCOUNTS,
    COMPLEXITY_FACTORS,
    AUTOMATION_PRICE,
    DELIVERY_FACTORS
)

# Получаем логгер
logger = logging.getLogger(__name__)

def calculate_lamella_count(length, lamella_step):
    """Расчет количества ламелей на основе длины и шага"""
    return round(length / lamella_step)

def calculate_pergola_cost(dimensions, options):
    """
    Рассчитывает стоимость перголы на основе заданных размеров и опций.
    
    Args:
        dimensions (dict): Словарь с размерами перголы (ширина, длина, высота)
        options (dict): Словарь с выбранными опциями
        
    Returns:
        dict: Словарь с результатами расчетов
    """
    try:
        # Извлекаем данные из входных словарей
        width = dimensions['width']  # ширина в мм
        length = dimensions['length']  # длина в мм
        height = dimensions['height']  # высота в мм
        
        pergola_type = options['pergola_type']
        lamella_type = options['lamella_type']
        installation_type = options['installation_type']
        lighting_type = options['lighting_type']
        control_type = options['control_type']
        color_type = options['color_type']
        
        selected_additional_systems = options.get('additional_systems', [])
        
        # Конвертируем размеры в метры для расчетов
        width_m = width / 1000
        length_m = length / 1000
        height_m = height / 1000
        
        # Рассчитываем базовую площадь
        area = width_m * length_m
        perimeter = 2 * (width_m + length_m)
        
        # Получаем данные о типе перголы и ламелей
        pergola_data = PERGOLA_TYPES[pergola_type]
        lamella_data = LAMELLA_TYPES[lamella_type]
        installation_data = INSTALLATION_TYPES[installation_type]
        
        # 1. Расчет базовой стоимости конструкции
        base_price = area * BASE_PRICE_PER_M2 * pergola_data['base_price_factor']
        
        # 2. Расчет стоимости ламелей
        lamella_count = calculate_lamella_count(length, lamella_data['step'])
        single_lamella_price = lamella_data['price_factor'] * width_m * lamella_data['mass'] * 40  # 40 евро за кг
        lamellas_price = lamella_count * single_lamella_price
        
        # 3. Расчет стоимости колонн
        column_count = 4 if installation_type == "standalone" else 2
        columns_price = column_count * COMPONENT_PRICES['column'] * (height_m / 3)  # Цена колонны зависит от высоты
        
        # 4. Расчет стоимости управления
        control_price = COMPONENT_PRICES[control_type]
        
        # 5. Расчет стоимости освещения
        lighting_data = LIGHTING_TYPES[lighting_type]
        lighting_price = lighting_data.get('price_per_meter', 0) * perimeter if lighting_type != 'none' else 0
        
        # 6. Расчет стоимости дополнительных систем
        additional_systems_price = 0
        additional_systems_details = []
        
        for system in selected_additional_systems:
            if system in ADDITIONAL_SYSTEMS:
                system_data = ADDITIONAL_SYSTEMS[system]
                system_price = system_data['price_per_m2'] * area
                additional_systems_price += system_price
                
                additional_systems_details.append({
                    'name': system_data['name'],
                    'area': round(area, 2),
                    'price_per_m2': system_data['price_per_m2'],
                    'total_price': round(system_price, 2)
                })
        
        # 7. Расчет стоимости окраски
        color_price = COMPONENT_PRICES[color_type]
        
        # 8. Применение коэффициента типа установки
        installation_factor = installation_data['price_factor']
        
        # 9. Применение скидки на площадь
        area_discount = 0
        for discount_tier in AREA_DISCOUNTS:
            if discount_tier['min_area'] <= area <= discount_tier['max_area']:
                area_discount = discount_tier['discount']
                break
        
        # 10. Определение сложности конфигурации
        complexity = "standard"
        if len(selected_additional_systems) > 0 or lighting_type != 'none':
            complexity = "complex"
        if control_type == 'smart_control' or color_type == 'custom_color':
            complexity = "custom"
            
        complexity_factor = COMPLEXITY_FACTORS[complexity]
        
        # 11. Расчет стоимости автоматизации
        automation_category = "small"
        if 20 <= area < 40:
            automation_category = "medium"
        elif 40 <= area < 80:
            automation_category = "large"
        elif area >= 80:
            automation_category = "extra_large"
            
        automation_price = AUTOMATION_PRICE[automation_category] if control_type != 'manual_control' else 0
        
        # 12. Расчет итоговой стоимости
        subtotal = (base_price + lamellas_price + columns_price + control_price + 
                    lighting_price + additional_systems_price + color_price) * installation_factor * complexity_factor
        
        discount_amount = subtotal * area_discount
        total_price_before_automation = subtotal - discount_amount
        total_cost = total_price_before_automation + automation_price
        
        # Формируем результат
        result = {
            'dimensions': {
                'width': width,
                'length': length,
                'height': height,
                'area': round(area, 2),
                'perimeter': round(perimeter, 2)
            },
            'selected_options': {
                'pergola_type': pergola_data['name'],
                'lamella_type': lamella_data['name'],
                'installation_type': installation_data['name'],
                'lighting_type': LIGHTING_TYPES[lighting_type]['name'],
                'control_type': control_type.replace('_', ' ').title(),
                'color_type': color_type.replace('_', ' ').title(),
                'additional_systems': selected_additional_systems
            },
            'cost_breakdown': {
                'base_structure': round(base_price, 2),
                'lamellas': {
                    'count': lamella_count,
                    'price_per_unit': round(single_lamella_price, 2),
                    'total_price': round(lamellas_price, 2)
                },
                'columns': {
                    'count': column_count,
                    'price_per_unit': round(COMPONENT_PRICES['column'] * (height_m / 3), 2),
                    'total_price': round(columns_price, 2)
                },
                'control': round(control_price, 2),
                'lighting': round(lighting_price, 2),
                'additional_systems': {
                    'total_price': round(additional_systems_price, 2),
                    'details': additional_systems_details
                },
                'color': round(color_price, 2),
                'installation_factor': installation_factor,
                'complexity_factor': complexity_factor,
                'area_discount': area_discount,
                'discount_amount': round(discount_amount, 2),
                'automation': round(automation_price, 2)
            },
            'total_cost': round(total_cost, 2)
        }
        
        logger.info(f"Успешный расчет стоимости перголы: {result['total_cost']} евро")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при расчете стоимости перголы: {str(e)}", exc_info=True)
        raise
