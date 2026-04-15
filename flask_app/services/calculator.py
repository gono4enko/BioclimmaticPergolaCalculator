"""
Сервис для расчетов стоимости перголы.
Бизнес-логика полностью синхронизирована с app.py (Streamlit версия).
Все цены в CSV — в евро. Конвертация в рубли происходит на уровне API.
"""
import os
import csv
import math
import logging

logger = logging.getLogger(__name__)


def clear_price_cache():
    _price_cache.clear()
    _variant_price_cache.clear()

PERGOLA_TYPES = {
    "B500NEW": "В500 - с поворотными ламелями",
    "B700NEW": "В700 - с поворотно-сдвижными ламелями",
    "B600": "В600 PIR - со стационарными панелями"
}

PERGOLA_TYPE_DESCRIPTIONS = {
    "B500NEW": "Современная пергола с поворотными алюминиевыми ламелями.",
    "B700NEW": "Премиальная пергола с поворотно-сдвижными ламелями.",
    "B600": "Пергола со стационарной крышей из PIR сэндвич-панелей."
}

LAMELLA_TYPES = {
    "B500-20NEW": "Ламели 200 мм (усиленные)",
    "B500-25NEW": "Ламели 250 мм (стандарт)",
    "B700-20NEW": "Ламели 200 мм (усиленные)",
    "B700-25NEW": "Ламели 250 мм (стандарт)",
    "B600-PIR": "PIR сэндвич-панель",
    "lamella-200": "Ламели 200 мм (усиленные)",
    "lamella-250": "Ламели 250 мм (стандарт)"
}

MAX_DIMENSIONS = {
    "B500NEW_250": {"width": 13.5, "length": 8.0},
    "B500NEW_200": {"width": 15.0, "length": 8.0},
    "B700NEW_250": {"width": 13.5, "length": 8.0},
    "B700NEW_200": {"width": 15.0, "length": 8.0},
    "B600": {"width": 13.5, "length": 8.0}
}

ADDITIONAL_COLUMNS_RULES = {
    "B500NEW": {"250": 6.5, "200": 6.85},
    "B700NEW": {"250": 6.5, "200": 6.85},
    "B600": {"PIR": 6.5}
}

COLUMNS_PRICES = {1: 653, 2: 980, 3: 1306}

GUTTER_INSERT_THRESHOLD = 6.5
GUTTER_INSERT_PRICE_PER_METER = 80

BANSBACH_DRIVE_RULES = {
    1: [
        {"width": 2.5, "length": 8.0, "tandem": False},
        {"width": 3.0, "length": 6.5, "tandem": True},
        {"width": 3.5, "length": 5.5, "tandem": True},
        {"width": 4.0, "length": 5.0, "tandem": True},
        {"width": float('inf'), "length": 5.0, "tandem": True}
    ],
    2: [
        {"width": 5.0, "length": 8.0, "tandem": False},
        {"width": 6.0, "length": 7.5, "tandem": True},
        {"width": 7.0, "length": 6.5, "tandem": True},
        {"width": 8.0, "length": 5.5, "tandem": True},
        {"width": float('inf'), "length": 5.0, "tandem": True}
    ],
    3: [
        {"width": 7.5, "length": 8.0, "tandem": False},
        {"width": 9.0, "length": 7.5, "tandem": True},
        {"width": 10.5, "length": 6.5, "tandem": True},
        {"width": 12.0, "length": 5.5, "tandem": True},
        {"width": float('inf'), "length": 5.0, "tandem": True}
    ]
}

SOMFY_DRIVE_RULES = {
    1: [
        {"width": 3.0, "length": 7.0, "tandem": True},
        {"width": 3.5, "length": 6.0, "tandem": True},
        {"width": float('inf'), "length": float('inf'), "tandem": False}
    ],
    2: [
        {"width": 6.0, "length": 7.0, "tandem": True},
        {"width": 7.0, "length": 6.0, "tandem": True},
        {"width": float('inf'), "length": float('inf'), "tandem": False}
    ],
    3: [
        {"width": 9.0, "length": 7.0, "tandem": True},
        {"width": 10.5, "length": 6.0, "tandem": True},
        {"width": float('inf'), "length": float('inf'), "tandem": False}
    ]
}

