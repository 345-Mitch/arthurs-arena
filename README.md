# arthurs-arena

Arthur's stickman fighting game, built in Scratch, with an Android tablet in mind.

## Arthur's Arena: Legends (newest)

`projects/arthurs-arena-legends.sb3` is the full game:

- **ADVENTURE mode**: stage after stage of small enemies (grunts, ninjas, small robots), then a boss, then on to the next stage, with tougher laps after the last.
- **BRAWL mode** (like a platform fighter): four fighters at once on stages with platforms and ramps, a camera that follows and zooms, damage %, knock-outs and lives.
- **Power levels 1 to 5**: win fights to level up. You get a new aura colour (red, orange, gold, blue, purple-white) and a new POWER move: FLAME DASH, then lightning strikes from the sky. Enemies and bosses get stronger with you, and bosses call down lightning too.
- **Levels**: EASY, NORMAL, HARD and CHAMPION. NORMAL makes fights about twice as long as before.
- **A paper intro**: a pencil draws the fighters and a ninja on notebook paper, then colours them in (with a SKIP button).
- **Dragon Ball-style power-ups**: yelling, a surging aura, shaking ground, cracks, a shockwave and boulders ripping out of the ground (more every level), and golden (then silver) super-form hair from power level 3.
- **BRAWL stages**: 14 to pick from, including a Pirate Ship with cannonballs, low-gravity Space, slippery Snowy Peak, bouncy Candy Land, conveyor-belt Robot Factory, a Jungle with a vine swing and coconuts, Dino Valley where you ride an armoured T-Rex, a Highway with trucks, and a Fishing Pond with a floating raft and jumping fish.
- **Extras from Grok's plan**: healing apples, sound on/off, a how-to-play card, PRACTICE mode and a debug overlay.
- **Ninjas**: a Bamboo Forest full of ninjas and the boss MASTER KAGE, who teleports in smoke and sends a squad of ninjas at you.
- **Human-like stick fighters**: bending elbows and knees, walking and breathing, wind-up punches, bodies that fold when hit, and shadows.
- **Story mode**: nine chapters to win back the Golden Crown from the Shadow King, with talking scenes you can skip.
- **Arcade mode**: endless waves that get harder, with a score and a best score.
- **Three fighters**: Arthur, Nova and Rocko, each with their own speed, power, health and SUPER move.
- **Moves**: punch, kick, jump and a double jump with a front flip, a spinning WHIRLWIND KICK (tap KICK twice), a HELICOPTER KICK (tap KICK twice in the air), hold-to-charge METEOR PUNCH and SKY KICK, air attacks, dodge, combos, a SUPER meter, perfect dodges, and a **fireball** you hold to charge up.
- **Spiky enemies and bosses**: Spike Bot, the giant **MEGA SPIKE** boss (Spike Roll, spike shots and Spike Rain), and a Shadow King who grows Spike Armor. Punching spikes hurts!
- **Weapons** fall into the arena: a sword, a hammer, a boomerang, a spear, nunchucks and a shield that blocks. Each one breaks after a few uses.
- Beat Story mode to unlock the **Golden Crown** for every fighter.

`LEGENDS.md` is the guide: how to play, every fighter, enemy and weapon, and easy remixes. `projects/LEGENDS_BLOCKS.md` lists every block.

Open it in the [Scratch editor](https://scratch.mit.edu/projects/editor/) with **File → Load from your computer**, then click the green flag.

**On Android:** install `dist/arthurs-arena.apk`. `ANDROID.md` shows how. `dist/arthurs-arena.html` is the same game as a web page for any browser.

## The boss arena

`projects/arthurs-arena-bosses.sb3` is the earlier, smaller game with Brute, Ivy and Quake. `BOSSES.md` explains it, and `projects/BLOCK_LISTING.md` lists every block.

## Building and testing

Both projects are made by Python scripts in `tools/`, so they can be rebuilt any time:

```bash
python3 tools/build_legends_sb3.py
python3 tools/build_bosses_sb3.py
```

`tools/test_legends.js` plays the Legends project in Scratch's own engine. See `LEGENDS.md` for how to run it.

The original template is [Stickman Battle](https://scratch.mit.edu/projects/732904827) by onigirikun_2009. `STARTER_GUIDE.md` is the longer plan. `CODEX_REVIEW.md` records the review notes from 2026-11-03.
