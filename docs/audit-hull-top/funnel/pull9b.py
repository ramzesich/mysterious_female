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
rows = []
for side, did in ((+14, "engineer"), (-14, "engineer,horn")):
    b = P.Browser(stepped=True)
    try:
        b.open(f"?play&at=funnel&did={did}"); b.wait(1.5)
        b.eval("window.__ship.scareContact = () => false")
        hx = b.eval("window.__ship.world.data.topdeck.funnel.hornX"); top = -228
        b.teleport(hx + 4 + side, top); b.wait(0.8)
        b.tap("e")
        frames, wide = [], []
        for i in range(16):
            b.wait(0.07 if i < 12 else 0.25)
            im = snap(b)
            v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
            x, y = int(hx - 36 - v[0]), int(top - 100 - v[1])
            frames.append(im.crop((x, y, x + 72, y + 104)).resize((216, 312), Image.NEAREST))
            if i in (8, 11, 15): wide.append(im)
        rows.append(frames)
        for k, im in enumerate(wide): im.save(os.path.join(OUT, f"blast-{'r' if side > 0 else 'l'}-{k}.png"))
        print("errors", b.errors)
    finally:
        b.close()
s = Image.new("RGB", (8 * 220, 4 * 316), "white")
for r, frames in enumerate(rows):
    for i, f in enumerate(frames):
        s.paste(f, ((i % 8) * 220, (r * 2 + i // 8) * 316))
s.save(os.path.join(OUT, "pull-strip2.png"))
