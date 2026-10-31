// Tuning constants. World units are internal pixels: the world camera is zoomed 2x, so the
// visible world is 480x270 inside a 960x540 canvas (GAME_DESIGN.md §2.1, §5.4).

export const VIEW = { width: 960, height: 540, zoom: 2 };

export const PLAYER = {
    bodyWidth: 10,
    bodyHeight: 30,
    runSpeed: 100,        // px/s
    groundAccel: 1400,    // px/s², how quickly she gets up to speed
    groundDecel: 1800,
    airAccel: 900,
    gravity: 900,
    jumpVelocity: 330,    // apex ≈ 60px, about two of her heights
    jumpCutVelocity: 150, // releasing jump early clips the climb to this, for a short hop
    maxFall: 420,
    coyoteMs: 90,         // jump still allowed this long after walking off an edge
    jumpBufferMs: 110,    // a jump pressed this long before landing still happens
    climbSpeed: 60,
    stairsSpeed: 80,      // along the slope
    stairsBoardReach: 10, // how close to a flight's end she must be to step onto it
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
