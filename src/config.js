// Tuning constants. World units are internal pixels: the world camera is zoomed 2x, so the
// visible world is 480x270 inside a 960x540 canvas (GAME_DESIGN.md §2.1, §5.4).

export const VIEW = { width: 960, height: 540, zoom: 2 };
// What cabin 8206's desk shows seen close, each from its find (`keep:her:<name>`, `keep:him:<name>`; §4 2.4): drawn
// in this order, the back row first (tools/build_desk.py).
export const DESK_THINGS = ['flag', 'plant', 'bookmark', 'diary', 'tshirt', 'sleepmask', 'handheld', 'pick'];
// What Bumbot's bed shows seen close on the day after, each from its find (`keep:cat:<name>`; §4 2.4, the user's).
export const BED_THINGS = ['massage', 'car', 'bell', 'feather', 'snack', 'ball', 'wool', 'sardines'];

// She is 59px tall (her PixelLab sprite), so decks are 144px and a deck's ceiling sits at ~2.2x her
// height (§5.4). Everything human-sized on board is sized to her, not to the ship.
export const PLAYER = {
    height: 59,           // the figure, feet to top of hair
    cell: 84,             // her sprite sheet's frame size; the feet sit on its bottom row
    sink: 1,              // her picture drawn this many px lower than her body's foot, everywhere: her feet
                          // a px into the floor line (the user, 2026-11-20); where she stands is unchanged
    bodyWidth: 14,
    bodyHeight: 56,
    runSpeed: 140,        // px/s
    groundAccel: 2000,    // px/s², how quickly she gets up to speed
    groundDecel: 2400,
    airAccel: 1300,
    gravity: 900,
    jumpVelocity: 350,    // apex ≈ 68px; with a 128px ceiling that leaves her a little headroom
    jumpCutVelocity: 150, // releasing jump early clips the climb to this, for a short hop
    maxFall: 420,
    coyoteMs: 90,         // jump still allowed this long after walking off an edge
    jumpBufferMs: 110,    // a jump pressed this long before landing still happens
    climbSpeed: 80,
    trunkSettle: 18,      // letting go of ↑/↓ this close to a trunk door settles her level with it
    stairsSpeed: 105,     // along the slope
    stairsBoardReach: 10, // how close to a flight's end she must be to step onto it
};

// Her idles (§3): after standing still for firstMs one plays once, then the other every gapMs.
export const IDLE = {
    firstMs: 4000,
    gapMs: [6000, 10000],
    anims: ['idle-tap', 'idle-look'],
};

// The people's idle clips (`idle`, `idle2`: breathing on the spot), on a clock of their own: every
// one plays at this many frames a second, whatever its sheet says (4 or 8), so that standing people
// breathe instead of shaking (the user, 2026-11-15). Every other clip of theirs keeps its own speed.
export const PEOPLE_IDLE = {
    fps: 1,
};

// Bumbot (§4): about 28px tall standing, stylised larger than a real cat beside her.
export const BUMBOT = {
    cell: 64,           // his sprite sheet's frame size; the feet sit on its bottom row
    noticeReach: 60,    // she goes to pick him up once she is this close on his deck
    reachGap: 34,       // where she stops: her hands, bent down, just short of him
    startleMs: 280,     // into her reach, when he hears her and leaps
    // (His clips made again, 2026-11-24: the leap is a real one now, straight up out of her hands, eight frames of it
    // at `startleFps` a second, and he runs as his front paws come down; `getUp`: what he plays first, out of what he
    // was doing, and at how many frames a second: quick. `under`: the rows under his floor that the frames of `fish`
    // and `rope` keep, so those are stood this much lower. `runFps`: his run's eight frames to a stride.)
    leapMs: 440, startleFps: 18,
    getUp: { asleep: ['wake', 5, 30], sat: ['stand-up', 2, 30] },
    under: 8, runFps: 24,
    holdMs: 450,        // she stays bent, reaching at nothing
    frontMs: 600,       // then turns to us and shrugs (her `shrug`, the user, 2026-11-24), this long after it, before play goes on
    runSpeed: 300,      // his escape, px/s: faster than she can ever run
};

// Near-catch 3 on the Stardust's stage (src/world/stage.js; remade 2026-11-24, docs/near-catch-3-remake-log.md). Times
// in ms of the scene's clock, places in px; where things stand: `STAGE` in tools/population.py, and the pieces' own
// layout, assets/ship/stage/stage.json.
export const STAGE = {
    sight: 154,             // she is taken this far from him: in front of the forward curtain, the wing ahead of her
    ahead: 93, aheadMs: 700,        // the picture goes this far ahead of her, in this long: the whole stage in it
    airUp: 200,             // in the air across that line, up to this high over his floor: in a jump, or off the balcony's front over the stage (she comes straight down in front of the curtain)
    // The scene's beats, one after another (the user, 2026-11-24: at 2.65 s it "plays too fast in the game and it's
    // hard to grasp what just happened ... a bit slower and with some delays, but in proper places"). Each hold is
    // where someone would hold: she freezes as the stage manager shouts, Bumbot looks up before he leaps, the rival
    // dangles from the lamp before it gives, a breath after he is gone.
    tipFps: 18, tipPx: 1.6, tipMs: 350,     // her tiptoe (near-catch 2's clip and pace), until she freezes mid-step
    noticeAt: 150,          // the stage manager turns, starts back, thrusts his clipboard at the cat
    catUp: 400, upFrom: 2, upFps: 30,       // Bumbot up from his washing, at the shout: when, from which frame of `stand-up`, how fast; he stands and looks
    danceStop: 450,         // the dancers stop
    // The rival out of the wing: when; px/s, his clip's own pace in its first frames (11 px a frame at 16 a second);
    // his run's frames a second, by its planted foot (7 px back a frame); the proscenium's edge in the stage's picture.
    rivalAt: 750, rivalSpeed: 180, runFps: 25, wingEdge: 36,
    backAfter: 60, backFps: 14,     // she starts back this long after he is out; held
    leapAfter: 60, leapMs: 240, ropeFrom: 2, ropeFps: 14,       // Bumbot leaps for the loop this long after the rival is out; his clip on the rope
    // The rival's clip, step by step: [frame, ms]. Its run at its own pace (it must flow from his run before it);
    // the net up, the leap; then he dangles on the lamp, legs kicking (its frames 6 and 7, twice over): the hold;
    // then the lamp gives, slowly, and the loop goes up; the hatch, and down.
    clip: [[0, 62], [1, 62], [2, 62], [3, 62], [4, 90], [5, 130], [6, 150], [7, 150], [6, 150], [7, 150],
           [8, 100], [9, 100], [10, 100], [11, 100], [12, 110], [13, 110], [14, 80], [15, 80], [16, 80]],
    swishFrame: 4, hookFrame: 5,    // its frames that sound: the net through the air, the lamp taking his weight (and again as he dangles)
    loop: 40,               // the loop's top over the floor
    ropeGain: 1.7,          // the loop's rise for the lamp's drop: the lamp stops at her head's height, he must be behind the valance
    kickMs: 350,            // let go, the lamp is dragged out aft this long, and swings from there
    puffFps: 12,            // the flour out of the hatch
    lookAfter: 130, lookFps: 14,    // once he is gone down the hatch, this long, and she straightens and looks up after Bumbot
    sneezeAfter: 250, sneezeEvery: 5000,    // the stage manager's first sneeze, this long after; then one this often, until his pills
    shrugAfter: 620, afterMs: 100,  // this long looking up, then turned to us, her shrug; then this long
    settleMs: 300,          // she is not freed before the rival has been gone this long
    spot: { half: 24, cone: 0.16, pool: 0.18 },     // Bumbot's spotlight: its half width on the boards, how strong
};

// Near-catch 2 at the Library's aft end (src/world/quiet.js; remade 2026-11-24, docs/near-catch-2-remake-log.md). Places
// in px from Bumbot's spot on the return trolley (`BEATS` in tools/population.py), times in ms.
export const QUIET = {
    sight: 64,              // she is taken this far from him: he and the rope are in the picture, the door at its edge
    ahead: 40, aheadMs: 700,        // the picture goes this far ahead of her as she creeps, in this long: the door well inside
    airUp: 80,              // in a jump across that line: up to this high over his floor
    gap: 39,                // where her creep stops: her hands, reaching, 2 px short of him
    tipFps: 18, tipPx: 1.6, // her tiptoe: frames a second, and the px her planted toes slide back a frame (her pace: 29 px/s)
    reachFps: 14,           // her reach: both arms out by its fifth frame
    backFps: 16, backFrames: 5,     // straightening: the reach's first five frames back
    backAfter: 150,         // after he has landed
    shushAt: 60,            // the librarian's finger to her lips, if she has not just given it
    wakeAt: 40, wakeFrom: 5, wakeFps: 30,   // he wakes this long into her reach: his `wake` from its sixth frame, quick
    leapMs: 340, land: 50, arc: 16,         // off the trolley: to the floor this far aft, this much rise in the leap
    nose: 18,               // his nose ahead of his middle, running
    plough: 200,            // px/s through the stand, until the door is open before him
    fallMs: 50,             // the stand's fall, a frame
    card: [8, 0], cardMs: 300,      // its card: this far aft as it goes down and turns face up
    lookMs: 1200,           // the librarian looks at the door
    watchMs: 500,           // with her hands full: she looks after him this long
    afterMs: 100,           // after her shrug
};

