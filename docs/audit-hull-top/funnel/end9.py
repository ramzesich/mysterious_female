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
    b.open("?play&at=funnel")
    b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    f = b.eval("(f => [f.x0, f.x1, f.y])(window.__ship.world.data.funnel)")
    print("funnel", f)
    b.teleport(f[1] - 60, f[2]); b.wait(1.5)
    snap(b).save(os.path.join(OUT, "end-now.png"))
    # walk right into the stop
    b.hold("right", 1.0); b.wait(0.5)
    print("stopped at", b.eval("window.__ship.player.x"), "x1", f[1])
    snap(b).save(os.path.join(OUT, "end-stop.png"))
    print("errors", b.errors)
finally:
    b.close()
