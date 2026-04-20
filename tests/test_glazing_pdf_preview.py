"""Tests verifying that the glazing preview section appears in generated PDFs.

Covers task #88: confirms that when glazing_openings are configured the
"Остекление по проёмам" section is rendered and the PDF is non-trivial in size.

Two approaches are used:
  1. API integration: POST /api/calculate → POST /api/export-pdf → assert valid PDF bytes.
  2. Unit-level: call generate_commercial_offer() directly with glazing data.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app

_PDF_MAGIC = b'%PDF'
_MIN_PDF_BYTES = 5_000

_BASE_CALC_PAYLOAD = {
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
    "zip_openings": [],
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


@pytest.fixture(scope="module")
def app():
    return create_app({"TESTING": True, "SECRET_KEY": "test-secret"})


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as c:
        yield c


def _calculate_with_glazing(client):
    payload = dict(_BASE_CALC_PAYLOAD, glazing_openings=[_GLAZING_OPENING])
    resp = client.post("/api/calculate", json=payload)
    assert resp.status_code == 200, f"Calculate returned {resp.status_code}: {resp.data[:200]}"
    data = resp.get_json()
    assert data.get("success"), f"Calculation failed: {data.get('error')}"
    return data["result"]


class TestGlazingPdfPreviewApi:
    """API-level tests: full calculate → export-pdf pipeline."""

    def test_export_pdf_with_glazing_returns_valid_pdf(self, client):
        """PDF export with glazing_openings returns a valid, non-trivial PDF."""
        result = _calculate_with_glazing(client)
        export_payload = {"result": result, "mode": "single"}
        resp = client.post("/api/export-pdf", json=export_payload)
        assert resp.status_code == 200, (
            f"export-pdf returned {resp.status_code}: {resp.data[:200]}"
        )
        assert resp.content_type == "application/pdf", (
            f"Expected application/pdf, got {resp.content_type}"
        )
        pdf_bytes = resp.data
        assert pdf_bytes[:4] == _PDF_MAGIC, (
            f"Response does not start with %PDF magic bytes: {pdf_bytes[:10]!r}"
        )
        assert len(pdf_bytes) >= _MIN_PDF_BYTES, (
            f"PDF too small ({len(pdf_bytes)} bytes < {_MIN_PDF_BYTES}); "
            "glazing section likely not rendered"
        )

    def test_pdf_with_glazing_is_larger_than_without(self, client):
        """PDF that includes glazing preview is larger than one without glazing."""
        result_no_glz = _calculate_with_glazing(client)
        result_no_glz_copy = dict(result_no_glz)
        if "glazing" in result_no_glz_copy:
            result_no_glz_copy["glazing"] = {"count": 0, "openings": [], "price": 0.0}

        result_with_glz = _calculate_with_glazing(client)

        resp_no = client.post("/api/export-pdf", json={"result": result_no_glz_copy, "mode": "single"})
        resp_yes = client.post("/api/export-pdf", json={"result": result_with_glz, "mode": "single"})

        assert resp_no.status_code == 200, f"No-glazing PDF failed: {resp_no.status_code}"
        assert resp_yes.status_code == 200, f"Glazing PDF failed: {resp_yes.status_code}"

        size_no = len(resp_no.data)
        size_yes = len(resp_yes.data)
        assert size_yes > size_no, (
            f"Expected glazing PDF ({size_yes} bytes) to exceed "
            f"no-glazing PDF ({size_no} bytes)"
        )


class TestGlazingPdfPreviewUnit:
    """Unit-level tests: call generate_commercial_offer() directly."""

    def _make_pergola_data(self):
        return {
            "pergola_type": "B500NEW",
            "lamella_type": "B500-25NEW",
            "lamella_size": "250",
            "width": 4.0,
            "length": 3.0,
            "height": 3.0,
            "modules": 1,
            "max_overhang": None,
            "facade_openings": [],
            "glazing_openings": [
                {
                    "side": "front",
                    "bay": 0,
                    "series": "S500",
                    "pc": 4,
                    "direction": "right",
                    "color": "ral7016",
                    "glass": "transparent",
                    "count": 1,
                    "w": 3.64,
                    "h": 2.5,
                    "area": 9.1,
                    "price_eur": 800.0,
                    "sashes": 2,
                }
            ],
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

    def test_generate_commercial_offer_with_glazing_returns_bytes(self):
        """generate_commercial_offer() returns PDF bytes when glazing_openings present."""
        from pdf_generator_fpdf_rus import generate_commercial_offer

        pergola_data = self._make_pergola_data()
        pdf_bytes = generate_commercial_offer(pergola_data)

        assert pdf_bytes is not None, "generate_commercial_offer() returned None"
        assert isinstance(pdf_bytes, bytes), (
            f"Expected bytes, got {type(pdf_bytes)}"
        )
        assert pdf_bytes[:4] == _PDF_MAGIC, (
            f"Result does not start with %PDF: {pdf_bytes[:10]!r}"
        )
        assert len(pdf_bytes) >= _MIN_PDF_BYTES, (
            f"PDF too small ({len(pdf_bytes)} bytes); glazing section may not have rendered"
        )

    def test_generate_commercial_offer_glazing_section_bigger_than_no_glazing(self):
        """PDF with glazing section is larger than PDF without glazing openings."""
        from pdf_generator_fpdf_rus import generate_commercial_offer

        data_with = self._make_pergola_data()
        data_without = self._make_pergola_data()
        data_without["glazing_openings"] = []

        pdf_with = generate_commercial_offer(data_with)
        pdf_without = generate_commercial_offer(data_without)

        assert pdf_with is not None and pdf_without is not None
        assert len(pdf_with) > len(pdf_without), (
            f"PDF with glazing ({len(pdf_with)} bytes) should be larger than "
            f"PDF without glazing ({len(pdf_without)} bytes)"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
