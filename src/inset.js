// A picture within the picture (the user, 2026-11-27, the horn's scene: what the blast sets off is 53 m forward of her
// and 13 m under her, so it is shown in a framed panel on her own screen while the horn sounds, the camera never
// leaving her): a second camera on the same world, live, at the game's own pixel size, with a sky of its own laid
// out for it and a frame drawn round it. It opens from its middle row, can be moved to another place, and closes.
//
// Sizes and places are in game pixels (the screen is 480 x 270 of them); the world spot is where its middle looks,
// `floorY` the floor of the place (the horizon stands over it as it does in play).
import { VIEW } from './config.js';
import { Backdrop, HORIZON_ABOVE } from './background.js';

const RIM = 2, EDGE = 1;                    // the frame: a light rim and a dark edge round it, in game px
const LIGHT = 0xf4f4f4, DARK = 0x2e222f;

export class Inset {
    constructor(scene) {
        this.scene = scene;
        const cams = scene.cameras, Z = VIEW.zoom;
        this.cam = cams.add(0, 0, 4 * Z, 4 * Z).setZoom(Z).setVisible(false);
        this.cam.roundPixels = true;
        // (Over the world's own camera, under the evening light's and the HUD's.)
        const list = cams.cameras;
        list.splice(list.indexOf(this.cam), 1);
        list.splice(list.indexOf(cams.main) + 1, 0, this.cam);
        // Its own sky and far sea, laid out for it; the world's own are the main camera's.
        // (In a container, as the windows' views are: its objects keep the order they were made in.)
        this.backdrop = new Backdrop(scene, { waterY: scene.waterY, depth: 0, gulls: scene.farGulls, cam: this.cam });
        this.sky = scene.add.container(0, 0, this.backdrop.objects).setScrollFactor(0).setDepth(scene.DEPTH.sky).setVisible(false);
        scene.worldLayer.add(this.sky);
        cams.main.ignore(this.sky);
        this.cam.ignore([scene.uiLayer, scene.washLayer, ...scene.backdrop.objects,
            ...[scene.windowView, scene.cabinView, scene.roomView].filter(Boolean).map(w => w.view)]);
        this.frame = scene.add.graphics().setScrollFactor(0).setDepth(-1).setVisible(false);
        scene.uiLayer.add(this.frame);
        scene.uiLayer.sendToBack(this.frame);
        this.open = 0;                      // 0 shut, 1 open
        this.to = 0;
        this.ms = 160;
    }

    // Open at `rect` (x, y, w, h on the screen) looking at the world's (x, floorY): the floor `foot` px over the
    // panel's bottom edge.
    show(rect, look) {
        this.rect = rect;
        this.look = { foot: 22, ...look };
        this.to = 1;
        this.backdrop.setDusk?.(this.scene.dusk ?? 0);
        return this;
    }

    // Look somewhere else: shut, then open there (`then`, called as it is shut).
    move(look, then) {
        this.next = { look, then };
        this.to = 0;
    }

    hide() {
        this.next = null;
        this.to = 0;
    }

    get shown() { return this.open > 0; }

    update(dt) {
        if (this.open === this.to && !this.open) return;
        const step = dt * 1000 / this.ms;
        this.open = this.to > this.open ? Math.min(1, this.open + step) : Math.max(0, this.open - step);
        if (!this.open && this.next) {
            this.look = { foot: 22, ...this.next.look };
            this.next.then?.();
            this.next = null;
            this.to = 1;
        }
        const on = this.open > 0, Z = VIEW.zoom, r = this.rect, cam = this.cam;
        cam.setVisible(on);
        this.frame.setVisible(on);
        this.sky.setVisible(on);
        if (!on) return;
        // (From its middle row out, eased.)
        const k = 1 - (1 - this.open) ** 2, h = Math.max(2, Math.round(r.h * k / 2) * 2), y = r.y + (r.h - h) / 2;
        cam.setViewport(r.x * Z, y * Z, r.w * Z, h * Z);
        // (The floor `foot` px over the whole panel's bottom edge, however far it is open.)
        const cy = this.look.floorY + this.look.foot - r.h / 2;
        cam.centerOn(Math.round(this.look.x), Math.round(cy));
        const horizon = (this.look.floorY - HORIZON_ABOVE - cam.scrollY - cam.height / 2) * cam.zoom + cam.height / 2;
        this.backdrop.update(dt, false, horizon);
        const g = this.frame.clear(), t = RIM + EDGE;
        // (The frame is the HUD camera's, drawn after this one: four strips round the picture, never over it.)
        const strips = (c, o, w) => {
            g.fillStyle(c, 1);
            g.fillRect((r.x - o) * Z, (y - o) * Z, (r.w + 2 * o) * Z, w * Z).fillRect((r.x - o) * Z, (y + h + o - w) * Z, (r.w + 2 * o) * Z, w * Z);
            g.fillRect((r.x - o) * Z, (y - o) * Z, w * Z, (h + 2 * o) * Z).fillRect((r.x + r.w + o - w) * Z, (y - o) * Z, w * Z, (h + 2 * o) * Z);
        };
        strips(DARK, t, EDGE);
        strips(LIGHT, RIM, RIM);
    }

    // The world's rectangle it shows.
    get view() { return this.cam.worldView; }

    destroy() {
        this.sky.destroy();
        this.frame.destroy();
        this.scene.cameras.remove(this.cam);
    }
}
