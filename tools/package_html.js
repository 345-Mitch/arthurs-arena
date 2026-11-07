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
const LOG_JS = `
(function () {
    // One tiny logger for the page modules: console output tagged by area, plus the last 200 lines kept in
    // window.ARENA_LOG so they can be read on a phone (chrome://inspect) after something goes wrong.
    var lines = window.ARENA_LOG = [];
    window.arenaLog = function (area, msg, data) {
        var line = '[' + new Date().toISOString().slice(11, 23) + '] [' + area + '] ' + msg +
                   (data === undefined ? '' : ' ' + (typeof data === 'string' ? data : JSON.stringify(data)));
        lines.push(line);
        if (lines.length > 200) lines.shift();
        try { console.log(line); } catch (e) {}
    };
})();
`;

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
        if (window.NET && NET.active) return;   // Wi-Fi play runs on the host's copy of the game
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

const LAYOUT_JS = `
(function () {
    // Screen layout only. The game fills the screen: as big as it fits, then zoomed in a little more so it reaches the edges
    // (trimming at most a thin strip off the far edges, where nothing important happens). The top bar,
    // joystick and buttons sit on top of it. Anything still left over shows the continued scenery.
    var MAX_ZOOM_NARROW = 1.2;   // screens squarer than the game (tablets, foldables): may trim the far left/right
    var MAX_ZOOM_WIDE = 1.12;    // screens wider than the game (phones): may trim a little top and bottom
    function fillScreen () {
        var sc = window.scaffolding;
        if (!sc || typeof sc.relayout !== 'function') return;
        var W = innerWidth, H = innerHeight;
        var fit = Math.min(W / 480, H / 360), cover = Math.max(W / 480, H / 360);
        var scale = Math.min(cover, fit * (W / H < 4 / 3 ? MAX_ZOOM_NARROW : MAX_ZOOM_WIDE));
        var x = Math.round((W - 480 * scale) / 2), y = Math.round((H - 360 * scale) / 2);
        if (sc._offsetFromLeft !== x || sc._offsetFromRight !== x || sc._offsetFromTop !== y || sc._offsetFromBottom !== y) {
            sc._offsetFromLeft = x; sc._offsetFromRight = x;
            sc._offsetFromTop = y; sc._offsetFromBottom = y;
            sc.relayout();
            arenaLog('layout', 'game drawn at', { scale: Math.round(scale * 100) / 100, x: x, y: y, screen: W + 'x' + H });
        }
    }
    setInterval(fillScreen, 250);   // cheap: it only re-lays out when the screen size changes
})();
`;

