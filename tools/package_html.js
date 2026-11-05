#!/usr/bin/env node
/*
 * Turn projects/arthurs-arena-legends.sb3 into one offline HTML file with
 * the TurboWarp packager. tools/build_android.py puts that file inside the
 * Android app. The same file also plays in any browser.
 *
 *   node tools/package_html.js [output.html]
 *
 * Needs: npm install @turbowarp/packager@3.14.0 (NODE_PATH may point at it).
 */
'use strict';
const fs = require('fs');
const path = require('path');
const Packager = require('@turbowarp/packager');

const ROOT = path.join(__dirname, '..');
const SB3 = path.join(ROOT, 'projects', 'arthurs-arena-legends.sb3');
const OUT = process.argv[2] || path.join(ROOT, 'dist', 'arthurs-arena.html');

// Scratch forgets variables when a packaged game closes. This keeps Best and
// Crown in the device's storage, so the high score and the crown unlock stay.
const SAVE_JS = `
(function () {
    var KEY = 'arthurs-arena-legends-save';
    var KEEP = ['Best', 'Crown', 'Power XP', 'Power Level'];   // keep the highest
    var LAST = ['Difficulty', 'Sound On', 'Stage Pick'];      // keep the last choice
    function stageVars () {
        var stage = vm.runtime.getTargetForStage && vm.runtime.getTargetForStage();
        if (!stage) return null;
        var out = {};
        Object.keys(stage.variables).forEach(function (id) {
            var v = stage.variables[id];
            if (KEEP.indexOf(v.name) !== -1 || LAST.indexOf(v.name) !== -1) out[v.name] = v;
        });
        return out;
    }
    var restored = false;
    setInterval(function () {
        var vars = stageVars();
        if (!vars || !vars.Best) return;
        var saved = {};
        try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
        if (!restored) {
            restored = true;
            KEEP.forEach(function (name) {
                if (vars[name] && Number(saved[name]) > Number(vars[name].value)) vars[name].value = Number(saved[name]);
            });
            LAST.forEach(function (name) {
                if (vars[name] && saved[name] !== undefined) vars[name].value = saved[name];
            });
            return;
        }
        var changed = false;
        KEEP.forEach(function (name) {
            if (vars[name] && Number(vars[name].value) > Number(saved[name] || 0)) {
                saved[name] = Number(vars[name].value);
                changed = true;
            }
        });
        LAST.forEach(function (name) {
            if (vars[name] && String(vars[name].value) !== String(saved[name])) {
                saved[name] = vars[name].value;
                changed = true;
            }
        });
        if (changed) {
            try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
        }
    }, 1000);
})();
`;

