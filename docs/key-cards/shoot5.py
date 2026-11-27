import sys, io, base64, os, json
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
def cam(b): return json.loads(b.eval("JSON.stringify([window.__ship.cameras.main.worldView.x, window.__ship.cameras.main.worldView.y])"))
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck5"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    b.teleport(8462, 1424); b.wait(1.5)
    b.tap("e"); b.wait(0.25)
    im = snap(b); im.save(os.path.join(OUT, "n-reader.png"))
    im.crop((170, 40, 330, 170)).resize((480, 390), Image.NEAREST).save(os.path.join(OUT, "n-reader-x3.png"))
    b.wait(2.0)
    b.eval("window.__skipCloseups = true; ['hk','deck','ent','off'].forEach(c => window.__ship.progress.open('cards', c))")
    b.wait(3.0)
    im = snap(b); im.save(os.path.join(OUT, "n-hud.png"))
    im.crop((0, 0, 120, 50)).resize((480, 200), Image.NEAREST).save(os.path.join(OUT, "n-hud-x4.png"))
    print("errors", b.errors)
finally:
    b.close()
