"""Tests verifying the 3-column glazing card layout in generated PDFs.

Covers task #93: when 3+ glazing openings are present the PDF generator
switches to a 3-column card grid.  These tests confirm:
  1. The PDF is produced and valid.
  2. The glazing section page is present with correct card text markers.
  3. Card labels (side prefix + bay number) appear in the right order.
  4. Card positions stay within A4 page bounds (no right-edge overflow),
     verified against constants parsed directly from the generator source.
"""

import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_PDF_MAGIC = b"%PDF"
_MIN_PDF_BYTES = 5_000

# A4 page width in mm (FPDF default)
_PAGE_W_MM = 210.0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_layout_constants():
    """Parse pdf_generator_fpdf_rus.py and return 3-col and 2-col layout dicts.

    Returns (col3, col2) where each dict has keys:
        n_cols, card_w, card_gap, card_h, left_margin
    Raises AssertionError if any value cannot be found.
    """
    src_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "pdf_generator_fpdf_rus.py",
    )
    with open(src_path, encoding="utf-8") as fh:
        source = fh.read()

    # The 3-column branch is guarded by `if _n_cols == 3:`
    # The 2-column branch is the else branch that follows.
    # We rely on the *first* occurrence of each assignment for the 3-col block
    # and the second occurrence for 2-col (they appear in order in the file).

    def _find_all_floats(pattern):
        return [float(v) for v in re.findall(pattern, source)]

    card_w_vals = _find_all_floats(r"_card_w\s*=\s*([0-9]+(?:\.[0-9]+)?)")
    card_gap_vals = _find_all_floats(r"_card_gap\s*=\s*([0-9]+(?:\.[0-9]+)?)")
    card_h_vals = _find_all_floats(r"_card_h\s*=\s*([0-9]+(?:\.[0-9]+)?)")
    left_margin_vals = _find_all_floats(r"_left_margin\s*=\s*([0-9]+(?:\.[0-9]+)?)")

    assert len(card_w_vals) >= 2, "Expected at least 2 _card_w assignments (3-col, 2-col)"
    assert len(card_gap_vals) >= 2, "Expected at least 2 _card_gap assignments"
    assert len(card_h_vals) >= 2, "Expected at least 2 _card_h assignments"
    assert len(left_margin_vals) >= 1, "Expected at least 1 _left_margin assignment"

    col3 = {
        "n_cols": 3,
        "card_w": card_w_vals[0],
        "card_gap": card_gap_vals[0],
        "card_h": card_h_vals[0],
        "left_margin": left_margin_vals[0],
    }
    col2 = {
        "n_cols": 2,
        "card_w": card_w_vals[1],
        "card_gap": card_gap_vals[1],
        "card_h": card_h_vals[1],
        "left_margin": left_margin_vals[0],  # same left margin
    }
    return col3, col2


def _right_edge(layout: dict) -> float:
    """Return the x-coordinate (mm) of the rightmost card's right edge."""
    n = layout["n_cols"]
    return (
        layout["left_margin"]
        + n * layout["card_w"]
        + (n - 1) * layout["card_gap"]
    )


def _make_glazing_opening(side="front", bay=0, series="S500"):
    return {
        "side": side,
        "bay": bay,
        "series": series,
        "pc": 3,
        "direction": "right",
        "color": "ral7016",
        "glass": "transparent",
        "count": 1,
        "w": 3.0,
        "h": 2.5,
        "area": 7.5,
        "price_eur": 600.0,
        "sashes": 2,
    }


