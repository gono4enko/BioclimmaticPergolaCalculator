"""Regression tests for the W500/W600/W700 guillotine glazing price-override
admin HTTP flow.

Covers task #84 — verifies that:

  (1) POST /admin/glazing-save-cell writes an override that flips the output
      of w_calc_price() for the matching W-series grid cell;
  (2) POST /admin/glazing-settings persists W-series surcharge values
      (W_RAL_SPECIAL_PCT, W_MULTIFUNCTIONAL_PCT, W500/600/700_PLAVNIK_RATE)
      and the calculator picks them up on the next call;
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
# Mock-DB helpers (mirrors test_glazing_admin_flow.py pattern)
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
# Helpers to retrieve a snapped (w, h) grid point for a W-series system
# ---------------------------------------------------------------------------

def _w_snap(series, w, h):
    """Return (w_snap, h_snap, wi, hi) — snapped values and their indices."""
    pd = c._GLAZING_PD_DEFAULTS[series]['all']
    wi = c._glaze_ci(pd['w'], w)
    hi = c._glaze_ci(pd['h'], h)
    return float(pd['w'][wi]), float(pd['h'][hi]), wi, hi


def _factory_cell(series, w_snap, h_snap):
    """Return the factory (unmodified) price at a given grid cell."""
    pd = c._GLAZING_PD_DEFAULTS[series]['all']
    wi = c._glaze_ci(pd['w'], w_snap)
    hi = c._glaze_ci(pd['h'], h_snap)
    return pd['p'][hi][wi]


# ===========================================================================
# (1) save-cell flips w_calc_price for each W series
# ===========================================================================

@pytest.mark.parametrize('series,test_w,test_h', [
    ('W500', 2.0, 2.0),
    ('W600', 2.0, 2.0),
    ('W700', 2.0, 2.0),
])
def test_save_cell_flips_price(admin_client, series, test_w, test_h):
    """Saving an override via /admin/glazing-save-cell changes w_calc_price."""
    c.clear_glazing_cache()
    base = c.w_calc_price(series, test_w, test_h, plavnik=False)

    w_snap, h_snap, wi, hi = _w_snap(series, test_w, test_h)
    factory_cell = _factory_cell(series, w_snap, h_snap)
    new_cell_price = factory_cell + 999.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[(series, 'all', w_snap, h_snap, new_cell_price)],
        settings_rows=[],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-save-cell', json={
            'system': series, 'config': 'all',
            'w': test_w, 'h': test_h, 'price': new_cell_price,
        })
        assert resp.status_code == 200, resp.get_data(as_text=True)
        assert resp.get_json().get('ok') is True

        bumped = c.w_calc_price(series, test_w, test_h, plavnik=False)

    assert round(bumped - base, 2) == round(999.0, 2), (
        f"series={series}: base={base}, bumped={bumped}"
    )


# ===========================================================================
# (2) glazing-settings surcharges applied by w_calc_price
# ===========================================================================

def test_w_ral_special_pct_surcharge_applied(admin_client):
    """Saving W_RAL_SPECIAL_PCT changes the ral_special surcharge in w_calc_price."""
    c.clear_glazing_cache()
    base = c.w_calc_price('W500', 2.0, 2.0, color='ral_special', plavnik=False)

    new_pct = 20.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[],
        settings_rows=[('W_RAL_SPECIAL_PCT', new_pct)],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-settings', json={
            'values': {'W_RAL_SPECIAL_PCT': new_pct},
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        bumped = c.w_calc_price('W500', 2.0, 2.0, color='ral_special', plavnik=False)

    assert bumped > base, (
        f"Higher W_RAL_SPECIAL_PCT ({new_pct}%) should raise price; "
        f"base={base}, bumped={bumped}"
    )


def test_w_multifunctional_pct_surcharge_applied(admin_client):
    """Saving W_MULTIFUNCTIONAL_PCT changes the multifunctional surcharge."""
    c.clear_glazing_cache()
    base = c.w_calc_price('W500', 2.0, 2.0, glass='multifunctional', plavnik=False)

    new_pct = 25.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[],
        settings_rows=[('W_MULTIFUNCTIONAL_PCT', new_pct)],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-settings', json={
            'values': {'W_MULTIFUNCTIONAL_PCT': new_pct},
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        bumped = c.w_calc_price('W500', 2.0, 2.0, glass='multifunctional', plavnik=False)

    assert bumped > base, (
        f"Higher W_MULTIFUNCTIONAL_PCT ({new_pct}%) should raise price; "
        f"base={base}, bumped={bumped}"
    )


@pytest.mark.parametrize('series,key,w_test', [
    ('W500', 'W500_PLAVNIK_RATE', 3.5),
    ('W600', 'W600_PLAVNIK_RATE', 3.5),
    ('W700', 'W700_PLAVNIK_RATE', 3.5),
])
def test_plavnik_rate_surcharge_applied(admin_client, series, key, w_test):
    """Doubling PLAVNIK_RATE increases the plavnik add-on in w_calc_price."""
    c.clear_glazing_cache()
    default_rate = c._GLAZING_SETTINGS_DEFAULTS[key]
    base = c.w_calc_price(series, w_test, 2.0, plavnik=True)

    new_rate = default_rate * 2.0

    write_c = _write_conn()
    reload_c = _make_conn(_make_cursor(
        overrides_rows=[],
        settings_rows=[(key, new_rate)],
    ))
    conns = iter([write_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-settings', json={
            'values': {key: new_rate},
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        bumped = c.w_calc_price(series, w_test, 2.0, plavnik=True)

    expected_delta = round(default_rate * w_test, 2)
    assert round(bumped - base, 2) == expected_delta, (
        f"{series} {key}: base={base}, bumped={bumped}, "
        f"expected_delta={expected_delta}"
    )


# ===========================================================================
# (3) glazing-reset restores factory defaults for each W series
# ===========================================================================

@pytest.mark.parametrize('series,test_w,test_h', [
    ('W500', 2.0, 2.0),
    ('W600', 2.0, 2.0),
    ('W700', 2.0, 2.0),
])
def test_reset_restores_factory_defaults(admin_client, series, test_w, test_h):
    """POST /admin/glazing-reset clears W-series overrides; calc returns defaults."""
    c.clear_glazing_cache()
    factory_price = c.w_calc_price(series, test_w, test_h, plavnik=False)

    configs = c._glazing_pd_for(series)
    pd = configs['all']
    wi = c._glaze_ci(pd['w'], test_w)
    hi = c._glaze_ci(pd['h'], test_h)
    pd['p'][hi][wi] += 999.0
    c._GLAZING_LOADED = True

    overridden_price = c.w_calc_price(series, test_w, test_h, plavnik=False)
    assert overridden_price != factory_price, "Override must actually change the price"

    reset_c = _write_conn()
    reload_c = _make_conn(_make_cursor(overrides_rows=[], settings_rows=[]))
    conns = iter([reset_c, reload_c])

    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}), \
         patch('psycopg2.connect', side_effect=lambda *a, **kw: next(conns)):
        resp = admin_client.post('/admin/glazing-reset', json={
            'system': series,
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        restored_price = c.w_calc_price(series, test_w, test_h, plavnik=False)

    assert round(restored_price, 2) == round(factory_price, 2), (
        f"{series}: factory={factory_price}, overridden={overridden_price}, "
        f"restored={restored_price}"
    )


# ===========================================================================
# DB integration tests  (skipped when DATABASE_URL is absent)
# ===========================================================================

import psycopg2 as _psycopg2


def _db_conn():
    return _psycopg2.connect(_DB_URL)


def _cleanup_override(system, config, w, h):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM glazing_price_overrides "
                "WHERE system=%s AND config=%s AND w_dec=%s AND h_dec=%s",
                (system, config, w, h),
            )
        conn.commit()


def _cleanup_setting(key):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM glazing_settings WHERE key=%s", (key,))
        conn.commit()


def _fetch_override(system, config, w, h):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT price FROM glazing_price_overrides "
                "WHERE system=%s AND config=%s AND w_dec=%s AND h_dec=%s",
                (system, config, w, h),
            )
            row = cur.fetchone()
    return row[0] if row else None


def _fetch_setting(key):
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT value FROM glazing_settings WHERE key=%s", (key,)
            )
            row = cur.fetchone()
    return row[0] if row else None


@_skip_no_db
@pytest.mark.parametrize('series,test_w,test_h', [
    ('W500', 2.0, 2.0),
    ('W600', 2.0, 2.0),
    ('W700', 2.0, 2.0),
])
def test_db_save_cell_persists_and_flips_price(admin_client, series, test_w, test_h):
    """Integration: save-cell writes to real DB; w_calc_price picks up the row."""
    factory_pd = c._GLAZING_PD_DEFAULTS[series]['all']
    w_snap, h_snap, wi, hi = _w_snap(series, test_w, test_h)
    factory_cell = factory_pd['p'][hi][wi]
    new_cell_price = factory_cell + 999.0

    _cleanup_override(series, 'all', w_snap, h_snap)
    c.clear_glazing_cache()
    base = c.w_calc_price(series, test_w, test_h, plavnik=False)

    try:
        resp = admin_client.post('/admin/glazing-save-cell', json={
            'system': series, 'config': 'all',
            'w': w_snap, 'h': h_snap, 'price': new_cell_price,
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        stored = _fetch_override(series, 'all', w_snap, h_snap)
        assert stored is not None, f"Override row not found for {series}"
        assert abs(float(stored) - new_cell_price) < 0.01, (
            f"DB row price {stored} != expected {new_cell_price}"
        )

        c.clear_glazing_cache()
        bumped = c.w_calc_price(series, test_w, test_h, plavnik=False)
        assert round(bumped - base, 2) == round(999.0, 2), (
            f"{series}: base={base}, bumped={bumped}"
        )
    finally:
        _cleanup_override(series, 'all', w_snap, h_snap)
        c.clear_glazing_cache()


@_skip_no_db
@pytest.mark.parametrize('key,series', [
    ('W_RAL_SPECIAL_PCT', 'W500'),
    ('W_MULTIFUNCTIONAL_PCT', 'W500'),
    ('W500_PLAVNIK_RATE', 'W500'),
    ('W600_PLAVNIK_RATE', 'W600'),
    ('W700_PLAVNIK_RATE', 'W700'),
])
def test_db_glazing_settings_persists_w_surcharge(admin_client, key, series):
    """Integration: W-series settings saved to DB and reloaded by calculator."""
    _cleanup_setting(key)
    c.clear_glazing_cache()

    new_value = 99.0

    try:
        resp = admin_client.post('/admin/glazing-settings', json={
            'values': {key: new_value},
        })
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        stored = _fetch_setting(key)
        assert stored is not None, f"Setting row not found for key={key}"
        assert abs(float(stored) - new_value) < 0.01, (
            f"DB value {stored} != expected {new_value}"
        )

        c.clear_glazing_cache()
        assert abs(c._gs(key) - new_value) < 0.01, (
            f"_gs({key!r}) returned {c._gs(key)} instead of {new_value}"
        )
    finally:
        _cleanup_setting(key)
        c.clear_glazing_cache()


@_skip_no_db
@pytest.mark.parametrize('series,test_w,test_h', [
    ('W500', 2.0, 2.0),
    ('W600', 2.0, 2.0),
    ('W700', 2.0, 2.0),
])
def test_db_reset_removes_row_and_restores_price(admin_client, series, test_w, test_h):
    """Integration: reset endpoint deletes the W-series row; calc returns factory."""
    w_snap, h_snap, wi, hi = _w_snap(series, test_w, test_h)
    factory_cell = _factory_cell(series, w_snap, h_snap)
    new_cell_price = factory_cell + 999.0

    _cleanup_override(series, 'all', w_snap, h_snap)

    c.clear_glazing_cache()
    factory_price = c.w_calc_price(series, test_w, test_h, plavnik=False)

    with _db_conn() as conn:
        with conn.cursor() as cur:
            c._ensure_glazing_tables(cur)
            cur.execute(
                "INSERT INTO glazing_price_overrides "
                "(system, config, w_dec, h_dec, price, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, NOW()) "
                "ON CONFLICT (system, config, w_dec, h_dec) "
                "DO UPDATE SET price = EXCLUDED.price, updated_at = NOW()",
                (series, 'all', w_snap, h_snap, new_cell_price),
            )
        conn.commit()

    c.clear_glazing_cache()
    overridden_price = c.w_calc_price(series, test_w, test_h, plavnik=False)
    assert overridden_price != factory_price, (
        f"{series}: override must change the price before reset"
    )

    try:
        resp = admin_client.post('/admin/glazing-reset', json={'system': series})
        assert resp.status_code == 200
        assert resp.get_json().get('ok') is True

        still_there = _fetch_override(series, 'all', w_snap, h_snap)
        assert still_there is None, (
            f"{series}: override row still in DB after reset: price={still_there}"
        )

        c.clear_glazing_cache()
        restored_price = c.w_calc_price(series, test_w, test_h, plavnik=False)
        assert round(restored_price, 2) == round(factory_price, 2), (
            f"{series}: factory={factory_price}, overridden={overridden_price}, "
            f"restored={restored_price}"
        )
    finally:
        _cleanup_override(series, 'all', w_snap, h_snap)
        c.clear_glazing_cache()


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
