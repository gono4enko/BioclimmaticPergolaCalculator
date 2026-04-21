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
        """Full UI flow: B500NEW → 4.5×3 m → front ZIP Soltis/Somfy → verify КП block."""
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                # Step 1 — Navigate and select B500NEW
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()

                # Step 2 — Choose "Автовыбор" variant
                page.locator('#variant-options [data-variant="auto"]').click()

                # Step 3 — Enter dimensions 4.5 × 3 m (front opening must exceed 4.0 m
                # to enable ZIP-130 mode where Soltis fabric is offered).
                page.locator('#input-width').fill("4.5")
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
                # Front opening must exceed 4.0 m so Soltis (ZIP-130) is offered.
                page.locator('#input-width').fill("4.5")
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

    def test_zip_multiple_openings_results_count(self):
        """Enable ZIP on left + right + front openings; results block must show count ≥ 3."""
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                # Navigate and configure B500NEW 4×3 m
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()
                page.locator('#variant-options [data-variant="auto"]').click()
                page.locator('#input-width').fill("4")
                page.locator('#input-length').fill("3")
                page.locator('#input-length').press("Tab")

                expect(page.locator('#step-4')).to_be_visible(timeout=5000)

                # Open the facade/ZIP spoiler
                page.locator('details.facade-spoiler > summary').click()

                zip_table = page.locator('#zip-opening-table')
                expect(zip_table).to_be_visible(timeout=5000)

                # Enable ZIP on front opening
                toggle_front = page.locator('.zip-toggle-btn[data-key="front_0"]')
                expect(toggle_front).to_be_visible(timeout=3000)
                toggle_front.click()

                # Enable ZIP on left opening
                toggle_left = page.locator('.zip-toggle-btn[data-key="left_0"]')
                expect(toggle_left).to_be_visible(timeout=3000)
                toggle_left.click()

                # Enable ZIP on right opening
                toggle_right = page.locator('.zip-toggle-btn[data-key="right_0"]')
                expect(toggle_right).to_be_visible(timeout=3000)
                toggle_right.click()

                # Verify all three toggles show "ZIP ✓"
                assert "ZIP" in toggle_front.inner_text(), (
                    f"front_0 toggle should show ZIP enabled, got: {toggle_front.inner_text()!r}"
                )
                assert "ZIP" in toggle_left.inner_text(), (
                    f"left_0 toggle should show ZIP enabled, got: {toggle_left.inner_text()!r}"
                )
                assert "ZIP" in toggle_right.inner_text(), (
                    f"right_0 toggle should show ZIP enabled, got: {toggle_right.inner_text()!r}"
                )

                # Calculate
                calc_btn = page.locator('#calc-btn')
                expect(calc_btn).to_be_visible(timeout=3000)
                calc_btn.click()

                results = page.locator('#results-section')
                expect(results).to_be_visible(timeout=15000)
                results_text = results.inner_text()

                # Verify the ZIP count in the results header is ≥ 3
                zip_count_match = re.search(r'ZIP-маркиз[ыа]\s*\(\s*(\d+)\s*шт\.', results_text)
                assert zip_count_match is not None, (
                    f"Expected 'ZIP-маркизы (N шт.)' pattern in results, got:\n{results_text[:800]}"
                )
                zip_count = int(zip_count_match.group(1))
                assert zip_count >= 3, (
                    f"Expected ≥3 ZIP units in results block (3 openings enabled), got count={zip_count}"
                )

            finally:
                browser.close()

    def test_zip_overlay_notice_when_glazing_active(self):
        """Enable S500 glazing on front opening, then enable ZIP; overlay notice must appear."""
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                # Navigate and configure B500NEW 4×3 m
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()
                page.locator('#variant-options [data-variant="auto"]').click()
                page.locator('#input-width').fill("4")
                page.locator('#input-length').fill("3")
                page.locator('#input-length').press("Tab")

                expect(page.locator('#step-4')).to_be_visible(timeout=5000)

                # Open the facade/ZIP spoiler
                page.locator('details.facade-spoiler > summary').click()

                # Select S500 glazing on the front opening via the facade type selector
                facade_sel = page.locator(
                    'select.facade-type-sel[data-side="front"][data-bay="0"]'
                )
                expect(facade_sel).to_be_visible(timeout=5000)
                facade_sel.select_option("S500")

                # Now enable ZIP on the same front opening from the ZIP table
                zip_table = page.locator('#zip-opening-table')
                expect(zip_table).to_be_visible(timeout=5000)

                toggle_front = page.locator('.zip-toggle-btn[data-key="front_0"]')
                expect(toggle_front).to_be_visible(timeout=3000)
                toggle_front.click()

                # The ZIP table row for front_0 should now display the overlay notice
                # "Накладной монтаж" because glazing is active on the same opening
                front_row = page.locator('#zip-opening-table tr[data-key="front_0"]')
                expect(front_row).to_be_visible(timeout=3000)
                expect(front_row).to_contain_text("Накладной монтаж", timeout=3000)

            finally:
                browser.close()

    def test_zip_match_pergola_button_appears_and_updates_color(self):
        """Match button appears when glazing color differs from ZIP color; clicking it syncs the colors.

        Flow:
        1. Configure B500NEW 4×3 m with S500 glazing on front opening.
           S500 defaults to color ral7016, which maps to ZIP color ral7024.
        2. Enable ZIP on front_0 — ZIP color defaults to ral9016.
        3. Because ral7024 (desired) != ral9016 (current) the '≈ pergola' match
           button must appear.
        4. The button's data-match attribute must equal 'ral7024'.
        5. After clicking the button the ZIP color becomes ral7024 and the button
           disappears (colors now match so showMatchBtn becomes false).
        """
        with sync_playwright() as pw:
            browser, page = _open_page(pw)
            try:
                # Navigate and configure B500NEW 4×3 m
                page.goto(BASE_URL + "/", wait_until="networkidle")
                page.locator('[data-type="B500NEW"]').click()
                page.locator('#variant-options [data-variant="auto"]').click()
                page.locator('#input-width').fill("4")
                page.locator('#input-length').fill("3")
                page.locator('#input-length').press("Tab")

                expect(page.locator('#step-4')).to_be_visible(timeout=5000)

                # Open the facade/ZIP spoiler
                page.locator('details.facade-spoiler > summary').click()

                # Enable ZIP on front_0 FIRST so it gets the default color ral9016.
                # The match button only appears when the current ZIP color differs
                # from the glazing-mapped color; if ZIP is enabled after glazing is
                # set, it already inherits the mapped color and no button appears.
                zip_table = page.locator('#zip-opening-table')
                expect(zip_table).to_be_visible(timeout=5000)

                toggle_front = page.locator('.zip-toggle-btn[data-key="front_0"]')
                expect(toggle_front).to_be_visible(timeout=3000)
                toggle_front.click()

                # NOW select S500 glazing on front_0 (defaults to ral7016 color).
                # Selecting glazing also disables the ZIP on this opening (the UI
                # does not allow facade/glazing and ZIP at the same position by
                # default).  The ZIP state record is preserved (color = ral9016).
                facade_sel = page.locator(
                    'select.facade-type-sel[data-side="front"][data-bay="0"]'
                )
                expect(facade_sel).to_be_visible(timeout=5000)
                facade_sel.select_option("S500")

                # Re-enable ZIP on front_0.  Now buildZipTable renders the params
                # card with: curZipColor=ral9016 (saved), matchColor=ral7024
                # (ral7016→ral7024 via _ZIP_NEAREST_MAP), hasGlzColor=true
                # → showMatchBtn = true → "≈ pergola" button is rendered.
                toggle_front2 = page.locator('.zip-toggle-btn[data-key="front_0"]')
                expect(toggle_front2).to_be_visible(timeout=3000)
                toggle_front2.click()

                # Assert the match button is visible
                # ral7016 (glazing) → ral7024 (nearest ZIP) ≠ ral9016 (current ZIP)
                match_btn = page.locator('.zip-match-btn[data-key="front_0"]')
                expect(match_btn).to_be_visible(timeout=5000)

                # Button label must contain the "≈ pergola" text
                btn_text = match_btn.inner_text()
                assert "≈" in btn_text or "\u2248" in btn_text, (
                    f"Expected '≈' in match button label, got: {btn_text!r}"
                )

                # data-match must be ral7024 (the nearest ZIP color for ral7016)
                data_match = match_btn.get_attribute("data-match")
                assert data_match == "ral7024", (
                    f"Expected data-match='ral7024', got: {data_match!r}"
                )

                # Click the match button — ZIP color updates to ral7024
                match_btn.click()

                # After clicking, the button must disappear because the ZIP color
                # now matches the glazing-derived color (ral7024 == ral7024)
                expect(match_btn).not_to_be_visible(timeout=5000)

                # The ral7024 color swatch in the ZIP color picker must be selected.
                # Selected swatches get: box-shadow:0 0 0 2px #1a3a6e,0 0 0 4px white
                swatch_ral7024 = page.locator(
                    'button.zip-cp-opt[data-key="front_0"][data-color="ral7024"]'
                )
                expect(swatch_ral7024).to_be_visible(timeout=3000)
                swatch_style = swatch_ral7024.get_attribute("style") or ""
                assert "box-shadow" in swatch_style, (
                    f"Expected ral7024 swatch to appear selected (box-shadow ring), got style: {swatch_style!r}"
                )

            finally:
                browser.close()
