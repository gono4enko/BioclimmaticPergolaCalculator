"""Auto-extracted from Decolife flask_app/utils.py — verbatim copy."""
import math
from ._helpers import (DIM_COLOR, DIM_FONT, DIM_SMALL_FONT, DIM_OFFSET, DIM_TEXT_GAP,
    DIM_EXT_LEN, DIM_TARGET_PX, DIM_MARGIN_L, DIM_MARGIN_R, DIM_MARGIN_T, DIM_MARGIN_B,
    _scale_from_ref, _dim_defs, _dim_h, _dim_v,
    _draw_zip_fill, _draw_facade_fill, _draw_s100_glazing_fill,
    _w_color_hex, _draw_w_glazing_fill, _draw_glazing_fill)

def generate_front_view_svg(width, height=3.0, modules=1, max_overhang=None, ref=None, title='Вид спереди', extra_columns=0, col_mm=164, beam_h_mm=280, fill_type=None, fills_per_bay=None, glazings_per_bay=None, zips_per_bay=None):
    """Front/side elevation. width = horizontal dimension (m), height in m.
    Uses shared scale (DIM_TARGET_PX/ref) so views align with top view.
    """
    COLUMN_W_M = max(0.05, float(col_mm or 164) / 1000)
    BEAM_H_M = max(0.10, float(beam_h_mm or 280) / 1000)
    PAD_OVERHANG_M = 0.082
    SLAB_H_M = 0.05

    width = max(0.5, float(width))
    height = max(1.5, float(height))
    if height < BEAM_H_M + 0.5:
        height = BEAM_H_M + 0.5

    total_w_m = width + 2 * PAD_OVERHANG_M
    total_h_m = height + SLAB_H_M

    if not ref:
        ref = max(width, height, 0.5)
    scale = _scale_from_ref(ref)

    real_w_px = max(60.0, total_w_m * scale)
    real_h_px = max(60.0, total_h_m * scale)

    svg_w = int(DIM_MARGIN_L + real_w_px + DIM_MARGIN_R)
    svg_h = int(DIM_MARGIN_T + real_h_px + DIM_MARGIN_B)

    ox = DIM_MARGIN_L
    oy = DIM_MARGIN_T

    beam_color = '#1a3a6e'
    beam_fill = '#9fb8d6'
    column_fill = '#1a3a6e'
    slab_stroke = '#666'
    text_color = '#333'
    small_font = '10px'

    pad_px = PAD_OVERHANG_M * scale
    col_w_px = max(2.5, COLUMN_W_M * scale)
    beam_h_px = max(3.0, BEAM_H_M * scale)
    slab_h_px = max(2.5, SLAB_H_M * scale)

    pergola_top = oy
    pergola_bottom = oy + height * scale
    slab_top = pergola_bottom
    slab_bottom = slab_top + slab_h_px

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += _dim_defs('f')

    col_left_x = ox + pad_px
    col_right_x = ox + real_w_px - pad_px - col_w_px

    col_xs = [col_left_x, col_right_x]
    inner_span_m = width - COLUMN_W_M
    needs_extra = (max_overhang is not None and inner_span_m > max_overhang + 0.001)
    mod_count = max(1, int(modules))
    extra_col_xs = []
    if mod_count > 1:
        for i in range(1, mod_count):
            cxp = ox + pad_px + (width * scale / mod_count) * i - col_w_px / 2
            col_xs.append(cxp)
    elif needs_extra:
        cxp = ox + real_w_px / 2 - col_w_px / 2
        col_xs.append(cxp)
        extra_col_xs.append(cxp)
    extra_n = max(int(extra_columns or 0), 0)
    if extra_n > 0:
        for i in range(1, extra_n + 1):
            cxp = ox + pad_px + (width * scale / (extra_n + 1)) * i - col_w_px / 2
            col_xs.append(cxp)
            extra_col_xs.append(cxp)

    col_top_y = pergola_top
    col_h_px = pergola_bottom - pergola_top

    for cxp in col_xs:
        svg += (f'<rect x="{cxp}" y="{col_top_y}" width="{col_w_px}" height="{col_h_px}" '
                f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    beam_x = col_left_x
    beam_w = (col_right_x + col_w_px) - col_left_x
    svg += (f'<rect x="{beam_x}" y="{pergola_top}" width="{beam_w}" height="{beam_h_px}" '
            f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="1"/>')

    svg += (f'<rect x="{ox}" y="{slab_top}" width="{real_w_px}" height="{slab_h_px}" '
            f'fill="url(#hatch)" stroke="{slab_stroke}" stroke-width="0.8"/>')

    svg += (f'<text x="{svg_w/2}" y="{oy - 14}" text-anchor="middle" '
            f'font-size="13px" font-weight="bold" fill="{text_color}">{title}</text>')

    h_dim_x = ox + real_w_px + DIM_OFFSET
    svg += _dim_v(h_dim_x, pergola_top, pergola_bottom, f'{height:.2f} м', prefix='f', side='right')

    w_dim_y = slab_bottom + DIM_OFFSET
    svg += _dim_h(ox, ox + real_w_px, w_dim_y, f'{width:.2f} м', prefix='f', below=True)

    beam_h_label = int(round(float(beam_h_mm or 280)))
    svg += (f'<text x="{col_right_x + col_w_px + 4}" y="{pergola_top + beam_h_px/2 + 3}" '
            f'text-anchor="start" font-size="{small_font}" fill="{DIM_COLOR}">{beam_h_label}</text>')

    _ldr_attach_x = col_left_x
    _ldr_attach_y = col_top_y + beam_h_px + (col_h_px - beam_h_px) * 0.38
    _ldr_elbow_x = col_left_x - 10
    _ldr_elbow_y = _ldr_attach_y - 18
    _ldr_shelf_end_x = max(4.0, _ldr_elbow_x - 52)
    svg += (f'<defs><marker id="f-dot" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5">'
            f'<circle cx="2.5" cy="2.5" r="2" fill="{DIM_COLOR}"/></marker></defs>')
    svg += (f'<polyline points="{_ldr_attach_x:.1f},{_ldr_attach_y:.1f} '
            f'{_ldr_elbow_x:.1f},{_ldr_elbow_y:.1f} '
            f'{_ldr_shelf_end_x:.1f},{_ldr_elbow_y:.1f}" '
            f'fill="none" stroke="{DIM_COLOR}" stroke-width="0.8" '
            f'marker-start="url(#f-dot)"/>')
    col_mm_label = int(col_mm) if col_mm else 164
    svg += (f'<text x="{_ldr_elbow_x:.1f}" y="{_ldr_elbow_y - 3:.1f}" '
            f'text-anchor="end" font-size="{small_font}" fill="{DIM_COLOR}">□ {col_mm_label}×{col_mm_label} мм</text>')

    if fills_per_bay or (fill_type and fill_type.strip()) or glazings_per_bay or zips_per_bay:
        fill_y0 = pergola_top + beam_h_px
        fill_h_px = pergola_bottom - fill_y0
        sorted_xs = sorted(col_xs)
        for _bi in range(len(sorted_xs) - 1):
            _fx0 = sorted_xs[_bi] + col_w_px
            _fx1 = sorted_xs[_bi + 1]
            if _fx1 - _fx0 > 2:
                has_zip = bool(zips_per_bay and _bi < len(zips_per_bay) and zips_per_bay[_bi])
                glz_spec = None
                if glazings_per_bay and _bi < len(glazings_per_bay):
                    glz_spec = glazings_per_bay[_bi]
                if glz_spec:
                    svg += _draw_glazing_fill(glz_spec, _fx0, fill_y0, _fx1 - _fx0, fill_h_px)
                else:
                    if fills_per_bay and _bi < len(fills_per_bay) and fills_per_bay[_bi]:
                        bay_fill = fills_per_bay[_bi]
                    else:
                        bay_fill = fill_type
                    svg += _draw_facade_fill(bay_fill, _fx0, fill_y0, _fx1 - _fx0, fill_h_px)
                if has_zip:
                    svg += _draw_zip_fill(_fx0, fill_y0, _fx1 - _fx0, fill_h_px)

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg

def generate_side_view_svg(length, height=3.0, modules=1, max_overhang=None, ref=None,
                          title="Вид сбоку", extra_columns=0, col_mm=164, beam_h_mm=280,
                          fill_type=None, fills_per_bay=None,
                          glazings_per_bay=None, zips_per_bay=None):
    """Side elevation = front-view rendering with width=length and 'Вид сбоку' title."""
    return generate_front_view_svg(length, height=height, modules=modules,
        max_overhang=max_overhang, ref=ref or length, title=title,
        extra_columns=extra_columns, col_mm=col_mm, beam_h_mm=beam_h_mm,
        fill_type=fill_type, fills_per_bay=fills_per_bay,
        glazings_per_bay=glazings_per_bay, zips_per_bay=zips_per_bay)
