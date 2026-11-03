# Bumbusik

A browser platformer, a gift for the developer's wife: she plays Bumbusik, a cruise ship crew member
chasing the stowaway cat Bumbot around a Norwegian Sun-like ship. **`GAME_DESIGN.md` is the source of
truth**: read the relevant section before any design or content work, and record new decisions there
(tagged Decided / Proposed / Open / Later).

## Stack and running

- Phaser 4.2.1, vendored (`vendor/phaser.min.js`); plain JS ES modules; no npm, no build.
- Run: `python tools/serve.py` (caching off, so reloads are never stale), open
  <http://localhost:8000>. URL flags: `?play` skip title,
  `?reset` clear save, `?debug` bodies + state, `?cards=all` every key card, `?at=pool` start at a
  named place (list in `README.md`; for testing).
- Hosted on GitHub Pages from `main` root: every asset path must be relative.

## Layout

| Path | What |
|---|---|
| `src/config.js` | All tuning: scale, speeds, jump, dash |
| `src/scenes/ShipScene.js` | The game: map, objects, player modes (play, ladder, stairs, trunk, lift, scripted), scares, dash, checkpoints, card-locked stairs, escape trunks, elevators, Bumbot near-catches |
| `tools/ship_layout.py` | **The ship's layout**: decks, stair cores, atrium, escape trunks and every venue in metres from the bow (bow on the left). Edit positions here |
| `maps/ship.json` | Tiled-format map of the whole ship (placeholder art), **generated** from the layout by `python tools/build_ship_map.py` |
| `docs/ship-profile.svg` | Side schematic of the ship, drawn from the layout by `python tools/draw_ship_profile.py`; shown in `GAME_DESIGN.md` §5.3 |
| `reference/` | **Git-ignored**: NCL's ship map PDF and its side profile (also flipped to bow-left), the source of real proportions. Copyrighted, never commit |
| `assets/source/<char>/` | Raw PixelLab frames, kept so sprites can be rebuilt without regenerating |
| `assets/sprites/` | Built sheets: run `python tools/build_sprites.py` after changing sources |
| `assets/ship/` | The ship's art atlas (doors, furniture, fittings, each with a muted `-bg` twin), built from `assets/source/ship/` by `python tools/build_ship_art.py` |
| `tools/palettize.py` | Converts any image to the Resurrect 64 palette (`assets/palette/`) |
| `tools/playtest.py` | Headless Chrome playtests with real key presses; `python tools/playtest.py [scenario]`. Positions come from the map builder |

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

Lessons learned (2026-10-31):

- **Never name an object in an animation's `action_description`** unless it should be drawn:
  "bends down to pick up a cat" drew a cat into her hands. Describe only the body.
- Frame URLs come from `get_character` (the job reply has no animation id). Downloading them from
  backblaze.pixellab.ai needs a `User-Agent` header and the URL's `?t=` token, or it returns 403.
- Characters don't come out smaller than ~28px tall, and small redraws lose the likeness. To get a
  smaller sprite, shrink a bigger design ourselves (box-resample, snap to Resurrect 64) and import
  it with `create_character` v3 + `reference_image_url` + `direction_images` (0.25 generations).
- skeleton-v3 custom poses are humanoid only; for Bumbot use template clips (`running-8-frames`,
  `licking`, `jump`, `sitting`, `eating`) in skeleton-v3 mode, or v3 text mode.
- Generated frames sit at slightly different heights: anchor planted-feet clips with `"feet"` in
  `tools/build_sprites.py`, or the clip floats a pixel.
- Upload local images with `get_upload_url` + curl, then pass `upload:<id>`; never inline base64.

## Working with the user

- **Start each session from `GAME_DESIGN.md` §8 "Next up"**: it records where work stopped. The
  user works from more than one computer, so progress lives in the repo (design doc, this file,
  commits), never only in local memory or uncommitted files.
- Design is settled by numbered question lists; the user answers by number.
- When a generated piece doesn't read as intended, offer to drop or replace it rather than re-rolling
  again and again: the user prefers removing it to over-iterating. Free fixes are fine to just do.
- Work on a feature branch; merge to `main` and push only when the user approves.
- **To approve a piece of art, show the user the image in the chat** (a preview or screenshot) and
  ask; don't send them to launch the game for it.
- Test in headless Chrome (the user uses Chrome, not Edge). Keep image viewing and tool output lean:
  the user watches session usage.
