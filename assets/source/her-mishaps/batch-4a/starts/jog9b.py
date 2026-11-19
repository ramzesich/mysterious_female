"""9b's start and end (2026-11-19): her standing frame as the game shows it (facing east, the jogger coming from the
east), at canvas x 84 so that she can go back west; the end: her slipfall's last frame (sat on her bottom, facing
east), 18 px further back. A strip of slipfall, dazed-sit and reel to choose the end from."""
from starts2 import *
O = R + "assets/source/her-mishaps/batch-4a/starts/jog9/b/"
st = Image.new("RGBA", (128, 128)); put(st, herf("stand"), 84); st.save(O + "start.png")
cands = [herf("slipfall", i) for i in range(8)] + [herf("dazed-sit", 0), herf("reel", 5)]
row(cands, O + "end-cands.png", k=3, bg=(200, 200, 205, 255))
