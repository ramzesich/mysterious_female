"""The art handlers' clips cut out of their green ground (part 11's item 10, 2026-11-28). In each clip the painting is a
flat magenta panel (`carry/masked.png`: the chosen carry picture `carry/e1.png` with the painting's own pixels turned
magenta, the hands and the younger one's body over it kept), so that the game draws its one painting there frame by
frame: each frame's figures with the panel and the green taken out (`cut/<clip>/<i>.png`), and where the panel was
(`cut/<clip>.json`: its box per frame). Usage: python cut.py <clip folder under walk/ ...> <name>"""
import json, sys
from collections import deque
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
PAINTING = Image.open(HERE.parent.parent / "things/tries/painting/lighthouse.png").convert("RGBA")
PAINTING = PAINTING.crop(PAINTING.getbbox())


def clear_inside(im, box):
    """Inside the painting's outline (stood on the panel's box): only what joins a figure from outside it is kept; the
    rest (bits of the panel the generator redrew: a grey line along its top) is the painting's place."""
    x0, y1 = box[0], box[3]
    y0 = y1 - PAINTING.height + 1
    # (its whole box: its top row is mostly empty between the corners' ornaments, and the generator drew a line there)
    inside = lambda x, y: 0 <= x - x0 < PAINTING.width and 0 <= y - y0 < PAINTING.height
    solid = lambda x, y: 0 <= x < im.width and 0 <= y < im.height and im.getpixel((x, y))[3] > 0
    keep, q = set(), deque()
    for y in range(im.height):
        for x in range(im.width):
            if inside(x, y) and solid(x, y) and any(solid(x + dx, y + dy) and not inside(x + dx, y + dy)
                                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                keep.add((x, y)); q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in keep and inside(*n) and solid(*n):
                keep.add(n); q.append(n)
    for y in range(im.height):
        for x in range(im.width):
            if inside(x, y) and (x, y) not in keep:
                im.putpixel((x, y), (0, 0, 0, 0))


def is_green(c):
    r, g, b = c[:3]
    # (the ground, and the darker green the edit left along the panel's edge, 48 105 24)
    return (g > 140 and r < 90 and b < 90) or (g > r + 30 and g > b + 30)


def is_panel(c):
    r, g, b = c[:3]
    return r > 150 and b > 150 and g < 120


def cut(src, name):
    out = HERE / "cut" / name
    out.mkdir(parents=True, exist_ok=True)
    boxes = []
    frames = sorted(src.glob("f*.png"))
    for i, f in enumerate(frames):
        im = Image.open(f).convert("RGBA")
        xs, ys = [], []
        for y in range(im.height):
            for x in range(im.width):
                c = im.getpixel((x, y))
                if is_panel(c):
                    xs.append(x); ys.append(y)
                    im.putpixel((x, y), (0, 0, 0, 0))
                elif is_green(c):
                    im.putpixel((x, y), (0, 0, 0, 0))
        box = [min(xs), min(ys), max(xs), max(ys)] if xs else None
        if box:
            clear_inside(im, box)
        im.save(out / f"{i}.png")
        boxes.append(box)
    (HERE / "cut" / f"{name}.json").write_text(json.dumps({"frames": len(frames), "panel": boxes}) + "\n", encoding="utf8")
    print(name, len(frames), boxes)


if __name__ == "__main__":
    cut(HERE / sys.argv[1], sys.argv[2])
