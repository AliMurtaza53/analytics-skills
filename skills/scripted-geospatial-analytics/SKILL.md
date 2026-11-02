---
name: scripted-geospatial-analytics
description: Build reproducible spatiotemporal and geospatial analyses from scripts, use self-contained HTML windows for rapid checks, and use ArcGIS Pro for targeted visual review and cartographic refinement. Use when working with AIS, boundary-sensitive metrics, change analysis, port resilience, maps, or spatial data pipelines.
---

# Scripted geospatial analytics

Use scripts as the analytical source of truth. Use HTML for fast inspection. Use ArcGIS Pro for human review, geometry inspection, and final cartography when it adds value.

## Operating model

1. **Define the question and support.** State the metric, unit, time window, event or comparison, spatial support, baseline, and intended interpretation before calculating results.
2. **Inventory inputs.** Record source, URL or file path, provider, release/update date, download date, CRS, fields used, filters, and license or access limits.
3. **Snapshot external data.** Use live services to discover and inspect layers. Save a dated local copy before analysis. Keep the original snapshot unchanged; create derived working layers separately.
4. **Analyze in code.** Prefer small, rerunnable scripts with explicit parameters. Write intermediate tables and final data products to named output folders. Avoid manual edits to analytical outputs.
5. **Generate a quick-check HTML window.** Make it self-contained and readable without a server. Include the map or chart, counts, date range, filters, CRS, support name, source, and a visible status such as `PROVISIONAL`, `ILLUSTRATIVE`, or `VALIDATED`.
6. **Review visually.** Open the HTML first. Use ArcGIS Pro when geometry, layer alignment, labels, symbology, or boundary interpretation needs inspection. Record decisions and corrections in a review table or notes file.
7. **Rebuild after decisions.** Apply approved changes to the script or source layer, rerun the analysis, regenerate HTML and final figures, and preserve the prior snapshot.
8. **Package provenance.** Save the script, inputs manifest, parameters, outputs, quick-check HTML, figures, review decisions, and a short README together.

## Boundary registry

When a study uses more than one spatial support, maintain a CSV registry before rerunning metrics. Use one row per boundary or support. Include: stable ID, name, boundary class, role, status, source organization, source landing page, feature-layer URL or local snapshot path, metrics or uses, ArcGIS Pro checks, and limitations. Keep official layers, analytical constructs, retrieval windows, and contextual areas in separate classes. Record when a candidate source has not been verified for the study area.

Use the registry to drive three decisions: which layer a script reads, which layer ArcGIS Pro reviews, and which boundary name appears in figures and prose. Do not substitute a live service for the recorded snapshot without updating the registry and rerunning validation.

## Data and geometry rules

- Distinguish **observations**, **official features**, **analytical constructs**, and **synthetic placeholders** in filenames, metadata, legends, and prose.
- Treat a retrieval rectangle as a data window, not a port boundary.
- Treat gates, buffers, and derived unions as analyst-defined supports unless the source explicitly publishes them as official features.
- Do not call a layer a port, terminal, channel, or service area without documenting who defined it and for what purpose.
- Keep geometry review separate from metric computation when possible. A plausible map does not validate a boundary.
- Use a projected CRS for distance, area, buffers, and travel-time geometry. Preserve the source CRS and document transformations.
- Check geometry validity, empty or null shapes, duplicate identifiers, feature counts, extent, overlap, and temporal coverage before computing metrics.

## AIS workflow

- Preserve raw AIS observations. Derive filtered cargo/tanker, moving, low-speed, and trajectory tables in separate outputs.
- Record vessel-type filters, speed thresholds, time zone, sampling interval, gap cap, interpolation rule, and track-pairing window.
- Treat a point as a retained report, not automatically as a unique visit or a minute of occupancy.
- For passage metrics, report the gates, crossing tolerance, ordering rule, pairing window, and censoring rule.
- For area metrics, report the support geometry and whether membership is point-in-polygon, segment intersection, or buffered proximity.
- Compare like with like. A change in metric and a change in spatial support are different sources of sensitivity.

## Quick-check HTML standard

Every HTML review should answer these questions near the top:

- What was measured?
- Where was it measured?
- When was it measured?
- Which records and filters were used?
- How many rows, vessels, events, or features were retained?
- What remains provisional or unvalidated?

Prefer one page with a map, a compact summary table, and one diagnostic chart. Use local assets or inline data so the page remains reviewable offline. Do not present synthetic values beside empirical values without an explicit label.

## ArcGIS Pro handoff

Use ArcGIS Pro after the scripted extract exists. Add the saved source and derived layers, inspect alignment and scale, review labels and symbology, and mark boundary decisions. Export approved geometry or a review decision; do not silently redraw the analytical source inside the map document.

## Validation checklist

- [ ] Inputs and versions are recorded.
- [ ] The local snapshot is preserved.
- [ ] CRS and transformations are documented.
- [ ] Counts and date ranges pass basic sanity checks.
- [ ] Geometry validity and spatial alignment are checked.
- [ ] Filters and thresholds are visible in the HTML review.
- [ ] Official, observed, constructed, and synthetic layers are distinguishable.
- [ ] Metric results state their support and limitations.
- [ ] ArcGIS review decisions are recorded and reflected in the rerun.
- [ ] Final outputs can be rebuilt from the saved script and inputs.

