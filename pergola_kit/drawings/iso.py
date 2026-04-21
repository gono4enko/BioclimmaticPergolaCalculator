"""Auto-extracted from Decolife flask_app/utils.py — verbatim copy."""
import math
from ._helpers import (DIM_COLOR, DIM_FONT, DIM_SMALL_FONT, DIM_OFFSET, DIM_TEXT_GAP,
    DIM_EXT_LEN, DIM_TARGET_PX, DIM_MARGIN_L, DIM_MARGIN_R, DIM_MARGIN_T, DIM_MARGIN_B,
    _scale_from_ref, _dim_defs, _dim_h, _dim_v,
    _draw_zip_fill, _draw_facade_fill, _draw_s100_glazing_fill,
    _w_color_hex, _draw_w_glazing_fill, _draw_glazing_fill)

def generate_isometric_svg(width, length, height=3.0, lamella_count=None, modules=1, lamella_open_deg=55, max_overhang=None, extra_columns=0, fill_front=None, fill_right=None, fill_left=None, fill_back=None, fills_front_per_bay=None, fills_back_per_bay=None, fills_left_per_bay=None, fills_right_per_bay=None):
    """3D isometric view of pergola with tilted/open lamellas.
    Camera looks from front-right-above. X = ширина (вправо-вниз),
    Z = длина (влево-вниз в глубину), Y = высота (вверх).
    """
    import math

    width = max(0.5, float(width))
    length = max(0.5, float(length))
    height = max(1.5, float(height))
    open_deg = min(80, max(0, float(lamella_open_deg)))
    open_rad = math.radians(open_deg)

    BEAM_H = 0.28
    COL_W = 0.164
    CENTER_BEAM_W = 0.28
    LAM_W = 0.25
    LAM_T = 0.04

    svg_w = 620
    svg_h = 460
    pad_x = 80
    pad_top = 40
    pad_bot = 80

    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))

    def project(p):
        x, y, z = p
        sx = (x - z) * cos30
        sy = (x + z) * sin30 - y
        return sx, sy

    test_pts = [
        (0, 0, 0), (width, 0, 0), (width, 0, length), (0, 0, length),
        (0, height, 0), (width, height, 0), (width, height, length), (0, height, length),
    ]
    proj = [project(p) for p in test_pts]
    xs = [p[0] for p in proj]; ys = [p[1] for p in proj]
    span_x = max(xs) - min(xs); span_y = max(ys) - min(ys)
    scale = min((svg_w - 2 * pad_x) / span_x, (svg_h - pad_top - pad_bot) / span_y)
    ox = pad_x - min(xs) * scale + ((svg_w - 2 * pad_x) - span_x * scale) / 2
    oy = pad_top - min(ys) * scale

    def s(p):
        sx, sy = project(p)
        return ox + sx * scale, oy + sy * scale

    def quad(pts, fill, stroke='#1a3a6e', sw=0.8):
        coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in pts))
        return f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'

    def line(p1, p2, stroke='#1a3a6e', sw=0.6, opacity=1.0):
        x1, y1 = s(p1); x2, y2 = s(p2)
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'

    col_dark = '#143055'
    col_med = '#2a4a7e'
    col_light = '#3d6396'
    beam_top = '#b8c8df'
    beam_front = '#7d9bc0'
    beam_side = '#5d7da8'
    lam_top = '#daeaf8'
    lam_front = '#7ab4d4'
    lam_edge = '#0d2550'
    ground = '#eef2f7'
    text_color = '#333'

    def _iso_fill_face(ft, pts_bot_left, pts_bot_right, pts_top_left, pts_top_right, n_h_lines=8):
        _out = ''
        if not ft or not ft.strip():
            return _out
        ft = ft.strip()
        if ft in ('FP-20', 'FP-PIR'):
            bg = '#455a6a' if ft == 'FP-PIR' else '#527080'
            line_c = '#1f2a35'
            edge_c = '#26323f'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], bg, edge_c, 1.2)
            n_v_lines = 10
            for _li in range(1, n_v_lines):
                _t = _li / n_v_lines
                def _lerp(a, b, __t=_t):
                    return (a[0]+__t*(b[0]-a[0]), a[1]+__t*(b[1]-a[1]), a[2]+__t*(b[2]-a[2]))
                _out += line(_lerp(pts_bot_left, pts_bot_right), _lerp(pts_top_left, pts_top_right), line_c, 0.6, 0.85)
        elif ft == 'S500':
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.2)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.0),
                          _lerpS(pts_bot_left, pts_bot_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.0)], '#dde8ee', frame_c, 0.4)
            n_panels = 4
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.9, 0.95)
            _out += line(pts_top_left, pts_top_right, frame_c, 1.4, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.4, 1.0)
        elif ft == 'S100':
            # Frameless: lighter, more transparent glass; thin top + bottom rails; thin mullions
            frame_c = '#2e3338'
            glass_c = '#cfe0ea'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 0.5)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            # Subtle slide-stack hint
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.55),
                          _lerpS(pts_bot_left, pts_bot_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 0.55)], '#e6f0f6', frame_c, 0.3)
            n_panels = 6
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.5, 0.7)
            # Heavier top + bottom rails (frameless = no side frame)
            _out += line(pts_top_left, pts_top_right, frame_c, 1.6, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.2, 1.0)
        elif ft.split(':')[0] in ('W500', 'W600', 'W700'):
            # Guillotine: glass panel + thick top/bottom rails + (sashes-1) horizontal mid-rails.
            _wparts = ft.split(':')
            _wseries = _wparts[0]
            try:
                _wsashes = max(2, min(3, int(_wparts[1])))
            except Exception:
                _wsashes = 2
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0' if _wseries == 'W500' else ('#aac7d8' if _wseries == 'W600' else '#9bbacd')
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.0)
            def _lerpW(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            # Draw (sashes-1) horizontal mid-rails evenly spaced between top and bottom
            for _ri in range(1, _wsashes):
                _t = _ri / _wsashes
                _ml = _lerpW(pts_bot_left,  pts_top_left,  _t)
                _mr = _lerpW(pts_bot_right, pts_top_right, _t)
                _out += line(_ml, _mr, frame_c, 1.4, 1.0)
            # Heavy top + bottom rails
            _out += line(pts_top_left, pts_top_right, frame_c, 1.8, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.6, 1.0)
        elif ft.startswith('FZ-44'):
            slat_c = '#415568'
            gap_r = 0.08 if '-100' in ft else (0.30 if '-70' in ft else 0.52)
            n_slats = 8
            for _si in range(n_slats):
                t0 = _si / n_slats
                t1 = t0 + (1.0 - gap_r) / n_slats
                def _lp(a, b, _t):
                    return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
                _out += quad([_lp(pts_bot_left, pts_top_left, t0),
                              _lp(pts_bot_right, pts_top_right, t0),
                              _lp(pts_bot_right, pts_top_right, t1),
                              _lp(pts_bot_left, pts_top_left, t1)], slat_c, slat_c, 0.3)
        elif ft == 'ZIP':
            def _lz(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            cas_t = 0.07
            bot_t = 0.04
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left],
                         '#c8d8e8', '#1a3a6e', 0.6)
            _cas_bl = _lz(pts_top_left,  pts_bot_left,  cas_t)
            _cas_br = _lz(pts_top_right, pts_bot_right, cas_t)
            _out += quad([_cas_bl, _cas_br, pts_top_right, pts_top_left], '#1e2d3a', '#1e2d3a', 0.3)
            _bot_tl = _lz(pts_bot_left,  pts_top_left,  bot_t)
            _bot_tr = _lz(pts_bot_right, pts_top_right, bot_t)
            _out += quad([pts_bot_left, pts_bot_right, _bot_tr, _bot_tl], '#1e2d3a', '#1e2d3a', 0.3)
            for _li in range(1, 10):
                _t = cas_t + _li * (1.0 - cas_t - bot_t) / 10
                _out += line(_lz(pts_top_left, pts_bot_left, _t), _lz(pts_top_right, pts_bot_right, _t),
                             '#8aa0b2', 0.7, 0.65)
        return _out

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'

    g00 = (-0.4, 0, -0.4); g10 = (width + 0.4, 0, -0.4)
    g11 = (width + 0.4, 0, length + 0.4); g01 = (-0.4, 0, length + 0.4)
    svg += quad([g00, g10, g11, g01], ground, '#cfd6e0', 0.5)

    mod_count = max(1, int(modules))
    if mod_count == 1:
        col_xs = [COL_W / 2, width - COL_W / 2]
    else:
        col_xs = [COL_W / 2]
        for i in range(1, mod_count):
            col_xs.append(width / mod_count * i)
        col_xs.append(width - COL_W / 2)
    col_zs = [COL_W / 2, length - COL_W / 2]
    has_mid_z = max_overhang is not None and length > float(max_overhang) + 0.001
    extra_n = max(int(extra_columns or 0), 0)
    mid_z_positions = []
    if extra_n > 0:
        for i in range(1, extra_n + 1):
            mid_z_positions.append(length / (extra_n + 1) * i)
    elif has_mid_z:
        mid_z_positions.append(length / 2)
    for mz in mid_z_positions:
        col_zs.insert(-1, mz)
    has_mid_z = bool(mid_z_positions)

    column_top = height - BEAM_H

    def _front_bay_bounds(_mi):
        _bx0 = col_xs[0] if _mi == 0 else width / mod_count * _mi + COL_W / 2
        _bx1 = col_xs[-1] if _mi == mod_count - 1 else width / mod_count * (_mi + 1) - COL_W / 2
        return _bx0, _bx1

    _sorted_zs = sorted(col_zs)
    _n_lr_bays = max(1, len(_sorted_zs) - 1)

    def _side_bay_bounds(_bi):
        z0 = _sorted_zs[_bi] + COL_W / 2
        z1 = _sorted_zs[_bi + 1] - COL_W / 2
        return z0, z1

    def _bay_specs(side, single, per_bay, n_bays):
        out = []
        for _bi in range(n_bays):
            v = None
            if per_bay is not None and _bi < len(per_bay):
                v = per_bay[_bi]
            elif single and str(single).strip():
                v = single
            out.append(v if (v and str(v).strip()) else None)
        return out

    _front_specs = _bay_specs('front', fill_front, fills_front_per_bay, mod_count)
    _back_specs  = _bay_specs('back',  fill_back,  fills_back_per_bay,  mod_count)
    _left_specs  = _bay_specs('left',  fill_left,  fills_left_per_bay,  _n_lr_bays)
    _right_specs = _bay_specs('right', fill_right, fills_right_per_bay, _n_lr_bays)

    fill_back_svg = ''
    for _mi in range(mod_count):
        _spec = _back_specs[_mi]
        if not _spec: continue
        _bx0, _bx1 = _front_bay_bounds(_mi)
        fill_back_svg += _iso_fill_face(_spec, (_bx0, 0, length), (_bx1, 0, length),
                                        (_bx0, column_top, length), (_bx1, column_top, length))

    fill_left_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _left_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_left_svg += _iso_fill_face(_spec, (0, 0, _z0), (0, 0, _z1),
                                        (0, column_top, _z0), (0, column_top, _z1))

    fill_right_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _right_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_right_svg += _iso_fill_face(_spec, (width, 0, _z0), (width, 0, _z1),
                                         (width, column_top, _z0), (width, column_top, _z1))

    fill_front_svg = ''
    any_other_fill = any(_back_specs) or any(_left_specs) or any(_right_specs)
    for _mi in range(mod_count):
        _fx0, _fx1 = _front_bay_bounds(_mi)
        _pbl = (_fx0, 0, 0); _pbr = (_fx1, 0, 0)
        _ptl = (_fx0, column_top, 0); _ptr = (_fx1, column_top, 0)
        _spec = _front_specs[_mi]
        if _spec:
            fill_front_svg += _iso_fill_face(_spec, _pbl, _pbr, _ptl, _ptr)
        elif any_other_fill:
            coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in [_pbl, _pbr, _ptr, _ptl]))
            fill_front_svg += f'<polygon points="{coords}" fill="#eef2f7" fill-opacity="0.78" stroke="#2a4a7e" stroke-width="1.0" stroke-dasharray="6,3" stroke-linejoin="round"/>'

    SW_SIL = 1.2

    def draw_column(cx, cz, y0, y1, sw=SW_SIL):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark, '#1a3a6e', sw)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light, '#1a3a6e', sw)
        return out

    back_cols = [(cx, col_zs[-1]) for cx in col_xs]
    mid_cols = []
    for mz in mid_z_positions:
        for cx in col_xs:
            mid_cols.append((cx, mz))
    front_cols = [(cx, col_zs[0]) for cx in col_xs]

    svg += fill_back_svg

    back_cols.sort(key=lambda c: -c[0])
    for cx, cz in back_cols:
        svg += draw_column(cx, cz, 0, height)

    by0 = column_top
    by1 = height

    def draw_beam(x0, x1, z0, z1, y0, y1, top_c, front_c, side_c, sw=SW_SIL):
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], front_c, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], side_c, '#1a3a6e', sw)
        out += quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], top_c, '#1a3a6e', sw)
        return out

    svg += fill_left_svg
    svg += fill_right_svg
    svg += fill_front_svg

    svg += draw_beam(0, width, length - COL_W, length, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, COL_W, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(width - COL_W, width, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, width, 0, COL_W, by0, by1, beam_top, beam_front, beam_side)

    if lamella_count and lamella_count > 0:
        lam_n = int(lamella_count)
        seg_count = mod_count
        lam_per_seg = max(1, lam_n)
        for s_idx in range(seg_count):
            x_left = (width / seg_count) * s_idx + (COL_W if s_idx == 0 else COL_W / 2)
            x_right = (width / seg_count) * (s_idx + 1) - (COL_W if s_idx == seg_count - 1 else COL_W / 2)
            if x_right - x_left < 0.1:
                continue
            z_first = COL_W + 0.05
            z_last = length - COL_W - 0.05
            z_span = z_last - z_first
            spacing = z_span / max(1, lam_per_seg)
            y_center = column_top + 0.06

            half_w = LAM_W / 2
            half_t = LAM_T / 2
            dy_w = math.sin(open_rad) * half_w
            dz_w = math.cos(open_rad) * half_w
            dy_t = math.cos(open_rad) * half_t
            dz_t = math.sin(open_rad) * half_t

            lam_list = []
            for k in range(lam_per_seg):
                cz = z_first + spacing * (k + 0.5)
                lam_list.append(cz)
            for cz in lam_list:
                A = (x_left,  y_center - dy_w - dy_t, cz - dz_w + dz_t)
                B = (x_right, y_center - dy_w - dy_t, cz - dz_w + dz_t)
                C = (x_right, y_center - dy_w + dy_t, cz - dz_w - dz_t)
                D = (x_left,  y_center - dy_w + dy_t, cz - dz_w - dz_t)
                E = (x_left,  y_center + dy_w + dy_t, cz + dz_w - dz_t)
                F = (x_right, y_center + dy_w + dy_t, cz + dz_w - dz_t)
                G = (x_right, y_center + dy_w - dy_t, cz + dz_w + dz_t)
                H = (x_left,  y_center + dy_w - dy_t, cz + dz_w + dz_t)

                svg += quad([D, C, F, E], lam_top, lam_edge, 1.0)
                svg += quad([B, C, F, G], lam_front, lam_edge, 1.0)
                svg += quad([A, B, G, H], '#5a90b8', lam_edge, 1.0)

    if mod_count >= 2:
        for i in range(1, mod_count):
            cx_mid = width / mod_count * i
            svg += draw_beam(cx_mid - CENTER_BEAM_W / 2, cx_mid + CENTER_BEAM_W / 2,
                             COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    if mid_cols:
        mid_cols.sort(key=lambda c: c[0])
        for cx, cz in mid_cols:
            svg += draw_column(cx, cz, 0, height)

    front_cols.sort(key=lambda c: c[0])
    for cx, cz in front_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += _dim_defs('i')

    def _iso_dim(p1, p2, nx, ny, label, off=28, text_off=14):
        d1x = p1[0] + nx * off
        d1y = p1[1] + ny * off
        d2x = p2[0] + nx * off
        d2y = p2[1] + ny * off
        ang = math.degrees(math.atan2(d2y - d1y, d2x - d1x))
        if ang > 90 or ang < -90:
            ang -= 180
            d1x, d2x = d2x, d1x
            d1y, d2y = d2y, d1y
        midx = (d1x + d2x) / 2
        midy = (d1y + d2y) / 2
        tnx, tny = nx, ny
        if (tnx * math.cos(math.radians(ang)) + tny * math.sin(math.radians(ang))) > 0:
            pass
        tx = midx + nx * text_off
        ty = midy + ny * text_off
        return (
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p1[0] + nx*off:.1f}" y2="{p1[1] + ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{p2[0]:.1f}" y1="{p2[1]:.1f}" x2="{p2[0] + nx*off:.1f}" y2="{p2[1] + ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{d1x:.1f}" y1="{d1y:.1f}" x2="{d2x:.1f}" y2="{d2y:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" '
            f'marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" '
            f'fill="{DIM_COLOR}" transform="rotate({ang:.1f},{tx:.1f},{ty:.1f})">{label}</text>'
        )

    p_bl_floor = s((0, 0, length))
    p_br_floor = s((width, 0, length))
    nx_w_back = -math.cos(math.radians(30))
    ny_w_back = math.sin(math.radians(30))
    svg += _iso_dim(p_bl_floor, p_br_floor, nx_w_back, ny_w_back, f'{width:.2f} м (Ш)')

    p_fr_floor = s((width, 0, 0))
    nx_l_right = math.cos(math.radians(30))
    ny_l_right = math.sin(math.radians(30))
    svg += _iso_dim(p_fr_floor, p_br_floor, nx_l_right, ny_l_right, f'{length:.2f} м (Д)')

    p_btr = s((width, 0, 0))
    p_ttr = s((width, height, 0))
    hd_x = max(p_btr[0], p_ttr[0]) + 32
    svg += (f'<line x1="{p_btr[0]:.1f}" y1="{p_btr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{p_ttr[0]:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_ttr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{hd_x:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" '
            f'marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
            f'<text x="{hd_x + 14:.1f}" y="{(p_btr[1]+p_ttr[1])/2:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" '
            f'fill="{DIM_COLOR}" transform="rotate(-90,{hd_x + 14:.1f},{(p_btr[1]+p_ttr[1])/2:.1f})">{height:.2f} м (В)</text>')

    label_y_top = 22
    svg += (f'<text x="{svg_w/2}" y="{label_y_top}" text-anchor="middle" '
            f'font-size="14px" font-weight="600" fill="#1a3a6e">Изометрия — ламели открыты {int(open_deg)}°</text>')

    info_y = svg_h - 28
    info = f'{width:.2f} (Ш) × {length:.2f} (Д) × {height:.2f} (В) м'
    if lamella_count:
        info += f', {int(lamella_count)} ламелей по {int(LAM_W*1000)} мм'
    svg += (f'<text x="{svg_w/2}" y="{info_y}" text-anchor="middle" '
            f'font-size="11px" fill="{text_color}">{info}</text>')

    svg += (f'<text x="{svg_w/2}" y="{svg_h - 12}" text-anchor="middle" '
            f'font-size="9px" fill="#888" font-style="italic">'
            f'Колонна {int(COL_W*1000)}×{int(COL_W*1000)} мм, лоток {int(BEAM_H*1000)} мм</text>')

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg

def generate_pir_iso_svg(width, length, height=3.0, modules=1, max_overhang=None, extra_columns=0, fill_front=None, fill_right=None, fill_left=None, fill_back=None, fills_front_per_bay=None, fills_back_per_bay=None, fills_left_per_bay=None, fills_right_per_bay=None):
    """Isometric view for B600 pergola with PIR sandwich-panel roof.
    Panel joints spaced proportionally to actual panel width (~0.9 m).
    """
    import math

    width = max(0.5, float(width))
    length = max(0.5, float(length))
    height = max(1.5, float(height))

    BEAM_H = 0.28
    COL_W = 0.164
    CENTER_BEAM_W = 0.28
    PANEL_W_NOM = 0.9

    svg_w = 620
    svg_h = 460
    pad_x = 80
    pad_top = 40
    pad_bot = 80

    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))

    def project(p):
        x, y, z = p
        return (x - z) * cos30, (x + z) * sin30 - y

    test_pts = [
        (0, 0, 0), (width, 0, 0), (width, 0, length), (0, 0, length),
        (0, height, 0), (width, height, 0), (width, height, length), (0, height, length),
    ]
    proj = [project(p) for p in test_pts]
    xs = [p[0] for p in proj]; ys = [p[1] for p in proj]
    span_x = max(xs) - min(xs); span_y = max(ys) - min(ys)
    scale = min((svg_w - 2 * pad_x) / span_x, (svg_h - pad_top - pad_bot) / span_y)
    ox = pad_x - min(xs) * scale + ((svg_w - 2 * pad_x) - span_x * scale) / 2
    oy = pad_top - min(ys) * scale

    def s(p):
        sx, sy = project(p)
        return ox + sx * scale, oy + sy * scale

    def quad(pts, fill, stroke='#1a3a6e', sw=0.8):
        coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in pts))
        return f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'

    def seg(p1, p2, stroke='#1a3a6e', sw=0.7):
        x1, y1 = s(p1); x2, y2 = s(p2)
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"/>'

    def line(p1, p2, stroke='#1a3a6e', sw=0.6, opacity=1.0):
        x1, y1 = s(p1); x2, y2 = s(p2)
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'

    col_dark = '#143055'; col_med = '#2a4a7e'; col_light = '#3d6396'
    beam_top = '#b8c8df'; beam_front = '#7d9bc0'; beam_side = '#5d7da8'
    pir_top = '#c8d8eb'; pir_front = '#8fafc8'; pir_joint = '#6a87a8'
    ground = '#eef2f7'

    def _iso_fill_face(ft, pts_bot_left, pts_bot_right, pts_top_left, pts_top_right, n_h_lines=8):
        _out = ''
        if not ft or not ft.strip():
            return _out
        ft = ft.strip()
        if ft in ('FP-20', 'FP-PIR'):
            bg = '#455a6a' if ft == 'FP-PIR' else '#527080'
            line_c = '#334455'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], bg, bg, 0.0)
            for _li in range(1, n_h_lines + 1):
                _t = _li / (n_h_lines + 1)
                def _lerp(a, b, __t=_t):
                    return (a[0]+__t*(b[0]-a[0]), a[1]+__t*(b[1]-a[1]), a[2]+__t*(b[2]-a[2]))
                _out += seg(_lerp(pts_bot_left, pts_top_left), _lerp(pts_bot_right, pts_top_right), line_c, 0.7)
        elif ft == 'S500':
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.2)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.0),
                          _lerpS(pts_bot_left, pts_bot_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.45),
                          _lerpS(pts_top_left, pts_top_right, 0.0)], '#dde8ee', frame_c, 0.4)
            n_panels = 4
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.9, 0.95)
            _out += line(pts_top_left, pts_top_right, frame_c, 1.4, 1.0)
            _out += line(pts_bot_left, pts_bot_right, frame_c, 1.4, 1.0)
        elif ft == 'S100':
            frame_c = '#2e3338'
            glass_c = '#cfe0ea'
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 0.5)
            def _lerpS(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            _out += quad([_lerpS(pts_bot_left, pts_bot_right, 0.55),
                          _lerpS(pts_bot_left, pts_bot_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 1.0),
                          _lerpS(pts_top_left, pts_top_right, 0.55)], '#e6f0f6', frame_c, 0.3)
            n_panels = 6
            for _li in range(1, n_panels):
                _t = _li / n_panels
                _out += line(_lerpS(pts_bot_left, pts_bot_right, _t), _lerpS(pts_top_left, pts_top_right, _t), frame_c, 0.5, 0.7)
            _out += seg(pts_top_left, pts_top_right, frame_c, 1.6)
            _out += seg(pts_bot_left, pts_bot_right, frame_c, 1.2)
        elif ft.split(':')[0] in ('W500', 'W600', 'W700'):
            _wparts = ft.split(':')
            _wseries = _wparts[0]
            try:
                _wsashes = max(2, min(3, int(_wparts[1])))
            except Exception:
                _wsashes = 2
            frame_c = '#1f2a35'
            glass_c = '#bcd4e0' if _wseries == 'W500' else ('#aac7d8' if _wseries == 'W600' else '#9bbacd')
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left], glass_c, frame_c, 1.0)
            def _lerpW(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            for _ri in range(1, _wsashes):
                _t = _ri / _wsashes
                _ml = _lerpW(pts_bot_left,  pts_top_left,  _t)
                _mr = _lerpW(pts_bot_right, pts_top_right, _t)
                _out += seg(_ml, _mr, frame_c, 1.4)
            _out += seg(pts_top_left, pts_top_right, frame_c, 1.8)
            _out += seg(pts_bot_left, pts_bot_right, frame_c, 1.6)
        elif ft.startswith('FZ-44'):
            slat_c = '#415568'
            gap_r = 0.08 if '-100' in ft else (0.30 if '-70' in ft else 0.52)
            n_slats = 8
            for _si in range(n_slats):
                t0 = _si / n_slats
                t1 = t0 + (1.0 - gap_r) / n_slats
                def _lp(a, b, _t):
                    return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
                _out += quad([_lp(pts_bot_left, pts_top_left, t0),
                              _lp(pts_bot_right, pts_top_right, t0),
                              _lp(pts_bot_right, pts_top_right, t1),
                              _lp(pts_bot_left, pts_top_left, t1)], slat_c, slat_c, 0.3)
        elif ft == 'ZIP':
            def _lz(a, b, _t):
                return (a[0]+_t*(b[0]-a[0]), a[1]+_t*(b[1]-a[1]), a[2]+_t*(b[2]-a[2]))
            cas_t = 0.07
            bot_t = 0.04
            _out += quad([pts_bot_left, pts_bot_right, pts_top_right, pts_top_left],
                         '#c8d8e8', '#1a3a6e', 0.6)
            _cas_bl = _lz(pts_top_left,  pts_bot_left,  cas_t)
            _cas_br = _lz(pts_top_right, pts_bot_right, cas_t)
            _out += quad([_cas_bl, _cas_br, pts_top_right, pts_top_left], '#1e2d3a', '#1e2d3a', 0.3)
            _bot_tl = _lz(pts_bot_left,  pts_top_left,  bot_t)
            _bot_tr = _lz(pts_bot_right, pts_top_right, bot_t)
            _out += quad([pts_bot_left, pts_bot_right, _bot_tr, _bot_tl], '#1e2d3a', '#1e2d3a', 0.3)
            for _li in range(1, 10):
                _t = cas_t + _li * (1.0 - cas_t - bot_t) / 10
                _out += seg(_lz(pts_top_left, pts_bot_left, _t), _lz(pts_top_right, pts_bot_right, _t),
                            '#8aa0b2', 0.7)
        return _out

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'

    g00 = (-0.4, 0, -0.4); g10 = (width + 0.4, 0, -0.4)
    g11 = (width + 0.4, 0, length + 0.4); g01 = (-0.4, 0, length + 0.4)
    svg += quad([g00, g10, g11, g01], ground, '#cfd6e0', 0.5)

    mod_count = max(1, int(modules))
    col_xs = [COL_W / 2]
    for i in range(1, mod_count):
        col_xs.append(width / mod_count * i)
    col_xs.append(width - COL_W / 2)
    col_zs = [COL_W / 2, length - COL_W / 2]
    has_mid_z = max_overhang is not None and length > float(max_overhang) + 0.001
    extra_n = max(int(extra_columns or 0), 0)
    mid_z_positions = []
    if extra_n > 0:
        for i in range(1, extra_n + 1):
            mid_z_positions.append(length / (extra_n + 1) * i)
    elif has_mid_z:
        mid_z_positions.append(length / 2)
    for mz in mid_z_positions:
        col_zs.insert(-1, mz)
    has_mid_z = bool(mid_z_positions)

    column_top = height - BEAM_H

    SW_SIL = 1.2

    def draw_column(cx, cz, y0, y1, sw=SW_SIL):
        x0 = cx - COL_W / 2; x1 = cx + COL_W / 2
        z0 = cz - COL_W / 2; z1 = cz + COL_W / 2
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)], col_med, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col_dark, '#1a3a6e', sw)
        out += quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], col_light, '#1a3a6e', sw)
        return out

    def draw_beam(x0, x1, z0, z1, y0, y1, tc, fc, sc, sw=SW_SIL):
        out = ''
        out += quad([(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], fc, '#1a3a6e', sw)
        out += quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], sc, '#1a3a6e', sw)
        out += quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], tc, '#1a3a6e', sw)
        return out

    by0 = column_top; by1 = height

    def _front_bay_bounds(_mi):
        _bx0 = col_xs[0] if _mi == 0 else width / mod_count * _mi + COL_W / 2
        _bx1 = col_xs[-1] if _mi == mod_count - 1 else width / mod_count * (_mi + 1) - COL_W / 2
        return _bx0, _bx1

    _sorted_zs = sorted(col_zs)
    _n_lr_bays = max(1, len(_sorted_zs) - 1)

    def _side_bay_bounds(_bi):
        z0 = _sorted_zs[_bi] + COL_W / 2
        z1 = _sorted_zs[_bi + 1] - COL_W / 2
        return z0, z1

    def _bay_specs(single, per_bay, n_bays):
        out = []
        for _bi in range(n_bays):
            v = None
            if per_bay is not None and _bi < len(per_bay):
                v = per_bay[_bi]
            elif single and str(single).strip():
                v = single
            out.append(v if (v and str(v).strip()) else None)
        return out

    _front_specs = _bay_specs(fill_front, fills_front_per_bay, mod_count)
    _back_specs  = _bay_specs(fill_back,  fills_back_per_bay,  mod_count)
    _left_specs  = _bay_specs(fill_left,  fills_left_per_bay,  _n_lr_bays)
    _right_specs = _bay_specs(fill_right, fills_right_per_bay, _n_lr_bays)

    fill_back_svg = ''
    for _mi in range(mod_count):
        _spec = _back_specs[_mi]
        if not _spec: continue
        _bx0, _bx1 = _front_bay_bounds(_mi)
        fill_back_svg += _iso_fill_face(_spec, (_bx0, 0, length), (_bx1, 0, length),
                                        (_bx0, column_top, length), (_bx1, column_top, length))
    fill_left_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _left_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_left_svg += _iso_fill_face(_spec, (0, 0, _z0), (0, 0, _z1),
                                        (0, column_top, _z0), (0, column_top, _z1))
    fill_right_svg = ''
    for _bi in range(_n_lr_bays):
        _spec = _right_specs[_bi]
        if not _spec: continue
        _z0, _z1 = _side_bay_bounds(_bi)
        fill_right_svg += _iso_fill_face(_spec, (width, 0, _z0), (width, 0, _z1),
                                         (width, column_top, _z0), (width, column_top, _z1))
    fill_front_svg = ''
    any_other_fill = any(_back_specs) or any(_left_specs) or any(_right_specs)
    for _mi in range(mod_count):
        _fx0, _fx1 = _front_bay_bounds(_mi)
        _pbl = (_fx0, 0, 0); _pbr = (_fx1, 0, 0)
        _ptl = (_fx0, column_top, 0); _ptr = (_fx1, column_top, 0)
        _spec = _front_specs[_mi]
        if _spec:
            fill_front_svg += _iso_fill_face(_spec, _pbl, _pbr, _ptl, _ptr)
        elif any_other_fill:
            coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (s(p) for p in [_pbl, _pbr, _ptr, _ptl]))
            fill_front_svg += f'<polygon points="{coords}" fill="#eef2f7" fill-opacity="0.78" stroke="#2a4a7e" stroke-width="1.0" stroke-dasharray="6,3" stroke-linejoin="round"/>'

    svg += fill_back_svg

    back_cols = [(cx, col_zs[-1]) for cx in col_xs]
    back_cols.sort(key=lambda c: -c[0])
    for cx, cz in back_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += fill_left_svg
    svg += fill_right_svg
    svg += fill_front_svg

    svg += draw_beam(0, width, length - COL_W, length, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, COL_W, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    inner_x0 = COL_W
    inner_x1 = width - COL_W
    z_near = COL_W
    z_far = length - COL_W
    z_span = z_far - z_near

    n_panels = max(1, round(z_span / PANEL_W_NOM))
    panel_depth = z_span / n_panels

    RIB_PITCH = 0.075
    pir_shadow = '#7a94b2'
    pir_highlight = '#ddeef8'

    for i in range(n_panels):
        pz0 = z_near + i * panel_depth
        pz1 = z_near + (i + 1) * panel_depth
        svg += quad([(inner_x0, height, pz0), (inner_x0, height, pz1),
                     (inner_x1, height, pz1), (inner_x1, height, pz0)], pir_top, pir_joint, 0.4)
        if i == 0:
            svg += quad([(inner_x0, column_top, pz0), (inner_x0, height, pz0),
                         (inner_x1, height, pz0), (inner_x1, column_top, pz0)], pir_front, pir_joint, 0.4)
        n_ribs = max(1, int(panel_depth / RIB_PITCH))
        actual_pitch = panel_depth / n_ribs
        for k in range(n_ribs + 1):
            rz = pz0 + k * actual_pitch
            if rz > pz1 + 1e-6:
                break
            rz = min(rz, pz1)
            svg += seg((inner_x0, height, rz), (inner_x1, height, rz), pir_shadow, 0.55)
            hlz = rz + actual_pitch * 0.35
            if hlz < pz1 - 1e-6:
                svg += seg((inner_x0, height, hlz), (inner_x1, height, hlz), pir_highlight, 0.5)

    for i in range(1, n_panels):
        jz = z_near + i * panel_depth
        svg += seg((inner_x0, height, jz), (inner_x1, height, jz), pir_joint, 1.2)

    if mod_count >= 2:
        for i in range(1, mod_count):
            cx_mid = width / mod_count * i
            svg += draw_beam(cx_mid - CENTER_BEAM_W / 2, cx_mid + CENTER_BEAM_W / 2,
                             COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)

    svg += draw_beam(width - COL_W, width, COL_W, length - COL_W, by0, by1, beam_top, beam_front, beam_side)
    svg += draw_beam(0, width, 0, COL_W, by0, by1, beam_top, beam_front, beam_side)

    if has_mid_z:
        mid_cols = [(cx, col_zs[1]) for cx in col_xs]
        mid_cols.sort(key=lambda c: c[0])
        for cx, cz in mid_cols:
            svg += draw_column(cx, cz, 0, height)

    front_cols = [(cx, col_zs[0]) for cx in col_xs]
    front_cols.sort(key=lambda c: c[0])
    for cx, cz in front_cols:
        svg += draw_column(cx, cz, 0, height)

    svg += _dim_defs('i')

    def _iso_dim(p1, p2, nx, ny, label, off=28, text_off=14):
        d1x = p1[0] + nx * off; d1y = p1[1] + ny * off
        d2x = p2[0] + nx * off; d2y = p2[1] + ny * off
        ang = math.degrees(math.atan2(d2y - d1y, d2x - d1x))
        if ang > 90 or ang < -90:
            ang -= 180
            d1x, d2x = d2x, d1x
            d1y, d2y = d2y, d1y
        midx = (d1x + d2x) / 2; midy = (d1y + d2y) / 2
        tx = midx + nx * text_off; ty = midy + ny * text_off
        return (
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p1[0]+nx*off:.1f}" y2="{p1[1]+ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{p2[0]:.1f}" y1="{p2[1]:.1f}" x2="{p2[0]+nx*off:.1f}" y2="{p2[1]+ny*off:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
            f'<line x1="{d1x:.1f}" y1="{d1y:.1f}" x2="{d2x:.1f}" y2="{d2y:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" fill="{DIM_COLOR}" transform="rotate({ang:.1f},{tx:.1f},{ty:.1f})">{label}</text>'
        )

    p_bl = s((0, 0, length)); p_br = s((width, 0, length))
    nx_w = -cos30; ny_w = sin30
    svg += _iso_dim(p_bl, p_br, nx_w, ny_w, f'{width:.2f} м (Ш)')

    p_fr = s((width, 0, 0))
    nx_l = cos30; ny_l = sin30
    svg += _iso_dim(p_fr, p_br, nx_l, ny_l, f'{length:.2f} м (Д)')

    p_btr = s((width, 0, 0)); p_ttr = s((width, height, 0))
    hd_x = max(p_btr[0], p_ttr[0]) + 32
    svg += (
        f'<line x1="{p_btr[0]:.1f}" y1="{p_btr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
        f'<line x1="{p_ttr[0]:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_ttr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="0.5" stroke-dasharray="3,2"/>'
        f'<line x1="{hd_x:.1f}" y1="{p_ttr[1]:.1f}" x2="{hd_x:.1f}" y2="{p_btr[1]:.1f}" stroke="{DIM_COLOR}" stroke-width="1.2" marker-start="url(#i-aht)" marker-end="url(#i-ah)"/>'
        f'<text x="{hd_x+14:.1f}" y="{(p_btr[1]+p_ttr[1])/2:.1f}" text-anchor="middle" font-size="12px" font-weight="bold" fill="{DIM_COLOR}" transform="rotate(-90,{hd_x+14:.1f},{(p_btr[1]+p_ttr[1])/2:.1f})">{height:.2f} м (В)</text>'
    )

    svg += (f'<text x="{svg_w/2}" y="22" text-anchor="middle" '
            f'font-size="14px" font-weight="600" fill="#1a3a6e">Изометрия — PIR панели</text>')
    panel_mm = int(round(panel_depth * 1000))
    _psuffix = 'и' if 2 <= n_panels <= 4 else ('ей' if n_panels >= 5 else 'ь')
    svg += (f'<text x="{svg_w/2}" y="{svg_h - 28}" text-anchor="middle" '
            f'font-size="11px" fill="#333">{width:.2f} (Ш) × {length:.2f} (Д) × {height:.2f} (В) м, '
            f'{n_panels} панел{_psuffix} ~{panel_mm} мм</text>')
    svg += (f'<text x="{svg_w/2}" y="{svg_h - 12}" text-anchor="middle" '
            f'font-size="9px" fill="#888" font-style="italic">'
            f'Колонна {int(COL_W*1000)}×{int(COL_W*1000)} мм, лоток {int(BEAM_H*1000)} мм</text>')

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg
