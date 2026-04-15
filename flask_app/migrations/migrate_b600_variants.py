#!/usr/bin/env python3
"""
Migration: Parse B600 variant price tables from images via Claude Vision API.
Variants: Standard (PIR), Light (PIR Light)
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
        'path': 'attached_assets/Снимок_экрана_2026-04-15_в_20.16.00_1776273364235.png',
        'pergola_type': 'B600',
        'lamella_size': 'PIR',
        'variant': 'Standard',
        'description': 'B600 PIR Bioclimatic. Пергола с сэндвич панелями PIR. 1 модуль: widths 2.5, 3.0, 3.5, 4.0, 4.5, 5.0. 2 модуля: widths 6.0, 7.0, 8.0, 9.0, 10.0. 3 модуля: widths 10.5, 13.0, 15.0. Вынос от 2.5 до 8.0m с шагом 0.5m. Note: 5.0 and 10.0 and 15.0 columns are marked with ** (без снеговой нагрузки)'
    },
    {
        'path': 'attached_assets/Снимок_экрана_2026-04-15_в_20.16.16_1776273379866.png',
        'pergola_type': 'B600',
        'lamella_size': 'PIR',
        'variant': 'Light',
        'description': 'B600 PIR Light Bioclimatic. Пергола с сэндвич панелями PIR Light. 1 модуль: widths 2.5, 3.0, 3.5, 4.0. 2 модуля: widths 5.0, 6.0, 7.0, 8.0. 3 модуля: widths 7.5, 9.0, 10.5, 12.0. Вынос от 2.5 до 8.0m с шагом 0.5m'
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
5. Some width values appear in BOTH 2-module and 3-module groups (e.g., 7.5, 9.0, 10.5). Include them in both groups and list their prices. Use keys like "7.5" for 2-module and "7.5_3mod" for 3-module if the same width appears in multiple module groups.
6. Pay careful attention to 4-5 digit numbers. Common OCR errors: confusing 3/8, 5/6, 1/7

Return ONLY valid JSON, no markdown formatting, no extra text."""


def parse_price_image(image_info):
    path = image_info['path']
    print(f"\n{'='*60}")
    print(f"Parsing: {image_info['variant']} ({image_info['lamella_size']})")
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
    rows = []
    module_groups = parsed.get('module_groups', {})
    prices = parsed.get('prices', {})

    width_to_module = {}
    for mod_str, widths in module_groups.items():
        mod = int(mod_str)
        for w in widths:
            w_key = str(w)
            if w_key not in width_to_module:
                width_to_module[w_key] = mod

    import re
    for depth_str, width_prices in prices.items():
        depth = float(depth_str)
        for width_str, price in width_prices.items():
            suffix_match = re.search(r'_(\d+)mod', width_str)
            clean_w = re.sub(r'_\d+mod', '', width_str)
            width = float(clean_w)

            if suffix_match:
                mod = int(suffix_match.group(1))
            else:
                mod = width_to_module.get(str(width), 1)

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
    print(f"\n--- Verification for {image_info['variant']} ---")

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
                import re
                nums = re.findall(r'[\d.]+', line)
                if len(nums) >= 3:
                    d_val = None
                    w_val = None
                    for i, n in enumerate(nums):
                        if '.' in n:
                            if d_val is None:
                                d_val = n
                            elif w_val is None:
                                w_val = n
                    actual_str = line.split('actual value is')[-1].strip().rstrip('.€ ')
                    actual_val = int(''.join(c for c in actual_str if c.isdigit()))
                    if d_val and w_val:
                        corrections[(d_val, w_val)] = actual_val
                        print(f"  CORRECTION: {d_val} x {w_val} = {actual_val}")
            except Exception as e:
                print(f"  Could not parse correction: {line} ({e})")
                pass

    return corrections


def insert_to_db(all_rows):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("DELETE FROM price_data WHERE pergola_type='B600'")
    deleted = cur.rowcount
    print(f"\nDeleted {deleted} old B600 rows")

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
        WHERE pergola_type='B600'
        GROUP BY variant, lamella_size
        ORDER BY variant, lamella_size
    """)
    print("\nSummary:")
    for row in cur.fetchall():
        print(f"  {row[0]} {row[1]}: {row[2]} rows, price range {row[3]:.0f}-{row[4]:.0f}€")

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
