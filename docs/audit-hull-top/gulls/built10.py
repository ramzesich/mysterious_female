# Finding 10 built: both flocks as the game now places them (no mock), a few moments apart (their poses change).
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
    rows = []
    for hx, x0, y0, w, h in ((2292, 2052, 280, 476, 50), (3425, 3225, 335, 400, 95)):
        b.teleport(hx, 416); b.wait(1.2)
        row = []
        for t in range(3):
            im = snap(b); v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
            x, y = int(x0 - v[0]), int(y0 - v[1]); row.append(im.crop((x, y, x + w, y + h)))
            b.wait(3.0)
        rows.append(row)
    W = max(r[0].width for r in rows) * 2
    s = Image.new("RGB", (W, sum((r[0].height * 2 + 4) * 3 + 10 for r in rows)), "white"); yy = 0
    for r in rows:
        for im in r: s.paste(im.resize((im.width * 2, im.height * 2), Image.NEAREST), (0, yy)); yy += im.height * 2 + 4
        yy += 10
    s.save(os.path.join(OUT, "built.png"))
    print("errors", b.errors)
finally:
    b.close()
