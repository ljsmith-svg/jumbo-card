"""Package an existing multipart Josh 3MF for Bambu. Never regenerate geometry.
Requires official extracted Bambu Studio resources and a project settings template
exported by that executable. See README for the tested invocation and provenance.
"""
from pathlib import Path
import argparse,copy,json,zipfile,xml.etree.ElementTree as ET,hashlib
import numpy as np

CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
NS={'m':CORE}
ET.register_namespace('',CORE)

def mesh_digest(model):
    values=[]
    for obj in model.findall('m:resources/m:object',NS):
        mesh=obj.find('m:mesh',NS)
        if mesh is not None:
            values.append((obj.get('id'), [(x.tag,sorted(x.attrib.items())) for x in mesh.iter()]))
    return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()

def read_zip(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}

def flatten(profiles,kind,name,stack=()):
    assert name not in stack,'Profile inheritance cycle'
    d=json.loads((profiles/kind/(name+'.json')).read_text())
    out={}
    parent=d.get('inherits')
    if parent:out.update(flatten(profiles,kind,parent,stack+(name,)))
    for inc in d.get('include',[]):out.update(flatten(profiles,kind,inc,stack+(name,)))
    out.update(d)
    return out

def package(source,template,resources,target,version='02.08.02.61'):
    entries=read_zip(source)
    root=ET.fromstring(entries['3D/3dmodel.model'])
    before=mesh_digest(root)
    cfg=json.loads(read_zip(template)['Metadata/project_settings.config'])
    profiles=resources/'profiles'/'BBL'
    meta={'name','inherits','include','type','from','instantiation','version','setting_id','filament_id','description','alias','renamed_from','compatible_printers','compatible_printers_condition','compatible_prints','compatible_prints_condition'}
    for kind,name in [('machine','Bambu Lab P1S 0.4 nozzle'),('process','0.20mm Standard @BBL X1C')]:
        for k,v in flatten(profiles,kind,name).items():
            if k not in meta:cfg[k]=v
    filament=flatten(profiles,'filament','Generic PLA')
    for k,v in filament.items():
        if k not in meta:
            cfg[k]=(v[:1]*3 if v else []) if isinstance(v,list) else v
    cfg.update({'printer_model':'Bambu Lab P1S','printer_settings_id':'Bambu Lab P1S 0.4 nozzle','printer_variant':'0.4','print_settings_id':'0.20mm Standard @BBL X1C','filament_colour':['#FFFFFF','#020202','#F20512'],'filament_settings_id':['Generic PLA']*3,'filament_ids':[filament.get('filament_id','GFL99')]*3,'filament_type':['PLA']*3,'inherits_group':['']*5,'different_settings_to_system':['']*5,'curr_bed_type':'Textured PEI Plate'})
    cfg.update({'filament_self_index':['1','2','3'],'filament_map':['1']*3,'filament_map_2':['1']*3,'filament_nozzle_map':['1']*3,'filament_volume_map':['0']*3,'filament_extruder_variant':['Direct Drive Standard']*3})
    for key in ['filament_is_support','filament_soluble']:
        cfg[key]=['0']*3
    # Preserve native format compatibility markers, while identifying this exporter.
    for name,text in [('Application','BambuStudio-'+version),('BambuStudio:3mfVersion','1'),('Designer','Just Lois Studio - prototype export correction')]:
        existing=root.find("m:metadata[@name='"+name+"']",NS)
        if existing is None:existing=ET.Element('{'+CORE+'}metadata',{'name':name});root.insert(0,existing)
        existing.text=text
    resources_node=root.find('m:resources',NS)
    meshes=[o for o in resources_node.findall('m:object',NS) if o.find('m:mesh',NS) is not None]
    names={'white':('White_Backing_and_Artwork',1),'black':('Black_Artwork',2),'red':('Red_Artwork',3)}
    assert len(meshes)==3 and {o.get('name') for o in meshes}==set(names)
    assembly=[o for o in resources_node.findall('m:object',NS) if o.find('m:components',NS) is not None]
    assert len(assembly)==1
    object_id=assembly[0].get('id')
    config=ET.Element('config');obj=ET.SubElement(config,'object',{'id':object_id})
    ET.SubElement(obj,'metadata',{'key':'name','value':'Josh - multicolor export test'})
    ET.SubElement(obj,'metadata',{'key':'extruder','value':'1'})
    for o in meshes:
        name,fil=names[o.get('name')]
        o.set('name',name)
        part=ET.SubElement(obj,'part',{'id':o.get('id'),'subtype':'normal_part'})
        ET.SubElement(part,'metadata',{'key':'name','value':name})
        ET.SubElement(part,'metadata',{'key':'extruder','value':str(fil)})
    # One group translation centers the unchanged model; relative geometry is untouched.
    pts=np.array([[float(v.get(k)) for k in ['x','y','z']] for o in meshes for v in o.findall('m:mesh/m:vertices/m:vertex',NS)])
    center=(pts.min(axis=0)+pts.max(axis=0))/2
    item=root.find('m:build/m:item',NS)
    assert item is not None and item.get('transform') is None,'Unexpected pre-existing build transform'
    tx,ty=128-center[0],128-center[1]
    item.set('transform',f'1 0 0 0 1 0 0 0 1 {tx:.9f} {ty:.9f} 0')
    plate=ET.SubElement(config,'plate')
    for k,v in [('plater_id','1'),('plater_name','Josh multicolor test'),('locked','false')]:ET.SubElement(plate,'metadata',{'key':k,'value':v})
    instance=ET.SubElement(plate,'model_instance')
    for k,v in [('object_id',object_id),('instance_id','0'),('identify_id','1')]:ET.SubElement(instance,'metadata',{'key':k,'value':v})
    entries['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    entries['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    entries['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
    # Declare settings files rather than leaving untyped archive entries.
    types=ET.fromstring(entries['[Content_Types].xml'])
    typens='http://schemas.openxmlformats.org/package/2006/content-types'
    if not any(e.get('Extension')=='config' for e in types):ET.SubElement(types,'{'+typens+'}Default',{'Extension':'config','ContentType':'application/octet-stream'})
    entries['[Content_Types].xml']=ET.tostring(types,encoding='utf-8',xml_declaration=True)
    assert before==mesh_digest(root),'Geometry changed'
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in entries.items():z.writestr(n,data)
    report={'geometry_digest_before':before,'geometry_digest_after':mesh_digest(root),'geometry_arrays_exactly_unchanged':True,'group_translation_mm':[tx,ty,0],'filaments':cfg['filament_colour'],'parts':{name:fil for name,fil in names.values()},'source':source.name,'bambu_version':version,'geometry_correction_deferred':'Backing is still combined with white artwork; export-only correction.'}
    target.with_suffix('.validation.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--template',type=Path,required=True);p.add_argument('--resources',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(package(a.source,a.template,a.resources,a.output),indent=2))