// Near-catch 1 at the Seven Seas' pass (src/world/pass.js; remade 2026-11-24, docs/near-catch-1-remake-log.md). Places
// in px from Bumbot's spot on the counter (`BEATS` in tools/population.py), times in ms.
export const PASS = {
    counter: -77,           // the counter's forward end (its picture's left edge)
    plate: 22,              // the plate's middle: under his mouth as he eats
    sight: 110,             // she stops and cries this far from him: he is well in the picture by then, eating (the user: at 200
                            // "we can barely see Bumbot and what he is actually doing")
    airUp: 80,              // crossing that line in a jump, up to this high over his floor: she comes straight down there first
    pause: 400,             // then her dash, this long after the cry (the user: "a little pause in between")
    stop: -6,               // where her dash ends: where he was
    minMs: 420,             // from nearer than a dash this long, the dash that much later still
    lookAt: 60, lookMs: 200, lookFrames: 6,     // his look back over his shoulder: when, how long, how many of its frames
    turnMs: 220,            // his turn round
    boltBefore: 100,        // he is off this long before she is there
    hit: -27,               // where he is as his nose meets the bowl
    leap: -54, land: -154, leapMs: 340, arc: 18,    // off the counter's end: from, to (on the floor), how long, how high over a straight line
    slide: 12, slideMs: 66,                     // the bowl pushed along the top before its own clip takes over
    fallFps: 12, landFrame: 2,                  // the bowl's fall: its pace, the frame it hits the floor in
    mouth: [-11, -34],      // where its tangerines come out, from the counter's end on the floor's line
    air: 280, roll: [34, 8], rollMs: 520, bounce: 5, bounceMs: 180,     // a tangerine: in the air, how far short of its rest it lands (and more for each next one), its roll, its one bounce
    turnHer: 220,           // she turns after him this long after the bowl goes
    watchMs: 800,           // and to us this long after she is there
    afterMs: 250,           // after her shrug, before she is free
    hintMs: 3000,           // "D to dash" over her
};

// A way she cannot go (the user, 2026-11-24): where a sign already says why (a rope's card, a ladder's chain) she says
// nothing, turns to us and shrugs (her `shrug` clip, `fps` frames a second: at 9 "very slowly", the user), and the sign lights up a moment (`flashMs`,
// its own colours added over it at most `glow`); a lock with nothing to read keeps its padlock over her and she shrugs.
// Not again before `againMs`, held against it or not.
export const SHRUG = { fps: 14, againMs: 2500, flashMs: 600, glow: 0.55, signReach: 90 };

// Cabin 8206's bed (§5.3, the user, 2026-11-06): standing still on it this long, she bounces on it
// for joy, in place, hopping from one foot to the other, her arms waving up and down: one cycle
// (a hop on each foot) this long, each hop this high (px), in the air for this share of it.
export const BED_JOY = {
    idleMs: 1000,
    cycleMs: 640,
    hop: 7,
    air: 0.7,
};

// The spa's massage (the user, 2026-11-22; src/world/spa.js): E within `reach` px of the second table's middle, on its
// floor. The masseur walks `walk` px a second (his walk's planted foot), stands `end` px past the table's ends to
// stretch, kneads `knead` times a round. Her climb on and off the table at `climbMs` a frame; the guest
// gets up at her clip's speed and, standing, is `guestUp` px right of the table's middle (her clip's last frame). Gone
// away this far from the table (or off its deck), the guest is lying on it again (`resetAway`). His toss of Bumbot's
// massage gun (6) the first time: the gun in his hands in his clip's frames `held` ([px ahead of his middle, px up]),
// let go at frame `release` from `from`.
export const MASSAGE = {
    m: 45.45, reach: 40, walk: 28, end: 10, knead: 3, climbMs: 120, guestUp: 19, resetAway: 380,
    // (The guest's walk out, faster: "walking away too slowly", the user; her clip at 12 frames a second, tools/cast.py.)
    guestWalk: 42,
    // (Where she sits in the sauna meanwhile, facing us: the first bench's seat (49.6 m), px aft of the table's middle.)
    bench: 196,
    // (One round: behind the table facing us, a stretch at the feet, in front his back to us, a stretch at the head; the
    // guest's round and round, hers once, the user's. His picture `lower` px lower but facing us behind the table.)
    rounds: ['front', 'foot', 'back', 'head'],
    lower: 1,
    keep: 'keep:cat:massage',
    toss: { clip: 'toss', held: { 1: [6, 30], 2: [15, 34], 3: [19, 40] }, release: 4, from: [18, 41] },
};

// Cabin 8206's shower (§5.3, the user, 2026-11-08): E at its door and she showers, singing (small
// notes rise, no sound), and comes out with a towel round her head, worn until she leaves the cabin.
// Times in ms: her stepping in or out, the shower; how often a note and a puff of steam rise.
export const SHOWER = {
    walkSpeed: 70,       // px/s, to the opening
    hangMs: 700,         // on her way out: the towel from her head to the door's handle, held this long
    stepMs: 320,
    showerMs: 4500,
    noteEveryMs: 520,
    steamEveryMs: 140,
    reach: 14,           // how far past the door's sides she can be to use it
};

// Elevators (§5.1): the car's speed between decks and how long the doors take to slide.
export const LIFT = {
    speed: 200,         // px/s, about 1.4 decks a second
    doorMs: 260,
};

// Side walks (§5.3): the height of the glass railing in front of one.
export const SIDEWALK = {
    railHeight: 22,
};

// Swimming in the pools (§5.3): her breaststroke's speed, how far below the surface her feet must be
// before she is in, where the swim pose sits against the surface, and how close to a pool's side
// she can swim.
// The shadow along the edges of the cut-away deck (§5.3): its colour, darkest alpha, and how deep
// it reaches in (px) under the deck above, over the deck below, and at the ends.
export const CUT_SHADOW = {
    colour: 0x2e222f,
    alpha: 0.6,
    top: 20,
    bottom: 8,
    ends: 18,
};

// The locks (§6.1, src/progression.js): on since step 0 of docs/build-plan.md (2026-11-11). With
// `required: false` nothing is locked; `?cards=all` opens everything, for testing round the ship.
export const KEY_CARDS = {
    required: true,
};

// The parts of a deck behind a wall across it (the bridge, the spa): with `on`, a part stays closed
// and dimmed while she is on the other side of its wall. Off for now, each opens with its deck, until
// we settle how the ship is split and what is locked (the user, 2026-11-08).
export const LOCKED_PARTS = {
    on: false,
};

// Sound (§7.1, src/sfx.js): on since the sound step (2026-11-14); M mutes it in the game, and
// `?sound=off` silences a session. `volume` is the whole of it, `effects` and `ambience` (the sea, the
// engines, the wind) its two halves. An effect from a place in the world (`sfx.at(x, y)`) is at its
// full loudness within `near` px of her and gone at `far`; a pixel up or down counts as
// `deckWeight` along (a deck away is another room).
export const SOUND = {
    on: true,
    volume: 0.9,
    effects: 2,
    ambience: 0.4,
    near: 260,
    far: 980,
    deckWeight: 2.2,
    stride: 30,        // px of floor to one footstep
    // Her run's frames with a foot coming down (her-run, 8 frames): its footsteps sound on them, in
    // step with her feet at any speed (the user, 2026-11-17: a step each 30 px ran a third faster
    // than her feet, one every 40 px).
    runSteps: [3, 7],
    // Her walk with a tray or a cone in her hands (`her-carry-run`): a step as each foot lands, its widest stances
    // (the user, 2026-11-19: by the floor walked they ran much quicker than her feet).
    carrySteps: [0, 4],
};

// Deck 6's promenade doors (§5.3): the quick fade to black and back as she steps through.
export const PROMENADE = {
    fadeMs: 140,
    endStop: 10,      // px past the end pier's inner edge where she stops at the promenade's ends
};

