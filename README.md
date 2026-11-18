# Bumbusik

A browser platformer set on a cruise ship: Bumbusik, one of the crew, chases the stowaway cat
Bumbot from her cabin on deck 3 to the tip of the bow. Design: [GAME_DESIGN.md](GAME_DESIGN.md).
The whole route can be played, in English and Ukrainian, with the keyboard or an Xbox controller;
what is still to build is in [docs/plan-the-rest.md](docs/plan-the-rest.md).

## Running it

Browsers won't load the map from a `file://` page, so serve the folder:

```
python tools/serve.py
```

then open <http://localhost:8000>. It turns browser caching off, so a reload always picks up the
latest build (`python -m http.server` works too, but Chrome may keep stale copies). Every asset
path is relative, so GitHub Pages can serve it from the repository's root; for now Pages shows a
placeholder page from the branch `placeholder`, and the game is not published.

URL flags, combinable (`?play&debug`):

| Flag | Effect |
|---|---|
| `?play` | Skip the welcome screen and the intro: straight into the game |
| `?intro=<part>` | Start the intro at one of its parts, for a look at it: `focus`, `sky`, `down`, `sea`, `right`, `ship`, `dive`, `corridor`, `step`, `badge`, `turn` (with `?reset`: the whole intro is a new game's). Esc ends the intro at once |
| `?reset` | Clear the saved progress |
| `?debug` | Show collision boxes and her position/state |
| `?cards=all` | Every lock open and every verb known (crawl, wall jump, glide), for testing round the ship. Without it the locks are on: stairs, doors and lifts open with the key cards and the story, as in the game |
| `?tangerines=infinite` | A tangerine is never used up (the cry, the throw, the pocket), for testing |
| `?pocket=off` | A hit is a fright even with tangerines on her (the pocket off), for testing |
| `?real` | Keep the save between loads. **For now nothing is saved** (`DEV_FRESH` in `src/config.js`, the user's wish while the game is made): every load is a new game; the playtests open with `?real` |
| `?at=<place>` | Start at a named place, for testing (a link for each: [docs/start-links.md](docs/start-links.md)): `crew` (deck 3's crew corridor, at her cabin's door: where the game starts), `gangway`, `deck4` (deck 4's corridor between the suitcase and the porter), `deck4-aft` (deck 4's corridor aft, by the robot vacuum's round), `deck5` (deck 5's corridor between its two paper rounds), `pool`, `deck12`, `atrium`, `atrium-floor`, `promenade` (outside, on deck 6's promenade), `walkway` (the boat walkway over it, at the station locker), `balcony` (outside, on the balcony of deck 9's balcony cabin; with `&cards=all` she has the grip socks), `library` (inside it), `bar`, `theatre`, `bridge`, `buffet`, `diner`, `bow` (the mooring deck), `stern` (deck 9's aft terrace), `cabin` (inside cabin 8206, deck 8), `linen` (inside the linen room, deck 9), `housekeeping` (deck 9, where the red trunk comes up), `deck9-aft` (deck 9's corridor, short of the darting vacuum), `steward` (deck 9's corridor at its aft end, by the steward's jammed trolley), `door9`, `trays10`, `wet`, `gull9`, `sprinkler9`, `steam11` (step 4a's gags, each by its thing: deck 9's swinging door, deck 10's tray, deck 11's deck chair, a balcony gull, deck 9's sprinkler, deck 11's sauna steam), `spa` and `gym` (deck 11), `spinnaker`, `chapel` (inside it), `champs`, `court`, `sushi`, `bistro`, `sundeck` (by the old lady), `technical` (the technical ladder's foot at Cagney's), `teppanyaki`, `terrace` (the aft terrace), `cagneys` (by the wedding cake) (deck 12), `funnel` (the funnel's top), `kids` (Splash Academy, deck 7), `captain` (the captain's door, deck 9), `sunset` (the balcony forward of the spa, where the last glide starts), `home` (deck 8, a few doors from cabin 8206) |
| `?did=<flags>` | Start with things already done, for testing: story flags, comma-separated (`engineer,horn,lady` the top deck's errands; `wedding`; `bb6,alarm` the bridge's scene; `books_all` every book back; `alarm,sunset` the finale's glide; `alarm,sunset,catch` the way home with Bumbot in her arms; `...,home` the day after). E.g. `?play&at=champs&cards=all&did=engineer,horn,lady&tangerines=infinite` |
| `?lang=ua` | The game in Ukrainian for this session (`?lang=en`: in English, the default). The choice made in the game is remembered; this one is not |
| `?sound=off` | No sound for this session (it is on otherwise; **M** mutes and unmutes in the game, and that is remembered). Every sound by a button: <http://localhost:8000/tools/soundboard.html> |

## Controls

| Action | Keyboard | Xbox controller |
|---|---|---|
| Run | ← / → | Left stick / D-pad |
| Jump (hold for higher) | Space | A |
| Climb ladders, take stairs | ↑ / ↓ | Left stick / D-pad |
| "Кісюнічка!!!": the cry, and the lunge once learned (one tangerine each) | D | B |
| Throw a tangerine: a roll; with ↑, a lob | F, ↑ + F | Y, ↑ + Y |
| Activate: open doors, take and give things, talk | E | X |
| In the grip socks: at a balcony's partition, jump again in the air to vault it; with ↑ held, each jump at a partition's pole, a pillar or a column is a kick straight up | Space, ↑ + Space | A, ↑ + A |
| Down through a balcony's floor to the one below | ↓ + Space | ↓ + A |
| With the parasol: glide (hold in the air); over an atrium walk's railing, then hold to float down | Space (held), ↓ + Space | A (held), ↓ + A |
| The whole ship from outside (the game pauses): +/− zoom, the mouse wheel zooms toward the pointer; O or Esc to go back | O | |
| On the welcome screen: choose, start | ↑ / ↓, Enter or Space | Left stick / D-pad, A or Menu |
| End the intro at once | Esc | Menu or B |
| Sound off and on | M | |

A controller is detected once a button is pressed on it; whichever was touched last, keyboard or
controller, is the one in use. The controller rumbles at ten moments of the game.

## Layout

| Path | What |
|---|---|
| `index.html`, `style.css` | Page shell |
| `src/` | The game: `main.js` (Phaser config), `scenes/ShipScene.js` (the game itself), `intro.js` (the welcome screen and the intro), controls and rumble, the save, the locks (`progression.js`), every text in English and Ukrainian (`lang.js`), every sound, synthesised (`sfx.js`), the sea (`sea.js`), the far background (`background.js`), all tuning in `config.js` |
| `src/world/` | What is on the ship: the people, the things that move and can hit her, the rooms, the Library's books, the tangerines, the story's scenes, one file per region or kind |
| `vendor/phaser.min.js` | Phaser 4.2.1, vendored (no npm, no build) |
| `maps/ship.json`, `maps/world.json` | The ship (Tiled JSON format) and everything placed on it; both generated |
| `assets/sprites/`, `assets/ship/` | The built sheets (her, Bumbot, the people, the things, her mishaps' gags) and the ship's art (its atlas, the rooms, the livery); raw art in `assets/source/` |
| `assets/tiles/placeholder.png` | The ship's tileset, generated (the name is from the first days: it carries the painted side now) |
| `tools/ship_layout.py`, `tools/population.py` | The ship's layout in metres from the bow, and everything placed on it: edit positions here |
| `tools/build_ship_map.py` | Generates both maps and the tileset from them |
| `tools/build_*.py`, `tools/draw_*.py` | Build the sheets and the atlas from the raw art; draw the rooms and a few pieces by hand |
| `tools/serve.py` | Serves the game locally with caching off |
| `tools/playtest.py` | Headless playtests in Chrome (needs `websocket-client`) |
| `tools/check_*.py`, `tools/shoot_people.py`, `tools/render_ship.py` | Checks by rule and by picture: overlaps, the people's proportions, the corridors' lengths, the sound; everyone in place close up; the whole ship from outside |
| `docs/` | The plans, the population spec, the build's log, a start link for every place |

The full table, with the project's rules, is in [CLAUDE.md](CLAUDE.md).

## Testing

```
python tools/playtest.py boot stairs   # the scenarios named
python tools/playtest.py -j 6          # all 38, six at a time (about a minute)
python tools/playtest.py --failed      # those that failed last time
python tools/playtest.py --times       # each scenario's last time, slowest first
python tools/playtest.py --real boot sound deck3   # in real time, for comparing
```

It drives the real game with key presses in headless Chrome (muted) and saves screenshots to
`bumbusik-playtest` in the system temp folder (`python tools/tempdir.py` prints which; the
variable `BUMBUSIK_TEMP` names another). Once a page is loaded the test stops the game's loop and
steps it itself, a sixtieth of a second a frame, drawing only for screenshots: a scenario takes
seconds, and gives the same result every run. `boot` and `sound` always run in real time.
`tools/check_sound.py` measures every sound without playing it; how a sound sounds is judged by
ear on the soundboard, <http://localhost:8000/tools/soundboard.html>.
