"""Design tokens for analytic slides. Everything visual is defined here; layouts only place things."""
SLIDE_W, SLIDE_H = 13.333, 7.5  # inches, 16:9 widescreen
MARGIN = 0.5
DPI = 200

THEMES = {
    # 'paper' matches the manuscript figures (Times New Roman); 'sans' is the same palette in Arial for slides that sit
    # next to non-paper material.
    'paper': dict(font='Times New Roman', title='#16324F', text='#1d2a35', muted='#5b6672', land='#efece6',
                  water='#f6faff', frame='#8d99a6', status='#D55E00', card='#ffffff', rule='#d5dbe1'),
    'sans': dict(font='Arial', title='#16324F', text='#1d2a35', muted='#5b6672', land='#efece6',
                 water='#f6faff', frame='#8d99a6', status='#D55E00', card='#ffffff', rule='#d5dbe1'),
}

# Badge / layer accent colors: colorblind-checked set used in the manuscript figures (blue, green, vermillion, amber, purple, slate).
ACCENTS = ['#3a7ca5', '#009E73', '#D55E00', '#E1A730', '#7B4FA3', '#3d4d5c']

# Type scale (pt). Slides never go below MIN_PT; the register auto-shrinks from BODY_PT down to MIN_PT before failing.
TITLE_PT, SUBTITLE_PT, HEAD_PT, BODY_PT, MIN_PT, CAPTION_PT, TICK_PT, FOOT_PT = 28, 15, 14, 12, 10, 12, 9, 9

# Basemap sources (contextily names). 'none' draws plain land/water from the theme.
BASEMAPS = {
    'esri_gray': 'Esri.WorldGrayCanvas',
    'osm': 'OpenStreetMap.Mapnik',
    'esri_imagery': 'Esri.WorldImagery',  # use with basemap_alpha ~0.45 so overlays stay visible
    'none': None,
}
