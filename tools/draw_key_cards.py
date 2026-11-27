"""The key cards' world pictures (the user, 2026-11-27: "redesign the access cards, their icons in the game world"),
drawn by rule in the close-up's own colours (`assets/source/closeups/key-card.png`, recoloured by
`tools/build_closeups.py`): the whole card in its colour, a white band where the close-up has it, its chip, the clip
and a navy lanyard. 8 x 12 px, a little bigger than life, as the other things she finds.

- `key-card-<card>.png`: upright, hung from a small loop of the lanyard over its clip (the user's loop A): the card
  in a giver's hand and flying to her (`world.handOver`, `tossOver`).
- `key-card-<card>-lying.png`: lying flat on a floor, seen a little from above, its top (the band) to the left and the
  lanyard in a loop beside it (the user's version 5): the Officer's card dropped on the sun deck in the horn's scene.

Into `assets/source/things/`; then run `tools/build_things.py`.

    python tools/draw_key_cards.py
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "source" / "things"

H = lambda s: tuple(bytes.fromhex(s)) + (255,)
NAVY, WHITE, CHIP, CLIP = H("323353"), H("ffffff"), H("b2ba90"), H("9babb2")
# The cards' colours: `CARD_COLOURS` in src/progression.js, `CARDS` in tools/build_closeups.py.
CARDS = {"deck": "4d9be6", "ent": "e83b3b", "hk": "1ebc73", "off": "f9c22b"}
# The loop over the clip (x on the card's 8 columns, y up from the clip's navy row).
LOOP = [(3, 1), (4, 1), (2, 2), (5, 2), (1, 3), (6, 3), (1, 4), (6, 4), (2, 5), (3, 5), (4, 5), (5, 5)]
# The lanyard lying in a loop beside the card (x, y on the lying picture), from its clip.
LYING_LOOP = [(12, 4), (13, 4), (14, 4), (15, 3), (16, 2), (17, 1), (18, 1), (19, 2), (19, 3), (18, 4), (17, 4), (16, 4)]


def upright(colour):
    fill = H(colour)
    top = max(y for _, y in LOOP) + 2
    im = Image.new("RGBA", (8, top + 12))
    px = im.load()
    for y in range(12):
        for x in range(8):
            if x in (0, 7) and y in (0, 11):
                continue
            px[x, top + y] = NAVY if (x in (0, 7) or y in (0, 11)) else fill
    for x in range(1, 7):
        for y in (2, 3):
            px[x, top + y] = WHITE
    px[5, top + 5] = CHIP
    px[3, top - 1] = px[4, top - 1] = CLIP
    px[3, top - 2] = px[4, top - 2] = NAVY
    for x, y in LOOP:
        px[x, top - 2 - y] = NAVY
    return im


def lying(colour):
    fill = H(colour)
    im = Image.new("RGBA", (20, 5))
    px = im.load()
    for x in range(12):
        for y in range(1, 5):
            if x in (0, 11) and y in (1, 4):
                continue
            px[x, y] = NAVY if (y in (1, 4) or x in (0, 11)) else fill
    for y in (2, 3):
        px[2, y] = px[3, y] = WHITE
    px[8, 2] = CHIP
    for x, y in LYING_LOOP:
        px[x, y] = NAVY
    px[12, 3] = CLIP
    return im


def main():
    for card, colour in CARDS.items():
        upright(colour).save(OUT / f"key-card-{card}.png")
        lying(colour).save(OUT / f"key-card-{card}-lying.png")
        print(f"key-card-{card}, key-card-{card}-lying")


if __name__ == "__main__":
    main()
