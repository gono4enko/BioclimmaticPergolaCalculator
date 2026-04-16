"""
Скрипт для загрузки контента с decolife.pro и сохранения в локальные JSON-файлы.
Использование: python scripts/fetch_decolife.py
Если сайт недоступен — сохраняет данные из встроенного fallback.
"""
import os
import re
import json
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECOLIFE_DIR = os.path.join(BASE_DIR, 'flask_app', 'static', 'decolife')

URLS = {
    "b500": "https://decolife.pro/bioklimaticheskie-pergoly/b500/",
    "b700": "https://decolife.pro/bioklimaticheskie-pergoly/b700/",
    "b600": "https://decolife.pro/bioklimaticheskie-pergoly/b600/",
}

FALLBACK_DATA = {
    "b500": {
        "model": "B500 NEW",
        "title": "Биоклиматическая пергола B500 с поворотными ламелями",
        "subtitle": "Алюминиевая пергола с системой поворотных ламелей для максимального комфорта",
        "description": "Модель B500 NEW — это современная биоклиматическая пергола с поворотными алюминиевыми ламелями шириной 250 мм. Система позволяет плавно регулировать угол наклона ламелей от 0° до 135°, обеспечивая оптимальное количество света, тени и вентиляции. В закрытом положении ламели образуют герметичную крышу, защищающую от дождя и снега.",
        "features": [
            {"title": "Поворотные ламели", "text": "Угол поворота 0°–135° для точной регулировки света и тени"},
            {"title": "Интегрированный водоотвод", "text": "Система водоотведения скрыта внутри колонн — без видимых труб"},
            {"title": "Модульная конструкция", "text": "До 3-х модулей для покрытия площади до 15 × 6.5 м"},
            {"title": "Алюминиевый каркас", "text": "Окрашенный порошковым методом алюминий — любой цвет RAL"},
            {"title": "Автоматика", "text": "Управление с пульта ДУ, датчики дождя и ветра"},
            {"title": "LED-подсветка", "text": "Встроенная подсветка белая или RGB для вечернего освещения"}
        ],
        "advantages": [
            "Защита от дождя, снега и ветра",
            "Регулировка инсоляции на 100%",
            "Срок службы более 25 лет",
            "Минимальное обслуживание",
            "Увеличение площади жилого пространства",
            "Повышение стоимости недвижимости"
        ],
        "images": [],
        "warranty": "5 лет на конструкцию, 2 года на автоматику",
        "production": "Производство Decolife (Беларусь)"
    },
    "b700": {
        "model": "B700 NEW",
        "title": "Биоклиматическая пергола B700 с поворотно-сдвижными ламелями",
        "subtitle": "Премиальная пергола с функцией открытого неба — ламели поворачиваются и сдвигаются",
        "description": "Модель B700 NEW — флагманская биоклиматическая пергола с поворотно-сдвижными ламелями. Помимо поворота на 0°–135°, ламели полностью сдвигаются в пакет, открывая до 85% площади крыши для наслаждения открытым небом. Усиленная конструкция и увеличенные пролёты позволяют перекрывать большие площади.",
        "features": [
            {"title": "Поворот + сдвиг", "text": "Ламели поворачиваются и сдвигаются в пакет, открывая до 85% крыши"},
            {"title": "Увеличенные пролёты", "text": "Ширина модуля до 5 м, длина (вынос) до 6.85 м"},
            {"title": "Усиленный каркас", "text": "Колонны 164×164 мм, балка 164×280 мм с интегрированным лотком"},
            {"title": "Модульная система", "text": "До 3-х модулей для максимального покрытия"},
            {"title": "Премиальная автоматика", "text": "Мотор Somfy, датчики дождя и ветра, управление со смартфона"},
            {"title": "Доп. опции", "text": "Остекление, маркизы, отопление, акустическая система"}
        ],
        "advantages": [
            "Эффект «открытого неба» — уникальная функция сдвижных ламелей",
            "Максимальная защита в любую погоду",
            "Подходит для коммерческих объектов (рестораны, отели)",
            "Широкий выбор модификаций (Basic, Light, Pro 250, Pro 200)",
            "Увеличивает полезную площадь объекта круглый год",
            "Премиальный внешний вид и высокая надёжность"
        ],
        "images": [],
        "warranty": "5 лет на конструкцию, 2 года на автоматику",
        "production": "Производство Decolife (Беларусь)"
    },
    "b600": {
        "model": "B600",
        "title": "Пергола B600 со стационарной крышей из PIR сэндвич-панелей",
        "subtitle": "Надёжная всесезонная пергола с теплоизолированной крышей",
        "description": "Модель B600 — пергола со стационарной крышей из PIR сэндвич-панелей толщиной 100 мм. Обеспечивает 100% герметичность и полную теплоизоляцию. Идеальна для регионов с обильными осадками и перепадами температур. Стационарная крыша выдерживает максимальные снеговые нагрузки.",
        "features": [
            {"title": "PIR сэндвич-панели", "text": "Толщина 100 мм, 100% герметичность и теплоизоляция"},
            {"title": "Стационарная крыша", "text": "Максимальная надёжность, снеговая нагрузка до 200 кг/м²"},
            {"title": "Модульная конструкция", "text": "Standard до 15 м, Light до 12 м в ширину"},
            {"title": "Водоотвод", "text": "Интегрированная система отвода воды внутри колонн"},
            {"title": "Доп. опции", "text": "Остекление, LED-подсветка, инфракрасные обогреватели"},
            {"title": "Всесезонность", "text": "Полноценное использование круглый год в любом климате"}
        ],
        "advantages": [
            "100% защита от осадков и ветра",
            "Полная теплоизоляция — комфорт зимой и летом",
            "Идеальна для присоединения к дому как дополнительная комната",
            "Максимальная снеговая нагрузка среди всех моделей",
            "Два варианта: Standard и Light",
            "Долговечность и минимальное обслуживание"
        ],
        "images": [],
        "warranty": "5 лет на конструкцию, 2 года на автоматику",
        "production": "Производство Decolife (Беларусь)"
    }
}

