"""Her four things in the world (2026-11-28), each in place in the game's own view, she beside it, ringed and numbered."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image, ImageDraw, ImageFont
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"
THINGS = [("keep_flag", "?play&at=shore5", -40, "Her flag of Ukraine: deck 5, the Restaurant Reservations desk, its far end"),
          ("keep_plant", "?play&at=maid6", -40, "Her plant (the Albuca): deck 6, the maid's cabin, the window sill (taken from the bed)"),
          ("keep_bookmark", "?play&at=deck9", -40, "Her bookmark in its book: deck 9, the guest cabin being cleaned"),
          ("keep_pad", "?play&at=theatre", -40, "Her massage pad: deck 7, the theatre, on a seat, under its arm")]
font = ImageFont.truetype("arial.ttf", 22)
tiles = []
b = P.Browser(stepped=True)
try:
    for k, (tid, q, side, label) in enumerate(THINGS, 1):
        b.open(q, start=None); b.wait(1.0)
        b.eval(f"{S}.scareContact = () => false")
        T = f"{S}.world.things.find(t => t.id === '{tid}')"
        t = json.loads(b.eval(f"JSON.stringify((t => ({{x: t.x, y: t.y, route: t.route}}))({T}))"))
        b.teleport(t["x"] + side, t["y"], t["route"] or "inside"); b.wait(1.5)
        box = json.loads(b.eval(f"JSON.stringify((r => [r.x, r.y, r.width, r.height])({T}.pick.getBounds()))"))
        cam = json.loads(b.eval(f"JSON.stringify([{S}.cameras.main.worldView.x, {S}.cameras.main.worldView.y])"))
        b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
        if b.taken: b.advance(1/60, draw=True)
        b.wait_for("window.__snap", timeout=10)
        im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
        im = im.resize((im.width // 2, im.height // 2), Image.NEAREST)
        big = im.resize((im.width * 2, im.height * 2), Image.NEAREST); g = ImageDraw.Draw(big)
        cx, cy = (box[0] - cam[0] + box[2] / 2) * 2, (box[1] - cam[1] + box[3] / 2) * 2
        r = max(box[2], box[3]) * 2 + 10
        g.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 214, 0), width=4)
        g.rectangle([0, 0, big.width, 34], fill=(20, 16, 24)); g.text((10, 5), f"{k}.  {label}", font=font, fill=(255, 240, 200))
        big.save(os.path.join(OUT, f"her-{k}.png")); tiles.append(big)
    print("errors", b.errors)
finally:
    b.close()
w, h = tiles[0].size
sheet = Image.new("RGB", (w + 4, 2 * (h // 2) + 4), (40, 40, 40))
for i, t in enumerate(tiles):
    sheet.paste(t.resize((w // 2, h // 2), Image.LANCZOS), ((i % 2) * (w // 2 + 4), (i // 2) * (h // 2 + 4)))
sheet.save(os.path.join(OUT, "her-four.png"))
