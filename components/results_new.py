"""
Модуль для отображения результатов расчета перголы.
"""
import streamlit as st
from datetime import datetime

def render_results(results):
    """
    Отображает результаты расчета стоимости перголы
    
    Args:
        results (dict): Словарь с результатами расчета
    """
    # Добавляем якорь для прокрутки к результатам
    st.markdown('<div id="calculation-results"></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: #0066cc; font-size: 2.0rem; font-weight: 600; margin-bottom: 1rem;">Результаты расчета</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Проверяем, есть ли ошибка в результатах
    if 'error' in results:
        st.error(f"Ошибка при расчете: {results['error']}")
        return
    
    # Форматируем цены для отображения
    def format_price(price):
        return f"{price:,.2f}".replace(",", " ").replace(".", ",")
    
    # Создаем карточку с результатами
    with st.container():
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <h3 style="color: #0066cc; font-size: 1.6rem; font-weight: 600; margin-bottom: 1rem;">Итоговая стоимость</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Отображаем итоговую стоимость
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Стоимость в евро",
                f"€ {format_price(results['total_price'])}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Стоимость в рублях",
                f"₽ {format_price(results['total_price_rub'])}",
                delta=None,
                help=f"По курсу {results['euro_rate']} руб. за евро"
            )
    
    # Отображаем детальную спецификацию
    with st.expander("Подробная спецификация", expanded=True):
        # Заголовок таблицы
        st.markdown("""
            <div style="display: grid; grid-template-columns: 5fr 1fr 1fr 2fr; gap: 10px; font-weight: bold; 
                        padding: 10px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 10px;">
                <div>Наименование</div>
                <div>Цена</div>
                <div>Кол-во</div>
                <div>Сумма</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Базовая перголя
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 5fr 1fr 1fr 2fr; gap: 10px; 
                        padding: 10px; border-bottom: 1px solid #eee;">
                <div>Пергола {results.get('pergola_type', 'B500NEW')} с ламелями {results.get('lamella_size', '250')}мм</div>
                <div>€ {format_price(results['base_price'])}</div>
                <div>1</div>
                <div>€ {format_price(results['base_price'])}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Дополнительные опции
        for option in results.get('options_prices', []):
            st.markdown(f"""
                <div style="display: grid; grid-template-columns: 5fr 1fr 1fr 2fr; gap: 10px; 
                            padding: 10px; border-bottom: 1px solid #eee;">
                    <div>{option['name']}</div>
                    <div>€ {format_price(option['price'])}</div>
                    <div>{option['quantity']}</div>
                    <div>€ {format_price(option['total'])}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Итоговая строка
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 5fr 1fr 1fr 2fr; gap: 10px; 
                        padding: 10px; background-color: #f8f9fa; font-weight: bold; border-radius: 4px; margin-top: 10px;">
                <div>ИТОГО</div>
                <div></div>
                <div></div>
                <div>€ {format_price(results['total_price'])}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Добавляем информацию о времени расчета
    st.caption(f"Расчет выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    # Добавляем кнопку для загрузки коммерческого предложения в PDF
    st.download_button(
        label="Скачать КП в PDF",
        data=b"Placeholder for PDF data",  # Здесь должны быть данные PDF
        file_name=f"KP_Pergola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        help="Скачать коммерческое предложение с полной спецификацией перголы в формате PDF"
    )