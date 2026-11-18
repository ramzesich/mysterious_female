# Plan: fast playtests (the stepped clock)

Written 2026-11-18 on the user's word ("The tests are taking too much time now ... come up with a
smart solution to speed up the development cycle without compromising on QA"; then "Yes" to a plan
for the implementation session). It changes `tools/playtest.py` and the tools that use its
`Browser`; it changes nothing in the game.

**Built 2026-11-18** (the user: "Implement the entire fast test plan"), all four steps and §3.5's and
§3.6's pieces; what it gave and what it found are in §7.

## Start here (for whichever session builds it)

1. Read `CLAUDE.md` ("Working with the user": the whole suite is never started unasked; every
   test browser muted; after each change show the result and stop).
2. Build the steps of §4 in order. **Step 1 ends with numbers shown to the user** (two scenarios,
   real against stepped) before anything else is converted.
3. The scratch scripts the numbers of §1 came from are in `%TEMP%\bumbusik-speed\` (`probe.py`,
   `probe2.py`, `probe3.py`); they are not in the repo and need not be.

## 1. What was measured (2026-11-18, a copy of commit `3f39a69`, this machine)

| What | Measured |
|---|---|
| The test browser's graphics | The RTX 4080 through Direct3D 11: not software. Nothing to gain there |
| A frame of the game in the test browser | About 10.6 ms (95 frames a second), nearly all of it drawing |
| A frame of the game **not drawn** (`game.headlessStep(t, 1000 / 60)`) | About 0.2 ms: **2 game seconds in 26 ms, 600 game seconds in 6.7 s**, some 80 to 90 times real time |
| A frame stepped by hand and drawn (`game.step`) | 12 ms: no gain, drawing is the cost |
| One call into the page (`Browser.eval`) while the game's loop runs | 10.5 ms: it waits behind a frame |
| The same with the game's loop stopped | 0.19 ms |
| A page load (`Browser.open`) | 1.4 to 2.0 s, of which 0.8 s are fixed sleeps |
| A screenshot | 40 to 50 ms |
| Her run, right held for 2 s | Real time 276 px; stepped, drawn or not, 278 px (two more frames were stepped) |
| Her jump's height | 65 px in real time, stepped and drawn, stepped and undrawn |
| `scene.time.delayedCall` under the stepped clock | Follows it |
| A tween under the stepped clock | **Does not** (the tween manager reads `Date.now()`); with `Date.now` and `performance.now` returning the stepped clock it does (48, 98, 100 and complete at 0.5, 1.0 and 1.1 s) |

Read from the code, not measured:

- `tools/playtest.py`: 38 scenarios in 4,843 lines, **650 `time.sleep` calls**, 48 page loads, 205
  screenshots, one browser, one scenario after another, every wait in real seconds. The literal
  sleeps and key holds in the scenario bodies alone add up to about 12.5 minutes; the polling
  loops and the helpers come on top. The whole suite took about 65 minutes when it was last run.
- `region4`, `region6`, `region8`: about 300 lines and 55 to 70 checks each, in one function. A
  check that fails near the end means all of it again.
- The game reads the engine's clock everywhere but two places (`src/rumble.js`, an id in
  `src/world/tangerine.js`), one `setTimeout` (the rumble's), and the sound, which runs on the
  audio context's own clock (`src/sfx.js`).
- Found while looking: **five test browsers were still running after their scripts had ended**
  (a script stopped by a timeout does not take its browser with it), two of them using 2.6 cores
  and 2 GB. Closed with the user's leave.

## 2. The idea

**The test steps the game instead of waiting for it.** Once a page has loaded, the test stops the
engine's own loop and owns the clock: "wait two seconds" becomes "advance 120 frames of a sixtieth
of a second each, undrawn", which takes a few milliseconds. A frame is drawn only when a picture
of it is wanted.

Three things follow, each worth having by itself:

1. **Speed.** The waiting, which is most of a scenario, costs almost nothing.
2. **The same run every time.** Every frame has the same length, and a check reads the game
   between two frames, never in the middle of one. The failures of the "one run in three" kind
   (a walk that sometimes ended short, a poll that overshot a door) have no cause left.
3. **Scenarios side by side.** Nothing depends on how busy the machine is, so several browsers
   can run at once. Each already has its own ports and its own profile.

QA is not traded away: the checks, the key presses (real key events, as now) and the game's code
are the same. What changes is where the clock comes from.

## 3. The design

### 3.1 In the page: `takeover`

Installed by `Browser.open()` once the ship scene is there (its `wait_for` as now, in real time:
loading is the browser's own work):

- `window.__game.loop.stop()`; `window.__t` starts at the loop's last time.
- `Date.now` and `performance.now` return the stepped clock (each keeps its own offset), so the
  tween manager and the rumble follow it.
- `window.__advance(frames, draw)`: for each frame `__t += 1000 / 60`, then
  `game.headlessStep(__t, 1000 / 60)`, or `game.step(...)` when `draw`.
- A new page (the next `open()`) starts in real time again and is taken over again.

### 3.2 In `tools/playtest.py`: one clock for every wait

- `Browser.advance(seconds)`: `round(seconds * 60)` frames, at least one, undrawn.
- **Module functions `wait(seconds)` and `now()`** that go to the current browser's stepped clock
  (one browser per process), and to `time.sleep` and `time.time` under `--real`. **Every
  `time.sleep(` in the scenarios and helpers becomes `wait(`, every `time.time()` deadline
  `now()`**: a mechanical replacement, so all 38 scenarios move at once and none is rewritten.
  The polling helpers (`hold_until`, `wait_for`, `wait_js`, `wait_flag`) then work as they are:
  each turn of their loop advances a few frames and asks the page, at 0.2 ms a question.
- `hold(keys, seconds)`: keys down, `advance`, keys up. The key events go through Chrome as now.
- `shot()`: one drawn frame, then the screenshot. `close_up()` likewise.
- Left in real time: the browser's start, the page's load, and `fake_pad`'s set-up.

### 3.3 What stays in real time

- **`sound`** (the audio context keeps its own clock) and `tools/check_sound.py`.
- **`boot`**, as the proof that the game's own loop still runs.
- Any scenario under `--real`, for comparing.
- Whatever the user judges by eye: motion, pace, a gag. That is the real game, as now.

A short real-time set (`boot`, `sound`, `deck3`) is the one to run before a merge is proposed.

### 3.4 The runner

- `python tools/playtest.py -j 6 region4 region7 vacuum`: one process and one browser for each
  scenario, six at a time; the output of each printed whole, in the order asked, with its time.
- `--failed`: only the scenarios that failed in the last run (kept in
  `%TEMP%/bumbusik-playtest/last.json`).
- `--times`: the time of every scenario, slowest first.
- **Leftover browsers:** `Browser` closes itself on exit (`atexit`), and each run first closes
  any `bumbusik-chrome-*` browser whose starting process is gone, and removes its profile folder.

### 3.5 Smaller cases (as scenarios are next touched, not all at once)

A region's scenario becomes a set of named cases, each a function that starts from a prepared
state (`enter_regionN`, `?at=`, `?did=`) and checks one thing: `region4.trolley`, `region4.towels`,
`region4.linen`. `python tools/playtest.py region4` runs them all; `region4.towels` one. **A new
check goes in as a case of its own from now on.** The old long functions are cut up only when a
step works in them anyway.

### 3.6 Optional, if a run still differs from the next

Seed the randomness in tests (`Math.random` and Phaser's `RND` from one seed, `--seed`), so a
failing run can be played again exactly. About sixty places in the game draw a random number.

## 4. The build, step by step

### Step 1. The stepped clock on two scenarios

- `takeover`, `advance`, `wait`, `now`, `--real` (§3.1, §3.2), with the replacement made across
  the file.
- Run `vacuum` and `region4` both ways. **Shown to the user: for each, the time in real time and
  stepped, and every check's result side by side.** A check that differs is looked into before
  going on (a wait that was tuned to real-time slack, a thing that reads the wall clock).
- Look at the stepped run's screenshots: they must show what the real run's show.

### Step 2. The rest of the scenarios

- Each scenario once with `--real` and once stepped, the checks compared; the list of those that
  differ and why. `sound` and `boot` pinned to real time.
- The other tools that use `Browser` (`check_overlaps.py`, `shoot_people.py`, `render_ship.py`)
  tried stepped; `check_sound.py` left real.

### Step 3. The runner

- `-j`, `--failed`, `--times`, the leftover browsers (§3.4).
- The whole suite once, stepped and six at a time, **on the user's word only** (the rule stands:
  never started unasked). Its time is the number that says whether "run the whole of it before a
  merge" can be the rule again.

### Step 4. The rules

- `CLAUDE.md`: the playtest's line in the table, and "Working with the user" (what is run after a
  change, what before a merge, the real-time set).
- `docs/progress-decisions.md`: the entry, with the times before and after.
- The memory note on the whole suite.

## 5. Risks

- **Something else reads real time.** Found so far: tweens (answered by §3.1), the sound (left
  real), the rumble's `setTimeout` (the `gamepad` scenario: check it stepped; pin it to real time
  if its checks need the timer). Step 2's comparison is what finds the rest.
- **A check that passed by luck of timing fails stepped.** That is a find, not a cost: it is
  looked at, and either the game or the check is mended.
- **A check that needs a drawn frame** (a texture's size, a camera's view): `advance(..., draw)`
  for that wait.
- **The real loop is no longer what most tests run.** Hence `boot` and the short real-time set,
  and the user's own play.
- **Six browsers at once draw on one graphics card:** only screenshots draw, so the load is small;
  `-j` is a number, lowered if pictures come back wrong.

## 6. What it should give (an estimate, to be replaced by step 1's numbers)

The waits vanish and the questions to the page get fifty times quicker; the page loads (about
1.5 s each, 48 of them) and the screenshots (about 45 ms each) stay. A region's scenario of two
to four minutes should come down to well under half a minute, and six run side by side.

## 7. What was built (2026-11-18)

| Scenario set | Real time | Stepped |
|---|---|---|
| `vacuum` | 8.3 s | 1.6 s |
| `region4` | 126.8 s | 5.7 s |
| The 38 scenarios one after another (each its own process) | about 2,080 s (35 min) | about 230 s |
| The 38 scenarios, `-j 6` | | **55 s** |
| `check_overlaps.py` | 20 s | 6 s |
| `shoot_people.py` | 399 s | 21 s |
| `render_ship.py` | 27 s | 5 s |

Every check of every scenario was run both ways: of the 878 found in both, all 878 have the same
result (the real-time baseline ran with the tests as mended below). The screenshots show the same
moments; where a camera is still easing after a move, a few px apart (the headless real loop draws
about 95 frames a second, the stepped one 60).

**Found in the harness** (each would have made stepped runs differ from real ones):

- Undrawn frames left the cameras where they were (Phaser moves them in `preRender`): the vacuum's
  ride ended at once. `__advance` calls `preRender` on every camera.
- A batch of frames ran before any awaited continuation of the game's scenes: the chute's fall came
  0.2 s late. The browser gets its turn between frames (a `MessageChannel` message).
- `game.loop.delta` froze with the loop: the cake never swayed. `__advance` keeps the loop's time,
  delta and frame.
- Six browsers at once: a file refused by the test server (backlog 5), a boot stopped. Backlog 128,
  and a page that does not come up is loaded once more.

**Found in the tests** (checks that had passed by real time's slack; each mended to wait for the
thing itself): the trunk's lock message within the stairs' 0.9 s (`golden`); the funnel stairway's
last step (`golden`, `region8`); the jogger's pass, her return, and the hop timed from his pause
(`region2`); the jump over the trays (`region7`); the terrace gull's swoop when it had to fly back
first (`region8`, 6 s to 8 s). And one for the game's own change: 17's steam gag is longer than
the old fright, so `region9` waits for her return and checks the gag (fan, then swoon).

**Seeded:** `Math.random` in every test page and Phaser's RND at the takeover, from `--seed` (1).
**Still varies between runs:** the game's clock at the takeover (the page's load time), which sets
every timed thing's phase; checks that catch a thing in its round wait for the round.

**The runner:** `-j N`, `--failed`, `--times` (`%TEMP%/bumbusik-playtest/last.json`), leftover
browsers closed and their profile folders removed at each run (1,471 old folders were there), each
`Browser` closed on exit. Cases (§3.5): `scenario_<name>__<case>` is `<name>.<case>`; none of the old
scenarios has been cut up.
