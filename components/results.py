"""
Компонент для отображения результатов расчета
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime

def render_results(results):
    """
    Отображает результаты расчета стоимости перголы
    
    Args:
        results (dict): Словарь с результатами расчета
    """
    st.subheader("Результаты расчета")
    
    # Создаем вкладки для различных видов результатов
    tab1, tab2, tab3, tab4 = st.tabs(["Общие данные", "Детализация стоимости", "Технические параметры", "Экспорт"])
    
    with tab1:
        st.markdown(f"### Итоговая стоимость: {results['total_cost']} €")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Основные параметры:")
            st.markdown(f"**Тип перголы:** {results['selected_options']['pergola_type']}")
            st.markdown(f"**Тип ламелей:** {results['selected_options']['lamella_type']}")
            st.markdown(f"**Тип монтажа:** {results['selected_options']['installation_type']}")
            st.markdown(f"**Управление:** {results['selected_options']['control_type']}")
            
            st.markdown("#### Размеры:")
            st.markdown(f"**Ширина:** {results['dimensions']['width']} мм")
            st.markdown(f"**Длина:** {results['dimensions']['length']} мм")
            st.markdown(f"**Высота:** {results['dimensions']['height']} мм")
            st.markdown(f"**Площадь:** {results['dimensions']['area']} м²")
        
        with col2:
            st.markdown("#### Дополнительные опции:")
            st.markdown(f"**Освещение:** {results['selected_options']['lighting_type']}")
            st.markdown(f"**Цвет:** {results['selected_options']['color_type']}")
            
            if results['selected_options']['additional_systems']:
                st.markdown("**Дополнительные системы:**")
                for system in results['selected_options']['additional_systems']:
                    if system == 'glazing_guillotine':
                        st.markdown("- Гильотинное остекление (W-серия)")
                    elif system == 'glazing_sliding':
                        st.markdown("- Раздвижное остекление (S-серия)")
                    elif system == 'zip_screen':
                        st.markdown("- Подъемный ZIP экран")
            else:
                st.markdown("**Дополнительные системы:** Нет")
            
            # Добавляем кнопку для печати
            st.markdown("#### Экспорт:")
            if st.button("Распечатать результаты", use_container_width=True):
                st.markdown("Пожалуйста, используйте функцию печати вашего браузера (Ctrl+P)")
    
    with tab2:
        st.markdown("### Детализация стоимости")
        
        # Создаем таблицу с детализацией стоимости
        cost_items = []
        
        # Базовая конструкция
        cost_items.append({
            "Наименование": "Базовая конструкция",
            "Количество": f"{results['dimensions']['area']} м²",
            "Стоимость": f"{results['cost_breakdown']['base_structure']} €"
        })
        
        # Ламели
        cost_items.append({
            "Наименование": f"Ламели ({results['selected_options']['lamella_type']})",
            "Количество": f"{results['cost_breakdown']['lamellas']['count']} шт.",
            "Стоимость": f"{results['cost_breakdown']['lamellas']['total_price']} €"
        })
        
        # Колонны
        cost_items.append({
            "Наименование": "Колонны",
            "Количество": f"{results['cost_breakdown']['columns']['count']} шт.",
            "Стоимость": f"{results['cost_breakdown']['columns']['total_price']} €"
        })
        
        # Управление
        cost_items.append({
            "Наименование": f"Система управления ({results['selected_options']['control_type']})",
            "Количество": "1 комплект",
            "Стоимость": f"{results['cost_breakdown']['control']} €"
        })
        
        # Освещение
        if results['selected_options']['lighting_type'] != "Без освещения":
            cost_items.append({
                "Наименование": f"Освещение ({results['selected_options']['lighting_type']})",
                "Количество": f"{results['dimensions']['perimeter']} м",
                "Стоимость": f"{results['cost_breakdown']['lighting']} €"
            })
        
        # Дополнительные системы
        if results['cost_breakdown']['additional_systems']['total_price'] > 0:
            for system in results['cost_breakdown']['additional_systems']['details']:
                cost_items.append({
                    "Наименование": system['name'],
                    "Количество": f"{system['area']} м²",
                    "Стоимость": f"{system['total_price']} €"
                })
        
        # Окраска
        if results['cost_breakdown']['color'] > 0:
            cost_items.append({
                "Наименование": f"Окраска ({results['selected_options']['color_type']})",
                "Количество": "1 комплект",
                "Стоимость": f"{results['cost_breakdown']['color']} €"
            })
        
        # Автоматизация
        if results['cost_breakdown']['automation'] > 0:
            cost_items.append({
                "Наименование": "Система автоматизации",
                "Количество": "1 комплект",
                "Стоимость": f"{results['cost_breakdown']['automation']} €"
            })
        
        # Скидка на площадь
        if results['cost_breakdown']['discount_amount'] > 0:
            cost_items.append({
                "Наименование": f"Скидка на площадь ({results['cost_breakdown']['area_discount']*100}%)",
                "Количество": "",
                "Стоимость": f"-{results['cost_breakdown']['discount_amount']} €"
            })
        
        # Итого
        cost_items.append({
            "Наименование": "**ИТОГО**",
            "Количество": "",
            "Стоимость": f"**{results['total_cost']} €**"
        })
        
        # Отображаем таблицу
        st.table(pd.DataFrame(cost_items))
        
        # Отображаем дополнительную информацию о коэффициентах
        st.markdown("### Применённые коэффициенты")
        coef_data = []
        
        coef_data.append({
            "Наименование коэффициента": "Коэффициент типа установки",
            "Значение": results['cost_breakdown']['installation_factor']
        })
        
        coef_data.append({
            "Наименование коэффициента": "Коэффициент сложности",
            "Значение": results['cost_breakdown']['complexity_factor']
        })
        
        st.table(pd.DataFrame(coef_data))
    
    with tab3:
        st.markdown("### Технические параметры")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Основные характеристики")
            st.markdown(f"**Тип перголы:** {results['selected_options']['pergola_type']}")
            st.markdown(f"**Тип ламелей:** {results['selected_options']['lamella_type']}")
            st.markdown(f"**Количество ламелей:** {results['cost_breakdown']['lamellas']['count']} шт.")
            st.markdown(f"**Количество колонн:** {results['cost_breakdown']['columns']['count']} шт.")
            
            if 'pergola_type' in st.session_state:
                pergola_type = st.session_state['pergola_type']
                if pergola_type.startswith('B500'):
                    st.markdown("**Тип поворота ламелей:** Нижняя ось вращения")
                elif pergola_type.startswith('B700'):
                    st.markdown("**Тип поворота ламелей:** Сдвижные ламели")
                elif pergola_type.startswith('B400'):
                    st.markdown("**Тип поворота ламелей:** Центральная ось вращения")
        
        with col2:
            st.markdown("#### Ограничения и рекомендации")
            # Общая информация о нагрузочных характеристиках из каталога
            st.markdown("""
            **Нагрузочные характеристики (на основе каталога):**
            - Максимальный пролет между колоннами: до 7 м
            - Максимальный вынос: до 8 м
            - Максимальная высота колонн: до 7 м
            
            **Рекомендации по эксплуатации:**
            - Максимальный прогиб ламели под рабочей нагрузкой не более 15-20 мм
            - Максимальный прогиб ламели под снеговой нагрузкой не более 30-40 мм при закрытых ламелях
            """)
    
    with tab4:
        st.markdown("### Экспорт данных")
        
        # Подготовка данных для экспорта
        export_data = {
            "calculation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pergola_info": {
                "type": results['selected_options']['pergola_type'],
                "lamella_type": results['selected_options']['lamella_type'],
                "installation_type": results['selected_options']['installation_type'],
                "dimensions": results['dimensions'],
                "options": {
                    "lighting": results['selected_options']['lighting_type'],
                    "control": results['selected_options']['control_type'],
                    "color": results['selected_options']['color_type'],
                    "additional_systems": results['selected_options']['additional_systems']
                }
            },
            "cost_breakdown": results['cost_breakdown'],
            "total_cost": results['total_cost']
        }
        
        # Экспорт в JSON
        json_data = json.dumps(export_data, indent=4, ensure_ascii=False)
        st.download_button(
            label="Скачать результаты в JSON",
            data=json_data,
            file_name=f"pergola_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )
        
        # Экспорт в CSV
        def generate_csv():
            csv_rows = []
            
            # Заголовок
            csv_rows.append(f"Расчет перголы от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            csv_rows.append("")
            
            # Основная информация
            csv_rows.append("Основная информация:")
            csv_rows.append(f"Тип перголы,{results['selected_options']['pergola_type']}")
            csv_rows.append(f"Тип ламелей,{results['selected_options']['lamella_type']}")
            csv_rows.append(f"Тип монтажа,{results['selected_options']['installation_type']}")
            csv_rows.append("")
            
            # Размеры
            csv_rows.append("Размеры:")
            csv_rows.append(f"Ширина (мм),{results['dimensions']['width']}")
            csv_rows.append(f"Длина (мм),{results['dimensions']['length']}")
            csv_rows.append(f"Высота (мм),{results['dimensions']['height']}")
            csv_rows.append(f"Площадь (м²),{results['dimensions']['area']}")
            csv_rows.append("")
            
            # Опции
            csv_rows.append("Дополнительные опции:")
            csv_rows.append(f"Освещение,{results['selected_options']['lighting_type']}")
            csv_rows.append(f"Управление,{results['selected_options']['control_type']}")
            csv_rows.append(f"Цвет,{results['selected_options']['color_type']}")
            
            # Дополнительные системы
            if results['selected_options']['additional_systems']:
                csv_rows.append("Дополнительные системы:")
                for system in results['selected_options']['additional_systems']:
                    if system == 'glazing_guillotine':
                        csv_rows.append("- Гильотинное остекление (W-серия)")
                    elif system == 'glazing_sliding':
                        csv_rows.append("- Раздвижное остекление (S-серия)")
                    elif system == 'zip_screen':
                        csv_rows.append("- Подъемный ZIP экран")
            csv_rows.append("")
            
            # Стоимость
            csv_rows.append("Стоимость:")
            csv_rows.append(f"Базовая конструкция,{results['cost_breakdown']['base_structure']} €")
            csv_rows.append(f"Ламели,{results['cost_breakdown']['lamellas']['total_price']} €")
            csv_rows.append(f"Колонны,{results['cost_breakdown']['columns']['total_price']} €")
            csv_rows.append(f"Управление,{results['cost_breakdown']['control']} €")
            
            if results['cost_breakdown']['lighting'] > 0:
                csv_rows.append(f"Освещение,{results['cost_breakdown']['lighting']} €")
            
            if results['cost_breakdown']['additional_systems']['total_price'] > 0:
                csv_rows.append(f"Дополнительные системы,{results['cost_breakdown']['additional_systems']['total_price']} €")
            
            if results['cost_breakdown']['color'] > 0:
                csv_rows.append(f"Окраска,{results['cost_breakdown']['color']} €")
            
            if results['cost_breakdown']['automation'] > 0:
                csv_rows.append(f"Автоматизация,{results['cost_breakdown']['automation']} €")
            
            if results['cost_breakdown']['discount_amount'] > 0:
                csv_rows.append(f"Скидка,{results['cost_breakdown']['discount_amount']} €")
            
            csv_rows.append(f"ИТОГО,{results['total_cost']} €")
            
            return "\n".join(csv_rows)
        
        csv_data = generate_csv()
        st.download_button(
            label="Скачать результаты в CSV",
            data=csv_data,
            file_name=f"pergola_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
        
        # Информация для печати
        st.markdown("""
        ### Печать отчета
        
        Для печати полного отчета о расчете вы можете:
        1. Перейти на вкладку "Общие данные"
        2. Нажать кнопку "Распечатать результаты"
        3. Использовать функцию печати вашего браузера (Ctrl+P)
        """)
