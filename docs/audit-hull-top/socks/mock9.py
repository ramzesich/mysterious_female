# Finding 9: the generated windsock tries mocked up at the funnel's socks (old socks hidden), the stairway's foot one
# moved forward clear of the rail (the user's 3a).
import sys, io, base64, os
import numpy as np
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(OUT, "..", "..", "..", "assets", "source", "windsock", "tries")
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGBA")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
def view(b): return b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
def states(name):
    im = Image.open(os.path.join(SRC, name + ".png")).convert("RGBA"); a = np.array(im)
    on = a[:, :, 3] >= 128; cols = np.where(on.any(0))[0]
    groups, s0, pv = [], cols[0], cols[0]
    for c in cols[1:]:
        if c != pv + 1: groups.append((s0, pv)); s0 = c
        pv = c
    groups.append((s0, pv)); out = []
    for x0, x1 in groups:
        sub = a[:, x0:x1 + 1]; rows = np.where((sub[:, :, 3] >= 128).any(1))[0]; y0 = rows[0]
        pic = Image.fromarray(sub[y0:rows[-1] + 1].copy())
        s = np.array(pic); grey = (s[:, :, 3] >= 128) & (np.abs(s[:, :, 0].astype(int) - s[:, :, 2]) < 30)
        ys, xs = np.where(grey[:8]); out.append((pic, (int(round(xs.mean())), int(round(ys.mean())))))
    return out
TRIES = {"A": states("sheet-a"), "B": states("sheet-b")}
b = P.Browser(stepped=True)
try:
    shots = {}
    b.open("?play&at=stairway"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    b.hold("left", 0.25); b.wait(0.8)       # (she steps forward, off the moved pole)
    print("her", b.eval("[window.__ship.player.x, window.__ship.player.y]"))
    G = "window.__ship.world.movers.find(m => m.flappers && m.flappers.length === 3 && !m.F)"
    poles = b.eval(f"({G}).flappers.map(f => [Math.round(f.img.x - 1), Math.round(f.img.y - 1)])")   # pole tops
    b.eval(f"window.__ship.children.list.filter(o => o.type === 'Rectangle' && o.width === 2 && o.height === 40).forEach(o => o.setVisible(false)); ({G}).flappers.forEach(f => f.img.setVisible(false))")
    b.wait(0.3); shots["stair"] = (snap(b), view(b))
    b.open("?play&at=funnel"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false"); b.teleport(9690, -228); b.wait(1.0)
    b.eval(f"window.__ship.children.list.filter(o => o.type === 'Rectangle' && o.width === 2 && o.height === 40).forEach(o => o.setVisible(false)); ({G}).flappers.forEach(f => f.img.setVisible(false))")
    b.wait(0.3); shots["top"] = (snap(b), view(b))
    print("poles", poles)
    NEW3 = poles[2][0] - 46        # the stairway foot's sock moved forward
    places = [("stair", poles[0]), ("top", poles[1]), ("stair", (NEW3, poles[2][1]))]
    rows = []
    for t in ("A", "B"):
        for si, (pic, eye) in enumerate(TRIES[t]):
            frames = {k: v[0].copy() for k, v in shots.items()}
            for key, (px, py) in places:
                im = frames[key]; v = shots[key][1]
                sx, sy = int(px - v[0]), int(py - v[1])
                from PIL import ImageDraw
                ImageDraw.Draw(im).rectangle((sx, sy, sx + 1, sy + 39), fill=(232, 234, 236, 255))
                im.alpha_composite(pic, (sx + 1 - eye[0], sy - eye[1]))
            rows.append((t, si, frames))
    # crops: the stairway's two (x 8420..8700, y 95..285) and the top's (9650..9800, -330..-220), 2x
    def crop(key, frames, x0, y0, w, h):
        v = shots[key][1]; x, y = int(x0 - v[0]), int(y0 - v[1])
        return frames[key].crop((x, y, x + w, y + h)).resize((w * 2, h * 2), Image.NEAREST)
    tiles = [[crop("stair", f, 8360, 100, 340, 185), crop("top", f, 9680, -330, 130, 110)] for _, _, f in rows]
    tw, th = tiles[0][0].size; ow = tiles[0][1].size[0]
    sheet = Image.new("RGB", ((tw + ow + 16) * 3, (th + 8) * 2), "white")
    for i, (a, c) in enumerate(tiles):
        x = (i % 3) * (tw + ow + 16); y = (i // 3) * (th + 8)
        sheet.paste(a, (x, y)); sheet.paste(c, (x + tw + 4, y))
    sheet.save(os.path.join(OUT, "mock-tries.png"))
    print("errors", b.errors)
finally:
    b.close()
