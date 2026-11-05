#!/usr/bin/env node
/*
 * Plays projects/arthurs-arena-legends.sb3 inside Scratch's own engine
 * (scratch-vm), with no screen, using a simple bot that taps the buttons.
 *
 * Setup once:   npm install --prefix /tmp/scratch-tools scratch-vm
 * Run:          NODE_PATH=/tmp/scratch-tools/node_modules node tools/test_legends.js
 *
 * Time is faked, so a 3-minute story run takes a few seconds.
 */
'use strict';

let fakeNow = 1700000000000;
Date.now = () => fakeNow;

// Scratch's "say for N seconds" uses setTimeout, so timers follow the fake clock too.
const realSetTimeout = setTimeout;
let timers = [];
let fakeTimers = false;
global.setTimeout = (fn, ms, ...args) => {
    if (!fakeTimers) return realSetTimeout(fn, ms, ...args);
    const t = {at: fakeNow + (ms || 0), fn: () => fn(...args), id: Symbol('t')};
    timers.push(t);
    return t;
};
const realClearTimeout = clearTimeout;
global.clearTimeout = t => {
    if (t && t.id) timers = timers.filter(x => x !== t);
    else realClearTimeout(t);
};
const runTimers = () => {
    const due = timers.filter(t => t.at <= fakeNow);
    timers = timers.filter(t => t.at > fakeNow);
    due.forEach(t => t.fn());
};
const settle = () => new Promise(r => setImmediate(r));

const fs = require('fs');
const path = require('path');
const VirtualMachine = require('scratch-vm');
try {
    require('minilog').disable();
} catch (e) { /* older vm */ }

const SB3 = path.join(__dirname, '..', 'projects', 'arthurs-arena-legends.sb3');
const FRAME = 1000 / 30;

const problems = [];
const fail = msg => problems.push(msg);

async function boot (skipIntro = true) {
    const vm = new VirtualMachine();
    const errors = [];
    const origError = console.error;
    console.error = (...a) => errors.push(a.join(' '));
    console.warn = () => {};
    console.log = (...a) => {
        const text = a.join(' ');
        if (!/^(Loading|Done)/.test(text)) process.stdout.write(text + '\n');
    };
    await vm.loadProject(fs.readFileSync(SB3));
    console.error = origError;
    // One pass over all scripts per frame, like Scratch with a screen.
    // (With no renderer nothing asks for a redraw, and a frozen fake clock
    // would otherwise keep the engine looping inside a single frame.)
    let passes = 0;
    Object.defineProperty(vm.runtime, 'redrawRequested', {
        get: () => passes++ > 0,
        set: v => {
            if (!v) passes = 0;
        }
    });
    vm.runtime.currentStepTime = FRAME;
    fakeTimers = true;
    timers = [];
    vm.greenFlag();
    if (skipIntro) {
        // tests start at the title: tap through the paper intro
        for (let i = 0; i < 3; i++) {
            fakeNow += FRAME;
            runTimers();
            await settle();
            vm.runtime._step();
        }
        vm.runtime.startHats('event_whenbroadcastreceived', {BROADCAST_OPTION: 'skip intro'});
    }
    return {vm, errors};
}

function tools (vm) {
    const rt = vm.runtime;
    const stage = rt.getTargetForStage();
    const byName = {};
    for (const v of Object.values(stage.variables)) byName[v.name] = v;
    const sprite = name => rt.getSpriteTargetByName(name);
    // Scratch keeps "1" and 1 alike; compare like Scratch does.
    const get = name => {
        const v = byName[name].value;
        return typeof v === 'string' && v.trim() !== '' && !isNaN(Number(v)) ? Number(v) : v;
    };
    const set = (name, value) => {
        byName[name].value = value;
    };
    const click = name => rt.startHats('event_whenthisspriteclicked', null, sprite(name));
    const send = msg => rt.startHats('event_whenbroadcastreceived', {BROADCAST_OPTION: msg});
    const step = async (n = 1) => {
        for (let i = 0; i < n; i++) {
            fakeNow += FRAME;
            runTimers();
            await settle();
            rt._step();
        }
    };
    const costume = name => {
        const t = sprite(name);
        return t.getCostumes()[t.currentCostume].name;
    };
    const clones = name => rt.targets.filter(t => !t.isOriginal && t.sprite.name === name);
    return {rt, stage, sprite, get, set, click, send, step, costume, clones};
}

