from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
p=Path(__file__).parent
fig,axes=plt.subplots(1,2,figsize=(14,6),layout='constrained')
for ax,file,title in zip(axes,['original-masks.npz','optimized-masks.npz'],['Original 35 mm artwork','Optimized artwork — 0.4 mm nozzle']):
 d=np.load(p/file);xs=d['xs'];ys=d['ys'];rgb=np.ones((*d['White_Artwork'].shape,3))
 rgb[d['Black_Artwork']]=[.008,.008,.008];rgb[d['Red_Artwork']]=[.949,.02,.071]
 ax.imshow(rgb,origin='lower',extent=[xs[0],xs[-1],ys[0],ys[-1]],interpolation='none');ax.set_title(title);ax.set_aspect('equal');ax.set_xlabel('Width (mm)');ax.set_ylabel('Height (mm)')
fig.savefig(p/'artwork-comparison.png',dpi=160)