DRIVE_PRICES = {
    "B500NEW": {"standard": 700, "tandem": 1250},
    "B700NEW": {"standard": 300, "tandem": 1000}
}

REMOTE_CONTROL_TYPES = {
    1: {"name": "Simu 1K", "price": 25},
    5: {"name": "Simu 5K", "price": 40},
    15: {"name": "Simu 15K", "price": 90}
}

LIGHTING_PRICES = {
    "controller": 300,
    "white_led": 20,
    "rgb_led": 20
}

_price_cache = {}
_variant_price_cache = {}


def _get_plural_form(number, one, two, five):
    n = abs(number) % 100
    if 11 <= n <= 19:
        return five
    n = n % 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return two
    return five


def _load_prices_from_db(pergola_type, lamella_size):
    try:
        import psycopg2
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            return None
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT width, length, price, modules FROM price_data WHERE pergola_type=%s AND lamella_size=%s ORDER BY width, length, modules",
                    (pergola_type, lamella_size)
                )
                rows = cur.fetchall()
        if not rows:
            return None
        prices = {}
        for w, l, p, m in rows:
            wf = float(w)
            lf = float(l)
            pf = float(p)
            if wf not in prices:
                prices[wf] = {}
            expected_mod = get_modules_by_dimensions(lf, None)
            if lf not in prices[wf]:
                prices[wf][lf] = pf
            elif m and int(m) == expected_mod:
                prices[wf][lf] = pf
        return prices
    except Exception as e:
        logger.warning(f"Ошибка загрузки цен из БД: {e}")
        return None


def _load_variant_prices_from_db(pergola_type, lamella_size):
    try:
        import psycopg2
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            return None
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT variant, width, length, price, modules FROM price_data "
                    "WHERE pergola_type=%s AND lamella_size=%s AND variant IS NOT NULL "
                    "ORDER BY variant, modules, width, length",
                    (pergola_type, lamella_size)
                )
                rows = cur.fetchall()
        if not rows:
            return None
        variants = {}
        for variant, w, l, p, m in rows:
            if variant not in variants:
                variants[variant] = {}
            mod = int(m) if m else 1
            if mod not in variants[variant]:
                variants[variant][mod] = {}
            wf = float(w)
            lf = float(l)
            pf = float(p)
            if wf not in variants[variant][mod]:
                variants[variant][mod][wf] = {}
            variants[variant][mod][wf][lf] = pf
        return variants
    except Exception as e:
        logger.warning(f"Ошибка загрузки вариантных цен из БД: {e}")
        return None


def load_variant_prices(pergola_type, lamella_size):
    cache_key = (pergola_type, lamella_size, 'variants')
    if cache_key in _variant_price_cache:
        return _variant_price_cache[cache_key]
    variants = _load_variant_prices_from_db(pergola_type, lamella_size)
    if variants:
        _variant_price_cache[cache_key] = variants
        logger.info(f"Вариантные цены {pergola_type}/{lamella_size}: {list(variants.keys())}")
    return variants


def _find_price_in_variant(variant_data, mod, depth, width):
    if mod not in variant_data:
        return None
    mod_data = variant_data[mod]
    available_depths = sorted(mod_data.keys())
    available_widths = set()
    for d in mod_data.values():
        available_widths.update(d.keys())
    available_widths = sorted(available_widths)

    if not available_depths or not available_widths:
        return None

    depth_match = None
    for d in available_depths:
        if d >= depth - 0.01:
            depth_match = d
            break
    if depth_match is None:
        depth_match = available_depths[-1]

    width_match = None
    for w in available_widths:
        if w >= width - 0.01:
            width_match = w
            break
    if width_match is None:
        width_match = available_widths[-1]

    if depth_match in mod_data and width_match in mod_data[depth_match]:
        return mod_data[depth_match][width_match]
    return None


