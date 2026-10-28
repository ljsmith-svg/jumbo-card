from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
import numpy as np
import manifold3d as mf
p=Path(__file__).parent
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(p/'geometry/Josh-Four-Part-Core.3mf') as z:r=E.fromstring(z.read('3D/3dmodel.model'))
solids={}
for o in r.findall('m:resources/m:object',ns):
 vs=o.findall('m:mesh/m:vertices/m:vertex',ns)
 if not vs:continue
 vertices=np.array([[float(v.get(a)) for a in ['x','y','z']] for v in vs],dtype=np.float64)
 faces=np.array([[int(f.get(a)) for a in ['v1','v2','v3']] for f in o.findall('m:mesh/m:triangles/m:triangle',ns)],dtype=np.uint64)
 m=mf.Manifold(mf.Mesh64(vertices,faces));assert m.status()==mf.Error.NoError
 solids[o.get('name')]=m
 expect=[0,14] if o.get('name')=='Backing' else [14,16]
 assert np.allclose([vertices[:,2].min(),vertices[:,2].max()],expect,atol=1e-8)
assert set(solids)=={'Backing','White_Artwork','Black_Artwork','Red_Artwork'}
base=solids['Backing'];assert len(base.decompose())==1
rear=base.slice(.5);front=base.slice(13.5)
error=(rear-front).area()+(front-rear).area()
# Nine-decimal coordinate serialization and section interpolation produce
# sub-micron-squared residuals; a 1e-6 mm2 tolerance detects any artwork recess.
assert abs(error)<1e-6,'Backing front/rear footprint differs; unexpected detailed recesses'
from itertools import combinations
pairs={a+'/'+b:abs((ma^mb).volume()) for (a,ma),(b,mb) in combinations(solids.items(),2)}
assert max(pairs.values())<1e-7
report={'one_continuous_backing':True,'backing_thickness_mm':14,'all_artwork_z_mm':[14,16],'backing_front_rear_cross_section_difference_mm2':error,'cross_section_numeric_tolerance_mm2':1e-6,'artwork_in_backing_volume':False,'pairwise_overlap_mm3':pairs,'overlap_numeric_tolerance_mm3':1e-7}
(p/'construction-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
