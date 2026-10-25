"""Text register: status chip + numbered entries, each with fixed-schema fields (Geometry / Source / Rule / Use / Not).

Auto-fits: tries BODY_PT, then smaller in 0.5 pt steps down to MIN_PT; raises if the text still does not fit,
because the fix is to cut words (one idea per slide), not to shrink type.
"""
import textwrap
from . import theme as T
from . import scene

NL = chr(10)
LABEL_W = 0.82  # minimum inches for the field-label column; widened to the longest label in the register


def _label_w(entries, fs):
    longest = max((len(l) for e in entries for l, _ in e.get('fields', [])), default=0)
    return max(LABEL_W, longest * fs * 0.56 / 72 + 0.12)


def _layout(entries, w, fs):
    """Return rows [(kind, y_in, payload...)] and total height in inches for font size fs."""
    lh = fs * 1.32 / 72
    chars = max(10, int((w - _label_w(entries, fs) - 0.45) * 72 / (fs * 0.43)))
    rows, y = [], 0.0
    for e in entries:
        rows.append(('head', y, e))
        y += (T.HEAD_PT * 1.5) / 72
        for label, value in e.get('fields', []):
            lines = textwrap.wrap(str(value), chars) or ['']
            rows.append(('field', y, label, lines))
            y += lh * len(lines) + 0.03
        y += 0.12
    return rows, y - 0.12, lh


def draw_register(fig, rect, entries, status, theme, accents=T.ACCENTS):
    """rect = (x, y, w, h) inches, bottom-left origin. Draws top-down inside the rect."""
    W, H = T.SLIDE_W, T.SLIDE_H
    x, y, w, h = rect
    ax = fig.add_axes([x / W, y / H, w / W, h / H])
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis('off')
    top = 0.0
    if status:
        ax.text(0, 0.0, status, ha='left', va='top', fontsize=T.BODY_PT, fontweight='bold', family=theme['font'],
                color='white', bbox=dict(boxstyle='round,pad=0.35', fc=theme['status'], ec='none'))
        top = 0.55
        if scene.CURRENT is not None:
            scene.CURRENT.text(x, y + h, status, ha='left', va='top', size=T.BODY_PT, bold=True, color='#ffffff', fill=theme['status'],
                               name='Status chip')
    fs = float(T.BODY_PT)
    while True:
        rows, total, lh = _layout(entries, w, fs)
        if total <= h - top or fs <= T.MIN_PT:
            break
        fs -= 0.5
    if total > h - top + 1e-6:
        raise ValueError(f'register needs {total:.2f} in but has {h - top:.2f} in at {fs} pt: cut words, do not shrink further')
    S = scene.CURRENT
    for kind, yy, *rest in rows:
        yy += top
        if kind == 'head':
            e = rest[0]
            c = e.get('color', accents[(int(str(e['id'])[0]) - 1) % len(accents)] if str(e['id'])[0].isdigit() else accents[0])
            ax.text(0.17, yy + 0.02, str(e['id']), ha='center', va='top', fontsize=T.BODY_PT, fontweight='bold', color='white',
                    family=theme['font'], bbox=dict(boxstyle='circle,pad=0.28', fc=c, ec='white', lw=1.4))
            if S is not None:
                d = T.BODY_PT * 1.85 / 72
                S.oval(x + 0.17, y + h - (yy + 0.02 + T.BODY_PT * 0.62 / 72), d, c, edge='#ffffff', edge_w=1.4, name=f"Badge {e['id']}")
                S.text(x + 0.17, y + h - (yy + 0.02 + T.BODY_PT * 0.62 / 72), str(e['id']), ha='center', va='center', size=T.BODY_PT,
                       bold=True, color='#ffffff', name=f"Badge label {e['id']}")
                S.text(x + 0.5, y + h - yy, e['title'].upper(), ha='left', va='top', size=T.HEAD_PT, bold=True, color=c, name=f"Heading {e['id']}")
            ax.text(0.5, yy, e['title'].upper(), ha='left', va='top', fontsize=T.HEAD_PT, fontweight='bold', color=c,
                    family=theme['font'])
        else:
            label, lines = rest
            if S is not None:
                S.text(x + 0.5, y + h - yy, label, ha='left', va='top', size=fs, bold=True, color=theme['muted'], name='Field label')
                S.text(x + 0.5 + _label_w(entries, fs), y + h - yy, NL.join(lines), ha='left', va='top', size=fs, color=theme['text'],
                       spacing=1.1, name='Field value')
            ax.text(0.5, yy, label, ha='left', va='top', fontsize=fs, fontweight='bold', color=theme['muted'], family=theme['font'])
            ax.text(0.5 + _label_w(entries, fs), yy, '\n'.join(lines), ha='left', va='top', fontsize=fs, color=theme['text'],
                    family=theme['font'], linespacing=1.32)
    return ax, fs