def _get_valid_module_counts(variant_data, width):
    valid = []
    for mod in [1, 2, 3]:
        if mod not in variant_data:
            continue
        mod_widths = set()
        for depth_data in variant_data[mod].values():
            mod_widths.update(depth_data.keys())
        if not mod_widths:
            continue
        min_w = min(mod_widths)
        max_w = max(mod_widths)
        if width >= min_w - 0.01 and width <= max_w + 0.01:
            valid.append(mod)
    return valid


def get_best_variant_price(pergola_type, lamella_size, width_m, length_m):
    variants = load_variant_prices(pergola_type, lamella_size)
    if not variants:
        return None, None, None

    lookup_depth = length_m
    lookup_width = width_m

    best_price = None
    best_variant = None
    best_modules = None

    for variant_name, variant_data in variants.items():
        valid_mods = _get_valid_module_counts(variant_data, lookup_width)
        for mod in valid_mods:
            price = _find_price_in_variant(variant_data, mod, lookup_depth, lookup_width)
            if price is not None:
                if best_price is None or price < best_price:
                    best_price = price
                    best_variant = variant_name
                    best_modules = mod

    return best_price, best_variant, best_modules


def _load_prices_from_csv(pergola_type, lamella_size):
    file_mapping = {
        ("B500NEW", "200"): ["data/price_tables/Прайс_В500-20.csv", "attached_assets/Price_B500-20.csv", "attached_assets/Прайс_В500-20.csv"],
        ("B500NEW", "250"): ["data/price_tables/Прайс_В500-25.csv", "attached_assets/Price_B500-25.csv", "attached_assets/Прайс_В500-25.csv"],
        ("B700NEW", "200"): ["data/price_tables/Прайс_B700-20.csv", "attached_assets/Price_B700-20.csv", "attached_assets/Прайс_B700-20.csv"],
        ("B700NEW", "250"): ["data/price_tables/Прайс_B700-25.csv", "attached_assets/Price_B700-25.csv", "attached_assets/Прайс_B700-25.csv"],
        ("B600", "PIR"): ["data/price_tables/Прайс_В600_PIR.csv", "attached_assets/Price_B600_PIR.csv", "attached_assets/Прайс_В600_PIR.csv"]
    }

    cache_key = (pergola_type, lamella_size)
    if cache_key not in file_mapping:
        return None

    file_path = None
    for path in file_mapping[cache_key]:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        return None

    prices = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            delimiter = ';' if ';' in first_line else ','
            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)

            first_row = next(reader)
            modules_row = first_row if "модуль" in ' '.join(first_row).lower() else None
            header = next(reader) if modules_row else first_row

            length_values = []
            for val in header[1:]:
                if val.strip():
                    try:
                        length_values.append(float(val.replace(',', '.').strip()))
                    except ValueError:
                        continue

            for row in reader:
                if not row or len(row) <= 1:
                    continue
                try:
                    width = float(row[0].strip().replace(',', '.'))
                    for i, price_str in enumerate(row[1:]):
                        if i < len(length_values) and price_str.strip():
                            length = length_values[i]
                            try:
                                price = float(price_str.replace(' ', '').replace(',', '.'))
                                if width not in prices:
                                    prices[width] = {}
                                prices[width][length] = price
                            except ValueError:
                                continue
                except (ValueError, IndexError):
                    continue

        logger.info(f"Загружено {len(prices)} записей из CSV {file_path}")
        return prices
    except Exception as e:
        logger.error(f"Ошибка загрузки прайса {file_path}: {e}")
        return None


