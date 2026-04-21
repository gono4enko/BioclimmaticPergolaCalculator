import math

def calculate_modules(width, model_key):
    # Standard module width is 4.5m
    return max(1, math.ceil(width / 4.5))

def calculate_lamella_count(length, model_key):
    if "250" in model_key or "B200_25" in model_key:
        pitch = 0.25
    elif "200" in model_key or "B200_20" in model_key:
        pitch = 0.20
    else:
        pitch = 0.25
    return max(4, math.ceil(length / pitch))

def needs_extra_column_for_fill(bay_width, fill_type):
    # ZIP130 max width is 5.0m
    if fill_type.lower().startswith('zip'):
        return bay_width > 5.0
    # Facade max panels
    if fill_type.lower() == 'facade':
        return bay_width > 4.0
    return False
