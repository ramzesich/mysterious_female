import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image, ImageDraw
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__)); TAG = sys.argv[1]
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    return Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
SPOTS = [("court", 7600, 370), ("sundeck", 6400, 370), ("kids", 3500, 370), ("terrace", 10900, 370)]
b = P.Browser(stepped=True)
try:
    b.open("?play&cards=all"); b.wait(1.0)
    b.eval("(() => { const s = window.__ship; s.enterOverview(true); s.uiLayer.setVisible(false); s.cameras.main.setZoom(1); })()"); b.wait(0.5)
    for n, x, y in SPOTS:
        b.eval(f"window.__ship.cameras.main.centerOn({x}, {y})"); b.wait(0.3)
        im = snap(b); w, h = im.size
        im.crop((w // 2 - 240, h // 2 - 50, w // 2 + 240, h // 2 + 50)).save(os.path.join(OUT, f"{TAG}-{n}.png"))
finally:
    b.close()
