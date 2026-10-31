import { VIEW, PLAYER, DASH, LONG_FALL_MARGIN } from '../config.js';
import { Controls } from '../controls.js';
import { sfx } from '../sfx.js';
import { loadSave, writeSave } from '../save.js';

// Tile ids from the tileset (see tools/build_slice_map.py).
const LADDER_TOP = 3;

const DEPTH = {
    sky: 0, sea: 1, back: 2, decor: 3, stairs: 4, playerBehind: 5,
    solid: 6, ladders: 7, props: 8, player: 9, fx: 10,
};

const approach = (value, target, step) =>
    value < target ? Math.min(value + step, target) : Math.max(value - step, target);

const HALF = PLAYER.height / 2;
const LAMP_RISE = 81; // the checkpoint lamp sits just above the 74px door

// Each hazard gets its own fright (§5.6).
const FRIGHTS = { vacuum: 'Іііі!' };

export class ShipScene extends Phaser.Scene {
    constructor() {
        super('ship');
    }

    create() {
        this.save = loadSave();
        this.controls = new Controls(this);
        this.worldLayer = this.add.layer();
        this.uiLayer = this.add.layer();

        this.buildMap();
        this.buildObjects();
        this.buildPlayer();
        this.buildCameras();
        this.buildHud();

        this.mode = 'play'; // play | ladder | stairs | scripted
        this.dashUntil = 0;
        this.bubbleUntil = 0;
        this.lastTrailAt = 0;
        this.jumpBufferedAt = -Infinity;
        this.script = null;

        this.spawnAt(this.initialSpawn());
        window.__ship = this; // handle for headless tests and the console
    }

    // --- Building --------------------------------------------------------------------------

    buildMap() {
        const map = this.make.tilemap({ key: 'ship' });
        this.map = map;
        const props = Array.isArray(map.properties)
            ? Object.fromEntries(map.properties.map(p => [p.name, p.value]))
            : map.properties || {};
        this.deckPitch = props.deckPitch;
        this.hullMinX = props.hullMinX;
        this.waterY = props.waterY;

        const W = map.widthInPixels;
        const H = map.heightInPixels;
        const tiles = map.addTilesetImage('placeholder', 'tiles');

        const sky = this.add.image(0, 0, 'sky').setOrigin(0).setDisplaySize(W, this.waterY).setDepth(DEPTH.sky);
        this.sea = this.add.tileSprite(0, this.waterY, W, H - this.waterY, 'sea').setOrigin(0).setDepth(DEPTH.sea);
        const back = map.createLayer('background', tiles).setDepth(DEPTH.back);
        this.solidLayer = map.createLayer('solid', tiles).setDepth(DEPTH.solid);
        this.ladderLayer = map.createLayer('ladders', tiles).setDepth(DEPTH.ladders);

        this.solidLayer.setCollisionByExclusion([-1]);
        // A ladder's top is a one-way floor: solid to stand on, open to climb through.
        this.solidLayer.forEachTile(t => {
            if (t.index === LADDER_TOP) t.setCollision(false, false, true, false);
        });

        this.worldLayer.add([sky, this.sea, back, this.solidLayer, this.ladderLayer]);
    }