// The first pool's scene (deck 11, near-catch 5; docs/pool-remake-log.md). The drain: how long the water takes (ms), how
// long the wall stays wet and the floor's puddles last after it (ms). The hatch: her place beside it as she opens it (px
// from its middle), how long she takes down its ladder (ms), how far down she goes out of sight (px), how long she is out of
// sight between the tank's floor and the hallway's ceiling while deck 10's side opens (ms). `ceiling`: deck
// 10's hallway's ceiling line, px over its floor; `out`: how far under it she is as she drops out. `floor`: in the dry
// tank her picture is drawn this many px lower than her body, on the floor's strip of pale tiles (the user,
// 2026-11-24: at the wall's foot "she looks floating in the air"; 3 px at first, then "two more pixels down");
// `puddlesFrom`: how far through the drain the puddles begin to show ("only ... at the very last moment"); `under`: how much of the hatch and the drain's grate
// is left under the water ("much less visible when in the water"), the rest washed toward `floorTile`, the tank's
// floor's own pale tile colour (ShipScene's `poolTanks`).
// Near-catch 6 on the bridge (src/world/bridge.js; remade 2026-11-25, docs/near-catch-6-remake-log.md). Places in px
// from the alarm station's middle (`BOW["bridge"]` in tools/population.py), times in ms from the take-over: the
// storyboard's clock (assets/source/bridge/storyboard.py).
export const BRIDGE = {
    sight: 61,              // she is taken this far aft of the station: Bumbot, the officer and the hatch in the picture
    airUp: 80,              // in a jump across that line: up to this high over the floor
    ahead: 59, leadIn: 150, aheadMs: 700, aheadBack: 600,   // the picture goes this far ahead of her, over her last `leadIn` px up to the line (or in this long, from a jump); given back so
    officer0: -86,          // the officer frozen mid-creep: one round of his creep (42 px) from where he swings
    netX: 65,               // where he swings from: his x in his net's clip (px from its pictures' left)
    back: -69,              // Bumbot back on the console, forward: where his climb's clip starts
    onConsole: 38, onStation: 37,       // his paws, px over the floor
    crouchAt: 150, crouchMs: 100,       // she goes down on her heels: a frame
    callAt: 950, callMs: 1400, beckonMs: 125,   // her call's popup; her beckoning, a frame
    washMs: 110, lookAt: 1000, upAt: 1300, standMs: 50,     // he washes; looks at her; gets up
    hopAt: 1900, thereAt: 2300, hopUp: 14,      // onto the station's top, over its button
    creepAt: 1850, creepFps: 8.7,       // the officer after him: 8 frames, his planted foot sliding 5.3 px a frame
    swingAt: 2770, swingFps: 14,        // his swing: the hoop is down two frames on
    springAt: 2790, springUp: 52, landAt: 3380, // Bumbot off the station, over him, onto the console behind him
    startAfter: 30, upMs: 80,           // she starts up onto her feet, a frame
    whoopAfter: 150, loudMs: 7000,      // the alarm's first whoop after the clang; whoop after whoop for this long
    stuck: [4, 5, 6, 5], stuckMs: 170,  // his net stuck on the station: these pictures over and over
    lidAt: 3450, lidMs: 70,             // the hatch's lid drops, a frame
    ladderAt: 3700, downAt: 4300, ratchets: 6,  // its ladder lets down
    climbAt: 4350, climbFps: 14, rungFrom: 4,   // Bumbot's climb; his claws on the rungs from this picture
    tugAt: 4450, tugFrom: 7, tugFps: 10,        // the officer tugs, upright
    fallAt: 5550, fallFrom: 18, fallFps: 12,    // the net free: he goes over backward, it comes down over his head
    lookUpAt: 5000, lookMs: 90,         // she looks up after Bumbot
    freeAt: 6300,
    wobbleMs: 160,          // the officer frozen: a frame of his wobble
    sighEvery: 5000, sighMs: 200,       // sat under his net: a sigh this often, a frame
};

export const POOL = {
    drainMs: 5000, wetMs: 7000, puddleMs: 12000, puddlesFrom: 0.93, floor: 5, under: 0.3, floorTile: 0x8fd3ff,
    hatch: { beside: 30, downMs: 950, down: 76, through: 280 },
    ceiling: 129, out: 20,
    // (Near-catch 5 from the water, the user, 2026-11-25: it starts when Bumbot and the hot tub behind him are in the
    // picture, the tub's aft side `seen` px inside it; hit by the jet he comes down in the water `plunge` px in front
    // of her; her call starts `callAt` ms into her clip of it and he sits up from his fishing; `callMs` to the kid.)
    seen: 12, plunge: 42, callAt: 220, callMs: 900,
};

// (Enriched 2026-11-25, the user: a full stroke of sixteen frames, `fps` of them a second, its splash on frame
// `strokeAt`. At rest she lets the stroke run out to its glide (`settle` times as fast once she is to come up; from the
// frames where her knees are drawn up, `tucked`, she comes up from there, at `tuckedAt` of the rise) and, `restMs` on,
// comes upright in `riseMs`, kneeling on the pool's floor with her head out of the water; a way pressed, she is back
// in her stroke in `diveMs`. The rings she makes in the surface: one every `ringMs`.)
export const SWIM = {
    speed: 70,
    entry: 6,
    float: 21,          // the waterline at her shoulders, head above it
    margin: 18,
    fps: 14, strokeAt: 10, settle: 1.8, tucked: [5, 6, 7, 8, 9], tuckedAt: 3 / 8,
    restMs: 450, riseMs: 520, diveMs: 300, ringMs: 1300,
};

// The verbs of §6.1.2 (src/world/verbs.js). Crawling: her speed and her height on all fours. The
// wall jump in grip socks: a kick up (a share of her jump) and away from the wall (px/s), her
// steering held for kickMs; pressed to a wall she slides down it slowly. The parasol: how fast she
// sinks under it. Pushing a cart. With a tray in her hands a jump is a low hop.
// The shaft from the linen room to deck 8 forward (src/world/world.js `buildDuct`; docs/shaft-remake-log.md): the dark
// round it (black: the user, 2026-11-23, "make the cut away black"; coming out of the linen room it starts from a
// room's dim, `roomDim`, and closes to black as the shaft's pictures come), a grille's cone of light down to deck 8's
// floor (its width under the grille, wide enough for a sign high on the wall, and at its foot; its soft edge), shown
// only while she is over that grille (within `over` px of its middle), how faint it is while she is not over it (within `over` px of its middle), the fade of the shaft's own
// pictures as she goes in and drops out, how far the view looks down in it; how near the mouth she turns into it from
// the cart, the slope's lip, where its slide sets her down past its foot and how long it takes; how near the last
// grille's middle it gives way, and how far out of it her feet are as the drop begins.
export const SHAFT = {
    dim: 1, roomDim: 0.88, cone: { top: 56, foot: 170, soft: 14 }, over: 40, fadeMs: 260, look: 42,
    reach: 22, lip: 22, land: 18, slideMs: 520, trap: 6, out: 22,
    // The drop out of its far end (the user, 2026-11-24): she falls on hands and knees until her feet are `dropCrawlH`
    // px under the ceiling, then upright, her picture's middle kept (her feet `dropShift` px lower; her head then no
    // higher than the shaft's top, 36 px over its floor).
    dropCrawlH: 10, dropShift: 13,
};

// The laundry chute from the linen room down to the laundry (src/world/story.js `chute`; the user, 2026-11-24): the
// crossfades between a room and the hull, the drop from the hatch to the outlet's mouth (about 2 s, "Let's try 2s"), how
// long before she shows the laundry is fully in, and how deep she lands in the cart's towels (her feet over the floor).
// Near-catch 4, the linen room (remade 2026-11-24 on the user's structure: docs/near-catch-4-remake-log.md,
// src/world/linen.js). `gap`: the cart's front from his body's aft end as he goes, px (minus: past it, the cart bumps his
// shelf; it was 2 px short of him: the pillows then lay across the door's frame). His leap to the mouth's lip, `leapMs`,
// `up` px over the shaft's floor for her (the mouth as drawn opens 5 px higher than that floor: he "is shown from below
// the entrance", the user), the cover knocked `coverAt` ms into it, as his fore paws reach it (it fell only once he was
// in the mouth); in on his belly, `crawlMs`. `fps`: the pillows' clip, paced so that the cart, pushed at her 40 px a
// second, is where the clip's own cart stood as the last two leave it (28 px on, frame 10). `hintMs`: "↓ to crawl" over
// her, the first time she stands on the cart once he is gone. `sounds`: on the clip's frames (frame, effect, which of the lying pairs it comes from).
// Splash Academy's pillow siege (src/world/splash.js; plan-the-rest §7f, the user, 2026-11-27): the knight forward of the
// castle and the king aft of it lob one pillow over it to each other. The holder stands over it lying at their toes `wait`
// s, picks it up and throws (`throw`, `fps`); it leaves their hands at `release` [frame, px ahead of their feet, px up]
// and flies `flight` s in a lob peaking `peak` px over the floor (clear of the flags, 95, and under the ceiling, 128), turning a quarter at a time,
// down onto the other's toes (`lie`: px ahead of their feet, `lieUp` its middle over the floor). A hit: her gag 26 and
// the thrower cheers `cheerS` s. Her cry or her dash near one: the nearer ducks `duckS` s (holding the pillow back).
export const SIEGE = {
    wait: 0.9, fps: 10, flight: 1.5, peak: 112, lie: 14, lieUp: 5, cheerS: 1.8, duckS: 1.0,
    release: { splash_king: [12, 24, 39], splash_knight: [13, 17, 37] },
};

