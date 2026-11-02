# analytics-skills

Personal collection of Claude skills for analytical work, laid out like `isaaccorley/geospatial-skills`: `skills/<name>/SKILL.md` plus supporting code and references.

| Skill | What it does |
|---|---|
| `analytic-slides` | Presentation design system for analytic slides: a brief (audience, purpose, depth) drives title style, register schema, legend and map conventions; renders map+register, two-map comparison, annotated map and map+chart slides to PNG/PDF/PPTX |
| `multipanel-figures` | House rules for multi-panel manuscript figures (page geometry, font ratios, titles and letters, legends, colorblind-checked palette, registry-driven build). The reference implementation lives in the ResiFlow repo (`results/viz`, branch `viz/paper-figures`) |
| `scripted-geospatial-analytics` | Reproducible spatiotemporal and geospatial analysis workflow: scripted metrics, dated data snapshots, self-contained HTML quick checks, targeted ArcGIS Pro review, and provenance packaging |

Install a skill by copying (or symlinking) `skills/<name>` into `~/.claude/skills/`.
Both skills share one palette and type system so slides and manuscript figures read as one body of work.
