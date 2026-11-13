"""Downloads the people's frames from PixelLab (tools/cast.py) into assets/source/people/<name>/:
the standing pose as stand.png (turned to us: front.png, away: back.png), each animation's east frames as <animation>/<i>.png.

    python tools/fetch_people.py [name ...]      (no names: everyone not fetched yet; --all: everyone)

The download is PixelLab's ZIP of a character (no key needed), laid out as
<state>/rotations/<direction>.png and <state>/animations/<name>/<direction>/frame_NNN.png.
"""

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

from cast import CAST

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "source" / "people"


def fetch(name, facing="east"):
    cid = CAST[name][0]
    req = urllib.request.Request(f"https://api.pixellab.ai/mcp/characters/{cid}/download",
                                 headers={"User-Agent": "Mozilla/5.0"})
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=120).read()))
    out = OUT / name
    out.mkdir(parents=True, exist_ok=True)
    clips = {}
    for entry in z.namelist():
        parts = entry.split("/")
        if len(parts) == 3 and parts[1] == "rotations" and parts[2] in (f"{facing}.png", "south.png", "north.png"):
            (out / {"south.png": "front.png", "north.png": "back.png"}.get(parts[2], "stand.png")).write_bytes(z.read(entry))
        elif len(parts) == 5 and parts[1] == "animations" and parts[3] == facing:
            clip = parts[2]
            (out / clip).mkdir(exist_ok=True)
            n = int(parts[4].split("_")[1].split(".")[0])
            (out / clip / f"{n}.png").write_bytes(z.read(entry))
            clips[clip] = max(clips.get(clip, 0), n + 1)
    return clips


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = args or [n for n in CAST if "--all" in sys.argv or not (OUT / n / "stand.png").exists()]
    for name in names:
        try:
            print(name, fetch(name))
        except Exception as e:          # still being drawn, most likely
            print(name, "FAILED:", e)


if __name__ == "__main__":
    main()
