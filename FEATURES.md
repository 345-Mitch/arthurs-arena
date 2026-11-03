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

## 4. Sound on/off

A big speaker button mutes the game, and the choice can be written into the save code Scratch already uses.

Plain Scratch has no local storage. A normal variable forgets its value when the green flag starts, because the flag loads the value saved in the project. There is no block for cookies, files, or the tablet's storage.

A cloud variable can store this, with hard limits. Cloud variables hold numbers only (0 and 1 are fine, the word "off" is not). They need a Scratcher account, they need the internet, and they are shared by everyone looking at the project. One public `☁ SoundOn` would mute the game for every player at once. Offline on the tablet, the cloud value does not update. That is a poor fit for Arthur's home tablet.

The realistic place to remember the choice is the save code this game already teaches: press **Save**, copy the code, and type it in on **Load** (`セーブ` and `ロード` sprites, list `セーブする`). Add one extra digit. Old codes that do not have the digit still load.

**Sprites:** new `SoundButton` (two costumes, `on` and `off`, a big speaker). Existing `音楽` (plays `魔王魂  ファンタジー10` in a `forever` loop after `ゲームスタート` and sets volume to 70 or 0). Existing `セーブ` and `ロード`.

**Variables:** new `SoundOn` (1 or 0). The project already uses `セーブ` and `答え　数` while loading.

**Messages:** `ゲームスタート`, `戦闘開始`, `勝利`, `敗北`. Those are the messages where `音楽` already runs `set volume to`.

**Blocks:**

1. Make `SoundButton` large (`set size to 150%` or bigger) and park it in a corner on every screen: `when green flag clicked` → `show`, `go to front layer`, `go to x: 200 y: 160`.
2. `when this sprite clicked`: `if SoundOn = 1 then set SoundOn to 0 else set SoundOn to 1`. `if SoundOn = 1 then switch costume to on` and `set volume to 70`. `else switch costume to off`, `set volume to 0`, `stop all sounds`.
3. On `音楽`, at the **bottom** of each script that already does `set volume to 70` (the `ゲームスタート`, `勝利`, and `敗北` scripts), add `if SoundOn = 0 then set volume to 0` and `stop all sounds`. Those scripts currently force volume back to 70. The check has to come after that, or the mute button loses.
4. The `戦闘開始` script on `音楽` already sets volume to 0. Leave that fade alone, and still end it with the same `if SoundOn = 0` check so unmuting later in a fight can `set volume to 70` from the button in step 2.
5. Saving: on the `セーブ` sprite, where the code is joined together, `join` `SoundOn` as the last character. On the `ロード` sprite, the project already reads one letter at a time with `letter (答え　数) of answer`. After the old letters are read, read one more letter into `SoundOn`. `if answer is empty` or that letter is not 0 or 1, `set SoundOn to 1` and keep going. An old save code should still load the game.
6. `when green flag clicked` on `SoundButton`: `set SoundOn to 1` only if you have not loaded a code yet. A simple way is a variable `LoadedSound` that the load script sets to 1. `if LoadedSound = 0 then set SoundOn to 1`. Sound stays on until Arthur taps the button or loads a code.

## 5. How to play

A big overlay with three icons: move, punch, and kick.

The fight controls are the messages `左` `右` `上` `下` (move), `パンチ` (punch), and `キック` (kick). `コントローラー` sends the move messages when the arrow keys are pressed. Guard (`ガード`) and the sword button (`剣ボタン`) stay off this overlay so the three icons can be huge.

**Sprites:** new `HowTo`. Costumes: `closed`, and `page` (a large card). Three more costumes, or three tiny extra sprites: a shoe or arrow for move, a fist for punch, a boot for kick. New `HowToButton` with the word HELP in big letters.

**Variables:** new `HowToOpen` (1 or 0).

**Messages:** new `show help` and `hide help`. Also `ステージかいし`, so the card hides when a fight starts.

**Blocks:**

