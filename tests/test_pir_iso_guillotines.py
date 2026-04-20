"""Regression tests for per-bay guillotine rendering in the PIR (B600) isometric SVG preview.

Covers task #96: verifies that the /api/pergola-iso.svg endpoint with pir=1
correctly renders different fill types per bay using generate_pir_iso_svg,
mirroring the assertions already present in tests/test_iso_per_bay.py for the
standard bioclimatic pergola.

  (1) Front wall with a S500 panel on bay 1 and a W600 guillotine on bay 2
      — both fill colours appear in the returned SVG.
  (2) Side wall (left) with a W700 guillotine on bay 1 and a S500 panel on bay 2
      — both fill colours appear in the returned SVG.
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app

# ---------------------------------------------------------------------------
# Distinctive SVG fill colours produced by _iso_fill_face
# ---------------------------------------------------------------------------
# S500 glass panel
S500_GLASS = '#bcd4e0'
# W600 guillotine glass
W600_GLASS = '#aac7d8'
# W700 guillotine glass
W700_GLASS = '#9bbacd'
# Dark frame colour shared by all W-series guillotines (heavy top/bottom rails)
W_FRAME = '#1f2a35'


# ---------------------------------------------------------------------------
# Fixture – Flask test client with TESTING mode, DB patched out
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def client():
    """Create a Flask test client without a real database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch('psycopg2.connect', return_value=mock_conn):
        app = create_app({'TESTING': True, 'DATABASE_URL': 'postgresql://test'})
        with app.test_client() as c:
            yield c


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _svg(client, params: dict) -> str:
    """GET /api/pergola-iso.svg with the given query params, assert 200."""
    qs = '&'.join(f'{k}={v}' for k, v in params.items())
    resp = client.get(f'/api/pergola-iso.svg?{qs}')
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    assert resp.content_type.startswith('image/svg+xml')
    return resp.data.decode('utf-8')


# ---------------------------------------------------------------------------
# Test 1 (PIR): Front wall – S500 on bay 1, W600 guillotine on bay 2
# ---------------------------------------------------------------------------

def test_pir_front_wall_panel_and_guillotine(client):
    """B600/PIR: both the S500 glass colour and the W600 guillotine glass colour
    must appear in the SVG when assigned to different bays on the front wall."""
    svg = _svg(client, {
        'w': '6',
        'l': '4',
        'h': '3',
        'm': '2',
        'pir': '1',
        'fill_front_1': 'S500',
        'fill_front_2': 'W600',
    })

    assert S500_GLASS in svg, (
        f'S500 glass fill ({S500_GLASS}) not found in PIR SVG — '
        'bay 1 (S500 panel) was not rendered on the front wall'
    )
    assert W600_GLASS in svg, (
        f'W600 guillotine glass fill ({W600_GLASS}) not found in PIR SVG — '
        'bay 2 (W600 guillotine) was not rendered on the front wall'
    )
    assert W_FRAME in svg, (
        f'W-series frame colour ({W_FRAME}) not found in PIR SVG — '
        'guillotine structural rails are missing on the front wall'
    )


# ---------------------------------------------------------------------------
# Test 2 (PIR): Left wall – W700 guillotine on bay 1, S500 panel on bay 2
# ---------------------------------------------------------------------------

def test_pir_left_wall_guillotine_and_panel(client):
    """B600/PIR: both the W700 guillotine glass colour and the S500 glass colour
    must appear in the SVG when assigned to different bays on the left side wall.
    xc=1 adds a mid-span column, splitting the depth into 2 left-wall bays."""
    svg = _svg(client, {
        'w': '6',
        'l': '6',
        'h': '3',
        'm': '2',
        'xc': '1',
        'pir': '1',
        'fill_left_1': 'W700',
        'fill_left_2': 'S500',
    })

    assert W700_GLASS in svg, (
        f'W700 guillotine glass fill ({W700_GLASS}) not found in PIR SVG — '
        'bay 1 (W700 guillotine) was not rendered on the left wall'
    )
    assert S500_GLASS in svg, (
        f'S500 glass fill ({S500_GLASS}) not found in PIR SVG — '
        'bay 2 (S500 panel) was not rendered on the left wall'
    )
    assert W_FRAME in svg, (
        f'W-series frame colour ({W_FRAME}) not found in PIR SVG — '
        'guillotine structural rails are missing on the left wall'
    )