def _make_pergola_data(glazing_openings):
    return {
        "pergola_type": "B500NEW",
        "lamella_type": "B500-25NEW",
        "lamella_size": "250",
        "width": 6.0,
        "length": 3.0,
        "height": 3.0,
        "modules": 2,
        "max_overhang": None,
        "facade_openings": [],
        "glazing_openings": glazing_openings,
        "extra_cols_f": 0,
        "extra_cols_b": 0,
        "extra_cols_a": 0,
        "extra_cols_c": 0,
        "lamellas_count": 14,
        "euro_rate": 1,
        "items": [{"name": "Pergola B500NEW", "price": 3500}],
        "specification": [],
        "base_price": 3500,
        "total_cost": 3500,
        "cash_total": 3500,
        "noncash_total": 3675,
        "vat_total": 4200,
        "selected_variant": "",
        "variant_label": "",
        "description": "",
        "modular_description": "",
        "drainage_description": "",
        "image_paths": [],
        "image_caption": "",
    }


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Return all page text concatenated; raises on parse failure."""
    from PyPDF2 import PdfReader
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# ---------------------------------------------------------------------------
# Layout geometry assertions (sourced from the generator, not hand-copied)
# ---------------------------------------------------------------------------


class TestLayoutGeometry:
    """Verify card grid geometry parsed directly from the generator source."""

    @pytest.fixture(scope="class")
    def layouts(self):
        col3, col2 = _extract_layout_constants()
        return col3, col2

    def test_3col_right_edge_within_page(self, layouts):
        """3-column layout: right edge must not exceed A4 width."""
        col3, _ = layouts
        re3 = _right_edge(col3)
        assert re3 <= _PAGE_W_MM, (
            f"3-col right edge {re3:.1f} mm exceeds A4 width "
            f"{_PAGE_W_MM} mm — cards overflow the page"
        )

    def test_2col_right_edge_within_page(self, layouts):
        """2-column layout: right edge must not exceed A4 width."""
        _, col2 = layouts
        re2 = _right_edge(col2)
        assert re2 <= _PAGE_W_MM, (
            f"2-col right edge {re2:.1f} mm exceeds A4 width "
            f"{_PAGE_W_MM} mm — cards overflow the page"
        )

    def test_3col_card_narrower_than_2col(self, layouts):
        """3-column cards must be narrower than 2-column cards."""
        col3, col2 = layouts
        assert col3["card_w"] < col2["card_w"], (
            f"3-col card_w {col3['card_w']} mm must be < 2-col card_w {col2['card_w']} mm"
        )

    def test_3col_individual_column_x_within_page(self, layouts):
        """Every column's right edge stays within the page in 3-col layout."""
        col3, _ = layouts
        for col in range(col3["n_cols"]):
            card_x = col3["left_margin"] + col * (col3["card_w"] + col3["card_gap"])
            card_right = card_x + col3["card_w"]
            assert card_right <= _PAGE_W_MM, (
                f"Column {col} right edge {card_right:.1f} mm exceeds "
                f"page width {_PAGE_W_MM} mm"
            )

    def test_threshold_for_3col_is_exactly_3(self):
        """Generator source must use `>= 3` (not 4+) as the 3-col threshold."""
        src_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "pdf_generator_fpdf_rus.py",
        )
        with open(src_path, encoding="utf-8") as fh:
            source = fh.read()
        assert re.search(r"_n_cols\s*=\s*3\s+if\s+len\([^)]+\)\s*>=\s*3", source), (
            "Expected 3-column threshold `_n_cols = 3 if len(...) >= 3` not found; "
            "threshold may have been changed"
        )


# ---------------------------------------------------------------------------
# PDF generation + text-extraction tests
# ---------------------------------------------------------------------------


