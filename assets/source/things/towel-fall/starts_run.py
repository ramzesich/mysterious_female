"""The fall on her, second version (2026-11-18; the user: she seemed to stop for the towels to fall on
her): her own run frames (`her/run-steady/<i>.png`, the game's, 96 px: her middle at x 48, her feet on
row 79) mid-stride 36 px past the redrawn stack (`soft/fall/0.png`), the start of a clip pinned to the
same buried heap (`soft/bury/8.png`), so that she comes into it running."""
import os, sys
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(here, "..", "..", "..", "..")
X, FLOOR = 36, 120
AT = int(os.environ.get("AT", 36))   # px past the stack's middle
for i in sys.argv[1:]:
    img = Image.open(os.path.join(here, "soft/fall/0.png")).convert("RGBA")
    run = Image.open(os.path.join(R, f"assets/source/her/run-steady/{i}.png")).convert("RGBA")
    img.alpha_composite(run, (X + AT - 48, FLOOR - 79))
    img.save(os.path.join(here, f"start-run-{i}-{AT}.png"))
