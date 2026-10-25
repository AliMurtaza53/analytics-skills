---
name: multipanel-figures
description: House style for advisor-ready multi-panel bar-chart figures (ResiFlow RQ1/RQ2/RQ3 sheets) - page geometry, font-size ratios, panel letters and sub-panel numbering, data labels, tick/axis rules, whitespace, legends, grouped-event boxes, v2 layout variant. Use whenever creating or editing a multi-panel matplotlib figure, a new RQ sheet, or fixing spacing/labels in results/viz/build_advisor_package.py.
---

# Multi-panel figure conventions

Reference implementation: `results/viz/build_advisor_package.py` (layout, fonts, sheets) and `results/viz/build_advisor_review_figures.py` (`grouped_hazard_labels`, `plot_generic`, `finish_labels_and_legends`). Change the generator, never hand-edit PDFs/PNGs. Rebuild with `python build_advisor_package.py --labeled-only --no-zip` (add `--v2` for the v2 variant), render the PNG, and LOOK at it after every change.

Items marked (inferred) were read off the rendered figures, not from a documented constant; confirm before treating as law.

## Page and canvas
- Every figure is 180 mm wide, vector PDF, no scaling. Combined sheets are US Letter, figures centered horizontally, vertically centered with at least 12 mm margins. Stacked panel heights must total <= 255 mm (the script asserts this).
- Each panel canvas is sized to its content (e.g. RQ3 A 56 mm, B 197 mm; RQ2 A 70, B 75, C 110). Do not pad a canvas to "look balanced"; trim it.
- One sheet per RQ: RQ1 solo figure (page 1) + A over B (page 2); RQ2 A/B/C stacked; RQ3 A over B.

## Fonts (Times New Roman)
Ratios relative to the panel letter "(A)" = 12 pt:
| Element | Size | Style |
|---|---|---|
| Panel letter "(A)" | 12 pt | bold |
| Sub-panel title "(i) Total cost" | 11 pt | bold, black, left-aligned |
| Tick labels, axis labels, legend, y category labels, group labels | 10 pt | regular (group labels bold, `#333333`) |
| Bar-end data labels | 10 pt | bold, black |
| Stack (segment) labels | 8 pt | regular |
So: 12 / 11 / 10 / 8. The package forces every Text object to 10 pt in one pass, so any per-element size override must come AFTER that loop.

## Panel letters and sub-panel titles
- Panel letter sits at fig x = .025, left-aligned, bold. Baseline = top of the first-row sub-panel titles; if there are no titles, it clears the top of the axes by 4 pt. Never closer than 17 pt to the top of the canvas (`align_panel_label` does this - call it again after any `subplots_adjust`/`set_position`).
- No title text for single-plot panels; the letter is the only heading (e.g. RQ1 A, RQ3 A/B).
- When a panel holds several distinct sub-plots, each is numbered `(i)`, `(ii)`, `(iii)`, `(iv)` with a short bold descriptive title placed above its axes, left-aligned with the axes (`loc='left'`). Sub-plots are numbered because they show different quantities. Sub-plots that only repeat one measure for different events (RQ2 C) are titled by event name with the same numbering.
- Event order and names are fixed everywhere: (i) Hurricane Harvey, (ii) New Madrid Earthquake, (iii) New Madrid Landslide, (iv) Winter Storm Jonas.
- Row labels of the top row sit right under the baseline of the panel letter / title block, with no extra gap (RQ1 B.i is the model).

## Grid of sub-plots
- Symmetric layout: 2 columns, even when rows differ (RQ1 B is 2x2, RQ2 A and B are 1x2, RQ2 C is 2x2). Don't leave a ragged or single-column panel in a multi-panel sheet.
- Within a column that shares a unit, only the bottom row gets tick labels and the x-axis label; upper rows show ticks only (RQ2 C). Sub-plots with different units keep their own labels (RQ1 B).
- Whitespace between panels is the bare minimum and the same on every sheet: the gap from the bottom of one panel's last element (x-label or legend) to the next panel letter should look like RQ2 A->B. Tune each canvas's `top`/`bottom` and height instead of adding padding. Same rule inside a panel: no gap between the last bar and the x-axis.

## Axes, ticks, grids
- X-axis labels are sentence case with units in parentheses: "Direct infrastructure damage cost (billions of dollars, 2023)", "Rerouting cost (millions of dollars, 2023)".
- Axis starts at 0. Tick labels: at least 6 on a full-width (double-column) plot, more rather than fewer; nicer steps (0.5, 0.75, 1, 30k...) via explicit locators.
- Axis upper limit = last labeled tick at most one step past the longest bar plus label; cap at a round tick (RQ1 A at 4.5, RQ3 B at 9). Never leave a long unlabeled tail. A loop widens xlim only until the bar-end labels fit (+3 px).
- 100 % stacked bars: ticks and grid stop at 100 %; do not let the axis run to 120 %. The only extra room is the small space for the bold "100%" total label.
- Bars: height .64 of the row pitch; y-limits `(n - .52, -.48)` so the gap above the first bar and below the last bar are equal and small. Top and right spines off; faint vertical gridlines only (inferred).
- Thousands/millions: put the scale in the axis label and divide tick values (RQ1 B.ii "Thousands of dollars (2023) per lane-mile").

