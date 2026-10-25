"""Write a Scene as a native, editable PowerPoint slide (everything except the basemap tiles is a PowerPoint object)."""
from lxml import etree
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from . import theme as T

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def _rgb(hexstr):
    from matplotlib.colors import to_hex
    h = to_hex(hexstr).lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _alpha(color_parent, alpha):
    """Add <a:alpha> to the srgbClr inside a fill or line element."""
    if alpha is None or alpha >= 0.999:
        return
    for clr in color_parent._element.iter('{%s}srgbClr' % NS['a']):
        a = etree.SubElement(clr, '{%s}alpha' % NS['a'])
        a.set('val', str(int(alpha * 100000)))


def _fill(shape, color, alpha=1.0):
    if color is None:
        shape.fill.background()
        return
    shape.fill.solid(); shape.fill.fore_color.rgb = _rgb(color)
    if alpha < 0.999:
        sp = shape._element.spPr
        for clr in sp.find('{%s}solidFill' % NS['a']).iter('{%s}srgbClr' % NS['a']):
            etree.SubElement(clr, '{%s}alpha' % NS['a']).set('val', str(int(alpha * 100000)))


def _line(shape, color, w_pt, dash=None, alpha=1.0):
    if color is None:
        shape.line.fill.background()
        return
    shape.line.color.rgb = _rgb(color); shape.line.width = Pt(w_pt)
    if dash:
        shape.line.dash_style = {'--': MSO_LINE.DASH, ':': MSO_LINE.ROUND_DOT}.get(dash, MSO_LINE.DASH)
    if alpha < 0.999:
        ln = shape._element.spPr.find('{%s}ln' % NS['a'])
        for clr in ln.iter('{%s}srgbClr' % NS['a']):
            etree.SubElement(clr, '{%s}alpha' % NS['a']).set('val', str(int(alpha * 100000)))


def _measure(lines, size, bold, font):
    fp = FontProperties(family=font, weight='bold' if bold else 'normal')
    w = 0.0
    for ln in lines:
        if ln.strip():
            w = max(w, TextPath((0, 0), ln, size=size, prop=fp).get_extents().width)
    return w / 72.0  # inches


def _e(inches):
    return Emu(int(round(inches * 914400)))


def write(scene, path, notes=''):
    H = T.SLIDE_H
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(T.SLIDE_W), Inches(T.SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    groups = {}

    for it in scene.items:
        k = it['k']
        if k == 'image':
            p = slide.shapes.add_picture(it['path'], _e(it['x']), _e(H - it['y'] - it['h']), _e(it['w']), _e(it['h']))
            p.name = it.get('name') or 'Basemap'
        elif k == 'rect':
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if it['rounded'] else MSO_SHAPE.RECTANGLE,
                                         _e(it['x']), _e(H - it['y'] - it['h']), _e(it['w']), _e(it['h']))
            _fill(shp, it['fill'], it['alpha']); _line(shp, it['edge'], it['edge_w'], it['dash'])
            shp.shadow.inherit = False
            shp.name = it.get('name') or 'Rectangle'
        elif k == 'oval':
            holder = slide.shapes
            if it.get('group'):
                if it['group'] not in groups:
                    groups[it['group']] = slide.shapes.add_group_shape(); groups[it['group']].name = it['group']
                holder = groups[it['group']].shapes
            d = it['d']
            shp = holder.add_shape(MSO_SHAPE.OVAL, _e(it['cx'] - d / 2), _e(H - it['cy'] - d / 2), _e(d), _e(d))
            _fill(shp, it['fill'], it['alpha']); _line(shp, it['edge'], it['edge_w'])
            shp.shadow.inherit = False
            if it.get('name'):
                shp.name = it['name']
        elif k == 'poly':
            pts = [(_e(x), _e(H - y)) for x, y in it['pts']]
            fb = slide.shapes.build_freeform(pts[0][0], pts[0][1], scale=1.0)
            fb.add_line_segments(pts[1:], close=it['closed'])
            shp = fb.convert_to_shape()
            _fill(shp, it['fill'], it['fill_alpha']) if it['fill'] else shp.fill.background()
            _line(shp, it['color'], it['lw'], it['dash'], it['alpha'])
            shp.shadow.inherit = False
            shp.name = it.get('name') or 'Line'
        elif k == 'text':
            _text(slide, it, H)
        elif k == 'card':
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, _e(it['x']), _e(H - it['y_top']), _e(it['w']), _e(it['h']))
            _fill(shp, '#ffffff'); _line(shp, it['color'], 1.8)
            shp.shadow.inherit = False
            tf = shp.text_frame; tf.word_wrap = True
            tf.margin_left = tf.margin_right = Inches(0.1); tf.margin_top = tf.margin_bottom = Inches(0.05)
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            for i, line in enumerate(it['s'].split('\n')):
                para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                para.alignment = PP_ALIGN.LEFT
                r = para.add_run(); r.text = line
                r.font.name = scene.font; r.font.size = Pt(it['size']); r.font.bold = (i == 0)
                r.font.color.rgb = _rgb(it['color'] if i == 0 else '#1d2a35')
            shp.name = it.get('name') or 'Callout'
        elif k == 'chart':
            _chart(slide, it, H, scene.font)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    prs.save(str(path))
    return path


