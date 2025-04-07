"""
Компонент для отображения результатов расчета
"""
import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime
from utils.logger import log_user_action

def render_results(results):
    """
    Отображает результаты расчета стоимости перголы
    
    Args:
        results (dict): Словарь с результатами расчета
    """
    st.subheader("Результаты расчета")
    
    # Проверяем наличие результатов
    if not results or 'error' in results:
        error_message = results.get('error', 'Произошла ошибка при расчете стоимости перголы')
        st.error(error_message)
        return
    
    # Отображаем сообщение о корректировке длины и другие важные сообщения
    if 'correction_message' in results and results['correction_message']:
        st.warning(results['correction_message'])
        
    # Проверяем, является ли выбранная пергола моделью с включенной автоматизацией
    is_automation_included = False
    detailed_costs = results.get('detailed_costs', {})
    if "automation_type" in detailed_costs and "automation" in detailed_costs.get('additional_options', {}):
        # Получаем информацию о перголе из сессии
        if 'options' in st.session_state:
            pergola_type = st.session_state.options.get('pergola_type')
            
            if pergola_type == 'B500NEW':
                is_automation_included = True
                st.info("Для пергол B500NEW автоматизация Bansbach включена в базовую комплектацию. " +
                       f"Тип привода ({detailed_costs['automation_type']}) выбран автоматически в зависимости от размеров перголы.")
            
            elif pergola_type == 'B700NEW':
                is_automation_included = True
                st.info("Для пергол B700NEW автоматизация Somfy включена в базовую комплектацию. " +
                       f"Тип привода ({detailed_costs['automation_type']}) выбран автоматически в зависимости от размеров перголы.")
    
    # Создаем метрики для отображения основных показателей
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Итоговая стоимость", 
            value=f"{results['total_cost']} €"
        )
    
    with col2:
        dimensions = results.get('dimensions', {})
        width_m = dimensions.get('width_m', 0)
        length_m = dimensions.get('length_m', 0)
        st.metric(
            label="Размеры (Ш×Д)", 
            value=f"{width_m:.3f}×{length_m:.3f} м"
        )
    
    with col3:
        st.metric(
            label="Количество ламелей", 
            value=f"{results.get('lamella_count', 0)} шт."
        )
    
    # Отображаем детальную информацию
    with st.expander("Детальная информация о стоимости"):
        detailed_costs = results.get('detailed_costs', {})
        
        # Создаем DataFrame для более наглядного отображения
        cost_items = [
            ["Базовая стоимость перголы", detailed_costs.get('base_price', 0), "€"]
        ]
        
        # Добавляем стоимость дополнительных колонн
        columns_cost = detailed_costs.get('additional_columns', 0)
        if columns_cost > 0:
            cost_items.append(["Дополнительные колонны", columns_cost, "€"])
            
        # Добавляем стоимость вставки для усиления лотка
        gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
        if gutter_insert_cost > 0:
            cost_items.append(["Вставка для усиления лотка", gutter_insert_cost, "€"])
        
        # Добавляем стоимость освещения и детали
        lighting_cost = detailed_costs.get('lighting', 0)
        if lighting_cost > 0:
            # Получаем детали освещения, если они есть
            lighting_details = detailed_costs.get('lighting_details', {})
            lighting_type = lighting_details.get('type', 'none')
            
            # Импортируем названия типов освещения
            from config.pergola_types import LIGHTING_TYPES
            
            # Формируем название освещения на основе типа
            if lighting_type in LIGHTING_TYPES:
                lighting_name = LIGHTING_TYPES[lighting_type]['name']
            else:
                lighting_name = "Освещение"
                
            cost_items.append([lighting_name, lighting_cost, "€"])
            
            # Если есть детальная информация о компонентах освещения, отображаем её
            if lighting_details:
                led_length = lighting_details.get('led_length', 0)
                led_cost = lighting_details.get('led_cost', 0)
                controllers_count = lighting_details.get('controllers_count', 0)
                controllers_cost = lighting_details.get('controllers_cost', 0)
                
                if led_length > 0:
                    cost_items.append([f"-- Светодиодная лента ({led_length:.2f} м)", led_cost, "€"])
                
                if controllers_count > 0:
                    cost_items.append([f"-- Блоки управления Somfy RTS Dimmer ({controllers_count} шт.)", controllers_cost, "€"])
        
        # Добавляем стоимость дополнительных опций
        additional_options = detailed_costs.get('additional_options', {})
        for option, cost in additional_options.items():
            if option == "automation":
                automation_type = detailed_costs.get('automation_type', 'T1')
                automation_manufacturer = detailed_costs.get('automation_manufacturer', 'Bansbach')
                option_name = f"Автоматизация {automation_manufacturer} ({automation_type})"
            elif option == "motor":
                option_name = "Электропривод"
            elif option == "sound":
                option_name = "Аудиосистема"
            else:
                option_name = f"Опция: {option}"
            cost_items.append([option_name, cost, "€"])
        
        # Общая стоимость
        cost_items.append(["Итого", results['total_cost'], "€"])
        
        # Создаем DataFrame и отображаем его
        df = pd.DataFrame(cost_items, columns=["Наименование", "Стоимость", "Валюта"])
        st.table(df)
    
    # Добавляем кнопку для скачивания результатов в CSV
    csv = generate_csv(results)
    b64 = base64.b64encode(csv.encode()).decode()
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pergola_calculation_{current_date}.csv"
    
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Скачать результаты в CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Логируем действие пользователя
    log_user_action("Просмотр результатов расчета", {"total_cost": results['total_cost']})

