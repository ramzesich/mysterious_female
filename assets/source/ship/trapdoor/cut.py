"""The stage's open trap door (2026-11-19, the user: "What is that black rectangle in the middle? I'm falling through
it"; option 1, a generated open trap door). `inpaint_image_pro_flash` of the game's own stage at 1:1 (`src-stage.png`,
the trap door's old drawing, her and the light hidden; the trap door's middle at column 48), seed 9: its lid up on its
hinge, a ladder's top in the opening. Kept: what it changed, but not where it took out the mic stand above the floor
(columns 55 on, rows above 46: the game's own mic stand stays, moved 0.25 m aft); shifted 7 px left, so the opening's
middle is the drop's (`TRAPDOOR_M`); its ladder's right rail made its left's. Out: `assets/ship/trapdoor-open.png`, its column `MID` the trap door's middle,
its last row the stage floor's (row 56 of the source)."""
from PIL import Image
import os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
R = H + "../../../../"
src = Image.open(H + "src-stage.png").convert("RGB"); new = Image.open(H + "inpaint-s9.png").convert("RGB")
a, b = src.load(), new.load()
SHIFT, X0, X1, Y0, Y1 = -7, 38, 72, 26, 57
out = Image.new("RGBA", (X1 - X0, Y1 - Y0))
o = out.load()
for y in range(Y0, Y1):
    for x in range(X0, X1):
        if a[x, y] != b[x, y] and (x < 55 or y >= 46):
            o[x - X0, y - Y0] = b[x, y] + (255,)
box = out.getbbox()
pic = out.crop(box)
# (The user: "fix the stairs' right side to match its left": the ladder's right rail stopped at the floor; its
# left rail, columns 13-14 rows 12-22 of the picture, from the inpaint itself (opaque), is copied onto 21-22.)
ref = new.crop((X0 + box[0], Y0 + box[1], X0 + box[2], Y0 + box[3])).convert("RGBA")
pic.paste(ref.crop((13, 12, 15, 23)), (21, 12))
# (Where the trap door's middle falls in the picture: the drop is at source column 48.)
mid = 48 - SHIFT - (X0 + box[0])
pic.save(R + "assets/ship/trapdoor-open.png")
print("size", pic.size, "middle column", mid, "bottom row", Y0 + box[3] - 1)
