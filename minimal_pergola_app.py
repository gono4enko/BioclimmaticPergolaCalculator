"""
Минимальная версия приложения для расчета пергол с рабочим PDF-экспортом.
Использует только базовые компоненты без дополнительных модулей.
"""
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from fpdf import FPDF

st.set_page_config(
    page_title="Калькулятор пергол (Упрощенная версия)",
    page_icon="🏠",
    layout="wide"
)

# Подготавливаем директории для данных и PDF
os.makedirs("data", exist_ok=True)
os.makedirs("data/price_tables", exist_ok=True)
os.makedirs("generated_pdf", exist_ok=True)

# Фиксированные данные для расчета
PERGOLA_TYPES = ["B500", "B600", "B700"]
LAMELLA_SIZES = ["200", "250"]
WIDTH_RANGE = (2.0, 7.0, 0.5)  # (мин, макс, шаг)
LENGTH_RANGE = (2.0, 7.0, 0.5)  # (мин, макс, шаг)

# Сессионные переменные
if 'results' not in st.session_state:
    st.session_state.results = None

# Генерация синтетических данных для цен (в реальном приложении здесь загрузка из CSV)
def generate_price_data():
    """Генерирует тестовые цены для разных размеров пергол"""
    base_price = 350000
    width_range = [round(w, 1) for w in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]]
    length_range = [round(l, 1) for l in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]]
    
    price_data = {}
    for width in width_range:
        for length in length_range:
            # Формула цены: базовая + коэффициент площади + доп. за каждый размер
            area = width * length
            price = base_price + (area * 15000) + (width * 5000) + (length * 5000)
            key = f"{width}x{length}"
            price_data[key] = round(price)
    
    return price_data

