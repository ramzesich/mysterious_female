"""Bumbot's bed seen close with his eight, the user's own massage gun among them (2026-11-28)."""
import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"
b = P.Browser(stepped=True)
try:
    b.open("?play&at=cabin&did=catch,home&keeps=bed", start=None); b.wait(1.0)
    b.eval(f"window.__skipCloseups = false; {S}.world.seenClose('bed')"); b.wait(1.0)
    b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    im.resize((im.width//2, im.height//2), Image.NEAREST).save(os.path.join(OUT, "gun-bed.png"))
    print("errors", b.errors)
finally:
    b.close()
