#!/usr/bin/env python3
"""
Migration: Parse B500 variant price tables from images via Claude Vision API.
Variants: Basic (250mm), Light (250mm), Pro (250mm), Pro (200mm)
"""
import os
import sys
import json
import base64
import urllib.request
import psycopg2
import time

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

PRICE_IMAGES = [
    {
        'path': 'attached_assets/Снимок_экрана_2026-04-14_в_21.38.29_1776191913738.png',
        'pergola_type': 'B500NEW',
        'lamella_size': '250',
        'variant': 'Basic',
        'description': 'B500-25П Basic Bioclimatic, Ламель 250x46 BASIC. 1 модуль: 2.5-4.5m, 2 модуля: 5.0-9.0m, 3 модуля: 7.5-13.5m. Вынос от 2.5 до 8.0m с шагом 0.5m'
    },
    {
        'path': 'attached_assets/Снимок_экрана_2026-04-14_в_21.38.50_1776191934429.png',
        'pergola_type': 'B500NEW',
        'lamella_size': '250',
        'variant': 'Light',
        'description': 'B500-25П Light Bioclimatic, Ламель 250x45 LIGHT. 1 модуль: 2.5-4.0m, 2 модуля: 5.0-8.0m, 3 модуля: 7.5-12.0m. Вынос от 2.5 до 8.0m с шагом 0.5m'
    },
    {
        'path': 'attached_assets/Снимок_экрана_2026-04-14_в_21.39.10_1776191956963.png',
        'pergola_type': 'B500NEW',
        'lamella_size': '250',
        'variant': 'Pro',
        'description': 'B500-25П Pro Bioclimatic, Ламель 250x53 PRO. 1 модуль: 2.5-4.5m, 2 модуля: 5.0-9.0m, 3 модуля: 7.5-13.5m. Вынос от 2.5 до 8.0m с шагом 0.5m'
    },
    {
        'path': 'attached_assets/Снимок_экрана_2026-04-14_в_21.39.32_1776191976994.png',
        'pergola_type': 'B500NEW',
        'lamella_size': '200',
        'variant': 'Pro',
        'description': 'B500-20П Pro Bioclimatic, Ламель 200x56 PRO. 1 модуль: 3.0-5.0m, 2 модуля: 6.0-10.0m, 3 модуля: 9.0-15.0m. Вынос от 2.45 до 8.05m с шагом 0.4m'
    }
]

PROMPT_TEMPLATE = """Analyze this price table image for: {description}

Extract ALL prices from the main price table. The table structure:
- Left column: depth values (Вынос, м)
- Top row: width values (Ширина, м) grouped by module count (1 модуль, 2 модуля, 3 модуля)
- Each cell has a MAIN price (large number) and sometimes a smaller italic number below (per-m² price - IGNORE these)

Return a JSON object with this exact structure:
{{
    "module_groups": {{
        "1": [list of width values as floats],
        "2": [list of width values as floats],
        "3": [list of width values as floats]
    }},
    "depths": [list of depth values as floats, from top to bottom],
    "prices": {{
        "depth_as_string": {{
            "width_as_string": main_price_as_integer,
            ...for every width column...
        }},
        ...for every depth row...
    }}
}}

CRITICAL RULES:
1. Extract ONLY the main large prices (integers like 5489, 10405, etc.), NOT the small italic per-m² numbers below
2. Use decimal points: 2.5 not 2,5
3. Include EVERY row and EVERY column - do not skip any
4. Prices are whole integers with no decimals
5. Some width values appear in BOTH 2-module and 3-module groups (e.g., 7.5, 9.0). Include them in both groups and list their prices. Use keys like "7.5" for 2-module and "7.5_3mod" for 3-module if the same width appears in multiple module groups.
6. Pay careful attention to 4-5 digit numbers. Common OCR errors: confusing 3/8, 5/6, 1/7

Return ONLY valid JSON, no markdown formatting, no extra text."""


def parse_price_image(image_info):
    """Parse a single price table image using Claude Vision API."""
    path = image_info['path']
    print(f"\n{'='*60}")
    print(f"Parsing: {image_info['variant']} ({image_info['lamella_size']}mm)")
    print(f"Image: {path}")

    with open(path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode('utf-8')

    prompt = PROMPT_TEMPLATE.format(description=image_info['description'])

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 16000,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    }

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01'
        }
    )

    print("Calling Claude Vision API...")
    resp = urllib.request.urlopen(req, timeout=180)
    result = json.loads(resp.read().decode())
    text = result['content'][0]['text']

    if '```json' in text:
        text = text.split('```json')[1].split('```')[0]
    elif '```' in text:
        text = text.split('```')[1].split('```')[0]

    parsed = json.loads(text.strip())

    depths = parsed.get('depths', [])
    module_groups = parsed.get('module_groups', {})
    prices = parsed.get('prices', {})

    total_cells = sum(len(row) for row in prices.values())
    print(f"  Depths: {len(depths)} rows")
    print(f"  Module groups: 1={len(module_groups.get('1',[]))} 2={len(module_groups.get('2',[]))} 3={len(module_groups.get('3',[]))}")
    print(f"  Total cells: {total_cells}")

    return parsed


