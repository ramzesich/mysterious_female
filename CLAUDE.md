# Bumbusik

A browser platformer, a gift for the developer's wife: she plays Bumbusik, a cruise ship crew member
chasing the stowaway cat Bumbot around a Norwegian Sun-like ship. **`GAME_DESIGN.md` is the source of
truth**: read the relevant section before any design or content work, and record new decisions there
(tagged Decided / Proposed / Open / Later).

## Stack and running

- Phaser 4.2.1, vendored (`vendor/phaser.min.js`); plain JS ES modules; no npm, no build.
- Run: `python -m http.server`, open <http://localhost:8000>. URL flags: `?play` skip title,
  `?reset` clear save, `?debug` bodies + state.
- Hosted on GitHub Pages from `main` root: every asset path must be relative.

## Layout

| Path | What |
|---|---|
| `src/config.js` | All tuning: scale, speeds, jump, dash |
| `src/scenes/ShipScene.js` | The game: map, objects, player modes (play, ladder, stairs, scripted), scares, dash, checkpoints |
| `maps/ship.json` | Tiled-format map, **generated** by `tools/build_slice_map.py`. The current slice is test geometry, not the real ship layout |
| `assets/source/<char>/` | Raw PixelLab frames, kept so sprites can be rebuilt without regenerating |
| `assets/sprites/` | Built sheets: run `python tools/build_sprites.py` after changing sources |
| `tools/palettize.py` | Converts any image to the Resurrect 64 palette (`assets/palette/`) |
| `tools/playtest.py` | Headless Chrome playtests with real key presses; `python tools/playtest.py [scenario]` |

## Rules that are easy to break

- Scale: one deck = 144px; she is 59px tall in an 84px cell, feet on the cell's bottom row. Every
  human-sized thing (doors, furniture, railings) is sized to her, never to the ship.
- No death: failures are "scares" (run off, long fall out of frame, life ring overboard). Never use
  the word death, in code or on screen.
- Nothing floats: every object rests on or hangs from something plausible.
- Sprites face east; west is `flipX`. Background props are muted so they never read as interactive.

## Art: PixelLab (MCP)

- Generations cost money (trial, then a short paid month). **State the cost and ask before spending
  generations.** The trial runs one job at a time.
- For her animations use `skeleton-v3` mode: it moves her stored sprite instead of redrawing it, so
  hair and proportions stay consistent. Template mode redraws and drifts.
- Save raw output to `assets/source/`, convert with the palette tools, never commit reference photos.

## Working with the user

- Design is settled by numbered question lists; the user answers by number.
- Work on a feature branch; merge to `main` and push only when the user approves.
- Test in headless Chrome (the user uses Chrome, not Edge). Keep image viewing and tool output lean:
  the user watches session usage.
