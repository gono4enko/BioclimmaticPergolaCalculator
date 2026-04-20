"""Pytest tests verifying that ZIP awning product images are embedded in the PDF.

Covers task #90: calls generate_commercial_offer() with ZIP awning openings of
type ZIP100 and ZIP130 and asserts that:
  - The returned bytes are a valid PDF (starts with %PDF)
  - The file size significantly exceeds a baseline PDF without ZIP awnings,
    which is consistent with embedded product images being present
  - Both ZIP100 and ZIP130 image variants can be included in a single PDF
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Availability guard – skip if fpdf or PIL are not installed
# ---------------------------------------------------------------------------
try:
    from pdf_generator_fpdf_rus import generate_commercial_offer
    _PDF_GEN_AVAILABLE = True
    _PDF_GEN_IMPORT_ERROR = None
except (ImportError, ModuleNotFoundError) as exc:
    _PDF_GEN_AVAILABLE = False
    _PDF_GEN_IMPORT_ERROR = str(exc)

pytestmark = pytest.mark.skipif(
    not _PDF_GEN_AVAILABLE,
    reason=f"pdf_generator_fpdf_rus or a required dependency is not installed: {_PDF_GEN_IMPORT_ERROR}",
)


# ---------------------------------------------------------------------------
# Minimal pergola_data fixture helpers
# ---------------------------------------------------------------------------

def _base_pergola_data(**overrides):
    """Return a minimal pergola_data dict sufficient to generate a PDF."""
    data = {
        "pergola_type": "B500NEW",
        "width": 4.0,
        "length": 3.0,
        "height": 3.0,
        "total_price_eur": 2500.0,
        "cash_total": 275000,
        "euro_rate": 110,
        "zip_price_eur": 0.0,
        "zip_openings": [],
        "items": [],
        "options": {},
        "dimensions": {},
    }
    data.update(overrides)
    return data


def _zip_opening(zip_type="ZIP100", side="front", bay=0,
                 fabric="veozip", color="ral9016", drive="manual",
                 width=4.0, height=2.4, total_eur=350.0):
    """Return a single ZIP opening dict as expected by generate_commercial_offer."""
    return {
        "zip_type": zip_type,
        "side": side,
        "bay": bay,
        "fabric": fabric,
        "color": color,
        "drive": drive,
        "adj_w": width,
        "adj_h": height,
        "count": 1,
        "sections": 1,
        "total_eur": total_eur,
        "has_glazing": False,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestZipAwningPdfImages:
    """Verify ZIP awning product images are embedded in the generated PDF."""

    def test_pdf_without_zip_is_valid(self):
        """Baseline: PDF without ZIP openings is generated successfully."""
        data = _base_pergola_data()
        pdf_bytes = generate_commercial_offer(data)
        assert pdf_bytes is not None, "generate_commercial_offer returned None"
        assert isinstance(pdf_bytes, (bytes, bytearray)), "Result should be bytes"
        assert pdf_bytes[:4] == b"%PDF", (
            f"Result does not start with %PDF; got {pdf_bytes[:8]!r}"
        )

    def test_pdf_with_zip100_image_is_larger_than_baseline(self):
        """PDF with a ZIP100 opening must be larger than a baseline PDF (images embedded)."""
        baseline_data = _base_pergola_data()
        baseline_bytes = generate_commercial_offer(baseline_data)
        assert baseline_bytes is not None, "Baseline PDF generation failed"

        zip_data = _base_pergola_data(
            zip_openings=[_zip_opening(zip_type="ZIP100")],
            zip_price_eur=350.0,
        )
        zip_bytes = generate_commercial_offer(zip_data)
        assert zip_bytes is not None, "ZIP100 PDF generation returned None"
        assert zip_bytes[:4] == b"%PDF", (
            f"ZIP100 PDF does not start with %PDF; got {zip_bytes[:8]!r}"
        )

        size_diff = len(zip_bytes) - len(baseline_bytes)
        assert size_diff > 10_000, (
            f"Expected PDF with ZIP100 image to be >10 KB larger than baseline, "
            f"but size difference is only {size_diff} bytes "
            f"(baseline={len(baseline_bytes)}, zip={len(zip_bytes)}). "
            f"This suggests the image was not embedded."
        )

    def test_pdf_with_zip130_image_is_larger_than_baseline(self):
        """PDF with a ZIP130 opening must be larger than a baseline PDF (images embedded)."""
        baseline_data = _base_pergola_data()
        baseline_bytes = generate_commercial_offer(baseline_data)
        assert baseline_bytes is not None, "Baseline PDF generation failed"

        zip_data = _base_pergola_data(
            zip_openings=[_zip_opening(zip_type="ZIP130")],
            zip_price_eur=400.0,
        )
        zip_bytes = generate_commercial_offer(zip_data)
        assert zip_bytes is not None, "ZIP130 PDF generation returned None"
        assert zip_bytes[:4] == b"%PDF", (
            f"ZIP130 PDF does not start with %PDF; got {zip_bytes[:8]!r}"
        )

        size_diff = len(zip_bytes) - len(baseline_bytes)
        assert size_diff > 10_000, (
            f"Expected PDF with ZIP130 image to be >10 KB larger than baseline, "
            f"but size difference is only {size_diff} bytes "
            f"(baseline={len(baseline_bytes)}, zip={len(zip_bytes)}). "
            f"This suggests the image was not embedded."
        )

    def test_pdf_with_both_zip_types_is_larger_than_single_type(self):
        """PDF with ZIP100 + ZIP130 openings should be larger than one with only ZIP100."""
        single_data = _base_pergola_data(
            zip_openings=[_zip_opening(zip_type="ZIP100")],
            zip_price_eur=350.0,
        )
        single_bytes = generate_commercial_offer(single_data)
        assert single_bytes is not None, "Single ZIP type PDF generation returned None"

        both_data = _base_pergola_data(
            zip_openings=[
                _zip_opening(zip_type="ZIP100", side="front"),
                _zip_opening(zip_type="ZIP130", side="back", total_eur=420.0),
            ],
            zip_price_eur=770.0,
        )
        both_bytes = generate_commercial_offer(both_data)
        assert both_bytes is not None, "Dual ZIP type PDF generation returned None"
        assert both_bytes[:4] == b"%PDF", (
            f"Dual ZIP PDF does not start with %PDF; got {both_bytes[:8]!r}"
        )

        size_diff = len(both_bytes) - len(single_bytes)
        assert size_diff > 5_000, (
            f"Expected PDF with both ZIP types to be >5 KB larger than single-type PDF, "
            f"but size difference is only {size_diff} bytes "
            f"(single={len(single_bytes)}, both={len(both_bytes)}). "
            f"This suggests the second ZIP image (ZIP130) was not embedded."
        )

    def test_zip_image_files_exist_on_disk(self):
        """Sanity check: zip100.png and zip130.png are present at their expected paths."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        facade_dir = os.path.join(base_dir, "flask_app", "static", "images", "facade")

        zip100_path = os.path.join(facade_dir, "zip100.png")
        zip130_path = os.path.join(facade_dir, "zip130.png")

        assert os.path.exists(zip100_path), (
            f"zip100.png not found at expected path: {zip100_path}"
        )
        assert os.path.isfile(zip100_path), f"zip100.png is not a regular file"
        assert os.path.getsize(zip100_path) > 0, "zip100.png is empty"

        assert os.path.exists(zip130_path), (
            f"zip130.png not found at expected path: {zip130_path}"
        )
        assert os.path.isfile(zip130_path), f"zip130.png is not a regular file"
        assert os.path.getsize(zip130_path) > 0, "zip130.png is empty"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
