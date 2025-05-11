"""
Тестовый модуль для проверки генерации PDF без зависимости от основного приложения
"""
import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF

st.set_page_config(
    page_title="Тест генерации PDF",
    page_icon="📄",
    layout="centered"
)

def create_basic_pdf(output_path):
    """
    Создает простой PDF-файл с минимальным содержимым.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Заголовок
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Test PDF Document", 0, 1, "C")
        
        # Текстовое содержимое
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        pdf.cell(0, 10, "This is a test PDF document", 0, 1)
        
        # Сохранение файла
        pdf.output(output_path)
        return True
    except Exception as e:
        st.error(f"Ошибка при создании PDF: {str(e)}")
        return False

# Создаем директорию для PDF если ее нет
os.makedirs("test_pdf", exist_ok=True)

st.title("Тест генерации PDF")

col1, col2 = st.columns(2)

with col1:
    st.write("### Создать простой PDF")
    if st.button("Создать тестовый PDF"):
        pdf_path = os.path.join("test_pdf", f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        with st.spinner("Создание PDF..."):
            if create_basic_pdf(pdf_path):
                st.success(f"PDF успешно создан: {pdf_path}")
                
                # Отображаем информацию о файле
                file_size = os.path.getsize(pdf_path) / 1024  # размер в КБ
                st.info(f"Размер файла: {file_size:.1f} КБ")
                
                # Добавляем кнопку скачивания
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    st.download_button(
                        label="Скачать тестовый PDF",
                        data=pdf_bytes,
                        file_name="test_pdf.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("Ошибка при создании PDF")

with col2:
    st.write("### Информация")
    st.info("""
    Эта страница тестирует базовую функциональность генерации PDF 
    без зависимости от основного приложения.
    
    Нажмите кнопку слева, чтобы создать и скачать простой PDF-файл.
    """)
    
    # Показываем список существующих PDF
    st.write("### Созданные PDF:")
    if os.path.exists("test_pdf"):
        pdf_files = [f for f in os.listdir("test_pdf") if f.endswith('.pdf')]
        if pdf_files:
            for pdf_file in pdf_files:
                file_path = os.path.join("test_pdf", pdf_file)
                file_size = os.path.getsize(file_path) / 1024  # размер в КБ
                st.text(f"{pdf_file} ({file_size:.1f} КБ)")
        else:
            st.text("Нет созданных PDF файлов")
    else:
        st.text("Директория test_pdf не найдена")
        
# Показываем строковое представление используемого класса FPDF
st.write("### Информация о FPDF:")
st.code(f"FPDF class: {FPDF}")
st.code(f"FPDF version: {FPDF.__version__ if hasattr(FPDF, '__version__') else 'Unknown'}")
st.code(f"FPDF module path: {FPDF.__module__}")