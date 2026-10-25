"""Illustrative example (Beryl x Houston-Galveston geometry review). Geometry and AIS tracks are SYNTHETIC stand-ins drawn
to resemble the reviewed sheet; replace with real layers. Run:  python examples/beryl_example.py
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from slidekit.build import build, LAYOUTS  # noqa: E402

rng = np.random.default_rng(7)
channel = [[-95.30, 29.75], [-95.22, 29.72], [-95.12, 29.74], [-95.05, 29.76], [-95.0, 29.68], [-94.95, 29.55],
           [-94.88, 29.45], [-94.80, 29.35], [-94.72, 29.31], [-94.65, 29.30]]
tracks = []
for _ in range(14):  # offshore approach tracks converging on the outer gate
    start = np.array([-94.4 + rng.uniform(-.08, .1), 28.75 + rng.uniform(0, .5)])
    end = np.array([-94.75, 29.3])
    t = np.linspace(0, 1, 60)[:, None]
    tracks.append(start + (end - start) * t + rng.normal(0, .015, (60, 2)).cumsum(0) * .35)
ais = np.vstack(tracks)
register = [
    dict(id=1, title='Extraction support', color='#3a7ca5', fields=[
        ('Geometry', 'Houston–Galveston rectangle'), ('Source', 'Analyst-defined coordinates'),
        ('Rule', '−95.5 to −94.3° lon; 28.7 to 30.1° lat'), ('Use', 'Download, screen and contextualize AIS'),
        ('Not', 'A port, harbor or legal boundary')]),
    dict(id=2, title='Corridor support', color='#009E73', fields=[
        ('Geometry', '500 m buffer around selected centerlines'), ('Source', 'Historical National Waterway Network'),
        ('Rule', 'Name match for Houston/Galveston channel links'), ('Use', 'Measure movement in the navigation system'),
        ('Not', 'A current surveyed channel polygon')]),
    dict(id=3, title='Passage support', color='#D55E00', fields=[
        ('Geometry', 'Outer gate (3A) + inner gate (3B)'), ('Source', 'Analyst seed points + historical centerline'),
        ('Rule', 'Snap to line; draw perpendicular ±2.5 km; pair crossings by vessel within 48 h'),
        ('Use', 'Count completed reference-reach passages'), ('Not', 'A berth call, cargo delivery or legal reopening')]),
]
bbox = [-95.5, 28.7, -94.3, 30.1]
map1 = dict(bbox=bbox, basemap='esri_gray', caption='Candidate analytical supports', layers=[
    dict(type='points', coords=ais.tolist(), color='#3a7ca5', s=4, alpha=.55),
    dict(type='bbox', coords=bbox, color='#3a7ca5', lw=2.2, ls='--'),
    dict(type='line', coords=channel, color='#009E73', lw=3.0, alpha=.9),
    dict(type='gate', coords=[[-94.84, 29.31], [-94.78, 29.39]], color='#D55E00'),
    dict(type='gate', coords=[[-95.09, 29.72], [-95.03, 29.78]], color='#E1A730'),
], badges=[dict(id=1, lonlat=[-95.4, 30.02], color='#3a7ca5'), dict(id=2, lonlat=[-95.13, 29.68], color='#009E73'),
           dict(id='3A', lonlat=[-94.73, 29.28], color='#D55E00'), dict(id='3B', lonlat=[-95.2, 29.82], color='#E1A730')])
map2 = dict(bbox=[-95.15, 29.2, -94.55, 29.9], basemap='esri_gray', caption='Passage gates (zoom)', layers=[
    dict(type='line', coords=channel, color='#009E73', lw=3.0),
    dict(type='gate', coords=[[-94.84, 29.31], [-94.78, 29.39]], color='#D55E00'),
    dict(type='gate', coords=[[-95.09, 29.72], [-95.03, 29.78]], color='#E1A730'),
], badges=[dict(id='3A', lonlat=[-94.73, 29.28], color='#D55E00'), dict(id='3B', lonlat=[-95.12, 29.8], color='#E1A730')])
spec = dict(
    name='beryl_houston_galveston',
    title='Beryl × Houston–Galveston: three supports, three questions',
    subtitle='Geometry must be approved before scaling to other events',
    status='PROVISIONAL — analyst review required',
    maps=[map1, map2], register=register,
    callouts=[
        dict(id=1, title='Extraction', text='Screens AIS only; not a port boundary.', target=[-94.33, 30.06], color='#3a7ca5'),
        dict(id=2, title='Corridor', text='500 m around historical centerlines.', target=[-95.0, 29.6], color='#009E73'),
        dict(id='3A', title='Outer gate', text='Pairs crossings by vessel within 48 hours.', target=[-94.81, 29.35], color='#D55E00')],
    takeaway='Approve or revise each support before any count is reported.',
    source='Display points: moving cargo/tanker AIS reports on 8 July 2024 (synthetic stand-ins in this example). AIS is shown for context and did not define the supports. Basemap: Esri World Light Gray Canvas.')

if __name__ == '__main__':
    out = Path(__file__).resolve().parent / 'out'
    for lay in LAYOUTS:
        print(build(spec, lay, out=out, formats=('png', 'pdf', 'pptx')))
