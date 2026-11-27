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
        frames = []; seen = set()
        for i in range(40):
            b.wait(1/60 * 3)
            st = b.eval("(s => { const h = s.world.story?.cordHandle || Object.values(s.world).find(v => v && v.cordHandle)?.cordHandle; const a = s.player.anims; return [a.currentAnim && a.currentAnim.key, a.currentFrame && a.currentFrame.index, s.player.x, s.player.flipX]; })(window.__ship)")
            key = (st[0], st[1])
            if st[0] != 'her-pull' or key in seen: continue
            seen.add(key)
            im = snap(b)
            v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
            x, y = int(hx - 10 - v[0]), int(top - 80 - v[1])
            frames.append(im.crop((x, y, x + 36, y + 50)).resize((216, 300), Image.NEAREST))
        print(side, "frames", sorted(seen), "her", st)
        rows.append(frames)
        print("errors", b.errors)
    finally:
        b.close()
s = Image.new("RGB", (5 * 220, 2 * 304), "white")
for r, frames in enumerate(rows):
    for i, f in enumerate(frames[:5]): s.paste(f, (i * 220, r * 304))
s.save(os.path.join(OUT, "fist-frames.png"))
