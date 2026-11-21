// A steel wire rope, as the drill's winch has wound on its drum (the user, 2026-11-21: "make it similar to the cable
// that's on the coil", then every boat's cables made the same): 3 px wide, its two edges dark, its middle a twist of
// light and dark every two rows, in the winch picture's own greys (tools/build_drill.py). Drawn into a Graphics from
// `y0` down to `y1` (both world px), centred on column `x`; the twist counts from `y0`, where the rope hangs from.
export const WIRE = { edge: 0x1a1f23, light: 0x6b6b68, dark: 0x41464b };

export function wire(g, x, y0, y1) {
    const h = Math.round(y1 - y0);
    if (h <= 0) return g;
    g.fillStyle(WIRE.edge, 1).fillRect(x - 1, y0, 1, h).fillRect(x + 1, y0, 1, h);
    g.fillStyle(WIRE.dark, 1).fillRect(x, y0, 1, h);
    g.fillStyle(WIRE.light, 1);
    for (let y = 0; y < h; y += 4) g.fillRect(x, y0 + y, 1, Math.min(2, h - y));
    return g;
}
