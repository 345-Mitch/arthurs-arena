# Arthur's Arena — Starter Guide

A stickman fighting game built in Scratch, made for Arthur to play on his Android tablet.

## Phase 1: Play the template (today)

1. Open https://scratch.mit.edu/projects/732904827 in a browser on the tablet.
2. Tap the green flag and play. Everything is tap controls — move by tapping where you want Arthur to go, tap to punch and kick.
3. Click **See inside** to peek at the blocks. No pressure to change anything yet.

## Phase 2: Make it Arthur's (this week)

- Title screen: change the backdrop text to **Arthur's Arena**.
- Hero sprite: rename it to Arthur, or redraw the stickman with his favorite colors.
- Win screen: add a say block that says **Arthur wins!** when the enemy's health hits zero.
- All of this is just text swaps and costume edits — the hardest part is finding the right sprite.

The boss project already has these three. The title backdrop says **Arthur's Arena**, the hero sprite is named Arthur and his costumes have his name on them, and he says **Arthur wins!** when a fight ends. See `BOSSES.md`.

## Phase 3: First real change (next week)

- Duplicate the enemy sprite and give it a different color so Arthur fights a rival, not a clone.
- Add a second attack: copy the punch block, change the hitbox size, and wire it to a different tap zone.
- Try a simple variable: `ArthurHealth` starting at 100, subtracting when the enemy lands a hit.

## Boss fights

`projects/arthurs-arena-bosses.sb3` is a small arena Arthur can open in Scratch and read from the inside. Load it with **File → Load from your computer**, then press the green flag.

Three bosses, after a normal rival so the boss bar is easy to see:

- **Brute** runs to the spot where Arthur was standing. Move while he says **Ready?**
- **Ivy** throws three shots, low then high then low. Jump the low ones.
- **Quake** stomps out a wave. Jump it. Under half health he gets faster, and a card says **Quake is angry!**

`BOSSES.md` is the guide. `projects/BLOCK_LISTING.md` is every block, in order. `CODEX_REVIEW.md` says what the Codex pass turned up.

## Phase 4: Android install (when it feels ready)

- Scratch's tablet app can run the project directly from the browser.
- For a proper APK install, use a Scratch-to-APK wrapper or embed the project URL in a WebView app. We'll pick the route once the game is fun enough to show off.

## Notes for Mitch

- Repo: https://github.com/345-Mitch/arthurs-arena
- Original template by onigirikun_2009, English remix by brakZ.
- Keep commits small and dated so Arthur can see the project growing.
- Security: this repo is public and contains no secrets — fine for a kid's game project.
