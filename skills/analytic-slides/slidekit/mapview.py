"""One framed map: basemap + vector layers + numbered badges + ticks + scale bar + north arrow.

Layer spec (all coordinates lon/lat, WGS84):
  {'type': 'bbox',   'coords': [w, s, e, n], 'color', 'lw', 'ls'}
  {'type': 'line',   'coords': [[lon, lat], ...], 'color', 'lw', 'alpha', 'halo': True, 'label'}
  {'type': 'gate',   'coords': [[lon, lat], [lon, lat]], 'color', 'lw'}
  {'type': 'points', 'coords': [[lon, lat], ...], 'color', 's', 'alpha', 'label'}
  {'type': 'polygon','coords': [[lon, lat], ...], 'color', 'alpha', 'edge'}
"""
import numpy as np
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Polygon
from matplotlib.lines import Line2D
from pyproj import Transformer

from . import theme as T
from . import scene

_TO_MERC = Transformer.from_crs(4326, 3857, always_xy=True)
_TO_LL = Transformer.from_crs(3857, 4326, always_xy=True)


def merc(coords):
    a = np.asarray(coords, float).reshape(-1, 2)
    x, y = _TO_MERC.transform(a[:, 0], a[:, 1])
    return np.column_stack([x, y])


def fit_box(bbox, avail_w, avail_h):
    """Largest box with the bbox's (Web Mercator) aspect inside avail_w x avail_h (inches)."""
    (x0, y0), (x1, y1) = merc([bbox[0], bbox[1]])[0], merc([bbox[2], bbox[3]])[0]
    aspect = (x1 - x0) / (y1 - y0)
    w, h = avail_w, avail_w / aspect
    if h > avail_h:
        w, h = avail_h * aspect, avail_h
    return w, h


def _basemap(ax, name, alpha, theme):
    ax.set_facecolor(theme['water'])
    src = T.BASEMAPS.get(name)
    if not src:
        return False
    try:
        import contextily as ctx
        provider = ctx.providers
        for part in src.split('.'):
            provider = provider[part]
        ctx.add_basemap(ax, source=provider, crs='EPSG:3857', attribution=False, alpha=alpha, zorder=0)
        return True
    except Exception as exc:  # offline or provider change: fall back to the plain frame, say so
        print(f'[mapview] basemap {name!r} unavailable ({type(exc).__name__}); using plain frame')
        return False


def _nice_km(target_km):
    for v in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500):
        if v >= target_km:
            return v
    return 1000


