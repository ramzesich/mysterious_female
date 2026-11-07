"""Builds the ship's art atlas (assets/ship/ship.png + .json, Phaser's JSON-hash atlas format) from
the raw PixelLab frames kept in assets/source/ship/ (GAME_DESIGN.md §2.1, §5.3).

Every piece is snapped to Resurrect 64. Doors are fitted to her scale (§5.4) by repeating plain
rows and dropping plain columns, so nothing is resampled. Every piece also gets a muted twin,
"<name>-bg", faded toward the corridor wall, for the background layer: props behind the action
never read as interactive (§2.1). The muted twins are not snapped back to the palette: the nearest
palette colour to a faded terracotta is a salmon pink, so they keep their faded hue instead.

Sources (PixelLab 1-direction objects, sidescroller view, Resurrect 64 palette, 2026-11-02):
    doors-1/   object d9b861cb-8039-4298-8c0f-7a1fc4c43861, 16 doors, 85px canvas
    props-1/   object 54a30b88-6f96-4b26-9999-a023a0f2a8e2, 64 props, 32px canvas
    props-2/   object 96d63a62-142f-4bd2-bc2b-22f1232daf2f, 64 props, 32px canvas
    props-3/   object a7fdf27e-6193-4767-a661-0a25d536c3df, 64 props, 32px canvas: restaurants,
               café, lobby (2026-11-03, for deck 5)
    props-4/   object 88f0ed0d-37b0-407f-ab67-523f0d24288a, 64 props, 32px canvas: bar, library,
               photo studio, shops, nightclub, theatre (2026-11-03, for deck 6)
    tall-1/    object 084f5932-777f-4804-93b7-6773efa99d7c, 16 tall pieces, 64px canvas (deck 6)
    theatre-seat/  map object a388646f-b80d-403a-87ab-4446106a66dc, 48px (try-2 kept, unused)
    props-5/   object f8f4f1fa-4267-48b8-b9e6-725209ad5a70, 64 props, 32px canvas: plaques,
               paintings, bar, casino, shop, kids' club (2026-11-03, for deck 7)
    tall-2/    object 310360e6-4a51-4387-ab44-88d5cbecbeed, 16 tall pieces, 64px canvas (deck 7)
    casino/    map objects: roulette 4c864558-dfe5-47cc-b1df-eb529f809ceb, blackjack
               aa1f888b-8206-42fc-88f3-5c50eb6adcad: three-quarter views, replaced; casino-2/ and
               balcony-rail/ hold four more table tries and two balcony tries, unused
    casino-drawn/  drawn by tools/draw_casino.py in strict side view: the roulette and blackjack
               tables, the Stardust balcony's front
    bridge-1/  object 1db4def9-4b46-4b61-8aa1-cc309ed5fed0, 16 bridge pieces, 64px canvas (deck 10,
               2026-11-06), shrunk to her scale ("height")
    tall-3/    object 4aa9472f-752f-47c8-888f-fb21a2d41c18, 16 spa, salon and gym pieces, 64px canvas
               (deck 11, 2026-11-06)
    tall-4/    object 38f8dc2d-2715-4873-bc7d-e22ba5a3f60e, 16 pool deck, buffet and outdoor café
               pieces, 64px canvas (deck 11), the soft serve ice cream machine among them
    props-6/   object b0dbbf7a-10f0-4ee7-90c7-0a1f72a006c0, 64 props, 32px canvas: spa, gym, pool,
               buffet (deck 11)
    sauna/     map objects: try 1 c5ad8bd8-a350-4b8e-9635-eaa6b10ab2db (three-quarter view, unused),
               try 2 b6055af6-53c6-4648-9c06-a87129189bae (flat side view): both unused, an outdoor cabin
               (the user: the sauna is built into the spa; drawn by the game instead)
    tall-5/    object bad65107-81b0-46cc-83a0-9bd72cf5f983, 16 sports, sports bar, kids' pool and
               lounge pieces, 64px canvas (deck 12, 2026-11-07)
    tall-6/    object a2f3d441-ee4b-4d22-beb9-27ea4a50efef, 16 restaurant pieces: steakhouse, sushi,
               teppanyaki, bistro, cantina, 64px canvas (deck 12)
    props-7/   object 3ddc73b3-825a-4e68-8a89-02182e1df110, 64 props, 32px canvas: restaurants,
               sports, kids' pool, chapel (deck 12)

Run from the repo root:  python tools/build_ship_art.py
"""

