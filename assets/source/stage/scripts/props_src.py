"""The two halves of the new stage with the game's own drum kit and grand piano laid in where the plan has them,
as sources for PixelLab's redraw of each prop in the stage's light."""
from pathlib import Path
from PIL import Image
import json
R = Path(r"C:\Users\ramze\Development\mysterious_female-catch3")
G = R / "assets/source/stage/gen"
half = Image.open(G / "stage-left-s11.png").convert("RGBA")
atlas = Image.open(R / "assets/ship/ship.png").convert("RGBA")
fr = json.load(open(R / "assets/ship/ship.json", encoding="utf8"))["frames"]
def piece(name, flip=False):
    f = fr[name]["frame"]
    p = atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
    return p.transpose(Image.FLIP_LEFT_RIGHT) if flip else p
left = half.copy()
p = piece("drum-kit"); left.alpha_composite(p, (58 - p.width // 2, 128 - p.height))
left.convert("RGB").save(G / "src-left-drums.png")
right = half.transpose(Image.FLIP_LEFT_RIGHT)
p = piece("grand-piano", True); right.alpha_composite(p, (93 - p.width // 2, 128 - p.height))
right.convert("RGB").save(G / "src-right-piano.png")
print("drums box", 58 - 31, 128 - 47, "piano box", 93 - 30, 128 - 61)