## Data labels
- Totals sit at the end of the bar (about 9 pt right of the bar/error bar), bold, black, with units: `$2.89 Bn` (2 decimals for billions), `$864 Mn` (integer, thousands separator for millions), `$41,947/lane-mi`, `$140/person`, `0.22%`, `100%`.
- Stack (segment) labels are OFF by default (too crowded). Turn them on only for a plot where every segment's text fits inside its segment at final size - typically 100 % stacks such as RQ3 A. Check at the final physical size; if any label would not fit, drop all of them for that plot.
- Labels must never exceed the axes' right edge.

## Legends
- One shared legend per panel (not per sub-plot), no frame, centered under the x-axis label, ~10 pt below the label's lower edge, 10 pt text.
- Five or more categories: 2 columns. Reserve bottom margin for the full row count (RQ3 B needs 3 rows; with too little margin matplotlib silently clips the legend at the canvas edge and entries disappear).
- Category colors are fixed per concept across all figures (Direct dark slate, Rerouting blue, Isolation amber; severity as a sequential blue ramp; hazards each with their own color; industries teal/amber/terracotta/blue/grey). Reuse the same mapping for the same concept.

## Grouped categories (events with several rows each)
- Light panel box per group (face `#fafafa`, edge `#dddddd`), thin `#eeeeee` separator lines between groups, rotated bold group label centered on each box at axes-fraction x = -.18, box extending to x = -.235.
- Group labels carry their numeral: `(i) Hurricane / Harvey`. "New Madrid ..." names are split over 3 lines in tight boxes. Rows inside a group are sorted by value, largest first.
- v2 layout (`--v2`): numerals move outside the box on the left, plot shifts right by the width reclaimed from capping the x-axis, then the plot is stretched left by `V2_STRETCH` (.035 of figure width) so it still fills the page width.

## Pitfalls that already bit us
- `fig.subplots_adjust(...)` resets any `ax.set_position(...)`; re-apply the shift afterwards (see the RQ3 combined branch).
- Anything placed in axes-fraction units (group boxes, labels, numerals) must be rescaled by old_width / new_width when the axes width changes, otherwise it collides with tick labels.
- Re-run `align_panel_label` after any vertical layout change.
- Source files use CRLF; do scripted edits with `newline=''` or normalise first.
- `--v2` also rebuilds all other plots with a `_v2` suffix; delete the extras and only keep the ones requested. v2 overwrites any existing `_v2` file.
- Synthetic placeholder data are labeled as such in README.txt / provenance.json; keep that wording until real results replace them.

## Checklist before saying "done"
1. Rebuilt via the script; PNG viewed at full page.
2. Fonts 12/11/10/8 only; sentence-case axis labels; (i)-(iv) numbering consistent.
3. No clipped legend or label; no overlap with tick labels; totals inside axes.
4. Gaps between panels consistent with RQ2; no gap between last bar and axis.
5. Axis caps at a labeled tick; 100 % plots cap at 100 %.
6. Only requested files changed (check `labeled/` and `unlabeled/` folders).

## labeled_v2 numbering revision (supersedes the (i)-(iv) rules above where they conflict)
Build: `python build_advisor_package.py --labeled-v2 --no-zip` -> `advisor_package/labeled_v2/`.
- Event numerals (i)-(iv) are gone everywhere (group labels, RQ2 Passenger/Freight, RQ2 C event titles). Event names stay, in the same fixed order.
- Each plot with its own metric / x-axis gets a letter, left to right then top to bottom, in a bold 12 pt title of the form "(B) Total Cost": title case, with small words (by, of, in, to, per, and) lowercase. Examples: "(A) Direct Costs by Top States", "(C) Cost per Lane-mile of Roadways". Plots that share one x-axis label (RQ2 A, B, C) keep one letter per panel.
- `_wlabel` sheets carry these titles; `_nolabel` sheets keep the bare "(A)" letter. RQ2 and RQ3 have both; RQ1_2 exists only titled; RQ1_1 is a solo export with no labels.
- Titled sheets leave extra room between title and plot (title baseline +4 pt for single plots, +5 pt above subtitles, axes title pad 8 pt). Unlettered sub-plot subtitles (Passenger, Freight, event names) stay 11 pt bold.
- RQ1_1 solo is cropped with `bbox_inches='tight'` (pad .04 in) at 300 dpi, same pixel density as the sheets.
- Axis caps stay (RQ1_2 A at 4.5, RQ3 B at 9); the bars stretch to fill the width instead of shifting the plot. RQ1_2 A is 112 mm tall with 11 pt event names so three-line names fit their 3-row boxes.

