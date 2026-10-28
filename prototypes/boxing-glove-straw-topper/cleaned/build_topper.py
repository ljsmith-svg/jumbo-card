"""Build a physical-test assembly from the original JPEG embedded in the supplied SVG.
No generated mockup, cropped SVG page, or Josh geometry is used.
"""
from pathlib import Path
import json, zipfile, xml.etree.ElementTree as E
from itertools import combinations
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from skimage.measure import find_contours
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import make_valid
from shapely.affinity import affine_transform
import manifold3d as mf
import trimesh

P=Path(__file__).parent
def polygons(g):
 if g.geom_type=='Polygon': return [g] if g.area>1e-8 else []
 return [p for c in getattr(g,'geoms',[]) for p in polygons(c)]
im=np.asarray(Image.open(P/'source.jpg').convert('RGB')).astype(float)
fg=(im.max(2)-im.min(2)>40)|(im.mean(2)<150)
lab,n=nd.label(fg);counts=np.bincount(lab.ravel());counts[0]=0
fg=lab==counts.argmax()
bodymask=nd.binary_fill_holes(fg)
ys,xs=np.where(bodymask);xmin,xmax,ymin,ymax=xs.min()-.5,xs.max()+.5,ys.min()-.5,ys.max()+.5
scale=35/(xmax-xmin)
def region(mask):
 # XOR contours preserves nested holes, unlike joining filled loops.
 g=Polygon()
 for c in find_contours(np.pad(mask,1),.5):
  xy=np.column_stack((c[:,1]-1,c[:,0]-1))
  p=make_valid(Polygon(xy))
  if p.area*scale*scale<.006:continue
  g=g.symmetric_difference(p)
 return make_valid(affine_transform(g,[scale,0,0,-scale,-xmin*scale,ymax*scale]))
body=unary_union(polygons(region(bodymask))).simplify(.008,preserve_topology=True)
# RGB nearest-color quantization removes JPEG shades without inventing colors.
palette=np.array([[2,2,2],[255,24,126],[248,163,199],[255,255,255]])
labels=np.argmin(((im[:,:,None,:]-palette[None,None,:,:])**2).sum(3),axis=2)
# Saturation distinguishes the two pink inks despite shading/compression in the JPEG.
sat=(im.max(2)-im.min(2))/np.maximum(im.max(2),1)
labels[(labels!=0)&(labels!=3)]=np.where(sat[(labels!=0)&(labels!=3)]>.67,1,2)
labels=nd.median_filter(labels,size=3)
# Each region enclosed by black linework is one flat ink color. Classifying its
# median removes pale JPEG fringes inside otherwise solid hot-pink regions.
islands,n=nd.label((labels!=0)&bodymask)
for i,slice_ in enumerate(nd.find_objects(islands),1):
 if slice_ is None:continue
 local=islands[slice_]==i;rgb=np.median(im[slice_][local],axis=0)
 saturation=(rgb.max()-rgb.min())/max(rgb.max(),1)
 ink=3 if saturation<.15 and rgb.mean()>200 else (1 if saturation>.67 else 2)
 sub=labels[slice_];sub[local]=ink
names=['Black_Artwork','Hot_Pink_Artwork','Light_Pink_Artwork','White_Detail']
regions={}
for i,name in enumerate(names):
 g=region((labels==i)&bodymask).intersection(body)
 # Remove only sub-resolution JPEG specks; remaining space joins the black linework.
 g=unary_union([p for p in polygons(g) if p.area>=.006])
 regions[name]=g.simplify(.008,preserve_topology=True)
from artwork_cleanup import clean_outlined_colors
original_regions=dict(regions)
regions,cleanup=clean_outlined_colors(regions,body)
(P/'cleanup-report.json').write_text(json.dumps(cleanup,indent=2))
def solid(g,height,z=0):
 ss=[]
 for p in polygons(make_valid(g)):
  rings=[np.asarray(p.exterior.coords)[:-1]]+[np.asarray(r.coords)[:-1] for r in p.interiors]
  m=mf.CrossSection(rings,mf.FillRule.EvenOdd).extrude(height).translate([0,0,z])
  if not m.is_empty():ss.append(m)
 return mf.Manifold.batch_boolean(ss,mf.OpType.Add)
front=solid(body,2,14)
white=solid(regions['White_Detail'],2,14)^front
light=(solid(regions['Light_Pink_Artwork'],2,14)^front)-white
hot=(solid(regions['Hot_Pink_Artwork'],2,14)^front)-(white+light)
black=front-(white+light+hot)
# One centered, constant-diameter passage, in the backing plane, parallel to Y.
cx=17.5; cy=body.bounds[3]/2
cutter=mf.Manifold.cylinder(120,5,5,256,True).rotate([90,0,0]).translate([cx,cy,7])
back=solid(body,14)-cutter
parts={'Backing':back,'Black_Artwork':black,'Hot_Pink_Artwork':hot,'Light_Pink_Artwork':light,'White_Detail':white}
assert len(back.decompose())==1,'Backing must be continuous'
out=P/'geometry';out.mkdir(exist_ok=True)
report={'source':'Original JPEG embedded in uploaded SVG; full uncropped artwork','width_mm':35,'height_mm':body.bounds[3],'backing_z_mm':[0,14],'artwork_z_mm':[14,16],'channel_nominal_diameter_mm':10,'added_clearance_mm':0,'channel_polygon_flat_to_flat_mm':10*np.cos(np.pi/256),'channel_axis':'Y','channel_center_x_mm':cx,'channel_center_z_mm':7,'front_rear_nominal_walls_mm':2,'parts':{},'overlap_mm3':{},'physical_test':'Not performed','minimum_wall_scope':'2mm front/rear nominal walls. Irregular entrance/exit rims are not certified to have 2mm all around.','artwork_preparation':'Color quantization with 0.67 saturation split between pinks and 3-pixel median denoising; 0.008mm contour simplification; specks/holes below 0.006mm2 removed. Fine details not uniformly widened.'}
report['edge_cleanup']=cleanup
meshes={}
for name,m in parts.items():
 assert m.status()==mf.Error.NoError
 raw=m.to_mesh64();t=trimesh.Trimesh(vertices=np.asarray(raw.vert_properties)[:,:3],faces=np.asarray(raw.tri_verts),process=False)
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
 t.export(out/(name+'.stl'));meshes[name]=t
 report['parts'][name]={'volume_mm3':float(t.volume),'triangles':len(t.faces),'watertight':True,'components':len(m.decompose()),'bounds_mm':t.bounds.tolist()}
