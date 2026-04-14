"""
Migration script: Import CSV price data into PostgreSQL price_data table.
Adds updated_at column if missing, then loads all 5 CSV price combinations.
Idempotent — safe to run multiple times (deletes + re-inserts per combination).
"""
import csv
import os
import sys

import psycopg2


FILE_MAPPING = {
    ("B500NEW", "250"): "attached_assets/Price_B500-25.csv",
    ("B500NEW", "200"): "attached_assets/Price_B500-20.csv",
    ("B700NEW", "250"): "attached_assets/Price_B700-25.csv",
    ("B700NEW", "200"): "attached_assets/Price_B700-20.csv",
    ("B600", "PIR"): "attached_assets/Price_B600_PIR.csv",
}


def run_migration(db_url=None):
    db_url = db_url or os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS price_data (
                    id SERIAL PRIMARY KEY,
                    pergola_type VARCHAR(20) NOT NULL,
                    lamella_size VARCHAR(10) NOT NULL,
                    width NUMERIC(6,2) NOT NULL,
                    length NUMERIC(6,2) NOT NULL,
                    price NUMERIC(10,2) NOT NULL,
                    modules INTEGER DEFAULT 1
                )
            """)
            cur.execute("""
                DO $$ BEGIN
                    ALTER TABLE price_data ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
                EXCEPTION WHEN duplicate_column THEN NULL;
                END $$;
            """)
        conn.commit()

    total_inserted = 0

    with psycopg2.connect(db_url) as conn:
        for (ptype, lsize), fpath in FILE_MAPPING.items():
            if not os.path.exists(fpath):
                print(f"SKIP: {fpath} not found")
                continue

            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM price_data WHERE pergola_type=%s AND lamella_size=%s",
                    (ptype, lsize),
                )

                with open(fpath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    delimiter = ";" if ";" in first_line else ","
                    f.seek(0)
                    reader = csv.reader(f, delimiter=delimiter)

                    first_row = next(reader)
                    modules_row = (
                        first_row
                        if "модуль" in " ".join(first_row).lower()
                        else None
                    )
                    header = next(reader) if modules_row else first_row

                    width_values = []
                    module_values = []
                    for i, val in enumerate(header[1:]):
                        if val.strip():
                            try:
                                w = float(val.replace(",", ".").strip())
                                width_values.append(w)
                                mod = 1
                                if modules_row and (i + 1) < len(modules_row):
                                    mod_str = modules_row[i + 1].lower()
                                    if "3 модул" in mod_str:
                                        mod = 3
                                    elif "2 модул" in mod_str:
                                        mod = 2
                                    elif "1 модул" in mod_str:
                                        mod = 1
                                module_values.append(mod)
                            except ValueError:
                                continue

                    count = 0
                    for row in reader:
                        if not row or len(row) <= 1:
                            continue
                        try:
                            depth = float(row[0].strip().replace(",", "."))
                            for i, price_str in enumerate(row[1:]):
                                if i < len(width_values) and price_str.strip():
                                    try:
                                        price = float(
                                            price_str.replace(" ", "").replace(",", ".")
                                        )
                                        width = width_values[i]
                                        mod = (
                                            module_values[i]
                                            if i < len(module_values)
                                            else 1
                                        )
                                        cur.execute(
                                            "INSERT INTO price_data (pergola_type, lamella_size, width, length, price, modules, updated_at) VALUES (%s,%s,%s,%s,%s,%s,NOW())",
                                            (ptype, lsize, depth, width, price, mod),
                                        )
                                        count += 1
                                    except ValueError:
                                        continue
                        except (ValueError, IndexError):
                            continue

                    total_inserted += count
                    print(f"OK: {ptype}/{lsize} — {count} rows from {fpath}")

        conn.commit()

    print(f"\nTotal inserted: {total_inserted}")
    return total_inserted


if __name__ == "__main__":
    run_migration()
