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
const EXT_JS = `
(function () {
    // fill the black bars round the game with the stage's own backdrop, mirrored outward from each edge,
    // so the sky, ground and hills carry on to the edges of the screen
    var TEXT = ['Title', 'Select', 'Arcade', 'Ending'];   // backdrops with words on: soften their mirror images
    var cv = document.createElement('canvas');
    cv.id = 'ext';
    cv.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:-1;pointer-events:none';
    document.body.insertBefore(cv, document.body.firstChild);
    var ctx = cv.getContext('2d');
    var last = '';
    function picture (costume) {
        // the renderer keeps each backdrop as a ready-drawn picture (the packager frees the original file)
        var skin = window.vm && vm.renderer && vm.renderer._allSkins && vm.renderer._allSkins[costume.skinId];
        if (skin && skin._svgImage && skin._svgImage.naturalWidth) return skin._svgImage;
        if (skin && skin._canvas && skin._canvas.width) return skin._canvas;
        return null;
    }
    function draw () {
        var sc = window.scaffolding, vm = window.vm;
        if (!sc || !vm || !vm.runtime.getTargetForStage || !sc._layers) return;
        var stage = vm.runtime.getTargetForStage();
        if (!stage) return;
        var costume = stage.getCostumes()[stage.currentCostume];
        var r = sc._layers.getBoundingClientRect();
        var dpr = window.devicePixelRatio || 1;
        var key = costume.assetId + '|' + [r.left, r.top, r.width, r.height, innerWidth, innerHeight, dpr].map(Math.round).join(',');
        var img = picture(costume);
        if (key === last || !img || r.width < 2) return;
        last = key;
        cv.width = Math.round(innerWidth * dpr);
        cv.height = Math.round(innerHeight * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        if (TEXT.indexOf(costume.name) !== -1) {
            // a backdrop with words on: stretch its outer edge to the screen edges (a mirror would show backwards words)
            var iw = img.naturalWidth || img.width, ih = img.naturalHeight || img.height, e = Math.max(2, Math.round(iw / 80));
            var W = innerWidth, H = innerHeight;
            ctx.drawImage(img, 0, 0, e, ih, 0, r.top, r.left, r.height);
            ctx.drawImage(img, iw - e, 0, e, ih, r.right, r.top, W - r.right, r.height);
            ctx.drawImage(img, 0, 0, iw, e, r.left, 0, r.width, r.top);
            ctx.drawImage(img, 0, ih - e, iw, e, r.left, r.bottom, r.width, H - r.bottom);
            ctx.drawImage(img, 0, 0, e, e, 0, 0, r.left, r.top);
            ctx.drawImage(img, iw - e, 0, e, e, r.right, 0, W - r.right, r.top);
            ctx.drawImage(img, 0, ih - e, e, e, 0, r.bottom, r.left, H - r.bottom);
            ctx.drawImage(img, iw - e, ih - e, e, e, r.right, r.bottom, W - r.right, H - r.bottom);
        } else {
        // tiles round the stage: odd steps are mirror images, so every edge meets itself and the scene flows on
        for (var i = -3; i <= 3; i++) {
            for (var j = -2; j <= 2; j++) {
                if (i === 0 && j === 0) continue;
                var x = r.left + i * r.width, y = r.top + j * r.height;
                if (x > innerWidth || x + r.width < 0 || y > innerHeight || y + r.height < 0) continue;
                ctx.save();
                ctx.translate(x + (i % 2 ? r.width : 0), y + (j % 2 ? r.height : 0));
                ctx.scale(i % 2 ? -1 : 1, j % 2 ? -1 : 1);
                ctx.drawImage(img, 0, 0, r.width, r.height);
                ctx.restore();
            }
        }
        }
        // a slight shade outside the stage, so the real playing area still stands out
        ctx.fillStyle = 'rgba(0,0,0,0.18)';
        ctx.fillRect(0, 0, innerWidth, r.top);
        ctx.fillRect(0, r.bottom, innerWidth, innerHeight - r.bottom);
        ctx.fillRect(0, r.top, r.left, r.height);
        ctx.fillRect(r.right, r.top, innerWidth - r.right, r.height);
    }
    (function tick () {
        try { draw(); } catch (e) {}
        requestAnimationFrame(tick);
    })();
})();
`;

