"""Auto-extracted from Decolife flask_app/utils.py — verbatim copy."""
import math
from ._helpers import (DIM_COLOR, DIM_FONT, DIM_SMALL_FONT, DIM_OFFSET, DIM_TEXT_GAP,
    DIM_EXT_LEN, DIM_TARGET_PX, DIM_MARGIN_L, DIM_MARGIN_R, DIM_MARGIN_T, DIM_MARGIN_B,
    _scale_from_ref, _dim_defs, _dim_h, _dim_v,
    _draw_zip_fill, _draw_facade_fill, _draw_s100_glazing_fill,
    _w_color_hex, _draw_w_glazing_fill, _draw_glazing_fill)

def generate_top_view_svg(width, length, modules=1, is_pir=False, lamella_count=None, max_overhang=None, ref=None, extra_columns=0, xc_left=0, xc_right=0, xc_front=0, xc_back=0):
    inner_fill = '#eef3fa'
    beam_color = '#1a3a6e'
    beam_fill = '#9fb8d6'
    column_fill = '#1a3a6e'
    lamella_color = '#5d7da8'
    text_color = '#333'
    label_font = '10px'

    BEAM_WIDTH_M = 0.164
    CENTER_BEAM_WIDTH_M = 0.28
    COLUMN_M = 0.164

    if not ref:
        ref = max(width, length, 0.5)
    scale = _scale_from_ref(ref)

    rect_w = max(60.0, width * scale)
    rect_h = max(60.0, length * scale)
    svg_w = int(DIM_MARGIN_L + rect_w + DIM_MARGIN_R)
    svg_h = int(DIM_MARGIN_T + rect_h + DIM_MARGIN_B)
    area = round(width * length, 1)

    beam_px_x = max(2.5, BEAM_WIDTH_M * scale)
    beam_px_y = max(2.5, BEAM_WIDTH_M * scale)
    center_beam_px = max(3.5, CENTER_BEAM_WIDTH_M * scale)
    col_px = max(3.5, COLUMN_M * scale)

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    svg += _dim_defs('t')

    rx = DIM_MARGIN_L
    ry = DIM_MARGIN_T

    svg += (f'<rect x="{rx}" y="{ry}" width="{rect_w}" height="{rect_h}" '
            f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="1"/>')

    inner_x = rx + beam_px_x
    inner_y = ry + beam_px_y
    inner_w = rect_w - 2 * beam_px_x
    inner_h = rect_h - 2 * beam_px_y

    if is_pir:
        panel_count = max(1, modules)
        for i in range(1, panel_count):
            mx = rx + (rect_w / panel_count) * i
            svg += (f'<rect x="{mx - beam_px_x / 2}" y="{ry}" width="{beam_px_x}" height="{rect_h}" '
                    f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="0.8"/>')

        seg_w = (inner_w - (panel_count - 1) * beam_px_x) / panel_count
        for i in range(panel_count):
            sx = inner_x + i * (seg_w + beam_px_x)
            svg += (f'<rect x="{sx}" y="{inner_y}" width="{seg_w}" height="{inner_h}" '
                    f'fill="{inner_fill}" stroke="none"/>')

        cx = rx + rect_w / 2
        cy = ry + rect_h / 2
        svg += f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">PIR панели</text>'
        svg += f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">{panel_count} секц.</text>'
    else:
        mod_count = max(1, modules)

        for i in range(1, mod_count):
            mx = rx + (rect_w / mod_count) * i
            svg += (f'<rect x="{mx - center_beam_px / 2}" y="{ry}" width="{center_beam_px}" height="{rect_h}" '
                    f'fill="{beam_fill}" stroke="{beam_color}" stroke-width="0.8"/>')

        seg_w = (inner_w - (mod_count - 1) * center_beam_px) / mod_count
        for m in range(mod_count):
            sx = inner_x + m * (seg_w + center_beam_px)
            svg += (f'<rect x="{sx}" y="{inner_y}" width="{seg_w}" height="{inner_h}" '
                    f'fill="{inner_fill}" stroke="none"/>')

            lam_count = lamella_count or max(4, int(inner_h / 7))
            spacing = inner_h / (lam_count + 1)
            for k in range(1, lam_count + 1):
                ly = inner_y + spacing * k
                svg += (f'<line x1="{sx + 1}" y1="{ly}" x2="{sx + seg_w - 1}" y2="{ly}" '
                        f'stroke="{lamella_color}" stroke-width="0.5" opacity="0.55"/>')

        cx = rx + rect_w / 2
        cy = ry + rect_h / 2
        total_lam = lamella_count or max(4, int(inner_h / 7))
        svg += f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="{label_font}" fill="{text_color}">{total_lam} ламелей</text>'

    col_count_x = max(2, modules + 1)
    col_xs = []
    if col_count_x == 2:
        col_xs = [rx + col_px / 2, rx + rect_w - col_px / 2]
    else:
        col_xs.append(rx + col_px / 2)
        for i in range(1, modules):
            col_xs.append(rx + (rect_w / modules) * i)
        col_xs.append(rx + rect_w - col_px / 2)

    col_ys_base = [ry + col_px / 2, ry + rect_h - col_px / 2]

    needs_extra = (max_overhang is not None and length and length > max_overhang + 0.001)
    reinf_rows = max(int(extra_columns or 0), 1 if needs_extra else 0)

    xc_l = max(int(xc_left or 0), 0)
    xc_r = max(int(xc_right or 0), 0)
    xc_f = max(int(xc_front or 0), 0)
    xc_bk = max(int(xc_back or 0), 0)

    left_x = col_xs[0]
    right_x = col_xs[-1]

    def _extra_ys(n):
        return [ry + (rect_h / (n + 1)) * i for i in range(1, n + 1)]

    def _extra_xs(n):
        return [rx + (rect_w / (n + 1)) * i for i in range(1, n + 1)]

    for cxp in col_xs:
        is_left = abs(cxp - left_x) < 2
        is_right = abs(cxp - right_x) < 2
        n_side = max(reinf_rows, xc_l if is_left else (xc_r if is_right else 0))
        ys = col_ys_base + _extra_ys(n_side) if n_side > 0 else col_ys_base
        for cyp in ys:
            svg += (f'<rect x="{cxp - col_px / 2}" y="{cyp - col_px / 2}" '
                    f'width="{col_px}" height="{col_px}" '
                    f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    top_y = col_ys_base[0]
    bot_y = col_ys_base[1]
    for n_fb, y_pos in ((xc_f, top_y), (xc_bk, bot_y)):
        if n_fb > 0:
            for ex in _extra_xs(n_fb):
                svg += (f'<rect x="{ex - col_px / 2}" y="{y_pos - col_px / 2}" '
                        f'width="{col_px}" height="{col_px}" '
                        f'fill="{column_fill}" stroke="{column_fill}" stroke-width="0.5"/>')

    arrow_y = ry + rect_h + DIM_OFFSET
    svg += _dim_h(rx, rx + rect_w, arrow_y, f'{width:.2f} м', prefix='t', below=True)

    arrow_x = rx - DIM_OFFSET
    svg += _dim_v(arrow_x, ry, ry + rect_h, f'{length:.2f} м', prefix='t', side='left')

    svg += (f'<text x="{rx + rect_w / 2}" y="{ry - 14}" text-anchor="middle" '
            f'font-size="13px" font-weight="bold" fill="{text_color}">Вид сверху · S = {area} м²</text>')

    svg += f'<rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" fill="none" stroke="#bcc4d0" stroke-width="0.8"/>'
    svg += '</svg>'
    return svg
