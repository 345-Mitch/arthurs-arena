# Arthur's Arena — 10 UI and debugging features

Written 2026-11-03 for Mitch and Arthur.

This is a plan for Arthur's Arena. The boss fights live in `projects/arthurs-arena-bosses.sb3` on branch `grok/bosses` (pull request #2). The scripts in that file are written out in `BOSSES.md` and `projects/BLOCK_LISTING.md` on that branch. The big Stickman Battle project it comes from is [project 732904827](https://scratch.mit.edu/projects/732904827) by onigirikun_2009. This file does not change either project. It says what to build, in blocks a kid can follow.

Open the bosses file and click **See inside**. The names there are English. The big project is still a mix of Japanese and English. A Japanese name below has a short English meaning next to it.

Big text, big buttons, kind messages, and a debug screen Mitch can turn on. Those are the rules for every feature.

## What changed from the starting list

All 10 seeds are still here. Fight notes now follow the bosses file. The big template is named only where its bosses are different.

1. **Health bars.** `Arthur Bar` and `Boss Bar` in the bosses file already turn green above 60 percent, yellow above 30, and red at 30 or below. Rival's bar scale is 55. Brute, Ivy, and Quake use 100, with a big BOSS label. Arthur's health is 100. Boss health is Brute 24, Ivy 24, Quake 30. The template's `体力バー` sprite is still save-code, and its bosses still use `敵:体力`.
2. **Hit flash.** The bosses file already sets the color effect to 40 for 0.12 seconds. Arthur flashes on `boss hits arthur`. Brute, Ivy, and Quake flash on `arthur hits boss`. The template's ouch message `いてっ` stays in the big project.
3. **Screen shake.** The bosses file already has `shake`. Brute sends it when his charge hits. Quake sends it on STOMP, including the faster wave under half health. `Ground` and `Impact` hop. Buttons stay still. Arthur's y stays with the jump, because `Arthur Jumping` is how he dodges Quake. The template's small shake is `揺れ`. `揺れ2` stays on the energy-wave sprite `波動`.
4. **Sound.** The choice is an extra digit on the save code the game already uses. A normal variable resets when the green flag starts. A cloud variable is numbers-only, needs a Scratcher account, needs the internet, and is shared by every viewer. The speaker button broadcasts `apply sound`. Each sprite that plays a sound sets its own volume. Details are in feature 4.
5. **How to play.** Still three icons: move, punch, kick. Guard and the sword stay off this card so those three can be huge.
6. **Missing picture.** Scratch has no "load failed" hat. The check is `costume name` and `backdrop name`, and the plain stickman is a costume drawn into the project. Details are in feature 6.
7. **Debug.** Scratch has no FPS block, so the overlay shows loops per second. Scratch cannot list running scripts. The bosses file already has a hidden `Game State` (`title`, `intro`, `fight`, `boss`, `win`, `lose`). An earlier draft called this `CurrentState`. That would be a second variable for the same job, so the overlay shows `Game State`.
8. **Try again.** The bosses file already has RETRY and HOME. RETRY broadcasts `start fight` and leaves `Which Fight` alone, so the same person comes back. HOME broadcasts `show title`. The 5-second count is the part to add on top of those two buttons.
9. **Tap zones.** A miss sets `TapZone` to `none` and leaves health alone. One short hint plays the first time. The hero's `mouse down?` loop during `ステージかいし` is why this matters: the other buttons already use `when this sprite clicked`.
10. **Version line.** The words are `Arthur's Arena v0.2`, on backdrop `ホーム`.

## The 10 features

1. **Colour health bars** — Arthur's bar and the boss bar turn green, then yellow, then red, and a big number shows the health.
2. **Hit flash** — The stickman flashes when he gets hurt, so a hit is obvious.
3. **Screen shake** — Brute's hit and Quake's stomp hop the ground, and the buttons stay still.
4. **Sound on/off** — A big speaker button mutes the game, and the choice can be written into the save code Scratch already uses.
5. **How to play** — A big overlay with three icons: move, punch, and kick.
6. **Missing-picture fallback** — If the hero costume is the wrong one, show a plain stickman and a friendly sentence.
7. **Debug overlay** — A button shows a loops-per-second count, health, and `Game State`.
8. **Try-again countdown** — After a loss, a big prompt counts down from 5 and then restarts the fight.
9. **Tap zones** — Only taps inside the button boxes punch, kick, or move. Other taps do nothing.
10. **Version line** — The home screen shows **Arthur's Arena v0.2** so Mitch can see which build is open.

