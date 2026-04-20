"""Playwright end-to-end tests for the ZIP awning selection and pricing flow.

Covers task #78: drives the browser through the full calculator UI to verify:
  - B500NEW + 4×3 m dimensions reach Step 4
  - ZIP toggle on front opening works ("+ ZIP" → "ZIP ✓")
  - Soltis fabric and Somfy electric drive can be selected
  - Calculate produces a results section with the ZIP block (count ≥ 1)

Tests are skipped automatically when `playwright` is not installed.
Run against a live server:  BASE_URL=http://localhost:5000 pytest tests/test_zip_awning_e2e.py -v
Or against the default dev URL when the app is running locally.
"""

import os
import re
import time

import pytest

# ---------------------------------------------------------------------------
# Playwright availability guard
# ---------------------------------------------------------------------------
try:
    from playwright.sync_api import sync_playwright, expect, TimeoutError as PWTimeout
    _PW_AVAILABLE = True
except ImportError:
    _PW_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _PW_AVAILABLE,
    reason="playwright package not installed — install with: pip install playwright && playwright install chromium",
)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_page(playwright):
    """Launch a headless Chromium browser and return (browser, page)."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    return browser, page


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestZipAwningE2E:
    """Playwright browser tests for the ZIP awning UI flow."""

    def test_zip_awning_full_flow_b500new_soltis_somfy(self):
        """Full UI flow: B500NEW → 4×3 m → front ZIP Soltis/Somfy → verify КП block."""
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                # Step 1 — Navigate and select B500NEW
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()

                # Step 2 — Choose "Автовыбор" variant
                page.locator('#variant-options [data-variant="auto"]').click()

                # Step 3 — Enter dimensions 4 × 3 m
                page.locator('#input-width').fill("4")
                page.locator('#input-length').fill("3")
                page.locator('#input-length').press("Tab")  # trigger blur/change

                # Step 4 should be visible now
                step4 = page.locator('#step-4')
                expect(step4).to_be_visible(timeout=5000)

                # Expand "Заполнение проёмов" details spoiler
                spoiler_summary = page.locator('details.facade-spoiler > summary')
                spoiler_summary.click()

                # Wait for ZIP table to appear
                zip_table = page.locator('#zip-opening-table')
                expect(zip_table).to_be_visible(timeout=5000)

                # Enable ZIP on the front opening (front_0)
                toggle_btn = page.locator('.zip-toggle-btn[data-key="front_0"]')
                expect(toggle_btn).to_be_visible(timeout=3000)
                assert "+ ZIP" in toggle_btn.inner_text(), (
                    f"Expected '+ ZIP' on toggle before enabling, got: {toggle_btn.inner_text()!r}"
                )
                toggle_btn.click()

                # After click the button text should change to "ZIP ✓"
                expect(toggle_btn).to_contain_text("ZIP", timeout=3000)
                assert "ZIP" in toggle_btn.inner_text(), (
                    f"Expected 'ZIP' in button text after enabling, got: {toggle_btn.inner_text()!r}"
                )

                # Select Soltis fabric
                fabric_sel = page.locator('select.zip-fld[data-fld="fabric"][data-key="front_0"]')
                expect(fabric_sel).to_be_visible(timeout=3000)
                fabric_sel.select_option("soltis")

                # Switch drive to electric
                drive_type_sel = page.locator('select.zip-fld[data-fld="drive_type"][data-key="front_0"]')
                expect(drive_type_sel).to_be_visible(timeout=3000)
                drive_type_sel.select_option("electric")

                # After switching to electric a brand select should appear
                brand_sel = page.locator('select.zip-fld[data-fld="drive"][data-key="front_0"]')
                expect(brand_sel).to_be_visible(timeout=3000)
                brand_sel.select_option("somfy")

                # Click "Рассчитать стоимость"
                calc_btn = page.locator('#calc-btn')
                expect(calc_btn).to_be_visible(timeout=3000)
                calc_btn.click()

                # Wait for results section to appear (spinner disappears after calc)
                results = page.locator('#results-section')
                expect(results).to_be_visible(timeout=15000)
                assert results.inner_text() != "", "Results section should not be empty"

                # Verify ZIP block is present in results
                results_text = results.inner_text()
                assert "ZIP" in results_text, (
                    f"Expected 'ZIP' in results, got:\n{results_text[:500]}"
                )
                assert "ZIP-маркиз" in results_text, (
                    f"Expected 'ZIP-маркиз' in results, got:\n{results_text[:500]}"
                )

                # Verify the ZIP block title contains the unit count "(N шт.)"
                # The rendered title is: "ZIP-маркизы (N шт.) — вертикальные рулонные шторы"
                zip_count_match = re.search(r'ZIP-маркиз[ыа]\s*\(\s*(\d+)\s*шт\.', results_text)
                assert zip_count_match is not None, (
                    f"Expected 'ZIP-маркизы (N шт.)' pattern in results, got:\n{results_text[:600]}"
                )
                zip_count = int(zip_count_match.group(1))
                assert zip_count >= 1, (
                    f"Expected ≥1 ZIP unit in results block, got count={zip_count}"
                )

            finally:
                browser.close()

    def test_zip_toggle_shows_soltis_and_electric_selects(self):
        """Enabling ZIP renders fabric and drive selects; Soltis and Somfy are selectable."""
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()
                page.locator('#variant-options [data-variant="auto"]').click()
                page.locator('#input-width').fill("4")
                page.locator('#input-length').fill("3")
                page.locator('#input-length').press("Tab")

                page.locator('details.facade-spoiler > summary').click()
                page.locator('.zip-toggle-btn[data-key="front_0"]').click()

                # Fabric select must have "soltis" as an option
                fabric_sel = page.locator('select.zip-fld[data-fld="fabric"][data-key="front_0"]')
                expect(fabric_sel).to_be_visible(timeout=3000)
                options = fabric_sel.locator('option').all()
                option_values = [o.get_attribute('value') for o in options]
                assert 'soltis' in option_values, (
                    f"Expected 'soltis' in fabric options: {option_values}"
                )
                assert 'veozip' in option_values, (
                    f"Expected 'veozip' in fabric options: {option_values}"
                )

                # Drive type select must include "electric"
                drive_type_sel = page.locator('select.zip-fld[data-fld="drive_type"][data-key="front_0"]')
                expect(drive_type_sel).to_be_visible(timeout=3000)
                drive_type_sel.select_option("electric")

                # Brand select must appear with "somfy" option
                brand_sel = page.locator('select.zip-fld[data-fld="drive"][data-key="front_0"]')
                expect(brand_sel).to_be_visible(timeout=3000)
                brand_options = [o.get_attribute('value') for o in brand_sel.locator('option').all()]
                assert 'somfy' in brand_options, (
                    f"Expected 'somfy' in brand options: {brand_options}"
                )
                assert 'simu' in brand_options, (
                    f"Expected 'simu' in brand options: {brand_options}"
                )

            finally:
                browser.close()

    def test_zip_info_badge_shows_count_after_enabling(self):
        """After enabling ZIP on the front opening the info badge shows '1 проём'."""
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()
                page.locator('#variant-options [data-variant="auto"]').click()
                page.locator('#input-width').fill("4")
                page.locator('#input-length').fill("3")
                page.locator('#input-length').press("Tab")

                page.locator('details.facade-spoiler > summary').click()
                page.locator('.zip-toggle-btn[data-key="front_0"]').click()

                info = page.locator('#zip-area-info')
                expect(info).to_be_visible(timeout=3000)
                info_text = info.inner_text()
                assert "1" in info_text, (
                    f"Expected '1' in ZIP info badge after enabling, got: {info_text!r}"
                )

            finally:
                browser.close()
