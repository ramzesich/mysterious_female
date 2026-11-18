"""17's frames: frame 0 (and the fan's pinned last frame) is her puff picture exactly (`s17-puff.png`);
each frame's lowest row set on the floor (row 120); loose specks (<=3 px, apart from her) taken out."""
from PIL import Image
from pathlib import Path
B = Path(__file__).resolve().parent.parent.parent
PUFF = Image.open(B / "starts/steam/s17-puff.png").convert("RGBA")
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
            if len(comp)<=3:
                for q in comp: px[q]=(0,0,0,0)
    return p
for clip in ("fan","swoon"):
    out = B / f"steam-{clip}"; out.mkdir(exist_ok=True)
    for i in range(9):
        if i == 0 or (clip == "fan" and i == 8): p = PUFF.copy()
        else:
            p=clean(Image.open(B / f"raw/steam/{clip}/{i}.png").convert("RGBA"))
            low=p.getbbox()[3]-1
            if low != 120:
                q=Image.new("RGBA",p.size);q.alpha_composite(p,(0,120-low));p=q
        p.save(out / f"{i}.png");print(clip,i,p.getbbox())
