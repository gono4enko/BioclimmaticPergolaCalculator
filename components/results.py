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
            value=f"{width_m:.1f}×{length_m:.1f} м"
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
        
        # Добавляем стоимость освещения
        lighting_cost = detailed_costs.get('lighting', 0)
        if lighting_cost > 0:
            cost_items.append(["Освещение", lighting_cost, "€"])
        
        # Добавляем стоимость дополнительных опций
        additional_options = detailed_costs.get('additional_options', {})
        for option, cost in additional_options.items():
            cost_items.append([f"Опция: {option}", cost, "€"])
        
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
    output.write(f"Ширина: {dimensions.get('width_mm', 0)} мм ({dimensions.get('width_m', 0):.1f} м)\n")
    output.write(f"Длина: {dimensions.get('length_mm', 0)} мм ({dimensions.get('length_m', 0):.1f} м)\n")
    output.write(f"Высота: {dimensions.get('height_mm', 0)} мм ({dimensions.get('height_m', 0):.1f} м)\n\n")
    
    # Записываем количество ламелей
    output.write(f"Количество ламелей: {results.get('lamella_count', 0)} шт.\n\n")
    
    # Записываем детальные расходы
    detailed_costs = results.get('detailed_costs', {})
    output.write("Детальная информация о стоимости:\n")
    output.write(f"Базовая стоимость перголы: {detailed_costs.get('base_price', 0)} €\n")
    
    # Стоимость освещения
    lighting_cost = detailed_costs.get('lighting', 0)
    if lighting_cost > 0:
        output.write(f"Освещение: {lighting_cost} €\n")
    
    # Стоимость дополнительных опций
    additional_options = detailed_costs.get('additional_options', {})
    for option, cost in additional_options.items():
        output.write(f"Опция {option}: {cost} €\n")
    
    # Общая стоимость
    output.write(f"\nИтоговая стоимость: {results['total_cost']} €\n")
    
    return output.getvalue()