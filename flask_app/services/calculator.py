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
    "B600": "В600 PIR - со стационарными панелями",
    "B200": "В200 MAF AERO FLAT - со стационарными ламелями"
}

PERGOLA_TYPE_DESCRIPTIONS = {
    "B500NEW": "Современная пергола с поворотными алюминиевыми ламелями.",
    "B700NEW": "Премиальная пергола с поворотно-сдвижными ламелями.",
    "B600": "Пергола со стационарной крышей из PIR сэндвич-панелей.",
    "B200": "Пергола со стационарными ламелями AERO/FLAT 200×50 мм. Шаг 20 или 25 см."
}

LAMELLA_TYPES = {
    "B500-20NEW": "Ламели 200 мм (усиленные)",
    "B500-25NEW": "Ламели 250 мм (стандарт)",
    "B700-20NEW": "Ламели 200 мм (усиленные)",
    "B700-25NEW": "Ламели 250 мм (стандарт)",
    "B600-PIR": "PIR сэндвич-панель",
    "B200-20": "Стационарные ламели 200×50 мм, шаг 20 см",
    "B200-25": "Стационарные ламели 200×50 мм, шаг 25 см",
    "B200-20A": "AERO ламели 200×50 мм (аэродинамические, наклонные), шаг 20 см",
    "B200-25A": "AERO ламели 200×50 мм (аэродинамические, наклонные), шаг 25 см",
    "B200-20F": "FLAT ламели 200×50 мм (плоские, римский стиль), шаг 20 см",
    "B200-25F": "FLAT ламели 200×50 мм (плоские, римский стиль), шаг 25 см",
    "lamella-200": "Ламели 200 мм (усиленные)",
    "lamella-250": "Ламели 250 мм (стандарт)"
}

MAX_DIMENSIONS = {
    "B500NEW_250": {"width": 13.5, "length": 8.0},
    "B500NEW_200": {"width": 15.0, "length": 8.0},
    "B700NEW_250": {"width": 13.5, "length": 8.0},
    "B700NEW_200": {"width": 15.0, "length": 8.0},
    "B600": {"width": 15.0, "length": 8.0},
    "B200_20": {"width": 13.5, "length": 12.1},
    "B200_25": {"width": 13.5, "length": 12.1}
}

ADDITIONAL_COLUMNS_RULES = {
    "B500NEW": {"250": 6.5, "200": 6.85},
    "B700NEW": {"250": 6.5, "200": 6.85},
    "B600": {"PIR": 6.5}
    # B200: стоимость уже включена в прайс — см. B200_REINFORCEMENT_RULES
}

# B200 — пороги по выносу (length_m), при которых требуется
# усилитель балки или дополнительная колонна. Стоимость уже учтена
# в табличной цене (выделена в прайсе цветом), поэтому здесь только
# флаги для отображения в спецификации и на эскизе.
B200_REINFORCEMENT_RULES = {
    "20": {"reinforcer": 6.5, "extra_column": 7.7},
    "25": {"reinforcer": 6.6, "extra_column": 7.6},
}


def get_b200_reinforcement(width_m, length_m, lamella_size, modules):
    """Определяет, нужен ли усилитель балки или доп. колонна для B200.
    Возвращает dict: {kind: 'extra_column'|'reinforcer'|None, extra_columns_count: int}.
    Стоимость не добавляется — она уже включена в табличную цену прайса.
    """
    rules = B200_REINFORCEMENT_RULES.get(str(lamella_size))
    if not rules:
        return {"kind": None, "extra_columns_count": 0}
    overhang = float(length_m or 0)
    if overhang > rules["extra_column"] + 0.001:
        return {"kind": "extra_column", "extra_columns_count": 1}
    if int(modules or 1) >= 2 and overhang > rules["reinforcer"] + 0.001:
        return {"kind": "reinforcer", "extra_columns_count": 0}
    return {"kind": None, "extra_columns_count": 0}

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

FACADE_PRICES = {
    "FP-20":     199,
    "FP-PIR":    150,
    "FZ-44-50":   99,
    "FZ-44-70":  124,
    "FZ-44-100": 170,
}

FACADE_NAMES = {
    "FP-20":     "\u0424\u0430\u0441\u0430\u0434\u043d\u044b\u0435 \u043f\u0430\u043d\u0435\u043b\u0438 FP-20",
    "FP-PIR":    "\u0424\u0430\u0441\u0430\u0434\u043d\u044b\u0435 \u043f\u0430\u043d\u0435\u043b\u0438 FP-PIR",
    "FZ-44-50":  "\u0424\u0430\u0441\u0430\u0434\u043d\u044b\u0435 \u0436\u0430\u043b\u044e\u0437\u0438 FZ-44 (\u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 50%)",
    "FZ-44-70":  "\u0424\u0430\u0441\u0430\u0434\u043d\u044b\u0435 \u0436\u0430\u043b\u044e\u0437\u0438 FZ-44 (\u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 70%)",
    "FZ-44-100": "\u0424\u0430\u0441\u0430\u0434\u043d\u044b\u0435 \u0436\u0430\u043b\u044e\u0437\u0438 FZ-44 (\u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 100%)",
}

FACADE_COL_WIDTHS = {
    "Light": 0.150,
    "B200":  0.100,
}
FACADE_BEAM_HEIGHTS = {
    "Light": 0.250,
    "B200":  0.200,
}
FACADE_PERGOLA_HEIGHT = 3.0

FACADE_MAX_PANEL_W = {
    "FZ-44": 2.0,
    "FP-20": 4.0,
    "FP-PIR": 4.0,
}
FACADE_EXTRA_COL_PRICE_PER_M = 200.0


