from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,hashlib,shutil
import numpy as np
import shapely
from shapely.geometry import Polygon
import manifold3d as mf
import trimesh
from analyze_artwork import extract,polygons,SOURCE,NS

OUT=Path(__file__).parent
regions,original=extract()
optimized={name:shapely.from_wkb((OUT/f'optimized-{name}.wkb').read_bytes()) for name in regions}

def solid(g):
 parts=[]
 for p in polygons(g):
  rings=[np.asarray(p.exterior.coords)[:-1]]+[np.asarray(r.coords)[:-1] for r in p.interiors]
  s=mf.CrossSection(rings,mf.FillRule.EvenOdd).extrude(2).translate([0,0,14])
  if not s.is_empty():parts.append(s)
 return mf.Manifold.batch_boolean(parts,mf.OpType.Add)

front=original['White_Artwork']+original['Black_Artwork']+original['Red_Artwork']
white=solid(optimized['White_Artwork'])^front
red=(solid(optimized['Red_Artwork'])^front)-white
black=front-(white+red)
solids={'Backing':original['Backing'],'White_Artwork':white,'Black_Artwork':black,'Red_Artwork':red}

with zipfile.ZipFile(SOURCE) as z:entries={n:z.read(n) for n in z.namelist()}
r=E.fromstring(entries['3D/3dmodel.model']);core=NS['m'];E.register_namespace('',core)
def digest(mesh):return hashlib.sha256(json.dumps([(x.tag,sorted(x.attrib.items())) for x in mesh.iter()],sort_keys=True).encode()).hexdigest()
backing=r.find("m:resources/m:object[@name='Backing']/m:mesh",NS);before=digest(backing)
outgeom=OUT/'geometry';outgeom.mkdir(exist_ok=True)
report={'unchanged_backing_mesh_digest_before':before,'channel_nominal_mm':10,'clearance_mm':0,'body_thickness_mm':14,'artwork_height_mm':2,'overall_width_mm':35,'parts':{},'overlap_volume_mm3':{}}
for obj in r.findall('m:resources/m:object',NS):
 name=obj.get('name')
 if name not in solids:continue
 s=solids[name];assert s.status()==mf.Error.NoError
 if name=='Backing':
  if (OUT/'input/Backing.stl').exists():
   shutil.copy2(OUT/'input/Backing.stl',outgeom/'Backing.stl')
  else:
   raw=s.to_mesh64();trimesh.Trimesh(vertices=np.array(raw.vert_properties)[:,:3],faces=np.array(raw.tri_verts),process=False).export(outgeom/'Backing.stl')
 else:
  raw=s.to_mesh64();v=np.array(raw.vert_properties)[:,:3];f=np.array(raw.tri_verts)
  mesh=trimesh.Trimesh(vertices=v,faces=f,process=False);assert mesh.is_watertight and mesh.is_winding_consistent
  mesh.export(outgeom/f'{name}.stl')
  old=obj.find('m:mesh',NS);obj.remove(old)
  me=E.SubElement(obj,'{'+core+'}mesh');vs=E.SubElement(me,'{'+core+'}vertices');fs=E.SubElement(me,'{'+core+'}triangles')
  for point in v:E.SubElement(vs,'{'+core+'}vertex',{k:f'{x:.9f}' for k,x in zip(['x','y','z'],point)})
  for face in f:E.SubElement(fs,'{'+core+'}triangle',{k:str(int(x)) for k,x in zip(['v1','v2','v3'],face)})
 report['parts'][name]={'volume_mm3':s.volume(),'z_range_mm':[s.bounding_box()[2],s.bounding_box()[5]],'triangles':s.num_tri(),'watertight':True}
assert before==digest(backing)
report['unchanged_backing_mesh_digest_after']=digest(backing)
from itertools import combinations
for (a,ma),(b,mb) in combinations(solids.items(),2):
 volume=abs((ma^mb).volume());assert volume<1e-7,(a,b,volume);report['overlap_volume_mm3'][a+'/'+b]=volume
assert abs((front-(white+red+black)).volume())<1e-7
assert len(original['Backing'].decompose())==1
entries['3D/3dmodel.model']=E.tostring(r,encoding='utf-8',xml_declaration=True)
cfg=json.loads(entries['Metadata/project_settings.config'])
cfg['wall_generator']='arachne';cfg['different_settings_to_system'][0]='wall_generator'
# Calculated by official Bambu Studio 02.08.02.61 for this exact palette.
assert cfg['filament_colour']==['#FFFFFF','#020202','#F20512']
cfg['flush_volumes_matrix']=['0','186','353','663','0','499','679','194','0'];cfg['flush_volumes_vector']=['140']*6
assert len(cfg['flush_volumes_matrix'])==len(cfg['filament_colour'])**2==9
assert cfg['nozzle_diameter']==['0.4']
entries['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
config=E.fromstring(entries['Metadata/model_settings.config'])
for meta in config.findall('object/metadata'):
 if meta.get('key')=='name':meta.set('value','Josh - 0.4mm nozzle artwork')
for meta in config.findall('plate/metadata'):
 if meta.get('key')=='plater_name':meta.set('value','Josh 0.4mm optimized')
entries['Metadata/model_settings.config']=E.tostring(config,encoding='utf-8',xml_declaration=True)
name='Josh-35mm-04Nozzle-Optimized.3mf'
with zipfile.ZipFile(OUT/name,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in entries.items():z.writestr(n,b)
report['settings_changes']={'wall_generator':['classic','arachne'],'flush_volumes_matrix_count':[16,9],'flush_volumes_vector_count':[8,6]}
(OUT/'geometry-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