Implementation steps for each feature come in the sections below.

Boss notes below follow `projects/arthurs-arena-bosses.sb3`. The order is Rival, then three bosses. `Which Fight` is 1 Rival, 2 Brute, 3 Ivy, 4 Quake.

| Fight | Who | Health | What they do | Hooks already in the file |
| --- | --- | --- | --- | --- |
| 2 | Brute | 24 | Says **Ready?**, saves `Arthur X` into `Charge X`, then glides to that spot. The hit is 10. | `broadcast shake` when the charge touches Arthur |
| 3 | Ivy | 24 | Three shots, one at a time: low, high, low. `Shot Height` is 0, then 156, then 0. Each hit is 8. | Message `ivy shot`. Ivy Shot sets `Hurt Power` and broadcasts `boss hits arthur` |
| 4 | Quake | 30 | Says **STOMP!** An orange wave rolls on the ground. The hit is 12, and only if `Arthur Jumping` is 0. Under half health, `Wave Speed` goes from 16 to 26. | Messages `shake`, `quake wave`, and `quake angry` |

Shared hooks in that file:

- Bars: `Arthur Bar` and `Boss Bar`. Green above 60 percent, yellow above 30, red at 30 or below. `Boss Bar Scale` is 55 for Rival and 100 for a boss. `Boss Label` says BOSS for Brute, Ivy, and Quake.
- Health: `Arthur Health` and `Arthur Max Health` are 100. `Boss Health` and `Boss Max Health` are the pair on `Boss Card`.
- `Game State` is `title`, `intro`, `fight`, `boss`, `win`, or `lose`. It is hidden. Rival is `fight`. Brute, Ivy, and Quake are `boss`.

The big template still has its own bosses: `魔王敵` (Demon King), `炎敵` (flame), and `暴走敵` (berserk), with `敵:体力` and the message `揺れ`. Those fights stay in project 732904827. The steps below use the bosses file. A template name is only a pointer back to that older fight.

## 1. Colour health bars

Arthur's bar and the boss bar turn green, then yellow, then red, and a big number shows the health.

This is already in the bosses file. Use `Arthur Bar` and `Boss Bar`. A second pair of bar sprites would sit on top of them.

**Sprites:** `Arthur Bar`, `Arthur Bar Back`, `Boss Bar`, `Boss Bar Back`, `Boss Label`. Rival is the smaller bar. Brute, Ivy, and Quake are the big one.

**Variables:** `Arthur Health`, `Arthur Max Health`, `Boss Health`, `Boss Max Health`, `Bar Percent`, `Boss Bar Scale`, `Which Fight`.

**Messages:** `intro done` shows the bars. `show title`, `arthur loses`, `arthur champion`, and `round clear` hide them.

**Blocks:**

1. The coloured costume's centre is the left edge, so the bar shrinks toward the left as health drops. `Arthur Bar` and `Boss Bar` already run `forever` while `Fight On` = 1. They set `Bar Percent` to `(health / max) * 100`, keep it between 0 and 100, then `switch costume to green` above 60, `yellow` above 30, and `red` otherwise.
2. Both loops already do `if max < 1 then set max to 1` before the divide. Leave that. It stops a divide-by-zero on the first frame.
3. `Boss Bar` sets `Boss Bar Scale` to 55 when `Which Fight` = 1 (Rival) and to 100 for Brute (2), Ivy (3), and Quake (4). The size block is `(Bar Percent * Boss Bar Scale) / 100`. `Boss Label` switches to the BOSS costume at size 120 for those three, and to RIVAL at size 70 for Rival.
4. `Boss Card` sets each fight's health as a pair, on `start fight`, before `intro done`. Brute is `Boss Max Health` 24 and `Boss Health` 24. Ivy is 24 and 24. Quake is 30 and 30, and it also sets `Quake Phase` to 1. Change both numbers together. One number alone makes the percent wrong, so a full-health boss can open on yellow or red.
5. The number is the variable monitor. On `intro done` the Stage already runs `show variable Arthur Health` and `show variable Boss Health`. Drag those readouts next to the bars so the digits are big and easy to see. On `show title`, `arthur loses`, and `arthur champion` the Stage hides them. Leave that.
6. The big template still has `魔王敵`, `炎敵`, and `暴走敵`, and the variable `敵:体力`. Its sprite `体力バー` holds save-code blocks, not a drawing of a bar. These steps follow the bosses file.

