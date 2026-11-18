"""The shut glass door seen edge on, exactly as `buildBulkhead` draws it (steel frame: a 4 px slab,
its glass between), its two-way handle left out, on a 32 x 80 canvas (the slab in columns 14 to 17,
its top on row 3, its bottom on the floor's last row, 76): the source a one-way door's profile is
inpainted into on its free side (the user, 2026-11-18: "the door profile should also differ from a
two-way glass door"). Also the masks: `mask-bar.png` (its free side, the bar's height),
`mask-closer.png` (its free side, the bar's height and the top).

python assets/source/ship/pushbar/edge.py"""
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
im = Image.new("RGBA", (32, 80), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rectangle((14, 3, 17, 76), fill=(0x9b, 0xab, 0xb2, 255))
d.rectangle((15, 5, 16, 5 + 66 - 1), fill=(0xbf, 0xe6, 0xf5, 255))
im.save(HERE / "edge-plain.png")
two = im.copy(); ImageDraw.Draw(two).rectangle((11, 40, 20, 42), fill=(0x9b, 0xab, 0xb2, 255))
two.save(HERE / "edge-twoway.png")
for name, boxes in (("bar", [(4, 33, 13, 48)]), ("closer", [(4, 33, 13, 48), (4, 3, 13, 14)])):
    m = Image.new("RGB", (32, 80), (0, 0, 0))
    for b in boxes: ImageDraw.Draw(m).rectangle(b, fill=(255, 255, 255))
    m.save(HERE / f"mask-{name}.png")
print("ok")