def draw_map(fig, rect, mapspec, theme, accents=T.ACCENTS):
    """rect = (x, y, w, h) in inches from the bottom-left of the slide. Returns the axes."""
    W, H = T.SLIDE_W, T.SLIDE_H
    bw, bh = fit_box(mapspec['bbox'], rect[2], rect[3])
    x = rect[0] + (rect[2] - bw) / 2 if mapspec.get('center', False) else rect[0]
    y = rect[1] + rect[3] - bh  # top-align
    ax = fig.add_axes([x / W, y / H, bw / W, bh / H])
    (x0, y0), (x1, y1) = merc([mapspec['bbox'][0], mapspec['bbox'][1]])[0], merc([mapspec['bbox'][2], mapspec['bbox'][3]])[0]
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('auto')
    got = _basemap(ax, mapspec.get('basemap', 'esri_gray'), mapspec.get('basemap_alpha', 1.0), theme)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    if not got and mapspec.get('land'):
        ax.add_patch(Polygon(merc(mapspec['land']), closed=True, fc=theme['land'], ec=theme['frame'], lw=.6, zorder=1))

    handles = []
    for L in mapspec.get('layers', []):
        kind, c = L['type'], L.get('color', accents[0])
        pts = merc(L['coords'])
        if kind == 'bbox':
            w_, s_, e_, n_ = L['coords']
            r = merc([[w_, s_], [e_, n_]])
            ax.add_patch(Rectangle(r[0], r[1, 0] - r[0, 0], r[1, 1] - r[0, 1], fill=False, ec=c, lw=L.get('lw', 2.0),
                                   ls=L.get('ls', '--'), zorder=3))
        elif kind == 'line':
            ln, = ax.plot(pts[:, 0], pts[:, 1], color=c, lw=L.get('lw', 2.0), alpha=L.get('alpha', .9), zorder=4,
                          solid_capstyle='round',
                          path_effects=[pe.withStroke(linewidth=L.get('lw', 2.0) + 2.5, foreground='white', alpha=.8)] if L.get('halo', True) else None)
            handles.append((ln, L))
        elif kind == 'gate':
            ln, = ax.plot(pts[:, 0], pts[:, 1], color=c, lw=L.get('lw', 4.5), solid_capstyle='butt', zorder=6)
            handles.append((ln, L))
        elif kind == 'points':
            sc = ax.scatter(pts[:, 0], pts[:, 1], s=L.get('s', 3), color=c, alpha=L.get('alpha', .5), lw=0, zorder=2)
            handles.append((Line2D([], [], marker='o', ls='', color=c, ms=5, alpha=.8), L))
        elif kind == 'polygon':
            ax.add_patch(Polygon(pts, closed=True, fc=c, ec=L.get('edge', c), alpha=L.get('alpha', .25), lw=1.2, zorder=2))

    for b in mapspec.get('badges', []):
        px, py = merc(b['lonlat'])[0]
        ax.text(px, py, str(b['id']), ha='center', va='center', color='white', fontsize=T.CAPTION_PT, fontweight='bold',
                family=theme['font'], zorder=8,
                bbox=dict(boxstyle='circle,pad=0.28', fc=b.get('color', accents[0]), ec='white', lw=1.6))

    # frame, ticks in degrees, no axis titles (units are in the tick labels)
    for s in ax.spines.values():
        s.set_edgecolor(theme['frame']); s.set_linewidth(.9)
    lon_ticks = np.linspace(mapspec['bbox'][0], mapspec['bbox'][2], 4)
    lat_ticks = np.linspace(mapspec['bbox'][1], mapspec['bbox'][3], 5)
    if mapspec.get('coords', True):  # degree ticks: geometry review / specialists; omitted for general audiences
        ax.set_xticks(merc(np.column_stack([lon_ticks, np.full(4, mapspec['bbox'][1])]))[:, 0])
        ax.set_xticklabels([f'{v:.2f}°' for v in lon_ticks])
        ax.set_yticks(merc(np.column_stack([np.full(5, mapspec['bbox'][0]), lat_ticks]))[:, 1])
        ax.set_yticklabels([f'{v:.2f}°' for v in lat_ticks])
        ax.tick_params(labelsize=T.TICK_PT, length=2.5, color=theme['frame'], labelcolor=theme['muted'], pad=2)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_family(theme['font'])
    else:
        ax.set_xticks([]); ax.set_yticks([])

    # scale bar (true ground distance at the map's mid latitude)
    mid_lat = np.mean([mapspec['bbox'][1], mapspec['bbox'][3]])
    m_per_unit = np.cos(np.radians(mid_lat))
    km = _nice_km((x1 - x0) * m_per_unit / 1000 * .22)
    ln = km * 1000 / m_per_unit
    sx, sy = x0 + (x1 - x0) * .04, y0 + (y1 - y0) * .045
    ax.plot([sx, sx + ln], [sy, sy], color='#1d2a35', lw=2.6, solid_capstyle='butt', zorder=9)
    ax.text(sx + ln / 2, sy + (y1 - y0) * .012, f'{km} km', ha='center', va='bottom', fontsize=T.TICK_PT + 1,
            family=theme['font'], color='#1d2a35', zorder=9,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])
    if mapspec.get('north_arrow', False):
        ax.annotate('', xy=(.945, .93), xytext=(.945, .85), xycoords='axes fraction',
                    arrowprops=dict(arrowstyle='-|>', color='#1d2a35', lw=1.6), zorder=9)
        ax.text(.945, .835, 'N', transform=ax.transAxes, ha='center', va='top', fontsize=T.CAPTION_PT, fontweight='bold',
                family=theme['font'], color='#1d2a35', zorder=9)

    leg = None if mapspec.get('legend') is False else _legend(ax, handles, mapspec.get('legend_detail', 'full'), theme, mapspec.get('legend_loc', 'lower left'),
                  mapspec.get('legend_anchor', (0.02, 0.095)))
    if mapspec.get('inset'):
        _inset(fig, ax, mapspec, theme)
    ax._slide_box = (x, y, bw, bh)

    def xf(lonlat):
        X, Y = merc([lonlat])[0]
        return (x + (X - x0) / (x1 - x0) * bw, y + (Y - y0) / (y1 - y0) * bh)
    ax._xf = xf
    if scene.CURRENT is not None:
        _record(fig, scene.CURRENT, mapspec, theme, accents, (x, y, bw, bh), (x0, y0, x1, y1), xf, leg, km, ln)
    return ax


KIND_TITLES = {'observation': 'Observations', 'construct': 'Analytical constructs', 'official': 'Official features'}


