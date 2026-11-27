import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__)); TAG = sys.argv[1]
def snap(b, half=True):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST) if half else im
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12&cards=all"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    for n, x in [("stand", 3600), ("swim", 3380), ("inside", 3150)]:
        b.teleport(x, 416, "inside"); b.wait(3)
        # the camera on the pool, so every shot frames it alike
        b.eval("(() => { const c = window.__ship.cameras.main; c.stopFollow(); c.centerOn(3390, 470); })()"); b.wait(0.2)
        snap(b).save(os.path.join(OUT, f"{TAG}-{n}.png"))
    # the outside view at 1:1 on the pool
    b.eval("(() => { const s = window.__ship; s.enterOverview(true); s.uiLayer.setVisible(false); const c = s.cameras.main; c.setZoom(1); c.centerOn(3390, 470); })()"); b.wait(0.5)
    im = snap(b, half=False); w, h = im.size
    im.crop((w//2 - 240, h//2 - 135, w//2 + 240, h//2 + 135)).save(os.path.join(OUT, f"{TAG}-outside.png"))
    print("errors", b.errors[:3])
finally:
    b.close()
