#!/usr/bin/env node
/*
 * Wi-Fi play test: two copies of the packaged game (dist/arthurs-arena.html, or the file given)
 * in a real browser, joined by a stand-in for the Android app's ArenaNet helper. One hosts, one
 * joins, both pick a fighter, they play a BRAWL in lockstep, and the test checks that:
 *   - the two screens stay in step (same fighters, same positions, every second),
 *   - the friend's joystick drives fighter 2,
 *   - leaving tells the other phone.
 *
 *   node tools/test_wifi.js [game.html]
 * Needs Playwright (require('playwright')).
 */
'use strict';
const path = require('path');
const {chromium, devices} = require('playwright');

const HTML = path.resolve(process.argv[2] || path.join(__dirname, '..', 'dist', 'arthurs-arena.html'));

// window.ArenaNet as the app provides it; send() is carried to the other page by the test
const FAKE = `
(function () {
    var st = { status: 'idle', error: '', ip: '10.0.0.' + (window.__who === 'A' ? 5 : 6), found: [] };
    var inbox = [];
    window.__netIn = function (line) { inbox.push(line); };
    window.__netStatus = function (s) { st.status = s; };
    window.ArenaNet = {
        state: function () { return JSON.stringify(st); },
        poll: function () { var s = inbox.join('\\n'); inbox = []; return s; },
        send: function (line) { if (st.status === 'connected') window.__netOut(line); },
        myIp: function () { return st.ip; },
        host: function (name) { st.status = 'hosting'; window.__netOut('#host ' + name); },
        find: function () { st.status = 'idle'; st.found = [{ name: 'ARENA TEST', host: '10.0.0.5', port: 47123 }]; },
        join: function () { window.__netOut('#join'); },
        stop: function () { if (st.status === 'connected') window.__netOut('#bye'); st.status = 'idle'; }
    };
})();
`;

const fails = [];
const fail = m => fails.push(m);

