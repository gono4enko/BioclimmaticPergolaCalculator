import math
import csv
import os

def _load_csv_matrix(filename):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)
    if not os.path.exists(path):
        return None, None, None
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        widths = [float(x) for x in header[1:]]
        heights = []
        prices = []
        for row in reader:
            heights.append(float(row[0]))
            prices.append([float(x) for x in row[1:]])
    return widths, heights, prices

def _lookup_matrix(widths, heights, prices, w, h):
    wi = -1
    for i, val in enumerate(widths):
        if w <= val + 1e-6:
            wi = i
            break
    if wi == -1: wi = len(widths) - 1
    
    hi = -1
    for i, val in enumerate(heights):
        if h <= val + 1e-6:
            hi = i
            break
    if hi == -1: hi = len(heights) - 1
    
    return prices[hi][wi], widths[wi], heights[hi]

def glazing_calc_price(w, h, glass='transparent', color='ral7016', overrides=None):
    widths, heights, prices = _load_csv_matrix('s500.csv')
    if not prices: return None
    
    base_val, lw, lh = _lookup_matrix(widths, heights, prices, w, h)
    
    # Surcharges from GLAZING_SETTINGS
    # Transparent: 4800, Tinted: 5800 RUB/m2. 
    # But wait, the spec says CSV is in EUR. 
    # In original code, glass price was in RUB and converted to EUR.
    # Here we should use EUR surcharges. 
    # From generate_csvs.py: glass.csv has (5800-4800)/100 = 10 EUR/m2 surcharge for tinted
    
    glass_surcharge = 0
    if glass == 'tinted':
        glass_surcharge = 10.0 * (w * h)
        
    color_surcharge = 0
    if color == 'custom':
        color_surcharge = base_val * 0.1 # 10%
        
    # Original glazing_calc_price had complex RUB->EUR conversion.
    # We'll simplify to EUR only.
    # comp + glass_part + deliv_part + install_part
    # Let's assume the CSV price already includes base components.
    
    total = base_val + glass_surcharge + color_surcharge
    
    return {
        "base_eur": round(base_val, 2),
        "glazing_supplement_eur": round(glass_surcharge, 2),
        "color_supplement_eur": round(color_surcharge, 2),
        "total_eur": round(total, 2),
        "lookup": {"w": lw, "h": lh}
    }

def s100_calc_price(w, h, glass='transparent', color='ral7016', overrides=None):
    widths, heights, prices = _load_csv_matrix('s100.csv')
    if not prices: return None
    base_val, lw, lh = _lookup_matrix(widths, heights, prices, w, h)
    
    glass_surcharge = 0
    if glass == 'tinted':
        glass_surcharge = 10.0 * (w * h)
        
    total = base_val + glass_surcharge
    
    return {
        "base_eur": round(base_val, 2),
        "glazing_supplement_eur": round(glass_surcharge, 2),
        "total_eur": round(total, 2),
        "lookup": {"w": lw, "h": lh}
    }
