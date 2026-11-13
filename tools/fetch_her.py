"""Downloads clips of her PixelLab character ("Bumbusik (final)") into assets/source/her/<clip>/<i>.png.

    python tools/fetch_her.py <animation name> [<direction>] ...

The animation's name is the one it was given on PixelLab (animate_character's animation_name); the
direction defaults to east. Then add the clip to tools/build_sprites.py and run it.
"""

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HER = "ebd5dadc-1318-4717-b0c0-6f429a7a58f0"


def main():
    args = sys.argv[1:]
    req = urllib.request.Request(f"https://api.pixellab.ai/mcp/characters/{HER}/download?states={HER}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=180).read()))
    for clip in args:
        name, _, facing = clip.partition(":")
        facing = facing or "east"
        entries = [n for n in z.namelist() if f"/animations/{name}/{facing}/" in n]
        out = ROOT / "assets" / "source" / "her" / name
        out.mkdir(parents=True, exist_ok=True)
        for n in entries:
            i = int(n.split("_")[-1].split(".")[0])
            (out / f"{i}.png").write_bytes(z.read(n))
        print(name, facing, len(entries), "frames")


if __name__ == "__main__":
    main()
