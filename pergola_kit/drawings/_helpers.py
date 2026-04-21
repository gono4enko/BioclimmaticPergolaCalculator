"""Auto-extracted from Decolife flask_app/utils.py — verbatim copies of SVG generators.
No Flask, no DB, no admin dependencies. Standard library only."""
import math

# === SVG dimension constants (from flask_app/utils.py L445-455) ===
DIM_COLOR = '#1a3a6e'
DIM_FONT = '13px'
DIM_SMALL_FONT = '10px'
DIM_OFFSET = 26
DIM_TEXT_GAP = 14
DIM_EXT_LEN = 6
DIM_TARGET_PX = 280
DIM_MARGIN_L = 110
DIM_MARGIN_R = 64
DIM_MARGIN_T = 46
DIM_MARGIN_B = 64


def _scale_from_ref(ref):
    if not ref or ref <= 0:
        ref = 5.0
    return DIM_TARGET_PX / float(ref)


def _dim_defs(prefix='d'):
    return (
        f'<defs><marker id="{prefix}-ah" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">'
        f'<path d="M0,0 L8,3.5 L0,7" fill="{DIM_COLOR}"/></marker>'
        f'<marker id="{prefix}-aht" markerWidth="9" markerHeight="7" refX="0" refY="3.5" orient="auto">'
        f'<path d="M8,0 L0,3.5 L8,7" fill="{DIM_COLOR}"/></marker>'
        f'<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="6" stroke="#666" stroke-width="0.7"/></pattern></defs>'
    )


def _dim_h(x1, x2, y, label, prefix='d', below=True, font=None):
    f = font or DIM_FONT
    ext1_y0 = y - DIM_EXT_LEN if below else y + DIM_EXT_LEN
    ext1_y1 = y + 2 if below else y - 2
    text_y = y + DIM_TEXT_GAP if below else y - DIM_TEXT_GAP + 4
    return (
        f'<line x1="{x1}" y1="{ext1_y0}" x2="{x1}" y2="{ext1_y1}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{x2}" y1="{ext1_y0}" x2="{x2}" y2="{ext1_y1}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{DIM_COLOR}" stroke-width="1.2" '
        f'marker-start="url(#{prefix}-aht)" marker-end="url(#{prefix}-ah)"/>'
        f'<text x="{(x1+x2)/2}" y="{text_y}" text-anchor="middle" '
        f'font-size="{f}" font-weight="bold" fill="{DIM_COLOR}">{label}</text>'
    )


def _dim_v(x, y1, y2, label, prefix='d', side='left', font=None):
    f = font or DIM_FONT
    ext_x0 = x + DIM_EXT_LEN if side == 'left' else x - DIM_EXT_LEN
    ext_x1 = x - 2 if side == 'left' else x + 2
    text_x = x - DIM_TEXT_GAP if side == 'left' else x + DIM_TEXT_GAP
    return (
        f'<line x1="{ext_x0}" y1="{y1}" x2="{ext_x1}" y2="{y1}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{ext_x0}" y1="{y2}" x2="{ext_x1}" y2="{y2}" stroke="{DIM_COLOR}" stroke-width="0.6"/>'
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{DIM_COLOR}" stroke-width="1.2" '
        f'marker-start="url(#{prefix}-aht)" marker-end="url(#{prefix}-ah)"/>'
        f'<text x="{text_x}" y="{(y1+y2)/2}" text-anchor="middle" '
        f'font-size="{f}" font-weight="bold" fill="{DIM_COLOR}" '
        f'transform="rotate(-90,{text_x},{(y1+y2)/2})">{label}</text>'
    )


