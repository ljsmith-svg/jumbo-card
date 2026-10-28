from pathlib import Path
import json,hashlib
import numpy as np
from validation_helpers import archive,assignments,leaves
P=Path(__file__).parent
f=P/'Boxing-Glove-35mm-P1S.3mf'
source=archive(f);native=archive('/tmp/bambu-export-investigation/boxing-glove/final/native-sliced.3mf')
a,c=assignments(source);b,d=assignments(native)
expected={'Backing':1,'Black_Artwork':2,'Hot_Pink_Artwork':3,'Light_Pink_Artwork':4,'White_Detail':1}
assert a==b==expected
assert c['filament_colour']==d['filament_colour']==['#FFFFFF','#020202','#FF187E','#F8A3C7']
assert len(c['flush_volumes_matrix'])==len(d['flush_volumes_matrix'])==16
assert len(c['inherits_group'])==len(c['different_settings_to_system'])==6
assert c['wall_generator']==d['wall_generator']=='arachne'
assert c['nozzle_diameter']==d['nozzle_diameter']==['0.4']
src=leaves(source);saved=leaves(native);assert len(src)==len(saved)==5
errors=[]
for (v,fcs),(vv,ff) in zip(src,saved):
 assert v.shape==vv.shape and np.array_equal(fcs,ff)
 err=float(abs(v-vv).max());assert err<1e-5;errors.append(err)
result=json.loads(Path('/tmp/bambu-export-investigation/boxing-glove/final/result.json').read_text())
assert result['return_code']==0
plate=result['sliced_plates'][0];assert not plate['warning_message']
assert {x['id'] for x in plate['filaments']}=={1,2,3,4}
assert all(x['main_used_g']>0 for x in plate['filaments'])
report={'bambu_version':'02.08.02.61','bambu_slice_return_code':0,'bambu_slice_warning':plate['warning_message'],'native_import_save_parts_and_filaments':a,'all_four_filaments_actually_used':True,'maximum_native_save_coordinate_roundoff_mm':max(errors),'nozzle_mm':.4,'layer_height_mm':.2,'wall_generator':'arachne','width_mm':35,'proportional_height_mm':40.487693710118506,'backing_thickness_mm':14,'raised_artwork_mm':2,'channel_nominal_diameter_mm':10,'added_clearance_mm':0,'estimated_print_time_minutes':plate['total_predication']/60,'estimated_filament_with_purge_g':sum(x['total_used_g'] for x in plate['filaments']),'estimated_model_filament_g':sum(x['main_used_g'] for x in plate['filaments']),'physical_fit_and_detail_test':'Required; not performed','sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
