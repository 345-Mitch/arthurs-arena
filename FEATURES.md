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

The template already shakes the screen and already has boss fights. Feature 3 reuses that. `origin/grok/bosses` was not on the remote on 2026-11-03, so the boss notes below use the bosses already inside project 732904827. When a new boss branch adds sprites, use the same three hooks: colour the enemy bar from `敵:体力`, broadcast `大揺れ` on the heavy attack, and set `CurrentState` to `boss`.

Bosses already in the template:

| Sprite | English | Start message | Attack messages | Backdrop |
| --- | --- | --- | --- | --- |
| `魔王敵` | Demon King | `ステージ魔王` | `魔敵技`, `魔敵技2`, `魔滴技3` | `魔王` |
| `炎敵` | flame boss | `ステージ炎` | `炎敵技`, `炎敵技２` | `炎` |
| `暴走敵` | berserk boss | `ステージ暴走` | `暴敵技`, `暴敵技2` | `暴走` |

Arthur's health variable is `自分:体力`. The shared enemy and boss health variable is `敵:体力`. Arthur's max health for the current power-up level is `現在の体力` (the fight script copies it into `自分:体力` when it receives `ステージかいし`).

## 1. Colour health bars

Arthur's bar and the enemy bar turn green, then yellow, then red, and a big number shows the health.

The sprite named `体力バー` is a bad place for this. Its blocks are part of the save code, not a drawing of a bar. The numbers Arthur already sees are the digit sprites `体力1桁目` through `体力4桁目` (Arthur) and `敵　体力1桁目` through `敵　体力4桁目` (enemy). Keep those. Add two new sprites for the colour.

Health in this game is not "out of 100". Arthur's max grows with power-ups (`現在の体力` is set to 50, then 60, then on up past 1000). Boss health is set on the Stage to numbers like 5000, 7000, and 8200. Colour uses a percent of the max, so the Demon King bar stays green at the start of the fight.

**Sprites:** new `ArthurBar`, new `EnemyBar`. Leave the digit sprites as they are.

**Variables:** `自分:体力`, `現在の体力`, `敵:体力`, new `ArthurMax`, new `EnemyMax`, new `BarPercent`.

**Messages:** `ステージかいし` (fight start), `ステージ魔王`, `ステージ炎`, `ステージ暴走`, `勝利` (win), `敗北` (loss).

**Blocks:**

1. On `ArthurBar`, draw three costumes: a thick rectangle named `green`, `yellow`, and `red`. Put the costume centre on the **left** edge so the bar grows to the right. Do the same for `EnemyBar`.
2. When I receive `ステージかいし`: `set ArthurMax to 現在の体力`. `if ArthurMax < 1 then set ArthurMax to 1` (this stops a divide-by-zero if a fight starts before max health is set). `show`, `go to front layer`, `go to x: -160 y: 150`, `set size to 40%` as the starting height.
3. `forever` on `ArthurBar`: `set BarPercent to ((自分:体力 / ArthurMax) * 100)`. `if BarPercent > 100 then set BarPercent to 100`. `if BarPercent < 0 then set BarPercent to 0`. `if BarPercent > 60 then switch costume to green`, `else if BarPercent > 30 then switch costume to yellow`, `else switch costume to red`. Then `set size to BarPercent`. The left-centred costume keeps the bar glued to the left while the length changes.
4. On the Stage, at the start of each fight (the same scripts that `set 敵:体力` to 140, 270, 400, 500, 1000, 5000, 7000, or 8200), add `set EnemyMax to 敵:体力`. Do this **before** any hit subtracts health. `EnemyBar` uses `敵:体力 / EnemyMax` the same way as step 3, sitting at `x: 40 y: 150`.
5. When I receive `ステージ魔王` or the backdrop switches to `魔王`: `EnemyBar` `says Boss` for 2 seconds in big text (`set size to 150%` on a small label sprite, or a costume that says BOSS). The bar itself still follows `敵:体力`.
6. When I receive `勝利` or `敗北`: `hide` both bars, matching `自分体力` and `敵体力`, which already hide on those messages.
7. The digit sprites stay the numeric readout. If they are hard to read on the tablet, `set size to 200%` on `体力1桁目` through `体力4桁目` and the four enemy digit sprites when the fight starts.