def _draw_zip_fill(x, y, w, h):
    """Draw a vertical ZIP roller awning in elevation view.
    Structure: cassette box (top) → side guide rails → fabric panel → bottom bar.
    Matches the appearance of Decolife/SIMU ZIP100/ZIP130 technical drawings.
    """
    if w < 2 or h < 2:
        return ''
    cassette_c = '#1e2d3a'   # dark aluminium cassette / rails
    rail_c     = '#253545'
    fabric_c   = '#c8d8e8'   # light grey-blue, typical solar-screen tone
    stripe_c   = '#8aa0b2'   # horizontal weft lines
    bottom_c   = '#1e2d3a'   # weighted hem bar

    cassette_h = max(3.5, min(h * 0.07, 11))
    rail_w     = max(2.0, w * 0.04)
    bottom_h   = max(2.0, h * 0.04)

    fy = y + cassette_h                     # fabric top edge
    fh = max(1.0, h - cassette_h - bottom_h)  # fabric height
    fx = x + rail_w                         # fabric left edge
    fw = max(1.0, w - 2 * rail_w)           # fabric width

    out = ''
    # 1. Top cassette housing (where the roller and fabric reel live)
    out += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{cassette_h:.1f}" '
            f'fill="{cassette_c}" rx="1" opacity="0.92"/>')
    # Small drum-circle hint inside the cassette
    dr = max(1.0, cassette_h * 0.30)
    dcx, dcy = x + w / 2, y + cassette_h / 2
    out += (f'<circle cx="{dcx:.1f}" cy="{dcy:.1f}" r="{dr:.1f}" '
            f'fill="none" stroke="#7090a8" stroke-width="0.7" opacity="0.55"/>')

    # 2. Left guide rail
    out += (f'<rect x="{x:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bottom_h:.1f}" fill="{rail_c}" opacity="0.88"/>')
    # 3. Right guide rail
    out += (f'<rect x="{x + w - rail_w:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bottom_h:.1f}" fill="{rail_c}" opacity="0.88"/>')

    # 4. Fabric panel (solar screen)
    out += (f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" '
            f'fill="{fabric_c}" opacity="0.72"/>')
    # 5. Horizontal weft lines (woven screen texture)
    n_lines = max(4, int(fh / 7))
    for i in range(1, n_lines + 1):
        ly = fy + i * fh / (n_lines + 1)
        out += (f'<line x1="{fx:.1f}" y1="{ly:.1f}" x2="{fx + fw:.1f}" y2="{ly:.1f}" '
                f'stroke="{stripe_c}" stroke-width="0.55" opacity="0.55"/>')

    # 6. Bottom weighted bar
    out += (f'<rect x="{fx:.1f}" y="{fy + fh:.1f}" width="{fw:.1f}" height="{bottom_h:.1f}" '
            f'fill="{bottom_c}" opacity="0.88"/>')

    # 7. "ZIP" label centred on fabric
    out += (f'<text x="{x + w / 2:.1f}" y="{fy + fh / 2:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="9px" font-weight="bold" '
            f'fill="#1e2d3a" opacity="0.65">ZIP</text>')
    return out


def _draw_facade_fill(fill_type, x, y, w, h):
    """Return SVG string for facade opening fill in flat elevation views."""
    out = ''
    ft = (fill_type or '').strip()
    if not ft or w < 2 or h < 2:
        return out
    if ft in ('FP-20', 'FP-PIR'):
        bg = '#4e6070' if ft == 'FP-PIR' else '#5d7080'
        line_c = '#3b4e5e' if ft == 'FP-PIR' else '#4a5e6e'
        out += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{bg}" opacity="0.80"/>'
        n = max(3, int(h / 18))
        for i in range(1, n + 1):
            ly = y + i * h / (n + 1)
            out += (f'<line x1="{x:.1f}" y1="{ly:.1f}" x2="{x + w:.1f}" y2="{ly:.1f}" '
                    f'stroke="{line_c}" stroke-width="0.9" opacity="0.55"/>')
    elif ft.startswith('FZ-44'):
        slat_c = '#4d6578'
        gap_r = 0.08 if '-100' in ft else (0.30 if '-70' in ft else 0.52)
        n_slats = max(4, int(h / 13))
        sh = h / n_slats
        sfh = max(1.0, sh * (1.0 - gap_r))
        for i in range(n_slats):
            sy = y + i * sh
            out += f'<rect x="{x:.1f}" y="{sy:.1f}" width="{w:.1f}" height="{sfh:.1f}" fill="{slat_c}" opacity="0.80"/>'
    return out