## 2. Hit flash

The stickman flashes when he gets hurt, so a hit is obvious.

The bosses file already blinks the colour effect. Arthur blinks when a boss hits him. Brute, Ivy, and Quake blink when Arthur's punch or kick lands. Keep that blink. A second script on the same message stacks the colour and the flash lasts too long.

**Sprites:** `Arthur`, `Brute`, `Ivy`, `Quake`. Rival uses the same blink. `Ivy Shot` and `Quake Wave` are the attacks, so the flash stays on Ivy and Quake, not on the ball or the wave.

**Variables:** `Which Fight`. No new variable.

**Messages:** `boss hits arthur` (Arthur flashes). `arthur hits boss` (the boss flashes).

**Blocks:**

1. On `Arthur`, `when I receive boss hits arthur` already does `set color effect to 40`, `wait 0.12 seconds`, `set color effect to 0`. Leave it.
2. On `Brute`, the same three blocks run `when I receive arthur hits boss`, inside `if Which Fight = 2`. `Ivy` checks `Which Fight = 3`. `Quake` checks `Which Fight = 4`. The check matters: all three sprites hear every hit, and only the one in the fight should flash.
3. A new boss copies step 2 and checks its own `Which Fight` number. One blink script per sprite.
4. The big template's ouch message is `いてっ`, and its bosses are `魔王敵`, `炎敵`, and `暴走敵`. The ghost effect in that project hides punches and buttons. The blink in both files stays the color effect.

## 3. Screen shake

Brute's hit and Quake's stomp hop the ground, and the buttons stay still.

Scratch has no camera. The bosses file fakes the shake with the message `shake`. `Ground` and `Impact` hop, then hop back. The buttons never hear `shake`. Arthur does not hear it either: his y is the jump, and `Arthur Jumping` is what makes Quake's wave miss.

**Sprites:** `Ground` and `Impact` hop. `Brute` and `Quake` send `shake`. Leave `Left Button`, `Right Button`, `Jump Button`, `Punch Button`, and `Kick Button` off this message. A hopping button is a missed tap.

**Variables:** `Arthur X`, `Charge X`, `Arthur Jumping`, `Quake Phase`, `Wave Speed`, `Shot Height`.

**Messages:** `shake`. Quake also sends `quake wave`. Ivy sends `ivy shot` and does not shake today.

**Blocks:**

1. Brute's loop runs when `Fight On` = 1 and `Which Fight` = 2. He `set Charge X to Arthur X`, `switch costume to lean`, and `say Ready? for 0.7 seconds`. Then he glides to `Charge X`. If he is `touching Arthur`, he sets `Hurt Power` to 10, `broadcast boss hits arthur`, and `broadcast shake`. Move while he says Ready? and the glide misses.
2. Quake says STOMP! and `broadcast shake`, then `broadcast quake wave`. The wave hurts only when `Arthur Jumping` is 0, and the hit is 12. Under half health (`Boss Health` below `Boss Max Health / 2`) the Stage `broadcast quake angry`, then `Wave Speed` is 26 instead of 16 and the warning is 0.25 seconds. That faster stomp still broadcasts `shake`.
3. On `Ground`, `when I receive shake` already `repeat 3`: `change y by 6`, `wait 0.05 seconds`, `change y by -6`, `wait 0.05 seconds`. `Impact` does `change y by 8` for the same three hops, then `hide`. The down step puts them back. Leave those scripts. Do not add `shake` to Arthur.
4. Ivy is the gap. Her three shots are low, high, low (`Shot Height` 0, then 156, then 0) and each hit is 8. On `Ivy Shot`, next to `broadcast boss hits arthur`, add `broadcast shake`. The ground then hops on her hits too. The buttons still get no shake script.
5. A bigger hop while Quake is angry: on `Ground`, `if Quake Phase = 2 then change y by 10`, `else change y by 6`. Same three repeats, and the matching `change y by` negative number so the floor ends where it started.
6. The big template's small shake is `揺れ`, on the fighters, including `魔王敵`, `炎敵`, and `暴走敵`. `揺れ2` belongs to the energy-wave sprite `波動`. The bosses file's message is `shake`. Extend `shake`.

