"""Regression tests for the glazing price-override admin HTTP flow.

Covers task #74: verifies that

  (1) POST /admin/glazing-save-cell writes an override that flips the output
      of glazing_calc_price / s100_calc_price for the matching grid cell;
  (2) POST /admin/glazing-settings persists a new surcharge value and the
      calculator picks it up on the next call;
  (3) POST /admin/glazing-reset clears overrides so the calculator returns
      factory defaults again.

The suite has two layers:
- Fast mock tests: psycopg2 is patched so no real DB is required.
- DB integration tests: use the actual DATABASE_URL to verify that SQL
  INSERT/DELETE statements are genuinely persisted and reloaded by the
  calculator.  These tests skip automatically when DATABASE_URL is absent.
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app
from flask_app.services import calculator as c

_DB_URL = os.environ.get('DATABASE_URL', '')
_HAS_DB = bool(_DB_URL)
_skip_no_db = pytest.mark.skipif(not _HAS_DB, reason='DATABASE_URL not set')


# ---------------------------------------------------------------------------
# Mock-DB helpers
# ---------------------------------------------------------------------------

def _make_cursor(overrides_rows=None, settings_rows=None, rowcount=0):
    """Cursor whose fetchall() yields overrides first, then settings."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchall.side_effect = [
        list(overrides_rows or []),
        list(settings_rows or []),
    ]
    cur.rowcount = rowcount
    return cur


def _make_conn(cur):
    conn = MagicMock()
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cur
    return conn