def flatten_to_rows(parsed, image_info):
    """Convert parsed JSON to flat list of DB rows."""
    rows = []
    module_groups = parsed.get('module_groups', {})
    prices = parsed.get('prices', {})

    width_to_module = {}
    for mod_str, widths in module_groups.items():
        mod = int(mod_str)
        for w in widths:
            w_key = str(w)
            if w_key in width_to_module:
                width_to_module[w_key + '_3mod'] = mod
            else:
                width_to_module[w_key] = mod

    for depth_str, width_prices in prices.items():
        depth = float(depth_str)
        for width_str, price in width_prices.items():
            clean_w = width_str.replace('_3mod', '')
            width = float(clean_w)

            if '_3mod' in width_str:
                mod = width_to_module.get(width_str, 3)
            else:
                mod = width_to_module.get(width_str, 1)

            rows.append({
                'pergola_type': image_info['pergola_type'],
                'lamella_size': image_info['lamella_size'],
                'variant': image_info['variant'],
                'width': depth,
                'length': width,
                'price': float(price),
                'modules': mod
            })

    return rows


def verify_pass(parsed, image_info):
    """Run verification pass on parsed data."""
    print(f"\n--- Verification for {image_info['variant']} {image_info['lamella_size']}mm ---")

    with open(image_info['path'], 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode('utf-8')

    verify_prompt = """Look at this price table image and verify these specific cell values.
For each cell, tell me if the value is CORRECT or what the actual value should be.

Check these cells (format: depth x width = extracted_price):
"""
    prices = parsed.get('prices', {})
    depths = sorted([float(d) for d in prices.keys()])
    sample_cells = []

    if depths:
        first_depth = str(depths[0])
        last_depth = str(depths[-1])
        mid_depth = str(depths[len(depths)//2])
        for d_key in [first_depth, mid_depth, last_depth]:
            d_str = d_key
            for dk in prices.keys():
                if abs(float(dk) - float(d_key)) < 0.01:
                    d_str = dk
                    break
            if d_str in prices:
                widths_in_row = list(prices[d_str].keys())
                for w in [widths_in_row[0], widths_in_row[-1]]:
                    sample_cells.append((d_str, w, prices[d_str][w]))

    for d, w, p in sample_cells:
        verify_prompt += f"- Depth {d}m x Width {w}m = {p}€\n"

    verify_prompt += "\nFor each cell, respond with: depth x width: CORRECT or depth x width: WRONG, actual value is XXXX"

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
                {"type": "text", "text": verify_prompt}
            ]
        }]
    }

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01'
        }
    )

    resp = urllib.request.urlopen(req, timeout=120)
    result = json.loads(resp.read().decode())
    verification_text = result['content'][0]['text']
    print(verification_text)

    corrections = {}
    for line in verification_text.split('\n'):
        if 'WRONG' in line.upper() and 'actual' in line.lower():
            try:
                parts = line.split(':')
                cell_ref = parts[0].strip().lstrip('- ')
                actual_str = line.split('actual value is')[-1].strip().rstrip('.€ ')
                actual_val = int(''.join(c for c in actual_str if c.isdigit()))
                d_str = cell_ref.split('x')[0].strip().rstrip('m ')
                w_str = cell_ref.split('x')[1].strip().split('=')[0].strip().rstrip('m ')
                corrections[(d_str, w_str)] = actual_val
                print(f"  CORRECTION: {d_str} x {w_str} = {actual_val}")
            except Exception:
                pass

    return corrections


def insert_to_db(all_rows):
    """Insert all parsed rows into the database."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("DELETE FROM price_data WHERE pergola_type='B500NEW'")
    deleted = cur.rowcount
    print(f"\nDeleted {deleted} old B500NEW rows")

    insert_sql = """INSERT INTO price_data (pergola_type, lamella_size, variant, width, length, price, modules, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"""

    for row in all_rows:
        cur.execute(insert_sql, (
            row['pergola_type'], row['lamella_size'], row['variant'],
            row['width'], row['length'], row['price'], row['modules']
        ))

    conn.commit()
    print(f"Inserted {len(all_rows)} new variant rows")

    cur.execute("""
        SELECT variant, lamella_size, COUNT(*), MIN(price), MAX(price)
        FROM price_data
        WHERE pergola_type='B500NEW'
        GROUP BY variant, lamella_size
        ORDER BY variant, lamella_size
    """)
    print("\nSummary:")
    for row in cur.fetchall():
        print(f"  {row[0]} {row[1]}mm: {row[2]} rows, price range {row[3]:.0f}-{row[4]:.0f}€")

    cur.close()
    conn.close()


def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    all_rows = []
    all_parsed = []

    for img_info in PRICE_IMAGES:
        if not os.path.exists(img_info['path']):
            print(f"ERROR: Image not found: {img_info['path']}")
            sys.exit(1)

        parsed = parse_price_image(img_info)
        all_parsed.append((parsed, img_info))

        rows = flatten_to_rows(parsed, img_info)
        print(f"  Flattened to {len(rows)} DB rows")
        all_rows.extend(rows)

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Total rows to insert: {len(all_rows)}")

    print(f"\n{'='*60}")
    print("VERIFICATION PASS")
    for parsed, img_info in all_parsed:
        corrections = verify_pass(parsed, img_info)
        if corrections:
            for (d_str, w_str), actual_val in corrections.items():
                for row in all_rows:
                    if (row['variant'] == img_info['variant'] and
                        row['lamella_size'] == img_info['lamella_size'] and
                        abs(row['width'] - float(d_str)) < 0.01 and
                        abs(row['length'] - float(w_str.replace('_3mod',''))) < 0.01):
                        old_price = row['price']
                        row['price'] = float(actual_val)
                        print(f"  Applied correction: {d_str}x{w_str} {old_price} → {actual_val}")
        time.sleep(1)

    insert_to_db(all_rows)
    print("\nMigration complete!")


if __name__ == '__main__':
    main()