def load_price_data(pergola_type, lamella_size):
    cache_key = (pergola_type, lamella_size)
    if cache_key in _price_cache:
        return _price_cache[cache_key]

    prices = _load_prices_from_db(pergola_type, lamella_size)
    if prices:
        _price_cache[cache_key] = prices
        logger.info(f"Цены {pergola_type}/{lamella_size}: {len(prices)} строк из PostgreSQL")
        return prices

    prices = _load_prices_from_csv(pergola_type, lamella_size)
    if prices:
        _price_cache[cache_key] = prices
        return prices

    logger.error(f"Цены для {pergola_type}/{lamella_size} не найдены ни в БД, ни в CSV")
    return {}


def _get_modules_info_from_db(pergola_type, lamella_size):
    try:
        import psycopg2
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            return None
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT length, modules FROM price_data WHERE pergola_type=%s AND lamella_size=%s AND modules IS NOT NULL ORDER BY length, modules",
                    (pergola_type, lamella_size)
                )
                rows = cur.fetchall()
        if not rows:
            return None
        modules_map = {}
        for length_val, mod in rows:
            lf = round(float(length_val), 2)
            mi = int(mod)
            expected = get_modules_by_dimensions(lf, None)
            if lf not in modules_map:
                modules_map[lf] = mi
            elif mi == expected:
                modules_map[lf] = mi
        return modules_map
    except Exception as e:
        logger.warning(f"Ошибка загрузки модулей из БД: {e}")
        return None


def _get_modules_info_from_csv(pergola_type, lamella_size):
    file_mapping = {
        ("B500NEW", "200"): ["data/price_tables/Прайс_В500-20.csv", "attached_assets/Price_B500-20.csv"],
        ("B500NEW", "250"): ["data/price_tables/Прайс_В500-25.csv", "attached_assets/Price_B500-25.csv"],
        ("B700NEW", "200"): ["data/price_tables/Прайс_B700-20.csv", "attached_assets/Price_B700-20.csv"],
        ("B700NEW", "250"): ["data/price_tables/Прайс_B700-25.csv", "attached_assets/Price_B700-25.csv"],
        ("B600", "PIR"): ["data/price_tables/Прайс_В600_PIR.csv", "attached_assets/Price_B600_PIR.csv"]
    }
    key = (pergola_type, lamella_size)
    if key not in file_mapping:
        return None

    file_path = None
    for path in file_mapping[key]:
        if os.path.exists(path):
            file_path = path
            break
    if not file_path:
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            delimiter = ';' if ';' in first_line else ','
            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)
            first_row = next(reader)
            if "модуль" not in ' '.join(first_row).lower():
                return None
            header = next(reader)
            modules_map = {}
            for i, val in enumerate(header[1:], 1):
                if val.strip():
                    try:
                        w = float(val.replace(',', '.').strip())
                        mod_info = first_row[i] if i < len(first_row) else ""
                        if "1 модуль" in mod_info:
                            modules_map[w] = 1
                        elif "2 модуля" in mod_info:
                            modules_map[w] = 2
                        elif "3 модуля" in mod_info:
                            modules_map[w] = 3
                    except (ValueError, IndexError):
                        continue
            return modules_map
    except Exception:
        return None


def get_modules_info_from_csv(pergola_type, lamella_size):
    result = _get_modules_info_from_db(pergola_type, lamella_size)
    if result:
        return result
    return _get_modules_info_from_csv(pergola_type, lamella_size)


def adjust_length_for_lamella_size(length_m, lamella_size):
    if lamella_size == 'PIR':
        lamella_size_mm = 250
    else:
        lamella_size_mm = int(lamella_size)
    lamella_size_m = lamella_size_mm / 1000
    num_lamellas = math.ceil(length_m / lamella_size_m)
    return round(num_lamellas * lamella_size_m, 2)


def get_modules_by_dimensions(width, length, pergola_type=None):
    if width <= 4.5:
        return 1
    elif width <= 9.0:
        return 2
    else:
        return 3