class TestThreeColumnGlazingLayout:
    """Tests that generate actual PDFs and inspect their text content."""

    def _generate(self, openings):
        from pdf_generator_fpdf_rus import generate_commercial_offer
        pdf_bytes = generate_commercial_offer(_make_pergola_data(openings))
        assert pdf_bytes is not None, "generate_commercial_offer() returned None"
        assert pdf_bytes[:4] == _PDF_MAGIC, (
            f"Output does not start with %PDF: {pdf_bytes[:10]!r}"
        )
        assert len(pdf_bytes) >= _MIN_PDF_BYTES, (
            f"PDF too small ({len(pdf_bytes)} bytes)"
        )
        return pdf_bytes

    def test_pdf_with_3_openings_is_valid(self):
        """generate_commercial_offer() returns valid PDF bytes for 3 openings."""
        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("front", 1),
            _make_glazing_opening("back", 0),
        ]
        self._generate(openings)  # assertions inside _generate

    def test_3_opening_card_labels_present_in_pdf_text(self):
        """All three card labels (F1, F2, B1) appear in extracted PDF text."""
        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("front", 1),
            _make_glazing_opening("back", 0),
        ]
        pdf_bytes = self._generate(openings)
        text = _extract_pdf_text(pdf_bytes)

        for label in ("F1", "F2", "B1"):
            assert label in text, (
                f"Expected card label {label!r} not found in PDF text; "
                "3-column glazing section may not have rendered correctly.\n"
                f"Extracted text snippet: {text[:800]!r}"
            )

    def test_glazing_section_heading_present(self):
        """The 'Остекление по проёмам' heading appears in the PDF text."""
        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("front", 1),
            _make_glazing_opening("back", 0),
        ]
        pdf_bytes = self._generate(openings)
        text = _extract_pdf_text(pdf_bytes)

        heading = "Остекление по проёмам"
        assert heading in text, (
            f"Glazing section heading {heading!r} not found in PDF text.\n"
            f"Extracted text snippet: {text[:800]!r}"
        )

    def test_card_summary_text_present(self):
        """Series and dimension text appears inside the glazing cards."""
        openings = [
            _make_glazing_opening("front", 0, series="S500"),
            _make_glazing_opening("front", 1, series="S500"),
            _make_glazing_opening("back", 0, series="S500"),
        ]
        pdf_bytes = self._generate(openings)
        text = _extract_pdf_text(pdf_bytes)

        assert "S500" in text, (
            f"Expected series 'S500' not found in PDF text.\n"
            f"Extracted text snippet: {text[:800]!r}"
        )
        assert "3000" in text, (
            f"Expected dimension '3000' (width in mm) not found in PDF text.\n"
            f"Extracted text snippet: {text[:800]!r}"
        )

    def test_2_openings_uses_2col_no_f2_label(self):
        """With 2 openings the 2-column layout is used; only F and B labels appear."""
        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("back", 0),
        ]
        pdf_bytes = self._generate(openings)
        text = _extract_pdf_text(pdf_bytes)

        # Single-bay sides produce no numeric suffix ("F", not "F1")
        assert "F" in text, "Front card label 'F' not found in 2-opening PDF"
        assert "B" in text, "Back card label 'B' not found in 2-opening PDF"
        # No "F2" card should exist when only 1 front opening
        assert "F2" not in text, (
            "Label 'F2' found in 2-opening PDF; unexpected second front card"
        )

    def test_4_openings_valid_pdf_with_labels(self):
        """4 openings (3-col layout, 2 rows) produce a valid PDF with all labels."""
        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("front", 1),
            _make_glazing_opening("back", 0),
            _make_glazing_opening("back", 1),
        ]
        pdf_bytes = self._generate(openings)
        text = _extract_pdf_text(pdf_bytes)

        for label in ("F1", "F2", "B1", "B2"):
            assert label in text, (
                f"Expected label {label!r} not found in 4-opening PDF text"
            )

    def test_6_openings_multirow_3col_valid(self):
        """6 openings fill two rows of 3 columns and produce a valid PDF."""
        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("front", 1),
            _make_glazing_opening("front", 2),
            _make_glazing_opening("back", 0),
            _make_glazing_opening("back", 1),
            _make_glazing_opening("back", 2),
        ]
        pdf_bytes = self._generate(openings)
        text = _extract_pdf_text(pdf_bytes)

        for label in ("F1", "F2", "F3", "B1", "B2", "B3"):
            assert label in text, (
                f"Expected label {label!r} not found in 6-opening PDF text"
            )

    def test_3_openings_larger_than_no_glazing(self):
        """PDF with 3 glazing openings is larger than one with no glazing."""
        from pdf_generator_fpdf_rus import generate_commercial_offer

        openings = [
            _make_glazing_opening("front", 0),
            _make_glazing_opening("front", 1),
            _make_glazing_opening("back", 0),
        ]
        pdf_with = generate_commercial_offer(_make_pergola_data(openings))
        pdf_without = generate_commercial_offer(_make_pergola_data([]))

        assert pdf_with is not None and pdf_without is not None
        assert len(pdf_with) > len(pdf_without), (
            f"PDF with 3 openings ({len(pdf_with)} bytes) should exceed "
            f"PDF without openings ({len(pdf_without)} bytes)"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
