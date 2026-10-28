from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
import numpy as np
from validation_helpers import archive,assignments,leaves,NS
from analyze_artwork import SOURCE
p=Path(__file__).parent
original=archive(SOURCE);fixed=archive(p/'Josh-35mm-04Nozzle-Optimized.3mf')
native=archive('/tmp/bambu-export-investigation/nozzle-04/optimized/optimized-sliced.3mf')
def backing_digest(es):
 r=E.fromstring(es['3D/3dmodel.model']);m=r.find("m:resources/m:object[@name='Backing']/m:mesh",NS)
 return hashlib.sha256(json.dumps([(x.tag,sorted(x.attrib.items())) for x in m.iter()],sort_keys=True).encode()).hexdigest()
assert backing_digest(original)==backing_digest(fixed)
expected={'Backing':1,'White_Artwork':1,'Black_Artwork':2,'Red_Artwork':3}
a,c=assignments(fixed);na,nc=assignments(native)
assert a==na==expected
assert c['filament_colour']==nc['filament_colour']==['#FFFFFF','#020202','#F20512']
assert c['wall_generator']==nc['wall_generator']=='arachne'
assert len(c['flush_volumes_matrix'])==len(nc['flush_volumes_matrix'])==9
assert len(c['flush_volumes_vector'])==6
assert c['nozzle_diameter']==nc['nozzle_diameter']==['0.4']
actual=leaves(fixed);roundtrip=leaves(native);assert len(actual)==len(roundtrip)==4
errors=[]
for (v,f),(nv,nf) in zip(actual,roundtrip):
 assert v.shape==nv.shape and np.array_equal(f,nf)
 error=float(np.max(abs(v-nv)));assert error<1e-5;errors.append(error)
result=json.loads(Path('/tmp/bambu-export-investigation/nozzle-04/optimized/result.json').read_text())
assert result['return_code']==0 and len(result['sliced_plates'])==1
filaments=result['sliced_plates'][0]['filaments']
assert {f['id'] for f in filaments}=={1,2,3} and all(f['main_used_g']>0 for f in filaments)
paths=json.loads((p/'toolpath-analysis.json').read_text())
before=sum(d['path_length_below_034mm_mm'] for d in paths['before'].values());after=sum(d['path_length_below_034mm_mm'] for d in paths['after'].values())
assert after<before
report={'backing_mesh_exactly_unchanged':True,'backing_mesh_sha256':backing_digest(fixed),'channel_nominal_mm':10,'clearance_mm':0,'four_parts_and_assignments':a,'wall_generator':'arachne','nozzle_mm':.4,'bambu_slice_return_code':result['return_code'],'bambu_version':'02.08.02.61','all_three_filaments_used':True,'top_layer_paths_below_034mm_before_mm':before,'top_layer_paths_below_034mm_after_mm':after,'thin_path_length_reduction_percent':100*(1-after/before),'native_reexport_max_coordinate_roundoff_mm':max(errors),'physical_print_test':'not performed','delivery_sha256':hashlib.sha256((p/'Josh-35mm-04Nozzle-Optimized.3mf').read_bytes()).hexdigest()}
(p/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
