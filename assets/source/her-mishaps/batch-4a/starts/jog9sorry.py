"""The jogger's sorry (9b, 9c; 2026-11-19): his run frame 3 as the game draws it (facing east, the sheet's way), she
sat 40 px before him facing him (her dazed-sit frame 0, mirrored), to be taken out of every frame after. A loop: the
end is the start."""
from starts2 import *
from PIL import ImageOps
PM = json.load(open(R + "assets/sprites/people.json")); PS = Image.open(R + "assets/sprites/people.png").convert("RGBA")
PC, PCOLS = PM["cell"], PM["cols"]; J = PM["people"]["jogger"]
def cell(i): return PS.crop(((i % PCOLS) * PC, (i // PCOLS) * PC, (i % PCOLS) * PC + PC, (i // PCOLS) * PC + PC))
O = R + "assets/source/her-mishaps/batch-4a/starts/jog9/sorry/"
HX, SX = 44, 84
im = Image.new("RGBA", (128, 128))
im.alpha_composite(cell(J["anims"]["run"][3]), (HX - PC // 2, FLOOR + 1 - PC))
put(im, ImageOps.mirror(herf("dazed-sit", 0)), SX)
im.save(O + "start.png")
him = Image.new("RGBA", (128, 128)); him.alpha_composite(cell(J["anims"]["run"][3]), (HX - PC // 2, FLOOR + 1 - PC)); him.save(O + "him-alone.png")
her = Image.new("RGBA", (128, 128)); put(her, ImageOps.mirror(herf("dazed-sit", 0)), SX); her.save(O + "her-alone.png")
row([im], O + "start-big.png", k=4, bg=(200, 200, 205, 255))
