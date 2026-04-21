"""Unit + integration tests for ZIP overlay dimension increments when glazing is active.

Covers task #106: verifies that when a ZIP awning opening overlaps with a glazing
opening the backend calculation correctly adds the +100 mm width adjustment and
the +100 mm (ZIP100) / +130 mm (ZIP130) height adjustment.

Tests are split into three layers:
  1. Direct function tests against ``zip_calc_price`` in calculator.py
  2. API-level tests through ``POST /api/calculate`` that mirror the real request path
  3. PDF-level tests (task #115) that confirm the КП commercial offer prints the
     overlay-incremented dimensions in the ZIP awning label, not the raw opening size.
"""

import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app
from flask_app.services.calculator import (
    zip_calc_price,
    ZIP_OVERLAY_ADD_W,
    ZIP100_OVERLAY_ADD_H,
    ZIP130_OVERLAY_ADD_H,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-secret'})


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_PAYLOAD = {
    "pergola_type": "B500NEW",
    "lamella_type": "B500-25NEW",
    "lamella_size": "250",
    "width": 4.0,
    "length": 3.0,
    "height": 3.0,
    "lighting": [],
    "installation": False,
    "selected_variant": "",
    "facade_type": "",
    "facade_openings": [],
    "glazing_openings": [],
}

_GLAZING_OPENING = {
    "side": "front",
    "bay": 0,
    "series": "S500",
    "pc": 4,
    "direction": "right",
    "color": "ral7016",
    "glass": "transparent",
    "count": 1,
}

_ZIP_FRONT_BAY0 = {
    "side": "front",
    "bay": 0,
    "fabric": "veozip",
    "color": "ral9016",
    "drive": "manual",
    "count": 1,
}


def _calculate(client, *, glazing_openings=None, zip_openings=None):
    payload = dict(
        _BASE_PAYLOAD,
        glazing_openings=glazing_openings or [],
        zip_openings=zip_openings or [],
    )
    resp = client.post('/api/calculate', json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    data = resp.get_json()
    assert data.get('success'), f"Calculation failed: {data.get('error')}"
    return data


# ===========================================================================
# Layer 1 – direct ``zip_calc_price`` unit tests
# ===========================================================================

class TestZipCalcPriceOverlayDimensions:
    """zip_calc_price must apply the correct dimensional increments."""

    def test_no_glazing_leaves_dimensions_unchanged(self):
        """Without glazing adj_w and adj_h equal the raw input dimensions."""
        op_w, op_h = 3.0, 2.5
        result = zip_calc_price(op_w, op_h, has_glazing=False)
        assert 'error' not in result, f"Unexpected error: {result.get('error')}"
        assert result['adj_w'] == pytest.approx(op_w, abs=1e-6), (
            f"adj_w should equal op_w={op_w}, got {result['adj_w']}")
        assert result['adj_h'] == pytest.approx(op_h, abs=1e-6), (
            f"adj_h should equal op_h={op_h}, got {result['adj_h']}")

    def test_glazing_adds_100mm_to_width(self):
        """has_glazing=True must add ZIP_OVERLAY_ADD_W (0.100 m) to width."""
        op_w, op_h = 3.0, 2.5
        result = zip_calc_price(op_w, op_h, has_glazing=True)
        assert 'error' not in result, f"Unexpected error: {result.get('error')}"
        expected_w = op_w + ZIP_OVERLAY_ADD_W
        assert result['adj_w'] == pytest.approx(expected_w, abs=1e-6), (
            f"Expected adj_w={expected_w} (op_w + {ZIP_OVERLAY_ADD_W}), "
            f"got {result['adj_w']}")

    def test_glazing_zip100_adds_100mm_to_height(self):
        """ZIP100 overlay must add ZIP100_OVERLAY_ADD_H (0.100 m) to height."""
        op_w, op_h = 3.0, 2.5
        result = zip_calc_price(op_w, op_h, has_glazing=True,
                                zip_type_override='ZIP100')
        assert 'error' not in result, f"Unexpected error: {result.get('error')}"
        assert result['zip_type'] == 'ZIP100'
        expected_h = op_h + ZIP100_OVERLAY_ADD_H
        assert result['adj_h'] == pytest.approx(expected_h, abs=1e-6), (
            f"Expected adj_h={expected_h} (op_h + {ZIP100_OVERLAY_ADD_H}) "
            f"for ZIP100 overlay, got {result['adj_h']}")

    def test_glazing_zip130_adds_130mm_to_height(self):
        """ZIP130 overlay must add ZIP130_OVERLAY_ADD_H (0.130 m) to height."""
        op_w, op_h = 3.0, 2.5
        result = zip_calc_price(op_w, op_h, has_glazing=True,
                                zip_type_override='ZIP130')
        assert 'error' not in result, f"Unexpected error: {result.get('error')}"
        assert result['zip_type'] == 'ZIP130'
        expected_h = op_h + ZIP130_OVERLAY_ADD_H
        assert result['adj_h'] == pytest.approx(expected_h, abs=1e-6), (
            f"Expected adj_h={expected_h} (op_h + {ZIP130_OVERLAY_ADD_H}) "
            f"for ZIP130 overlay, got {result['adj_h']}")

    def test_glazing_overlay_width_increment_equals_100mm_constant(self):
        """The overlay width constant must be exactly 0.100 m (100 mm)."""
        assert ZIP_OVERLAY_ADD_W == pytest.approx(0.100, abs=1e-9), (
            f"ZIP_OVERLAY_ADD_W must be 0.100 m, got {ZIP_OVERLAY_ADD_W}")

    def test_glazing_overlay_zip100_height_increment_equals_100mm_constant(self):
        """ZIP100 overlay height constant must be exactly 0.100 m (100 mm)."""
        assert ZIP100_OVERLAY_ADD_H == pytest.approx(0.100, abs=1e-9), (
            f"ZIP100_OVERLAY_ADD_H must be 0.100 m, got {ZIP100_OVERLAY_ADD_H}")

    def test_glazing_overlay_zip130_height_increment_equals_130mm_constant(self):
        """ZIP130 overlay height constant must be exactly 0.130 m (130 mm)."""
        assert ZIP130_OVERLAY_ADD_H == pytest.approx(0.130, abs=1e-9), (
            f"ZIP130_OVERLAY_ADD_H must be 0.130 m, got {ZIP130_OVERLAY_ADD_H}")

    def test_glazing_flag_is_recorded_in_result(self):
        """The returned dict must echo has_glazing=True when overlay is active."""
        result = zip_calc_price(3.0, 2.5, has_glazing=True)
        assert result.get('has_glazing') is True, (
            f"Expected has_glazing=True in result, got {result.get('has_glazing')}")

    def test_no_glazing_flag_is_recorded_in_result(self):
        """The returned dict must echo has_glazing=False when no overlay."""
        result = zip_calc_price(3.0, 2.5, has_glazing=False)
        assert result.get('has_glazing') is False, (
            f"Expected has_glazing=False in result, got {result.get('has_glazing')}")

    def test_overlay_adj_w_is_larger_than_without_overlay(self):
        """adj_w with glazing must exceed adj_w without glazing."""
        op_w, op_h = 3.0, 2.5
        r_no = zip_calc_price(op_w, op_h, has_glazing=False)
        r_gl = zip_calc_price(op_w, op_h, has_glazing=True)
        assert r_gl['adj_w'] > r_no['adj_w'], (
            f"adj_w with glazing ({r_gl['adj_w']}) should exceed "
            f"adj_w without ({r_no['adj_w']})")

    def test_overlay_adj_h_is_larger_than_without_overlay(self):
        """adj_h with glazing must exceed adj_h without glazing."""
        op_w, op_h = 3.0, 2.5
        r_no = zip_calc_price(op_w, op_h, has_glazing=False)
        r_gl = zip_calc_price(op_w, op_h, has_glazing=True)
        assert r_gl['adj_h'] > r_no['adj_h'], (
            f"adj_h with glazing ({r_gl['adj_h']}) should exceed "
            f"adj_h without ({r_no['adj_h']})")


# ===========================================================================
# Layer 2 – API integration tests through POST /api/calculate
# ===========================================================================

class TestZipOverlayDimensionsViaApi:
    """API-level tests: ZIP opening on the same bay as glazing gets overlay dims."""

    def _get_zip_opening(self, data, side, bay):
        """Return the first ZIP opening matching (side, bay) from the result."""
        openings = data['result']['zip']['openings']
        matches = [o for o in openings if o['side'] == side and o['bay'] == bay]
        assert matches, (
            f"No ZIP opening for side={side} bay={bay} in {openings}")
        return matches[0]

    def test_zip_without_glazing_has_no_width_increment(self, client):
        """ZIP on a non-glazed opening must NOT add 100 mm to adj_w."""
        data_no_glz = _calculate(client, zip_openings=[_ZIP_FRONT_BAY0])
        data_glz = _calculate(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        op_no = self._get_zip_opening(data_no_glz, 'front', 0)
        op_gl = self._get_zip_opening(data_glz, 'front', 0)
        assert op_no['has_glazing'] is False, (
            f"Expected has_glazing=False for non-glazed ZIP, got {op_no['has_glazing']}")
        assert op_no['adj_w'] == pytest.approx(op_gl['adj_w'] - ZIP_OVERLAY_ADD_W, abs=1e-4), (
            f"Non-glazed adj_w ({op_no['adj_w']}) should be exactly "
            f"{ZIP_OVERLAY_ADD_W} m less than glazed adj_w ({op_gl['adj_w']})")

    def test_zip_with_glazing_has_glazing_flag_true(self, client):
        """ZIP opening co-located with glazing must have has_glazing=True."""
        data = _calculate(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        op = self._get_zip_opening(data, 'front', 0)
        assert op['has_glazing'] is True, (
            f"Expected has_glazing=True for ZIP opening with glazing, "
            f"got {op['has_glazing']}")

    def test_zip_with_glazing_adj_w_exceeds_no_glazing_adj_w(self, client):
        """adj_w with overlay glazing must be exactly 100 mm larger than without."""
        data_no_glz = _calculate(client, zip_openings=[_ZIP_FRONT_BAY0])
        data_glz = _calculate(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        op_no = self._get_zip_opening(data_no_glz, 'front', 0)
        op_gl = self._get_zip_opening(data_glz, 'front', 0)
        diff_w = round(op_gl['adj_w'] - op_no['adj_w'], 6)
        assert diff_w == pytest.approx(ZIP_OVERLAY_ADD_W, abs=1e-4), (
            f"Expected adj_w difference of {ZIP_OVERLAY_ADD_W} m (100 mm), "
            f"got {diff_w} m (no-glz adj_w={op_no['adj_w']}, "
            f"glz adj_w={op_gl['adj_w']})")

    def test_zip_with_glazing_adj_h_exceeds_no_glazing_adj_h(self, client):
        """adj_h with overlay glazing must be larger by the overlay height increment."""
        data_no_glz = _calculate(client, zip_openings=[_ZIP_FRONT_BAY0])
        data_glz = _calculate(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        op_no = self._get_zip_opening(data_no_glz, 'front', 0)
        op_gl = self._get_zip_opening(data_glz, 'front', 0)
        diff_h = round(op_gl['adj_h'] - op_no['adj_h'], 6)
        zip_type = op_gl.get('zip_type', op_no.get('zip_type'))
        expected_h_add = (ZIP130_OVERLAY_ADD_H
                          if zip_type == 'ZIP130'
                          else ZIP100_OVERLAY_ADD_H)
        assert diff_h == pytest.approx(expected_h_add, abs=1e-4), (
            f"Expected adj_h difference of {expected_h_add} m for {zip_type} overlay, "
            f"got {diff_h} m (no-glz adj_h={op_no['adj_h']}, "
            f"glz adj_h={op_gl['adj_h']})")

    def test_zip_with_glazing_costs_more_than_without_glazing(self, client):
        """Overlay dimensions increase area, so price with glazing must exceed price without."""
        data_no_glz = _calculate(client, zip_openings=[_ZIP_FRONT_BAY0])
        data_glz = _calculate(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        price_no = data_no_glz['result']['zip']['price']
        price_gl = data_glz['result']['zip']['price']
        assert price_gl > price_no, (
            f"ZIP price with glazing overlay ({price_gl}) should exceed "
            f"ZIP price without glazing ({price_no})")

    def test_different_side_zip_is_not_affected_by_front_glazing(self, client):
        """ZIP on the back (no glazing) must not gain overlay increments."""
        back_zip = dict(_ZIP_FRONT_BAY0, side='back')
        data_no_glz = _calculate(client, zip_openings=[back_zip])
        data_glz = _calculate(
            client,
            glazing_openings=[_GLAZING_OPENING],  # glazing only on front
            zip_openings=[back_zip],
        )
        op_no = self._get_zip_opening(data_no_glz, 'back', 0)
        op_gl = self._get_zip_opening(data_glz, 'back', 0)
        assert op_gl['has_glazing'] is False, (
            f"Back-side ZIP should not inherit front glazing overlay, "
            f"got has_glazing={op_gl['has_glazing']}")
        assert op_gl['adj_w'] == pytest.approx(op_no['adj_w'], abs=1e-4), (
            f"Back ZIP adj_w should be unaffected by front glazing; "
            f"no-glz={op_no['adj_w']}, with-front-glz={op_gl['adj_w']}")


# ===========================================================================
# Layer 3 – PDF-level tests (task #115)
# ===========================================================================

_PDF_MAGIC = b'%PDF'


def _extract_pdf_text(pdf_bytes):
    """Return all text concatenated across all pages of the PDF."""
    import PyPDF2
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    return '\n'.join((p.extract_text() or '') for p in reader.pages)


def _export_pdf(client, result):
    resp = client.post('/api/export-pdf', json={'result': result, 'mode': 'single'})
    assert resp.status_code == 200, (
        f"export-pdf returned {resp.status_code}: {resp.data[:200]}")
    assert resp.data[:4] == _PDF_MAGIC, (
        f"Response is not a PDF: {resp.data[:10]!r}")
    return resp.data


class TestZipOverlayDimensionsInPdf:
    """The КП PDF must print overlay-incremented dims for ZIP+glazing openings."""

    def _calc_result(self, client, *, glazing_openings=None, zip_openings=None):
        return _calculate(
            client,
            glazing_openings=glazing_openings,
            zip_openings=zip_openings,
        )['result']

    def _zip_dim_string(self, adj_w, adj_h):
        """The PDF prints ZIP dimensions as ``{adj_w:.2f}×{adj_h:.2f} м``."""
        return f"{adj_w:.2f}\u00d7{adj_h:.2f}"

    def test_pdf_prints_overlay_adjusted_dims_for_zip_with_glazing(self, client):
        """ZIP+glazing on the same bay → PDF must contain the overlay-adjusted dim string."""
        result = self._calc_result(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        op = result['zip']['openings'][0]
        assert op['has_glazing'] is True
        adj_dim = self._zip_dim_string(op['adj_w'], op['adj_h'])

        pdf_bytes = _export_pdf(client, result)
        text = _extract_pdf_text(pdf_bytes)
        assert adj_dim in text, (
            f"Expected overlay-adjusted ZIP dimension '{adj_dim}' in PDF, "
            f"but it was not found. adj_w={op['adj_w']}, adj_h={op['adj_h']}.")

    def test_pdf_does_not_print_raw_dims_for_zip_with_glazing(self, client):
        """When overlay applies, the PDF must NOT print the raw (pre-overlay) ZIP dim string.

        The raw dim string is what the PDF would emit if the template incorrectly pulled
        opening width/height instead of adj_w/adj_h. This test guards against that
        regression.
        """
        result_glz = self._calc_result(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        result_no_glz = self._calc_result(client, zip_openings=[_ZIP_FRONT_BAY0])

        op_no = result_no_glz['zip']['openings'][0]
        raw_dim = self._zip_dim_string(op_no['adj_w'], op_no['adj_h'])

        pdf_bytes = _export_pdf(client, result_glz)
        text = _extract_pdf_text(pdf_bytes)

        # The raw dim string should NOT appear in the spec line / items table /
        # cost table for the ZIP awning when overlay is in effect. We allow the
        # raw dim to appear in OTHER unrelated contexts (e.g. glazing tables
        # render their own raw dims), so we restrict the search to lines that
        # mention ZIP-маркиза.
        zip_lines = [ln for ln in text.splitlines() if 'ZIP' in ln]
        joined = '\n'.join(zip_lines)
        assert raw_dim not in joined, (
            f"Raw (pre-overlay) ZIP dim '{raw_dim}' must NOT appear on any "
            f"ZIP line of the PDF when glazing overlay is active. "
            f"Offending lines:\n{joined}")

    def test_pdf_zip_dim_increases_by_overlay_constants_when_glazing_added(self, client):
        """The dim-mm pair printed for the ZIP awning must grow by +100 / +100 mm."""
        result_glz = self._calc_result(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        result_no_glz = self._calc_result(client, zip_openings=[_ZIP_FRONT_BAY0])

        text_glz = _extract_pdf_text(_export_pdf(client, result_glz))
        text_no = _extract_pdf_text(_export_pdf(client, result_no_glz))

        op_glz = result_glz['zip']['openings'][0]
        op_no = result_no_glz['zip']['openings'][0]

        adj_dim_glz = self._zip_dim_string(op_glz['adj_w'], op_glz['adj_h'])
        adj_dim_no = self._zip_dim_string(op_no['adj_w'], op_no['adj_h'])

        assert adj_dim_glz in text_glz, (
            f"Overlay PDF missing '{adj_dim_glz}'")
        assert adj_dim_no in text_no, (
            f"No-overlay PDF missing '{adj_dim_no}'")

        # And they must actually differ by the overlay constants.
        diff_w = round(op_glz['adj_w'] - op_no['adj_w'], 6)
        diff_h = round(op_glz['adj_h'] - op_no['adj_h'], 6)
        expected_h = (ZIP130_OVERLAY_ADD_H if op_glz.get('zip_type') == 'ZIP130'
                      else ZIP100_OVERLAY_ADD_H)
        assert diff_w == pytest.approx(ZIP_OVERLAY_ADD_W, abs=1e-4), (
            f"PDF dim width should grow by {ZIP_OVERLAY_ADD_W} m, got {diff_w}")
        assert diff_h == pytest.approx(expected_h, abs=1e-4), (
            f"PDF dim height should grow by {expected_h} m, got {diff_h}")

    def test_pdf_zip_label_uses_adj_w_adj_h_pattern(self, client):
        """At least one 'ZIP-маркиза' line in the PDF must contain the adj dim string."""
        result = self._calc_result(
            client,
            glazing_openings=[_GLAZING_OPENING],
            zip_openings=[_ZIP_FRONT_BAY0],
        )
        op = result['zip']['openings'][0]
        adj_dim = self._zip_dim_string(op['adj_w'], op['adj_h'])

        text = _extract_pdf_text(_export_pdf(client, result))
        # Find lines containing the ZIP awning label and ensure adj dim is present
        # somewhere near them. PyPDF2 occasionally splits lines; flatten newlines
        # for the scan to be robust.
        flat = re.sub(r'\s+', ' ', text)
        assert 'ZIP-маркиза' in flat, "PDF missing ZIP-маркиза label entirely"
        assert adj_dim in flat, (
            f"PDF text does not contain the overlay-adjusted ZIP dim '{adj_dim}'. "
            f"This means the template is likely rendering raw opening dims.")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
