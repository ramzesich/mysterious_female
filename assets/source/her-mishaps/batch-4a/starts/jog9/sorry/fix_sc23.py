"""His scratch (sc23) mended by hand (2026-11-19, the user: "He has three hands in the second half"): in frames 6 to 8
his far hand still peeked out in front of his shorts where it hangs when he stands, though that arm is up behind his
head (x 49-52, rows 96-101: frame 5's pixels there, which have none); and in frame 6 a few skin pixels showed at the
back of his head (x 36-41, rows 64-69: frame 8's, his hair). Then (the user: "remove the extra two pixels ... Make his
shorts look the same as on the previous frames"): in frames 5 to 8 a bump of two px stood out of the shorts' front edge
(x 49-50, rows 98-99) and their side's dark stripe was gone: the shorts there (x 42-51, rows 95-101) are frame 4's. Run after `clean.py`'s cleaning of `raw/sc23`."""
from PIL import Image
import os
D = os.path.dirname(os.path.abspath(__file__)) + "/clean-sc23/"
f5, f8 = Image.open(D + "5.png").convert("RGBA"), Image.open(D + "8.png").convert("RGBA")
hip, head = (49, 96, 53, 102), (36, 64, 42, 70)
for i in (6, 7, 8):
    im = Image.open(D + f"{i}.png").convert("RGBA")
    im.paste(f5.crop(hip), hip[:2])
    if i in (6, 7): im.paste(f8.crop(head), head[:2])
    im.save(D + f"{i}.png")
f4 = Image.open(D + "4.png").convert("RGBA")
shorts = (42, 95, 52, 102)
for i in (5, 6, 7, 8):
    im = Image.open(D + f"{i}.png").convert("RGBA")
    im.paste(f4.crop(shorts), shorts[:2])
    im.save(D + f"{i}.png")
print("ok")
