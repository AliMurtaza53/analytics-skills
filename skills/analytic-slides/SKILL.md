---
name: analytic-slides
description: Build clean 16:9 analytic slides (one idea per slide) from a spec - a framed basemap map with a fixed-schema text register, two maps for comparison, or one annotated map with callouts. Use for fast 2-10 slide/minute talks built on analytical work (geometry reviews, event maps, method explainers). Same spec, switchable layouts; outputs PNG, PDF and PPTX.
---

# Analytic slides

Rulebook + builder for presentation slides that carry analytical content. Companion to the manuscript rules in `multipanel-figures` (same palette, typography and honesty conventions).

## Rules (apply to every slide)
1. **One key idea per slide.** Three kinds: a *comparison*, a *dense data/procedure point*, or *one graphic explained*. If two ideas, make two slides.
2. **Title = the claim**, one line (<= ~60 characters). The builder errors if it does not fit. Subtitle = the one qualifier or scope, one line, never touching the title (fixed spacing).
3. **Honesty chip.** Anything not final carries a status chip (`PROVISIONAL - analyst review required`, `ILLUSTRATIVE`, ...). Every register entry ends with a **Not** line: what the object is *not*.
4. **Fixed register schema** (extendable later): `Geometry / Source / Rule / Use / Not`, one numbered, color-coded entry per object. Badge numbers on the map match the register.
5. **Type:** title 28 pt, subtitle 15, entry heads 14, body 12 (auto-shrinks to 10, never below; if it still does not fit the builder raises: cut words), map captions 12-13, ticks/footer 9. Theme `paper` = Times New Roman (matches the manuscript), `sans` = Arial.
6. **Map frame:** thin neutral frame, degree tick labels only (no axis titles), scale bar in km at the map's mid-latitude, small north arrow (`north_arrow: False` to hide). Overlays use halo-ed lines and numbered badges with white rims.
7. **Color:** accents come from the colorblind-checked set (blue `#3a7ca5`, green `#009E73`, vermillion `#D55E00`, amber `#E1A730`, purple `#7B4FA3`, slate `#3d4d5c`); vermillion is also the status chip. Never encode meaning by color alone: badges carry numbers/letters.
8. **Basemap:** default `esri_gray` (Esri World Light Gray Canvas). Others: `osm`, `esri_imagery` (use `basemap_alpha` ~0.45 so overlays stay visible), `none` (plain land/water). Planned: NOAA ENC charts for navigation geography. Overlay analytic layers as vectors; the basemap is context only. State the basemap in the footer.
9. **Footer source line** (<= 2 lines, 9 pt): data source + vintage + what the display points are and are not.
10. **Synthetic or placeholder geometry must say so in the footer.**

## Layouts (switch with one argument; content spec is unchanged)
| layout | use when | content used |
|---|---|---|
| `map_side` | one map + objects to explain | `maps[0]`, `register`, `status` |
| `two_maps_side` | comparison (overview vs zoom, before vs after, A vs B) | `maps[0:2]` with `caption`s, `register` |
| `annotated_map` | one graphic explained by callouts | `maps[0]`, `callouts` (or auto from `register` entries that have a badge), `takeaway` |

Register or callout cards use the free space beside the map; the register hugs the map and takes the leftover width, so tall maps never leave a dead gap. In `annotated_map`, if the map is wide enough that <3.6 in remain, cards move inside the frame (give each a `box` in axes fraction).

## Spec (dict or JSON)
```
name, title, subtitle, status, source, takeaway (annotated only),
maps: [{bbox:[w,s,e,n], basemap, basemap_alpha, caption, north_arrow,
        layers:[{type: bbox|line|gate|points|polygon, coords, color, lw, ls, alpha, label}],
        badges:[{id, lonlat, color}]}],
register: [{id, title, color, fields:[[label, text], ...]}],
callouts: [{id, title, text, target:[lon,lat], color}]   # optional
```
Layer `label` entries build a small legend inside the map.

## Use
```
python -m slidekit.build spec.json --layout map_side --theme paper --out out/
# or from Python:  from slidekit.build import build;  build(spec, 'annotated_map', out='out')
```
Run from `skills/analytic-slides/`. Example with all three layouts: `python examples/beryl_example.py` -> `examples/out/*_{map_side,two_maps_side,annotated_map}.{png,pdf,pptx}` (synthetic geometry).
PPTX = one full-bleed picture slide with the title/takeaway/source in the notes (editable text is a possible extension).

## Checklist before presenting
- Title states the claim; one idea only; status chip present if not final.
- Every register entry has a Not line; badges match the register.
- Footer names data, vintage, basemap, and whether geometry is synthetic.
- No text under 10 pt; map ticks readable at projector distance (try the PNG at 50% size).
- Tried the other layout? Switching costs nothing.

## Extending
New layouts go in `slidekit/build.py` (`LAYOUTS`, `_DISPATCH`), tokens in `slidekit/theme.py`, new layer types in `slidekit/mapview.py`, new register fields by adding labels (the schema is not enforced yet). Planned: chart-slide layout (consistent with `multipanel-figures`), NOAA ENC basemap, editable PPTX text boxes, JSON schema validation.

Needs: python 3.10+, matplotlib, contextily, pyproj, python-pptx (internet for basemap tiles; falls back to a plain frame offline and says so).
