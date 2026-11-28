"""Each book before (its old place, no wash) and after (moved, washed at rest), enlarged 4x, she out of the way."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image, ImageDraw, ImageFont
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"
def snap(b):
    b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
BOOKS = [(2, "?play&at=walkway", -60), (3, "?play&at=theatre", -60), (5, "?play&at=cabin", -60), (6, "?play&at=deck5", -60),
         (8, "?play&at=sundeck&did=engineer,horn", -70), (10, "?play&at=bridge", -60), (11, "?play&at=walkway", -60),
         (14, "?play&at=captain", -60), (15, "?play&at=kids&did=catch", 60)]
MOVED = {8: (-2, 0), 10: (0, -1)}       # (before: where it was)
font = ImageFont.truetype("arial.ttf", 18)
rows = []
b = P.Browser(stepped=True)
try:
    for n, q, side in BOOKS:
        b.open(q, start=None); b.wait(1.0)
        b.eval(f"{S}.scareContact = () => false")
        T = f"{S}.world.things.find(t => t.id === 'book_{n}')"
        t = json.loads(b.eval(f"JSON.stringify((t => ({{x: t.x, y: t.y, route: t.route}}))({T}))"))
        b.teleport(t["x"] + side, t["y"], t["route"] or "inside"); b.wait(1.5)
        # (the glint off, so that both pictures are the book's own)
        b.eval(f"{T}.pick.glintOff = true; {S}.tweens.getTweensOf({T}.pick).forEach(x => x.pause())")
        dx, dy = MOVED.get(n, (0, 0))
        b.eval(f"{S}.highlight.restOff = true; {T}.pick.x += {dx}; {T}.pick.y += {dy}"); b.wait(0.1)
        r = json.loads(b.eval(f"JSON.stringify((o => {{ const r = o.getBounds(); return [r.x, r.y, r.width, r.height]; }})({T}.pick))"))
        cam = json.loads(b.eval(f"JSON.stringify([{S}.cameras.main.worldView.x, {S}.cameras.main.worldView.y])"))
        before = snap(b)
        b.eval(f"{S}.highlight.restOff = false; {T}.pick.x -= {dx}; {T}.pick.y -= {dy}"); b.wait(0.1)
        after = snap(b)
        cx, cy = r[0] - cam[0] + r[2] / 2, r[1] - cam[1] + r[3] / 2
        box = (int(cx - 30), int(cy - 18), int(cx + 30), int(cy + 18))
        rows.append((n, [im.crop(box).resize((240, 144), Image.NEAREST) for im in (before, after)]))
    print("errors", b.errors)
finally:
    b.close()
sheet = Image.new("RGB", (3 * (2 * 240 + 24) + 16, 3 * (144 + 30) + 8), (40, 40, 40))
g = ImageDraw.Draw(sheet)
for i, (n, (a, c)) in enumerate(rows):
    x, y = 8 + (i % 3) * (2 * 240 + 24), 4 + (i // 3) * (144 + 30)
    g.text((x, y), f"{i + 1}.  Book {n}:  before  |  after", font=font, fill=(255, 240, 200))
    sheet.paste(a, (x, y + 24)); sheet.paste(c, (x + 244, y + 24))
sheet.save(os.path.join(OUT, "before-after-x4.png"))
