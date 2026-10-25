"""Build one 16:9 analytic slide from a spec dict/JSON. Switch layouts with `layout=` (or --layout) without touching content.

Layouts
  map_side        one framed map (left, ~62%) + text register (right)
  two_maps_side   two framed maps (comparison) + narrower register
  annotated_map   one large map + numbered callout cards with leader lines + one-line takeaway

CLI:  python -m slidekit.build spec.json [--layout map_side|two_maps_side|annotated_map] [--theme paper|sans] [--out DIR]
"""
import argparse
import json
import textwrap
NL = chr(10)
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from . import theme as T
from .mapview import draw_map, merc
from .register import draw_register
from . import briefs

LAYOUTS = ('map_side', 'two_maps_side', 'annotated_map', 'map_chart')
M = T.MARGIN
TITLE_TOP = T.SLIDE_H - 0.32
CONTENT_TOP = T.SLIDE_H - 1.35
FOOT_H = 0.5


def _text(fig, x, y, s, **kw):
    return fig.text(x / T.SLIDE_W, y / T.SLIDE_H, s, **kw)


def _header(fig, spec, theme):
    t = _text(fig, M, TITLE_TOP, spec['title'], ha='left', va='top', fontsize=T.TITLE_PT, fontweight='bold',
              color=theme['title'], family=theme['font'])
    sub = spec.get('subtitle')
    if sub:
        _text(fig, M, TITLE_TOP - 0.62, sub, ha='left', va='top', fontsize=T.SUBTITLE_PT, color=theme['muted'], family=theme['font'])
    fig.canvas.draw()
    r = t.get_window_extent(fig.canvas.get_renderer())
    if r.width / fig.dpi > T.SLIDE_W - 2 * M:
        raise ValueError(f"title too long for one line ({r.width / fig.dpi:.1f} in): shorten it (title = the claim, <= ~60 chars)")


def _footer(fig, spec, theme):
    note = spec.get('source') or ''
    if note:
        _text(fig, M, 0.22, '\n'.join(textwrap.wrap(note, 150)), ha='left', va='bottom', fontsize=T.FOOT_PT, color=theme['muted'],
              family=theme['font'])


def _caption(fig, ax, text, theme):
    x, y, w, h = ax._slide_box
    _text(fig, x, y + h + 0.08 + 0.0, '', fontsize=1)  # placeholder to keep API simple
    if text:
        _text(fig, x, y + h + 0.1 + 0.62, text, ha='left', va='bottom', fontsize=T.CAPTION_PT, fontweight='bold', color=theme['text'],
              family=theme['font'])


def _title_above(fig, ax, text, theme):
    x, y, w, h = ax._slide_box
    if text:
        _text(fig, x, y + h + 0.07, text, ha='left', va='bottom', fontsize=T.CAPTION_PT + 1, fontweight='bold', color=theme['text'],
              family=theme['font'])


def layout_map_side(fig, spec, theme):
    top, bottom = CONTENT_TOP, M + FOOT_H
    min_reg = 4.8
    ax = draw_map(fig, (M, bottom, T.SLIDE_W - 2 * M - min_reg - 0.5, top - bottom), spec['maps'][0], theme)
    right = ax._slide_box[0] + ax._slide_box[2]
    reg_x = right + 0.55  # register hugs the map and takes all remaining width (no dead gap)
    draw_register(fig, (reg_x, bottom, T.SLIDE_W - M - reg_x, top - bottom), spec['register'], spec.get('status'), theme)
    return [ax]


def layout_two_maps(fig, spec, theme):
    if len(spec['maps']) < 2:
        raise ValueError('two_maps_side needs spec["maps"] with two entries')
    top, bottom = CONTENT_TOP - 0.38, M + FOOT_H
    min_reg, gap = 4.3, 0.75
    map_w = (T.SLIDE_W - 2 * M - min_reg - 0.5 - gap) / 2
    axes, x = [], M
    for i in (0, 1):
        ax = draw_map(fig, (x, bottom, map_w, top - bottom), spec['maps'][i], theme)
        _title_above(fig, ax, spec['maps'][i].get('caption'), theme)
        axes.append(ax)
        x = ax._slide_box[0] + ax._slide_box[2] + gap
    reg_x = x - gap + 0.55
    draw_register(fig, (reg_x, bottom, T.SLIDE_W - M - reg_x, CONTENT_TOP - bottom), spec['register'], spec.get('status'), theme)
    return axes