import json
from pathlib import Path

from PIL import Image

from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "ship"
OUT = ROOT / "assets" / "ship"

CABIN_WOOD = (0xCD, 0x68, 0x3D)       # the plain cabin door's terracotta
WALL = (0xE9, 0xDF, 0xCC)             # the corridor wall that muted pieces fade toward
MUTE = 0.35

# name: (sheet, frame, fit, options). fit is (width, height) for doors, or None to keep the drawn
# size. Options: "fill", the door's body was drawn transparent and is filled with the cabin door's
# wood; "lever", the row of a closed door's lever in the source, so every handle on board ends up
# at the same height (LEVER pixels above the floor); "height", shrink the piece to this many px tall
# (box-resampled, then snapped back to the palette), when the sheet drew it too big for her;
# "from_x", drop the frame's columns left of this (a neighbour's end drawn into it); "join", the
# columns (from, to) of the next frame to add on the right, where the sheet drew one piece across two.
DOOR = (28, 74)                        # sized to her, like every door on board (§5.4)
LEVER = 36                             # about half the door's height, as on a real door
PIECES = {
    "door-cabin": ("doors-1", 1, DOOR, {"lever": 37}),
    "door-cabin-stickers-1": ("doors-1", 3, DOOR, {"fill": True, "lever": 36}),
    "door-cabin-stickers-2": ("doors-1", 12, DOOR, {"lever": 36}),
    "door-cabin-stickers-3": ("doors-1", 14, DOOR, {"fill": True, "lever": 36}),
    "door-cabin-ajar": ("doors-1", 5, DOOR, {}),
    "door-crew": ("doors-1", 6, DOOR, {"lever": 37}),
    "door-crew-ajar": ("doors-1", 7, DOOR, {}),
    "door-crew-exit": ("doors-1", 13, None, {}),
    "door-deck": ("doors-1", 8, DOOR, {"lever": 35}),
    "door-deck-open": ("doors-1", 15, DOOR, {}),
    "door-watertight": ("doors-1", 11, None, {}),
}
PROPS = [
    "club-chair-side", "club-chair", "bar-stool", "lounge-chair", "side-table", "life-ring",
    "life-ring-rail", "railing", "extinguisher", "picture-sea", "picture-ship", "picture-art",
    "sconce-round", "downlight", "exit-sign", "assembly-sign", "hose-cabinet", "telephone",
    "plant", "sunlounger", "outdoor-table", None, "ship-model", "towel-trolley", "service-cart",
    "bin", "deck-chair", None, "hard-hat", "tub-chair", "table-lamp", "sticker-palm",
    "porthole", "gauge", None, None, None, "bell", "liferaft", None, None, "towel-shelf",
    "towel-table", "wall-sconce", None, "axe-cabinet", "minibar", "safe", "luggage-rack",
    "life-jacket", "coat-stand", "binoculars", "first-aid", "desk", "chair", "clock", "dresser",
    "bedside-lamp", "notice-board", "wet-floor", "telegraph", "globe", None, "bed",
]
for i, name in enumerate(PROPS):
    if name:
        PIECES[name] = ("props-1", i, None, {})
# The second sheet: the side-view life ring for overboard (§5.6), and small pieces asked for with it.
PROPS_2 = {
    0: "life-ring-side", 1: "life-ring-side-2", 4: "fish-plate", 5: "fish-tray", 6: "pool-ladder",
    7: "pool-towels", 8: "drinks-tray", 9: "plates", 10: "bollard", 11: "cleat", 12: "ice-cream",
    13: "ice-cream-cup", 14: "towel-swan", 15: "rubber-duck", 17: "anchor", 19: "deck-chair-2",
    20: "sunlounger-2", 23: "key-card", 24: "captain-hat", 25: "sailor-cap", 28: "compass",
    30: "lantern", 34: "sunglasses", 36: "beach-ball", 37: "cocktail", 42: "cake", 43: "coffee",
    45: "suitcase", 46: "duffel-bag", 47: "map", 55: "bar-stool-2", 60: "trophy", 61: "dartboard",
    62: "poker", 63: "ship-cake",
}
for i, name in PROPS_2.items():
    PIECES[name] = ("props-2", i, None, {})
