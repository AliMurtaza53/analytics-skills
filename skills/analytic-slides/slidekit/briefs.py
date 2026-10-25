"""Presentation brief -> design defaults, register schemas, and a QA report.

The brief has three independent dimensions (audience, purpose, depth) plus venue/delivery. They drive the register
schema, how much of it is shown, coordinate ticks, legend detail and the title style. Every default can be overridden
in the spec (explicit keys always win).
"""

AUDIENCES = ('public', 'policy', 'interdisciplinary', 'domain_expert', 'technical_reviewer')
PURPOSES = ('inform', 'explain', 'compare', 'persuade', 'decide', 'validate')
DEPTHS = ('introductory', 'intermediate', 'advanced')

# Register schemas: ordered field labels; `essential` = what remains at low technical depth.
SCHEMAS = {
    'geometry_validation': dict(fields=['Geometry', 'Source', 'Rule', 'Use', 'Not', 'Decision'], essential=['Geometry', 'Use', 'Not']),
    'results': dict(fields=['Finding', 'Evidence', 'Interpretation', 'Caveat'], essential=['Finding', 'Evidence', 'Caveat']),
    'methods': dict(fields=['Inputs', 'Transformation', 'Outputs', 'Assumptions'], essential=['Inputs', 'Outputs', 'Assumptions']),
    'decision': dict(fields=['Problem', 'Alternatives', 'Tradeoffs', 'Recommendation'], essential=['Problem', 'Recommendation']),
}

# purpose -> default register schema and title style (guidance printed in the QA report; titles are never rewritten)
PURPOSE_RULES = {
    'validate': dict(schema='geometry_validation', title_style='decision-oriented question or action, e.g. "Are the passage gates correctly positioned?"'),
    'explain': dict(schema='methods', title_style='descriptive, e.g. "Defining three spatial supports for AIS"'),
    'inform': dict(schema='results', title_style='finding/claim, e.g. "Channel activity fell sharply during Beryl"'),
    'persuade': dict(schema='results', title_style='finding/claim with the implication'),
    'compare': dict(schema='results', title_style='contrast, e.g. "Regional activity masks channel disruption"'),
    'decide': dict(schema='decision', title_style='action-oriented, e.g. "Validate channel geometry before scaling"'),
}

TECHNICAL = ('domain_expert', 'technical_reviewer')


def resolve(brief):
    """Fill defaults from the brief. Unknown/missing brief -> neutral technical-review defaults (backward compatible)."""
    b = dict(audience='technical_reviewer', purpose='validate', depth='advanced', venue='', delivery='live')
    b.update(brief or {})
    assert b['audience'] in AUDIENCES, f'audience must be one of {AUDIENCES}'
    assert b['purpose'] in PURPOSES, f'purpose must be one of {PURPOSES}'
    assert b['depth'] in DEPTHS, f'depth must be one of {DEPTHS}'
    technical = b['audience'] in TECHNICAL or b['purpose'] == 'validate'
    return dict(
        brief=b,
        schema=PURPOSE_RULES[b['purpose']]['schema'],
        title_style=PURPOSE_RULES[b['purpose']]['title_style'],
        coords=technical,                     # degree tick labels: geometry review / specialists only
        legend_detail='full' if technical else 'simple',
        north_arrow=False,                    # north-up maps do not need one
        essential_only=b['depth'] == 'introductory',
        max_fields=None if b['depth'] == 'advanced' else (3 if b['depth'] == 'introductory' else 4),
    )


def apply_schema(register, schema_name, essential_only=False, max_fields=None, strict=True):
    """Validate/trim register fields against the schema. Returns a new register list."""
    if schema_name == 'free':
        return register
    sc = SCHEMAS[schema_name]
    out = []
    for e in register:
        labels = [l for l, _ in e.get('fields', [])]
        bad = [l for l in labels if l not in sc['fields']]
        if bad and strict:
            raise ValueError(f"register entry {e.get('id')}: fields {bad} not in schema '{schema_name}' {sc['fields']} "
                             f"(use schema 'free' or fix the labels)")
        fields = sorted(e.get('fields', []), key=lambda f: sc['fields'].index(f[0]) if f[0] in sc['fields'] else 99)
        if essential_only:
            fields = [f for f in fields if f[0] in sc['essential']]
        elif max_fields:
            keep = [f for f in fields if f[0] in sc['essential']]
            rest = [f for f in fields if f[0] not in sc['essential']]
            fields = sorted((keep + rest)[:max_fields], key=lambda f: sc['fields'].index(f[0]))
        out.append(dict(e, fields=fields))
    return out


def qa(spec, resolved, register_used):
    """Substantive checks the renderer cannot enforce. Returns a list of strings (empty = nothing flagged)."""
    w = []
    sch = resolved['schema']
    if sch == 'geometry_validation':
        for e in spec.get('register', []):
            if 'Not' not in [l for l, _ in e.get('fields', [])]:
                w.append(f"entry {e.get('id')} has no 'Not' line (what it is not): required for geometry review")
    foot = (spec.get('source') or '').lower()
    if spec.get('synthetic') and 'synthetic' not in foot and 'illustrative' not in foot:
        w.append('spec is marked synthetic but the footer does not say so: scientific-integrity rule')
    if spec.get('status') is None and spec.get('synthetic'):
        w.append('synthetic/provisional content should carry a status chip')
    if len(spec['title']) > 60:
        w.append(f"title is {len(spec['title'])} characters; consider shortening ({resolved['title_style']})")
    w.append(f"INFO title style for purpose '{resolved['brief']['purpose']}': {resolved['title_style']}")
    w.append('INFO manual tests: 10-second comprehension; is the main evidence the first thing the eye lands on; '
             'can the viewer say WHERE this happens; are data/assumptions/uncertainty shown honestly; readable at projector size')
    return w