## Palette (colorblind-checked; used by the labeled_v3 set)
Checked with Machado 2009 protan/deutan/tritan simulation and CIEDE2000 (aim: closest pair >= ~10, adjacent stacks higher). Source of truth: `HAZARD_COLORS`, `COST_COLORS`, `SEVERITY_COLORS`, `INDUSTRY_COLORS` in build_advisor_review_figures.py.
- Cost components (unchanged, shared across RQ1 B-E and RQ2): Direct `#3d4d5c`, Rerouting `#3a7ca5`, Isolation `#e1a730`. Min dE 17+ and a lightness ladder (L* 32/50/72) so they survive grayscale.
- Rerouting parts (RQ2 A) stay in the Rerouting blue family: Operating `#7fb6da`, Time `#3a7ca5` (= parent), Toll `#d3e6f3`.
- Events: Harvey `#56B4E9` (sky blue, was `#0072B2`, which clashed with the Rerouting blue on the RQ1_2 page), Earthquake `#D55E00`, Landslide `#8C510A`, Winter Storm `#009E73`. Best achievable min dE with the cost trio is ~10.
- Industries: Agriculture `#4c9f85`, Mining `#e8c65e`, Petroleum `#c26a3d`, Manufactured `#4E79A7`, Mixed `#c9cdd2`. Old teal vs grey pair was dE 1.2 under deuteranopia. Fills must keep black text contrast >= 4.5 for stack labels.
- Severity stays a light-to-dark blue ramp (optional: purple, `#dadaeb/#9e9ac8/#54278f`, if blue should mean only Rerouting).
- Before adding or changing a color, rerun the CVD check on the palette and on any palettes sharing a sheet.

## labeled_v3 revisions (latest)
- RQ2 C uses one shared, centered x-axis label under the 2x2 grid (like RQ2 A and B), not one per column; extra bottom margin (.20) so the legend is not clipped.
- Unit-style x-axis labels read "Billions of dollars, 2023", "Thousands of dollars, 2023, per lane-mile", "Dollars, 2023, per capita" (comma style, sentence case).
- RQ3 A is no longer a 100 % share chart (advisor: a share-only bar is a pie chart). It is a regular stacked bar of total disrupted freight cost per event, segments = industry mix, bold totals at the end, axis snapped to a labeled tick (0-35). Stack % labels are omitted because the small segments cannot all fit (all-or-none rule). The 100 % cap rule applies only to share charts, if one is ever used again.

## Current conventions (latest; these override anything above that conflicts)
**No white border.** Every sheet and solo figure in `labeled_v3` and `prototypes` is cropped to its drawn content plus a ~1 mm pad (`crop_to_content` in build_advisor_package.py for sheets; `bbox_inches='tight'`, pad .04 in for RQ1_1). Same scale and 300 dpi, only the page/crop box shrinks. The Letter-page and 12 mm margin rules above no longer apply to the exported files (the 255 mm stack-height assert still guards the layout).

**Folders and build flags** (all under results/viz/advisor_package/):
| Folder | Meaning | Build |
|---|---|---|
| `labeled`, `unlabeled` | original package, (i)-(iv) numerals, old palette | `build_advisor_package.py [--labeled-only]` |
| `labeled_v2` | first numbering revision, old palette | superseded; kept for comparison |
| `labeled_v3` | current set: lettered titles, no event numerals, colorblind palette, billions, tight crop | `--labeled-v2 --no-zip` |
| `prototypes` | RQ2 A+B merged, RQ3 A exposure ratio | `--labeled-v2 --proto --no-zip` |
`--v2` is the older "numerals outside the boxes" variant. The flag `--labeled-v2` writes to `labeled_v3` (name kept for history; folder name comes from `V3_DIR`).

**File naming in labeled_v3 / prototypes:** `RQ1_1` (solo, no labels), `RQ1_2` (lettered titles only), `RQ2_nolabel` / `RQ2_wlabel`, `RQ3_nolabel` / `RQ3_wlabel`, `RQ2_proto` / `RQ3_proto`. `_nolabel` = bare "(A)" letters; `_wlabel` = "(A) Title Case Title". PDF + PNG (300 dpi) for each.

**Lettering and titles:** one letter per plot that has its own metric / x-axis, left to right then top to bottom; plots that share one x-axis label (RQ2 A, B, C) keep one letter per panel. Titles bold 12 pt, title case with small words lowercase; unlettered subtitles (Passenger, Freight, event names) 11 pt bold. No (i)-(iv) event numerals anywhere. In RQ1_2 the left-column titles are flush with the (A) margin and right-column titles are shifted left by the width of "(" so the letter sits over the y-axis.

