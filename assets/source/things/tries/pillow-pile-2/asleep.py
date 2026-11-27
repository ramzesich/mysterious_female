"""The pile with the king and the knight asleep on it (the user's try 3, `kids-text-s7.png`: edit_image_pro_flash of
`pile.png`, 112165e8), its tubes' openings put back exactly as approved (`pile.png`'s columns 0 to 15 and 184 to 199,
where only the tubes are: the redraw had moved a few px of each), then shrunk to 65% (the user's choice of four sizes,
2026-11-27: the kids came at their source size, "The kids look enormous"; at 65% their heads are their own in the game)
by the people's build's own shrink. -> `../../pillow-castle-down.png`.
    python asleep.py"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools"))
from build_people import shrunk     # noqa: E402
from palettize import palettize     # noqa: E402

SCALE = 0.65

kids = Image.open("kids-text-s7.png").convert("RGBA")
pile = Image.open("pile.png").convert("RGBA")
out = kids.copy()
for x0, x1 in ((0, 16), (184, 200)):
    box = (x0, 55, x1, 96)
    clear = Image.new("RGBA", (x1 - x0, 41))
    out.paste(clear, box[:2])
    out.alpha_composite(pile.crop(box), box[:2])
out = shrunk(palettize(out), SCALE)
out = out.crop(out.getbbox())
out.save("../../pillow-castle-down.png")
print("wrote pillow-castle-down.png", out.getbbox())
