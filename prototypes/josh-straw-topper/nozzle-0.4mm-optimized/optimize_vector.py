from pathlib import Path
import json
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
from analyze_artwork import polygons,raster,metrics
OUT=Path(__file__).parent
original={name:shapely.from_wkb((OUT/f'original-{name}.wkb').read_bytes()) for name in ['White_Artwork','Black_Artwork','Red_Artwork']}
footprint=unary_union(list(original.values()))
changes=[]

def adjusted(name,g):
 result=[]
 for i,p in enumerate(polygons(g)):
  circle=shapely.maximum_inscribed_circle(p,tolerance=.005)
  a,b=list(circle.coords);width=2*np.linalg.norm(np.array(a)-b)
  if p.area<.04 and width<.34:
   changes.append({'color':name,'component':i,'action':'absorb_unprintable_speck','area_mm2':p.area,'max_width_mm':float(width)})
   continue
  delta=max(0,(.44-width)/2) if width<.40 else 0
  delta=min(delta,.17)
  # Uniform widening of whole deficient components keeps smooth consistent
  # outlines; avoid local skeleton circles that can create bulbous letter edges.
  q=p.buffer(delta,quad_segs=12) if delta else p
  q=q.buffer(.035,quad_segs=8).buffer(-.035,quad_segs=8)
  q=q.buffer(-.025,quad_segs=8).buffer(.025,quad_segs=8)
  q=q.simplify(.008,preserve_topology=True)
  if delta:changes.append({'color':name,'component':i,'action':'uniform_stroke_widen','offset_mm':float(delta),'max_width_before_mm':float(width)})
  result.append(q)
 return unary_union(result).intersection(footprint)

white=adjusted('White_Artwork',original['White_Artwork'])
red=adjusted('Red_Artwork',original['Red_Artwork']).difference(white)
# Retain small black letter counters by enlarging them rather than filling them.
black_protected=[]
for p in polygons(original['Black_Artwork']):
 if p.area<.04:continue
 line=shapely.maximum_inscribed_circle(p,tolerance=.005);a,b=line.coords;width=2*np.linalg.norm(np.array(a)-b)
 if width<.40:
  q=p.buffer(min(.17,(.44-width)/2),quad_segs=12).intersection(footprint)
  black_protected.append(q)
  changes.append({'color':'Black_Artwork','action':'enlarge_small_counter','offset_mm':float(min(.17,(.44-width)/2))})
if black_protected:
 reserve=unary_union(black_protected);white=white.difference(reserve);red=red.difference(reserve)
black=footprint.difference(unary_union([white,red]))
# Absorb sub-printable black fragments created at correction intersections.
for p in polygons(black):
 line=shapely.maximum_inscribed_circle(p,tolerance=.005);a,b=line.coords
 width=2*np.linalg.norm(np.array(a)-b)
 if p.area>=.04 and width>=.34:continue
 rim=p.buffer(.035)
 if rim.intersection(white).area>=rim.intersection(red).area:white=unary_union([white,p])
 else:red=unary_union([red,p])
 changes.append({'color':'Black_Artwork','action':'absorb_unprintable_speck','area_mm2':p.area})
black=footprint.difference(unary_union([white,red]))
result={'White_Artwork':white,'Black_Artwork':black,'Red_Artwork':red}
xs,ys,oldmasks=raster(original);_,_,newmasks=raster(result)
for name,g in result.items():(OUT/f'optimized-{name}.wkb').write_bytes(g.wkb)
np.savez_compressed(OUT/'optimized-masks.npz',xs=xs,ys=ys,**newmasks)
report={'method':'Vector component stroke widening, sub-nozzle contour cleanup, protected letter counters, shared color partition','analysis_grid_mm':.025,'nominal_line_mm':.42,'arachne_min_bead_mm':.34,'correction_max_offset_mm':.17,'contour_simplification_mm':.008,'speck_area_threshold_mm2':.04,'changes':changes,'before':metrics(oldmasks,original),'after':metrics(newmasks,result),'color_changed_area_mm2':float(sum(original[n].symmetric_difference(result[n]).area for n in original)/2),'total_face_area_mm2':footprint.area}
(OUT/'optimization-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['changes','before']},indent=2))
