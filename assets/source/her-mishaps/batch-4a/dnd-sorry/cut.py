"""Gag 23's frames from the generator's (`raw/`), mended (README):
  cover/0..8   her start (`raw/cover1`, seed 7) frames 0 to 6; 7 and 8 are 6 again with her blush set by hand on her
               cheek, light then full (`raw/blush.py`): the generator's own turned her whole hands hot pink
  tiptoe/0..8  the tiptoe loop: 0 is cover/8; 1 to 8 (`raw/tip6`) drawn by animate_with_skeleton_v3 from cover/8 along
               skeletons laid out by rule (`raw/tiptoe_kp.py`: two tiny steps on her toes, the body level; the user found
               PixMiniMax's strides, `raw/tip2`, "a bit like a skip-dancing"); frames 4 to 6 put down 1 px onto the
               floor (row 120)"""
from pathlib import Path
from PIL import Image
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "raw"))
from blush import blush

CHEEK = (65, 73, 70, 78)
(HERE / "cover").mkdir(exist_ok=True)
(HERE / "tiptoe").mkdir(exist_ok=True)
for i in range(7):
    Image.open(HERE / f"raw/cover1/{i}.png").convert("RGBA").save(HERE / f"cover/{i}.png")
f6 = Image.open(HERE / "raw/cover1/6.png").convert("RGBA")
blush(f6, *CHEEK, strong=False).save(HERE / "cover/7.png")
blush(f6, *CHEEK).save(HERE / "cover/8.png")
for i in range(9):
    im = Image.open(HERE / f"raw/tip6/{i}.png").convert("RGBA")
    if i in (4, 5, 6):
        out = Image.new("RGBA", im.size)
        out.alpha_composite(im, (0, 1))
        im = out
    im.save(HERE / f"tiptoe/{i}.png")
