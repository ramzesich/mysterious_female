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
b = P.Browser(stepped=True)
try:
    b.open("?play&at=funnel")
    b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    b.eval("window.__ship.smoke.forEach(t => { t.pause(); t.targets[0].setVisible(false); })")
    b.eval("window.__ship.player.setAlpha(0)")
    b.eval("(c => { c.stopFollow(); c.centerOn(9238, -388); })(window.__ship.cameras.main)")
    b.wait(0.5)
    wv = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
    for dusk in (0, 1):
        b.eval(f"window.__ship.setDusk({dusk})"); b.wait(0.3)
        snap(b).save(os.path.join(OUT, f"src-{dusk}.png"))
    json.dump({"view": wv}, open(os.path.join(OUT, "src.json"), "w")); print(wv, b.errors)
finally:
    b.close()
