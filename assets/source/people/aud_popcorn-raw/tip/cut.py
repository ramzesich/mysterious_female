"""The popcorn man's tip (part 11's item 12, 2026-11-27): PixMiniMax seed 1 (`s1/`, job
b4b80c22-7cc5-40ba-bc7f-9a0ebd62a2ac) from `start.png` (his game picture, `../../aud_popcorn/stand.png`, on green over a
floor strip at row 88) cut into frames of his own canvas.

Each frame: the green and the floor strip out; the generator's copy of the seat out (a pixel inside the seat's shape
still the start's seat pixel); then the game's own seat split as `audience-seated/compose.py` splits it (the backrest
and the far arm behind him, from row 60 the near arm, the seat's front and legs in front). The kernels lying on the
floor (rows 82 to 87, ahead of his shoes, a kernel's colour, not in the start) are a layer of their own: `floor-<i>.png`
(the game's lying popcorn is the last one). Specks at the top and kernels left in the air once the rest lie are taken
out; in the last frames a kernel with nothing under it rests on one or on the floor. Out: `cut/<i>.png` (128 x 96, his cell's floor at row 88, his middle at
x 44) and `cut/floor-<i>.png`.
"""
import os
from PIL import Image

H = os.path.dirname(os.path.abspath(__file__)) + "/"
SEAT = Image.open(H + "../../../ship/theatre-seat-side/frame_0.png").convert("RGBA")
OX, OY = 4, 8                 # his 80 px cell on the start's canvas
FLOOR = 88                    # the strip's first row: her floor
NEAR_FROM = 60
GREEN = (0, 200, 60)
KERNEL = {(243, 247, 245), (253, 195, 169)}
# (13 and 14 left out: he lurches and the generator's seat moves with him, its back out behind the game's.)
FRAMES = list(range(13)) + [15, 16]

start = Image.open(H + "start.png").convert("RGB")
far, near = Image.new("RGBA", start.size), Image.new("RGBA", start.size)
for y in range(SEAT.height):
    for x in range(SEAT.width):
        p = SEAT.getpixel((x, y))
        if p[3]:
            (far if y < NEAR_FROM else near).putpixel((x + OX, y + OY), p)


def is_seat(x, y, c):
    sx, sy = x - OX, y - OY
    if not (0 <= sx < SEAT.width and 0 <= sy < SEAT.height) or not SEAT.getpixel((sx, sy))[3]:
        return False
    return c == start.getpixel((x, y)) and c == SEAT.getpixel((sx, sy))[:3]


def floor_kernel(x, y, c):
    return 82 <= y < FLOOR and x >= 50 and c in KERNEL and c != start.getpixel((x, y))


os.makedirs(H + "cut", exist_ok=True)
for i in FRAMES:
    f = Image.open(H + f"s1/f{i:02d}.png").convert("RGB")
    him, lying = Image.new("RGBA", f.size), Image.new("RGBA", f.size)
    for y in range(FLOOR):
        for x in range(f.width):
            c = f.getpixel((x, y))
            if c == GREEN or is_seat(x, y, c):
                continue
            if y < 30 or (i >= 12 and c in KERNEL and x >= 64 and y < 82):
                continue      # (a speck at the top; kernels left hanging in the air once the rest have landed)
            (lying if floor_kernel(x, y, c) else him).putpixel((x, y), (*c, 255))
    if i >= 15:
        # (Lying: a kernel with nothing under it comes down until it rests on one or on the floor.)
        for y in range(FLOOR - 2, 81, -1):
            for x in range(f.width):
                if lying.getpixel((x, y))[3]:
                    v = y
                    while v + 1 < FLOOR and not lying.getpixel((x, v + 1))[3]:
                        v += 1
                    if v != y:
                        lying.putpixel((x, v), lying.getpixel((x, y)))
                        lying.putpixel((x, y), (0, 0, 0, 0))
    out = far.copy()
    out.alpha_composite(him)
    out.alpha_composite(near)
    out.save(H + f"cut/{i}.png")
    lying.save(H + f"cut/floor-{i}.png")
print("cut", len(FRAMES))