// A bot that plays fair: it only uses what a player could see and the buttons.
function makeBot (T, hero) {
    const stats = {punches: 0, kicks: 0, jumps: 0, dodges: 0, supers: 0, weapons: new Set(), perfect: 0,
        combos: 0, breaks: 0, fireballs: 0, ouches: 0, rainDodges: 0, powerMoves: 0, retries: 0, chapters: new Set(), waves: 0, popups: new Set()};
    let frame = 0;
    let lastMove = 0;
    let picked = false;
    let charging = 0;
    const tick = () => {
        frame++;
        const state = T.get('State');
        if (state === 'select') {
            if (!picked) T.click(['Pick Arthur', 'Pick Nova', 'Pick Rocko'][hero - 1]);
            picked = true;
            return;
        }
        picked = false;
        if (state !== 'fight' || T.get('Fight On') !== 1) return;
        const hx = T.get('Hero X');
        const ex = T.get('Enemy X');
        const d = Math.abs(ex - hx);
        const toward = ex > hx ? 'move right' : 'move left';
        const away = ex > hx ? 'move left' : 'move right';
        const enemyPose = T.costume('Enemy');
        const shot = T.sprite('Enemy Shot');
        const wave = T.sprite('Ground Wave');
        const drop = T.sprite('Weapon Drop');

        if (T.get('Power Level') > 1 && d < 200 && frame % 45 === 0 && T.get('Hero Lock') === 0) {
            T.set('Want Power', 1);
            stats.powerMoves++;
        }
        if (T.get('Super') === 100 && T.get('Hero Air') === 0 && T.get('Hero Lock') === 0) {
            T.set('Want Super', 1);
            stats.supers++;
            return;
        }
        if (shot.visible) {
            const sd = Math.abs(shot.x - hx);
            const low = T.get('Shot Y') < -40;
            if (low && sd < 75 && sd > 30 && T.get('Hero Air') === 0) {
                T.set('Want Jump', 1);
                stats.jumps++;
                return;
            }
        }
        if (wave.visible) {
            const wd = Math.abs(wave.x - hx);
            if (wd < 95 && wd > 40 && T.get('Hero Air') === 0) {
                T.set('Want Jump', 1);
                stats.jumps++;
                return;
            }
        }
        const name = T.get('Enemy Name');
        // fireballs: hold FIRE for a while, then let go
        if (charging > 0) {
            charging--;
            if (charging === 0) T.set('Fire Held', 0);
            return;
        }
        // ninja minions close by: turn and hit them
        const ninjas = T.clones('Ninja Minion').filter(c => c.visible);
        const near = ninjas.find(c => Math.abs(c.x - hx) < 55);
        if (near && frame % 5 === 0) {
            T.send(near.x > hx ? 'move right' : 'move left');
            T.set(frame % 15 ? 'Want Punch' : 'Want Kick', 1);
            stats.ninjaHits = (stats.ninjaHits || 0) + 1;
            return;
        }
        // Spike Rain: step away from a red mark under the hero
        const marks = T.clones('Spike Rain').filter(c => c.visible && c.getCostumes()[c.currentCostume].name === 'warning');
        const danger = marks.find(c => Math.abs(c.x - hx) < 34);
        if (danger) {
            if (frame - lastMove > 2) {
                T.send(danger.x > hx || hx > 190 ? 'move left' : 'move right');
                lastMove = frame;
            }
            stats.rainDodges++;
            return;
        }
        if ((name === 'spikebot' || name === 'megaspike' || name === 'shadow') && T.get('Spikes') === 1) {
            // never punch the spikes: jump over the roll, or charge a fireball from afar
            if (d < 95 && T.get('Hero Air') === 0) {
                T.set('Want Jump', 1);
                stats.jumps++;
            } else if (d >= 95 && T.get('Fireball Out') === 0) {
                T.set('Fire Held', 1);
                charging = 32;
                stats.fireballs++;
            }
            return;
        }
        if (d > 160 && T.get('Fireball Out') === 0 && frame % 40 === 0) {
            T.set('Fire Held', 1);
            charging = frame % 80 === 0 ? 32 : 2; // sometimes a full charge, sometimes a quick tap
            stats.fireballs++;
            return;
        }
        if (/windup$/.test(enemyPose) && (name === 'brute' || name === 'shadow')) {
            // Brute and the King wind up before a charge: dodge late for a perfect dodge
            if (frame % 9 === 0 && T.get('Hero Lock') === 0) {
                T.set('Want Dodge', 1);
                stats.dodges++;
            }
            return;
        }
        if (drop.visible && T.get('Weapon') === 'none' && drop.y < -40) {
            if (Math.abs(drop.x - hx) > 20 && frame - lastMove > 4) {
                T.send(drop.x > hx ? 'move right' : 'move left');
                lastMove = frame;
            }
            return;
        }
        const reach = 70 + T.get('Weapon Reach') + T.get('Enemy Body');
        if (T.get('Weapon') === 'boomerang' && T.get('Boomerang Out') === 0 && d < 200) {
            T.set('Want Punch', 1);
            stats.punches++;
            return;
        }
        if (d > reach - 10) {
            if (frame - lastMove > 3) {
                T.send(toward);
                lastMove = frame;
            }
        } else if (frame % 5 === 0) {
            if (frame % 15 === 0) {
                T.set('Want Kick', 1);
                stats.kicks++;
            } else {
                T.set('Want Punch', 1);
                stats.punches++;
            }
        }
        if (name === 'ivy' && d < 40 && frame % 30 === 0) T.send(away);
    };
    return {tick, stats};
}

function watch (T, stats, label) {
    // things that must never get stuck
    let lockFrames = 0;
    let boomFrames = 0;
    let lastPop = null;
    return () => {
        lockFrames = T.get('Hero Lock') === 1 ? lockFrames + 1 : 0;
        boomFrames = T.get('Boomerang Out') === 1 ? boomFrames + 1 : 0;
        if (lockFrames === 120) fail(`${label}: Hero Lock stuck on for 4 seconds`);
        if (boomFrames === 150) fail(`${label}: boomerang never came back`);
        const hp = T.get('Hero HP');
        if (hp < 0 || hp > T.get('Hero Max')) fail(`${label}: Hero HP out of range ${hp}`);
        if (T.get('Super') > 100) fail(`${label}: Super over 100`);
        const pop = T.get('Pop Text');
        if (pop !== lastPop) {
            lastPop = pop;
            if (/^COMBO/.test(pop)) stats.combos++;
            if (/PERFECT/.test(pop)) stats.perfect++;
            if (/broke/.test(pop)) stats.breaks++;
            if (/SPIKES/.test(pop)) stats.ouches++;
            stats.popups.add(pop.replace(/x\d+/, 'xN'));
        }
        if (T.get('Weapon') !== 'none') stats.weapons.add(T.get('Weapon'));
    };
}

async function storyRun (hero) {
    const {vm, errors} = await boot();
    const T = tools(vm);
    await T.step(10);
    if (T.get('State') !== 'title') fail('green flag did not reach the title');
    if (!T.sprite('Story Button').visible) fail('Story button hidden on the title');
    T.click('Story Button');
    await T.step(3);
    if (T.get('State') !== 'select') fail('Story button did not open fighter select');
    const bot = makeBot(T, hero);
    const check = watch(T, bot.stats, `story hero ${hero}`);
    let frames = 0;
    let lastChapter = 0;
    while (frames < 30 * 60 * 12) {
        await T.step();
        frames++;
        bot.tick();
        check();
        const state = T.get('State');
        if (T.get('Chapter') !== lastChapter) {
            lastChapter = T.get('Chapter');
            bot.stats.chapters.add(lastChapter);
        }
        if (state === 'story' && T.sprite('Skip Button').visible && frames % 200 === 0 && hero === 2) {
            T.click('Skip Button'); // Nova's run also checks the skip button
        }
        if (state === 'over' && T.sprite('Retry Button').visible) {
            bot.stats.retries++;
            T.click('Retry Button');
        }
        if (state === 'ending' && T.sprite('Home Button').visible) break;
    }
    const minutes = (frames / 30 / 60).toFixed(1);
    if (T.get('State') !== 'ending') fail(`story hero ${hero}: did not reach the ending in ${minutes} min (chapter ${T.get('Chapter')})`);
    if (T.get('Crown') !== 1) fail(`story hero ${hero}: crown not unlocked`);
    if (T.get('Power Level') < 3) fail(`story hero ${hero}: power level only ${T.get('Power Level')} after the story (XP ${T.get('Power XP')})`);
    if (T.get('Best') < T.get('Score')) fail('Best not updated after story');
    // Home goes back to the title, and the crown stays
    T.click('Home Button');
    await T.step(10);
    if (T.get('State') !== 'title') fail('Home did not go to the title');
    if (errors.length) fail(`story hero ${hero}: engine errors: ${errors.slice(0, 3).join(' | ')}`);
    return {minutes, stats: bot.stats, score: T.get('Score'), powerLevel: T.get('Power Level'), xp: T.get('Power XP')};
}

async function arcadeRun (hero) {
    const {vm, errors} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Arcade Button');
    await T.step(3);
    const bot = makeBot(T, hero);
    const check = watch(T, bot.stats, `arcade hero ${hero}`);
    let frames = 0;
    let bestWave = 0;
    let deaths = 0;
    const kinds = new Set();
    while (frames < 30 * 60 * 6 && deaths < 2) {
        await T.step();
        frames++;
        bot.tick();
        check();
        bestWave = Math.max(bestWave, T.get('Wave'));
        if (T.get('State') === 'fight') kinds.add(T.get('Enemy Type'));
        if (T.get('State') === 'over' && T.sprite('Retry Button').visible) {
            deaths++;
            const before = T.get('Score');
            T.click('Retry Button');
            await T.step(2);
            if (T.get('Wave') !== 1) fail('arcade retry did not restart at wave 1');
            if (T.get('Best') < before) fail('arcade Best lower than the last score');
        }
    }
    if (bestWave < 3) fail(`arcade hero ${hero}: only reached wave ${bestWave}`);
    if (errors.length) fail(`arcade: engine errors: ${errors.slice(0, 3).join(' | ')}`);
    return {bestWave, deaths, kinds: [...kinds].sort(), stats: bot.stats, best: T.get('Best')};
}

