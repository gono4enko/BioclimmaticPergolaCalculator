def _zip_motor_eur(brand, w, h):
    brand = brand.lower()
    small = (w <= 3.5 and h <= 4.0)
    if brand == 'simu':
        return 175.0
    if brand == 'somfy':
        return 180.0 if small else 230.0
    if brand == 'decolife':
        return 130.0
    return 50.0  # manual/unknown