// Splash Academy's tag (src/world/splash.js): two kids run laps over their stretch, the one ahead at `lead` m/s, the one
// chasing at `chase`; at an end the one ahead turns, they meet, `tagS` s of giggles, and the tagged one counts `countS` s
// and chases the other the other way. Into her: on her bottom (27), and both freeze, giggling. Her cry or her dash near
// them: both freeze like statues `freezeS` s.
// A kid touches her within `reach` px of their middle with her feet under `clear` px over the floor (their shoulders: they
// are 37 and 44 px tall; at 34 px and 13 px a hop over one still counted, the user, 2026-11-27).
// (Slower, the user, 2026-11-27: at 2.1 and 2.4 it was "nearly impossible to clear". Their run's clip is played at
// `pace` m/s to its 12 frames a second, slower in step with them.)
export const TAG = { lead: 1.6, chase: 1.8, pace: 2.1, tagS: 0.6, countS: 0.8, freezeS: 3, fps: 12, reach: 9, clear: 26 };

export const PILLOWS = {
    gap: -6, leapMs: 320, up: 5, coverAt: 140, crawlMs: 420, fps: 14.3, hintMs: 3000,
    sounds: [[10, 'towelFlump', 'far'], [13, 'towelFlump', 'near']],
};

export const CHUTE = { fadeMs: 150, dropMs: 2000, leadMs: 60, sink: 30, goneFrame: 12,
    // (Out of it: she dives head first until her head is `binFloor` px over the floor (under it: so that her feet are
    // under the heap's top, all of her in it, the cart drawn over her through the floor's slab); lies there
    // `lieMs`, her feet `under` px under the floor, and stands up in it in `riseMs`.)
    binFloor: -12, lieMs: 260, under: 10, riseMs: 380 };   // (`goneFrame`: her going-in clip's frame, from 1, by which she is all in the hatch)

// Her moves on the balconies (src/world/balcony.js; tools/build_balconies.py): within `reach` px of a partition's
// middle Space starts one; the clips' paces (ms a frame); `stand`: her middle from the partition's where a move sets her
// down, `drop` px over the floor after the crossing; `front`: over her depth, the part of her that is in front of the
// balcony's glass, rail and partition; `peek`: the crossing's frame at which she sees who is on the next balcony, held
// `peekMs` before she goes back; `hintMs`: each move's hint over her, the second no sooner than `hintGap` after the
// first. At a column of the boat walkway (the same climb): `lift`, her picture's px up on the walkway; over it on deck 8
// she hops onto and off the rail, her feet `hop` px up for `hopMs`.
export const BALCONY = { reach: 22, stand: 11, drop: 5, front: 0.36, mountMs: 45, swingMs: 35, climbMs: 50, alongMs: 50, peek: 6, peekMs: 600, hintMs: 3200,
    hop: 16, hopMs: 80, lift: 2, hintGap: 3800 };

export const VERBS = {
    crawlSpeed: 88,
    crawlHeight: 26,
    crawlDrop: 1,         // px her picture is drawn under her body on hands and knees (the user, 2026-11-26), `setCrawl`
    kickUp: 0.96,
    kickAway: 120,
    kickMs: 110,
    slideFall: 50,
    gripReach: 5,
    glideFall: 55,
    pushSpeed: 40,        // px/s: her push clip's steps at 11 frames a second (it was 60, her feet slid)
    hop: 0.62,
};

// With Bumbot in her arms, on the way home (§6.1.9): a calm walk, a lower jump; and nothing she
// needs her hands for (ladders, trunks, the crawl, the dash, the parasol, E at things).
export const HOLDING = {
    speed: 0.8,
    jump: 0.86,
};

// The win screen's own message (§6.4, Later: the user's to write), in the game's two languages
// (src/lang.js). Empty, nothing is shown.
export const WIN_MESSAGE = { en: '', ua: '' };

// D (B on the controller): every press costs one tangerine, whatever it does (docs/plan-three-uses.md
// §1.1). The cry, "Кісюнічка!!!", startles the people and animals within `reach` px on her deck
// for `startleMs`; each is deaf to the next for `deafMs`. `gapMs`: no second D sooner.
export const CRY = {
    reach: 4.5 * 48,
    startleMs: 3000,
    deafMs: 8000,
    bubbleMs: 1600,
    gapMs: 600,
    shout: 'Кісюнічка!!!',
};

// With the cry, once she has learned it at the Seven Seas (near-catch 1), the lunge: `ms` at
// `speed` times her run the way she faces; nothing frightens her by contact during it and for
// `safeTailMs` after. (Under Bumbot's 300 px a second.)
export const LUNGE = {
    ms: 1000,
    speed: 2,
    safeTailMs: 300,
};

// How she takes a hit (docs/plan-three-uses.md §1.6). Every obstacle that can hit her by its own
// name: each `scareContact`, `scareAir`, `Carry.spill` and `world.lunged` names one (`mark`: what a
// lunge through it leaves on her hair, 'wet', 'soot', 'steam'). Which of its scenarios a hit is,
// by the side of her it is on and who was moving: src/world/mishaps.js.
export const MISHAPS = {
    chips: {},              // the casino's spilled chips
    lead: {},               // the dog's lead (deck 4)
    trays: {},              // trays on the floor by a "Do Not Disturb" door
    papers: {},             // the paper rounds' papers (deck 5)
    vacuum: {},             // the robot vacuums (decks 4 and 9)
    suitcase: {},           // the runaway suitcase (deck 4)
    deckchair: {},          // the deck chair on the wet patch (deck 11)
    cart: {},               // the porter and his cart (deck 4)
    jogger: {},             // the jogger (the promenade)
    breakfast: {},          // the breakfast stewardess's tray (deck 5)
    trolley: {},            // her room-service trolley, wheeled or parked at a door
    stewardess: {},         // the breakfast stewardess herself, her hands empty
    robe: {},               // the lady in her bathrobe, standing in the corridor (deck 4)
    jet: {},                // the kid's water pistol (deck 11)
    light: {},              // the stage's swinging light
    door: {},               // a door that flies open
    ball: {},               // the court's basketballs (deck 12)
    boat: {},               // the boat drill's boat (the walkway)
    sprinkler: { mark: 'wet' },
    steam: { mark: 'steam' },   // the sauna's steam
    towels: {},             // the towel stack
    flare: { mark: 'soot' },    // Teppanyaki's flares
    railgull: {},           // the gulls on the balcony rails
    funnelgull: {},         // the funnel's gulls, on the stairway
    crossgull: {},          // the gulls across her glide to the bow
    dnd: {},                // a "Do Not Disturb" door
    balcony: {},            // the occupied balcony
    gymball: {},            // the gym's balls rolling with the ship (deck 11)
    pillow: {},             // Splash Academy's pillow siege (deck 7)
    kid: {},                // Splash Academy's two playing tag (deck 7)
};

