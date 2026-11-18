"""19's frames: frame 0 and 8 of both clips are her soot picture exactly (`s19-soot.png`); each frame's
lowest row on the floor (row 120); loose specks (<=3 px, apart from her) out, except the smoke's own
(grey: the wisp off her hair, the coughed puff breaking up)."""
import sys
from PIL import Image
from pathlib import Path
B = Path(__file__).resolve().parent.parent.parent
SOOT = Image.open(B / "starts/flare/s19-soot.png").convert("RGBA")
def grey(c): return max(c[:3]) - min(c[:3]) < 12 and 50 < c[0] < 140
# (Singed hair tips standing apart from the hair in one frame: hers, kept.)
TIPS = {(70, 57), (72, 58)}
def clean(p, report):
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
                keep = all(grey(px[q]) for q in comp) or comp[0] in TIPS
                report.append((comp[0], len(comp), px[comp[0]], "kept" if keep else "out"))
                if not keep:
                    for q in comp: px[q]=(0,0,0,0)
    return p
for clip in ("blink","cough"):
    out = B / f"flare-{clip}"; out.mkdir(exist_ok=True)
    for i in range(9):
        if i in (0, 8): p = SOOT.copy(); rep = []
        else:
            rep = []
            p=clean(Image.open(B / f"raw/flare/{clip}/{i}.png").convert("RGBA"), rep)
            low=p.getbbox()[3]-1
            if low != 120:
                q=Image.new("RGBA",p.size);q.alpha_composite(p,(0,120-low));p=q
        p.save(out / f"{i}.png");print(clip,i,p.getbbox(),rep)
