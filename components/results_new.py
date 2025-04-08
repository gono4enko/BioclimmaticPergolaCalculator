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
    Отображает результаты расчета стоимости перголы в новом дизайне
    с таблицами "Спецификация перголы" и "Стоимость" в соответствии с макетом
    
    Args:
        results (dict): Словарь с результатами расчета
    """
    # Проверяем наличие результатов
    if not results or 'error' in results:
        error_message = results.get('error', 'Произошла ошибка при расчете стоимости перголы')
        st.error(error_message)
        return
    
    # Получаем основные данные для отображения
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
    if width_m > 4.5:
        modules_count = 2
    if width_m > 9:
        modules_count = 3
    
    # Создаем таблицу спецификации в соответствии с новым дизайном
    # Получаем информацию о перголе
    pergola_type = "Не задан"
    lamella_type = "Не задан"
    lighting_type = "Без подсветки"
    
    if 'options' in st.session_state:
        pergola_options = st.session_state.options
        # Тип перголы
        pt = pergola_options.get('pergola_type', '')
        if pt == 'B500NEW':
            pergola_type = "B500 с поворотными ламелями"
        elif pt == 'B700NEW':
            pergola_type = "B700 с поворотно-сдвижными ламелями"
        elif pt == 'B600':
            pergola_type = "B600 PIR со стационарными сэндвич-панелями"
        
        # Тип ламелей
        lt = pergola_options.get('lamella_type', '')
        if 'B500-20NEW' in lt:
            lamella_type = "200×56 мм NEW (Усиленная)"
        elif 'B500-25NEW' in lt:
            lamella_type = "250×53 мм NEW (Стандартная)"
        elif 'B700-20NEW' in lt:
            lamella_type = "200×56 мм NEW (Усиленная)"
        elif 'B700-25NEW' in lt:
            lamella_type = "250×53 мм NEW (Стандартная)"
        elif 'B600' in lt:
            lamella_type = "PIR сэндвич-панели"
            
        # Освещение
        light = pergola_options.get('lighting_type', 'none')
        if light == 'led':
            lighting_type = "Сверхъяркая LED подсветка"
        elif light == 'rgb':
            lighting_type = "Светодиодная RGB подсветка"
        elif light == 'led_rgb':
            lighting_type = "Комбинированное LED + RGB освещение"
        else:
            lighting_type = "Без подсветки"
    
    # Узнаем автоматику и компоненты
    automation_info = "Базовая автоматика"
    remote_control_info = ""
    automation_manufacturer = ""
    automation_type = ""
    
    if "automation_type" in detailed_costs:
        automation_type = detailed_costs.get('automation_type', '')
        automation_manufacturer = detailed_costs.get('automation_manufacturer', '')
        remote_control = detailed_costs.get('remote_control', '')
        
        if automation_manufacturer == "Bansbach":
            automation_info = f"Базовая автоматика ({automation_manufacturer} {automation_type})"
            if remote_control:
                if remote_control == "Simu 1K":
                    remote_control_info = f"Пульт управления: {remote_control} (1-канальный)"
                elif remote_control == "Simu 5K":
                    remote_control_info = f"Пульт управления: {remote_control} (5-канальный)"
                elif remote_control == "Simu 15K":
                    remote_control_info = f"Пульт управления: {remote_control} (15-канальный)"
                else:
                    remote_control_info = f"Пульт управления: {remote_control}"
        elif automation_manufacturer == "Somfy":
            automation_info = f"Базовая автоматика ({automation_manufacturer} {automation_type})"
            if remote_control:
                if remote_control == "Simu 1K":
                    remote_control_info = f"Пульт управления: {remote_control} (1-канальный)"
                elif remote_control == "Simu 5K":
                    remote_control_info = f"Пульт управления: {remote_control} (5-канальный)"
                elif remote_control == "Simu 15K":
                    remote_control_info = f"Пульт управления: {remote_control} (15-канальный)"
                else:
                    remote_control_info = f"Пульт управления: {remote_control}"
    
    # Получаем стоимость в евро (без конвертации)
    base_price_eur = detailed_costs.get('base_price', 0)
    automation_cost_eur = detailed_costs.get('additional_options', {}).get('automation', 0)
    remote_control_cost_eur = detailed_costs.get('remote_control_cost', 0)
    
    # Добавляем стоимость пульта к стоимости автоматики
    automation_with_remote_cost_eur = automation_cost_eur + remote_control_cost_eur
    
    # Рассчитываем стоимость доставки (10% от суммы всех элементов перголы)
    # Получаем данные о дополнительных колоннах и усилителе лотка
    additional_columns_cost = detailed_costs.get('additional_columns', 0)
    gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
    lighting_cost = detailed_costs.get('lighting', 0)
    
    # Формируем подробную информацию о подсветке для отображения в спецификации
    lighting_details_html = ""
    if lighting_type != "Без подсветки" and 'lighting_details' in detailed_costs:
        light_details = detailed_costs.get('lighting_details', {})
        led_length = light_details.get('led_length', 0)
        controllers_count = light_details.get('controllers_count', 0)
        
        # Формируем HTML списка для подсветки без лишних отступов 
        # Используем экранированный HTML-код, чтобы избежать проблем с отображением
        led_length_str = f"{led_length:.2f}"
        controllers_str = str(controllers_count)
        lighting_details_html = f'Светодиодная лента, {led_length_str} м. Блок управления Somfy RTS Dimmer, {controllers_str} шт.'
    
    # Считаем сумму всех элементов перголы без установки
    total_pergola_elements = base_price_eur + automation_with_remote_cost_eur + additional_columns_cost + gutter_insert_cost + lighting_cost
    
    # 10% от суммы всех элементов
    delivery_cost_eur = round(total_pergola_elements * 0.1)
    
    # Общая стоимость в евро
    total_cost_eur = results['total_cost']
    
    # Добавляем стили для нового дизайна таблиц
    st.markdown("""
    <style>
    /* Подключение шрифта SF Pro Text */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Text:wght@400;500;600;700&display=swap');
    
    /* Применение шрифта ко всем элементам */
    * {
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 400;
    }
    
    /* Основные стили */
    .result-heading {
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 15px 0;
        text-align: center;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Стили для таблиц спецификации и стоимости */
    .spec-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
        background-color: #f9f9f9;
        border-radius: 8px;
        overflow: hidden;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .spec-table th {
        padding: 12px 15px;
        background-color: #4a75e2;
        color: white;
        text-align: left;
        font-weight: bold;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .spec-table td {
        padding: 5px 15px;
        border-bottom: 1px solid #eee;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .spec-table tr:nth-child(even) {
        background-color: #f0f0f0;
    }
    
    .spec-table tr:last-child td {
        border-bottom: none;
    }
    
    /* Стили для цен */
    .price-value {
        text-align: right;
        font-weight: bold;
    }
    
    /* Стили для итоговой суммы */
    .total-row {
        font-size: 22px;
        font-weight: bold;
        color: #333;
        margin-top: 20px;
        margin-bottom: 30px;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .total-amount {
        color: #1b6b1b;
    }
    
    /* Стили для кнопки */
    .calc-button {
        display: inline-block;
        background-color: #1E4B96;
        color: white;
        padding: 12px 25px;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        margin-bottom: 20px;
        text-decoration: none;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Переопределение стилей Streamlit для использования SF Pro Text */
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, 
    .st-am, .st-an, .st-ao, .st-ap, .st-aq, .st-ar, .st-as, .st-at, 
    h1, h2, h3, h4, h5, h6, p, div, span, button, input, select, textarea {
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 400;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Отображаем заголовок результатов по центру
    st.markdown('<div style="text-align: center;"><h3 class="result-heading">Результаты расчета</h3></div>', unsafe_allow_html=True)
    
    # Создаем две колонки для таблиц
    col1, col2 = st.columns(2)
    
    with col1:
        # Таблица "Спецификация перголы"
        st.markdown("""
        <div style="background-color: #4a75e2; color: white; padding: 10px 15px; border-radius: 5px 5px 0 0; font-weight: bold;">
            Спецификация перголы
        </div>
        """, unsafe_allow_html=True)
        
        # Содержимое таблицы
        st.markdown(f"""
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; width: 30%; color: #000000;">Тип перголы:</td>
                <td style="padding: 6px 10px; color: #000000;">{pergola_type}</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Тип ламелей:</td>
                <td style="padding: 6px 10px; color: #000000;">{lamella_type}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Ширина:</td>
                <td style="padding: 6px 10px; color: #000000;">{width_m} м</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Вынос:</td>
                <td style="padding: 6px 10px; color: #000000;">{length_m} м</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Количество ламелей:</td>
                <td style="padding: 6px 10px; color: #000000;">{results.get('lamella_count', '-')} шт</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Площадь:</td>
                <td style="padding: 6px 10px; color: #000000;">{area} м²</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Количество модулей:</td>
                <td style="padding: 6px 10px; color: #000000;">{modules_count} модуль</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Компоненты автоматики:</td>
                <td style="padding: 6px 10px; color: #000000;">
                    <ul style="margin: 0; padding-left: 20px; color: #000000;">
                        <li>Привод {automation_manufacturer} {automation_type} ({modules_count} {'комплект' if modules_count == 1 else 'комплекта' if 2 <= modules_count <= 4 else 'комплектов'})</li>
                        <li>{remote_control_info}</li>
                    </ul>
                </td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Подсветка:</td>
                <td style="padding: 6px 10px; color: #000000;">
                    {lighting_type}
                    <p style="margin: 0; padding: 0; color: #000000;">{lighting_details_html.replace('<code>', '').replace('</code>', '')}</p>
                </td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
    
    with col2:
        # Таблица "Стоимость"
        st.markdown("""
        <div style="background-color: #4a75e2; color: white; padding: 10px 15px; border-radius: 5px 5px 0 0; font-weight: bold;">
            Стоимость
        </div>
        """, unsafe_allow_html=True)
        
        # Содержимое таблицы
        # Получаем данные о дополнительных колоннах и усилителе лотка
        additional_columns_cost = detailed_costs.get('additional_columns', 0)
        gutter_insert_cost = detailed_costs.get('gutter_insert', 0)
        
        # Создаем HTML-разметку для таблицы стоимости в том же стиле, что и таблица спецификации
        price_table_html = """
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; width: 70%; color: #000000;">Базовая стоимость конструкции:</td>
                <td style="padding: 6px 10px; text-align: right; color: #000000;">""" + str(int(base_price_eur)) + """ €</td>
            </tr>
        """
        
        # Добавляем строку с дополнительными колоннами, если они есть
        row_count = 1  # Счетчик строк для чередования цвета фона
        
        if additional_columns_cost > 0:
            row_count += 1
            price_table_html += """
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Стоимость дополнительных колонн:</td>
                <td style="padding: 6px 10px; text-align: right; color: #000000;">""" + str(int(additional_columns_cost)) + """ €</td>
            </tr>
            """
        
        # Добавляем строку с усилителем лотка, если он есть
        if gutter_insert_cost > 0:
            row_count += 1
            bg_color = "#f9f9f9" if row_count % 2 == 1 else "#f0f0f0"
            price_table_html += """
            <tr style="background-color: """ + bg_color + """;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Стоимость усилителя лотка:</td>
                <td style="padding: 6px 10px; text-align: right; color: #000000;">""" + str(int(gutter_insert_cost)) + """ €</td>
            </tr>
            """
        
        # Добавляем строку со стоимостью автоматики
        row_count += 1
        bg_color = "#f9f9f9" if row_count % 2 == 1 else "#f0f0f0"
        price_table_html += """
        <tr style="background-color: """ + bg_color + """;">
            <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Стоимость автоматики:</td>
            <td style="padding: 6px 10px; text-align: right; color: #000000;">""" + str(int(automation_with_remote_cost_eur)) + """ €</td>
        </tr>
        """
        
        # Добавляем строку со стоимостью подсветки, если она установлена
        if lighting_cost > 0:
            row_count += 1
            bg_color = "#f9f9f9" if row_count % 2 == 1 else "#f0f0f0"
            price_table_html += """
            <tr style="background-color: """ + bg_color + """;">
                <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Стоимость подсветки:</td>
                <td style="padding: 6px 10px; text-align: right; color: #000000;">""" + str(int(lighting_cost)) + """ €</td>
            </tr>
            """
        
        # Добавляем строку с доставкой
        row_count += 1
        bg_color = "#f9f9f9" if row_count % 2 == 1 else "#f0f0f0"
        delivery_cost = 0  # Установлено в ноль согласно требованию
        price_table_html += """
        <tr style="background-color: """ + bg_color + """;">
            <td style="padding: 6px 10px; font-weight: bold; color: #000000;">Доставка:</td>
            <td style="padding: 6px 10px; text-align: right; color: #000000;">""" + str(int(delivery_cost)) + """ €</td>
        </tr>
        """
        
        # Добавляем строку ИТОГО
        row_count += 1
        bg_color = "#f9f9f9" if row_count % 2 == 1 else "#f0f0f0"
        price_table_html += """
        <tr style="background-color: """ + bg_color + """;">
            <td style="padding: 6px 10px; font-weight: bold; font-size: 18px; color: #000000;">ИТОГО:</td>
            <td style="padding: 6px 10px; text-align: right; font-weight: bold; font-size: 18px; color: #1b6b1b;">""" + str(int(total_cost_eur)) + """ €</td>
        </tr>
        </table>
        """
        
        # Отображаем созданную таблицу с обертыванием в контейнер для безопасности
        with st.container():
            # Используем компонент с CSS классом для отображения HTML
            st.components.v1.html(f"""
                <div class="price-table-container">
                    {price_table_html}
                </div>
                <style>
                    .price-table-container table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    .price-table-container table tr td {{
                        padding: 6px 10px;
                    }}
                </style>
            """, height=250)  # Задаем фиксированную высоту для компонента
        
        # Убрана кнопка "Изменить параметры"
    
    # Убрана общая стоимость внизу страницы и кнопка "Скачать спецификацию"
    
    # Добавляем скрытый элемент для скролла к результатам
    st.markdown("""
    <div id="results-anchor" style="height: 1px; width: 1px; position: absolute;"></div>
    """, unsafe_allow_html=True)
    
    # Логируем просмотр результатов
    log_user_action("Просмотр результатов расчета", {"total_cost": results['total_cost']})


def generate_csv(results):
    """
    Генерирует CSV-файл с результатами расчета
    
    Args:
        results (dict): Словарь с результатами расчета
        
    Returns:
        str: Содержимое CSV-файла
    """
    dimensions = results.get('dimensions', {})
    width_m = dimensions.get('width_m', 0)
    length_m = dimensions.get('length_m', 0)
    height_m = dimensions.get('height_m', 0)
    area = round(width_m * length_m, 2)
    
    detailed_costs = results.get('detailed_costs', {})
    correction_message = results.get('correction_message', '')
    
    # Определяем тип перголы и автоматики
    pergola_type = ""
    lamella_type = ""
    modules_count = 1
    if width_m > 4.5:
        modules_count = 2
    if width_m > 9:
        modules_count = 3
    
    if 'options' in st.session_state:
        pergola_options = st.session_state.options
        pt = pergola_options.get('pergola_type', '')
        if pt == 'B500NEW':
            pergola_type = "Пергола с поворотными ламелями (B500)"
        elif pt == 'B700NEW':
            pergola_type = "Пергола со сдвижными ламелями (B700)"
        elif pt == 'B600':
            pergola_type = "Стационарная пергола с PIR-панелями (B600)"
            
        lt = pergola_options.get('lamella_type', '')
        if '20' in lt:
            lamella_type = "200 × 56 мм"
        elif '25' in lt and 'B500' in lt:
            lamella_type = "250 × 53 мм"
        elif '25' in lt and 'B700' in lt:
            lamella_type = "250 × 53 мм" 
        elif 'B600' in lt:
            lamella_type = "PIR панели"
    
    # Создаем DataFrame для CSV
    data = {
        'Параметр': [
            'Тип перголы',
            'Тип ламелей',
            'Размеры (Ш × В × Д)',
            'Площадь',
            'Количество модулей',
            'Дополнительная информация',
            'Базовая стоимость',
            'Дополнительные колонны',
            'Усилитель лотка',
            'Автоматика',
            'Пульт ДУ',
            'Подсветка',
            'Доставка',
            'Итоговая стоимость'
        ],
        'Значение': [
            pergola_type,
            lamella_type,
            f"{width_m} × {height_m} × {length_m} м",
            f"{area} м²",
            modules_count,
            correction_message,
            f"{detailed_costs.get('base_price', 0)} €",
            f"{detailed_costs.get('additional_columns', 0)} €",
            f"{detailed_costs.get('gutter_insert', 0)} €",
            f"{detailed_costs.get('additional_options', {}).get('automation', 0)} €",
            f"{detailed_costs.get('remote_control_cost', 0)} €",
            f"{detailed_costs.get('lighting', 0)} €",
            f"{0} €", # Доставка пока установлена на 0
            f"{results.get('total_cost', 0)} €"
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Преобразуем в CSV и кодируем в base64
    csv_string = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    b64 = base64.b64encode(csv_string.encode('utf-8-sig')).decode()
    
    return b64