## 2. Hit flash

The stickman flashes when he gets hurt, so a hit is obvious.

A hit already broadcasts `いてっ` (ouch) and subtracts `Enemy Attack Strength` from `自分:体力`. The hero, the enemies, and the bosses already listen for `揺れ`. Flash is a separate, short colour blink so it still reads on a white stickman.

**Sprites:** `主人公` (Arthur), and the fighter who got hit: `敵1`, `敵2`, `敵3`, `敵4`, `敵5`, `炎敵`, `暴走敵`, `魔王敵`.

**Variables:** `自分:体力`, `敵:体力`. No new variable.

**Messages:** `いてっ`. New message `敵いてっ` for when the enemy or boss loses health.

**Blocks:**

1. On `主人公`, `when I receive いてっ`: `set color effect to 40`, `wait 0.1 seconds`, `set color effect to 0`. Keep this script short. The old `いてっ` scripts should keep doing what they already do.
2. Find the scripts that already `change 敵:体力 by` a minus, or `set 敵:体力` to a smaller number, on the punch and kick path (`when I receive パンチ` and `when I receive キック` on `主人公`, and the hit checks on the enemy sprites). After the health goes down, `broadcast 敵いてっ`.
3. On each enemy sprite and on `魔王敵`, `炎敵`, and `暴走敵`, `when I receive 敵いてっ`: same colour blink as step 1. `if 敵:体力 < 1 then set color effect to 0` so a defeated boss does not stay pink.
4. Do not use the ghost effect for the flash. This project already sets ghost to 100 to hide punches and buttons. A ghost flash looks like the stickman vanished.

## 3. Screen shake

Heavy hits and boss attacks nudge the fighters, and the buttons stay still.

Scratch has no camera. The project already fakes a shake: `when I receive 揺れ` (shake) on `主人公`, `地面` (the ground), the enemy sprites, `炎敵`, `暴走敵`, and `魔王敵` does `change y by`, `wait`, then `change y by` the other way. Copy that pattern. Do not reuse `揺れ2`: that message drives the energy-wave sprite `波動`, and mixing a camera shake into it would move the wave.

**Sprites:** the same ones that already receive `揺れ`: `主人公`, `地面`, `敵1` through `敵5`, `炎敵`, `暴走敵`, `魔王敵`. Do not put the shake on `ガードボタン`, `剣ボタン`, `戦闘ボタン`, or `ホームボタン`. A shaking button is a missed tap.

**Variables:** `Enemy Attack Strength`.

**Messages:** existing `揺れ`. New `大揺れ` (big shake). Boss attacks that should send it: `魔敵技`, `魔敵技2`, `魔滴技3`, `炎敵技`, `炎敵技２`, `暴敵技`, `暴敵技2`.

**Blocks:**

1. On `主人公`, duplicate the `when I receive 揺れ` script. Change the hat to `when I receive 大揺れ`. In the copy, `change y by 12`, `wait 0.05 seconds`, `change y by -12`, and `repeat` that 4 times. The normal `揺れ` script stays the small one.
2. Copy that same `大揺れ` script onto `地面` and onto each enemy and boss sprite that already has a `揺れ` script. Each sprite wiggles itself. That is the pattern the project already uses.
3. On the boss sprites, inside `when I receive 魔敵技`, `魔敵技2`, `魔滴技3`, `炎敵技`, `炎敵技２`, `暴敵技`, and `暴敵技2`, add `broadcast 大揺れ` at the moment the attack costume starts.
4. Where Arthur already gets hurt (the `touching color` checks on `主人公` that `broadcast 揺れ`), add `if Enemy Attack Strength > 30 then broadcast 大揺れ else broadcast 揺れ`. A small hit stays a small shake. A boss hit is the big one.
5. After the repeats, `set y to` the y the sprite had at the start of the shake (store it in a variable like `ShakeHomeY` on that sprite first). A cancelled fight should not leave the ground crooked.
