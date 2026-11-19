"""Gag 22's clip cut out: `raw/flip2/` (index 0 the input, her glide with the open parasol) to `flip/0.png` ..
`flip/8.png`, facing east as generated, on its 128 px canvas (her feet in the input at (56, 112)). Loose specks
apart from her and the parasol (the wind's white dashes and red scraps the generator drew under the canopy in
frames 1 to 3) are taken out: only the largest piece is kept. And from frame 2 on the generator lit the shaft's
left column pale (the parasol's light grey): the shaft is put back in its own olive, as in the input."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
OUT = HERE / "flip"
OUT.mkdir(exist_ok=True)
for i in range(9):
    f = np.array(Image.open(HERE / "raw" / "flip2" / f"0{i}.png").convert("RGBA"))
    d = f[..., 3] > 0
    lab, n = ndimage.label(d, structure=np.ones((3, 3)))
    sizes = ndimage.sum(d, lab, range(1, n + 1))
    keep = 1 + int(np.argmax(sizes))
    gone = int(d.sum() - sizes[keep - 1])
    d &= lab == keep
    f[~d] = 0
    # The shaft: rows between the canopy and the 3 pale rows over her hand (the input has them too) whose
    # only px near it are in its two columns.
    for y in range(30, 55):
        row = np.nonzero(f[y, 60:70, 3])[0] + 60
        if len(row) and row.min() >= 62 and row.max() <= 65:
            for x in row:
                if tuple(f[y, x, :3]) == (199, 220, 208):
                    f[y, x, :3] = (76, 62, 36)
    Image.fromarray(f).save(OUT / f"{i}.png")
    print(i, "loose px", gone, "partial alpha", int(((f[..., 3] > 0) & (f[..., 3] < 255)).sum()))
