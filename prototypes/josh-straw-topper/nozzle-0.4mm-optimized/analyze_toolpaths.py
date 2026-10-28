from pathlib import Path
import re,json,math
import numpy as np
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).parent
BOUNDS=(110.5,115.1095293275,145.5,140.8904706725)
PX=.025
COLORS={0:(255,255,255),1:(2,2,2),2:(242,5,18)}
PARAM=re.compile(r'([XYZEIJ])([-+]?\d*\.?\d+)')

def read(path):
 x=y=0.;evalue=0.;relative=True;tool=0;z=0.;width=.42;segments=[]
 for line in Path(path).read_text().splitlines():
  if line.startswith('; Z_HEIGHT:'):z=float(line.split(':',1)[1])
  if line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
  code=line.split(';',1)[0].strip()
  if not code:continue
  if re.fullmatch(r'T\d+',code):tool=int(code[1:]);continue
  if code=='M83':relative=True;continue
  if code=='M82':relative=False;continue
  a={k:float(v) for k,v in PARAM.findall(code)}
  op=code.split()[0]
  if op=='G92':
   if 'E' in a:evalue=a['E']
   continue
  if op not in ['G0','G1','G2','G3']:continue
  nx,ny=a.get('X',x),a.get('Y',y)
  extrusion=a.get('E',0.) if relative else a.get('E',evalue)-evalue
  if 'E' in a:evalue=a['E'] if not relative else evalue+a['E']
  if extrusion>0 and tool in COLORS and abs(z-16)<.001 and ('X' in a or 'Y' in a) and BOUNDS[0]-.01<=x<=BOUNDS[2]+.01 and BOUNDS[1]-.01<=y<=BOUNDS[3]+.01 and BOUNDS[0]-.01<=nx<=BOUNDS[2]+.01 and BOUNDS[1]-.01<=ny<=BOUNDS[3]+.01:
   pts=[(x,y),(nx,ny)]
   if op in ['G2','G3'] and ('I' in a or 'J' in a):
    cx,cy=x+a.get('I',0),y+a.get('J',0);r=math.hypot(x-cx,y-cy);start=math.atan2(y-cy,x-cx);end=math.atan2(ny-cy,nx-cx)
    delta=(end-start)%(2*math.pi)
    if op=='G2':delta=delta-2*math.pi if delta else -2*math.pi
    n=max(2,math.ceil(abs(delta)*r/.04));theta=np.linspace(start,start+delta,n+1);pts=list(zip(cx+r*np.cos(theta),cy+r*np.sin(theta)))
   length=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]));segments.append((tool,width,length,pts))
  x,y=nx,ny
 return segments

def plot(segments):
 d=np.load(ROOT/'original-masks.npz');xs,ys=d['xs'],d['ys'];shape=d['White_Artwork'].shape
 rgb=np.full((*shape,3),255,dtype=np.uint8);support=np.logical_or.reduce([d[n] for n in ['White_Artwork','Black_Artwork','Red_Artwork']]);rgb[support]=[180]*3
 im=Image.fromarray(rgb);draw=ImageDraw.Draw(im)
 for tool,width,length,pts in segments:
  p=[((x-BOUNDS[0]-xs[0])/PX,(y-BOUNDS[1]-ys[0])/PX) for x,y in pts]
  w=max(1,round(width/PX));draw.line(p,fill=COLORS[tool],width=w,joint='curve')
 return np.asarray(im)

if __name__=='__main__':
 report={};fig,axes=plt.subplots(1,2,figsize=(14,6),layout='constrained')
 for key,path,ax,title in [('before','/tmp/bambu-export-investigation/nozzle-04/baseline/plate_1.gcode',axes[0],'Original artwork / Classic walls'),('after','/tmp/bambu-export-investigation/nozzle-04/optimized/plate_1.gcode',axes[1],'Optimized artwork / Arachne walls')]:
  seg=read(path);assert seg,'No final-layer paths parsed'
  report[key]={}
  for tool,color in [(0,'white'),(1,'black'),(2,'red')]:
   s=[x for x in seg if x[0]==tool];length=sum(x[2] for x in s);thin=sum(x[2] for x in s if x[1]<.34)
   assert length>0
   report[key][color]={'extrusion_path_length_mm':length,'path_length_below_034mm_mm':thin,'fraction_below_034mm':thin/length}
  ax.imshow(plot(seg),origin='lower');ax.set_title(title);ax.axis('off')
 fig.suptitle('Actual Bambu Studio top-layer extrusion coverage — gray indicates uncovered area')
 fig.savefig(ROOT/'sliced-toolpath-comparison.png',dpi=160)
 (ROOT/'toolpath-analysis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
