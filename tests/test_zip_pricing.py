"""Unit tests for zip_calc_price() — fabric surcharges, drive premiums, and ZIP type selection."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app.services import calculator as c


# ---------------------------------------------------------------------------
# Fabric surcharge tests
# ---------------------------------------------------------------------------

def test_soltis_costs_more_than_veozip():
    """Soltis fabric adds 15 EUR/m² over veozip (base fabric)."""
    w, h = 2.0, 2.5
    result_veozip = c.zip_calc_price(w, h, fabric='veozip')
    result_soltis = c.zip_calc_price(w, h, fabric='soltis')

    assert result_veozip['fabric_eur'] == 0.0, "veozip should have no fabric surcharge"
    assert result_soltis['fabric_eur'] > 0.0, "soltis should have a positive fabric surcharge"

    area = result_soltis['area']
    expected_surcharge = round(area * 15.0, 2)
    assert result_soltis['fabric_eur'] == expected_surcharge, (
        f"Expected Soltis surcharge {expected_surcharge} EUR, got {result_soltis['fabric_eur']}"
    )


def test_soltis_total_is_higher_than_veozip_by_surcharge_plus_assembly():
    """The total price difference between Soltis and Veozip equals fabric_eur * (1 + assembly%)."""
    w, h = 3.0, 2.0
    result_veozip = c.zip_calc_price(w, h, fabric='veozip')
    result_soltis = c.zip_calc_price(w, h, fabric='soltis')

    fabric_diff = result_soltis['fabric_eur'] - result_veozip['fabric_eur']
    assembly_pct = c._zip_setting('ZIP_ASSEMBLY_PCT') / 100.0
    expected_total_diff = round(fabric_diff * (1 + assembly_pct), 2)
    actual_total_diff = round(result_soltis['total_eur'] - result_veozip['total_eur'], 2)

    assert actual_total_diff == expected_total_diff, (
        f"Total diff {actual_total_diff} EUR doesn't match expected {expected_total_diff} EUR"
    )


def test_soltis_surcharge_scales_with_area():
    """Soltis surcharge is proportional to awning area (15 EUR/m²)."""
    surcharge_per_m2 = 15.0

    r1 = c.zip_calc_price(2.0, 2.0, fabric='soltis')
    r2 = c.zip_calc_price(3.0, 2.0, fabric='soltis')

    diff_area = r2['area'] - r1['area']
    diff_fabric_eur = round(r2['fabric_eur'] - r1['fabric_eur'], 2)

    assert diff_fabric_eur == round(diff_area * surcharge_per_m2, 2), (
        f"Fabric surcharge scaling mismatch: area diff={diff_area}, fabric diff={diff_fabric_eur}"
    )


# ---------------------------------------------------------------------------
# Drive premium tests
# ---------------------------------------------------------------------------

def test_somfy_small_costs_more_than_simu():
    """Somfy (small) costs 5 EUR more than SIMU for a small opening (w<=3.5, h<=4.0)."""
    w, h = 2.0, 2.5  # small: w <= 3.5 and h <= 4.0
    result_simu = c.zip_calc_price(w, h, drive='simu')
    result_somfy = c.zip_calc_price(w, h, drive='somfy')

    assert result_somfy['drive_eur'] == 180.0, (
        f"Somfy small drive cost should be 180 EUR, got {result_somfy['drive_eur']}"
    )
    assert result_simu['drive_eur'] == 175.0, (
        f"SIMU drive cost should be 175 EUR, got {result_simu['drive_eur']}"
    )
    assert result_somfy['drive_eur'] > result_simu['drive_eur'], (
        "Somfy should be more expensive than SIMU"
    )


def test_somfy_large_premium_over_simu():
    """Somfy (large) costs 55 EUR more than SIMU for a large opening."""
    w, h = 4.0, 4.5  # large: h > 4.0
    result_simu = c.zip_calc_price(w, h, drive='simu', zip_type_override='ZIP130')
    result_somfy = c.zip_calc_price(w, h, drive='somfy', zip_type_override='ZIP130')

    assert result_somfy['drive_eur'] == 230.0, (
        f"Somfy large drive cost should be 230 EUR, got {result_somfy['drive_eur']}"
    )
    assert result_simu['drive_eur'] == 175.0, (
        f"SIMU drive cost should be 175 EUR, got {result_simu['drive_eur']}"
    )
    assert result_somfy['drive_eur'] - result_simu['drive_eur'] == 55.0


def test_somfy_small_vs_large_threshold():
    """Somfy price jumps from 180 to 230 when opening exceeds small dimensions."""
    # Small: w <= 3.5 AND h <= 4.0
    small = c.zip_calc_price(3.5, 4.0, drive='somfy')
    # Large: h > 4.0
    large = c.zip_calc_price(3.5, 4.5, drive='somfy', zip_type_override='ZIP130')

    assert small['drive_eur'] == 180.0, f"Small Somfy expected 180 EUR, got {small['drive_eur']}"
    assert large['drive_eur'] == 230.0, f"Large Somfy expected 230 EUR, got {large['drive_eur']}"


# ---------------------------------------------------------------------------
# ZIP100 vs ZIP130 auto-selection tests
# ---------------------------------------------------------------------------

def test_zip100_selected_for_small_opening():
    """Openings within ZIP100 limits (w<=4.0, h<=3.5) should use ZIP100."""
    result = c.zip_calc_price(3.0, 2.5)
    assert result['zip_type'] == 'ZIP100', (
        f"Expected ZIP100 for 3.0x2.5, got {result['zip_type']}"
    )


def test_zip130_selected_when_width_exceeds_zip100_limit():
    """Opening wider than 4.0m should automatically select ZIP130."""
    result = c.zip_calc_price(4.5, 2.5)
    assert result['zip_type'] == 'ZIP130', (
        f"Expected ZIP130 for 4.5x2.5, got {result['zip_type']}"
    )


def test_zip130_selected_when_height_exceeds_zip100_limit():
    """Opening taller than 3.5m should automatically select ZIP130."""
    result = c.zip_calc_price(3.0, 4.0)
    assert result['zip_type'] == 'ZIP130', (
        f"Expected ZIP130 for 3.0x4.0, got {result['zip_type']}"
    )


def test_zip100_at_exact_boundary():
    """An opening exactly at the ZIP100 boundary (4.0 x 3.5) should use ZIP100."""
    result = c.zip_calc_price(4.0, 3.5)
    assert result['zip_type'] == 'ZIP100', (
        f"Expected ZIP100 at exact boundary 4.0x3.5, got {result['zip_type']}"
    )


def test_zip_type_override_forces_zip130():
    """zip_type_override='ZIP130' forces ZIP130 even for small openings."""
    result = c.zip_calc_price(2.0, 2.0, zip_type_override='ZIP130')
    assert result['zip_type'] == 'ZIP130', (
        f"Expected ZIP130 override to take effect, got {result['zip_type']}"
    )


def test_zip130_costs_more_than_zip100_for_same_opening():
    """ZIP130 base price is higher than ZIP100 for the same small opening."""
    r100 = c.zip_calc_price(2.0, 2.0, zip_type_override='ZIP100')
    r130 = c.zip_calc_price(2.0, 2.0, zip_type_override='ZIP130')
    assert r130['base_eur'] >= r100['base_eur'], (
        f"ZIP130 base price ({r130['base_eur']}) should be >= ZIP100 ({r100['base_eur']})"
    )