1. `HowToButton`: `set size to 180%`, `go to x: -200 y: 160`, `go to front layer`. `when this sprite clicked`: `if HowToOpen = 0 then broadcast show help else broadcast hide help`.
2. On `HowTo`, `when I receive show help`: `set HowToOpen to 1`, `show`, `go to front layer`, `go to x: 0 y: 0`, `switch costume to page`, `set size to 200%`.
3. On the page costume, draw three pictures in a row with words under them: MOVE, PUNCH, KICK. Words are part of the costume so they stay big on the tablet. Under the pictures, one line: "Tap HELP again to close."
4. `when I receive hide help` or `when I receive ステージかいし`: `set HowToOpen to 0`, `hide`.
5. `when this sprite clicked` on `HowTo` while it is open: `broadcast hide help`, so a tap on the card itself also closes it. The button is the obvious target. The card is a second, just as big, target.

## 6. Missing-picture fallback

If the hero costume is the wrong one, show a plain stickman and a friendly sentence.

Scratch will not tell you that a picture failed to download. The project finishes loading before the green flag runs. There is no "when load fails" hat, and there is no try/catch block. A costume that was never added is already missing in the editor. `switch costume to` a name that is not in the list does not change the costume.

What Scratch **can** check is `costume name` and `backdrop name`. The fallback is a costume you draw yourself, plus a check that the name is one you expect.

**Sprites:** `主人公`. Add a costume named `plain stickman` (circle head, five lines). New sprite `OopsText` for the message. On the Stage, add a backdrop named `oops` (a flat colour and the words "Arthur's Arena").

**Variables:** new `PictureOK` (1 or 0).

**Messages:** none required. The check runs `when green flag clicked`.

**Blocks:**

1. Draw `plain stickman` on `主人公` and draw the `oops` backdrop. These live inside the project, so they are there even if a fancier costume was deleted.
2. `when green flag clicked` on `主人公`: `set PictureOK to 0`. `if costume name = コスチューム1` (the costume the fight script already switches to at `ステージかいし`) `then set PictureOK to 1`. Add `or` for the other hero costumes you still trust.
3. `if PictureOK = 0 then switch costume to plain stickman`, `set size to 100%`, `go to x: 0 y: 0`, `show`.
4. On `OopsText`, `when green flag clicked`: `if PictureOK = 0 then say A picture is missing. Here is a plain stickman so you can still play. for 5 seconds`, with the sprite `set size to 200%` and `go to front layer`. `else hide`.
5. Backdrop check, on the Stage, `when green flag clicked`: `if backdrop name = oops then` you are already on the safe backdrop. The home backdrop you want is `ホーム`. `if backdrop name is not ホーム and PictureOK = 0 then switch backdrop to oops`. Only do this at the flag, before `ホーム画面` runs, so a normal fight backdrop (`1`, `魔王`, `炎`, `暴走`, and the others) is not replaced mid-game.
6. Keep the sentence kind. No error codes on screen.

## 7. Debug overlay

A button shows a loops-per-second count, health, gold, and the current state.

Scratch has no FPS block, and it cannot list the scripts that are running. Two stand-ins are honest and still useful. A `forever` loop that counts once per trip around the loop, copied out each time `timer` passes 1, is "loops this second". It is not a real frame rate, and Turbo Mode makes the number huge. "Which script is running" is a variable the important scripts set themselves, named `CurrentState`.

There is no `score` variable. The number this game already shows as a reward is `gold`. The overlay shows `gold`.

The overlay stays hidden until the button is tapped, so Arthur's fight screen stays clear.

**Sprites:** new `DebugButton`, a big "DEBUG" label, `set size to 140%`, at `x: 200 y: -160`.

**Variables to show:** new `ShowDebug` (1 or 0), new `LoopsPerSecond`, new `LoopCount`, new `CurrentState`. Checked values: `自分:体力`, `敵:体力`, `gold`, `ステージ`, `試合中` (in a match), `試合終了` (match over).