const HUD_JS = `
(function () {
    // the health bars, names and score live in a bar across the very top of the screen, edge to edge,
    // and the game is drawn just under it, so nothing covers the fight
    var css = [
        '#hud{position:fixed;left:0;right:0;top:0;height:10vmin;z-index:40;display:none;align-items:center;gap:2vmin;',
        ' padding:0 2vmin;box-sizing:border-box;background:linear-gradient(rgba(10,10,25,.55),rgba(10,10,25,0));',
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
        if (window.NET && NET.active && NET.leave) { NET.leave(); return; }
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
    (function tick () {
        try {
            if (get('State') !== null) {
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

const NET_JS = `
(function () {
    // Wi-Fi play: two copies of the app on the same Wi-Fi (or a phone's hotspot) play one BRAWL together.
    // Both phones run the very same match ("lockstep"): each frame they swap only the buttons pressed,
    // and with the same seed for "pick random" and a frame-by-frame clock they stay exactly in step.
    var NET = window.NET = { active: false, capture: false, take: function () { return false; } };
    var api = window.ArenaNet;
    if (!api) return;   // only inside the Android app
    var FRAME = 1000 / 30, DELAY = 4;   // my buttons count 4 frames later, so they have time to reach my friend
    var PULSES = ['Want Punch', 'Want Kick', 'Want Jump', 'Want Dodge', 'Want Super', 'Want Power', 'Want Drop'];
    var STATES = ['Joy X', 'Joy Y', 'Fire Held'];
    var DROP = ['Punch Held', 'Kick Held'];
    var KINDS = ['arthur', 'nova', 'rocko'];
    var KEEP = ['Best', 'Crown', 'Power XP', 'Power Level', 'Difficulty', 'Sound On', 'Stage Pick'];
    var local = { 'Joy X': 0, 'Joy Y': 0, 'Fire Held': 0 }, pulses = {};
    NET.take = function (name, value) {
        if (!NET.capture) return false;
        if (PULSES.indexOf(name) !== -1) { if (Number(value) === 1) pulses[name] = 1; return true; }
        if (STATES.indexOf(name) !== -1) { local[name] = Number(value) || 0; return true; }
        return DROP.indexOf(name) !== -1;
    };

    // ---- the game's variables
    var vars = null;
    function rt () { return window.vm && vm.runtime; }
    function v (name) {
        if (!vars) {
            var st = rt() && rt().getTargetForStage();
            if (!st) return null;
            vars = {};
            Object.keys(st.variables).forEach(function (id) { vars[st.variables[id].name] = st.variables[id]; });
        }
        return vars[name] || null;
    }
    function get (name) { var x = v(name); return x ? x.value : null; }
    function set (name, value) { var x = v(name); if (x) x.value = value; }
    function list (name) { var x = v(name); return x && x.value instanceof Array ? x.value : []; }
    function click (sprite) { var t = rt().getSpriteTargetByName(sprite); if (t) rt().startHats('event_whenthisspriteclicked', null, t); }
    function title (kind) {
        try { return JSON.parse(get('HUD Info'))[kind][0]; } catch (e) { return String(kind).toUpperCase(); }
    }

    // ---- the screen: a WI-FI button on the BRAWL fighter screen opens the panel
    var css = [
        '#netBtn{position:fixed;left:2vmin;top:12vmin;z-index:60;display:none;padding:1.4vmin 2.6vmin;border-radius:2vmin;',
        ' background:#0ea5e9;color:#fff;font:900 2.8vmin Verdana,Arial,sans-serif;border:.5vmin solid #fff;box-shadow:0 .6vmin 0 rgba(0,0,0,.35)}',
        '#netPanel{position:fixed;inset:0;z-index:70;display:none;align-items:center;justify-content:center;background:rgba(2,6,23,.6);',
        ' font:900 2.7vmin Verdana,Arial,sans-serif;color:#0f172a}',
        '#netPanel .card{background:#fffbeb;border:.8vmin solid #0f172a;border-radius:3vmin;padding:3vmin 4vmin;min-width:60vmin;max-width:86vw;text-align:center}',
        '#netPanel h2{margin:0 0 2vmin;font-size:4.2vmin;color:#0369a1}',
        '#netPanel p{margin:1.2vmin 0;font-weight:600;font-size:2.5vmin}',
        '#netPanel .btns{display:flex;flex-wrap:wrap;gap:2vmin;justify-content:center;margin-top:2vmin}',
        '#netPanel button{font:900 2.8vmin Verdana,Arial,sans-serif;color:#fff;border:.5vmin solid #0f172a;border-radius:2vmin;padding:1.6vmin 3vmin;',
        ' background:#16a34a;box-shadow:0 .6vmin 0 rgba(0,0,0,.35)}',
        '#netPanel button.grey{background:#64748b}#netPanel button.blue{background:#2563eb}#netPanel button.picked{outline:.8vmin solid #facc15}',
        '#netPanel input{font:700 2.8vmin Verdana,Arial,sans-serif;padding:1vmin;border-radius:1.4vmin;border:.4vmin solid #0f172a;width:30vmin}'
    ].join('');
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    var btn = document.createElement('div');
    btn.id = 'netBtn';
    btn.textContent = '📶 PLAY A FRIEND';
    document.body.appendChild(btn);
    var panel = document.createElement('div');
    panel.id = 'netPanel';
    document.body.appendChild(panel);

    var S = { view: 'off', role: '', peer: '', myPick: '', peerPick: '', myName: '', ready: { me: false, peer: false }, note: '' };
    function show (view, note) {
        if (view !== S.view) arenaLog('net', 'screen ' + S.view + ' -> ' + view, note || undefined);
        S.view = view;
        S.note = note || '';
        draw();
    }
    function button (label, cls, fn) {
        var b = document.createElement('button');
        b.textContent = label;
        if (cls) b.className = cls;
        b.addEventListener('click', function (e) { e.preventDefault(); fn(); });
        return b;
    }
    // ---- the panel is a small state machine: S.view is the state, VIEWS[state] draws it.
    // Each view returns { title, text or html, buttons, extra rows below the buttons, footer buttons }.
    function el (tag, text) { var e = document.createElement(tag); if (text) e.textContent = text; return e; }
    var VIEWS = {
        menu: function () {
            return { title: '📶 PLAY A FRIEND',
                     text: 'Both phones need Arthur\\'s Arena and the same Wi-Fi (or one phone\\'s hotspot). One taps HOST, the other taps JOIN.',
                     buttons: [button('HOST A GAME', 'blue', host), button('JOIN A GAME', '', find), button('CLOSE', 'grey', leave)] };
        },
        hosting: function (st) {
            return { title: 'WAITING FOR A FRIEND…',
                     html: 'Tell your friend to tap <b>JOIN A GAME</b>.<br>Your game is <b>' + S.myName + '</b>' + (st.ip ? ' (' + st.ip + ')' : ''),
                     buttons: [button('CANCEL', 'grey', leave)] };
        },
        joining: function (st) {
            var games = (st.found || []).map(function (g) {
                return button(g.name, 'blue', function () { arenaLog('net', 'joining', g); api.join(g.host, g.port); show('connecting'); });
            });
            var row = el('p', 'Not there? Type the number on your friend\\'s screen: ');
            var input = el('input');
            input.placeholder = '192.168.1.5';
            input.inputMode = 'decimal';
            row.appendChild(input);
            row.appendChild(button('JOIN', '', function () {
                var ip = input.value.trim();
                if (!ip) return;
                arenaLog('net', 'joining typed address', ip);
                api.join(ip, 0);
                show('connecting');
            }));
            return { title: 'JOIN A GAME', text: games.length ? 'Tap your friend\\'s game:' : 'Looking for games on this Wi-Fi…',
                     buttons: games, extra: [row], footer: [button('CANCEL', 'grey', leave)] };
        },
        connecting: function (st) {
            return { title: 'JOINING…', text: st.status === 'error' ? 'Could not join: ' + st.error : 'Connecting to your friend…',
                     buttons: [button('CANCEL', 'grey', leave)] };
        },
        pick: function () {
            var buttons = KINDS.map(function (k) {
                return button(title(k), S.myPick === k ? 'blue picked' : 'blue', function () {
                    S.myPick = k; send({ t: 'pick', kind: k }); draw(); maybeStart();
                });
            });
            if (S.role === 'host') {
                var names = [];
                try { names = JSON.parse(get('Stage Names')); } catch (e) {}
                var pick = Number(get('Stage Pick')) || 0;
                buttons.push(button('STAGE: ' + (pick ? names[pick - 1] : 'RANDOM'), 'grey', function () {
                    set('Stage Pick', (pick + 1) % (names.length + 1)); draw();
                }));
            }
            return { title: 'CONNECTED! 🎉',
                     text: 'Pick your fighter' + (S.role === 'host' ? ' (you are fighter 1, your friend is fighter 2):'
                                                                    : ' (your friend is fighter 1, you are fighter 2):'),
                     buttons: buttons,
                     extra: [el('p', S.peerPick ? 'Your friend picked ' + title(S.peerPick) + '.' : 'Waiting for your friend to pick…')],
                     footer: [button('LEAVE', 'grey', leave)] };
        },
        after: function () {
            return { title: S.note || 'GOOD GAME!', text: 'Play again with your friend?',
                     buttons: [button(S.ready.me ? 'WAITING…' : 'REMATCH', '', function () {
                         S.ready.me = true; send({ t: 'again' }); draw(); maybeStart();
                     }), button('LEAVE', 'grey', leave)] };
        },
        message: function () {
            return { title: 'WI-FI PLAY', text: S.note, buttons: [button('OK', '', function () { show('off'); })] };
        }
    };
    function row (buttons) {
        var r = el('div');
        r.className = 'btns';
        (buttons || []).forEach(function (b) { r.appendChild(b); });
        return r;
    }
    function draw () {
        var view = VIEWS[S.view];
        panel.style.display = view ? 'flex' : 'none';
        if (!view) return;   // 'off'
        var st = {};
        try { st = JSON.parse(api.state()); } catch (e) {}
        var v = view(st), card = el('div'), p = el('p');
        card.className = 'card';
        card.appendChild(el('h2', v.title));
        if (v.html) p.innerHTML = v.html; else p.textContent = v.text || '';
        card.appendChild(p);
        card.appendChild(row(v.buttons));
        (v.extra || []).forEach(function (x) { card.appendChild(x); });
        if (v.footer) card.appendChild(row(v.footer));
        panel.innerHTML = '';
        panel.appendChild(card);
    }
    btn.addEventListener('click', function (e) { e.preventDefault(); show('menu'); });

    function host () {
        S.role = 'host';
        S.myName = 'ARENA ' + (10 + Math.floor(Math.random() * 90));
        arenaLog('net', 'hosting', S.myName);
        api.host(S.myName);
        show('hosting');
    }
    function find () { S.role = 'guest'; arenaLog('net', 'looking for games'); api.find(); show('joining'); }
    function send (msg) { api.send(JSON.stringify(msg)); }
    function leave () {
        arenaLog('net', 'leaving', { view: S.view, inMatch: !!L });
        if (lastStatus === 'connected') send({ t: 'bye' });   // tell my friend before hanging up
        if (L) stopLockstep(false);
        api.stop();
        S.role = ''; S.myPick = ''; S.peerPick = ''; S.ready = { me: false, peer: false };
        show('off');
    }
    NET.leave = function () { leave(); click('Quit Button'); };
    NET.frame = function () { return L ? L.f : -1; };

    // ---- starting a match: the host sends the seed, the fighters and a copy of its game; both start together
    function maybeStart () {
        if (S.role !== 'host' || L) return;
        var fresh = S.view === 'pick' && S.myPick && S.peerPick;
        var again = S.view === 'after' && S.ready.me && S.ready.peer;
        if (!fresh && !again) return;
        var seed = Math.floor(Math.random() * 4294967295);
        rt().stopAll();
        var cfg = { seed: seed, host: S.myPick, guest: S.peerPick, stage: Number(get('Stage Pick')) || 0 };
        var snap = snapshot();
        arenaLog('net', 'starting match', { cfg: cfg, snapshotBytes: JSON.stringify(snap).length });
        send({ t: 'start', cfg: cfg, snap: snap });
        startLockstep('host', cfg, null);
    }
    function snapshot () {
        var out = [];
        rt().targets.forEach(function (t) {
            if (!t.isOriginal) return;
            var vs = {};
            Object.keys(t.variables).forEach(function (id) {
                var x = t.variables[id].value;
                vs[id] = x instanceof Array ? x.slice() : x;
            });
            out.push({ n: t.isStage ? '' : t.sprite.name, x: t.x, y: t.y, d: t.direction, s: t.size, c: t.currentCostume, vis: t.visible,
                       rs: t.rotationStyle, fx: Object.assign({}, t.effects), vars: vs });
        });
        return out;
    }
    function applySnapshot (snap) {
        snap.forEach(function (o) {
            var t = o.n === '' ? rt().getTargetForStage() : rt().getSpriteTargetByName(o.n);
            if (!t) return;
            if (!t.isStage) {
                t.setRotationStyle(o.rs);
                t.setXY(o.x, o.y, true);
                t.setDirection(o.d);
                t.setSize(o.s);
                t.setVisible(o.vis);
            }
            t.setCostume(o.c);
            Object.keys(o.fx || {}).forEach(function (k) { t.setEffect(k, o.fx[k]); });
            Object.keys(o.vars).forEach(function (id) {
                if (!t.variables[id]) return;
                var x = o.vars[id];
                t.variables[id].value = x instanceof Array ? x.slice() : x;
            });
        });
    }

    // ---- lockstep
    var L = null, saved = null;
    function seeded (seed) {
        var a = seed >>> 0;
        return function () {
            a = (a + 0x6D2B79F5) >>> 0;
            var t = a;
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }
    function startLockstep (role, cfg, snap) {
        arenaLog('lockstep', 'start as ' + role, cfg);
        var r = rt();
        var mine = {};
        KEEP.forEach(function (k) { mine[k] = get(k); });
        saved = { random: Math.random, now: Date.now, st: window.setTimeout, ct: window.clearTimeout, mine: mine };
        L = { role: role, cfg: cfg, f: 0, inputs: {}, hashes: {}, timers: [], tid: 1, passes: 0, acc: 0, last: performance.now(),
              clock: saved.now.call(Date), busy: false, waitSince: 0 };
        // identical starting point on both phones
        Math.random = seeded(cfg.seed);
        Date.now = function () { return L.clock; };
        window.setTimeout = function (fn, ms) {
            var args = Array.prototype.slice.call(arguments, 2), id = L.tid++;
            L.timers.push({ at: L.clock + (Number(ms) || 0), fn: fn, args: args, id: id });
            return id;
        };
        window.clearTimeout = function (id) { L.timers = L.timers.filter(function (t) { return t.id !== id; }); };
        r.frameLoop.stop();
        Object.defineProperty(r, 'redrawRequested', {
            configurable: true,
            get: function () { return L.passes++ > 0; },
            set: function (x) { if (!x) L.passes = 0; }
        });
        r.stopAll();
        if (snap) applySnapshot(snap);
        set('Sound On', mine['Sound On']);           // sound is up to each phone
        set('My Slot', role === 'host' ? 1 : 2);     // only changes which fighter this screen marks as "you"
        local = { 'Joy X': 0, 'Joy Y': 0, 'Fire Held': 0 };
        pulses = {};
        for (var f = 0; f < DELAY; f++) L.inputs[f] = { host: '0,0,0,0', guest: '0,0,0,0' };
        NET.active = true;
        NET.capture = true;
        r.greenFlag();
        S.ready = { me: false, peer: false };
        show('off');
        requestAnimationFrame(pump);
    }
    function encode () {
        var bits = 0;
        PULSES.forEach(function (p, i) { if (pulses[p]) bits |= 1 << i; });
        pulses = {};
        return [Math.round(local['Joy X'] * 100) / 100, Math.round(local['Joy Y'] * 100) / 100, local['Fire Held'] ? 1 : 0, bits].join(',');
    }
    function applyInputs (code, pre) {
        var p = code.split(',');
        set(pre + 'Joy X', Number(p[0]));
        set(pre + 'Joy Y', Number(p[1]));
        set(pre + 'Fire Held', Number(p[2]));
        var bits = Number(p[3]);
        PULSES.forEach(function (name, i) { if (bits & (1 << i)) set(pre + name, 1); });
    }
    function setup (f) {
        // the same opening moves on both phones: skip the intro, open BRAWL, pick the host's fighter
        var c = L.cfg;
        if (f === 2) rt().startHats('event_whenbroadcastreceived', { BROADCAST_OPTION: 'skip intro' });
        if (f === 6) click('Brawl Button');
        if (f === 10) {
            set('Net Players', 2);
            set('P2 Kind', c.guest);
            set('Stage Pick', c.stage);
            click('Pick ' + c.host.charAt(0).toUpperCase() + c.host.slice(1));
        }
    }
    function stateHash () {
        var parts = [list('B X'), list('B Y'), list('B Dmg'), list('B Stock')].map(function (l) {
            return l.map(function (x) { return Math.round(Number(x) * 10); }).join(',');
        });
        parts.push(Math.round(Number(get('Cam X')) * 10), get('Brawl Stage'), get('State'));
        var s = parts.join('|'), h = 0;
        for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
        return h;
    }
    var macro = (function () {
        var ch = new MessageChannel(), q = [];
        ch.port1.onmessage = function () { var fn = q.shift(); if (fn) fn(); };
        return function (fn) { q.push(fn); ch.port2.postMessage(0); };
    })();
    function frameReady () { var i = L.inputs[L.f]; return i && i.host !== undefined && i.guest !== undefined; }
    function doFrame (done) {
        // 1. my buttons for a few frames ahead go to my friend (and to me)
        var mine = encode(), ahead = L.f + DELAY;
        L.inputs[ahead] = L.inputs[ahead] || {};
        L.inputs[ahead][L.role] = mine;
        send({ t: 'in', f: ahead, d: mine });
        // 2. both players' buttons for this frame go into the game
        var inp = L.inputs[L.f];
        applyInputs(inp.host, '');
        applyInputs(inp.guest, 'P2 ');
        setup(L.f);
        // 3. the clock moves one frame; timers that are due fire
        L.clock += FRAME;
        var due = L.timers.filter(function (t) { return t.at <= L.clock; });
        L.timers = L.timers.filter(function (t) { return t.at > L.clock; });
        due.forEach(function (t) { try { t.fn.apply(null, t.args); } catch (e) {} });
        // 4. let promises settle, then run one frame of the game
        macro(function () {
            if (!L) return;   // left the match in the meantime
            rt()._step();
            if (!L) return;
            delete L.inputs[L.f];
            if (L.f % 30 === 0) {
                var h = stateHash();
                L.hashes[L.f] = L.hashes[L.f] || {};
                L.hashes[L.f].me = h;
                send({ t: 'hash', f: L.f, h: h });
                checkHash(L.f);
            }
            L.f++;
            if (get('State') === 'over') { matchOver(); return; }
            done();
        });
    }
    function checkHash (f) {
        var h = L && L.hashes[f];
        if (!h || h.me === undefined || h.peer === undefined) return;
        if (h.me !== h.peer) {
            arenaLog('lockstep', 'OUT OF STEP at frame ' + f, { mine: h.me, friend: h.peer, state: get('State') });
            send({ t: 'desync', f: f });
            stopLockstep(false);
            click('Quit Button');
            show('message', 'The two phones got out of step, so the match stopped. Sorry! Tap PLAY A FRIEND to try again.');
            return;
        }
        delete L.hashes[f];
    }
    function pump (now) {
        if (!L) return;
        pollNet();   // the friend's buttons, every frame
        if (!L) return;
        L.acc = Math.min(L.acc + (now - L.last), 6 * FRAME);
        L.last = now;
        if (!L.busy) {
            var steps = 0;
            var next = function () {
                if (!L) return;
                if (L.acc < FRAME || steps >= 3) { L.busy = false; return; }
                if (!frameReady()) {
                    L.busy = false;
                    if (!L.waitSince) L.waitSince = now;
                    if (now - L.waitSince > 1000 && !L.stallLogged) {
                        L.stallLogged = true;
                        arenaLog('lockstep', 'waiting over 1 s for my friend (no buttons yet)', { frame: L.f });
                    }
                    return;
                }
                if (L.stallLogged) arenaLog('lockstep', 'friend caught up', { frame: L.f, waitedMs: Math.round(now - L.waitSince) });
                L.waitSince = 0;
                L.stallLogged = false;
                steps++;
                L.acc -= FRAME;
                doFrame(next);
            };
            L.busy = true;
            next();
        }
        requestAnimationFrame(pump);
    }
    function matchOver () {
        var won = Number(get('Brawl Winner')) === Number(get('My Slot'));
        arenaLog('lockstep', 'match over', { frame: L && L.f, winner: get('Brawl Winner'), mySlot: get('My Slot'), won: won });
        stopLockstep(true, won);
        show('after', won ? 'YOU WIN! 🏆' : 'GOOD GAME!');
    }
    function stopLockstep (finished, won) {
        if (!L) return;
        arenaLog('lockstep', 'stop', { frame: L.f, finished: !!finished, won: !!won });
        var r = rt();
        var timers = L.timers, mine = saved.mine;
        Math.random = saved.random;
        Date.now = saved.now;
        window.setTimeout = saved.st;
        window.clearTimeout = saved.ct;
        delete r.redrawRequested;
        r.redrawRequested = false;
        L = null;
        NET.active = false;
        NET.capture = false;
        set('Net Players', 0);
        set('My Slot', 1);
        // my own saved progress comes back (the match used the host's), plus XP if I won
        KEEP.forEach(function (k) { set(k, mine[k]); });
        if (finished && won) { set('XP Gain', 2); r.startHats('event_whenbroadcastreceived', { BROADCAST_OPTION: 'gain xp' }); }
        timers.forEach(function (t) { window.setTimeout.apply(null, [t.fn, 0].concat(t.args)); });
        r.frameLoop.start();
    }

    // ---- messages from the friend's phone
    function receive (m) {
        if (m.t === 'hello') {
            arenaLog('net', 'friend says hello', { version: m.v, name: m.name });
            if (m.v !== get('Game Version')) {
                leave();
                show('message', 'Both phones need the same version of the game (yours is v' + get('Game Version') + ', your friend\\'s is v' + m.v + ').');
                return;
            }
            S.peer = m.name || 'friend';
        } else if (m.t === 'pick') {
            S.peerPick = m.kind;
            if (S.view === 'pick') draw();
            maybeStart();
        } else if (m.t === 'start' && S.role === 'guest') {
            arenaLog('net', 'host started the match', m.cfg);
            S.myPick = m.cfg.guest;
            rt().stopAll();
            startLockstep('guest', m.cfg, m.snap);
        } else if (m.t === 'in' && L) {
            L.inputs[m.f] = L.inputs[m.f] || {};
            L.inputs[m.f][L.role === 'host' ? 'guest' : 'host'] = m.d;
        } else if (m.t === 'hash' && L) {
            L.hashes[m.f] = L.hashes[m.f] || {};
            L.hashes[m.f].peer = m.h;
            checkHash(m.f);
        } else if (m.t === 'again') {
            S.ready.peer = true;
            if (S.view === 'after') draw();
            maybeStart();
        } else if (m.t === 'desync' && L) {
            arenaLog('lockstep', 'friend reports OUT OF STEP', { frame: m.f });
            stopLockstep(false);
            click('Quit Button');
            show('message', 'The two phones got out of step, so the match stopped. Sorry! Tap PLAY A FRIEND to try again.');
        } else if (m.t === 'bye') {
            arenaLog('net', 'friend left');
            var was = !!L;
            if (L) stopLockstep(false);
            api.stop();
            S.role = '';
            if (was) click('Quit Button');
            show('message', 'Your friend left the game.');
        }
    }
    function pollNet () {
        var lines = api.poll();
        if (lines) lines.split('\\n').forEach(function (l) {
            if (!l) return;
            try { receive(JSON.parse(l)); } catch (e) {}
        });
    }
    var lastStatus = 'idle';
    setInterval(function () {
        pollNet();
        var st = {};
        try { st = JSON.parse(api.state()); } catch (e) {}
        if (st.status !== lastStatus) {
            arenaLog('net', 'connection ' + lastStatus + ' -> ' + st.status, st.error || undefined);
            if (st.status === 'connected') {
                send({ t: 'hello', v: get('Game Version'), name: S.myName || 'friend' });
                S.myPick = ''; S.peerPick = '';
                show('pick');
            } else if (st.status === 'lost' && S.role) {
                if (L) { stopLockstep(false); click('Quit Button'); }
                S.role = '';
                show('message', 'Lost the connection to your friend.');
            }
            lastStatus = st.status;
        }
        if (S.view === 'joining' || S.view === 'connecting') draw();
        // the WI-FI button sits on the BRAWL fighter screen
        var onSelect = get('State') === 'select' && get('Mode') === 'brawl' && !L;
        btn.style.display = onSelect && S.view === 'off' ? 'block' : 'none';
    }, 250);
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

    // (the game fills the whole screen under the controls: see LAYOUT_JS)

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
    function set (name, value) {
        if (window.NET && NET.take(name, value)) return;   // Wi-Fi play: the lockstep engine sends it
        var x = v(name); if (x) x.value = value;
    }
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
    o.custom.js = LOG_JS + SAVE_JS + LAYOUT_JS + EXT_JS + HUD_JS + NET_JS + PAD_JS;
    const result = await packager.package();
    fs.mkdirSync(path.dirname(OUT), {recursive: true});
    fs.writeFileSync(OUT, result.data);
    console.log(`wrote ${path.relative(process.cwd(), OUT)} (${Math.round(result.data.length / 1024)} KB)`);
})().catch(e => {
    console.error(e);
    process.exit(1);
});
