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
    var KEEP = ['Best', 'Crown'];
    function stageVars () {
        var stage = vm.runtime.getTargetForStage && vm.runtime.getTargetForStage();
        if (!stage) return null;
        var out = {};
        Object.keys(stage.variables).forEach(function (id) {
            var v = stage.variables[id];
            if (KEEP.indexOf(v.name) !== -1) out[v.name] = v;
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
            return;
        }
        var changed = false;
        KEEP.forEach(function (name) {
            if (vars[name] && Number(vars[name].value) > Number(saved[name] || 0)) {
                saved[name] = Number(vars[name].value);
                changed = true;
            }
        });
        if (changed) {
            try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
        }
    }, 1000);
})();
`;

(async () => {
    const loaded = await Packager.loadProject(fs.readFileSync(SB3));
    const packager = new Packager.Packager();
    packager.project = loaded;
    const o = packager.options;
    o.autoplay = true;               // no green flag to tap: the title shows straight away
    o.framerate = 30;
    o.resizeMode = 'preserve-ratio';
    o.appearance.background = '#000000';
    o.appearance.accent = '#facc15';
    o.loadingScreen.text = "Arthur's Arena";
    o.app.windowTitle = "Arthur's Arena";
    o.app.packageName = 'arthurs-arena';
    o.cloudVariables.mode = 'local';
    o.custom.js = SAVE_JS;
    const result = await packager.package();
    fs.mkdirSync(path.dirname(OUT), {recursive: true});
    fs.writeFileSync(OUT, result.data);
    console.log(`wrote ${path.relative(process.cwd(), OUT)} (${Math.round(result.data.length / 1024)} KB)`);
})().catch(e => {
    console.error(e);
    process.exit(1);
});
