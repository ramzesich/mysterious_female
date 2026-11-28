"""The row she chooses from, all fifteen books, she sitting in the Library's armchair: the canvas at full size."""
import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    return Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
b = P.Browser(stepped=True)
try:
    b.open("?play&at=library&books=all", start=None); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    c = b.eval("(t => [t.x, t.y])(window.__ship.world.things.find(t => t.id === 'sec_chair'))")
    b.teleport(c[0], c[1]); b.wait(0.6)
    b.tap("e"); b.wait(2.5)
    print(b.eval("JSON.stringify(window.__ship.world.library.choosing && window.__ship.world.library.choosing.at)"))
    snap(b).save(os.path.join(OUT, "row-full.png"))
    print("errors", b.errors)
finally:
    b.close()