**Messages:** the ones that should stamp `CurrentState`: `ホーム画面` → `home`, `ゲームスタート` → `title`, `ステージかいし` → `fight`, `ステージ魔王` / `ステージ炎` / `ステージ暴走` → `boss`, `勝利` → `win`, `敗北` → `lose`.

**Blocks:**

1. `when this sprite clicked` on `DebugButton`: `if ShowDebug = 0 then set ShowDebug to 1 else set ShowDebug to 0`.
2. `if ShowDebug = 1 then show variable` for `LoopsPerSecond`, `CurrentState`, `自分:体力`, `敵:体力`, `gold`, and `ステージ`. `else hide variable` for each of those. `show variable` and `hide variable` are in the Variables category. Drag the readouts to the top edge so they do not cover the buttons.
3. Loops counter, on the Stage: `when green flag clicked` → `reset timer`, `set LoopCount to 0`. Then `forever`: `change LoopCount by 1`, `if timer > 1 then set LoopsPerSecond to LoopCount`, `set LoopCount to 0`, `reset timer`.
4. On the Stage scripts that already receive the messages in the list above, add `set CurrentState to home` (or `fight`, `boss`, `win`, `lose`) as the first block. A boss start should set `boss` even though `ステージかいし` also runs, so put the `boss` set in the boss script **after** the fight script's set, or check `backdrop name = 魔王` inside the fight start and set `boss` in that case.
5. `when green flag clicked`: `set ShowDebug to 0` and hide the variables. The button still shows, so Mitch can turn the overlay on after a crash-like soft lock (a fight that never broadcasts `勝利` or `敗北`). `CurrentState` staying on `fight` while both stickmen are gone is the clue.

## 8. Try-again countdown

After a loss, a big prompt counts down from 5 and then restarts the fight.

`when I receive 敗北` already hides the fighters, hides the health digits, and switches the backdrop. That is the dead end. The countdown sprite shows on top of that backdrop.

**Sprites:** new `TryAgain` with a large costume that reads "Arthur got knocked down." New `FightAgainButton` ("FIGHT AGAIN") and new `HomeButton2` ("HOME") if `ホームボタン` is hidden on `敗北` (it is not in the defeat hide list, but the fight buttons `ガードボタン` and `剣ボタン` do hide). Make both new buttons `set size to 180%`.

**Variables:** new `RestartIn`. Existing `ステージ` tells you which fight to run again. `試合終了` is already set around a loss.

**Messages:** `敗北` opens the prompt. `FightAgainButton` broadcasts the start message for `ステージ` (see the table in the intro: stage value lines up with `ステージ1`, `ステージ2`, `ステージ炎`, `ステージ暴走`, `ステージ魔王`, and the other stage messages the Stage already receives). `HomeButton2` broadcasts `ホーム画面`. New message `cancel restart` so a tap stops the countdown.

**Blocks:**

1. On `TryAgain`, `when I receive 敗北`: `show`, `go to front layer`, `go to x: 0 y: 40`, `set RestartIn to 5`.
2. `repeat until RestartIn = 0`: `say (join "Try again? " (join RestartIn " ...")) for 1 seconds`, `wait 1 seconds`, `change RestartIn by -1`. The say block is the big text. `set size to 200%` on `TryAgain`.
3. `if RestartIn = 0 then broadcast` the stage start message for the current `ステージ`, using `if ステージ = 1 then broadcast ステージ1` and one `if` per stage you have, including `if backdrop name = 魔王 then broadcast ステージ魔王`. Then `hide`.
4. On `FightAgainButton`, `when this sprite clicked`: `set RestartIn to 0` and `broadcast cancel restart`, then broadcast the same stage message. `when I receive cancel restart` on `TryAgain` stops the loop: use a second check inside the loop, `if RestartIn = 0 then stop this script`, placed at the top of the repeat. Set `RestartIn` to 0 **before** the broadcast so the loop notices.
5. On `HomeButton2`, `when this sprite clicked`: `set RestartIn to 0`, `broadcast cancel restart`, `broadcast ホーム画面`, `hide` the prompt. Arthur can leave. Waiting also works: at 0 the fight starts on its own.
6. `when I receive 勝利`: `hide` the prompt so a win never shows the loss countdown.

