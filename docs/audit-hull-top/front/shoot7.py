import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
from build_ship_map import floor_y, exact_x
OUT = os.path.dirname(os.path.abspath(__file__))
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
b = P.Browser(stepped=True)
try:
    b.open("?play&at=spinnaker")
    b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    for deck, m in ((12, 38), (12, 33), (11, 27)):
        b.teleport(exact_x(m), floor_y(deck)); b.wait(1.5)
        snap(b).save(os.path.join(OUT, f"play-{deck}-{m}.png"))
        print(deck, m, b.eval("[window.__ship.player.x, window.__ship.player.y]"))
    print("errors", b.errors)
finally:
    b.close()
