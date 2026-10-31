import { PLAYER } from '../config.js';
import { makeTextures } from '../textures.js';

export class BootScene extends Phaser.Scene {
    constructor() {
        super('boot');
    }

    preload() {
        // Relative paths only: on GitHub Pages the game lives under /<repo>/ (§7.2).
        this.load.tilemapTiledJSON('ship', 'maps/ship.json');
        this.load.image('tiles', 'assets/tiles/placeholder.png');
        this.load.spritesheet('her', 'assets/sprites/her.png', { frameWidth: PLAYER.cell, frameHeight: PLAYER.cell });
        this.load.json('her-meta', 'assets/sprites/her.json');
    }

    create() {
        makeTextures(this);
        // Her looping animations; single poses (stand, rise, apex, fall, front, back, climb-out)
        // are set as frames.
        const meta = this.cache.json.get('her-meta');
        const frames = (name, order = meta.anims[name].map((_, i) => i)) =>
            order.map(i => ({ key: 'her', frame: meta.anims[name][i] }));
        for (const [name, fps] of [['run', 14], ['climb', 10]]) {
            this.anims.create({ key: `her-${name}`, frames: frames(name), frameRate: fps, repeat: -1 });
        }
        // Her idles play once each. The foot tap repeats its two taps (frames 2-5) a few times
        // between putting her hands on her hips and taking them off.
        const tap = [0, 1, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 6, 7];
        this.anims.create({ key: 'her-idle-tap', frames: frames('idle-tap', tap), frameRate: 7 });
        this.anims.create({ key: 'her-idle-look', frames: frames('idle-look'), frameRate: 6 });
        // The nails' generated last two frames drew a blot on her face, so she lowers her hands by
        // playing the first two backwards.
        this.anims.create({ key: 'her-idle-nails', frames: frames('idle-nails', [0, 1, 2, 3, 4, 5, 2, 3, 4, 5, 6, 7, 7, 1, 0]), frameRate: 7 });
        const params = new URLSearchParams(location.search);
        this.scene.start(params.has('play') ? 'ship' : 'title');
    }
}
