"""The dog's lick (approved 2026-11-17): her butterflies back to her dazed clip's yellow.

PixMiniMax (raw/, from `raw/start.png`: her dazed-lie frame 1 with the dog's standing picture,
turned to her, in front of her face, its feet on her floor) drew some of them purple and teal.
Above her (rows 0 to 60), a px of a colour the start picture does not have, not already a yellow,
takes the yellow of the start's butterflies (the darkest ones its shade). The dog's pink tongue is
lower and is kept. Raw frame 0 is the start picture; 1 to 8 are written here as 0 to 7.

    python assets/source/her-mishaps/dog-lick/butterflies.py
"""
import colorsys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
YELLOW, SHADE = (211, 183, 71, 255), (138, 115, 71, 255)


def main():
    start = Image.open(HERE / "raw" / "0.png").convert("RGBA")
    known = {start.getpixel((x, y)) for y in range(start.height) for x in range(start.width)}
    for i in range(1, 9):
        im = Image.open(HERE / "raw" / f"{i}.png").convert("RGBA")
        for y in range(61):
            for x in range(im.width):
                c = im.getpixel((x, y))
                if not c[3] or c in known:
                    continue
                h, s, _v = colorsys.rgb_to_hsv(*[k / 255 for k in c[:3]])
                if s > 0.3 and not 0.05 < h < 0.2:
                    lum = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
                    im.putpixel((x, y), SHADE if lum < 30 else YELLOW)
        im.save(HERE / f"{i - 1}.png")
    print("wrote", HERE)


if __name__ == "__main__":
    main()
