"""Unit tests for zip_calc_price() — fabric surcharges, drive premiums, and ZIP type selection."""
import os
import sys

import pytest

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


def test_zip_settings_defaults_assembly_pct():
    """ZIP_SETTINGS default for assembly percentage must be 8%."""
    assert c._ZIP_SETTINGS_DEFAULTS['ZIP_ASSEMBLY_PCT'] == 8.0, (
        "Default ZIP assembly percentage changed from expected 8%"
    )


def test_zip_settings_defaults_install_eur_m2():
    """ZIP_SETTINGS default for install rate must be 20 EUR/m²."""
    assert c._ZIP_SETTINGS_DEFAULTS['ZIP_INSTALL_EUR_M2'] == 20.0, (
        "Default ZIP install rate changed from expected 20 EUR/m²"
    )


def test_zip_settings_defaults_color_special_pct():
    """ZIP_SETTINGS default for special color surcharge must be 10%."""
    assert c._ZIP_SETTINGS_DEFAULTS['ZIP_COLOR_SPECIAL_PCT'] == 10.0, (
        "Default ZIP special color percentage changed from expected 10%"
    )


def test_zip_settings_reload_resets_to_defaults():
    """Clearing the ZIP cache and reloading must restore all default constant values."""
    original_soltis = c._ZIP_SETTINGS_DEFAULTS['ZIP_FABRIC_SOLTIS_EUR_M2']
    original_copaco = c._ZIP_SETTINGS_DEFAULTS['ZIP_FABRIC_COPACO_EUR_M2']
    original_assembly = c._ZIP_SETTINGS_DEFAULTS['ZIP_ASSEMBLY_PCT']
    original_install = c._ZIP_SETTINGS_DEFAULTS['ZIP_INSTALL_EUR_M2']
    original_color_special = c._ZIP_SETTINGS_DEFAULTS['ZIP_COLOR_SPECIAL_PCT']

    c.ZIP_SETTINGS['ZIP_FABRIC_SOLTIS_EUR_M2'] = 999.0
    c.ZIP_SETTINGS['ZIP_FABRIC_COPACO_EUR_M2'] = 999.0
    c.ZIP_SETTINGS['ZIP_ASSEMBLY_PCT'] = 999.0
    c.ZIP_SETTINGS['ZIP_INSTALL_EUR_M2'] = 999.0
    c.ZIP_SETTINGS['ZIP_COLOR_SPECIAL_PCT'] = 999.0

    c.clear_zip_cache()
    c._ensure_zip_loaded()

    assert c.ZIP_SETTINGS['ZIP_FABRIC_SOLTIS_EUR_M2'] == original_soltis, (
        f"After reload, Soltis surcharge should reset to {original_soltis} EUR/m²"
    )
    assert c.ZIP_SETTINGS['ZIP_FABRIC_COPACO_EUR_M2'] == original_copaco, (
        f"After reload, Copaco surcharge should reset to {original_copaco} EUR/m²"
    )
    assert c.ZIP_SETTINGS['ZIP_ASSEMBLY_PCT'] == original_assembly, (
        f"After reload, assembly percentage should reset to {original_assembly}%"
    )
    assert c.ZIP_SETTINGS['ZIP_INSTALL_EUR_M2'] == original_install, (
        f"After reload, install rate should reset to {original_install} EUR/m²"
    )
    assert c.ZIP_SETTINGS['ZIP_COLOR_SPECIAL_PCT'] == original_color_special, (
        f"After reload, special color percentage should reset to {original_color_special}%"
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


# ---------------------------------------------------------------------------
# DB override integration tests for ZIP_SETTINGS
# ---------------------------------------------------------------------------

class _FakeCursor:
    def __init__(self, settings_rows, override_rows):
        self._settings_rows = settings_rows
        self._override_rows = override_rows
        self._last_query = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, query, *args, **kwargs):
        self._last_query = query

    def fetchall(self):
        q = (self._last_query or '').lower()
        if 'from zip_price_overrides' in q:
            return list(self._override_rows)
        if 'from zip_settings' in q:
            return list(self._settings_rows)
        return []


