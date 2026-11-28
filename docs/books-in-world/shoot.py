"""Every book lying in the world to be picked up (2026-11-28), each in place in the game's own view, she beside it."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image, ImageDraw
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"
def snap(b):
    b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
# (book, the start link's query, she stands this many px to its side)
BOOKS = [(2, "?play&at=walkway", -40), (3, "?play&at=theatre", -40), (5, "?play&at=cabin", -40), (6, "?play&at=deck5", -40),
         (8, "?play&at=sundeck&did=engineer,horn", -50), (10, "?play&at=bridge", -40), (11, "?play&at=walkway", -40),
         (14, "?play&at=captain", -40), (15, "?play&at=kids&did=catch", 40)]
b = P.Browser(stepped=True)
try:
    for n, q, side in BOOKS:
        b.open(q, start=None); b.wait(1.0)
        b.eval(f"{S}.scareContact = () => false")
        t = json.loads(b.eval(f"JSON.stringify((t => t && {{x: t.x, y: t.y, route: t.route, shown: t.items?.some(i => i.visible)}})({S}.world.things.find(t => t.id === 'book_{n}')))"))
        floor = b.eval(f"(t => t.floorY ?? null)({S}.world.things.find(t => t.id === 'book_{n}'))")
        y = floor or t["y"]
        b.teleport(t["x"] + side, y, t["route"] or "inside"); b.wait(1.5)
        cam = json.loads(b.eval(f"JSON.stringify([{S}.cameras.main.worldView.x, {S}.cameras.main.worldView.y, {S}.route, {S}.player.x, {S}.player.y])"))
        bx = json.loads(b.eval(f"JSON.stringify((t => (t.items || []).map(i => {{ const r = i.getBounds(); return [r.x, r.y, r.width, r.height]; }}))({S}.world.things.find(t => t.id === 'book_{n}')))"))
        im = snap(b)
        im.save(os.path.join(OUT, f"book-{n:02d}.png"))
        json.dump({"cam": cam[:2], "boxes": bx, "thing": t}, open(os.path.join(OUT, f"book-{n:02d}.json"), "w"))
        print(n, t, cam)
    print("errors", b.errors)
finally:
    b.close()