// Touch controls for phones and tablets: a thumb joystick on the left and
// action buttons on the right. They live outside Scratch because Scratch only
// follows one finger, and you need to walk and punch at the same time.
// They write the same variables the Scratch buttons do (Want Punch, ...), plus
// Joy X for walking. Touch Pad = 1 tells the game to hide its own buttons.
const PAD_JS = `
(function () {
    if (!('ontouchstart' in window) && !(navigator.maxTouchPoints > 0)) return; // computers keep the Scratch buttons
    var css = [
        '#pad{position:fixed;inset:0;pointer-events:none;z-index:50;display:none;-webkit-user-select:none;user-select:none}',
        '#pad.on{display:block}',
        // the controls live in two side columns (SIDE wide); the game is shrunk to fit between them
        '#joy{position:absolute;left:0;bottom:0;width:27vmin;height:64vh;pointer-events:auto;touch-action:none}',
        '#base{position:absolute;width:22vmin;height:22vmin;margin:-11vmin 0 0 -11vmin;border-radius:50%;',
        ' background:radial-gradient(circle,rgba(255,255,255,.10),rgba(255,255,255,.22));border:.8vmin solid rgba(255,255,255,.55);box-sizing:border-box}',
        '#knob{position:absolute;left:50%;top:50%;width:10vmin;height:10vmin;margin:-5vmin 0 0 -5vmin;border-radius:50%;',
        ' background:radial-gradient(circle at 35% 30%,#93c5fd,#2563eb);border:.6vmin solid #fff;box-shadow:0 .6vmin 1.5vmin rgba(0,0,0,.45)}',
        '.pb{position:absolute;width:12.5vmin;height:12.5vmin;margin:-6.25vmin 0 0 -6.25vmin;border-radius:50%;pointer-events:auto;touch-action:none;',
        ' display:flex;align-items:center;justify-content:center;font:900 2.4vmin Verdana,Arial,sans-serif;color:#fff;',
        ' border:.6vmin solid rgba(255,255,255,.85);box-shadow:0 .7vmin 0 rgba(0,0,0,.35);opacity:.88;box-sizing:border-box}',
        '.pb.down{transform:translateY(.5vmin) scale(.93);box-shadow:0 .2vmin 0 rgba(0,0,0,.35);opacity:1}',
        '#bP{background:#ea580c}#bK{background:#ca8a04}#bJ{background:#16a34a}#bD{background:#64748b}',
        '#bF{background:#dc2626;width:15vmin;height:15vmin;margin:-7.5vmin 0 0 -7.5vmin;font-size:2.9vmin;text-shadow:0 .3vmin 0 rgba(0,0,0,.4)}',
        '#bF.full{animation:glow .3s infinite alternate}',
        '#bW{background:#7c3aed;width:12vmin;height:12vmin;margin:-6vmin 0 0 -6vmin;font-size:2.1vmin}',
        '#bW.locked{background:#334155;color:#94a3b8}',
        '#bS{background:#475569;width:12vmin;height:12vmin;margin:-6vmin 0 0 -6vmin;font-size:2.1vmin}',
        '#bS.ready{background:#facc15;color:#7c2d12;animation:glow .5s infinite alternate}',
        '@keyframes glow{from{box-shadow:0 0 1vmin #fde047}to{box-shadow:0 0 4vmin #fde047}}'
    ].join('');
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    var pad = document.createElement('div');
    pad.id = 'pad';
    pad.innerHTML = '<div id="joy"><div id="base"><div id="knob"></div></div></div>' +
        '<div class="pb" id="bP">PUNCH</div><div class="pb" id="bK">KICK</div>' +
        '<div class="pb" id="bJ">JUMP</div><div class="pb" id="bD">DODGE</div><div class="pb" id="bS">SUPER</div>' +
        '<div class="pb" id="bF">FIRE</div><div class="pb" id="bW">POWER</div>';
    document.body.appendChild(pad);

    // right-hand buttons in a diamond, like a game controller
    // right column: two buttons wide, three rows; left column: FIRE above the joystick
    function place (id, left, top) {
        var el = document.getElementById(id);
        el.style.left = 'calc(' + left + ')';
        el.style.top = 'calc(' + top + ')';
    }
    var A = '100vw - 20vmin', B = '100vw - 7vmin';
    place('bP', A, '100vh - 8vmin'); place('bK', B, '100vh - 8vmin');
    place('bD', A, '100vh - 21.5vmin'); place('bJ', B, '100vh - 21.5vmin');
    place('bS', A, '100vh - 35vmin'); place('bW', B, '100vh - 35vmin');
    place('bF', '13.5vmin', '36vh - 9vmin');

    // keep the game itself clear of the buttons: tell the player to leave a column free on each side
    var SIDE = 0.27;
    function reserve () {
        var sc = window.scaffolding;
        if (!sc || typeof sc.relayout !== 'function') return;
        var side = Math.round(SIDE * Math.min(innerWidth, innerHeight));
        if (sc._offsetFromLeft !== side || sc._offsetFromRight !== side) {
            sc._offsetFromLeft = side;
            sc._offsetFromRight = side;
            sc.relayout();
        }
    }

    var vars = null;
    function v (name) {
        if (!vars) {
            var stage = window.vm && vm.runtime.getTargetForStage && vm.runtime.getTargetForStage();
            if (!stage) return null;
            vars = {};
            Object.keys(stage.variables).forEach(function (id) { vars[stage.variables[id].name] = stage.variables[id]; });
        }
        return vars[name] || null;
    }
    function set (name, value) { var x = v(name); if (x) x.value = value; }
    function get (name) { var x = v(name); return x ? x.value : null; }
    function buzz () { if (navigator.vibrate) { try { navigator.vibrate(12); } catch (e) {} } }

    // buttons: press sets the Want variable; holding PUNCH or KICK charges a power move
    // (Punch Held / Kick Held stay 1 until you let go)
    [['bP', 'Want Punch', 'Punch Held'], ['bK', 'Want Kick', 'Kick Held'], ['bJ', 'Want Jump', false],
     ['bD', 'Want Dodge', false], ['bS', 'Want Super', false], ['bW', 'Want Power', false]].forEach(function (b) {
        var el = document.getElementById(b[0]);
        el.addEventListener('pointerdown', function (e) {
            e.preventDefault();
            el.setPointerCapture(e.pointerId);
            el.classList.add('down');
            set(b[1], 1);
            buzz();
            if (b[2]) set(b[2], 1);
        });
        function up () { el.classList.remove('down'); if (b[2]) set(b[2], 0); }
        el.addEventListener('pointerup', up);
        el.addEventListener('pointercancel', up);
    });

    // FIRE: hold to charge a fireball, let go to shoot
    var bF = document.getElementById('bF');
    bF.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        bF.setPointerCapture(e.pointerId);
        bF.classList.add('down');
        set('Fire Held', 1);
        buzz();
    });
    function fireUp () { bF.classList.remove('down'); set('Fire Held', 0); }
    bF.addEventListener('pointerup', fireUp);
    bF.addEventListener('pointercancel', fireUp);

    // floating joystick: put your thumb anywhere in the bottom-left area
    var joy = document.getElementById('joy'), base = document.getElementById('base'), knob = document.getElementById('knob');
    var held = null, ox = 0, oy = 0, jumpArmed = true;
    function home () {
        var b = joy.getBoundingClientRect(), m = Math.min(innerWidth, innerHeight);
        base.style.left = (0.135 * m) + 'px';
        base.style.top = (b.height - 0.14 * m) + 'px';
        knob.style.transform = '';
    }
    function move (e) {
        var R = Math.min(innerWidth, innerHeight) * 0.11;
        var dx = e.clientX - ox, dy = e.clientY - oy, d = Math.sqrt(dx * dx + dy * dy), up = dy;
        if (d > R) { dx = dx * R / d; dy = dy * R / d; }
        knob.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
        set('Joy X', Math.round(dx / R * 100) / 100);
        set('Joy Y', Math.round(-up / R * 100) / 100); // BRAWL: push down to drop through a platform
        // flick the stick up to jump (measured before the knob is held to its ring,
        // so walking sideways and flicking up still jumps)
        if (up < -0.6 * R && jumpArmed) { set('Want Jump', 1); jumpArmed = false; buzz(); }
        if (up > -0.3 * R) jumpArmed = true;
    }
    joy.addEventListener('pointerdown', function (e) {
        if (held !== null) return;
        e.preventDefault();
        held = e.pointerId;
        joy.setPointerCapture(e.pointerId);
        var b = joy.getBoundingClientRect();
        ox = e.clientX; oy = e.clientY;
        base.style.left = (e.clientX - b.left) + 'px';
        base.style.top = (e.clientY - b.top) + 'px';
        move(e);
    });
    joy.addEventListener('pointermove', function (e) { if (e.pointerId === held) move(e); });
    function release (e) {
        if (e.pointerId !== held) return;
        held = null;
        set('Joy X', 0);
        set('Joy Y', 0);
        jumpArmed = true;
        home();
    }
    joy.addEventListener('pointerup', release);
    joy.addEventListener('pointercancel', release);
    addEventListener('resize', home);

    // show the pad only during a fight; light SUPER when it is ready
    var bS = document.getElementById('bS');
    var bW = document.getElementById('bW');
    (function tick () {
        reserve();
        if (get('State') !== null) {
            set('Touch Pad', 1);
            var fighting = get('State') === 'fight' || get('State') === 'brawl';
            if (fighting !== pad.classList.contains('on')) {
                pad.classList.toggle('on', fighting);
                if (!fighting) { set('Joy X', 0); held = null; }
                home();
            }
            bS.classList.toggle('ready', Number(get('Super')) >= 100);
            // POWER: locked until power level 2; a ring fills while it recharges
            var lvl = Number(get('Power Level')) || 1;
            var colors = ['#ef4444', '#f97316', '#facc15', '#3b82f6', '#a855f7'];
            bW.classList.toggle('locked', lvl < 2);
            bW.textContent = lvl < 2 ? 'LOCKED' : 'POWER';
            var now = vm.runtime.ioDevices.clock.projectTimer();
            var left = Number(get('Power Ready At')) - now;
            var pct = Math.max(0, Math.min(1, 1 - left / 6));
            bW.style.background = lvl < 2 ? '' : (pct < 1 ? 'conic-gradient(' + colors[lvl - 1] + ' ' + (pct * 360) + 'deg, #334155 0)' : colors[lvl - 1]);
            var c = Number(get('Charge')) || 0;   // the FIRE button fills up gold while charging
            bF.style.background = c > 0 ? 'conic-gradient(#facc15 ' + (c * 3.6) + 'deg, #dc2626 0)' : '';
            bF.classList.toggle('full', c >= 100);
        }
        requestAnimationFrame(tick);
    })();
})();
`;

(async () => {
    const loaded = await Packager.loadProject(fs.readFileSync(SB3));
    const packager = new Packager.Packager();
    packager.project = loaded;
    const o = packager.options;
    o.autoplay = true;               // no green flag to tap: the title shows straight away
    o.framerate = 30;
    o.fencing = false;               // BRAWL's camera moves platforms past the screen edge; don't push them back in
    o.resizeMode = 'preserve-ratio';
    o.appearance.background = '#000000';
    o.appearance.accent = '#facc15';
    o.loadingScreen.text = '';      // no name here: the title screen shows it once
    o.app.windowTitle = "Arthur's Arena";
    o.app.packageName = 'arthurs-arena';
    o.cloudVariables.mode = 'local';
    o.custom.js = SAVE_JS + PAD_JS;
    const result = await packager.package();
    fs.mkdirSync(path.dirname(OUT), {recursive: true});
    fs.writeFileSync(OUT, result.data);
    console.log(`wrote ${path.relative(process.cwd(), OUT)} (${Math.round(result.data.length / 1024)} KB)`);
})().catch(e => {
    console.error(e);
    process.exit(1);
});
