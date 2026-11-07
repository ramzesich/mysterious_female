// Keyboard and Xbox controller mapped to the same actions (§3.1). Each frame produces one state
// object; `*Pressed` fields are true only on the frame the button went down.

const STICK_DEADZONE = 0.4;

export class Controls {
    constructor(scene) {
        this.scene = scene;
        this.keys = scene.input.keyboard.addKeys({
            left: 'LEFT', right: 'RIGHT', up: 'UP', down: 'DOWN',
            jump: 'SPACE', dash: 'D', activate: 'E', start: 'ENTER',
            outside: 'O', escape: 'ESC', zoomIn: 'PLUS', zoomOut: 'MINUS',
            zoomInPad: 'NUMPAD_ADD', zoomOutPad: 'NUMPAD_SUBTRACT',
        });
        this.prev = {};
        this.state = {};
    }

    pad() {
        const gp = this.scene.input.gamepad;
        return gp && gp.total > 0 ? gp.getPad(0) : null;
    }

    update() {
        const k = this.keys;
        const pad = this.pad();
        const stick = pad ? pad.leftStick : { x: 0, y: 0 };

        const held = {
            left: k.left.isDown || (pad && (pad.left || stick.x < -STICK_DEADZONE)),
            right: k.right.isDown || (pad && (pad.right || stick.x > STICK_DEADZONE)),
            up: k.up.isDown || (pad && (pad.up || stick.y < -STICK_DEADZONE)),
            down: k.down.isDown || (pad && (pad.down || stick.y > STICK_DEADZONE)),
            jump: k.jump.isDown || (pad && pad.A),
            dash: k.dash.isDown || (pad && pad.B),   // D for now (the user, 2026-11-06; it was Shift)
            activate: k.activate.isDown || (pad && pad.X),
            start: k.start.isDown || k.jump.isDown || (pad && (pad.A || pad.buttons[9]?.pressed)),
            // The outside view of the whole ship (O; Esc leaves it too), and its zoom (+/-).
            outside: k.outside.isDown,
            escape: k.escape.isDown,
            zoomIn: k.zoomIn.isDown || k.zoomInPad.isDown,
            zoomOut: k.zoomOut.isDown || k.zoomOutPad.isDown,
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
