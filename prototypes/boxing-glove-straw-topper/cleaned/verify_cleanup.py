"""Inspect actual exported meshes, not just color previews or cleanup metadata."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,hashlib
import numpy as np
import manifold3d as mf
from shapely.geometry import Polygon
from artwork_cleanup import polygons
P=Path(__file__).parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def read(path):
 with zipfile.ZipFile(path) as z:r=E.fromstring(z.read('3D/3dmodel.model'))
 solids={};digests={}
 for o in r.findall('m:resources/m:object',NS):
  me=o.find('m:mesh',NS)
  if me is None:continue
  name=o.get('name');digests[name]=hashlib.sha256(json.dumps([(e.tag,sorted(e.attrib.items())) for e in me.iter()],sort_keys=True).encode()).hexdigest()
  v=np.asarray([[float(x.get(k)) for k in ['x','y','z']] for x in me.findall('m:vertices/m:vertex',NS)],dtype=np.float64)
  f=np.asarray([[int(x.get(k)) for k in ['v1','v2','v3']] for x in me.findall('m:triangles/m:triangle',NS)],dtype=np.uint64)
  solids[name]=mf.Manifold(mf.Mesh64(v,f));assert solids[name].status()==mf.Error.NoError
 return solids,digests
def plane(s,z):
 g=Polygon()
 for ring in s.slice(z).to_polygons():g=g.symmetric_difference(Polygon(ring))
 return g
old,od=read(P.parent/'boxing-glove-topper/Boxing-Glove-35mm-P1S.3mf')
new,nd=read(P/'Boxing-Glove-35mm-Cleaned.3mf')
assert od['Backing']==nd['Backing'],'Backing mesh must remain exactly unchanged'
outline=plane(new['Backing'],.5);report={'backing_mesh_exactly_unchanged':True,'backing_digest':nd['Backing'],'channel_and_dimensions_preserved':True,'colors':{}}
for name in ['Light_Pink_Artwork','Hot_Pink_Artwork']:
 g=plane(new[name],15);oldg=plane(old[name],15)
 distance=g.distance(outline.exterior);assert distance>=.20-1e-6,(name,distance)
 added=g.difference(oldg).area;assert added<1e-6,'Cleanup must not add pink'
 report['colors'][name]={'components_before':len(polygons(oldg)),'components_after':len(polygons(g)),'actual_mesh_edge_clearance_mm':distance,'added_pink_area_mm2':added,'removed_pink_area_mm2':oldg.difference(g).area}
assert report['colors']['Light_Pink_Artwork']['components_after']<report['colors']['Light_Pink_Artwork']['components_before']
assert report['colors']['Hot_Pink_Artwork']['removed_pink_area_mm2']<1e-6
assert od['White_Detail']==nd['White_Detail']
report['white_detail_mesh_exactly_unchanged']=True
(P/'cleanup-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
