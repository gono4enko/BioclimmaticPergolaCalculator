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
    
    # Получаем сообщение об автоматике для отладки
    automation_message = detailed_costs.get('automation_message', '')
    print(f"DEBUG - automation_message: {automation_message}")
    
    # Определяем количество модулей по ширине
    # Если есть дополнительные колонны, значит уже рассчитано нужное количество модулей
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
            modules_count = 1
            if width_m > 7:
                modules_count = 3
            elif width_m > 4:
                modules_count = 2
    else:
        # По умолчанию определяем количество модулей по ширине
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
        automation_message = detailed_costs.get('automation_message', '')
        
        # Создаем новый список компонентов автоматики только с приводами
        # Используем количество модулей для определения количества приводов
        if automation_manufacturer == "Bansbach":
            if automation_type == "T1":
                # Привод Bansbach T1
                drive_info = f"Привод Bansbach T1 ({modules_count} {'привод' if modules_count == 1 else 'привода' if 2 <= modules_count <= 4 else 'приводов'})"
                automation_components.append(drive_info)
            else:
                # Привод Bansbach Tandem
                drive_info = f"Привод Bansbach Tandem ({modules_count} {'комплект' if modules_count == 1 else 'комплекта' if 2 <= modules_count <= 4 else 'комплектов'})"
                automation_components.append(drive_info)
        elif automation_manufacturer == "Somfy":
            if automation_type == "M1":
                # Привод Somfy M1
                drive_info = f"Привод Somfy M1 ({modules_count} {'привод' if modules_count == 1 else 'привода' if 2 <= modules_count <= 4 else 'приводов'})"
                automation_components.append(drive_info)
            else:
                # Привод Somfy M2 TANDEM
                drive_info = f"Привод Somfy M2 TANDEM ({modules_count} {'комплект' if modules_count == 1 else 'комплекта' if 2 <= modules_count <= 4 else 'комплектов'})"
                automation_components.append(drive_info)
    
    # Тип освещения с детальной информацией
    lighting_info = "Без подсветки"
    if lighting_type != 'none':
        lighting_name = LIGHTING_TYPES.get(lighting_type, {}).get('name', 'Освещение')
        
        # Получаем детальную информацию о подсветке, если она есть
        lighting_details = detailed_costs.get('lighting_details', {})
        
        # Создаем HTML для компонентов подсветки
        lighting_components = []
        
        # Добавляем информацию о светодиодной ленте
        if 'led_length' in lighting_details:
            led_length = lighting_details.get('led_length', 0)
            if led_length > 0:
                lighting_components.append(f"Светодиодная лента {lighting_name} ({led_length:.1f} м)")
        
        # Добавляем информацию о блоках управления
        if 'controllers_count' in lighting_details:
            controllers_count = lighting_details.get('controllers_count', 0)
            if controllers_count > 0:
                controller_text = f"Блок управления Somfy RTS Dimmer ({controllers_count} {'шт.' if controllers_count == 1 else 'шт.'})"
                lighting_components.append(controller_text)
        
        # Если есть компоненты освещения, формируем HTML
        if lighting_components:
            components_html = "<div class='spec-components'>"
            for component in lighting_components:
                components_html += f"<div class='spec-component-item'>• {component}</div>"
            components_html += "</div>"
            lighting_info = components_html
        else:
            lighting_info = f"{lighting_name}"
    
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
    
    # Создаем современную карточку для спецификации перголы
    with st.container():
        # Стили для современной карточки спецификации
        st.markdown("""
        <style>
        .spec-card {
            background-color: white;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }
        .spec-header {
            background-color: #4a69bd;
            color: white;
            padding: 1rem;
            font-size: 1.3rem;
            font-weight: bold;
            text-align: center;
        }
        .spec-content {
            padding: 0;
        }
        .spec-row {
            display: flex;
            border-bottom: 1px solid #eee;
            padding: 0.8rem 1.2rem;
        }
        .spec-row:last-child {
            border-bottom: none;
        }
        .spec-row:nth-child(odd) {
            background-color: #f8f9fa;
        }
        .spec-label {
            flex: 0 0 40%;
            font-weight: 600;
            color: #444;
        }
        .spec-value {
            flex: 0 0 60%;
            color: #333;
        }
        .spec-components {
            margin-top: 0.5rem;
        }
        .spec-component-item {
            margin-bottom: 0.3rem;
            font-size: 0.95rem;
        }
        .spec-total {
            background-color: #e6f2ff;
            font-weight: bold;
        }
        </style>
        
        <div class="spec-card">
            <div class="spec-header">Спецификация перголы</div>
            <div class="spec-content">
        """, unsafe_allow_html=True)
        
        # Подготовка данных для спецификации
        rows = []
        
        # Добавляем основные параметры перголы
        rows.append(("Тип перголы:", pergola_name))
        rows.append(("Тип ламелей:", lamella_info))
        rows.append(("Ширина:", f"{width_m:.2f} м"))
        rows.append(("Вынос:", f"{length_m:.2f} м"))
        rows.append(("Площадь:", f"{area:.2f} м²"))
        rows.append(("Количество модулей:", f"{modules_count} {'модуль' if modules_count == 1 else 'модуля' if modules_count < 5 else 'модулей'}"))
        rows.append(("Фактический размер:", f"{width_m:.2f} × {length_m:.2f} м"))
        
        # Добавляем информацию об автоматике
        if automation_manufacturer:
            automation_name = "Базовая автоматика"
            rows.append(("Автоматика:", automation_name))
            
            # Используем непосредственно automation_components, которые уже были сформированы
            if automation_components:
                modified_components = list(automation_components)
                
                # Добавляем пульт управления
                if 'remote_control' in detailed_costs:
                    remote_control = detailed_costs['remote_control']
                    modified_components.append(f"Пульт ДУ {remote_control}")
                
                # Формируем HTML для компонентов
                components_html = "<div class='spec-components'>"
                for component in modified_components:
                    components_html += f"<div class='spec-component-item'>• {component}</div>"
                components_html += "</div>"
                
                rows.append(("Компоненты автоматики:", components_html))
        
        # Добавляем информацию об освещении
        rows.append(("Подсветка:", lighting_info))
        
        # Если есть дополнительные колонны, добавляем их (без стоимости)
        additional_columns_cost = detailed_costs.get('additional_columns', 0)
        if additional_columns_cost > 0:
            rows.append(("Дополнительные колонны:", "Требуются дополнительные колонны для усиления конструкции"))
        
        # Если есть вставка для усиления лотка, добавляем её (без стоимости)
        gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
        if gutter_insert_cost > 0:
            rows.append(("Усиление лотка:", "Вставка для усиления лотка"))
        
        # Добавляем итоговую стоимость
        rows.append(("Итоговая стоимость:", f"{results.get('total_cost', 0)}€"))
        
        # Выводим строки спецификации
        for i, (label, value) in enumerate(rows):
            extra_class = " spec-total" if label == "Итоговая стоимость:" else ""
            st.markdown(f"""
            <div class="spec-row{extra_class}">
                <div class="spec-label">{label}</div>
                <div class="spec-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Закрываем контейнер спецификации
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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