async function mashTest () {
    // Tap everything every frame, the way a kid on a tablet might.
    const {vm} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Story Button');
    await T.step(3);
    T.click('Pick Rocko');
    await T.step(5);
    T.click('Skip Button');
    let frames = 0;
    while (T.get('Fight On') !== 1 && frames < 30 * 20) {
        await T.step();
        frames++;
    }
    if (T.get('Fight On') !== 1) return fail('mash: fight never started after Skip');
    // The Android joystick sets Joy X; Hero walks while it is held
    T.set('Hero Safe Until', 1e12);
    T.sprite('Hero').setXY(-100, -75);
    T.set('Joy X', 1);
    await T.step(15);
    const walked = T.sprite('Hero').x;
    T.set('Joy X', 0);
    await T.step(5);
    if (walked < -60) fail(`joystick: Hero did not walk right (x=${walked})`);
    if (Math.abs(T.sprite('Hero').x - walked) > 1) fail('joystick: Hero kept walking after release');
    for (let i = 0; i < 30 * 8; i++) {
        for (const want of ['Want Punch', 'Want Kick', 'Want Jump', 'Want Dodge', 'Want Super']) T.set(want, 1);
        if (i % 2) T.send('move right');
        T.click('Punch Button');
        await T.step();
    }
    T.set('Enemy HP', 999); // keep the fight going
    for (const want of ['Want Punch', 'Want Kick', 'Want Jump', 'Want Dodge', 'Want Super']) T.set(want, 0);
    await T.step(60);
    if (T.get('Hero Lock') !== 0) fail('mash: Hero Lock stuck after button mashing');
    if (T.get('Hero Air') !== 0) fail('mash: Hero Air stuck after button mashing');
    if (Math.abs(T.sprite('Hero').y - -75) > 0.5) fail(`mash: Hero is floating at y=${T.sprite('Hero').y}`);
    const hx = T.sprite('Hero').x;
    if (hx < -216 || hx > 216) fail(`mash: Hero left the stage x=${hx}`);
    // Quit goes home in the middle of a fight
    T.click('Quit Button');
    await T.step(10);
    if (T.get('State') !== 'title' || T.get('Fight On') !== 0) fail('mash: Quit did not return to the title');
    if (T.sprite('Enemy').visible) fail('mash: enemy still visible on the title');
}

async function weaponTest () {
    // Force each weapon and check it hits and breaks.
    const {vm} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Arcade Button');
    await T.step(3);
    T.click('Pick Arthur');
    let frames = 0;
    while (T.get('Fight On') !== 1 && frames < 300) {
        await T.step();
        frames++;
    }
    // no falling weapons or apples in this test: they could be picked up and swap the weapon under test
    for (const name of ['Weapon Drop', 'Apple']) {
        vm.runtime.stopForTarget(T.sprite(name));
        T.sprite(name).setVisible(false);
    }
    const weapons = {sword: [4, 28, 10], hammer: [9, 12, 5], boomerang: [0, 0, 6]};
    for (const [name, [bonus, reach, uses]] of Object.entries(weapons)) {
        T.set('Enemy HP', 999);
        T.set('Enemy Max', 999);
        T.set('Weapon', name);
        T.set('Weapon Bonus', bonus);
        T.set('Weapon Reach', reach);
        T.set('Weapon Uses', uses);
        for (let i = 0; i < uses + 3 && T.get('Fight On') === 1; i++) {
            // stand next to the enemy (boomerang from range)
            const gap = name === 'boomerang' ? 150 : 60;
            const ex = T.get('Enemy X');
            T.sprite('Hero').setXY(ex > 0 ? ex - gap : ex + gap, -75);
            T.set('Hero Safe Until', 1e12); // no damage during this test
            await T.step(2); // let Hero turn to face the enemy
            const hp = T.get('Enemy HP');
            T.set('Want Punch', 1);
            await T.step(name === 'boomerang' ? 40 : 14);
            if (T.get('Weapon') !== name && i < uses - 1) fail(`weapon ${name}: was swapped for ${T.get('Weapon')}`);
            if (i < uses && T.get('Enemy HP') >= hp) {
                fail(`weapon ${name}: swing ${i + 1} did not hit (hero ${T.get('Hero X')}, enemy ${T.get('Enemy X')}, ` +
                    `out ${T.get('Boomerang Out')}, uses ${T.get('Weapon Uses')}, lock ${T.get('Hero Lock')}, want ${T.get('Want Punch')})`);
            }
        }
        await T.step(10);
        if (T.get('Weapon') !== 'none') {
            fail(`weapon ${name}: did not break after ${uses} uses (weapon ${T.get('Weapon')}, uses left ${T.get('Weapon Uses')}, ` +
                 `lock ${T.get('Hero Lock')}, fight ${T.get('Fight On')}, boom out ${T.get('Boomerang Out')})`);
        }
        if (!T.sprite('Held Weapon').visible === false && T.get('Weapon') === 'none') fail('held weapon still shown');
    }
}

async function startArcadeAt (wave, hero = 'Pick Arthur') {
    const {vm} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Arcade Button');
    await T.step(3);
    T.click(hero);
    await T.step(2);
    T.set('Wave', wave);
    T.send('start fight');
    let frames = 0;
    while (T.get('Fight On') !== 1 && frames < 300) {
        await T.step();
        frames++;
    }
    return T;
}

async function fireTest () {
    const T = await startArcadeAt(1);
    if (T.get('Fight On') !== 1) return fail('fire: fight did not start');
    T.set('Enemy HP', 999);
    T.set('Enemy Max', 999);
    T.set('Hero Safe Until', 1e12);
    const shoot = async holdFrames => {
        T.sprite('Hero').setXY(T.get('Enemy X') > 0 ? T.get('Enemy X') - 170 : T.get('Enemy X') + 170, -75);
        await T.step(2);
        const hp = T.get('Enemy HP');
        T.set('Fire Held', 1);
        let maxCharge = 0;
        for (let i = 0; i < holdFrames; i++) {
            await T.step();
            maxCharge = Math.max(maxCharge, T.get('Charge'));
        }
        T.set('Fire Held', 0);
        let frames = 0;
        await T.step(2);
        while (T.get('Fireball Out') === 1 && frames < 90) {
            await T.step();
            frames++;
            if (process.env.DEBUG_FIRE) process.stdout.write(`f${frames} charge ${T.get('Charge')} out ${T.get('Fireball Out')} lock ${T.get('Hero Lock')} fight ${T.get('Fight On')} costume ${T.costume('Hero')}\n`);
        }
        await T.step(3);
        return {damage: hp - T.get('Enemy HP'), maxCharge, power: T.get('Fire Power'), out: T.get('Fireball Out')};
    };
    const tap = await shoot(1);
    const full = await shoot(45);
    if (tap.damage < 3 || tap.damage > 5) fail(`fire: tap fireball did ${tap.damage} damage (power ${tap.power})`);
    if (full.maxCharge !== 100) fail(`fire: holding never reached full charge (${full.maxCharge})`);
    if (full.damage < 14) fail(`fire: full fireball only did ${full.damage} damage`);
    if (full.out !== 0 || T.get('Charge') !== 0) {
        fail(`fire: fireball or charge stuck after shooting (out ${full.out}, charge ${T.get('Charge')}, held ${T.get('Fire Held')})`);
    }
    return {tap: tap.damage, full: full.damage};
}