// The scenarios of a hit, numbered as in the plan's tables (§1.6). `word`: what she cries
// (`fright.<word>` in src/lang.js). **A hit is its gag and her checkpoint, whatever she carries**
// (the user, 2026-11-19: "I want to play the respawn gags in most of the cases, tangerines or no";
// docs/plan-the-rest.md §3 1.2a): none is lost. `pocket: true`, only a gull that comes down on her
// (20, 21, 22): with a tangerine on her it flies off with one, she ducks (`react`, her clip
// `her-<react>`) and keeps her place, blinking (`POCKET`); with none, its gag. (`react` is also her
// start before running off, where no gag stands in.)
// Her gag, then her checkpoint; until each gag is made, the built one on that side
// stands in: `down` 'sit' (on her bottom, dazed) or 'belly' (on her front, dazed), or with no
// `down` she runs off (`off`). `nothing`: a slow thing she is looking at does not knock her over.
// `gag`: her own gag is made, one picture of her with the thing (`GAGS`, below), played when the
// thing that hit her says how it carries her (`ride` in `scareContact`); `down` is kept for a hit
// that cannot (a tray in her hands spilled, a hit in the air).
export const MISHAP_SCENES = {
    '1': { word: 'slipped', react: 'slipback', down: 'sit' },     // she runs onto the chips
    '2': { word: 'tripped', down: 'belly' },     // into the dog's lead: down whatever she carries
    '3': { word: 'tripped', react: 'stumble', down: 'belly', gag: 'tray' },  // onto the trays: she rides one off (`Trays.ride`)
    '4a': { word: 'slipped', react: 'stumble', down: 'belly', gag: 'paperFront' },   // a paper at her front: her leg up behind, on her belly
    '4b': { word: 'slipped', react: 'slipback', down: 'sit', gag: 'paperBehind' }, // at her heel: her leg up in front, on her bottom
    '5a': { word: 'vacuum', react: 'stumble', down: 'belly', gag: 'vacuum' }, // the vacuum, head-on
    '5b': { word: 'ride', react: 'stumble', down: 'sit', gag: 'vacuum' },   // it catches her from behind
    '6a': { word: 'bumped', react: 'stumble', down: 'sit', gag: 'suitcase' }, // she runs into the suitcase
    '6b': { word: 'bumped', react: 'stumble', down: 'sit', gag: 'suitcase' }, // it rolls into her back
    '6c': { word: 'bumped', react: 'reel', down: 'sit', gag: 'suitcase' },  // it rolls into her front
    '7a': { word: 'bumped', react: 'stumble', down: 'belly', gag: 'sledge' },  // the deck chair, head-on: face first onto it, she sleds on it (`WetPatch.ride`)
    '7b': { word: 'bumped', react: 'stumble', down: 'sit', gag: 'chair' },  // from behind: it takes her and collapses (`WetPatch.ride`). **Unreachable** since the chair stands still (2026-11-19); kept (the user, §3 1.3)
    '8a': { word: 'bumped', react: 'stumble', down: 'belly', gag: 'cartDrape' },  // into the porter's cart
    '8b': { word: 'bumped', react: 'reel', down: 'sit', gag: 'cartPush' },      // it pushes into her
    '8c': { word: 'bumped', react: 'stumble', down: 'sit', gag: 'cartSit' },      // it reaches her back
    '8d': { word: 'bumped', react: 'reel', down: 'sit', gag: 'cartBounce' },    // into his back
    '9a': { word: 'bumped', react: 'reel', down: 'sit', gag: 'jogSpin' },     // the jogger, head-on: spun round like a top, she sits dizzy; he runs on
    '9b': { word: 'bumped', react: 'reel', down: 'sit', gag: 'jogBowled' },  // he runs into her: bowled back onto her bottom, he scratches the back of his head, sorry (`jogGag`)
    '9c': { word: 'bumped', react: 'stumble', down: 'belly', gag: 'jogShoved' },  // into her back: shoved, she stumbles and belly-flops; he scratches his head
    '9d': { word: 'bumped', react: 'reel', down: 'sit', gag: 'jogBounce' },   // she into his back: 8d's bounce, he never notices
    '10a': { word: 'bumped', react: 'reel', down: 'sit', gag: 'trayFront' },        // into the breakfast tray
    '10b': { word: 'splashed', react: 'arch', gag: 'trayBack' },                     // it meets her back
    // Her trolley (the user, 2026-11-17: most of the round she wheels it, so it is what she meets).
    // At her front with no one just past it (parked), she trips over it head first (10c); with the
    // stewardess just past it (wheeled), she is bumped back and sits (10d, 8b's clip): over it she
    // would land on her; at her back, she trips forward away from it (10e, her own trip, dazed 1.2 s);
    // into the stewardess's back, she bounces off and sits (10f, 8d's clip).
    '10c': { word: 'tripped', react: 'stumble', down: 'belly', gag: 'trolleyTrip' },    // over it
    '10d': { word: 'bumped', react: 'reel', down: 'sit', gag: 'trolleyPush' },        // bumped back off it
    '10e': { word: 'tripped', react: 'stumble', down: 'belly', downMs: 1200 },          // at her back
    '10f': { word: 'bumped', react: 'reel', down: 'sit', gag: 'trolleyBounce' },      // into the stewardess's back
    '11a': { word: 'splashed', react: 'splutter', down: 'sit', gag: 'sprinkler' },  // the jet in her face: the wet gag, 16's (the user, 2026-11-19: `soakRide`)
    '11b': { word: 'splashed', react: 'arch', gag: 'sprinkler' },   // in her back; the same
    '12a': { word: 'bonked', react: 'reel', down: 'sit', gag: 'lightSpin' },  // the stage's light: 9a's spin, she sits dizzy (the user, 2026-11-19: reuse)
    '12b': { word: 'bonked', react: 'stumble', down: 'belly', gag: 'lightShoved' },  // at her back: 9c's stumble and belly-flop
    '13a': { word: 'bonked', react: 'rubnose', down: 'sit', gag: 'door' },  // a door in her face: flat on the wall (`SwingDoor.ride`)
    '13b': { word: 'bonked', react: 'stumble', down: 'belly' },     // it catches her past it. **Unreachable**: the door hits her only facing it (`SwingDoor`); kept (the user, 2026-11-19, §3 1.3)
    '14a': { word: 'bonked', react: 'reel', down: 'sit', gag: 'ballBack' },     // a basketball in her face: stiff as a skittle onto her back
    '14b': { word: 'bonked', react: 'stumble', down: 'belly', gag: 'ballFront' },  // on the back of her head: stiff as a plank onto her face
    '15': { word: 'bonked', react: 'duck', down: 'sit', gag: 'boat' },  // the drill's boat on her head ("Ouch!", the user, 2026-11-21): on all fours, she crawls out
    '16': { word: 'drenched', react: 'shiver', gag: 'sprinkler' },  // a sprinkler: soaked, a sneeze, she squelches back (`Sprinkler.ride`); whatever she carries (the user, 2026-11-18: "the wet gag regardless of the tangerines")
    '17': { word: 'fogged', react: 'splutter', gag: 'steam' },    // the sauna's steam: out of the cloud with her hair a huge puff, she fans herself and swoons (`Steam.ride`)
    '18': { word: 'buried', react: 'reel', down: 'sit', gag: 'towels' },  // the towel stack: its own clip with her (`thingGag`)
    '19': { word: 'singed', react: 'yelp', gag: 'flare' },        // a flare: out of a puff of smoke her face black, her hair on end and smoking; she blinks and coughs out a puff (`Flare.ride`)
    '20': { word: 'swooped', react: 'duck', pocket: true, gag: 'gull' },       // a gull on a balcony rail: on her head (`PerchGull.ride`)
    '21': { word: 'swooped', react: 'duck', pocket: true, down: 'sit', gag: 'stairs' },  // a funnel gull: on her bottom down the stairway (the ship scene's `stairsGag`)
    '22': { word: 'swooped', react: 'duck', pocket: true, gag: 'parasol' },                     // a gull across her glide
    '23': { word: 'startled', react: 'apology', gag: 'sorry' },   // a "Do Not Disturb" door: her hands over her eyes, she tiptoes off (the ship scene's `sorryGag`)
    '24': { word: 'startled', react: 'apology', gag: 'sorry' },   // the occupied balcony: as 23, she tiptoes off to the partition
    // A gym ball (plan-the-rest §7f, 8; the user, 2026-11-26): at her front she trips over it and falls forward, flat on her
    // belly (the built trip, as the dog's lead); at her back it bumps her onto her bottom. No gag of its own.
    '25a': { word: 'tripped', react: 'stumble', down: 'belly' },
    '25b': { word: 'bumped', react: 'reel', down: 'sit' },
    // Splash Academy's kids (plan-the-rest §7f; the user, 2026-11-27): a kid playing tag runs into her: on her bottom, the
    // built sit, dazed without the butterflies (`dazed`); a pillow lobbed over the castle comes down on her head: her gag
    // (`GAGS.pillow`), ending in that same dazed sit with the pillow on her head.
    '26': { word: 'bonked', react: 'duck', down: 'sit', gag: 'pillow', dazed: 'her-dazed-sit-plain' },
    '27': { word: 'bumped', react: 'reel', down: 'sit', dazed: 'her-dazed-sit-plain' },
};