(async () => {
    const browser = await chromium.launch({args: ['--use-gl=swiftshader', '--ignore-gpu-blocklist']});
    const pages = {};
    const errors = [];
    for (const who of ['A', 'B']) {
        const ctx = await browser.newContext({...devices['Galaxy Tab S4 landscape']});
        const p = await ctx.newPage();
        p.on('pageerror', e => errors.push(who + ': ' + e));
        await p.addInitScript(`window.__who = '${who}';`);
        await p.addInitScript(FAKE);
        pages[who] = p;
    }
    const other = who => (who === 'A' ? pages.B : pages.A);
    let hosting = false;
    for (const who of ['A', 'B']) {
        await pages[who].exposeFunction('__netOut', async line => {
            if (line.startsWith('#host')) { hosting = true; return; }
            if (line === '#join') {
                if (!hosting) return;
                await pages.A.evaluate(() => window.__netStatus('connected'));
                await pages.B.evaluate(() => window.__netStatus('connected'));
                return;
            }
            if (line === '#bye') {
                await other(who).evaluate(() => window.__netStatus('lost')).catch(() => {});
                return;
            }
            await other(who).evaluate(l => window.__netIn(l), line).catch(() => {});
        });
    }
    for (const who of ['A', 'B']) {
        const p = pages[who];
        await p.goto('file://' + HTML);
        await p.waitForFunction(() => window.vm && vm.runtime.getSpriteTargetByName('Skip Intro'), null, {timeout: 30000});
        await p.waitForTimeout(500);
        await p.evaluate(() => vm.runtime.startHats('event_whenthisspriteclicked', null, vm.runtime.getSpriteTargetByName('Skip Intro')));
        await p.waitForTimeout(500);
        await p.evaluate(() => vm.runtime.startHats('event_whenthisspriteclicked', null, vm.runtime.getSpriteTargetByName('Brawl Button')));
    }
    const A = pages.A, B = pages.B;
    await A.waitForSelector('#netBtn', {state: 'visible', timeout: 10000});
    if (!(await B.isVisible('#netBtn'))) fail('wifi: no PLAY A FRIEND button on the BRAWL screen');
    // A hosts, B joins
    await A.click('#netBtn');
    await A.click('text=HOST A GAME');
    await B.click('#netBtn');
    await B.click('text=JOIN A GAME');
    await B.click('text=ARENA TEST');
    await A.waitForSelector('text=CONNECTED!', {timeout: 10000});
    await B.waitForSelector('text=CONNECTED!', {timeout: 10000});
    await A.screenshot({path: path.join(process.env.SHOTS || '/tmp', 'wifi-pick.png')});
    await A.click('#netPanel button:has-text("ARTHUR")');
    await B.click('#netPanel button:has-text("ROCKO")');
    // the match starts on both
    for (const p of [A, B]) {
        await p.waitForFunction(() => {
            const v = n => Object.values(vm.runtime.getTargetForStage().variables).find(x => x.name === n).value;
            return v('Brawl On') == 1;
        }, null, {timeout: 30000});
    }
    const read = p => p.evaluate(() => {
        const st = vm.runtime.getTargetForStage();
        const l = n => st.lookupVariableByNameAndType(n, 'list').value.slice();
        return {kinds: l('B Kind'), x: l('B X').map(Number), y: l('B Y').map(Number), dmg: l('B Dmg').map(Number),
                net: window.NET && window.NET.active};
    });
    const a0 = await read(A), b0 = await read(B);
    if (a0.kinds[0] !== 'arthur' || a0.kinds[1] !== 'rocko') fail(`wifi: fighters on the host are ${a0.kinds}`);
    if (JSON.stringify(a0.kinds) !== JSON.stringify(b0.kinds)) fail(`wifi: the phones disagree on the fighters (${a0.kinds} vs ${b0.kinds})`);
    if (!a0.net || !b0.net) fail('wifi: lockstep is not running on both');
    // B pushes its joystick right for 2 seconds, then left; A presses punch now and then
    const center = async (p, sel) => {
        const box = await p.locator(sel).boundingBox();
        return [box.x + box.width / 2, box.y + box.height / 2];
    };
    const startX = (await read(B)).x[1];
    // B holds the joystick to the right (a real pointer: the pad captures it)
    const jb = await B.locator('#joy').boundingBox();
    await B.mouse.move(jb.x + jb.width * 0.5, jb.y + jb.height * 0.6);
    await B.mouse.down();
    await B.mouse.move(jb.x + jb.width * 0.5 + 80, jb.y + jb.height * 0.6, {steps: 3});
    const [px, py] = await center(A, '#bP');
    for (let i = 0; i < 6; i++) {
        await A.mouse.move(px, py);
        await A.mouse.down();
        await A.mouse.up();
        await A.waitForTimeout(330);
    }
    const p2joy = await Promise.all([A, B].map(p => p.evaluate(() =>
        Object.values(vm.runtime.getTargetForStage().variables).find(x => x.name === 'P2 Joy X').value)));
    const dir2 = await Promise.all([A, B].map(p => p.evaluate(() => {
        const b = vm.runtime.targets.find(t => !t.isOriginal && t.sprite.name === 'Brawler' &&
            Number(t.lookupVariableByNameAndType('My Id').value) === 2);
        return b && [Number(b.lookupVariableByNameAndType('Dir').value), Number(b.lookupVariableByNameAndType('Stun').value)];
    })));
    const midX = (await read(B)).x[1];
    await B.mouse.up();
    // the friend's stick reaches fighter 2 on BOTH phones (its position also depends on who hits it)
    if (!(p2joy[0] > 0.5 && p2joy[1] > 0.5)) fail(`wifi: the friend's joystick did not reach fighter 2 (P2 Joy X ${p2joy})`);
    if (dir2.some(d => !d || (d[1] <= 0 && d[0] !== 1))) fail(`wifi: fighter 2 is not heading right on both phones (${JSON.stringify(dir2)})`);
    // in step: compare the frame-stamped checks both phones made, and the state at the same frame
    await A.waitForTimeout(4000);
    const hashes = await Promise.all([A, B].map(p => p.evaluate(() => window.NET && window.NET.active)));
    if (!hashes[0] || !hashes[1]) fail('wifi: the match stopped early (out of step?)');
    const msgs = await Promise.all([A, B].map(p => p.evaluate(() => document.getElementById('netPanel').innerText)));
    if (msgs.some(m => /out of step/.test(m))) fail('wifi: the phones got out of step');
    await A.screenshot({path: path.join(process.env.SHOTS || '/tmp', 'wifi-host.png')});
    await B.screenshot({path: path.join(process.env.SHOTS || '/tmp', 'wifi-guest.png')});
    if (process.env.WIFI_FULL) {
        // play the match to the end: both phones must reach the "Play again" screen together, never out of step
        const t0 = Date.now();
        let ended = [false, false];
        while (Date.now() - t0 < 10 * 60 * 1000 && !(ended[0] && ended[1])) {
            for (const [p, sel] of [[A, '#bK'], [B, '#bP']]) {
                const box = await p.locator(sel).boundingBox();
                if (!box) continue;   // the pad hides when the match is over
                const [x, y] = [box.x + box.width / 2, box.y + box.height / 2];
                await p.mouse.move(x, y); await p.mouse.down(); await p.mouse.up();
            }
            await A.waitForTimeout(400);
            if (process.env.DEBUG_WIFI && Math.round((Date.now() - t0) / 400) % 25 === 0) {
                const info = await Promise.all([A, B].map(p => p.evaluate(() => {
                    const st = vm.runtime.getTargetForStage();
                    const v = n => Object.values(st.variables).find(x => x.name === n).value;
                    return [v('State'), window.NET.active, window.NET.frame(), st.lookupVariableByNameAndType('B Alive', 'list').value.join(''),
                            st.lookupVariableByNameAndType('B Stock', 'list').value.join(''), v('Brawl On'), v('Net Players'),
                            document.getElementById('netPanel').style.display, (document.querySelector('#netPanel h2') || {}).innerText];
                })));
                console.log(Math.round((Date.now() - t0) / 1000) + 's', JSON.stringify(info));
            }
            ended = await Promise.all([A, B].map(p => p.evaluate(() => /Play again/.test(document.getElementById('netPanel').innerText))));
            const txt = await Promise.all([A, B].map(p => p.evaluate(() => document.getElementById('netPanel').innerText)));
            if (txt.some(m => /out of step|Lost the connection/.test(m))) { fail('wifi: a full match stopped: ' + txt.join(' / ')); break; }
        }
        if (!(ended[0] && ended[1])) fail('wifi: the full match did not end on both phones');
        const titles = await Promise.all([A, B].map(p => p.evaluate(() => document.querySelector('#netPanel h2').innerText)));
        console.log('wifi full match:', Math.round((Date.now() - t0) / 1000) + 's', titles);
        await A.screenshot({path: path.join(process.env.SHOTS || '/tmp', 'wifi-after.png')});
        // rematch: both tap REMATCH and a new match starts on both
        await A.click('text=REMATCH');
        await B.click('text=REMATCH');
        for (const p of [A, B]) {
            await p.waitForFunction(() => window.NET && window.NET.active, null, {timeout: 15000}).catch(() => fail('wifi: rematch did not start'));
        }
    }
    // pause both at the same moment by comparing the frame numbers they report
    const frames = await Promise.all([A, B].map(p => p.evaluate(() => window.NET.frame && window.NET.frame())));
    // B leaves: A is told
    await B.evaluate(() => window.NET.leave());
    await A.waitForSelector('text=Your friend left', {timeout: 10000}).catch(() => fail('wifi: the host was not told the friend left'));
    const after = await A.evaluate(() => ({active: window.NET.active,
        state: Object.values(vm.runtime.getTargetForStage().variables).find(x => x.name === 'State').value}));
    if (after.active) fail('wifi: lockstep still running after the friend left');
    if (errors.length) fail('wifi: page errors ' + errors.slice(0, 3).join(' | '));
    console.log('wifi:', JSON.stringify({fighters: a0.kinds, p2Joy: p2joy, p2Dir: dir2, frames, hostAfter: after}));
    await browser.close();
    if (fails.length) {
        console.log('\nFAILED (' + fails.length + ')\n  ' + fails.join('\n  '));
        process.exit(1);
    }
    console.log('\nall checks passed');
})().catch(e => { console.error(e); process.exit(1); });
