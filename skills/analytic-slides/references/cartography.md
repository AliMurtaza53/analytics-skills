# Cartography decisions (context-dependent, not a fixed style)

| Element | Rule |
|---|---|
| Basemap | Choose by analytical purpose. `esri_gray` is the default for overlays; `osm` for road/rail/port network context; `esri_imagery` (alpha ~0.45) for terminal footprints and land use; `none` for abstract geometry. Overlay analytic layers as vectors; the basemap is context only. NOAA ENC (channels, depth) is planned, not implemented. |
| Geographic labels | Label essential places first (water bodies, the city, the port) before technical objects. |
| Extent | Enough context to see where the phenomenon sits; a tight zoom needs an inset or a second map. |
| Projection | Maps render in Web Mercator for tile alignment (fine for presentation). For distance/area analysis use an appropriate projected CRS (UTM/State Plane) in the analysis; never read measurements off the slide. The scale bar is corrected for latitude. |
| Legend | Only symbols needed to read the map. Full mode groups by kind: official features / analytical constructs / observations. Simple mode shows only layers with `simple_label`. Default position lower-left above the scale bar (`legend_loc`, `legend_anchor` override). |
| Scale bar | Include when distance matters (default on); `scale_bar: false` otherwise. |
| North arrow | Off by default (north-up maps); `north_arrow: true` only for rotated maps. |
| Coordinates | Degree ticks for geometry review and specialists; omitted for general audiences (`coords` overrides). |
| Inset | `inset: {bbox: [w,s,e,n], size: 1.9}` adds an orientation map with the main extent outlined, for audiences who need to know where this is. |
| Color | Semantic consistency across the deck: an object keeps its color and badge number on every slide. Colorblind-checked palette; vermillion is reserved for status and gates. |
| Labels | Hierarchy and collision avoidance; do not label everything. Numbered badges replace long labels; the register explains them. |