for (a,ma),(b,mb) in combinations(parts.items(),2):
 v=abs((ma^mb).volume());assert v<1e-7,(a,b,v);report['overlap_mm3'][a+'/'+b]=v
assert abs((back^cutter).volume())<1e-7
assert abs((front-(white+light+hot+black)).volume())<1e-7
N='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',N)
def el(tag,attrs={},parent=None):
 return E.Element('{'+N+'}'+tag,attrs) if parent is None else E.SubElement(parent,'{'+N+'}'+tag,attrs)
r=el('model',{'unit':'millimeter'});res=el('resources',parent=r)
mat=el('basematerials',{'id':'1'},res)
colors=['#FFFFFFFF','#020202FF','#FF187EFF','#F8A3C7FF']
for name,col in zip(['White','Black','Hot pink','Light pink'],colors):el('base',{'name':name,'displaycolor':col},mat)
indices={'Backing':0,'Black_Artwork':1,'Hot_Pink_Artwork':2,'Light_Pink_Artwork':3,'White_Detail':0}
for i,(name,t) in enumerate(meshes.items(),2):
 o=el('object',{'id':str(i),'name':name,'type':'model','pid':'1','pindex':str(indices[name])},res)
 me=el('mesh',parent=o);vs=el('vertices',parent=me);ts=el('triangles',parent=me)
 for v in t.vertices:el('vertex',{k:f'{x:.9f}' for k,x in zip(['x','y','z'],v)},vs)
 for f in t.faces:el('triangle',{k:str(int(x)) for k,x in zip(['v1','v2','v3'],f)},ts)
assembly=el('object',{'id':'7','type':'model','name':'Boxing glove - separate backing and artwork'},res);cs=el('components',parent=assembly)
for i in range(2,7):el('component',{'objectid':str(i)},cs)
b=el('build',parent=r);el('item',{'objectid':'7'},b)
entries={'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>',
 '_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
entries['3D/3dmodel.model']=E.tostring(r,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(P/'Boxing-Glove-Core.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,v in entries.items():z.writestr(n,v)
(P/'geometry-validation.json').write_text(json.dumps(report,indent=2))
# Actual geometry-color diagram for inspection (not a generated mockup).
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch
fig,ax=plt.subplots(figsize=(7,9));ax.set_aspect('equal')
for name,col in [('Black_Artwork','#020202'),('Hot_Pink_Artwork','#FF187E'),('Light_Pink_Artwork','#F8A3C7'),('White_Detail','#FFFFFF')]:
 for p in polygons(body if name=='Black_Artwork' else regions[name]):
  from shapely.geometry.polygon import orient
  p=orient(p);rings=[p.exterior,*p.interiors];verts=[];codes=[]
  for ring in rings:
   c=np.asarray(ring.coords);verts.extend(c);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(c)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(verts,codes),facecolor=col,edgecolor='none'))
ax.set_xlim(-1,36);ax.set_ylim(-1,body.bounds[3]+1);ax.set_xlabel('Width (mm)');ax.set_ylabel('Height (mm)');ax.set_title('35 mm boxing-glove topper — source-derived artwork')
fig.savefig(P/'artwork-geometry-preview.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,8),layout='constrained')
for ax,title,rr in zip(axes,['Before cleanup','After cleanup'],[original_regions,regions]):
 ax.set_aspect('equal')
 for pp in polygons(body):
  xx,yy=pp.exterior.xy;ax.fill(xx,yy,color='white',edgecolor='#999999',linewidth=.6)
 for pp in polygons(rr['Light_Pink_Artwork']):
  from shapely.geometry.polygon import orient
  pp=orient(pp);vs=[];cs=[]
  for ring in [pp.exterior,*pp.interiors]:
   co=np.asarray(ring.coords);vs.extend(co);cs.extend([MP.MOVETO]+[MP.LINETO]*(len(co)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(vs,cs),facecolor='#F8A3C7',edgecolor='none'))
 ax.set_xlim(-1,36);ax.set_ylim(-1,body.bounds[3]+1);ax.set_title(title);ax.axis('off')
fig.suptitle('Light-pink component isolated on white backing — actual XY geometry')
fig.savefig(P/'light-pink-cleanup-comparison.png',dpi=220);plt.close(fig)
print(json.dumps(report,indent=2))
