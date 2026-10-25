"""Scene recorder: the layouts draw with matplotlib AND record every element here (slide inches, origin bottom-left, like
matplotlib), so the PPTX writer can rebuild the same slide from native PowerPoint objects.

Only active while `CURRENT` is a Scene (set by build() when a native PPTX is requested); otherwise hooks are no-ops.
"""
CURRENT = None


class Scene:
    def __init__(self, font='Times New Roman'):
        self.items = []
        self.font = font

    # --- primitives (all coordinates in inches from the slide's bottom-left)
    def text(self, x, y, s, ha='left', va='bottom', size=12, bold=False, color='#000000', fill=None, edge=None, name=None,
             spacing=1.0, pad=0.07):
        if s:
            self.items.append(dict(k='text', x=x, y=y, s=str(s), ha=ha, va=va, size=size, bold=bold, color=color, fill=fill,
                                   edge=edge, name=name, spacing=spacing, pad=pad))

    def poly(self, pts, color, lw=1.0, closed=False, fill=None, alpha=1.0, fill_alpha=1.0, dash=None, name=None, cap='round'):
        self.items.append(dict(k='poly', pts=[tuple(p) for p in pts], color=color, lw=lw, closed=closed, fill=fill, alpha=alpha,
                               fill_alpha=fill_alpha, dash=dash, name=name))

    def oval(self, cx, cy, d, fill, edge=None, edge_w=1.0, alpha=1.0, name=None, group=None):
        self.items.append(dict(k='oval', cx=cx, cy=cy, d=d, fill=fill, edge=edge, edge_w=edge_w, alpha=alpha, name=name, group=group))

    def rect(self, x, y, w, h, edge=None, edge_w=1.0, fill=None, dash=None, rounded=False, alpha=1.0, name=None):
        self.items.append(dict(k='rect', x=x, y=y, w=w, h=h, edge=edge, edge_w=edge_w, fill=fill, dash=dash, rounded=rounded,
                               alpha=alpha, name=name))

    def line(self, p0, p1, color, lw=1.0, name=None):
        self.poly([p0, p1], color, lw, name=name)

    def image(self, path, x, y, w, h, name=None):
        self.items.append(dict(k='image', path=str(path), x=x, y=y, w=w, h=h, name=name))

    def card(self, x, y_top, w, h, text, color, size=14, name=None):
        """Callout card: rounded rectangle with colored outline and text inside (top-left anchored)."""
        self.items.append(dict(k='card', x=x, y_top=y_top, w=w, h=h, s=text, color=color, size=size, name=name))

    def chart(self, x, y, w, h, spec, name='Chart'):
        self.items.append(dict(k='chart', x=x, y=y, w=w, h=h, spec=spec, name=name))