def _text(slide, it, H):
    lines = it['s'].split('\n')
    size, bold, font = it['size'], it['bold'], it.get('font') or None
    f = it.get('font_family') or slide_font(it)
    w = _measure(lines, size, bold, f) + 0.04
    h = len(lines) * size * 1.2 * it['spacing'] / 72.0
    pad = it['pad'] if it['fill'] else 0.0
    x = {'left': it['x'], 'center': it['x'] - w / 2, 'right': it['x'] - w}[it['ha']]
    ytop = {'top': H - it['y'], 'bottom': H - it['y'] - h, 'center': H - it['y'] - h / 2, 'center_baseline': H - it['y'] - h / 2,
            'baseline': H - it['y'] - h * .8}[it['va']]
    if it['fill']:
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, _e(x - pad - .03), _e(ytop - pad * .8), _e(w + 2 * pad + .06), _e(h + 1.6 * pad))
        _fill(shp, it['fill']); _line(shp, it['edge'], 1.0) if it['edge'] else shp.line.fill.background()
        shp.shadow.inherit = False
        tf = shp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        align = PP_ALIGN.CENTER
    else:
        shp = slide.shapes.add_textbox(_e(x), _e(ytop), _e(w), _e(h))
        tf = shp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.TOP
        align = {'left': PP_ALIGN.LEFT, 'center': PP_ALIGN.CENTER, 'right': PP_ALIGN.RIGHT}[it['ha']]
    tf.word_wrap = False
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.line_spacing = it['spacing']
        r = para.add_run(); r.text = line
        r.font.name = f; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = _rgb(it['color'])
    shp.name = it.get('name') or ('Chip' if it['fill'] else 'Text')


_FONT = {'name': 'Times New Roman'}


def slide_font(it):
    return _FONT['name']


def _chart(slide, it, H, font):
    C = it['spec']
    cd = CategoryChartData(); cd.categories = C['categories']
    for s in C['series']:
        cd.add_series(s['name'], s['values'])
    kind = {'bar': XL_CHART_TYPE.COLUMN_CLUSTERED, 'hbar': XL_CHART_TYPE.BAR_CLUSTERED, 'line': XL_CHART_TYPE.LINE_MARKERS}[C['type']]
    gf = slide.shapes.add_chart(kind, _e(it['x']), _e(H - it['y'] - it['h']), _e(it['w']), _e(it['h']), cd)
    gf.name = 'Chart'
    ch = gf.chart
    ch.font.name = font; ch.font.size = Pt(T.BODY_PT)
    ch.has_legend = len(C['series']) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP; ch.legend.include_in_layout = False
    for s, spec in zip(ch.plots[0].series, C['series']):
        s.format.fill.solid() if C['type'] != 'line' else None
        col = _rgb(spec.get('color', T.ACCENTS[0]))
        if C['type'] == 'line':
            s.format.line.color.rgb = col; s.format.line.width = Pt(2.6); s.smooth = False
        else:
            s.format.fill.fore_color.rgb = col
    if C.get('annotate', True):
        pl = ch.plots[0]; pl.has_data_labels = True
        pl.data_labels.font.size = Pt(T.BODY_PT); pl.data_labels.font.bold = True
        if C['type'] != 'line':
            pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    if C['type'] != 'line':
        ch.plots[0].gap_width = 60
    ch.value_axis.major_gridlines.format.line.color.rgb = _rgb('#d5dbe1')
    ch.value_axis.format.line.fill.background()
    if C.get('ylabel'):
        ch.value_axis.has_title = True; ch.value_axis.axis_title.text_frame.text = C['ylabel']
    if C.get('xlabel'):
        ch.category_axis.has_title = True; ch.category_axis.axis_title.text_frame.text = C['xlabel']
