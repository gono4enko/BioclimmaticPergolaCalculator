"""Auto-extracted from Decolife flask_app/utils.py — verbatim copy."""
import math
from ._helpers import (DIM_COLOR, DIM_FONT, DIM_SMALL_FONT, DIM_OFFSET, DIM_TEXT_GAP,
    DIM_EXT_LEN, DIM_TARGET_PX, DIM_MARGIN_L, DIM_MARGIN_R, DIM_MARGIN_T, DIM_MARGIN_B,
    _scale_from_ref, _dim_defs, _dim_h, _dim_v,
    _draw_zip_fill, _draw_facade_fill, _draw_s100_glazing_fill,
    _w_color_hex, _draw_w_glazing_fill, _draw_glazing_fill)

def generate_zip_detail_svg(zip_type='ZIP100', w_m=2.0, h_m=2.7, fabric='Veozip (Screen Veosol)'):
    """Generate a labeled technical elevation sketch of a ZIP roller awning.

    Shows cassette housing, guide rails, fabric panel, bottom bar, and
    annotation callouts — suitable for embedding in the КП scheme section.
    """
    vw, vh = 620, 400
    dark  = '#1e2d3a'
    mid   = '#253545'
    fab_c = '#c8d8e8'
    str_c = '#8aa0b2'
    ann   = '#1a3a6e'

    cassette_mm = 100 if zip_type == 'ZIP100' else 130
    max_area    = '≈ 14 м²' if zip_type == 'ZIP100' else '≤ 25 м²'

    lbl_w   = 175
    rpad    = 60   # extra right margin to fit height dimension
    drw_x0  = lbl_w + 10
    drw_x1  = vw - rpad
    drw_y0  = 55
    drw_y1  = vh - 48
    drw_w   = drw_x1 - drw_x0
    drw_h   = drw_y1 - drw_y0

    h_mm    = h_m * 1000
    w_mm    = w_m * 1000
    cas_h   = max(8, min(22, cassette_mm / h_mm * drw_h))
    rail_w  = max(4, min(14, 50 / w_mm * drw_w))
    bot_h   = max(4, min(14, 40 / h_mm * drw_h))

    fy      = drw_y0 + cas_h
    fh      = max(10, drw_h - cas_h - bot_h)
    fx      = drw_x0 + rail_w
    fw      = max(10, drw_w - 2 * rail_w)

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" '
           f'width="{vw}" height="{vh}" font-family="Arial, sans-serif">')

    svg += (f'<rect width="{vw}" height="{vh}" fill="#f7f9fc" rx="8"/>')

    title_text = f'{zip_type} — Вертикальная ZIP-маркиза'
    svg += (f'<text x="{vw/2:.1f}" y="28" text-anchor="middle" font-size="14px" '
            f'font-weight="bold" fill="{ann}">{title_text}</text>')
    cas_size_label = '90×100' if cassette_mm == 100 else '100×130'
    svg += (f'<text x="{vw/2:.1f}" y="45" text-anchor="middle" font-size="11px" '
            f'fill="#555">Короб {cas_size_label} мм · max {max_area} · {w_m:.2f}×{h_m:.2f} м</text>')

    svg += (f'<rect x="{drw_x0}" y="{drw_y0}" width="{drw_w}" height="{cas_h:.1f}" '
            f'fill="{dark}" rx="2" opacity="0.93"/>')
    dr_r = max(4.0, cas_h * 0.28)
    svg += (f'<circle cx="{drw_x0 + drw_w/2:.1f}" cy="{drw_y0 + cas_h/2:.1f}" r="{dr_r:.1f}" '
            f'fill="none" stroke="#6a8fa8" stroke-width="1.2" opacity="0.6"/>')

    svg += (f'<rect x="{drw_x0:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bot_h:.1f}" fill="{mid}" opacity="0.90"/>')
    svg += (f'<rect x="{drw_x0 + drw_w - rail_w:.1f}" y="{fy:.1f}" width="{rail_w:.1f}" '
            f'height="{fh + bot_h:.1f}" fill="{mid}" opacity="0.90"/>')

    svg += (f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" '
            f'fill="{fab_c}" opacity="0.75"/>')
    n_lines = max(12, int(fh / 8))
    for i in range(1, n_lines + 1):
        ly = fy + i * fh / (n_lines + 1)
        svg += (f'<line x1="{fx:.1f}" y1="{ly:.1f}" x2="{fx + fw:.1f}" y2="{ly:.1f}" '
                f'stroke="{str_c}" stroke-width="0.8" opacity="0.65"/>')

    svg += (f'<rect x="{fx:.1f}" y="{fy + fh:.1f}" width="{fw:.1f}" height="{bot_h:.1f}" '
            f'fill="{dark}" opacity="0.90"/>')

    def ann_line(label1, label2, ty, target_x, target_y, anchor='end'):
        lx = lbl_w - 4
        svg_l = ''
        svg_l += (f'<text x="{lx}" y="{ty}" text-anchor="{anchor}" font-size="10.5px" '
                  f'fill="{ann}" font-weight="600">{label1}</text>')
        if label2:
            svg_l += (f'<text x="{lx}" y="{ty+14}" text-anchor="{anchor}" font-size="9.5px" '
                      f'fill="#555">{label2}</text>')
        arrow_start_x = lx + 2
        svg_l += (f'<line x1="{arrow_start_x}" y1="{ty - 4}" x2="{target_x}" y2="{target_y}" '
                  f'stroke="{ann}" stroke-width="0.9" stroke-dasharray="3,2"/>')
        svg_l += (f'<circle cx="{target_x}" cy="{target_y}" r="2.5" fill="{ann}"/>')
        return svg_l

    cas_y_mid = drw_y0 + cas_h / 2
    rail_mid_y = fy + fh * 0.38
    fab_mid_y  = fy + fh * 0.55
    bot_mid_y  = fy + fh + bot_h / 2

    svg += ann_line('Кассета (короб)', f'{cas_size_label} мм · Ø{78 if cassette_mm==130 else 55} мм вал',
                    int(cas_y_mid), drw_x0 + drw_w * 0.4, cas_y_mid)
    svg += ann_line('Боковые направляющие', 'ZIP-канал (zip-замок)', int(rail_mid_y), drw_x0 + rail_w / 2, rail_mid_y)
    svg += ann_line('Полотно', fabric, int(fab_mid_y), fx + fw * 0.35, fab_mid_y)
    svg += ann_line('Нижняя планка', '(утяжелитель)', int(bot_mid_y), fx + fw * 0.3, bot_mid_y)

    hline_x = drw_x1 + 16
    svg += (f'<line x1="{hline_x}" y1="{drw_y0}" x2="{hline_x + 6}" y2="{drw_y0}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{hline_x}" y1="{drw_y1}" x2="{hline_x + 6}" y2="{drw_y1}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{hline_x + 3}" y1="{drw_y0}" x2="{hline_x + 3}" y2="{drw_y1}" '
            f'stroke="{ann}" stroke-width="0.9" marker-start="url(#dah)" marker-end="url(#dah2)"/>')
    svg += (f'<defs><marker id="dah" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">'
            f'<path d="M6,0 L0,3 L6,6" stroke="{ann}" stroke-width="0.8" fill="none"/></marker>'
            f'<marker id="dah2" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse">'
            f'<path d="M6,0 L0,3 L6,6" stroke="{ann}" stroke-width="0.8" fill="none"/></marker>'
            f'</defs>')
    svg += (f'<text x="{hline_x + 14}" y="{(drw_y0 + drw_y1)/2:.1f}" text-anchor="middle" '
            f'font-size="10px" fill="{ann}" font-weight="600" '
            f'transform="rotate(-90,{hline_x + 14},{(drw_y0 + drw_y1)/2:.1f})">{h_m:.2f} м</text>')

    wline_y = drw_y1 + 22
    svg += (f'<line x1="{drw_x0}" y1="{wline_y}" x2="{drw_x0}" y2="{wline_y + 5}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{drw_x1}" y1="{wline_y}" x2="{drw_x1}" y2="{wline_y + 5}" '
            f'stroke="{ann}" stroke-width="1"/>')
    svg += (f'<line x1="{drw_x0}" y1="{wline_y + 3}" x2="{drw_x1}" y2="{wline_y + 3}" '
            f'stroke="{ann}" stroke-width="0.9" marker-start="url(#dah)" marker-end="url(#dah2)"/>')
    svg += (f'<text x="{(drw_x0 + drw_x1)/2:.1f}" y="{wline_y + 17}" text-anchor="middle" '
            f'font-size="10px" fill="{ann}" font-weight="600">{w_m:.2f} м</text>')

    zip_mech_y = fy + fh * 0.18
    zip_mech_x = fx - 1
    svg += (f'<rect x="{zip_mech_x - 3:.1f}" y="{zip_mech_y - 5:.1f}" width="5" height="10" '
            f'fill="#a0b8c8" rx="1" opacity="0.75"/>')

    svg += '</svg>'
    return svg
