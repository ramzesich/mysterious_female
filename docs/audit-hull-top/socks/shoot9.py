# Finding 9: the funnel's three windsocks, at rest and in a gust, each close up.
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
def crop(b, im, wx, wy, w, h, k):
    v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
    x, y = int(wx - v[0]), int(wy - v[1])
    return im.crop((x, y, x + w, y + h)).resize((w * k, h * k), Image.NEAREST)
GUSTS = "(() => { const w = window.__ship.world; for (const m of w.movers) if (m.flappers && m.def && m.def.x0 === w.data.funnel.x0 - 0 || (m.flappers && m.flappers.length === 3 && !m.F)) return m; })()"
def until(b, phase):
    for _ in range(600):
        if b.eval(f"(g => g.phase(window.__ship.time.now))({GUSTS})") == phase: return
        b.wait(0.05)
b = P.Browser(stepped=True)
try:
    b.open("?play&at=funnel"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    socks = b.eval(f"({GUSTS}).flappers.map(f => [Math.round(f.img.x), Math.round(f.img.y)])")
    print("socks", socks)
    shots, closes = [], []
    for i, (sx, sy) in enumerate(socks):
        b.eval(f"(c => {{ c.stopFollow(); c.centerOn({sx + 40}, {sy + 20}); }})(window.__ship.cameras.main)"); b.wait(0.5)
        for ph in ("calm", "blow"):
            until(b, ph); b.wait(0.5 if ph == "blow" else 0.3)
            im = snap(b); im.save(os.path.join(OUT, f"sock{i+1}-{ph}.png")); shots.append(im)
            closes.append(crop(b, im, sx - 50, sy - 12, 100, 70, 3))
    w, h = shots[0].size
    s = Image.new("RGB", (w * 2 + 4, h * 3 + 8), "white")
    for i, im in enumerate(shots): s.paste(im, ((i % 2) * (w + 4), (i // 2) * (h + 4)))
    s.save(os.path.join(OUT, "socks-sheet.png"))
    cw, ch = closes[0].size
    c = Image.new("RGB", (cw * 2 + 6, ch * 3 + 12), "white")
    for i, im in enumerate(closes): c.paste(im, ((i % 2) * (cw + 6), (i // 2) * (ch + 6)))
    c.save(os.path.join(OUT, "socks-close.png"))
    print("errors", b.errors)
finally:
    b.close()
