# Arthur's Arena: Legends

Written 2026-11-05 for Arthur.

This is the big version of Arthur's Arena. It has a **Story** with five chapters, an **Arcade** mode that never ends, three fighters to pick from, falling weapons, combos, and a SUPER move.

The playable file is `projects/arthurs-arena-legends.sb3`. The boss game from before (`projects/arthurs-arena-bosses.sb3`, see `BOSSES.md`) is still there.

## Load it

1. Open the [Scratch editor](https://scratch.mit.edu/projects/editor/).
2. Choose **File**, then **Load from your computer**.
3. Pick `projects/arthurs-arena-legends.sb3`.
4. Click the green flag.

On the tablet, the file has to be on the Scratch website first. Sign in, load the file, and save it. Then open that project's link in the tablet browser.

## The story

> The Shadow King stole the Golden Crown of the Arena! Win it back, champion!

| Chapter | Where | Who you fight | How to beat them |
| --- | --- | --- | --- |
| 1 | The Training Yard | **Rival** | He walks up and punches. Punch back! |
| 2 | Ivy's Woods | **Ivy** | She shouts **Low!** or **High!** before she throws. Jump the low shots. Stay down for the high ones. |
| 3 | The Rocky Pass | **Brute** | He says **Ready?**, then charges where you are standing. Move or DODGE. |
| 4 | The Volcano Gate | **Quake** | He shouts **STOMP!** and sends a wave along the ground. Jump over it. |
| 5 | Shadow Castle | **The Shadow King** | He uses all of those tricks. At half health he gets **angry**: he gets faster and throws two shots. |

Before each fight there is a chapter card, and then the hero and the enemy talk. Tap **SKIP** if you just want to fight.

Win chapter 5 and the Golden Crown drops onto your fighter's head. After that, **every fighter wears the crown** in every fight. Save the project to keep it.

If you get knocked out, tap **RETRY** to try the same chapter again. You get full health, and the talking is skipped.

## Arcade

Fight wave after wave until you get knocked down.

- Waves 1 to 4 are Rival, Ivy, Brute and Quake. Every 5th wave is the Shadow King.
- Every wave, enemies get more health, hit a little harder, and attack faster.
- Clearing a wave gives you back 30 health.
- **Score** goes up for every hit, for combos, for perfect dodges and for every wave. **Best** is your top score. It shows on the title screen.

## Pick your fighter

| Fighter | Good at | Health | Steps | Punch | Kick | SUPER move |
| --- | --- | --- | --- | --- | --- | --- |
| **Arthur** (blue, red headband) | Everything | 100 | 22 | 5 | 8 | **HERO SLASH**: zooms in for one big 18 hit |
| **Nova** (pink, gold star) | Speed | 80 | 32 | 4 | 7 | **STAR DASH**: three quick dash kicks of 5 each |
| **Rocko** (green, spiky hair) | Power and health | 130 | 15 | 7 | 10 | **ROCK SLAM**: jumps up and slams down for 22 and shakes the ground |

Each fighter says their own line before **READY... FIGHT!**

## Buttons

The buttons are along the bottom of the screen.

| Button | Keyboard | What it does |
| --- | --- | --- |
| ◀ LEFT / RIGHT ▶ | arrows | Step. **Hold** the button to keep walking. |
| JUMP | up arrow or space | Jump. You can punch and kick in the air. |
| DODGE | C | Hop backwards and turn see-through. Nothing can hurt you while you dodge. |
| PUNCH | Z | Quick hit. With a boomerang, PUNCH throws it. |
| KICK | X | Steps in and hits harder. |
| SUPER | V | Your fighter's SUPER move. It works when the button is gold and you are on the ground. |
| ✕ (top middle) | | Go back to the title. |

You always turn to face the enemy, so you can fight from either side.

## Cool moves

- **Combos.** Hit again within about a second to keep a combo going. Every 3rd hit in a row shows **COMBO x3!** (then x6, x9 ...) and does 3 extra damage.
- **SUPER meter.** The thin bar under your health fills when you land hits or get hurt. When it is full it flashes, the SUPER button turns gold, and you see **SUPER READY!** You can't be hurt during your SUPER.
- **Perfect dodge.** If you DODGE just as an attack would have hit you, you see **PERFECT DODGE!** You take no damage, a big chunk of SUPER fills up, and you get 100 points. Try it when Brute charges!
- **Tap ahead.** If you tap PUNCH while a kick is still going, the punch happens right after. Big fighting games call this an input buffer.

## Weapons

Every few seconds a glowing weapon falls from the sky. Walk over it to pick it up. You can only hold one at a time, and each one breaks after a few swings. **Oh no! The sword broke!**

| Weapon | Extra damage | Reach | Uses | Special |
| --- | --- | --- | --- | --- |
| Sword | +4 | Long | 10 swings | Hits from further away |
| Hammer | +9 | A bit longer | 5 swings | Every hit shakes the ground |
| Boomerang | hits for 7 | Across the arena | 6 throws | PUNCH throws it. It flies out, hits, and comes back to your hand |

## Easy remixes

All the fighter numbers are in the **Stage**, in the script `when I receive [hero picked]`. All the enemy numbers are in the Stage script `when I receive [load enemy]`. Change a number, click the green flag, and play.

- Make Arthur stronger: change his `set [Punch Power] to [5]` to `[7]`.
- Make the Shadow King easier: change his `set [Enemy Max] to [90]` to `[60]`.
- Make weapons fall more often: in the **Weapon Drop** sprite, change `wait (pick random [3] to [7])` to `[2] to [4]`.
- Make your own catchphrase: in the **Hero** sprite, `when I receive [fighters ready]`, change `say [I'm Arthur!]`.
- Draw a new fighter: costumes are named `arthur idle`, `arthur punch` and so on. Paint over them in the Costumes tab.

`projects/LEGENDS_BLOCKS.md` lists every script in every sprite, so you can find any block.

## Notes for Mitch

The `.sb3` and the block listing are built by a script, so they can be remade any time:

```bash
python3 tools/build_legends_sb3.py
```

The script checks the project before it writes it. It checks that every costume, backdrop, sound, variable and message exists, and that every message that is sent is also received.

`tools/test_legends.js` plays the built project in Scratch's own engine (scratch-vm), with no screen and a fake clock. A bot finishes Story mode with each of the three fighters and plays Arcade for six minutes. Then the test mashes every button at once and checks each weapon hits and breaks. It also checks that nothing gets stuck: Hero locked, the boomerang never returning, health out of range, the Quit, Retry and Home buttons.

```bash
npm install --prefix /tmp/scratch-tools scratch-vm
NODE_PATH=/tmp/scratch-tools/node_modules node tools/test_legends.js
```

How it is built:

- **Buttons never start long scripts.** In Scratch, a broadcast restarts a script that is already running. Two quick taps could leave a "busy" flag stuck on for the rest of the fight. So the buttons only set `Want Punch`, `Want Kick` and so on, and two loops in the Hero sprite act on them. LEFT and RIGHT still broadcast, because a step has no wait in it.
- **Hits use distance, not "touching".** Every hit checks how far apart the two fighters are. That works the same on every device, and it can be tested without a screen.
- **Hurt and stun use timestamps, not waits.** `Enemy Stun Until` and `Hero Safe Until` hold a `timer` value, so a hit that arrives mid-wait cannot break anything.
- Sounds are small beeps and thumps made by the build script, so there are no outside files.
- The main scripts have comments in the editor that explain what they do.