async function powerUpTest () {
    // Dragon Ball style power-up before a fight; golden hair from level 3, silver at 5
    const out = {};
    for (const level of [1, 3, 5]) {
        const {vm} = await boot();
        const T = tools(vm);
        await T.step(5);
        T.set('Power Level', level);
        T.click('Arcade Button');
        await T.step(3);
        T.click('Pick Rocko');
        let rocks = 0, powering = false, yelled = false, frames = 0;
        while (T.get('Fight On') !== 1 && frames < 30 * 10) {
            await T.step();
            frames++;
            rocks = Math.max(rocks, T.clones('Debris').length);
            if (T.get('Powering') === 1) powering = true;
            if (((T.sprite('Hero').getCustomState('Scratch.looks') || {}).text || '').startsWith('HAAA')) yelled = true;
        }
        const look = T.get('Hero Look');
        if (process.env.DEBUG_PU) process.stdout.write(`name ${T.get('Hero Name')} hero ${T.get('Hero')} look ${look} costume ${T.costume('Hero')} state ${T.get('State')}\n`);
        out[level] = {look, rocks, powering, yelled, seconds: +(frames / 30).toFixed(1)};
        if (!powering || !yelled || rocks < 5) fail(`powerup: level ${level} show missing (powering ${powering}, yell ${yelled}, rocks ${rocks})`);
        const want = level >= 5 ? 'rocko silver' : level >= 3 ? 'rocko gold' : 'rocko';
        if (look !== want) fail(`powerup: level ${level} look is ${look}, expected ${want}`);
        if (!T.costume('Hero').startsWith(want + ' ')) fail(`powerup: hero costume ${T.costume('Hero')}`);
        if (T.get('Hero Lock') !== 0) fail('powerup: hero still locked after powering up');
        // walking still uses the golden costumes
        T.set('Joy X', 1);
        await T.step(8);
        T.set('Joy X', 0);
        if (!T.costume('Hero').startsWith(want + ' ')) fail(`powerup: walking lost the look (${T.costume('Hero')})`);
    }
    return out;
}

async function flipTest () {
    // tap JUMP once: a jump; tap again in the air: a higher second jump with a front flip
    const T = await startArcadeAt(1);
    if (T.get('Fight On') !== 1) return fail('flip: fight did not start');
    T.set('Enemy Stun Until', 1e12);
    T.set('Hero Safe Until', 1e12);
    const jump = async twice => {
        let top = -999, flips = new Set(), frames = 0;
        T.set('Want Jump', 1);
        await T.step(6);
        if (twice) T.set('Want Jump', 1);
        do {
            await T.step();
            frames++;
            top = Math.max(top, T.sprite('Hero').y);
            const c = T.costume('Hero');
            if (c.includes(' flip ')) flips.add(c.split(' flip ')[1]);
        } while (T.get('Hero Air') === 1 && frames < 120);
        return {top: Math.round(top + 75), flips: [...flips].sort(), frames, landed: T.get('Hero Air') === 0 && T.sprite('Hero').y === -75};
    };
    const once = await jump(false);
    await T.step(10);
    const twice = await jump(true);
    if (!once.landed || !twice.landed) fail('flip: the hero did not land back on the ground');
    if (once.flips.length) fail('flip: a single jump flipped');
    if (twice.flips.length < 4) fail(`flip: the second jump only showed flip frames ${twice.flips}`);
    if (twice.top <= once.top + 20) fail(`flip: the second jump was not higher (${once.top} vs ${twice.top})`);
    // a third tap in the air does nothing
    T.set('Want Jump', 1); await T.step(6); T.set('Want Jump', 1); await T.step(4); T.set('Want Jump', 1);
    let frames = 0;
    while (T.get('Hero Air') === 1 && frames < 150) { await T.step(); frames++; }
    if (T.get('Hero Air') !== 0) fail('flip: a third tap kept the hero in the air');
    return {once, twice};
}

async function adventureTest () {
    const {vm} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Adventure Button');
    await T.step(3);
    T.click('Pick Arthur');
    const out = {stages: []};
    const expect = [['grunt', 'brute'], ['ninja', 'kage'], ['robot', 'megaspike']];
    for (let st = 0; st < expect.length; st++) {
        let frames = 0;
        while (T.get('Fight On') !== 1 && frames < 30 * 12) { await T.step(); frames++; }
        if (T.get('Wave Phase') !== 1) return fail(`adventure: stage ${st + 1} did not start with waves`);
        if (T.sprite('Enemy').visible) fail(`adventure: the boss showed during the waves of stage ${st + 1}`);
        T.set('Hero Safe Until', 1e12);
        const kinds = new Set();
        let waves = 0;
        frames = 0;
        // beat every small enemy that shows up
        while (T.get('Wave Phase') === 1 && frames < 30 * 90) {
            await T.step();
            frames++;
            waves = Math.max(waves, T.get('Wave Num'));
            for (const c of T.clones('Ninja Minion')) {
                kinds.add(c.getCostumes()[c.currentCostume].name.split(' ')[0]);
                if (frames % 10 === 0) {
                    T.set('Area X', c.x); T.set('Area R', 20); T.set('Area Power', 6); T.set('Area Kind', 'hit');
                    T.send('area hit');
                }
            }
            if (T.clones('Ninja Minion').length > 3) fail('adventure: more than 3 small enemies at once');
        }
        if (T.get('Wave Phase') !== 0) return fail(`adventure: stage ${st + 1} waves never ended (wave ${T.get('Wave Num')}, beaten ${T.get('Beaten')}/${T.get('Wave Total')})`);
        frames = 0;
        while (!T.sprite('Enemy').visible && frames < 120) { await T.step(); frames++; }
        await T.step(40);
        const boss = T.get('Enemy Name');
        if (!kinds.has(expect[st][0]) || [...kinds].some(k => k !== expect[st][0])) fail(`adventure: stage ${st + 1} small enemies were ${[...kinds]}`);
        if (boss !== expect[st][1]) fail(`adventure: stage ${st + 1} boss is ${boss}`);
        if (!T.sprite('Enemy').visible) fail(`adventure: stage ${st + 1} boss never appeared`);
        out.stages.push({kinds: [...kinds], waves, boss});
        // beat the boss, with some damage taken: health carries over (+30)
        T.set('Hero HP', 40);
        T.set('Enemy HP', 1);
        T.set('Enemy Stun Until', 0);
        T.set('Hit Power', 5);
        T.send('hero hits');
        frames = 0;
        while (T.get('Adv Stage') === st + 1 && frames < 30 * 8) { await T.step(); frames++; }
        if (T.get('Adv Stage') !== st + 2) return fail(`adventure: did not move on after stage ${st + 1}`);
        if (T.get('Hero HP') !== 70) fail(`adventure: health after stage ${st + 1} is ${T.get('Hero HP')}, expected 70`);
    }
    // quitting resets the waves so Story still works
    T.click('Quit Button');
    await T.step(10);
    if (T.get('Wave Phase') !== 0) fail('adventure: Quit left the waves on');
    return out;
}

