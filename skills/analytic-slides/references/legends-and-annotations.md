# Legends and annotations

- Distinguish **observations** (AIS reports, sensor data), **analytical constructs** (buffers, gates, extraction windows) and **official features** (published waterway network, charted channel). Set `kind` on each layer (`observation` | `construct` | `official`); the full legend groups by it. This is scientific integrity, not decoration.
- Technical-reviewer legend: AIS extraction boundary; 500 m channel corridor; passage counting gate; AIS position report. Policy legend: "Port region", "Navigation channel" (`simple_label`).
- Annotation density follows depth: introductory = 2-3 one-sentence callouts; advanced = full register.
- Callouts: numbered to match map badges; short leader lines; at most 2 lines at 12-14 pt; place cards in free space beside the map, not on data. Auto-generated callouts come from register entries that have a badge and use their `Use` text.
- Badge numbers/letters carry identity; color is redundant, never the only cue.
- A "Not" line (what the object is not) is mandatory in geometry review.
