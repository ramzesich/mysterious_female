import json
from PIL import Image
R="C:/Users/ramze/Development/mysterious_female/"
M=json.load(open(R+"assets/sprites/her.json"));SH=Image.open(R+"assets/sprites/her.png").convert("RGBA");C,COLS=M["cell"],M["cols"]
def herf(a,n=0):
    i=M["anims"][a][n];return SH.crop(((i%COLS)*C,(i//COLS)*C,(i%COLS)*C+C,(i//COLS)*C+C))
def put(im,pic,px): im.alpha_composite(pic,(px-42,121-84))
wet=Image.open("wet-9b13cff9-439d-4cde-84b6-8403b239d72b.png").convert("RGBA")
w=Image.new("RGBA",(128,128)); w.alpha_composite(wet,(64-42-6,37-8)); w.save("s16-wet.png"); print("wet",w.getbbox())
s=Image.new("RGBA",(128,128)); put(s,herf("stand"),64); s.save("s16-stand.png"); print("stand",s.getbbox())
for n in (1,3,5,7):
    r=Image.new("RGBA",(128,128)); put(r,herf("run",n),54); r.save(f"s16-run{n}.png"); print(n,r.getbbox())
