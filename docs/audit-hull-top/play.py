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

PLACES = sys.argv[1].split(",")
dusk = "--dusk" in sys.argv
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12&cards=all")
    b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    if dusk: b.eval("window.__ship.setDusk(1)")
    for p in PLACES:
        b.eval(f"window.__ship.spawnAt(window.__ship.places['{p}'])")
        b.wait(2.0)
        im = snap(b)
        name = f"p-{p}{'-dusk' if dusk else ''}.png"
        im.save(os.path.join(OUT, name)); print(name, im.size)
    print("errors", b.errors)
finally:
    b.close()
