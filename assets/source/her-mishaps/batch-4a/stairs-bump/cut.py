"""Gag 21's frames cut out of the generated ones (`raw/`): her pixels are those that differ from the stage
the clip was made on (`raw/stairs.png`, `raw/foot-stage.png`), loose specks of under 6 px taken out. Kept
as the generator drew them, facing east and descending east (the game flips them: the funnel's stairway
descends west). `sit/` sit1's frames 1 to 6, `bump/` bump2's 0 to 8, `foot/` foot1's 1 to 7, `dazed/`
dazed1's 1 to 8 (made on an opaque ground: the generator filled the stage's empty sky with a flat grey,
taken out with the faint grey it smudged here and there).
Each sit/bump frame stands on a step's corner at (48, 64) (left edge of column 48, row 64); each foot frame
on the foot of the flight at (50, 100).

python assets/source/her-mishaps/batch-4a/stairs-bump/cut.py"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"


GREY = np.array([128, 126, 126])


def cut(path, stage):
    st = np.array(Image.open(RAW / stage).convert("RGBA")).astype(int)
    f = np.array(Image.open(path).convert("RGBA")).astype(int)
    d = np.abs(f - st).sum(2) > 0
    sky = st[..., 3] == 0
    if (np.abs(f[sky][:, :3] - GREY).sum(1) == 0).mean() > 0.5:
        d &= ~(sky & (np.abs(f[..., :3] - GREY).sum(2) < 24))
    lab, n = ndimage.label(d, structure=np.ones((3, 3)))
    sizes = ndimage.sum(d, lab, range(1, n + 1))
    for k, sz in enumerate(sizes, 1):
        if sz < 6:
            d[lab == k] = False
    o = np.zeros_like(f)
    o[d] = f[d]
    return Image.fromarray(o.astype(np.uint8))


for name, src, stage, frames in [("sit", "sit1", "stairs.png", range(1, 7)),
                                 ("bump", "bump2", "stairs.png", range(0, 9)),
                                 ("foot", "foot1", "foot-stage.png", range(1, 8)),
                                 ("dazed", "dazed1", "foot-stage.png", range(1, 9))]:
    out = HERE / name
    out.mkdir(exist_ok=True)
    for j, i in enumerate(frames):
        cut(RAW / src / f"{i:02d}.png", stage).save(out / f"{j}.png")
    print(name, len(frames))