// Her gags with a thing (§1.6): whichever side it hit her on, she rides it off (the user,
// 2026-11-16: "I prefer the ride in all cases"); `word` over her head for every one of them
// (the vacuum's "Weeeee!"), else the scenario's. One picture of her with it (`assets/sprites/her-mishaps.png`, cells of
// `GAG_CELL`, the thing's middle on the cell's middle), played where she was hit while the world's
// own is hidden. `her`: px from the thing's middle to hers as she starts sitting down, so that she
// starts where she stood. The vacuum (5b) carries her off out of the screen, gathering speed to
// `speed` px/s by `accel`; the suitcase (6b) rolls on to the end of its roll (from an end, to the
// other) at up to `top` px/s with her on it, slowing (`slow`: its speed per px left, at least
// `least`), tips her off, and she sits there `holdMs`, dazed, butterflies over her head (`dazed`).
// The ride takes `rideS` wherever she was hit (that speed profile run faster for a longer roll),
// and never less than `pace` times its speeds (the user, 2026-11-17: "the suitcase sequence takes
// too long"; their pick, a ride of 3.3 s and the clips 10% quicker). A gag with `fall` plays where she stands,
// facing her way, then she stays so `holdMs`, then her checkpoint: the papers (4a, 4b), whose clip
// starts with her standing on the world's paper; `paper`: px from her middle to the paper's, along
// her facing, in that first picture, so that the clip is set down where the world's paper is (and
// the world's own taken away), and `fast`: its first frames' ms each, the push carried into the fall.
export const GAG_CELL = 112;
// A gag's own sounds on its clips' frames (§3 1.3, 2026-11-19): `sounds: { clip key: { frame (from 1): effect } }`,
// played from the sprite that shows it (the ship scene's `addedtoscene` hook). `onClips` gives several clips the same.
const onClips = (keys, at) => Object.fromEntries(keys.map(k => [k, at]));
const SPIN = onClips(['gags-jog-spin-stand', 'gags-jog-spin1', 'gags-jog-spin3', 'gags-jog-spin5', 'gags-jog-spin7'], { 1: 'spin' });
const STIFF = (first, prefix) => ({ [`${prefix}-stand`]: { 1: first, 7: 'bellyFlop' }, [`${prefix}1`]: { 1: first, 8: 'bellyFlop' }, [`${prefix}3`]: { 1: first, 8: 'bellyFlop' },
    [`${prefix}5`]: { 1: first, 8: 'bellyFlop' }, [`${prefix}7`]: { 1: first, 8: 'bellyFlop' } });
