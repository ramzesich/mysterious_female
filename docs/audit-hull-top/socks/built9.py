# Finding 9 built: the generated windsocks (try B) in the game as built, through one gust round each (5 s at 10 frames a
# second, 2x): the funnel's stairway (its bend's sock and its foot's, moved forward) and top; the bow's two in the
# finale's wind (after the alarm): the mooring deck's at the stem and the Spinnaker balcony's.
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
FUNNEL = "window.__ship.world.movers.find(m => m.flappers && m.flappers.length === 3 && !m.F)"
BOW = "window.__ship.world.movers.find(m => m.flappers && m.F)"
def record(b, G, crop, frames_n=52):
    ph = lambda: b.eval(f"(g => g.phase(window.__ship.time.now))({G})")
    for _ in range(400):
        if ph() != "calm": break
        b.wait(0.05)
    for _ in range(400):
        if ph() == "calm": break
        b.wait(0.05)
    out = []
    for i in range(frames_n):
        im = snap(b); v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
        x0, y0, w, h = crop; x, y = int(x0 - v[0]), int(y0 - v[1])
        out.append(im.crop((x, y, x + w, y + h)).resize((w * 2, h * 2), Image.NEAREST))
        b.wait(0.1 - 1/60)
    return out
def save(name, frames):
    frames[0].save(os.path.join(OUT, f"{name}.gif"), save_all=True, append_images=frames[1:], duration=100, loop=0)
    pick = [frames[i] for i in (5, 34, 44)]; w, h = pick[0].size
    s = Image.new("RGB", (3 * (w + 4), h), "white")
    for i, f in enumerate(pick): s.paste(f, (i * (w + 4), 0))
    s.save(os.path.join(OUT, f"{name}-phases.png"))
b = P.Browser(stepped=True)
try:
    b.open("?play&at=bow&did=alarm"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    b.teleport(600, 1136); b.wait(1.0)
    # (Her on the mooring deck, the camera on the balcony: standing on it starts the sunset's scene.)
    b.eval("(c => { c.stopFollow(); c.centerOn(1700, 520); })(window.__ship.cameras.main)"); b.wait(0.5)
    save("built-bow-balcony", record(b, BOW, (1595, 465, 180, 110)))
    print("errors", b.errors)
finally:
    b.close()
