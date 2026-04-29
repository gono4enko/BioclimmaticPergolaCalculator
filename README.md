# Калькулятор стоимости пергол v4.3.5

Bilingual (RU) калькулятор биоклиматических пергол для брендов B500NEW, B700NEW, B600 (PIR) и B200 MAF AERO FLAT.
Многошаговая форма → расчёт → коммерческое предложение (КП) с PDF-экспортом и админ-панелью.

Стек: **Flask + Gunicorn**, PostgreSQL (опционально, цены подгружаются из CSV в `data/price_tables/` как fallback).

---

## 🚀 PRODUCTION DEPLOYMENT

### 1. Системные зависимости (Ubuntu 24.04)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev
```

### 2. Установка приложения

```bash
sudo mkdir -p /var/www/bioclim-calculator
cd /var/www/bioclim-calculator
git clone https://github.com/gono4enko/BioclimmaticPergolaCalculator.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **ВАЖНО**: `requirements.txt` пинит `fpdf==1.7.2` — НЕ обновляйте до fpdf2. Код калькулятора использует абсолютные пути к шрифтам, специфичные для fpdf 1.7.2 (`add_font(uni=True)` с абсолютным путём).

### 3. Переменные окружения (`.env`)

Скопируйте `.env.example` → `.env` и заполните:

```bash
cp .env.example .env
nano .env
```

Минимум обязательных:
- `DATABASE_URL` — postgres://… (опционально; CSV fallback в `data/price_tables/`)
- `SECRET_KEY` — длинная случайная строка для Flask sessions
- `ADMIN_PASSWORD` — пароль админ-панели `/admin`
- `ANTHROPIC_API_KEY` — для AI-функций (опционально)
- `GMAIL_USER`, `GMAIL_PASSWORD`, `RECIPIENT_EMAIL` — Gmail SMTP для приёма
  заявок «Жду звонка» / Telegram / Max. `GMAIL_PASSWORD` — это пароль приложения
  Google (16 символов), создаётся в https://myaccount.google.com/apppasswords
  (требуется 2FA на аккаунте). Без них заявки сохраняются только в БД, email не уйдёт.

> 📌 **Загрузка `.env`**: приложение автоматически подгружает `.env` через `python-dotenv`
> при старте (см. `flask_app/__init__.py`). Реальные переменные окружения имеют приоритет
> над `.env`, поэтому Replit Secrets ничего не перезатирают. Убедитесь, что `python-dotenv`
> установлен на сервере (`pip install python-dotenv` или `pip install -r requirements.txt`),
> иначе при старте появится предупреждение `[startup] WARNING: python-dotenv не установлен`.

### 4. Запуск через gunicorn

⚠️ **КРИТИЧНО**: gunicorn ВСЕГДА запускайте с флагом `--chdir`, иначе относительные пути к `data/`, `flask_app/static/` и подобные ресурсы не разрешатся:

```bash
gunicorn \
    --chdir /var/www/bioclim-calculator \
    --bind 0.0.0.0:8081 \
    --workers 2 \
    --timeout 120 \
    --reuse-port \
    'flask_app:create_app()'
```

**Почему `--chdir` критичен:**
- `flask_app/services/calculator.py` ищет CSV-цены в `data/price_tables/` — относительный путь
- Шаблоны Jinja2 (`flask_app/templates/`) — относительный путь
- Static-файлы (`flask_app/static/`) — относительный путь
- Без `--chdir` gunicorn запускается из вашего текущего каталога (`pwd`) и эти пути ломаются

> Шрифты PDF (`fonts/DejaVuSans.ttf`) уже разрешаются абсолютно через `__file__`-based `_FONTS_DIR` — это безопасно при любом CWD. Но всё остальное — нет.

### 5. systemd unit (рекомендуется)

`/etc/systemd/system/bioclim.service`:

```ini
[Unit]
Description=Bioclim Pergola Calculator
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/bioclim-calculator
EnvironmentFile=/var/www/bioclim-calculator/.env
ExecStart=/var/www/bioclim-calculator/venv/bin/gunicorn \
    --chdir /var/www/bioclim-calculator \
    --bind 127.0.0.1:8081 \
    --workers 2 \
    --timeout 120 \
    'flask_app:create_app()'
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bioclim
sudo systemctl status bioclim
```

### 6. Диагностика шрифтов PDF

При первом импорте `pdf_generator_fpdf_rus` в логах должно появиться:

```
[pdf_generator] FONTS_DIR: /var/www/bioclim-calculator/fonts
[pdf_generator] Файл существует: True
[pdf_generator] __file__: /var/www/bioclim-calculator/pdf_generator_fpdf_rus.py
```

Если `Файл существует: False` — проверьте, что папка `fonts/` со шрифтами `DejaVuSans.ttf` / `DejaVuSans-Bold.ttf` есть рядом с `pdf_generator_fpdf_rus.py`.

### 7. nginx (reverse-proxy)

```nginx
server {
    listen 80;
    server_name calc.example.ru;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

---

## Использование

1. Выберите размеры перголы (ширина и вынос)
2. Выберите тип перголы и ламелей
3. Выберите опции освещения и автоматики
4. Укажите, нужна ли установка
5. Нажмите «Рассчитать стоимость» → получите КП с возможностью PDF-экспорта

## Встраивание на Tilda

См. `embed_code_for_tilda.html` — готовый iframe с авто-подстройкой высоты через `postMessage`.

## Бэкап CSV-цен

```bash
python3 export_prices.py   # Экспортирует все price_data в data/price_tables/*.csv
```
