"""16's frames: each frame 1 px over the floor (row 120) set down (an airborne run frame, 2 px or more up, kept);
loose specks (<=3 px, apart from her) taken out unless they are water (bluish)."""
from PIL import Image
CLIPS={"drench":"drench2","run1":"run1","run3":"run3","run5":"run5","run7":"run7b","sneeze":"sneeze2","walk":"walk"}
def blue(c): return c[2]>c[0]+30 and c[2]>150
def clean(p):
    W,H=p.size;px=p.load();seen=set()
    for y in range(H):
        for x in range(W):
            if px[x,y][3]<=0 or (x,y) in seen: continue
            comp=[(x,y)];seen.add((x,y));k=0
            while k<len(comp):
                a,b=comp[k];k+=1
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        q=(a+dx,b+dy)
                        if 0<=q[0]<W and 0<=q[1]<H and q not in seen and px[q][3]>0: seen.add(q);comp.append(q)
            if len(comp)<=3 and not all(blue(px[q]) for q in comp):
                for q in comp: px[q]=(0,0,0,0)
    return p
for k,n in CLIPS.items():
    for i in range(9):
        p=clean(Image.open(f"raw/{n}-{i}.png").convert("RGBA"))
        low=p.getbbox()[3]-1
        if low==119: q=Image.new("RGBA",p.size);q.alpha_composite(p,(0,1));p=q
        p.save(f"fixed/{k}-{i}.png");print(k,i,low,"->",p.getbbox()[3]-1)
