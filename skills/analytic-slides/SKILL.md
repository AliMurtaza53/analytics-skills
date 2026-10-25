---
name: analytic-slides
description: Design and build 16:9 analytic slides for fast scientific talks (one idea per slide). Starts from a presentation brief (audience, purpose, technical depth) that drives title style, register schema, legend and map conventions, then renders map+register, two-map comparison, annotated map, or map+chart slides to PNG/PDF/PPTX. Use when turning geospatial or analytical work into slides, geometry reviews, method explainers or result slides.
---

# Analytic slides

A presentation design system first, a renderer second. Decide *what to communicate, to whom, and how* before deciding where the map goes. Goal: maximize accurate understanding per unit of audience attention, not information per slide. Palette and typography are shared with `multipanel-figures` (manuscript figures).

## Workflow
1. **Brief** (`spec.brief`): audience, purpose, depth, venue, delivery. See `references/audience-and-purpose.md`. These drive defaults; any explicit spec key overrides them.
2. **Story**: one key idea per slide (a comparison, a data/procedure-dense point, or one graphic explained). Pick the title style from the purpose (`references/title-and-subtitle.md`); the subtitle narrows the title or is omitted.
3. **Layout and content**: choose the layout and the register schema (below); decide the legend detail and annotation density (`references/cartography.md`, `references/legends-and-annotations.md`).
4. **Render**: `build(spec, layout)`. Switch layouts freely, the content spec does not change.
5. **QA**: read the `[qa]` lines, then run the five audience tests (`references/quality-control.md`). If it does not fit: remove redundancy, simplify labels, switch layout or split the slide. Never just shrink text.

## Brief -> defaults (explicit keys always win)
| Brief | Register schema | Coordinate ticks | Legend |
|---|---|---|---|
| validate, or specialist audience | `geometry_validation` | on | full, grouped by kind |
| explain | `methods` | specialists only | simple unless specialist |
| inform / persuade / compare | `results` | off | simple |
| decide | `decision` | off | simple |
Depth trims the register: advanced = all fields, intermediate = 4, introductory = essentials only. North arrow is off by default (north-up).

## Register schemas (order matters; extendable; `schema: free` disables checking)
- `geometry_validation`: Geometry, Source, Rule, Use, Not, Decision
- `results`: Finding, Evidence, Interpretation, Caveat
- `methods`: Inputs, Transformation, Outputs, Assumptions
- `decision`: Problem, Alternatives, Tradeoffs, Recommendation

## Layouts (`layout=`)
| layout | use when | content |
|---|---|---|
| `map_side` | one map + objects/results to explain | `maps[0]`, `register` |
| `two_maps_side` | spatial comparison (same extent/scale/classes unless the point is the zoom) | `maps[0:2]` with `caption`, `register` |
| `annotated_map` | one graphic explained by callouts | `maps[0]`, `callouts` (or auto from badges), `takeaway` |
| `map_chart` | geography linked to quantitative evidence | `maps[0]`, `chart` (bar/hbar/line), `takeaway` |
Planned: methodology/process flow, full-width chart, comparison table, decision matrix.

## Integrity rules (mandatory, not style)
Synthetic or placeholder geometry/values: footer says so + status chip. Observations, analytical constructs and official features are distinguished (layer `kind`; legend groups them). Every geometry-review object has a `Not` line. Footer names data, vintage, basemap. Never invent a number for a finding; mark placeholders ILLUSTRATIVE.

## Spec (dict or JSON; see `templates/`)
```
name, title, subtitle, status, source, takeaway, synthetic: bool, schema (optional override)
brief: {audience, purpose, depth, venue, delivery}
maps: [{bbox:[w,s,e,n], basemap: esri_gray|osm|esri_imagery|none, basemap_alpha, caption,
        coords, north_arrow, scale_bar, legend_detail: full|simple, legend_loc, legend_anchor, inset:{bbox,size},
        layers:[{type: bbox|line|gate|points|polygon, coords, color, lw, ls, alpha,
                 kind: observation|construct|official, label, simple_label}],
        badges:[{id, lonlat, color}]}]
register: [{id, title, color, fields:[[label, text], ...]}]
callouts: [{id, title, text, target:[lon,lat], color}]
chart: {type: bar|hbar|line, categories, series:[{name, values, color}], xlabel, ylabel, annotate}
```

## Use
```
python -m slidekit.build spec.json --layout map_side --theme paper --out out/
python examples/beryl_example.py      # geometry review (3 layouts) + method explainer, synthetic data
```
Templates: `templates/{geometry-review,methodology,research-result,map-comparison}.json` (placeholders are marked REPLACE). Run from `skills/analytic-slides/`. Needs python 3.10+, matplotlib, contextily, pyproj, python-pptx; internet for basemap tiles (falls back to a plain frame offline and says so).
PPTX output is one full-bleed picture with the text in the notes; editable PowerPoint objects are a planned improvement.

## Extending
Layouts: `slidekit/build.py` (`LAYOUTS`, `_DISPATCH`). Tokens: `slidekit/theme.py`. Brief logic and schemas: `slidekit/briefs.py`. Layers/legend/inset: `slidekit/mapview.py`. Register: `slidekit/register.py`. Reference docs live in `references/`; keep SKILL.md a concise decision guide.
