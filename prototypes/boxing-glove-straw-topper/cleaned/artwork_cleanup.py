"""Opt-in cleanup for black-outlined artwork; never apply to unoutlined designs.
All dimensions refer to final print size. Log edits and enforce the edge guard.
"""
from shapely import maximum_inscribed_circle
from shapely.geometry import Polygon
from shapely.ops import unary_union

def polygons(g):
 if g.geom_type=='Polygon':return [g] if not g.is_empty else []
 return [p for c in getattr(g,'geoms',[]) for p in polygons(c)]

def clean_outlined_colors(regions, silhouette):
 guard=.20
 interior=silhouette.buffer(-guard)
 cleaned=dict(regions);report={'policy':'Black-outlined boxing-glove art only','outer_black_guard_mm':guard,'light_pink_minimum_component_max_width_mm':.30,'light_pink_opening_radius_mm':.06,'colors':{}}
 for name in ['Light_Pink_Artwork','Hot_Pink_Artwork']:
  before=regions[name];g=before.intersection(interior);removed=[]
  before_count=len(polygons(before));edge_removed=before.difference(g).area
  if name=='Light_Pink_Artwork':
   # Opening removes needle-like fringes. Whole-region removal targets narrow
   # isolated slivers, not butterfly dots (which belong to the hot-pink ink).
   g=g.buffer(-.06).buffer(.06).intersection(g)
   kept=[]
   for p in polygons(g):
    width=2*maximum_inscribed_circle(p,tolerance=.003).length
    if width<.30:removed.append({'area_mm2':p.area,'maximum_width_mm':width,'bounds_mm':list(p.bounds)})
    else:kept.append(p)
   g=unary_union(kept) if kept else Polygon()
  cleaned[name]=g
  assert g.difference(interior.buffer(1e-8)).area<1e-8
  report['colors'][name]={'area_before_mm2':before.area,'area_after_mm2':g.area,'removed_area_mm2':before.difference(g).area,'area_removed_by_edge_guard_mm2':edge_removed,'component_count_before':before_count,'component_count_after':len(polygons(g)),'removed_narrow_components':removed,'remaining_edge_guard_violations':0,'minimum_distance_to_exterior_mm':g.distance(silhouette.exterior) if silhouette.geom_type=='Polygon' else None}
 return cleaned,report
