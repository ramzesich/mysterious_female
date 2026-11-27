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
def crop(b, im, wx, wy, w, h, k):
    v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
    x, y = int(wx - v[0]), int(wy - v[1])
    return im.crop((x, y, x + w, y + h)).resize((w * k, h * k), Image.NEAREST)
b = P.Browser(stepped=True)
try:
    b.open("?play&at=funnel&did=engineer"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    T = b.eval("(t => [t.hornX, t.toolboxX])(window.__ship.world.data.topdeck.funnel)"); top = -228
    hx, bx = T
    print("errors so far", b.errors)
    b.teleport(hx - 60, top); b.wait(1.2)
    im = snap(b); im.save(os.path.join(OUT, "built-horn.png"))
    c1 = crop(b, im, hx - 50, top - 125, 90, 128, 3)
    b.teleport(bx - 40, top); b.wait(1.2)
    im = snap(b); im.save(os.path.join(OUT, "built-box.png"))
    c2 = crop(b, im, bx - 30, top - 40, 60, 44, 4)
    # the pull, first time: she at the cord, E
    b.teleport(hx + 4, top); b.wait(0.8)
    b.tap("e"); b.wait(0.5)
    im = snap(b); im.save(os.path.join(OUT, "built-pull.png"))
    c3 = crop(b, im, hx - 50, top - 125, 90, 128, 3)
    s = Image.new("RGB", (c1.width + c2.width + c3.width + 24, max(c1.height, c3.height)), "white")
    s.paste(c1, (0, 0)); s.paste(c3, (c1.width + 12, 0)); s.paste(c2, (c1.width + c3.width + 24, 0))
    s.save(os.path.join(OUT, "built-close.png"))
    print("errors", b.errors)
finally:
    b.close()