def get_base_price(pergola_type, lamella_size, width_m, length_m):
    prices = load_price_data(pergola_type, lamella_size)
    if not prices:
        raise ValueError(f"Не удалось загрузить данные о ценах для {pergola_type}/{lamella_size}")

    available_widths = sorted(prices.keys())
    available_lengths = set()
    for wd in prices.values():
        available_lengths.update(wd.keys())
    available_lengths = sorted(available_lengths)

    lookup_width = length_m
    lookup_length = width_m

    if lookup_width in available_widths:
        width_match = lookup_width
    else:
        width_match = next((w for w in available_widths if w > lookup_width), max(available_widths))

    if lookup_length in available_lengths:
        length_match = lookup_length
    else:
        length_match = next((l for l in available_lengths if l > lookup_length), max(available_lengths))

    if width_match in prices and length_match in prices[width_match]:
        return prices[width_match][length_match]

    min_price = None
    for w in available_widths:
        if w >= lookup_width:
            for l in available_lengths:
                if l >= lookup_length:
                    if w in prices and l in prices[w]:
                        p = prices[w][l]
                        if min_price is None or p < min_price:
                            min_price = p

    if min_price is not None:
        return min_price

    raise ValueError(f"Не удалось найти цену для {pergola_type} {width_m}x{length_m}м")


def needs_additional_columns(pergola_type, lamella_size, length_m):
    threshold = ADDITIONAL_COLUMNS_RULES.get(pergola_type, {}).get(lamella_size)
    if threshold is None:
        return False
    return length_m > threshold


def calculate_gutter_insert_price(length_m, modules):
    if length_m <= GUTTER_INSERT_THRESHOLD:
        return False, 0, 0, 0
    gutters_count = modules + 1
    total_length = length_m * gutters_count
    total_price = GUTTER_INSERT_PRICE_PER_METER * total_length
    return True, total_price, gutters_count, total_length


def get_drive_price(pergola_type, width_m, length_m, modules):
    if pergola_type == "B500NEW":
        if abs(width_m - 3.0) < 0.01 and abs(length_m - 8.0) < 0.01:
            return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
        rules = BANSBACH_DRIVE_RULES.get(modules, [])
        for rule in rules:
            if length_m > 6.0:
                return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
            if width_m > rule["width"] and length_m > rule["length"]:
                if rule["tandem"]:
                    return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
                else:
                    return "Bansbach Т1, Germany", DRIVE_PRICES["B500NEW"]["standard"], False
        return "Bansbach Т1, Germany", DRIVE_PRICES["B500NEW"]["standard"], False

    elif pergola_type == "B700NEW":
        rules = SOMFY_DRIVE_RULES.get(modules, [])
        for rule in rules:
            width_check = width_m <= rule["width"] if modules == 1 else width_m > rule["width"]
            if width_check and length_m > rule["length"]:
                if rule["tandem"]:
                    return "Somfy M2 TANDEM", DRIVE_PRICES["B700NEW"]["tandem"], True
                else:
                    return "Somfy M1", DRIVE_PRICES["B700NEW"]["standard"], False
        return "Somfy M1", DRIVE_PRICES["B700NEW"]["standard"], False

    return "", 0, False


def get_remote_control(devices_count):
    if devices_count <= 1:
        return "Simu 1K", REMOTE_CONTROL_TYPES[1]["price"]
    elif devices_count <= 5:
        return "Simu 5K", REMOTE_CONTROL_TYPES[5]["price"]
    else:
        return "Simu 15K", REMOTE_CONTROL_TYPES[15]["price"]


def calculate_lighting_perimeter(width_m, length_m, modules=1):
    if modules <= 1:
        return 2 * (width_m + length_m)
    module_width = width_m / modules
    return modules * 2 * (module_width + length_m)