const HUD_JS = `
(function () {
    // the health bars, names and score live in a bar across the very top of the screen, edge to edge,
    // and the game is drawn just under it, so nothing covers the fight
    var css = [
        '#hud{position:fixed;left:0;right:0;top:0;height:10vmin;z-index:40;display:none;align-items:center;gap:2vmin;',
        ' padding:0 2vmin;box-sizing:border-box;background:linear-gradient(rgba(10,10,25,.72),rgba(10,10,25,.38));',
        ' font:900 2.5vmin Verdana,Arial,sans-serif;color:#fff;pointer-events:none;-webkit-user-select:none;user-select:none}',
        '#hud.on{display:flex}',
        '#hud .side{flex:1;display:flex;flex-direction:column;gap:.7vmin;min-width:0}',
        '#hud .row{display:flex;align-items:center;gap:1.2vmin}',
        '#hud .right .row{flex-direction:row-reverse}',
        '#hud .tag{padding:.25vmin 1.4vmin;border-radius:1vmin;white-space:nowrap;border:.35vmin solid rgba(255,255,255,.75);',
        ' text-shadow:0 .25vmin 0 rgba(0,0,0,.35)}',
        '#hud .bar{flex:1;height:2.8vmin;background:#1e293b;border:.4vmin solid #0b1220;border-radius:1.6vmin;overflow:hidden;display:flex}',
        '#hud .right .bar{justify-content:flex-end}',
        '#hud .fill{height:100%;border-radius:1.2vmin;transition:width .12s linear}',
        '#hud .sup{height:1.5vmin;margin-left:0}',
        '#hud .sup.full .fill{animation:hudglow .35s infinite alternate}',
        '@keyframes hudglow{from{filter:brightness(1)}to{filter:brightness(1.45)}}',
        '#hud .mid{display:flex;align-items:center;gap:1.2vmin}',
        '#hud .box{background:#e2e8f0;color:#334155;border-radius:1vmin;padding:.3vmin 1.2vmin;white-space:nowrap;font-size:2.3vmin}',
        '#hud .box b{background:#f97316;color:#fff;border-radius:.8vmin;padding:0 1vmin;margin-left:.8vmin}',
        '#hud .quit{pointer-events:auto;width:6vmin;height:6vmin;border-radius:50%;background:#334155;border:.45vmin solid #fff;',
        ' display:flex;align-items:center;justify-content:center;font-size:2.8vmin;touch-action:none;cursor:pointer}',
        '#hud .fighters{flex:1;display:flex;gap:1.5vmin;justify-content:space-between}',
        '#hud .ftr{flex:1;display:flex;align-items:center;gap:1vmin;background:rgba(15,23,42,.8);border:.4vmin solid;border-radius:1.4vmin;',
        ' padding:.4vmin 1vmin;min-width:0}',
        '#hud .ftr.out{opacity:.4}',
        '#hud .pct{background:#f97316;border-radius:.8vmin;padding:0 .8vmin;font-size:3vmin;min-width:7vmin;text-align:center}',
        '#hud .nm{font-size:1.9vmin;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
        '#hud .dots{display:flex;gap:.5vmin}#hud .dots i{width:1.6vmin;height:1.6vmin;border-radius:50%;border:.3vmin solid #fff;display:block}'
    ].join('');
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    var hud = document.createElement('div');
    hud.id = 'hud';
    document.body.appendChild(hud);

    var stage = null, vars = null, info = null, mode = '';
    function v (name) {
        if (!vars) {
            stage = window.vm && vm.runtime.getTargetForStage && vm.runtime.getTargetForStage();
            if (!stage) return null;
            vars = {};
            Object.keys(stage.variables).forEach(function (id) { vars[stage.variables[id].name] = stage.variables[id]; });
        }
        return vars[name] || null;
    }
    function get (name) { var x = v(name); return x ? x.value : null; }
    function list (name) { var x = v(name); return x && x.value instanceof Array ? x.value : []; }
    function who (key) {
        if (!info) { try { info = JSON.parse(get('HUD Info')); } catch (e) { info = {}; } }
        return info[key] || [String(key || '').toUpperCase(), '#334155'];
    }
    function quitTap (e) {
        e.preventDefault();
        var t = vm.runtime.getSpriteTargetByName('Quit Button');
        if (t) vm.runtime.startHats('event_whenthisspriteclicked', null, t);
    }
    function healthColor (p) { return p > 60 ? '#16a34a' : (p > 30 ? '#eab308' : '#dc2626'); }
    function build (m) {
        mode = m;
        if (m === 'fight') {
            hud.innerHTML =
                '<div class="side left"><div class="row"><span class="tag" id="hT"></span><div class="bar"><div class="fill" id="hF"></div></div></div>' +
                '<div class="row"><span class="tag" style="visibility:hidden" id="hT2"></span><div class="bar sup" id="sB"><div class="fill" id="sF"></div></div></div></div>' +
                '<div class="mid"><span class="box">Score<b id="sc">0</b></span><span class="box" id="wvB">Wave<b id="wv">1</b></span>' +
                '<div class="quit" id="hq">✕</div></div>' +
                '<div class="side right"><div class="row"><span class="tag" id="eT"></span><div class="bar"><div class="fill" id="eF"></div></div></div>' +
                '<div class="row" style="visibility:hidden"><span class="tag" id="eT2"></span><div class="bar sup"></div></div></div>';
        } else {
            hud.innerHTML = '<div class="fighters" id="fs"></div><div class="mid"><div class="quit" id="hq">✕</div></div><div class="fighters" id="fs2"></div>';
        }
        document.getElementById('hq').addEventListener('pointerdown', quitTap);
    }
    function pct (a, b) { a = Number(a) || 0; b = Number(b) || 1; return Math.max(0, Math.min(100, a / b * 100)); }
    function fight () {
        if (mode !== 'fight') build('fight');
        var h = who(get('Hero Name')), hT = document.getElementById('hT');
        hT.textContent = get('Hero Title') || h[0]; hT.style.background = h[1];
        document.getElementById('hT2').textContent = hT.textContent;
        var hp = pct(get('Hero HP'), get('Hero Max')), hF = document.getElementById('hF');
        hF.style.width = hp + '%'; hF.style.background = healthColor(hp);
        var sp = pct(get('Super'), 100), sF = document.getElementById('sF');
        sF.style.width = sp + '%'; sF.style.background = sp >= 100 ? '#fde047' : '#f59e0b';
        document.getElementById('sB').classList.toggle('full', sp >= 100);
        var squad = Number(get('Wave Phase')) === 1, e = squad ? ['ENEMY WAVE', '#b45309'] : who(get('Enemy Name'));
        var eT = document.getElementById('eT');
        eT.textContent = e[0]; eT.style.background = e[1];
        document.getElementById('eT2').textContent = e[0];
        var ep = pct(get('Enemy HP'), get('Enemy Max')), eF = document.getElementById('eF');
        eF.style.width = ep + '%'; eF.style.background = healthColor(ep);
        document.getElementById('sc').textContent = get('Score');
        document.getElementById('wvB').style.display = get('Mode') === 'arcade' ? '' : 'none';
        document.getElementById('wv').textContent = get('Wave');
    }
    function brawl () {
        if (mode !== 'brawl') build('brawl');
        var kinds = list('B Kind'), stock = list('B Stock'), alive = list('B Alive');
        var html = ['', ''];
        for (var i = 0; i < kinds.length && i < 4; i++) {
            var k = who(kinds[i]), dots = '';
            for (var d = 0; d < 3; d++) dots += '<i style="background:' + (d < Number(stock[i]) ? k[1] : '#334155') + '"></i>';
            html[i < 2 ? 0 : 1] += '<div class="ftr' + (Number(alive[i]) === 1 ? '' : ' out') + '" style="border-color:' + k[1] + '">' +
                '<span class="pct">' + Math.round(Number(get('P' + (i + 1) + ' %')) || 0) + '%</span>' +
                '<span><div class="nm">' + k[0] + '</div><div class="dots">' + dots + '</div></span></div>';
        }
        document.getElementById('fs').innerHTML = html[0];
        document.getElementById('fs2').innerHTML = html[1];
    }
    function reserveTop () {
        var sc = window.scaffolding;
        if (!sc || typeof sc.relayout !== 'function') return;
        var top = Math.round(0.10 * Math.min(innerWidth, innerHeight));
        if (sc._offsetFromTop !== top) { sc._offsetFromTop = top; sc.relayout(); }
    }
    (function tick () {
        try {
            if (get('State') !== null) {
                reserveTop();
                if (Number(get('Page HUD')) !== 1) v('Page HUD').value = 1;
                var state = get('State'), on = state === 'fight' || (state === 'brawl' && Number(get('Brawl Live')) === 1);
                hud.classList.toggle('on', on);
                if (on) { if (state === 'fight') fight(); else brawl(); }
            }
        } catch (e) {}
        requestAnimationFrame(tick);
    })();
})();
`;