    buildObjects() {
        const prop = (o, name, fallback) => (o.properties || []).find(p => p.name === name)?.value ?? fallback;
        this.checkpoints = [];
        this.tangerines = [];
        this.flights = [];
        this.vacuums = [];
        this.crates = this.physics.add.staticGroup();
        const stairsGfx = this.add.graphics().setDepth(DEPTH.stairs);
        const decorGfx = this.add.graphics().setDepth(DEPTH.decor);
        this.worldLayer.add([decorGfx, stairsGfx]);

        for (const o of this.map.getObjectLayer('objects').objects) {
            switch (o.type) {
                case 'spawn':
                    this.spawnPoint = { id: 'spawn', x: o.x, y: o.y };
                    break;

                case 'checkpoint': {
                    const door = this.add.image(o.x, o.y, 'door').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    const glow = this.add.image(o.x, o.y - LAMP_RISE, 'glow').setDepth(DEPTH.props).setVisible(false);
                    const lamp = this.add.image(o.x, o.y - LAMP_RISE, 'lamp').setDepth(DEPTH.props);
                    this.worldLayer.add([door, glow, lamp]);
                    const cp = { id: o.name, x: o.x, y: o.y, door, lamp, glow, active: false };
                    this.checkpoints.push(cp);
                    if (this.save.activated.includes(o.name)) this.lightCheckpoint(cp, false);
                    break;
                }

                case 'tangerine': {
                    if (this.save.collected.includes(o.name)) break;
                    // Everything rests on something (§6.3): here, a small side table.
                    const table = this.add.image(o.x, o.y, 'sidetable').setOrigin(0.5, 1).setDepth(DEPTH.decor);
                    const sprite = this.add.image(o.x, o.y - table.height, 'tangerine').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    const glint = this.add.image(sprite.x + 2, sprite.y - 6, 'dot').setDepth(DEPTH.props).setAlpha(0);
                    this.tweens.add({ targets: glint, alpha: 1, duration: 120, yoyo: true, repeat: -1, repeatDelay: 2400, delay: Phaser.Math.Between(0, 2000) });
                    this.worldLayer.add([table, sprite, glint]);
                    this.tangerines.push({ id: o.name, sprite, glint });
                    break;
                }

                case 'stairs': {
                    const [a, b] = o.polyline.map(p => ({ x: o.x + p.x, y: o.y + p.y }));
                    const [bottom, top] = a.y > b.y ? [a, b] : [b, a];
                    const flight = { name: o.name, bottom, top, length: Phaser.Math.Distance.BetweenPoints(bottom, top) };
                    this.flights.push(flight);
                    this.drawStairs(stairsGfx, flight);
                    break;
                }

                case 'breakable': {
                    if (this.save.broken.includes(o.name)) break;
                    const crate = this.crates.create(o.x + o.width / 2, o.y + o.height / 2, 'crate');
                    crate.setDepth(DEPTH.props);
                    crate.name = o.name;
                    this.worldLayer.add(crate);
                    break;
                }

                case 'vacuum': {
                    const sprite = this.add.image(o.x, o.y, 'vacuum').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    this.worldLayer.add(sprite);
                    this.vacuums.push({
                        sprite, alive: true, dir: 1,
                        minX: prop(o, 'minX', o.x - 80), maxX: prop(o, 'maxX', o.x + 80), speed: prop(o, 'speed', 40),
                    });
                    break;
                }

                case 'sign': {
                    const text = this.add.text(o.x, o.y, prop(o, 'text', ''), {
                        fontFamily: 'Verdana, sans-serif', fontSize: '7px', color: '#8f846f',
                        backgroundColor: '#f3ecdd', padding: { x: 3, y: 2 }, resolution: 4,
                    }).setOrigin(0.5).setDepth(DEPTH.decor);
                    this.worldLayer.add(text);
                    break;
                }

                case 'decor':
                    if (prop(o, 'kind') === 'shelldoor') this.drawShellDoor(decorGfx, o);
                    break;
            }
        }
    }

    // Stairs are in the background plane: she walks up them "behind" the floor slabs (§5.1).
    drawStairs(g, { bottom, top }) {
        const steps = Math.round((bottom.y - top.y) / 8);
        const dx = (top.x - bottom.x) / steps;
        const dy = (bottom.y - top.y) / steps;
        for (let i = 0; i < steps; i++) {
            const x = bottom.x + dx * i;
            const tread = bottom.y - dy * (i + 1);
            g.fillStyle(0xd6c9ae, 1);
            g.fillRect(Math.min(x, x + dx), tread, Math.abs(dx), bottom.y - tread);
            g.fillStyle(0xe8dcc4, 1);
            g.fillRect(Math.min(x, x + dx), tread, Math.abs(dx), 2);
        }
        g.lineStyle(1, 0xa89878, 1);
        g.lineBetween(bottom.x, bottom.y - 24, top.x, top.y - 24);
        g.lineBetween(bottom.x, bottom.y - 24, bottom.x, bottom.y);
        g.lineBetween(top.x, top.y - 24, top.x, top.y);
    }