def _write_conn():
    """A connection used only for writes (INSERT/DELETE); no fetchall needed."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.rowcount = 1
    return _make_conn(cur)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-secret'})


@pytest.fixture
def admin_client(app):
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        yield client


# ---------------------------------------------------------------------------
# (1) save-cell flips glazing_calc_price output for S500
# ---------------------------------------------------------------------------

def test_save_cell_flips_s500_price(admin_client):
    """Saving an override via /admin/glazing-save-cell changes the S500 price."""
    c.clear_glazing_cache()
    # With no DATABASE_URL set, _ensure_glazing_loaded uses factory defaults.
    base = c.glazing_calc_price(3.0, 2.0, 3)

    cd = c.GLAZING_PD['3']
    wi = c._glaze_ci(cd['w'], 3.0)
    hi = c._glaze_ci(cd['h'], 2.0)
    w_snap = float(cd['w'][wi])
    h_snap = float(cd['h'][hi])
    new_price = cd['p'][hi][wi] + 999.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[('S500', '3', w_snap, h_snap, new_price)],
        settings_rows=[],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-save-cell', json={
            'system': 'S500', 'config': '3',
            'w': 3.0, 'h': 2.0, 'price': new_price,
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        bumped = c.glazing_calc_price(3.0, 2.0, 3)

    expected_delta = 999.0 * (
        1 + c._GLAZING_SETTINGS_DEFAULTS['S500_DELIVERY_PCT'] / 100.0
        * (1 + c._GLAZING_SETTINGS_DEFAULTS['S500_MARKUP_PCT'] / 100.0)
    )
    assert round(bumped - base, 2) == round(expected_delta, 2), (
        f"base={base}, bumped={bumped}, expected_delta={expected_delta}"
    )


# ---------------------------------------------------------------------------
# (1b) save-cell flips s100_calc_price output for S100
# ---------------------------------------------------------------------------

def test_save_cell_flips_s100_price(admin_client):
    """Saving an override via /admin/glazing-save-cell changes the S100 price."""
    c.clear_glazing_cache()
    base = c.s100_calc_price(3.0, 2.0, 3)

    cd = c.S100_PD['3']
    wi = c._glaze_ci(cd['w'], 3.0)
    hi = c._glaze_ci(cd['h'], 2.0)
    w_snap = float(cd['w'][wi])
    h_snap = float(cd['h'][hi])
    new_price = cd['p'][hi][wi] + 999.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[('S100', '3', w_snap, h_snap, new_price)],
        settings_rows=[],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-save-cell', json={
            'system': 'S100', 'config': '3',
            'w': 3.0, 'h': 2.0, 'price': new_price,
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        bumped = c.s100_calc_price(3.0, 2.0, 3)

    assert bumped == base + 999.0, f"base={base}, bumped={bumped}"


# ---------------------------------------------------------------------------
# (2) glazing-settings surcharge persisted and applied by calculator
# ---------------------------------------------------------------------------

def test_glazing_settings_save_flips_surcharge(admin_client):
    """Saving S500_MARKUP_PCT via /admin/glazing-settings changes the price."""
    c.clear_glazing_cache()
    base = c.glazing_calc_price(3.0, 2.0, 3)

    new_markup = 50.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[],
        settings_rows=[('S500_MARKUP_PCT', new_markup)],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-settings', json={
            'values': {'S500_MARKUP_PCT': new_markup},
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        bumped = c.glazing_calc_price(3.0, 2.0, 3)

    assert bumped != base, f"Expected price to change; base={base}, bumped={bumped}"
    assert bumped > base, (
        f"Higher markup ({new_markup}%) should increase price; "
        f"base={base}, bumped={bumped}"
    )


# ---------------------------------------------------------------------------
# (3) glazing-reset restores factory defaults
# ---------------------------------------------------------------------------

def test_glazing_reset_restores_factory_defaults(admin_client):
    """POST /admin/glazing-reset removes overrides; calculator returns defaults."""
    c.clear_glazing_cache()
    factory_price = c.glazing_calc_price(3.0, 2.0, 3)

    cd = c.GLAZING_PD['3']
    wi = c._glaze_ci(cd['w'], 3.0)
    hi = c._glaze_ci(cd['h'], 2.0)
    cd['p'][hi][wi] += 999.0
    c._GLAZING_LOADED = True

    overridden_price = c.glazing_calc_price(3.0, 2.0, 3)
    assert overridden_price != factory_price, "Override must actually change the price"

    reset_c = _write_conn()
    reload_c = _make_conn(_make_cursor(overrides_rows=[], settings_rows=[]))
    conns = iter([reset_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-reset', json={
            'system': 'S500', 'config': '3',
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        restored_price = c.glazing_calc_price(3.0, 2.0, 3)

    assert round(restored_price, 2) == round(factory_price, 2), (
        f"factory={factory_price}, overridden={overridden_price}, "
        f"restored={restored_price}"
    )


# ---------------------------------------------------------------------------
# DB integration tests  (skipped when DATABASE_URL is absent)
# ---------------------------------------------------------------------------
#
# These tests exercise the real psycopg2 path end-to-end: the HTTP endpoint
# writes to glazing_price_overrides / glazing_settings, the cache is cleared,
# and _ensure_glazing_loaded re-reads the row from the database.  After each
# test all inserted rows are deleted to avoid cross-test contamination.

import psycopg2 as _psycopg2


def _db_conn():
    return _psycopg2.connect(_DB_URL)


def _cleanup_override(system='S500', config='3', w=3.0, h=2.0):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM glazing_price_overrides "
                "WHERE system=%s AND config=%s AND w_dec=%s AND h_dec=%s",
                (system, config, w, h),
            )
        conn.commit()


def _cleanup_setting(key='S500_MARKUP_PCT'):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM glazing_settings WHERE key=%s", (key,))
        conn.commit()


def _fetch_override(system='S500', config='3', w=3.0, h=2.0):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT price FROM glazing_price_overrides "
                "WHERE system=%s AND config=%s AND w_dec=%s AND h_dec=%s",
                (system, config, w, h),
            )
            row = cur.fetchone()
    return row[0] if row else None


def _fetch_setting(key='S500_MARKUP_PCT'):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT value FROM glazing_settings WHERE key=%s", (key,)
            )
            row = cur.fetchone()
    return row[0] if row else None


@_skip_no_db
def test_db_save_cell_persists_and_flips_s500_price(admin_client):
    """Integration: save-cell writes to the real DB; calc picks up the row."""
    factory_cd = c._GLAZING_PD_DEFAULTS['S500']['3']
    wi = c._glaze_ci(factory_cd['w'], 3.0)
    hi = c._glaze_ci(factory_cd['h'], 2.0)
    w_snap = float(factory_cd['w'][wi])
    h_snap = float(factory_cd['h'][hi])
    new_cell_price = factory_cd['p'][hi][wi] + 999.0

    _cleanup_override('S500', '3', w_snap, h_snap)
    c.clear_glazing_cache()
    base = c.glazing_calc_price(3.0, 2.0, 3)

    try:
        resp = admin_client.post('/admin/glazing-save-cell', json={
            'system': 'S500', 'config': '3',
            'w': w_snap, 'h': h_snap, 'price': new_cell_price,
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        stored = _fetch_override('S500', '3', w_snap, h_snap)
        assert stored is not None, "Override row not found in glazing_price_overrides"
        assert abs(float(stored) - new_cell_price) < 0.01, (
            f"DB row price {stored} != expected {new_cell_price}"
        )

        c.clear_glazing_cache()
        bumped = c.glazing_calc_price(3.0, 2.0, 3)
        expected_delta = 999.0 * (
            1 + c._GLAZING_SETTINGS_DEFAULTS['S500_DELIVERY_PCT'] / 100.0
            * (1 + c._GLAZING_SETTINGS_DEFAULTS['S500_MARKUP_PCT'] / 100.0)
        )
        assert round(bumped - base, 2) == round(expected_delta, 2), (
            f"base={base}, bumped={bumped}, expected_delta={expected_delta}"
        )
    finally:
        _cleanup_override('S500', '3', w_snap, h_snap)
        c.clear_glazing_cache()


@_skip_no_db
def test_db_glazing_settings_persists_and_flips_surcharge(admin_client):
    """Integration: settings endpoint persists to DB; calc reloads the value."""
    _cleanup_setting('S500_MARKUP_PCT')
    c.clear_glazing_cache()
    base = c.glazing_calc_price(3.0, 2.0, 3)

    new_markup = 50.0
    try:
        resp = admin_client.post('/admin/glazing-settings', json={
            'values': {'S500_MARKUP_PCT': new_markup},
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        stored = _fetch_setting('S500_MARKUP_PCT')
        assert stored is not None, "Setting row not found in glazing_settings"
        assert abs(float(stored) - new_markup) < 0.01, (
            f"DB row value {stored} != expected {new_markup}"
        )

        c.clear_glazing_cache()
        bumped = c.glazing_calc_price(3.0, 2.0, 3)
        assert bumped > base, (
            f"Higher markup ({new_markup}%) should raise price; "
            f"base={base}, bumped={bumped}"
        )
    finally:
        _cleanup_setting('S500_MARKUP_PCT')
        c.clear_glazing_cache()


@_skip_no_db
def test_db_glazing_reset_removes_row_and_restores_price(admin_client):
    """Integration: reset endpoint deletes the row; calc returns factory value."""
    factory_cd = c._GLAZING_PD_DEFAULTS['S500']['3']
    wi = c._glaze_ci(factory_cd['w'], 3.0)
    hi = c._glaze_ci(factory_cd['h'], 2.0)
    w_snap = float(factory_cd['w'][wi])
    h_snap = float(factory_cd['h'][hi])
    new_cell_price = factory_cd['p'][hi][wi] + 999.0

    _cleanup_override('S500', '3', w_snap, h_snap)

    c.clear_glazing_cache()
    factory_price = c.glazing_calc_price(3.0, 2.0, 3)

    with _db_conn() as conn:
        with conn.cursor() as cur:
            c._ensure_glazing_tables(cur)
            cur.execute(
                "INSERT INTO glazing_price_overrides "
                "(system, config, w_dec, h_dec, price, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, NOW()) "
                "ON CONFLICT (system, config, w_dec, h_dec) "
                "DO UPDATE SET price = EXCLUDED.price, updated_at = NOW()",
                ('S500', '3', w_snap, h_snap, new_cell_price),
            )
        conn.commit()

    c.clear_glazing_cache()
    overridden_price = c.glazing_calc_price(3.0, 2.0, 3)
    assert overridden_price != factory_price, (
        "Override must change the price before reset"
    )

    try:
        resp = admin_client.post('/admin/glazing-reset', json={
            'system': 'S500', 'config': '3',
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        still_there = _fetch_override('S500', '3', w_snap, h_snap)
        assert still_there is None, (
            f"Override row still in DB after reset: price={still_there}"
        )

        c.clear_glazing_cache()
        restored_price = c.glazing_calc_price(3.0, 2.0, 3)
        assert round(restored_price, 2) == round(factory_price, 2), (
            f"factory={factory_price}, overridden={overridden_price}, "
            f"restored={restored_price}"
        )
    finally:
        _cleanup_override('S500', '3', w_snap, h_snap)
        c.clear_glazing_cache()


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
