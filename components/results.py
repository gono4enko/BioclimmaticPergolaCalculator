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
    
    # Добавляем стили для современного блока результатов
    st.markdown("""
    <style>
    .results-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        overflow: hidden;
    }
    .results-header {
        background-color: #4a69bd;
        color: white;
        padding: 1rem;
        font-size: 1.3rem;
        font-weight: bold;
        text-align: center;
    }
    .results-content {
        display: flex;
        flex-wrap: wrap;
        padding: 1rem;
    }
    .metric-card {
        flex: 1 1 calc(33.333% - 1rem);
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .metric-price {
        font-size: 2rem;
        font-weight: bold;
        color: #4a69bd;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #666;
    }
    .download-button {
        text-align: center;
        margin-top: 1.5rem;
    }
    @media (max-width: 768px) {
        .metric-card {
            flex: 1 1 100%;
        }
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
    /* Настраиваем отображение номеров строк */
    .col_heading.level0.col0, .data.row0.col0, .data.row1.col0, .data.row2.col0, .data.row3.col0, .data.row4.col0, 
    .data.row5.col0, .data.row6.col0, .data.row7.col0, .data.row8.col0, .data.row9.col0, .data.row10.col0, .data.row11.col0 {
        text-align: center !important;
        width: 40px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем современную карточку для отображения результатов
    st.markdown("""
    <div class="results-card">
        <div class="results-header">Результаты расчета</div>
        <div class="results-content">
    """, unsafe_allow_html=True)
    
    # Получаем основные данные для отображения
    dimensions = results.get('dimensions', {})
    width_m = dimensions.get('width_m', 0)
    length_m = dimensions.get('length_m', 0)
    area = round(width_m * length_m, 2)
    
    # Определяем количество модулей
    detailed_costs = results.get('detailed_costs', {})
    additional_columns_cost = detailed_costs.get('additional_columns', 0)
    
    # Определяем количество модулей по ширине
    modules_count = 1
    if additional_columns_cost > 0:
        # Стоимость дополнительных колонн зависит от количества модулей
        # 1 модуль - 653€, 2 модуля - 980€, 3 модуля - 1306€
        if abs(additional_columns_cost - 653) < 1:
            modules_count = 1
        elif abs(additional_columns_cost - 980) < 1:
            modules_count = 2
        elif abs(additional_columns_cost - 1306) < 1:
            modules_count = 3
        else:
            # По умолчанию определяем количество модулей по ширине
            if width_m > 7:
                modules_count = 3
            elif width_m > 4:
                modules_count = 2
    else:
        # По умолчанию определяем количество модулей по ширине
        if width_m > 7:
            modules_count = 3
        elif width_m > 4:
            modules_count = 2
    
    # Отображаем основные метрики
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-price">{results['total_cost']} €</div>
        <div class="metric-label">Итоговая стоимость</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-value">{width_m:.1f}×{length_m:.1f} м</div>
        <div class="metric-label">Размеры (Ш×В)</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-value">{area:.1f} м²</div>
        <div class="metric-label">Площадь перголы</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-value">{modules_count}</div>
        <div class="metric-label">Количество модулей</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Закрываем контейнер
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    with st.expander("Детальная информация о стоимости", expanded=False):
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
                
                # Добавляем информацию о пульте управления
                if 'remote_control' in detailed_costs and 'remote_control_cost' in detailed_costs:
                    cost_items.append([f"Пульт ДУ {detailed_costs['remote_control']}", detailed_costs['remote_control_cost'], "€"])
            elif option == "motor":
                option_name = "Электропривод"
            elif option == "sound":
                option_name = "Аудиосистема"
            else:
                option_name = f"Опция: {option}"
            cost_items.append([option_name, cost, "€"])
        
        # Общая стоимость
        cost_items.append(["Итого", results['total_cost'], "€"])
        
        # Создаем DataFrame и отображаем его в развернутом виде
        df = pd.DataFrame(cost_items, columns=["Наименование", "Стоимость", "Валюта"])
        
        # Применяем стиль для выделения итоговой строки
        st.markdown("""
        <style>
        .dataframe tr:last-child {
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Отображаем таблицу без свернутого вида (с развернутыми строками)
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
    width_m = dimensions.get('width_m', 0)
    length_m = dimensions.get('length_m', 0)
    output.write("Размеры перголы:\n")
    output.write(f"Ширина: {width_m:.2f} м\n")
    output.write(f"Вынос: {length_m:.2f} м\n")
    output.write(f"Высота: {dimensions.get('height_m', 0):.2f} м\n")
    
    # Определяем количество модулей
    detailed_costs = results.get('detailed_costs', {})
    additional_columns_cost = detailed_costs.get('additional_columns', 0)
    
    # Определяем количество модулей по ширине или стоимости дополнительных колонн
    modules_count = 1
    if additional_columns_cost > 0:
        # Стоимость дополнительных колонн зависит от количества модулей
        # 1 модуль - 653€, 2 модуля - 980€, 3 модуля - 1306€
        if abs(additional_columns_cost - 653) < 1:
            modules_count = 1
        elif abs(additional_columns_cost - 980) < 1:
            modules_count = 2
        elif abs(additional_columns_cost - 1306) < 1:
            modules_count = 3
        else:
            # По умолчанию определяем количество модулей по ширине
            if width_m > 7:
                modules_count = 3
            elif width_m > 4:
                modules_count = 2
    else:
        # По умолчанию определяем количество модулей по ширине
        if width_m > 7:
            modules_count = 3
        elif width_m > 4:
            modules_count = 2
            
    output.write(f"Количество модулей: {modules_count}\n")
    output.write(f"Площадь перголы: {width_m * length_m:.2f} м²\n")
    
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