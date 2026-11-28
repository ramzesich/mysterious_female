"""The five balloons of `small-s1.png` (the user's choice of two, 2026-11-28: generated at the game's size with the red
balloon of `s1.png`, their first choice, as the style; taking rows out of `s1.png` turned them into diamonds) cut apart
into `cut/<colour>.png`, each trimmed to what is drawn."""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
COLOURS = ["red", "yellow", "blue", "green", "pink"]


def pieces(im):
    """Each balloon: a run of columns with something in them, trimmed."""
    a = im.getchannel("A")
    cols = [any(a.getpixel((x, y)) for y in range(im.height)) for x in range(im.width)]
    out, x = [], 0
    while x < im.width:
        if cols[x]:
            x0 = x
            while x < im.width and cols[x]:
                x += 1
            p = im.crop((x0, 0, x, im.height))
            out.append(p.crop(p.getbbox()))
        x += 1
    return out


if __name__ == "__main__":
    (HERE / "cut").mkdir(exist_ok=True)
    bs = pieces(Image.open(HERE / "small-s1.png").convert("RGBA"))
    assert len(bs) == 5, len(bs)
    for name, b in zip(COLOURS, bs):
        b.save(HERE / "cut" / f"{name}.png")
        print(name, b.size)
