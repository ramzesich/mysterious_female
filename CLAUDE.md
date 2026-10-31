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

- Generations cost money (Tier 1 month: 2000 generations until 2026-11-30). **State the cost and
  ask before spending generations.** Several jobs can run at once.
- For her animations use `skeleton-v3` mode: it moves her stored sprite instead of redrawing it, so
  hair and proportions stay consistent. Template mode redraws and drifts.
- Save raw output to `assets/source/`, convert with the palette tools, never commit reference photos.
- Her PixelLab character (all animations come from it): **"Bumbusik (final)"**,
  id `ebd5dadc-1318-4717-b0c0-6f429a7a58f0`, 4 directions, 64px. Earlier tries are kept on PixelLab
  for comparison; don't animate those.
- Bumbot's PixelLab character: **"Bumbot (final)"**, id `81f4c718-6c1b-43aa-b3e0-da0cfdd7c855`, 4
  directions, 48px canvas: our hand-shrunk sprite imported, not generated. The 48px candidate it
  came from (`assets/source/bumbot/pixellab/`) and the other tries are kept for comparison.

## Working with the user

- Design is settled by numbered question lists; the user answers by number.
- Work on a feature branch; merge to `main` and push only when the user approves.
- Test in headless Chrome (the user uses Chrome, not Edge). Keep image viewing and tool output lean:
  the user watches session usage.
