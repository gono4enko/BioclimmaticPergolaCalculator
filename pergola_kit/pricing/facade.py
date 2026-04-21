FACADE_MAX_PANEL_W = {
    "FZ-44": 2.0,
    "FP-20": 4.0,
    "FP-PIR": 4.0,
}

FACADE_PRICES = {
    "FP-20":     199,
    "FP-PIR":    150,
    "FZ-44-50":   99,
    "FZ-44-70":  124,
    "FZ-44-100": 170,
}

def facade_calc_price(subtype, width, height, overrides=None):
    price_per_m2 = FACADE_PRICES.get(subtype, 0)
    if overrides and subtype in overrides:
        price_per_m2 = overrides[subtype]
    
    area = width * height
    base_eur = area * price_per_m2
    
    return {
        "base_eur": round(base_eur, 2),
        "total_eur": round(base_eur, 2),
        "lookup": {"w": width, "h": height}
    }
