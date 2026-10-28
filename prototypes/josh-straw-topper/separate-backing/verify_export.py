"""Verify immutable geometry and real Bambu load/save assignments."""
from pathlib import Path
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
from export_bambu import mesh_digest
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PROD='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def archive(p):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  return {n:z.read(n) for n in z.namelist()}
def assignments(es):
 r=E.fromstring(es['Metadata/model_settings.config']);c=json.loads(es['Metadata/project_settings.config'])
 a={}
 for part in r.findall('object/part'):
  d={m.get('key'):m.get('value') for m in part.findall('metadata')}
  a[d['name']]=int(d['extruder'])
 return a,c

def leaves(es):
 roots={p:E.fromstring(data) for p,data in es.items() if p.endswith('.model')}
 lookup={(p,o.get('id')):o for p,r in roots.items() for o in r.findall('m:resources/m:object',NS)}
 def mat(text):
  m=np.eye(4)
  if text:
   a=np.array(list(map(float,text.split()))).reshape(4,3).T;m[:3,:]=a
  return m
 result=[]
 def walk(path,ident,t):
  o=lookup[(path,ident)];vs=o.findall('m:mesh/m:vertices/m:vertex',NS)
  if vs:
   v=np.array([[float(x.get(a)) for a in ['x','y','z']] for x in vs]);v=(np.c_[v,np.ones(len(v))]@t.T)[:,:3]
   f=np.array([[int(x.get(a)) for a in ['v1','v2','v3']] for x in o.findall('m:mesh/m:triangles/m:triangle',NS)])
   result.append((v,f));return
  for c in o.findall('m:components/m:component',NS):walk(c.get(PROD+'path',path).lstrip('/'),c.get('objectid'),t@mat(c.get('transform')))
 for item in roots['3D/3dmodel.model'].findall('m:build/m:item',NS):walk('3D/3dmodel.model',item.get('objectid'),mat(item.get('transform')))
 return result

def verify(source,corrected,roundtrip):
 original=archive(source);fixed=archive(corrected);native=archive(roundtrip)
 digest=mesh_digest(E.fromstring(original['3D/3dmodel.model']))
 assert digest==mesh_digest(E.fromstring(fixed['3D/3dmodel.model']))
 expected={'Backing':1,'White_Artwork':1,'Black_Artwork':2,'Red_Artwork':3}
 fa,fc=assignments(fixed);na,nc=assignments(native)
 assert fa==na==expected
 assert fc['filament_colour']==nc['filament_colour']==['#FFFFFF','#020202','#F20512']
 assert fc['nozzle_diameter']==['0.4'] and fc['printer_model']=='Bambu Lab P1S'
 assert len(fc['inherits_group'])==len(fc['filament_colour'])+2
 assert fc['filament_self_index']==['1','2','3']
 assert len(fc['filament_extruder_variant'])==len(fc['filament_self_index'])
 for key in ['filament_map','filament_map_2','filament_nozzle_map','filament_volume_map']:
  assert len(fc[key])==3
 before=leaves(fixed);after=leaves(native);assert len(before)==len(after)==4
 errors=[]
 for (v,f),(nv,nf) in zip(before,after):
  assert v.shape==nv.shape and np.array_equal(f,nf)
  error=float(abs(v-nv).max());errors.append(error);assert error<0.00001
 report={'geometry_digest':digest,'original_mesh_arrays_exactly_preserved':True,'bambu_roundtrip_part_assignments':na,'bambu_roundtrip_palette':nc['filament_colour'],'native_save_max_coordinate_roundoff_mm':max(errors),'triangle_counts':[len(f) for v,f in before],'printer':'Bambu Lab P1S 0.4 nozzle','source_sha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'corrected_sha256':hashlib.sha256(Path(corrected).read_bytes()).hexdigest()}
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('corrected',type=Path);p.add_argument('roundtrip',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();r=verify(a.source,a.corrected,a.roundtrip);a.report.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
