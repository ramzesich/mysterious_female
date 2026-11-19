// Tuning constants. World units are internal pixels: the world camera is zoomed 2x, so the
// visible world is 480x270 inside a 960x540 canvas (GAME_DESIGN.md §2.1, §5.4).

export const VIEW = { width: 960, height: 540, zoom: 2 };

// She is 59px tall (her PixelLab sprite), so decks are 144px and a deck's ceiling sits at ~2.2x her
// height (§5.4). Everything human-sized on board is sized to her, not to the ship.
export const PLAYER = {
    height: 59,           // the figure, feet to top of hair
    cell: 84,             // her sprite sheet's frame size; the feet sit on its bottom row
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
    leapMs: 160,        // the leap before he runs
    holdMs: 450,        // she stays bent, reaching at nothing
    frontMs: 600,       // then turns to us before play goes on
    runSpeed: 300,      // his escape, px/s: faster than she can ever run
};

// Cabin 8206's bed (§5.3, the user, 2026-11-06): standing still on it this long, she bounces on it
// for joy, in place, hopping from one foot to the other, her arms waving up and down: one cycle
// (a hop on each foot) this long, each hop this high (px), in the air for this share of it.
export const BED_JOY = {
    idleMs: 1000,
    cycleMs: 640,
    hop: 7,
    air: 0.7,
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

export const SWIM = {
    speed: 70,
    entry: 6,
    float: 21,          // the waterline at her shoulders, head above it
    margin: 18,
};

// The verbs of §6.1.2 (src/world/verbs.js). Crawling: her speed and her height on all fours. The
// wall jump in grip socks: a kick up (a share of her jump) and away from the wall (px/s), her
// steering held for kickMs; pressed to a wall she slides down it slowly. The parasol: how fast she
// sinks under it. Pushing a cart. With a tray in her hands a jump is a low hop.
export const VERBS = {
    crawlSpeed: 88,
    crawlHeight: 26,
    kickUp: 0.96,
    kickAway: 120,
    kickMs: 110,
    vaultClear: 16,       // a kick off a balcony's partition carries her feet this far over its panel
    vaultMin: 210,        // and is never weaker than this (px/s up)
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

// The pocket (docs/plan-three-uses.md §1.3): a hit that would be a fright or a spilled tray, with a
// tangerine on her, is forgiven. She flinches for `flinchMs` (the her-hit clip), pushed back at
// `push` px a second (slowed by `slow`), and blinks for `safeMs`, untouchable; she keeps her
// place and her tray. The tangerine is knocked out of her pocket (LOOSE.knock). `?pocket=off`
// switches it off.
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
};

// The scenarios of a hit, numbered as in the plan's tables (§1.6). `word`: what she cries
// (`fright.<word>` in src/lang.js). With a tangerine on her: `react`, her clip (`her-<react>`), and
// `toss`, the way she is thrown: 'on' pushed on, 'back' thrown back, 'drop' no side; 'gull' a gull
// takes the tangerine, 'hand' she hands it over. (Otherwise the tangerine always rolls off behind
// her, whatever `toss` says: the user, 2026-11-17.)
// With none: her gag, then her checkpoint; until each gag is made, the built one on that side
// stands in: `down` 'sit' (on her bottom, dazed) or 'belly' (on her front, dazed), or with no
// `down` she runs off (`off`). `nothing`: a slow thing she is looking at does not knock her over.
// `gag`: her own gag is made, one picture of her with the thing (`GAGS`, below), played when the
// thing that hit her says how it carries her (`ride` in `scareContact`); `down` is kept for a hit
// that cannot (a tray in her hands spilled, a hit in the air).
// `pocket: false`: an exception to the tangerines (the user, 2026-11-17: "She has to fall here anyway,
// tangerines or no. This will be an exception"): with tangerines on her she gets what she gets with
// none (the gag, her checkpoint) and keeps them all. `pocket()` asks it, whatever the hit.
export const MISHAP_SCENES = {
    '1': { word: 'slipped', react: 'slipback', toss: 'back', down: 'sit' },     // she runs onto the chips
    '2': { word: 'tripped', down: 'belly', pocket: false },     // into the dog's lead: down whatever she carries
    '3': { word: 'tripped', react: 'stumble', toss: 'on', down: 'belly', gag: 'tray' },  // onto the trays: she rides one off (`Trays.ride`)
    '4a': { word: 'slipped', react: 'stumble', toss: 'on', down: 'belly', gag: 'paperFront' },   // a paper at her front: her leg up behind, on her belly
    '4b': { word: 'slipped', react: 'slipback', toss: 'back', down: 'sit', gag: 'paperBehind' }, // at her heel: her leg up in front, on her bottom
    '5a': { word: 'vacuum', react: 'stumble', toss: 'on', down: 'belly', gag: 'vacuum' }, // the vacuum, head-on
    '5b': { word: 'ride', react: 'stumble', toss: 'on', down: 'sit', gag: 'vacuum' },   // it catches her from behind
    '6a': { word: 'bumped', react: 'stumble', toss: 'on', down: 'sit', gag: 'suitcase' }, // she runs into the suitcase
    '6b': { word: 'bumped', react: 'stumble', toss: 'on', down: 'sit', gag: 'suitcase' }, // it rolls into her back
    '6c': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'suitcase' },  // it rolls into her front
    '7a': { word: 'bumped', react: 'stumble', toss: 'on', down: 'belly', gag: 'sledge' },  // the deck chair, head-on: face first onto it, she sleds on it (`WetPatch.ride`)
    '7b': { word: 'bumped', react: 'stumble', toss: 'on', down: 'sit', gag: 'chair' },  // from behind: it takes her and collapses (`WetPatch.ride`)
    '8a': { word: 'bumped', react: 'stumble', toss: 'on', down: 'belly', gag: 'cartDrape' },  // into the porter's cart
    '8b': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'cartPush' },      // it pushes into her
    '8c': { word: 'bumped', react: 'stumble', toss: 'on', down: 'sit', gag: 'cartSit' },      // it reaches her back
    '8d': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'cartBounce' },    // into his back
    '9a': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'jogSpin' },     // the jogger, head-on: spun round like a top, she sits dizzy; he runs on
    '9b': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'jogBowled' },  // he runs into her: bowled back onto her bottom, he scratches the back of his head, sorry (`jogGag`)
    '9c': { word: 'bumped', react: 'stumble', toss: 'on', down: 'belly', gag: 'jogShoved' },  // into her back: shoved, she stumbles and belly-flops; he scratches his head
    '9d': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'jogBounce' },   // she into his back: 8d's bounce, he never notices
    '10a': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'trayFront' },        // into the breakfast tray
    '10b': { word: 'splashed', react: 'arch', toss: 'on', gag: 'trayBack' },                     // it meets her back
    // Her trolley (the user, 2026-11-17: most of the round she wheels it, so it is what she meets).
    // At her front with no one just past it (parked), she trips over it head first (10c); with the
    // stewardess just past it (wheeled), she is bumped back and sits (10d, 8b's clip): over it she
    // would land on her; at her back, she trips forward away from it (10e, her own trip, dazed 1.2 s);
    // into the stewardess's back, she bounces off and sits (10f, 8d's clip).
    '10c': { word: 'tripped', react: 'stumble', toss: 'on', down: 'belly', gag: 'trolleyTrip' },    // over it
    '10d': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'trolleyPush' },        // bumped back off it
    '10e': { word: 'tripped', react: 'stumble', toss: 'on', down: 'belly', downMs: 1200 },          // at her back
    '10f': { word: 'bumped', react: 'reel', toss: 'back', down: 'sit', gag: 'trolleyBounce' },      // into the stewardess's back
    '11a': { word: 'splashed', react: 'splutter', toss: 'back', down: 'sit', gag: 'sprinkler' },  // the jet in her face; with none on her the wet gag, 16's (the user, 2026-11-19: `soakRide`)
    '11b': { word: 'splashed', react: 'arch', toss: 'on', gag: 'sprinkler' },   // in her back; the same
    '12a': { word: 'bonked', react: 'reel', toss: 'back', down: 'sit', gag: 'lightSpin' },  // the stage's light: 9a's spin, she sits dizzy (the user, 2026-11-19: reuse)
    '12b': { word: 'bonked', react: 'stumble', toss: 'on', down: 'belly', gag: 'lightShoved' },  // at her back: 9c's stumble and belly-flop
    '13a': { word: 'bonked', react: 'rubnose', toss: 'back', down: 'sit', gag: 'door' },  // a door in her face: flat on the wall (`SwingDoor.ride`)
    '13b': { word: 'bonked', react: 'stumble', toss: 'on', down: 'belly' },     // it catches her past it
    '14a': { word: 'bonked', react: 'reel', toss: 'back', down: 'sit', gag: 'ballBack' },     // a basketball in her face: stiff as a skittle onto her back
    '14b': { word: 'bonked', react: 'stumble', toss: 'on', down: 'belly', gag: 'ballFront' },  // on the back of her head: stiff as a plank onto her face
    '15': { word: 'bumped', react: 'duck', toss: 'drop', down: 'sit' },         // the drill's boat
    '16': { word: 'drenched', react: 'shiver', toss: 'drop', gag: 'sprinkler', pocket: false },  // a sprinkler: soaked, a sneeze, she squelches back (`Sprinkler.ride`); whatever she carries (the user, 2026-11-18: "the wet gag regardless of the tangerines")
    '17': { word: 'fogged', react: 'splutter', toss: 'drop', gag: 'steam' },    // the sauna's steam: out of the cloud with her hair a huge puff, she fans herself and swoons (`Steam.ride`)
    '18': { word: 'buried', react: 'reel', toss: 'drop', down: 'sit', gag: 'towels' },  // the towel stack: its own clip with her (`thingGag`)
    '19': { word: 'singed', react: 'yelp', toss: 'drop', gag: 'flare' },        // a flare: out of a puff of smoke her face black, her hair on end and smoking; she blinks and coughs out a puff (`Flare.ride`)
    '20': { word: 'swooped', react: 'duck', toss: 'gull', gag: 'gull' },       // a gull on a balcony rail: on her head (`PerchGull.ride`)
    '21': { word: 'swooped', react: 'duck', toss: 'gull', down: 'sit', gag: 'stairs' },  // a funnel gull: on her bottom down the stairway (the ship scene's `stairsGag`)
    '22': { word: 'swooped', react: 'duck', toss: 'gull', gag: 'parasol' },                     // a gull across her glide
    '23': { word: 'startled', react: 'apology', toss: 'hand', gag: 'sorry' },   // a "Do Not Disturb" door: her hands over her eyes, she tiptoes off (the ship scene's `sorryGag`)
    '24': { word: 'startled', react: 'apology', toss: 'hand', gag: 'sorry' },   // the occupied balcony: as 23, she tiptoes off to the partition
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
export const GAGS = {
    vacuum: { word: 'ride', her: 18, sit: 'gag-vacuum-sit', ride: 'gag-vacuum-ride', speed: 230, accel: 240 },
    paperFront: { fall: 'gag-paper-front', paper: 8, holdMs: 2000 },
    paperBehind: { fall: 'gag-paper-behind', paper: -6, holdMs: 2000 },
    suitcase: { her: 20, sit: 'gag-suitcase-sit', ride: 'gag-suitcase-ride', tip: 'gag-suitcase-tip', dazed: 'gag-suitcase-dazed', top: 80, slow: 1.4, least: 16, pace: 1.1, rideS: 3.3, holdMs: 1180 },
    // The porter's cart (8a to 8d; the ship scene's `cartGag`). `cart`: the clip has the cart in it
    // and is set down where she stands, the cart's middle `cartAt` px ahead of hers (behind, less
    // than 0), the porter brought up to it and his own cart hidden; else it is her alone, set down
    // `her` px behind her middle, and the world's porter and cart stay. 8a: she runs into its front
    // and folds over the bags, her legs kicking (`loop`, slowly: at 8 a second it read as twitching, the user). 8b: it pushes her back (the cart's front
    // kept at hers, `fronts`: px ahead of her middle in each frame of the clip) till she sits. 8c:
    // she sits into the bags; he wheels her `rideM` metres, sees her, tips his cap (`tip`, his
    // clip). 8d: she bounces off his back and sits; he walks on `walkOnMs`, then turns round to
    // her. Then `holdMs`, her checkpoint.
    cartDrape: { cart: true, cartAt: 26, clip: 'gag-cart-drape', loop: 'gag-cart-kick', holdMs: 1600 },
    cartPush: { clip: 'gag-cart-push', her: 18, fronts: [11, 11, 8, 5, 0, -6, -7, -7], holdMs: 1600 },
    cartSit: { cart: true, cartAt: -26, clip: 'gag-cart-sit', rideM: 2, tip: 'tip', holdMs: 900 },
    cartBounce: { clip: 'gag-cart-bounce', her: 18, walkOnMs: 450, holdMs: 1600 },
    // The jogger (9b; the ship scene's `jogGag`): her clip where she stands (`gags` sheet), he stops where
    // he met her and plays `sorry` (his far arm up to the back of his head), then `scratch` until her
    // checkpoint, `holdMs` after her clip ends.
    jogBowled: { clip: 'gags-jog-bowled', jog: true, his: 'sorry', loop: 'scratch', holdMs: 1700 },
    // 9a: one clip from each odd frame of her run (`clips`), he runs on; she ends sat dizzy (her own dazed
    // sit, butterflies). 9c: he stops behind her and scratches his head; she ends dazed on her belly.
    // 9d: 8d's bounce off his back (her-mishaps sheet, `her` px behind her middle); he never notices.
    jogSpin: { clips: 'gags-jog-spin', jog: true, at: 'spin', dazed: 'sit', holdMs: 1700 },
    jogShoved: { clip: 'gags-jog-shoved', jog: true, at: 'shove', dazed: 'lie', his: 'sorry', loop: 'scratch', holdMs: 1700 },
    jogBounce: { clip: 'gag-cart-bounce', jog: true, bounce: true, her: 18, holdMs: 1600 },
    // The stage's light (12a, 12b; the user, 2026-11-19: reuse the jogger's): 9a's spin, 9c's belly-flop.
    lightSpin: { clips: 'gags-jog-spin', jog: true, at: 'spin', dazed: 'sit', holdMs: 1700 },
    lightShoved: { clip: 'gags-jog-shoved', jog: true, at: 'shove', dazed: 'lie', holdMs: 1700 },
    // The court's basketballs (14a, 14b; plan-the-rest §3 1.2): stiff as a plank onto her back or her face, from
    // her stand or her run's quarter, then lying so with the butterflies (`lie`, set on by `ball.dx`).
    // (`drop`: hit in the air, she stops there and drops straight down; the gag where she lands.)
    ballBack: { clips: 'gags-ball-back', jog: true, meta: 'ball', at: 'back', lie: 'gags-ball-back-lie', holdMs: 1700, drop: true },
    ballFront: { clips: 'gags-ball-front', jog: true, meta: 'ball', at: 'front', lie: 'gags-ball-front-lie', holdMs: 1700, drop: true },
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
    trolleyTrip: { fall: 'gag-trolley-trip', at: -20, holdMs: 900 },
    trolleyPush: { fall: 'gag-cart-push', her: 18, holdMs: 1000 },
    trolleyBounce: { fall: 'gag-cart-bounce', her: 18, holdMs: 1200 },
    // The towel stack (18): its own clips with her in them, played by the stack (`TowelStack.ride` in
    // src/world/movers.js, the ship scene's `thingGag`): buried, then her head up in a towel turban, a
    // towel swan on it; `holdMs` after, her checkpoint.
    towels: { holdMs: 1400 },
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
    sorry: { sorry: true, speed: 100, holdMs: 600 },
};

