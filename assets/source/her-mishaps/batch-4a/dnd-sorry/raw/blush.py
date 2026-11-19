"""Her blush, set by hand on the skin of her cheek between her hair and her hands (the generator's own turned
her whole hands hot pink): the skin's light shades in a patch go to the palette's pinks."""
from PIL import Image
LIGHT, MID, DARK = (253, 203, 176), (252, 167, 144), (246, 129, 129)
PINK, ROSE = (237, 128, 153), (207, 101, 127)

def blush(im, x0, y0, x1, y1, strong=True):
    im = im.copy(); px = im.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = px[x, y]
            if not c[3]: continue
            if c[:3] == LIGHT: px[x, y] = (*(PINK if strong else DARK), 255)
            elif c[:3] in (MID, DARK): px[x, y] = (*(ROSE if strong else PINK), 255)
    return im