async function adventureBotRun () {
    // the bot plays ADVENTURE with the buttons only
    const {vm, errors} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Adventure Button');
    await T.step(3);
    const bot = makeBot(T, 1);
    let frames = 0, deaths = 0;
    while (T.get('Adv Stage') < 4 && frames < 30 * 60 * 10) {
        await T.step();
        frames++;
        bot.tick();
        if (T.get('State') === 'over' && T.sprite('Retry Button').visible) {
            deaths++;
            T.click('Retry Button');
        }
    }
    if (T.get('Adv Stage') < 4) fail(`adventure bot: only reached stage ${T.get('Adv Stage')} in 10 minutes (${deaths} retries)`);
    if (errors.length) fail(`adventure bot: engine errors ${errors.slice(0, 2)}`);
    return {minutes: +(frames / 1800).toFixed(1), retries: deaths, ninjaHits: bot.stats.ninjaHits || 0};
}

async function whirlTest () {
    // tap KICK twice quickly: WHIRLWIND KICK (spins, up to 3 hits, both sides, then a short cooldown)
    const T = await startArcadeAt(1);
    if (T.get('Fight On') !== 1) return fail('whirl: fight did not start');
    T.set('Enemy HP', 999); T.set('Enemy Max', 999); T.set('Hero Safe Until', 1e12); T.set('Enemy Stun Until', 0);
    const ex = T.get('Enemy X');
    T.sprite('Hero').setXY(ex > 0 ? ex - 70 : ex + 70, -75);
    await T.step(3);
    const hp = T.get('Enemy HP');
    T.set('Want Kick', 1);
    await T.step(4);
    T.set('Want Kick', 1);
    const spins = new Set();
    let top = -999;
    for (let i = 0; i < 40; i++) {
        await T.step();
        const c = T.costume('Hero');
        if (c.includes(' spin ')) spins.add(c.split(' spin ')[1]);
        top = Math.max(top, T.sprite('Hero').y);
    }
    const dealt = hp - T.get('Enemy HP');
    if (spins.size < 4) fail(`whirl: only spin frames ${[...spins]}`);
    if (top < -70) fail('whirl: the hero did not lift off');
    if (dealt < 4 + 2 * 4) fail(`whirl: kick + whirlwind only did ${dealt}`);
    if (T.get('Hero Lock') !== 0 || T.sprite('Hero').y !== -75) fail('whirl: hero not back on the ground and free');
    // a single tap is still a normal kick
    await T.step(60);
    T.set('Want Kick', 1);
    let single = false;
    for (let i = 0; i < 25; i++) { await T.step(); if (T.costume('Hero').includes(' spin ')) single = true; }
    if (single) fail('whirl: a single tap spun');
    return {spinFrames: [...spins].sort(), dealt, liftedTo: Math.round(top + 75)};
}

async function introTest () {
    const {vm} = await boot(false);
    const T = tools(vm);
    await T.step(5);
    if (T.get('State') !== 'intro') return fail(`intro: green flag went to ${T.get('State')}, not the intro`);
    if (T.sprite('Hero').visible || T.sprite('Story Button').visible) fail('intro: title things showed during the intro');
    const pen = new Set();
    let frames = 0;
    while (T.get('State') === 'intro' && frames < 30 * 15) {
        await T.step();
        frames++;
        if (T.sprite('Pencil').visible) pen.add(`${Math.round(T.sprite('Pencil').x)},${Math.round(T.sprite('Pencil').y)}`);
    }
    if (T.get('State') !== 'title') fail('intro: never reached the title');
    if (pen.size < 40) fail(`intro: the pencil only visited ${pen.size} spots (4 fighters, ninja included)`);
    if (T.sprite('Sketch').visible) fail('intro: the drawing stayed on the title screen');
    // the SKIP button works
    const viaButton = await boot(false);
    const T3 = tools(viaButton.vm);
    await T3.step(10);
    if (!T3.sprite('Skip Intro').visible) fail('intro: no SKIP button');
    T3.click('Skip Intro');
    await T3.step(5);
    if (T3.get('State') !== 'title' || T3.sprite('Skip Intro').visible) fail('intro: SKIP did not go to the title');
    // and tapping anywhere works
    const again = await boot(false);
    const T2 = tools(again.vm);
    await T2.step(15);
    T2.rt.startHats('event_whenstageclicked');
    await T2.step(5);
    if (T2.get('State') !== 'title' || T2.sprite('Sketch').visible) fail('intro: tapping did not skip to the title');
    return {seconds: +(frames / 30).toFixed(1), pencilSpots: pen.size};
}

async function grokTest () {
    // Grok's ideas: practice fight, healing apple, sound on/off, how to play, debug overlay
    const {vm} = await boot();
    const T = tools(vm);
    await T.step(10);
    T.click('Help Button');
    await T.step(3);
    if (!T.sprite('Help Card').visible) fail('grok: ? did not show the how-to-play card');
    T.click('Help Card');
    await T.step(2);
    if (T.sprite('Help Card').visible) fail('grok: tapping the card did not close it');
    T.click('Sound Button');
    await T.step(3);
    if (T.get('Sound On') !== 0 || vm.runtime.getTargetForStage().volume !== 0) fail('grok: sound did not turn off');
    T.click('Sound Button');
    await T.step(3);
    if (vm.runtime.getTargetForStage().volume !== 100) fail('grok: sound did not turn back on');
    T.click('Version');
    await T.step(2);
    if (T.get('Debug') !== 1) fail('grok: tapping the version did not open the debug overlay');
    T.click('Version');
    await T.step(2);
    T.click('Practice Button');
    await T.step(3);
    T.click('Pick Nova');
    let frames = 0;
    while (T.get('Fight On') !== 1 && frames < 300) {
        await T.step();
        frames++;
    }
    if (T.get('Mode') !== 'practice' || T.get('Fight On') !== 1) return fail('grok: practice did not start');
    for (let i = 0; i < 30 * 8; i++) await T.step();
    if (T.get('Hero HP') !== T.get('Hero Max')) fail('grok: the practice dummy hit back');
    T.set('Enemy HP', 2);
    T.set('Hit Power', 5);
    T.set('Enemy Stun Until', 0);
    T.send('hero hits');
    await T.step(5);
    if (T.get('Fight On') !== 1 || T.get('Enemy HP') !== T.get('Enemy Max')) fail('grok: the practice dummy did not fill back up');
    // the apple: arcade, hurt, wait for it, walk over it
    T.click('Quit Button');
    await T.step(5);
    T.click('Arcade Button');
    await T.step(3);
    T.click('Pick Arthur');
    frames = 0;
    while (T.get('Fight On') !== 1 && frames < 300) {
        await T.step();
        frames++;
    }
    T.set('Enemy Stun Until', 1e12);
    T.set('Hero HP', 40);
    T.set('Hero Safe Until', 1e12);
    const apple = T.sprite('Apple');
    frames = 0;
    while (!(apple.visible && apple.y < -40) && frames < 30 * 25) {
        await T.step();
        frames++;
    }
    if (!apple.visible) return fail('grok: no apple fell when hurt');
    T.sprite('Hero').setXY(apple.x, -75);
    await T.step(6);
    if (T.get('Hero HP') !== 65) fail(`grok: the apple healed to ${T.get('Hero HP')}, expected 65`);
    return {appleAfterSeconds: Math.round(frames / 30)};
}

