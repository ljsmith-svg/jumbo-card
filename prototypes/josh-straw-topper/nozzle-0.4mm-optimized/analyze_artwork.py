from pathlib import Path
import os,json,zipfile,xml.etree.ElementTree as E
import numpy as np
import manifold3d as mf
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

OUT=Path(__file__).parent
SOURCE=Path(os.environ.get('JOSH_SOURCE_3MF',str(OUT/'input/Josh-35mm-Separate-Backing.3mf')))
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PIXEL=.025;MIN_WIDTH=.42

def polygons(g):
 if g.geom_type=='Polygon':return [g] if g.area>1e-12 else []
 return [p for x in getattr(g,'geoms',[]) for p in polygons(x)]

def extract():
 with zipfile.ZipFile(SOURCE) as z:root=E.fromstring(z.read('3D/3dmodel.model'))
 regions={};solids={}
 for o in root.findall('m:resources/m:object',NS):
  vs=o.findall('m:mesh/m:vertices/m:vertex',NS)
  if not vs:continue
  v=np.asarray([[float(x.get(k)) for k in ['x','y','z']] for x in vs],dtype=np.float64)
  f=np.asarray([[int(x.get(k)) for k in ['v1','v2','v3']] for x in o.findall('m:mesh/m:triangles/m:triangle',NS)],dtype=np.uint64)
  s=mf.Manifold(mf.Mesh64(v,f));assert s.status()==mf.Error.NoError
  name=o.get('name');solids[name]=s
  if name=='Backing':continue
  region=Polygon()
  for ring in s.slice(15).to_polygons():
   region=region.symmetric_difference(Polygon(ring))
  region=shapely.make_valid(region)
  assert abs(region.area-s.volume()/2)<1e-5,(name,region.area,s.volume()/2)
  regions[name]=region
 return regions,solids

def raster(regions):
 maxy=max(g.bounds[3] for g in regions.values())
 xs=np.arange(-.4,35.4,PIXEL)+PIXEL/2;ys=np.arange(-.4,maxy+.4,PIXEL)+PIXEL/2
 xx,yy=np.meshgrid(xs,ys)
 masks={name:shapely.contains_xy(g,xx,yy) for name,g in regions.items()}
 return xs,ys,masks

def metrics(masks,regions):
 report={}
 for name,mask in masks.items():
  distance=ndi.distance_transform_edt(mask)*PIXEL
  skel=skeletonize(mask)
  widths=2*distance[skel]
  labels,n=ndi.label(mask,structure=np.ones((3,3)))
  max_widths=2*ndi.maximum(distance,labels,index=np.arange(1,n+1))
  report[name]={'area_mm2':regions[name].area,'vector_components':len(polygons(regions[name])),'raster_islands':n,'islands_max_width_below_042mm':int(np.sum(max_widths<MIN_WIDTH)),'skeleton_length_below_042mm_mm':float(np.count_nonzero(widths<MIN_WIDTH)*PIXEL),'skeleton_width_percentiles_mm':np.percentile(widths,[10,50,90]).tolist()}
 return report

if __name__=='__main__':
 regions,solids=extract()
 for name,g in regions.items():(OUT/f'original-{name}.wkb').write_bytes(g.wkb)
 xs,ys,masks=raster(regions)
 np.savez_compressed(OUT/'original-masks.npz',xs=xs,ys=ys,**masks)
 report=metrics(masks,regions);(OUT/'original-feature-analysis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