# The third sheet: deck 5's restaurants, the atrium café, Guest Services (the user's photos).
PROPS_3 = [
    "table-dinner", "table-flowers", "table-long", "dining-chair", "dark-chair", "dark-table-lamp",
    "cafe-table", "cafe-chair", "counter", "desk-screen", "brochure-stand", "menu-lectern", "easel-sign",
    "rope-barrier", "service-station", "dessert-trolley", "wine-trolley", "palm", "orchid",
    "espresso-machine", "pastry-case", "banquette", "armchair-cream", "bar-cart", "poster-beach",
    "poster-fjord", "poster-city", "world-map", "wall-clock", "sconce-cream", "chandelier",
    "lamp-pleated", "floor-lamp", "screen-divider", "high-chair", "breadsticks", "oil-vinegar",
    "wine-glasses", "candle", "rose-vase", "wine-bottle", "luggage-trolley", "suitcases",
    "info-screen", "info-kiosk", "water-dispenser", "sanitizer", "wet-floor-sign", "urn", "bust",
    "olive-tree", "wine-barrel", "painting-ship", "mirror-gilt", "music-stand", "sideboard",
    "ice-swan", "cake-stand", "coffee-tray", "fruit-bowl", "plate-stack", "flower-vase",
    "umbrella-stand", "counter-bell",
]
for i, name in enumerate(PROPS_3):
    PIECES[name] = ("props-3", i, None, {})
# The fourth sheet and the first tall one: deck 6 (the user's photos and NCL's plan). The
# front-facing armchairs and theatre seats are left out (the game sees things from the side).
PROPS_4 = [
    None, None, "bar-table", "green-lamp", "tan-bar-stool", "beer-taps", "whisky", "cocktail-glass",
    "brass-ceiling-lamp", "nautical-chart", "ships-wheel", "telescope", "captain-portrait",
    "ship-in-bottle", "ships-bell", "camera-tripod", "softbox", "photo-couple", "photo-sunset",
    "photo-family", "reading-chair", "reading-table", "book-stack", "bankers-lamp", "magazine-rack",
    "chess-table", "computer-desk", "office-chair", "printer", "jewellery-counter", "perfume-stand",
    "sunglasses-stand", "handbag-shelf", "tshirt-rack", "souvenir-shelf", "till", "shopping-bag",
    "watch-case", "teddy-sailor", "dj-decks", "disco-ball", "velvet-armchair", "cocktail-table",
    "speaker-stand", "velvet-stool", "neon-bar", None, "mic-stand", "guitar", "bass-guitar",
    "keyboard", "spotlight", "amplifier", "snare-drum", "red-rope", "podium", "leaflet-stand",
    "popcorn", "champagne-bucket", "teal-bar-chair", "brass-lantern", "world-map-small", "fern",
    "plaque-stand",
]
for i, name in enumerate(PROPS_4):
    if name:
        PIECES[name] = ("props-4", i, None, {})
TALL_1 = [
    "bookcase", "ship-cabinet", "back-bar", "chesterfield-sofa", "mannequin", "grand-piano",
    "drum-kit", None, "photo-backdrop", "shop-shelves", "dress-rack", "dj-booth", "velvet-sofa",
    "bar-counter", "speaker-stack", "palm-tall",
]
for i, name in enumerate(TALL_1):
    if name:
        PIECES[name] = ("tall-1", i, None, {})
PIECES["theatre-seat"] = ("theatre-seat", 0, None, {})
# Deck 7's sheets (NCL's plan and the user's photos). Left out: the sheet's casino tables (no felt,
# no wheel), a famous portrait, a garbled "welcome" sign.
PROPS_5 = [
    "plaque-shield", "plaque-medallion", "certificate", "plaque-lighthouse", "plaque-crown",
    "plaque-red", "painting-harbour", "welcome-card", "painting-abstract", None, "painting-sea",
    "painting-flowers", "painting-blue", "bronze-sculpture", "gallery-bench", "track-spot",
    "champagne", "champagne-flutes", "decanter", "deco-lamp", "leather-club-chair", "marble-table",
    "chrome-stool", "cigar-box", "chips", "dice", "cards", "casino-stool", "chip-rack",
    "perfume-display", "liquor-shelf", "shop-basket", "watch-stand", "chocolates", "beanbag-orange",
    "beanbag-blue", "kids-chair", "kids-table", "toy-blocks", "rocking-horse", "toy-train",
    "teddy", "toy-box", "controller", "dartboard-2", "headphones", "cushion", "board-game",
    "cactus", "kids-drawing", "pin-map", "lifebuoy-deco", "porthole-mirror", "wheel-clock",
    "cruise-model", None, "table-sign", "jackpot-sign", "carpet-end", "rope-post", "monstera",
    "wall-tv", "vending-machine", "ice-cream-sign",
]
for i, name in enumerate(PROPS_5):
    if name:
        PIECES[name] = ("props-5", i, None, {})
