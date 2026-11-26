"""Splash Academy's pillow fort with its doorways (plan-the-rest §7f, P6; the user, 2026-11-26: "it is unclear that there
are openings she is supposed to crawl through"): `tall-s8.png` (the approved fort's stacks made doorways up to the blanket,
two edits) split in two. In front of her (`pillow-fort.png`): all of it but the doorways' dark and the lit floor at their
foot, which go behind her (`pillow-fort-back.png`) with a faint shade of the same dark under the blanket between them, the
inside of one tunnel. So she shows going through each doorway and along the inside."""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
OUT = HERE.parent.parent                         # assets/source/things/
DARK = (50, 44, 60)
DOORS = ((14, 22), (152, 161))                   # the doorways' columns (measured)
SHADE = 0.32                                     # the inside's shade under the blanket, of the doorways' dark

src = Image.open(HERE / "tall-s8.png").convert("RGBA")
W, H = src.size
front, back = src.copy(), Image.new("RGBA", src.size, (0, 0, 0, 0))
f, b, s = front.load(), back.load(), src.load()
near = lambda c, k: sum((a - b) ** 2 for a, b in zip(c[:3], k)) <= 40 ** 2
for x0, x1 in DOORS:
    for x in range(x0, x1 + 1):
        for y in range(28, H):
            p = s[x, y]
            if p[3] and (near(p, DARK) or y >= H - 5):
                b[x, y] = p
                f[x, y] = (0, 0, 0, 0)
# The inside: under the blanket, from the first empty row under it to the floor, between the doorways.
for x in range(DOORS[0][1] + 1, DOORS[1][0]):
    y = 0
    while y < H and not s[x, y][3]:
        y += 1
    while y < H and s[x, y][3]:
        y += 1
    for yy in range(y, H):
        if not s[x, yy][3] and not b[x, yy][3]:
            b[x, yy] = DARK + (round(255 * SHADE),)
front.save(OUT / "pillow-fort.png")
back.save(OUT / "pillow-fort-back.png")
print("front and back", src.size)
