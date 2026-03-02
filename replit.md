# Калькулятор биоклиматических пергол

## Описание
Двуязычное (русский) приложение для расчёта стоимости биоклиматических пергол. Flask + Gunicorn фронтенд и бэкенд на порту 5000.

## Архитектура
- **Flask** (`flask_app/`) — основное приложение (калькулятор, API, PDF), порт 5000
- **Gunicorn** — production-сервер, 2 воркера, таймаут 120 сек
- **Streamlit** (`app.py`) — устаревший фронтенд, сохранён для справки

## Запуск
- FlaskApp: `gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --reuse-port --reload 'flask_app:create_app()'`

## Структура проекта
- `flask_app/` — Flask-приложение
  - `__init__.py` — фабрика приложения `create_app()`
  - `controllers/api_routes.py` — API: `/api/calculate`, `/api/pergola-types`, `/api/lamella-sizes/<type>`, `/api/max-dimensions`, `/api/export-pdf`
  - `controllers/main_routes.py` — HTML-страницы: `/`, `/calculator`, `/catalog`, `/about`, `/health`
  - `services/calculator.py` — бизнес-логика расчёта (порт из app.py)
  - `templates/calculator.html` — страница калькулятора (Bootstrap 5)
  - `static/js/calculator.js` — клиентская логика формы
  - `static/css/calculator.css` — стили калькулятора
- `pdf_generator_fpdf_rus.py` — PDF-генератор через fpdf2 (кириллица)
- `config/pricing_settings.py` — курс евро, наценки доставки/установки (JSON-файл)
- `config/promotions.py` — сезонные акции и скидки
- `config/pergola_descriptions.py` — описания типов пергол
- `data/price_tables/` — CSV прайс-листы (русские имена файлов)
- `fonts/` — шрифты DejaVuSans для PDF

## Бизнес-логика расчёта
- CSV прайс-листы: строка = длина (вынос), столбец = ширина. Ширина и длина ПОМЕНЯНЫ в CSV vs параметрах калькулятора
- Курс евро: 110 ₽/€ по умолчанию (из `config/pricing_settings.json`)
- Модули по ширине: ≤4.5м = 1, ≤9.0м = 2, >9.0м = 3
- Доп. колонны: порог 6.5м (ламели 250/PIR) или 6.85м (ламели 200)
- Усилитель лотка: порог >6.5м, цена 80 €/м, кол-во лотков = модули+1
- Привод B500: Bansbach (Т1=700€, Tandem=1250€); длина>6м всегда Tandem
- Привод B700: Somfy (M1=300€, Tandem=1000€)
- Пульт ДУ: Simu 1K/5K/15K (25/40/90€) по числу каналов
- Подсветка: 20 €/м (белая/RGB), контроллер 300 €
- Доставка: 7% наценка, Установка: 13% наценка (от базовой суммы)
- 3 ИТОГО строки: Наличный (base RUB), Безналичный (×1.08), С НДС 22% (×1.15)

## Типы пергол
- B500NEW — поворотные ламели (200/250 мм)
- B700NEW — поворотно-сдвижные ламели (200/250 мм)
- B600 — стационарные PIR-панели

## MAX_DIMENSIONS ключи
Формат: `{тип_перголы}_{размер_ламели}` — например `B500NEW_250`, `B700NEW_200`, `B600`

## PDF-генерация
- `format_pergola_data_for_pdf()` готовит данные расчёта для PDF
- `generate_commercial_offer()` генерирует PDF (bytes)
- Flask API `/api/export-pdf` — принимает POST с результатом расчёта, возвращает PDF-файл
- Цены конвертируются EUR→RUB перед передачей в PDF

## База данных
PostgreSQL через DATABASE_URL

## Деплой
- `deploymentTarget: autoscale`
- Gunicorn на порту 5000
- Запуск: `gunicorn --bind=0.0.0.0:5000 --workers 2 --timeout 120 --reuse-port flask_app:create_app()`