TALL_2 = [
    "slot-side", "slot-pair", None, None, "arcade-cabinet", "claw-machine", "pinball", "foosball",
    "air-hockey", "atm", "easel-painting", "tv-console", "play-kitchen", "dancer-statue",
    "beanbags", "kids-bookshelf",
]
for i, name in enumerate(TALL_2):
    if name:
        PIECES[name] = ("tall-2", i, None, {})
PIECES["roulette"] = ("casino-drawn", 0, None, {})
PIECES["blackjack"] = ("casino-drawn", 1, None, {})
PIECES["balcony-front"] = ("casino-drawn", 2, None, {})
# Deck 10's bridge (2026-11-06): the sheet drew everything about her height; each is shrunk to its
# real size next to her (59 px, about 1.65 m).
BRIDGE_1 = [
    ("bridge-console", 46), ("helm-console", 44), ("captain-chair", 50), ("officer-chair", 38),
    ("engine-telegraph", 42), ("radar-pedestal", 46), ("chart-table", 34), ("ecdis-stand", 46),
    ("binnacle", 44), ("bridge-monitors", None), ("radio-desk", 40), ("clock-barometer", None),
    ("wing-console", 40), ("coffee-counter", 44), ("alarm-panel", 59), ("logbook-lectern", 42),
]
for i, (name, h) in enumerate(BRIDGE_1):
    PIECES[name] = ("bridge-1", i, None, {"height": h} if h else {})
# Deck 11's sheets (NCL's plan, the user's photos, 2026-11-06), the tall pieces shrunk to her scale.
TALL_3 = [
    ("treadmill", 50), ("exercise-bike", 44), ("rowing-machine", 30), ("weight-bench", 42),
    ("dumbbell-rack", 34), ("cross-trainer", 56), ("massage-table", 30), ("sauna-bench", 36),
    ("sauna-stove", 28), ("salon-chair", 40), ("hood-dryer", 52), ("salon-mirror", 36),
    ("spa-desk", 40), ("manicure-table", 40), ("yoga-rack", 40), ("bamboo", 60),
]
TALL_4 = [
    ("hot-tub", 40), ("pool-bar", None), ("parasol", None), ("pool-shower", None),
    ("towel-cart", 36), ("buffet-hot", 44), ("buffet-salad", 44), ("juice-station", 42),
    ("coffee-station", 40), ("ice-cream-machine", 44), ("ice-cream-counter", 40),
    ("cafe-blue-chair", 34), ("cafe-wood-table", 27), ("wicker-chair", 32), ("round-white-table", 27),
    ("planter-palm", None),
]
for sheet, pieces in (("tall-3", TALL_3), ("tall-4", TALL_4)):
    for i, (name, h) in enumerate(pieces):
        PIECES[name] = (sheet, i, None, {"height": h} if h else {})
