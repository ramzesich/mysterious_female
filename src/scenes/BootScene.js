import { PLAYER, BUMBOT } from '../config.js';
import { makeTextures } from '../textures.js';

export class BootScene extends Phaser.Scene {
    constructor() {
        super('boot');
    }

    preload() {
        // Relative paths only: on GitHub Pages the game lives under /<repo>/ (§7.2).
        this.load.tilemapTiledJSON('ship', 'maps/ship.json');
        // The plan's world (tools/population.py through the map builder): rooms, people, things.
        this.load.json('world', 'maps/world.json');
        // Its rooms that are drawn (tools/draw_rooms.py); the others the game draws bare.
        this.load.once('filecomplete-json-world', (_key, _type, world) => {
            for (const r of world.rooms) if (r.art) this.load.image(`room-${r.id}`, `assets/ship/rooms/${r.id}.png`);
        });
        this.load.image('tiles', 'assets/tiles/placeholder.png');
        this.load.atlas('shipart', 'assets/ship/ship.png', 'assets/ship/ship.json');
        this.load.atlas('livery', 'assets/ship/livery.png', 'assets/ship/livery.json');
        this.load.image('lifeboat', 'assets/ship/lifeboat.png');
        this.load.image('tender', 'assets/ship/tender.png');
        this.load.image('rescue-boat', 'assets/ship/rescue-boat.png');
        this.load.image('cabin-8206', 'assets/ship/cabin-8206.png');
        this.load.image('cabin-door-open', 'assets/ship/cabin-door-open.png');
        this.load.image('linen-room', 'assets/ship/linen-room.png');
        this.load.image('linen-door-open', 'assets/ship/linen-door-open.png');
        // The linen room's laundry cart (she pushes it), the adjoining cabins' blanket fort (in front
        // of her), and what shows under the duct's grilles (tools/draw_rooms.py).
        this.load.image('linen-cart', 'assets/ship/linen-cart.png');
        this.load.image('fort', 'assets/ship/rooms/adjoin-fort.png');
        for (const what of ['lobby', 'dome', 'balloons', 'snore']) this.load.image(`peek-${what}`, `assets/ship/peeks/${what}.png`);
        this.load.image('chapel-room', 'assets/ship/chapel-room.png');
        this.load.image('chapel-door-open', 'assets/ship/chapel-door-open.png');
        this.load.spritesheet('her', 'assets/sprites/her.png', { frameWidth: PLAYER.cell, frameHeight: PLAYER.cell });
        this.load.json('her-meta', 'assets/sprites/her.json');
        this.load.spritesheet('her-towel', 'assets/sprites/her-towel.png', { frameWidth: PLAYER.cell, frameHeight: PLAYER.cell });
        this.load.json('her-towel-meta', 'assets/sprites/her-towel.json');
        for (const name of ['inside', 'open', 'glass', 'towel']) this.load.image(`cabin-shower-${name}`, `assets/ship/cabin-shower-${name}.png`);
        this.load.spritesheet('bumbot', 'assets/sprites/bumbot.png', { frameWidth: BUMBOT.cell, frameHeight: BUMBOT.cell });
        this.load.json('bumbot-meta', 'assets/sprites/bumbot.json');
        // The ship's people (tools/cast.py, tools/build_people.py): one sheet, a grid of equal cells.
        this.load.json('people-meta', 'assets/sprites/people.json');
        this.load.spritesheet('people', 'assets/sprites/people.png', { frameWidth: 80, frameHeight: 80 });
        // The plan's own things (the delivery robot, the gulls: tools/build_things.py), and the ten
        // books' pages (tools/draw_pages.py).
        this.load.atlas('things', 'assets/sprites/things.png', 'assets/sprites/things.json');
        for (let n = 1; n <= 10; n++) this.load.image(`page-${n}`, `assets/ship/pages/page-${n}.png`);
    }

