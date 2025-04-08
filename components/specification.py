"""
Компонент для отображения спецификации перголы
"""
import streamlit as st
from config.pergola_types import PERGOLA_TYPES, LAMELLA_TYPES, LIGHTING_TYPES
import os

def render_specification(results, options):
    """
    Отображает спецификацию перголы в виде таблицы
    
    Args:
        results (dict): Словарь с результатами расчета
        options (dict): Словарь с выбранными опциями
    """
    # Проверяем наличие результатов
    if not results or 'error' in results:
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
    automation_manufacturer = ""
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
                automation_components.append(f"Bansbach T1, Germany ({automation_cost}€)")
            else:
                automation_components.append(f"Bansbach Tandem, Germany ({automation_cost}€)")
            automation_components.append("Пульт управления: Simu 1K (25€)")
        elif automation_manufacturer == "Somfy":
            if automation_type == "M1":
                automation_components.append(f"Somfy M1, France ({automation_cost}€)")
            else:
                automation_components.append(f"Somfy M2 TANDEM, France ({automation_cost}€)")
            automation_components.append("Пульт управления: Somfy RTS (25€)")
    
    # Тип освещения и его стоимость
    lighting_info = "Без подсветки"
    if lighting_type != 'none':
        lighting_cost = detailed_costs.get('lighting', 0)
        lighting_name = LIGHTING_TYPES.get(lighting_type, {}).get('name', 'Освещение')
        lighting_info = f"{lighting_name} ({lighting_cost}€)"
    
    # Получаем информацию о типе ламелей
    lamella_info = ""
    if lamella_type in LAMELLA_TYPES:
        lamella_width = LAMELLA_TYPES[lamella_type].get('width', 0)
        lamella_thickness = LAMELLA_TYPES[lamella_type].get('thickness', 0)
        if lamella_width > 0 and lamella_thickness > 0:
            lamella_info = f"{lamella_width} × {lamella_thickness} мм"
        else:
            lamella_info = LAMELLA_TYPES[lamella_type].get('name', '')
    
    # Информация о перголе
    pergola_name = ""
    if pergola_type == "B500NEW":
        pergola_name = "Биоклиматическая пергола с поворотными ламелями (B500)"
    elif pergola_type == "B700NEW":
        pergola_name = "Биоклиматическая пергола с поворотно-сдвижными ламелями (B700)"
    elif pergola_type == "B600":
        pergola_name = "Пергола со стационарной крышей из PIR панелей (B600)"
    else:
        pergola_name = PERGOLA_TYPES.get(pergola_type, {}).get('name', '')
    
    # Создаем CSS стили для таблицы спецификации
    st.markdown("""
    <style>
    .specification-container {
        margin-top: 2rem;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .specification-header {
        background-color: #4a69bd;
        color: white;
        padding: 1rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .specification-table {
        width: 100%;
        border-collapse: collapse;
    }
    .specification-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .specification-table tr:nth-child(odd) {
        background-color: #ffffff;
    }
    .specification-table td {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid #e9ecef;
    }
    .specification-table td:first-child {
        width: 40%;
        font-weight: 500;
    }
    .automation-components {
        list-style-type: disc;
        margin: 0.5rem 0 0.5rem 1.5rem;
        padding: 0;
    }
    .automation-components li {
        margin-bottom: 0.3rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем HTML для спецификации
    specification_html = f"""
    <div class="specification-container">
        <div class="specification-header">
            Спецификация перголы
        </div>
        <table class="specification-table">
            <tr>
                <td>Тип перголы:</td>
                <td>{pergola_name}</td>
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
    
    # Добавляем информацию об автоматике
    if automation_manufacturer:
        automation_name = f"Базовая автоматика ({automation_cost}€)"
        
        specification_html += f"""
            <tr>
                <td>Автоматика:</td>
                <td>{automation_name}</td>
            </tr>
        """
        
        # Добавляем компоненты автоматики
        if automation_components:
            components_list = ""
            for component in automation_components:
                components_list += f"<li>{component}</li>"
                
            specification_html += f"""
            <tr>
                <td>Компоненты автоматики:</td>
                <td>
                    <ul class="automation-components">
                        {components_list}
                    </ul>
                </td>
            </tr>
            """
    
    # Добавляем информацию об освещении
    specification_html += f"""
            <tr>
                <td>Подсветка:</td>
                <td>{lighting_info}</td>
            </tr>
    """
    
    # Если есть вставка для усиления лотка, добавляем её
    gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
    if gutter_insert_cost > 0:
        specification_html += f"""
            <tr>
                <td>Усиление лотка:</td>
                <td>Вставка для усиления лотка ({gutter_insert_cost}€)</td>
            </tr>
        """
    
    # Добавляем итоговую стоимость
    specification_html += f"""
            <tr>
                <td><strong>Итоговая стоимость:</strong></td>
                <td><strong>{results.get('total_cost', 0)}€</strong></td>
            </tr>
        </table>
    </div>
    """
    
    # Отображаем спецификацию
    st.markdown(specification_html, unsafe_allow_html=True)
    
    # Добавляем изображение выбранной модели перголы
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Определяем, какое изображение показать
        image_path = None
        if pergola_type == "B500NEW":
            if os.path.exists("attached_assets/В500 со вращением ламелей.png"):
                image_path = "attached_assets/В500 со вращением ламелей.png"
        elif pergola_type == "B700NEW":
            if os.path.exists("attached_assets/В700 со сдвижением ламелей.png"):
                image_path = "attached_assets/В700 со сдвижением ламелей.png"
        elif pergola_type == "B600":
            if os.path.exists("attached_assets/В600 с сэндвич панелями.png"):
                image_path = "attached_assets/В600 с сэндвич панелями.png"
        
        if image_path:
            st.image(image_path, width=250)
    
    with col2:
        # Отображаем описание модели
        if pergola_type in PERGOLA_TYPES:
            st.subheader(PERGOLA_TYPES[pergola_type].get('name', ''))
            st.write(PERGOLA_TYPES[pergola_type].get('description', ''))
    
    # Добавляем заметки или примечания
    if 'correction_message' in results and results['correction_message']:
        st.info(results['correction_message'])