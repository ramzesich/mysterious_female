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
    b.open("?play&at=deck12")
    b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    x0, y0 = b.eval("[window.__ship.player.x, window.__ship.player.y]")
    print("start", x0, y0, (x0/48-10))
    snap(b).save(os.path.join(OUT, "play-113.png"))
    for m in (106, 119):
        b.teleport((m+10)*48, y0); b.wait(1.5)
        snap(b).save(os.path.join(OUT, f"play-{m}.png"))
    b.eval("(() => { const s = window.__ship; if (!s.overview) s.enterOverview(); s.uiLayer.setVisible(false); })()")
    b.wait(1.0)
    cam = "window.__ship.cameras.main"
    b.eval(f"{cam}.setZoom(1)")
    b.eval(f"{cam}.centerOn({(113+10)*48}, {y0-40})"); b.wait(0.5)
    snap(b).save(os.path.join(OUT, "out-113.png"))
    print("errors", b.errors)
finally:
    b.close()