def generate_csv(results):
    """
    Генерирует CSV-файл с результатами расчета
    
    Args:
        results (dict): Словарь с результатами расчета
        
    Returns:
        str: Содержимое CSV-файла
    """
    output = io.StringIO()
    
    # Записываем заголовок
    output.write("Расчет стоимости перголы\n")
    output.write(f"Дата расчета: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
    
    # Записываем размеры
    dimensions = results.get('dimensions', {})
    output.write("Размеры перголы:\n")
    output.write(f"Ширина: {dimensions.get('width_m', 0):.3f} м\n")
    output.write(f"Длина: {dimensions.get('length_m', 0):.3f} м\n")
    output.write(f"Высота: {dimensions.get('height_m', 0):.3f} м\n")
    
    # Записываем сообщение о корректировке длины, если оно есть
    if 'correction_message' in results and results['correction_message']:
        output.write(f"\nПримечание: {results['correction_message']}\n")
    
    # Записываем количество ламелей
    output.write(f"Количество ламелей: {results.get('lamella_count', 0)} шт.\n\n")
    
    # Записываем детальные расходы
    detailed_costs = results.get('detailed_costs', {})
    output.write("Детальная информация о стоимости:\n")
    output.write(f"Базовая стоимость перголы: {detailed_costs.get('base_price', 0)} €\n")
    
    # Стоимость дополнительных колонн
    columns_cost = detailed_costs.get('additional_columns', 0)
    if columns_cost > 0:
        output.write(f"Дополнительные колонны: {columns_cost} €\n")
        
    # Стоимость вставки для усиления лотка
    gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
    if gutter_insert_cost > 0:
        output.write(f"Вставка для усиления лотка: {gutter_insert_cost} €\n")
    
    # Стоимость освещения и детали
    lighting_cost = detailed_costs.get('lighting', 0)
    if lighting_cost > 0:
        # Получаем детали освещения, если они есть
        lighting_details = detailed_costs.get('lighting_details', {})
        lighting_type = lighting_details.get('type', 'none')
        
        # Импортируем названия типов освещения
        from config.pergola_types import LIGHTING_TYPES
        
        # Формируем название освещения на основе типа
        if lighting_type in LIGHTING_TYPES:
            lighting_name = LIGHTING_TYPES[lighting_type]['name']
        else:
            lighting_name = "Освещение"
            
        output.write(f"{lighting_name}: {lighting_cost} €\n")
        
        # Если есть детальная информация о компонентах освещения, отображаем её
        if lighting_details:
            led_length = lighting_details.get('led_length', 0)
            led_cost = lighting_details.get('led_cost', 0)
            controllers_count = lighting_details.get('controllers_count', 0)
            controllers_cost = lighting_details.get('controllers_cost', 0)
            
            if led_length > 0:
                output.write(f"-- Светодиодная лента ({led_length:.2f} м): {led_cost} €\n")
            
            if controllers_count > 0:
                output.write(f"-- Блоки управления Somfy RTS Dimmer ({controllers_count} шт.): {controllers_cost} €\n")
    
    # Стоимость дополнительных опций
    additional_options = detailed_costs.get('additional_options', {})
    for option, cost in additional_options.items():
        if option == "automation":
            automation_type = detailed_costs.get('automation_type', 'T1')
            automation_manufacturer = detailed_costs.get('automation_manufacturer', 'Bansbach')
            output.write(f"Автоматизация {automation_manufacturer} ({automation_type}): {cost} €\n")
            
            # Если есть сообщение о выбранном приводе, добавляем его
            automation_message = detailed_costs.get('automation_message', '')
            if automation_message:
                output.write(f"Примечание: {automation_message}\n")
        elif option == "motor":
            output.write(f"Электропривод: {cost} €\n")
        elif option == "sound":
            output.write(f"Аудиосистема: {cost} €\n")
        else:
            output.write(f"Опция {option}: {cost} €\n")
    
    # Общая стоимость
    output.write(f"\nИтоговая стоимость: {results['total_cost']} €\n")
    
    return output.getvalue()