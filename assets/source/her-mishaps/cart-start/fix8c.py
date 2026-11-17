from PIL import Image
import numpy as np
from scipy import ndimage
d='cart-8c-sit-2'
f0=np.array(Image.open(f'{d}/0.png').convert('RGBA')).astype(int)
lab,n=ndimage.label(f0[:,:,3]>0)
objs=ndimage.find_objects(lab)
cid=[k+1 for k,o in enumerate(objs) if o[1].start==38][0]
cm=lab==cid
cartc=np.unique(f0[cm][:,:3],axis=0); herc=np.unique(f0[(lab>0)&~cm][:,:3],axis=0)
ys,xs=np.where(cm); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
box=np.zeros(cm.shape,bool); box[y0:y1,x0:x1]=True
def dist(a,pal): return ((a[...,None,:]-pal[None,None])**2).sum(-1).min(-1)
for i in range(9):
  a=np.array(Image.open(f'{d}/{i}.png').convert('RGBA')).astype(int)
  l,_=ndimage.label(a[:,:,3]>0)
  for k,o in enumerate(ndimage.find_objects(l)):
    if o[0].stop-o[0].start<=12 and o[0].stop<57: a[l==k+1]=0
  if 1<=i<=5:
    op=a[:,:,3]>0
    rgb=a[:,:,:3]
    herish=op&((~box)|(dist(rgb,herc)<dist(rgb,cartc)))
    dark=rgb.sum(-1)<150
    core=herish&~dark
    # outline pixels count as hers only next to her own colours
    near=ndimage.binary_dilation(core,np.ones((3,3)))
    m=herish&(~box|~dark|near)
    hl,_=ndimage.label(m)
    keep=set(np.unique(hl[m&~box]))-{0}
    m=np.isin(hl,list(keep))
    out=np.zeros_like(a); out[cm]=f0[cm]; out[m]=a[m]
    a=out
  Image.fromarray(a.astype(np.uint8)).save(f'cart-8c-fixed/{i}.png')
s=Image.new('RGBA',(9*60,60),(225,215,195,255))
for i in range(9): s.alpha_composite(Image.open(f'cart-8c-fixed/{i}.png').crop((30,40,90,100)),(i*60,0))
s.resize((s.width*4,240),Image.NEAREST).save('c8-fixed-zoom.png')
