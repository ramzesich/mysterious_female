# Delivery 2's teapot and its cup (plan-the-rest §5 3.2), drawn by hand px by px over PixelLab's redraw of try 4
# (tries/tea-4-small.png; the user, 2026-11-23: "Fix the teapot's pixels"): the navy outline, white, the navy band, a
# pale blue-grey shade. Writes ../delivery-teapot.png.
from PIL import Image
G = """
..........oo........
.........onno.......
.......oowwwwoo.....
......owwwwwwwso....
.....owwwwwwwwwso..o
.....onnnnnnnnnnoosw
.oooooowwwwwwwwsowo.
oowwwwowwwwwwwwsoo..
o.owwsowwwwwwwwso...
..owwsowwwwwwwso....
.ooooooooooooooo....
"""
C = {'o': (0x0d,0x10,0x34), 'w': (0xfd,0xfd,0xfd), 'n': (0x19,0x18,0x50), 's': (0xc8,0xd2,0xe3)}
rows=[r for r in G.strip().split('\n')]
im=Image.new('RGBA',(len(rows[0]),len(rows)))
for y,r in enumerate(rows):
    assert len(r)==len(rows[0]),(y,len(r))
    for x,ch in enumerate(r):
        if ch in C: im.putpixel((x,y),C[ch]+(255,))
import pathlib; HERE = pathlib.Path(__file__).parent
im.save(HERE.parent / 'delivery-teapot.png')
