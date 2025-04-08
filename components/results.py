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
    # Проверяем наличие результатов
    if not results or 'error' in results:
        error_message = results.get('error', 'Произошла ошибка при расчете стоимости перголы')
        st.error(error_message)
        return
    
    # Добавляем стили для блока результатов
    st.markdown("""
    <style>
    .result-header {
        text-align: center;
        margin-bottom: 1rem;
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .result-container {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        height: 100%;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .download-button {
        text-align: center;
        margin-top: 1rem;
    }
    .download-link {
        display: inline-block;
        background-color: #1E3A8A;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .download-link:hover {
        background-color: #2E4A9A;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем HTML-блок для отображения результатов
    st.markdown('<div class="result-header">Результаты расчета</div>', unsafe_allow_html=True)
    
    # Отображаем сообщение о корректировке длины и другие важные сообщения
    if 'correction_message' in results and results['correction_message']:
        st.warning(results['correction_message'])
    
    # Начинаем контейнер для метрик
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    
    # Создаем метрики для отображения основных показателей
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Итоговая стоимость</div>
            <div class="metric-value">{results['total_cost']} €</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dimensions = results.get('dimensions', {})
        width_m = dimensions.get('width_m', 0)
        length_m = dimensions.get('length_m', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Размеры (Ш×Д)</div>
            <div class="metric-value">{width_m:.2f}×{length_m:.2f} м</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        area = width_m * length_m
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Площадь перголы</div>
            <div class="metric-value">{area:.2f} м²</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Завершаем контейнер для метрик
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Проверяем, является ли выбранная пергола моделью с включенной автоматизацией
    detailed_costs = results.get('detailed_costs', {})
    if "automation_type" in detailed_costs and "automation" in detailed_costs.get('additional_options', {}):
        # Получаем информацию о перголе из сессии
        if 'options' in st.session_state:
            pergola_type = st.session_state.options.get('pergola_type')
            
            if pergola_type == 'B500NEW':
                st.info(f"Для пергол B500NEW автоматизация Bansbach включена в базовую комплектацию. Тип привода ({detailed_costs['automation_type']}) выбран автоматически в зависимости от размеров перголы.")
            
            elif pergola_type == 'B700NEW':
                st.info(f"Для пергол B700NEW автоматизация Somfy включена в базовую комплектацию. Тип привода ({detailed_costs['automation_type']}) выбран автоматически в зависимости от размеров перголы.")
    
    # Отображаем детальную информацию в раскрывающейся панели
    with st.expander("Детальная информация о стоимости"):
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
    
    st.markdown(f"""
    <div class="download-button">
        <a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">
            <i class="fas fa-download"></i> Скачать результаты в CSV
        </a>
    </div>
    """, unsafe_allow_html=True)
    
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
    output.write(f"Ширина: {dimensions.get('width_m', 0):.2f} м\n")
    output.write(f"Длина: {dimensions.get('length_m', 0):.2f} м\n")
    output.write(f"Высота: {dimensions.get('height_m', 0):.2f} м\n")
    
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