    // A copy of some of her frames (by index in her sheet) with everything from row `chin` of each
    // cell down turned into a plain silhouette: the shape filled with one colour, its edge darker.
    veilFrames(key, indices, chin) {
        const cell = PLAYER.cell;
        const src = this.textures.get('her').getSourceImage();
        const tex = this.textures.createCanvas(key, cell * indices.length, cell);
        const ctx = tex.getContext();
        indices.forEach((n, i) => ctx.drawImage(src, n * cell, 0, cell, cell, i * cell, 0, cell, cell));
        const img = ctx.getImageData(0, 0, tex.width, cell);
        const d = img.data, w = tex.width;
        const solid = (x, y) => x >= 0 && x < w && y < cell && d[(y * w + x) * 4 + 3] > 0;
        const fill = [0xe8, 0xab, 0x9d], edge = [0xc7, 0x8a, 0x81];
        const out = new Uint8ClampedArray(d);
        for (let y = chin; y < cell; y++) {
            for (let x = 0; x < w; x++) {
                const k = (y * w + x) * 4;
                if (!d[k + 3]) continue;
                const rim = !solid(x - 1, y) || !solid(x + 1, y) || !solid(x, y + 1) || (x % cell === 0);
                out.set(rim ? edge : fill, k);
                out[k + 3] = 255;
            }
        }
        img.data.set(out);
        ctx.putImageData(img, 0, 0);
        indices.forEach((_, i) => tex.add(i, 0, i * cell, 0, cell, cell));
        tex.refresh();
        return key;
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
        // With a tray in her hands (§6.1.2): her walk with her forearms out, if it is drawn yet.
        if (meta.anims['carry-run']) {
            this.anims.create({ key: 'her-carry-run', frames: frames('carry-run'), frameRate: 11, repeat: -1 });
        }
        // A start at a bump; her quirks (§6.1.11), each a clip of its own.
        if (meta.anims.hit) this.anims.create({ key: 'her-hit', frames: frames('hit', [0, 1, 1, 2, 3]), frameRate: 10 });
        for (const [name, fps] of [['shiver', 12], ['dance', 9], ['pose', 6], ['bow', 8]]) {
            if (meta.anims[name]) this.anims.create({ key: `her-${name}`, frames: frames(name), frameRate: fps, repeat: -1 });
        }
        // Her verbs' own clips (§6.1.2): on hands and knees, pushing a cart; the honeymooners' camera
        // raised to her eye and held.
        if (meta.anims.crawl) this.anims.create({ key: 'her-crawl', frames: frames('crawl'), frameRate: 11, repeat: -1 });
        if (meta.anims.push) this.anims.create({ key: 'her-push', frames: frames('push'), frameRate: 9, repeat: -1 });
        if (meta.anims.camera) this.anims.create({ key: 'her-camera', frames: frames('camera', [0, 1, 2, 3]), frameRate: 9 });
        // Region 6: clinging to a wall, slipping on wet tiles, licking a cone, the canister held up,
        // sitting down at the table and eating there.
        if (meta.anims.wallslide) this.anims.create({ key: 'her-wallslide', frames: frames('wallslide'), frameRate: 7, repeat: -1 });
        if (meta.anims.slip) this.anims.create({ key: 'her-slip', frames: frames('slip'), frameRate: 11, repeat: -1 });
        if (meta.anims.lick) this.anims.create({ key: 'her-lick', frames: frames('lick'), frameRate: 5, repeat: -1 });
        if (meta.anims.pour) this.anims.create({ key: 'her-pour', frames: frames('pour'), frameRate: 4 });
        if (meta.anims['sit-eat']) {
            this.anims.create({ key: 'her-sit-eat', frames: frames('sit-eat', [0, 1, 2, 3]), frameRate: 7 });
            this.anims.create({ key: 'her-eat-sat', frames: frames('sit-eat', [3, 4, 5, 6, 5, 4]), frameRate: 5, repeat: -1 });
        }
        // Reading in the library's chair: she sits down, and stays sat with the book.
        if (meta.anims.read) this.anims.create({ key: 'her-read', frames: frames('read'), frameRate: 8 });
        // Bending down to pick Bumbot up (a near-catch), and straightening up again.
        this.anims.create({ key: 'her-reach', frames: frames('reach'), frameRate: 10 });
        this.anims.create({ key: 'her-straighten', frames: frames('reach').reverse(), frameRate: 12 });
        // Waving from the life ring, overboard: the frames with her hand up, back and forth.
        this.anims.create({ key: 'her-wave', frames: frames('wave', [1, 2, 3, 4, 5, 4, 3, 2]), frameRate: 9, repeat: -1 });
        // At the bow: arms spread wide into the wind, held (the bow view).
        this.anims.create({ key: 'her-arms-wide', frames: frames('arms-wide', [1, 2, 3, 4, 5]), frameRate: 8 });
        // Bouncing on the cabin's bed for joy, foot to foot, arms waving up and down (facing us): the
        // game steps through its frames itself, in time with her hops.
        this.anims.create({ key: 'her-bed-joy', frames: frames('bed-joy'), frameRate: 9, repeat: -1 });
        // Breaststroke in a pool.
        this.anims.create({ key: 'her-swim', frames: frames('swim'), frameRate: 8, repeat: -1 });
        // Washing her hair in cabin 8206's shower, behind its frosted door: from her chin down only
        // the shape of her, in one soft body colour with a slightly darker edge, never her clothes
        // (the user, 2026-11-08), under the door's thick frosting.
        const veil = this.veilFrames('her-shower-veil', meta.anims.shower, 40);
        this.anims.create({ key: 'her-shower', frames: [0, 1, 2, 3, 4, 5, 4, 3, 2, 1].map(i => ({ key: veil, frame: i })), frameRate: 7, repeat: -1 });
        // After the shower, a towel round her head (cabin 8206): the same clips, under 'her-towel-'.
        const towel = this.cache.json.get('her-towel-meta');
        const towelFrames = (name, order = towel.anims[name].map((_, i) => i)) =>
            order.map(i => ({ key: 'her-towel', frame: towel.anims[name][i] }));
        this.anims.create({ key: 'her-towel-run', frames: towelFrames('run'), frameRate: 14, repeat: -1 });
        this.anims.create({ key: 'her-towel-idle-tap', frames: towelFrames('idle-tap', tap), frameRate: 7 });
        this.anims.create({ key: 'her-towel-idle-look', frames: towelFrames('idle-look', look), frameRate: 7 });
        this.anims.create({ key: 'her-towel-bed-joy', frames: towelFrames('bed-joy'), frameRate: 9, repeat: -1 });
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
        // Wet from the pool, he shakes himself dry.
        if (cat.anims.shake) this.anims.create({ key: 'bumbot-shake', frames: catFrames('shake', [1, 2, 3, 4, 5, 6]), frameRate: 8 });
        const params = new URLSearchParams(location.search);
        this.scene.start(params.has('play') ? 'ship' : 'title');
    }
}
