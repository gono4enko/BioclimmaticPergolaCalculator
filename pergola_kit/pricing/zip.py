import os
from .glazing import _load_csv_matrix, _lookup_matrix
from .motors import _zip_motor_eur

def zip_calc_price(series, width, height, fabric='veozip', color='ral9016', drive='manual', has_glazing=False, overrides=None):
    filename = f"{series.lower()}.csv"
    widths, heights, prices = _load_csv_matrix(filename)
    if not prices: return None
    
    # Adjusted dims for overlay if has_glazing
    adj_w = width
    adj_h = height
    if has_glazing:
        adj_w += 0.12 # ZIP_OVERLAY_ADD_W
        adj_h += 0.10 # ZIP100_OVERLAY_ADD_H
        
    base_val, lw, lh = _lookup_matrix(widths, heights, prices, adj_w, adj_h)
    
    # Fabric surcharge
    # generate_csvs.py uses ZIP_FABRIC_SURCHARGE which was 0 for veozip
    fabric_surcharge = 0
    if fabric == 'soltis': fabric_surcharge = 40.0 * (adj_w * adj_h)
    elif fabric == 'copaco': fabric_surcharge = 35.0 * (adj_w * adj_h)
    
    # Motor
    motor_eur = _zip_motor_eur(drive, adj_w, adj_h)
    
    total = (base_val + fabric_surcharge + motor_eur) * 1.1 # Assembly 10%
    
    return {
        "base_eur": round(base_val, 2),
        "motor_eur": round(motor_eur, 2),
        "fabric_eur": round(fabric_surcharge, 2),
        "total_eur": round(total, 2),
        "lookup": {"w": lw, "h": lh}
    }
