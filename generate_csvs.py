import sys
import os
import csv

# Add project root to sys.path to import flask_app.services.calculator
sys.path.insert(0, os.getcwd())

from flask_app.services.calculator import (
    ZIP100_W, ZIP100_H, ZIP100_P,
    ZIP130_W, ZIP130_H, ZIP130_P,
    GLAZING_PD, S100_PD,
    W500_PD, W600_PD, W700_PD,
    FACADE_PRICES,
    ZIP_FABRIC_SURCHARGE,
    _zip_motor_eur,
    GLAZING_SETTINGS
)

def pivot_to_csv(filename, width_axis, height_axis, price_grid):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([''] + [str(w) for w in width_axis])
        for h_idx, h_val in enumerate(height_axis):
            writer.writerow([str(h_val)] + [str(price_grid[h_idx][w_idx]) for w_idx in range(len(width_axis))])

# ZIP (using the axes found in source)
pivot_to_csv('pergola_kit/data/zip100.csv', ZIP100_W, ZIP100_H, ZIP100_P)
pivot_to_csv('pergola_kit/data/zip130.csv', ZIP130_W, ZIP130_H, ZIP130_P)

# S500 / S100
pivot_to_csv('pergola_kit/data/s500.csv', GLAZING_PD['4']['w'], GLAZING_PD['4']['h'], GLAZING_PD['4']['p'])
pivot_to_csv('pergola_kit/data/s100.csv', S100_PD['4']['w'], S100_PD['4']['h'], S100_PD['4']['p'])

# W500/600/700
pivot_to_csv('pergola_kit/data/w500.csv', W500_PD['w'], W500_PD['h'], W500_PD['p'])
pivot_to_csv('pergola_kit/data/w600.csv', W600_PD['w'], W600_PD['h'], W600_PD['p'])
pivot_to_csv('pergola_kit/data/w700.csv', W700_PD['w'], W700_PD['h'], W700_PD['p'])

# facade.csv
with open('pergola_kit/data/facade.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['type', 'price_eur_m2'])
    for k, v in FACADE_PRICES.items():
        writer.writerow([k, v])

# motors.csv
motor_w = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
motor_h = [1.0, 2.0, 3.0, 4.0, 5.0]
with open('pergola_kit/data/motors.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['brand', 'width', 'height', 'price_eur'])
    for brand in ['somfy', 'simu', 'decolife']:
        for w in motor_w:
            for h in motor_h:
                writer.writerow([brand, w, h, _zip_motor_eur(brand, w, h)])

# fabrics.csv
with open('pergola_kit/data/fabrics.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['fabric', 'surcharge_eur_m2'])
    for k, v in ZIP_FABRIC_SURCHARGE.items():
        writer.writerow([k, v])

# glass.csv
with open('pergola_kit/data/glass.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['type', 'surcharge_eur_m2'])
    writer.writerow(['transparent', 0.0])
    writer.writerow(['tinted', GLAZING_SETTINGS.get('S500_TINTED_EUR_M2', 5800.0) - GLAZING_SETTINGS.get('S500_TRANSPARENT_EUR_M2', 4800.0)])

print("CSV files generated successfully.")
