"""Verify immutable geometry and real Bambu load/save assignments."""
from pathlib import Path
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
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

