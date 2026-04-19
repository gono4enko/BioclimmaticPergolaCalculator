"""Validation tests for glazing dispatch in calculator.perform_calculation.

Covers task #63: malformed glazing selections must produce a clear error,
not be silently re-priced as the default S500.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from flask_app.services.calculator import perform_calculation


BASE_DIMENSIONS = {"width": 4.0, "length": 3.0, "height": 3.0}
BASE_OPTIONS = {
    "pergola_type": "B500NEW",
    "lamella_type": "B500-25NEW",
    "lamella_size": "250",
    "lighting": [],
    "installation": False,
}


def _calc(glazing_openings):
    opts = dict(BASE_OPTIONS)
    opts["glazing_openings"] = glazing_openings
    return perform_calculation(BASE_DIMENSIONS, opts)


# ---- valid baseline still works ------------------------------------------------

def test_valid_s500_opening_is_priced():
    res = _calc([{
        "side": "front", "bay": 0, "series": "S500",
        "pc": 4, "direction": "right",
        "color": "ral7016", "glass": "transparent", "count": 1,
    }])
    assert "error" not in res, res
    assert res["glazing"]["count"] == 1
    assert res["glazing"]["price"] > 0


def test_valid_s100_opening_is_priced():
    res = _calc([{
        "side": "front", "bay": 0, "series": "S100",
        "pc": 4, "direction": "right",
        "color": "ral9t08", "glass": "transparent", "count": 1,
    }])
    assert "error" not in res, res
    assert res["glazing"]["openings"][0]["series"] == "S100"


# ---- rejection cases -----------------------------------------------------------

def test_missing_series_is_rejected():
    res = _calc([{"side": "front", "bay": 0, "pc": 4,
                  "color": "ral7016", "glass": "transparent"}])
    assert "error" in res
    assert "series" in res["error"].lower()


def test_unknown_series_is_rejected():
    res = _calc([{"side": "front", "bay": 0, "series": "S999",
                  "pc": 4, "color": "ral7016", "glass": "transparent"}])
    assert "error" in res
    assert "S999" in res["error"]


def test_s100_with_s500_color_is_rejected():
    # ral7016 belongs to S500, not S100.
    res = _calc([{"side": "front", "bay": 0, "series": "S100",
                  "pc": 4, "color": "ral7016", "glass": "transparent"}])
    assert "error" in res
    assert "color" in res["error"].lower()


def test_s500_with_s100_color_is_rejected():
    # ral9t08 belongs to S100, not S500.
    res = _calc([{"side": "front", "bay": 0, "series": "S500",
                  "pc": 4, "color": "ral9t08", "glass": "transparent"}])
    assert "error" in res
    assert "color" in res["error"].lower()


def test_s100_panel_count_outside_allowed_set_is_rejected():
    # 5 is not in S100_PC_ALLOWED = (3, 4, 6, 8, 12).
    res = _calc([{"side": "front", "bay": 0, "series": "S100",
                  "pc": 5, "color": "ral9t08", "glass": "transparent"}])
    assert "error" in res
    assert "panel" in res["error"].lower() or "5" in res["error"]


def test_s500_panel_count_outside_allowed_set_is_rejected():
    # 7 is not in S500 allowed (2,3,4,5,6,8,10).
    res = _calc([{"side": "front", "bay": 0, "series": "S500",
                  "pc": 7, "color": "ral7016", "glass": "transparent"}])
    assert "error" in res


def test_s100_low_panel_count_is_rejected():
    # pc=1 is below the minimum and not in the allowed set; must error.
    res = _calc([{"side": "front", "bay": 0, "series": "S100",
                  "pc": 1, "color": "ral9t08", "glass": "transparent"}])
    assert "error" in res
    assert "panel" in res["error"].lower() or "1" in res["error"]


def test_s500_low_panel_count_is_rejected():
    # pc=1 is below the minimum and not in the allowed set; must error.
    res = _calc([{"side": "front", "bay": 0, "series": "S500",
                  "pc": 1, "color": "ral7016", "glass": "transparent"}])
    assert "error" in res


def test_s500_with_s100_glass_is_rejected():
    # tinted_mass belongs to S100, not S500.
    res = _calc([{"side": "front", "bay": 0, "series": "S500",
                  "pc": 4, "color": "ral7016", "glass": "tinted_mass"}])
    assert "error" in res
    assert "glass" in res["error"].lower()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