## 4. Sound on/off

A big speaker button mutes the game, and the choice can be written into the save code Scratch already uses.

Plain Scratch has no local storage. A normal variable forgets its value when the green flag starts, because the flag loads the value saved in the project. There is no block for cookies, files, or the tablet's storage.

A cloud variable can store this, with hard limits. Cloud variables hold numbers only (0 and 1 are fine, the word "off" is not). They need a Scratcher account, they need the internet, and they are shared by everyone looking at the project. One public `☁ SoundOn` would mute the game for every player at once. Offline on the tablet, the cloud value does not update. That is a poor fit for Arthur's home tablet.

The realistic place to remember the choice is the save code this game already teaches: press **Save**, copy the code, and type it in on **Load** (`セーブ` and `ロード` sprites, list `セーブする`). Add one extra digit. Old codes that do not have the digit still load.

Scratch's `set volume` block changes the volume of the sprite that runs the block. It does not change the volume of the sprite that is playing the music. A `set volume` on `SoundButton` mutes the button only. `stop all sounds` can cut off what is playing, and then `音楽`'s `forever` loop starts `魔王魂  ファンタジー10` again at `音楽`'s own volume, which the button never changed. A later tap that unmutes the button cannot turn `音楽` back up after `音楽` has set its own volume to 0. The button broadcasts. Every sprite that plays a sound sets its own volume when that message arrives.

The bosses file has no sounds and no speaker button. If a sound is added there, that new sprite needs the same `when I receive apply sound` script.

**Sprites:** new `SoundButton` (two costumes, `on` and `off`, a big speaker). Existing `音楽` (plays `魔王魂  ファンタジー10` in a `forever` loop after `ゲームスタート`, and sets its own volume to 70 or 0). `敵1`, `敵2`, and `敵3` play a sound when they receive `揺れ`. Any other sprite with a `play sound` or `start sound` block needs the same handler. Existing `セーブ` and `ロード`.

**Variables:** new `SoundOn` (1 or 0). The project already uses `セーブ` and `答え　数` while loading.

**Messages:** new `apply sound`. Also `ゲームスタート`, `戦闘開始`, `勝利`, and `敗北`, because those are where `音楽` already runs `set volume` on itself.

**Blocks:**

1. Make `SoundButton` large (`set size to 150%` or bigger) and park it in a corner on every screen: `when green flag clicked` → `show`, `go to front layer`, `go to x: 200 y: 160`.
2. `when this sprite clicked`: `if SoundOn = 1 then set SoundOn to 0 else set SoundOn to 1`. `if SoundOn = 1 then switch costume to on`, `else switch costume to off`. Then `broadcast apply sound`. The button does not run `set volume` and does not run `stop all sounds`.
3. On `音楽`, and on `敵1`, `敵2`, `敵3`, and every other sprite that plays a sound: `when I receive apply sound` → `if SoundOn = 1 then set volume to 70`, `else set volume to 0` and `stop all sounds`. The `set volume` has to be inside that sprite's script. A broadcast is what makes each sprite run its own block. Copy this script onto each of them.
4. On `音楽`, the `ゲームスタート`, `勝利`, and `敗北` scripts already `set volume to 70`. That line turns the music back up even when the speaker shows off. At the bottom of each of those scripts, `broadcast apply sound`, so `音楽` applies `SoundOn` to itself after the 70. The `戦闘開始` script sets volume to 0 as a quiet battle. Leave that fade, and end it with `if SoundOn = 0 then set volume to 0` on `音楽`. Do not broadcast `apply sound` from the fade, or an unmute-state would jump straight back to 70. A tap on the speaker during the fight still broadcasts `apply sound`, which is how `音楽` follows the button.
5. Saving: on the `セーブ` sprite, where the code is joined together, `join` `SoundOn` as the last character. On the `ロード` sprite, the project already reads one letter at a time with `letter (答え　数) of answer`. After the old letters are read, read one more letter into `SoundOn`. `if answer is empty` or that letter is not 0 or 1, `set SoundOn to 1` and keep going. An old save code should still load the game. Then `broadcast apply sound`. Writing the variable is not enough. The music sprite does not see the number until it receives the message.
6. `when green flag clicked` on `SoundButton`: `set SoundOn to 1` only if you have not loaded a code yet. A simple way is a variable `LoadedSound` that the load script sets to 1. `if LoadedSound = 0 then set SoundOn to 1`. Then `broadcast apply sound`, so every sound sprite picks up the starting value. Sound stays on until Arthur taps the button or loads a code.

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

