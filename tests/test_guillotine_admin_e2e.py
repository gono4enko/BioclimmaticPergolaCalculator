"""Playwright end-to-end tests for the W500/W600/W700 guillotine glazing price
editing admin flow.

Covers task #84 — drives a real browser through the admin UI to verify:
  - W500/W600/W700 can be selected in the #glazSystem dropdown
  - The price matrix table loads and displays correct dimensions per series
  - A cell override is persisted (via API setup) and highlighted in the UI
  - The "Сбросить к заводским" (reset) button removes overrides
  - Surcharge settings for W-series appear in the #glazSettingsWrap section

Tests are skipped automatically when `playwright` is not installed.
Run against a live server:  BASE_URL=http://localhost:5000 pytest tests/test_guillotine_admin_e2e.py -v
"""

import os

import pytest

try:
    from playwright.sync_api import sync_playwright, expect
    _PW_AVAILABLE = True
except ImportError:
    _PW_AVAILABLE = False

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
# ADMIN_PASSWORD must be supplied via environment — no hardcoded fallback so
# real credentials are never committed.  Tests skip when the variable is unset.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
_HAS_ADMIN_PW = bool(ADMIN_PASSWORD)

pytestmark = [
    pytest.mark.skipif(
        not _PW_AVAILABLE,
        reason=(
            "playwright package not installed — "
            "install with: pip install playwright && playwright install chromium"
        ),
    ),
    pytest.mark.skipif(
        not _HAS_ADMIN_PW,
        reason="ADMIN_PASSWORD env var not set — admin UI tests require it",
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_page(playwright):
    """Launch a headless Chromium browser and return (browser, context, page)."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    return browser, context, page


def _admin_login(page):
    """Navigate to admin login and authenticate, landing on /admin/prices."""
    page.goto(BASE_URL + "/admin/login", wait_until="networkidle")
    page.locator('input[type="password"]').fill(ADMIN_PASSWORD)
    page.locator('button[type="submit"], input[type="submit"]').click()
    page.wait_for_url("**/admin/prices", timeout=5000)


def _api_save_cell(page, system, w, h, price):
    """POST /admin/glazing-save-cell using the browser context (inherits session cookie)."""
    resp = page.evaluate("""
        async ([system, w, h, price]) => {
            const r = await fetch('/admin/glazing-save-cell', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({system, config: 'all', w, h, price})
            });
            return await r.json();
        }
    """, [system, w, h, price])
    return resp


def _api_reset(page, system):
    """POST /admin/glazing-reset using the browser context (inherits session cookie)."""
    resp = page.evaluate("""
        async (system) => {
            const r = await fetch('/admin/glazing-reset', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({system})
            });
            return await r.json();
        }
    """, system)
    return resp


def _load_matrix(page, system):
    """Select a system in the dropdown and click 'Показать матрицу' for glazing."""
    page.locator("#glazSystem").select_option(system)
    # There are multiple 'Показать матрицу' buttons on the page (glazing + ZIP).
    # Scope to the glazing card by its unique header text.
    glazing_card = page.locator(".card", has=page.locator("#glazSystem"))
    glazing_card.locator("button.btn-primary", has_text="Показать матрицу").click()
    # Wait for the fetch to complete and the table to render
    expect(page.locator("#glazWrap table.price-table")).to_be_visible(timeout=6000)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGuillotineAdminUI:
    """Playwright browser tests for the W-series price matrix admin flow."""

    def test_w500_matrix_loads_with_correct_dimensions(self):
        """W500 matrix table loads, shows correct width/height axes, hides config group."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)
                _load_matrix(page, "W500")

                # Matrix table must be present
                table = page.locator("#glazWrap table.price-table")
                expect(table).to_be_visible(timeout=5000)

                table_text = table.inner_text()

                # W500 width axis starts at 1.0 m (not 2.0 like W600/W700)
                assert "1.00" in table_text, (
                    f"W500 table should contain 1.00 m column; got:\n{table_text[:300]}"
                )
                # W500 height axis starts at 1.5 m
                assert "1.50" in table_text, (
                    f"W500 table should contain 1.50 m row; got:\n{table_text[:300]}"
                )

                # Config group is hidden for W-series (single 'all' config)
                config_group = page.locator("#glazConfigGroup")
                assert config_group.evaluate(
                    "el => el.style.display === 'none' || el.offsetParent === null"
                ), "W500: #glazConfigGroup should be hidden"

                # Edit button must be visible
                expect(page.locator("#glazEditBtn")).to_be_visible(timeout=3000)

                # Note mentions "ceiling" rounding (W-series specific)
                wrap_text = page.locator("#glazWrap").inner_text()
                assert "ceiling" in wrap_text.lower(), (
                    f"W500 matrix note should mention ceiling rounding; got:\n{wrap_text[-200:]}"
                )

            finally:
                browser.close()

    def test_w600_matrix_starts_at_2m_not_1m(self):
        """W600 matrix loads with width axis starting at 2.00 m (no 1.00 m column)."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)
                _load_matrix(page, "W600")

                table = page.locator("#glazWrap table.price-table")
                expect(table).to_be_visible(timeout=5000)

                header_text = table.locator("tr:first-child").inner_text()

                assert "2.00" in header_text, (
                    f"W600 header should contain 2.00 m; got: {header_text!r}"
                )
                assert "1.00" not in header_text, (
                    f"W600 header should NOT contain 1.00 m (starts at 2.0); "
                    f"got: {header_text!r}"
                )
                # Height row should also start at 2.0
                rows_text = table.inner_text()
                assert "2.00" in rows_text, (
                    f"W600 table should have 2.00 m height row; got:\n{rows_text[:300]}"
                )

            finally:
                browser.close()

    def test_w700_matrix_loads_correctly(self):
        """W700 matrix loads with correct dimensions (same axes as W600)."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)
                _load_matrix(page, "W700")

                table = page.locator("#glazWrap table.price-table")
                expect(table).to_be_visible(timeout=5000)

                header_text = table.locator("tr:first-child").inner_text()
                rows_text = table.inner_text()

                assert "2.00" in header_text, (
                    f"W700 header should contain 2.00 m; got: {header_text!r}"
                )
                assert "2.50" in header_text, (
                    f"W700 header should contain 2.50 m; got: {header_text!r}"
                )
                assert "1.00" not in header_text, (
                    f"W700 header should NOT contain 1.00 m; got: {header_text!r}"
                )
                assert "2.50" in rows_text, (
                    f"W700 table should have 2.50 m height row; got:\n{rows_text[:300]}"
                )

            finally:
                browser.close()

    def test_cell_override_highlights_in_w500_matrix(self):
        """After saving a cell override via API, the cell shows yellow highlight in UI."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)

                # Clean up any prior override for this test cell
                _api_reset(page, "W500")

                # Set an override via the in-browser fetch (inherits auth cookie)
                result = _api_save_cell(page, "W500", 1.0, 1.5, 9999)
                assert result.get("ok") is True, (
                    f"API save-cell should return ok=True; got: {result}"
                )

                # Load/reload matrix to show the override
                _load_matrix(page, "W500")

                # Overridden cell must have class "cell-overridden" (yellow)
                overridden = page.locator("#glazWrap td.cell-overridden")
                expect(overridden.first).to_be_visible(timeout=5000)

                # The ↺ per-cell reset button must appear inside the overridden cell
                reset_btn = page.locator("#glazWrap td.cell-overridden .cell-reset-btn")
                expect(reset_btn.first).to_be_visible(timeout=3000)

                # Badge must warn about overrides
                wrap_text = page.locator("#glazWrap").inner_text()
                assert "⚠" in wrap_text or "изменено" in wrap_text, (
                    f"Expected override warning badge; got:\n{wrap_text[-300:]}"
                )

            finally:
                # Cleanup
                _api_reset(page, "W500")
                browser.close()

    def test_reset_all_w500_overrides_restores_factory_badge(self):
        """'Сбросить к заводским' removes W500 overrides; factory badge appears."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)

                # Ensure at least one override exists
                _api_reset(page, "W500")
                result = _api_save_cell(page, "W500", 1.0, 1.5, 9999)
                assert result.get("ok") is True, f"Setup save-cell failed: {result}"

                # Load matrix so the reset button is active
                _load_matrix(page, "W500")

                # Accept the confirm() dialog before clicking reset.
                # Must register the handler BEFORE the click that triggers it.
                page.on("dialog", lambda dialog: dialog.accept())
                glazing_card = page.locator(".card", has=page.locator("#glazSystem"))
                glazing_card.locator("button.btn-outline-danger").click()

                # Wait for the async reset request + matrix reload to complete.
                # Note: loadGlazingMatrix() clears #glazStatus immediately on start,
                # so we verify the observable result (factory badge) rather than status text.
                page.wait_for_function(
                    "() => document.querySelector('#glazWrap')?.innerText?.includes('Все цены заводские')",
                    timeout=8000
                )

                # Factory badge must appear (no more overrides)
                wrap_text = page.locator("#glazWrap").inner_text()
                assert "Все цены заводские" in wrap_text, (
                    f"Expected green factory badge after reset; got:\n{wrap_text[-300:]}"
                )

                # No overridden cells should remain
                overridden = page.locator("#glazWrap td.cell-overridden")
                assert overridden.count() == 0, (
                    f"Expected 0 overridden cells after reset; found {overridden.count()}"
                )

            finally:
                browser.close()

    def test_edit_mode_shows_inputs_and_save_persists_cell(self):
        """Edit mode renders input fields; saving a change persists it to DB."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)

                # Clean up any prior override
                _api_reset(page, "W500")

                _load_matrix(page, "W500")

                # Enter edit mode
                page.locator("#glazEditBtn").click()

                # Inputs should appear in the table
                inputs = page.locator("#glazWrap input[type='number']")
                expect(inputs.first).to_be_visible(timeout=3000)

                # Read original value of first cell, set a new one
                original = inputs.first.input_value()
                new_val = str(int(float(original)) + 500)
                inputs.first.fill(new_val)

                # Save changes
                expect(page.locator("#glazSaveBtn")).to_be_visible(timeout=2000)
                page.locator("#glazSaveBtn").click()

                # After save, the matrix reloads and #glazStatus is cleared by loadGlazingMatrix().
                # Verify the actual result: at least one cell should be highlighted yellow
                # (cell-overridden), which proves the save succeeded and the matrix reloaded.
                overridden = page.locator("#glazWrap td.cell-overridden")
                expect(overridden.first).to_be_visible(timeout=8000)

            finally:
                _api_reset(page, "W500")
                browser.close()

    def test_w_series_surcharges_visible_in_settings_section(self):
        """W-series surcharge settings (RAL special, plavnik rates) appear in settings panel."""
        with sync_playwright() as pw:
            browser, context, page = _open_page(pw)
            try:
                _admin_login(page)

                # Settings panel is populated on DOMContentLoaded via fetch.
                # Wait until it has content (at least one input should appear).
                settings_wrap = page.locator("#glazSettingsWrap")
                settings_wrap.scroll_into_view_if_needed()
                expect(settings_wrap.locator("input[type='number']").first).to_be_visible(timeout=6000)

                wrap_text = settings_wrap.inner_text()

                assert "RAL special" in wrap_text or "W_RAL_SPECIAL" in wrap_text, (
                    f"W RAL special label missing from settings; got:\n{wrap_text[:500]}"
                )
                assert "W500" in wrap_text and "плавник" in wrap_text.lower(), (
                    f"W500 plavnik label missing from settings; got:\n{wrap_text[:500]}"
                )
                assert "W600" in wrap_text, (
                    f"W600 label missing from settings; got:\n{wrap_text[:500]}"
                )
                assert "W700" in wrap_text, (
                    f"W700 label missing from settings; got:\n{wrap_text[:500]}"
                )

            finally:
                browser.close()