const PAD_JS = `
(function () {
    if (!('ontouchstart' in window) && !(navigator.maxTouchPoints > 0)) return; // computers keep the Scratch buttons
    var css = [
        '#pad{position:fixed;inset:0;pointer-events:none;z-index:50;display:none;-webkit-user-select:none;user-select:none}',
        '#pad.on{display:block}',
        // the controls live in two side columns (SIDE wide); the game is shrunk to fit between them
        '#joy{position:absolute;left:0;bottom:0;width:21vmin;height:70vh;pointer-events:auto;touch-action:none}',
        '#base{position:absolute;width:18vmin;height:18vmin;margin:-9vmin 0 0 -9vmin;border-radius:50%;',
        ' background:radial-gradient(circle,rgba(255,255,255,.10),rgba(255,255,255,.22));border:.8vmin solid rgba(255,255,255,.55);box-sizing:border-box}',
        '#knob{position:absolute;left:50%;top:50%;width:8vmin;height:8vmin;margin:-4vmin 0 0 -4vmin;border-radius:50%;',
        ' background:radial-gradient(circle at 35% 30%,#93c5fd,#2563eb);border:.6vmin solid #fff;box-shadow:0 .6vmin 1.5vmin rgba(0,0,0,.45)}',
        '.pb{position:absolute;width:9.6vmin;height:9.6vmin;margin:-4.8vmin 0 0 -4.8vmin;border-radius:50%;pointer-events:auto;touch-action:none;',
        ' display:flex;align-items:center;justify-content:center;font:900 1.9vmin Verdana,Arial,sans-serif;color:#fff;',
        ' border:.6vmin solid rgba(255,255,255,.85);box-shadow:0 .7vmin 0 rgba(0,0,0,.35);opacity:.82;box-sizing:border-box}',
        '.pb.down{transform:translateY(.5vmin) scale(.93);box-shadow:0 .2vmin 0 rgba(0,0,0,.35);opacity:1}',
        '#bP{background:#ea580c}#bK{background:#ca8a04}#bJ{background:#16a34a}#bD{background:#64748b}',
        '#bF{background:#dc2626;width:10.2vmin;height:10.2vmin;margin:-5.1vmin 0 0 -5.1vmin;font-size:2vmin;text-shadow:0 .3vmin 0 rgba(0,0,0,.4)}',
        '#bF.full{animation:glow .3s infinite alternate}',
        '#bW{background:#7c3aed;width:9vmin;height:9vmin;margin:-4.5vmin 0 0 -4.5vmin;font-size:1.6vmin}',
        '#bW.locked{background:#334155;color:#94a3b8}',
        '#bS{background:#475569;width:7.8vmin;height:7.8vmin;margin:-3.9vmin 0 0 -3.9vmin;font-size:1.5vmin}',
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
    // the round cluster: PUNCH, KICK, JUMP and DODGE in a diamond, SUPER, POWER and FIRE round it
    var r = 7.8;   // vmin from the middle of the diamond to each of its buttons
    function ring (id, dx, dy) {
        place(id, '100vw - 13.4vmin + ' + (dx * r) + 'vmin', '100vh - 13.4vmin + ' + (dy * r) + 'vmin');
    }
    ring('bP', 0, 1); ring('bK', 1, 0); ring('bJ', 0, -1); ring('bD', -1, 0);
    ring('bS', -1.15, -1.55); ring('bF', -2.15, 0.85); ring('bW', -2.3, -0.6);

    // make room for the controls, but only about half of it: the game is drawn wider and the lower
    // half of the joystick and the button cluster sits over the bottom of the game (mostly the floor)
    var LEFT = 0.11, RIGHT = 0.19;
    function reserve () {
        var sc = window.scaffolding;
        if (!sc || typeof sc.relayout !== 'function') return;
        var m = Math.min(innerWidth, innerHeight), left = Math.round(LEFT * m), right = Math.round(RIGHT * m);
        if (sc._offsetFromLeft !== left || sc._offsetFromRight !== right) {
            sc._offsetFromLeft = left;
            sc._offsetFromRight = right;
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
        base.style.left = (0.11 * m) + 'px';
        base.style.top = (b.height - 0.115 * m) + 'px';
        knob.style.transform = '';
    }
    function move (e) {
        var R = Math.min(innerWidth, innerHeight) * 0.09;
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
    o.custom.js = SAVE_JS + EXT_JS + HUD_JS + PAD_JS;
    const result = await packager.package();
    fs.mkdirSync(path.dirname(OUT), {recursive: true});
    fs.writeFileSync(OUT, result.data);
    console.log(`wrote ${path.relative(process.cwd(), OUT)} (${Math.round(result.data.length / 1024)} KB)`);
})().catch(e => {
    console.error(e);
    process.exit(1);
});
