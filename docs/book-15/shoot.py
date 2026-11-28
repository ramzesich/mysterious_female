"""Book 15 in the running game: its cover as she gets it, the row she chooses from, its page (2026-11-28)."""
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
    b.open("?play&at=library&books=12,13,14"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    b.eval("window.__skipCloseups = false; window.__ship.world.cover(15)"); b.wait(1.0)
    snap(b).save(os.path.join(OUT, "cover.png"))
    b.tap("e"); b.wait(1.0)
    b.eval("window.__skipCloseups = true; window.__ship.world.library.got(15); window.__ship.world.library.choose([12,13,14,15], 3)"); b.wait(0.8)
    snap(b).save(os.path.join(OUT, "row.png"))
    b.tap("e"); b.wait(1.0)
    snap(b).save(os.path.join(OUT, "page.png"))
    print("errors", b.errors)
finally:
    b.close()
