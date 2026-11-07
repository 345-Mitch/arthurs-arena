---
name: game-developer
description: How to change Arthur's Arena (the Scratch stickman fighter built by Python scripts, packaged as an offline web page and an Android app). Use for any game feature, fix, art or build work in this repository.
---

# Game developer guidelines for Arthur's Arena

Work like an experienced game developer on a game a child plays every day.

## Principles

- **KISS and YAGNI.** Build what was asked, in the simplest way that works on a phone. No speculative options or frameworks. Don't rewrite working code just for style.
- **Single responsibility.** Each script, sprite, page module or Java class does one job. If a change needs a second job, add a second piece rather than growing the first.
- **State pattern for anything with modes.** When behaviour depends on "what is happening now" (screens, connection, a boss's phases, a move with wind-up/active/recovery), keep one state variable and one handler per state, with clear transitions. Avoid long `if … else if …` chains and boolean flag tangles. Example: the Wi-Fi panel in `tools/package_html.js` (`S.view` + `VIEWS[state]`).
- **Log the critical points.** Connections, match start/stop, out-of-step checks, layout changes, saves, anything that can fail on a real device. Keep logs short and data-rich; don't log every frame.
- **English everywhere,** with brief, clear comments that explain *why* (kid-readable where the block listing shows them).
- **Modular and easy to maintain.** Constants at the top of the builder, helpers for repeated patterns, no copy-paste of near-identical blocks.

## Where things live

| Piece | File | Notes |
| --- | --- | --- |
| The game (Scratch project) | `tools/build_legends_sb3.py` | Python DSL → `projects/arthurs-arena-legends.sb3` and `projects/LEGENDS_BLOCKS.md`. `VERSION` at the top. |
| Web page modules | `tools/package_html.js` | One string per job, joined in `o.custom.js`: `LOG_JS` (logger), `SAVE_JS`, `LAYOUT_JS`, `EXT_JS` (scenery beyond the stage), `HUD_JS` (top bar), `NET_JS` (Wi-Fi play), `PAD_JS` (touch controls). |
| Android app | `android/` + `tools/build_android.py` | `MainActivity.smali` (the WebView), `android/java/.../ArenaNet.java` (Wi-Fi), `android/stubs` (compile-time stand-ins). `VERSION_CODE`/`VERSION_NAME` in the build script. |
| Tests | `tools/test_legends.js`, `tools/test_wifi.js` | Headless scratch-vm with a fake clock; Playwright for the packaged page. |

## Scratch rules this project depends on

- Buttons only set `Want …` variables; loops act on them (a broadcast restarts a running script).
- Hits use distance, not "touching". Hurt/stun use timestamps, not waits.
- Per-frame loops over fighters/platforms go in custom blocks run without screen refresh (`B.define`/`call`).
- Any sprite that clones checks `Is Clone` first (the builder's validator enforces it, along with unique variable ids, costume names and blocks).
- Wi-Fi play is lockstep: nothing that changes game state may depend on the real clock, `Math.random` outside the seeded one, or which phone you are (`My Slot` is visual only).

## Logging

- Page: `arenaLog(area, message, data)`; the last 200 lines are kept in `window.ARENA_LOG` (read them with `chrome://inspect` on a connected phone). Areas in use: `layout`, `net`, `lockstep`.
- Android: `android.util.Log` with tag `ArenaNet` (`adb logcat -s ArenaNet`).
- Tests check the important lines exist (`tools/test_wifi.js`).

## Done means

1. `python3 tools/build_legends_sb3.py` (the validator must pass).
2. Relevant tests, then the full suite: `NODE_PATH=/tmp/scratch-tools/node_modules node tools/test_legends.js` (`ONLY=part` for one part); `node tools/test_wifi.js <page.html>` for page/Wi-Fi changes.
3. Look at real screenshots (Playwright, `--use-gl=swiftshader`) for anything visual, on a tablet, a long phone and a squarish screen.
4. Update `LEGENDS.md` / `README.md` / `ANDROID.md`, bump `VERSION`, `VERSION_CODE`, `VERSION_NAME`.
5. `NODE_PATH=/tmp/scratch-tools/node_modules python3 tools/build_android.py`, commit, push, send the APK.
