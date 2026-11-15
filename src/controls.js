// Keyboard and Xbox controller mapped to the same actions (§3.1). Each frame produces one state
// object; `*Pressed` fields are true only on the frame the button went down.

const STICK_DEADZONE = 0.4;
// Up and down count on the stick only while it points mostly up or down, so running with it tilted
// a little down never crawls or drops her through a walk (§3.1).
const STICK_UPRIGHT = 0.75;     // |y| must be at least this share of |x|
const TRIGGER = 0.5;            // how far a trigger goes in before it counts

// The Xbox controller's buttons in the browser's standard layout.
const PAD = { A: 0, B: 1, X: 2, Y: 3, LB: 4, RB: 5, LT: 6, RT: 7, VIEW: 8, MENU: 9, LS: 10, RS: 11 };

export class Controls {
    constructor(scene) {
        this.scene = scene;
        this.keys = scene.input.keyboard.addKeys({
            left: 'LEFT', right: 'RIGHT', up: 'UP', down: 'DOWN',
            jump: 'SPACE', dash: 'D', activate: 'E', start: 'ENTER',
            outside: 'O', escape: 'ESC', zoomIn: 'PLUS', zoomOut: 'MINUS', mute: 'M',
            zoomInPad: 'NUMPAD_ADD', zoomOutPad: 'NUMPAD_SUBTRACT',
        });
        this.prev = {};
        this.state = {};
        this.padIndex = null;
        this.device = 'keys';       // what she played with last: 'keys' or 'pad' (the rumble's)
    }

    // The controller, while it is what she plays with (src/rumble.js).
    padInUse() {
        return this.device === 'pad' ? this.lastPad : null;
    }

    // The controller in use: whichever connected one was touched last, whatever slot the browser
    // gave it (a pad reconnected may come back in another).
    pad() {
        const gp = this.scene.input.gamepad;
        const pads = gp ? gp.gamepads.filter(p => p && p.connected !== false) : [];
        if (!pads.length) return null;
        const touched = pads.find(p => p.buttons.some(b => b.pressed)
            || Math.abs(p.leftStick.x) > STICK_DEADZONE || Math.abs(p.leftStick.y) > STICK_DEADZONE);
        if (touched) {
            this.padIndex = touched.index;
            this.device = 'pad';
        }
        return (this.lastPad = pads.find(p => p.index === this.padIndex) || pads[0]);
    }

    update() {
        const k = this.keys;
        if (Object.values(k).some(key => key.isDown)) this.device = 'keys';
        const pad = this.pad();
        const stick = pad ? pad.leftStick : { x: 0, y: 0 };
        const button = name => !!pad && !!pad.buttons[PAD[name]]?.pressed;
        const trigger = name => !!pad && (pad.buttons[PAD[name]]?.value ?? 0) > TRIGGER;
        const upright = Math.abs(stick.y) >= Math.abs(stick.x) * STICK_UPRIGHT;

        const held = {
            left: k.left.isDown || (pad && (pad.left || stick.x < -STICK_DEADZONE)),
            right: k.right.isDown || (pad && (pad.right || stick.x > STICK_DEADZONE)),
            up: k.up.isDown || (pad && (pad.up || (upright && stick.y < -STICK_DEADZONE))),
            down: k.down.isDown || (pad && (pad.down || (upright && stick.y > STICK_DEADZONE))),
            jump: k.jump.isDown || button('A'),
            dash: k.dash.isDown || button('B'),   // D for now (the user, 2026-11-06; it was Shift)
            activate: k.activate.isDown || button('X'),
            start: k.start.isDown || k.jump.isDown || button('A') || button('MENU'),
            // The outside view of the whole ship (O, or the right stick's click; Esc or B leaves it
            // too), and its zoom (+/-, or the triggers). Esc, Menu or B skip the intro.
            outside: k.outside.isDown || button('RS'),
            escape: k.escape.isDown || button('MENU') || button('B'),
            mute: k.mute.isDown,        // the sound, off and on: the keyboard only (the user, 2026-11-15)
            zoomIn: k.zoomIn.isDown || k.zoomInPad.isDown || trigger('RT'),
            zoomOut: k.zoomOut.isDown || k.zoomOutPad.isDown || trigger('LT'),
        };

        const state = {};
        for (const name of Object.keys(held)) {
            state[name] = !!held[name];
            state[name + 'Pressed'] = state[name] && !this.prev[name];
            state[name + 'Released'] = !state[name] && !!this.prev[name];
        }
        this.prev = held;
        this.state = state;
        return state;
    }
}