    drawShellDoor(g, o) {
        g.fillStyle(0xd9cdb6, 1);
        g.fillRect(o.x, o.y, o.width, o.height);
        g.lineStyle(2, 0xb9ab90, 1);
        g.strokeRect(o.x + 2, o.y + 2, o.width - 4, o.height - 2);
        g.lineBetween(o.x + o.width / 2, o.y + 2, o.x + o.width / 2, o.y + o.height);
        g.fillStyle(0xa9c8d8, 1);
        g.fillCircle(o.x + o.width / 4, o.y + 16, 4);
        g.fillCircle(o.x + (o.width * 3) / 4, o.y + 16, 4);
    }

    buildPlayer() {
        this.herFrames = this.cache.json.get('her-meta').frames;
        const p = this.physics.add.sprite(0, 0, 'her', this.herFrames.stand).setOrigin(0.5, 1).setDepth(DEPTH.player);
        p.body.setSize(PLAYER.bodyWidth, PLAYER.bodyHeight);
        p.body.setOffset((PLAYER.cell - PLAYER.bodyWidth) / 2, PLAYER.cell - PLAYER.bodyHeight);
        p.body.setMaxVelocity(10000, PLAYER.maxFall);
        this.worldLayer.add(p);
        this.player = p;

        this.physics.add.collider(p, this.solidLayer);
        this.physics.add.collider(p, this.crates, null, (_, crate) => {
            if (!this.isDashing()) return true;
            this.smash(crate.x, crate.y);
            this.save.broken.push(crate.name);
            crate.disableBody(true, true);
            return false;
        });
    }

    buildCameras() {
        const cam = this.cameras.main;
        cam.setZoom(VIEW.zoom);
        cam.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels);
        cam.setDeadzone(40, 24);
        cam.ignore(this.uiLayer);

