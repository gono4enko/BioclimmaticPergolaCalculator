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
    pergola_type = ""
    lamella_type = ""
    lighting_type = "Без подсветки"
    
    if 'options' in st.session_state:
        pergola_options = st.session_state.options
        # Тип перголы
        pt = pergola_options.get('pergola_type', '')
        if pt == 'B500NEW':
            pergola_type = "Биоклиматическая пергола с поворотными ламелями (B500)"
        elif pt == 'B700NEW':
            pergola_type = "Биоклиматическая пергола со сдвижными ламелями (B700)"
        elif pt == 'B600':
            pergola_type = "Стационарная пергола с PIR-панелями (B600)"
            
        # Тип ламелей
        lt = pergola_options.get('lamella_type', '')
        if '20' in lt:
            lamella_type = "200 × 56 мм"
        elif '25' in lt and 'B500' in lt:
            lamella_type = "250 × 53 мм"
        elif '25' in lt and 'B700' in lt:
            lamella_type = "250 × 53 мм" 
        elif 'B600' in lt:
            lamella_type = "PIR панели"
            
        # Освещение
        light = pergola_options.get('lighting_type', 'none')
        if light == 'led':
            lighting_type = "LED-подсветка"
        elif light == 'rgb':
            lighting_type = "RGB-подсветка"
        elif light == 'none':
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
                    remote_control_info = f"Пульт управления: {remote_control} (1-канальный, 25€)"
                elif remote_control == "Simu 5K":
                    remote_control_info = f"Пульт управления: {remote_control} (5-канальный, 40€)"
                elif remote_control == "Simu 15K":
                    remote_control_info = f"Пульт управления: {remote_control} (15-канальный, 90€)"
                else:
                    remote_control_info = f"Пульт управления: {remote_control}"
        elif automation_manufacturer == "Somfy":
            automation_info = f"Базовая автоматика ({automation_manufacturer} {automation_type})"
            if remote_control:
                if remote_control == "Simu 1K":
                    remote_control_info = f"Пульт управления: {remote_control} (1-канальный, 25€)"
                elif remote_control == "Simu 5K":
                    remote_control_info = f"Пульт управления: {remote_control} (5-канальный, 40€)"
                elif remote_control == "Simu 15K":
                    remote_control_info = f"Пульт управления: {remote_control} (15-канальный, 90€)"
                else:
                    remote_control_info = f"Пульт управления: {remote_control}"
    
    # Получаем стоимость в евро (без конвертации)
    base_price_eur = detailed_costs.get('base_price', 0)
    automation_cost_eur = detailed_costs.get('additional_options', {}).get('automation', 0)
    remote_control_cost_eur = detailed_costs.get('remote_control_cost', 0)
    
    # Добавляем стоимость пульта к стоимости автоматики
    automation_with_remote_cost_eur = automation_cost_eur + remote_control_cost_eur
    
    # Рассчитываем стоимость изготовления (10%)
    manufacturing_cost_eur = round(base_price_eur * 0.1)
    
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
    
    # Отображаем заголовок результатов
    st.markdown('<h3 class="result-heading">Результаты расчета</h3>', unsafe_allow_html=True)
    
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
                <td style="padding: 6px 10px; font-weight: bold; width: 30%;">Тип перголы:</td>
                <td style="padding: 6px 10px;">{pergola_type}</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold;">Тип ламелей:</td>
                <td style="padding: 6px 10px;">{lamella_type}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold;">Ширина:</td>
                <td style="padding: 6px 10px;">{width_m} м</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold;">Вынос:</td>
                <td style="padding: 6px 10px;">{length_m} м</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold;">Площадь:</td>
                <td style="padding: 6px 10px;">{area} м²</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold;">Количество модулей:</td>
                <td style="padding: 6px 10px;">{modules_count} модуль</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold;">Фактический размер:</td>
                <td style="padding: 6px 10px;">{width_m} × {length_m} м</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold;">Автоматика:</td>
                <td style="padding: 6px 10px;">{automation_info}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold;">Компоненты автоматики:</td>
                <td style="padding: 6px 10px;">
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Модуль 1: {automation_manufacturer} {automation_type}, Germany ({automation_cost_eur//modules_count} €)</li>
                        <li>{remote_control_info}</li>
                    </ul>
                </td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold;">Подсветка:</td>
                <td style="padding: 6px 10px;">{lighting_type}</td>
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
        st.markdown(f"""
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold; width: 70%;">Базовая стоимость конструкции:</td>
                <td style="padding: 6px 10px; text-align: right; font-weight: bold;">{base_price_eur:,} €</td>
            </tr>
            <tr style="background-color: #f0f0f0;">
                <td style="padding: 6px 10px; font-weight: bold;">Стоимость автоматики:</td>
                <td style="padding: 6px 10px; text-align: right; font-weight: bold;">{automation_with_remote_cost_eur:,} €</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 6px 10px; font-weight: bold;">Изготовление и подготовка (10%):</td>
                <td style="padding: 6px 10px; text-align: right; font-weight: bold;">{manufacturing_cost_eur:,} €</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        # Кнопка "Изменить параметры" с улучшенным скроллом и обработкой ошибок
        st.markdown(f"""
        <div style="margin-top: 20px;">
            <button 
                onclick="try {{ 
                    window.scrollTo({{ top: 0, behavior: 'smooth' }}); 
                    console.log('Scrolled to top smoothly'); 
                }} catch (e) {{ 
                    window.scrollTo(0, 0); 
                    console.log('Used fallback scroll method: ' + e); 
                }}"
                style="width: 100%; padding: 12px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">
                Изменить параметры
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # Итоговая стоимость (на всю ширину)
    st.markdown(f"""
    <div style="margin-top: 20px; text-align: right; font-size: 24px; font-weight: bold;">
        Итого: <span style="color: #1b6b1b;">{total_cost_eur:,} €</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Записываем информацию о просмотре результатов в лог
    log_user_action("Просмотр результатов расчета", {"total_cost": results["total_cost"]})

def generate_csv(results):
    """
    Генерирует CSV-файл с результатами расчета
    
    Args:
        results (dict): Словарь с результатами расчета
        
    Returns:
        str: Содержимое CSV-файла
    """
    output = io.StringIO()
    
    # Получаем данные для CSV
    dimensions = results.get('dimensions', {})
    width_m = dimensions.get('width_m', 0)
    length_m = dimensions.get('length_m', 0)
    area = round(width_m * length_m, 2)
    
    # Получаем информацию о перголе
    pergola_type = ""
    lamella_type = ""
    lighting_type = "Без освещения"
    
    if 'options' in st.session_state:
        pergola_options = st.session_state.options
        # Тип перголы
        pt = pergola_options.get('pergola_type', '')
        if pt == 'B500NEW':
            pergola_type = "Биоклиматическая с поворотными ламелями (B500)"
        elif pt == 'B700NEW':
            pergola_type = "Биоклиматическая со сдвижными ламелями (B700)"
        elif pt == 'B600':
            pergola_type = "Стационарная с PIR-панелями (B600)"
            
        # Тип ламелей
        lt = pergola_options.get('lamella_type', '')
        if '20' in lt:
            lamella_type = "200 мм усиленные"
        elif '25' in lt:
            lamella_type = "250 мм стандартные"
        elif 'B600' in lt:
            lamella_type = "PIR панели"
            
        # Освещение
        light = pergola_options.get('lighting_type', 'none')
        if light == 'led':
            lighting_type = "LED освещение"
        elif light == 'rgb':
            lighting_type = "RGB освещение"
        elif light == 'none':
            lighting_type = "Без освещения"
    
    # Получаем детали расчета
    detailed_costs = results.get('detailed_costs', {})
    
    # Создаем данные для CSV
    csv_data = [
        ["Калькулятор стоимости пергол", "", ""],
        ["", "", ""],
        ["Дата расчета", datetime.now().strftime("%d.%m.%Y %H:%M"), ""],
        ["", "", ""],
        ["СПЕЦИФИКАЦИЯ ПЕРГОЛЫ", "", ""],
        ["Тип перголы", pergola_type, ""],
        ["Тип ламелей", lamella_type, ""],
        ["Ширина", f"{width_m} м", ""],
        ["Длина (вынос)", f"{length_m} м", ""],
        ["Площадь", f"{area} м²", ""],
        ["Освещение", lighting_type, ""],
        ["", "", ""],
        ["РАСЧЕТ СТОИМОСТИ", "", ""],
        ["Базовая стоимость", detailed_costs.get('base_price', 0), "€"],
    ]
    
    # Добавляем стоимость дополнительных колонн, если есть
    additional_columns = detailed_costs.get('additional_columns', 0)
    if additional_columns > 0:
        csv_data.append(["Стоимость дополнительных колонн", additional_columns, "€"])
    
    # Добавляем стоимость освещения, если есть
    lighting_cost = detailed_costs.get('lighting', 0)
    if lighting_cost > 0:
        csv_data.append(["Стоимость освещения", lighting_cost, "€"])
    
    # Добавляем стоимость автоматизации, если есть
    automation_cost = detailed_costs.get('additional_options', {}).get('automation', 0)
    if automation_cost > 0:
        automation_type = detailed_costs.get('automation_type', '')
        automation_manufacturer = detailed_costs.get('automation_manufacturer', '')
        csv_data.append([f"Автоматизация {automation_manufacturer} {automation_type}", automation_cost, "€"])
    
    # Добавляем стоимость пульта ДУ, если есть
    remote_control_cost = detailed_costs.get('remote_control_cost', 0)
    if remote_control_cost > 0:
        remote_control = detailed_costs.get('remote_control', '')
        csv_data.append([f"Пульт ДУ {remote_control}", remote_control_cost, "€"])
    
    # Добавляем общую стоимость
    csv_data.append(["", "", ""])
    csv_data.append(["ИТОГО", results.get('total_cost', 0), "€"])
    
    # Записываем данные в CSV
    pd.DataFrame(csv_data).to_csv(output, index=False, header=False)
    
    return output.getvalue()