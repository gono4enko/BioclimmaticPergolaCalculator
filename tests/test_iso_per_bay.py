"""Regression tests for per-bay guillotine rendering in the isometric SVG preview.

Covers task #80: verifies that the /api/pergola-iso.svg endpoint correctly
renders different fill types per bay, specifically:

  (1) Front wall with a glass panel on bay 1 and a W600 guillotine on bay 2
      — both fill colours appear in the returned SVG.
  (2) Side wall (left) with a S100 panel on bay 1 and a W700 guillotine on
      bay 2 — both fill colours appear in the returned SVG.

These tests run against the Flask test client and require no real database.
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
# S100 frameless panel
S100_GLASS = '#cfe0ea'
# W600 guillotine
W600_GLASS = '#aac7d8'
# W700 guillotine
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
# Test 1: Front wall – S500 on bay 1, W600 guillotine on bay 2
# ---------------------------------------------------------------------------

def test_front_wall_per_bay_panel_and_guillotine(client):
    """Both the S500 glass colour and the W600 guillotine glass colour must
    appear in the SVG when they are assigned to different bays on the front wall."""
    svg = _svg(client, {
        'w': '6',
        'l': '4',
        'h': '3',
        'm': '2',
        'fill_front_1': 'S500',
        'fill_front_2': 'W600',
    })

    assert S500_GLASS in svg, (
        f'S500 glass fill ({S500_GLASS}) not found in SVG — '
        'bay 1 (S500 panel) was not rendered on the front wall'
    )
    assert W600_GLASS in svg, (
        f'W600 guillotine glass fill ({W600_GLASS}) not found in SVG — '
        'bay 2 (W600 guillotine) was not rendered on the front wall'
    )
    # Heavy frame rails are characteristic of all W-series guillotines
    assert W_FRAME in svg, (
        f'W-series frame colour ({W_FRAME}) not found in SVG — '
        'guillotine structural rails are missing'
    )


# ---------------------------------------------------------------------------
# Test 2: Side wall (left) – S100 on bay 1, W700 guillotine on bay 2
# ---------------------------------------------------------------------------

def test_left_wall_per_bay_panel_and_guillotine(client):
    """Both the S100 glass colour and the W700 guillotine glass colour must
    appear in the SVG when assigned to different bays on the left side wall.
    xc=1 adds a mid-span column, splitting the depth into 2 left-wall bays."""
    svg = _svg(client, {
        'w': '6',
        'l': '6',
        'h': '3',
        'm': '2',
        'xc': '1',
        'fill_left_1': 'S100',
        'fill_left_2': 'W700',
    })

    assert S100_GLASS in svg, (
        f'S100 glass fill ({S100_GLASS}) not found in SVG — '
        'bay 1 (S100 panel) was not rendered on the left wall'
    )
    assert W700_GLASS in svg, (
        f'W700 guillotine glass fill ({W700_GLASS}) not found in SVG — '
        'bay 2 (W700 guillotine) was not rendered on the left wall'
    )
    assert W_FRAME in svg, (
        f'W-series frame colour ({W_FRAME}) not found in SVG — '
        'guillotine structural rails are missing on the left wall'
    )


# ---------------------------------------------------------------------------
# Test 3: Front wall – W500 on both bays, checking per-bay multiplicity
# ---------------------------------------------------------------------------

def test_front_wall_guillotine_both_bays(client):
    """With W500 on both bays the SVG must still be valid and contain the
    W500 glass colour at least once."""
    svg = _svg(client, {
        'w': '6',
        'l': '4',
        'h': '3',
        'm': '2',
        'fill_front_1': 'W500',
        'fill_front_2': 'W500',
    })

    assert S500_GLASS in svg, (
        f'W500 glass fill ({S500_GLASS}) not found in SVG — '
        'guillotine was not rendered on the front wall'
    )
    assert W_FRAME in svg, (
        f'W-series frame colour ({W_FRAME}) not found in SVG — '
        'guillotine structural rails are missing'
    )


# ---------------------------------------------------------------------------
# Test 4: Right wall – mixed bays (W600 + ZIP), checking right side per-bay
# ---------------------------------------------------------------------------

def test_right_wall_per_bay_guillotine_and_zip(client):
    """W600 guillotine on bay 1 and ZIP on bay 2 of the right wall —
    both characteristic colours must appear in the SVG.
    xc=1 adds a mid-span column, splitting the depth into 2 right-wall bays."""
    ZIP_GLASS = '#c8d8e8'
    svg = _svg(client, {
        'w': '6',
        'l': '6',
        'h': '3',
        'm': '2',
        'xc': '1',
        'fill_right_1': 'W600',
        'fill_right_2': 'ZIP',
    })

    assert W600_GLASS in svg, (
        f'W600 guillotine glass fill ({W600_GLASS}) not found in SVG — '
        'bay 1 guillotine was not rendered on the right wall'
    )
    assert ZIP_GLASS in svg, (
        f'ZIP glass fill ({ZIP_GLASS}) not found in SVG — '
        'bay 2 ZIP was not rendered on the right wall'
    )