def perform_calculation(dimensions, options):
    try:
        from config import pricing_settings

        width_m = float(dimensions.get("width", 0))
        length_m = float(dimensions.get("length", 0))
        pergola_type = options.get("pergola_type", "")
        lamella_type = options.get("lamella_type", "")
        lighting_options = options.get("lighting", [])
        installation = options.get("installation", False)

        lamella_size = options.get("lamella_size", "")
        if not lamella_size:
            lamella_size = "PIR" if "PIR" in lamella_type else ("200" if "20" in lamella_type and "200" not in lamella_type else ("200" if "200" in lamella_type else "250"))

        if pergola_type == "B600":
            dim_key = pergola_type
        else:
            dim_key = f"{pergola_type}_{lamella_size}"

        if dim_key in MAX_DIMENSIONS:
            max_w = MAX_DIMENSIONS[dim_key]["width"]
            max_l = MAX_DIMENSIONS[dim_key]["length"]
            if width_m > max_w:
                raise ValueError(f"Ширина ({width_m} м) превышает максимум ({max_w} м)")
            if length_m > max_l:
                raise ValueError(f"Вынос ({length_m} м) превышает максимум ({max_l} м)")

        modules = get_modules_by_dimensions(width_m, length_m, pergola_type)

        if pergola_type in ["B500NEW", "B700NEW"]:
            lamella_size_mm = 200 if lamella_size == "200" else 250
            length_m = adjust_length_for_lamella_size(length_m, lamella_size)
            lamellas_count = int(length_m * 1000 / lamella_size_mm)
        else:
            lamellas_count = 0

        selected_variant = None
        if pergola_type == "B500NEW":
            variant_price, variant_name, variant_modules = get_best_variant_price(
                pergola_type, lamella_size, width_m, length_m
            )
            if variant_price is not None:
                base_price = variant_price
                selected_variant = variant_name
                modules = variant_modules
                logger.info(f"B500 вариант: {variant_name}, модулей: {variant_modules}, цена: {variant_price}€")
            else:
                base_price = get_base_price(pergola_type, lamella_size, width_m, length_m)
        else:
            base_price = get_base_price(pergola_type, lamella_size, width_m, length_m)

        lamella_display = {"200": "200 мм", "250": "250 мм", "PIR": "PIR"}.get(lamella_size, lamella_size)
        variant_suffix = f" {selected_variant}" if selected_variant else ""
        variant_lamella = f" ({selected_variant})" if selected_variant else " (стандарт)"
        if pergola_type in ["B500NEW", "B700NEW"]:
            pergola_name = (f"Пергола серии {pergola_type}{variant_suffix} - с поворотными ламелями "
                           f"{width_m:.2f}×{length_m:.2f} м. Ламели {lamella_display}{variant_lamella}. "
                           f"Количество ламелей - {lamellas_count} шт. ({modules} {_get_plural_form(modules, 'модуль', 'модуля', 'модулей')})")
        else:
            pergola_name = (f"Пергола серии {pergola_type} - PIR панели "
                           f"{width_m:.2f}×{length_m:.2f} м. ({modules} {_get_plural_form(modules, 'модуль', 'модуля', 'модулей')})")

        items = [{"name": pergola_name, "price": base_price}]
        total_price = base_price
        specification = []

        if selected_variant:
            lamella_info = f"Ламели {lamella_display} ({selected_variant})"
        else:
            lamella_info = LAMELLA_TYPES.get(lamella_type, lamella_type)
        pergola_type_display = PERGOLA_TYPES.get(pergola_type, pergola_type)
        if selected_variant:
            pergola_type_display = pergola_type_display.replace("В500", f"В500 {selected_variant}")
        lamellas_text = f", Количество ламелей - {lamellas_count} шт." if lamellas_count > 0 else ""
        specification.append({
            "name": f"Пергола серии {pergola_type_display} {width_m:.2f}×{length_m:.2f} м. {lamella_info}{lamellas_text}",
            "count": f"{modules} {_get_plural_form(modules, 'модуль', 'модуля', 'модулей')}"
        })

        need_columns = needs_additional_columns(pergola_type, lamella_size, length_m)
        if need_columns:
            columns_price = COLUMNS_PRICES.get(modules, 0)
            col_count = modules + 1
            items.append({"name": f"Дополнительные колонны ({col_count} шт.)", "price": columns_price})
            total_price += columns_price
            specification.append({"name": "Дополнительные колонны", "count": f"{col_count} шт."})

        gutter_needed, gutter_price, gutters_count, total_gutter_length = calculate_gutter_insert_price(length_m, modules)
        if gutter_needed:
            items.append({"name": f"Усилитель лотка ({gutters_count} лотка, {total_gutter_length:.2f} м)", "price": gutter_price})
            total_price += gutter_price
            specification.append({
                "name": "Усилитель лотка",
                "count": f"{total_gutter_length:.2f} м ({gutters_count} {_get_plural_form(gutters_count, 'лоток', 'лотка', 'лотков')})"
            })

        devices_count = 0
        if pergola_type in ["B500NEW", "B700NEW"]:
            drive_name, drive_price, is_tandem = get_drive_price(pergola_type, width_m, length_m, modules)
            drive_count = modules
            total_drive_price = drive_price * drive_count
            items.append({
                "name": f"Привод {drive_name} (для {drive_count} {_get_plural_form(drive_count, 'модуль', 'модуля', 'модулей')})",
                "price": total_drive_price
            })
            total_price += total_drive_price
            specification.append({"name": f"Привод {drive_name}", "count": f"{drive_count} шт."})

            devices_count = drive_count
            led_controllers = 0
            if "white_led" in lighting_options:
                led_controllers += 1
            if "rgb_led" in lighting_options:
                led_controllers += 1
            devices_count += led_controllers

            remote_name, remote_price = get_remote_control(devices_count)
            items.append({
                "name": f"Пульт ДУ {remote_name} ({devices_count} {_get_plural_form(devices_count, 'канал', 'канала', 'каналов')})",
                "price": remote_price
            })
            total_price += remote_price
            specification.append({"name": f"Пульт ДУ {remote_name}", "count": "1 шт."})

        has_lighting = "white_led" in lighting_options or "rgb_led" in lighting_options
        if has_lighting:
            lighting_perimeter = calculate_lighting_perimeter(width_m, length_m, modules)
            controllers_count = 0
            if "white_led" in lighting_options:
                controllers_count += 1
            if "rgb_led" in lighting_options:
                controllers_count += 1

            controller_price = LIGHTING_PRICES["controller"] * controllers_count
            items.append({"name": f"Блок управления освещением Somfy RTS Dimmer ({controllers_count} шт.)", "price": controller_price})
            total_price += controller_price
            specification.append({"name": "Блок управления освещением Somfy RTS Dimmer", "count": f"{controllers_count} шт."})

            if "white_led" in lighting_options:
                white_cost = LIGHTING_PRICES["white_led"] * lighting_perimeter
                items.append({"name": f"Светодиодная лента белая ({lighting_perimeter:.2f} м)", "price": white_cost})
                total_price += white_cost
                specification.append({"name": "Светодиодная лента белая", "count": f"{lighting_perimeter:.2f} м"})

            if "rgb_led" in lighting_options:
                rgb_cost = LIGHTING_PRICES["rgb_led"] * lighting_perimeter
                items.append({"name": f"Светодиодная лента RGB ({lighting_perimeter:.2f} м)", "price": rgb_cost})
                total_price += rgb_cost
                specification.append({"name": "Светодиодная лента RGB", "count": f"{lighting_perimeter:.2f} м"})

            if pergola_type == "B600":
                lighting_devices = controllers_count
                remote_name, remote_price = get_remote_control(lighting_devices)
                items.append({
                    "name": f"Пульт ДУ {remote_name} для освещения ({lighting_devices} {_get_plural_form(lighting_devices, 'канал', 'канала', 'каналов')})",
                    "price": remote_price
                })
                total_price += remote_price
                specification.append({
                    "name": f"Пульт ДУ {remote_name} для освещения",
                    "count": f"1 шт. ({lighting_devices} {_get_plural_form(lighting_devices, 'канал', 'канала', 'каналов')})"
                })

        base_total = total_price

        delivery_pct = pricing_settings.get_delivery_markup_percent()
        delivery_price = round(base_total * delivery_pct / 100, 2)
        items.append({"name": "Доставка", "price": delivery_price})
        total_price += delivery_price
        specification.append({"name": "Доставка", "count": "1"})

        installation_price = 0
        if installation:
            install_pct = pricing_settings.get_installation_markup_percent()
            installation_price = round(base_total * install_pct / 100, 2)
            items.append({"name": "Установка", "price": installation_price})
            total_price += installation_price
            specification.append({"name": "Установка", "count": "1"})

        total_price = round(total_price, 2)

        euro_rate = pricing_settings.get_euro_rate()
        total_rub = round(total_price * euro_rate)

        results = {
            "dimensions": {"width": width_m, "length": length_m, "modules": modules},
            "options": {
                "pergola_type": pergola_type,
                "lamella_type": lamella_type,
                "lamella_size": lamella_size,
                "lighting": lighting_options,
                "installation": installation
            },
            "items": items,
            "specification": specification,
            "total_price_eur": total_price,
            "euro_rate": euro_rate,
            "totals": {
                "cash": total_rub,
                "non_cash": round(total_rub / 0.92),
                "with_vat": round(total_rub / 0.85)
            },
            "delivery": {"percentage": delivery_pct, "price": delivery_price},
            "installation": {"selected": installation, "price": installation_price},
            "lamellas_count": lamellas_count,
            "pergola_type_name": PERGOLA_TYPES.get(pergola_type, pergola_type),
            "lamella_type_name": LAMELLA_TYPES.get(lamella_type, lamella_type),
            "selected_variant": selected_variant
        }

        return results

    except Exception as e:
        logger.error(f"Ошибка при расчете: {e}")
        return {"error": str(e)}


