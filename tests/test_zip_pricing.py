"""Unit tests for zip_calc_price() — fabric surcharges, drive premiums, and ZIP type selection."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app.services import calculator as c


# ---------------------------------------------------------------------------
# Default constant snapshot tests
# ---------------------------------------------------------------------------

def test_zip_settings_defaults_fabric_soltis():
    """ZIP_SETTINGS default for Soltis fabric surcharge must be 15 EUR/m²."""
    assert c._ZIP_SETTINGS_DEFAULTS['ZIP_FABRIC_SOLTIS_EUR_M2'] == 15.0, (
        "Default Soltis fabric surcharge changed from expected 15 EUR/m²"
    )


def test_zip_settings_defaults_fabric_copaco():
    """ZIP_SETTINGS default for Copaco fabric surcharge must be 15 EUR/m²."""
    assert c._ZIP_SETTINGS_DEFAULTS['ZIP_FABRIC_COPACO_EUR_M2'] == 15.0, (
        "Default Copaco fabric surcharge changed from expected 15 EUR/m²"
    )


def test_zip_fabric_surcharge_veozip_is_zero():
    """ZIP_FABRIC_SURCHARGE: veozip (base fabric) must have no surcharge."""
    assert c.ZIP_FABRIC_SURCHARGE['veozip'] == 0.0, (
        "veozip surcharge changed from expected 0.0 EUR/m²"
    )


def test_zip_fabric_surcharge_soltis_is_15():
    """ZIP_FABRIC_SURCHARGE: soltis constant must be 15 EUR/m²."""
    assert c.ZIP_FABRIC_SURCHARGE['soltis'] == 15.0, (
        "soltis surcharge constant changed from expected 15 EUR/m²"
    )


def test_zip_fabric_surcharge_copaco_is_15():
    """ZIP_FABRIC_SURCHARGE: copaco constant must be 15 EUR/m²."""
    assert c.ZIP_FABRIC_SURCHARGE['copaco'] == 15.0, (
        "copaco surcharge constant changed from expected 15 EUR/m²"
    )


def test_zip_motor_eur_simu_is_175():
    """SIMU drive motor default must be 175 EUR."""
    assert c._zip_motor_eur('simu', 2.0, 2.5) == 175.0, (
        "SIMU motor price changed from expected 175 EUR"
    )


def test_zip_motor_eur_somfy_small_is_180():
    """Somfy small drive motor default must be 180 EUR (w<=3.5, h<=4.0)."""
    assert c._zip_motor_eur('somfy', 3.5, 4.0) == 180.0, (
        "Somfy small motor price changed from expected 180 EUR"
    )


def test_zip_motor_eur_somfy_large_is_230():
    """Somfy large drive motor default must be 230 EUR (h>4.0)."""
    assert c._zip_motor_eur('somfy', 3.5, 4.5) == 230.0, (
        "Somfy large motor price changed from expected 230 EUR"
    )


def test_zip_motor_eur_decolife_is_130():
    """Decolife drive motor default must be 130 EUR."""
    assert c._zip_motor_eur('decolife', 2.0, 2.5) == 130.0, (
        "Decolife motor price changed from expected 130 EUR"
    )


def test_zip_motor_eur_manual_is_50():
    """Manual drive motor default must be 50 EUR."""
    assert c._zip_motor_eur('manual', 2.0, 2.5) == 50.0, (
        "Manual motor price changed from expected 50 EUR"
    )


def test_zip_settings_reload_resets_to_defaults():
    """Clearing the ZIP cache and reloading must restore all default constant values."""
    original_soltis = c._ZIP_SETTINGS_DEFAULTS['ZIP_FABRIC_SOLTIS_EUR_M2']
    original_copaco = c._ZIP_SETTINGS_DEFAULTS['ZIP_FABRIC_COPACO_EUR_M2']

    c.ZIP_SETTINGS['ZIP_FABRIC_SOLTIS_EUR_M2'] = 999.0
    c.ZIP_SETTINGS['ZIP_FABRIC_COPACO_EUR_M2'] = 999.0

    c.clear_zip_cache()
    c._ensure_zip_loaded()

    assert c.ZIP_SETTINGS['ZIP_FABRIC_SOLTIS_EUR_M2'] == original_soltis, (
        f"After reload, Soltis surcharge should reset to {original_soltis} EUR/m²"
    )
    assert c.ZIP_SETTINGS['ZIP_FABRIC_COPACO_EUR_M2'] == original_copaco, (
        f"After reload, Copaco surcharge should reset to {original_copaco} EUR/m²"
    )


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


def test_copaco_costs_more_than_veozip():
    """Copaco fabric adds 15 EUR/m² over veozip (base fabric)."""
    w, h = 2.0, 2.5
    result_veozip = c.zip_calc_price(w, h, fabric='veozip')
    result_copaco = c.zip_calc_price(w, h, fabric='copaco')

    assert result_veozip['fabric_eur'] == 0.0, "veozip should have no fabric surcharge"
    assert result_copaco['fabric_eur'] > 0.0, "copaco should have a positive fabric surcharge"

    area = result_copaco['area']
    expected_surcharge = round(area * 15.0, 2)
    assert result_copaco['fabric_eur'] == expected_surcharge, (
        f"Expected Copaco surcharge {expected_surcharge} EUR, got {result_copaco['fabric_eur']}"
    )


def test_copaco_total_is_higher_than_veozip_by_surcharge_plus_assembly():
    """The total price difference between Copaco and Veozip equals fabric_eur * (1 + assembly%)."""
    w, h = 3.0, 2.0
    result_veozip = c.zip_calc_price(w, h, fabric='veozip')
    result_copaco = c.zip_calc_price(w, h, fabric='copaco')

    fabric_diff = result_copaco['fabric_eur'] - result_veozip['fabric_eur']
    assembly_pct = c._zip_setting('ZIP_ASSEMBLY_PCT') / 100.0
    expected_total_diff = round(fabric_diff * (1 + assembly_pct), 2)
    actual_total_diff = round(result_copaco['total_eur'] - result_veozip['total_eur'], 2)

    assert actual_total_diff == expected_total_diff, (
        f"Total diff {actual_total_diff} EUR doesn't match expected {expected_total_diff} EUR"
    )


def test_copaco_surcharge_scales_with_area():
    """Copaco surcharge is proportional to awning area (15 EUR/m²)."""
    surcharge_per_m2 = 15.0

    r1 = c.zip_calc_price(2.0, 2.0, fabric='copaco')
    r2 = c.zip_calc_price(3.0, 2.0, fabric='copaco')

    diff_area = r2['area'] - r1['area']
    diff_fabric_eur = round(r2['fabric_eur'] - r1['fabric_eur'], 2)

    assert diff_fabric_eur == round(diff_area * surcharge_per_m2, 2), (
        f"Fabric surcharge scaling mismatch: area diff={diff_area}, fabric diff={diff_fabric_eur}"
    )


def test_copaco_and_soltis_have_same_fabric_eur_for_same_opening():
    """Copaco and Soltis carry the same 15 EUR/m² surcharge — fabric_eur must match for identical openings."""
    for w, h in [(2.0, 2.5), (3.0, 2.0), (4.0, 3.5), (4.5, 4.0)]:
        result_soltis = c.zip_calc_price(w, h, fabric='soltis')
        result_copaco = c.zip_calc_price(w, h, fabric='copaco')

        assert result_copaco['fabric_eur'] == result_soltis['fabric_eur'], (
            f"Copaco and Soltis fabric_eur mismatch for {w}x{h}: "
            f"soltis={result_soltis['fabric_eur']}, copaco={result_copaco['fabric_eur']}"
        )
        assert result_copaco['total_eur'] == result_soltis['total_eur'], (
            f"Copaco and Soltis total_eur mismatch for {w}x{h}: "
            f"soltis={result_soltis['total_eur']}, copaco={result_copaco['total_eur']}"
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
