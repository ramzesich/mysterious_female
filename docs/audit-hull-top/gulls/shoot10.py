# Finding 10: the bow's two flocks of gulls (before the horn), the game's full view and close, she standing by each.
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
    b.open("?play&at=spinnaker"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    for name, (hx, x0, y0, w, h) in {"pool": (3385, 3230, 340, 310, 90), "screen": (2292, 2050, 280, 490, 50)}.items():
        b.teleport(hx, 416); b.wait(1.2)
        print(name, b.eval("[window.__ship.player.x, window.__ship.player.y]"))
        im = snap(b); im.save(os.path.join(OUT, f"{name}.png"))
        v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
        x, y = int(x0 - v[0]), int(y0 - v[1])
        k = 3 if w < 400 else 2
        im.crop((x, y, x + w, y + h)).resize((w * k, h * k), Image.NEAREST).save(os.path.join(OUT, f"{name}-close.png"))
    print("errors", b.errors)
finally:
    b.close()