**Messages:** new `pictures checked`, sent at the end of the hero's green-flag script so the message and the backdrop wait until `PictureOK` is set.

**Blocks:**

1. Draw `plain stickman` on `主人公` and draw the `oops` backdrop. These live inside the project, so they are there even if a fancier costume was deleted.
2. `when green flag clicked` on `主人公`: `set PictureOK to 0`. `if costume name = コスチューム1` (the costume the fight script already switches to at `ステージかいし`) `then set PictureOK to 1`. Add `or` for the other hero costumes you still trust.
3. `if PictureOK = 0 then switch costume to plain stickman`, `set size to 100%`, `go to x: 0 y: 0`, `show`.
4. End the hero's green-flag script with `broadcast pictures checked`. Green-flag scripts start together, so a `say` on the flag can run before `PictureOK` is set.
5. On `OopsText`, `when I receive pictures checked`: `set size to 200%`, `go to front layer`. `if PictureOK = 0 then say A picture is missing. Here is a plain stickman so you can still play. for 5 seconds`. `else hide`.
6. On the Stage, `when I receive pictures checked`: `if PictureOK = 0 then switch backdrop to oops`. The home backdrop is `ホーム`. Fight backdrops (`1`, `魔王`, `炎`, `暴走`, and the rest) are chosen later by their own messages. This check runs once, from `pictures checked`.
7. Keep the sentence kind. No error codes on screen.

## 7. Debug overlay

A button shows a loops-per-second count, health, and `Game State`.

Scratch has no FPS block, and it cannot list the scripts that are running. A `forever` loop that counts once per trip, copied out each time `timer` passes 1, is "loops this second". It is not a real frame rate, and Turbo Mode makes the number huge. "Which script is running" is a variable the Stage sets itself.

That variable already exists. It is `Game State`, and the bosses file hides it on the green flag. An earlier draft of this plan called it `CurrentState`. A second variable would drift out of date the first time a fight script forgot to set both. The overlay shows `Game State`.

The bosses file has no `gold` variable. The template's reward number is `gold`. Here the overlay shows `Which Fight` next to the two health numbers.

**Sprites:** new `DebugButton`, a big DEBUG label, `set size to 140%`, at `x: 200 y: -160`.

**Variables to show:** new `ShowDebug` (1 or 0), new `LoopsPerSecond`, new `LoopCount`. Already in the file: `Game State`, `Arthur Health`, `Boss Health`, `Which Fight`.

**Messages:** the Stage already sets `Game State` on these:

| Message | `Game State` | Who |
| --- | --- | --- |
| green flag, `show title` | `title` | title |
| `start fight` | `intro` | name card, before the fight |
| `intro done` and `Which Fight` = 1 | `fight` | Rival |
| `intro done` and `Which Fight` is 2, 3, or 4 | `boss` | Brute, Ivy, Quake |
| `arthur wins round` and `Which Fight` = 4 | `win` | Quake, the champion |
| `arthur loses` | `lose` | Arthur's health hit 0 |

**Blocks:**

1. `when this sprite clicked` on `DebugButton`: `if ShowDebug = 0 then set ShowDebug to 1 else set ShowDebug to 0`.
2. `if ShowDebug = 1 then show variable` for `LoopsPerSecond`, `Game State`, `Arthur Health`, `Boss Health`, and `Which Fight`. `else hide variable` for each of those. `Game State` starts hidden. This button is how Mitch sees it. Hiding it again keeps Arthur's screen clear. Drag the readouts to the top edge so they do not cover the buttons.
3. Loops counter, on the Stage: `when green flag clicked` → `reset timer`, `set LoopCount to 0`. Then `forever`: `change LoopCount by 1`, `if timer > 1 then set LoopsPerSecond to LoopCount`, `set LoopCount to 0`, `reset timer`.
4. Leave the Stage's `set Game State` blocks as they are. `intro done` is the one that picks `fight` for Rival and `boss` for Brute, Ivy, and Quake. Do not add `CurrentState` beside them.
5. `when green flag clicked` on `DebugButton`: `set ShowDebug to 0` and hide the debug variables. The Stage already hides `Game State`, `Arthur Health`, and `Boss Health` on the flag. The button still shows, so Mitch can turn the overlay on if a fight never reaches `win` or `lose`. `Game State` stuck on `boss` while both stickmen are gone is the clue.

