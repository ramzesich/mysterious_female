import { VIEW } from '../config.js';
import { Controls } from '../controls.js';
import { sfx } from '../sfx.js';

// "Bumbusik" and Start, nothing else (§7.1). The goal is never stated anywhere (§1).
export class TitleScene extends Phaser.Scene {
    constructor() {
        super('title');
    }

    create() {
        const { width, height } = VIEW;
        this.add.image(0, 0, 'sky').setOrigin(0).setDisplaySize(width, height * 0.62);
        this.sea = this.add.tileSprite(0, height * 0.62, width / 2, height * 0.38 / 2, 'sea')
            .setOrigin(0).setScale(2);

        this.add.text(width / 2, height * 0.3, 'Bumbusik', {
            fontFamily: 'Georgia, serif', fontSize: '84px', color: '#ffffff',
            stroke: '#1d2b53', strokeThickness: 8,
        }).setOrigin(0.5);

        const start = this.add.text(width / 2, height * 0.56, 'Start', {
            fontFamily: 'Georgia, serif', fontSize: '36px', color: '#1d2b53',
            backgroundColor: '#ffffff', padding: { x: 28, y: 10 },
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        start.on('pointerdown', () => this.begin());
        this.tweens.add({ targets: start, scale: 1.06, duration: 700, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

        this.controls = new Controls(this);
        this.started = false;
    }

    begin() {
        if (this.started) return;
        this.started = true;
        sfx.unlock();
        sfx.checkpoint();
        this.scene.start('ship');
    }

    update(time, delta) {
        this.sea.tilePositionX += delta * 0.01;
        if (this.controls.update().startPressed) this.begin();
    }
}
