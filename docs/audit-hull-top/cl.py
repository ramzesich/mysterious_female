import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
SPOTS = [("fwdpool", 3380, 416), ("fwdpool2", 3150, 416), ("bowdeck", 2300, 416), ("terr-end", 10990, 416), ("radar", 2700, 416), ("mast", 4086, 416), ("globes", 4700, 416)]
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12&cards=all"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    for n, x, y in SPOTS:
        b.teleport(x, y, "inside"); b.wait(2.0)
        im = snap(b)
        v = b.eval("(() => { const v = window.__ship.cameras.main.worldView; return [v.x, v.y, v.width, v.height]; })()")
        im.save(os.path.join(OUT, f"c-{n}.png")); print(n, [round(a) for a in v], b.eval("[Math.round(window.__ship.player.x), Math.round(window.__ship.player.y)]"))
finally:
    b.close()