async function ninjaTest () {
    const T = await startArcadeAt(7); // wave 7 is MASTER KAGE
    if (T.get('Enemy Name') !== 'kage') return fail(`ninja: wave 7 is ${T.get('Enemy Name')}`);
    const out = {shuriken: false, smoke: false, teleport: false};
    T.set('Enemy HP', 999);
    T.set('Enemy Max', 999);
    // watch the boss for a while
    for (let i = 0; i < 30 * 25 && !(out.shuriken && out.smoke && out.teleport); i++) {
        await T.step();
        T.set('Hero HP', 100);
        if (T.sprite('Enemy Shot').visible && T.costume('Enemy Shot') === 'shuriken') out.shuriken = true;
        if (T.clones('Smoke').length) out.smoke = true;
        if (T.sprite('Enemy').effects.ghost === 100) out.teleport = true;
        if (T.clones('Ninja Minion').length > 3) fail('ninja: more than 3 minions');
    }
    if (!out.shuriken) fail('ninja: MASTER KAGE never threw a shuriken');
    if (!out.smoke || !out.teleport) fail('ninja: MASTER KAGE never vanished in smoke');
    // a full squad, then try for more: still only 3
    T.set('Enemy Stun Until', 1e12);
    T.set('Summon Count', 3);
    T.send('ninja summon');
    await T.step(40);
    T.send('ninja summon');
    await T.step(40);
    const squad = T.clones('Ninja Minion').length;
    if (squad !== 3 || T.get('Minions') !== 3) fail(`ninja: squad is ${squad} clones, Minions ${T.get('Minions')}`);
    // beat one ninja with punches
    T.set('Hero Safe Until', 1e12);
    const target = T.clones('Ninja Minion')[0];
    let punches = 0;
    while (T.clones('Ninja Minion').includes(target) && punches < 20) {
        const side = target.x > T.get('Hero X') ? 1 : -1;
        T.sprite('Hero').setXY(target.x - 30 * side, -75);
        T.set('Turn Dir', side);
        T.set('Turn Until', 1e12);
        await T.step(2);
        T.set('Want Punch', 1);
        await T.step(12);
        punches++;
    }
    T.set('Turn Until', 0);
    if (T.clones('Ninja Minion').includes(target)) fail('ninja: 20 punches did not beat a ninja');
    await T.step(20);
    out.punchesToBeat = punches;
    if (T.get('Minions') !== T.clones('Ninja Minion').length) fail(`ninja: Minions ${T.get('Minions')} but ${T.clones('Ninja Minion').length} clones`);
    // lightning hits ninjas too
    const n2 = T.clones('Ninja Minion')[0];
    if (n2) {
        const hp = n2.lookupVariableByNameAndType('HP').value;
        T.set('Bolt X', n2.x); T.set('Bolt Y', -75); T.set('Bolt Owner', 'hero'); T.set('Bolt Power', 4); T.set('Bolt Size', 100);
        T.send('bolt');
        await T.step(6);
        if (T.clones('Ninja Minion').includes(n2) && n2.lookupVariableByNameAndType('HP').value >= hp) fail('ninja: lightning missed a ninja under it');
    }
    // the fight ends: every ninja leaves
    T.set('Enemy HP', 1);
    T.set('Enemy Stun Until', 0);
    T.set('Hit Power', 5);
    T.send('hero hits');
    await T.step(30);
    if (T.clones('Ninja Minion').length || T.get('Minions') !== 0) fail('ninja: minions stayed after the boss was beaten');
    return out;
}

async function powerTest () {
    const T = await startArcadeAt(1);
    if (T.get('Fight On') !== 1) return fail('power: fight did not start');
    const out = {};
    // level 1: POWER is locked
    T.set('Want Power', 1);
    await T.step(5);
    if (T.get('Power Ready At') !== 0) fail('power: POWER worked at level 1');
    for (let level = 2; level <= 5; level++) {
        T.set('Power Level', level);
        T.set('Enemy HP', 999);
        T.set('Enemy Max', 999);
        T.set('Hero Safe Until', 1e12);
        T.set('Power Ready At', 0);
        T.set('Enemy Stun Until', 0);
        T.sprite('Hero').setXY(T.get('Enemy X') > 0 ? T.get('Enemy X') - 120 : T.get('Enemy X') + 120, -75);
        await T.step(3);
        let bolts = 0;
        T.set('Want Power', 1);
        for (let i = 0; i < 75; i++) {
            await T.step();
            bolts = Math.max(bolts, T.clones('Lightning').length);
        }
        const dealt = 999 - T.get('Enemy HP');
        const aura = T.costume('Power Aura');
        out[level] = {dealt, bolts, aura};
        if (dealt < 8) fail(`power: level ${level} POWER move only did ${dealt}`);
        if (level >= 3 && bolts < 1) fail(`power: level ${level} made no lightning`);
        if (!aura.startsWith(`lv${level} `)) fail(`power: level ${level} aura is ${aura}`);
        if (T.get('Hero Lock') !== 0) fail(`power: Hero stuck after level ${level} POWER move`);
        await T.step(10);
        T.set('Want Power', 1); // cooling down: nothing happens
        const before = T.get('Enemy HP');
        await T.step(20);
        if (T.get('Enemy HP') < before - 8) fail(`power: level ${level} POWER worked again during the cooldown`);
    }
    // a boss bolt: hurts if you stand under it, not if you move away
    T.set('Enemy Stun Until', 1e12); // hold the Rival still so only the bolt can hurt
    T.sprite('Hero').setXY(T.get('Enemy X') > 0 ? T.get('Enemy X') - 200 : T.get('Enemy X') + 200, -75);
    await T.step(3);
    T.set('Hero Safe Until', 0);
    T.set('Hero HP', 100);
    T.set('Bolt X', T.get('Hero X')); T.set('Bolt Y', -75); T.set('Bolt Owner', 'enemy'); T.set('Bolt Power', 10); T.set('Bolt Size', 100);
    T.send('bolt');
    await T.step(30);
    if (T.get('Hero HP') >= 100) fail('power: standing under an enemy bolt did not hurt');
    T.set('Hero HP', 100);
    await T.step(25);
    T.set('Hero Safe Until', 0);
    T.set('Bolt X', T.get('Hero X') + 120);
    T.send('bolt');
    await T.step(30);
    if (T.get('Hero HP') < 100) fail('power: an enemy bolt far away still hurt');
    // XP: 3 XP reaches level 2, 18 reaches level 5
    T.set('Power Level', 1); T.set('Power XP', 0); T.set('XP Gain', 3);
    T.send('gain xp');
    await T.step(2);
    if (T.get('Power Level') !== 2) fail(`power: 3 XP gave level ${T.get('Power Level')}`);
    T.set('XP Gain', 15);
    T.send('gain xp');
    await T.step(2);
    if (T.get('Power Level') !== 5) fail(`power: 18 XP gave level ${T.get('Power Level')}`);
    return out;
}