class _FakeConn:
    def __init__(self, settings_rows, override_rows):
        self._settings_rows = settings_rows
        self._override_rows = override_rows

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cursor(self):
        return _FakeCursor(self._settings_rows, self._override_rows)

    def commit(self):
        pass


class _FakePsycopg2:
    def __init__(self, settings_rows, override_rows):
        self._settings_rows = settings_rows
        self._override_rows = override_rows

    def connect(self, dsn):
        return _FakeConn(self._settings_rows, self._override_rows)


@pytest.fixture
def restore_zip_state():
    """Ensure ZIP_SETTINGS, overrides, and cache flag are restored after a test."""
    saved_settings = dict(c.ZIP_SETTINGS)
    saved_overrides = dict(c._ZIP_PRICE_OVERRIDES)
    saved_loaded = c._ZIP_LOADED
    saved_db_url = os.environ.get('DATABASE_URL')
    saved_psycopg2 = sys.modules.get('psycopg2')
    try:
        yield
    finally:
        c.ZIP_SETTINGS.clear()
        c.ZIP_SETTINGS.update(saved_settings)
        c._ZIP_PRICE_OVERRIDES.clear()
        c._ZIP_PRICE_OVERRIDES.update(saved_overrides)
        c._ZIP_LOADED = saved_loaded
        if saved_db_url is None:
            os.environ.pop('DATABASE_URL', None)
        else:
            os.environ['DATABASE_URL'] = saved_db_url
        if saved_psycopg2 is None:
            sys.modules.pop('psycopg2', None)
        else:
            sys.modules['psycopg2'] = saved_psycopg2
        c.clear_zip_cache()


def _install_fake_db(monkeypatch, settings_rows, override_rows=()):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://fake/db')
    fake = _FakePsycopg2(settings_rows, override_rows)
    monkeypatch.setitem(sys.modules, 'psycopg2', fake)
    c.clear_zip_cache()


def test_zip_setting_reflects_db_override_assembly_pct(monkeypatch, restore_zip_state):
    """_zip_setting() must return the DB row value, not the hardcoded default, after cache reload."""
    default_assembly = c._ZIP_SETTINGS_DEFAULTS['ZIP_ASSEMBLY_PCT']
    db_value = default_assembly + 17.5
    assert db_value != default_assembly

    _install_fake_db(monkeypatch, settings_rows=[('ZIP_ASSEMBLY_PCT', db_value)])

    assert c._zip_setting('ZIP_ASSEMBLY_PCT') == db_value, (
        f"DB-injected ZIP_ASSEMBLY_PCT ({db_value}) should override default ({default_assembly})"
    )


def test_zip_setting_reflects_db_overrides_for_all_known_keys(monkeypatch, restore_zip_state):
    """All keys in ZIP_SETTINGS must be overridable from the zip_settings DB table."""
    overrides = {
        'ZIP_ASSEMBLY_PCT': 12.34,
        'ZIP_INSTALL_EUR_M2': 42.5,
        'ZIP_COLOR_SPECIAL_PCT': 33.0,
        'ZIP_FABRIC_SOLTIS_EUR_M2': 99.99,
        'ZIP_FABRIC_COPACO_EUR_M2': 77.7,
    }
    for k, v in overrides.items():
        assert c._ZIP_SETTINGS_DEFAULTS[k] != v, f"chosen override for {k} matches default"

    _install_fake_db(monkeypatch, settings_rows=list(overrides.items()))

    for k, v in overrides.items():
        assert c._zip_setting(k) == v, (
            f"_zip_setting({k!r}) should return DB value {v}, got {c._zip_setting(k)}"
        )


def test_zip_setting_unknown_db_key_is_ignored(monkeypatch, restore_zip_state):
    """Unknown keys in zip_settings DB rows must not be added to ZIP_SETTINGS."""
    _install_fake_db(monkeypatch, settings_rows=[('NOT_A_REAL_ZIP_KEY', 1234.0)])
    c._ensure_zip_loaded()
    assert 'NOT_A_REAL_ZIP_KEY' not in c.ZIP_SETTINGS


