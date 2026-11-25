"""Near-catch 6's clips, cut out of their green grounds (docs/near-catch-6-remake-log.md). Every clip is PixMiniMax's, made
on a plain green or on a green copy of the bridge's forward end (`sets.py`); a pixel is the ground's when its green
leads its red and its blue by 50. Loose specks go. Each frame stays on its own canvas: `clips.json` says how a
canvas lies in the world (what column and row are the figure's x and its floor, or, for a clip made on the set, the
world's px of its corner).

    python assets/source/bridge/cut.py
"""
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
TRIES, OUT = HERE / "tries", HERE / "clips"
# clip -> (the try's name, its pictures in the order played, how its canvas lies in the world)
#   {"x": col, "floor": row}: the figure's own x is that column, its floor line under that row (a clip that goes with her
#       or with him, wherever they stand);
#   {"x0": px, "y0": px}: the canvas's corner in the world (a clip made on the set); "mirror": the canvas's columns run
#       forward (the world's x is x0 - col).
HER = {"x": 64, "floor": 97}           # her 84 px cell at (22, 14)
HIM = {"x": 64, "floor": 111}          # his 80 px cell at (24, 32)
CLIPS = {
    "her-call": ("call-s3", list(range(9)), HER),                # down onto her heels, a hand held out
    "her-call-loop": ("callloop-s5", list(range(8)), HER),       # beckoning; 8 is 0 again
    "her-call-up": ("callup-s5", list(range(9)), HER),           # startled, up onto her feet: ends as her stand
    "rival-stalk-in": ("stalk-s3", list(range(9)), HIM),         # from his stand into the stalk (not played: he is in it when she comes)
    "rival-stalk": ("stalkloop-s5", list(range(8)), HIM),        # frozen mid-step, wobbling
    "rival-creep": ("creep-s5", list(range(8)), HIM),            # two tiptoe steps
    "rival-net": ("swing-s4", list(range(25)), {"x0": 1880, "y0": 592}),   # the swing onto the button, the tugs, the fall, the net over his head
    "rival-netted": ("netted-loop-s6", list(range(8)), {"x0": 1880, "y0": 592}),    # sat under his own net: one long sigh; 8 is 0 again
    "bumbot-climb": ("climb-s4", list(range(17)), {"x0": 1960, "y0": 560, "mirror": True}),
}
LEAST = 6
HERS = {"her-call": "call", "her-call-loop": "call-loop", "her-call-up": "call-up"}     # into assets/source/her/call/


def parts(cells):
    seen, out = set(), []
    for s in cells:
        if s in seen:
            continue
        comp, todo = [], [s]
        seen.add(s)
        while todo:
            x, y = todo.pop()
            comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in cells and q not in seen:
                        seen.add(q)
                        todo.append(q)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def cut(im):
    im = im.convert("RGB")
    w, h = im.size
    p = im.load()
    body = {(x, y) for y in range(h) for x in range(w) if not (p[x, y][1] > p[x, y][0] + 50 and p[x, y][1] > p[x, y][2] + 50)}
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    dropped = 0
    for comp in parts(body):
        if len(comp) < LEAST:
            dropped += len(comp)
            continue
        for x, y in comp:
            op[x, y] = p[x, y] + (255,)
    return out, dropped


def main():
    meta = {}
    for clip, (name, frames, lie) in CLIPS.items():
        d = OUT / clip
        d.mkdir(parents=True, exist_ok=True)
        dropped, boxes = 0, []
        for i, n in enumerate(frames):
            f, k = cut(Image.open(TRIES / f"{name}-{n}.png"))
            dropped += k
            f.save(d / f"{i}.png")
            boxes.append(f.getbbox())
        if clip in HERS:
            # (Hers go into her sheet: each frame on her sources' 96 px canvas, where her stand's frame is: 16 columns and
            # 32 rows off the picture's, her 84 px cell being at (22, 14) of it.)
            hd = HERE.parent / "her" / "call" / HERS[clip]
            hd.mkdir(parents=True, exist_ok=True)
            for i in range(len(frames)):
                Image.open(d / f"{i}.png").crop((16, 32, 112, 128)).save(hd / f"{i}.png")
        size = Image.open(TRIES / f"{name}-{frames[0]}.png").size
        meta[clip] = {"frames": len(frames), "size": list(size), **lie, "boxes": boxes}
        print(f"{clip}: {len(frames)} frames, specks dropped {dropped} px, first {boxes[0]}, last {boxes[-1]}")
    (OUT / "clips.json").write_text(json.dumps(meta, indent=1), encoding="utf8")


if __name__ == "__main__":
    main()