def layout_annotated(fig, spec, theme):
    """One large map; numbered callout cards with leader lines. Cards use the open space beside the map when there is
    >= 3.6 in of it, otherwise they sit inside the map frame (wide maps)."""
    top, bottom = CONTENT_TOP, M + FOOT_H
    ax = draw_map(fig, (M, bottom, T.SLIDE_W - 2 * M, top - bottom), spec['maps'][0], theme)
    bx, by, bw, bh = ax._slide_box
    callouts = spec.get('callouts') or _auto_callouts(spec)
    free_x = bx + bw + 0.55
    free_w = T.SLIDE_W - M - free_x
    side = free_w >= 3.6
    card_w = min(free_w, 6.0) if side else 3.1
    y_cursor = top - 0.05
    for i, c in enumerate(callouts):
        color = c.get('color', T.ACCENTS[i % len(T.ACCENTS)])
        chars = int(card_w * 72 / ((T.BODY_PT + 2) * 0.46))
        body = f"{c['id']}  {c['title'].upper()}" + NL + NL.join(textwrap.wrap(c['text'], chars))
        n_lines = body.count(NL) + 1
        tx, ty = merc(c['target'])[0]
        if side:
            kw = dict(xytext=(free_x / T.SLIDE_W, y_cursor / T.SLIDE_H), textcoords='figure fraction', ha='left', va='top')
            y_cursor -= n_lines * (T.BODY_PT + 2) * 1.4 / 72 + 0.6
        else:
            kw = dict(xytext=c.get('box', (0.02, 0.96 - i * 0.3)), textcoords='axes fraction', ha='left', va='top')
        ax.annotate(body, xy=(tx, ty), xycoords='data', fontsize=T.BODY_PT + (2 if side else 0), family=theme['font'], color=theme['text'],
                    bbox=dict(boxstyle='round,pad=0.55', fc='white', ec=color, lw=1.8),
                    arrowprops=dict(arrowstyle='-', color=color, lw=1.8, shrinkA=0, shrinkB=2, relpos=(0, .5)),
                    zorder=20, annotation_clip=False, linespacing=1.3, **kw)
    if spec.get('takeaway'):
        if side:
            wrapped = NL.join(textwrap.wrap(spec['takeaway'], int(card_w * 72 / ((T.HEAD_PT + 3) * 0.5))))
            _text(fig, free_x, bottom + 0.05, wrapped, ha='left', va='bottom', fontsize=T.HEAD_PT + 3, fontweight='bold',
                  color=theme['title'], family=theme['font'])
        else:
            _text(fig, M, M + FOOT_H - 0.05, spec['takeaway'], ha='left', va='bottom', fontsize=T.HEAD_PT + 3, fontweight='bold',
                  color=theme['title'], family=theme['font'])
    if spec.get('status'):  # right-aligned on the subtitle row, never on the title row
        _text(fig, T.SLIDE_W - M, TITLE_TOP - 0.62, spec['status'], ha='right', va='top', fontsize=T.BODY_PT, fontweight='bold',
              color='white', family=theme['font'], bbox=dict(boxstyle='round,pad=0.35', fc=theme['status'], ec='none'))
    return [ax]


def _auto_callouts(spec):
    """Fallback so any register-based spec can be shown as annotated_map: one card per register entry with a badge."""
    badges = {str(b['id']): b for b in spec['maps'][0].get('badges', [])}
    out = []
    for e in spec['register']:
        b = badges.get(str(e['id']))
        if not b:
            continue
        use = dict(e.get('fields', [])).get('Use') or (e['fields'][0][1] if e.get('fields') else '')
        out.append(dict(id=e['id'], title=e['title'], text=use, target=b['lonlat'], color=e.get('color', b.get('color'))))
    return out


def layout_map_chart(fig, spec, theme):
    """Map (left) + one chart (right) linking geography to quantitative evidence; takeaway below the chart.
    spec['chart'] = {type: bar|hbar|line, categories, series: [{name, values, color}], xlabel, ylabel, annotate}"""
    top, bottom = CONTENT_TOP, M + FOOT_H
    ax = draw_map(fig, (M, bottom, 5.6, top - bottom), spec['maps'][0], theme)
    right = ax._slide_box[0] + ax._slide_box[2]
    cx = right + 0.9
    cw = T.SLIDE_W - M - cx
    ch = (top - bottom) - (1.0 if spec.get('takeaway') else 0.3)
    cax = fig.add_axes([cx / T.SLIDE_W, (top - ch) / T.SLIDE_H, cw / T.SLIDE_W, (ch - 0.35) / T.SLIDE_H])
    C = spec['chart']
    cats = C['categories']
    series = C['series']
    n = len(series)
    for k, s in enumerate(series):
        col = s.get('color', T.ACCENTS[k % len(T.ACCENTS)])
        if C['type'] == 'line':
            cax.plot(cats, s['values'], color=col, lw=2.6, marker='o', ms=5, label=s['name'])
        elif C['type'] == 'hbar':
            h = .7 / n
            ys = np.arange(len(cats)) + (k - (n - 1) / 2) * h
            cax.barh(ys, s['values'], height=h, color=col, label=s['name'])
        else:
            w = .7 / n
            xs = np.arange(len(cats)) + (k - (n - 1) / 2) * w
            cax.bar(xs, s['values'], width=w, color=col, label=s['name'])
        if C.get('annotate', True) and C['type'] != 'line':
            for i, v in enumerate(s['values']):
                if C['type'] == 'hbar':
                    cax.annotate(f"{v:g}", (v, i + (k - (n - 1) / 2) * (.7 / n)), xytext=(4, 0), textcoords='offset points', va='center',
                                 fontsize=T.BODY_PT, fontweight='bold', family=theme['font'])
                else:
                    cax.annotate(f"{v:g}", (i + (k - (n - 1) / 2) * (.7 / n), v), xytext=(0, 3), textcoords='offset points', ha='center',
                                 fontsize=T.BODY_PT, fontweight='bold', family=theme['font'])
    if C['type'] == 'hbar':
        cax.set_yticks(range(len(cats))); cax.set_yticklabels(cats); cax.invert_yaxis()
    elif C['type'] == 'bar':
        cax.set_xticks(range(len(cats))); cax.set_xticklabels(cats)
    for sp in ('top', 'right'):
        cax.spines[sp].set_visible(False)
    cax.tick_params(labelsize=T.BODY_PT - 1)
    for lab in cax.get_xticklabels() + cax.get_yticklabels():
        lab.set_family(theme['font'])
    cax.set_xlabel(C.get('xlabel', ''), fontsize=T.BODY_PT, family=theme['font'])
    cax.set_ylabel(C.get('ylabel', ''), fontsize=T.BODY_PT, family=theme['font'])
    cax.grid(axis='x' if C['type'] == 'hbar' else 'y', color=theme['rule'], lw=.6)
    cax.set_axisbelow(True)
    if n > 1:
        cax.legend(frameon=False, prop=dict(family=theme['font'], size=T.BODY_PT), loc='upper right')
    if spec.get('takeaway'):
        _text(fig, cx, bottom + 0.05, NL.join(textwrap.wrap(spec['takeaway'], int(cw * 72 / ((T.HEAD_PT + 3) * 0.5)))),
              ha='left', va='bottom', fontsize=T.HEAD_PT + 3, fontweight='bold', color=theme['title'], family=theme['font'])
    if spec.get('status'):
        _text(fig, T.SLIDE_W - M, TITLE_TOP - 0.62, spec['status'], ha='right', va='top', fontsize=T.BODY_PT, fontweight='bold',
              color='white', family=theme['font'], bbox=dict(boxstyle='round,pad=0.35', fc=theme['status'], ec='none'))
    return [ax]