async function bossTest () {
    const T = await startArcadeAt(5); // wave 5 is the MEGA SPIKE boss
    if (T.get('Enemy Name') !== 'megaspike') return fail(`boss: wave 5 is ${T.get('Enemy Name')}, not MEGA SPIKE`);
    T.set('Enemy HP', 999);
    T.set('Enemy Max', 999);
    const seen = {rain: false, spikeShot: false, roll: false};
    const heroStart = T.get('Hero HP');
    for (let i = 0; i < 30 * 40 && !(seen.rain && seen.spikeShot && seen.roll); i++) {
        await T.step();
        T.set('Hero HP', 100); // keep the hero alive; we only watch the attacks
        T.set('Hero Max', 100);
        const bubble = (T.sprite('Enemy').getCustomState('Scratch.looks') || {}).text || '';
        if (bubble === 'SPIKE ROLL!') seen.roll = true;
        const shot = T.sprite('Enemy Shot');
        if (shot.visible && T.costume('Enemy Shot') === 'spike') seen.spikeShot = true;
        if (T.clones('Spike Rain').length) {
            seen.rain = true;
            T.set('Hero Safe Until', 0);
        }
    }
    if (!seen.rain) fail('boss: MEGA SPIKE never used Spike Rain');
    if (!seen.spikeShot) fail('boss: MEGA SPIKE never shot spikes');
    if (!seen.roll) fail('boss: MEGA SPIKE never did a Spike Roll');
    // Spike Rain hurts a hero who stands still under it
    T.set('Hero HP', 100);
    T.set('Hero Safe Until', 0);
    T.set('Hero Safe', 0);
    T.send('spike rain');
    await T.step(50);
    if (T.get('Hero HP') >= 100) fail('boss: standing under Spike Rain did not hurt');
    // two Spike Rains close together: clones must not make more clones
    await T.step(60);
    T.send('spike rain');
    await T.step(5);
    T.send('spike rain');
    await T.step(5);
    const spikes = T.clones('Spike Rain').length;
    // 2 rains = 10 spikes, plus maybe one MEGA SPIKE casts itself; clones copying clones would make 30+
    if (spikes > 15) fail(`boss: two Spike Rains made ${spikes} spikes (clones copying clones)`);
    // half health starts OVERDRIVE
    T.set('Enemy Max', 80);
    T.set('Enemy HP', 41);
    T.set('Hit Power', 2);
    T.set('Enemy Stun Until', 0);
    T.send('hero hits');
    await T.step(3);
    if (T.get('Enemy Phase') !== 2) fail('boss: OVERDRIVE did not start at half health');
    return {attacks: Object.keys(seen).filter(k => seen[k]), heroStart};
}

async function spikeTest () {
    const T = await startArcadeAt(4); // wave 4 is Spike Bot
    if (T.get('Enemy Name') !== 'spikebot') return fail(`spikes: wave 4 is ${T.get('Enemy Name')}, not Spike Bot`);
    // wait for the spikes to come out
    let frames = 0;
    while (T.get('Spikes') !== 1 && frames < 200) {
        await T.step();
        frames++;
    }
    if (T.get('Spikes') !== 1) return fail('spikes: Spike Bot never put its spikes out');
    T.set('Enemy HP', 999);
    T.set('Enemy Speed', 0); // hold it still: in punch reach, but not touching
    T.sprite('Hero').setXY(T.get('Enemy X') > 0 ? T.get('Enemy X') - 70 : T.get('Enemy X') + 70, -75);
    await T.step(2);
    T.set('Hero Safe Until', 0);
    const heroHp = T.get('Hero HP');
    T.set('Want Punch', 1);
    await T.step(4);
    const hurt = heroHp - T.get('Hero HP');
    if (T.get('Enemy HP') !== 999) fail('spikes: a bare-handed punch got through the spikes');
    if (hurt < 5) fail(`spikes: punching spikes did not hurt Hero (lost ${hurt})`);
    // let it cool down, then punching works again
    frames = 0;
    while (T.get('Spikes') !== 0 && frames < 200) {
        await T.step();
        frames++;
    }
    T.set('Hero Safe Until', 1e12);
    T.sprite('Hero').setXY(T.get('Enemy X') > 0 ? T.get('Enemy X') - 50 : T.get('Enemy X') + 50, -75);
    await T.step(2);
    T.set('Want Punch', 1);
    await T.step(6);
    if (T.get('Enemy HP') >= 999) fail('spikes: punching a cooled-down Spike Bot did nothing');
    return {spikeDamageToHero: hurt};
}