export const GAGS = {
    // Splash Academy's pillow (26; the user, 2026-11-27): it drops on her head and she plops down (PixMiniMax from her stand
    // with the world's pillow over her head to her dazed sit's first frame with it on her head, that frame exactly its last:
    // `assets/source/her-mishaps/pillow-sit/`), drawn `sink` px under her foot as the built sit is; then her own dazed sit
    // without the butterflies (`sit`), the pillow on her head (`hat`), as a kid's hit leaves her.
    pillow: { fall: 'gag-pillow-sit', holdMs: 1800, sink: 3, sit: 'her-dazed-sit-plain', hat: 'splash-pillow' },
    vacuum: { word: 'ride', her: 18, sit: 'gag-vacuum-sit', ride: 'gag-vacuum-ride', speed: 230, accel: 240 },
    paperFront: { fall: 'gag-paper-front', paper: 8, holdMs: 2000 },
    paperBehind: { fall: 'gag-paper-behind', paper: -6, holdMs: 2000 },
    suitcase: { her: 20, sit: 'gag-suitcase-sit', ride: 'gag-suitcase-ride', tip: 'gag-suitcase-tip', dazed: 'gag-suitcase-dazed', top: 80, slow: 1.4, least: 16, pace: 1.1, rideS: 3.3, holdMs: 1180 },
    // (The red one, deck 5's: the same clips recoloured, tools/recolour_suitcase.py; the user, 2026-11-26.)
    'suitcase-red': { sit: 'gag-redcase-sit', ride: 'gag-redcase-ride', tip: 'gag-redcase-tip', dazed: 'gag-redcase-dazed' },
    // The porter's cart (8a to 8d; the ship scene's `cartGag`). `cart`: the clip has the cart in it
    // and is set down where she stands, the cart's middle `cartAt` px ahead of hers (behind, less
    // than 0), the porter brought up to it and his own cart hidden; else it is her alone, set down
    // `her` px behind her middle, and the world's porter and cart stay. 8a: she runs into its front
    // and folds over the bags, her legs kicking (`loop`, slowly: at 8 a second it read as twitching, the user). 8b: it pushes her back (the cart's front
    // kept at hers, `fronts`: px ahead of her middle in each frame of the clip) till she sits. 8c:
    // she sits into the bags; he wheels her `rideM` metres, sees her, tips his cap (`tip`, his
    // clip). 8d: she bounces off his back and sits; he walks on `walkOnMs`, then turns round to
    // her. Then `holdMs`, her checkpoint.
    cartDrape: { cart: true, cartAt: 26, clip: 'gag-cart-drape', loop: 'gag-cart-kick', holdMs: 1600, sounds: { 'gag-cart-drape': { 1: 'cartBump' } } },
    cartPush: { clip: 'gag-cart-push', her: 18, fronts: [11, 11, 8, 5, 0, -6, -7, -7], holdMs: 1600, sounds: { 'gag-cart-push': { 1: 'cartBump', 7: 'thump' } } },
    cartSit: { cart: true, cartAt: -26, clip: 'gag-cart-sit', rideM: 2, tip: 'tip', holdMs: 900, sounds: { 'gag-cart-sit': { 1: 'cartBump' } } },
    cartBounce: { clip: 'gag-cart-bounce', her: 18, walkOnMs: 450, holdMs: 1600, sounds: { 'gag-cart-bounce': { 1: 'cartBump', 5: 'thump' } } },
    // The jogger (9b; the ship scene's `jogGag`): her clip where she stands (`gags` sheet), he stops where
    // he met her and plays `sorry` (his far arm up to the back of his head), then `scratch` until her
    // checkpoint, `holdMs` after her clip ends.
    jogBowled: { clip: 'gags-jog-bowled', jog: true, his: 'sorry', loop: 'scratch', holdMs: 1700, sounds: { 'gags-jog-bowled': { 4: 'thump' } } },
    // 9a: one clip from each odd frame of her run (`clips`), he runs on; she ends sat dizzy (her own dazed
    // sit, butterflies). 9c: he stops behind her and scratches his head; she ends dazed on her belly.
    // 9d: 8d's bounce off his back (her-mishaps sheet, `her` px behind her middle); he never notices.
    jogSpin: { clips: 'gags-jog-spin', jog: true, at: 'spin', dazed: 'sit', holdMs: 1700, sounds: SPIN },
    jogShoved: { clip: 'gags-jog-shoved', jog: true, at: 'shove', dazed: 'lie', his: 'sorry', loop: 'scratch', holdMs: 1700, sounds: { 'gags-jog-shoved': { 15: 'bellyFlop' } } },
    jogBounce: { clip: 'gag-cart-bounce', jog: true, bounce: true, her: 18, holdMs: 1600, sounds: { 'gag-cart-bounce': { 5: 'thump' } } },
    // The stage's light (12a, 12b; the user, 2026-11-19: reuse the jogger's): 9a's spin, 9c's belly-flop.
    lightSpin: { clips: 'gags-jog-spin', jog: true, at: 'spin', dazed: 'sit', holdMs: 1700, sounds: SPIN },
    lightShoved: { clip: 'gags-jog-shoved', jog: true, at: 'shove', dazed: 'lie', holdMs: 1700, sounds: { 'gags-jog-shoved': { 15: 'bellyFlop' } } },
    // The court's basketballs (14a, 14b; plan-the-rest §3 1.2): stiff as a plank onto her back or her face, from
    // her stand or her run's quarter, then lying so with the butterflies (`lie`, set on by `ball.dx`).
    // (`drop`: hit in the air, she stops there and drops straight down; the gag where she lands.)
    ballBack: { clips: 'gags-ball-back', jog: true, meta: 'ball', at: 'back', lie: 'gags-ball-back-lie', holdMs: 1700, drop: true, sounds: STIFF('headBonk', 'gags-ball-back') },
    ballFront: { clips: 'gags-ball-front', jog: true, meta: 'ball', at: 'front', lie: 'gags-ball-front-lie', holdMs: 1700, drop: true, sounds: STIFF('headBonk', 'gags-ball-front') },
    // The drill's boat (15; the user, 2026-11-21, in place of 14a's fall of 2026-11-19): bumped on the head, she sinks onto
    // all fours, dizzy, the butterflies over her head, and crawls out from under it the way she was facing (`crawl`, px
    // a second, at her crawl clip's pace), the boat resting just over her back (`DRILL.pinPx`); then `holdMs`, her
    // checkpoint (the ship scene's `crawlGag`, `assets/sprites/drill.png`).
    // (`crawlMs`: she crawls no longer than this, as short as the other gags: the user, 2026-11-21, "the time she takes to
    // crouch away is too long. Other gags are ended earlier".)
    // ("Don't stop her crouch until the screen fades away completely": she crawls on through the fade.)
    boat: { crawl: 45, crawlMs: 1200, drop: true, sounds: { 'drill-drop': { 1: 'boatThump' } } },
    // The breakfast stewardess's tray (10a, 10b; `fallGag`, her alone where she stands, the world's
    // stewardess and dropped tray staying), only when the stewardess had a tray in her hands (`tray`;
    // else the built fall stands in). 10a: she runs into it, reels and sits, the toast on her head
    // and the flower behind her ear. 10b: it meets her back: the same clip, and she turns round to
    // face it as she falls (`turn`: the clip flipped to her other side, on purpose; the user,
    // 2026-11-17, liked it so: a squirm on the spot looked wrong and the case is rare).
    trayFront: { fall: 'gag-tray-sit', tray: true, holdMs: 1800 },
    trayBack: { fall: 'gag-tray-sit', tray: true, turn: true, holdMs: 1800 },
    // Her trolley (10c, 10d, 10f; `fallGag`): the trip over it (10c) is set down by the trolley's
    // middle (`at`: px from it to the clip's middle), the world's trolley drawn over her while it
    // plays (`ride.hide()`); bumped back off it (10d) and bounced off the stewardess (10f), her
    // alone, `her` px behind her middle, as 8b's and 8d's.
    trolleyTrip: { fall: 'gag-trolley-trip', at: -20, holdMs: 900, sounds: { 'gag-trolley-trip': { 1: 'trolleyRattle', 7: 'bellyFlop' } } },
    trolleyPush: { fall: 'gag-cart-push', her: 18, holdMs: 1000, sounds: { 'gag-cart-push': { 1: 'trolleyRattle', 7: 'thump' } } },
    trolleyBounce: { fall: 'gag-cart-bounce', her: 18, holdMs: 1200, sounds: { 'gag-cart-bounce': { 1: 'trolleyRattle', 5: 'thump' } } },
    // The towel stack (18): its own clips with her in them, played by the stack (`TowelStack.ride` in
    // src/world/movers.js, the ship scene's `thingGag`): buried, then her head up in a towel turban, a
    // towel swan on it; `holdMs` after, her checkpoint.
    towels: { holdMs: 1400, sounds: { 'towels-bury': { 6: 'towelFlump' }, ...onClips(['towels-run0', 'towels-run2', 'towels-run4', 'towels-run6'], { 7: 'towelFlump' }) } },
    // Step 4a's first gags, each the thing's own clip with her (`gags` sheet, tools/build_gags.py),
    // played by the thing (`thingGag`). The door (13a): slammed flat on the wall, she slides down. The
    // tray (3): she rides it off at up to `speed` px/s (from her run's, `accel` px/s²). The deck chair
    // (7b): it takes her on `slideMs` along the wet patch, then collapses. The gull (20): it sits on her
    // head and she runs off flailing at her run's speed, out of the screen.
    door: { holdMs: 1200 },
    tray: { holdMs: 600, speed: 260, accel: 300 },
    chair: { holdMs: 1300, slideMs: 450 },
    // 7a: the chair head on (`WetPatch.ride`): she dives face first onto it and it folds flat; from the clip's frame
    // `sledFrom` she sleds on it the way she dived, from her slide's speed to a stop over `slideMs`, at most `reach` px
    // past the patch's end (clear of the palm's pot); a beat (`holdMs`), her checkpoint.
    sledge: { holdMs: 1300, slideMs: 500, sledFrom: 6, reach: 14 },
    gull: { holdMs: 400 },
    // The sprinkler (16): from her run she slides to a stop over `slideMs`; soaked, she stands
    // `holdWetMs`, sneezes (its sound `sneezeAtMs` in), and squelches off at `walkV` px/s for `walkMs`.
    sprinkler: { holdMs: 150, slideMs: 330, holdWetMs: 250, sneezeAtMs: 450, walkV: 26, walkMs: 2300 },  // (walkMs 1300 until 2026-11-19, the user: "it cuts off a bit too soon")
    // The steam (17): a burst wraps her for `coverMs` (from her run she slides to a stop over
    // `slideMs`; set `clear` px clear of the sauna's door) and thins over `clearMs`, her hair a huge puff; she stands `holdPuffMs`, fans herself,
    // swoons and sits (her plop `plopAtMs` into it).
    steam: { holdMs: 900, slideMs: 330, clear: 34, coverMs: 380, clearMs: 650, holdPuffMs: 250, plopAtMs: 500 },
    // The flare (19): a puff of black smoke wraps her for `coverMs` while she jumps back out of the
    // flame (`back` px past its reach, over `slideMs`), and thins over `clearMs`: her face sooty, her
    // hair on end; she stands `holdSootMs`, blinks, and coughs out a puff (its sound `coughAtMs` in).
    flare: { holdMs: 1000, slideMs: 260, back: 44, coverMs: 360, clearMs: 600, holdSootMs: 300, coughAtMs: 330 },
    // A funnel gull's swoop on the stairway (21): from the step's corner nearest her she sits down hard,
    // facing down the flight, and at once bumps down on her bottom, a step each three frames at a
    // constant pace (the user, 2026-11-18: "let her just bump down at a constant speed, starting
    // immediately"), to the foot, and off onto the roof, slumped; `frameMs` each frame. Then dizzy, butterflies
    // over her head (the user, 2026-11-18): her dazed loop `dazedLoops` times at `dazedMs` a frame, `holdMs` after.
    stairs: { stairs: true, word: 'bumpy', frameMs: 60, dazedMs: 110, dazedLoops: 2, holdMs: 0 },
    // 22: a gull across her glide with no tangerine on her (the ship scene's `parasolGag`): the parasol
    // blown inside out, `flipMs` a frame while she still sinks at the glide's pace; then she looks up at it
    // and kicks her legs, `kickMs` a frame, dropping out of the screen, a softer fall than a closed
    // parasol's (`fall` px/s², at most `maxFall` px/s: it still catches a little air).
    parasol: { air: true, word: 'whoa', flipMs: 80, kickMs: 100, fall: 500, maxFall: 240 },
    // 23 and 24: a "Do Not Disturb" door opened on its guest, or a balcony with someone on it, with no tangerine on her (the ship scene's `sorryGag`): a
    // startled hop, both hands over her eyes, her cheek blushing; then she turns away from the door and tiptoes off
    // at `speed` px/s (her planted foot's own pace, 2.6 px a frame, at the clip's 26 ms a frame) to the next wall or door across the
    // deck or a balcony's partition (`partitionShort`), a beat there (`holdMs`), or out of the screen; then her checkpoint.
    sorry: { sorry: true, speed: 100, holdMs: 600, sounds: { 'gags-dnd-tiptoe': { 3: 'tiptoe', 7: 'tiptoe' } } },
};

// Teppanyaki's flares (`Flare` in src/world/topdeck.js): the chef's flourish before the flame, s;
// the flame's rise to its full heat, s; the lull after a flare, when her running at it does not start
// another, ms; how much later her cry makes his next one, ms; how near she may be, of the way she runs
// in the flourish and the rise, for her coming to start one (nearer, the flame would rise behind her).
// The funnel's smoke (the user, 2026-11-27: "the approach we did with the DJ's smoke machine. Just less volume. Out of each
// pipe. Random cycles of more and less amount of smoke"): soft puffs drawn each frame by the ship scene (`drawSmoke`), out of
// each pipe's mouth across its width, rising (`rise` px) and bending aft with the wind (`drift` px) over a puff's `lifeMs`,
// swelling from `r0` to `r0 + grow` as they thin. Each pipe gives more and less by turns (two slow swells out of step,
// `swellMs`, its own phase), at least `least`; a puff born while its pipe gives little is never born, so a lull drifts off
// up the plume as one.
export const FUNNEL_SMOKE = { puffs: 44, lifeMs: 3000, rise: 55, drift: 100, r0: 3.5, grow: 7, alpha: 0.45, least: 0.15,
    swellMs: [2300, 1300], burst: { r: 3, alpha: 1.6 } };   // (`burst`: the horn's blast, `smokeBurst`)
