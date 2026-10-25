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
# Layer `kind` drives the legend grouping: observation (AIS) / construct (analyst-defined) / official (published feature).
bbox = [-95.5, 28.7, -94.3, 30.1]
LAYERS = [
    dict(type='points', coords=ais.tolist(), color='#3a7ca5', s=4, alpha=.55, kind='observation', label='AIS position report',
         simple_label='Vessel positions'),
    dict(type='bbox', coords=bbox, color='#3a7ca5', lw=2.2, ls='--'),
    dict(type='line', coords=channel, color='#009E73', lw=3.0, alpha=.9, kind='official', label='Channel centerline (historical)',
         simple_label='Navigation channel'),
    dict(type='gate', coords=[[-94.84, 29.31], [-94.78, 29.39]], color='#D55E00', kind='construct', label='Passage counting gate'),
    dict(type='gate', coords=[[-95.09, 29.72], [-95.03, 29.78]], color='#E1A730'),
]
BADGES = [dict(id=1, lonlat=[-95.4, 30.02], color='#3a7ca5'), dict(id=2, lonlat=[-95.13, 29.68], color='#009E73'),
          dict(id='3A', lonlat=[-94.73, 29.28], color='#D55E00'), dict(id='3B', lonlat=[-95.2, 29.82], color='#E1A730')]
map1 = dict(bbox=bbox, basemap='esri_gray', caption='Candidate analytical supports', layers=LAYERS, badges=BADGES)
map2 = dict(bbox=[-95.15, 29.2, -94.55, 29.9], basemap='esri_gray', caption='Passage gates (zoom)', legend=False,
            layers=[l for l in LAYERS if l['type'] in ('line', 'gate')],
            badges=[b for b in BADGES if str(b['id']).startswith('3')])
SOURCE = ('Display points: moving cargo/tanker AIS reports on 8 July 2024 (SYNTHETIC stand-ins in this example). AIS is shown for '
          'context and did not define the supports. Basemap: Esri World Light Gray Canvas.')

# 1) Technical review (default brief): validate, specialist audience, advanced depth -> geometry-validation register, coordinate
#    ticks, full grouped legend, decision-oriented title.
spec = dict(
    name='beryl_geometry_review', synthetic=True,
    brief=dict(audience='technical_reviewer', purpose='validate', depth='advanced', venue='geometry review', delivery='live'),
    title='Three spatial definitions require validation',
    subtitle='Houston–Galveston · Hurricane Beryl, July 2024 · extraction, corridor and passage supports',
    status='PROVISIONAL — analyst review required', source=SOURCE,
    maps=[map1, map2], register=register,
    callouts=[
        dict(id=1, title='Extraction', text='Screens AIS only; not a port boundary.', target=[-94.33, 30.06], color='#3a7ca5'),
        dict(id=2, title='Corridor', text='500 m around historical centerlines.', target=[-95.0, 29.6], color='#009E73'),
        dict(id='3A', title='Outer gate', text='Pairs crossings by vessel within 48 hours.', target=[-94.81, 29.35], color='#D55E00')],
    takeaway='Approve or revise each support before any count is reported.')

# 2) Same geometry, different audience: interdisciplinary researchers, explain a method, intermediate depth -> methods register,
#    no coordinate ticks, simple legend, descriptive title. Only the brief and the words change.
methods_register = [
    dict(id=1, title='Extraction', color='#3a7ca5', fields=[
        ('Inputs', 'AIS position reports, 8 July 2024'), ('Transformation', 'Keep cargo/tanker reports inside the Houston–Galveston rectangle'),
        ('Outputs', 'A screened set of vessel positions'), ('Assumptions', 'The rectangle is a data window, not a port boundary')]),
    dict(id=2, title='Corridor', color='#009E73', fields=[
        ('Inputs', 'Historical waterway centerlines'), ('Transformation', 'Select channel links by name; buffer by 500 m'),
        ('Outputs', 'Positions that fall in the navigation system'), ('Assumptions', 'Historical lines approximate today’s channel')]),
    dict(id=3, title='Passage', color='#D55E00', fields=[
        ('Inputs', 'Channel centerline + analyst seed points'), ('Transformation', 'Draw perpendicular gates; pair crossings by vessel within 48 h'),
        ('Outputs', 'Completed passages between the two gates'), ('Assumptions', 'A passage is not a berth call or a legal reopening')]),
]
spec_method = dict(spec, name='beryl_method_explainer',
                   brief=dict(audience='interdisciplinary', purpose='explain', depth='intermediate', venue='research showcase', delivery='live'),
                   title='Defining three spatial supports for AIS',
                   subtitle='Houston–Galveston · Hurricane Beryl, July 2024', register=methods_register, callouts=None, takeaway=None)

if __name__ == '__main__':
    out = Path(__file__).resolve().parent / 'out'
    for lay in ('map_side', 'two_maps_side', 'annotated_map'):
        print(build(spec, lay, out=out, formats=('png', 'pdf', 'pptx')))
    print(build(spec_method, 'map_side', out=out, formats=('png', 'pdf', 'pptx')))
