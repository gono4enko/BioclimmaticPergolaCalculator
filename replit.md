# Калькулятор биоклиматических пергол

## Описание
Двуязычное (русский) приложение для расчёта стоимости биоклиматических пергол. Streamlit-фронтенд + Flask-бэкенд для генерации PDF.

## Архитектура
- **Streamlit** (`app.py`) — основное приложение калькулятора, порт 5000
- **Flask** (`flask_app/`) — бэкенд для PDF-генерации и API, порт 8000

## Запуск
- StreamlitApp: `streamlit run app.py --server.port 5000`
- FlaskApp: `python -m flask --app flask_app:create_app run --host=0.0.0.0 --port=8000`

## Структура проекта
- `app.py` — основной файл Streamlit-приложения (~5000 строк)
- `flask_app/` — Flask-приложение (controllers, models, services, templates)
- `flask_app/services/pdf_generator.py` — PDF-генерация через ReportLab (возвращает bytes)
- `pdf_generator_fpdf_rus.py` — основной PDF-генератор через fpdf2 (возвращает bytes)
- `components/` — компоненты Streamlit (admin_auth, gallery, dimensions_form)
- `config/` — конфигурация цен и описаний пергол
- `fonts/` — шрифты DejaVuSans для PDF
- `data/price_tables/` — CSV прайс-листы

## Ключевые функции в app.py
- `render_pergola_type_form()` — выбор типа перголы (1-й блок)
- `render_lamella_type_form()` — выбор типа ламелей (2-й блок)
- `render_dimensions_form()` — ввод размеров (3-й блок)
- `render_additional_options_form()` — доп. опции: освещение, установка (4-й блок)
- `perform_calculation()` — расчёт стоимости
- `render_results()` — отображение результатов
- `main()` — главная функция (~строка 4116)

## Типы пергол
- B500NEW — поворотные ламели (200/250 мм)
- B700NEW — поворотно-сдвижные ламели (200/250 мм)
- B600 — стационарные PIR-панели

## MAX_DIMENSIONS ключи
Формат: `{тип_перголы}_{размер_ламели}` — например `B500NEW_250`, `B700NEW_200`, `B600`

## PDF-генерация
- Все PDF-генераторы возвращают `bytes` (не сохраняют файлы на диск)
- `export_to_pdf()` в app.py возвращает `(pdf_bytes, file_name)` tuple
- Streamlit UI: `st.download_button(data=pdf_bytes)` — прямое скачивание без промежуточных файлов
- Flask API `/export-pdf`: возвращает PDF через `send_file(BytesIO(pdf_bytes))`
- Кэш PDF в session_state: `pdf_bytes`, `pdf_file_name` — сбрасываются при пересчёте

## База данных
PostgreSQL через DATABASE_URL
