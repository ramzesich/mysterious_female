import { PLAYER, BUMBOT, THROW, GAG_CELL, BOOKS, DESK_THINGS, BED_THINGS, SHRUG } from '../config.js';
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
            // (What of a room is in front of her while she stands on its bed: the maid's cabin's swan.)
            for (const e of world.ents) if (e.kind === 'platform' && e.front) this.load.image(`room-${e.front}`, `assets/ship/rooms/${e.front}.png`);
        });
        this.load.image('tiles', 'assets/tiles/placeholder.png');
        this.load.atlas('shipart', 'assets/ship/ship.png', 'assets/ship/ship.json');
        this.load.atlas('livery', 'assets/ship/livery.png', 'assets/ship/livery.json');
        // A one-way glass door's open leaf, its push bar across it (assets/source/ship/pushbar/).
        this.load.image('door-glass-pushbar', 'assets/ship/door-glass-pushbar.png');
        this.load.image('trapdoor-open', 'assets/ship/trapdoor-open.png');
        this.load.image('door-glass-oneway-edge', 'assets/ship/door-glass-oneway-edge.png');
        // (A "Do Not Disturb" door shut with its sign on the lever's mount, and the sign alone, on the balconies'
        // partitions: `assets/source/ship/dnd-hanger/`.)
        this.load.image('door-cabin-dnd', 'assets/ship/door-cabin-dnd.png');
        this.load.image('dnd-hanger', 'assets/ship/dnd-hanger.png');
        this.load.image('lifeboat', 'assets/ship/lifeboat.png');
        this.load.image('lifeboat-round', 'assets/ship/lifeboat-round.png');   // (the one she goes into, round windows)
        this.load.image('tender', 'assets/ship/tender.png');
        this.load.image('rescue-boat', 'assets/ship/rescue-boat.png');
        this.load.image('cabin-8206', 'assets/ship/cabin-8206.png');
        this.load.image('cabin-8206-bed', 'assets/ship/cabin-8206-bed.png');   // (the bed again, over her husband on the sofa)
        // (Her husband's near hand drawn again over her as they embrace at his table: `husband-raw/embrace/hand.py`.)
        for (const n of [1, 2]) this.load.image(`hug-hand-${n}`, `assets/sprites/hug-hand-${n}.png`);
        this.load.image('cabin-door-open', 'assets/ship/cabin-door-open.png');
        this.load.image('linen-room', 'assets/ship/linen-room.png');
        // The laundry chute (tools/build_laundry_chute.py): her going in at the linen room's hatch, the towel she comes
        // out of it with, and where each is.
        this.load.spritesheet('chute-in', 'assets/ship/chute/in.png', { frameWidth: 128, frameHeight: 128 });
        this.load.image('chute-towel', 'assets/ship/chute/towel.png');
        this.load.image('chute-dive', 'assets/ship/chute/dive.png');
        this.load.spritesheet('chute-towel-fall', 'assets/ship/chute/towel-fall.png', { frameWidth: 64, frameHeight: 64 });
        this.load.json('chute', 'assets/ship/chute/chute.json');
        this.load.image('linen-door-open', 'assets/ship/linen-door-open.png');
        // The linen room's laundry cart (she pushes it), the adjoining cabins' blanket fort (in front
        // of her), and what shows under the duct's grilles (tools/draw_rooms.py).
        this.load.image('fort', 'assets/ship/rooms/adjoin-fort.png');
        // The shaft from the linen room to deck 8 forward (tools/build_shaft.py), where each of its pictures stands.
        for (const what of ['strip', 'front', 'mouth', 'mouth-far', 'cover', 'cover-down', 'exit-grille', 'exit-hole', 'exit-hang']) this.load.image(`shaft-${what}`, `assets/ship/shaft/${what}.png`);
        this.load.json('shaft', 'assets/ship/shaft/shaft.json');
        // (The cover's fall off the mouth: a quarter turn in 13 squares of 42 px, `fall` in shaft.json.)
        this.load.spritesheet('shaft-cover-fall', 'assets/ship/shaft/cover-fall.png', { frameWidth: 42, frameHeight: 42 });
        // (The way out's grille swinging down on its hinge: `swing` in shaft.json.)
        this.load.spritesheet('shaft-exit-swing', 'assets/ship/shaft/exit-swing.png', { frameWidth: 48, frameHeight: 40 });
        this.load.atlas('shaft-slide', 'assets/ship/shaft/slide.png', 'assets/ship/shaft/slide.json');
        // The pool's scene (tools/build_pool.py): the drain's lever, the hatch in the tank's floor, the drain's grate, the
        // ladder's lower part, the ceiling panel in deck 10's hallway; where each stands.
        this.load.json('pool-layout', 'assets/ship/pool/pool.json');
        this.load.image('pool-lever-strip', 'assets/ship/pool/lever.png');
        for (const what of ['hatch-shut', 'hatch-back', 'hatch-lip', 'drain', 'ceiling-shut', 'ceiling-open', 'ladder-low']) {
            this.load.image(`pool-${what}`, `assets/ship/pool/${what}.png`);
        }
        // The Seven Seas' pass, near-catch 1 (tools/build_pass.py): its counter, the plate of the lunch, the fruit bowl's
        // fall off the counter's end (frames of 96 x 64; where they stand: pass.json).
        this.load.json('pass-layout', 'assets/ship/pass/pass.json');
        this.load.image('pass-counter', 'assets/ship/pass/counter.png');
        this.load.image('pass-plate', 'assets/ship/pass/plate.png');
        this.load.spritesheet('pass-bowl-fall', 'assets/ship/pass/bowl-fall.png', { frameWidth: 96, frameHeight: 64 });
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
        // The Library's return trolley and the board of the shelf the books go back to (generated: library.js).
        this.load.image('book-trolley', 'assets/sprites/book-trolley.png');
        this.load.image('book-shelf', 'assets/sprites/book-shelf.png');
        // Cabin 8206's desk seen close: the bare desk and her four things and his four (tools/build_desk.py).
        this.load.image('desk-bare', 'assets/ship/desk/bare.png');
        this.load.json('desk-layout', 'assets/ship/desk/layout.json');
        for (const k of DESK_THINGS) this.load.image(`desk-${k}`, `assets/ship/desk/${k}.png`);
        this.load.image('bed-bare', 'assets/ship/bed/bare.png');
        this.load.json('bed-layout', 'assets/ship/bed/layout.json');
        for (const k of BED_THINGS) this.load.image(`bed-${k}`, `assets/ship/bed/${k}.png`);
        // The photo slots' pictures (§6.1.11; E at a slot's frame opens its picture over the screen: world.js's `slot`):
        // the reading nook's, her armchair at home (the user's photo, cut out, redrawn by PixelLab, recoloured to her greys).
        for (const id of ['slot_nook', 'slot_cucina']) {
            this.load.image(`photo-${id}`, `assets/ship/photos/${id}.png`);
            this.load.image(`thumb-${id}`, `assets/ship/photos/thumb-${id}.png`);     // (on the wall: small, framed)
        }
        // A small puff of dust (the Library's bookcase sliding open; assets/source/things/dust-puff/README.md).
        this.load.spritesheet('dust-puff', 'assets/sprites/dust-puff.png', { frameWidth: 20, frameHeight: 21 });
        this.load.spritesheet('towels', 'assets/sprites/towels.png', { frameWidth: 128, frameHeight: 128 });
        this.load.json('towels-meta', 'assets/sprites/towels.json');
        // Step 4a's first gags (tools/build_gags.py): the door that bursts open (13a), the tray ridden (3),
        // the deck chair that collapses (7b), the gull on her head (20).
        this.load.spritesheet('gags', 'assets/sprites/gags.png', { frameWidth: 128, frameHeight: 128 });
        // (The court's two players, `tools/build_court.py`: their frames set by the balls' round, `Balls` in topdeck.js.)
        this.load.spritesheet('court', 'assets/sprites/court.png', { frameWidth: 96, frameHeight: 96 });
        this.load.json('court-meta', 'assets/sprites/court.json');
        this.load.json('gags-meta', 'assets/sprites/gags.json');
        for (const name of ['inside', 'open', 'glass', 'towel']) this.load.image(`cabin-shower-${name}`, `assets/ship/cabin-shower-${name}.png`);
        this.load.spritesheet('bumbot', 'assets/sprites/bumbot.png', { frameWidth: BUMBOT.cell, frameHeight: BUMBOT.cell });
        this.load.json('bumbot-meta', 'assets/sprites/bumbot.json');
        // The ship's people (tools/cast.py, tools/build_people.py): one sheet, a grid of equal cells.
        this.load.json('people-meta', 'assets/sprites/people.json');
        this.load.spritesheet('people', 'assets/sprites/people.png', { frameWidth: 80, frameHeight: 80 });
        // The plan's own things (the delivery robot, the gulls: tools/build_things.py).
        this.load.atlas('things', 'assets/sprites/things.png', 'assets/sprites/things.json');
        // The flower frame round the screen while she carries delivery 1's vase (tools/build_things.py).
        this.load.image('flower-frame', 'assets/sprites/flower-frame.png');
        // Each thing to find and each key card seen close, shown when she gets it (tools/build_closeups.py).
        this.load.atlas('closeups', 'assets/sprites/closeups.png', 'assets/sprites/closeups.json');
        // Each book's first page and its title in the pages' lettering, for the row she chooses from
        // (tools/draw_pages.py); her reading clips, in the armchairs and on her bed (tools/build_reading.py).
        for (let n = 1; n <= BOOKS; n++) {
            this.load.image(`page-${n}`, `assets/ship/pages/page-${n}.png`);
            this.load.image(`book-title-${n}`, `assets/ship/pages/title-${n}.png`);
            // (its cover, her own copy's, shown when she gets it: tools/build_covers.py)
            this.load.image(`cover-${n}`, `assets/ship/covers/cover-${n}.png`);
            this.load.image(`cover-mini-${n}`, `assets/ship/covers/mini-${n}.png`);
        }
        this.load.atlas('reading', 'assets/sprites/reading.png', 'assets/sprites/reading.json');
        this.load.json('reading-meta', 'assets/sprites/reading.json');
        // The boat drill's own clips (tools/build_drill.py): the crewman turning his winch; her gag under the boat.
        this.load.spritesheet('drill', 'assets/sprites/drill.png', { frameWidth: 96, frameHeight: 96 });
        this.load.json('drill-meta', 'assets/sprites/drill.json');
        // Her pull-up over the lifeboat's roof hatch, facing us (tools/build_hatch.py).
        this.load.spritesheet('mantle-front', 'assets/sprites/mantle-front.png', { frameWidth: 96, frameHeight: 96 });
        this.load.json('mantle-front-meta', 'assets/sprites/mantle-front.json');
        // The welcome screen's menu (tools/build_menu.py): its lettering and its plate.
        this.load.atlas('menu', 'assets/sprites/menu.png', 'assets/sprites/menu.json');
        // The sky's art (tools/build_sky.py): the intro's clouds and sun, where they stand, the god
        // rays and the bloom; the far clouds' strip of the game's background.
        this.load.atlas('skyart', 'assets/sprites/sky.png', 'assets/sprites/sky.json');
        this.load.json('sky-layout', 'assets/sprites/sky-layout.json');
        this.load.image('sky-rays', 'assets/sprites/sky-rays.png');
        this.load.image('sky-glow', 'assets/sprites/sky-glow.png');
        this.load.image('sky-strip', 'assets/sprites/sky-strip.png');
        this.load.image('sky-dusk-rays', 'assets/sprites/sky-dusk-rays.png');
        this.load.image('sky-dusk-glow', 'assets/sprites/sky-dusk-glow.png');
        this.load.image('sky-dusk-strip', 'assets/sprites/sky-dusk-strip.png');
        // The popups' art (tools/build_popups.py: frames, icons, lettering) and where every picture's
        // head is (tools/build_heads.py), for src/popup.js.
        this.load.atlas('popups', 'assets/sprites/popups.png', 'assets/sprites/popups.json');
        this.load.json('popup-layout', 'assets/sprites/popup-layout.json');
        // The HUD's pictures (tools/build_hud.py), for src/hud.js.
        this.load.atlas('hud', 'assets/sprites/hud.png', 'assets/sprites/hud.json');
        this.load.json('heads', 'assets/sprites/heads.json');
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
        // Holding on to the funnel stairway's rail in a gust (assets/source/her/stair-cling/): she crouches
        // into it, holds on with her hair fluttering, and stands back up by the crouch backwards.
        for (const way of ['up', 'down']) {
            const name = `cling-${way}`;
            if (!meta.anims[name]) continue;
            this.anims.create({ key: `her-${name}-in`, frames: frames(name, [1, 2, 3, 4, 5, 6, 7, 8]), frameRate: 16 });
            this.anims.create({ key: `her-${name}-hold`, frames: frames(name, [5, 6, 7, 8, 7, 6]), frameRate: 8, repeat: -1 });
            this.anims.create({ key: `her-${name}-out`, frames: frames(name, [6, 4, 3, 2, 1, 0]), frameRate: 14 });
        }
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
        // Facing us, a shrug: a way she cannot go, a near-catch missed (SHRUG).
        if (meta.anims.shrug) this.anims.create({ key: 'her-shrug', frames: frames('shrug'), frameRate: SHRUG.fps });
        // At her husband's table: down into the patio chair with her cone, licking it, getting up after the book.
        if (meta.anims['sit-cone']) {
            this.anims.create({ key: 'her-sit-cone', frames: frames('sit-cone'), frameRate: 8 });
            this.anims.create({ key: 'her-lick-cone', frames: frames('lick-cone'), frameRate: 5, repeat: -1 });
            this.anims.create({ key: 'her-sat', frames: frames('sat') });
            this.anims.create({ key: 'her-sit-up', frames: frames('sit-up'), frameRate: 10 });
        }
        // Her arms up round his neck as they kiss (back to us), and down again (played backwards).
        if (meta.anims.embrace) this.anims.create({ key: 'her-embrace', frames: frames('embrace'), frameRate: 8 });
        // Region 8: the horn's cord pulled, held at its lowest; a shot at the hoop; hanging from the
        // open parasol's handle.
        if (meta.anims.pull) this.anims.create({ key: 'her-pull', frames: frames('pull', [0, 1, 2, 3, 4]), frameRate: 10 });
        if (meta.anims.throw) this.anims.create({ key: 'her-throw', frames: frames('throw'), frameRate: 12 });
        // F: her underarm toss (docs/plan-three-uses.md §1.2); THROW.releaseMs is its fifth frame.
        if (meta.anims.toss) this.anims.create({ key: 'her-toss', frames: frames('toss'), frameRate: THROW.fps });
        if (meta.anims.airtoss) this.anims.create({ key: 'her-airtoss', frames: frames('airtoss'), frameRate: THROW.airFps });
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
        // (At the pool's rim under Bumbot: her head up and an arm up out of the water after him, then held, straining.)
        if (meta.anims['swim-reach']) {
            this.anims.create({ key: 'her-swim-reach', frames: frames('swim-reach').slice(0, 5), frameRate: 9 });
            this.anims.create({ key: 'her-swim-strain', frames: frames('swim-reach').slice(4), frameRate: 6, repeat: -1 });
        }
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
        // (15: her drop under the drill's boat, from her run (its frame 0, left out), then her crawl on all fours.)
        const dm = this.cache.json.get('drill-meta');
        // (Quick, the user, 2026-11-21: "now there is a delay": from its third frame, at 20 a second.)
        this.anims.create({ key: 'drill-drop', frames: dm.drop.slice(2).map(f => ({ key: 'drill', frame: f })), frameRate: 20 });
        this.anims.create({ key: 'drill-crawl', frames: dm.crawl.map(f => ({ key: 'drill', frame: f })), frameRate: 10, repeat: -1 });
        // (7a: the trip and the dive quick, 240 ms from the hit to her landing on the chair (the user: "reduce the delay"); the rest at 10 a second.)
        this.anims.create({ key: 'gags-sledge', frames: gf('chair-sledge', 1, undefined, i => [40, 40, 50, 50, 60][i] ?? 100), frameRate: 10 });
        this.anims.create({ key: 'gags-jog-bowled', frames: gf('jog-bowled', 1), frameRate: 14 });
        for (const n of [1, 3, 5, 7, '-stand']) this.anims.create({ key: `gags-jog-spin${n}`, frames: gf(`jog-spin${n}`, 1), frameRate: 14 });
        this.anims.create({ key: 'gags-jog-shoved', frames: gf('jog-shoved', 1), frameRate: 14 });
        // (14a, 14b: stiff as a plank onto her back or her face, from her stand or a quarter of her run; then lying
        // there, the butterflies circling, at her dazed clips' pace.)
        for (const w of ['back', 'front']) {
            for (const n of [1, 3, 5, 7, '-stand']) this.anims.create({ key: `gags-ball-${w}${n}`, frames: gf(`ball-${w}${n}`, 1), frameRate: 14 });
            this.anims.create({ key: `gags-ball-${w}-lie`, frames: gf(`ball-${w}-lie`), frameRate: 6, repeat: -1 });
        }
        this.anims.create({ key: 'gags-gull-flail', frames: gf('gull-flail', 1), frameRate: 10 });
        this.anims.create({ key: 'gags-gull-run', frames: gf('gull-run', 1), frameRate: 12, repeat: -1 });
        // (16, a sprinkler: drenched where she stands, or stopping short from her run at its own 14 a
        // second; then a sneeze, and she squelches off.)
        this.anims.create({ key: 'gags-sprinkler-stand', frames: gf('sprinkler-stand', 1), frameRate: 10 });
        for (const n of [1, 3, 5, 7]) this.anims.create({ key: `gags-sprinkler-run${n}`, frames: gf(`sprinkler-run${n}`, 1, 9, i => (i < 3 ? 71 : 95)) });
        this.anims.create({ key: 'gags-sprinkler-sneeze', frames: gf('sprinkler-sneeze', 1), frameRate: 10 });
        this.anims.create({ key: 'gags-sprinkler-walk', frames: gf('sprinkler-walk', 1), frameRate: 8, repeat: -1 });
        // (17, the sauna's steam: her hair a huge puff, she fans herself, then swoons and sits.)
        this.anims.create({ key: 'gags-steam-fan', frames: gf('steam-fan', 1), frameRate: 10 });
        this.anims.create({ key: 'gags-steam-swoon', frames: gf('steam-swoon', 1), frameRate: 9 });
        this.anims.create({ key: 'gags-flare-blink', frames: gf('flare-blink', 1), frameRate: 8 });
        this.anims.create({ key: 'gags-flare-cough', frames: gf('flare-cough', 1), frameRate: 9 });
        // (23, a "Do Not Disturb" door opened on its guest: a startled hop, her hands over her eyes, blushing; then off
        // on tiptoe, two tiny steps a round, quick: the user, 2026-11-19, "make her move faster", and again: 26 ms a frame. Frame 0 of the cover
        // is her standing, shown already; of the tiptoe, the cover's last.)
        if (gg.anims['dnd-cover']) {
            this.anims.create({ key: 'gags-dnd-cover', frames: gf('dnd-cover', 1), frameRate: 1000 / 90 });
            this.anims.create({ key: 'gags-dnd-tiptoe', frames: gf('dnd-tiptoe', 1), frameRate: 1000 / 26, repeat: -1 });
        }
        // Bumbot, made again (plan-the-rest §7a, 2026-11-24; tools/build_sprites.py's `BUMBOT`): every clip from the one
        // picture the user chose. What he does at a spot loops with a pause between rounds; the run is his escape.
        const cat = this.cache.json.get('bumbot-meta');
        const catFrames = (name, order = cat.anims[name].map((_, i) => i)) =>
            order.map(i => ({ key: 'bumbot', frame: cat.anims[name][i] }));
        const span = (a, b) => Array.from({ length: b - a + 1 }, (_, i) => a + i);
        const clip = (key, name, fps, { order, repeat = 0, delay = 0 } = {}) =>
            this.anims.create({ key: `bumbot-${key}`, frames: catFrames(name, order), frameRate: fps, repeat, repeatDelay: delay });
        // On his feet.
        clip('idle', 'idle', 8, { repeat: -1, delay: 1600 });
        clip('walk', 'walk', 10, { repeat: -1 });
        clip('run', 'run', BUMBOT.runFps, { repeat: -1 });
        clip('look-back', 'look-back', 10);
        clip('turn', 'turn', 12);
        clip('stretch', 'stretch', 8);
        clip('shake', 'shake', 12);
        // (Eating: his head is down from the fourth frame on; the bites loop.)
        clip('eat', 'eat', 8, { order: span(3, 16), repeat: -1 });
        clip('crawl', 'crawl', 12, { order: span(7, 16), repeat: -1 });
        // His jump, three ways. `jump`: from the crouch to the crouch he lands in, each frame set on its own lowest
        // pixel (the pool's scene places him by his paws and paces it, at 12 a second: src/world/lido.js). `leap`: up and
        // through the air, held on its last frame, for a leap the game moves him through. `startle`: straight up on
        // the spot with the clip's own rise, to his front paws coming down (a near-catch: ShipScene's `nearCatch`).
        clip('jump', 'leap', 12, { order: span(1, 12) });
        clip('leap', 'leap', 22, { order: span(3, 9) });
        clip('startle', 'jump', BUMBOT.startleFps, { order: span(3, 10) });
        clip('land', 'jump', 16, { order: span(10, 16) });
        // Sitting.
        clip('sit', 'sit', 10);
        clip('sat', 'sat', 8, { repeat: -1, delay: 2200 });
        clip('stand-up', 'stand-up', 12);
        clip('wash', 'wash', 9, { repeat: -1, delay: 500 });
        clip('bat', 'bat', 11, { repeat: -1, delay: 350 });
        // (At the first pool's rim, a paw down at the water: its frames reach under his floor, `BUMBOT.under` px.)
        clip('fish', 'fish', 10, { repeat: -1, delay: 900 });
        // Lying.
        clip('loaf', 'loaf', 10);
        clip('loaf-rest', 'loaf-rest', 6, { repeat: -1, delay: 1800 });
        clip('loaf-up', 'loaf-up', 12);
        clip('lie-down', 'lie-down', 10);
        clip('asleep', 'asleep', 5, { repeat: -1 });
        clip('wake', 'wake', 12);
        // (On the stage's fly rope: the catch, then holding on. Its frames reach under his floor too.)
        clip('rope', 'rope', 14);
        // (The welcome screen and the intro are the ship scene's own: src/intro.js.)
        this.scene.start('ship');
    }
}