PROPS_6 = [
    "spa-towels", "oil-bottles", "spa-candle", "spa-stones", "cucumber-water", "bathrobe",
    "spa-slippers", "hair-dryer", "shampoo", "comb-jar", "nail-polish", "lotion", "dumbbells",
    "kettlebell", "gym-bottle", "yoga-mat", "gym-towel", "medicine-ball", "sunscreen", "flip-flops",
    "beach-bag", "swim-ring", "pool-noodle", "sun-hat", "striped-towel", "umbrella-cocktail",
    "beer-bucket", "fruit-tray", "salad-bowl", "bread-basket", "cake-slice", "pizza", "sushi",
    "eggs-bacon", "pancakes", "coffee-cup", "orange-juice", "water-glass", "cutlery-napkin",
    "napkin-holder", "salt-pepper", "ketchup-mustard", "white-plates", "tray-stack", "cone", "sundae",
    "cone-stack", "sprinkles", "chafing-dish", "soup-tureen", "fruit-bowl-2", "cheese-board",
    "croissants", "lemonade", "iced-coffee", "teapot", "small-plant", "bud-vase", "life-ring-rope",
    "whistle", "thermometer", "folded-umbrella", "chalkboard", "fish-lemon",
]
# Drawn about 28 px whatever they are: each shrunk to its real size next to her (a cup is a few px).
PROPS_6_HEIGHT = {
    "spa-towels": 10, "oil-bottles": 9, "spa-candle": 7, "spa-stones": 8, "cucumber-water": 10,
    "bathrobe": 30, "spa-slippers": 5, "hair-dryer": 9, "shampoo": 9, "comb-jar": 9, "nail-polish": 5,
    "lotion": 8, "dumbbells": 9, "kettlebell": 10, "gym-bottle": 9, "yoga-mat": 8, "gym-towel": 8,
    "medicine-ball": 11, "sunscreen": 7, "flip-flops": 4, "beach-bag": 14, "swim-ring": 18,
    "pool-noodle": 10, "sun-hat": 7, "striped-towel": 8, "umbrella-cocktail": 8, "beer-bucket": 11,
    "fruit-tray": 6, "salad-bowl": 6, "bread-basket": 7, "cake-slice": 6, "pizza": 5, "sushi": 5,
    "eggs-bacon": 4, "pancakes": 6, "coffee-cup": 5, "orange-juice": 6, "water-glass": 6,
    "cutlery-napkin": 7, "napkin-holder": 5, "salt-pepper": 5, "ketchup-mustard": 7, "white-plates": 10,
    "tray-stack": 9, "cone": 7, "sundae": 7, "cone-stack": 8, "sprinkles": 7, "chafing-dish": 8,
    "soup-tureen": 8, "fruit-bowl-2": 7, "cheese-board": 6, "croissants": 5, "lemonade": 9,
    "iced-coffee": 7, "teapot": 7, "small-plant": 12, "bud-vase": 9, "life-ring-rope": 22,
    "whistle": 4, "thermometer": 12, "folded-umbrella": 30, "chalkboard": 30, "fish-lemon": 6,
}
for i, name in enumerate(PROPS_6):
    PIECES[name] = ("props-6", i, None, {"height": PROPS_6_HEIGHT[name]})
# The main console runs on into the helm's frame (the user saw its end cut off): joined whole.
PIECES["bridge-console"][3]["join"] = (0, 18)
PIECES["helm-console"][3]["from_x"] = 22
# Deck 12's sheets (NCL's plan, the user's photos, 2026-11-07), shrunk to her scale.
TALL_5 = [
    ("basketball-hoop", 118), ("golf-net", 80), ("cue-rack", 48), ("kids-slide", 46),
    ("mushroom-fountain", 62), ("champs-bar", 40), ("sports-tv", 24), ("ceiling-fan", 12),
    ("navy-sofa", 30), ("cane-chair", 34), ("flower-pedestal", 50), ("trophy-cabinet", 64),
    ("beer-fridge", 60), ("champs-stool", 40), ("putting-flag", 30), ("deck-steps", 40),
]
TALL_6 = [
    ("teppanyaki-grill", 32), ("sushi-counter", 40), ("paper-lantern", 18), ("shoji-screen", 62),
    ("steak-booth", 42), ("wine-cabinet", 66), ("carving-trolley", 34), ("bistro-bar", 54),
    ("bistro-chair", 36), ("bistro-table", 28), ("cantina-bar", 40), ("mexican-chair", 38),
    ("saguaro", 54), ("pinata", 24), ("tequila-barrel", 30), ("mexican-table", 28),
]
for sheet, pieces in (("tall-5", TALL_5), ("tall-6", TALL_6)):
    for i, (name, h) in enumerate(pieces):
        PIECES[name] = (sheet, i, None, {"height": h})
        # tall-5 wrote each piece's name in its frame's top rows (all but the stool's): blanked
        # (`caption`, the rows to clear).
        if sheet == "tall-5" and name != "champs-stool":
            PIECES[name][3]["caption"] = 8