// Her fists in her pull at the horn's cord (`her-pull`, frames 0 to 4 of her sheet's `pull`; the user, 2026-11-27: her hands
// held nothing): [the fist's front column, its top row] in her 84 px cell, facing right, measured from the front-most skin
// pixels. The handle follows them; at rest its top hangs `HORN_REST` px over the funnel's top, where the first frame
// takes it.
export const HORN_FISTS = [[50, 31], [51, 30], [52, 35], [53, 45], [53, 39]];
export const HORN_REST = 56;
// The horn's scene (src/world/horn.js; the user's remake, 2026-11-27, docs/horn-remake-log.md): one clock, in ms from
// the moment her fist closes on the handle. The camera's three shots (the top, the sun deck, the bow) are cut to, each as
// Bumbot comes into it: he is what sets everyone off (the user: "What moves things around is running Bumbot, not the
// horn").
export const HORN = {
    stepSpeed: 62,                      // px/s: her step or two to the cord
    pullMs: 70,                         // a frame of her pull
    blastAt: 320, blastMs: 1500,        // the blast
    shake: 0.006, ringMs: 170,
    letGo: 560, cordMs: 260,            // she lets go of the handle; it swings back up
    earsMs: 70, trembleMs: 110,         // her hands to her ears, a frame; hunched, a frame
    downAfter: 150, turnAfter: 260,     // her hands down once it stops; she turns the way he went
    // Bumbot off the bar: px up and forward (clear of the trumpets' bells), in ms, a hang; his fall to the platform
    // `land` px forward of her; a crouch; away.
    cat: { up: 34, drift: 22, upMs: 240, hang: 120, fallMs: 400, land: 58, crouch: 110, run: 620, frameMs: 70, runMs: 55 },
    floorAt: 164,                       // a shot's floor on the screen, px from its top (where the top's own floor is)
    sunAt: 2550, sunCalm: 320,          // the cut to the sun deck; nothing yet
    catRun: 520,                        // px/s: Bumbot through a shot
    // His leap over the sunbed and what stands at its foot: off the floor this far aft of its middle, down this far
    // forward of it, this high.
    catLeap: [70, 52, 30],
    startBefore: 14, startMs: 90,       // the officer off his knees as Bumbot is this far from him
    cardFrame: 3, cardMs: 520, cardUp: 16,
    // (The old lady starts as Bumbot is this far aft of her: her book goes up, her start's fifth frame, as he is in the
    // air over her.)
    boltBefore: 205, boltMs: 91,
    ladyStep: 6, hurry: 100, hurryMs: 45,
    turnMs: 140, chargeAfter: 420, charge: 340, chargeMs: 62,
    hurdle: [74, 60, 250],              // off the floor this far aft of the sunbed's middle, down this far forward; px/s over it
    sunHold: 420,                       // the sun deck as they left it, before the cut
    flyBefore: 1500, flyMs: 2400,       // the kids' pool's gulls set off this long before the cut to the bow, to cross it
    bowCalm: 300, liftBefore: 30,       // Bumbot into the bow's shot along the windscreen's rail; each gull up as he is this far from it
    bowHold: 1550,                      // from his coming to the cut back to her
    endHold: 250,
};
export const FLARE = { tellS: 0.9, riseS: 0.13, coolMs: 2500, lateMs: 1500, nearK: 0.65 };

// The drill's boat (`DrillBoat`, src/world/outside.js; the user, 2026-11-19: "the drill starts too late, I can
// just run past it freely"): lowered over `lowerS`, hoisted over `hoistS`. Like the flares it answers her
// coming: running at it, the tell starts so that the keel is at her head as she is `inPx` under its end; not
// once she is nearer than `nearK` of that, and not for `lullMs` after it is hoisted (her way through). On her,
// it comes down over her lying (stiff on her back, 15) as far as on the bare walkway (`pinPx` higher: none, the
// user: "the first gif had the boat at a lower level") and stays down until she is back at her checkpoint.
export const DRILL = { lowerS: 1.1, hoistS: 1.6, lullMs: 1500, nearK: 0.6, inPx: 64, pinPx: 26 };

// Handing a tangerine over (§1.6, 23 and 24): her apology's clip, the tangerine in her held-out
// hands from its `frame` on (behind her, her hands over it: `dx` px ahead of her, `dy` up), taken
// by the hand at the door `giveMs` in; she stands for `ms`.
// The Library's books (GAME_DESIGN.md §6.1.2, docs/plan-three-uses.md §4.1): fifteen out on the ship (the fifteenth on
// Splash Academy's bookshelf since 2026-11-27, the user's; its title, text and cover to come from them); the shelf's
// gaps, the nook's `books_all`, the HUD's count and the pages all go by this.
export const BOOKS = 15;

export const HAND_OVER = { dx: 18, dy: 33, frame: 2, giveMs: 950, ms: 1400 };

// A tangerine she gets flies to the HUD's count (§1.7): `ms` along an arc `arc` px high (the
// screen's px), one after another `gapMs` apart; the count changes as each lands.
export const TALLY = { ms: 400, arc: 70, gapMs: 80 };

// A gull's take (the ship scene's `pocket()`): she flinches `flinchMs` (her duck: `recoverMs`), her
// way slowed by `slow` px a second each second, and blinks for `safeMs`, untouchable.
export const POCKET = {
    flinchMs: 340,
    safeMs: 1500,
    slow: 300,
    recoverMs: 700,
};

// A tangerine loose in the world (src/world/tangerine.js): how it bounces (`bounce`, a share of
// its speed kept), how fast a floor slows its roll (px a second, each second), below what speed
// it lies still, how near her feet she picks it up, how long
// before she can catch it again, and from what speed down onto a floor it makes a sound.
export const LOOSE = {
    bounce: 0.35,
    rollDecel: 200,
    rest: 10,
    reach: 12,
    pickDelayMs: 600,
    thudAt: 60,
    landKeep: 0.45,     // of its speed along the floor kept when it comes down hard (a lob stops near where it lands)
    hardAt: 260,        // px/s down that is a hard landing
};

// F (Y on the controller): the throw (docs/plan-three-uses.md §1.2), one tangerine, underarm from
// her hand (`hand` px ahead of her middle, `handY` over her feet). The roll: low, it bounces once
// and rolls about six metres. With ↑, the lob: high and short, its top about 2.3 m ahead and just
// under a corridor's ceiling. She stands for `ms` while she throws; it leaves her hand at `releaseMs`.
export const THROW = {
    roll: { vx: 240, vy: 60 },
    lob: { vx: 250, vy: 355 },
    hand: 18,
    handY: 32,
    ms: 440,
    releaseMs: 250,
    fps: 16,
    // In the air (the user, 2026-11-20: "a player expects" to throw while jumping): F straight forward from her
    // hand's height, ↑ and F the lob from there; once a jump, her arc kept, her clip (`her-airtoss`) over her jump's
    // pose for `airMs`, the fruit off her hand at `airReleaseMs`; `carry` of her own speed along goes with it.
    // (Forward and a little up: a level throw dropped below a gull on a light within 1.5 m; this one meets it
    // from 0.5 to 2.5 m whenever in the jump it leaves her hand, but at the end of her fall.)
    air: { vx: 260, vy: 200 },
    airHand: 7,
    airHandY: 23,
    airMs: 400,
    airFps: 20,
    airReleaseMs: 150,
    carry: 0.5,
};

// A fall longer than one deck is a scare (§5.6). The margin keeps an ordinary one-deck drop, plus
// a little rounding, well clear of the limit, even from the top of a deck's end bulwark, 32px over
// its floor (the user fell from deck 9's stern bulwark to deck 8's terrace, 2026-11-07).
export const LONG_FALL_MARGIN = 56;

// While the game is being made, nothing is saved (the user, 2026-11-16: "remove save games (for
// now) ... Just don't save my progress"): every load is a new game, and every link works as it
// did (the plain one with the welcome screen and the intro, `?play`, `?at=`, the rest). `?real`
// keeps the save, as she will get it; every playtest opens with it. Set to false before the gift.
export const DEV_FRESH = true;

/** Whether this load keeps no save (`DEV_FRESH`, unless `?real`). */
export function devFresh() {
    return DEV_FRESH && !new URLSearchParams(location.search).has('real');
}

export const SAVE_KEY = 'bumbusik-save-v3';   // v2: the progression (§6.1); v3: the verbs, the books
