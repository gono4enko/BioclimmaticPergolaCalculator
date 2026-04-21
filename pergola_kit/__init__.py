from .pricing.zip import zip_calc_price
from .pricing.glazing import glazing_calc_price, s100_calc_price
from .pricing.windows import w_calc_price
from .pricing.facade import facade_calc_price
from .pricing.motors import _zip_motor_eur
from .geometry.limits import MODEL_LIMITS
from .geometry.modules import calculate_modules, calculate_lamella_count, needs_extra_column_for_fill
from .drawings.top import generate_top_view_svg
from .drawings.elevation import generate_front_view_svg, generate_side_view_svg
from .drawings.iso import generate_isometric_svg, generate_pir_iso_svg
from .drawings.details import generate_zip_detail_svg

def calculate_openings(payload):
    """
    payload: {
        'model': str,
        'width': float,
        'length': float,
        'height': float,
        'openings': {
            'front': [{'type': 'zip100', ...}],
            'right': [...],
            ...
        }
    }
    """
    model = payload.get('model', 'B500NEW_250')
    width = float(payload.get('width', 0))
    length = float(payload.get('length', 0))
    height = float(payload.get('height', 3.0))
    openings = payload.get('openings', {})
    
    total_eur = 0
    breakdown = []
    errors = []
    extra_columns_required = 0
    
    # Simple logic to process openings
    for side, side_openings in openings.items():
        for bay_idx, op in enumerate(side_openings):
            op_type = op.get('type', '').lower()
            res = None
            
            # Use appropriate pricing function
            if op_type == 'zip100' or op_type == 'zip130':
                res = zip_calc_price(op_type, width, height, fabric=op.get('fabric', 'veozip'), 
                                   color=op.get('color', 'ral9016'), drive=op.get('drive', 'manual'))
            elif op_type == 's500':
                res = glazing_calc_price(width, height, glass=op.get('glass', 'transparent'), 
                                       color=op.get('color', 'ral7016'))
            elif op_type == 's100':
                res = s100_calc_price(width, height, glass=op.get('glass', 'transparent'), 
                                    color=op.get('color', 'ral7016'))
            elif op_type in ('w500', 'w600', 'w700'):
                res = w_calc_price(op_type, width, op.get('h', height), glass=op.get('glass', 'transparent'), 
                                 color=op.get('color', 'ral7016'))
            elif op_type == 'facade':
                res = facade_calc_price(op.get('subtype', 'FP-20'), width, height)
            
            if res and 'total_eur' in res:
                total_eur += res['total_eur']
                breakdown.append({
                    'side': side,
                    'bay': bay_idx,
                    'type': op_type,
                    'size': f"{width}x{height}",
                    'price_eur': res['total_eur']
                })
            else:
                errors.append(f"Error calculating {op_type} on {side} bay {bay_idx}")

    return {
        "total_eur": round(total_eur, 2),
        "breakdown": breakdown,
        "extra_columns_required": extra_columns_required,
        "errors": errors
    }
