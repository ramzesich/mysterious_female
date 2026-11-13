# Bumbusik

A browser platformer set on a cruise ship. Design: [GAME_DESIGN.md](GAME_DESIGN.md).

## Running it

Browsers won't load the map from a `file://` page, so serve the folder:

```
python tools/serve.py
```

then open <http://localhost:8000>. It turns browser caching off, so a reload always picks up the
latest build (`python -m http.server` works too, but Chrome may keep stale copies). GitHub Pages
serves it the same way.

URL flags, combinable (`?play&debug`):

| Flag | Effect |
|---|---|
| `?play` | Skip the title screen |
| `?reset` | Clear the saved progress |
| `?debug` | Show collision boxes and her position/state |
| `?cards=all` | Every lock open and every verb known (crawl, wall jump, glide), for testing round the ship |
| `?cards=locked` | Key cards are off for now (everything is open); this turns the locks back on, for testing |
| `?tangerines=infinite` | The dash never uses up a tangerine, for testing |
| `?at=<place>` | Start at a named place, for testing: `gangway`, `pool`, `deck12`, `atrium`, `atrium-floor`, `promenade` (outside, on deck 6's promenade), `walkway` (the boat walkway over it, at the station locker), `balcony` (outside, on the balcony of deck 9's balcony cabin; with `&cards=all` she has the grip socks), `library` (inside it), `bar`, `theatre`, `bridge`, `buffet`, `diner`, `bow` (the mooring deck), `stern` (deck 9's aft terrace), `cabin` (inside cabin 8206, deck 8), `linen` (inside the linen room, deck 9), `housekeeping` (deck 9, where the red trunk comes up), `spa` and `gym` (deck 11), `spinnaker`, `chapel` (inside it), `champs`, `court`, `sushi`, `bistro` (deck 12) |
| `?sound` | Sound is off for now; this turns it on |

## Controls

| Action | Keyboard | Xbox controller |
|---|---|---|
| Run | ← / → | Left stick / D-pad |
| Jump (hold for higher) | Space | A |
| Climb ladders, take stairs | ↑ / ↓ | Left stick / D-pad |
| Кісюнічка dash (costs a tangerine) | D | B |
| Activate: open doors | E | X |
| The whole ship from outside (the game pauses): +/− zoom, the mouse wheel zooms toward the pointer; O or Esc to go back | O | |

A controller is detected once a button is pressed on it.

## Layout

| Path | What |
|---|---|
| `index.html`, `style.css` | Page shell |
| `src/` | The game: `main.js` (Phaser config), `scenes/`, controls, sound, save, the sea (`sea.js`), the far background (`background.js`), tuning in `config.js` |
| `vendor/phaser.min.js` | Phaser 4.2.1, vendored (no npm, no build) |
| `maps/ship.json` | The ship map, Tiled JSON format |
| `assets/tiles/placeholder.png` | Placeholder tileset |
| `tools/ship_layout.py` | The ship's layout in metres from the bow: edit positions here |
| `tools/build_ship_map.py` | Generates the map and tileset from the layout |
| `tools/serve.py` | Serves the game locally with caching off |
| `tools/playtest.py` | Headless playtests in Chrome (needs `websocket-client`) |
| `tools/render_ship.py` | Renders the whole ship from outside at full size, for work on the outer shell |

## Testing

```
python tools/playtest.py            # all scenarios
python tools/playtest.py stairs     # one scenario
```

It drives the real game with key presses in headless Chrome and saves screenshots to the system
temp folder.