def _draw_s100_glazing_fill(pc, direction, color, glass, x, y, w, h):
    """Frameless S100: thin top + bottom rails (no side frame), thin vertical mullions
    between glass panels. Center-split for 3+3/4+4/6+6 (pc 6 with center, 8, 12)."""
    if w < 4 or h < 4:
        return ''
    pc = max(3, min(12, int(pc)))
    is_center = (direction == 'center') or pc in (8, 12) or (pc == 6 and direction == 'center')
    if color == 'ral9016':
        pC = '#d8d8d8'
    elif color == 'ral8028':
        pC = '#5c3d1e'
    elif color == 'ral7024':
        pC = '#3a4148'
    elif color == 'ral_special':
        pC = '#7a7a7a'
    else:  # ral9t08 default — текст. графит
        pC = '#2e3338'
    is_tinted = (glass == 'tinted_mass')
    if is_tinted:
        cG1, cG2 = '#7d8e96', '#5d7078'
    else:
        cG1, cG2 = '#d8e8f0', '#b8d4e6'
    # Profile heights from spec: top 50mm (3p) / 46mm (4/6p), bottom 20mm
    top_mm = 50 if pc == 3 else 46
    bot_mm = 20
    top_px = max(2.5, min(8, h * (top_mm / 3000.0) * 1.6 + 2.5))
    bot_px = max(1.8, min(5, h * (bot_mm / 3000.0) * 1.6 + 1.5))
    mid_px = max(0.6, min(1.6, w * 0.0035))
    center_px = max(1.2, min(3, w * 0.006))
    # Thin vertical side jambs (frameless still has L/R end profiles per spec photos)
    side_px = max(1.2, min(3.5, w * 0.005))
    out = []
    inner_x = x + side_px
    inner_y = y + top_px
    inner_w = w - 2 * side_px
    inner_h = h - top_px - bot_px
    if inner_w < 4 or inner_h < 4:
        return ''
    if is_center:
        cx = inner_x + inner_w / 2
        out.append(f'<rect x="{cx - center_px / 2:.1f}" y="{inner_y:.1f}" width="{center_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
    half_n = pc / 2 if is_center else pc
    if is_center:
        usable = (inner_w - center_px) / 2
        panel_w = (usable - (half_n - 1) * mid_px) / half_n
    else:
        panel_w = (inner_w - (pc - 1) * mid_px) / pc
    for i in range(pc):
        if is_center:
            section_idx = i % (pc // 2)
            section_off = (inner_w - center_px) / 2 + center_px if i >= pc // 2 else 0
        else:
            section_idx = i
            section_off = 0
        px = inner_x + section_off + section_idx * (panel_w + mid_px)
        if section_idx > 0:
            out.append(f'<rect x="{px - mid_px:.1f}" y="{inner_y:.1f}" width="{mid_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
        out.append(f'<rect x="{px:.1f}" y="{inner_y:.1f}" width="{panel_w:.1f}" height="{inner_h:.1f}" fill="{cG1}" opacity="0.92"/>')
        out.append(f'<rect x="{px + panel_w * 0.55:.1f}" y="{inner_y:.1f}" width="{panel_w * 0.45:.1f}" height="{inner_h:.1f}" fill="{cG2}" opacity="0.35"/>')
    # Top + bottom thin rails
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{top_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y + h - bot_px:.1f}" width="{w:.1f}" height="{bot_px:.1f}" fill="{pC}"/>')
    return ''.join(out)


def _w_color_hex(color):
    if color == 'ral9016':     return '#d8d8d8'
    if color == 'ral8028':     return '#5c3d1e'
    if color == 'ral7024':     return '#3a4148'
    if color == 'ral_special': return '#7a7a7a'
    return '#2e3338'  # ral9t08 default


def _draw_w_glazing_fill(series, sashes, color, glass, x, y, w, h):
    """W500/W600/W700 guillotine: top/middle/bottom horizontal rails,
    no vertical mullions, chain marker on top rail. 2 or 3 sashes."""
    if w < 4 or h < 4:
        return ''
    try:
        sashes = max(2, min(3, int(sashes)))
    except Exception:
        sashes = 2
    pC = _w_color_hex(color)
    is_multi = (glass == 'multifunctional')
    cG1 = '#a8c0d0' if is_multi else '#cce0f0'
    cG2 = '#7d97a8' if is_multi else '#a8c8e0'
    top_px = max(4, min(11, h * 0.06))
    bot_px = max(3, min(7, h * 0.035))
    mid_px = max(2, min(5, h * 0.022))
    side_px = max(2, min(7, w * 0.018))
    out = []
    # Glass background panels (split into N horizontal sashes)
    inner_x = x + side_px
    inner_y = y + top_px
    inner_w = w - 2 * side_px
    inner_h = h - top_px - bot_px
    if inner_w < 4 or inner_h < 4:
        return ''
    sash_h = (inner_h - (sashes - 1) * mid_px) / sashes
    for i in range(sashes):
        sy = inner_y + i * (sash_h + mid_px)
        out.append(f'<rect x="{inner_x:.1f}" y="{sy:.1f}" width="{inner_w:.1f}" height="{sash_h:.1f}" fill="{cG1}"/>')
        out.append(f'<rect x="{inner_x + inner_w * 0.55:.1f}" y="{sy:.1f}" width="{inner_w * 0.4:.1f}" height="{sash_h:.1f}" fill="{cG2}" opacity="0.35"/>')
        if i < sashes - 1:
            out.append(f'<rect x="{inner_x:.1f}" y="{sy + sash_h:.1f}" width="{inner_w:.1f}" height="{mid_px:.1f}" fill="{pC}"/>')
    # Side jambs
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x + w - side_px:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    # Top rail with chain marker
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{top_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y + h - bot_px:.1f}" width="{w:.1f}" height="{bot_px:.1f}" fill="{pC}"/>')
    # Chain marker (small lift indicator) on top rail
    cmx = x + w * 0.5
    cmy = y + top_px * 0.5
    out.append(f'<circle cx="{cmx:.1f}" cy="{cmy:.1f}" r="{min(3, top_px*0.35):.1f}" fill="#dfe7ef" stroke="#1a3a6e" stroke-width="0.6"/>')
    # Series label on bottom rail
    label_y = y + h - bot_px * 0.25
    out.append(f'<text x="{x + w*0.5:.1f}" y="{label_y:.1f}" text-anchor="middle" font-size="6" fill="#dfe7ef" font-family="Arial,sans-serif">{series}</text>')
    return ''.join(out)


def _draw_glazing_fill(spec, x, y, w, h):
    """Render a sliding/guillotine schematic into the elevation opening.
    spec formats:
      S500: 'pc:direction:color:glass'
      S100: 'S100:pc:direction:color:glass'
      W:    'W500|W600|W700:sashes:color:glass'
    """
    if not spec or w < 4 or h < 4:
        return ''
    try:
        parts = (spec or '').split(':')
        head = parts[0].upper() if parts else ''
        if head in ('W500', 'W600', 'W700'):
            sashes = int(parts[1]) if len(parts) >= 2 else 2
            color = parts[2] if len(parts) >= 3 else 'ral9t08'
            glass = parts[3] if len(parts) >= 4 else 'transparent'
            return _draw_w_glazing_fill(head, sashes, color, glass, x, y, w, h)
        series = 'S500'
        if head == 'S100':
            series = 'S100'
            parts = parts[1:]
        if parts and parts[0].upper() == 'S500':
            parts = parts[1:]
        if series == 'S100':
            pc = max(3, min(12, int(parts[0]))) if len(parts) >= 1 else 4
        else:
            pc = max(2, min(10, int(parts[0]))) if len(parts) >= 1 else 4
        direction = parts[1] if len(parts) >= 2 else 'right'
        color = parts[2] if len(parts) >= 3 else ('ral9t08' if series == 'S100' else 'ral7016')
        glass = parts[3] if len(parts) >= 4 else 'transparent'
    except Exception:
        return ''
    if series == 'S100':
        return _draw_s100_glazing_fill(pc, direction, color, glass, x, y, w, h)
    is_center = direction == 'center' or pc in (6, 8, 10)
    if color == 'ral9016':
        pC, pD = '#d0d0d0', '#909090'
    elif color == 'ral8028':
        pC, pD = '#5c3d1e', '#3a2410'
    elif color == 'custom':
        pC, pD = '#777', '#111'
    else:
        pC, pD = '#3a4048', '#111'
    is_tinted = (glass == 'tinted')
    is_bronze = is_tinted and color == 'ral8028'
    if is_bronze:
        cG1, cG2 = '#b8956a', '#9a7548'
    elif is_tinted:
        cG1, cG2 = '#8a9ea8', '#6a8088'
    else:
        cG1, cG2 = '#cce0f0', '#a8c8e0'
    top_px = max(3, min(10, h * 0.05))
    bot_px = max(2, min(6, h * 0.025))
    side_px = max(3, min(10, w * 0.025))
    mid_px = max(1.2, min(3, w * 0.005))
    center_px = max(2, min(6, w * 0.01))
    out = []
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{top_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y + h - bot_px:.1f}" width="{w:.1f}" height="{bot_px:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    out.append(f'<rect x="{x + w - side_px:.1f}" y="{y:.1f}" width="{side_px:.1f}" height="{h:.1f}" fill="{pC}"/>')
    inner_x = x + side_px
    inner_y = y + top_px
    inner_w = w - 2 * side_px
    inner_h = h - top_px - bot_px
    if inner_w < 4 or inner_h < 4:
        return ''.join(out)
    if is_center:
        cx = inner_x + inner_w / 2
        out.append(f'<rect x="{cx - center_px / 2:.1f}" y="{inner_y:.1f}" width="{center_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
    half_n = pc / 2 if is_center else pc
    if is_center:
        usable = (inner_w - center_px) / 2
        panel_w = (usable - (half_n - 1) * mid_px) / half_n
    else:
        panel_w = (inner_w - (pc - 1) * mid_px) / pc
    for i in range(pc):
        if is_center:
            section_idx = i % (pc // 2)
            section_off = (inner_w - center_px) / 2 + center_px if i >= pc // 2 else 0
        else:
            section_idx = i
            section_off = 0
        px = inner_x + section_off + section_idx * (panel_w + mid_px)
        if section_idx > 0:
            out.append(f'<rect x="{px - mid_px:.1f}" y="{inner_y:.1f}" width="{mid_px:.1f}" height="{inner_h:.1f}" fill="{pC}"/>')
        out.append(f'<rect x="{px:.1f}" y="{inner_y:.1f}" width="{panel_w:.1f}" height="{inner_h:.1f}" fill="{cG1}"/>')
        out.append(f'<rect x="{px + panel_w * 0.5:.1f}" y="{inner_y:.1f}" width="{panel_w * 0.5:.1f}" height="{inner_h:.1f}" fill="{cG2}" opacity="0.3"/>')
    rail_y = y + h - bot_px
    out.append(f'<rect x="{x:.1f}" y="{rail_y - 1:.1f}" width="{w:.1f}" height="2" fill="#b8c4cc"/>')
    return ''.join(out)

