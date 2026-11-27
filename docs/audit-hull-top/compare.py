import sys, json, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import build_ship_map as B
from ship_layout import VENUES
OUT = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(OUT, "sweep.json")))
floors = {d: B.FLOOR_ROW[d] * 16 for d in B.FLOOR_ROW}
def venue(d, m):
    for dd, a, b, n, k in VENUES:
        if dd == d and a <= m < b: return n
    return "-"
runs = []
skipped = 0
for deck, rows in res.items():
    d = int(deck)
    cur = None
    for x, y, mode, route, vd, shown in rows:
        m = B.metres(x // 16)
        if mode != "play" or route != "inside" or abs(y - floors[d]) > 3:
            skipped += 1; continue
        exp = B.indoor(d, m); act = shown > 0.5
        if exp != act:
            if cur and cur["kind"] == (exp, act) and x - cur["x1"] <= 96:
                cur["x1"] = x; cur["n"] += 1
            else:
                cur = dict(deck=d, x0=x, x1=x, n=1, kind=(exp, act), venue=venue(d, m)); runs.append(cur)
print("skipped (moved/scripted):", skipped)
for r in runs:
    m0, m1 = B.metres(r["x0"] // 16), B.metres(r["x1"] // 16)
    e, a = r["kind"]
    print(f"deck {r['deck']:>2}  {m0:6.1f}-{m1:6.1f} m  x {r['x0']}-{r['x1']}  pts {r['n']:>3}  expected {'DIM' if e else 'open'}, got {'DIM' if a else 'open'}  ({r['venue']})")
