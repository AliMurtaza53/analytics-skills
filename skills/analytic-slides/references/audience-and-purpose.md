# Audience, purpose, technical depth (decide these first)

Three independent inputs, plus venue and delivery. Do not collapse them into one "audience type": a domain expert at a research showcase needs a different slide than the same expert auditing geometry.

| Dimension | Options | Controls |
|---|---|---|
| audience | public, policy, interdisciplinary, domain_expert, technical_reviewer | terminology, background explained, visual complexity |
| purpose | inform, explain, compare, persuade, decide, validate | narrative, register schema, callouts, takeaway |
| depth | introductory, intermediate, advanced | how much of the register shows, coordinates, assumptions, citations |

Defaults the builder derives (all overridable by explicit spec keys):

| Brief | Register schema | Coordinate ticks | Legend | Fields shown |
|---|---|---|---|---|
| purpose validate, or a specialist audience | geometry_validation | yes | full, grouped by kind | all (advanced) |
| purpose explain | methods | only for specialists | simple unless specialist | 4 (intermediate) / essentials (introductory) |
| purpose inform / persuade / compare | results | no | simple | as above |
| purpose decide | decision | no | simple | as above |

Same analysis, different slide: change only the brief and the words. Example: `examples/beryl_example.py` (geometry review vs method explainer from one set of layers).

Principle: the goal is not to maximize information per slide; it is to maximize accurate understanding per unit of audience attention. One key idea per slide. If a slide needs two ideas, make two slides. If the register will not fit at 10 pt, cut words or split; never shrink.