## 9. Tap zones

Only taps inside the button boxes punch, kick, or move. Other taps do nothing.

Buttons already use `when this sprite clicked` (`ガードボタン`, `剣ボタン`, `戦闘ボタン`, `ホームボタン`), so a tap on empty stage does not press them. The fight loop on `主人公` is the risky one: during `ステージかいし` it watches `mouse down?` for the whole screen. A tap on a button can also be read as a move. The check below runs first and ignores anything outside the boxes.

**Sprites:** `コントローラー` (it already turns arrow keys into `左` `右` `上` `下`). `主人公`. The punch and kick are messages, not a single button sprite, so add two big button sprites if the remix does not already have them: `PunchButton` and `KickButton`, `set size to 180%`, sitting on the right side of the fight. Move zone is the left half of the stage, above the ground.

**Variables:** new `TapZone` (`none`, `move`, `punch`, `kick`). New `ShownTapHint` so the hint plays once.

**Messages:** `パンチ`, `キック`, `左`, `右`, `上`, `下`. Only send these from the zone check during a touch fight.

**Blocks:**

1. Drag `PunchButton` and `KickButton` where Arthur's thumb can reach. Write down the edges. A button from x 120 to 200 and y -40 to 40 is a punch box. Do the same for kick, just below it, and for move (x less than 0, and y greater than the ground).
2. On `コントローラー`, add a `forever` next to the arrow-key script: `if mouse down? then` test the boxes with `mouse x` and `mouse y`. `if mouse x > 120 and mouse x < 200 and mouse y > -40 and mouse y < 40 then set TapZone to punch` and `broadcast パンチ`. The kick box broadcasts `キック`. The left side `set TapZone to move` and broadcasts `右` or `左` based on whether `mouse x` is greater than the hero's `x position`.
3. `else set TapZone to none`. Do not broadcast. Do not change health.
4. On the first ignored tap only: `if TapZone = none and ShownTapHint = 0 then say Tap the big punch or kick button. for 2 seconds`, `set ShownTapHint to 1`. Later misses stay quiet so a fight is not a stream of popups.
5. While `TapZone` is `punch` or `kick`, skip the move branch in the hero's `mouse down?` script (`when I receive ステージかいし` on `主人公`). Wrap that move with `if TapZone = move then`. A thumb on Punch should not also walk Arthur.
6. Arrow keys on `コントローラー` stay as they are. This check is for taps.

## 10. Version line

The home screen shows **Arthur's Arena v0.2** so Mitch can see which build is open.

The title backdrop is `ホーム`, shown when the Stage receives `ホーム画面`. The thumbnail sprite `サムネイル` also reacts to `ゲームスタート`. The version sits on the home screen only, big enough to read, along the bottom so the title stays clear.

**Sprites:** new `VersionTag`. One costume with the words `Arthur's Arena v0.2` drawn in thick letters, or a text variable of that name. A costume is easier to make large.

**Variables:** none, if the words are a costume. If you would rather use a variable, name it `VersionText`, `set VersionText to Arthur's Arena v0.2`, and `show variable` only on the home screen.

**Messages:** `ホーム画面` and `ゲームスタート` show it. `ステージかいし`, `マップへ`, `ガチャ画面へ`, `装備選択　画面` hide it.

**Blocks:**

1. `when I receive ホーム画面`: `show`, `go to front layer`, `go to x: 0 y: -150`, `set size to 120%`.
2. `when I receive ゲームスタート`: same show, in case the title uses that message instead of `ホーム画面`.
3. `when I receive ステージかいし`: `hide`. Same hide on `マップへ` and the gacha and equipment messages, so the line does not sit on a boss.
4. Bump the costume text when the build changes (`v0.3`, `v0.4`). The words on the costume are the thing Mitch compares on the tablet.
