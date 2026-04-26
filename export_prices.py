#!/usr/bin/env python3
"""Экспорт цен из таблицы price_data в CSV-файлы data/price_tables/.

Создаёт wide-матрицу в формате существующих файлов:
    Row 1: Количество модулей;1 модуль;1 модуль;2 модуля;...
    Row 2: Вылет\\Ширина (м);3.0;3.5;6.0;...
    Data:  2.45;6245;6810;11917;...

Имена файлов:
    Прайс_<TYPE>-<SIZE>.csv               — flat (агрегированный, без варианта)
    Прайс_<TYPE>-<SIZE>_<VARIANT>.csv    — отдельный вариант (Pro/Basic/Light/...)

После запуска все цены лежат в репозитории — БД для переноса не нужна.

Использование:
    python export_prices.py
"""

import csv
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import psycopg2

OUTPUT_DIR = Path("data/price_tables")


def fmt_num(v):
    if v is None or v == "":
        return ""
    if float(v) == int(float(v)):
        return str(int(float(v)))
    return f"{float(v):g}"


def module_label(mc):
    if mc == 1:
        return "1 модуль"
    if 2 <= mc <= 4:
        return f"{mc} модуля"
    return f"{mc} модулей"


def write_matrix_csv(path: Path, entries):
    """entries = list of (modules, db_width, db_length, price).

    В DB схеме:
        db_width  = вылет перголы (rows in CSV)
        db_length = ширина перголы (columns in CSV)
    """
    if not entries:
        return 0

    # Колонки = db_length (ширина перголы), модули привязаны к колонке
    col_modules = {}
    for mod, _, l, _ in entries:
        if l not in col_modules:
            col_modules[l] = mod
        else:
            col_modules[l] = min(col_modules[l], mod)

    cols = sorted(col_modules.keys(), key=lambda l: (col_modules[l], l))
    rows = sorted({w for _, w, _, _ in entries})

    grid = defaultdict(dict)
    for _, w, l, p in entries:
        grid[w][l] = p

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Количество модулей"] + [module_label(col_modules[l]) for l in cols])
        writer.writerow(["Вылет\\Ширина (м)"] + [fmt_num(l) for l in cols])
        for w in rows:
            row_data = [fmt_num(w)]
            for l in cols:
                p = grid[w].get(l)
                row_data.append(fmt_num(p) if p is not None else "")
            writer.writerow(row_data)
    return len(entries)


def main():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        sys.exit("ERROR: DATABASE_URL не задана")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Подключение к БД...")
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pergola_type, lamella_size, variant, modules, width, length, price "
                "FROM price_data "
                "ORDER BY pergola_type, lamella_size, variant NULLS FIRST, modules, width, length"
            )
            rows = cur.fetchall()

    print(f"Получено {len(rows)} строк из price_data")

    # Группировка
    by_variant = defaultdict(list)   # (type, size, variant) -> [(mod, w, l, p), ...]
    by_flat = defaultdict(list)      # (type, size) -> [(mod, w, l, p), ...]   все варианты + null

    for ptype, lsize, variant, modules, w, l, p in rows:
        if w is None or l is None or p is None:
            continue
        v = (variant or "").strip()
        item = (int(modules) if modules else 1, float(w), float(l), float(p))
        by_flat[(ptype, lsize)].append(item)
        if v:
            by_variant[(ptype, lsize, v)].append(item)
        else:
            by_variant[(ptype, lsize, "")].append(item)

    # Дедуп для flat: для дубликатов (w,l) последний выигрывает
    flat_dedup = {}
    for key, entries in by_flat.items():
        seen = {}
        for mod, w, l, p in entries:
            seen[(w, l)] = (mod, w, l, p)
        flat_dedup[key] = list(seen.values())

    # Дедуп для variant
    variant_dedup = {}
    for key, entries in by_variant.items():
        seen = {}
        for mod, w, l, p in entries:
            seen[(w, l)] = (mod, w, l, p)
        variant_dedup[key] = list(seen.values())

    written = []

    # 1) Flat-файлы (для load_price_data)
    for (ptype, lsize), entries in sorted(flat_dedup.items()):
        fname = f"Прайс_{ptype}-{lsize}.csv"
        fpath = OUTPUT_DIR / fname
        n = write_matrix_csv(fpath, entries)
        if n:
            written.append((str(fpath), n, "flat"))

    # 2) Variant-файлы (для load_variant_prices)
    for (ptype, lsize, variant), entries in sorted(variant_dedup.items()):
        if not variant:
            continue   # уже сохранён как flat
        fname = f"Прайс_{ptype}-{lsize}_{variant}.csv"
        fpath = OUTPUT_DIR / fname
        n = write_matrix_csv(fpath, entries)
        if n:
            written.append((str(fpath), n, f"variant={variant}"))

    print()
    print("=" * 78)
    print(f"Создано CSV-файлов: {len(written)}")
    print("=" * 78)
    for fpath, n, kind in written:
        print(f"  [{kind:>16}]  {fpath}  ({n} цен)")
    print()
    print(f"Всего записей: {sum(n for _, n, _ in written)}")
    print(f"Каталог: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
