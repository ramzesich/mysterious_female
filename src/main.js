import { VIEW, PLAYER } from './config.js';
import { BootScene } from './scenes/BootScene.js';
import { ShipScene } from './scenes/ShipScene.js';
import * as lang from './lang.js';

const params = new URLSearchParams(location.search);
window.__lang = lang;       // for the playtests (tools/playtest.py, `lang`)

window.__game = new Phaser.Game({
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
    scene: [BootScene, ShipScene],
});