**Units and labels:** all cost figures in billions ("$0.16 Bn", 2 decimals), including RQ2 A/B; x-axis labels 11 pt (one point above body text); shared x-axis label centered under multi-column panels (RQ2 A, B, C). Unit wording: "Billions of dollars, 2023", "Thousands of dollars, 2023, per lane-mile", "Dollars, 2023, per capita".

**RQ3 A (prototype):** exposure ratio = share of disrupted cost / share of baseline truck flow, 2x2 events, bars from 1.0 in industry colors, bold "1.46x" labels. Baseline = `rq3_baseline_mix_by_event.csv` from `compute_rq3_baseline_mix.py` over FAF5 county OD (`C:\Users\akothaw\Desktop\data\soge_clusters\census_datasets\faf5_county_od.pq`, daily truck trips, flows touching the event's top-5 states). Numerator is still synthetic until `costs_long.csv` exists. RQ3 B shrinks to 160 mm when A is the exposure plot (bottom margin .21 so the 3-row legend is not clipped).

**RQ2 A+B (prototype):** one panel, rows = event x {Passenger, Freight} with event boxes, stack = Operating / Time / Toll (Rerouting blues) + Isolation (amber), one shared axis in billions (0-2.25). Passenger side and the Operating/Time/Toll split are synthetic. Rotated event names need ~12 mm per row (panel 135 mm).

**Palette and accessibility:** see the palette section; rerun the CVD check whenever colors change. Never reuse the Rerouting blue for another concept on the same sheet.

**Always:** edit the generator, rebuild, view the PNG; delete stray `_v2` / `_parts` outputs; keep the skill in sync with new rules.

## RQ3 A per advisor (2026-10-22, supersedes the exposure-ratio prototype as the default)
RQ3 A = aggregate disrupted freight cost per event, stacked by industry (federal-policy view); RQ3 B = the same by state. A's event total must equal the sum of B's bars (check this: a rounding bug once printed $29.00 Bn for $29.32 Bn; `stacked_barh` now always formats totals with 2 decimals). Real-data path: `rq3_real_data.py` (cost = freight rerouting + isolation at a chosen event day, split by `freight_industry_mix.json` flow shares; Direct infrastructure damage excluded because it cannot be attributed to a commodity). Real events differ by up to 5 orders of magnitude (Jonas $103 M vs Mineral landslide $3.5 K), so a linear shared axis shows only the largest bar; plan a log-scaled totals panel plus 100 % industry shares, or report units per event.

## Latest rules (2026-10-22, evening)
- Every legend gets a bold 10 pt descriptive heading via `title_legends` (e.g. "Cost type (stacked segments)", "Industry: freight commodity group (stacked segments)"); legend-bearing panels need ~12 mm below the x-label (RQ1_2 bottom .215, RQ2 C .235, heights RQ1c 140, RQ2a 79, RQ2c 126). Sheet page height is dynamic (total + 8 mm).
- RQ3 legend: 3 columns, two rows (five long names do not fit one row at 10 pt).
- Three-line rotated event labels: "New / Madrid / Earthquake" and "Winter / Storm / Jonas" in the RQ1_2 A boxes.
- RQ3 prototype: A = freight tonnage (Mt) and B = freight value ($Bn, 2017$, tons x FAF5 $/ton) side by side, state plot becomes C. Mining is large by tons and tiny by value; Mixed freight the reverse.
- Event set and naming: see memory `project-candidate-event-set`; "Winter Storm Jonas".

## Legend format (2026-10-22 late)
Legends carry a bold explainer as the first entry of the same row ("Cost type:", "Direct damage severity:", "Rerouting cost component:", "Non-damage cost type:" for Rerouting+Isolation only, "Freight commodity group:"). No "(stacked segments)". RQ3's five-entry legend: explainer column plus two rows of entries (columnspacing .4, handlelength 1.2 to fit 180 mm). Built by `title_legends` (recreates the legend). Axis label dollar years must match the registry columns `axis_dollar_year` / `dollar_year_by_component`.

## Architecture (2026-10-22): registry-driven paper set
See `results/viz/FIG_PIPELINE.md`. The paper set is defined by `visual_registry.csv` rows with `paper_figure` set (letters, titles, template, height, legend explainer); shared elements live in `results/viz/figlib/` (`legends`, `layout`, `registry`, `templates`); `python build_paper_final.py` builds and writes `advisor_package/final` + `MANIFEST.csv`. To change a title, letter, legend explainer or height, edit the registry, not the code. Title alignment: in a row of panel titles the first is flush with the sheet's left margin (like the panel letter), the right-hand one is shifted left by the width of "(" so its letter sits over the y-axis.
