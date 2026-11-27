"""The castle's pile (the user's try 1, `s3.png`) with try 2's opening (`s17.png`, its left tube's left end) in place of both its
tubes' openings: try 1's own cut away, try 2's set in where it was, flipped for the right one (the user, 2026-11-27).
Try 2's tube is a px shorter: one middle row of its opening repeated, so its outline meets try 1's above and below.
    python openings.py   -> pile.png"""
from PIL import Image

a = Image.open("s3.png").convert("RGBA")
b = Image.open("s17.png").convert("RGBA")
# Try 2's opening: columns 2 to 12 (its rim's line), rows 60 to 95; its tube's outline rows 67 and 94.
src = b.crop((2, 60, 13, 96))
w, h = src.size
tall = Image.new("RGBA", (w, h + 1))
tall.paste(src.crop((0, 0, w, 21)), (0, 0))            # rows 60..80
tall.paste(src.crop((0, 20, w, h)), (0, 21))           # row 80 again, then the rest
# Try 1's tubes: outline rows 65 and 93; the left opening to column 14 (its rim's line), the right one from 184.
TOP = 65 - (67 - 60)
out = a.copy()
px = out.load()
for y in range(55, 96):
    for x in range(0, 15):
        px[x, y] = (0, 0, 0, 0)
    for x in range(184, 200):
        px[x, y] = (0, 0, 0, 0)
out.alpha_composite(tall, (14 - (w - 1), TOP))
out.alpha_composite(tall.transpose(Image.FLIP_LEFT_RIGHT), (184, TOP))
out.save("pile.png")
print("wrote pile.png", out.getbbox())
