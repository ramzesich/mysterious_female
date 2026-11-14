"""Every sound of the game (src/sfx.js) rendered by the browser without playing it, then measured:
how loud, how long, where its weight lies; and drawn, one spectrogram each, on contact sheets.

    python tools/check_sound.py [name ...]      (no names: all of them, and the ambience's layers)

Nobody hears a thing here. It finds an effect that is silent, clipped, far louder or fainter than
its neighbours, or longer than meant; the sheets show whether a sound has the shape it was written
to have (a horn's low steady bands, a meow's rise and fall). How they sound is for the user's ears:
`tools/soundboard.html`. Pictures and WAVs go to %TEMP%/bumbusik-playtest/sound.
"""

import base64
import json
import sys
import time
import wave

import numpy as np
from PIL import Image, ImageDraw
from scipy import signal

from playtest import OUT, Browser

RATE = 22050
SECONDS = 7.5
DIR = OUT / "sound"
QUIET, LOUD = 0.03, 0.75          # an effect's peak should lie between these (full scale is 1)

RENDER = """(async () => {
    const [l, r] = await window.sfx.render(%s, %s, %s, %d);
    const n = l.length, out = new Int16Array(n);
    for (let i = 0; i < n; i++) out[i] = Math.max(-1, Math.min(1, (l[i] + r[i]) / 2)) * 32767;
    const bytes = new Uint8Array(out.buffer);
    let s = '';
    for (let i = 0; i < bytes.length; i += 8192) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 8192));
    return btoa(s);
})()"""


def render(b, name, args, seconds=SECONDS):
    res = b.send("Runtime.evaluate", expression=RENDER % (json.dumps(name), json.dumps(args), seconds, RATE),
                 awaitPromise=True, returnByValue=True)
    if "exceptionDetails" in res:
        raise RuntimeError(f"{name}: {res['exceptionDetails'].get('exception', {}).get('description')}")
    return np.frombuffer(base64.b64decode(res["result"]["value"]), dtype=np.int16).astype(np.float32) / 32767


def measure(x):
    peak = float(np.abs(x).max())
    loud = np.nonzero(np.abs(x) > max(0.004, peak * 0.03))[0]
    if not len(loud):
        return dict(peak=peak, rms=0.0, length=0.0, centre=0)
    part = x[loud[0]:loud[-1] + 1]
    spec = np.abs(np.fft.rfft(part * np.hanning(len(part))))
    freqs = np.fft.rfftfreq(len(part), 1 / RATE)
    return dict(peak=peak, rms=float(np.sqrt((part ** 2).mean())), length=(loud[-1] - loud[0]) / RATE,
                centre=int((spec * freqs).sum() / max(spec.sum(), 1e-9)))


def picture(x, label, w=300, h=96):
    """A spectrogram: time left to right (the sound's own length, at least a second), pitch upward
    on a logarithmic scale from 40 Hz to 11 kHz, brighter = louder."""
    loud = np.nonzero(np.abs(x) > 0.002)[0]
    end = max(RATE, (loud[-1] if len(loud) else 0) + RATE // 8)
    x = x[:end]
    f, t, s = signal.spectrogram(x, RATE, nperseg=512, noverlap=384)
    db = 10 * np.log10(s + 1e-12)
    db = np.clip((db + 95) / 60, 0, 1)
    rows = np.geomspace(40, 11000, h)
    idx = np.clip(np.searchsorted(f, rows), 0, len(f) - 1)
    img = db[idx][::-1]
    cols = np.clip((np.arange(w) / w * img.shape[1]).astype(int), 0, img.shape[1] - 1)
    img = img[:, cols]
    rgb = np.stack([img ** 0.8 * 255, img ** 1.6 * 230, 40 + img ** 3 * 215], axis=-1).astype(np.uint8)
    tile = Image.new("RGB", (w, h + 14), (20, 24, 40))
    tile.paste(Image.fromarray(rgb), (0, 14))
    ImageDraw.Draw(tile).text((3, 1), f"{label}  {end / RATE:.1f}s", fill=(255, 255, 255))
    return tile


def save_wav(x, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    only = sys.argv[1:]
    DIR.mkdir(parents=True, exist_ok=True)
    b = Browser()
    try:
        b.send("Page.navigate", url=f"http://127.0.0.1:{b.http_port}/tools/soundboard.html")
        b.wait_for("window.sfx && window.sfx.groups", timeout=15)
        groups = b.eval("window.sfx.groups")
        demos = b.eval("window.sfx.demos")
        layers = b.eval("window.sfx.layers")
        bad, tiles = [], []
        print(f"{'':24}{'peak':>6}{'rms':>7}{'length':>8}{'centre':>8}")
        for group, names in groups.items():
            print(f"--- {group}")
            for name in names:
                if only and name not in only:
                    continue
                for args in demos.get(name, [[]]):
                    label = name + (f"({','.join(map(str, args))})" if args else "")
                    x = render(b, name, args)
                    m = measure(x)
                    note = ""
                    if m["peak"] < QUIET:
                        note = "  << too faint"
                    elif m["peak"] > LOUD:
                        note = "  << too loud"
                    elif m["length"] > SECONDS - 0.5:
                        note = "  << never ends"
                    if note:
                        bad.append(label)
                    print(f"{label:24}{m['peak']:6.2f}{m['rms']:7.3f}{m['length']:7.2f}s{m['centre']:6d}Hz{note}")
                    tiles.append(picture(x, label))
                    save_wav(x, DIR / f"{label.replace('(', '-').replace(')', '').replace(',', '-')}.wav")
        if not only:
            print("--- The ambience (each layer alone at 1, eight seconds)")
            for layer in layers:
                x = render(b, "ambience", [{layer: 1}], 8)
                m = measure(x)
                print(f"{layer:24}{m['peak']:6.2f}{m['rms']:7.3f}{m['length']:7.2f}s{m['centre']:6d}Hz")
                tiles.append(picture(x, "ambience: " + layer))
                save_wav(x, DIR / f"ambience-{layer}.wav")
        per, cols = 40, 4
        for n in range(0, len(tiles), per):
            page = tiles[n:n + per]
            w, h = page[0].size
            sheet = Image.new("RGB", (cols * (w + 4), -(-len(page) // cols) * (h + 4)), (0, 0, 0))
            for i, tile in enumerate(page):
                sheet.paste(tile, (i % cols * (w + 4), i // cols * (h + 4)))
            path = DIR / f"sheet-{n // per + 1}.png"
            sheet.save(path)
            print("sheet:", path)
        if b.errors:
            print("console:", b.errors[:5])
        print("FAIL: " + ", ".join(bad) if bad else "all within bounds")
        return 1 if bad or b.errors else 0
    finally:
        b.close()


if __name__ == "__main__":
    sys.exit(main())