# Функция для создания PDF
def create_simple_pdf(data):
    """
    Создает простой PDF файл с информацией о перголе
    """
    try:
        # Имя файла с меткой времени для уникальности
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"pergola_quote_{timestamp}.pdf"
        
        # Полный путь к файлу
        pdf_file_path = os.path.join("generated_pdf", pdf_filename)
        
        # Создаем PDF объект
        pdf = FPDF()
        pdf.add_page()
        
        # Заголовок
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Расчет стоимости перголы", 0, 1, "C")
        pdf.ln(5)
        
        # Основные параметры
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Параметры перголы:", 0, 1)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(60, 6, "Модель:", 0, 0)
        pdf.cell(0, 6, f"{data.get('pergola_type', 'B500')}", 0, 1)
        
        pdf.cell(60, 6, "Ширина:", 0, 0)
        pdf.cell(0, 6, f"{data.get('width', 3.0)} м", 0, 1)
        
        pdf.cell(60, 6, "Длина:", 0, 0)
        pdf.cell(0, 6, f"{data.get('length', 4.0)} м", 0, 1)
        
        pdf.cell(60, 6, "Цвет:", 0, 0)
        pdf.cell(0, 6, "Стандартный", 0, 1)
        
        pdf.ln(10)
        
        # Стоимость
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Стоимость:", 0, 1)
        
        total_price = data.get('price', 0)
        discount = total_price * 0.05  # 5% скидка
        final_price = total_price - discount
        
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(60, 6, "Базовая стоимость:", 0, 0)
        pdf.cell(0, 6, f"{total_price:,.0f} руб.", 0, 1)
        
        pdf.cell(60, 6, "Скидка:", 0, 0)
        pdf.cell(0, 6, f"{discount:,.0f} руб.", 0, 1)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(60, 6, "Итоговая стоимость:", 0, 0)
        pdf.cell(0, 6, f"{final_price:,.0f} руб.", 0, 1)
        
        pdf.ln(15)
        
        # Подпись
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 10, "С уважением,", 0, 1)
        pdf.cell(0, 6, "Компания «Комфортный Дом»", 0, 1)
        pdf.cell(0, 6, "Тел: +7 (XXX) XXX-XX-XX", 0, 1)
        
        # Сохраняем PDF
        pdf.output(pdf_file_path)
        
        return pdf_file_path
    except Exception as e:
        st.error(f"Ошибка при создании PDF: {str(e)}")
        print(f"Ошибка при создании PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

# Функция для расчета стоимости
def calculate_price(pergola_type, width, length):
    """
    Рассчитывает стоимость перголы исходя из типа и размеров
    """
    # В реальном приложении здесь сложная логика с данными из CSV
    price_data = generate_price_data()
    
    # Округляем до ближайшего доступного размера
    width_rounded = round(width * 2) / 2  # округление до 0.5
    length_rounded = round(length * 2) / 2  # округление до 0.5
    
    # Получаем цену из данных или используем формулу если нет точного соответствия
    key = f"{width_rounded}x{length_rounded}"
    base_price = price_data.get(key)
    
    # Коэффициенты по типу перголы
    type_coefficient = 1.0
    if pergola_type == "B600":
        type_coefficient = 1.15
    elif pergola_type == "B700":
        type_coefficient = 1.25
    
    final_price = base_price * type_coefficient
    
    return {
        "base_price": base_price,
        "final_price": final_price,
        "discount": final_price * 0.05,  # 5% скидка
        "price_after_discount": final_price * 0.95
    }

# Интерфейс пользователя
st.title("Калькулятор стоимости перголы")

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #2c3e50;
    }
    .result-box {
        padding: 20px;
        border-radius: 5px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Форма для ввода данных
with st.form("calculator_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Параметры перголы")
        pergola_type = st.selectbox("Тип перголы", PERGOLA_TYPES)
        lamella_size = st.selectbox("Размер ламелей (мм)", LAMELLA_SIZES)
        
    with col2:
        st.subheader("Размеры")
        width = st.slider("Ширина (м)", 
                        min_value=WIDTH_RANGE[0], 
                        max_value=WIDTH_RANGE[1], 
                        step=WIDTH_RANGE[2],
                        value=3.0)
        
        length = st.slider("Длина (м)", 
                        min_value=LENGTH_RANGE[0], 
                        max_value=LENGTH_RANGE[1],
                        step=LENGTH_RANGE[2],
                        value=4.0)
    
    submit_button = st.form_submit_button("Рассчитать стоимость")

# Обработка отправки формы
if submit_button:
    # Запускаем расчет
    price_results = calculate_price(pergola_type, width, length)
    
    # Сохраняем результаты в сессии
    st.session_state.results = {
        "pergola_type": pergola_type,
        "lamella_size": lamella_size,
        "width": width,
        "length": length,
        "price": price_results["final_price"],
        "discount": price_results["discount"],
        "price_after_discount": price_results["price_after_discount"]
    }
    
    # Отображаем результаты анимированно
    with st.container():
        st.subheader("Результаты расчета")
        
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Параметры:")
            st.write(f"**Тип перголы:** {pergola_type}")
            st.write(f"**Размер ламелей:** {lamella_size} мм")
            st.write(f"**Размеры:** {width} x {length} м")
        
        with col2:
            st.markdown("### Стоимость:")
            st.write(f"**Базовая стоимость:** {price_results['final_price']:,.0f} руб.")
            st.write(f"**Скидка:** {price_results['discount']:,.0f} руб.")
            st.write(f"**Итоговая стоимость:** {price_results['price_after_discount']:,.0f} руб.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Кнопка для создания PDF
        if st.button("📄 Экспорт в PDF"):
            with st.spinner("Создаем PDF документ..."):
                pdf_path = create_simple_pdf(st.session_state.results)
                
                if pdf_path and os.path.exists(pdf_path):
                    # Отображаем информацию о файле
                    file_size = os.path.getsize(pdf_path) / 1024  # Размер в КБ
                    st.success(f"PDF успешно создан! Размер файла: {file_size:.1f} КБ")
                    
                    # Кнопка скачивания
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Скачать PDF",
                            data=f.read(),
                            file_name=f"Пергола_{pergola_type}_{width}x{length}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.error("Не удалось создать PDF файл, пожалуйста, повторите попытку.")

# Информация внизу страницы
st.markdown("---")
st.caption("© 2025 Комфортный дом | Калькулятор пергол (минимальная версия)")