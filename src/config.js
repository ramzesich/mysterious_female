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

// Elevators (§5.1): the car's speed between decks and how long the doors take to slide.
export const LIFT = {
    speed: 200,         // px/s, about 1.4 decks a second
    doorMs: 260,
};

// The atrium's side walks (§5.3): how far past its edges she can step up onto one, and the height
// of the glass railing in front of it. How high a side walk stands comes from the map.
export const SIDEWALK = {
    reach: 24,
    railHeight: 22,
};

export const DASH = {
    durationMs: 10000,
    speedMultiplier: 2,
    bubbleMs: 1600,
    shout: 'Кісюнічка!!!',
};

// A fall longer than one deck is a scare (§5.6). The margin keeps an ordinary one-deck drop, plus
// a little rounding, well clear of the limit.
export const LONG_FALL_MARGIN = 24;

export const SAVE_KEY = 'bumbusik-save-v1';
