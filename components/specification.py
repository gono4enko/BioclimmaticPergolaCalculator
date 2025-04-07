"""
Компонент для отображения спецификации перголы
"""
import streamlit as st
from config.pergola_types import PERGOLA_TYPES, LAMELLA_TYPES, LIGHTING_TYPES

def render_specification(results, options):
    """
    Отображает спецификацию перголы в виде таблицы
    
    Args:
        results (dict): Словарь с результатами расчета
        options (dict): Словарь с выбранными опциями
    """
    st.subheader("Спецификация перголы")
    
    # Проверяем наличие результатов
    if not results or 'error' in results:
        st.error("Нет данных для отображения спецификации")
        return
    
    # Создаем таблицу спецификации
    pergola_type = options.get('pergola_type', '')
    lamella_type = options.get('lamella_type', '')
    lighting_type = options.get('lighting_type', 'none')
    
    # Получаем размеры
    dimensions = results.get('dimensions', {})
    width_m = dimensions.get('width_m', 0)
    length_m = dimensions.get('length_m', 0)
    height_m = dimensions.get('height_m', 0)
    area = round(width_m * length_m, 2)
    
    # Определяем количество модулей
    detailed_costs = results.get('detailed_costs', {})
    additional_columns_cost = detailed_costs.get('additional_columns', 0)
    
    # Определяем количество модулей по ширине
    modules_count = 1
    if width_m > 7:
        modules_count = 3
    elif width_m > 4:
        modules_count = 2
    
    # Определяем тип и стоимость автоматики
    automation_cost = 0
    automation_type = ""
    automation_components = []
    
    # Проверяем, включена ли автоматика
    if "automation_type" in detailed_costs:
        automation_type = detailed_costs.get('automation_type', '')
        automation_manufacturer = detailed_costs.get('automation_manufacturer', '')
        
        if "automation" in detailed_costs.get('additional_options', {}):
            automation_cost = detailed_costs['additional_options']['automation']
        
        # Добавляем компоненты автоматики
        if automation_manufacturer == "Bansbach":
            if automation_type == "T1":
                automation_components.append("Bansbach T1, Germany (700€)")
            else:
                automation_components.append("Bansbach Tandem, Germany (1400€)")
            automation_components.append("Пульт управления: Simu 1K (25€)")
        elif automation_manufacturer == "Somfy":
            if automation_type == "M1":
                automation_components.append("Somfy M1, France (300€)")
            else:
                automation_components.append("Somfy M2 TANDEM, France (1000€)")
            automation_components.append("Пульт управления: Somfy RTS (25€)")
    
    # Тип освещения и его стоимость
    lighting_info = "Без подсветки"
    if lighting_type != 'none':
        lighting_details = detailed_costs.get('lighting_details', {})
        lighting_name = LIGHTING_TYPES.get(lighting_type, {}).get('name', 'Освещение')
        led_length = lighting_details.get('led_length', 0)
        controllers_count = lighting_details.get('controllers_count', 0)
        lighting_cost = detailed_costs.get('lighting', 0)
        
        lighting_info = f"{lighting_name} ({lighting_cost}€)"
    
    # Получаем информацию о типе ламелей
    lamella_info = ""
    if lamella_type in LAMELLA_TYPES:
        lamella_width = LAMELLA_TYPES[lamella_type].get('width', 0)
        lamella_height = LAMELLA_TYPES[lamella_type].get('height', 0)
        lamella_info = f"{lamella_width} × {lamella_height} мм"
    
    # Информация о перголе
    pergola_info = ""
    if pergola_type in PERGOLA_TYPES:
        pergola_info = PERGOLA_TYPES[pergola_type].get('name', '')
    
    # Создаем CSS стили для таблицы
    st.markdown("""
    <style>
    .specification-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .specification-table th {
        background-color: #4c6ef5;
        color: white;
        font-weight: bold;
        text-align: left;
        padding: 10px;
    }
    .specification-table td {
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    .specification-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .specification-table tr:nth-child(odd) {
        background-color: #ffffff;
    }
    .specification-table ul {
        margin: 0;
        padding-left: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем HTML для таблицы спецификации
    html_table = f"""
    <table class="specification-table">
        <tr>
            <th colspan="2">Спецификация перголы</th>
        </tr>
        <tr>
            <td>Тип перголы:</td>
            <td>{pergola_info}</td>
        </tr>
        <tr>
            <td>Тип ламелей:</td>
            <td>{lamella_info}</td>
        </tr>
        <tr>
            <td>Ширина:</td>
            <td>{width_m} м</td>
        </tr>
        <tr>
            <td>Вынос:</td>
            <td>{length_m} м</td>
        </tr>
        <tr>
            <td>Площадь:</td>
            <td>{area} м²</td>
        </tr>
        <tr>
            <td>Количество модулей:</td>
            <td>{modules_count} {'модуль' if modules_count == 1 else 'модуля' if modules_count < 5 else 'модулей'}</td>
        </tr>
        <tr>
            <td>Фактический размер:</td>
            <td>{width_m} × {length_m} м</td>
        </tr>
    """
    
    # Добавляем информацию об автоматике, если она есть
    if automation_type:
        automation_name = "Базовая автоматика"
        if automation_cost > 0:
            automation_name += f" ({automation_cost}€)"
        
        html_table += f"""
        <tr>
            <td>Автоматика:</td>
            <td>{automation_name}</td>
        </tr>
        """
        
        # Добавляем компоненты автоматики
        if automation_components:
            html_table += """
            <tr>
                <td>Компоненты автоматики:</td>
                <td>
                    <ul>
            """
            
            for component in automation_components:
                html_table += f"<li>{component}</li>"
            
            html_table += """
                    </ul>
                </td>
            </tr>
            """
    
    # Добавляем информацию об освещении
    html_table += f"""
        <tr>
            <td>Подсветка:</td>
            <td>{lighting_info}</td>
        </tr>
    """
    
    # Если есть вставка для усиления лотка, добавляем её
    gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
    if gutter_insert_cost > 0:
        html_table += f"""
        <tr>
            <td>Усиление лотка:</td>
            <td>Вставка для усиления ({gutter_insert_cost}€)</td>
        </tr>
        """
    
    # Добавляем итоговую стоимость
    html_table += f"""
        <tr>
            <td><strong>Итоговая стоимость:</strong></td>
            <td><strong>{results.get('total_cost', 0)}€</strong></td>
        </tr>
    </table>
    """
    
    # Отображаем таблицу
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Добавляем заметки или примечания
    if 'correction_message' in results and results['correction_message']:
        st.info(results['correction_message'])