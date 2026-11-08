"""Estimates the skeleton of a sprite in each PNG with PixelLab's /v2/estimate-skeleton (0.1
generations each) and writes <png>.kp.json beside it: 18 COCO joints as fractions of the image,
ready for animate_with_skeleton_v3's keypoints. Used to give a new state of her character (the
towel turban) the very motion of her existing clips: estimate their frames, then animate the new
state's pose with them (GAME_DESIGN.md §5.3). Frames already estimated are skipped, so a dropped
connection can just be run again.

    python tools/estimate_skeleton.py frame.png [more.png ...]

The token is the one in the PixelLab MCP entry of ~/.claude.json; it is read, never printed.
Nothing here ships with the game."""
import base64, json, os, sys, urllib.request

cfg = json.load(open(os.path.expanduser("~/.claude.json"), encoding="utf-8"))
def find(o):
    if isinstance(o, dict):
        if "pixellab" in o and isinstance(o["pixellab"], dict) and "headers" in o["pixellab"]:
            return o["pixellab"]["headers"]
        for v in o.values():
            r = find(v)
            if r: return r
headers = find(cfg)
auth = next(v for k, v in headers.items() if k.lower() == "authorization")

for path in sys.argv[1:]:
    out = path + ".kp.json"
    if os.path.exists(out):
        continue
    body = json.dumps({"image": {"type": "base64", "base64": base64.b64encode(open(path, "rb").read()).decode()}}).encode()
    req = urllib.request.Request("https://api.pixellab.ai/v2/estimate-skeleton", data=body, method="POST",
                                 headers={"Authorization": auth, "Content-Type": "application/json", "User-Agent": "bumbusik-tools"})
    with urllib.request.urlopen(req, timeout=60) as r:
        kp = json.load(r)["keypoints"]
    json.dump(kp, open(out, "w"))
    print(os.path.basename(os.path.dirname(path)), os.path.basename(path), len(kp))
