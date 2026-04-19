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
  - `controllers/api_routes.py` — API: `/api/calculate`, `/api/pergola-types`, `/api/lamella-sizes/<type>`, `/api/max-dimensions`, `/api/export-pdf`, `/api/kp/<calc_id>`
  - `controllers/main_routes.py` — HTML-страницы: `/`, `/calculator`, `/kp/<calc_id>`, `/catalog`, `/about`, `/health`
  - `utils.py` — утилиты: generate_calc_id(), save/load_calculation(), generate_top_view_svg(), svg_to_png_path(), generate_qr_image(), check_scheduler_health()
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
  - Спец. режимы: `Автовыбор` (auto — cheapest), `Все варианты` (all — comparison table)
- **PDF export "Все варианты"**: `generate_commercial_offer(data, all_variants=list)` — сравнительная таблица модификаций + тех. характеристики (вес, снег/ветер, герметичность, макс. ширина модуля, защита от нагрева)
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
- B200 — стационарные ламели 200×50 мм, варианты: FLAT-20 (шаг 400 мм) / FLAT-25 (шаг 500 мм)
  - Колонны 100×100 мм, балка 200×50 мм
  - Нет привода, нет водоотвода (водостока). Опционально: LED-подсветка, пульт ДУ
  - Цены в БД: pergola_type='B200', lamella_size='20' или '25' (без variant IS NOT NULL)
  - selected_variant устанавливается из requested_variant для B200 (специальный elif в calculator.py)
  - Max: 13.5 м (ширина) × 12.1 м (вынос)

## MAX_DIMENSIONS ключи
Формат: `{тип_перголы}_{размер_ламели}` — например `B500NEW_250`, `B700NEW_200`, `B600`, `B200_20`, `B200_25`

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
- `/admin/glazing-prices?system=S500|S100` — матрица цен остекления (с применёнными правками)
- `/admin/glazing-save-cell` — правка одной ячейки матрицы остекления (`glazing_price_overrides`)
- `/admin/glazing-reset` — сброс правок остекления для системы (или конкретной конфигурации)
- `/admin/glazing-settings` — GET/POST наценок и стоимостей (`glazing_settings`)
- `/admin/scheduler` — визуальная панель статуса планировщика очистки
- `/admin/scheduler-status` — JSON API статуса планировщика
- Blueprint: `flask_app/controllers/admin_routes.py`
- Шаблоны: `admin_login.html`, `admin_prices.html`, `admin_scheduler.html`

## Маркетинговое КП
- **Динамический счётчик**: `flask_app/utils.py` → `get_pergola_count()` = base(10) + weeks_since(2026-01-01)
- **КП номер**: `generate_kp_number(pergola_type)` → формат B{тип}-{DDMMYY}-{random4}
- **Decolife контент**: `flask_app/static/decolife/{b500,b700,b600}/data.json` — описания, особенности, преимущества
- **API**: `/api/decolife-data/<pergola_type>` — возвращает JSON с маркетинговым контентом
- **Имя заказчика**: необязательное поле в Step 4, передаётся в PDF и отображается в KP
- **Web KP 10 блоков**: 1) Заголовок (номер+дата+14дней), 2) Цена-герой (urgency+80/20), 3) О модели + фото Decolife, 4) Особенности, 5) Преимущества, 6) Спецификация (micro-hints), 7) Стоимость/сравнение, 8) Гарантии+компания (счётчик), 9) Этапы+upsell, 10) Галерея+CTA
- **PDF 6 страниц**: P1=Hero cover (синий header, фото, цена, KP#), P2=Decolife описание+фото+параметры+спецификация, P3=Стоимость+варианты оплаты+сравнение, P4=Описание перголы (condensed), P5=Галерея, P6=Гарантии+upsell+примечания+контакты
- **Decolife fetcher**: `scripts/fetch_decolife.py` — загрузка/обновление контента, fallback на встроенные данные; автобутстрап+persist при старте
- **Счётчик на главной**: `index.html` → `#install-counter` в Hero секции + fetch `/api/promotions`
- **CSS**: `.kp-section`, `.kp-block`, `.kp-price-hero`, `.kp-urgency-banner`, `.kp-upsell-grid`, `.kp-gallery-grid`, `.kp-payment-terms`
- **Постоянная ссылка на КП**: `/kp/<calc_id>` — загружает сохранённый расчёт из `data/calculations/{calc_id}.json`
- **Очистка расчётов**: `CALC_RETENTION_DAYS` env var (default 30) — срок хранения файлов расчётов перед автоудалением; `CLEANUP_INTERVAL_HOURS` env var (default 24) — интервал автоочистки через APScheduler
- **Кнопка «Поделиться»**: копирует ссылку `/kp/{id}` в буфер обмена
- **SVG-схема в PDF**: вид сверху с размерами, ламелями/PIR-панелями, модулями (page 2)
- **QR-код в PDF**: на последней странице, ссылка на конкретный расчёт `/kp/<calc_id>`
- **Static cache**: CSS/JS v28

## Визуальные компоненты
- Hero-секция с параллакс-эффектом (`hero_pergola.jpg`)
- Промо-бейджи: загружаются через `/api/promotions`, рендерятся в `#promo-badges-container`
- Галерея: 8 фото проектов в секции «Реализованные проекты»
- Счётчик установок: анимированный, данные из `/api/promotions` (dynamic via `get_pergola_count()`)
- Лид-форма: Telegram, Max, Перезвонить — с маской телефона и rate-limiting
- Iframe-детект: баннер «Открыть полную версию» при встраивании
- Yandex Metrika: счётчик 65714473 в base.html, цели `calc_success`, `calculator_lead`

## Деплой
- `deploymentTarget: autoscale`
- Gunicorn на порту 5000
- Запуск: `gunicorn --bind=0.0.0.0:5000 --workers 2 --timeout 120 --reuse-port flask_app:create_app()`
- Flask стартует за ~1-2 сек (vs ~15 сек Streamlit)

## Гильотинное остекление (W-серия)
- **Модели**:
  - `W500` (стеклопакет 20 мм): W 1.0–5.0 м, H 1.5–3.5 м
  - `W600` (28 мм): W 2.0–5.0 м, H 2.0–4.0 м
  - `W700` (терморазрыв, 28 мм): W 2.0–5.0 м, H 2.0–4.0 м
- **Конфигурация проёма**: 2/3 створки (авто 3 при W > 3.6 м), цвет профиля (RAL 9T08/7024/8028/9016/Special +10%), тип стеклопакета (Прозрачное/Multifunctional +10%), опция «плавник» (авто при W > 3.0 м, 80 €/м для W500, 100 €/м для W600/W700).
- **Привод**: SIMU или SOMFY; автоподбор момента (`w·h·7.5 + 4` Нм) и Tandem-режим (обязателен при W > 3.0 м).
- **Управление**: каждое окно W-серии учитывается как +1 канал пульта ДУ (для B500/B700 — суммируется с приводами и LED-контроллерами; для B600/B200 — с контроллерами освещения, либо отдельный пульт, если света нет).
- **Спецификация**: формат spec `W500|W600|W700:sashes:color:glass`; рендерится в фасадных схемах и iso-видах как горизонтально-поднимающиеся створки.