# ---------- S500 sliding panoramic glazing ----------
GLAZING_PD = {
    '3':   {'w': [1.8, 2.4, 3.0, 3.6], 'h': [1.7, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
            'p': [
                [729, 801, 873, 925],  # h=1.7: 925 at w=3.6 confirmed from Decolife source (smaller +52 step vs ~+72 elsewhere is intentional)
                [768, 840, 911, 983],
                [799, 871, 943, 1015],
                [831, 903, 975, 1047],
                [863, 935, 1007, 1079],
                [895, 967, 1039, 1111],
                [926, 998, 1070, 1142]]},
    '4':   {'w': [2.5, 3.0, 3.5, 4.0, 4.5, 5.0], 'h': [1.7, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
            'p': [
                [934, 1002, 1071, 1139, 1207, 1275],
                [981, 1049, 1117, 1185, 1253, 1321],
                [1019, 1087, 1156, 1224, 1292, 1360],
                [1058, 1126, 1194, 1262, 1330, 1399],
                [1096, 1165, 1233, 1301, 1369, 1437],
                [1135, 1203, 1271, 1340, 1408, 1476],
                [1174, 1242, 1310, 1378, 1446, 1514]]},
    '5':   {'w': [3.0, 3.5, 4.0, 4.5, 5.0, 6.0], 'h': [1.7, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
            'p': [
                [1126, 1202, 1278, 1354, 1430, 1581],
                [1181, 1257, 1332, 1408, 1484, 1635],
                [1226, 1302, 1378, 1453, 1529, 1681],
                [1271, 1347, 1423, 1499, 1574, 1726],
                [1317, 1392, 1467, 1544, 1620, 1771],
                [1362, 1438, 1513, 1589, 1665, 1816],
                [1407, 1483, 1559, 1634, 1710, 1832]]},  # h=3.25: 1832 at w=6.0 confirmed from Decolife source (smaller +16 step vs +45 elsewhere is intentional)
    '3+3': {'w': [3.0, 3.6, 4.2, 4.8, 6.0, 7.2], 'h': [1.7, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
            'p': [
                [950, 1002, 1053, 1105, 1208, 1311],
                [1001, 1052, 1104, 1155, 1258, 1361],
                [1043, 1095, 1146, 1198, 1301, 1404],
                [1086, 1137, 1189, 1240, 1343, 1446],
                [1128, 1179, 1231, 1282, 1385, 1488],
                [1170, 1222, 1273, 1325, 1428, 1530],
                [1212, 1264, 1315, 1367, 1470, 1573]]},
    '4+4': {'w': [5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 'h': [1.7, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
            'p': [
                [1837, 2032, 2110, 2247, 2383, 2519],
                [1927, 2122, 2200, 2336, 2473, 2609],
                [2002, 2196, 2275, 2411, 2547, 2684],
                [2076, 2271, 2349, 2486, 2622, 2758],
                [2151, 2346, 2424, 2560, 2697, 2833],
                [2226, 2420, 2499, 2635, 2771, 2908],
                [2301, 2495, 2573, 2710, 2846, 2983]]},
    '5+5': {'w': [6.0, 7.0, 8.0, 9.0, 10.0, 12.0], 'h': [1.7, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
            'p': [
                [2224, 2376, 2527, 2679, 2830, 3134],
                [2330, 2482, 2633, 2785, 2936, 3240],
                [2419, 2570, 2722, 2873, 3025, 3328],
                [2507, 2659, 2810, 2962, 3113, 3416],
                [2595, 2747, 2898, 3050, 3201, 3505],
                [2684, 2835, 2987, 3138, 3290, 3593],
                [2772, 2924, 3075, 3227, 3378, 3681]]},
}

GLAZING_TRANSPARENT_EUR_M2 = 4800
GLAZING_TINTED_EUR_M2 = 5800
GLAZING_INSTALL_EUR_M2 = 3500
GLAZING_MARKUP_PCT = 25
GLAZING_DELIVERY_PCT = 10
GLAZING_PAINT_PCT = 10
GLAZING_PANEL_KG = 30
GLAZING_MAX_KG = 88

GLAZING_COLOR_NAMES = {
    'ral7016': '\u0410\u043d\u0442\u0440\u0430\u0446\u0438\u0442 RAL 7016',
    'ral8028': '\u041a\u043e\u0440\u0438\u0447\u043d\u0435\u0432\u044b\u0439 RAL 8028',
    'ral9016': '\u0411\u0435\u043b\u044b\u0439 RAL 9016',
    'custom':  '\u041e\u043a\u0440\u0430\u0441\u043a\u0430 \u043f\u043e RAL',
}
GLAZING_GLASS_NAMES = {
    'transparent': '\u043f\u0440\u043e\u0437\u0440.',
    'tinted':      '\u0442\u043e\u043d\u0438\u0440.',
}
GLAZING_DIR_NAMES = {
    'right':  '\u0432\u043f\u0440\u0430\u0432\u043e',
    'left':   '\u0432\u043b\u0435\u0432\u043e',
    'center': '\u043e\u0442 \u0446\u0435\u043d\u0442\u0440\u0430',
}
GLAZING_SIDE_NAMES = {
    'front': '\u0444\u0430\u0441\u0430\u0434',
    'back':  '\u0441\u0437\u0430\u0434\u0438',
    'left':  '\u0441\u043b\u0435\u0432\u0430',
    'right': '\u0441\u043f\u0440\u0430\u0432\u0430',
}


def _glaze_ci(arr, v):
    """Return index of value in arr closest to v."""
    if not arr:
        return 0
    best = 0
    bd = abs(arr[0] - v)
    for i in range(1, len(arr)):
        d = abs(arr[i] - v)
        if d < bd:
            bd = d
            best = i
    return best


def _glaze_ceil(arr, v):
    """Return index of the smallest value in arr that is >= v.
    Used for pricing where the customer should always be billed for the
    next available size up. Falls back to the last index when v exceeds
    the table's maximum (matrix bound is enforced upstream)."""
    if not arr:
        return 0
    for i, a in enumerate(arr):
        if a + 1e-9 >= v:
            return i
    return len(arr) - 1


def glazing_min_panels(w, h):
    """Min panel count for a sash given opening size."""
    try:
        w = float(w); h = float(h)
    except Exception:
        return 2
    if w <= 0 or h <= 0:
        return 2
    min_by_weight = math.ceil(w * h * GLAZING_PANEL_KG / GLAZING_MAX_KG)
    min_by_width = 2
    if w > 3.6:  min_by_width = 4
    if w > 5.0:  min_by_width = 5
    if w > 6.0:  min_by_width = 6
    if w > 7.0:  min_by_width = 8
    if w > 10.0: min_by_width = 10
    return max(min_by_width, int(min_by_weight))


def glazing_calc_price(w, h, pc, direction='right', color='ral7016', glass='transparent', euro_rate=100.0):
    """Return per-opening glazing price in EUR (incl. paint, glass, delivery, install).
    Mirrors S500 standalone calculator pricing."""
    try:
        w = float(w); h = float(h); pc = int(pc)
    except Exception:
        return 0.0
    if w <= 0 or h <= 0 or pc <= 0:
        return 0.0
    conf = str(pc); dir_ = direction or 'right'
    if pc == 2:
        conf = '3'
    elif pc == 6:
        conf = '3+3'; dir_ = 'center'
    elif pc == 8:
        conf = '4+4'; dir_ = 'center'
    elif pc == 10:
        conf = '5+5'; dir_ = 'center'
    elif w >= 6.0:
        conf = conf if pc <= 5 else '3+3'
        dir_ = 'center'
    elif dir_ == 'center':
        conf = conf if pc <= 5 else '3+3'
    cd = GLAZING_PD.get(conf)
    if not cd:
        return 0.0
    comp = cd['p'][_glaze_ci(cd['h'], h)][_glaze_ci(cd['w'], w)]
    if color == 'custom':
        comp *= (1 + GLAZING_PAINT_PCT / 100.0)
    area = w * h
    glass_eur = GLAZING_TINTED_EUR_M2 if glass == 'tinted' else GLAZING_TRANSPARENT_EUR_M2
    rate = euro_rate if euro_rate and euro_rate > 0 else 100.0
    glass_part = area * glass_eur * (1 + GLAZING_MARKUP_PCT / 100.0) / rate  # ₽ → €
    install_part = area * GLAZING_INSTALL_EUR_M2 * (1 + GLAZING_MARKUP_PCT / 100.0) / rate
    deliv_part = comp * (GLAZING_DELIVERY_PCT / 100.0) * (1 + GLAZING_MARKUP_PCT / 100.0)
    # ₽-priced components (glass, install) are converted to € using current pricing_settings rate.
    # Comp price is already in EUR (taken straight from PD table).
    return comp + glass_part + deliv_part + install_part


# ---------- S100 frameless sliding glazing ----------
S100_PD = {
    '3':   {'w': [1.8, 2.4, 3.0, 3.6], 'h': [1.5, 2.0, 2.5, 3.0],
            'p': [
                [740, 847, 953, 1060],
                [814, 943, 1073, 1202],
                [888, 1040, 1192, 1344],
                [962, 1136, 1311, 1485]]},
    '4':   {'w': [2.0, 2.5, 3.0, 3.5, 4.0], 'h': [1.5, 2.0, 2.5, 3.0],
            'p': [
                [887, 981, 1075, 1169, 1263],
                [972, 1085, 1197, 1310, 1423],
                [1057, 1188, 1320, 1451, 1583],
                [1142, 1292, 1442, 1592, 1743]]},
    '6':   {'w': [3.0, 4.0, 4.5, 5.0, 6.0], 'h': [1.5, 2.0, 2.5, 3.0],
            'p': [
                [1427, 1533, 1639, 1745, 1957],
                [1573, 1698, 1822, 1947, 2196],
                [1719, 1862, 2006, 2149, 2436],
                [1864, 2027, 2189, 2351, 2676]]},
    '3+3': {'w': [3.0, 3.6, 4.2, 4.8, 6.0], 'h': [1.5, 2.0, 2.5, 3.0],
            'p': [
                [1272, 1380, 1488, 1596, 1812],
                [1401, 1532, 1662, 1793, 2053],
                [1530, 1683, 1836, 1989, 2295],
                [1660, 1835, 2010, 2189, 2536]]},
    '4+4': {'w': [4.0, 5.0, 6.0, 7.0, 8.0], 'h': [1.5, 2.0, 2.5, 3.0],
            'p': [
                [1740, 1938, 2136, 2334, 2532],
                [1913, 2148, 2384, 2619, 2855],
                [2085, 2358, 2631, 2904, 3177],
                [2258, 2569, 2879, 3189, 3500]]},
    '6+6': {'w': [7.0, 8.0, 9.0, 10.0, 12.0], 'h': [1.5, 2.0, 2.5, 3.0],
            'p': [
                [2803, 3018, 3234, 3449, 3879],
                [3097, 3352, 3603, 3856, 4361],
                [3392, 3682, 3972, 4263, 4843],
                [3686, 4014, 4342, 4669, 5325]]},
}

S100_RAL_SPECIAL_PCT = 10
S100_TINTED_SURCHARGE_EUR_M2 = (GLAZING_TINTED_EUR_M2 - GLAZING_TRANSPARENT_EUR_M2)  # 1000 ₽/м²
S100_PC_ALLOWED = (3, 4, 6, 8, 12)
S100_MIN_W = 1.8
S100_MAX_W = 12.0
S100_MIN_H = 1.5
S100_MAX_H = 3.0

S100_COLOR_NAMES = {
    'ral9t08':     'Графит текстурный RAL 9T08',
    'ral7024':     'Графит матовый RAL 7024',
    'ral8028':     'Коричневый Муар RAL 8028',
    'ral9016':     'Белый матовый RAL 9016',
    'ral_special': 'RAL special (+10%)',
}
S100_GLASS_NAMES = {
    'transparent': '\u043f\u0440\u043e\u0437\u0440.',
    'tinted_mass': '\u0442\u043e\u043d\u0438\u0440. \u0432 \u043c\u0430\u0441\u0441\u0435',
}


def s100_min_panels(w, h):
    """Min panel count for an S100 sash given opening width."""
    try:
        w = float(w); h = float(h)
    except Exception:
        return 3
    if w <= 0 or h <= 0:
        return 3
    if w > 8.0:  return 12
    if w > 6.0:  return 8
    if w > 4.0:  return 6
    if w > 3.6:  return 4
    return 3


def _s100_conf(pc, direction, w):
    """Map (pc, direction) to S100_PD config key."""
    pc = int(pc)
    dir_ = direction or 'right'
    if pc == 3:    return '3', dir_
    if pc == 4:    return '4', dir_
    if pc == 6:
        if dir_ == 'center':
            return '3+3', 'center'
        return '6', dir_
    if pc == 8:    return '4+4', 'center'
    if pc == 12:   return '6+6', 'center'
    # Fallback: pick smallest config that fits
    if pc <= 6:    return '6', dir_
    if pc <= 8:    return '4+4', 'center'
    return '6+6', 'center'


def s100_calc_price(w, h, pc, direction='right', color='ral9t08', glass='transparent', euro_rate=100.0):
    """Per-opening S100 price in EUR. Closest-cell lookup of S100_PD,
    +10% for ral_special, plus tinted glass surcharge per m²."""
    try:
        w = float(w); h = float(h); pc = int(pc)
    except Exception:
        return 0.0
    if w <= 0 or h <= 0 or pc <= 0:
        return 0.0
    conf, _dir = _s100_conf(pc, direction, w)
    cd = S100_PD.get(conf)
    if not cd:
        return 0.0
    comp = cd['p'][_glaze_ci(cd['h'], h)][_glaze_ci(cd['w'], w)]
    if color == 'ral_special':
        comp *= (1 + S100_RAL_SPECIAL_PCT / 100.0)
    if glass == 'tinted_mass':
        rate = euro_rate if euro_rate and euro_rate > 0 else 100.0
        area = w * h
        comp += area * S100_TINTED_SURCHARGE_EUR_M2 * (1 + GLAZING_MARKUP_PCT / 100.0) / rate
    return comp


# ---------- W500 / W600 / W700 lifting (guillotine) glazing ----------
# Price matrices: rows = heights (m), cols = widths (m), values = EUR per window.
# Approximate baseline pricing derived from the manufacturer spec sheets;
# admin can adjust later via Task #64.

def _w_grid(w_axis, h_axis, base_per_m2, frame_per_m):
    """Build a price grid where price = base_per_m2*w*h + frame_per_m*(w+h)*2."""
    grid = []
    for h in h_axis:
        row = []
        for w in w_axis:
            p = round(base_per_m2 * w * h + frame_per_m * (w + h) * 2.0)
            row.append(p)
        grid.append(row)
    return grid


W500_PD = {
    'w': [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
    'h': [1.5, 2.0, 2.5, 3.0, 3.5],
    'p': _w_grid([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                 [1.5, 2.0, 2.5, 3.0, 3.5], 480, 55),
}
W600_PD = {
    'w': [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
    'h': [2.0, 2.5, 3.0, 3.5, 4.0],
    'p': _w_grid([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                 [2.0, 2.5, 3.0, 3.5, 4.0], 620, 70),
}
W700_PD = {
    'w': [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
    'h': [2.0, 2.5, 3.0, 3.5, 4.0],
    'p': _w_grid([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                 [2.0, 2.5, 3.0, 3.5, 4.0], 760, 80),
}

W_SERIES_NAMES = {
    'W500': 'W500 — гильотинное остекление (стеклопакет 20 мм / стекло 10 мм)',
    'W600': 'W600 — гильотинное остекление (стеклопакет 28 мм)',
    'W700': 'W700 — гильотинное остекление с терморазрывом (стеклопакет 28 мм)',
}
W_BOUNDS = {
    'W500': {'w_min': 1.0, 'w_max': 5.0, 'h_min': 1.5, 'h_max': 3.5},
    'W600': {'w_min': 2.0, 'w_max': 5.0, 'h_min': 2.0, 'h_max': 4.0},
    'W700': {'w_min': 2.0, 'w_max': 5.0, 'h_min': 2.0, 'h_max': 4.0},
}
W_COLOR_NAMES = {
    'ral9t08':     'Графит текстурный RAL 9T08',
    'ral7024':     'Графит матовый RAL 7024',
    'ral8028':     'Коричневый Муар RAL 8028',
    'ral9016':     'Белый матовый RAL 9016',
    'ral_special': 'RAL special (+10%)',
}
W_GLASS_NAMES = {
    'transparent':     'Прозрачное',
    'multifunctional': 'Мультифункциональное (+10%)',
}
W_RAL_SPECIAL_PCT = 10
W_MULTIFUNCTIONAL_PCT = 10
W_PLAVNIK_RATE = {  # €/пог.м (пара плавников)
    'W500': 80,
    'W600': 100,
    'W700': 100,
}
W_PLAVNIK_TRIGGER_W = 3.0


def _w_pd(series):
    s = (series or '').upper()
    if s == 'W500': return W500_PD
    if s == 'W600': return W600_PD
    if s == 'W700': return W700_PD
    return None


def w_min_sashes(width_m):
    """Guillotine windows: 2 sashes by default, 3 when wider than 3.6m."""
    try:
        w = float(width_m)
    except Exception:
        return 2
    return 3 if w > 3.6 else 2


def w_calc_price(series, w, h, color='ral9t08', glass='transparent',
                 plavnik=None, euro_rate=100.0):
    """Per-window price in EUR for W500/W600/W700 guillotine glazing."""
    try:
        w = float(w); h = float(h)
    except Exception:
        return 0.0
    if w <= 0 or h <= 0:
        return 0.0
    pd = _w_pd(series)
    if not pd:
        return 0.0
    s = series.upper()
    b = W_BOUNDS[s]
    w_c = max(b['w_min'], min(b['w_max'], w))
    h_c = max(b['h_min'], min(b['h_max'], h))
    # W series uses ceiling lookup so non-grid sizes round up to the next
    # available billable bin (customer is never undercharged).
    comp = pd['p'][_glaze_ceil(pd['h'], h_c)][_glaze_ceil(pd['w'], w_c)]
    if color == 'ral_special':
        comp *= (1 + W_RAL_SPECIAL_PCT / 100.0)
    if glass == 'multifunctional':
        comp *= (1 + W_MULTIFUNCTIONAL_PCT / 100.0)
    # Auto-on плавник when wider than trigger
    if plavnik is None:
        plavnik = (w > W_PLAVNIK_TRIGGER_W)
    if plavnik:
        comp += W_PLAVNIK_RATE.get(s, 0) * w
    return round(comp, 2)


# ---- Guillotine drive selection ----
# Approximate required torque (Нм) ≈ weight × drum radius. Conservatively
# we use weight ≈ w*h*30 kg (double-glaze sash) × 0.03 m drum + safety margin.

def _w_required_torque(w, h):
    try:
        w = float(w); h = float(h)
    except Exception:
        return 0.0
    return round(w * h * 7.5 + 4.0, 1)


W_DRIVES_SIMU = [
    {'name': 'Simu RTS T6 80/12', 'torque': 80, 'price': 280, 'tandem': False},
    {'name': 'Simu RTS T6 120/12', 'torque': 120, 'price': 380, 'tandem': False},
    {'name': 'Simu RTS T6 TANDEM', 'torque': 240, 'price': 760, 'tandem': True},
]
W_DRIVES_SOMFY = [
    {'name': 'Somfy Altus 60 RTS 85/17', 'torque': 85, 'price': 310, 'tandem': False},
    {'name': 'Somfy Altus 60 RTS 120/12', 'torque': 120, 'price': 410, 'tandem': False},
    {'name': 'Somfy Altus 60 RTS TANDEM', 'torque': 240, 'price': 820, 'tandem': True},
]


def pick_guillotine_drive(w, h, brand='simu', force_tandem=False):
    """Return (drive_name, price_eur, is_tandem, required_torque_nm)."""
    req = _w_required_torque(w, h)
    catalog = W_DRIVES_SOMFY if (brand or 'simu').lower() == 'somfy' else W_DRIVES_SIMU
    if force_tandem:
        d = catalog[-1]
        return d['name'], d['price'], True, req
    for d in catalog:
        if d['torque'] >= req:
            return d['name'], d['price'], d['tandem'], req
    d = catalog[-1]
    return d['name'], d['price'], True, req


def _facade_extra_cols(full_bay_w, col_w, max_panel_w):
    """Compute number of extra support columns and resulting section width.
    Returns (n_extra, section_width_m).
    Formula: section_w = (full_bay_w - (n_extra+2)*col_w) / (n_extra+1)
    """
    n_extra = 0
    while n_extra < 50:
        n_sections = n_extra + 1
        n_cols = n_extra + 2
        usable = full_bay_w - n_cols * col_w
        if usable <= 0:
            break
        section_w = usable / n_sections
        if section_w <= max_panel_w:
            break
        n_extra += 1
    n_sections = n_extra + 1
    usable = max(0.01, full_bay_w - (n_extra + 2) * col_w)
    section_w = max(0.01, usable / n_sections)
    return n_extra, section_w

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


def get_best_variant_price(pergola_type, lamella_size, width_m, length_m, requested_variant=None):
    variants = load_variant_prices(pergola_type, lamella_size)
    if not variants:
        return None, None, None

    lookup_depth = length_m
    lookup_width = width_m

    if requested_variant and requested_variant in variants:
        variant_data = variants[requested_variant]
        valid_mods = _get_valid_module_counts(variant_data, lookup_width)
        for mod in valid_mods:
            price = _find_price_in_variant(variant_data, mod, lookup_depth, lookup_width)
            if price is not None:
                return price, requested_variant, mod
        return None, None, None

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


def get_modules_by_dimensions(width, length, pergola_type=None, max_module_width=None):
    mw = max_module_width if max_module_width else 4.5
    return max(1, math.ceil(width / mw))


def get_length_modules(length, max_overhang=None):
    if not max_overhang or length <= max_overhang + 0.001:
        return 1
    return max(2, math.ceil(length / max_overhang))


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
        height_m = float(dimensions.get("height", 3.0))
        pergola_type = options.get("pergola_type", "")
        lamella_type = options.get("lamella_type", "")
        lighting_options = options.get("lighting", [])
        installation = options.get("installation", False)

        lamella_size = options.get("lamella_size", "")
        if not lamella_size:
            if pergola_type == "B200":
                lamella_size = "20"
            else:
                lamella_size = "PIR" if "PIR" in lamella_type else ("200" if "20" in lamella_type and "200" not in lamella_type else ("200" if "200" in lamella_type else "250"))

        if pergola_type == "B600":
            dim_key = pergola_type
        elif pergola_type == "B200":
            dim_key = f"B200_{lamella_size}"
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
        elif pergola_type == "B200":
            # B200: шаг 20 см → питч 400 мм, шаг 25 см → питч 500 мм
            lamella_pitch_mm = 400 if lamella_size == "20" else 500
            lamellas_count = int(length_m * 1000 / lamella_pitch_mm)
        else:
            lamellas_count = 0

        requested_variant = options.get('selected_variant', '')
        selected_variant = None
        variant_price, variant_name, variant_modules = get_best_variant_price(
            pergola_type, lamella_size, width_m, length_m, requested_variant=requested_variant or None
        )
        if variant_price is not None:
            base_price = variant_price
            selected_variant = variant_name
            modules = variant_modules
            logger.info(f"{pergola_type} вариант: {variant_name}, модулей: {variant_modules}, цена: {variant_price}€")
        elif pergola_type == "B200" and requested_variant and requested_variant not in ("auto", "all"):
            # B200 цены хранятся по lamella_size, не по варианту — запоминаем имя варианта
            base_price = get_base_price(pergola_type, lamella_size, width_m, length_m)
            selected_variant = requested_variant
        else:
            base_price = get_base_price(pergola_type, lamella_size, width_m, length_m)

        lamella_display = {"200": "200 мм", "250": "250 мм", "PIR": "PIR",
                           "20": "шаг 20 см", "25": "шаг 25 см"}.get(lamella_size, lamella_size)
        variant_suffix = f" {selected_variant}" if selected_variant else ""
        variant_lamella = f" ({selected_variant})" if selected_variant else " (стандарт)"
        if pergola_type in ["B500NEW", "B700NEW"]:
            lamella_motion = "поворотно-сдвижными" if pergola_type == "B700NEW" else "поворотными"
            pergola_name = (f"Пергола серии {pergola_type}{variant_suffix} - с {lamella_motion} ламелями "
                           f"{width_m:.2f}×{length_m:.2f} м. Ламели {lamella_display}{variant_lamella}. "
                           f"Количество ламелей - {lamellas_count} шт. ({modules} {_get_plural_form(modules, 'модуль', 'модуля', 'модулей')})")
        elif pergola_type == "B200":
            variant_flat = f" {selected_variant}" if selected_variant else ""
            pergola_name = (f"Пергола серии B200 MAF AERO FLAT{variant_flat} - стационарные ламели 200×50 мм "
                           f"{width_m:.2f}×{length_m:.2f} м. {lamella_display.capitalize()}. "
                           f"Количество ламелей - {lamellas_count} шт. ({modules} {_get_plural_form(modules, 'модуль', 'модуля', 'модулей')})")
        else:
            variant_pir = f" {selected_variant}" if selected_variant else ""
            pergola_name = (f"Пергола серии {pergola_type}{variant_pir} - PIR панели "
                           f"{width_m:.2f}×{length_m:.2f} м. ({modules} {_get_plural_form(modules, 'модуль', 'модуля', 'модулей')})")

        items = [{"name": pergola_name, "price": base_price}]
        total_price = base_price
        specification = []

        if pergola_type == "B200":
            lamella_info = f"Стационарные ламели 200×50 мм, {lamella_display}"
            if selected_variant:
                lamella_info += f" ({selected_variant})"
        elif selected_variant:
            lamella_info = f"Ламели {lamella_display} ({selected_variant})"
        else:
            lamella_info = LAMELLA_TYPES.get(lamella_type, lamella_type)
        pergola_type_display = PERGOLA_TYPES.get(pergola_type, pergola_type)
        if selected_variant:
            pergola_type_display = pergola_type_display.replace("В500", f"В500 {selected_variant}")
            pergola_type_display = pergola_type_display.replace("В700", f"В700 {selected_variant}")
            pergola_type_display = pergola_type_display.replace("В600 PIR", f"В600 PIR {selected_variant}")
            pergola_type_display = pergola_type_display.replace("В200 MAF AERO FLAT", f"В200 MAF AERO FLAT {selected_variant}")
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

        # B200: усилитель балки / доп. колонна (стоимость уже в цене прайса)
        b200_reinf = {"kind": None, "extra_columns_count": 0}
        if pergola_type == "B200":
            b200_reinf = get_b200_reinforcement(width_m, length_m, lamella_size, modules)
            if b200_reinf["kind"] == "extra_column":
                col_count = modules + 1
                specification.append({
                    "name": "Дополнительная колонна (включена в цену)",
                    "count": f"{col_count} шт. (промежуточный ряд)"
                })
            elif b200_reinf["kind"] == "reinforcer":
                specification.append({
                    "name": "Усилитель несущей балки (включён в цену)",
                    "count": f"{modules} шт."
                })

        # Усилитель лотка — только для B500/B700 (B200 и B600 не используют)
        if pergola_type in ["B500NEW", "B700NEW"]:
            gutter_needed, gutter_price, gutters_count, total_gutter_length = calculate_gutter_insert_price(length_m, modules)
            if gutter_needed:
                items.append({"name": f"Усилитель лотка ({gutters_count} лотка, {total_gutter_length:.2f} м)", "price": gutter_price})
                total_price += gutter_price
                specification.append({
                    "name": "Усилитель лотка",
                    "count": f"{total_gutter_length:.2f} м ({gutters_count} {_get_plural_form(gutters_count, 'лоток', 'лотка', 'лотков')})"
                })

        # Pre-count W-series guillotine windows (each adds +1 channel to the remote).
        # Mirror the validation that perform_calculation runs later: drop entries that
        # are out-of-bounds, on a side already taken by a facade panel, or that name
        # an unknown side. This keeps the remote pult sized to what is actually billed.
        _glz_ops_pre = options.get("glazing_openings", []) or []
        _facade_openings_pre = options.get("facade_openings", []) or []
        _facade_keys_pre = set()
        for _fop in _facade_openings_pre:
            if isinstance(_fop, dict) and _fop.get("side") and _fop.get("type"):
                _facade_keys_pre.add((_fop.get("side"), int(_fop.get("bay", 0))))
        try:
            _col_w_pre = (0.150 if selected_variant == "Light"
                          else (0.100 if pergola_type == "B200" else 0.164))
            _beam_h_pre = (0.250 if selected_variant == "Light"
                           else (0.200 if pergola_type == "B200" else 0.280))
            _open_h_pre = max(0.1, height_m - _beam_h_pre)
            _side_max_bay_pre = {"front": 0, "back": 0, "left": 0, "right": 0}
            for _op in (_glz_ops_pre + _facade_openings_pre):
                if not isinstance(_op, dict):
                    continue
                _s = _op.get("side", "")
                if _s in _side_max_bay_pre:
                    _side_max_bay_pre[_s] = max(_side_max_bay_pre[_s], int(_op.get("bay", 0)))
            _length_modules_pre = max(_side_max_bay_pre["left"], _side_max_bay_pre["right"]) + 1
            _full_fb_bay_w_pre = width_m / max(1, modules)
            _full_lr_bay_w_pre = length_m / max(1, _length_modules_pre)
        except Exception:
            _col_w_pre, _open_h_pre = 0.164, max(0.1, height_m - 0.28)
            _full_fb_bay_w_pre = width_m / max(1, modules)
            _full_lr_bay_w_pre = length_m
        w_window_count = 0
        for _gop in _glz_ops_pre:
            if not isinstance(_gop, dict):
                continue
            _ser = (_gop.get("series") or "").upper()
            if _ser not in ("W500", "W600", "W700"):
                continue
            _side = _gop.get("side", "")
            if _side not in ("front", "back", "left", "right"):
                continue
            _bay = int(_gop.get("bay", 0) or 0)
            if (_side, _bay) in _facade_keys_pre:
                continue
            _full_bay = _full_fb_bay_w_pre if _side in ("front", "back") else _full_lr_bay_w_pre
            _op_w = max(0.1, _full_bay - 2 * _col_w_pre)
            _op_h = _open_h_pre
            _bnd = W_BOUNDS.get(_ser)
            if not _bnd or _op_w < _bnd['w_min'] or _op_h < _bnd['h_min'] \
                    or _op_w > _bnd['w_max'] or _op_h > _bnd['h_max']:
                continue
            w_window_count += max(1, int(_gop.get("count", 1) or 1))

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
            devices_count += w_window_count

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

            if pergola_type in ["B600", "B200"]:
                lighting_devices = controllers_count + w_window_count
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

        facade_type = options.get("facade_type", "")
        facade_openings = options.get("facade_openings", [])
        facade_area = 0.0
        facade_price_eur = 0.0
        extra_cols_f = 0
        extra_cols_b = 0
        extra_cols_a = 0
        extra_cols_c = 0
        total_extra_cols = 0

        if facade_openings:
            sv = selected_variant or ""
            if "Light" in sv:
                col_w = FACADE_COL_WIDTHS["Light"]
                beam_h = FACADE_BEAM_HEIGHTS["Light"]
            elif pergola_type == "B200":
                col_w = FACADE_COL_WIDTHS["B200"]
                beam_h = FACADE_BEAM_HEIGHTS["B200"]
            else:
                col_w = 0.164
                beam_h = 0.280
            open_h = max(0.1, height_m - beam_h)
            side_labels = {"front": "\u0441\u043f\u0435\u0440\u0435\u0434\u0438",
                           "back": "\u0441\u0437\u0430\u0434\u0438",
                           "left": "\u0441\u043b\u0435\u0432\u0430",
                           "right": "\u0441\u043f\u0440\u0430\u0432\u0430"}
            side_max_bay = {"left": 0, "right": 0}
            for _op in facade_openings:
                if not isinstance(_op, dict):
                    continue
                _s = _op.get("side", "")
                if _s in side_max_bay:
                    side_max_bay[_s] = max(side_max_bay[_s], int(_op.get("bay", 0)))
            length_modules = max(side_max_bay["left"], side_max_bay["right"]) + 1

            full_front_back_bay_w = width_m / max(1, modules)
            full_side_bay_w = length_m / max(1, length_modules)

            type_groups = {}
            extra_cols_by_key = {}

            for opening in facade_openings:
                if not isinstance(opening, dict):
                    continue
                o_type = opening.get("type") or facade_type
                if not o_type or o_type not in FACADE_PRICES:
                    continue
                side = opening.get("side", "")
                if side not in ("front", "back", "left", "right"):
                    continue

                product_family = "FZ-44" if o_type.startswith("FZ-44") else o_type
                max_panel_w = FACADE_MAX_PANEL_W.get(product_family, 4.0)

                if side in ("front", "back"):
                    full_bay_w = full_front_back_bay_w
                else:
                    full_bay_w = full_side_bay_w

                n_extra, section_w = _facade_extra_cols(full_bay_w, col_w, max_panel_w)
                n_sections = n_extra + 1
                opening_area = section_w * n_sections * open_h

                key = (side, opening.get("bay", 0))
                extra_cols_by_key[key] = n_extra

                if o_type not in type_groups:
                    type_groups[o_type] = {"area": 0.0, "sides": {}}
                type_groups[o_type]["area"] += opening_area
                type_groups[o_type]["sides"][side] = type_groups[o_type]["sides"].get(side, 0) + 1

            for (side, _bay), n_extra in extra_cols_by_key.items():
                if side == "front":
                    extra_cols_f = max(extra_cols_f, n_extra)
                elif side == "back":
                    extra_cols_b = max(extra_cols_b, n_extra)
                elif side == "left":
                    extra_cols_a = max(extra_cols_a, n_extra)
                elif side == "right":
                    extra_cols_c = max(extra_cols_c, n_extra)
                total_extra_cols += n_extra

            for o_type, grp in type_groups.items():
                g_area = round(grp["area"], 2)
                g_price = round(g_area * FACADE_PRICES[o_type], 2)
                facade_area += g_area
                facade_price_eur += g_price
                total_price += g_price
                parts = []
                for s in ("front", "back", "left", "right"):
                    if s in grp["sides"]:
                        cnt = grp["sides"][s]
                        parts.append(f"{side_labels[s]} \u00d7{cnt}" if cnt > 1 else side_labels[s])
                sides_str = ", ".join(parts)
                n_open = sum(grp["sides"].values())
                facade_name = FACADE_NAMES[o_type]
                items.append({
                    "name": f"{facade_name} ({sides_str}, {n_open} \u043f\u0440\u043e\u0451\u043c\u0430, {g_area:.2f} \u043c\u00b2)",
                    "price": g_price
                })
                specification.append({
                    "name": facade_name,
                    "count": f"{n_open} \u043f\u0440\u043e\u0451\u043c\u0430, {g_area:.2f} \u043c\u00b2"
                })

            if total_extra_cols > 0:
                extra_col_unit = round(FACADE_EXTRA_COL_PRICE_PER_M * height_m, 2)
                extra_col_total_price = round(extra_col_unit * total_extra_cols, 2)
                total_price += extra_col_total_price
                items.append({
                    "name": (f"\u0414\u043e\u043f. \u043a\u043e\u043b\u043e\u043d\u043d\u0430 \u0434\u043b\u044f "
                             f"\u0444\u0430\u0441\u0430\u0434\u043d\u044b\u0445 \u043f\u0430\u043d\u0435\u043b\u0435\u0439 "
                             f"({total_extra_cols} \u0448\u0442.)"),
                    "price": extra_col_total_price
                })
                specification.append({
                    "name": "\u0414\u043e\u043f. \u043a\u043e\u043b\u043e\u043d\u043d\u0430 \u0444\u0430\u0441\u0430\u0434\u043d\u044b\u0445 \u043f\u0430\u043d\u0435\u043b\u0435\u0439",
                    "count": f"{total_extra_cols} \u0448\u0442."
                })
            else:
                extra_col_total_price = 0

            facade_area = round(facade_area, 2)
            facade_price_eur = round(facade_price_eur, 2)

        base_total = total_price

        delivery_pct = pricing_settings.get_delivery_markup_percent()
        delivery_price = round(base_total * delivery_pct / 100, 2)
        total_price += delivery_price

        installation_price = 0
        install_pct = 0
        if installation:
            install_pct = pricing_settings.get_installation_markup_percent()
            installation_price = round(base_total * install_pct / 100, 2)
            total_price += installation_price

        glazing_openings = options.get("glazing_openings", []) or []
        glazing_total_eur = 0.0
        glazing_total_area = 0.0
        glazing_normalized = []

        if glazing_openings:
            sv_g = selected_variant or ""
            if "Light" in sv_g:
                col_w_g = FACADE_COL_WIDTHS["Light"]
                beam_h_g = FACADE_BEAM_HEIGHTS["Light"]
            elif pergola_type == "B200":
                col_w_g = FACADE_COL_WIDTHS["B200"]
                beam_h_g = FACADE_BEAM_HEIGHTS["B200"]
            else:
                col_w_g = 0.164
                beam_h_g = 0.280
            open_h_g = max(0.1, height_m - beam_h_g)

            side_max_bay_g = {"left": 0, "right": 0}
            for _op in glazing_openings:
                if not isinstance(_op, dict):
                    continue
                _s = _op.get("side", "")
                if _s in side_max_bay_g:
                    side_max_bay_g[_s] = max(side_max_bay_g[_s], int(_op.get("bay", 0)))
            length_modules_g = max(side_max_bay_g["left"], side_max_bay_g["right"]) + 1

            full_fb_bay_w = width_m / max(1, modules)
            full_lr_bay_w = length_m / max(1, length_modules_g)

            # Build set of (side,bay) keys already taken by facade openings
            _facade_keys = set()
            for _fop in (facade_openings or []):
                if isinstance(_fop, dict) and _fop.get("side") and _fop.get("type"):
                    _facade_keys.add((_fop.get("side"), int(_fop.get("bay", 0))))

            _allowed_pcs_s500 = (2, 3, 4, 5, 6, 8, 10)
            _allowed_pcs_s100 = S100_PC_ALLOWED
            for op in glazing_openings:
                if not isinstance(op, dict):
                    continue
                side = op.get("side", "")
                if side not in ("front", "back", "left", "right"):
                    continue
                bay_g = int(op.get("bay", 0))
                # Backend mutual exclusion: facade wins
                if (side, bay_g) in _facade_keys:
                    continue
                raw_series = op.get("series")
                if raw_series is None or str(raw_series).strip() == '':
                    raise ValueError(
                        f"Glazing opening (side={side}, bay={bay_g}): missing 'series'. "
                        f"Expected one of S500, S100, W500, W600, W700.")
                series_g = str(raw_series).upper()
                if series_g not in ('S500', 'S100', 'W500', 'W600', 'W700'):
                    raise ValueError(
                        f"Glazing opening (side={side}, bay={bay_g}): unknown series '{raw_series}'. "
                        f"Expected one of S500, S100, W500, W600, W700.")
                count_g = max(1, int(op.get("count", 1) or 1))

                full_bay_w = full_fb_bay_w if side in ("front", "back") else full_lr_bay_w
                op_w = max(0.1, full_bay_w - 2 * col_w_g)
                op_h = open_h_g

                # ---- W-series guillotine branch ----
                if series_g in ('W500', 'W600', 'W700'):
                    bnd = W_BOUNDS[series_g]
                    if op_w < bnd['w_min'] or op_h < bnd['h_min'] or op_w > bnd['w_max'] or op_h > bnd['h_max']:
                        continue
                    color_g = op.get("color") or 'ral9t08'
                    if color_g not in W_COLOR_NAMES:
                        raise ValueError(
                            f"Glazing opening (side={side}, bay={bay_g}, series={series_g}): "
                            f"color '{color_g}' is not valid for {series_g}. "
                            f"Allowed: {sorted(W_COLOR_NAMES.keys())}.")
                    glass_g = op.get("glass") or 'transparent'
                    if glass_g not in W_GLASS_NAMES:
                        raise ValueError(
                            f"Glazing opening (side={side}, bay={bay_g}, series={series_g}): "
                            f"glass '{glass_g}' is not valid for {series_g}. "
                            f"Allowed: {sorted(W_GLASS_NAMES.keys())}.")
                    sashes_g = int(op.get("sashes") or 0)
                    if sashes_g not in (2, 3):
                        sashes_g = w_min_sashes(op_w)
                    plavnik_g = op.get("plavnik")
                    if plavnik_g is None:
                        plavnik_g = (op_w > W_PLAVNIK_TRIGGER_W)
                    plavnik_g = bool(plavnik_g)
                    _glz_rate = pricing_settings.get_euro_rate() or 100.0
                    price_one = w_calc_price(series_g, op_w, op_h, color_g, glass_g,
                                             plavnik=plavnik_g, euro_rate=_glz_rate)
                    price_eur = round(price_one * count_g, 2)
                    area_one = round(op_w * op_h, 2)

                    # Drive selection per window (force tandem when wider than 3m).
                    # Brand binds to the pergola's automation family (B700NEW → Somfy,
                    # everything else → Simu) unless the opening explicitly overrides it.
                    _pergola_default_brand = 'somfy' if pergola_type == 'B700NEW' else 'simu'
                    brand_g = (op.get("brand") or _pergola_default_brand).lower()
                    if brand_g not in ('simu', 'somfy'):
                        brand_g = _pergola_default_brand
                    force_tandem = (op_w > 3.0)
                    drive_name, drive_price, is_tandem, req_torque = pick_guillotine_drive(
                        op_w, op_h, brand=brand_g, force_tandem=force_tandem)
                    drive_total = round(drive_price * count_g, 2)

                    bay_label = f"\u043f\u0440\u043e\u0451\u043c {bay_g + 1}" if (
                        (side in ('front', 'back') and modules > 1) or
                        (side in ('left', 'right') and length_modules_g > 1)
                    ) else "\u043f\u0440\u043e\u0451\u043c"
                    plav_label = ", плавник" if plavnik_g else ""
                    gloss = (f"Гильотинное остекление {series_g} "
                             f"({GLAZING_SIDE_NAMES[side]}, {bay_label}, "
                             f"{sashes_g} створки, "
                             f"{W_GLASS_NAMES.get(glass_g, glass_g)}, "
                             f"{W_COLOR_NAMES.get(color_g, color_g)}{plav_label}, "
                             f"{op_w:.2f}\u00d7{op_h:.2f} \u043c"
                             f"{(', ' + str(count_g) + ' шт.') if count_g > 1 else ''})")
                    items.append({"name": gloss, "price": price_eur})
                    specification.append({
                        "name": (f"Гильотинное остекление {series_g} · "
                                 f"{W_GLASS_NAMES.get(glass_g, glass_g)} · "
                                 f"{W_COLOR_NAMES.get(color_g, color_g)}"
                                 f"{plav_label} · {op_w:.2f}\u00d7{op_h:.2f} \u043c"),
                        "count": (f"{count_g} шт. \u00b7 {sashes_g} створки"
                                  f" \u00b7 {area_one * count_g:.2f} \u043c\u00b2")
                    })
                    items.append({
                        "name": f"Привод {drive_name} ({req_torque:.1f} Нм, {GLAZING_SIDE_NAMES[side]} · {bay_label})",
                        "price": drive_total
                    })
                    specification.append({
                        "name": f"Привод {drive_name}",
                        "count": f"{count_g} шт."
                    })
                    total_price += price_eur + drive_total
                    glazing_total_eur += price_eur
                    glazing_total_area += area_one * count_g
                    glazing_normalized.append({
                        "series": series_g,
                        "side": side, "bay": bay_g,
                        "sashes": sashes_g,
                        "color": color_g, "glass": glass_g,
                        "plavnik": plavnik_g,
                        "brand": brand_g,
                        "drive": drive_name,
                        "drive_torque": req_torque,
                        "drive_price_eur": drive_total,
                        "count": count_g,
                        "w": round(op_w, 3), "h": round(op_h, 3),
                        "area": round(area_one * count_g, 2),
                        "price_eur": price_eur,
                    })
                    continue

                if series_g == 'S100':
                    pc_g = int(op.get("pc", 3) or 3)
                    direction_g = op.get("direction") or 'right'
                    color_g = op.get("color") or 'ral9t08'
                    glass_g = op.get("glass") or 'transparent'

                    if pc_g not in _allowed_pcs_s100:
                        raise ValueError(
                            f"Glazing opening (side={side}, bay={bay_g}, series=S100): "
                            f"panel count {pc_g} is not allowed. "
                            f"Allowed values: {list(_allowed_pcs_s100)}.")
                    _min_pc = s100_min_panels(op_w, op_h)
                    if pc_g < _min_pc:
                        raise ValueError(
                            f"Glazing opening (side={side}, bay={bay_g}, series=S100): "
                            f"panel count {pc_g} is below the minimum {_min_pc} required "
                            f"for opening {op_w:.2f}x{op_h:.2f} m.")
                    if pc_g in (8, 12):
                        direction_g = 'center'
                    if pc_g == 6 and direction_g == 'center':
                        pass  # use 3+3 mapping
                    if op_w < S100_MIN_W or op_h < S100_MIN_H or op_w > S100_MAX_W or op_h > S100_MAX_H:
                        continue
                    if color_g not in S100_COLOR_NAMES:
                        raise ValueError(
                            f"Glazing opening (side={side}, bay={bay_g}, series=S100): "
                            f"color '{color_g}' is not valid for S100. "
                            f"Allowed: {sorted(S100_COLOR_NAMES.keys())}.")
                    if glass_g not in S100_GLASS_NAMES:
                        raise ValueError(
                            f"Glazing opening (side={side}, bay={bay_g}, series=S100): "
                            f"glass '{glass_g}' is not valid for S100. "
                            f"Allowed: {sorted(S100_GLASS_NAMES.keys())}.")

                    _glz_rate = pricing_settings.get_euro_rate() or 100.0
                    price_eur = s100_calc_price(op_w, op_h, pc_g, direction_g, color_g, glass_g, euro_rate=_glz_rate)
                    price_eur = round(price_eur * count_g, 2)
                    area_one = round(op_w * op_h, 2)

                    bay_label = f"\u043f\u0440\u043e\u0451\u043c {bay_g + 1}" if (
                        (side in ('front', 'back') and modules > 1) or
                        (side in ('left', 'right') and length_modules_g > 1)
                    ) else "\u043f\u0440\u043e\u0451\u043c"
                    pc_label = f"{pc_g} \u043f\u0430\u043d."
                    gloss = (f"\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 S100 "
                             f"({GLAZING_SIDE_NAMES[side]}, {bay_label}, {pc_label}, "
                             f"{S100_GLASS_NAMES.get(glass_g, glass_g)}, "
                             f"{S100_COLOR_NAMES.get(color_g, color_g)}, "
                             f"{op_w:.2f}\u00d7{op_h:.2f} \u043c"
                             f"{(', ' + str(count_g) + ' шт.') if count_g > 1 else ''})")
                    items.append({"name": gloss, "price": price_eur})
                    specification.append({
                        "name": "\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 S100",
                        "count": (f"{count_g} \u0448\u0442. \u00b7 {pc_g} \u043f\u0430\u043d\u0435\u043b\u0435\u0439"
                                  f" \u00b7 {area_one * count_g:.2f} \u043c\u00b2")
                    })
                    total_price += price_eur
                    glazing_total_eur += price_eur
                    glazing_total_area += area_one * count_g
                    glazing_normalized.append({
                        "series": "S100",
                        "side": side, "bay": bay_g,
                        "pc": pc_g, "direction": direction_g,
                        "color": color_g, "glass": glass_g, "count": count_g,
                        "w": round(op_w, 3), "h": round(op_h, 3),
                        "area": round(area_one * count_g, 2),
                        "price_eur": price_eur,
                    })
                    continue

                # ---- S500 branch (original) ----
                pc_g = int(op.get("pc", 3) or 3)
                direction_g = op.get("direction") or 'right'
                color_g = op.get("color") or 'ral7016'
                glass_g = op.get("glass") or 'transparent'

                if color_g not in GLAZING_COLOR_NAMES:
                    raise ValueError(
                        f"Glazing opening (side={side}, bay={bay_g}, series=S500): "
                        f"color '{color_g}' is not valid for S500. "
                        f"Allowed: {sorted(GLAZING_COLOR_NAMES.keys())}.")
                if glass_g not in GLAZING_GLASS_NAMES:
                    raise ValueError(
                        f"Glazing opening (side={side}, bay={bay_g}, series=S500): "
                        f"glass '{glass_g}' is not valid for S500. "
                        f"Allowed: {sorted(GLAZING_GLASS_NAMES.keys())}.")

                if pc_g not in _allowed_pcs_s500:
                    raise ValueError(
                        f"Glazing opening (side={side}, bay={bay_g}, series=S500): "
                        f"panel count {pc_g} is not allowed. "
                        f"Allowed values: {list(_allowed_pcs_s500)}.")
                _min_pc = glazing_min_panels(op_w, op_h)
                if pc_g < _min_pc:
                    raise ValueError(
                        f"Glazing opening (side={side}, bay={bay_g}, series=S500): "
                        f"panel count {pc_g} is below the minimum {_min_pc} required "
                        f"for opening {op_w:.2f}x{op_h:.2f} m.")
                if (op_w >= 6 and pc_g >= 6) or pc_g >= 8:
                    direction_g = 'center'
                if pc_g % 2 != 0 and direction_g == 'center':
                    direction_g = 'right'
                if op_w < 1.8 or op_h < 1.7 or op_w > 12.0 or op_h > 3.25:
                    continue

                _glz_rate = pricing_settings.get_euro_rate() or 100.0
                price_eur = glazing_calc_price(op_w, op_h, pc_g, direction_g, color_g, glass_g, euro_rate=_glz_rate)
                price_eur = round(price_eur * count_g, 2)
                area_one = round(op_w * op_h, 2)

                bay_label = f"\u043f\u0440\u043e\u0451\u043c {bay_g + 1}" if (
                    (side in ('front', 'back') and modules > 1) or
                    (side in ('left', 'right') and length_modules_g > 1)
                ) else "\u043f\u0440\u043e\u0451\u043c"
                pc_label = f"{pc_g} \u0441\u0442\u0432."
                gloss = (f"\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 S500 "
                         f"({GLAZING_SIDE_NAMES[side]}, {bay_label}, {pc_label}, "
                         f"{GLAZING_GLASS_NAMES.get(glass_g, glass_g)}, "
                         f"{GLAZING_COLOR_NAMES.get(color_g, color_g)}, "
                         f"{op_w:.2f}\u00d7{op_h:.2f} \u043c"
                         f"{(', ' + str(count_g) + ' шт.') if count_g > 1 else ''})")
                items.append({"name": gloss, "price": price_eur})
                specification.append({
                    "name": "\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 S500",
                    "count": (f"{count_g} \u0448\u0442. \u00b7 {pc_g} \u0441\u0442\u0432\u043e\u0440\u043e\u043a"
                              f" \u00b7 {area_one * count_g:.2f} \u043c\u00b2")
                })
                total_price += price_eur
                glazing_total_eur += price_eur
                glazing_total_area += area_one * count_g
                glazing_normalized.append({
                    "series": "S500",
                    "side": side, "bay": bay_g,
                    "pc": pc_g, "direction": direction_g,
                    "color": color_g, "glass": glass_g, "count": count_g,
                    "w": round(op_w, 3), "h": round(op_h, 3),
                    "area": round(area_one * count_g, 2),
                    "price_eur": price_eur,
                })

        glazing_total_eur = round(glazing_total_eur, 2)
        glazing_total_area = round(glazing_total_area, 2)

        # B600/B200 with W-windows but no lighting → still need a remote
        if (pergola_type in ["B600", "B200"]
                and not has_lighting
                and w_window_count > 0):
            _w_remote_name, _w_remote_price = get_remote_control(w_window_count)
            items.append({
                "name": f"Пульт ДУ {_w_remote_name} ({w_window_count} {_get_plural_form(w_window_count, 'канал', 'канала', 'каналов')})",
                "price": _w_remote_price
            })
            total_price += _w_remote_price
            specification.append({
                "name": f"Пульт ДУ {_w_remote_name}",
                "count": f"1 шт. ({w_window_count} {_get_plural_form(w_window_count, 'канал', 'канала', 'каналов')})"
            })

        # Push delivery + installation rows AFTER glazing so they appear last in spec/items
        items.append({"name": "Доставка", "price": delivery_price})
        specification.append({"name": "Доставка", "count": "1"})
        if installation:
            items.append({"name": "Установка", "price": installation_price})
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
            "reinforcement": b200_reinf if pergola_type == "B200" else {"kind": None, "extra_columns_count": 0},
            "total_price_eur": total_price,
            "euro_rate": euro_rate,
            "totals": {
                "cash": total_rub,
                "non_cash": round(total_rub / 0.92),
                "with_vat": round(total_rub / 0.85)
            },
            "delivery": {"percentage": delivery_pct, "price": delivery_price},
            "installation": {"selected": installation, "price": installation_price},
            "facade": {
                "type": facade_type,
                "openings": facade_openings,
                "area": facade_area,
                "price": facade_price_eur,
                "extra_cols_f": extra_cols_f,
                "extra_cols_b": extra_cols_b,
                "extra_cols_a": extra_cols_a,
                "extra_cols_c": extra_cols_c,
                "extra_cols_count": total_extra_cols,
            },
            "glazing": {
                "openings": glazing_normalized,
                "area": glazing_total_area,
                "price": glazing_total_eur,
                "count": sum(int(o.get("count", 1) or 1) for o in glazing_normalized),
            },
            "lamellas_count": lamellas_count,
            "pergola_type_name": PERGOLA_TYPES.get(pergola_type, pergola_type),
            "lamella_type_name": LAMELLA_TYPES.get(lamella_type, lamella_type),
            "selected_variant": selected_variant
        }

        return results

    except Exception as e:
        logger.error(f"Ошибка при расчете: {e}")
        return {"error": str(e)}


def perform_all_variants_calculation(dimensions, options):
    from config.variant_specs import VARIANT_DISPLAY_ORDER
    pergola_type = options.get("pergola_type", "")
    variants_order = VARIANT_DISPLAY_ORDER.get(pergola_type, [])
    all_results = []

    for vo in variants_order:
        variant_name = vo["variant"]
        ls = vo["lamella_size"]
        label = vo["label"]

        if pergola_type in ["B500NEW", "B700NEW"]:
            lt = f"{pergola_type.replace('NEW','')}-{('20' if ls == '200' else '25')}NEW"
        elif pergola_type == "B200":
            suffix = "A" if variant_name.startswith("AERO") else "F"
            lt = f"B200-{ls}{suffix}"
        else:
            lt = "B600-PIR"

        opts = dict(options)
        opts["selected_variant"] = variant_name
        opts["lamella_size"] = ls
        opts["lamella_type"] = lt

        result = perform_calculation(dimensions, opts)
        if "error" not in result:
            result["variant_label"] = label
            all_results.append(result)

    all_results.sort(key=lambda r: r["totals"]["cash"])
    return all_results


def get_pergola_types_list():
    return [
        {"id": "B500NEW", "name": PERGOLA_TYPES["B500NEW"], "description": PERGOLA_TYPE_DESCRIPTIONS["B500NEW"], "image": "b500_rotation.png"},
        {"id": "B700NEW", "name": PERGOLA_TYPES["B700NEW"], "description": PERGOLA_TYPE_DESCRIPTIONS["B700NEW"], "image": "b700_sliding.png"},
        {"id": "B600", "name": PERGOLA_TYPES["B600"], "description": PERGOLA_TYPE_DESCRIPTIONS["B600"], "image": "b600_sandwich.png"},
        {"id": "B200", "name": PERGOLA_TYPES["B200"], "description": PERGOLA_TYPE_DESCRIPTIONS["B200"], "image": "b200_aero_flat.jpg"}
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
    elif pergola_type == "B200":
        return [
            {"id": "20", "name": "Шаг 20 см (FLAT-20)", "lamella_type": "B200-20"},
            {"id": "25", "name": "Шаг 25 см (FLAT-25)", "lamella_type": "B200-25"}
        ]
    return []


def get_max_dimensions(pergola_type, lamella_size):
    if pergola_type == "B600":
        key = pergola_type
    elif pergola_type == "B200":
        key = f"B200_{lamella_size}"
    else:
        key = f"{pergola_type}_{lamella_size}"
    return MAX_DIMENSIONS.get(key, {"width": 13.5, "length": 8.0})