MIN_IMG_SIZE = 200


def _strip_tags(html_str):
    return re.sub(r'<[^>]+>', '', html_str).strip()


def _extract_text_blocks(html, tag='p'):
    return [_strip_tags(m) for m in re.findall(rf'<{tag}[^>]*>(.*?)</{tag}>', html, re.DOTALL) if len(_strip_tags(m)) > 20]


def _extract_h1(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    return _strip_tags(m.group(1)) if m else ''


def _extract_images(html, base_url, max_count=6):
    img_urls = []
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html):
        src = m.group(1)
        if src.startswith('data:'):
            continue
        if not src.startswith('http'):
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                src = f"{parsed.scheme}://{parsed.netloc}{src}"
            else:
                src = base_url.rstrip('/') + '/' + src
        skip_patterns = ['logo', 'icon', 'favicon', 'sprite', 'svg', 'thumb_small']
        if any(pat in src.lower() for pat in skip_patterns):
            continue
        img_urls.append(src)
        if len(img_urls) >= max_count:
            break
    return img_urls


def _download_image(url, save_path):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read()
        if len(data) < 5000:
            return False
        with open(save_path, 'wb') as f:
            f.write(data)
        try:
            from PIL import Image
            img = Image.open(save_path)
            w, h = img.size
            if w < MIN_IMG_SIZE or h < MIN_IMG_SIZE:
                os.remove(save_path)
                return False
        except ImportError:
            pass
        return True
    except Exception as e:
        print(f"    Ошибка загрузки {url}: {e}")
        return False


def _parse_html(html, key, base_url):
    result = dict(FALLBACK_DATA[key])

    h1 = _extract_h1(html)
    if h1:
        result['title'] = h1

    paragraphs = _extract_text_blocks(html, 'p')
    if paragraphs:
        long_paragraphs = [p for p in paragraphs if len(p) > 80]
        if long_paragraphs:
            result['description'] = long_paragraphs[0]

    li_items = [_strip_tags(m) for m in re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL) if len(_strip_tags(m)) > 10]
    if len(li_items) >= 3:
        result['advantages'] = li_items[:8]

    img_urls = _extract_images(html, base_url)
    result['_image_urls'] = img_urls

    return result


def _download_model_images(key, image_urls):
    img_dir = os.path.join(DECOLIFE_DIR, key, 'images')
    os.makedirs(img_dir, exist_ok=True)

    saved = []
    for idx, url in enumerate(image_urls[:6]):
        ext = '.jpg'
        if '.png' in url.lower():
            ext = '.png'
        elif '.webp' in url.lower():
            ext = '.webp'
        fname = f"product_{idx + 1}{ext}"
        fpath = os.path.join(img_dir, fname)
        if _download_image(url, fpath):
            saved.append(fname)
            print(f"    Сохранено: {fname}")
    return saved


def ensure_data_files():
    for folder in ["b500", "b700", "b600"]:
        folder_path = os.path.join(DECOLIFE_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
        data_path = os.path.join(folder_path, "data.json")
        if not os.path.exists(data_path):
            print(f"Создаю fallback {data_path}")
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(FALLBACK_DATA[folder], f, ensure_ascii=False, indent=2)


def fetch_and_parse():
    results = {}
    for key, url in URLS.items():
        print(f"\n  [{key.upper()}] Загрузка {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; PergolaBot/1.0)"})
            resp = urllib.request.urlopen(req, timeout=15)
            html = resp.read().decode("utf-8", errors="replace")
            print(f"  [{key.upper()}] Получено {len(html)} символов")
            parsed = _parse_html(html, key, url)
            image_urls = parsed.pop('_image_urls', [])
            if image_urls:
                print(f"  [{key.upper()}] Найдено {len(image_urls)} изображений, загрузка...")
                saved_images = _download_model_images(key, image_urls)
                parsed['images'] = saved_images
            results[key] = parsed
        except Exception as e:
            print(f"  [{key.upper()}] Ошибка: {e}")
    return results


def main():
    print("=== Decolife Content Fetcher ===")
    ensure_data_files()

    print("\nПопытка загрузки и парсинга с decolife.pro...")
    fetched = fetch_and_parse()

    if not fetched:
        print("Сайт недоступен. Используем локальные данные (fallback).")
        return

    for key, data in fetched.items():
        data_path = os.path.join(DECOLIFE_DIR, key, "data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  [{key.upper()}] Данные сохранены в {data_path}")

    print("\nГотово!")


if __name__ == "__main__":
    main()
