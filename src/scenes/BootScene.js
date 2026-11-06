import { PLAYER, BUMBOT } from '../config.js';
import { makeTextures } from '../textures.js';

export class BootScene extends Phaser.Scene {
    constructor() {
        super('boot');
    }

    preload() {
        // Relative paths only: on GitHub Pages the game lives under /<repo>/ (§7.2).
        this.load.tilemapTiledJSON('ship', 'maps/ship.json');
        this.load.image('tiles', 'assets/tiles/placeholder.png');
        this.load.atlas('shipart', 'assets/ship/ship.png', 'assets/ship/ship.json');
        this.load.image('livery', 'assets/ship/livery.png');
        this.load.image('lifeboat', 'assets/ship/lifeboat.png');
        this.load.image('cabin-8206', 'assets/ship/cabin-8206.png');
        this.load.image('cabin-door-open', 'assets/ship/cabin-door-open.png');
        this.load.spritesheet('her', 'assets/sprites/her.png', { frameWidth: PLAYER.cell, frameHeight: PLAYER.cell });
        this.load.json('her-meta', 'assets/sprites/her.json');
        this.load.spritesheet('bumbot', 'assets/sprites/bumbot.png', { frameWidth: BUMBOT.cell, frameHeight: BUMBOT.cell });
        this.load.json('bumbot-meta', 'assets/sprites/bumbot.json');
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
        // The look back holds on its turned frames (2-4) for about a second, or it is missed.
        const look = [0, 1, 2, 3, 3, 3, 4, 4, 4, 5, 6, 7];
        this.anims.create({ key: 'her-idle-look', frames: frames('idle-look', look), frameRate: 7 });
        // Bending down to pick Bumbot up (a near-catch), and straightening up again.
        this.anims.create({ key: 'her-reach', frames: frames('reach'), frameRate: 10 });
        this.anims.create({ key: 'her-straighten', frames: frames('reach').reverse(), frameRate: 12 });
        // Waving from the life ring, overboard: the frames with her hand up, back and forth.
        this.anims.create({ key: 'her-wave', frames: frames('wave', [1, 2, 3, 4, 5, 4, 3, 2]), frameRate: 9, repeat: -1 });
        // At the bow: arms spread wide into the wind, held (the bow view).
        this.anims.create({ key: 'her-arms-wide', frames: frames('arms-wide', [1, 2, 3, 4, 5]), frameRate: 8 });
        // Breaststroke in a pool.
        this.anims.create({ key: 'her-swim', frames: frames('swim'), frameRate: 8, repeat: -1 });
        // Bumbot: his spot activities loop until she comes close; the run is his escape.
        const cat = this.cache.json.get('bumbot-meta');
        const catFrames = (name, order = cat.anims[name].map((_, i) => i)) =>
            order.map(i => ({ key: 'bumbot', frame: cat.anims[name][i] }));
        for (const [name, fps, repeat] of [['run', 16, -1], ['wash', 7, -1], ['sit', 6, 0], ['eat', 7, -1], ['jump', 12, 0]]) {
            this.anims.create({ key: `bumbot-${name}`, frames: catFrames(name), frameRate: fps, repeat });
        }
        // Catching a fly at the pool: the leap, over and over, with a pause on the ground.
        this.anims.create({ key: 'bumbot-fly', frames: catFrames('jump'), frameRate: 12, repeat: -1, repeatDelay: 900 });
        // Batting: seated, paw down and up. Its frames 6 and 8 drew stray blobs, so they are skipped.
        this.anims.create({ key: 'bumbot-bat', frames: catFrames('bat', [4, 5, 7, 5]), frameRate: 6, repeat: -1 });
        const params = new URLSearchParams(location.search);
        this.scene.start(params.has('play') ? 'ship' : 'title');
    }
}
