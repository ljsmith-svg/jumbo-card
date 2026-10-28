from pathlib import Path
import xml.etree.ElementTree as ET
import math,json,zipfile
import numpy as np
from svgpathtools import parse_path
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely import make_valid
from shapely.ops import unary_union
from shapely.affinity import affine_transform
import trimesh
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--hole',type=int,choices=[10],default=10)
args=parser.parse_args()
HOLE=float(args.hole)
OUT=Path(__file__).parent / 'geometry'
OUT.mkdir(exist_ok=True)
SRC=Path(__file__).parent / 'source' / 'Josh.svg'
root=ET.parse(SRC).getroot()
def polygons(g):
 if g.geom_type=='Polygon':return [g] if g.area>1e-9 else []
 return [p for c in getattr(g,'geoms',[]) for p in polygons(c)]
def shape(d):
 result=[]
 for sub in parse_path(d).continuous_subpaths():
  pts=[]
  for seg in sub:
   n=max(2,math.ceil(seg.length(error=1e-4)/0.7))
   pts.extend((seg.point(i/n).real,seg.point(i/n).imag) for i in range(n))
  if len(pts)>2:result.extend(polygons(make_valid(Polygon(pts))))
 return unary_union(result)
raw=[shape(e.attrib['d']) for e in root]
# Path 0 is the exterior white background. Path 1 is the enclosing black silhouette.
bounds=raw[1].bounds; scale=35.0/(bounds[2]-bounds[0])
def transform(g):return affine_transform(g,[scale,0,0,-scale,-bounds[0]*scale,bounds[3]*scale])
body2=transform(raw[1]); body2=unary_union([Polygon(p.exterior) for p in polygons(body2)])
regions={c:Polygon() for c in ['#ffffff','#020202','#f20512']}
for e,g in zip(list(root)[1:],raw[1:]):
 g=transform(g).intersection(body2)
 for c in regions:regions[c]=regions[c].difference(g)
 c=e.attrib['fill'];regions[c]=unary_union([regions[c],g])
import manifold3d as mf

def solid(g,height,z=0):
    solids=[]
    # All planar boundaries come from the same original SVG partition. No independent
    # polygon simplification or small-feature area threshold is applied here.
    for p in polygons(g):
        rings=[np.asarray(p.exterior.coords)[:-1]]+[np.asarray(r.coords)[:-1] for r in p.interiors]
        m=mf.CrossSection(rings,mf.FillRule.EvenOdd).extrude(height).translate([0,0,z])
        if not m.is_empty():solids.append(m)
    return mf.Manifold.batch_boolean(solids,mf.OpType.Add)

def mesh(m):
    rawmesh=m.to_mesh64()
    return trimesh.Trimesh(vertices=np.array(rawmesh.vert_properties)[:,:3],faces=np.array(rawmesh.tri_verts),process=False)

hole_x=35.0*35.0/63.5
cutter=mf.Manifold.cylinder(100,HOLE/2,HOLE/2,192,True).rotate([90,0,0]).translate([hole_x,body2.bounds[3]/2,7])
backing=solid(body2,14)-cutter
front=solid(body2,2,14)
# Assign visible SVG colors; final subtraction removes numeric sliver intersections
# and makes the three artwork bodies an exact partition of the common front layer.
red=solid(regions['#f20512'],2,14) ^ front
black=(solid(regions['#020202'],2,14) ^ front)-red
white=front-(red+black)
solids={'Backing':backing,'White_Artwork':white,'Black_Artwork':black,'Red_Artwork':red}
parts={name:mesh(m) for name,m in solids.items()}
report={'width_mm':35,'height_mm':float(body2.bounds[3]),'backing_z_mm':[0,14],'artwork_z_mm':[14,16],'channel_diameter_mm':HOLE,'added_clearance_mm':0,'channel_center_x_mm':hole_x,'channel_center_z_mm':7,'nominal_front_rear_walls_mm':(14-HOLE)/2,'parts':{},'pairwise_overlap_mm3':{}}
assert len(backing.decompose())==1,'Backing must be one continuous solid'
for name,m in solids.items():
    assert m.status()==mf.Error.NoError
    t=parts[name];assert t.is_watertight and t.is_winding_consistent and t.volume>0
    t.export(OUT/f'{name}.stl')
    report['parts'][name]={'z_range_mm':t.bounds[:,2].tolist(),'volume_mm3':float(t.volume),'triangles':len(t.faces),'watertight':True,'connected_components':len(m.decompose())}
from itertools import combinations
for (a,ma),(b,mb) in combinations(solids.items(),2):
    v=abs((ma^mb).volume());report['pairwise_overlap_mm3'][a+' / '+b]=v
    assert v<1e-7,(a,b,v)
assert abs((front-(red+black+white)).volume())<1e-7
assert abs(((red+black+white)-front).volume())<1e-7
assert abs((backing^cutter).volume())<1e-7
# Legacy-front reference is compared only in XY; its black inlay is deliberately
# replaced with black artwork wholly above the continuous backing.
report['artwork_partition_volume_error_mm3']=abs(front.volume()-red.volume()-black.volume()-white.volume())
report['backing_components']=len(backing.decompose())
report['bore_intersection_volume_mm3']=abs((backing^cutter).volume())
report['minimum_wall_scope']='Front/rear nominal walls are 2mm. Full irregular entrance/exit wall analysis and physical fit remain required.'

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
def el(tag,attrs=None,parent=None):
    return ET.Element('{'+NS+'}'+tag,attrs or {}) if parent is None else ET.SubElement(parent,'{'+NS+'}'+tag,attrs or {})
model=el('model',{'unit':'millimeter'});res=el('resources',parent=model)
mat=el('basematerials',{'id':'1'},res)
for name,col in [('White','#FFFFFFFF'),('Black','#020202FF'),('Red','#F20512FF')]:el('base',{'name':name,'displaycolor':col},mat)
for index,(name,m) in enumerate(parts.items(),2):
    color={'Backing':0,'White_Artwork':0,'Black_Artwork':1,'Red_Artwork':2}[name]
    obj=el('object',{'id':str(index),'name':name,'type':'model','pid':'1','pindex':str(color)},res)
    me=el('mesh',parent=obj);vs=el('vertices',parent=me);fs=el('triangles',parent=me)
    for v in m.vertices:el('vertex',{k:f'{x:.9f}' for k,x in zip(['x','y','z'],v)},vs)
    for f in m.faces:el('triangle',{k:str(int(x)) for k,x in zip(['v1','v2','v3'],f)},fs)
assembly=el('object',{'id':'6','type':'model','name':'Josh - four separate parts'},res);cs=el('components',parent=assembly)
for ident in range(2,6):el('component',{'objectid':str(ident)},cs)
build=el('build',parent=model);el('item',{'objectid':'6'},build)
with zipfile.ZipFile(OUT/'Josh-Four-Part-Core.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
(OUT/'geometry-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