def get_pergola_types_list():
    return [
        {"id": "B500NEW", "name": PERGOLA_TYPES["B500NEW"], "description": PERGOLA_TYPE_DESCRIPTIONS["B500NEW"], "image": "b500_rotation.png"},
        {"id": "B700NEW", "name": PERGOLA_TYPES["B700NEW"], "description": PERGOLA_TYPE_DESCRIPTIONS["B700NEW"], "image": "b700_sliding.png"},
        {"id": "B600", "name": PERGOLA_TYPES["B600"], "description": PERGOLA_TYPE_DESCRIPTIONS["B600"], "image": "b600_sandwich.png"}
    ]


def get_lamella_sizes_for_type(pergola_type):
    if pergola_type in ["B500NEW", "B700NEW"]:
        return [
            {"id": "200", "name": "Ламели 200 мм (усиленные)", "lamella_type": f"{pergola_type.replace('NEW','')}-20NEW"},
            {"id": "250", "name": "Ламели 250 мм (стандарт)", "lamella_type": f"{pergola_type.replace('NEW','')}-25NEW"}
        ]
    elif pergola_type == "B600":
        return [
            {"id": "PIR", "name": "PIR сэндвич-панель", "lamella_type": "B600-PIR"}
        ]
    return []


def get_max_dimensions(pergola_type, lamella_size):
    if pergola_type == "B600":
        key = pergola_type
    else:
        key = f"{pergola_type}_{lamella_size}"
    return MAX_DIMENSIONS.get(key, {"width": 13.5, "length": 8.0})
