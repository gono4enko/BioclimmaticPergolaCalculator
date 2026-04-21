from .glazing import _load_csv_matrix, _lookup_matrix

def w_calc_price(series, w, h, glass='transparent', color='ral7016', overrides=None):
    filename = f"{series.lower()}.csv"
    widths, heights, prices = _load_csv_matrix(filename)
    if not prices: return None
    
    base_val, lw, lh = _lookup_matrix(widths, heights, prices, w, h)
    
    total = base_val
    return {
        "base_eur": round(base_val, 2),
        "total_eur": round(total, 2),
        "lookup": {"w": lw, "h": lh}
    }
