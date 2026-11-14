"""Renders the whole ship from outside, every deck closed, at full size (one game pixel to one image
pixel), for work on the outer shell (GAME_DESIGN.md §8, the outside of the ship). She and the HUD
are hidden; the camera steps across the world and the game's own frames are stitched together.

Writes ship-full.png (13344 x 2160) and ship-full-preview.png (1600 wide) into the exterior
screenshots folder, %TEMP%/bumbusik-playtest/exterior (the user's wish: the outside work's pictures
in their own folder), or into the folder given. Needs the same Chrome as tools/playtest.py.
    python tools/render_ship.py [out_dir]
"""

import base64
import io
import os
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playtest import Browser  # noqa: E402

def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ["TEMP"]) / "bumbusik-playtest" / "exterior"
    out.mkdir(parents=True, exist_ok=True)
    b = Browser()
    try:
        b.open("?play&tangerines=infinite")
        time.sleep(1.0)
        W, H = b.eval("[window.__ship.map.widthInPixels, window.__ship.map.heightInPixels]")
        # The game's own outside view (O): every deck's side closed, her and the HUD hidden, the game
        # paused; at one image pixel to a game pixel, stepped across the world.
        b.eval("""(() => { const s = window.__ship; s.enterOverview();
          s.uiLayer.setVisible(false); s.cameras.main.setZoom(1); })()""")
        time.sleep(1.5)
        vw, vh = b.eval("[window.__ship.cameras.main.width, window.__ship.cameras.main.height]")
        vw, vh = int(vw), int(vh)
        sheet = Image.new("RGB", (W, H))
        for y in range(0, H, vh):
            for x in range(0, W, vw):
                b.eval(f"window.__ship.cameras.main.setScroll({x}, {y})")
                time.sleep(0.25)
                b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
                b.wait_for("window.__snap", timeout=10)
                data = b.eval("window.__snap").split(",", 1)[1]
                im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
                sheet.paste(im.crop((0, 0, min(vw, W - x), min(vh, H - y))), (x, y))
        sheet.save(out / "ship-full.png")
        sheet.resize((1600, round(H * 1600 / W)), Image.LANCZOS).save(out / "ship-full-preview.png")
        print("wrote", out / "ship-full.png", "errors:", b.errors)
    finally:
        b.close()


if __name__ == "__main__":
    main()
