# Arthur's Arena — 10 UI and debugging features

Written 2026-11-03 for Mitch and Arthur.

This is a plan for the Scratch game [Stickman Battle](https://scratch.mit.edu/projects/732904827) (project 732904827 by onigirikun_2009). The starter guide renames the hero Arthur and the title to **Arthur's Arena**. This file does not change the Scratch project. It says what to build, in blocks a kid can follow.

Open the project and click **See inside**. Names in the project are a mix of Japanese and English. Each Japanese name below has a short English meaning next to it.

Big text, big buttons, kind messages, and a debug screen Mitch can turn on. Those are the rules for every feature.

## The 10 features

1. **Colour health bars** — Arthur's bar and the enemy bar turn green, then yellow, then red, and a big number shows the health.
2. **Hit flash** — The stickman flashes when he gets hurt, so a hit is obvious.
3. **Screen shake** — Heavy hits and boss attacks nudge the fighters, and the buttons stay still.
4. **Sound on/off** — A big speaker button mutes the game, and the choice can be written into the save code Scratch already uses.
5. **How to play** — A big overlay with three icons: move, punch, and kick.
6. **Missing-picture fallback** — If the hero costume is the wrong one, show a plain stickman and a friendly sentence.
7. **Debug overlay** — A button shows a loops-per-second count, health, gold, and the current state.
8. **Try-again countdown** — After a loss, a big prompt counts down from 5 and then restarts the fight.
9. **Tap zones** — Only taps inside the button boxes punch, kick, or move. Other taps do nothing.
10. **Version line** — The home screen shows **Arthur's Arena v0.2** so Mitch can see which build is open.

Implementation steps for each feature come in the sections below.
