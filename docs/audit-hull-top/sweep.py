import sys, json, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
JS = r"""(async (deck) => {
  const s = window.__ship, L = s.solidLayer, f = s.deckFloors[deck], out = [];
  s.scareContact = () => false;
  for (let x = 24; x < s.map.widthInPixels; x += 48) {
    const c = Math.floor(x / 16);
    const floor = L.getTileAt(c, f), a1 = L.getTileAt(c, f - 1), a2 = L.getTileAt(c, f - 2), a3 = L.getTileAt(c, f - 3);
    if (!floor || floor.index <= 0) continue;
    if ([a1, a2, a3].some(t => t && t.index > 0)) continue;
    s.spawnAt({ x, y: f * 16, route: 'inside' });
    await window.__advance(15, false);
    out.push([x, Math.round(s.player.y), s.mode, s.route, s.viewDeck, +s.deckDim.shown.toFixed(2)]);
  }
  return out;
})"""
b = P.Browser(stepped=True)
res = {}
try:
    b.open("?play&cards=all&did=bb1,bb2,bb3,bb4,bb5,bb6"); b.wait(1.0)
    for deck in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        res[deck] = b.eval(JS + f"({deck})", settle=True)
        print(deck, len(res[deck]), flush=True)
    json.dump(res, open(os.path.join(OUT, "sweep.json"), "w"))
    print("errors", b.errors[:3])
finally:
    b.close()
