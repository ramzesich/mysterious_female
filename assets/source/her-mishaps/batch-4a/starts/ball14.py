"""14a's and 14b's starts and ends (2026-11-19), from her built sheet. The end is her standing frame turned a quarter,
pixel for pixel (stiff as a plank): 14a on her back, head behind her (west), heels where they were; 14b on her face,
head ahead (east). From her stand and her run frames 1, 3, 5, 7; run starts end a little further on (her momentum)."""
from starts2 import *
O = R + "assets/source/her-mishaps/batch-4a/starts/ball14/"
st = herf("stand"); bb = st.getbbox(); body = st.crop(bb)
heel = bb[0], bb[2]          # her body's columns in the cell (42 its middle)
print("stand bbox", bb)
def flat(back, feet_x):
    """Her stand turned flat, its shoes' end at canvas column feet_x, on the floor row."""
    im = Image.new("RGBA", (128, 128))
    r = body.rotate(90 if back else -90, expand=True)     # 90: head to the west (left)
    x = feet_x - r.width + 1 if back else feet_x
    im.alpha_composite(r, (x, FLOOR + 1 - r.height)); return im
def feet(pic, px):
    """The columns of her shoes (the lowest 3 rows) when put at px."""
    a = pic.getchannel("A"); w, h = a.size
    xs = [x for y in range(h - 4, h) for x in range(w) if a.getpixel((x, y))]
    return min(xs) + px - 42, max(xs) + px - 42
pics = []
for name, back, px in (("a", True, 92), ("b", False, 36)):
    for n in ("stand", 1, 3, 5, 7):
        pic = herf("stand") if n == "stand" else herf("run", n)
        s = Image.new("RGBA", (128, 128)); put(s, pic, px)
        f0, f1 = feet(pic, px)
        on = 0 if n == "stand" else (5 if back else 12)
        m = (f0 + f1) // 2
        e = flat(back, (m + 4 if back else m - 4) + on)
        tag = "st" if n == "stand" else f"r{n}"
        s.save(O + f"{name}-start-{tag}.png"); e.save(O + f"{name}-end-{tag}.png")
        both = s.copy(); both.alpha_composite(e); pics += [s, e]
        print(name, tag, "feet", f0, f1, "end", e.getbbox())
row(pics, O + "starts-ends.png", k=2, bg=(200, 200, 205, 255))
