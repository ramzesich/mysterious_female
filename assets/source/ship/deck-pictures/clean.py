"""The chosen tries (tries/, PixelLab map objects: ids in README.md) to the frames `tools/build_ship_art.py` reads
(frame_<n>.png, in the order of NAMES): each cut to its frame, the hanging wire or hooks some were drawn with taken
off (rows over the frame with few px against its own), and the escape plan's stray red mark on its frame's corner
given the frame's grey. Run from anywhere: python assets/source/ship/deck-pictures/clean.py"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
# Deck by deck, as `drawCabinDoors` hangs them (the user's choice, 2026-11-24).
NAMES = [
    "d4-roster-2", "d4-lifejacket", "d4-escape-plan-2", "d4-firstaid", "d4-lifeboat-2",
    "d5-ship-sea", "d5-ship-harbour", "d5-ship-islands-2", "d5-ship-bow",
    "d6-chart-harbour", "d6-port-town", "d6-islands", "d6-chart-rose",
    "d8-waves", "d8-lighthouse", "d8-sailboat", "d8-sunset",
    "d9-fern", "d9-flower", "d9-lemon", "d9-monstera",
    "d10-liner", "d10-bow", "d10-night", "d10-funnels-2",
]


def clean(im):
    a = im.split()[3]
    rows = [sum(1 for x in range(im.width) if a.getpixel((x, y))) for y in range(im.height)]
    widest = max(rows)
    top = next(y for y, n in enumerate(rows) if n >= 0.6 * widest)
    bot = max(y for y, n in enumerate(rows) if n >= 0.6 * widest)
    im = im.crop((0, top, im.width, bot + 1))
    return im.crop(im.getbbox())


def main():
    for i, n in enumerate(NAMES):
        im = clean(Image.open(HERE / "tries" / f"{n}.png").convert("RGBA"))
        if n == "d4-escape-plan-2":
            px = im.load()
            for y in range(im.height):
                for x in range(im.width):
                    r, g, b, al = px[x, y]
                    if al and r > 150 and g < 90 and (x < 3 or y > im.height - 4):
                        px[x, y] = px[x + 1, y] if x < 3 else px[x, y - 1]
        im.save(HERE / f"frame_{i}.png")
        print(i, n, im.size)


if __name__ == "__main__":
    main()