async function brawlTest () {
    const {vm, errors} = await boot();
    const T = tools(vm);
    const list = name => vm.runtime.getTargetForStage().lookupVariableByNameAndType(name, 'list').value.map(Number);
    await T.step(10);
    T.click('Brawl Button');
    await T.step(3);
    if (T.get('State') !== 'select') return fail('brawl: BRAWL did not open fighter select');
    T.set('Power Level', 4);
    const STAGES = 10;
    T.set('Stage Pick', 1);
    T.click('Pick Rocko');
    const out = {stages: [], matches: 0, wins: 0, kos: 0, maxDmg: 0, zoom: [9, 0], landed: false, rampOk: false};
    out.cannon = false;
    out.bounce = false;
    for (let match = 0; match < STAGES; match++) {
        let frames = 0;
        let checked = false;
        while (T.get('Brawl On') !== 1 && frames < 300) {
            await T.step();
            frames++;
            if (!checked && T.get('Banner') === 'fight') {
                // FIGHT! is showing: everyone has dropped onto a platform or ramp
                checked = true;
                const X = list('B X'), Y = list('B Y');
                const x1 = list('Plat X1'), y1 = list('Plat Y1'), x2 = list('Plat X2'), y2 = list('Plat Y2');
                const onSome = (x, y) => x1.some((_, k) => x >= x1[k] && x <= x2[k] &&
                    Math.abs(y - (y1[k] + (x - x1[k]) * (y2[k] - y1[k]) / (x2[k] - x1[k]))) < 1.5);
                if (!X.every((x, k) => onSome(x, Y[k]))) fail(`brawl: someone is not standing on the stage at FIGHT!: ${JSON.stringify([X, Y])}`);
                out.landed = true;
                if (T.get('Brawl Stage') !== 1) out.rampOk = out.rampOk || X.some((x, k) => onSome(x, Y[k]) && x1.some((_, j) => y1[j] !== y2[j] && x >= x1[j] && x <= x2[j]));
            }
        }
        if (T.get('Brawl On') !== 1) return fail('brawl: match never started');
        out.stages.push(T.get('Brawl Stage'));
        if (T.clones('Brawler').length !== 4) fail(`brawl: ${T.clones('Brawler').length} fighters, expected 4`);
        if (T.clones('Brawl Platform').length !== T.get('Plat Count')) fail('brawl: platform clones do not match the stage');
        if (T.sprite('Punch Button').visible && T.get('Touch Pad') === 0) { /* computer buttons may show */ }
        let lastStocks = list('B Stock').reduce((a, b) => a + b, 0);
        frames = 0;
        while (T.get('State') === 'brawl' && frames < 30 * 60 * 4) {
            await T.step();
            frames++;
            // a simple player: walk to the nearest fighter and attack; jump when they are higher
            const X = list('B X'), Y = list('B Y'), alive = list('B Alive'), dmg = list('B Dmg');
            let best = -1, bd = 1e9;
            for (let j = 1; j < 4; j++) {
                if (alive[j] !== 1) continue;
                const d = Math.abs(X[j] - X[0]) + Math.abs(Y[j] - Y[0]);
                if (d < bd) { bd = d; best = j; }
            }
            T.set('Joy X', 0);
            if (best >= 0 && alive[0] === 1) {
                const dx = X[best] - X[0], dy = Y[best] - Y[0];
                if (Math.abs(X[0]) > 280) T.set('Joy X', X[0] > 0 ? -1 : 1); // stay on the stage
                else if (Math.abs(dx) > 40) T.set('Joy X', dx > 0 ? 1 : -1);
                if ((dy > 50 || Y[0] < -140) && frames % 12 === 0) T.set('Want Jump', 1);
                if (dy < -60 && frames % 30 === 0) T.set('Want Drop', 1);
                if (Math.abs(dx) < 50 && Math.abs(dy) < 45 && frames % 6 === 0) T.set(frames % 18 ? 'Want Punch' : 'Want Kick', 1);
                if (T.get('Super') === 100 && Math.abs(dx) < 60) T.set('Want Super', 1);
                if (Math.abs(dx) < 120 && frames % 60 === 0) T.set('Want Power', 1);
                out.bolts = Math.max(out.bolts || 0, T.clones('Lightning').length);
            }
            out.maxDmg = Math.max(out.maxDmg, ...dmg);
            const z = T.get('Zoom');
            out.zoom = [Math.min(out.zoom[0], z), Math.max(out.zoom[1], z)];
            const stocks = list('B Stock').reduce((a, b) => a + b, 0);
            if (stocks < lastStocks) out.kos += lastStocks - stocks;
            lastStocks = stocks;
            if (process.env.DEBUG_BRAWL && frames % 300 === 0) {
                process.stdout.write(`t${frames / 30}s X ${X.map(Math.round)} Y ${Y.map(Math.round)} dmg ${dmg.map(Math.round)} stocks ${list('B Stock')} alive ${alive} zoom ${T.get('Zoom').toFixed(2)}\n`);
            }
            if (T.sprite('Cannonball').visible) out.cannon = true;
            if (T.get('Stage Key') === 'candy' && T.clones('Brawler').some(c => c.lookupVariableByNameAndType('VY').value > 16)) out.bounce = true;
            if (T.clones('Brawler').length > 4 || T.clones('Popup').length > 20) fail('brawl: too many clones');
        }
        if (T.get('State') !== 'over') return fail(`brawl: match ${match + 1} did not finish in 4 minutes`);
        out.matches++;
        if (T.get('Brawl Winner') === 1) out.wins++;
        await T.step(10);
        if (T.clones('Brawler').length !== 0 || T.clones('Brawl Platform').length !== 0) fail('brawl: clones left after the match');
        if (!T.sprite('Retry Button').visible) fail('brawl: no RETRY after the match');
        T.set('Stage Pick', match + 2);
        T.click('Retry Button');
        await T.step(3);
    }
    if (!out.cannon) fail('brawl: no cannonball on the Pirate Ship');
    if (!out.bounce) fail('brawl: nobody bounced on Candy Land');
    if (out.kos < STAGES) fail(`brawl: only ${out.kos} K.O.s in ${STAGES} matches`);
    if (!out.bolts) fail('brawl: POWER lightning never struck');
    if (out.zoom[0] < 0.49 || out.zoom[1] > 1.16 || out.zoom[1] - out.zoom[0] < 0.05) fail(`brawl: camera zoom ${out.zoom}`);
    if (new Set(out.stages).size < STAGES) fail(`brawl: not every stage was played: ${out.stages}`);
    T.click('Quit Button');
    await T.step(10);
    if (T.get('State') !== 'title' || T.clones('Brawler').length || T.get('Brawl Live') !== 0) {
        fail(`brawl: Quit did not clean up (state ${T.get('State')}, fighters ${T.clones('Brawler').length}, live ${T.get('Brawl Live')})`);
    }
    await T.step(120); // the countdown must not start the match again after quitting
    if (T.get('Brawl On') === 1 || T.get('State') !== 'title') fail('brawl: the match came back after Quit');
    if (errors.length) fail(`brawl: engine errors ${errors.slice(0, 2)}`);
    return out;
}

(async () => {
    const t0 = Date.now();
    const results = {};
    const only = process.env.ONLY; // e.g. ONLY=brawl runs just that part
    const want = name => !only || only.split(',').includes(name);
    if (want('story')) for (const hero of [1, 2, 3]) results[`story ${hero}`] = await storyRun(hero);
    if (want('arcade')) results.arcade = await arcadeRun(1);
    if (want('fire')) results.fire = await fireTest();
    if (want('spikes')) results.spikes = await spikeTest();
    if (want('boss')) results.boss = await bossTest();
    if (want('power')) results.power = await powerTest();
    if (want('ninja')) results.ninja = await ninjaTest();
    if (want('grok')) results.grok = await grokTest();
    if (want('intro')) results.intro = await introTest();
    if (want('powerup')) results.powerup = await powerUpTest();
    if (want('flip')) results.flip = await flipTest();
    if (want('whirl')) results.whirl = await whirlTest();
    if (want('adventure')) results.adventure = await adventureTest();
    if (want('adventure')) results.adventureBot = await adventureBotRun();
    if (want('brawl')) results.brawl = await brawlTest();
    if (want('mash')) await mashTest();
    if (want('weapons')) await weaponTest();
    const show = r => JSON.stringify(r, (k, v) => (v instanceof Set ? [...v] : v));
    for (const [k, v] of Object.entries(results)) process.stdout.write(`${k}: ${show(v)}\n`);
    if (problems.length) {
        process.stdout.write(`\nFAILED (${problems.length})\n  ${problems.join('\n  ')}\n`);
        process.exit(1);
    }
    process.stdout.write(`\nall checks passed${t0 ? '' : ''}\n`);
    process.exit(0);
})();
