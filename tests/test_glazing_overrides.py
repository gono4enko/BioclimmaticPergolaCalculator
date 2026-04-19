"""Regression tests for admin-editable S500/S100 glazing pricing.

Verifies that overrides written to the in-memory matrices and the
`GLAZING_SETTINGS` dict are picked up by both calc functions, and that
`_ensure_glazing_loaded()` is invoked from the calc entry points (so
DB overrides are applied even when no surcharge code path runs)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app.services import calculator as c


def _baseline_then_override(target_pd, conf, w, h, calc_fn, calc_args):
    base = calc_fn(*calc_args)
    cd = target_pd[conf]
    wi = c._glaze_ci(cd['w'], w)
    hi = c._glaze_ci(cd['h'], h)
    original = cd['p'][hi][wi]
    cd['p'][hi][wi] = original + 999
    bumped = calc_fn(*calc_args)
    cd['p'][hi][wi] = original
    return base, bumped


def test_s500_matrix_override_applied():
    base, bumped = _baseline_then_override(
        c.GLAZING_PD, '3', 3.0, 2.0,
        c.glazing_calc_price, (3.0, 2.0, 3),
    )
    expected = 999.0 * (1 + c._gs('S500_DELIVERY_PCT') / 100.0 * (1 + c._gs('S500_MARKUP_PCT') / 100.0))
    assert round(bumped - base, 2) == round(expected, 2)


def test_s100_matrix_override_applied_with_default_color_and_glass():
    # default args: color='ral9t08', glass='transparent' — no surcharge path.
    base, bumped = _baseline_then_override(
        c.S100_PD, '3', 3.0, 2.0,
        c.s100_calc_price, (3.0, 2.0, 3),
    )
    assert bumped == base + 999, (base, bumped)


def test_glazing_settings_override_changes_surcharge():
    base = c.glazing_calc_price(3.0, 2.0, 3)
    c.GLAZING_SETTINGS['S500_MARKUP_PCT'] = 50.0
    try:
        bumped = c.glazing_calc_price(3.0, 2.0, 3)
        assert bumped != base
    finally:
        c.GLAZING_SETTINGS['S500_MARKUP_PCT'] = c._GLAZING_SETTINGS_DEFAULTS['S500_MARKUP_PCT']


def test_clear_glazing_cache_resets_matrix_to_defaults():
    cd = c.GLAZING_PD['3']
    original = cd['p'][0][0]
    cd['p'][0][0] = 12345.0
    c.clear_glazing_cache()
    # Trigger reload: any calc call funnels through _ensure_glazing_loaded.
    c.glazing_calc_price(1.8, 1.7, 3)
    assert c.GLAZING_PD['3']['p'][0][0] == original
