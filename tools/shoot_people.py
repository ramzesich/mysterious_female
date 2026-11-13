"""Every person in place in the game, close up, tiled into sheets (%TEMP%/bumbusik-playtest/
people-in-place-N.png): the look a wide screenshot does not give. She is put beside each for scale,
their deck is cut open, and everyone is shown whatever the story's state (a person who appears in
several places shows in all of them).

    python tools/shoot_people.py [person id ...]      (ids from tools/population.py; none: everyone)

What to look for is in CLAUDE.md, "Looking closely": proportions against her, which way they face
(towards what they use), what they overlap, what they stand or sit on, what is in their hands.
"""

import sys
import time

from PIL import Image, ImageDraw

import playtest as P
from build_ship_map import floor_y

W, H = 220, 110        # game px around each person


def main():
    # (Those named: two across, enlarged three times; everyone: three across, twice.)
    cols, zoom, per = (2, 3, 8) if len(sys.argv) > 1 else (3, 2, 18)
    b = P.Browser()
    tiles = []
    try:
        P.enter_region8(b)
        b.eval("(() => { const s = window.__ship, pe = s.world.people;"
               " pe.shown = p => p.route === 'inside' || p.route === s.route; pe.refresh(); })()")
        ids = sys.argv[1:] or b.eval("window.__ship.world.people.list.map(p => p.id)")
        for pid in ids:
            p = b.eval(f"(() => {{ const p = window.__ship.world.people.byId['{pid}'];"
                       " return p ? { x: p.sprite.x, y: p.y, route: p.route } : null; })()")
            if not p:
                print("not in the game:", pid)
                continue
            b.teleport(p["x"] + 60, p["y"], p["route"])
            b.eval("window.__ship.world.people.refresh()")
            time.sleep(1.2)
            deck = round(5 + (floor_y(5) - p["y"]) / 144) if p["route"] == "inside" else None
            tile = Image.open(b.close_up("people-in-place", p["x"] + 20, p["y"] - 40, W, H, zoom, deck))
            ImageDraw.Draw(tile).text((4, 4), pid, fill=(255, 255, 0))
            tiles.append(tile)
    finally:
        b.close()
    for n in range(0, len(tiles), per):
        part = tiles[n:n + per]
        sheet = Image.new("RGB", (cols * W * zoom, ((len(part) + cols - 1) // cols) * H * zoom))
        for i, tile in enumerate(part):
            sheet.paste(tile, ((i % cols) * W * zoom, (i // cols) * H * zoom))
        out = P.OUT / f"people-in-place-{n // per}.png"
        sheet.save(out)
        print(out, sheet.size)


if __name__ == "__main__":
    main()
