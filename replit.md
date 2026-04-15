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
- Курс евро: 100 ₽/€ (из `config/pricing_settings.json`)
- Модули по ширине (B600): ≤4.5м = 1, ≤9.0м = 2, >9.0м = 3
- **B500/B700 вариантное ценообразование**: 3 варианта (Basic/Light/Pro) с ручным выбором пользователем через Step 2 "Модификация"
  - B500 Basic 250мм: 1мод 2.5-4.5м, 2мод 5.0-9.0м, 3мод 7.5-13.5м
  - B500 Light 250мм: 1мод 2.5-4.0м, 2мод 5.0-8.0м, 3мод 7.5-12.0м
  - B500 Pro 250мм: 1мод 2.5-4.5м, 2мод 5.0-9.0м, 3мод 7.5-13.5м
  - B500 Pro 200мм: 1мод 3.0-5.0м, 2мод 6.0-10.0м, 3мод 9.0-15.0м
  - B700 Basic 250мм: 1мод 2.5-4.5м, 2мод 5.0-9.0м, 3мод 7.5-13.5м
  - B700 Light 250мм: 1мод 2.5-4.0м, 2мод 5.0-8.0м, 3мод 7.5-12.0м
  - B700 Pro 250мм: 1мод 2.5-4.5м, 2мод 5.0-9.0м, 3мод 7.5-13.5м
  - B700 Pro 200мм: 1мод 3.0-5.0м, 2мод 6.0-10.0м, 3мод 9.0-15.0м
  - `get_best_variant_price()` использует `requested_variant` от пользователя; если не указан — выбирает минимум
  - Результат включает `selected_variant` (имя выбранного варианта)
  - В описании перголы и ламелей указывается выбранный вариант
- **Шаг "Модификация" (Step 2)**: после выбора типа перголы показывает карточки вариантов с тех. характеристиками (ламель, колонна, балка, макс. вылет)
  - Конфиг: `config/variant_specs.py` — `VARIANT_SPECS`, `VARIANT_DISPLAY_ORDER`, `get_variant_options()`
  - API: `/api/variant-options/<pergola_type>` — возвращает варианты с характеристиками
- Доп. колонны: порог 6.5м (ламели 250/PIR) или 6.85м (ламели 200)
- Усилитель лотка: порог >6.5м, цена 80 €/м, кол-во лотков = модули+1
- Привод B500: Bansbach (Т1=700€, Tandem=1250€); длина>6м всегда Tandem
- Привод B700: Somfy (M1=300€, Tandem=1000€)
- Пульт ДУ: Simu 1K/5K/15K (25/40/90€) по числу каналов
- Подсветка: 20 €/м (белая/RGB), контроллер 300 €
- Доставка: 7% наценка, Установка: 13% наценка (от базовой суммы)
- 3 ИТОГО строки: Наличный (base RUB), Безналичный (÷0.92), С НДС (÷0.85)

## Типы пергол
- B500NEW — поворотные ламели (200/250 мм), варианты: Basic/Light/Pro
- B700NEW — поворотно-сдвижные ламели (200/250 мм), варианты: Basic/Light/Pro
- B600 — стационарные PIR-панели, варианты: Standard/Light
  - Standard: 1мод 2.5-5.0м, 2мод 6.0-10.0м, 3мод 10.5-15.0м (max ширина 15.0м)
  - Light: 1мод 2.5-4.0м, 2мод 5.0-8.0м, 3мод 7.5-12.0м (max ширина 12.0м)

## MAX_DIMENSIONS ключи
Формат: `{тип_перголы}_{размер_ламели}` — например `B500NEW_250`, `B700NEW_200`, `B600`

## PDF-генерация
- `format_pergola_data_for_pdf()` готовит данные расчёта для PDF
- `generate_commercial_offer()` генерирует PDF (bytes)
- Flask API `/api/export-pdf` — принимает POST с результатом расчёта, возвращает PDF-файл
- Цены конвертируются EUR→RUB перед передачей в PDF

## База данных
PostgreSQL через DATABASE_URL
- `price_data` — прайс-листы (pergola_type, lamella_size, variant, width=вылет, length=ширина, price EUR, modules, updated_at). B500NEW: 729 строк, B700NEW: 699 строк (Basic/Light/Pro), B600: 318 строк (Standard/Light)
- `leads` — заявки с лид-формы (phone, city, calc_text, channel, ip, created_at)
- Калькулятор читает цены из PostgreSQL (приоритет), fallback на CSV-файлы

## Админ-панель (/admin)
- `/admin/login` — авторизация по паролю (env `ADMIN_PASSWORD`)
- `/admin/prices` — просмотр/редактирование цен по моделям
- `/admin/parse-price-image` — загрузка скриншота прайс-листа → распознавание через Claude Vision (env `ANTHROPIC_API_KEY`)
- `/admin/apply-parsed-prices` — сохранение распознанных цен в БД + сброс кэша калькулятора
- `/admin/save-cell` — сохранение одной ячейки
- `/admin/get-prices` — получение текущих цен из БД
- Blueprint: `flask_app/controllers/admin_routes.py`
- Шаблоны: `admin_login.html`, `admin_prices.html`

## Визуальные компоненты
- Hero-секция с параллакс-эффектом (`hero_pergola.jpg`)
- Промо-бейджи: загружаются через `/api/promotions`, рендерятся в `#promo-badges-container`
- Галерея: 8 фото проектов в секции «Реализованные проекты»
- Счётчик установок: анимированный, данные из `/api/promotions`
- Лид-форма: Telegram, Max, Перезвонить — с маской телефона и rate-limiting
- Iframe-детект: баннер «Открыть полную версию» при встраивании
- Yandex Metrika: счётчик 65714473 в base.html, цели `calc_success`, `calculator_lead`

## Деплой
- `deploymentTarget: autoscale`
- Gunicorn на порту 5000
- Запуск: `gunicorn --bind=0.0.0.0:5000 --workers 2 --timeout 120 --reuse-port flask_app:create_app()`
- Flask стартует за ~1-2 сек (vs ~15 сек Streamlit)
