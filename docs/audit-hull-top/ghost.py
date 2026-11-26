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
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12&cards=all"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    b.teleport(3380, 416, "inside")
    for t in (1, 3, 6):
        b.wait(t if t == 1 else t - (1 if t == 3 else 3))
        im = snap(b); im.save(os.path.join(OUT, f"g-{t}.png"))
        v = b.eval("(() => { const s = window.__ship; return [Math.round(s.player.y), s.mode, s.world?.currentDeck?.() ?? null]; })()")
        band = im.crop((0, 252, 480, 268)); px = list(band.getdata())
        dark = sum(1 for p in px if sum(p) < 600)
        print(t, v, "non-white px in band:", dark)
    # her on the floor beside the pool
    b.teleport(3200, 416, "inside"); b.wait(4)
    im = snap(b); im.save(os.path.join(OUT, "g-floor.png"))
    px = list(im.crop((0, 252, 480, 268)).getdata()); print("floor", sum(1 for p in px if sum(p) < 600))
finally:
    b.close()
