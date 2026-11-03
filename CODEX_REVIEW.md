# Codex review notes

Checked 2026-11-03 before the boss project was built.

## What was on the repo

- Branch `codex-review` points at the same commit as `main`: `94aefa4` ("Add starter guide for Arthur's stickman fighting game in Scratch"). The diff is empty. Both branches contain `README.md` and `STARTER_GUIDE.md` only.
- Issues: none.
- Commit comments on `94aefa4` and `46eb807`: none.
- Discussions: disabled.

The only Codex review that had finished was on pull request #1 (`grok/features`, file `FEATURES.md`), not on `codex-review`.

## Adopted

Codex left one finding, on the sound toggle in `FEATURES.md` (review comment on line 135 of that file). Scratch's volume block changes the volume of the sprite that runs the block. A button that sets its own volume does not mute the music sprite `音楽`, and a later `stop all sounds` does not keep the music sprite from starting again.

This boss project has no sounds and no mute button. If a sound is added later, the button should broadcast a message, and every sprite that plays a sound should set its own volume when it receives that message. `FEATURES.md` itself was left for the features branch.

## Skipped

There were no other Codex findings to apply. Nothing on `codex-review`, and no issue or commit comments.

## Ideas used from the template and the features plan

These are not Codex comments. They are notes from reading project 732904827 and from `FEATURES.md` on `grok/features`, kept only where they help a kid play.

Used here:

- The three template bosses suggested the patterns: `暴走敵` rushes, `炎敵` throws fire, and `魔王敵` plus the `波動` wave is a heavy slam. Brute, Ivy, and Quake are those patterns with short English scripts, plus a half-health phase on Quake.
- Health bars use a percent of that fight's max. Green above 60, yellow above 30, red at 30 or below. The costume's center is the left edge, so the bar shrinks to the right.
- The boss bar is a 240 by 22 costume at size 100. Rival, the normal enemy, uses the same costume at size 55. Arthur's bar is a 150 by 14 costume at size 70.
- A hit flashes the color effect to 40 for 0.12 seconds. The ghost effect is not used.
- Brute's hit and Quake's stomp broadcast `shake`. The Ground sprite and the Impact sprite move. The buttons do not.
- Punch, kick, jump, and move happen only when those buttons are clicked.
- The lose screen says "Arthur got knocked down." and shows RETRY and HOME.
- `Game State` is `title`, `intro`, `fight`, `boss`, `win`, or `lose`. A later debug readout can show it. It stays hidden during play.

Left for the template, or for a later pass:

- The template's enemy health variable `敵:体力` and the messages `大揺れ` and `ステージ魔王`. This arena uses `Boss Health`, `shake`, and `Game State` instead, because the template is 122 sprites and the scripts are mostly Japanese.
- The template's boss health numbers 5000, 7000, and 8200. Rival has 10, Brute and Ivy have 24, and Quake has 30, so the hits can be counted. Arthur's health refills to 100 at the start of each fight.
- The 5-second try-again countdown. RETRY starts the same fight when it is tapped.
- A sound toggle, a debug overlay, and a `v0.2` version line. Those are the features plan. A `v0.2` label on this file would look like that other build.
- Shaking Arthur himself. `Arthur Jumping` is what makes Quake's wave miss, so his y stays under the jump script. The ground shakes instead.
