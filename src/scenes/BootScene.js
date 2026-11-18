import { PLAYER, BUMBOT, THROW, GAG_CELL } from '../config.js';
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
            // (What of a room's picture is in front of the things lying in it: a bowl's side.)
            for (const r of world.rooms) if (r.front) this.load.image(`room-${r.id}-front`, `assets/ship/rooms/${r.id}-front.png`);
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
        // With Bumbot in her arms (the way home, §6.1.9).
        this.load.spritesheet('her-cat', 'assets/sprites/her-cat.png', { frameWidth: PLAYER.cell, frameHeight: PLAYER.cell });
        this.load.json('her-cat-meta', 'assets/sprites/her-cat.json');
        // Her mishap gags, each one picture of her with the thing (docs/plan-three-uses.md §1.6).
        this.load.spritesheet('her-mishaps', 'assets/sprites/her-mishaps.png', { frameWidth: GAG_CELL, frameHeight: GAG_CELL });
        this.load.json('her-mishaps-meta', 'assets/sprites/her-mishaps.json');
        // The towel stack's own clips (deck 9; tools/build_towels.py): its fall, it on her, her coming up.
        this.load.spritesheet('towels', 'assets/sprites/towels.png', { frameWidth: 128, frameHeight: 128 });
        this.load.json('towels-meta', 'assets/sprites/towels.json');
        // Step 4a's first gags (tools/build_gags.py): the door that bursts open (13a), the tray ridden (3),
        // the deck chair that collapses (7b), the gull on her head (20).
        this.load.spritesheet('gags', 'assets/sprites/gags.png', { frameWidth: 128, frameHeight: 128 });
        this.load.json('gags-meta', 'assets/sprites/gags.json');
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
        // The welcome screen's menu (tools/build_menu.py): its lettering and its plate.
        this.load.atlas('menu', 'assets/sprites/menu.png', 'assets/sprites/menu.json');
    }

    // A copy of some of her frames (by index in her sheet) with everything from row `chin` of each
    // cell down turned into a plain silhouette: the shape filled with one colour, its edge darker.
    veilFrames(key, indices, chin) {
        const cell = PLAYER.cell;
        const src = this.textures.get('her').getSourceImage();
        const tex = this.textures.createCanvas(key, cell * indices.length, cell);
        const ctx = tex.getContext();
        // (Each frame from where it is on her sheet: it is packed in rows since step 9, so frame n is
        // not at n cells along; read as one strip, the shower's frames came out empty and she was
        // hidden behind the glass.)
        indices.forEach((n, i) => {
            const f = this.textures.getFrame('her', n);
            ctx.drawImage(src, f.cutX, f.cutY, cell, cell, i * cell, 0, cell, cell);
        });
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
        // Her falls: down (their first four frames), then dazed where she lies, butterflies circling
        // over her head (clips of their own, drawn with them).
        for (const name of ['slipfall', 'tripfall']) {
            if (meta.anims[name]) this.anims.create({ key: `her-${name}`, frames: frames(name, [0, 1, 2, 3]), frameRate: 10 });
        }
        // (Their first frame is the pose they start from, without the butterflies: left out.)
        for (const name of ['dazed-sit', 'dazed-lie']) {
            if (meta.anims[name]) this.anims.create({ key: `her-${name}`, frames: frames(name, [1, 2, 3, 4, 5]), frameRate: 6, repeat: -1 });
        }
        if (meta.anims.slipback) this.anims.create({ key: 'her-slipback', frames: frames('slipback'), frameRate: 9 });
        if (meta.anims.stumble) this.anims.create({ key: 'her-stumble', frames: frames('stumble'), frameRate: 9 });
        // Her reactions to a hit with a tangerine on her (docs/plan-three-uses.md §1.6), once each.
        for (const [name, fps] of [['reel', 9], ['rubnose', 9], ['splutter', 9], ['arch', 9], ['yelp', 10], ['duck', 9], ['apology', 7]]) {
            if (meta.anims[name]) this.anims.create({ key: `her-${name}`, frames: frames(name), frameRate: fps });
        }
        for (const [name, fps] of [['shiver', 12], ['dance', 9], ['pose', 6], ['bow', 8]]) {
            if (meta.anims[name]) this.anims.create({ key: `her-${name}`, frames: frames(name), frameRate: fps, repeat: -1 });
        }
        // Her verbs' own clips (§6.1.2): on hands and knees, pushing a cart; the honeymooners' camera
        // raised to her eye and held.
        if (meta.anims.crawl) this.anims.create({ key: 'her-crawl', frames: frames('crawl'), frameRate: 11, repeat: -1 });
        // (11 a second at VERBS.pushSpeed: her planted foot slides back about 3.6 px a frame, as the floor.)
        if (meta.anims.push) this.anims.create({ key: 'her-push', frames: frames('push'), frameRate: 11, repeat: -1 });
        if (meta.anims.camera) this.anims.create({ key: 'her-camera', frames: frames('camera', [0, 1, 2, 3]), frameRate: 9 });
        // Region 6: clinging to a wall, slipping on wet tiles, licking a cone, the canister held up,
        // sitting down at the table and eating there.
        if (meta.anims.wallslide) this.anims.create({ key: 'her-wallslide', frames: frames('wallslide'), frameRate: 7, repeat: -1 });
        if (meta.anims.slip) this.anims.create({ key: 'her-slip', frames: frames('slip'), frameRate: 11, repeat: -1 });
        if (meta.anims.lick) this.anims.create({ key: 'her-lick', frames: frames('lick'), frameRate: 5, repeat: -1 });
        if (meta.anims.pour) this.anims.create({ key: 'her-pour', frames: frames('pour'), frameRate: 4 });
        // Region 9: her fingers on the Spinnaker's piano; her knock at the captain's door, her back to us.
        if (meta.anims.keys) this.anims.create({ key: 'her-keys', frames: frames('keys'), frameRate: 9 });
        if (meta.anims.knock) this.anims.create({ key: 'her-knock', frames: frames('knock'), frameRate: 9 });
        // At her cabin's mirror: a hand over her hair (the intro plays her `badge` clip frame by frame).
        if (meta.anims.hair) this.anims.create({ key: 'her-hair', frames: frames('hair'), frameRate: 8 });
        if (meta.anims['sit-eat']) {
            this.anims.create({ key: 'her-sit-eat', frames: frames('sit-eat', [0, 1, 2, 3]), frameRate: 7 });
            this.anims.create({ key: 'her-eat-sat', frames: frames('sit-eat', [3, 4, 5, 6, 5, 4]), frameRate: 5, repeat: -1 });
        }
        // Region 8: the horn's cord pulled, held at its lowest; a shot at the hoop; hanging from the
        // open parasol's handle.
        if (meta.anims.pull) this.anims.create({ key: 'her-pull', frames: frames('pull', [0, 1, 2, 3, 4]), frameRate: 10 });
        if (meta.anims.throw) this.anims.create({ key: 'her-throw', frames: frames('throw'), frameRate: 12 });
        // F: her underarm toss (docs/plan-three-uses.md §1.2); THROW.releaseMs is its fifth frame.
        if (meta.anims.toss) this.anims.create({ key: 'her-toss', frames: frames('toss'), frameRate: THROW.fps });
        if (meta.anims.glide) this.anims.create({ key: 'her-glide', frames: frames('glide'), frameRate: 2, repeat: -1 });
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
        // With Bumbot in her arms: her walk, and her head bent to him now and then as she stands.
        const held = this.cache.json.get('her-cat-meta');
        const heldFrames = (name, order = held.anims[name].map((_, i) => i)) =>
            order.map(i => ({ key: 'her-cat', frame: held.anims[name][i] }));
        this.anims.create({ key: 'her-cat-run', frames: heldFrames('run'), frameRate: 11, repeat: -1 });
        this.anims.create({ key: 'her-cat-stroke', frames: heldFrames('stroke', [0, 1, 2, 3, 4, 4, 4, 3, 4, 4, 3, 2, 1, 0]), frameRate: 6 });
        // Her gags with a thing (§1.6): sitting down onto it, the ride, the end of it; the papers' (`gag-<clip>`).
        const gag = this.cache.json.get('her-mishaps-meta');
        for (const [name, fps, repeat] of [['vacuum-sit', 11, 0], ['vacuum-ride', 10, -1],
                                           ['suitcase-sit', 11, 0], ['suitcase-ride', 8.8, -1], ['suitcase-tip', 11, 0], ['suitcase-dazed', 11, -1],
                                           ['paper-behind', 10, 0], ['paper-front', 10, 0],
                                           ['cart-drape', 10, 0], ['cart-kick', 4, -1], ['cart-sit', 10, 0], ['cart-push', 10, 0], ['cart-bounce', 10, 0],
                                           ['tray-sit', 10, 0], ['trolley-trip', 10, 0],
                                           ['dog-lick', 8, 1]]) {
            if (!gag.anims[name]) continue;
            // (The papers' first three frames quicker: the paper's push carried into the fall.)
            const fast = name.startsWith('paper-') ? 3 : 0;
            this.anims.create({ key: `gag-${name}`, frames: gag.anims[name].map((f, i) => ({ key: 'her-mishaps', frame: f, duration: i < fast ? 60 : undefined })), frameRate: fps, repeat });
        }
        // The towel stack's (`TowelStack` in src/world/movers.js): frame 0 of each is the start, left out.
        const tw = this.cache.json.get('towels-meta');
        for (const [name, fps] of [['fall', 12], ['bury', 11], ['emerge', 9]])
            this.anims.create({ key: `towels-${name}`, frames: tw.anims[name].slice(1).map(f => ({ key: 'towels', frame: f })), frameRate: fps });
        // The fall on her running (one from each phase of her run): all nine, frame 0 her own run frame; she
        // runs on in the first at her run's own 14 a second (10 px a frame: her 140 px/s), then 11.
        for (const n of [0, 2, 4, 6])
            this.anims.create({ key: `towels-run${n}`, frames: tw.anims[`run${n}`].map((f, i) => ({ key: 'towels', frame: f, duration: i < 4 ? 71 : 91 })) });
        // Step 4a's first gags (`gags` sheet): frame 0 of a clip is the world's own picture (the shut
        // door; her own run, slip or standing frame with the thing), left out where the world shows it.
        const gg = this.cache.json.get('gags-meta');
        const gf = (name, from = 0, to = gg.anims[name].length, ms) => gg.anims[name].slice(from, to).map((f, i) => ({ key: 'gags', frame: f, duration: ms?.(i) }));
        this.anims.create({ key: 'gags-door-burst', frames: gf('door-burst', 1), frameRate: 13 });
        this.anims.create({ key: 'gags-door-squash', frames: gf('door-squash', 1), frameRate: 13 });
        this.anims.create({ key: 'gags-door-slide', frames: gf('door-slide', 1), frameRate: 8 });
        // (A "Do Not Disturb" door: open on the guest, held there, then shut.)
        this.anims.create({ key: 'gags-dnd-open', frames: gf('door-burst-full', 1, 6), frameRate: 13 });
        this.anims.create({ key: 'gags-dnd-shut', frames: gf('door-burst-full', 6), frameRate: 13 });
        // (The hop onto the tray at her run's own 14 a second, then the ride; its last four wheel on.)
        for (const k of ['tray-ride', 'tray-ride3', 'tray-ride1', 'tray-ride5']) {
            this.anims.create({ key: `gags-${k}`, frames: gf(k, 0, 9, i => (i < 3 ? 71 : 95)) });
            this.anims.create({ key: `gags-${k}-wheel`, frames: gf(k, 5, 9), frameRate: 9, repeat: -1 });
        }
        this.anims.create({ key: 'gags-chair', frames: gf('chair-collapse', 1), frameRate: 10 });
        this.anims.create({ key: 'gags-gull-flail', frames: gf('gull-flail', 1), frameRate: 10 });
        this.anims.create({ key: 'gags-gull-run', frames: gf('gull-run', 1), frameRate: 12, repeat: -1 });
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
        // (The welcome screen and the intro are the ship scene's own: src/intro.js.)
        this.scene.start('ship');
    }
}
