import { VIEW, PLAYER } from './config.js';
import { BootScene } from './scenes/BootScene.js';
import { TitleScene } from './scenes/TitleScene.js';
import { ShipScene } from './scenes/ShipScene.js';

const params = new URLSearchParams(location.search);

new Phaser.Game({
    type: Phaser.AUTO,
    parent: 'game',
    width: VIEW.width,
    height: VIEW.height,
    backgroundColor: '#0d1422',
    pixelArt: true,
    roundPixels: true,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    input: { gamepad: true },
    physics: {
        default: 'arcade',
        arcade: { gravity: { y: PLAYER.gravity }, debug: params.has('debug') },
    },
    scene: [BootScene, TitleScene, ShipScene],
});