def _legend(ax, handles, detail, theme, loc='lower left', anchor=(0.02, 0.095)):
    """Legend by layer kind. full: grouped headers (observation / analytical construct / official feature) with `label`.
    simple: only layers that define `simple_label`, no headers. Layers without a label never appear."""
    rows = []
    if detail == 'simple':
        rows = [(h, L['simple_label']) for h, L in handles if L.get('simple_label')]
    else:
        for kind in ('official', 'construct', 'observation'):
            grp = [(h, L['label']) for h, L in handles if L.get('label') and L.get('kind', 'construct') == kind]
            if grp:
                rows.append((Line2D([], [], ls='', marker=''), KIND_TITLES[kind]))
                rows.extend(grp)
    if not rows:
        return None
    leg = ax.legend([h for h, _ in rows], [t for _, t in rows], loc=loc, bbox_to_anchor=anchor, frameon=True,
                    prop=dict(family=theme['font'], size=T.TICK_PT + 1), facecolor='white', edgecolor=theme['rule'],
                    framealpha=.92, borderpad=.5, handlelength=1.6, labelspacing=.35)
    leg.set_zorder(9)
    for txt, (_, label) in zip(leg.get_texts(), rows):
        if label in KIND_TITLES.values():
            txt.set_fontweight('bold'); txt.set_color(theme['muted'])
    return leg


def _inset(fig, ax, mapspec, theme):
    """Orientation inset: wider extent with the main map's extent outlined. mapspec['inset'] = {'bbox': [w,s,e,n], 'size': inches}."""
    W, H = T.SLIDE_W, T.SLIDE_H
    spec = mapspec['inset']
    x, y, bw, bh = ax._slide_box
    iw, ih = fit_box(spec['bbox'], spec.get('size', 1.9), spec.get('size', 1.9))
    pad = 0.08
    ia = fig.add_axes([(x + pad) / W, (y + bh - ih - pad) / H, iw / W, ih / H], zorder=12)
    (x0, y0), (x1, y1) = merc([spec['bbox'][0], spec['bbox'][1]])[0], merc([spec['bbox'][2], spec['bbox'][3]])[0]
    ia.set_xlim(x0, x1); ia.set_ylim(y0, y1)
    _basemap(ia, spec.get('basemap', 'esri_gray'), 1.0, theme)
    ia.set_xlim(x0, x1); ia.set_ylim(y0, y1)
    w_, s_, e_, n_ = mapspec['bbox']
    r = merc([[w_, s_], [e_, n_]])
    ia.add_patch(Rectangle(r[0], r[1, 0] - r[0, 0], r[1, 1] - r[0, 1], fill=False, ec=T.ACCENTS[2], lw=1.8, zorder=5))
    ia.set_xticks([]); ia.set_yticks([])
    for s in ia.spines.values():
        s.set_edgecolor('white'); s.set_linewidth(2.2)


def _basemap_png(path, bw, bh, lims, mapspec, theme):
    import matplotlib.pyplot as plt
    f = plt.figure(figsize=(bw, bh), dpi=200)
    a = f.add_axes([0, 0, 1, 1]); a.set_axis_off()
    a.set_xlim(lims[0], lims[2]); a.set_ylim(lims[1], lims[3])
    _basemap(a, mapspec.get('basemap', 'esri_gray'), mapspec.get('basemap_alpha', 1.0), theme)
    a.set_xlim(lims[0], lims[2]); a.set_ylim(lims[1], lims[3])
    f.savefig(path, dpi=200)
    plt.close(f)