_DISPATCH = {'map_side': layout_map_side, 'two_maps_side': layout_two_maps, 'annotated_map': layout_annotated, 'map_chart': layout_map_chart}


def _apply_brief(spec):
    """Resolve the presentation brief into per-slide defaults (explicit spec keys always win) and print the QA report."""
    spec = json.loads(json.dumps(spec)) if False else dict(spec)
    r = briefs.resolve(spec.get('brief'))
    spec['_resolved'] = r
    maps = []
    for m in spec.get('maps', []):
        m = dict(m)
        m.setdefault('coords', r['coords'])
        m.setdefault('north_arrow', r['north_arrow'])
        m.setdefault('legend_detail', r['legend_detail'])
        maps.append(m)
    spec['maps'] = maps
    if spec.get('register'):
        schema = spec.get('schema', r['schema'])
        spec['register'] = briefs.apply_schema(spec['register'], schema, r['essential_only'], r['max_fields'])
    for line in briefs.qa(spec, r, spec.get('register')):
        print('[qa]', line)
    return spec


def build(spec, layout=None, theme='paper', out='.', formats=('png', 'pdf', 'pptx'), name=None):
    layout = layout or spec.get('layout', 'map_side')
    assert layout in LAYOUTS, f'layout must be one of {LAYOUTS}'
    th = T.THEMES[theme]
    spec = _apply_brief(spec)
    mpl.rcParams.update({'font.family': th['font'], 'font.size': T.BODY_PT, 'pdf.fonttype': 42, 'savefig.dpi': T.DPI})
    fig = plt.figure(figsize=(T.SLIDE_W, T.SLIDE_H), dpi=T.DPI, facecolor='white')
    _header(fig, spec, th)
    _DISPATCH[layout](fig, spec, th)
    _footer(fig, spec, th)
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    stem = f"{name or spec.get('name', 'slide')}_{layout}"
    paths = {}
    if 'png' in formats:
        paths['png'] = out / f'{stem}.png'; fig.savefig(paths['png'], dpi=T.DPI)
    if 'pdf' in formats:
        paths['pdf'] = out / f'{stem}.pdf'; fig.savefig(paths['pdf'])
    if 'pptx' in formats:
        from pptx import Presentation
        from pptx.util import Inches
        if 'png' not in paths:
            paths['png'] = out / f'{stem}.png'; fig.savefig(paths['png'], dpi=T.DPI)
        prs = Presentation(); prs.slide_width, prs.slide_height = Inches(T.SLIDE_W), Inches(T.SLIDE_H)
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(str(paths['png']), 0, 0, width=prs.slide_width, height=prs.slide_height)
        s.notes_slide.notes_text_frame.text = '\n'.join(filter(None, [spec['title'], spec.get('subtitle'), spec.get('takeaway'), spec.get('source')]))
        paths['pptx'] = out / f'{stem}.pptx'; prs.save(paths['pptx'])
    plt.close(fig)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('--layout', choices=LAYOUTS); ap.add_argument('--theme', default='paper', choices=list(T.THEMES))
    ap.add_argument('--out', default='.')
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8'))
    print(build(spec, a.layout, a.theme, a.out))


if __name__ == '__main__':
    main()
