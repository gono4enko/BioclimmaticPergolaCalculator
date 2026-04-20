"""API integration tests for the ZIP awning selection and pricing flow.

Covers task #78: verifies that the ZIP awning feature works correctly
from payload wiring through calculation to results rendering.

These tests call POST /api/calculate with a zip_openings payload and assert
the ZIP block in the JSON response (count, openings, fabric, drive, price).

For the browser UI flow see tests/test_zip_awning_e2e.py which uses Playwright
to drive the full step-4 toggle → Soltis + Somfy → calculate → КП verification.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app


@pytest.fixture
def app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-secret'})


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


_BASE_PAYLOAD = {
    "pergola_type": "B500NEW",
    "lamella_type": "B500-25NEW",
    "lamella_size": "250",
    "width": 4.0,
    "length": 3.0,
    "height": 3.0,
    "lighting": ["white_led"],
    "installation": True,
    "selected_variant": "",
    "facade_type": "",
    "facade_openings": [],
    "glazing_openings": [],
}


def _calculate(client, zip_openings):
    payload = dict(_BASE_PAYLOAD, zip_openings=zip_openings)
    resp = client.post('/api/calculate', json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    data = resp.get_json()
    assert data.get('success'), f"Calculation failed: {data.get('error')}"
    return data


class TestZipAwningFlow:
    """ZIP awning payload wiring and calculation result tests."""

    def test_no_zip_returns_empty_zip_block(self, client):
        """Without zip_openings the ZIP block in the result has count=0."""
        data = _calculate(client, zip_openings=[])
        zip_block = data['result']['zip']
        assert zip_block['count'] == 0, f"Expected 0 ZIP units, got {zip_block['count']}"
        assert zip_block['openings'] == [], "Expected empty openings list"
        assert zip_block['price'] == 0.0, f"Expected price 0, got {zip_block['price']}"

    def test_front_zip_veozip_manual_creates_one_unit(self, client):
        """Enabling ZIP on the front opening with default options produces 1 unit."""
        zip_openings = [{'side': 'front', 'bay': 0, 'fabric': 'veozip',
                         'color': 'ral9016', 'drive': 'manual', 'count': 1}]
        data = _calculate(client, zip_openings)
        zip_block = data['result']['zip']
        assert zip_block['count'] >= 1, (
            f"Expected ≥1 ZIP unit, got {zip_block['count']}")
        assert len(zip_block['openings']) == 1, (
            f"Expected 1 opening entry, got {len(zip_block['openings'])}")
        op = zip_block['openings'][0]
        assert op['side'] == 'front', f"Expected side=front, got {op['side']}"
        assert op['fabric'] == 'veozip', f"Expected fabric=veozip, got {op['fabric']}"
        assert op['drive'] == 'manual', f"Expected drive=manual, got {op['drive']}"
        assert op['total_eur'] > 0, f"Expected non-zero price, got {op['total_eur']}"

    def test_soltis_fabric_costs_more_than_veozip(self, client):
        """Soltis fabric (+15 €/m²) results in a higher price than Veozip."""
        base_zip = [{'side': 'front', 'bay': 0, 'fabric': 'veozip',
                     'color': 'ral9016', 'drive': 'manual', 'count': 1}]
        soltis_zip = [{'side': 'front', 'bay': 0, 'fabric': 'soltis',
                       'color': 'ral9016', 'drive': 'manual', 'count': 1}]
        price_base = _calculate(client, base_zip)['result']['zip']['price']
        price_soltis = _calculate(client, soltis_zip)['result']['zip']['price']
        assert price_soltis > price_base, (
            f"Soltis ({price_soltis}) should cost more than Veozip ({price_base})")

    def test_somfy_electric_drive_wired_correctly(self, client):
        """Somfy electric drive: response records drive=somfy and adds pult info."""
        zip_openings = [{'side': 'front', 'bay': 0, 'fabric': 'soltis',
                         'color': 'ral9016', 'drive': 'somfy', 'count': 1}]
        data = _calculate(client, zip_openings)
        zip_block = data['result']['zip']
        op = zip_block['openings'][0]
        assert op['drive'] == 'somfy', f"Expected drive=somfy, got {op['drive']}"
        assert zip_block['pult_name'] is not None, "Expected pult_name for electric drive"
        assert zip_block['pult_eur'] > 0, (
            f"Expected pult price > 0, got {zip_block['pult_eur']}")

    def test_somfy_costs_at_least_as_much_as_manual(self, client):
        """Electric Somfy drive must cost more than manual (50 € base)."""
        manual_zip = [{'side': 'front', 'bay': 0, 'fabric': 'veozip',
                       'color': 'ral9016', 'drive': 'manual', 'count': 1}]
        somfy_zip = [{'side': 'front', 'bay': 0, 'fabric': 'veozip',
                      'color': 'ral9016', 'drive': 'somfy', 'count': 1}]
        price_manual = _calculate(client, manual_zip)['result']['zip']['price']
        price_somfy = _calculate(client, somfy_zip)['result']['zip']['price']
        assert price_somfy > price_manual, (
            f"Somfy electric ({price_somfy}) should cost more than manual ({price_manual})")

    def test_items_list_contains_zip_line_for_front_opening(self, client):
        """The items list in the result includes a line item for the ZIP awning."""
        zip_openings = [{'side': 'front', 'bay': 0, 'fabric': 'soltis',
                         'color': 'ral9016', 'drive': 'somfy', 'count': 1}]
        data = _calculate(client, zip_openings)
        items = data['result'].get('items', [])
        zip_items = [it for it in items if 'ZIP' in it.get('name', '')]
        assert len(zip_items) >= 1, (
            f"Expected at least one ZIP line in items; found: {[i['name'] for i in items]}")
        assert zip_items[0]['price'] > 0, (
            f"ZIP line item price should be > 0, got {zip_items[0]['price']}")

    def test_zip_total_contributes_to_overall_price(self, client):
        """Adding ZIP raises the total price compared to no ZIP."""
        price_no_zip = _calculate(client, [])['result']['total_price_eur']
        zip_openings = [{'side': 'front', 'bay': 0, 'fabric': 'soltis',
                         'color': 'ral9016', 'drive': 'somfy', 'count': 1}]
        price_with_zip = _calculate(client, zip_openings)['result']['total_price_eur']
        assert price_with_zip > price_no_zip, (
            f"Total price with ZIP ({price_with_zip}) should exceed "
            f"price without ZIP ({price_no_zip})")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