def test_zip_setting_reverts_to_default_after_cache_clear_without_db(monkeypatch, restore_zip_state):
    """After clearing the cache and removing DATABASE_URL, _zip_setting() returns the default."""
    default_install = c._ZIP_SETTINGS_DEFAULTS['ZIP_INSTALL_EUR_M2']
    _install_fake_db(monkeypatch, settings_rows=[('ZIP_INSTALL_EUR_M2', default_install + 50.0)])
    assert c._zip_setting('ZIP_INSTALL_EUR_M2') == default_install + 50.0

    monkeypatch.delenv('DATABASE_URL', raising=False)
    c.clear_zip_cache()
    assert c._zip_setting('ZIP_INSTALL_EUR_M2') == default_install


# ---------------------------------------------------------------------------
# DB override integration tests for zip_price_overrides (per-cell price)
# ---------------------------------------------------------------------------

def test_zip_cell_price_override_changes_base_eur(monkeypatch, restore_zip_state):
    """A zip_price_overrides DB row must replace the CSV base price for that exact cell
    and change the resulting base_eur returned by zip_calc_price()."""
    # Opening that snaps to ZIP100 cell (w=2.00, h=2.5) without glazing overlay.
    op_w, op_h = 2.0, 2.5

    # First, capture CSV default base price with no DB override.
    _install_fake_db(monkeypatch, settings_rows=[], override_rows=[])
    default_result = c.zip_calc_price(op_w, op_h, fabric='veozip', drive='manual')
    csv_base = default_result['base_eur']
    assert default_result['zip_type'] == 'ZIP100'

    # Now inject a DB override for that exact cell (ZIP100, 2.00, 2.5).
    override_price = csv_base + 321.0
    assert override_price != csv_base

    # Re-install the fake DB with the override row and clear cache so it reloads.
    _install_fake_db(
        monkeypatch,
        settings_rows=[],
        override_rows=[('ZIP100', 2.00, 2.5, override_price)],
    )

    overridden = c.zip_calc_price(op_w, op_h, fabric='veozip', drive='manual')
    assert overridden['zip_type'] == 'ZIP100'
    assert overridden['base_eur'] == round(override_price, 2), (
        f"Expected DB-overridden base_eur={override_price}, "
        f"got {overridden['base_eur']} (csv default was {csv_base})"
    )
    assert overridden['base_eur'] != csv_base, (
        "DB override must differ from the CSV default; otherwise the test is inert."
    )

    # Sanity: total_eur must also shift by the override delta plus assembly%.
    assembly_pct = c._zip_setting('ZIP_ASSEMBLY_PCT') / 100.0
    expected_total_diff = round((override_price - csv_base) * (1 + assembly_pct), 2)
    actual_total_diff = round(overridden['total_eur'] - default_result['total_eur'], 2)
    assert actual_total_diff == expected_total_diff, (
        f"total_eur delta {actual_total_diff} should equal base delta*(1+assembly%) "
        f"= {expected_total_diff}"
    )


def test_zip_cell_price_override_only_affects_matching_cell(monkeypatch, restore_zip_state):
    """A DB override for one (zip_type, w_dec, h_dec) must NOT affect a different cell."""
    # Inject override for ZIP100 at (2.00, 2.5) only.
    _install_fake_db(
        monkeypatch,
        settings_rows=[],
        override_rows=[('ZIP100', 2.00, 2.5, 9999.0)],
    )
    # The overridden cell is affected.
    hit = c.zip_calc_price(2.0, 2.5, fabric='veozip', drive='manual')
    assert hit['zip_type'] == 'ZIP100'
    assert hit['base_eur'] == 9999.0

    # A different cell (different h) must keep its CSV base price.
    miss = c.zip_calc_price(2.0, 1.5, fabric='veozip', drive='manual')
    assert miss['zip_type'] == 'ZIP100'
    assert miss['base_eur'] != 9999.0, (
        "Override for (ZIP100, 2.00, 2.5) must not leak into (ZIP100, 2.00, 1.5)"
    )
