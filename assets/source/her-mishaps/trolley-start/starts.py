"""10c's start and end pictures (2026-11-17): her own standing sprite with the game's own room-service
trolley just ahead of her, its front to her (its handle, the stewardess's end, away); and the same with her lying on her belly past it (her tripfall's lying
frame), the end the clip is drawn toward. 192 x 112, the floor on row 104."""
import json, os
from PIL import Image
R = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
atlas = Image.open(os.path.join(R, "assets/ship/ship.png")).convert("RGBA")
fr = json.load(open(os.path.join(R, "assets/ship/ship.json")))["frames"]["service-cart"]["frame"]
cart = atlas.crop((fr["x"], fr["y"], fr["x"] + fr["w"], fr["y"] + fr["h"])).transpose(Image.FLIP_LEFT_RIGHT)   # its front to her, the handle away
her = Image.open(os.path.join(R, "assets/source/her-mishaps/paper-start/start-4a.png")).convert("RGBA")   # 80x80, feet row 73
lie = Image.open(os.path.join(R, "assets/source/her/tripfall/5.png")).convert("RGBA")                      # 96x96, floor row 74
W, H, FLOOR, CART = 192, 112, 104, 62
def base():
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(cart, (CART, FLOOR + 1 - cart.height))
    return img
start = base(); start.alpha_composite(her, (20, FLOOR - 73))
end = base(); end.alpha_composite(lie, (CART + cart.width + 3 - 27, FLOOR - 74))
here = os.path.dirname(os.path.abspath(__file__))
start.save(os.path.join(here, "start-10c.png")); end.save(os.path.join(here, "end-10c.png"))
print(start.getbbox(), end.getbbox(), cart.size)