# Two of its names ran onto a second line (the user saw the mushroom's).
PIECES["cue-rack"][3]["caption"] = 13
PIECES["mushroom-fountain"][3]["caption"] = 12
PROPS_7 = [
    ("margarita", 8), ("tacos", 5), ("nachos", 6), ("guacamole", 6), ("sombrero", 8), ("maracas", 9),
    ("hot-sauce", 8), ("tequila", 10), ("sake-set", 8), ("chopsticks", 5), ("nigiri", 5),
    ("miso-soup", 6), ("soy-sauce", 7), ("fried-rice", 6), ("bonsai", 12), ("lucky-cat", 10),
    ("steak-plate", 5), ("red-wine", 8), ("creme-brulee", 5), ("macarons", 6), ("baguette", 6),
    ("jar-candle", 6), ("rose-glass", 11), ("pepper-grinder", 9), ("bouquet", 12), ("ring-cushion", 5),
    ("pillar-candle", 14), ("pew-bow", 10), ("basketball", 9), ("volleyball", 9), ("golf-bag", 32),
    ("golf-balls", 9), ("shuffle-disc", 3), ("beer-pint", 8), ("chicken-wings", 6), ("peanuts", 5),
    ("foam-finger", 12), ("football-scarf", 12), ("rubber-duck-2", 6), ("bucket-spade", 9),
    ("arm-bands", 6), ("water-pistol", 8), ("toy-crocodile", 10), ("goggles", 4), ("martini", 8),
    ("olives", 5), ("menu-card", 8), ("brass-lamp", 14), ("ice-bucket", 11), ("reserved-sign", 4),
    ("folded-napkin", 6), ("butter-bread", 6), ("water-jug", 9), ("small-cactus", 10),
    ("chili-string", 16), ("paper-fan", 8), ("iron-teapot", 7), ("rice-bowl", 5), ("knife-block", 9),
    ("salt-shaker", 6), ("dessert-plate", 6), ("leafy-plant", 14), ("round-clock", 14), ("tissue-box", 6),
]
for i, (name, h) in enumerate(PROPS_7):
    PIECES[name] = ("props-7", i, None, {"height": h})
# The hot tub was drawn with its bottom curving up as if seen from above: it stands flat on the deck
# (the user saw it hang in the air).
PIECES["hot-tub"][3]["flat"] = True
# The grand piano's far legs stopped short of the floor (the user saw it float, 2026-11-07).
PIECES["grand-piano"][3]["legs"] = 8


def load(sheet, frame, from_x=0, join=None, caption=0):
    img = Image.open(SRC / sheet / f"frame_{frame}.png").convert("RGBA")
    if caption:
        # The sheet wrote each piece's name across the frame's top rows: blanked.
        img.paste((0, 0, 0, 0), (0, 0, img.width, caption))
    img = img.crop((from_x, 0, img.width, img.height))
    if join:
        a, b = join
        rest = Image.open(SRC / sheet / f"frame_{frame + 1}.png").convert("RGBA").crop((a, 0, b, img.height))
        whole = Image.new("RGBA", (img.width + rest.width, img.height))
        whole.paste(img, (0, 0))
        whole.paste(rest, (img.width, 0))
        img = whole
    return img.crop(img.getbbox())


def flat_base(img):
    """Run each column of a piece down to its bottom row in its lowest colour, so it stands flat."""
    img = img.copy()
    px = img.load()
    for x in range(img.width):
        ys = [y for y in range(img.height) if px[x, y][3] > 128]
        if ys:
            for y in range(ys[-1] + 1, img.height):
                px[x, y] = px[x, ys[-1]]
    return img


def leg_base(img, reach):
    """Run each leg down to the bottom row: columns that end within `reach` px of it (the piano drawn
    a little in perspective, its far legs short of the floor); the rest stay as drawn."""
    img = img.copy()
    px = img.load()
    for x in range(img.width):
        ys = [y for y in range(img.height) if px[x, y][3] > 128]
        if ys and img.height - 1 - reach <= ys[-1] < img.height - 1:
            for y in range(ys[-1] + 1, img.height):
                px[x, y] = px[x, ys[-1]]
    return img


def shrink(img, height):
    """Box-resample a piece down to `height` px tall, keeping its proportions; the edge pixels the
    resample half-covers are either kept whole or dropped."""
    w = max(1, round(img.width * height / img.height))
    out = img.resize((w, height), Image.BOX)
    out.putalpha(out.getchannel("A").point(lambda a: 255 if a >= 128 else 0))
    return out


def fill_body(img):
    """Fill the transparent body inside a door's frame with cabin wood."""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] < 128:
                px[x, y] = (*CABIN_WOOD, 255)
    return img


def plain_runs(img, axis):
    """Indices of rows (axis 0) or columns (axis 1) identical to the next one."""
    n = img.height if axis == 0 else img.width
    line = (lambda i: img.crop((0, i, img.width, i + 1)).tobytes()) if axis == 0 else \
           (lambda i: img.crop((i, 0, i + 1, img.height)).tobytes())
    return [i for i in range(n - 1) if line(i) == line(i + 1)]


