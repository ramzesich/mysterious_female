"""Draws the ship's side schematic, docs/ship-profile.svg, from tools/ship_layout.py: decks, stair
cores, the atrium and every venue at its position along the ship, bow on the left. Re-run after
editing the layout.

    python tools/draw_ship_profile.py
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

from ship_layout import ATRIUM, CORES, DECKS, EXTENT, FUNNEL, LENGTH, MAST, TRUNKS, VENUES

ROOT = Path(__file__).resolve().parent.parent

PX = 5          # pixels per metre
ROW = 30        # pixels per deck
LEFT, RIGHT = 70, 70
TOP = 110       # room for the funnel, mast and core labels

FILL = {
    "venue": "#cfe3f0", "outdoor": "#d6ecd0", "cabins": "#ececec", "crew": "#f3d9c9",
    "start": "#ffe08a", "finale": "#f7bdbd",
}


def x(m):
    return LEFT + m * PX


def row_top(deck):
    return TOP + (DECKS[-1] - deck) * ROW


def text(tx, ty, s, size=9, anchor="middle", color="#1d2b53", weight="normal"):
    return (f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{color}" font-weight="{weight}">{escape(s)}</text>')


def build():
    width = LEFT + LENGTH * PX + RIGHT
    bottom = row_top(DECKS[0]) + ROW
    height = bottom + 95
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>']

    # Sea and hull below deck 3.
    out.append(f'<rect x="0" y="{bottom + 14}" width="{width}" height="{height - bottom - 14}" fill="#dceefa"/>')
    f3, a3 = EXTENT[3]
    out.append(f'<polygon points="{x(f3):.0f},{bottom} {x(a3):.0f},{bottom} {x(a3 - 4):.0f},{bottom + 26} '
               f'{x(f3 + 14):.0f},{bottom + 26}" fill="#8aa1b5"/>')

    # Funnel and mast above the top deck.
    top12 = row_top(12)
    out.append(f'<rect x="{x(FUNNEL[0]):.0f}" y="{top12 - 60}" width="{(FUNNEL[1] - FUNNEL[0]) * PX}" '
               f'height="60" fill="#2b5d8a"/>')
    out.append(text((x(FUNNEL[0]) + x(FUNNEL[1])) / 2, top12 - 26, "Funnel", 10, color="#ffffff"))
    out.append(f'<rect x="{x(MAST[0]):.0f}" y="{top12 - 40}" width="{(MAST[1] - MAST[0]) * PX}" '
               f'height="40" fill="#7b8fa3"/>')
    out.append(text((x(MAST[0]) + x(MAST[1])) / 2, top12 - 44, "Mast", 9))

    # Each deck: its extent, then the venues on it.
    for deck in DECKS:
        y0 = row_top(deck)
        fwd, aft = EXTENT[deck]
        if deck == 3:
            out.append(f'<rect x="{x(fwd):.0f}" y="{y0}" width="{(aft - fwd) * PX}" height="{ROW}" '
                       f'fill="#c9c9c9" stroke="#ffffff"/>')
            out.append(text((x(fwd) + x(aft)) / 2, y0 + 19, "Deck 3: visible below deck 4, not playable",
                            9, color="#555555"))
        else:
            out.append(f'<rect x="{x(fwd):.0f}" y="{y0}" width="{(aft - fwd) * PX}" height="{ROW}" '
                       f'fill="#f7f7f7" stroke="#ffffff"/>')
        out.append(text(LEFT - 12, y0 + 19, str(deck), 11, "end", weight="bold"))
        out.append(text(x(LENGTH) + 12, y0 + 19, str(deck), 11, "start", weight="bold"))

    for deck, a, b, name, kind in VENUES:
        y0 = row_top(deck)
        out.append(f'<rect x="{x(a):.0f}" y="{y0 + 2}" width="{(b - a) * PX}" height="{ROW - 4}" '
                   f'rx="2" fill="{FILL[kind]}"/>')
        bumbot = re.search(r"\(Bumbot: [^)]*\)", name)
        label = re.sub(r"\s*\(Bumbot: [^)]*\)", "", name)
        weight = "bold" if bumbot or kind in ("start", "finale") else "normal"
        color = "#888888" if kind == "cabins" else "#1d2b53"
        out.append(text((x(a) + x(b)) / 2, y0 + 19, ("★ " if bumbot else "") + label, 9, color=color,
                        weight=weight))

    # The atrium, open through decks 5-9.
    a, b = ATRIUM["span"]
    lo, hi = ATRIUM["decks"]
    out.append(f'<rect x="{x(a):.0f}" y="{row_top(hi) + 2}" width="{(b - a) * PX}" '
               f'height="{(hi - lo + 1) * ROW - 4}" fill="#fff1c2" stroke="#e0c060" stroke-dasharray="3,2"/>')
    out.append(text((x(a) + x(b)) / 2, row_top(7) + 19, "Atrium", 9, weight="bold"))
    out.append(text((x(a) + x(b)) / 2, row_top(5) + 19, "Café", 9))

    # Stair-and-elevator cores, through every deck.
    for name, (a, b) in CORES.items():
        out.append(f'<rect x="{x(a):.0f}" y="{row_top(12)}" width="{(b - a) * PX}" '
                   f'height="{bottom - row_top(12)}" fill="#2b5d8a" opacity="0.85"/>')
        cx = (x(a) + x(b)) / 2
        # Under the hull, where nothing else is: the forward and midship cores are close together.
        dy = 52 if name == "midship" else 40
        out.append(text(cx, bottom + dy, f"{name} stairs + lifts", 9, weight="bold"))

    # Escape trunks: the shaft, with a door mark on each deck that has one.
    for name, m, decks, opts in TRUNKS:
        out.append(f'<line x1="{x(m):.1f}" y1="{row_top(max(decks)) + 4}" x2="{x(m):.1f}" '
                   f'y2="{row_top(min(decks)) + ROW - 4}" stroke="#e07a1f" stroke-width="2"/>')
        for deck in decks:
            out.append(f'<rect x="{x(m) - 3:.1f}" y="{row_top(deck) + ROW - 12}" width="6" height="8" '
                       f'fill="#e07a1f"/>')

    # Ends, scale and legend.
    out.append(text(LEFT, 24, "◀ FORWARD (bow)", 13, "start", weight="bold"))
    out.append(text(x(LENGTH), 24, "AFT (stern) ▶", 13, "end", weight="bold"))
    out.append(text(width / 2, 24, "Norwegian Sun, as laid out in the game", 13, weight="bold"))
    for m in range(0, LENGTH + 1, 50):
        out.append(f'<line x1="{x(m):.0f}" y1="{height - 30}" x2="{x(m):.0f}" y2="{height - 24}" stroke="#555"/>')
        out.append(text(x(m), height - 12, f"{m} m", 9, color="#555555"))
    legend = [("Indoor venue", FILL["venue"]), ("Outdoor", FILL["outdoor"]), ("Cabins", FILL["cabins"]),
              ("Crew only", FILL["crew"]), ("Start", FILL["start"]), ("Finale", FILL["finale"])]
    lx = LEFT
    for label, color in legend:
        out.append(f'<rect x="{lx}" y="40" width="12" height="12" fill="{color}" stroke="#bbb"/>')
        out.append(text(lx + 17, 50, label, 10, "start"))
        lx += 110
    out.append(text(lx + 4, 50, "★ Bumbot near-catch", 10, "start", weight="bold"))
    lx += 130
    out.append(f'<rect x="{lx}" y="40" width="6" height="12" fill="#e07a1f"/>')
    out.append(text(lx + 11, 50, "Escape trunk (ladder doors)", 10, "start"))
    out.append("</svg>")

    path = ROOT / "docs" / "ship-profile.svg"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
