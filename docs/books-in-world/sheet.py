"""The nine books lying in the world, numbered, each ringed in its shot: one sheet and one picture each (2x)."""
import json, os  # (Hebrew reversed for the caption: PIL draws it left to right)
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.dirname(os.path.abspath(__file__))
WHERE = {2: "Harry Potter and the Chamber of Secrets: the lifeboat, on its bench",
         3: "Танґо смерті: the dancers' dressing room, on the dressing table",
         5: "Її війна: cabin 8206, on her bed",
         6: "Harry Potter and the Philosopher's Stone: deck 5, the brochure stand",
         8: "Niebieskie nitki: the old lady's sunbed, after the horn",
         10: "Боря, выйди с моря: the bridge, the chart table",
         11: "נערה במעיל כחול"[::-1] + ": the boat walkway's end, a life-jacket box",
         14: "Pachinko: deck 9, the officers' corridor's end, a console table",
         15: "Diary of a Wimpy Kid: Splash Academy's bookshelf, on the way home"}
font = ImageFont.truetype("arial.ttf", 22)
small = ImageFont.truetype("arial.ttf", 16)
tiles = []
for k, n in enumerate(WHERE, 1):
    im = Image.open(os.path.join(OUT, f"book-{n:02d}.png")).convert("RGB")
    d = json.load(open(os.path.join(OUT, f"book-{n:02d}.json")))
    big = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    g = ImageDraw.Draw(big)
    for x, y, w, h in d["boxes"]:
        cx, cy = (x - d["cam"][0] + w / 2) * 2, (y - d["cam"][1] + h / 2) * 2
        r = max(w, h) * 2 + 10
        g.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 214, 0), width=4)
    g.rectangle([0, 0, big.width, 34], fill=(20, 16, 24))
    g.text((10, 5), f"{k}.  Book {n}: {WHERE[n]}", font=font, fill=(255, 240, 200))
    big.save(os.path.join(OUT, f"{k}-book-{n:02d}.png"))
    tiles.append(big)
w, h = tiles[0].size
sheet = Image.new("RGB", (3 * w // 2 + 8, 3 * h // 2 + 8), (40, 40, 40))
for i, t in enumerate(tiles):
    sheet.paste(t.resize((w // 2, h // 2), Image.LANCZOS), ((i % 3) * (w // 2 + 4), (i // 3) * (h // 2 + 4)))
sheet.save(os.path.join(OUT, "all-nine.png"))