## 8. Try-again countdown

After a loss, a big prompt counts down from 5 and then restarts the same fight.

The bosses file already handles the loss. On `arthur loses` the Stage sets `Game State` to `lose`, switches to the Lose backdrop, and Arthur says **Arthur got knocked down.** `Try Again` (the RETRY button) and `Home Button` show. RETRY `broadcast start fight` and does not change `Which Fight`, so Brute, Ivy, or Quake comes back. HOME `broadcast show title`.

The 5-second count is the new part. It sits on top of those two buttons. The buttons only set variables. The countdown script is the one that broadcasts, so a tap and the timer cannot both start a fight.

**Sprites:** new `Countdown`, with big words. Existing `Try Again` and `Home Button`. Do not add a second RETRY or HOME sprite.

**Variables:** new `RestartIn`, new `RestartChoice` (`fight` or `home`). `Which Fight` is already 2, 3, or 4 for Brute, Ivy, and Quake.

**Messages:** `arthur loses` opens the prompt. At 0 the prompt broadcasts `start fight` or `show title`. `show title` and `arthur champion` hide it.

**Blocks:**

1. On `Countdown`, `when I receive arthur loses`: `show`, `go to front layer`, `go to x: 0 y: 80`, `set size to 200%`, `set RestartIn to 5`, `set RestartChoice to fight`. `Try Again` and `Home Button` already show themselves on `arthur loses`.
2. `repeat until RestartIn < 1`: `say (join "Try again? " RestartIn)`, `wait 1 seconds`, `if RestartIn > 0 then change RestartIn by -1`. The `if` matters. A button sets `RestartIn` to 0 during the wait. Another `change by -1` would make it -1, and `repeat until RestartIn = 0` would never end.
3. After the loop: `if RestartChoice = home then broadcast show title`, `else broadcast start fight`. Then `hide`. `start fight` keeps `Which Fight`, which is the same thing RETRY already does.
4. On `Try Again`, `when this sprite clicked`: `set RestartChoice to fight`, `set RestartIn to 0`. Take the `broadcast start fight` off this click and leave it in step 3. A click that also broadcasts starts the fight twice.
5. On `Home Button`, `when this sprite clicked`: `set RestartChoice to home`, `set RestartIn to 0`. Step 3 then broadcasts `show title`.
6. `when I receive arthur champion` or `show title`: `hide` the countdown, so a win or a trip home never leaves the numbers up.
7. The big template's loss message is `敗北`, and its home message is `ホーム画面`. Its bosses are still `魔王敵`, `炎敵`, and `暴走敵`. The countdown in the bosses file uses `arthur loses`, `start fight`, and `show title`.

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

## More features from popular fighters

Features 1 to 10 stay as they are. These extra ones come from games a lot of people play: Super Smash Bros. Ultimate, Street Fighter 6, Mortal Kombat 1, Tekken 8, Brawlhalla, Brawl Stars, and Stick Fight: The Game.

