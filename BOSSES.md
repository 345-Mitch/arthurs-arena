# Arthur's Arena — Boss fights

Written 2026-11-03 for Arthur.

This is a small Scratch game you can play and remix. The big Stickman Battle project it comes from is [project 732904827](https://scratch.mit.edu/projects/732904827) by onigirikun_2009. That project has a rush enemy, a fire enemy, and a demon-king fight. Those fights are long and the blocks are mostly Japanese. This file is the same kind of fights, with short English blocks.

The playable file is `projects/arthurs-arena-bosses.sb3`.

Every block in that file is also written out in `projects/BLOCK_LISTING.md`. That listing is made by the same script as the project, so the two match. To rebuild both, run:

```bash
python3 tools/build_bosses_sb3.py
```

## Load it

1. Open the [Scratch editor](https://scratch.mit.edu/projects/editor/).
2. Choose **File**, then **Load from your computer**.
3. Pick `projects/arthurs-arena-bosses.sb3`.
4. Click the green flag.

On the tablet, the file has to live on the Scratch website first. Sign in, load the file, and save. Then open that project link in the tablet browser.

## How to play

The title says **Arthur's Arena**. Arthur stands on the title and says **I'm Arthur!** His name is also drawn on his costumes.

Tap **START**.

The buttons along the bottom are the only controls. A tap on the empty stage does nothing.

| Button | What it does |
| --- | --- |
| LEFT | Step left |
| RIGHT | Step right |
| JUMP | Jump. This is how you dodge |
| PUNCH | Hit for 5 |
| KICK | Step in and hit for 8 |

You fight four people, in this order:

| Fight | Who | Health | Bar | How they attack |
| --- | --- | --- | --- | --- |
| 1 | Rival | 10 | Small gray label, bar at size 55 | Walks toward Arthur and bumps him for 6 |
| 2 | Brute | 24 | Big **BOSS** label, bar at size 100 | Charges the spot where Arthur was standing. The hit is 10 |
| 3 | Ivy | 24 | Big boss bar | Throws three shots, one at a time: low, high, low. Each hit is 8 |
| 4 | Quake | 30 | Big boss bar | Stomps. An orange wave rolls across the ground. The hit is 12. Under half health he gets faster |

Arthur's health is 100, and it fills back up at the start of each fight. His bar is the thinner one on the left. It is smaller than a boss bar.

Bars are green above 60 percent, yellow above 30, and red at 30 or below.

When a fight ends, Arthur says **Arthur wins!** After Quake, he says that and then **You are the champion!** The win backdrop says **Arthur wins!** too.

If Arthur's health reaches 0, he says **Arthur got knocked down.** Tap **RETRY** for the same fight, or **HOME** for the title.

## Boss 1 — Brute, the charge

Brute is the big red stickman.

Before the fight, his name card says **BRUTE**. He pops up huge, says **Brute!**, and glides to his side. That is the splash.

In the fight he says **Ready?** and leans back. That is the warning. He remembers where Arthur is standing, then runs to that spot. Move while he says **Ready?** and the run misses. Stand still and he hits you.

The charge loop is on Brute, under the green flag:

```
when green flag clicked
hide
forever
  if <<(Fight On) = [1]> and <(Which Fight) = [2]>> then
    set [Charge X] to (Arthur X)
    switch costume to (lean)
    say [Ready?] for [0.7] seconds
    if <(Fight On) = [1]> then
      switch costume to (charge)
      glide [0.35] secs to x: (Charge X) y: [-30]
      if <touching (Arthur) ?> then
        set [Hurt Power] to [10]
        broadcast [boss hits arthur]
        broadcast [shake]
        change y by [8]
        wait [0.06] seconds
        change y by [-8]
      end
      switch costume to (idle)
      glide [0.4] secs to x: [160] y: [-30]
    end
  else
    wait [0.1] seconds
  end
end
```

`Which Fight` is 2 for Brute. The loop is quiet during the other fights because of that check.

To make him faster, change the glide `0.35` to a smaller number. To give him more health, change both health blocks on the Boss Card (they are a pair):

```
set [Boss Max Health] to [24]
set [Boss Health] to [24]
```

## Boss 2 — Ivy, the volley

Ivy is the purple stickman. Her aim costume holds a yellow ball.

Her card says **IVY** and **Low, high, low.** She says **Ivy!** for the splash, then stands on the right.

She tells you each shot before she throws it. **Low!** means jump. **High!** means stay on the ground. The shots are one ball sprite, sent three times. There are no clones.

```
when green flag clicked
hide
forever
  if <<(Fight On) = [1]> and <(Which Fight) = [3]>> then
    wait [0.4] seconds
    switch costume to (aim)
    say [Low!] for [0.35] seconds
    set [Shot Height] to [0]
    broadcast [ivy shot] and wait
    switch costume to (aim)
    say [High!] for [0.35] seconds
    set [Shot Height] to [156]
    broadcast [ivy shot] and wait
    switch costume to (aim)
    say [Low!] for [0.35] seconds
    set [Shot Height] to [0]
    broadcast [ivy shot] and wait
    switch costume to (idle)
    wait [0.5] seconds
  else
    wait [0.1] seconds
  end
end
```

Ivy Shot listens for `ivy shot`, starts at x 150, and sets its y to `Shot Height`. It moves left. If it touches Arthur, it sets `Hurt Power` to 8 and broadcasts `boss hits arthur`.

Step in to punch between volleys. Step back before the next **Low!**

## Boss 3 — Quake, the stomp

Quake is the biggest stickman, orange, and a little taller than the others.

His card says **QUAKE**. He says **Quake!** for the splash. Then he raises his arms, says **STOMP!**, and an orange wave rolls along the ground.

Jump when he says **STOMP!** The wave hurts Arthur only when `Arthur Jumping` is 0:

```
if <<touching (Arthur) ?> and <(Arthur Jumping) = [0]>> then
  set [Hurt Power] to [12]
  broadcast [boss hits arthur]
end
```

The jump script on Arthur sets `Arthur Jumping` to 1 before he leaves the ground, and back to 0 when he lands.

At half health the stage does this:

```
if <<(Which Fight) = [4]> and <<(Quake Phase) = [1]> and <<(Boss Health) > [0]> and <(Boss Health) < ((Boss Max Health) / [2])>>>> then
  set [Quake Phase] to [2]
  set [Fight On] to [0]
  broadcast [quake angry]
  wait [1.6] seconds
  set [Fight On] to [1]
end
```

The Boss Card shows **QUAKE IS ANGRY** and says **Quake is angry!** The fight pauses while that card is up. After it, Quake's warning is shorter (`0.25` seconds instead of `0.7`) and `Wave Speed` is 26 instead of 16. The wave still misses a jump.

Half health is `Boss Max Health / 2`. If you change Quake's health on the card, the angry phase still starts at half. Set both numbers:

```
set [Boss Max Health] to [30]
set [Boss Health] to [30]
set [Quake Phase] to [1]
```

## The name card

Boss Card runs this when a fight starts. Rival (fight 1) gets a short wait and no big card. Each boss gets a costume with his name, a **Get ready!** speech bubble, and then the message `intro done`, which turns `Fight On` to 1.

The boss sprite's own `start fight` script is the splash: big size, say his name, glide to his spot, then the smaller fight size.

| Sprite | Splash size | Fight size |
| --- | --- | --- |
| Rival | none | 80 |
| Brute | 200 | 150 |
| Ivy | 180 | 130 |
| Quake | 220 | 170 |
| Arthur | 80 on the title, standing low so the title stays clear | 100 in a fight |

## Sprites and costumes

Stick figures are drawn in a box 100 wide and 180 tall. The costume center is the feet, at x 50, y 168, so `go to y: -30` stands them on the floor. Arthur's costumes have the word **Arthur** on them.

| Sprite | Costumes | Looks |
| --- | --- | --- |
| Arthur | idle, punch, kick, jump, hurt, win | Blue. Punch reaches forward. Kick reaches further |
| Rival | idle, hurt | Gray |
| Brute | idle, lean, charge, hurt | Red. Lean is the **Ready?** pose. Charge leans forward |
| Ivy | idle, aim, hurt | Purple. Aim holds a yellow ball |
| Quake | idle, raise, slam, angry, hurt | Orange. Angry is a darker red with a stern face |
| Ivy Shot | ball | Yellow ball, 24 by 24 |
| Quake Wave | wave | Orange oval, 100 by 36, on the ground at y -40 |
| Arthur Bar, Arthur Bar Back | green, yellow, red, track | 150 by 14. The colored bar uses size `(Bar Percent) * 0.7` |
| Boss Bar, Boss Bar Back | green, yellow, red, track | 240 by 22. Boss Bar Scale is 55 for Rival and 100 for a boss |
| Boss Label | RIVAL, BOSS | Small gray label, or a bigger red BOSS label |
| Boss Card | brute card, ivy card, quake card, angry card | White card, 420 by 240, with the boss name |
| Ground | floor | Wide green strip. It hops when it receives `shake` |
| Impact | marks | Three orange lines. Shows during `shake` |
| Left, Right, Jump, Punch, Kick | button | 72 by 44, with the word on the costume |
| Start Button | start, again | START on the title, AGAIN after the champion |
| Try Again | button | RETRY, only after a loss |
| Home Button | button | HOME, only after a loss |

Backdrops, on the Stage:

| Backdrop | What it shows |
| --- | --- |
| Title | Dark blue, the words **Arthur's Arena**, and **Tap Start** |
| Arena | Light blue sky, green floor, **Arthur's Arena** at the top |
| Win | Gold, the words **Arthur wins!** |
| Lose | Dark, **Arthur got knocked down.** |

## Messages

| Message | Who sends it | What it means |
| --- | --- | --- |
| show title | Stage, Home Button | Back to the title |
| start fight | Start Button, Try Again, Boss Card | Show the card and the splash |
| intro done | Boss Card | The fight can begin |
| move left, move right, punch, kick, jump | The buttons | Arthur's controls |
| arthur hits boss | Arthur | Subtract `Hit Power` from `Boss Health` |
| boss hits arthur | Rival, Brute, Ivy Shot, Quake Wave | Subtract `Hurt Power` from `Arthur Health` |
| arthur wins round | Stage | Someone's health hit 0 |
| round clear | Stage | Arthur says **Arthur wins!**, then the next fight |
| arthur champion | Stage | Quake is beaten |
| arthur loses | Stage | Arthur's health hit 0 |
| ivy shot | Ivy | Throw the ball |
| quake wave | Quake | Roll the wave |
| quake angry | Stage | Half-health card |
| shake | Brute, Quake | Ground and Impact hop. Buttons stay still |

`Game State` is set to `title`, `intro`, `fight`, `boss`, `win`, or `lose`. It is hidden. Right-click the variable in Scratch and tick the box if you want to see it.

## A few easy remixes

- Punch damage is `set [Hit Power] to [5]` on Arthur's punch script. Kick is `set [Hit Power] to [8]`.
- Brute's hit is `set [Hurt Power] to [10]`. Ivy's is 8, on Ivy Shot. Quake's is 12, on Quake Wave. Rival's is 6.
- The boss bar size for a real boss is `set [Boss Bar Scale] to [100]`. Rival is `55`. Make a boss feel bigger by leaving 100, or try 120.
- `Which Fight` is 1 Rival, 2 Brute, 3 Ivy, 4 Quake. The Boss Card is the place that sets health for each number.

The full stack for every sprite is in `projects/BLOCK_LISTING.md`.
