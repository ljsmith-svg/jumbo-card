"""Separate new-art prototype exporter using the previously Bambu-verified P1S profile."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
P=Path(__file__).parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
E.register_namespace('',NS['m'])
cfg=json.loads((P/'p1s-profile-base.json').read_text())
for k,v in list(cfg.items()):
 if isinstance(v,list) and len(v)==3:cfg[k]=v+[v[-1]]
cfg.update({'filament_colour':['#FFFFFF','#020202','#FF187E','#F8A3C7'],'filament_self_index':['1','2','3','4'],'inherits_group':['']*6,'different_settings_to_system':['wall_generator','','','','',''],'flush_volumes_matrix':list(map(str,[0,186,342,195,663,0,545,606,630,204,0,457,363,223,254,0])),'flush_volumes_vector':['140']*8,'wipe_tower_x':['30'],'wipe_tower_y':['180']})
# Matrix calculated by official Bambu Studio 02.08.02.61 for this exact palette.
# Tower moved inward: inherited Y220 extended beyond the P1S bed with four colors.
with zipfile.ZipFile(P/'Boxing-Glove-Core.3mf') as z:entries={n:z.read(n) for n in z.namelist()}
r=E.fromstring(entries['3D/3dmodel.model'])
for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Designer','Just Lois Studio - boxing glove physical-test model')]:
 e=E.Element('{'+NS['m']+'}metadata',{'name':name});e.text=value;r.insert(0,e)
height=json.loads((P/'geometry-validation.json').read_text())['height_mm']
r.find('m:build/m:item',NS).set('transform',f'1 0 0 0 1 0 0 0 1 110.5 {128-height/2:.9f} 0')
config=E.Element('config');o=E.SubElement(config,'object',{'id':'7'})
for k,v in [('name','Boxing glove - separate backing and artwork'),('extruder','1')]:E.SubElement(o,'metadata',{'key':k,'value':v})
mapping={'Backing':1,'Black_Artwork':2,'Hot_Pink_Artwork':3,'Light_Pink_Artwork':4,'White_Detail':1}
for obj in r.findall('m:resources/m:object',NS):
 name=obj.get('name')
 if name not in mapping:continue
 p=E.SubElement(o,'part',{'id':obj.get('id'),'subtype':'normal_part'})
 for k,v in [('name',name),('extruder',str(mapping[name]))]:E.SubElement(p,'metadata',{'key':k,'value':v})
plate=E.SubElement(config,'plate')
for k,v in [('plater_id','1'),('plater_name','35mm boxing glove physical test'),('locked','false')]:E.SubElement(plate,'metadata',{'key':k,'value':v})
inst=E.SubElement(plate,'model_instance')
for k,v in [('object_id','7'),('instance_id','0'),('identify_id','1')]:E.SubElement(inst,'metadata',{'key':k,'value':v})
entries['3D/3dmodel.model']=E.tostring(r,encoding='utf-8',xml_declaration=True)
entries['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
entries['Metadata/model_settings.config']=E.tostring(config,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(P/'Boxing-Glove-35mm-P1S.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,v in entries.items():z.writestr(n,v)
print('Packaged five aligned components using four filament colors.')
