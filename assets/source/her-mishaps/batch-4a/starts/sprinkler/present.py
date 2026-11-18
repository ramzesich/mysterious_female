import random
from PIL import Image, ImageDraw
WALL,CARPET=(232,220,203,255),(70,80,110,255)
def cell(k,i,rain=False):
    im=Image.new("RGBA",(72,70),WALL);d=ImageDraw.Draw(im);d.rectangle((0,65,72,70),fill=CARPET)
    if rain:
        r=random.Random(i*7+len(k))
        for j in range(16):
            x=r.randint(4,68);y=r.randint(0,60);d.rectangle((x,y,x,y+4),fill=(0x8f,0xd3,0xff,240) if j%3 else (255,255,255,240))
    f=Image.open(f"fixed/{k}-{i}.png").convert("RGBA").crop((28,56,100,126));im.alpha_composite(f,(0,0))
    return im
def sheet(rows,path,K=3,gap=3):
    w=max(len(r) for r in rows)*(72+gap);h=len(rows)*(70+gap)
    S=Image.new("RGB",(w,h),(40,40,44))
    for y,r in enumerate(rows):
        for x,c in enumerate(r): S.paste(c,(x*(72+gap),y*(70+gap)))
    S.resize((S.width*K,S.height*K),Image.NEAREST).save(path);print(path,S.size)
seq=[cell("run7",i,True) for i in range(0,9)]
sheet([seq[:9],[cell("sneeze",i) for i in range(1,9)],[cell("walk",i) for i in range(1,9)]],"show16-seq.png",K=2)
sheet([[cell("drench",i,True) for i in range(0,9)]]+[[cell(k,i,True) for i in range(0,9)] for k in ("run1","run3","run5")],"show16-starts.png",K=2)