        // The HUD gets its own unzoomed camera, so its text stays crisp.
        this.uiCam = this.cameras.add(0, 0, VIEW.width, VIEW.height);
        this.uiCam.ignore(this.worldLayer);
    }

    buildHud() {
        const textStyle = {
            fontFamily: 'Verdana, sans-serif', fontSize: '24px', color: '#ffffff',
            stroke: '#1d2b53', strokeThickness: 5,
        };
        const icon = this.add.image(24, 20, 'tangerine').setOrigin(0).setScale(4);
        this.hudCount = this.add.text(62, 22, '', textStyle);
        this.dashBarBack = this.add.rectangle(24, 62, 164, 12, 0x1d2b53).setOrigin(0);
        this.dashBar = this.add.rectangle(26, 64, 160, 8, 0xf28c28).setOrigin(0);
        this.bubble = this.add.text(0, 0, DASH.shout, {
            fontFamily: 'Verdana, sans-serif', fontSize: '22px', fontStyle: 'bold', color: '#c8343f',
            backgroundColor: '#ffffff', padding: { x: 10, y: 6 },
        }).setOrigin(0.5, 1);
        this.alert = this.add.text(0, 0, '', {
            fontFamily: 'Verdana, sans-serif', fontSize: '22px', fontStyle: 'bold', color: '#1d2b53',
            backgroundColor: '#ffffff', padding: { x: 8, y: 4 },
        }).setOrigin(0.5, 1).setVisible(false);
        this.fade = this.add.rectangle(0, 0, VIEW.width, VIEW.height, 0x0d1422).setOrigin(0).setAlpha(0);
        this.debugText = this.add.text(VIEW.width - 12, 12, '', { fontFamily: 'monospace', fontSize: '14px', color: '#ffffff' })
            .setOrigin(1, 0).setVisible(new URLSearchParams(location.search).has('debug'));
        this.uiLayer.add([icon, this.hudCount, this.dashBarBack, this.dashBar, this.bubble, this.alert, this.fade, this.debugText]);
        this.refreshHud();
    }

    refreshHud() {
        this.hudCount.setText(`× ${this.save.tangerines}`);
        const left = Math.max(0, this.dashUntil - this.time.now);
        const dashing = left > 0;
        this.dashBarBack.setVisible(dashing);
        this.dashBar.setVisible(dashing).setSize(160 * (left / DASH.durationMs), 8);
    }

    // --- Spawning --------------------------------------------------------------------------

    initialSpawn() {
        return this.checkpoints.find(c => c.active && c.id === this.save.lastCheckpoint) || this.spawnPoint;
    }

    // She always comes back at the activated checkpoint closest to where she was: same deck
    // first, then the nearest deck, then the nearest along the deck (§5.5).
    closestCheckpoint(x, y) {
        let best = null;
        let bestScore = Infinity;
        for (const c of this.checkpoints) {
            if (!c.active) continue;
            const score = Math.round(Math.abs(c.y - y) / this.deckPitch) * 1e6 + Math.abs(c.x - x);
            if (score < bestScore) {
                best = c;
                bestScore = score;
            }
        }
        return best || this.spawnPoint;
    }

    spawnAt(point, { emerge = false } = {}) {
        const p = this.player;
        p.clearAlpha().setCrop().setDepth(DEPTH.player).setFlipX(false);
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(point.x, point.y);
        p.body.allowGravity = true;
        this.grounded = true;
        this.takeoffY = point.y;
        this.lastGroundedAt = this.time.now;
        this.alert.setVisible(false);

        const cam = this.cameras.main;
        cam.startFollow(p, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        cam.centerOn(p.x, p.y - HALF);

        if (!emerge) {
            this.mode = 'play';
            return;
        }
        // Stepping out of the crew cabin door.
        this.mode = 'scripted';
        sfx.door();
        p.setAlpha(0);
        if (point.door) {
            point.door.setAlpha(0.5);
            this.tweens.add({ targets: point.door, alpha: 1, duration: 400 });
        }
        this.tweens.add({ targets: p, alpha: 1, duration: 350, onComplete: () => { this.mode = 'play'; } });
    }

    // --- Main loop -------------------------------------------------------------------------

    update(time, delta) {
        const dt = Math.min(delta, 50) / 1000;
        const input = this.controls.update();
        this.sea.tilePositionX += dt * 12; // the ship is under way (§5.2)

        this.updateVacuums(dt);
        if (this.mode === 'play') this.updatePlay(input, dt, time);
        else if (this.mode === 'ladder') this.updateLadder(input, dt, time);
        else if (this.mode === 'stairs') this.updateStairs(input, dt, time);
        else if (this.script) this.script(dt, time);

        if (this.mode !== 'scripted') {
            this.checkPickups();
            this.checkCheckpoints();
            this.checkVacuums();
        }
        this.updateDash(time);
        this.updateOverlays();
    }

    updatePlay(input, dt, time) {
        const p = this.player;
        const body = p.body;
        const onFloor = body.blocked.down || body.touching.down;

        if (onFloor) {
            if (!this.grounded) sfx.land();
            this.grounded = true;
            this.lastGroundedAt = time;
            this.takeoffY = p.y;
        } else {
            this.grounded = false;
        }

        // Held, not just pressed, so holding ↓ carries her on down the next flight at a landing.
        if (onFloor && (input.up || input.down) && this.tryStairs(input)) return;
        if ((input.up || input.down) && this.tryLadder(input)) return;

        if (input.dashPressed) this.tryDash(time);

        const dashing = this.isDashing();
        const speed = PLAYER.runSpeed * (dashing ? DASH.speedMultiplier : 1);
        const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0);
        const accel = (onFloor ? (dir ? PLAYER.groundAccel : PLAYER.groundDecel) : PLAYER.airAccel) * (dashing ? 2 : 1);
        body.velocity.x = approach(body.velocity.x, dir * speed, accel * dt);
        if (dir) p.setFlipX(dir < 0);

        if (input.jumpPressed) this.jumpBufferedAt = time;
        const canJump = onFloor || time - this.lastGroundedAt < PLAYER.coyoteMs;
        if (canJump && time - this.jumpBufferedAt < PLAYER.jumpBufferMs) {
            body.velocity.y = -PLAYER.jumpVelocity;
            this.jumpBufferedAt = -Infinity;
            this.lastGroundedAt = -Infinity;
            sfx.jump();
        }
        if (input.jumpReleased && body.velocity.y < -PLAYER.jumpCutVelocity) {
            body.velocity.y = -PLAYER.jumpCutVelocity;
        }

        if (!onFloor) {
            if (p.x < this.hullMinX) {
                if (p.y >= this.waterY) return this.scareOverboard();
            } else if (p.y - this.takeoffY > this.deckPitch + LONG_FALL_MARGIN) {
                return this.scareFall();
            }
        }

        if (!onFloor) this.pose(body.velocity.y < -60 ? 'rise' : body.velocity.y < 60 ? 'apex' : 'fall');
        else if (Math.abs(body.velocity.x) > 10) this.pose('run', dashing ? 1.8 : Math.abs(body.velocity.x) / PLAYER.runSpeed);
        else this.pose('stand');
    }

    // --- Ladders ---------------------------------------------------------------------------

    ladderTileAt(x, y) {
        const t = this.ladderLayer.getTileAtWorldXY(x, y);
        return t && t.index > 0 ? t : null;
    }

    tryLadder(input) {
        const p = this.player;
        const tile = input.up ? this.ladderTileAt(p.x, p.y - HALF) : this.ladderTileAt(p.x, p.y + 2);
        if (!tile) return false;

        let top = tile.y;
        let bottom = tile.y;
        while (this.ladderLayer.getTileAt(tile.x, top - 1)?.index > 0) top--;
        while (this.ladderLayer.getTileAt(tile.x, bottom + 1)?.index > 0) bottom++;
        this.ladder = {
            x: tile.pixelX + tile.width / 2,
            topY: top * tile.height,
            bottomY: (bottom + 1) * tile.height,
        };

        this.mode = 'ladder';
        p.body.enable = false;
        p.x = this.ladder.x;
        p.setFlipX(false);
        this.pose('climb');
        this.ladderPose = 'climb';
        return true;
    }

    updateLadder(input, dt, time) {
        const p = this.player;
        const L = this.ladder;
        const v = (input.down ? 1 : 0) - (input.up ? 1 : 0);
        p.y = Phaser.Math.Clamp(p.y + v * PLAYER.climbSpeed * dt, L.topY, L.bottomY);

        // Her hands reach to about head height. Once that is above the last rung there is nothing
        // to grab, so her hands come down: climbing out of the hatch, or starting down into it.
        const handsAboveLadder = p.y - PLAYER.height * 0.85 < L.topY;
        if (handsAboveLadder) {
            if (this.ladderPose !== 'back') this.pose('back');
            this.ladderPose = 'back';
        } else {
            if (this.ladderPose !== 'climb') this.pose('climb');
            this.ladderPose = 'climb';
            if (v) p.anims.resume();
            else p.anims.pause();
        }

        const atTop = p.y <= L.topY;
        const atBottom = p.y >= L.bottomY;
        if (input.jumpPressed) {
            this.leaveLadderOrStairs();
            p.body.velocity.y = -PLAYER.jumpVelocity * 0.6;
            sfx.jump();
        } else if ((atTop && input.up) || (atBottom && input.down) || ((atTop || atBottom) && (input.left || input.right))) {
            this.leaveLadderOrStairs();
        }
    }

    leaveLadderOrStairs() {
        const p = this.player;
        this.mode = 'play';
        p.setDepth(DEPTH.player);
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(p.x, p.y);
        this.takeoffY = p.y;
    }

    // --- Stairs ----------------------------------------------------------------------------

    tryStairs(input) {
        const p = this.player;
        const reach = PLAYER.stairsBoardReach;
        for (const f of this.flights) {
            if (input.up && Math.abs(p.x - f.bottom.x) < reach && Math.abs(p.y - f.bottom.y) < 4) return this.enterStairs(f, 0);
            if (input.down && Math.abs(p.x - f.top.x) < reach && Math.abs(p.y - f.top.y) < 4) return this.enterStairs(f, 1);
        }
        return false;
    }

    enterStairs(flight, t) {
        this.mode = 'stairs';
        this.flight = flight;
        this.stairT = t;
        this.player.body.enable = false;
        this.player.setDepth(DEPTH.playerBehind);
        this.placeOnStairs();
        return true;
    }

    placeOnStairs() {
        const { bottom, top } = this.flight;
        this.player.x = Phaser.Math.Linear(bottom.x, top.x, this.stairT);
        this.player.y = Phaser.Math.Linear(bottom.y, top.y, this.stairT);
    }

    updateStairs(input, dt, time) {
        const p = this.player;
        const f = this.flight;
        const upward = Math.sign(f.top.x - f.bottom.x); // which horizontal direction climbs
        let v = 0;
        if (input.up || (upward > 0 ? input.right : input.left)) v = 1;
        else if (input.down || (upward > 0 ? input.left : input.right)) v = -1;

        this.stairT = Phaser.Math.Clamp(this.stairT + (v * PLAYER.stairsSpeed * dt) / f.length, 0, 1);
        this.placeOnStairs();
        if (v) {
            p.setFlipX(v * upward < 0);
            this.pose('run', 0.8);
        } else {
            this.pose('stand');
        }

        if ((this.stairT >= 1 && v > 0) || (this.stairT <= 0 && v < 0)) this.leaveLadderOrStairs();
    }

    // Her pose: a looping animation (run, climb) at an optional speed, or a single frame.
    pose(name, speed = 1) {
        const p = this.player;
        const key = `her-${name}`;
        if (this.anims.exists(key)) {
            p.anims.play(key, true);
            p.anims.timeScale = speed;
        } else {
            p.anims.stop();
            p.setFrame(this.herFrames[name]);
        }
    }

    // --- Pickups, checkpoints, hazards ---------------------------------------------------------

    checkPickups() {
        const p = this.player;
        for (const t of this.tangerines) {
            if (!t.sprite.active) continue;
            if (Math.abs(p.x - t.sprite.x) < 12 && t.sprite.y > p.y - PLAYER.height && t.sprite.y - 8 < p.y) {
                this.save.tangerines += 1;
                this.save.collected.push(t.id);
                sfx.pickup();
                t.glint.destroy();
                this.tweens.add({ targets: t.sprite, y: t.sprite.y - 12, alpha: 0, duration: 250, onComplete: () => t.sprite.destroy() });
                t.sprite.active = false;
                this.refreshHud();
            }
        }
    }

    checkCheckpoints() {
        const p = this.player;
        for (const c of this.checkpoints) {
            if (Math.abs(p.x - c.x) > 8 || Math.abs(p.y - c.y) > 6) continue;
            if (!c.active) {
                this.lightCheckpoint(c, true);
                this.save.activated.push(c.id);
            }
            if (this.save.lastCheckpoint !== c.id || !c.saved) {
                this.save.lastCheckpoint = c.id;
                writeSave(this.save);
                this.checkpoints.forEach(o => { o.saved = o === c; });
            }
        }
    }

    // An active checkpoint has to read from across the deck: the door stands ajar with the cabin
    // light on, and a green lamp above it glows.
    lightCheckpoint(c, celebrate) {
        c.active = true;
        c.door.setTexture('door-on');
        c.lamp.setTexture('lamp-on');
        c.glow.setVisible(true).setAlpha(0.55);
        this.tweens.add({ targets: c.glow, alpha: 0.25, scale: 0.8, duration: 1100, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        if (!celebrate) return;
        sfx.checkpoint();
        this.tweens.add({ targets: c.lamp, scale: 1.8, duration: 160, yoyo: true, ease: 'Quad.easeOut' });
        for (let i = 0; i < 14; i++) {
            const angle = (Math.PI * 2 * i) / 14;
            const spark = this.add.image(c.x, c.y - LAMP_RISE, 'dot').setTint(0x7dffa0).setDepth(DEPTH.fx);
            this.worldLayer.add(spark);
            this.tweens.add({
                targets: spark, x: c.x + Math.cos(angle) * 22, y: c.y - LAMP_RISE + Math.sin(angle) * 22, alpha: 0,
                duration: 500, ease: 'Quad.easeOut', onComplete: () => spark.destroy(),
            });
        }
    }

    updateVacuums(dt) {
        for (const v of this.vacuums) {
            if (!v.alive) continue;
            v.sprite.x += v.dir * v.speed * dt;
            if (v.sprite.x > v.maxX) v.dir = -1;
            else if (v.sprite.x < v.minX) v.dir = 1;
            v.sprite.setFlipX(v.dir < 0);
        }
    }

    checkVacuums() {
        const p = this.player;
        for (const v of this.vacuums) {
            if (!v.alive) continue;
            const s = v.sprite;
            const hit = Math.abs(p.x - s.x) < (PLAYER.bodyWidth / 2 + 6) && p.y > s.y - 6 && p.y - PLAYER.bodyHeight < s.y;
            if (!hit) continue;
            if (this.isDashing()) {
                v.alive = false;
                this.smash(s.x, s.y - 3);
                s.destroy();
            } else {
                this.scareContact(s.x, 'vacuum');
                return;
            }
        }
    }

    smash(x, y) {
        sfx.smash();
        for (let i = 0; i < 10; i++) {
            const b = this.add.image(x, y, 'dot').setDepth(DEPTH.fx).setTint(0xc9a26a);
            this.worldLayer.add(b);
            this.tweens.add({
                targets: b,
                x: x + Phaser.Math.Between(-24, 24),
                y: y + Phaser.Math.Between(-20, 8),
                alpha: 0,
                duration: Phaser.Math.Between(250, 450),
                onComplete: () => b.destroy(),
            });
        }
    }

    // --- The dash --------------------------------------------------------------------------

    isDashing() {
        return this.dashUntil > this.time.now;
    }

    tryDash(time) {
        if (this.isDashing() || this.save.tangerines <= 0) return;
        this.save.tangerines -= 1;
        this.dashUntil = time + DASH.durationMs;
        this.bubbleUntil = time + DASH.bubbleMs;
        sfx.dash();
        this.refreshHud();
    }

    updateDash(time) {
        const dashing = this.isDashing();
        if (this.wasDashing && !dashing) sfx.dashEnd();
        this.wasDashing = dashing;
        if (dashing || this.dashBar.visible) this.refreshHud();

        if (dashing && this.mode === 'play' && time - this.lastTrailAt > 45 && Math.abs(this.player.body.velocity.x) > 10) {
            this.lastTrailAt = time;
            const p = this.player;
            const ghost = this.add.image(p.x, p.y, 'her', p.frame.name).setOrigin(0.5, 1)
                .setFlipX(p.flipX).setAlpha(0.45).setDepth(DEPTH.player - 0.5);
            this.worldLayer.add(ghost);
            this.tweens.add({ targets: ghost, alpha: 0, duration: 260, onComplete: () => ghost.destroy() });
        }
    }

    // --- Scares (never death, §5.6) ------------------------------------------------------------

    beginScare() {
        this.mode = 'scripted';
        this.dashUntil = 0;
        this.bubbleUntil = 0;
        this.player.body.enable = false;
        this.cameras.main.stopFollow();
    }

    // A fright that fits what got her, then she runs off the screen.
    scareContact(fromX, kind) {
        const p = this.player;
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        const away = p.x >= fromX ? 1 : -1;
        sfx.scare();
        this.alert.setText(FRIGHTS[kind] || '!').setVisible(true);
        this.pose('rise');
        p.setFlipX(away < 0);
        this.script = null;
        this.tweens.add({
            targets: p, y: p.y - 14, duration: 170, yoyo: true, ease: 'Quad.easeOut',
            onComplete: () => {
                sfx.whoosh();
                this.script = (dt, time) => {
                    p.x += away * 260 * dt;
                    this.pose('run', 2);
                    const view = this.cameras.main.worldView;
                    if (p.x < view.x - 20 || p.x > view.right + 20) this.respawn();
                };
            },
        });
    }

    // Longer than one deck: the camera lets go and she drops out of the bottom of the screen.
    scareFall() {
        const p = this.player;
        let vy = p.body.velocity.y;
        this.beginScare();
        this.scareFrom = { x: p.x, y: this.takeoffY };
        p.setDepth(DEPTH.fx);
        this.pose('fall');
        sfx.whoosh();
        this.script = (dt) => {
            vy = Math.min(vy + PLAYER.gravity * dt, PLAYER.maxFall * 1.5);
            p.y += vy * dt;
            if (p.y - 40 > this.cameras.main.worldView.bottom) this.respawn();
        };
    }

    // Overboard: no drowning. A splash, then she bobs up smiling in a life ring, waving.
    scareOverboard() {
        const p = this.player;
        this.beginScare();
        this.scareFrom = { x: this.hullMinX + 16, y: this.takeoffY };
        this.cameras.main.startFollow(p, true, 0.15, 0.15);
        sfx.splash();
        this.smash(p.x, this.waterY);
        // Facing the camera, smiling; only her top half shows above the water.
        const shown = PLAYER.cell - PLAYER.height + 32;
        this.pose('front');
        p.setCrop(0, 0, PLAYER.cell, shown).setDepth(DEPTH.fx);
        p.y = this.waterY + PLAYER.cell - shown; // the crop's bottom edge sits on the water
        const ring = this.add.image(p.x, this.waterY - 3, 'lifering').setDepth(DEPTH.fx + 0.5);
        const wave = this.add.text(p.x + 14, this.waterY - 40, '👋', { fontSize: '12px', resolution: 4 }).setOrigin(0.5).setDepth(DEPTH.fx + 1);
        this.worldLayer.add([ring, wave]);
        this.tweens.add({ targets: [p, ring, wave], y: '-=2', duration: 300, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        this.tweens.add({ targets: wave, angle: { from: -20, to: 20 }, duration: 180, yoyo: true, repeat: -1 });
        this.script = null;
        this.time.delayedCall(1300, () => {
            this.respawn(() => {
                this.tweens.killTweensOf([p, ring, wave]);
                ring.destroy();
                wave.destroy();
            });
        });
    }

    respawn(cleanup) {
        if (this.respawning) return;
        this.respawning = true;
        this.script = null;
        const from = this.scareFrom || { x: this.player.x, y: this.player.y };
        const target = this.closestCheckpoint(from.x, from.y);
        this.tweens.add({
            targets: this.fade, alpha: 1, duration: 220,
            onComplete: () => {
                cleanup?.();
                this.tweens.killTweensOf(this.player);
                this.spawnAt(target, { emerge: true });
                this.tweens.add({ targets: this.fade, alpha: 0, duration: 260 });
                this.respawning = false;
            },
        });
    }

    // --- Screen-space overlays ------------------------------------------------------------------

    updateOverlays() {
        const cam = this.cameras.main;
        const p = this.player;
        const sx = (p.x - cam.worldView.x) * cam.zoom;
        const sy = (p.y - PLAYER.height - 6 - cam.worldView.y) * cam.zoom;
        this.bubble.setVisible(this.time.now < this.bubbleUntil).setPosition(sx, sy);
        this.alert.setPosition(sx, sy);
        if (this.debugText.visible) {
            this.debugText.setText(`${this.mode}  x ${p.x.toFixed(0)}  y ${p.y.toFixed(0)}  takeoff ${this.takeoffY?.toFixed(0)}`);
        }
    }
}
