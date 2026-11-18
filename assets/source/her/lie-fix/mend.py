"""Her legs lying on her belly, mended (the user, 2026-11-17: "in the lying position, the raised leg
looks wrong"): her trip (`tripfall`) and its dazed loop (`dazed-lie`) had one leg bent straight up
at the knee, a calf and a shoe standing on the end of her skirt. `lying.png` is PixelLab's edit of
the trip's lying frame (edit_image_pro_flash, palette held), both legs flat along the floor behind
her; it is the trip's lying frames (3 to 6) and, left of column 56 (her skirt and legs), every frame
of the dazed loop, so the legs do not change as one clip hands over to the other. The raw frames
are kept in `tripfall-raw/` and `dazed-lie-raw/`; `lying-dazed-unused.png` was the same edit of a
dazed frame (one long leg, not matching the trip's). 10c's trip over the trolley ends on the same
pose: `her-mishaps/trolley-start/fix10c.py` takes it from here."""
import os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
her = os.path.join(here, "..")
lying = Image.open(os.path.join(here, "lying.png")).convert("RGBA")
for i in range(3, 7):
    lying.save(os.path.join(her, "tripfall", f"{i}.png"))
CUT = 56
for i in range(1, 6):
    f = Image.open(os.path.join(here, "dazed-lie-raw", f"{i}.png")).convert("RGBA")
    out = Image.new("RGBA", f.size)
    out.alpha_composite(f.crop((CUT, 0, f.width, f.height)), (CUT, 0))
    out.alpha_composite(lying.crop((0, 0, CUT, lying.height)), (0, 0))
    out.save(os.path.join(her, "dazed-lie", f"{i}.png"))
print("mended")
