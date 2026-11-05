# arthurs-arena

Arthur's stickman fighting game, built in Scratch, with an Android tablet in mind.

## Arthur's Arena: Legends (newest)

`projects/arthurs-arena-legends.sb3` is the full game:

- **Story mode**: five chapters to win back the Golden Crown from the Shadow King, with talking scenes you can skip.
- **Arcade mode**: endless waves that get harder, with a score and a best score.
- **Three fighters**: Arthur, Nova and Rocko, each with their own speed, power, health and SUPER move.
- **Moves**: punch, kick, jump, air attacks, dodge, combos, a SUPER meter, and perfect dodges.
- **Weapons** fall into the arena: a sword, a hammer and a boomerang. Each one breaks after a few uses.
- Beat Story mode to unlock the **Golden Crown** for every fighter.

`LEGENDS.md` is the guide: how to play, every fighter, enemy and weapon, and easy remixes. `projects/LEGENDS_BLOCKS.md` lists every block.

Open it in the [Scratch editor](https://scratch.mit.edu/projects/editor/) with **File → Load from your computer**, then click the green flag.

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