def grow(img, lo, hi):
    """Repeat one plain row between rows lo and hi (the middle one), or the middle row if none."""
    rows = [r for r in plain_runs(img, 0) if lo < r < hi] or [(lo + hi) // 2]
    r = rows[len(rows) // 2]
    top, rest = img.crop((0, 0, img.width, r + 1)), img.crop((0, r, img.width, img.height))
    grown = Image.new("RGBA", (img.width, img.height + 1))
    grown.paste(top, (0, 0))
    grown.paste(rest, (0, r + 1))
    return grown


def fit(img, width, height, lever=None):
    """Grow or shrink a door through its plain stretches, never resampling. With `lever`, rows go
    in below the lever until it sits LEVER pixels above the floor, the rest above it."""
    if lever is not None:
        while img.height - lever < LEVER and img.height < height:
            img = grow(img, lever + 3, img.height - 3)
        while img.height < height:
            img = grow(img, 3, lever - 3)
            lever += 1
    while img.height < height:
        img = grow(img, img.height // 2, img.height - 3)
    while img.height > height:
        rows = [r for r in plain_runs(img, 0) if 2 < r < img.height - 3]
        r = rows[len(rows) // 2]
        img = _drop(img, r, 0)
    while img.width > width:
        cols = [c for c in plain_runs(img, 1) if 2 < c < img.width - 3]
        if not cols:
            break
        img = _drop(img, cols[len(cols) // 2], 1)
    return img


def _drop(img, i, axis):
    if axis == 0:
        a, b = img.crop((0, 0, img.width, i)), img.crop((0, i + 1, img.width, img.height))
        out = Image.new("RGBA", (img.width, img.height - 1))
        out.paste(a, (0, 0))
        out.paste(b, (0, i))
    else:
        a, b = img.crop((0, 0, i, img.height)), img.crop((i + 1, 0, img.width, img.height))
        out = Image.new("RGBA", (img.width - 1, img.height))
        out.paste(a, (0, 0))
        out.paste(b, (i, 0))
    return out


def muted(img):
    px = img.load()
    out = img.copy()
    dst = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                dst[x, y] = (*(round(c + (w - c) * MUTE) for c, w in zip((r, g, b), WALL)), a)
    return out


def build():
    pieces = {}
    for name, spec in PIECES.items():
        sheet, frame, size, opts = spec
        img = load(sheet, frame, opts.get("from_x", 0), opts.get("join"), opts.get("caption", 0))
        if opts.get("legs"):
            img = leg_base(img, opts["legs"])
        if opts.get("flat"):
            img = flat_base(img)
        if opts.get("fill"):
            img = fill_body(img)
        if size:
            img = fit(img, *size, lever=opts.get("lever"))
        if opts.get("height"):
            img = shrink(img, opts["height"])
        img = palettize(img)
        pieces[name] = img
        pieces[f"{name}-bg"] = muted(img)

    # Shelf packing, tallest first, one pixel apart.
    order = sorted(pieces, key=lambda n: -pieces[n].height)
    width, x, y, shelf, frames = 512, 0, 0, 0, {}
    for name in order:
        img = pieces[name]
        if x + img.width > width:
            x, y, shelf = 0, y + shelf + 1, 0
        frames[name] = (x, y, img.width, img.height)
        x += img.width + 1
        shelf = max(shelf, img.height)
    atlas = Image.new("RGBA", (width, y + shelf))
    for name, (fx, fy, _, _) in frames.items():
        atlas.paste(pieces[name], (fx, fy))

    OUT.mkdir(parents=True, exist_ok=True)
    atlas.save(OUT / "ship.png")
    meta = {"frames": {n: {"frame": {"x": x, "y": y, "w": w, "h": h}, "rotated": False, "trimmed": False,
                           "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h}}
                       for n, (x, y, w, h) in frames.items()},
            "meta": {"image": "ship.png", "size": {"w": atlas.width, "h": atlas.height}, "scale": "1"}}
    (OUT / "ship.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote assets/ship/ship.png ({atlas.width}x{atlas.height}, {len(frames)} pieces)")
    for name in PIECES:
        if PIECES[name][2]:
            print(f"  {name}: {pieces[name].width}x{pieces[name].height}")


if __name__ == "__main__":
    build()
