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
    b.open("?play&at=funnel")
    b.wait(4)
    b.eval("window.__ship.scareContact = () => false")
    for dusk in (0, 1):
        b.eval(f"window.__ship.setDusk({dusk})")
        frames = []
        for i in range(80):
            b.wait(0.1)
            frames.append(snap(b))
        frames[0].save(os.path.join(OUT, f"new-{dusk}.png"))
        frames[40].save(os.path.join(OUT, f"new-{dusk}-b.png"))
        frames[0].save(os.path.join(OUT, f"new-{dusk}.gif"), save_all=True, append_images=frames[1:], duration=100, loop=0)
    print("errors", b.errors)
finally:
    b.close()
