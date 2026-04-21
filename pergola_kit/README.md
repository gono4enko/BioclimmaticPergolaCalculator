# Pergola Kit

Python package for pergola pricing and SVG generation.

## Python Version
Target: 3.9+ (Standard Library only)

## Installation
Just copy the `pergola_kit` directory into your project.

## Usage

### Pricing Example
```python
from pergola_kit import calculate_openings

payload = {
    'model': 'B500NEW_250',
    'width': 6.0,
    'length': 4.0,
    'height': 3.0,
    'openings': {
        'front': [{'type': 'zip100', 'fabric': 'veozip', 'color': 'ral7016', 'drive': 'somfy'}],
        'right': [{'type': 's500', 'glass': 'tinted', 'color': 'ral9016'}],
        'left': [{'type': 'facade', 'subtype': 'FP-20'}],
        'back': [{'type': 'w600', 'h': 1.2, 'color': 'ral7016', 'glass': 'clear'}]
    }
}

result = calculate_openings(payload)
print(f"Total: {result['total_eur']} EUR")
```

### SVG Generation Example
```python
from pergola_kit import generate_top_view_svg, generate_isometric_svg

# Top view
top_svg = generate_top_view_svg(width=6.0, length=4.0, modules=2)

# Isometric view
iso_svg = generate_isometric_svg(width=6.0, length=4.0, height=3.0, modules=2, lamella_count=16)
```

## Model Limits
- **B500NEW_250**: Max 13.5x8.0m, pitch 250mm
- **B500NEW_200**: Max 15.0x8.0m, pitch 200mm
- **B700NEW_250**: Max 13.5x8.0m, pitch 250mm
- **B700NEW_200**: Max 15.0x8.0m, pitch 200mm
- **B600**: Max 15.0x8.0m, PIR panels
- **B200_20**: Max 13.5x12.1m, pitch 200mm
- **B200_25**: Max 13.5x12.1m, pitch 250mm

## Fill Types
- `zip100`, `zip130`: Requires `fabric`, `color`, `drive`.
- `s500`, `s100`: Requires `glass`, `color`.
- `w500`, `w600`, `w700`: Requires `glass`, `color`, optional `h`.
- `facade`: Requires `subtype`.

## Data Files
CSV files in `data/` use EUR pricing matrices.
- `zip100.csv`, `zip130.csv`: width (1.0 to 4.0/5.0m) x height (1.5 to 3.5/5.0m)
- `s500.csv`, `s100.csv`: width x height matrices
- `w500.csv`, `w600.csv`, `w700.csv`: width x height matrices
