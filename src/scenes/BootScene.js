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
        // Her looping animations; single poses (stand, rise, apex, fall, front, back) are set as
        // frames. The generated idle is not used for now: standing still is the plain `stand` pose.
        const meta = this.cache.json.get('her-meta');
        for (const [name, fps] of [['run', 14], ['climb', 10]]) {
            this.anims.create({
                key: `her-${name}`,
                frames: meta.anims[name].map(frame => ({ key: 'her', frame })),
                frameRate: fps,
                repeat: -1,
            });
        }
        const params = new URLSearchParams(location.search);
        this.scene.start(params.has('play') ? 'ship' : 'title');
    }
}