// Teppanyaki's flares (`Flare` in src/world/topdeck.js): the chef's flourish before the flame, s;
// the flame's rise to its full heat, s; the lull after a flare, when her running at it does not start
// another, ms; how much later her cry makes his next one, ms; how near she may be, of the way she runs
// in the flourish and the rise, for her coming to start one (nearer, the flame would rise behind her).
export const FLARE = { tellS: 0.9, riseS: 0.13, coolMs: 2500, lateMs: 1500, nearK: 0.65 };

// Handing a tangerine over (§1.6, 23 and 24): her apology's clip, the tangerine in her held-out
// hands from its `frame` on (behind her, her hands over it: `dx` px ahead of her, `dy` up), taken
// by the hand at the door `giveMs` in; she stands for `ms`.
export const HAND_OVER = { dx: 18, dy: 33, frame: 2, giveMs: 950, ms: 1400 };

// A tangerine she gets flies to the HUD's count (§1.7): `ms` along an arc `arc` px high (the
// screen's px), one after another `gapMs` apart; the count changes as each lands.
export const TALLY = { ms: 400, arc: 70, gapMs: 80 };

export const POCKET = {
    flinchMs: 340,
    safeMs: 1500,
    push: 120,
    hop: 90,
    slow: 300,
    recoverMs: 700,     // her slipback and her stumble, before she has her balance back
    stumblePush: 45,    // px/s on, tripped: stopped short to stagger (her run would carry it off)
};

// A tangerine loose in the world (src/world/tangerine.js): how it bounces (`bounce`, a share of
// its speed kept), how fast a floor slows its roll (px a second, each second), below what speed
// it lies still, how near her feet she picks it up, the speed it leaves her pocket at, how long
// before she can catch it again, and from what speed down onto a floor it makes a sound.
export const LOOSE = {
    bounce: 0.35,
    rollDecel: 200,
    rest: 10,
    reach: 12,
    knock: { vx: 220, vy: 200 },
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