def _record(fig, S, mapspec, theme, accents, box, lims, xf, leg, km, ln):
    """Record the map as native objects: basemap picture + vector layers, badges, ticks, scale bar, legend."""
    import tempfile
    from pathlib import Path
    bx, by, bw, bh = box
    x0, y0, x1, y1 = lims
    tmp = Path(tempfile.mkdtemp(prefix='slidemap_')) / 'basemap.png'
    _basemap_png(tmp, bw, bh, lims, mapspec, theme)
    S.image(tmp, bx, by, bw, bh, name='Basemap (picture)')

    def clamp(p):
        return (min(max(p[0], bx), bx + bw), min(max(p[1], by), by + bh))
    inside = lambda p: bx <= p[0] <= bx + bw and by <= p[1] <= by + bh
    for L in mapspec.get('layers', []):
        kind, c = L['type'], L.get('color', accents[0])
        pts = [xf(p) for p in L['coords']] if kind != 'bbox' else None
        label = L.get('label') or kind
        if kind == 'bbox':
            w_, s_, e_, n_ = L['coords']
            a, b = clamp(xf([w_, s_])), clamp(xf([e_, n_]))
            S.rect(a[0], a[1], b[0] - a[0], b[1] - a[1], edge=c, edge_w=L.get('lw', 2.0), dash=L.get('ls', '--'), name='Extent outline')
        elif kind == 'line':
            P = [clamp(p) for p in pts]
            if L.get('halo', True):
                S.poly(P, '#ffffff', L.get('lw', 2.0) + 2.5, alpha=.8, name=f'{label} (halo)')
            S.poly(P, c, L.get('lw', 2.0), alpha=L.get('alpha', .9), name=label)
        elif kind == 'gate':
            S.poly([clamp(p) for p in pts], c, L.get('lw', 4.5), name=label)
        elif kind == 'points':
            d = max(L.get('s', 3) ** .5, 1.5) / 72
            for p in pts:
                if inside(p):
                    S.oval(p[0], p[1], d, c, alpha=L.get('alpha', .5), group=f'{label} (points)')
        elif kind == 'polygon':
            S.poly([clamp(p) for p in pts], L.get('edge', c), 1.2, closed=True, fill=c, fill_alpha=L.get('alpha', .25), name=label)
    for b in mapspec.get('badges', []):
        px, py = xf(b['lonlat'])
        d = max(T.CAPTION_PT * 2.0 / 72, len(str(b['id'])) * T.CAPTION_PT * .75 / 72)
        S.oval(px, py, d, b.get('color', accents[0]), edge='#ffffff', edge_w=1.6, name=f"Badge {b['id']}")
        S.text(px, py, str(b['id']), ha='center', va='center', size=T.CAPTION_PT, bold=True, color='#ffffff', name=f"Badge label {b['id']}")
    S.rect(bx, by, bw, bh, edge=theme['frame'], edge_w=.9, name='Map frame')
    if mapspec.get('coords', True):
        bb = mapspec['bbox']
        for v in np.linspace(bb[0], bb[2], 4):
            S.text(xf([v, bb[1]])[0], by - 0.05, f'{v:.2f}°', ha='center', va='top', size=T.TICK_PT, color=theme['muted'], name='Tick')
        for v in np.linspace(bb[1], bb[3], 5):
            S.text(bx - 0.05, xf([bb[0], v])[1], f'{v:.2f}°', ha='right', va='center', size=T.TICK_PT, color=theme['muted'], name='Tick')
    if mapspec.get('scale_bar', True):
        sx, sy = bx + bw * .04, by + bh * .045
        wl = ln / (x1 - x0) * bw
        S.line((sx, sy), (sx + wl, sy), '#1d2a35', 2.6, name='Scale bar')
        S.text(sx + wl / 2, sy + bh * .012, f'{km} km', ha='center', va='bottom', size=T.TICK_PT + 1, color='#1d2a35', name='Scale label')
    if mapspec.get('north_arrow', False):
        S.line((bx + bw * .945, by + bh * .85), (bx + bw * .945, by + bh * .93), '#1d2a35', 1.6, name='North arrow')
        S.text(bx + bw * .945, by + bh * .835, 'N', ha='center', va='top', size=T.CAPTION_PT, bold=True, color='#1d2a35', name='North label')
    if mapspec.get('inset'):
        print('[pptx] inset map is not exported as native objects (present in the PNG/PDF only)')
    if leg is not None:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        dpi = fig.dpi
        e = leg.get_window_extent(r)
        S.rect(e.x0 / dpi, e.y0 / dpi, e.width / dpi, e.height / dpi, edge=theme['rule'], edge_w=.8, fill='#ffffff', alpha=.92, name='Legend box')
        for t, h in zip(leg.get_texts(), leg.legend_handles):
            te = t.get_window_extent(r)
            header = t.get_text() in KIND_TITLES.values()
            S.text(te.x0 / dpi, (te.y0 + te.y1) / 2 / dpi, t.get_text(), ha='left', va='center', size=T.TICK_PT + 1, bold=header,
                   color=theme['muted'] if header else '#000000', name='Legend text')
            if header:
                continue
            he = h.get_window_extent(r)
            cy = (he.y0 + he.y1) / 2 / dpi
            if h.get_marker() not in ('None', None, ''):
                S.oval((he.x0 + he.x1) / 2 / dpi, cy, 0.07, h.get_color(), alpha=.8, name='Legend symbol')
            else:
                S.line((he.x0 / dpi, cy), (he.x1 / dpi, cy), h.get_color(), max(h.get_linewidth(), 2), name='Legend symbol')