Two popular ideas are left out on purpose. Fortnite's storm circle shrinks and hurts anyone left outside it ([Epic's storm circle notes](https://dev.epicgames.com/documentation/en-us/fortnite/storm-circle)). A closing ring on one flat floor is a harsh timer for a kid. Mortal Kombat's finishing moves are left out too. The block button and the practice room are the parts that fit. Stick Fight is full of guns ([Steam page](https://store.steampowered.com/app/674940/Stick_Fight_The_Game/)). The arena pickup below is a healing apple, not a weapon.

Each idea uses the bosses file: `Game State`, `shake`, `Boss Bar`, `Which Fight`, and Brute, Ivy, and Quake.

## 11. A short dodge

Arthur slips aside for a moment, and the hit misses.

**Where it shows up:** Super Smash Bros. Ultimate has an air dodge that makes the fighter briefly unable to be hit ([SmashWiki: Air dodge](https://www.ssbwiki.com/Air_dodge)). Brawlhalla's dodge does the same job: a short invincible move that can slip an attack ([Brawlhalla Wiki: Movement](https://brawlhalla.wiki.gg/wiki/Movement)).

**Why it suits Arthur:** Brute says **Ready?** and then runs. Ivy calls **Low!** and **High!** Quake yells **STOMP!** A dodge gives Arthur one more answer when the jump is the wrong one. It is one big button, and it cannot be spammed.

**Sprites:** new `Dodge Button`, words DODGE, `set size to 180%`. It shows and hides with the other fight buttons, on `intro done`, and hides on `show title`, `arthur loses`, and `arthur champion`.

**Variables:** new `Dodge Safe` (1 or 0), new `Dodge Ready` (1 or 0).

**Messages:** the Stage already receives `boss hits arthur` from Brute, Ivy Shot, Quake Wave, and Rival. New message `boss missed`.

**Blocks:**

1. `Dodge Button`, `when this sprite clicked`: `if Fight On = 1 and Dodge Ready = 1`. `set Dodge Ready to 0`. `set Dodge Safe to 1`. On Arthur, `set ghost effect to 40` so he looks faded. `wait 0.4 seconds`. `set Dodge Safe to 0`. `clear graphic effects`. `wait 1 second`. `set Dodge Ready to 1`.
2. On the Stage, at the top of `when I receive boss hits arthur`: `if Dodge Safe = 1 then broadcast boss missed` and `stop this script`. Health does not change. The rest of that script, the one that subtracts `Hurt Power`, stays for a real hit.
3. On Arthur, `when I receive boss missed`: `say Missed! for 0.6 seconds`.
4. This covers Brute's charge (hit 10), Ivy's three shots (hit 8, low then high then low), and Quake's wave (hit 12, and only when `Arthur Jumping` is 0). The jump still dodges the wave by itself. The dodge is the extra slip.

## 12. A block that softens one hit

A big BLOCK button makes the next hit softer, and then it needs a rest.

**Where it shows up:** Super Smash Bros. Ultimate has a shield. It blocks most hits, and it cannot be held forever: it shrinks and can break ([SmashWiki: Shield](https://www.ssbwiki.com/Shield)). Street Fighter 6 has blocking, and a Drive Reversal you can do while blocking ([Capcom: Fighting Ground](https://www.streetfighter.com/6/en-us/mode/fightingground)). Mortal Kombat 1 has Block as its own button ([WB Games support: accessibility](https://mortalkombatgamessupport.wbgames.com/hc/en-us/articles/19435787154963-Mortal-Kombat-1-Accessibility-Features-A11Y)).

**Why it suits Arthur:** One button, one job. The next boss hit hurts less. Then the button rests, so holding it is not a wall. High and low blocks are left out. Ivy's **Low!** and **High!** are already a jump puzzle.

**Sprites:** new `Block Button`, words BLOCK, `set size to 180%`. Same show and hide as `Dodge Button`.

**Variables:** new `Blocking` (1 or 0), new `Block Ready` (1 or 0).

**Messages:** `boss hits arthur`.

**Blocks:**

1. `when green flag clicked` on `Block Button`: `set Block Ready to 1`. `set Blocking to 0`.
2. `when this sprite clicked`: `if Fight On = 1 and Block Ready = 1 and Dodge Safe = 0`. `set Blocking to 1`. `set Block Ready to 0`. Arthur `says Block! for 0.4 seconds`.
3. On the Stage, inside `boss hits arthur`, after the dodge check: `if Blocking = 1 then set Hurt Power to Hurt Power / 2`, `set Blocking to 0`, then do the normal health subtract. Brute's 10 becomes 5. Ivy's 8 becomes 4. Quake's 12 becomes 6. `Boss Bar` still follows `Boss Health`. Arthur's bar follows the smaller loss.
4. After that hit, `wait 1 second`, then `set Block Ready to 1`. A second hit during the rest is full strength.
5. If `Dodge Safe` is 1, the dodge already skipped the damage. The block does not also fire.

## 13. A power star

Landing hits fills a meter. When it is full, one big star hit shakes the ground.

**Where it shows up:** Street Fighter 6 spends a Super Art gauge on a big special. The gauge fills when attacks land, and it can hold three stocks ([Capcom: Fighting Ground](https://www.streetfighter.com/6/en-us/mode/fightingground), [SuperCombo: HUD](https://wiki.supercombo.gg/w/Street_Fighter_6/HUD)). In Brawl Stars, a Super charges mostly by hitting the other fighters, then fires from its own button ([Brawl Stars Wiki: Beginner's Guide](https://brawlstars.fandom.com/wiki/Beginner%27s_Guide)). Super Smash Bros. Ultimate's Rage Blaster "grows stronger if the user has taken lots of damage" ([official items page](https://www.smashbros.com/en_US/item/index.html)).

**Why it suits Arthur:** Punch is 5 and kick is 8. The star is one bigger hit he can see coming, because the button only appears when the meter is full. Under 30 health his bar is already red, so the meter fills faster and a cheer shows up. That is the comeback, without a finishing move.

**Sprites:** new `Power Meter` (a thin bar, costumes `empty` and `full`). New `Star Button`, words STAR, hidden until the meter is full. `set size to 180%`.

**Variables:** new `Power` (0 to 10). New `Said Cheer` (1 or 0). Already there: `Hit Power`, `Arthur Health`, `Arthur Max Health`.

**Messages:** `arthur hits boss` fills the meter. `boss hits arthur` is where the low-health cheer runs. New message `arthur power`.

**Blocks:**

1. On the Stage, `when I receive arthur hits boss`, after `Boss Health` changes: `if Arthur Health < 30 then change Power by 2`, `else change Power by 1`. 30 is the red zone on Arthur's bar, because his max is 100 and the bar turns red at 30 percent or below. `if Power > 10 then set Power to 10`.
2. On `when I receive boss hits arthur`, the first time `Arthur Health` is under 30: `if Said Cheer = 0 then` Arthur `says You can do it! for 1 second`, `set Said Cheer to 1`. Set `Said Cheer` back to 0 on `start fight`.
3. `Power Meter` `forever`: `if Power = 10 then switch costume to full` and `show` `Star Button`. `else switch costume to empty` and `hide` `Star Button`.
4. `Star Button`, `when this sprite clicked`: `if Power = 10 and Fight On = 1`. `broadcast arthur power`.
5. On Arthur, `when I receive arthur power`: `set Hit Power to 16`. If he is touching the fighter for this `Which Fight` (Rival 1, Brute 2, Ivy 3, Quake 4), the same touching checks his punch already uses, `broadcast arthur hits boss`. `broadcast shake`. `set Power to 0`. `say Star! for 0.6 seconds`.
6. `shake` is the same message Brute and Quake already send. `Ground` and `Impact` hop. The buttons do not.

## Codex review

Checked again on 2026-11-03, after Codex reviewed this pull request.

Codex flagged one thing. On feature 4, the review comment (pull request #1, `FEATURES.md`) says Scratch's volume block changes the volume of the sprite that runs the block. A mute button that runs `set volume` only changes itself. `stop all sounds` can cut off what is playing, and `音楽`'s `forever` loop can start the music again at `音楽`'s old volume. Unmuting from the button cannot turn `音楽` back up after `音楽` has set its own volume to 0.

Addressed in feature 4. The button broadcasts `apply sound` and does not set volume. Every sprite that plays a sound, including `音楽` and the hit sounds on `敵1`, `敵2`, and `敵3`, sets its own volume when it receives `apply sound`. The load script broadcasts `apply sound` after it writes `SoundOn` from the save code. The green flag does too. The earlier sentence in this section that said Codex flagged nothing was from before this review. This note replaces it.

Still true from the first look, and not part of the finding:

- Branch `codex-review` points at the same commit as `main`: `94aefa4` ("Add starter guide for Arthur's stickman fighting game in Scratch"). The diff is empty. Both branches contain `README.md` and `STARTER_GUIDE.md` only.
- Issues: none. Commit comments on `94aefa4` and `46eb807`: none. Discussions are disabled.

The limits in features 6 and 7 (no load-error hat, no FPS block, no list of running scripts) come from Scratch, not from Codex. Feature 4's volume rule is the Codex finding. The save-code limit in feature 4 is still a Scratch limit, and the volume rule sits on top of it.
