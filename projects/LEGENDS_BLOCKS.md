# Block listing for Arthur's Arena: Legends

Made by `tools/build_legends_sb3.py` from the same blocks that are inside
`projects/arthurs-arena-legends.sb3`. Use it to find a script in the editor.

## Stage

Costumes: Title, Select, Yard, Woods, Pass, Factory, Fortress, Bamboo, Dojo, Volcano, Castle, Arcade, Ending, Paper, brawl sky, brawl ramps, brawl pagoda, brawl pirate, brawl castle, brawl space, brawl snow, brawl candy, brawl factory, brawl towers, brawl jungle, brawl dino, brawl highway, brawl pond
Sounds: screech, honk, hit, big hit, hurt, ki roar, ki flare, transform, scribble, page, jump, whirl, swing, pickup, super, perfect, ko, charge, charged, fireball, big fireball, boom, spikes, clang, thunder, power up, alarm, poof, shuriken, spike fall, win
Sprite-only variables: SF Run, New Level, Frames, Second, AS Run, Waves, Near, I, FO Run, ED Run, HD Run, K, Pick, MI, Min X, Max X, Min Y, Max Y, Alive, Zoom To

```
when green flag clicked
set [State] to [title]
set [Fight On] to [0]
set [Score] to [0]
set [Weapon] to [none]
hide variable [Score]
hide variable [Wave]
hide variable [Best]
broadcast [intro]
```

> Green flag. Best and Crown are kept, so a saved project remembers them. The paper intro plays first.

```
when I receive [show title]
change [Session] by [1]
set [State] to [title]
set [Fight On] to [0]
set [Wave Phase] to [0]
switch backdrop to (Title)
clear graphic effects
hide variable [Score]
hide variable [Wave]
show variable [Best]
```

```
when I receive [choose hero]
set [State] to [select]
switch backdrop to (Select)
hide variable [Best]
```

```
when I receive [hero picked]
if <(Hero) = [1]> then
    set [Hero Name] to [arthur]
    set [Hero Title] to [ARTHUR]
    set [Hero Max] to [100]
    set [Step] to [22]
    set [Punch Power] to [5]
    set [Kick Power] to [8]
    set [Special Power] to [18]
    set [Special Name] to [HERO SLASH]
end
if <(Hero) = [2]> then
    set [Hero Name] to [nova]
    set [Hero Title] to [NOVA]
    set [Hero Max] to [80]
    set [Step] to [32]
    set [Punch Power] to [4]
    set [Kick Power] to [7]
    set [Special Power] to [15]
    set [Special Name] to [STAR DASH]
end
if <(Hero) = [3]> then
    set [Hero Name] to [rocko]
    set [Hero Title] to [ROCKO]
    set [Hero Max] to [130]
    set [Step] to [15]
    set [Punch Power] to [7]
    set [Kick Power] to [10]
    set [Special Power] to [22]
    set [Special Name] to [ROCK SLAM]
end
change [Hero Max] by ([10] * ((Power Level) - [1]))
set [Hero HP] to (Hero Max)
set [Score] to [0]
set [Super] to [0]
if <(Mode) = [story]> then
    set [Chapter] to [1]
    broadcast [story scene]
else
    if <(Mode) = [brawl]> then
        set [Score] to [0]
        broadcast [brawl start]
    else
        if <(Mode) = [adventure]> then
            set [Adv Stage] to [1]
            set [Lap] to [1]
            set [Score] to [0]
            broadcast [adventure stage]
        else
            set [Wave] to [1]
            broadcast [start fight]
        end
    end
end
```

> Each fighter has different health, speed, punch, kick and super.

```
when I receive [load enemy]
if <(Mode) = [practice]> then
    set [Enemy Type] to [1]
    switch backdrop to (Yard)
    set [Pace] to [1]
end
if <(Mode) = [adventure]> then
    if <(Adv Stage) = [1]> then
        set [Enemy Type] to [3]
        switch backdrop to (Yard)
    end
    if <(Adv Stage) = [2]> then
        set [Enemy Type] to [7]
        switch backdrop to (Bamboo)
    end
    if <(Adv Stage) = [3]> then
        set [Enemy Type] to [5]
        switch backdrop to (Factory)
    end
    if <(Adv Stage) = [4]> then
        set [Enemy Type] to [8]
        switch backdrop to (Volcano)
    end
    if <(Adv Stage) = [5]> then
        set [Enemy Type] to [9]
        switch backdrop to (Castle)
    end
    set [Pace] to ([1] - ([0.08] * ((Lap) - [1])))
end
if <(Mode) = [story]> then
    set [Enemy Type] to (Chapter)
    if <(Chapter) = [1]> then
        switch backdrop to (Yard)
    end
    if <(Chapter) = [2]> then
        switch backdrop to (Woods)
    end
    if <(Chapter) = [3]> then
        switch backdrop to (Pass)
    end
    if <(Chapter) = [4]> then
        switch backdrop to (Factory)
    end
    if <(Chapter) = [5]> then
        switch backdrop to (Fortress)
    end
    if <(Chapter) = [6]> then
        switch backdrop to (Bamboo)
    end
    if <(Chapter) = [7]> then
        switch backdrop to (Dojo)
    end
    if <(Chapter) = [8]> then
        switch backdrop to (Volcano)
    end
    if <(Chapter) = [9]> then
        switch backdrop to (Castle)
    end
    set [Pace] to [1]
else
    if <not <(Mode) = [arcade]>> then
    else
        if <((Wave) mod [9]) = [0]> then
            set [Enemy Type] to [9]
        else
            set [Enemy Type] to ((((Wave) - [1]) mod [9]) + [1])
        end
        switch backdrop to (Arcade)
        set [Pace] to ([8] / ([7] + (Wave)))
    end
end
if <(Enemy Type) = [1]> then
    set [Enemy Name] to [rival]
    set [Enemy Title] to [RIVAL]
    set [Enemy Max] to [24]
    set [Enemy Power] to [6]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [10]
    set [Enemy Size] to [78]
    set [Enemy Weapon] to [none]
end
if <(Enemy Type) = [2]> then
    set [Enemy Name] to [ivy]
    set [Enemy Title] to [IVY]
    set [Enemy Max] to [32]
    set [Enemy Power] to [8]
    set [Enemy Speed] to [1]
    set [Enemy Body] to [10]
    set [Enemy Size] to [82]
    set [Enemy Weapon] to [none]
end
if <(Enemy Type) = [3]> then
    set [Enemy Name] to [brute]
    set [Enemy Title] to [BRUTE]
    set [Enemy Max] to [44]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [1]
    set [Enemy Body] to [22]
    set [Enemy Size] to [110]
    set [Enemy Weapon] to [club]
end
if <(Enemy Type) = [4]> then
    set [Enemy Name] to [spikebot]
    set [Enemy Title] to [SPIKE BOT]
    set [Enemy Max] to [40]
    set [Enemy Power] to [10]
    set [Enemy Speed] to [3]
    set [Enemy Body] to [22]
    set [Enemy Size] to [100]
    set [Enemy Weapon] to [none]
end
if <(Enemy Type) = [5]> then
    set [Enemy Name] to [megaspike]
    set [Enemy Title] to [MEGA SPIKE]
    set [Enemy Max] to [80]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [34]
    set [Enemy Size] to [125]
    set [Enemy Weapon] to [mace]
end
if <(Enemy Type) = [6]> then
    set [Enemy Name] to [ninja]
    set [Enemy Title] to [NINJA]
    set [Enemy Max] to [40]
    set [Enemy Power] to [9]
    set [Enemy Speed] to [5]
    set [Enemy Body] to [12]
    set [Enemy Size] to [80]
    set [Enemy Weapon] to [katana]
end
if <(Enemy Type) = [7]> then
    set [Enemy Name] to [kage]
    set [Enemy Title] to [MASTER KAGE]
    set [Enemy Max] to [85]
    set [Enemy Power] to [11]
    set [Enemy Speed] to [6]
    set [Enemy Body] to [18]
    set [Enemy Size] to [100]
    set [Enemy Weapon] to [katana]
end
if <(Enemy Type) = [8]> then
    set [Enemy Name] to [quake]
    set [Enemy Title] to [QUAKE]
    set [Enemy Max] to [50]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [26]
    set [Enemy Size] to [120]
    set [Enemy Weapon] to [hammer]
end
if <(Enemy Type) = [9]> then
    set [Enemy Name] to [shadow]
    set [Enemy Title] to [SHADOW KING]
    set [Enemy Max] to [90]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [26]
    set [Enemy Size] to [125]
    set [Enemy Weapon] to [dark sword]
end
if <(Mode) = [adventure]> then
    set [Enemy Max] to ((Enemy Max) * ([1] + ([0.35] * ((Lap) - [1]))))
    change [Enemy Power] by ([2] * ((Lap) - [1]))
end
if <(Mode) = [arcade]> then
    change [Enemy Max] by ([8] * ((Wave) - [1]))
    change [Enemy Power] by (floor of (((Wave) - [1]) / [2]))
end
if <not <(Enemy Weapon) = [none]>> then
    change [Enemy Power] by [3]
end
if <(Difficulty) = [1]> then
    set [Enemy Max] to (round ((Enemy Max) * [1.2]))
    set [Enemy Power] to (round ((Enemy Power) * [0.75]))
    set [Pace] to ((Pace) * [1.2])
end
if <(Difficulty) = [2]> then
    set [Enemy Max] to (round ((Enemy Max) * [2]))
    set [Enemy Power] to (round ((Enemy Power) * [1]))
    set [Pace] to ((Pace) * [1])
end
if <(Difficulty) = [3]> then
    set [Enemy Max] to (round ((Enemy Max) * [2.8]))
    set [Enemy Power] to (round ((Enemy Power) * [1.25]))
    set [Pace] to ((Pace) * [0.85])
end
if <(Difficulty) = [4]> then
    set [Enemy Max] to (round ((Enemy Max) * [3.6]))
    set [Enemy Power] to (round ((Enemy Power) * [1.5]))
    set [Pace] to ((Pace) * [0.72])
end
set [Enemy Max] to (round ((Enemy Max) * ([1] + ([0.2] * ((Power Level) - [1])))))
change [Enemy Power] by ((Power Level) - [1])
set [Pace] to ((Pace) * ([1] - ([0.05] * ((Power Level) - [1]))))
set [Enemy HP] to (Enemy Max)
set [Enemy Phase] to [1]
```

> Story: the chapter picks the enemy. Arcade: waves 1-6 cycle (wave 5 is the MEGA SPIKE boss), every 7th wave is the Shadow King, and each wave is tougher and faster.

```
when I receive [start fight]
set [SF Run] to (Session)
set [Fight On] to [0]
set [State] to [fight]
broadcast [load enemy] and wait
if <not <(SF Run) = (Session)>> then
    stop [this script]
end
if <<(Mode) = [arcade]> and <(Page HUD) = [0]>> then
    show variable [Wave]
else
    if <not <(Mode) = [adventure]>> then
        set [Hero HP] to (Hero Max)
    end
end
delete all of [M X]
repeat [3]
    add [9999] to [M X]
end
if <(Page HUD) = [0]> then
    show variable [Score]
end
hide variable [Best]
set [Minions] to [0]
set [Combo] to [0]
set [Weapon] to [none]
set [Weapon Uses] to [0]
set [Boomerang Out] to [0]
set [Hero Lock] to [0]
set [Hero Safe] to [0]
set [Hero Air] to [0]
set [Spikes] to [0]
set [Charge] to [0]
set [Fireball Out] to [0]
set [Shot Live] to [0]
set [Hero Safe Until] to [0]
set [Enemy Stun Until] to [0]
broadcast [fighters ready] and wait
if <not <(SF Run) = (Session)>> then
    stop [this script]
end
broadcast [power up show] and wait
if <not <(SF Run) = (Session)>> then
    stop [this script]
end
if <<<(Enemy Type) = [5]> or <(Enemy Type) = [7]>> or <(Enemy Type) = [9]>> then
    start sound (alarm)
    set [Banner] to [boss]
    broadcast [banner]
    wait [1.5] seconds
    if <not <(SF Run) = (Session)>> then
        stop [this script]
    end
end
set [Banner] to [ready]
broadcast [banner]
wait [1.1] seconds
if <not <(SF Run) = (Session)>> then
    stop [this script]
end
set [Banner] to [fight]
broadcast [banner]
wait [0.3] seconds
if <not <(SF Run) = (Session)>> then
    stop [this script]
end
set [Want Punch] to [0]
set [Want Kick] to [0]
set [Want Jump] to [0]
set [Want Dodge] to [0]
set [Want Super] to [0]
set [Fight On] to [1]
broadcast [fight on]
if <(Mode) = [practice]> then
    set [Pop Text] to [PRACTICE: try every move!]
    broadcast [popup]
end
```

> READY... FIGHT! Taps before FIGHT! are thrown away.

```
when I receive [hero hits]
if <<<(Fight On) = [1]> and <(timer) > (Enemy Stun Until)>> and <(Wave Phase) = [0]>> then
    set [Enemy Stun Until] to ((timer) + [0.15])
    change [Hit Power] by ((Power Level) - [1])
    if <((timer) - (Combo Clock)) < [1.2]> then
        change [Combo] by [1]
    else
        set [Combo] to [1]
    end
    set [Combo Clock] to (timer)
    if <<(Combo) > [2]> and <((Combo) mod [3]) = [0]>> then
        change [Hit Power] by [3]
        set [Pop Text] to (join (join [COMBO x] (Combo)) [!])
        broadcast [popup]
    end
    change [Enemy HP] by ([0] - (Hit Power))
    change [Score] by (((Hit Power) * [10]) + ((Combo) * [5]))
    if <(Super) < [100]> then
        change [Super] by [4]
        if <not <(Super) < [100]>> then
            set [Super] to [100]
            broadcast [super ready]
        end
    end
    broadcast [enemy hurt]
    if <<<<<<(Enemy Type) = [5]> or <(Enemy Type) = [7]>> or <(Enemy Type) = [9]>> and <(Enemy Phase) = [1]>> and <(Enemy HP) > [0]>> and <(Enemy HP) < ((Enemy Max) / [2])>> then
        set [Enemy Phase] to [2]
        set [Pace] to ((Pace) * [0.7])
        broadcast [king angry]
    end
    if <(Enemy HP) < [1]> then
        if <(Mode) = [practice]> then
            set [Enemy HP] to (Enemy Max)
            set [Pop Text] to [Nice! Again!]
            broadcast [popup]
        else
            set [Enemy HP] to [0]
            set [Fight On] to [0]
            broadcast [enemy down]
        end
    end
end
```

> Hit Power is set just before this message. Hits inside 1.2 seconds build a combo; every 3rd hit is a bonus. The Shadow King gets angry at half health.

```
when I receive [enemy hits hero]
if <(Fight On) = [1]> then
    if <(Hero Safe) = [1]> then
        if <(timer) > (Perfect Until)> then
            set [Perfect Until] to ((timer) + [0.8])
            change [Super] by [25]
            if <(Super) > [99]> then
                set [Super] to [100]
            end
            change [Score] by [100]
            set [Pop Text] to [PERFECT DODGE!]
            broadcast [popup]
            start sound (perfect)
        end
    else
        if <<(Hero Safe) = [0]> and <(timer) > (Hero Safe Until)>> then
            set [Hero Safe Until] to ((timer) + [0.6])
            if <<(Weapon) = [shield]> and <(Weapon Uses) > [0]>> then
                set [Hurt Power] to (round ((Hurt Power) / [3]))
                change [Weapon Uses] by [-1]
                set [Pop Text] to [BLOCKED!]
                broadcast [popup]
                broadcast [swing sfx]
                if <(Weapon Uses) < [1]> then
                    broadcast [weapon break]
                end
            end
            change [Hero HP] by ([0] - (Hurt Power))
            set [Combo] to [0]
            if <(Super) < [100]> then
                change [Super] by [8]
                if <(Super) > [99]> then
                    set [Super] to [100]
                    broadcast [super ready]
                end
            end
            broadcast [hero hurt]
            if <(Hero HP) < [1]> then
                set [Hero HP] to [0]
                set [Fight On] to [0]
                broadcast [hero down]
            end
        end
    end
end
```

> Hurt Power is set by the attacker. Dodging at the last moment is a PERFECT DODGE: no damage and a big super boost.

```
when I receive [gain xp]
change [Power XP] by (XP Gain)
set [New Level] to [1]
if <not <(Power XP) < [0]>> then
    set [New Level] to [1]
end
if <not <(Power XP) < [3]>> then
    set [New Level] to [2]
end
if <not <(Power XP) < [7]>> then
    set [New Level] to [3]
end
if <not <(Power XP) < [12]>> then
    set [New Level] to [4]
end
if <not <(Power XP) < [18]>> then
    set [New Level] to [5]
end
if <(New Level) > (Power Level)> then
    set [Power Level] to (New Level)
    broadcast [power up]
end
```

> Win a fight: +1 XP (a boss or a brawl win: +2). At 3, 7, 12 and 18 XP your POWER LEVEL goes up: more health, harder hits, a new POWER move and a new aura colour. Enemies get stronger with you.

```
when I receive [power up]
if <(Power Level) = [1]> then
    set [Power Move] to [none]
end
if <(Power Level) = [2]> then
    set [Power Move] to [FLAME DASH]
end
if <(Power Level) = [3]> then
    set [Power Move] to [THUNDER STRIKE]
end
if <(Power Level) = [4]> then
    set [Power Move] to [BLUE STORM]
end
if <(Power Level) = [5]> then
    set [Power Move] to [ULTRA STORM]
end
start sound (power up)
set [Banner] to [power up]
broadcast [banner]
if <(State) = [fight]> then
    broadcast [power up show]
end
set [Pop Text] to (join [POWER LEVEL ] (join (Power Level) (join [: ] (Power Move))))
broadcast [popup]
repeat [4]
    set [brightness] effect to [50]
    wait [0.06] seconds
    set [brightness] effect to [0]
    wait [0.06] seconds
end
```

```
when I receive [bolt strike]
start sound (thunder)
set [brightness] effect to [70]
wait [0.05] seconds
set [brightness] effect to [25]
wait [0.05] seconds
set [brightness] effect to [0]
```

```
when I receive [power flash]
start sound (power up)
set [color] effect to [40]
wait [0.12] seconds
clear graphic effects
```

```
when [g] key pressed
set [Want Power] to [1]
```

> G: your POWER move (from power level 2).

```
when green flag clicked
forever
    sound_setvolumeto
    change [Frames] by [1]
    if <(timer) > ((Second) + [1])> then
        set [FPS] to (Frames)
        set [Frames] to [0]
        set [Second] to (timer)
    end
end
```

> Sound on/off (only the Stage plays sounds, so setting its volume is enough) and a frames-per-second count.

```
when [d] key pressed
broadcast [toggle debug]
```

> D: Mitch's debug overlay (or tap the version number on the title).

```
when I receive [toggle debug]
set [Debug] to ([1] - (Debug))
if <(Debug) = [1]> then
    show variable [FPS]
    show variable [State]
    show variable [Mode]
    show variable [Fight On]
    show variable [Hero HP]
    show variable [Enemy HP]
    show variable [Enemy Name]
    show variable [Minions]
    show variable [Power Level]
    show variable [Brawl Live]
else
    hide variable [FPS]
    hide variable [State]
    hide variable [Mode]
    hide variable [Fight On]
    hide variable [Hero HP]
    hide variable [Enemy HP]
    hide variable [Enemy Name]
    hide variable [Minions]
    hide variable [Power Level]
    hide variable [Brawl Live]
end
```

```
when I receive [adventure stage]
set [AS Run] to (Session)
set [Wave Phase] to [1]
set [Fight On] to [0]
if <(Adv Stage) = [1]> then
    set [Pop Text] to [STAGE 1: TRAINING YARD]
    set [Summon Kind] to [grunt]
end
if <(Adv Stage) = [2]> then
    set [Pop Text] to [STAGE 2: BAMBOO FOREST]
    set [Summon Kind] to [ninja]
end
if <(Adv Stage) = [3]> then
    set [Pop Text] to [STAGE 3: ROBOT FACTORY]
    set [Summon Kind] to [robot]
end
if <(Adv Stage) = [4]> then
    set [Pop Text] to [STAGE 4: VOLCANO GATE]
    set [Summon Kind] to [mix]
end
if <(Adv Stage) = [5]> then
    set [Pop Text] to [STAGE 5: SHADOW CASTLE]
    set [Summon Kind] to [mix]
end
broadcast [start fight]
wait [0.6] seconds
if <not <(AS Run) = (Session)>> then
    stop [this script]
end
broadcast [popup]
```

> ADVENTURE: a stage starts with waves of small enemies (the boss stays hidden), then the boss comes.

```
define (aim at nearest)   [run without screen refresh]
set [Near] to [99999]
set [I] to [0]
repeat [3]
    change [I] by [1]
    if <<(item (I) of [M X]) < [9000]> and <(abs of ((item (I) of [M X]) - (Hero X))) < (Near)>> then
        set [Near] to (abs of ((item (I) of [M X]) - (Hero X)))
        set [Enemy X] to (item (I) of [M X])
    end
end
```

```
when I receive [fight on]
set [FO Run] to (Session)
if <<(Mode) = [adventure]> and <(Wave Phase) = [1]>> then
    if <(Adv Stage) = [1]> then
        set [Waves] to [2]
    end
    if <(Adv Stage) = [2]> then
        set [Waves] to [2]
    end
    if <(Adv Stage) = [3]> then
        set [Waves] to [2]
    end
    if <(Adv Stage) = [4]> then
        set [Waves] to [2]
    end
    if <(Adv Stage) = [5]> then
        set [Waves] to [3]
    end
    set [Wave Num] to [0]
    repeat (Waves)
        change [Wave Num] by [1]
        if <<(Adv Stage) = [1]> and <(Wave Num) = [1]>> then
            set [Wave Total] to ([3] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [1]> and <(Wave Num) = [2]>> then
            set [Wave Total] to ([4] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [2]> and <(Wave Num) = [1]>> then
            set [Wave Total] to ([3] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [2]> and <(Wave Num) = [2]>> then
            set [Wave Total] to ([4] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [3]> and <(Wave Num) = [1]>> then
            set [Wave Total] to ([4] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [3]> and <(Wave Num) = [2]>> then
            set [Wave Total] to ([5] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [4]> and <(Wave Num) = [1]>> then
            set [Wave Total] to ([4] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [4]> and <(Wave Num) = [2]>> then
            set [Wave Total] to ([5] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [5]> and <(Wave Num) = [1]>> then
            set [Wave Total] to ([4] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [5]> and <(Wave Num) = [2]>> then
            set [Wave Total] to ([5] + ((Lap) - [1]))
        end
        if <<(Adv Stage) = [5]> and <(Wave Num) = [3]>> then
            set [Wave Total] to ([6] + ((Lap) - [1]))
        end
        set [Beaten] to [0]
        set [Spawned] to [0]
        set [Enemy Max] to (Wave Total)
        set [Enemy HP] to (Wave Total)
        set [Pop Text] to (join [WAVE ] (join (Wave Num) (join [ of ] (Waves))))
        broadcast [popup]
        repeat until <<not <(Beaten) < (Wave Total)>> or <(Fight On) = [0]>>
            if <<(Minions) < [3]> and <(Spawned) < (Wave Total)>> then
                change [Spawned] by [1]
                set [Summon Count] to [1]
                broadcast [ninja summon]
                wait [0.45] seconds
                if <not <(FO Run) = (Session)>> then
                    stop [this script]
                end
            end
            set [Enemy HP] to ((Wave Total) - (Beaten))
            (aim at nearest)
        end
        if <(Fight On) = [0]> then
            stop [this script]
        end
        wait [0.8] seconds
        if <not <(FO Run) = (Session)>> then
            stop [this script]
        end
    end
    broadcast [load enemy] and wait
    if <not <(FO Run) = (Session)>> then
        stop [this script]
    end
    set [Wave Phase] to [0]
    set [Enemy X] to [170]
    start sound (alarm)
    set [Banner] to [boss]
    broadcast [banner]
    broadcast [boss enter] and wait
    if <not <(FO Run) = (Session)>> then
        stop [this script]
    end
    wait [0.6] seconds
    if <not <(FO Run) = (Session)>> then
        stop [this script]
    end
    broadcast [fight on]
end
```

> The waves: small enemies come in (up to 3 at once) until the wave is beaten; the enemy bar shows how many are left. Then the boss arrives with a BOSS FIGHT! warning.

```
when I receive [enemy hurt]
start sound (hit)
```

```
when I receive [charge start]
start sound (charge)
```

```
when I receive [charge full]
start sound (charged)
set [Pop Text] to [FULL POWER!]
broadcast [popup]
```

```
when I receive [fire]
stop all sounds
if <(Fire Power) < [100]> then
    start sound (fireball)
else
    start sound (big fireball)
end
```

> Each stage of the fireball has its own sound: charging, full power, small or big fireball, and BOOM.

```
when I receive [boom]
start sound (boom)
```

```
when I receive [spikes out]
start sound (spikes)
```

```
when I receive [poof sfx]
start sound (poof)
```

```
when I receive [shuriken sfx]
start sound (shuriken)
```

```
when I receive [spike fall sfx]
wait [0.7] seconds
start sound (spike fall)
```

```
when I receive [spike ouch]
start sound (clang)
set [Pop Text] to [OUCH! SPIKES!]
broadcast [popup]
set [Hurt Power] to [5]
broadcast [enemy hits hero]
```

> Punching Spike Bot with bare hands while its spikes are out hurts you. Fireballs, weapons and SUPER still work.

```
when I receive [hero hurt]
start sound (hurt)
```

```
when I receive [shake]
start sound (big hit)
```

```
when I receive [weapon get]
start sound (pickup)
```

```
when I receive [swing sfx]
start sound (swing)
```

```
when I receive [whirl sfx]
start sound (whirl)
```

```
when I receive [jump sfx]
start sound (jump)
```

```
when I receive [super flash]
start sound (super)
repeat [3]
    set [brightness] effect to [40]
    wait [0.05] seconds
    set [brightness] effect to [0]
    wait [0.05] seconds
end
```

```
when I receive [king angry]
set [color] effect to [150]
wait [0.25] seconds
clear graphic effects
```

```
when I receive [enemy down]
set [ED Run] to (Session)
start sound (ko)
set [Banner] to [ko]
broadcast [banner]
wait [1.4] seconds
if <not <(ED Run) = (Session)>> then
    stop [this script]
end
if <(Mode) = [story]> then
    if <(Chapter) = [9]> then
        change [Score] by ([1000] + ((Hero HP) * [5]))
        if <(Score) > (Best)> then
            set [Best] to (Score)
        end
        set [XP Gain] to [2]
        broadcast [gain xp]
        broadcast [ending]
    else
        start sound (win)
        set [Banner] to [clear]
        broadcast [banner]
        change [Score] by ([500] + ((Hero HP) * [5]))
        set [XP Gain] to [1]
        if <<<(Enemy Type) = [5]> or <(Enemy Type) = [7]>> or <(Enemy Type) = [9]>> then
            set [XP Gain] to [2]
        end
        broadcast [gain xp]
        wait [2] seconds
        if <not <(ED Run) = (Session)>> then
            stop [this script]
        end
        change [Chapter] by [1]
        broadcast [story scene]
    end
else
    if <(Mode) = [adventure]> then
        start sound (win)
        set [Banner] to [stage clear]
        broadcast [banner]
        change [Score] by ([800] + ((Hero HP) * [5]))
        set [XP Gain] to [2]
        broadcast [gain xp]
        change [Hero HP] by [30]
        if <(Hero HP) > (Hero Max)> then
            set [Hero HP] to (Hero Max)
        end
        if <(Score) > (Best)> then
            set [Best] to (Score)
        end
        wait [2] seconds
        if <not <(ED Run) = (Session)>> then
            stop [this script]
        end
        change [Adv Stage] by [1]
        if <(Adv Stage) > [5]> then
            set [Adv Stage] to [1]
            change [Lap] by [1]
            set [Pop Text] to (join [LAP ] (join (Lap) [! Enemies are tougher!]))
            broadcast [popup]
            wait [1] seconds
            if <not <(ED Run) = (Session)>> then
                stop [this script]
            end
        end
        broadcast [adventure stage]
    else
        start sound (win)
        set [Banner] to [wave clear]
        broadcast [banner]
        change [Score] by ([200] + ((Wave) * [50]))
        set [XP Gain] to [1]
        if <<<(Enemy Type) = [5]> or <(Enemy Type) = [7]>> or <(Enemy Type) = [9]>> then
            set [XP Gain] to [2]
        end
        broadcast [gain xp]
        change [Hero HP] by [30]
        if <(Hero HP) > (Hero Max)> then
            set [Hero HP] to (Hero Max)
        end
        set [Pop Text] to [+30 HEALTH]
        broadcast [popup]
        if <(Score) > (Best)> then
            set [Best] to (Score)
        end
        wait [1.8] seconds
        if <not <(ED Run) = (Session)>> then
            stop [this script]
        end
        change [Wave] by [1]
        broadcast [start fight]
    end
end
```

> Adventure: heal and go on to the next stage. Story: next chapter, or the ending after the Shadow King. Arcade: heal a little and start the next, harder wave.

```
when I receive [hero down]
set [HD Run] to (Session)
start sound (ko)
set [State] to [over]
if <(Score) > (Best)> then
    set [Best] to (Score)
end
wait [0.6] seconds
if <not <(HD Run) = (Session)>> then
    stop [this script]
end
set [Banner] to [ko]
broadcast [banner]
wait [1.4] seconds
if <not <(HD Run) = (Session)>> then
    stop [this script]
end
broadcast [game over]
```

```
when I receive [ending]
set [State] to [ending]
switch backdrop to (Ending)
hide variable [Wave]
hide variable [Score]
```

```
when [left arrow] key pressed
broadcast [move left]
```

> Keyboard: arrows move, up or space jumps, Z punch, X kick, C dodge, V super. Hold F to charge a fireball (Hero's fire loop checks the F key).

```
when [right arrow] key pressed
broadcast [move right]
```

```
when [up arrow] key pressed
set [Want Jump] to [1]
```

```
when [space] key pressed
set [Want Jump] to [1]
```

```
when [z] key pressed
set [Want Punch] to [1]
```

```
when [x] key pressed
set [Want Kick] to [1]
```

```
when [c] key pressed
set [Want Dodge] to [1]
```

```
when [v] key pressed
set [Want Super] to [1]
```

```
when [down arrow] key pressed
set [Want Drop] to [1]
```

> BRAWL: down arrow drops through a thin platform.

```
when stage clicked
if <(State) = [intro]> then
    broadcast [skip intro]
end
```

> Tap during the intro to skip it.

```
when I receive [scribble]
start sound (scribble)
```

```
when I receive [ki rise]
start sound (ki roar)
repeat ([5] + ([2] * (Power Level)))
    broadcast [shake]
    wait [0.17] seconds
end
```

```
when I receive [ki flare]
start sound (ki flare)
```

```
when I receive [transform]
start sound (transform)
broadcast [popup]
repeat [3]
    set [brightness] effect to [90]
    wait [0.05] seconds
    set [brightness] effect to [0]
    wait [0.05] seconds
end
```

```
when I receive [color in]
start sound (pickup)
```

```
when I receive [page]
start sound (page)
```

```
define (move platforms)   [run without screen refresh]
set [K] to [0]
repeat (length of [Mv Id])
    change [K] by [1]
    set [MI] to (item (K) of [Mv Id])
    replace item (MI) of [Plat X1] with ((item (MI) of [Plat X1]) + (item (K) of [Mv V]))
    replace item (MI) of [Plat X2] with ((item (MI) of [Plat X2]) + (item (K) of [Mv V]))
    if <<(item (MI) of [Plat X1]) < (item (K) of [Mv Min])> or <(item (MI) of [Plat X1]) > (item (K) of [Mv Max])>> then
        replace item (K) of [Mv V] with ([-1] * (item (K) of [Mv V]))
    end
    replace item (MI) of [Plat Push] with (item (K) of [Mv V])
end
```

> Moving platforms (the T-Rex, the truck, the raft, the vine swing) drive back and forth.

```
when green flag clicked
forever
    if <<(Brawl Live) = [1]> and <(length of [Mv Id]) > [0]>> then
        (move platforms)
    end
end
```

> Moves the moving platforms once a frame during a BRAWL.

```
when I receive [brawl start]
set [State] to [brawl]
set [Brawl On] to [0]
set [Brawl Live] to [0]
set [Fight On] to [0]
broadcast [brawl clear] and wait
if <(Stage Pick) = [0]> then
    set [Brawl Stage] to (pick random [1] to [14])
else
    set [Brawl Stage] to (Stage Pick)
end
delete all of [Plat X1]
delete all of [Plat Y1]
delete all of [Plat X2]
delete all of [Plat Y2]
delete all of [Plat Bounce]
delete all of [Plat Push]
delete all of [Plat Art]
delete all of [Mv Id]
delete all of [Mv Min]
delete all of [Mv Max]
delete all of [Mv V]
delete all of [B X]
delete all of [B Y]
delete all of [B Dmg]
delete all of [B Stock]
delete all of [B Alive]
delete all of [B Hit]
delete all of [B KX]
delete all of [B KY]
delete all of [B Kind]
delete all of [B Pool]
if <(Brawl Stage) = [1]> then
    switch backdrop to (brawl sky)
    add [-290] to [Plat X1]
    add [-100] to [Plat Y1]
    add [290] to [Plat X2]
    add [-100] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-235] to [Plat X1]
    add [-10] to [Plat Y1]
    add [-105] to [Plat X2]
    add [-10] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [105] to [Plat X1]
    add [-10] to [Plat Y1]
    add [235] to [Plat X2]
    add [-10] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-65] to [Plat X1]
    add [78] to [Plat Y1]
    add [65] to [Plat X2]
    add [78] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [4]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [sky]
    set [Pop Text] to [SKY RUINS]
    broadcast [popup]
end
if <(Brawl Stage) = [2]> then
    switch backdrop to (brawl ramps)
    add [-340] to [Plat X1]
    add [-150] to [Plat Y1]
    add [-135] to [Plat X2]
    add [-65] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-135] to [Plat X1]
    add [-65] to [Plat Y1]
    add [135] to [Plat X2]
    add [-65] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [135] to [Plat X1]
    add [-65] to [Plat Y1]
    add [340] to [Plat X2]
    add [-150] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-215] to [Plat X1]
    add [35] to [Plat Y1]
    add [-95] to [Plat X2]
    add [35] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [95] to [Plat X1]
    add [35] to [Plat Y1]
    add [215] to [Plat X2]
    add [35] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-45] to [Plat X1]
    add [115] to [Plat Y1]
    add [45] to [Plat X2]
    add [115] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [6]
    set [Solid Count] to [3]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [ramps]
    set [Pop Text] to [RAMP VALLEY]
    broadcast [popup]
end
if <(Brawl Stage) = [3]> then
    switch backdrop to (brawl pagoda)
    add [-300] to [Plat X1]
    add [-130] to [Plat Y1]
    add [300] to [Plat X2]
    add [-130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-265] to [Plat X1]
    add [-40] to [Plat Y1]
    add [-175] to [Plat X2]
    add [5] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-175] to [Plat X1]
    add [5] to [Plat Y1]
    add [-85] to [Plat X2]
    add [-40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [85] to [Plat X1]
    add [-40] to [Plat Y1]
    add [175] to [Plat X2]
    add [5] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [175] to [Plat X1]
    add [5] to [Plat Y1]
    add [265] to [Plat X2]
    add [-40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-45] to [Plat X1]
    add [85] to [Plat Y1]
    add [45] to [Plat X2]
    add [85] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [6]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [pagoda]
    set [Pop Text] to [PAGODA ROOFS]
    broadcast [popup]
end
if <(Brawl Stage) = [4]> then
    switch backdrop to (brawl pirate)
    add [-300] to [Plat X1]
    add [-110] to [Plat Y1]
    add [300] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-205] to [Plat X1]
    add [15] to [Plat Y1]
    add [-125] to [Plat X2]
    add [15] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [125] to [Plat X1]
    add [15] to [Plat Y1]
    add [205] to [Plat X2]
    add [15] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-50] to [Plat X1]
    add [105] to [Plat Y1]
    add [50] to [Plat X2]
    add [105] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [190] to [Plat X1]
    add [-55] to [Plat Y1]
    add [300] to [Plat X2]
    add [-55] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [5]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [pirate]
    set [Pop Text] to [PIRATE SHIP]
    broadcast [popup]
end
if <(Brawl Stage) = [5]> then
    switch backdrop to (brawl castle)
    add [-310] to [Plat X1]
    add [-130] to [Plat Y1]
    add [310] to [Plat X2]
    add [-130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-290] to [Plat X1]
    add [-25] to [Plat Y1]
    add [-180] to [Plat X2]
    add [-25] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [180] to [Plat X1]
    add [-25] to [Plat Y1]
    add [290] to [Plat X2]
    add [-25] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-180] to [Plat X1]
    add [-130] to [Plat Y1]
    add [-110] to [Plat X2]
    add [-70] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-110] to [Plat X1]
    add [45] to [Plat Y1]
    add [110] to [Plat X2]
    add [45] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [110] to [Plat X1]
    add [-70] to [Plat Y1]
    add [180] to [Plat X2]
    add [-130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [6]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [castle]
    set [Pop Text] to [CASTLE WALLS]
    broadcast [popup]
end
if <(Brawl Stage) = [6]> then
    switch backdrop to (brawl space)
    add [-280] to [Plat X1]
    add [-110] to [Plat Y1]
    add [-30] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [30] to [Plat X1]
    add [-110] to [Plat Y1]
    add [280] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-25] to [Plat X1]
    add [-30] to [Plat Y1]
    add [25] to [Plat X2]
    add [-30] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-200] to [Plat X1]
    add [40] to [Plat Y1]
    add [-110] to [Plat X2]
    add [40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [110] to [Plat X1]
    add [40] to [Plat Y1]
    add [200] to [Plat X2]
    add [40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-40] to [Plat X1]
    add [130] to [Plat Y1]
    add [40] to [Plat X2]
    add [130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [6]
    set [Solid Count] to [2]
    set [Stage Grav] to [0.55]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [space]
    set [Pop Text] to [SPACE STATION]
    broadcast [popup]
end
if <(Brawl Stage) = [7]> then
    switch backdrop to (brawl snow)
    add [-320] to [Plat X1]
    add [-140] to [Plat Y1]
    add [-60] to [Plat X2]
    add [-60] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-60] to [Plat X1]
    add [-60] to [Plat Y1]
    add [60] to [Plat X2]
    add [-60] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [60] to [Plat X1]
    add [-60] to [Plat Y1]
    add [320] to [Plat X2]
    add [-140] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-230] to [Plat X1]
    add [30] to [Plat Y1]
    add [-120] to [Plat X2]
    add [30] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [120] to [Plat X1]
    add [30] to [Plat Y1]
    add [230] to [Plat X2]
    add [30] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [5]
    set [Solid Count] to [3]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.07]
    set [Stage Key] to [snow]
    set [Pop Text] to [SNOWY PEAK]
    broadcast [popup]
end
if <(Brawl Stage) = [8]> then
    switch backdrop to (brawl candy)
    add [-300] to [Plat X1]
    add [-110] to [Plat Y1]
    add [300] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-255] to [Plat X1]
    add [-45] to [Plat Y1]
    add [-195] to [Plat X2]
    add [-45] to [Plat Y2]
    add [1] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [195] to [Plat X1]
    add [-45] to [Plat Y1]
    add [255] to [Plat X2]
    add [-45] to [Plat Y2]
    add [1] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-120] to [Plat X1]
    add [40] to [Plat Y1]
    add [-40] to [Plat X2]
    add [40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [40] to [Plat X1]
    add [40] to [Plat Y1]
    add [120] to [Plat X2]
    add [40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-30] to [Plat X1]
    add [140] to [Plat Y1]
    add [30] to [Plat X2]
    add [140] to [Plat Y2]
    add [1] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [6]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [candy]
    set [Pop Text] to [CANDY LAND]
    broadcast [popup]
end
if <(Brawl Stage) = [9]> then
    switch backdrop to (brawl factory)
    add [-120] to [Plat X1]
    add [-110] to [Plat Y1]
    add [120] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-320] to [Plat X1]
    add [-110] to [Plat Y1]
    add [-120] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [1.8] to [Plat Push]
    add [0] to [Plat Art]
    add [120] to [Plat X1]
    add [-110] to [Plat Y1]
    add [320] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [-1.8] to [Plat Push]
    add [0] to [Plat Art]
    add [-220] to [Plat X1]
    add [10] to [Plat Y1]
    add [-80] to [Plat X2]
    add [10] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [1.5] to [Plat Push]
    add [0] to [Plat Art]
    add [80] to [Plat X1]
    add [10] to [Plat Y1]
    add [220] to [Plat X2]
    add [10] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [-1.5] to [Plat Push]
    add [0] to [Plat Art]
    add [-40] to [Plat X1]
    add [100] to [Plat Y1]
    add [40] to [Plat X2]
    add [100] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [6]
    set [Solid Count] to [3]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [factory]
    set [Pop Text] to [ROBOT FACTORY]
    broadcast [popup]
end
if <(Brawl Stage) = [10]> then
    switch backdrop to (brawl towers)
    add [-330] to [Plat X1]
    add [-130] to [Plat Y1]
    add [-185] to [Plat X2]
    add [-130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-185] to [Plat X1]
    add [-130] to [Plat Y1]
    add [-95] to [Plat X2]
    add [-60] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-95] to [Plat X1]
    add [-60] to [Plat Y1]
    add [95] to [Plat X2]
    add [-60] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [95] to [Plat X1]
    add [-60] to [Plat Y1]
    add [185] to [Plat X2]
    add [-130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [185] to [Plat X1]
    add [-130] to [Plat Y1]
    add [330] to [Plat X2]
    add [-130] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-300] to [Plat X1]
    add [5] to [Plat Y1]
    add [-200] to [Plat X2]
    add [5] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [200] to [Plat X1]
    add [5] to [Plat Y1]
    add [300] to [Plat X2]
    add [5] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-60] to [Plat X1]
    add [60] to [Plat Y1]
    add [60] to [Plat X2]
    add [60] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    set [Plat Count] to [8]
    set [Solid Count] to [5]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [towers]
    set [Pop Text] to [TOWER STEPS]
    broadcast [popup]
end
if <(Brawl Stage) = [11]> then
    switch backdrop to (brawl jungle)
    add [-300] to [Plat X1]
    add [-110] to [Plat Y1]
    add [300] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-260] to [Plat X1]
    add [-15] to [Plat Y1]
    add [-150] to [Plat X2]
    add [-15] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [150] to [Plat X1]
    add [-15] to [Plat Y1]
    add [260] to [Plat X2]
    add [-15] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-55] to [Plat X1]
    add [75] to [Plat Y1]
    add [55] to [Plat X2]
    add [75] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-40] to [Plat X1]
    add [-55] to [Plat Y1]
    add [40] to [Plat X2]
    add [-55] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [1] to [Plat Art]
    add [270] to [Plat X1]
    add [-70] to [Plat Y1]
    add [320] to [Plat X2]
    add [-70] to [Plat Y2]
    add [1] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [5] to [Mv Id]
    add [-230] to [Mv Min]
    add [150] to [Mv Max]
    add [1.6] to [Mv V]
    set [Plat Count] to [6]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [jungle]
    set [Pop Text] to [JUNGLE]
    broadcast [popup]
end
if <(Brawl Stage) = [12]> then
    switch backdrop to (brawl dino)
    add [-320] to [Plat X1]
    add [-120] to [Plat Y1]
    add [320] to [Plat X2]
    add [-120] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-80] to [Plat X1]
    add [-40] to [Plat Y1]
    add [70] to [Plat X2]
    add [-40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [1] to [Plat Art]
    add [-290] to [Plat X1]
    add [45] to [Plat Y1]
    add [-185] to [Plat X2]
    add [45] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [185] to [Plat X1]
    add [45] to [Plat Y1]
    add [290] to [Plat X2]
    add [45] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-45] to [Plat X1]
    add [120] to [Plat Y1]
    add [45] to [Plat X2]
    add [120] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [150] to [Plat X1]
    add [-72] to [Plat Y1]
    add [260] to [Plat X2]
    add [-72] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [1] to [Plat Art]
    add [2] to [Mv Id]
    add [-250] to [Mv Min]
    add [100] to [Mv Max]
    add [1.3] to [Mv V]
    add [6] to [Mv Id]
    add [-300] to [Mv Min]
    add [190] to [Mv Max]
    add [-0.9] to [Mv V]
    set [Plat Count] to [6]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [dino]
    set [Pop Text] to [DINO VALLEY]
    broadcast [popup]
end
if <(Brawl Stage) = [13]> then
    switch backdrop to (brawl highway)
    add [-330] to [Plat X1]
    add [-110] to [Plat Y1]
    add [330] to [Plat X2]
    add [-110] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-290] to [Plat X1]
    add [-35] to [Plat Y1]
    add [-130] to [Plat X2]
    add [40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-130] to [Plat X1]
    add [40] to [Plat Y1]
    add [130] to [Plat X2]
    add [40] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [130] to [Plat X1]
    add [40] to [Plat Y1]
    add [290] to [Plat X2]
    add [-35] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-60] to [Plat X1]
    add [72] to [Plat Y1]
    add [50] to [Plat X2]
    add [72] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [1] to [Plat Art]
    add [-300] to [Plat X1]
    add [125] to [Plat Y1]
    add [-210] to [Plat X2]
    add [125] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [210] to [Plat X1]
    add [125] to [Plat Y1]
    add [300] to [Plat X2]
    add [125] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [5] to [Mv Id]
    add [-125] to [Mv Min]
    add [15] to [Mv Max]
    add [1.2] to [Mv V]
    set [Plat Count] to [7]
    set [Solid Count] to [1]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [highway]
    set [Pop Text] to [HIGHWAY]
    broadcast [popup]
end
if <(Brawl Stage) = [14]> then
    switch backdrop to (brawl pond)
    add [-330] to [Plat X1]
    add [-100] to [Plat Y1]
    add [-120] to [Plat X2]
    add [-100] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [120] to [Plat X1]
    add [-100] to [Plat Y1]
    add [330] to [Plat X2]
    add [-100] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-50] to [Plat X1]
    add [-118] to [Plat Y1]
    add [50] to [Plat X2]
    add [-118] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [1] to [Plat Art]
    add [-245] to [Plat X1]
    add [5] to [Plat Y1]
    add [-150] to [Plat X2]
    add [5] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [150] to [Plat X1]
    add [5] to [Plat Y1]
    add [245] to [Plat X2]
    add [5] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-75] to [Plat X1]
    add [85] to [Plat Y1]
    add [75] to [Plat X2]
    add [85] to [Plat Y2]
    add [0] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [-15] to [Plat X1]
    add [-150] to [Plat Y1]
    add [15] to [Plat X2]
    add [-150] to [Plat Y2]
    add [1] to [Plat Bounce]
    add [0] to [Plat Push]
    add [0] to [Plat Art]
    add [3] to [Mv Id]
    add [-118] to [Mv Min]
    add [18] to [Mv Max]
    add [1.3] to [Mv V]
    set [Plat Count] to [7]
    set [Solid Count] to [2]
    set [Stage Grav] to [1]
    set [Stage Grip] to [0.45]
    set [Stage Key] to [pond]
    set [Pop Text] to [FISHING POND]
    broadcast [popup]
end
add [rival] to [B Pool]
add [ivy] to [B Pool]
add [brute] to [B Pool]
add [quake] to [B Pool]
add [shadow] to [B Pool]
add [ninja] to [B Pool]
add (Hero Name) to [B Kind]
if <(Net Players) = [2]> then
    add (P2 Kind) to [B Kind]
end
repeat ([3] - ([1] * <(Net Players) = [2]>))
    set [Pick] to (pick random [1] to (length of [B Pool]))
    add (item (Pick) of [B Pool]) to [B Kind]
    delete (Pick) of [B Pool]
end
delete all of [B SY]
repeat [4]
    add [-9999] to [B SY]
    add [0] to [B X]
    add [0] to [B Y]
    add [0] to [B Dmg]
    add [3] to [B Stock]
    add [1] to [B Alive]
    add [0] to [B Hit]
    add [0] to [B KX]
    add [0] to [B KY]
end
set [Cam X] to [0]
set [Cam Y] to [0]
set [Zoom] to [0.8]
set [Super] to [0]
set [Brawl Winner] to [0]
set [P2 Joy X] to [0]
set [P2 Joy Y] to [0]
set [P2 Want Jump] to [0]
set [P2 Want Drop] to [0]
set [P2 Want Punch] to [0]
set [P2 Want Kick] to [0]
set [P2 Want Super] to [0]
set [P2 Want Power] to [0]
set [P2 Want Dodge] to [0]
set [P2 Fire Held] to [0]
set [P2 Super] to [0]
set [P2 Charge] to [0]
set [P2 Power Ready At] to [0]
hide variable [Score]
hide variable [Wave]
hide variable [Best]
if <(Page HUD) = [0]> then
    show variable [P1 %]
    show variable [P2 %]
    show variable [P3 %]
    show variable [P4 %]
end
if <not <(State) = [brawl]>> then
    stop [this script]
end
set [Brawl Live] to [1]
broadcast [brawl go]
wait [0.8] seconds
if <not <(State) = [brawl]>> then
    stop [this script]
end
set [Banner] to [ready]
broadcast [banner]
wait [1.1] seconds
if <not <(State) = [brawl]>> then
    stop [this script]
end
set [Banner] to [fight]
broadcast [banner]
wait [0.3] seconds
if <not <(State) = [brawl]>> then
    stop [this script]
end
set [Want Punch] to [0]
set [Want Kick] to [0]
set [Want Jump] to [0]
set [Want Dodge] to [0]
set [Want Super] to [0]
set [Brawl On] to [1]
```

> BRAWL: picks the next stage, loads its platforms and ramps into lists, and picks 3 CPU fighters at random. Each fighter is a clone of Brawler and keeps its own place in the B lists (1 is you).

```
define (camera frame)   [run without screen refresh]
set [Min X] to [9999]
set [Max X] to [-9999]
set [Min Y] to [9999]
set [Max Y] to [-9999]
set [Alive] to [0]
set [K] to [0]
repeat [4]
    change [K] by [1]
    if <(item (K) of [B Alive]) = [1]> then
        change [Alive] by [1]
        if <(item (K) of [B X]) < (Min X)> then
            set [Min X] to (item (K) of [B X])
        end
        if <(item (K) of [B X]) > (Max X)> then
            set [Max X] to (item (K) of [B X])
        end
        if <(item (K) of [B Y]) < (Min Y)> then
            set [Min Y] to (item (K) of [B Y])
        end
        if <(item (K) of [B Y]) > (Max Y)> then
            set [Max Y] to (item (K) of [B Y])
        end
    end
end
set [P1 %] to (join (round (item [1] of [B Dmg])) [%])
set [P2 %] to (join (round (item [2] of [B Dmg])) [%])
set [P3 %] to (join (round (item [3] of [B Dmg])) [%])
set [P4 %] to (join (round (item [4] of [B Dmg])) [%])
if <(Alive) > [0]> then
    if <(Min X) < [-420]> then
        set [Min X] to [-420]
    end
    if <(Max X) > [420]> then
        set [Max X] to [420]
    end
    if <(Min Y) < [-200]> then
        set [Min Y] to [-200]
    end
    if <(Max Y) > [260]> then
        set [Max Y] to [260]
    end
    set [Zoom To] to ([420] / (((Max X) - (Min X)) + [200]))
    if <(Zoom To) > ([250] / (((Max Y) - (Min Y)) + [190]))> then
        set [Zoom To] to ([250] / (((Max Y) - (Min Y)) + [190]))
    end
    if <(Zoom To) > [1.15]> then
        set [Zoom To] to [1.15]
    end
    if <(Zoom To) < [0.5]> then
        set [Zoom To] to [0.5]
    end
    change [Zoom] by (((Zoom To) - (Zoom)) * [0.06])
    change [Cam X] by (((((Min X) + (Max X)) / [2]) - (Cam X)) * [0.1])
    change [Cam Y] by ((((((Min Y) + (Max Y)) / [2]) + [35]) - (Cam Y)) * [0.1])
end
if <<<(Brawl On) = [1]> and <not <(Net Players) = [2]>>> and <<(item [1] of [B Alive]) = [0]> or <(Alive) < [2]>>> then
    set [Brawl On] to [0]
    if <(item [1] of [B Alive]) = [1]> then
        set [Brawl Winner] to [1]
    else
        set [Brawl Winner] to [0]
    end
    broadcast [brawl end]
end
if <<<(Brawl On) = [1]> and <(Net Players) = [2]>> and <<<(item [1] of [B Alive]) = [0]> or <(item [2] of [B Alive]) = [0]>> or <(Alive) < [2]>>> then
    set [Brawl On] to [0]
    set [Brawl Winner] to [0]
    if <(item [1] of [B Alive]) = [1]> then
        set [Brawl Winner] to [1]
    end
    if <(item [2] of [B Alive]) = [1]> then
        set [Brawl Winner] to [2]
    end
    if <<(item [1] of [B Alive]) = [1]> and <(item [2] of [B Alive]) = [1]>> then
        set [Brawl Winner] to [0]
        set [K] to [0]
        repeat [4]
            change [K] by [1]
            if <(item (K) of [B Alive]) = [1]> then
                set [Brawl Winner] to (K)
            end
        end
    end
    broadcast [brawl end]
end
```

```
when green flag clicked
forever
    if <(Brawl Live) = [1]> then
        (camera frame)
    end
end
```

> The camera: finds the box around every fighter still in the game, then slides and zooms to fit it, like a platform fighter. Also copies everyone's damage into P1 % to P4 %, and ends the match when you are out or only one fighter is left.

```
when I receive [brawl end]
start sound (ko)
set [Banner] to [game]
broadcast [banner]
wait [1.8] seconds
if <not <(State) = [brawl]>> then
    stop [this script]
end
if <(Brawl Winner) = (My Slot)> then
    start sound (win)
    change [Score] by ([1000] * (Difficulty))
    set [XP Gain] to [2]
    broadcast [gain xp]
    if <(Score) > (Best)> then
        set [Best] to (Score)
    end
end
set [Brawl Live] to [0]
set [State] to [over]
broadcast [brawl clear] and wait
hide variable [P1 %]
hide variable [P2 %]
hide variable [P3 %]
hide variable [P4 %]
broadcast [game over]
```

```
when I receive [brawl clear]
set [Fire Held] to [0]
```

```
when I receive [brawl hit]
start sound (hit)
```

```
when I receive [boing]
start sound (jump)
```

```
when I receive [cannon fire]
start sound (big hit)
```

```
when I receive [honk]
start sound (honk)
```

```
when I receive [screech]
start sound (screech)
```

```
when I receive [brawl smash]
start sound (big hit)
```

```
when I receive [brawl ko]
start sound (boom)
```

```
when I receive [show title]
set [Brawl Live] to [0]
set [Brawl On] to [0]
hide variable [P1 %]
hide variable [P2 %]
hide variable [P3 %]
hide variable [P4 %]
```

```
when I receive [choose hero]
set [Brawl Live] to [0]
set [Brawl On] to [0]
hide variable [P1 %]
hide variable [P2 %]
hide variable [P3 %]
hide variable [P4 %]
```

## Debris

Costumes: rock 1, rock 2, boulder
Sprite-only variables: Is Clone, Rise

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [ki rise]
if <(Is Clone) = [0]> then
    repeat ([6] + ([4] * (Power Level)))
        go to x: ((Hero X) + (pick random ([-1] * ([80] + ([18] * (Power Level)))) to ([80] + ([18] * (Power Level))))) y: ([-75] + (pick random [-4] to [4]))
        create clone of (myself)
        wait [0.04] seconds
    end
end
```

> Rocks rip out of the ground while you power up. The higher your power level, the more rocks, the further out they come from, and from level 2 some are big boulders.

```
when I receive [ki flare]
if <(Is Clone) = [0]> then
    repeat [5]
        go to x: ((Hero X) + (pick random ([-1] * ([80] + ([18] * (Power Level)))) to ([80] + ([18] * (Power Level))))) y: ([-75] + (pick random [-4] to [4]))
        create clone of (myself)
        wait [0.07] seconds
    end
end
```

```
when I start as a clone
set [Is Clone] to [1]
set [ghost] effect to [0]
if <(pick random [1] to [6]) < (Power Level)> then
    switch costume to (boulder)
    set size to (pick random [55] to ([70] + ([14] * (Power Level)))) %
    set [Rise] to (pick random [2] to ([2] + (Power Level)))
    show
    go to [front] layer
    repeat [3]
        change x by [3]
        wait [0.03] seconds
        change x by [-3]
        wait [0.03] seconds
    end
else
    if <(pick random [1] to [2]) = [1]> then
        switch costume to (rock 1)
    else
        switch costume to (rock 2)
    end
    set size to (pick random [40] to [95]) %
    set [Rise] to (pick random [2] to ([4] + (Power Level)))
    show
    go to [front] layer
end
repeat ([18] + ([3] * (Power Level)))
    change y by (Rise)
    change x by (pick random [-1] to [1])
    turn right (pick random [3] to [11]) degrees
    wait [0.04] seconds
end
repeat [6]
    change [ghost] effect by [16]
    change y by (Rise)
    wait [0.04] seconds
end
delete this clone
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [story scene]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Ground Crack

Costumes: crack 1, crack 2, crack 3

```
when green flag clicked
hide
```

```
when I receive [ki rise]
if <(Power Level) > [1]> then
    if <(Power Level) > [3]> then
        switch costume to (crack 3)
    else
        if <(Power Level) > [2]> then
            switch costume to (crack 2)
        else
            switch costume to (crack 1)
        end
    end
    go to x: (Hero X) y: ([-75] - [4])
    set size to [30] %
    set [ghost] effect to [0]
    show
    go to [back] layer
    repeat [10]
        change size by ([5] + ([2] * (Power Level)))
        wait [0.04] seconds
    end
    wait ([0.6] + ([0.2] * (Power Level))) seconds
    repeat [10]
        change [ghost] effect by [10]
        wait [0.04] seconds
    end
    hide
end
```

> From power level 2 the ground cracks open under you. It gets wider every level.

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [brawl clear]
hide
```

```
when I receive [brawl start]
hide
```

## Shockwave

Costumes: ring

```
when green flag clicked
hide
```

```
when I receive [shockwave]
go to x: (Hero X) y: ([-75] + [6])
set size to [20] %
set [ghost] effect to [0]
show
go to [front] layer
repeat [14]
    change size by ([8] + ([4] * (Power Level)))
    change [ghost] effect by [7]
    wait [0.03] seconds
end
hide
```

> A ring of power blasts out along the ground (power level 2 and up, and when you transform).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [brawl clear]
hide
```

```
when I receive [brawl start]
hide
```

## Swirl

Costumes: swirl 1, swirl 2

```
when green flag clicked
hide
set [ghost] effect to [15]
forever
    if <<(Swirl On) = [1]> and <(State) = [fight]>> then
        go to x: (Hero X) y: ((Hero Y) + [40])
        if <((round ((timer) * [20])) mod [2]) = [0]> then
            switch costume to (swirl 1)
        else
            switch costume to (swirl 2)
        end
        show
        go to [front] layer
    else
        hide
    end
end
```

> Whirling motion lines round the WHIRLWIND and HELICOPTER KICKs.

## Ki Spark

Costumes: lv1, lv2, lv3, lv4, lv5
Sprite-only variables: Is Clone, Rise, Spread

```
define (spawn ki)   [run without screen refresh]
set [Spread] to ([26] + ([7] * (Power Level)))
repeat ([1] + (floor of (([1] + (Power Level)) * (([20] + (Ki)) / [100]))))
    go to x: ((Hero X) + (pick random ([-1] * (Spread)) to (Spread))) y: ((Hero Y) + (pick random [-5] to [45]))
    create clone of (myself)
end
```

```
when green flag clicked
hide
set [Is Clone] to [0]
forever
    if <<<(Is Clone) = [0]> and <(Powering) > [0]>> and <(State) = [fight]>> then
        (spawn ki)
    end
end
```

> While powering up, streaks of energy shoot upward round the hero. More of them, bigger and faster as the power builds, and more each power level.

```
when I start as a clone
set [Is Clone] to [1]
switch costume to (join [lv] (Power Level))
set size to (pick random [45] to ([70] + ([14] * (Power Level)))) %
set [Rise] to ((pick random [5] to [9]) + ((Power Level) + ((Ki) / [25])))
set [ghost] effect to [10]
show
go to [front] layer
repeat ([8] + (Power Level))
    change y by (Rise)
    change [ghost] effect by [9]
end
delete this clone
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [story scene]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [brawl start]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [enemy down]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [hero down]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Ki Dim

Costumes: dark
Sprite-only variables: Dim

```
when green flag clicked
hide
set [Dim] to [0]
forever
    if <<(Powering) = [1]> and <(State) = [fight]>> then
        set [Dim] to ((Ki) * ([0.14] + ([0.05] * (Power Level))))
        go to x: [0] y: [0]
        set [ghost] effect to ([100] - (Dim))
        show
        go to [back] layer
    else
        if <(Dim) > [0]> then
            change [Dim] by [-3]
            set [ghost] effect to ([100] - (Dim))
        else
            hide
        end
    end
end
```

> While powering up the backdrop darkens a little more each moment (and more each power level), so the aura blazes out of the dark.

## Ki Rays

Costumes: lv1, lv2, lv3, lv4, lv5

```
when green flag clicked
hide
```

```
when I receive [ki burst]
switch costume to (join [lv] (Power Level))
go to x: (Hero X) y: ((Hero Y) + [62])
set size to [20] %
point in direction [90]
set [ghost] effect to [15]
show
go to [front] layer
repeat ([10] + (Power Level))
    change size by ([10] + ([5] * (Power Level)))
    turn right [4] degrees
    change [ghost] effect by [7]
end
hide
```

> The peak of a power-up: a burst of light rays, bigger with more rays each power level.

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [brawl start]
hide
```

## Power Fist

Costumes: punch, kick

```
when green flag clicked
hide
forever
    if <<(Melee Charge) > [0]> and <(State) = [fight]>> then
        go to x: ((Hero X) + ((Glow DX) * (Facing))) y: ((Hero Y) + (Glow DY))
        switch costume to (Glow Kind)
        set size to ([25] + ((Melee Charge) * [0.75])) %
        turn right [15] degrees
        if <(Melee Charge) = [100]> then
            set [brightness] effect to ([35] * ((round ((timer) * [10])) mod [2]))
        else
            set [brightness] effect to [0]
        end
        show
        go to [front] layer
    else
        hide
    end
end
```

> Hold PUNCH or KICK: power gathers in your fist (gold) or foot (blue) and grows until you let go.

## Sketch

Costumes: frame 1, frame 2, frame 3, frame 4, frame 5, frame 6, frame 7, frame 8, frame 9, frame 10, frame 11, frame 12, frame 13, frame 14, frame 15, frame 16, frame 17, frame 18, frame 19, frame 20, frame 21, frame 22, frame 23, frame 24, frame 25, frame 26, frame 27, frame 28, frame 29, frame 30, frame 31, frame 32, frame 33, frame 34, frame 35, frame 36, frame 37, frame 38, frame 39, frame 40, frame 41, frame 42, frame 43, frame 44, frame 45, frame 46, frame 47, frame 48, frame 49, frame 50, frame 51, frame 52

```
when green flag clicked
hide
```

```
when I receive [intro]
set [State] to [intro]
switch backdrop to (Paper)
go to x: [0] y: [0]
set [ghost] effect to [0]
show
go to [front] layer
wait [0.2] seconds
switch costume to (frame 1)
set [Pen X] to [-176.6]
set [Pen Y] to [12]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 2)
set [Pen X] to [-141.4]
set [Pen Y] to [12]
wait [0.03] seconds
switch costume to (frame 3)
set [Pen X] to [-159]
set [Pen Y] to [-33.1]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 4)
set [Pen X] to [-159]
set [Pen Y] to [-58.4]
wait [0.03] seconds
switch costume to (frame 5)
set [Pen X] to [-141]
set [Pen Y] to [8.7]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 6)
set [Pen X] to [-132.6]
set [Pen Y] to [31.8]
wait [0.03] seconds
switch costume to (frame 7)
set [Pen X] to [-177]
set [Pen Y] to [8.7]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 8)
set [Pen X] to [-185.4]
set [Pen Y] to [31.8]
wait [0.03] seconds
switch costume to (frame 9)
set [Pen X] to [-150.3]
set [Pen Y] to [-88.9]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 10)
set [Pen X] to [-143.6]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 11)
set [Pen X] to [-167.7]
set [Pen Y] to [-88.9]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 12)
set [Pen X] to [-174.4]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 13)
set [Pen X] to [-55.8]
set [Pen Y] to [13.1]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 14)
set [Pen X] to [-20.6]
set [Pen Y] to [13.1]
wait [0.03] seconds
switch costume to (frame 15)
set [Pen X] to [-42.7]
set [Pen Y] to [-31.6]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 16)
set [Pen X] to [-47]
set [Pen Y] to [-56.2]
wait [0.03] seconds
switch costume to (frame 17)
set [Pen X] to [-18.4]
set [Pen Y] to [-14.4]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 18)
set [Pen X] to [4.7]
set [Pen Y] to [-12.2]
wait [0.03] seconds
switch costume to (frame 19)
set [Pen X] to [-49.9]
set [Pen Y] to [-24.8]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 20)
set [Pen X] to [-40.4]
set [Pen Y] to [-14.4]
wait [0.03] seconds
switch costume to (frame 21)
set [Pen X] to [-30.9]
set [Pen Y] to [-86.9]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 22)
set [Pen X] to [-20.6]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 23)
set [Pen X] to [-60.4]
set [Pen Y] to [-87.6]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 24)
set [Pen X] to [-71.2]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 25)
set [Pen X] to [36.4]
set [Pen Y] to [9.8]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 26)
set [Pen X] to [71.6]
set [Pen Y] to [9.8]
wait [0.03] seconds
switch costume to (frame 27)
set [Pen X] to [59.9]
set [Pen Y] to [-33.8]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 28)
set [Pen X] to [65]
set [Pen Y] to [-58.4]
wait [0.03] seconds
switch costume to (frame 29)
set [Pen X] to [68.9]
set [Pen Y] to [-22.5]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 30)
set [Pen X] to [78.2]
set [Pen Y] to [-12.2]
wait [0.03] seconds
switch costume to (frame 31)
set [Pen X] to [43.3]
set [Pen Y] to [-20.8]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 32)
set [Pen X] to [32]
set [Pen Y] to [-34.2]
wait [0.03] seconds
switch costume to (frame 33)
set [Pen X] to [92.3]
set [Pen Y] to [-58.2]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 34)
set [Pen X] to [118.9]
set [Pen Y] to [-51.8]
wait [0.03] seconds
switch costume to (frame 35)
set [Pen X] to [60.6]
set [Pen Y] to [-89.2]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 36)
set [Pen X] to [56.2]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 37)
set [Pen X] to [164.4]
set [Pen Y] to [9.8]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 38)
set [Pen X] to [199.6]
set [Pen Y] to [9.8]
wait [0.03] seconds
switch costume to (frame 39)
set [Pen X] to [175.3]
set [Pen Y] to [-34.4]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 40)
set [Pen X] to [168.8]
set [Pen Y] to [-58.4]
wait [0.03] seconds
switch costume to (frame 41)
set [Pen X] to [199.1]
set [Pen Y] to [-24.7]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 42)
set [Pen X] to [217.2]
set [Pen Y] to [-40.8]
wait [0.03] seconds
switch costume to (frame 43)
set [Pen X] to [167.1]
set [Pen Y] to [-22.7]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 44)
set [Pen X] to [173.2]
set [Pen Y] to [-36.4]
wait [0.03] seconds
switch costume to (frame 45)
set [Pen X] to [186.8]
set [Pen Y] to [-87.9]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 46)
set [Pen X] to [199.6]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 47)
set [Pen X] to [155.6]
set [Pen Y] to [-89.2]
broadcast [scribble]
wait [0.03] seconds
switch costume to (frame 48)
set [Pen X] to [142.4]
set [Pen Y] to [-120]
wait [0.03] seconds
switch costume to (frame 49)
set [Pen X] to [999]
broadcast [color in]
wait [0.3] seconds
switch costume to (frame 50)
set [Pen X] to [999]
broadcast [color in]
wait [0.3] seconds
switch costume to (frame 51)
set [Pen X] to [999]
broadcast [color in]
wait [0.3] seconds
switch costume to (frame 52)
set [Pen X] to [999]
broadcast [color in]
wait [0.3] seconds
wait [0.6] seconds
broadcast [page]
repeat [8]
    change [ghost] effect by [12]
    change x by [-40]
    wait [0.03] seconds
end
hide
set [Pen X] to [999]
broadcast [show title]
```

> The intro: a pencil draws Arthur, Nova and Rocko on notebook paper, stroke by stroke, then colours them in and turns the page to the title. Tap anywhere to skip.

```
when I receive [skip intro]
stop [other scripts in sprite]
hide
set [Pen X] to [999]
broadcast [show title]
```

```
when this sprite clicked
if <(State) = [intro]> then
    broadcast [skip intro]
end
```

## Pencil

Costumes: pencil

```
when green flag clicked
hide
forever
    if <<(State) = [intro]> and <(Pen X) < [900]>> then
        go to x: (Pen X) y: (Pen Y)
        show
        go to [front] layer
    else
        hide
    end
end
```

> The pencil follows the line being drawn.

## Skip Intro

Costumes: skip

```
when green flag clicked
hide
```

```
when I receive [intro]
go to x: [196] y: [-156]
show
go to [front] layer
```

```
when I receive [show title]
hide
```

```
when this sprite clicked
hide
broadcast [skip intro]
```

> Skip the drawing and go straight to the title.

## Ground Shake

Costumes: shadow

```
when green flag clicked
go to x: [0] y: [-80]
show
```

```
when I receive [brawl start]
hide
```

```
when I receive [intro]
hide
```

```
when I receive [start fight]
show
```

```
when I receive [show title]
show
```

```
when I receive [shake]
repeat [3]
    go to x: [0] y: [-76]
    wait [0.04] seconds
    go to x: [0] y: [-84]
    wait [0.04] seconds
end
go to x: [0] y: [-80]
```

## Hero

Costumes: arthur idle, arthur punch, arthur kick, arthur jump, arthur hurt, arthur win, arthur dodge, arthur special, arthur down, arthur charge, arthur idle b, arthur walk 1, arthur walk 2, arthur walk 3, arthur walk 4, arthur punch 1, arthur kick 1, arthur hurt high, arthur charge up, arthur spin 1, arthur spin 2, arthur spin 3, arthur spin 4, arthur heli 1, arthur heli 2, arthur heli 3, arthur heli 4, arthur sky kick, arthur windup, arthur flip 1, arthur flip 2, arthur flip 3, arthur flip 4, arthur gold idle, arthur gold punch, arthur gold kick, arthur gold jump, arthur gold hurt, arthur gold win, arthur gold dodge, arthur gold special, arthur gold down, arthur gold charge, arthur gold idle b, arthur gold walk 1, arthur gold walk 2, arthur gold walk 3, arthur gold walk 4, arthur gold punch 1, arthur gold kick 1, arthur gold hurt high, arthur gold charge up, arthur gold spin 1, arthur gold spin 2, arthur gold spin 3, arthur gold spin 4, arthur gold heli 1, arthur gold heli 2, arthur gold heli 3, arthur gold heli 4, arthur gold sky kick, arthur gold windup, arthur gold flip 1, arthur gold flip 2, arthur gold flip 3, arthur gold flip 4, arthur silver idle, arthur silver punch, arthur silver kick, arthur silver jump, arthur silver hurt, arthur silver win, arthur silver dodge, arthur silver special, arthur silver down, arthur silver charge, arthur silver idle b, arthur silver walk 1, arthur silver walk 2, arthur silver walk 3, arthur silver walk 4, arthur silver punch 1, arthur silver kick 1, arthur silver hurt high, arthur silver charge up, arthur silver spin 1, arthur silver spin 2, arthur silver spin 3, arthur silver spin 4, arthur silver heli 1, arthur silver heli 2, arthur silver heli 3, arthur silver heli 4, arthur silver sky kick, arthur silver windup, arthur silver flip 1, arthur silver flip 2, arthur silver flip 3, arthur silver flip 4, nova idle, nova punch, nova kick, nova jump, nova hurt, nova win, nova dodge, nova special, nova down, nova charge, nova idle b, nova walk 1, nova walk 2, nova walk 3, nova walk 4, nova punch 1, nova kick 1, nova hurt high, nova charge up, nova spin 1, nova spin 2, nova spin 3, nova spin 4, nova heli 1, nova heli 2, nova heli 3, nova heli 4, nova sky kick, nova windup, nova flip 1, nova flip 2, nova flip 3, nova flip 4, nova gold idle, nova gold punch, nova gold kick, nova gold jump, nova gold hurt, nova gold win, nova gold dodge, nova gold special, nova gold down, nova gold charge, nova gold idle b, nova gold walk 1, nova gold walk 2, nova gold walk 3, nova gold walk 4, nova gold punch 1, nova gold kick 1, nova gold hurt high, nova gold charge up, nova gold spin 1, nova gold spin 2, nova gold spin 3, nova gold spin 4, nova gold heli 1, nova gold heli 2, nova gold heli 3, nova gold heli 4, nova gold sky kick, nova gold windup, nova gold flip 1, nova gold flip 2, nova gold flip 3, nova gold flip 4, nova silver idle, nova silver punch, nova silver kick, nova silver jump, nova silver hurt, nova silver win, nova silver dodge, nova silver special, nova silver down, nova silver charge, nova silver idle b, nova silver walk 1, nova silver walk 2, nova silver walk 3, nova silver walk 4, nova silver punch 1, nova silver kick 1, nova silver hurt high, nova silver charge up, nova silver spin 1, nova silver spin 2, nova silver spin 3, nova silver spin 4, nova silver heli 1, nova silver heli 2, nova silver heli 3, nova silver heli 4, nova silver sky kick, nova silver windup, nova silver flip 1, nova silver flip 2, nova silver flip 3, nova silver flip 4, rocko idle, rocko punch, rocko kick, rocko jump, rocko hurt, rocko win, rocko dodge, rocko special, rocko down, rocko charge, rocko idle b, rocko walk 1, rocko walk 2, rocko walk 3, rocko walk 4, rocko punch 1, rocko kick 1, rocko hurt high, rocko charge up, rocko spin 1, rocko spin 2, rocko spin 3, rocko spin 4, rocko heli 1, rocko heli 2, rocko heli 3, rocko heli 4, rocko sky kick, rocko windup, rocko flip 1, rocko flip 2, rocko flip 3, rocko flip 4, rocko gold idle, rocko gold punch, rocko gold kick, rocko gold jump, rocko gold hurt, rocko gold win, rocko gold dodge, rocko gold special, rocko gold down, rocko gold charge, rocko gold idle b, rocko gold walk 1, rocko gold walk 2, rocko gold walk 3, rocko gold walk 4, rocko gold punch 1, rocko gold kick 1, rocko gold hurt high, rocko gold charge up, rocko gold spin 1, rocko gold spin 2, rocko gold spin 3, rocko gold spin 4, rocko gold heli 1, rocko gold heli 2, rocko gold heli 3, rocko gold heli 4, rocko gold sky kick, rocko gold windup, rocko gold flip 1, rocko gold flip 2, rocko gold flip 3, rocko gold flip 4, rocko silver idle, rocko silver punch, rocko silver kick, rocko silver jump, rocko silver hurt, rocko silver win, rocko silver dodge, rocko silver special, rocko silver down, rocko silver charge, rocko silver idle b, rocko silver walk 1, rocko silver walk 2, rocko silver walk 3, rocko silver walk 4, rocko silver punch 1, rocko silver kick 1, rocko silver hurt high, rocko silver charge up, rocko silver spin 1, rocko silver spin 2, rocko silver spin 3, rocko silver spin 4, rocko silver heli 1, rocko silver heli 2, rocko silver heli 3, rocko silver heli 4, rocko silver sky kick, rocko silver windup, rocko silver flip 1, rocko silver flip 2, rocko silver flip 3, rocko silver flip 4
Sprite-only variables: Last X, HVY, HVX, Hold Dir, Spin, Jumps, Flip, Look, Hold Until, Kick Queued, Line Until

```
when green flag clicked
set rotation style [left-right]
point in direction [90]
forever
    set [Hero X] to (x position)
    set [Hero Y] to (y position)
    if <<(Fight On) = [1]> and <(Hero Lock) = [0]>> then
        if <(timer) < (Turn Until)> then
            if <(Turn Dir) > [0]> then
                point in direction [90]
                set [Facing] to [1]
            else
                point in direction [-90]
                set [Facing] to [-1]
            end
        else
            if <(Enemy X) < ((x position) - [4])> then
                point in direction [-90]
                set [Facing] to [-1]
            else
                if <(Enemy X) > ((x position) + [4])> then
                    point in direction [90]
                    set [Facing] to [1]
                end
            end
        end
    end
end
```

> Hero X and Hero Y are read by everyone else. In a fight, Hero faces the way you are walking, then turns back to face the enemy, so you can fight ninjas on both sides.

```
when green flag clicked
forever
    set [Look] to (costume name)
    if <<<(State) = [fight]> or <(State) = [story]>> and <<(Look) contains [idle]?> or <(Look) contains [walk]?>>> then
        if <<(Hero Air) = [0]> and <(abs of ((x position) - (Last X))) > [0.6]>> then
            switch costume to (join (Hero Look) (join [ walk ] ((floor of ((((x position) + [1000]) / [11]) mod [4])) + [1])))
        else
            if <((round ((timer) * [1.6])) mod [2]) = [0]> then
                switch costume to (join (Hero Look) [ idle])
            else
                switch costume to (join (Hero Look) [ idle b])
            end
        end
    end
    set [Last X] to (x position)
end
```

> Makes the stick figure feel alive: breathing while standing, a 4-step walk cycle while moving. It only changes the standing and walking pictures, never a punch or a kick.

```
when green flag clicked
forever
    if <(Fight On) = [1]> then
        if <<(Want Super) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Super] to [0]
            if <<(Super) = [100]> and <(Hero Air) = [0]>> then
                set [Hero Lock] to [1]
                set [Hero Safe] to [2]
                set [Super] to [0]
                set [Pop Text] to (join (Special Name) [!])
                broadcast [popup]
                broadcast [super flash]
                switch costume to (join (Hero Look) [ special])
                wait [0.35] seconds
                if <(Hero) = [1]> then
                    glide [0.18] secs to x: ((Enemy X) - ([45] * (Facing))) y: [-75]
                    set [Hit Power] to (Special Power)
                    broadcast [hero hits]
                    if <(Minions) > [0]> then
                        set [Area X] to (Hero X)
                        set [Area R] to [90]
                        set [Area Power] to (Special Power)
                        set [Area Kind] to [hit]
                        broadcast [area hit]
                    end
                    broadcast [shake]
                    wait [0.4] seconds
                end
                if <(Hero) = [2]> then
                    repeat [3]
                        glide [0.1] secs to x: ((Enemy X) - ([40] * (Facing))) y: [-75]
                        switch costume to (join (Hero Look) [ kick])
                        set [Hit Power] to (round ((Special Power) / [3]))
                        broadcast [hero hits]
                        if <(Minions) > [0]> then
                            set [Area X] to (Hero X)
                            set [Area R] to [90]
                            set [Area Power] to (round ((Special Power) / [3]))
                            set [Area Kind] to [hit]
                            broadcast [area hit]
                        end
                        wait [0.2] seconds
                        switch costume to (join (Hero Look) [ special])
                        move [-40] steps
                        if <(x position) < [-215]> then
                            set x to [-215]
                        end
                        if <(x position) > [215]> then
                            set x to [215]
                        end
                    end
                end
                if <(Hero) = [3]> then
                    switch costume to (join (Hero Look) [ jump])
                    repeat [6]
                        change y by [18]
                    end
                    glide [0.15] secs to x: ((Enemy X) - ([40] * (Facing))) y: [-75]
                    switch costume to (join (Hero Look) [ special])
                    set [Hit Power] to (Special Power)
                    broadcast [hero hits]
                    if <(Minions) > [0]> then
                        set [Area X] to (Hero X)
                        set [Area R] to [90]
                        set [Area Power] to (Special Power)
                        set [Area Kind] to [hit]
                        broadcast [area hit]
                    end
                    broadcast [shake]
                    wait [0.4] seconds
                end
                set y to [-75]
                if <(x position) < [-215]> then
                    set x to [-215]
                end
                if <(x position) > [215]> then
                    set x to [215]
                end
                switch costume to (join (Hero Look) [ idle])
                set [Hero Safe] to [0]
                set [Hero Lock] to [0]
            end
        end
        if <<(Want Power) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Power] to [0]
            if <<<(Power Level) > [1]> and <(timer) > (Power Ready At)>> and <(Hero Air) = [0]>> then
                set [Hero Lock] to [1]
                set [Hero Safe] to [2]
                set [Power Ready At] to ((timer) + [6])
                switch costume to (join (Hero Look) [ charge up])
                set [Powering] to [1]
                broadcast [ki flare]
                say [HAA!] for [0.3] seconds
                set [Powering] to [0]
                if <(Power Level) = [1]> then
                    set [Power Move] to [none]
                end
                if <(Power Level) = [2]> then
                    set [Power Move] to [FLAME DASH]
                end
                if <(Power Level) = [3]> then
                    set [Power Move] to [THUNDER STRIKE]
                end
                if <(Power Level) = [4]> then
                    set [Power Move] to [BLUE STORM]
                end
                if <(Power Level) = [5]> then
                    set [Power Move] to [ULTRA STORM]
                end
                set [Pop Text] to (join (Power Move) [!])
                broadcast [popup]
                broadcast [power flash]
                if <(Power Level) = [2]> then
                    switch costume to (join (Hero Look) [ special])
                    glide [0.16] secs to x: ((Enemy X) + ([45] * (Facing))) y: [-75]
                    if <(x position) < [-215]> then
                        set x to [-215]
                    end
                    if <(x position) > [215]> then
                        set x to [215]
                    end
                    set [Hit Power] to [9]
                    broadcast [hero hits]
                    if <(Minions) > [0]> then
                        set [Area X] to (Hero X)
                        set [Area R] to [90]
                        set [Area Power] to [9]
                        set [Area Kind] to [hit]
                        broadcast [area hit]
                    end
                    broadcast [shake]
                    wait [0.3] seconds
                end
                if <(Power Level) = [3]> then
                    switch costume to (join (Hero Look) [ win])
                    wait [0.2] seconds
                    set [Bolt X] to (Enemy X)
                    set [Bolt Y] to [-75]
                    set [Bolt Owner] to [hero]
                    set [Bolt Power] to [13]
                    set [Bolt Size] to [100]
                    broadcast [bolt]
                    wait [0.55] seconds
                end
                if <(Power Level) = [4]> then
                    switch costume to (join (Hero Look) [ win])
                    wait [0.15] seconds
                    repeat [3]
                        set [Bolt X] to ((Enemy X) + (pick random [-18] to [18]))
                        set [Bolt Y] to [-75]
                        set [Bolt Owner] to [hero]
                        set [Bolt Power] to [7]
                        set [Bolt Size] to [100]
                        broadcast [bolt]
                        wait [0.25] seconds
                    end
                    wait [0.3] seconds
                end
                if <(Power Level) = [5]> then
                    switch costume to (join (Hero Look) [ win])
                    wait [0.15] seconds
                    repeat [4]
                        set [Bolt X] to ((Enemy X) + (pick random [-30] to [30]))
                        set [Bolt Y] to [-75]
                        set [Bolt Owner] to [hero]
                        set [Bolt Power] to [6]
                        set [Bolt Size] to [100]
                        broadcast [bolt]
                        wait [0.2] seconds
                    end
                    set [Bolt X] to (Enemy X)
                    set [Bolt Y] to [-75]
                    set [Bolt Owner] to [hero]
                    set [Bolt Power] to [14]
                    set [Bolt Size] to [100]
                    broadcast [bolt]
                    broadcast [shake]
                    wait [0.4] seconds
                end
                set y to [-75]
                switch costume to (join (Hero Look) [ idle])
                set [Hero Safe] to [0]
                set [Hero Lock] to [0]
            else
                if <(Power Level) = [1]> then
                    set [Pop Text] to [Win fights to unlock POWER!]
                    broadcast [popup]
                end
            end
        end
        if <<(Want Punch) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Punch] to [0]
            set [Hold Until] to ((timer) + [0.22])
            repeat until <<<not <<(Punch Held) = [1]> or <key (z) pressed?>>> or <(timer) > (Hold Until)>> or <(Fight On) = [0]>>
            end
            if <<<(Punch Held) = [1]> or <key (z) pressed?>> and <(Fight On) = [1]>> then
                set [Hero Lock] to [1]
                set [Melee Charge] to [1]
                set [Glow Kind] to [punch]
                set [Glow DX] to [-20]
                set [Glow DY] to [84]
                switch costume to (join (Hero Look) [ windup])
                broadcast [charge start]
                repeat until <<not <<(Punch Held) = [1]> or <key (z) pressed?>>> or <(Fight On) = [0]>>
                    if <(Melee Charge) < [100]> then
                        change [Melee Charge] by [3]
                        if <not <(Melee Charge) < [100]>> then
                            set [Melee Charge] to [100]
                            broadcast [charge full]
                        end
                    end
                    change x by (((((round ((timer) * [30])) mod [2]) * [2]) - [1]) * ((Melee Charge) / [40]))
                end
                if <(Fight On) = [1]> then
                    set [Hit Power] to (((Punch Power) + (Weapon Bonus)) + (round ((Melee Charge) / [9])))
                    set [Pop Text] to [METEOR PUNCH!]
                    broadcast [popup]
                    broadcast [whirl sfx]
                    set [Glow DX] to [36]
                    set [Glow DY] to [74]
                    switch costume to (join (Hero Look) [ punch])
                    repeat [6]
                        move ([4] + ((Melee Charge) / [12])) steps
                        if <(x position) < [-215]> then
                            set x to [-215]
                        end
                        if <(x position) > [215]> then
                            set x to [215]
                        end
                    end
                    if <(Weapon Bonus) > [0]> then
                        change [Weapon Uses] by [-1]
                        broadcast [swing]
                    else
                        broadcast [swing sfx]
                    end
                    if <(abs of ((Enemy X) - (Hero X))) < (([80] + (Weapon Reach)) + (Enemy Body))> then
                        if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                            broadcast [spike ouch]
                        else
                            broadcast [hero hits]
                            if <(Weapon) = [hammer]> then
                                broadcast [shake]
                            end
                        end
                    end
                    if <(Minions) > [0]> then
                        set [Area X] to ((Hero X) + ((Facing) * [49]))
                        set [Area R] to [49]
                        set [Area Power] to (Hit Power)
                        set [Area Kind] to [hit]
                        broadcast [area hit]
                    end
                    if <(Melee Charge) = [100]> then
                        broadcast [shake]
                        broadcast [ki flare]
                    end
                    wait [0.25] seconds
                end
                set [Melee Charge] to [0]
                if <<<not <(Weapon) = [none]>> and <(Weapon Uses) < [1]>> and <(Boomerang Out) = [0]>> then
                    broadcast [weapon break]
                end
                if <(Hero Air) = [1]> then
                    switch costume to (join (Hero Look) [ jump])
                else
                    switch costume to (join (Hero Look) [ idle])
                end
                set [Hero Lock] to [0]
                wait until <not <<(Punch Held) = [1]> or <key (z) pressed?>>>
                set [Punch Held] to [0]
                set [Want Punch] to [0]
            else
                switch costume to (join (Hero Look) [ punch 1])
                wait [0.06] seconds
                switch costume to (join (Hero Look) [ punch])
                if <<(Weapon) = [boomerang]> and <(Boomerang Out) = [0]>> then
                    set [Boomerang Out] to [1]
                    change [Weapon Uses] by [-1]
                    broadcast [throw boomerang]
                    broadcast [swing sfx]
                else
                    set [Hit Power] to ((Punch Power) + (Weapon Bonus))
                    if <(Weapon Bonus) > [0]> then
                        change [Weapon Uses] by [-1]
                        broadcast [swing]
                    else
                        broadcast [swing sfx]
                    end
                    if <(abs of ((Enemy X) - (Hero X))) < (([70] + (Weapon Reach)) + (Enemy Body))> then
                        if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                            broadcast [spike ouch]
                        else
                            broadcast [hero hits]
                            if <(Weapon) = [hammer]> then
                                broadcast [shake]
                            end
                        end
                    end
                    if <(Minions) > [0]> then
                        set [Area X] to ((Hero X) + ((Facing) * [38.5]))
                        set [Area R] to [38.5]
                        set [Area Power] to (Hit Power)
                        set [Area Kind] to [hit]
                        broadcast [area hit]
                    end
                    if <(Weapon) = [nunchucks]> then
                        wait [0.17] seconds
                        switch costume to (join (Hero Look) [ punch 1])
                        wait [0.04] seconds
                        switch costume to (join (Hero Look) [ punch])
                        broadcast [swing]
                        if <(abs of ((Enemy X) - (Hero X))) < (([70] + (Weapon Reach)) + (Enemy Body))> then
                            if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                                broadcast [spike ouch]
                            else
                                broadcast [hero hits]
                                if <(Weapon) = [hammer]> then
                                    broadcast [shake]
                                end
                            end
                        end
                        if <(Minions) > [0]> then
                            set [Area X] to ((Hero X) + ((Facing) * [38.5]))
                            set [Area R] to [38.5]
                            set [Area Power] to (Hit Power)
                            set [Area Kind] to [hit]
                            broadcast [area hit]
                        end
                    end
                end
                wait [0.16] seconds
                if <<<not <(Weapon) = [none]>> and <(Weapon Uses) < [1]>> and <(Boomerang Out) = [0]>> then
                    broadcast [weapon break]
                end
                if <(Hero Air) = [1]> then
                    switch costume to (join (Hero Look) [ jump])
                else
                    switch costume to (join (Hero Look) [ idle])
                end
            end
        end
        if <<(Want Kick) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Kick] to [0]
            if <<<((timer) - (Kick At)) < [0.8]> or <(Kick Queued) = [1]>> and <(timer) > (Whirl Ready At)>> then
                set [Kick At] to [0]
                set [Kick Queued] to [0]
                if <(Hero Air) = [1]> then
                    set [Hero Lock] to [1]
                    set [Whirl Ready At] to ((timer) + [1.2])
                    set [Pop Text] to [HELICOPTER KICK!]
                    broadcast [popup]
                    broadcast [whirl sfx]
                    set [HVY] to [7]
                    set [Jumps] to [2]
                    set [Flip] to [0]
                    set [Spin] to [0]
                    set [Swirl On] to [1]
                    repeat until <<<(Spin) > [30]> or <(Hero Air) = [0]>> or <(Fight On) = [0]>>
                        change [Spin] by [1]
                        switch costume to (join (Hero Look) (join [ heli ] (((Spin) mod [4]) + [1])))
                        if <(HVY) < [-1]> then
                            set [HVY] to [-1]
                        end
                        move [5] steps
                        if <(x position) < [-215]> then
                            set x to [-215]
                        end
                        if <(x position) > [215]> then
                            set x to [215]
                        end
                        if <((Spin) mod [5]) = [1]> then
                            set [Hit Power] to [3]
                            if <(abs of ((Enemy X) - (Hero X))) < ([70] + (Enemy Body))> then
                                if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                                    broadcast [spike ouch]
                                else
                                    broadcast [hero hits]
                                    if <(Weapon) = [hammer]> then
                                        broadcast [shake]
                                    end
                                end
                            end
                            if <(Minions) > [0]> then
                                set [Area X] to (Hero X)
                                set [Area R] to [70]
                                set [Area Power] to [3]
                                set [Area Kind] to [hit]
                                broadcast [area hit]
                            end
                        end
                        if <((Spin) mod [10]) = [0]> then
                            broadcast [whirl sfx]
                        end
                    end
                    set [Swirl On] to [0]
                    if <(Hero Air) = [1]> then
                        switch costume to (join (Hero Look) [ jump])
                    else
                        switch costume to (join (Hero Look) [ idle])
                    end
                    set [Hero Lock] to [0]
                else
                    set [Hero Lock] to [1]
                    set [Whirl Ready At] to ((timer) + [1.2])
                    set [Pop Text] to [WHIRLWIND KICK!]
                    broadcast [popup]
                    broadcast [whirl sfx]
                    if <(Hero Air) = [0]> then
                        change y by [16]
                    end
                    set [Spin] to [0]
                    set [Swirl On] to [1]
                    repeat [15]
                        change [Spin] by [1]
                        switch costume to (join (Hero Look) (join [ spin ] (((floor of ((Spin) / [2])) mod [4]) + [1])))
                        move [7] steps
                        if <(x position) < [-215]> then
                            set x to [-215]
                        end
                        if <(x position) > [215]> then
                            set x to [215]
                        end
                        if <((Spin) mod [5]) = [1]> then
                            set [Hit Power] to [4]
                            if <(abs of ((Enemy X) - (Hero X))) < ([64] + (Enemy Body))> then
                                if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                                    broadcast [spike ouch]
                                else
                                    broadcast [hero hits]
                                    if <(Weapon) = [hammer]> then
                                        broadcast [shake]
                                    end
                                end
                            end
                            if <(Minions) > [0]> then
                                set [Area X] to (Hero X)
                                set [Area R] to [64]
                                set [Area Power] to [4]
                                set [Area Kind] to [hit]
                                broadcast [area hit]
                            end
                        end
                    end
                    set [Swirl On] to [0]
                    if <(Hero Air) = [0]> then
                        set y to [-75]
                    end
                    if <(Hero Air) = [1]> then
                        switch costume to (join (Hero Look) [ jump])
                    else
                        switch costume to (join (Hero Look) [ idle])
                    end
                    set [Hero Lock] to [0]
                end
            else
                set [Kick Queued] to [0]
                set [Hold Until] to ((timer) + [0.22])
                repeat until <<<not <<(Kick Held) = [1]> or <key (x) pressed?>>> or <(timer) > (Hold Until)>> or <(Fight On) = [0]>>
                end
                if <<<(Kick Held) = [1]> or <key (x) pressed?>> and <(Fight On) = [1]>> then
                    set [Hero Lock] to [1]
                    set [Melee Charge] to [1]
                    set [Glow Kind] to [kick]
                    set [Glow DX] to [12]
                    set [Glow DY] to [40]
                    switch costume to (join (Hero Look) [ kick 1])
                    broadcast [charge start]
                    repeat until <<not <<(Kick Held) = [1]> or <key (x) pressed?>>> or <(Fight On) = [0]>>
                        if <(Melee Charge) < [100]> then
                            change [Melee Charge] by [3]
                            if <not <(Melee Charge) < [100]>> then
                                set [Melee Charge] to [100]
                                broadcast [charge full]
                            end
                        end
                        change x by (((((round ((timer) * [30])) mod [2]) * [2]) - [1]) * ((Melee Charge) / [40]))
                    end
                    if <(Fight On) = [1]> then
                        set [Hit Power] to (((Kick Power) + (Weapon Bonus)) + (round ((Melee Charge) / [12])))
                        set [Pop Text] to [SKY KICK!]
                        broadcast [popup]
                        broadcast [whirl sfx]
                        set [Glow DX] to [26]
                        set [Glow DY] to [76]
                        switch costume to (join (Hero Look) [ sky kick])
                        if <(Weapon Bonus) > [0]> then
                            change [Weapon Uses] by [-1]
                            broadcast [swing]
                        else
                            broadcast [swing sfx]
                        end
                        if <(Hero Air) = [0]> then
                            set [Hero Air] to [1]
                        end
                        set [Jumps] to [2]
                        set [Flip] to [0]
                        set [HVY] to ([9] + ((Melee Charge) / [14]))
                        repeat [4]
                            move [5] steps
                            if <(x position) < [-215]> then
                                set x to [-215]
                            end
                            if <(x position) > [215]> then
                                set x to [215]
                            end
                        end
                        if <(abs of ((Enemy X) - (Hero X))) < (([82] + (Weapon Reach)) + (Enemy Body))> then
                            if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                                broadcast [spike ouch]
                            else
                                broadcast [hero hits]
                                if <(Weapon) = [hammer]> then
                                    broadcast [shake]
                                end
                            end
                        end
                        if <(Minions) > [0]> then
                            set [Area X] to ((Hero X) + ((Facing) * [49.199999999999996]))
                            set [Area R] to [49.199999999999996]
                            set [Area Power] to (Hit Power)
                            set [Area Kind] to [hit]
                            broadcast [area hit]
                        end
                        repeat [5]
                            move [3] steps
                            if <(x position) < [-215]> then
                                set x to [-215]
                            end
                            if <(x position) > [215]> then
                                set x to [215]
                            end
                        end
                        set [Hit Power] to (round ((Hit Power) / [2]))
                        if <(abs of ((Enemy X) - (Hero X))) < (([82] + (Weapon Reach)) + (Enemy Body))> then
                            if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                                broadcast [spike ouch]
                            else
                                broadcast [hero hits]
                                if <(Weapon) = [hammer]> then
                                    broadcast [shake]
                                end
                            end
                        end
                        if <(Minions) > [0]> then
                            set [Area X] to ((Hero X) + ((Facing) * [49.199999999999996]))
                            set [Area R] to [49.199999999999996]
                            set [Area Power] to (Hit Power)
                            set [Area Kind] to [hit]
                            broadcast [area hit]
                        end
                        if <(Melee Charge) = [100]> then
                            broadcast [shake]
                            broadcast [ki flare]
                        end
                        wait [0.2] seconds
                    end
                    set [Melee Charge] to [0]
                    if <<<not <(Weapon) = [none]>> and <(Weapon Uses) < [1]>> and <(Boomerang Out) = [0]>> then
                        broadcast [weapon break]
                    end
                    if <(Hero Air) = [1]> then
                        switch costume to (join (Hero Look) [ jump])
                    else
                        switch costume to (join (Hero Look) [ idle])
                    end
                    set [Hero Lock] to [0]
                    wait until <not <<(Kick Held) = [1]> or <key (x) pressed?>>>
                    set [Kick Held] to [0]
                    set [Want Kick] to [0]
                else
                    set [Kick At] to (timer)
                    switch costume to (join (Hero Look) [ kick 1])
                    wait [0.07] seconds
                    switch costume to (join (Hero Look) [ kick])
                    move [14] steps
                    if <(x position) < [-215]> then
                        set x to [-215]
                    end
                    if <(x position) > [215]> then
                        set x to [215]
                    end
                    set [Hit Power] to ((Kick Power) + (Weapon Bonus))
                    if <(Weapon Bonus) > [0]> then
                        change [Weapon Uses] by [-1]
                        broadcast [swing]
                    else
                        broadcast [swing sfx]
                    end
                    if <(abs of ((Enemy X) - (Hero X))) < (([82] + (Weapon Reach)) + (Enemy Body))> then
                        if <<(Spikes) = [1]> and <(Weapon Bonus) = [0]>> then
                            broadcast [spike ouch]
                        else
                            broadcast [hero hits]
                            if <(Weapon) = [hammer]> then
                                broadcast [shake]
                            end
                        end
                    end
                    if <(Minions) > [0]> then
                        set [Area X] to ((Hero X) + ((Facing) * [45.1]))
                        set [Area R] to [45.1]
                        set [Area Power] to (Hit Power)
                        set [Area Kind] to [hit]
                        broadcast [area hit]
                    end
                    wait [0.22] seconds
                    move [-14] steps
                    if <(x position) < [-215]> then
                        set x to [-215]
                    end
                    if <(x position) > [215]> then
                        set x to [215]
                    end
                    if <<<not <(Weapon) = [none]>> and <(Weapon Uses) < [1]>> and <(Boomerang Out) = [0]>> then
                        broadcast [weapon break]
                    end
                    if <(Hero Air) = [1]> then
                        switch costume to (join (Hero Look) [ jump])
                    else
                        switch costume to (join (Hero Look) [ idle])
                    end
                    if <(Want Kick) = [1]> then
                        set [Kick Queued] to [1]
                    end
                end
            end
        end
        if <<(Want Dodge) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Dodge] to [0]
            if <(Hero Air) = [0]> then
                set [Hero Lock] to [1]
                set [Hero Safe] to [1]
                switch costume to (join (Hero Look) [ dodge])
                set [ghost] effect to [45]
                broadcast [swing sfx]
                repeat [6]
                    move [-10] steps
                    if <(x position) < [-215]> then
                        set x to [-215]
                    end
                    if <(x position) > [215]> then
                        set x to [215]
                    end
                end
                wait [0.14] seconds
                set [ghost] effect to [0]
                set [Hero Safe] to [0]
                switch costume to (join (Hero Look) [ idle])
                set [Hero Lock] to [0]
                wait [0.12] seconds
            end
        end
    else
        if <not <(State) = [brawl]>> then
            set [Want Punch] to [0]
            set [Want Kick] to [0]
            set [Want Dodge] to [0]
            set [Want Super] to [0]
            set [Want Power] to [0]
        end
    end
end
```

> The action loop. Buttons only set Want Punch, Want Kick and so on; this loop does one move at a time. A tap during a move waits its turn (a short input buffer, like big fighting games).

```
when green flag clicked
forever
    if <<(Want Jump) = [1]> and <not <(State) = [brawl]>>> then
        set [Want Jump] to [0]
        if <<(Fight On) = [1]> and <(Hero Lock) = [0]>> then
            if <(timer) < (Turn Until)> then
                set [Hold Dir] to (Turn Dir)
            else
                set [Hold Dir] to [0]
            end
            if <(Hero Air) = [0]> then
                set [Hero Air] to [1]
                set [Jumps] to [1]
                set [HVY] to [15]
                switch costume to (join (Hero Look) [ jump])
                broadcast [jump sfx]
                set [HVX] to ((Hold Dir) * [4])
            else
                if <(Jumps) = [1]> then
                    set [Jumps] to [2]
                    set [HVY] to [11]
                    set [Flip] to [16]
                    set [HVX] to ((Hold Dir) * [8])
                    broadcast [jump sfx]
                end
            end
        end
    end
    if <(Hero Air) = [1]> then
        change y by (HVY)
        change [HVY] by [-1.3]
        change x by (HVX)
        if <(x position) < [-215]> then
            set x to [-215]
        end
        if <(x position) > [215]> then
            set x to [215]
        end
        set [HVX] to ((HVX) * [0.96])
        if <(Flip) > [0]> then
            change [Flip] by [-1]
            if <<<(Hero Lock) = [0]> and <not <(costume name) contains [punch]?>>> and <not <(costume name) contains [kick]?>>> then
                if <(Flip) > [0]> then
                    switch costume to (join (Hero Look) (join [ flip ] ((floor of ((([16] - (Flip)) / [4]) mod [4])) + [1])))
                else
                    switch costume to (join (Hero Look) [ jump])
                end
            end
        end
        if <not <(y position) > [-75]>> then
            set y to [-75]
            set [Hero Air] to [0]
            set [Jumps] to [0]
            set [HVY] to [0]
            set [Flip] to [0]
            set [HVX] to [0]
            if <(Hero Lock) = [0]> then
                switch costume to (join (Hero Look) [ idle])
            end
        end
    end
end
```

> The jump loop runs beside the action loop, so you can punch and kick in the air. Tap JUMP again while in the air for a second jump with a front flip. Hold a direction when you jump and you also fly that way (further on the flip).

```
when green flag clicked
forever
    if <<<<(Fight On) = [1]> and <(Fireball Out) = [0]>> and <(Hero Lock) = [0]>> and <<(Fire Held) = [1]> or <key (f) pressed?>>> then
        set [Charge] to [1]
        broadcast [charge start]
        switch costume to (join (Hero Look) [ charge])
        repeat until <<<not <<(Fire Held) = [1]> or <key (f) pressed?>>> or <(Fight On) = [0]>> or <(Hero Lock) = [1]>>
            if <(Charge) < [100]> then
                change [Charge] by [3.5]
                if <not <(Charge) < [100]>> then
                    set [Charge] to [100]
                    broadcast [charge full]
                end
            end
        end
        set [Fire Held] to [0]
        if <<(Fight On) = [1]> and <(Hero Lock) = [0]>> then
            set [Fire Power] to (Charge)
            set [Charge] to [0]
            set [Fireball Out] to [1]
            broadcast [fire]
            switch costume to (join (Hero Look) [ punch])
            wait [0.15] seconds
            if <(Hero Air) = [1]> then
                switch costume to (join (Hero Look) [ jump])
            else
                switch costume to (join (Hero Look) [ idle])
            end
        end
        set [Charge] to [0]
    end
end
```

> The fire loop. Hold FIRE (or F) to charge; let go to shoot. A quick tap is a small fireball; a full charge (about 1 second) is a giant one that explodes.

```
when green flag clicked
forever
    if <<<(Fight On) = [1]> and <(Hero Lock) = [0]>> and <(abs of (Joy X)) > [0.2]>> then
        change x by (((Joy X) * (Step)) * [0.28])
        if <(x position) < [-215]> then
            set x to [-215]
        end
        if <(x position) > [215]> then
            set x to [215]
        end
        set [Turn Dir] to (Joy X)
        set [Turn Until] to ((timer) + [0.3])
    end
end
```

> Joystick walking. The Android app's joystick sets Joy X from -1 (left) to 1 (right) and Hero walks every frame. Faster fighters walk faster.

```
when I receive [move left]
if <<(Fight On) = [1]> and <(Hero Lock) = [0]>> then
    change x by ([-1] * (Step))
    if <(x position) < [-215]> then
        set x to [-215]
    end
    if <(x position) > [215]> then
        set x to [215]
    end
    set [Turn Dir] to [-1]
    set [Turn Until] to ((timer) + [0.45])
end
```

```
when I receive [move right]
if <<(Fight On) = [1]> and <(Hero Lock) = [0]>> then
    change x by ([1] * (Step))
    if <(x position) < [-215]> then
        set x to [-215]
    end
    if <(x position) > [215]> then
        set x to [215]
    end
    set [Turn Dir] to [1]
    set [Turn Until] to ((timer) + [0.45])
end
```

```
when I receive [hero hurt]
if <(Hero Lock) = [0]> then
    if <(pick random [1] to [2]) = [1]> then
        switch costume to (join (Hero Look) [ hurt])
    else
        switch costume to (join (Hero Look) [ hurt high])
    end
    move [-12] steps
    if <(x position) < [-215]> then
        set x to [-215]
    end
    if <(x position) > [215]> then
        set x to [215]
    end
end
set [color] effect to [60]
wait [0.15] seconds
set [color] effect to [0]
if <(Hero Lock) = [0]> then
    if <(Hero Air) = [1]> then
        switch costume to (join (Hero Look) [ jump])
    else
        switch costume to (join (Hero Look) [ idle])
    end
end
```

```
when I receive [show title]
show
clear graphic effects
point in direction [90]
set [Hero Name] to [arthur]
switch costume to (arthur idle)
go to x: [-212] y: [-75]
set size to [90] %
go to [front] layer
say [I'm Arthur!] for [2] seconds
```

```
when I receive [choose hero]
hide
```

```
when I receive [intro]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [fighters ready]
show
clear graphic effects
point in direction [90]
set [Facing] to [1]
set [Hero Look] to (Hero Name)
switch costume to (join (Hero Look) [ idle])
set size to [75] %
go to x: [-150] y: [-75]
if <(Hero) = [1]> then
    say [I'm Arthur!] for [1] seconds
end
if <(Hero) = [2]> then
    say [Too slow!] for [1] seconds
end
if <(Hero) = [3]> then
    say [Rock solid!] for [1] seconds
end
```

> Each fighter has a catchphrase before READY... FIGHT!

```
when I receive [scene setup]
show
clear graphic effects
point in direction [90]
set [Hero Look] to (Hero Name)
switch costume to (join (Hero Look) [ idle])
set size to [75] %
go to x: [-150] y: [-75]
```

```
when I receive [power up show]
set [Hero Lock] to [1]
switch costume to (join (Hero Look) [ charge up])
say [Hmmmm...] for [0.45] seconds
set [Ki] to [0]
set [Powering] to [1]
broadcast [ki rise]
say [HAAAAAA!]
if <(Power Level) > [1]> then
    broadcast [shockwave]
end
repeat ([9] + (Power Level))
    change [Ki] by ([100] / ([9] + (Power Level)))
    set [brightness] effect to ((Ki) * ([0.08] + ([0.05] * (Power Level))))
    change x by ([1] + (Power Level))
    wait [0.04] seconds
    change x by ([-1] * ([1] + (Power Level)))
    wait [0.04] seconds
end
set [Ki] to [100]
broadcast [ki burst]
if <(Power Level) > [2]> then
    if <(Power Level) > [4]> then
        set [Hero Look] to (join (Hero Name) [ silver])
    else
        set [Hero Look] to (join (Hero Name) [ gold])
    end
    if <(Power Level) > [4]> then
        set [Pop Text] to (join [ULTRA ] (join (Hero Title) [!]))
    else
        set [Pop Text] to (join [SUPER ] (join (Hero Title) [!]))
    end
    switch costume to (join (Hero Look) [ charge up])
    broadcast [transform]
    broadcast [shockwave]
    broadcast [ki burst]
end
repeat [4]
    change x by [2]
    wait [0.04] seconds
    change x by [-2]
    wait [0.04] seconds
end
say []
set [Powering] to [0]
set [Ki] to [0]
set [brightness] effect to [0]
switch costume to (join (Hero Look) [ idle])
set [Hero Lock] to [0]
```

> Powering up, Dragon Ball style: crouch, yell HAAAAA!, and the power builds: the aura grows from a flicker to a blaze, energy streams upward, the screen darkens and the hero glows, then a burst of light. The ground shakes and rocks float up. From power level 3 the hair turns golden (silver at level 5) for the rest of the fight.

```
when I receive [super ready]
if <<(Fight On) = [1]> and <(Powering) = [0]>> then
    set [Powering] to [2]
    broadcast [ki flare]
    wait [0.8] seconds
    if <(Powering) = [2]> then
        set [Powering] to [0]
    end
end
```

> A quick flare of power when the SUPER bar fills up. You can keep fighting while it flares.

```
when I receive [hero line]
say (Line)
set [Line Until] to ((timer) + (Line Secs))
wait until <<(timer) > (Line Until)> or <(Skip) = [1]>>
say []
```

```
when I receive [enemy down]
wait [1.3] seconds
set y to [-75]
clear graphic effects
switch costume to (join (Hero Look) [ win])
if <(Mode) = [story]> then
    say [Yes!] for [1.2] seconds
else
    say (join [Wave ] (join (Wave) [ clear!])) for [1.2] seconds
end
```

```
when I receive [hero down]
set y to [-75]
clear graphic effects
switch costume to (join (Hero Look) [ down])
```

```
when I receive [ending]
point in direction [90]
go to x: [-170] y: [-75]
switch costume to (join (Hero Look) [ win])
```

## Enemy

Costumes: rival idle, rival windup, rival attack, rival hurt, rival down, rival idle b, rival walk 1, rival walk 2, rival walk 3, rival walk 4, rival hurt high, ivy idle, ivy windup, ivy attack, ivy hurt, ivy down, ivy idle b, ivy walk 1, ivy walk 2, ivy walk 3, ivy walk 4, ivy hurt high, brute idle, brute windup, brute attack, brute hurt, brute down, brute idle b, brute walk 1, brute walk 2, brute walk 3, brute walk 4, brute hurt high, spikebot idle, spikebot windup, spikebot attack, spikebot hurt, spikebot down, spikebot idle b, spikebot walk 1, spikebot walk 2, spikebot walk 3, spikebot walk 4, spikebot hurt high, megaspike idle, megaspike windup, megaspike attack, megaspike hurt, megaspike down, megaspike idle b, megaspike walk 1, megaspike walk 2, megaspike walk 3, megaspike walk 4, megaspike hurt high, ninja idle, ninja windup, ninja attack, ninja hurt, ninja down, ninja idle b, ninja walk 1, ninja walk 2, ninja walk 3, ninja walk 4, ninja hurt high, kage idle, kage windup, kage attack, kage hurt, kage down, kage idle b, kage walk 1, kage walk 2, kage walk 3, kage walk 4, kage hurt high, quake idle, quake windup, quake attack, quake hurt, quake down, quake idle b, quake walk 1, quake walk 2, quake walk 3, quake walk 4, quake hurt high, shadow idle, shadow windup, shadow attack, shadow hurt, shadow down, shadow idle b, shadow walk 1, shadow walk 2, shadow walk 3, shadow walk 4, shadow hurt high, shadow angry, shadow spikes
Sprite-only variables: Pick, Line Until, Last X, Look

```
when green flag clicked
forever
    set [Look] to (costume name)
    if <<(State) = [fight]> and <<(Look) contains [idle]?> or <(Look) contains [walk]?>>> then
        if <(abs of ((x position) - (Last X))) > [0.6]> then
            switch costume to (join (Enemy Name) (join [ walk ] ((floor of ((((x position) + [1000]) / [11]) mod [4])) + [1])))
        else
            if <((round ((timer) * [1.4])) mod [2]) = [0]> then
                switch costume to (join (Enemy Name) [ idle])
            else
                switch costume to (join (Enemy Name) [ idle b])
            end
        end
    end
    set [Last X] to (x position)
end
```

> Enemies breathe while they wait and walk with a stride cycle.

```
when green flag clicked
set rotation style [left-right]
hide
forever
    if <(Wave Phase) = [0]> then
        set [Enemy X] to (x position)
    end
end
```

> Enemy X is read by Hero and the weapons.

```
when I receive [fight on]
repeat until <(Fight On) = [0]>
    if <(Hero X) < (x position)> then
        point in direction [-90]
        set [Enemy Facing] to [-1]
    else
        point in direction [90]
        set [Enemy Facing] to [1]
    end
    if <<<(timer) < (Enemy Stun Until)> or <(Mode) = [practice]>> or <(Wave Phase) = [1]>> then
        wait [0.05] seconds
    else
        if <(Enemy Type) = [1]> then
            if <<(abs of ((Hero X) - (x position))) < ([38] + (Enemy Body))> and <((Hero Y) - [-75]) < [60]>> then
                switch costume to (join (Enemy Name) [ attack])
                set [Enemy Swing Until] to ((timer) + [0.3])
                set [Hurt Power] to (Enemy Power)
                broadcast [enemy hits hero]
                wait ([0.3] * (Pace)) seconds
                switch costume to (join (Enemy Name) [ idle])
                wait ([0.45] * (Pace)) seconds
            else
                move (Enemy Speed) steps
                if <(x position) < [-210]> then
                    set x to [-210]
                end
                if <(x position) > [210]> then
                    set x to [210]
                end
                wait [0.03] seconds
            end
        end
        if <(Enemy Type) = [2]> then
            if <(abs of ((Hero X) - (x position))) < [130]> then
                glide [0.35] secs to x: ((x position) + ([-110] * (Enemy Facing))) y: [-75]
                if <(x position) < [-205]> then
                    set x to [-205]
                end
                if <(x position) > [205]> then
                    set x to [205]
                end
                if <(Hero X) < (x position)> then
                    point in direction [-90]
                    set [Enemy Facing] to [-1]
                else
                    point in direction [90]
                    set [Enemy Facing] to [1]
                end
            end
            wait ([0.35] * (Pace)) seconds
            if <(pick random [1] to [2]) = [1]> then
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [Low!]
                wait ([0.45] * (Pace)) seconds
                set [Enemy Says] to []
                set [Shot Y] to [-57]
                set [Shot Dir] to (Enemy Facing)
                switch costume to (join (Enemy Name) [ attack])
                broadcast [enemy shot] and wait
                switch costume to (join (Enemy Name) [ idle])
            else
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [High!]
                wait ([0.45] * (Pace)) seconds
                set [Enemy Says] to []
                set [Shot Y] to [50]
                set [Shot Dir] to (Enemy Facing)
                switch costume to (join (Enemy Name) [ attack])
                broadcast [enemy shot] and wait
                switch costume to (join (Enemy Name) [ idle])
            end
            wait ([0.55] * (Pace)) seconds
        end
        if <(Enemy Type) = [3]> then
            switch costume to (join (Enemy Name) [ windup])
            set [Enemy Says] to [Ready?]
            wait ([0.75] * (Pace)) seconds
            set [Enemy Says] to []
            set [Pick] to (Hero X)
            switch costume to (join (Enemy Name) [ attack])
            broadcast [swing sfx]
            set [Enemy Swing Until] to ((timer) + [0.3])
            glide ([0.4] * (Pace)) secs to x: (Pick) y: [-75]
            if <<(abs of ((Hero X) - (x position))) < ([34] + (Enemy Body))> and <((Hero Y) - [-75]) < [50]>> then
                set [Enemy Swing Until] to ((timer) + [0.3])
                set [Hurt Power] to (Enemy Power)
                broadcast [enemy hits hero]
                broadcast [shake]
            end
            switch costume to (join (Enemy Name) [ idle])
            wait ([0.45] * (Pace)) seconds
            glide [0.5] secs to x: ((x position) + ([-100] * (Enemy Facing))) y: [-75]
            if <(x position) < [-205]> then
                set x to [-205]
            end
            if <(x position) > [205]> then
                set x to [205]
            end
            wait ([0.3] * (Pace)) seconds
        end
        if <(Enemy Type) = [4]> then
            switch costume to (join (Enemy Name) [ windup])
            set [Enemy Says] to [SPIKES OUT!]
            wait ([0.55] * (Pace)) seconds
            set [Enemy Says] to []
            set [Spikes] to [1]
            switch costume to (join (Enemy Name) [ attack])
            broadcast [spikes out]
            set [Pick] to [0]
            repeat until <<(Pick) > [40]> or <(Fight On) = [0]>>
                change [Pick] by [1]
                move ((Enemy Speed) * [2]) steps
                if <(x position) < [-210]> then
                    set x to [-210]
                end
                if <(x position) > [210]> then
                    set x to [210]
                end
                if <<(x position) > [209]> or <(x position) < [-209]>> then
                    set [Pick] to [99]
                end
                if <<(abs of ((Hero X) - (x position))) < ([30] + (Enemy Body))> and <((Hero Y) - [-75]) < [55]>> then
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    set [Hurt Power] to (Enemy Power)
                    broadcast [enemy hits hero]
                    broadcast [shake]
                    set [Pick] to [99]
                end
            end
            set [Spikes] to [0]
            switch costume to (join (Enemy Name) [ idle])
            set [Enemy Says] to [Cooling down...]
            wait ([1.7] * (Pace)) seconds
            set [Enemy Says] to []
        end
        if <(Enemy Type) = [5]> then
            if <<(Power Level) > [2]> and <(pick random [1] to [4]) = [1]>> then
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [LIGHTNING!]
                wait ([0.5] * (Pace)) seconds
                set [Enemy Says] to []
                switch costume to (join (Enemy Name) [ attack])
                set [Enemy Swing Until] to ((timer) + [0.3])
                repeat (Power Level)
                    set [Bolt X] to (Hero X)
                    set [Bolt Y] to [-75]
                    set [Bolt Owner] to [enemy]
                    set [Bolt Power] to (Enemy Power)
                    set [Bolt Size] to [100]
                    broadcast [bolt]
                    wait ([0.45] * (Pace)) seconds
                end
                switch costume to (join (Enemy Name) [ idle])
                wait ([0.7] * (Pace)) seconds
            else
                set [Spikes] to [1]
                set [Pick] to (pick random [1] to [3])
                if <(Pick) = [1]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [SPIKE ROLL!]
                    wait ([0.6] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Spikes] to [1]
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [spikes out]
                    set [Pick] to [0]
                    repeat until <<(Pick) > [45]> or <(Fight On) = [0]>>
                        change [Pick] by [1]
                        move ((Enemy Speed) * [2.2]) steps
                        if <(x position) < [-205]> then
                            set x to [-205]
                        end
                        if <(x position) > [205]> then
                            set x to [205]
                        end
                        if <<(x position) > [204]> or <(x position) < [-204]>> then
                            set [Pick] to [999]
                        end
                        if <<(abs of ((Hero X) - (x position))) < ([30] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                            set [Enemy Swing Until] to ((timer) + [0.3])
                            set [Hurt Power] to (Enemy Power)
                            broadcast [enemy hits hero]
                            broadcast [shake]
                            set [Pick] to [999]
                        end
                    end
                end
                if <(Pick) = [2]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Low!]
                    wait ([0.45] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [-57]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [High!]
                    wait ([0.45] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [50]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    if <(Enemy Phase) = [2]> then
                        switch costume to (join (Enemy Name) [ windup])
                        set [Enemy Says] to [Low!]
                        wait ([0.45] * (Pace)) seconds
                        set [Enemy Says] to []
                        set [Shot Y] to [-57]
                        set [Shot Dir] to (Enemy Facing)
                        switch costume to (join (Enemy Name) [ attack])
                        broadcast [enemy shot] and wait
                        switch costume to (join (Enemy Name) [ idle])
                    end
                end
                if <(Pick) = [3]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [SPIKE RAIN!]
                    wait ([0.6] * (Pace)) seconds
                    set [Enemy Says] to []
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [spike rain] and wait
                end
                set [Spikes] to [0]
                switch costume to (join (Enemy Name) [ idle])
                set [Enemy Says] to [Cooling down...]
                wait ((Pace) * [1.4]) seconds
                set [Enemy Says] to []
            end
        end
        if <(Enemy Type) = [6]> then
            set [Pick] to (pick random [1] to [4])
            if <(Pick) = [1]> then
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [Shuriken!]
                wait ([0.3] * (Pace)) seconds
                set [Enemy Says] to []
                set [Shot Y] to [-57]
                set [Shot Dir] to (Enemy Facing)
                switch costume to (join (Enemy Name) [ attack])
                broadcast [enemy shot] and wait
                switch costume to (join (Enemy Name) [ idle])
                wait ([0.3] * (Pace)) seconds
            end
            if <(Pick) = [2]> then
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [Hyah!]
                wait ([0.35] * (Pace)) seconds
                set [Enemy Says] to []
                switch costume to (join (Enemy Name) [ attack])
                set [Enemy Swing Until] to ((timer) + [0.3])
                broadcast [swing sfx]
                set [Pick] to (Hero X)
                glide ([0.22] * (Pace)) secs to x: (Pick) y: [-75]
                if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    set [Hurt Power] to (Enemy Power)
                    broadcast [enemy hits hero]
                end
                glide [0.3] secs to x: ((x position) + ([-80] * (Enemy Facing))) y: [-75]
                if <(x position) < [-205]> then
                    set x to [-205]
                end
                if <(x position) > [205]> then
                    set x to [205]
                end
                switch costume to (join (Enemy Name) [ idle])
                wait ([0.35] * (Pace)) seconds
            end
            if <(Pick) = [3]> then
                set [Smoke X] to (x position)
                set [Smoke Y] to ([-75] + [40])
                broadcast [smoke]
                set [ghost] effect to [100]
                wait ([0.35] * (Pace)) seconds
                set x to ((Hero X) - ([70] * (Facing)))
                if <(x position) < [-205]> then
                    set x to [-205]
                end
                if <(x position) > [205]> then
                    set x to [205]
                end
                if <(Hero X) < (x position)> then
                    point in direction [-90]
                    set [Enemy Facing] to [-1]
                else
                    point in direction [90]
                    set [Enemy Facing] to [1]
                end
                set [ghost] effect to [0]
                set [Smoke X] to (x position)
                set [Smoke Y] to ([-75] + [40])
                broadcast [smoke]
                switch costume to (join (Enemy Name) [ windup])
                wait ([0.18] * (Pace)) seconds
                switch costume to (join (Enemy Name) [ attack])
                set [Enemy Swing Until] to ((timer) + [0.3])
                broadcast [swing sfx]
                if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    set [Hurt Power] to (Enemy Power)
                    broadcast [enemy hits hero]
                end
                wait ([0.35] * (Pace)) seconds
                switch costume to (join (Enemy Name) [ idle])
            end
            if <(Pick) = [4]> then
                if <(Minions) < [1]> then
                    if <(Minions) < [3]> then
                        switch costume to (join (Enemy Name) [ windup])
                        set [Enemy Says] to [NINJA SQUAD!]
                        wait ([0.6] * (Pace)) seconds
                        set [Enemy Says] to []
                        set [Summon Kind] to [ninja]
                        set [Summon Count] to [1]
                        broadcast [ninja summon]
                        switch costume to (join (Enemy Name) [ idle])
                        wait ([0.5] * (Pace)) seconds
                    else
                        set [Smoke X] to (x position)
                        set [Smoke Y] to ([-75] + [40])
                        broadcast [smoke]
                        set [ghost] effect to [100]
                        wait ([0.35] * (Pace)) seconds
                        set x to ((Hero X) - ([70] * (Facing)))
                        if <(x position) < [-205]> then
                            set x to [-205]
                        end
                        if <(x position) > [205]> then
                            set x to [205]
                        end
                        if <(Hero X) < (x position)> then
                            point in direction [-90]
                            set [Enemy Facing] to [-1]
                        else
                            point in direction [90]
                            set [Enemy Facing] to [1]
                        end
                        set [ghost] effect to [0]
                        set [Smoke X] to (x position)
                        set [Smoke Y] to ([-75] + [40])
                        broadcast [smoke]
                        switch costume to (join (Enemy Name) [ windup])
                        wait ([0.18] * (Pace)) seconds
                        switch costume to (join (Enemy Name) [ attack])
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        broadcast [swing sfx]
                        if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                            set [Enemy Swing Until] to ((timer) + [0.3])
                            set [Hurt Power] to (Enemy Power)
                            broadcast [enemy hits hero]
                        end
                        wait ([0.35] * (Pace)) seconds
                        switch costume to (join (Enemy Name) [ idle])
                    end
                else
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [High!]
                    wait ([0.3] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [50]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    wait ([0.3] * (Pace)) seconds
                end
            end
        end
        if <(Enemy Type) = [7]> then
            if <<(Power Level) > [2]> and <(pick random [1] to [4]) = [1]>> then
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [LIGHTNING!]
                wait ([0.5] * (Pace)) seconds
                set [Enemy Says] to []
                switch costume to (join (Enemy Name) [ attack])
                set [Enemy Swing Until] to ((timer) + [0.3])
                repeat (Power Level)
                    set [Bolt X] to (Hero X)
                    set [Bolt Y] to [-75]
                    set [Bolt Owner] to [enemy]
                    set [Bolt Power] to (Enemy Power)
                    set [Bolt Size] to [100]
                    broadcast [bolt]
                    wait ([0.45] * (Pace)) seconds
                end
                switch costume to (join (Enemy Name) [ idle])
                wait ([0.7] * (Pace)) seconds
            else
                set [Pick] to (pick random [1] to [5])
                if <(Pick) = [1]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Shuriken!]
                    wait ([0.3] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [-57]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [High!]
                    wait ([0.3] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [50]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Shuriken!]
                    wait ([0.3] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [-57]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    wait ([0.4] * (Pace)) seconds
                end
                if <(Pick) = [2]> then
                    set [Smoke X] to (x position)
                    set [Smoke Y] to ([-75] + [40])
                    broadcast [smoke]
                    set [ghost] effect to [100]
                    wait ([0.35] * (Pace)) seconds
                    set x to ((Hero X) - ([70] * (Facing)))
                    if <(x position) < [-205]> then
                        set x to [-205]
                    end
                    if <(x position) > [205]> then
                        set x to [205]
                    end
                    if <(Hero X) < (x position)> then
                        point in direction [-90]
                        set [Enemy Facing] to [-1]
                    else
                        point in direction [90]
                        set [Enemy Facing] to [1]
                    end
                    set [ghost] effect to [0]
                    set [Smoke X] to (x position)
                    set [Smoke Y] to ([-75] + [40])
                    broadcast [smoke]
                    switch costume to (join (Enemy Name) [ windup])
                    wait ([0.18] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ attack])
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    broadcast [swing sfx]
                    if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        set [Hurt Power] to (Enemy Power)
                        broadcast [enemy hits hero]
                    end
                    wait ([0.35] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ idle])
                    set [Smoke X] to (x position)
                    set [Smoke Y] to ([-75] + [40])
                    broadcast [smoke]
                    set [ghost] effect to [100]
                    wait ([0.35] * (Pace)) seconds
                    set x to ((Hero X) - ([70] * (Facing)))
                    if <(x position) < [-205]> then
                        set x to [-205]
                    end
                    if <(x position) > [205]> then
                        set x to [205]
                    end
                    if <(Hero X) < (x position)> then
                        point in direction [-90]
                        set [Enemy Facing] to [-1]
                    else
                        point in direction [90]
                        set [Enemy Facing] to [1]
                    end
                    set [ghost] effect to [0]
                    set [Smoke X] to (x position)
                    set [Smoke Y] to ([-75] + [40])
                    broadcast [smoke]
                    switch costume to (join (Enemy Name) [ windup])
                    wait ([0.18] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ attack])
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    broadcast [swing sfx]
                    if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        set [Hurt Power] to (Enemy Power)
                        broadcast [enemy hits hero]
                    end
                    wait ([0.35] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ idle])
                end
                if <(Pick) = [3]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Hyah!]
                    wait ([0.35] * (Pace)) seconds
                    set [Enemy Says] to []
                    switch costume to (join (Enemy Name) [ attack])
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    broadcast [swing sfx]
                    set [Pick] to (Hero X)
                    glide ([0.22] * (Pace)) secs to x: (Pick) y: [-75]
                    if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        set [Hurt Power] to (Enemy Power)
                        broadcast [enemy hits hero]
                    end
                    glide [0.3] secs to x: ((x position) + ([-80] * (Enemy Facing))) y: [-75]
                    if <(x position) < [-205]> then
                        set x to [-205]
                    end
                    if <(x position) > [205]> then
                        set x to [205]
                    end
                    switch costume to (join (Enemy Name) [ idle])
                    wait ([0.35] * (Pace)) seconds
                end
                if <(Pick) = [4]> then
                    if <(Enemy Phase) = [2]> then
                        if <(Minions) < [3]> then
                            switch costume to (join (Enemy Name) [ windup])
                            set [Enemy Says] to [NINJA SQUAD!]
                            wait ([0.6] * (Pace)) seconds
                            set [Enemy Says] to []
                            set [Summon Kind] to [ninja]
                            set [Summon Count] to [3]
                            broadcast [ninja summon]
                            switch costume to (join (Enemy Name) [ idle])
                            wait ([0.5] * (Pace)) seconds
                        else
                            set [Smoke X] to (x position)
                            set [Smoke Y] to ([-75] + [40])
                            broadcast [smoke]
                            set [ghost] effect to [100]
                            wait ([0.35] * (Pace)) seconds
                            set x to ((Hero X) - ([70] * (Facing)))
                            if <(x position) < [-205]> then
                                set x to [-205]
                            end
                            if <(x position) > [205]> then
                                set x to [205]
                            end
                            if <(Hero X) < (x position)> then
                                point in direction [-90]
                                set [Enemy Facing] to [-1]
                            else
                                point in direction [90]
                                set [Enemy Facing] to [1]
                            end
                            set [ghost] effect to [0]
                            set [Smoke X] to (x position)
                            set [Smoke Y] to ([-75] + [40])
                            broadcast [smoke]
                            switch costume to (join (Enemy Name) [ windup])
                            wait ([0.18] * (Pace)) seconds
                            switch costume to (join (Enemy Name) [ attack])
                            set [Enemy Swing Until] to ((timer) + [0.3])
                            broadcast [swing sfx]
                            if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                                set [Enemy Swing Until] to ((timer) + [0.3])
                                set [Hurt Power] to (Enemy Power)
                                broadcast [enemy hits hero]
                            end
                            wait ([0.35] * (Pace)) seconds
                            switch costume to (join (Enemy Name) [ idle])
                        end
                    else
                        if <(Minions) < [3]> then
                            switch costume to (join (Enemy Name) [ windup])
                            set [Enemy Says] to [NINJA SQUAD!]
                            wait ([0.6] * (Pace)) seconds
                            set [Enemy Says] to []
                            set [Summon Kind] to [ninja]
                            set [Summon Count] to [2]
                            broadcast [ninja summon]
                            switch costume to (join (Enemy Name) [ idle])
                            wait ([0.5] * (Pace)) seconds
                        else
                            set [Smoke X] to (x position)
                            set [Smoke Y] to ([-75] + [40])
                            broadcast [smoke]
                            set [ghost] effect to [100]
                            wait ([0.35] * (Pace)) seconds
                            set x to ((Hero X) - ([70] * (Facing)))
                            if <(x position) < [-205]> then
                                set x to [-205]
                            end
                            if <(x position) > [205]> then
                                set x to [205]
                            end
                            if <(Hero X) < (x position)> then
                                point in direction [-90]
                                set [Enemy Facing] to [-1]
                            else
                                point in direction [90]
                                set [Enemy Facing] to [1]
                            end
                            set [ghost] effect to [0]
                            set [Smoke X] to (x position)
                            set [Smoke Y] to ([-75] + [40])
                            broadcast [smoke]
                            switch costume to (join (Enemy Name) [ windup])
                            wait ([0.18] * (Pace)) seconds
                            switch costume to (join (Enemy Name) [ attack])
                            set [Enemy Swing Until] to ((timer) + [0.3])
                            broadcast [swing sfx]
                            if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                                set [Enemy Swing Until] to ((timer) + [0.3])
                                set [Hurt Power] to (Enemy Power)
                                broadcast [enemy hits hero]
                            end
                            wait ([0.35] * (Pace)) seconds
                            switch costume to (join (Enemy Name) [ idle])
                        end
                    end
                end
                if <(Pick) = [5]> then
                    set [Smoke X] to (x position)
                    set [Smoke Y] to ([-75] + [40])
                    broadcast [smoke]
                    set [ghost] effect to [100]
                    wait ([0.35] * (Pace)) seconds
                    set x to ((Hero X) - ([70] * (Facing)))
                    if <(x position) < [-205]> then
                        set x to [-205]
                    end
                    if <(x position) > [205]> then
                        set x to [205]
                    end
                    if <(Hero X) < (x position)> then
                        point in direction [-90]
                        set [Enemy Facing] to [-1]
                    else
                        point in direction [90]
                        set [Enemy Facing] to [1]
                    end
                    set [ghost] effect to [0]
                    set [Smoke X] to (x position)
                    set [Smoke Y] to ([-75] + [40])
                    broadcast [smoke]
                    switch costume to (join (Enemy Name) [ windup])
                    wait ([0.18] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ attack])
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    broadcast [swing sfx]
                    if <<(abs of ((Hero X) - (x position))) < ([42] + (Enemy Body))> and <((Hero Y) - [-75]) < [70]>> then
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        set [Hurt Power] to (Enemy Power)
                        broadcast [enemy hits hero]
                    end
                    wait ([0.35] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ idle])
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Shuriken!]
                    wait ([0.3] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [-57]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                end
            end
        end
        if <(Enemy Type) = [8]> then
            switch costume to (join (Enemy Name) [ windup])
            set [Enemy Says] to [STOMP!]
            wait ([0.6] * (Pace)) seconds
            set [Enemy Says] to []
            switch costume to (join (Enemy Name) [ attack])
            set [Enemy Swing Until] to ((timer) + [0.3])
            change y by [10]
            wait [0.05] seconds
            set y to [-75]
            broadcast [shake]
            set [Wave Dir] to (Enemy Facing)
            broadcast [ground wave] and wait
            switch costume to (join (Enemy Name) [ idle])
            wait ([0.5] * (Pace)) seconds
            if <(abs of ((Hero X) - (x position))) > [160]> then
                repeat [8]
                    move (Enemy Speed) steps
                end
                if <(x position) < [-205]> then
                    set x to [-205]
                end
                if <(x position) > [205]> then
                    set x to [205]
                end
            end
        end
        if <(Enemy Type) = [9]> then
            if <<(Power Level) > [2]> and <(pick random [1] to [4]) = [1]>> then
                switch costume to (join (Enemy Name) [ windup])
                set [Enemy Says] to [LIGHTNING!]
                wait ([0.5] * (Pace)) seconds
                set [Enemy Says] to []
                switch costume to (join (Enemy Name) [ attack])
                set [Enemy Swing Until] to ((timer) + [0.3])
                repeat (Power Level)
                    set [Bolt X] to (Hero X)
                    set [Bolt Y] to [-75]
                    set [Bolt Owner] to [enemy]
                    set [Bolt Power] to (Enemy Power)
                    set [Bolt Size] to [100]
                    broadcast [bolt]
                    wait ([0.45] * (Pace)) seconds
                end
                switch costume to (join (Enemy Name) [ idle])
                wait ([0.7] * (Pace)) seconds
            else
                if <(Enemy Phase) = [2]> then
                    set [Pick] to (pick random [1] to [5])
                else
                    set [Pick] to (pick random [1] to [4])
                end
                if <(Pick) = [5]> then
                    switch costume to (shadow spikes)
                    set [Spikes] to [1]
                    broadcast [spikes out]
                    set [Enemy Says] to [SPIKE ARMOR!]
                    wait ([0.5] * (Pace)) seconds
                    set [Enemy Says] to []
                    repeat [25]
                        move (Enemy Speed) steps
                        if <(x position) < [-205]> then
                            set x to [-205]
                        end
                        if <(x position) > [205]> then
                            set x to [205]
                        end
                        if <<(abs of ((Hero X) - (x position))) < ([30] + (Enemy Body))> and <((Hero Y) - [-75]) < [60]>> then
                            set [Enemy Swing Until] to ((timer) + [0.3])
                            set [Hurt Power] to (Enemy Power)
                            broadcast [enemy hits hero]
                        end
                    end
                    wait ([0.6] * (Pace)) seconds
                    set [Spikes] to [0]
                    switch costume to (join (Enemy Name) [ idle])
                    wait ([0.4] * (Pace)) seconds
                end
                if <(Pick) = [1]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Ready?]
                    wait ([0.75] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Pick] to (Hero X)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [swing sfx]
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    glide ([0.4] * (Pace)) secs to x: (Pick) y: [-75]
                    if <<(abs of ((Hero X) - (x position))) < ([34] + (Enemy Body))> and <((Hero Y) - [-75]) < [50]>> then
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        set [Hurt Power] to (Enemy Power)
                        broadcast [enemy hits hero]
                        broadcast [shake]
                    end
                    switch costume to (join (Enemy Name) [ idle])
                    wait ([0.45] * (Pace)) seconds
                    glide [0.5] secs to x: ((x position) + ([-100] * (Enemy Facing))) y: [-75]
                    if <(x position) < [-205]> then
                        set x to [-205]
                    end
                    if <(x position) > [205]> then
                        set x to [205]
                    end
                    wait ([0.3] * (Pace)) seconds
                end
                if <(Pick) = [2]> then
                    wait ([0.2] * (Pace)) seconds
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [Low!]
                    wait ([0.45] * (Pace)) seconds
                    set [Enemy Says] to []
                    set [Shot Y] to [-57]
                    set [Shot Dir] to (Enemy Facing)
                    switch costume to (join (Enemy Name) [ attack])
                    broadcast [enemy shot] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    if <(Enemy Phase) = [2]> then
                        switch costume to (join (Enemy Name) [ windup])
                        set [Enemy Says] to [High!]
                        wait ([0.45] * (Pace)) seconds
                        set [Enemy Says] to []
                        set [Shot Y] to [50]
                        set [Shot Dir] to (Enemy Facing)
                        switch costume to (join (Enemy Name) [ attack])
                        broadcast [enemy shot] and wait
                        switch costume to (join (Enemy Name) [ idle])
                    end
                    wait ([0.3] * (Pace)) seconds
                end
                if <(Pick) = [3]> then
                    switch costume to (join (Enemy Name) [ windup])
                    set [Enemy Says] to [STOMP!]
                    wait ([0.6] * (Pace)) seconds
                    set [Enemy Says] to []
                    switch costume to (join (Enemy Name) [ attack])
                    set [Enemy Swing Until] to ((timer) + [0.3])
                    change y by [10]
                    wait [0.05] seconds
                    set y to [-75]
                    broadcast [shake]
                    set [Wave Dir] to (Enemy Facing)
                    broadcast [ground wave] and wait
                    switch costume to (join (Enemy Name) [ idle])
                    wait ([0.5] * (Pace)) seconds
                    if <(abs of ((Hero X) - (x position))) > [160]> then
                        repeat [8]
                            move (Enemy Speed) steps
                        end
                        if <(x position) < [-205]> then
                            set x to [-205]
                        end
                        if <(x position) > [205]> then
                            set x to [205]
                        end
                    end
                end
                if <(Pick) = [4]> then
                    repeat [12]
                        move ((Enemy Speed) * [1.5]) steps
                        if <(x position) < [-210]> then
                            set x to [-210]
                        end
                        if <(x position) > [210]> then
                            set x to [210]
                        end
                    end
                    if <<(abs of ((Hero X) - (x position))) < ([38] + (Enemy Body))> and <((Hero Y) - [-75]) < [60]>> then
                        switch costume to (join (Enemy Name) [ attack])
                        set [Enemy Swing Until] to ((timer) + [0.3])
                        set [Hurt Power] to (Enemy Power)
                        broadcast [enemy hits hero]
                        wait ([0.3] * (Pace)) seconds
                        switch costume to (join (Enemy Name) [ idle])
                        wait ([0.45] * (Pace)) seconds
                    else
                        move (Enemy Speed) steps
                        if <(x position) < [-210]> then
                            set x to [-210]
                        end
                        if <(x position) > [210]> then
                            set x to [210]
                        end
                        wait [0.03] seconds
                    end
                end
            end
        end
        if <(Fight On) = [1]> then
            switch costume to (join (Enemy Name) [ idle])
        end
    end
end
```

> One brain for every enemy. 1 Rival walks in and punches. 2 Ivy throws low and high shots. 3 Brute says Ready? then charges where you were. 4 Spike Bot rolls at you with spikes out, then cools down. 5 BOSS MEGA SPIKE: spike roll, spike shots and Spike Rain, then it cools down. 6 Quake stomps a ground wave. 7 the Shadow King mixes them all, and grows Spike Armor when angry.

```
when I receive [enemy hurt]
if <(pick random [1] to [2]) = [1]> then
    switch costume to (join (Enemy Name) [ hurt])
else
    switch costume to (join (Enemy Name) [ hurt high])
end
move [-12] steps
if <(x position) < [-210]> then
    set x to [-210]
end
if <(x position) > [210]> then
    set x to [210]
end
set [brightness] effect to [60]
wait [0.1] seconds
set [brightness] effect to [0]
```

```
when I receive [king angry]
if <(Enemy Type) = [7]> then
    set [Enemy Says] to [Shadow clones... ATTACK!]
    wait [1.4] seconds
    set [Enemy Says] to []
    set [Summon Kind] to [ninja]
    set [Summon Count] to [2]
    broadcast [ninja summon]
end
if <(Enemy Type) = [9]> then
    switch costume to (shadow angry)
    set [Enemy Says] to [You're strong... but I'm STRONGER!]
    wait [1.6] seconds
    set [Enemy Says] to []
    switch costume to (shadow idle)
else
    if <(Enemy Type) = [5]> then
        switch costume to (megaspike attack)
        set [Enemy Says] to [OVERDRIVE!!]
        wait [1.2] seconds
        set [Enemy Says] to []
        switch costume to (megaspike idle)
    end
end
```

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [fighters ready]
show
clear graphic effects
set size to (Enemy Size) %
point in direction [-90]
set [Enemy Facing] to [-1]
go to x: [150] y: [-75]
switch costume to (join (Enemy Name) [ idle])
set [Enemy Says] to []
if <(Wave Phase) = [1]> then
    hide
end
```

```
when I receive [boss enter]
clear graphic effects
set size to (Enemy Size) %
point in direction [-90]
set [Enemy Facing] to [-1]
go to x: [170] y: [-75]
switch costume to (join (Enemy Name) [ idle])
set [Smoke X] to [170]
set [Smoke Y] to ([-75] + [40])
broadcast [smoke]
show
set [Enemy Says] to (Enemy Title)
wait [1.2] seconds
set [Enemy Says] to []
```

> ADVENTURE: the stage boss bursts in after the waves.

```
when I receive [scene setup]
show
clear graphic effects
set size to (Enemy Size) %
point in direction [-90]
go to x: [150] y: [-75]
switch costume to (join (Enemy Name) [ idle])
```

```
when I receive [story scene]
hide
```

```
when I receive [enemy line]
set [Enemy Says] to (Line)
set [Line Until] to ((timer) + (Line Secs))
wait until <<(timer) > (Line Until)> or <(Skip) = [1]>>
set [Enemy Says] to []
```

```
when I receive [enemy down]
set [Enemy Says] to []
set [Spikes] to [0]
wait [0.2] seconds
set y to [-75]
switch costume to (join (Enemy Name) [ down])
wait [1.3] seconds
repeat [10]
    change [ghost] effect by [10]
    wait [0.03] seconds
end
if <not <<(Mode) = [story]> and <(Chapter) = [9]>>> then
    hide
end
set [ghost] effect to [0]
```

```
when I receive [hero down]
wait [0.3] seconds
switch costume to (join (Enemy Name) [ idle])
set [Enemy Says] to [Ha! Try again!]
wait [2] seconds
set [Enemy Says] to []
```

```
when I receive [ending]
show
go to x: [170] y: [-75]
point in direction [-90]
switch costume to (shadow down)
```

## Enemy Shot

Costumes: ball, spike, shuriken
Sprite-only variables: Hit, Spin

```
when green flag clicked
hide
```

```
when I receive [enemy shot]
set [Spin] to [0]
set rotation style [left-right]
if <(Enemy Name) = [megaspike]> then
    switch costume to (spike)
else
    if <<(Enemy Name) = [ninja]> or <(Enemy Name) = [kage]>> then
        switch costume to (shuriken)
        set [Spin] to [1]
        set rotation style [all around]
        broadcast [shuriken sfx]
    else
        switch costume to (ball)
    end
end
point in direction ([90] * (Shot Dir))
go to x: ((Enemy X) + ([30] * (Shot Dir))) y: (Shot Y)
set [Hit] to [0]
show
go to [front] layer
set [Shot Cancel] to [0]
set [Shot Live] to [1]
repeat until <<<<(abs of (x position)) > [235]> or <(Hit) = [1]>> or <(Fight On) = [0]>> or <(Shot Cancel) = [1]>>
    change x by ([12] * (Shot Dir))
    set [Shot X] to (x position)
    if <(Spin) = [1]> then
        turn right [40] degrees
    end
    if <<<(abs of ((x position) - (Hero X))) < [18]> and <((Shot Y) - (Hero Y)) > [-10]>> and <((Shot Y) - (Hero Y)) < [108]>> then
        set [Hit] to [1]
        set [Hurt Power] to (Enemy Power)
        broadcast [enemy hits hero]
    end
end
hide
set [Shot Live] to [0]
set [Shot X] to [999]
```

> Low shots fly at knee height: jump them. High shots fly over your head: stay down. Dodge works on both. A fireball can knock a shot out of the air.

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Ground Wave

Costumes: wave
Sprite-only variables: Hit

```
when green flag clicked
hide
```

```
when I receive [ground wave]
go to x: ((Enemy X) + ([40] * (Wave Dir))) y: [-75]
set [Hit] to [0]
show
go to [front] layer
repeat until <<(abs of (x position)) > [235]> or <(Fight On) = [0]>>
    change x by (((Enemy Speed) * [3]) * (Wave Dir))
    if <<<(Hit) = [0]> and <(abs of ((x position) - (Hero X))) < [28]>> and <((Hero Y) - [-75]) < [25]>> then
        set [Hit] to [1]
        set [Hurt Power] to (Enemy Power)
        broadcast [enemy hits hero]
    end
end
hide
```

> The wave rolls along the ground. If Hero is up in the air, it rolls underneath.

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Held Weapon

Costumes: sword, hammer, boomerang, spear, nunchucks, shield
Sprite-only variables: Swing Until, C, D

```
when green flag clicked
hide
forever
    if <<<(State) = [fight]> and <not <(Weapon) = [none]>>> and <(Boomerang Out) = [0]>> then
        switch costume to (Weapon)
        set [C] to ([costume #] of (Hero))
        go to x: ((Hero X) + (((item (C) of [Hand X]) * [0.75]) * (Facing))) y: ((Hero Y) + ((item (C) of [Hand Y]) * [0.75]))
        set [D] to (item (C) of [Hand Dir])
        if <(timer) < (Swing Until)> then
            change [D] by [35]
        end
        if <(Facing) = [1]> then
            point in direction ((D) + [90])
        else
            point in direction ([90] - (D))
        end
        show
        go to [front] layer
    else
        hide
    end
end
```

> The weapon sits in Hero's front hand and lines up with the forearm, for every picture Hero can show (Hand X, Hand Y and Hand Dir are worked out from the poses when the game is built).

```
when I receive [swing]
set [Swing Until] to ((timer) + [0.15])
broadcast [swing sfx]
```

```
when I receive [weapon break]
set [Pop Text] to (join [Oh no! The ] (join (Weapon) [ broke!]))
broadcast [popup]
set [Weapon] to [none]
set [Weapon Bonus] to [0]
set [Weapon Reach] to [0]
set [Weapon Uses] to [0]
```

## Weapon Drop

Costumes: sword, hammer, boomerang, spear, nunchucks, shield
Sprite-only variables: Kind, Life, Got

```
when green flag clicked
hide
forever
    if <<(Fight On) = [1]> and <(Weapon) = [none]>> then
        wait (pick random [3] to [7]) seconds
        if <<(Fight On) = [1]> and <(Weapon) = [none]>> then
            set [Kind] to (pick random [1] to [6])
            if <(Kind) = [1]> then
                set [Kind] to [sword]
            end
            if <(Kind) = [2]> then
                set [Kind] to [hammer]
            end
            if <(Kind) = [3]> then
                set [Kind] to [boomerang]
            end
            if <(Kind) = [4]> then
                set [Kind] to [spear]
            end
            if <(Kind) = [5]> then
                set [Kind] to [nunchucks]
            end
            if <(Kind) = [6]> then
                set [Kind] to [shield]
            end
            switch costume to (Kind)
            go to x: (pick random [-170] to [60]) y: [170]
            show
            go to [front] layer
            repeat until <(y position) < [-45]>
                change y by [-10]
            end
            set y to [-50]
            set [Life] to [0]
            set [Got] to [0]
            repeat until <<<(Got) = [1]> or <(Life) > [150]>> or <(Fight On) = [0]>>
                change [Life] by [1]
                if <<(abs of ((x position) - (Hero X))) < [36]> and <((Hero Y) - [-75]) < [60]>> then
                    set [Got] to [1]
                end
                if <(Life) > [110]> then
                    set [ghost] effect to (((Life) - [110]) * [2])
                end
            end
            hide
            set [ghost] effect to [0]
            if <<<(Got) = [1]> and <(Fight On) = [1]>> and <(Weapon) = [none]>> then
                if <(Kind) = [sword]> then
                    set [Weapon Bonus] to [4]
                    set [Weapon Reach] to [28]
                    set [Weapon Uses] to [10]
                    set [Pop Text] to [SWORD!]
                end
                if <(Kind) = [hammer]> then
                    set [Weapon Bonus] to [9]
                    set [Weapon Reach] to [12]
                    set [Weapon Uses] to [5]
                    set [Pop Text] to [HAMMER!]
                end
                if <(Kind) = [boomerang]> then
                    set [Weapon Bonus] to [0]
                    set [Weapon Reach] to [0]
                    set [Weapon Uses] to [6]
                    set [Pop Text] to [BOOMERANG!]
                end
                if <(Kind) = [spear]> then
                    set [Weapon Bonus] to [5]
                    set [Weapon Reach] to [48]
                    set [Weapon Uses] to [8]
                    set [Pop Text] to [SPEAR!]
                end
                if <(Kind) = [nunchucks]> then
                    set [Weapon Bonus] to [2]
                    set [Weapon Reach] to [6]
                    set [Weapon Uses] to [12]
                    set [Pop Text] to [NUNCHUCKS!]
                end
                if <(Kind) = [shield]> then
                    set [Weapon Bonus] to [2]
                    set [Weapon Reach] to [0]
                    set [Weapon Uses] to [6]
                    set [Pop Text] to [SHIELD!]
                end
                set [Weapon] to (Kind)
                broadcast [popup]
                broadcast [weapon get]
            end
        end
    else
        wait [0.2] seconds
    end
end
```

> Every 3 to 7 seconds a weapon falls from the sky. Walk over it to pick it up. Sword: +4 power, longer reach, 10 swings. Hammer: +9 power and a shake, 5 swings. Boomerang: PUNCH throws it, 6 throws. Spear: +5 power and the longest reach, 8 jabs. Nunchucks: every punch hits twice, 12 swings. Shield: blocks most of the damage you take (each block uses it up a bit) and you can bash with it.

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Apple

Costumes: apple
Sprite-only variables: Life, Got

```
when green flag clicked
hide
forever
    if <<<(Fight On) = [1]> and <(State) = [fight]>> and <not <(Mode) = [practice]>>> then
        wait (pick random [10] to [16]) seconds
        if <<(Fight On) = [1]> and <(Hero HP) < (Hero Max)>> then
            go to x: (pick random [-180] to [120]) y: [170]
            show
            go to [front] layer
            repeat until <(y position) < [-49]>
                change y by [-8]
                turn right [0] degrees
            end
            set y to [-53]
            set [Life] to [0]
            set [Got] to [0]
            repeat until <<<(Got) = [1]> or <(Life) > [160]>> or <(Fight On) = [0]>>
                change [Life] by [1]
                if <<(abs of ((x position) - (Hero X))) < [32]> and <((Hero Y) - [-75]) < [60]>> then
                    set [Got] to [1]
                end
                if <(Life) > [120]> then
                    set [ghost] effect to (((Life) - [120]) * [2])
                end
            end
            hide
            set [ghost] effect to [0]
            if <<(Got) = [1]> and <(Fight On) = [1]>> then
                change [Hero HP] by [25]
                if <(Hero HP) > (Hero Max)> then
                    set [Hero HP] to (Hero Max)
                end
                set [Pop Text] to [YUM! +25 HEALTH]
                broadcast [popup]
                broadcast [weapon get]
            end
        end
    else
        wait [0.3] seconds
    end
end
```

> Grok's healing apple: when you are hurt, an apple sometimes falls. Walk over it for +25 health.

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Boomerang

Costumes: spin
Sprite-only variables: Dir, Hit, Steps

```
when green flag clicked
hide
```

```
when I receive [throw boomerang]
set [Dir] to (Facing)
set [Hit] to [0]
set [Steps] to [0]
go to x: ((Hero X) + ([20] * (Dir))) y: ((Hero Y) + [50])
show
go to [front] layer
repeat until <<<(Steps) > [16]> or <(abs of (x position)) > [230]>> or <(Hit) = [1]>>
    change [Steps] by [1]
    change x by ([15] * (Dir))
    turn right [45] degrees
    if <(abs of ((x position) - (Enemy X))) < ([26] + (Enemy Body))> then
        set [Hit] to [1]
        set [Hit Power] to [7]
        broadcast [hero hits]
    end
end
set [Steps] to [0]
repeat until <<(abs of ((x position) - (Hero X))) < [20]> or <(Steps) > [45]>>
    change [Steps] by [1]
    turn right [45] degrees
    if <(x position) < (Hero X)> then
        change x by [16]
    else
        change x by [-16]
    end
    set y to ((Hero Y) + [50])
end
hide
set [Boomerang Out] to [0]
if <(Weapon Uses) < [1]> then
    broadcast [weapon break]
end
```

> Flies out, hits once, then comes back to Hero's hand.

```
when I receive [show title]
hide
set [Boomerang Out] to [0]
```

```
when I receive [choose hero]
hide
set [Boomerang Out] to [0]
```

```
when I receive [story scene]
hide
set [Boomerang Out] to [0]
```

```
when I receive [hero down]
hide
set [Boomerang Out] to [0]
```

```
when I receive [enemy down]
hide
set [Boomerang Out] to [0]
```

```
when I receive [ending]
hide
set [Boomerang Out] to [0]
```

## Smoke

Costumes: puff
Sprite-only variables: Is Clone

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [smoke]
if <(Is Clone) = [0]> then
    go to x: (Smoke X) y: (Smoke Y)
    create clone of (myself)
end
```

> A puff of smoke when a ninja vanishes or appears. Only the original makes clones.

```
when I start as a clone
set [Is Clone] to [1]
set size to [50] %
set [ghost] effect to [0]
show
go to [front] layer
broadcast [poof sfx]
repeat [10]
    change size by [9]
    change [ghost] effect by [10]
    change y by [1]
    wait [0.03] seconds
end
delete this clone
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [story scene]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Ninja Minion

Costumes: ninja idle, grunt idle, robot idle, ninja run 1, grunt run 1, robot run 1, ninja run 2, grunt run 2, robot run 2, ninja slash, grunt slash, robot slash, ninja hurt, grunt hurt, robot hurt, ninja hurt high, grunt hurt high, robot hurt high, ninja flip, grunt flip, robot flip, ninja down, grunt down, robot down
Sprite-only variables: Is Clone, HP, Hit Until, Was Hit, Atk Until, Dir, D, Side, Gap, Kind, Slot, J, Speed

```
when green flag clicked
hide
set [Is Clone] to [0]
set [Minions] to [0]
delete all of [M X]
repeat [3]
    add [9999] to [M X]
end
```

```
define (pick slot)   [run without screen refresh]
set [Slot] to [0]
set [J] to [0]
repeat [3]
    change [J] by [1]
    if <<(Slot) = [0]> and <not <(item (J) of [M X]) < [9000]>>> then
        set [Slot] to (J)
    end
end
if <(Slot) > [0]> then
    replace item (Slot) of [M X] with (x position)
end
```

```
when I receive [ninja summon]
if <(Is Clone) = [0]> then
    repeat (Summon Count)
        if <<(Minions) < [3]> and <(Fight On) = [1]>> then
            set [Kind] to (Summon Kind)
            if <(Kind) = [mix]> then
                set [J] to (pick random [1] to [3])
                if <(J) = [1]> then
                    set [Kind] to [ninja]
                end
                if <(J) = [2]> then
                    set [Kind] to [grunt]
                end
                if <(J) = [3]> then
                    set [Kind] to [robot]
                end
            end
            if <(pick random [1] to [2]) = [1]> then
                set [Side] to [-1]
            else
                set [Side] to [1]
            end
            go to x: ((Side) * (pick random [150] to [215])) y: [-75]
            (pick slot)
            if <(Slot) > [0]> then
                change [Minions] by [1]
                set [Smoke X] to (x position)
                set [Smoke Y] to ([-75] + [40])
                broadcast [smoke]
                create clone of (myself)
            end
            wait [0.25] seconds
        end
    end
end
```

> Calls small enemies (up to 3 at once): ninjas, gray grunts or small robots (Summon Kind; "mix" picks any). MASTER KAGE's NINJA SQUAD and the ADVENTURE waves both use this.

```
when I start as a clone
set [Is Clone] to [1]
set [Gap] to (pick random [26] to [58])
set [HP] to (round (([7] + ([2] * (Difficulty))) * ([1] + ([0.35] * ((Power Level) - [1])))))
set [Was Hit] to [0]
set [Atk Until] to ((timer) + [0.6])
set [Speed] to ([3] + ([0.5] * (Difficulty)))
if <(Kind) = [robot]> then
    set size to [55] %
    change [Speed] by [1.5]
    change [HP] by [-2]
else
    set size to [70] %
end
if <(Kind) = [grunt]> then
    change [HP] by [1]
end
change [HP] by ([2] * ((Lap) - [1]))
switch costume to (join (Kind) [ flip])
show
go to [front] layer
wait [0.15] seconds
repeat until <<(HP) < [1]> or <(Fight On) = [0]>>
    replace item (Slot) of [M X] with (x position)
    if <(Was Hit) = [1]> then
        set [Was Hit] to [0]
        if <(pick random [1] to [2]) = [1]> then
            switch costume to (join (Kind) [ hurt])
        else
            switch costume to (join (Kind) [ hurt high])
        end
        set [brightness] effect to [60]
        move [-14] steps
        if <(x position) < [-220]> then
            set x to [-220]
        end
        if <(x position) > [220]> then
            set x to [220]
        end
        wait [0.15] seconds
        set [brightness] effect to [0]
    else
        set [D] to ((Hero X) - (x position))
        if <(D) > [0]> then
            point in direction [90]
        else
            point in direction [-90]
        end
        if <(abs of (D)) > (Gap)> then
            move (Speed) steps
            if <((round ((timer) * [9])) mod [2]) = [0]> then
                switch costume to (join (Kind) [ run 1])
            else
                switch costume to (join (Kind) [ run 2])
            end
        else
            if <<(timer) > (Atk Until)> and <(abs of (D)) < [45]>> then
                switch costume to (join (Kind) [ slash])
                broadcast [swing sfx]
                if <((Hero Y) - [-75]) < [50]> then
                    set [Hurt Power] to ([3] + (Power Level))
                    broadcast [enemy hits hero]
                end
                set [Atk Until] to ((timer) + ([1.1] - ([0.1] * (Difficulty))))
                wait [0.18] seconds
            else
                switch costume to (join (Kind) [ idle])
                if <<(timer) > (Atk Until)> and <(pick random [1] to [20]) = [1]>> then
                    set [Gap] to (pick random [26] to [40])
                end
            end
        end
    end
end
replace item (Slot) of [M X] with [9999]
if <(HP) < [1]> then
    switch costume to (join (Kind) [ down])
    change [Score] by [50]
    change [Beaten] by [1]
    wait [0.35] seconds
end
set [Smoke X] to (x position)
set [Smoke Y] to ([-75] + [30])
broadcast [smoke]
change [Minions] by [-1]
if <(Minions) < [0]> then
    set [Minions] to [0]
end
delete this clone
```

> One small enemy: runs at you, attacks when close, flinches when hit, vanishes in smoke when beaten. Robots are smaller and faster; grunts are a little tougher.

```
when I receive [area hit]
if <<<<(Is Clone) = [1]> and <(HP) > [0]>> and <(timer) > (Hit Until)>> and <(abs of ((x position) - (Area X))) < ((Area R) + [14])>> then
    change [HP] by ([0] - (Area Power))
    set [Hit Until] to ((timer) + [0.18])
    set [Was Hit] to [1]
    broadcast [brawl hit]
    if <(Area Kind) = [fire]> then
        set [Fire Stop] to [1]
    end
end
```

> Your punches, kicks, fireballs, lightning and SUPER moves also hit ninjas near them.

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
    set [Minions] to [0]
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
    set [Minions] to [0]
end
```

```
when I receive [story scene]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
    set [Minions] to [0]
end
```

## Hero Shadow

Costumes: shadow

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> or <(State) = [over]>> then
        go to x: (Hero X) y: ([-75] + [1])
        set size to ([75] - (((Hero Y) - [-75]) * [0.3])) %
        set [ghost] effect to ([10] + (((Hero Y) - [-75]) * [0.5]))
        go to [back] layer
        show
    else
        hide
    end
end
```

> A shadow on the floor gives depth: it shrinks and fades when you jump.

## Enemy Shadow

Costumes: shadow

```
when green flag clicked
hide
forever
    if <<<(State) = [fight]> and <(Enemy HP) > [0]>> and <(Wave Phase) = [0]>> then
        go to x: (Enemy X) y: ([-75] + [1])
        set size to ((Enemy Size) * [0.95]) %
        go to [back] layer
        show
    else
        hide
    end
end
```

> A shadow on the floor gives depth: it shrinks and fades when you jump.

## Spike Rain

Costumes: warning, spike
Sprite-only variables: Hit, Is Clone

```
when green flag clicked
hide
```

```
when I receive [spike rain]
if <(Is Clone) = [0]> then
    switch costume to (warning)
    go to x: (Hero X) y: [-75]
    create clone of (myself)
    repeat [4]
        go to x: (pick random [-210] to [210]) y: [-75]
        create clone of (myself)
    end
    broadcast [spike fall sfx]
    wait [1.6] seconds
end
```

> One spike falls where the hero is standing and the rest land anywhere. A red mark shows where. Move away, or DODGE. Only the original makes spikes (clones hear messages too).

```
when I start as a clone
set [Is Clone] to [1]
switch costume to (warning)
set y to [-75]
set [Hit] to [0]
show
repeat [4]
    set [ghost] effect to [50]
    wait [0.09] seconds
    set [ghost] effect to [0]
    wait [0.09] seconds
end
switch costume to (spike)
set y to [190]
go to [front] layer
repeat until <<(y position) < [-71]> or <(Fight On) = [0]>>
    change y by [-22]
    if <<<<(Hit) = [0]> and <(abs of ((x position) - (Hero X))) < [20]>> and <(y position) < ((Hero Y) + [120])>> and <(y position) > ((Hero Y) - [10])>> then
        set [Hit] to [1]
        set [Hurt Power] to [8]
        broadcast [enemy hits hero]
    end
end
wait [0.25] seconds
delete this clone
```

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Charge Glow

Costumes: glow

```
when green flag clicked
hide
forever
    if <<(Charge) > [0]> and <(State) = [brawl]>> then
        go to x: ((P1 Screen X) + (((P1 Screen Size) * [0.5]) * (Facing))) y: ((P1 Screen Y) + ((P1 Screen Size) * [0.9]))
        set size to (([25] + ((Charge) * [0.9])) * ((P1 Screen Size) / [75])) %
        show
        go to [front] layer
    end
    if <<(Charge) > [0]> and <(State) = [fight]>> then
        go to x: ((Hero X) + ([36] * (Facing))) y: ((Hero Y) + [66])
        set size to ([25] + ((Charge) * [0.9])) %
        if <(Charge) = [100]> then
            set [brightness] effect to ([30] * ((round ((timer) * [8])) mod [2]))
        else
            set [brightness] effect to [0]
        end
        show
        go to [front] layer
    else
        hide
    end
end
```

> The glowing ball in Hero's hand grows while FIRE is held.

## Fireball

Costumes: flame 1, flame 2
Sprite-only variables: Power, Dir, Done

```
when green flag clicked
hide
set [Fireball Out] to [0]
```

```
when I receive [fire]
set [Power] to (Fire Power)
set [Dir] to (Facing)
set [Done] to [0]
point in direction ([90] * (Dir))
set size to ([35] + ((Power) * [0.9])) %
go to x: ((Hero X) + ([40] * (Dir))) y: ((Hero Y) + [62])
show
go to [front] layer
repeat until <<<(abs of (x position)) > [235]> or <(Done) = [1]>> or <(Fight On) = [0]>>
    change x by (([9] + ((Power) / [25])) * (Dir))
    if <((round ((timer) * [12])) mod [2]) = [0]> then
        switch costume to (flame 1)
    else
        switch costume to (flame 2)
    end
    if <<<(Shot Live) = [1]> and <(abs of ((x position) - (Shot X))) < [26]>> and <(abs of ((y position) - (Shot Y))) < [34]>> then
        set [Shot Cancel] to [1]
        set [Pop Text] to [BLOCKED!]
        broadcast [popup]
        if <(Power) < [100]> then
            set [Done] to [1]
        end
    end
    if <(Minions) > [0]> then
        set [Fire Stop] to [0]
        set [Area X] to (x position)
        set [Area R] to ([14] + ((Power) / [8]))
        set [Area Power] to ([3] + (round ((Power) / [12])))
        set [Area Kind] to [fire]
        broadcast [area hit]
        if <<(Fire Stop) = [1]> and <(Power) < [100]>> then
            set [Done] to [1]
        end
    end
    if <(abs of ((x position) - (Enemy X))) < (([14] + (Enemy Body)) + ((Power) / [8]))> then
        set [Done] to [1]
        set [Hit Power] to ([3] + (round ((Power) / [12])))
        if <(Power) = [100]> then
            change [Hit Power] by [4]
            set [Boom X] to (x position)
            broadcast [boom]
            broadcast [shake]
        end
        broadcast [hero hits]
    end
end
hide
set [Fireball Out] to [0]
```

> Flies forward. Small fireball: 3 to 7 damage. Full power: 15 damage, a BOOM and a shake. It always gets past Spike Bot's spikes.

```
when I receive [show title]
hide
set [Fireball Out] to [0]
```

```
when I receive [choose hero]
hide
set [Fireball Out] to [0]
```

```
when I receive [story scene]
hide
set [Fireball Out] to [0]
```

```
when I receive [hero down]
hide
set [Fireball Out] to [0]
```

```
when I receive [enemy down]
hide
set [Fireball Out] to [0]
```

```
when I receive [ending]
hide
set [Fireball Out] to [0]
```

## Explosion

Costumes: boom

```
when green flag clicked
hide
```

```
when I receive [boom]
go to x: (Boom X) y: ([-75] + [70])
set size to [60] %
set [ghost] effect to [0]
show
go to [front] layer
repeat [8]
    change size by [25]
    turn right [15] degrees
    change [ghost] effect by [12]
    wait [0.02] seconds
end
hide
```

## Power Aura

Costumes: lv1 1, lv1 2, lv1 3, lv1 4, lv2 1, lv2 2, lv2 3, lv2 4, lv3 1, lv3 2, lv3 3, lv3 4, lv4 1, lv4 2, lv4 3, lv4 4, lv5 1, lv5 2, lv5 3, lv5 4
Sprite-only variables: Lit, Grow

```
when green flag clicked
hide
forever
    if <<<<(Super) = [100]> or <(Hero Safe) = [2]>> or <(Charge) = [100]>> or <(Melee Charge) = [100]>> then
        set [Lit] to [1]
    else
        set [Lit] to [0]
    end
    if <(Powering) > [0]> then
        set [Lit] to [1]
    end
    set [ghost] effect to (([88] - ([13] * (Power Level))) - ([30] * (Lit)))
    set [brightness] effect to (([5] * (Power Level)) + ([20] * (Lit)))
    set [Grow] to (([0.92] + ([0.05] * (Power Level))) + ([0.12] * (Lit)))
    if <(Powering) = [2]> then
        change [Grow] by ([0.35] + ([0.12] * ((round ((timer) * [12])) mod [2])))
    end
    if <(Powering) = [1]> then
        set [Grow] to (([0.5] + ([0.0075] * (Ki))) * ([1] + ([0.12] * (Power Level))))
        change [Grow] by (([0.06] * ((Ki) / [100])) * ((round ((timer) * [14])) mod [2]))
        set [ghost] effect to ([85] - ((Ki) * ([0.4] + ([0.09] * (Power Level)))))
        set [brightness] effect to ((Ki) * ([0.12] + ([0.06] * (Power Level))))
    end
    if <(State) = [fight]> then
        go to x: (Hero X) y: (Hero Y)
        set size to ([75] * (Grow)) %
        switch costume to (join [lv] (join (Power Level) (join [ ] (((floor of ((timer) * (([8] + ([3] * (Power Level))) + ((Ki) / [6])))) mod [4]) + [1]))))
        show
    else
        if <<<(State) = [brawl]> and <(Brawl Live) = [1]>> and <(item [1] of [B Alive]) = [1]>> then
            go to x: (P1 Screen X) y: (P1 Screen Y)
            set size to ((P1 Screen Size) * (Grow)) %
            if <(Brawl On) = [1]> then
                show
            else
                hide
            end
        else
            if <<(State) = [title]> and <(Power Level) > [1]>> then
                go to x: [-212] y: [-75]
                set size to ([90] * (Grow)) %
                show
            else
                hide
            end
        end
    end
    if <not <(State) = [fight]>> then
        switch costume to (join [lv] (join (Power Level) (join [ ] (((floor of ((timer) * (([8] + ([3] * (Power Level))) + ((Ki) / [6])))) mod [4]) + [1]))))
    end
end
```

> Your aura shows your POWER LEVEL: red, orange, gold, blue, then purple-white with lightning sparks. Each level has more flames and layers, is brighter and bigger and flickers faster. While powering up it starts small and builds with Ki to a blaze. It blazes when you are powered up (SUPER full, during a SUPER or POWER move, or a full fireball charge).

## Lightning

Costumes: bolt hero, bolt enemy, warn
Sprite-only variables: Is Clone, Bx, By, Who, Pw, Sz, J

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [bolt]
if <(Is Clone) = [0]> then
    set [Bx] to (Bolt X)
    set [By] to (Bolt Y)
    set [Who] to (Bolt Owner)
    set [Pw] to (Bolt Power)
    set [Sz] to (Bolt Size)
    create clone of (myself)
end
```

> Lightning from the sky. An enemy's bolt shows a yellow mark first: move away or DODGE. Only the original makes clones (clones hear messages too).

```
when I start as a clone
set [Is Clone] to [1]
set [ghost] effect to [0]
if <(Who) = [enemy]> then
    switch costume to (warn)
    set size to [100] %
    go to x: (Bx) y: (By)
    show
    repeat [4]
        set [ghost] effect to [60]
        wait [0.08] seconds
        set [ghost] effect to [0]
        wait [0.08] seconds
    end
end
if <(Who) = [enemy]> then
    switch costume to (bolt enemy)
else
    switch costume to (bolt hero)
end
set size to (Sz) %
go to x: (Bx) y: (By)
show
go to [front] layer
broadcast [bolt strike]
if <<(Who) = [hero]> and <(Fight On) = [1]>> then
    set [Hit Power] to (Pw)
    broadcast [hero hits]
    if <(Minions) > [0]> then
        set [Area X] to (Bx)
        set [Area R] to [40]
        set [Area Power] to (Pw)
        set [Area Kind] to [bolt]
        broadcast [area hit]
    end
end
if <<<(Who) = [enemy]> and <(Fight On) = [1]>> and <(abs of ((Hero X) - (Bx))) < [30]>> then
    set [Hurt Power] to (Pw)
    broadcast [enemy hits hero]
end
repeat [3]
    set [ghost] effect to [0]
    wait [0.04] seconds
    set [ghost] effect to [55]
    wait [0.04] seconds
end
delete this clone
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
end
```

```
when I receive [story scene]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
end
```

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
else
    hide
end
```

```
when I receive [brawl bolt]
if <(Is Clone) = [0]> then
    set [J] to [0]
    repeat [4]
        change [J] by [1]
        if <<<not <(J) = (Bolt From)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (item (Bolt From) of [B X]))) < ([110] * ((Power Level) - [1]))>> then
            replace item (J) of [B Hit] with ((item (J) of [B Hit]) + ([6] + ([2] * (Power Level))))
            if <(item (J) of [B X]) > (item (Bolt From) of [B X])> then
                set [Pw] to [1]
            else
                set [Pw] to [-1]
            end
            replace item (J) of [B KX] with (([3] + ((item (J) of [B Dmg]) / [12])) * (Pw))
            replace item (J) of [B KY] with ([9] + ((item (J) of [B Dmg]) / [9]))
            set [Bx] to (((item (J) of [B X]) - (Cam X)) * (Zoom))
            set [By] to (((item (J) of [B Y]) - (Cam Y)) * (Zoom))
            set [Who] to [brawl]
            set [Pw] to [0]
            set [Sz] to ((([200] - (By)) / [420]) * [100])
            create clone of (myself)
            wait [0.12] seconds
        end
    end
end
```

## Boss Weapon

Costumes: club, mace, hammer, dark sword, katana
Sprite-only variables: C, D

```
when green flag clicked
hide
forever
    if <<<<<(State) = [fight]> and <not <(Enemy Weapon) = [none]>>> and <(Enemy HP) > [0]>> and <(Wave Phase) = [0]>> and <<(Fight On) = [1]> or <(Enemy X) > [-300]>>> then
        switch costume to (Enemy Weapon)
        set size to ((Enemy Size) * [0.8]) %
        set [C] to ([costume #] of (Enemy))
        go to x: ((Enemy X) + (((item (C) of [EHand X]) * ((Enemy Size) / [100])) * (Enemy Facing))) y: (([y position] of (Enemy)) + ((item (C) of [EHand Y]) * ((Enemy Size) / [100])))
        set [D] to (item (C) of [EHand Dir])
        if <(timer) < (Enemy Swing Until)> then
            change [D] by [40]
        end
        if <(Enemy Facing) = [1]> then
            point in direction ((D) + [90])
        else
            point in direction ([90] - (D))
        end
        show
    else
        hide
    end
end
```

> Bosses carry weapons: Brute a club, MEGA SPIKE a spiked mace, ninjas and MASTER KAGE a katana, Quake a hammer, the Shadow King a dark sword. Each adds 3 to their hits. It swings when they attack.

```
when I receive [enemy down]
hide
```

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

## Crown

Costumes: crown

```
when green flag clicked
hide
forever
    if <<(Crown) = [1]> and <<(State) = [fight]> or <<(State) = [over]> and <not <(Mode) = [brawl]>>>>> then
        go to x: (Hero X) y: ((Hero Y) + [104])
        set size to [80] %
        show
        go to [front] layer
    else
        if <<<(Crown) = [1]> and <(State) = [brawl]>> and <(item [1] of [B Alive]) = [1]>> then
            go to x: (P1 Screen X) y: ((P1 Screen Y) + ((P1 Screen Size) * [1.4]))
            set size to ((P1 Screen Size) * [1.05]) %
            show
            go to [front] layer
        else
            if <not <(State) = [ending]>> then
                hide
            end
        end
    end
end
```

> Beat Story mode once and every fighter wears the Golden Crown.

```
when I receive [crown fall]
go to x: (Hero X) y: [190]
show
go to [front] layer
glide [1.2] secs to x: (Hero X) y: ((Hero Y) + [104])
wait [0.3] seconds
```

## Hero Bar Back

Costumes: track

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        go to x: [-228] y: [156]
        show
    else
        hide
    end
end
```

## Hero Bar

Costumes: green, yellow, red
Sprite-only variables: Pct

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        set [Pct] to (((Hero HP) / (Hero Max)) * [100])
        if <(Pct) < [1]> then
            set [Pct] to [1]
        end
        set size to (Pct) %
        if <(Pct) > [60]> then
            switch costume to (green)
        else
            if <(Pct) > [30]> then
                switch costume to (yellow)
            else
                switch costume to (red)
            end
        end
        go to x: [-228] y: [156]
        show
    else
        hide
    end
end
```

## Super Bar Back

Costumes: track

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        go to x: [-228] y: [138]
        show
    else
        hide
    end
end
```

## Super Bar

Costumes: charging, full
Sprite-only variables: Pct

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        set [Pct] to (((Super) / [100]) * [100])
        if <(Pct) < [1]> then
            set [Pct] to [1]
        end
        set size to (Pct) %
        if <(Super) = [100]> then
            switch costume to (full)
            set [brightness] effect to ([25] * ((round ((timer) * [6])) mod [2]))
        else
            switch costume to (charging)
            set [brightness] effect to [0]
        end
        go to x: [-228] y: [138]
        show
    else
        hide
    end
end
```

## Enemy Bar Back

Costumes: track

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        go to x: [228] y: [156]
        show
    else
        hide
    end
end
```

## Enemy Bar

Costumes: green, yellow, red
Sprite-only variables: Pct

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        set [Pct] to (((Enemy HP) / (Enemy Max)) * [100])
        if <(Pct) < [1]> then
            set [Pct] to [1]
        end
        set size to (Pct) %
        if <(Pct) > [60]> then
            switch costume to (green)
        else
            if <(Pct) > [30]> then
                switch costume to (yellow)
            else
                switch costume to (red)
            end
        end
        go to x: [228] y: [156]
        show
    else
        hide
    end
end
```

## Hero Tag

Costumes: arthur, nova, rocko

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        switch costume to (Hero Name)
        go to x: [-228] y: [174]
        show
    else
        hide
    end
end
```

## Enemy Tag

Costumes: rival, ivy, brute, spikebot, megaspike, ninja, kage, quake, shadow, squad

```
when green flag clicked
hide
forever
    if <<(State) = [fight]> and <(Page HUD) = [0]>> then
        if <(Wave Phase) = [1]> then
            switch costume to (squad)
        else
            switch costume to (Enemy Name)
        end
        go to x: [228] y: [174]
        show
    else
        hide
    end
end
```

## Popup

Costumes: dot
Sprite-only variables: My Text, Is Clone, My Seq

```
when green flag clicked
hide
```

```
when I receive [popup]
if <(Is Clone) = [0]> then
    set [My Text] to (Pop Text)
    change [Pop Seq] by [1]
    if <(State) = [brawl]> then
        go to x: [-70] y: [92]
    else
        go to x: [-70] y: [80]
    end
    create clone of (myself)
end
```

> Shows Pop Text at the top middle of the screen, away from the fighters. A new pop-up replaces the old one, so they never pile up. Clones hear messages too, so only the original makes new clones.

```
when I start as a clone
set [Is Clone] to [1]
set [My Seq] to (Pop Seq)
show
say (My Text)
repeat [18]
    if <(Pop Seq) > (My Seq)> then
        delete this clone
    end
    wait [0.06] seconds
end
delete this clone
```

```
when I receive [super ready]
if <(Is Clone) = [0]> then
    set [My Text] to [SUPER READY! Tap SUPER]
    change [Pop Seq] by [1]
    go to x: [-70] y: [80]
    create clone of (myself)
end
```

## Enemy Talk

Costumes: dot
Sprite-only variables: Said

```
when green flag clicked
set [Enemy Says] to []
set [Said] to []
say []
show
forever
    if <not <(Enemy Says) = []>> then
        go to x: ((Enemy X) - [30]) y: [22]
        if <not <(Said) = (Enemy Says)>> then
            set [Said] to (Enemy Says)
            say (Enemy Says)
        end
        go to [front] layer
    else
        if <not <(Said) = []>> then
            set [Said] to []
            say []
        end
    end
end
```

> Says what the enemy or boss says (Enemy Says), next to them but below the health bars.

```
when I receive [show title]
set [Enemy Says] to []
```

```
when I receive [choose hero]
set [Enemy Says] to []
```

```
when I receive [brawl start]
set [Enemy Says] to []
```

```
when I receive [intro]
set [Enemy Says] to []
```

## Hit Spark

Costumes: spark
Sprite-only variables: Is Clone

```
when green flag clicked
hide
```

```
when I receive [enemy hurt]
if <(Is Clone) = [0]> then
    go to x: (Enemy X) y: ([-75] + [60])
    create clone of (myself)
end
```

> Only the original makes sparks; clones hear messages too.

```
when I receive [hero hurt]
if <(Is Clone) = [0]> then
    go to x: (Hero X) y: ([-75] + [50])
    create clone of (myself)
end
```

```
when I start as a clone
set [Is Clone] to [1]
point in direction (pick random [0] to [90])
set size to [40] %
show
go to [front] layer
repeat [5]
    change size by [14]
    change [ghost] effect by [18]
    wait [0.02] seconds
end
delete this clone
```

## Banner

Costumes: ready, fight, ko, clear, wave clear, boss, game, stage clear, power up

```
when green flag clicked
hide
```

```
when I receive [banner]
switch costume to (Banner)
go to x: [0] y: [40]
set size to [40] %
show
go to [front] layer
repeat [6]
    change size by [10]
end
wait [0.7] seconds
hide
```

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [game over]
hide
```

## Story Card

Costumes: prologue, chapter 1, chapter 2, chapter 3, chapter 4, chapter 5, chapter 6, chapter 7, chapter 8, chapter 9, game over, arcade over, brawl win, brawl lose, the end, angry, kage angry, overdrive
Sprite-only variables: Until, SS Run

```
when green flag clicked
hide
```

```
when I receive [story scene]
set [SS Run] to (Session)
set [State] to [story]
set [Skip] to [0]
hide
broadcast [load enemy] and wait
if <not <(SS Run) = (Session)>> then
    stop [this script]
end
broadcast [skip on]
if <(Chapter) = [1]> then
    switch costume to (prologue)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [3.2])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    switch costume to (chapter 1)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [Nobody gets past the gate!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Then let's fight!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [2]> then
    switch costume to (chapter 2)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [My vines see everything.]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Then watch me jump!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [3]> then
    switch costume to (chapter 3)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [BRUTE... SMASH!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Not if I move first!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [4]> then
    switch costume to (chapter 4)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [BZZT! SPIKES... ONLINE!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Then I'll use FIREBALLS!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [5]> then
    switch costume to (chapter 5)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [I AM MEGA SPIKE! FEEL MY SPIKES!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Then I'll fight smart!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [6]> then
    switch costume to (chapter 6)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [You will never see us coming...]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [I can see you right now!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [7]> then
    switch costume to (chapter 7)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [I am MASTER KAGE. My ninjas are everywhere!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Then I'll beat every one of them!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [8]> then
    switch costume to (chapter 8)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [Feel the ground shake!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [I'll jump right over it!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
if <(Chapter) = [9]> then
    switch costume to (chapter 9)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [The Golden Crown is MINE!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
    if <(Skip) = [0]> then
        set [Line] to [Not for long!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
    if <not <(SS Run) = (Session)>> then
        stop [this script]
    end
end
broadcast [skip off]
if <not <(SS Run) = (Session)>> then
    stop [this script]
end
broadcast [start fight]
```

> Chapter card, then the hero and the enemy talk. SKIP jumps straight to the fight.

```
when I receive [ending]
set [Skip] to [0]
broadcast [skip on]
if <(Skip) = [0]> then
    set [Line] to [No! My crown...]
    set [Line Secs] to [2.2]
    broadcast [enemy line] and wait
end
if <(Skip) = [0]> then
    set [Line] to [It belongs to the whole arena!]
    set [Line Secs] to [2.2]
    broadcast [hero line] and wait
end
broadcast [crown fall] and wait
if <(Skip) = [0]> then
    set [Line] to [I did it!]
    set [Line Secs] to [2.2]
    broadcast [hero line] and wait
end
broadcast [skip off]
set [Crown] to [1]
switch costume to (the end)
set size to [70] %
go to x: [0] y: [82]
show
go to [front] layer
wait [0.5] seconds
broadcast [show home]
```

> After the Shadow King: the crown drops onto the hero. Beating Story once gives every fighter the crown.

```
when I receive [king angry]
if <(Enemy Type) = [9]> then
    switch costume to (angry)
else
    if <(Enemy Type) = [7]> then
        switch costume to (kage angry)
    else
        switch costume to (overdrive)
    end
end
set size to [80] %
go to x: [0] y: [60]
show
go to [front] layer
wait [1.4] seconds
hide
```

```
when I receive [game over]
if <(Mode) = [arcade]> then
    switch costume to (arcade over)
else
    switch costume to (game over)
end
if <(Mode) = [brawl]> then
    if <(Brawl Winner) = (My Slot)> then
        switch costume to (brawl win)
    else
        switch costume to (brawl lose)
    end
end
set size to [85] %
go to x: [0] y: [-5]
show
go to [front] layer
```

```
when I receive [show title]
hide
set size to [100] %
```

```
when I receive [choose hero]
hide
set size to [100] %
```

```
when I receive [start fight]
hide
set size to [100] %
```

```
when I receive [fight on]
hide
set size to [100] %
```

```
when I receive [brawl start]
hide
set size to [100] %
```

## Left Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
broadcast [move left]
wait [0.25] seconds
repeat until <not <mouse down?>>
    broadcast [move left]
    wait [0.09] seconds
end
```

> Tap to step. Hold to keep walking.

```
when I receive [fight on]
go to x: [-212] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Right Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
broadcast [move right]
wait [0.25] seconds
repeat until <not <mouse down?>>
    broadcast [move right]
    wait [0.09] seconds
end
```

> Tap to step. Hold to keep walking.

```
when I receive [fight on]
go to x: [-159] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Jump Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Want Jump] to [1]
```

> Sets Want Jump. Hero's loop does the move.

```
when I receive [fight on]
go to x: [-106] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Dodge Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Want Dodge] to [1]
```

> Sets Want Dodge. Hero's loop does the move.

```
when I receive [fight on]
go to x: [-53] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Punch Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Want Punch] to [1]
set [Punch Held] to [1]
wait until <not <mouse down?>>
set [Punch Held] to [0]
```

> Tap for a quick move. Hold to charge a power move (Punch Held).

```
when I receive [fight on]
go to x: [0] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Kick Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Want Kick] to [1]
set [Kick Held] to [1]
wait until <not <mouse down?>>
set [Kick Held] to [0]
```

> Tap for a quick move. Hold to charge a power move (Kick Held).

```
when I receive [fight on]
go to x: [53] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Fire Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Fire Held] to [1]
wait until <not <mouse down?>>
set [Fire Held] to [0]
```

> Hold to charge a fireball, let go to shoot.

```
when I receive [fight on]
go to x: [106] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Power Button

Costumes: button

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Want Power] to [1]
```

> Sets Want Power. Hero's loop does the move.

```
when I receive [fight on]
go to x: [159] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

## Super Button

Costumes: button, ready

```
when green flag clicked
hide
```

```
when this sprite clicked
set [Want Super] to [1]
```

> Sets Want Super. Hero's loop does the move.

```
when I receive [fight on]
go to x: [212] y: [-152]
if <(Touch Pad) = [0]> then
    show
    go to [front] layer
end
```

> Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).

```
when I receive [show title]
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [ending]
hide
```

```
when green flag clicked
forever
    if <(Super) = [100]> then
        switch costume to (ready)
    else
        switch costume to (button)
    end
end
```

## Power Badge

Costumes: lv1, lv2, lv3, lv4, lv5

```
when green flag clicked
hide
```

```
when I receive [show title]
go to x: [-160] y: [-140]
switch costume to (join [lv] (Power Level))
show
go to [front] layer
```

> Your POWER LEVEL on the title screen.

```
when I receive [choose hero]
hide
```

## Practice Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [show title]
go to x: [132] y: [-90]
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
set [Mode] to [practice]
broadcast [choose hero]
```

> Grok's practice fight: a dummy that never hits back and never goes down. Try every move.

## Help Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [show title]
go to x: [214] y: [-136]
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
broadcast [show help]
```

## Help Card

Costumes: help

```
when green flag clicked
hide
```

```
when I receive [show help]
set size to [85] %
go to x: [0] y: [22]
show
go to [front] layer
```

> Grok's how-to-play card.

```
when this sprite clicked
hide
```

```
when I receive [choose hero]
hide
```

```
when I receive [start fight]
hide
```

```
when I receive [brawl start]
hide
```

## Sound Button

Costumes: on, off

```
when green flag clicked
hide
```

```
when I receive [show title]
go to x: [166] y: [-136]
if <(Sound On) = [1]> then
    switch costume to (on)
else
    switch costume to (off)
end
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
set [Sound On] to ([1] - (Sound On))
if <(Sound On) = [1]> then
    switch costume to (on)
else
    switch costume to (off)
end
```

> Grok's sound on/off. The app remembers it.

## Version

Costumes: v

```
when green flag clicked
hide
```

```
when I receive [show title]
go to x: [214] y: [-172]
show
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
broadcast [toggle debug]
```

> Tap the version number to show or hide Mitch's debug overlay.

## Level Button

Costumes: easy, normal, hard, champion

```
when green flag clicked
hide
```

```
when I receive [show title]
go to x: [-30] y: [-90]
if <(Difficulty) = [1]> then
    switch costume to (easy)
end
if <(Difficulty) = [2]> then
    switch costume to (normal)
end
if <(Difficulty) = [3]> then
    switch costume to (hard)
end
if <(Difficulty) = [4]> then
    switch costume to (champion)
end
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
change [Difficulty] by [1]
if <(Difficulty) > [4]> then
    set [Difficulty] to [1]
end
if <(Difficulty) = [1]> then
    switch costume to (easy)
end
if <(Difficulty) = [2]> then
    switch costume to (normal)
end
if <(Difficulty) = [3]> then
    switch costume to (hard)
end
if <(Difficulty) = [4]> then
    switch costume to (champion)
end
broadcast [swing sfx]
```

> Tap to change the level: EASY, NORMAL, HARD, CHAMPION. Higher levels give enemies more health (longer fights), harder hits and faster attacks.

## Story Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [show title]
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
set [Mode] to [story]
broadcast [choose hero]
```

## Adventure Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [show title]
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
set [Mode] to [adventure]
broadcast [choose hero]
```

## Arcade Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [show title]
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
set [Mode] to [arcade]
broadcast [choose hero]
```

## Brawl Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [show title]
show
go to [front] layer
```

```
when I receive [choose hero]
hide
```

```
when this sprite clicked
set [Mode] to [brawl]
broadcast [choose hero]
```

## Pick Arthur

Costumes: card

```
when green flag clicked
hide
```

```
when I receive [choose hero]
go to x: [-150] y: [-10]
set size to [100] %
show
```

```
when I receive [show title]
hide
```

```
when I receive [hero picked]
hide
```

```
when this sprite clicked
set [Hero] to [1]
broadcast [hero picked]
```

> ARTHUR: All-rounder. Super move: HERO SLASH.

## Pick Nova

Costumes: card

```
when green flag clicked
hide
```

```
when I receive [choose hero]
go to x: [0] y: [-10]
set size to [100] %
show
```

```
when I receive [show title]
hide
```

```
when I receive [hero picked]
hide
```

```
when this sprite clicked
set [Hero] to [2]
broadcast [hero picked]
```

> NOVA: Super fast. Super move: STAR DASH.

## Pick Rocko

Costumes: card

```
when green flag clicked
hide
```

```
when I receive [choose hero]
go to x: [150] y: [-10]
set size to [100] %
show
```

```
when I receive [show title]
hide
```

```
when I receive [hero picked]
hide
```

```
when this sprite clicked
set [Hero] to [3]
broadcast [hero picked]
```

> ROCKO: Super strong. Super move: ROCK SLAM.

## Skip Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [skip on]
show
go to [front] layer
```

```
when I receive [skip off]
hide
```

```
when I receive [show title]
hide
```

```
when I receive [start fight]
hide
```

```
when this sprite clicked
set [Skip] to [1]
hide
```

> Skips the talking, like a cutscene skip.

## Retry Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [game over]
go to x: [-70] y: [-150]
show
go to [front] layer
```

```
when I receive [show title]
hide
```

```
when I receive [start fight]
hide
```

```
when I receive [brawl start]
hide
```

```
when this sprite clicked
hide
if <(Mode) = [arcade]> then
    set [Wave] to [1]
    set [Score] to [0]
    set [Hero HP] to (Hero Max)
end
set [Super] to [0]
if <(Mode) = [brawl]> then
    set [Score] to [0]
    broadcast [brawl start]
else
    if <(Mode) = [adventure]> then
        set [Hero HP] to (Hero Max)
        broadcast [adventure stage]
    else
        broadcast [start fight]
    end
end
```

> Story: try the same chapter again (no talking). Arcade: a new run from wave 1.

## Home Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [game over]
go to x: [70] y: [-150]
show
go to [front] layer
```

```
when I receive [show home]
go to x: [0] y: [-150]
show
go to [front] layer
```

```
when I receive [show title]
hide
```

```
when I receive [start fight]
hide
```

```
when I receive [brawl start]
hide
```

```
when this sprite clicked
hide
broadcast [show title]
```

## Quit Button

Costumes: button

```
when green flag clicked
hide
```

```
when I receive [fight on]
if <(Page HUD) = [0]> then
    go to x: [0] y: [165]
    show
    go to [front] layer
end
```

```
when I receive [brawl go]
if <(Page HUD) = [0]> then
    go to x: [0] y: [165]
    show
    go to [front] layer
end
```

```
when I receive [brawl end]
hide
```

```
when I receive [choose hero]
go to x: [-218] y: [-160]
show
go to [front] layer
```

```
when I receive [show title]
hide
```

```
when I receive [hero down]
hide
```

```
when I receive [enemy down]
hide
```

```
when I receive [story scene]
hide
```

```
when I receive [hero picked]
hide
```

```
when this sprite clicked
hide
set [Fight On] to [0]
broadcast [show title]
```

> Back to the title at any time.

## Brawler

Costumes: arthur idle, arthur punch, arthur kick, arthur jump, arthur hurt, arthur special, arthur idle b, arthur walk 1, arthur walk 2, arthur walk 3, arthur walk 4, arthur fall, arthur hurt high, arthur spin 1, arthur spin 2, arthur spin 3, arthur spin 4, arthur flip 1, arthur flip 2, arthur flip 3, arthur flip 4, nova idle, nova punch, nova kick, nova jump, nova hurt, nova special, nova idle b, nova walk 1, nova walk 2, nova walk 3, nova walk 4, nova fall, nova hurt high, nova spin 1, nova spin 2, nova spin 3, nova spin 4, nova flip 1, nova flip 2, nova flip 3, nova flip 4, rocko idle, rocko punch, rocko kick, rocko jump, rocko hurt, rocko special, rocko idle b, rocko walk 1, rocko walk 2, rocko walk 3, rocko walk 4, rocko fall, rocko hurt high, rocko spin 1, rocko spin 2, rocko spin 3, rocko spin 4, rocko flip 1, rocko flip 2, rocko flip 3, rocko flip 4, rival idle, rival punch, rival kick, rival jump, rival hurt, rival special, rival idle b, rival walk 1, rival walk 2, rival walk 3, rival walk 4, rival fall, rival hurt high, rival spin 1, rival spin 2, rival spin 3, rival spin 4, rival flip 1, rival flip 2, rival flip 3, rival flip 4, ivy idle, ivy punch, ivy kick, ivy jump, ivy hurt, ivy special, ivy idle b, ivy walk 1, ivy walk 2, ivy walk 3, ivy walk 4, ivy fall, ivy hurt high, ivy spin 1, ivy spin 2, ivy spin 3, ivy spin 4, ivy flip 1, ivy flip 2, ivy flip 3, ivy flip 4, brute idle, brute punch, brute kick, brute jump, brute hurt, brute special, brute idle b, brute walk 1, brute walk 2, brute walk 3, brute walk 4, brute fall, brute hurt high, brute spin 1, brute spin 2, brute spin 3, brute spin 4, brute flip 1, brute flip 2, brute flip 3, brute flip 4, quake idle, quake punch, quake kick, quake jump, quake hurt, quake special, quake idle b, quake walk 1, quake walk 2, quake walk 3, quake walk 4, quake fall, quake hurt high, quake spin 1, quake spin 2, quake spin 3, quake spin 4, quake flip 1, quake flip 2, quake flip 3, quake flip 4, shadow idle, shadow punch, shadow kick, shadow jump, shadow hurt, shadow special, shadow idle b, shadow walk 1, shadow walk 2, shadow walk 3, shadow walk 4, shadow fall, shadow hurt high, shadow spin 1, shadow spin 2, shadow spin 3, shadow spin 4, shadow flip 1, shadow flip 2, shadow flip 3, shadow flip 4, ninja idle, ninja punch, ninja kick, ninja jump, ninja hurt, ninja special, ninja idle b, ninja walk 1, ninja walk 2, ninja walk 3, ninja walk 4, ninja fall, ninja hurt high, ninja spin 1, ninja spin 2, ninja spin 3, ninja spin 4, ninja flip 1, ninja flip 2, ninja flip 3, ninja flip 4
Sprite-only variables: Is Clone, My Id, Kind, X, Y, VX, VY, Ground, Was Ground, Jumps, Stun, Atk CD, Pose Until, Speed, Punch, Kick, Weight, Face, Inv Until, Tgt, Think, Dir, Want Atk, Want Hop, J, Surf, NX, NY, Reach, Power, KB, Move Dir, Move Until, Smash, Dash, Flip, Spin, Whirl, Kick At, Kick Queued, Whirl Ready At, Best D, D, On Plat, Drop

```
define (fighter frame)   [run without screen refresh]
if <(item (My Id) of [B Hit]) > [0]> then
    if <(Inv Until) > (timer)> then
        replace item (My Id) of [B Hit] with [0]
    else
        replace item (My Id) of [B Dmg] with ((item (My Id) of [B Dmg]) + (item (My Id) of [B Hit]))
        replace item (My Id) of [B Hit] with [0]
        set [VX] to ((item (My Id) of [B KX]) / (Weight))
        set [VY] to ((item (My Id) of [B KY]) / (Weight))
        set [Stun] to ([8] + ((abs of (VX)) * [1.6]))
        set [Ground] to [0]
        if <(VY) > [8]> then
            switch costume to (join (Kind) [ hurt high])
        else
            switch costume to (join (Kind) [ hurt])
        end
        set [brightness] effect to [50]
    end
end
set [Want Atk] to [0]
set [Want Hop] to [0]
set [Dir] to [0]
if <<(Brawl On) = [1]> and <not <(Stun) > [0]>>> then
    if <(My Id) = [1]> then
        if <(abs of (Joy X)) > [0.2]> then
            set [Dir] to (Joy X)
        else
            if <(timer) < (Move Until)> then
                set [Dir] to (Move Dir)
            else
                set [Dir] to [0]
            end
        end
        if <(Want Jump) = [1]> then
            set [Want Jump] to [0]
            set [Want Hop] to [1]
        end
        if <<(Joy Y) < [-0.6]> or <(Want Drop) = [1]>> then
            set [Want Drop] to [0]
            if <<(Ground) = [1]> and <(On Plat) > (Solid Count)>> then
                set [Drop] to [8]
                set [Ground] to [0]
            end
        end
        if <<(Want Punch) = [1]> and <not <(Atk CD) > [0]>>> then
            set [Want Punch] to [0]
            set [Want Atk] to [1]
        end
        if <<<(Want Kick) = [1]> and <(Atk CD) > [0]>> and <(Kick At) > [0]>> then
            set [Kick Queued] to [1]
        end
        if <<(Want Kick) = [1]> and <not <(Atk CD) > [0]>>> then
            set [Want Kick] to [0]
            if <<<((timer) - (Kick At)) < [0.8]> or <(Kick Queued) = [1]>> and <(timer) > (Whirl Ready At)>> then
                set [Kick At] to [0]
                set [Whirl Ready At] to ((timer) + [1.2])
                set [Want Atk] to [5]
            else
                set [Kick At] to (timer)
                set [Want Atk] to [2]
            end
            set [Kick Queued] to [0]
        end
        if <(Want Super) = [1]> then
            set [Want Super] to [0]
            if <(Super) = [100]> then
                set [Want Atk] to [3]
            end
        end
        if <(Want Power) = [1]> then
            set [Want Power] to [0]
            if <<(Power Level) > [1]> and <(timer) > (Power Ready At)>> then
                set [Power Ready At] to ((timer) + [6])
                broadcast [power flash]
                if <(Power Level) = [2]> then
                    set [Want Atk] to [4]
                else
                    set [Pop Text] to [THUNDER!]
                    broadcast [popup]
                    set [Bolt From] to (My Id)
                    broadcast [brawl bolt]
                end
            end
        end
        if <(Want Dodge) = [1]> then
            set [Want Dodge] to [0]
            set [Inv Until] to ((timer) + [0.45])
            set [VX] to ((Face) * [-6])
        end
        if <<(Fire Held) = [1]> or <key (f) pressed?>> then
            if <(Charge) < [100]> then
                change [Charge] by [3.5]
            end
            if <(Charge) > [99]> then
                set [Charge] to [100]
            end
            set [Dir] to ((Dir) * [0.4])
        else
            if <<(Charge) > [0]> and <(BF Power) = [0]>> then
                set [BF X] to ((X) + ([20] * (Face)))
                set [BF Y] to ((Y) + [40])
                set [BF Dir] to (Face)
                set [BF Owner] to (My Id)
                set [BF Power] to ((Charge) + [1])
                broadcast [brawl fire]
                set [Fire Power] to (Charge)
                broadcast [fire]
            end
            set [Charge] to [0]
        end
    else
        if <<(My Id) = [2]> and <(Net Players) = [2]>> then
            if <(abs of (P2 Joy X)) > [0.2]> then
                set [Dir] to (P2 Joy X)
            else
                if <(timer) < (Move Until)> then
                    set [Dir] to (Move Dir)
                else
                    set [Dir] to [0]
                end
            end
            if <(P2 Want Jump) = [1]> then
                set [P2 Want Jump] to [0]
                set [Want Hop] to [1]
            end
            if <<(P2 Joy Y) < [-0.6]> or <(P2 Want Drop) = [1]>> then
                set [P2 Want Drop] to [0]
                if <<(Ground) = [1]> and <(On Plat) > (Solid Count)>> then
                    set [Drop] to [8]
                    set [Ground] to [0]
                end
            end
            if <<(P2 Want Punch) = [1]> and <not <(Atk CD) > [0]>>> then
                set [P2 Want Punch] to [0]
                set [Want Atk] to [1]
            end
            if <<<(P2 Want Kick) = [1]> and <(Atk CD) > [0]>> and <(Kick At) > [0]>> then
                set [Kick Queued] to [1]
            end
            if <<(P2 Want Kick) = [1]> and <not <(Atk CD) > [0]>>> then
                set [P2 Want Kick] to [0]
                if <<<((timer) - (Kick At)) < [0.8]> or <(Kick Queued) = [1]>> and <(timer) > (Whirl Ready At)>> then
                    set [Kick At] to [0]
                    set [Whirl Ready At] to ((timer) + [1.2])
                    set [Want Atk] to [5]
                else
                    set [Kick At] to (timer)
                    set [Want Atk] to [2]
                end
                set [Kick Queued] to [0]
            end
            if <(P2 Want Super) = [1]> then
                set [P2 Want Super] to [0]
                if <(P2 Super) = [100]> then
                    set [Want Atk] to [3]
                end
            end
            if <(P2 Want Power) = [1]> then
                set [P2 Want Power] to [0]
                if <<(Power Level) > [1]> and <(timer) > (P2 Power Ready At)>> then
                    set [P2 Power Ready At] to ((timer) + [6])
                    broadcast [power flash]
                    if <(Power Level) = [2]> then
                        set [Want Atk] to [4]
                    else
                        set [Pop Text] to [THUNDER!]
                        broadcast [popup]
                        set [Bolt From] to (My Id)
                        broadcast [brawl bolt]
                    end
                end
            end
            if <(P2 Want Dodge) = [1]> then
                set [P2 Want Dodge] to [0]
                set [Inv Until] to ((timer) + [0.45])
                set [VX] to ((Face) * [-6])
            end
            if <<(P2 Fire Held) = [1]> or <key (f) pressed?>> then
                if <(P2 Charge) < [100]> then
                    change [P2 Charge] by [3.5]
                end
                if <(P2 Charge) > [99]> then
                    set [P2 Charge] to [100]
                end
                set [Dir] to ((Dir) * [0.4])
            else
                if <<(P2 Charge) > [0]> and <(BF Power) = [0]>> then
                    set [BF X] to ((X) + ([20] * (Face)))
                    set [BF Y] to ((Y) + [40])
                    set [BF Dir] to (Face)
                    set [BF Owner] to (My Id)
                    set [BF Power] to ((P2 Charge) + [1])
                    broadcast [brawl fire]
                    set [Fire Power] to (P2 Charge)
                    broadcast [fire]
                end
                set [P2 Charge] to [0]
            end
        else
            if <<<(Tgt) = [0]> or <(pick random [1] to [20]) = [1]>> or <(item (Tgt) of [B Alive]) = [0]>> then
                set [Best D] to [99999]
                set [J] to [0]
                repeat [4]
                    change [J] by [1]
                    if <<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> then
                        set [D] to ((abs of ((item (J) of [B X]) - (X))) + (abs of ((item (J) of [B Y]) - (Y))))
                        if <(D) < (Best D)> then
                            set [Best D] to (D)
                            set [Tgt] to (J)
                        end
                    end
                end
            end
            set [Dir] to [0]
            if <<<(X) < [-300]> or <(X) > [300]>> or <(Y) < [-150]>> then
                if <(X) > [0]> then
                    set [Dir] to [-1]
                else
                    set [Dir] to [1]
                end
                if <<(VY) < [0]> and <(Jumps) < [3]>> then
                    set [Want Hop] to [1]
                end
            else
                if <(Tgt) > [0]> then
                    set [D] to ((item (Tgt) of [B X]) - (X))
                    if <(abs of (D)) > [38]> then
                        if <(D) > [0]> then
                            set [Dir] to [1]
                        else
                            set [Dir] to [-1]
                        end
                    end
                    if <((item (Tgt) of [B Y]) - (Y)) > [45]> then
                        if <<(Ground) = [1]> and <(pick random [1] to [6]) = [1]>> then
                            set [Want Hop] to [1]
                        end
                        if <<<(Ground) = [0]> and <(Jumps) = [1]>> and <(VY) < [1]>> then
                            set [Want Hop] to [1]
                        end
                    end
                    if <<((item (Tgt) of [B Y]) - (Y)) < [-50]> and <(pick random [1] to [15]) = [1]>> then
                        if <<(Ground) = [1]> and <(On Plat) > (Solid Count)>> then
                            set [Drop] to [8]
                            set [Ground] to [0]
                        end
                    end
                    if <<<(abs of (D)) < [48]> and <(abs of ((item (Tgt) of [B Y]) - (Y))) < [45]>> and <(pick random [0.0] to [1.0]) < (Think)>> then
                        set [Want Atk] to (pick random [1] to [2])
                    end
                end
            end
        end
    end
end
if <(Stun) > [0]> then
    change [Stun] by [-1]
    set [VX] to ((VX) * [0.96])
    if <(Stun) < [1]> then
        set [brightness] effect to [0]
    end
else
    if <(Ground) = [1]> then
        change [VX] by ((((Dir) * (Speed)) - (VX)) * (Stage Grip))
    else
        if <not <((Dir) * (VX)) > (Speed)>> then
            change [VX] by ((((Dir) * (Speed)) - (VX)) * [0.2])
        end
    end
    if <(Dir) > [0.1]> then
        set [Face] to [1]
    end
    if <(Dir) < [-0.1]> then
        set [Face] to [-1]
    end
end
if <<(Want Hop) = [1]> and <<(Jumps) < [2]> or <<(Jumps) = [2]> and <<(abs of (X)) > [250]> or <(Y) < (item [1] of [Plat Y1])>>>>> then
    if <(Jumps) = [0]> then
        set [VY] to [13.5]
        change [VX] by ((Dir) * [2.4])
    end
    if <(Jumps) = [1]> then
        set [VY] to [12]
        set [Flip] to [16]
        if <(abs of (Dir)) > [0.2]> then
            set [VX] to ((Dir) * ((Speed) + [4.8]))
        end
    end
    if <(Jumps) = [2]> then
        set [VY] to [15]
        set [Flip] to [16]
        if <(X) > [0]> then
            set [VX] to [-7]
        else
            set [VX] to [7]
        end
        if <(My Id) = (My Slot)> then
            set [Pop Text] to [RECOVERY ROCKET!]
            broadcast [popup]
        end
        broadcast [whirl sfx]
    end
    change [Jumps] by [1]
    set [Ground] to [0]
    broadcast [jump sfx]
end
if <(Atk CD) > [0]> then
    change [Atk CD] by [-1]
end
if <<(Want Atk) > [0]> and <not <(Atk CD) > [0]>>> then
    if <(Want Atk) = [1]> then
        switch costume to (join (Kind) [ punch])
        set [Reach] to [46]
        set [Power] to (Punch)
        if <(My Id) > [1]> then
            if <(Difficulty) = [1]> then
                set [Power] to (((Power) * [0.75]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [2]> then
                set [Power] to (((Power) * [1]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [3]> then
                set [Power] to (((Power) * [1.15]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [4]> then
                set [Power] to (((Power) * [1.3]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
        end
        set [J] to [0]
        repeat [4]
            change [J] by [1]
            if <<<<<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (X))) < (Reach)>> and <(abs of ((item (J) of [B Y]) - (Y))) < [50]>> and <(((item (J) of [B X]) - (X)) * (Face)) > [-12]>> then
                set [KB] to (([3] + ((Power) * [0.5])) + ((((item (J) of [B Dmg]) + (Power)) * (Power)) * [0.019]))
                replace item (J) of [B Hit] with ((item (J) of [B Hit]) + (Power))
                replace item (J) of [B KX] with ((Face) * (KB))
                replace item (J) of [B KY] with (((KB) * [0.6]) + [3])
                if <(My Id) = [1]> then
                    if <(Super) < [100]> then
                        change [Super] by [5]
                    end
                    if <(Super) > [100]> then
                        set [Super] to [100]
                    end
                end
                if <<(My Id) = [2]> and <(Net Players) = [2]>> then
                    if <(P2 Super) < [100]> then
                        change [P2 Super] by [5]
                    end
                    if <(P2 Super) > [100]> then
                        set [P2 Super] to [100]
                    end
                end
                broadcast [brawl hit]
            end
        end
        set [Atk CD] to [9]
    end
    if <(Want Atk) = [2]> then
        switch costume to (join (Kind) [ kick])
        set [Reach] to [56]
        set [Power] to (Kick)
        if <(My Id) > [1]> then
            if <(Difficulty) = [1]> then
                set [Power] to (((Power) * [0.75]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [2]> then
                set [Power] to (((Power) * [1]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [3]> then
                set [Power] to (((Power) * [1.15]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [4]> then
                set [Power] to (((Power) * [1.3]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
        end
        set [J] to [0]
        repeat [4]
            change [J] by [1]
            if <<<<<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (X))) < (Reach)>> and <(abs of ((item (J) of [B Y]) - (Y))) < [50]>> and <(((item (J) of [B X]) - (X)) * (Face)) > [-12]>> then
                set [KB] to (([3] + ((Power) * [0.5])) + ((((item (J) of [B Dmg]) + (Power)) * (Power)) * [0.019]))
                replace item (J) of [B Hit] with ((item (J) of [B Hit]) + (Power))
                replace item (J) of [B KX] with ((Face) * (KB))
                replace item (J) of [B KY] with (((KB) * [0.6]) + [3])
                if <(My Id) = [1]> then
                    if <(Super) < [100]> then
                        change [Super] by [5]
                    end
                    if <(Super) > [100]> then
                        set [Super] to [100]
                    end
                end
                if <<(My Id) = [2]> and <(Net Players) = [2]>> then
                    if <(P2 Super) < [100]> then
                        change [P2 Super] by [5]
                    end
                    if <(P2 Super) > [100]> then
                        set [P2 Super] to [100]
                    end
                end
                broadcast [brawl hit]
            end
        end
        set [Atk CD] to [16]
    end
    if <(Want Atk) = [3]> then
        switch costume to (join (Kind) [ special])
        if <(My Id) = [2]> then
            set [P2 Super] to [0]
        else
            set [Super] to [0]
        end
        set [Smash] to [16]
        set [Reach] to [70]
        set [Power] to (Smash)
        set [J] to [0]
        repeat [4]
            change [J] by [1]
            if <<<<<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (X))) < (Reach)>> and <(abs of ((item (J) of [B Y]) - (Y))) < [50]>> and <(((item (J) of [B X]) - (X)) * (Face)) > [-12]>> then
                set [KB] to (([3] + ((Power) * [0.5])) + ((((item (J) of [B Dmg]) + (Power)) * (Power)) * [0.019]))
                replace item (J) of [B Hit] with ((item (J) of [B Hit]) + (Power))
                replace item (J) of [B KX] with ((Face) * (KB))
                replace item (J) of [B KY] with (((KB) * [0.6]) + [3])
                if <(My Id) = [1]> then
                    if <(Super) < [100]> then
                        change [Super] by [5]
                    end
                    if <(Super) > [100]> then
                        set [Super] to [100]
                    end
                end
                if <<(My Id) = [2]> and <(Net Players) = [2]>> then
                    if <(P2 Super) < [100]> then
                        change [P2 Super] by [5]
                    end
                    if <(P2 Super) > [100]> then
                        set [P2 Super] to [100]
                    end
                end
                broadcast [brawl smash]
            end
        end
        set [Atk CD] to [20]
        set [Pop Text] to [SMASH!]
        broadcast [popup]
    end
    if <(Want Atk) = [4]> then
        switch costume to (join (Kind) [ special])
        set [VX] to ((Face) * [15])
        set [Dash] to [9]
        set [Reach] to [64]
        set [Power] to (Dash)
        set [J] to [0]
        repeat [4]
            change [J] by [1]
            if <<<<<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (X))) < (Reach)>> and <(abs of ((item (J) of [B Y]) - (Y))) < [50]>> and <(((item (J) of [B X]) - (X)) * (Face)) > [-12]>> then
                set [KB] to (([3] + ((Power) * [0.5])) + ((((item (J) of [B Dmg]) + (Power)) * (Power)) * [0.019]))
                replace item (J) of [B Hit] with ((item (J) of [B Hit]) + (Power))
                replace item (J) of [B KX] with ((Face) * (KB))
                replace item (J) of [B KY] with (((KB) * [0.6]) + [3])
                if <(My Id) = [1]> then
                    if <(Super) < [100]> then
                        change [Super] by [5]
                    end
                    if <(Super) > [100]> then
                        set [Super] to [100]
                    end
                end
                if <<(My Id) = [2]> and <(Net Players) = [2]>> then
                    if <(P2 Super) < [100]> then
                        change [P2 Super] by [5]
                    end
                    if <(P2 Super) > [100]> then
                        set [P2 Super] to [100]
                    end
                end
                broadcast [brawl smash]
            end
        end
        set [Atk CD] to [14]
        set [Pop Text] to [FLAME DASH!]
        broadcast [popup]
    end
    if <(Want Atk) = [5]> then
        set [Spin] to [15]
        set [VY] to [7]
        set [VX] to ((Face) * [6])
        set [Ground] to [0]
        set [Whirl] to [5]
        set [Reach] to [58]
        set [Power] to (Whirl)
        if <(My Id) > [1]> then
            if <(Difficulty) = [1]> then
                set [Power] to (((Power) * [0.75]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [2]> then
                set [Power] to (((Power) * [1]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [3]> then
                set [Power] to (((Power) * [1.15]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [4]> then
                set [Power] to (((Power) * [1.3]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
        end
        set [J] to [0]
        repeat [4]
            change [J] by [1]
            if <<<<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (X))) < (Reach)>> and <(abs of ((item (J) of [B Y]) - (Y))) < [50]>> then
                set [KB] to (([3] + ((Power) * [0.5])) + ((((item (J) of [B Dmg]) + (Power)) * (Power)) * [0.019]))
                replace item (J) of [B Hit] with ((item (J) of [B Hit]) + (Power))
                if <(item (J) of [B X]) > (X)> then
                    replace item (J) of [B KX] with (KB)
                else
                    replace item (J) of [B KX] with ([0] - (KB))
                end
                replace item (J) of [B KY] with (((KB) * [0.6]) + [3])
                if <(My Id) = [1]> then
                    if <(Super) < [100]> then
                        change [Super] by [5]
                    end
                    if <(Super) > [100]> then
                        set [Super] to [100]
                    end
                end
                if <<(My Id) = [2]> and <(Net Players) = [2]>> then
                    if <(P2 Super) < [100]> then
                        change [P2 Super] by [5]
                    end
                    if <(P2 Super) > [100]> then
                        set [P2 Super] to [100]
                    end
                end
                broadcast [brawl hit]
            end
        end
        set [Atk CD] to [18]
        set [Pop Text] to [WHIRLWIND KICK!]
        broadcast [popup]
        broadcast [whirl sfx]
    end
    set [Pose Until] to ((timer) + [0.18])
end
if <(Spin) > [0]> then
    change [Spin] by [-1]
    set [Pose Until] to ((timer) + [0.05])
    switch costume to (join (Kind) (join [ spin ] (((floor of ((Spin) / [2])) mod [4]) + [1])))
    if <(Spin) = [8]> then
        set [Reach] to [58]
        set [Power] to (Whirl)
        if <(My Id) > [1]> then
            if <(Difficulty) = [1]> then
                set [Power] to (((Power) * [0.75]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [2]> then
                set [Power] to (((Power) * [1]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [3]> then
                set [Power] to (((Power) * [1.15]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
            if <(Difficulty) = [4]> then
                set [Power] to (((Power) * [1.3]) * ([1] + ([0.1] * ((Power Level) - [1]))))
            end
        end
        set [J] to [0]
        repeat [4]
            change [J] by [1]
            if <<<<not <(J) = (My Id)>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (X))) < (Reach)>> and <(abs of ((item (J) of [B Y]) - (Y))) < [50]>> then
                set [KB] to (([3] + ((Power) * [0.5])) + ((((item (J) of [B Dmg]) + (Power)) * (Power)) * [0.019]))
                replace item (J) of [B Hit] with ((item (J) of [B Hit]) + (Power))
                if <(item (J) of [B X]) > (X)> then
                    replace item (J) of [B KX] with (KB)
                else
                    replace item (J) of [B KX] with ([0] - (KB))
                end
                replace item (J) of [B KY] with (((KB) * [0.6]) + [3])
                if <(My Id) = [1]> then
                    if <(Super) < [100]> then
                        change [Super] by [5]
                    end
                    if <(Super) > [100]> then
                        set [Super] to [100]
                    end
                end
                if <<(My Id) = [2]> and <(Net Players) = [2]>> then
                    if <(P2 Super) < [100]> then
                        change [P2 Super] by [5]
                    end
                    if <(P2 Super) > [100]> then
                        set [P2 Super] to [100]
                    end
                end
                broadcast [brawl hit]
            end
        end
    end
end
if <(Drop) > [0]> then
    change [Drop] by [-1]
end
change [VY] by ([-1] * (Stage Grav))
if <(VY) < [-15]> then
    set [VY] to [-15]
end
set [NX] to ((X) + (VX))
set [NY] to ((Y) + (VY))
set [Was Ground] to (Ground)
set [Ground] to [0]
if <not <(VY) > [0]>> then
    set [J] to [0]
    repeat (Plat Count)
        change [J] by [1]
        if <<<(Ground) = [0]> and <<not <(NX) < (item (J) of [Plat X1])>> and <not <(NX) > (item (J) of [Plat X2])>>>> and <<not <(Drop) > [0]>> or <not <(J) > (Solid Count)>>>> then
            set [Surf] to ((item (J) of [Plat Y1]) + (((NX) - (item (J) of [Plat X1])) * (((item (J) of [Plat Y2]) - (item (J) of [Plat Y1])) / ((item (J) of [Plat X2]) - (item (J) of [Plat X1])))))
            if <<not <(NY) > (Surf)>> and <not <((Y) + [12]) < (Surf)>>> then
                set [NY] to (Surf)
                set [VY] to [0]
                set [Ground] to [1]
                set [Jumps] to [0]
                set [Flip] to [0]
                set [On Plat] to (J)
            else
                if <<<<(Was Ground) = [1]> and <(NY) > (Surf)>> and <((NY) - (Surf)) < [10]>> and <not <(Stun) > [0]>>> then
                    set [NY] to (Surf)
                    set [VY] to [0]
                    set [Ground] to [1]
                    set [Jumps] to [0]
                    set [Flip] to [0]
                    set [On Plat] to (J)
                end
            end
        end
    end
end
set [X] to (NX)
set [Y] to (NY)
if <(Ground) = [1]> then
    change [X] by (item (On Plat) of [Plat Push])
    if <(item (On Plat) of [Plat Bounce]) = [1]> then
        set [VY] to [17]
        set [Ground] to [0]
        set [Jumps] to [1]
        broadcast [boing]
    end
end
replace item (My Id) of [B X] with (X)
replace item (My Id) of [B Y] with (Y)
if <<<(abs of (X)) > [560]> or <(Y) < [-360]>> or <(Y) > [470]>> then
    set [Pop Text] to [K.O.!]
    broadcast [popup]
    broadcast [brawl ko]
    replace item (My Id) of [B Stock] with ((item (My Id) of [B Stock]) - [1])
    if <(item (My Id) of [B Stock]) > [0]> then
        set [X] to (pick random [-80] to [80])
        set [Y] to [230]
        set [VX] to [0]
        set [VY] to [0]
        set [Stun] to [0]
        replace item (My Id) of [B Dmg] with [0]
        set [Inv Until] to ((timer) + [2.5])
        replace item (My Id) of [B X] with (X)
        replace item (My Id) of [B Y] with (Y)
    else
        replace item (My Id) of [B Alive] with [0]
        hide
    end
end
if <<(timer) > (Pose Until)> and <not <(Stun) > [0]>>> then
    if <(Ground) = [1]> then
        if <(abs of (VX)) > [0.6]> then
            switch costume to (join (Kind) (join [ walk ] ((floor of ((((X) + [1000]) / [13]) mod [4])) + [1])))
        else
            if <((round ((timer) * [1.6])) mod [2]) = [0]> then
                switch costume to (join (Kind) [ idle])
            else
                switch costume to (join (Kind) [ idle b])
            end
        end
    else
        if <(Flip) > [0]> then
            change [Flip] by [-1]
            switch costume to (join (Kind) (join [ flip ] ((floor of ((([16] - (Flip)) / [4]) mod [4])) + [1])))
        else
            if <(VY) > [0]> then
                switch costume to (join (Kind) [ jump])
            else
                switch costume to (join (Kind) [ fall])
            end
        end
    end
end
set [Surf] to [-9999]
set [NX] to (X)
set [J] to [0]
repeat (Plat Count)
    change [J] by [1]
    if <<not <(NX) < (item (J) of [Plat X1])>> and <not <(NX) > (item (J) of [Plat X2])>>> then
        set [D] to ((item (J) of [Plat Y1]) + (((NX) - (item (J) of [Plat X1])) * (((item (J) of [Plat Y2]) - (item (J) of [Plat Y1])) / ((item (J) of [Plat X2]) - (item (J) of [Plat X1])))))
        if <<not <(D) > ((Y) + [1])>> and <(D) > (Surf)>> then
            set [Surf] to (D)
        end
    end
end
replace item (My Id) of [B SY] with (Surf)
if <(Face) = [1]> then
    point in direction [90]
else
    point in direction [-90]
end
if <(Inv Until) > (timer)> then
    set [ghost] effect to ([40] * ((round ((timer) * [10])) mod [2]))
else
    set [ghost] effect to [0]
end
set size to ([45] * (Zoom)) %
go to x: (((X) - (Cam X)) * (Zoom)) y: (((Y) - (Cam Y)) * (Zoom))
if <(My Id) = (My Slot)> then
    set [P1 Screen X] to (x position)
    set [P1 Screen Y] to (y position)
    set [P1 Screen Size] to (size)
end
```

> Everything one fighter does in one frame. It is a custom block with "run without screen refresh" so its loops over fighters and platforms finish in one frame.

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [brawl go]
if <(Is Clone) = [0]> then
    set [My Id] to [0]
    repeat [4]
        change [My Id] by [1]
        create clone of (myself)
    end
end
```

> Makes the four fighters. Clone 1 is you; 2, 3 and 4 are CPU fighters.

```
when I start as a clone
set [Is Clone] to [1]
set [Kind] to (item (My Id) of [B Kind])
if <(Kind) = [arthur]> then
    set [Speed] to [3.4]
    set [Punch] to [4]
    set [Kick] to [7]
    set [Weight] to [1]
end
if <(Kind) = [nova]> then
    set [Speed] to [4.4]
    set [Punch] to [3]
    set [Kick] to [6]
    set [Weight] to [0.85]
end
if <(Kind) = [rocko]> then
    set [Speed] to [2.7]
    set [Punch] to [5]
    set [Kick] to [9]
    set [Weight] to [1.3]
end
if <(Kind) = [rival]> then
    set [Speed] to [3.3]
    set [Punch] to [4]
    set [Kick] to [7]
    set [Weight] to [1]
end
if <(Kind) = [ivy]> then
    set [Speed] to [3.6]
    set [Punch] to [3]
    set [Kick] to [6]
    set [Weight] to [0.9]
end
if <(Kind) = [brute]> then
    set [Speed] to [2.6]
    set [Punch] to [5]
    set [Kick] to [9]
    set [Weight] to [1.35]
end
if <(Kind) = [quake]> then
    set [Speed] to [2.5]
    set [Punch] to [5]
    set [Kick] to [10]
    set [Weight] to [1.4]
end
if <(Kind) = [shadow]> then
    set [Speed] to [3.5]
    set [Punch] to [5]
    set [Kick] to [8]
    set [Weight] to [1.1]
end
if <(Kind) = [ninja]> then
    set [Speed] to [4.8]
    set [Punch] to [4]
    set [Kick] to [6]
    set [Weight] to [0.8]
end
if <(Difficulty) = [1]> then
    set [Think] to [0.05]
end
if <(Difficulty) = [2]> then
    set [Think] to [0.11]
end
if <(Difficulty) = [3]> then
    set [Think] to [0.2]
end
if <(Difficulty) = [4]> then
    set [Think] to [0.3]
end
set [X] to (((My Id) * [110]) - [275])
set [Y] to [220]
set [VX] to [0]
set [VY] to [0]
set [Face] to [1]
if <(X) > [0]> then
    set [Face] to [-1]
end
set [Smash] to [16]
set [Dash] to [9]
set [Stun] to [0]
set [Jumps] to [0]
if <(My Id) = [1]> then
    set [Charge] to [0]
end
if <(My Id) = [2]> then
    set [P2 Charge] to [0]
end
clear graphic effects
switch costume to (join (Kind) [ jump])
show
go to [front] layer
repeat until <(Brawl Live) = [0]>
    if <(item (My Id) of [B Alive]) = [1]> then
        (fighter frame)
    end
end
delete this clone
```

> One fighter, every frame: 1 take hits (damage % goes up, knockback grows with it), 2 controls or the CPU brain, 3 attacks, 4 gravity and landing on platforms and ramps, 5 flying off the screen loses a life, 6 draw it where the camera sees it.

```
when I receive [move left]
if <<(Is Clone) = [1]> and <(My Id) = [1]>> then
    set [Move Dir] to [-1]
    set [Move Until] to ((timer) + [0.16])
end
```

```
when I receive [move right]
if <<(Is Clone) = [1]> and <(My Id) = [1]>> then
    set [Move Dir] to [1]
    set [Move Until] to ((timer) + [0.16])
end
```

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Brawl Fireball

Costumes: flame
Sprite-only variables: J, Done, Power

```
when green flag clicked
hide
set [BF Power] to [0]
```

```
when I receive [brawl fire]
set [Power] to ((BF Power) - [1])
set [Done] to [0]
point in direction ([90] * (BF Dir))
show
go to [front] layer
repeat until <<<(Done) = [1]> or <(abs of (BF X)) > [560]>> or <(Brawl Live) = [0]>>
    (fireball frame)
end
hide
set [BF Power] to [0]
```

> Your fireball in BRAWL. Bigger charge = more damage and more knockback.

```
define (fireball frame)   [run without screen refresh]
change [BF X] by (([8] + ((Power) / [25])) * (BF Dir))
set size to (([30] + ((Power) * [0.7])) * (Zoom)) %
go to x: (((BF X) - (Cam X)) * (Zoom)) y: (((BF Y) - (Cam Y)) * (Zoom))
set [J] to [0]
repeat [4]
    change [J] by [1]
    if <<<<<(Done) = [0]> and <not <(J) = (BF Owner)>>> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (BF X))) < [24]>> and <(abs of (((item (J) of [B Y]) + [38]) - (BF Y))) < [44]>> then
        set [Done] to [1]
        replace item (J) of [B Hit] with ((item (J) of [B Hit]) + ([3] + (round ((Power) / [10]))))
        replace item (J) of [B KX] with ((BF Dir) * ([4] + (((Power) * ((item (J) of [B Dmg]) + [20])) / [500])))
        replace item (J) of [B KY] with ([4] + (((Power) * ((item (J) of [B Dmg]) + [20])) / [800]))
        if <(Power) > [99]> then
            broadcast [brawl ko]
        else
            broadcast [brawl hit]
        end
    end
end
```

```
when I receive [brawl clear]
hide
set [BF Power] to [0]
```

```
when I receive [show title]
hide
set [BF Power] to [0]
```

## Brawl Platform

Costumes: sky 1, sky 2, sky 3, sky 4, ramps 1, ramps 2, ramps 3, ramps 4, ramps 5, ramps 6, pagoda 1, pagoda 2, pagoda 3, pagoda 4, pagoda 5, pagoda 6, pirate 1, pirate 2, pirate 3, pirate 4, pirate 5, castle 1, castle 2, castle 3, castle 4, castle 5, castle 6, space 1, space 2, space 3, space 4, space 5, space 6, snow 1, snow 2, snow 3, snow 4, snow 5, candy 1, candy 2, candy 3, candy 4, candy 5, candy 6, factory 1, factory 2, factory 3, factory 4, factory 5, factory 6, towers 1, towers 2, towers 3, towers 4, towers 5, towers 6, towers 7, towers 8, jungle 1, jungle 2, jungle 3, jungle 4, jungle 5, jungle 5 s, jungle 5 l, jungle 5 l s, jungle 6, dino 1, dino 2, dino 2 s, dino 2 l, dino 2 l s, dino 3, dino 4, dino 5, dino 6, dino 6 s, dino 6 l, dino 6 l s, highway 1, highway 2, highway 3, highway 4, highway 5, highway 5 s, highway 5 l, highway 5 l s, highway 6, highway 7, pond 1, pond 2, pond 3, pond 3 s, pond 3 l, pond 3 l s, pond 4, pond 5, pond 6, pond 7
Sprite-only variables: Is Clone, My Id, Stage Key, Suf

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [brawl go]
if <(Is Clone) = [0]> then
    if <(Brawl Stage) = [1]> then
        set [Stage Key] to [sky]
    end
    if <(Brawl Stage) = [2]> then
        set [Stage Key] to [ramps]
    end
    if <(Brawl Stage) = [3]> then
        set [Stage Key] to [pagoda]
    end
    if <(Brawl Stage) = [4]> then
        set [Stage Key] to [pirate]
    end
    if <(Brawl Stage) = [5]> then
        set [Stage Key] to [castle]
    end
    if <(Brawl Stage) = [6]> then
        set [Stage Key] to [space]
    end
    if <(Brawl Stage) = [7]> then
        set [Stage Key] to [snow]
    end
    if <(Brawl Stage) = [8]> then
        set [Stage Key] to [candy]
    end
    if <(Brawl Stage) = [9]> then
        set [Stage Key] to [factory]
    end
    if <(Brawl Stage) = [10]> then
        set [Stage Key] to [towers]
    end
    if <(Brawl Stage) = [11]> then
        set [Stage Key] to [jungle]
    end
    if <(Brawl Stage) = [12]> then
        set [Stage Key] to [dino]
    end
    if <(Brawl Stage) = [13]> then
        set [Stage Key] to [highway]
    end
    if <(Brawl Stage) = [14]> then
        set [Stage Key] to [pond]
    end
    set [My Id] to [0]
    repeat (Plat Count)
        change [My Id] by [1]
        create clone of (myself)
    end
end
```

```
when I start as a clone
set [Is Clone] to [1]
switch costume to (join (Stage Key) (join [ ] (My Id)))
show
repeat until <(Brawl Live) = [0]>
    set size to ([100] * (Zoom)) %
    if <(item (My Id) of [Plat Art]) = [1]> then
        set [Suf] to []
        if <(item (My Id) of [Plat Push]) < [0]> then
            set [Suf] to [ l]
        end
        if <((floor of ((timer) * [5])) mod [2]) = [1]> then
            set [Suf] to (join (Suf) [ s])
        end
        switch costume to (join (Stage Key) (join [ ] (join (My Id) (Suf))))
    end
    go to x: (((item (My Id) of [Plat X1]) - (Cam X)) * (Zoom)) y: (((item (My Id) of [Plat Y1]) - (Cam Y)) * (Zoom))
end
delete this clone
```

> Each platform or ramp is a clone that redraws itself where the camera sees it.

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Brawl HUD

Costumes: arthur 0, arthur 1, arthur 2, arthur 3, nova 0, nova 1, nova 2, nova 3, rocko 0, rocko 1, rocko 2, rocko 3, rival 0, rival 1, rival 2, rival 3, ivy 0, ivy 1, ivy 2, ivy 3, brute 0, brute 1, brute 2, brute 3, quake 0, quake 1, quake 2, quake 3, shadow 0, shadow 1, shadow 2, shadow 3, ninja 0, ninja 1, ninja 2, ninja 3
Sprite-only variables: Is Clone, My Id

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [brawl go]
if <(Is Clone) = [0]> then
    set [My Id] to [0]
    change [My Id] by [1]
    go to x: [-184] y: [159]
    create clone of (myself)
    change [My Id] by [1]
    go to x: [-78] y: [159]
    create clone of (myself)
    change [My Id] by [1]
    go to x: [74] y: [159]
    create clone of (myself)
    change [My Id] by [1]
    go to x: [180] y: [159]
    create clone of (myself)
end
```

```
when I start as a clone
set [Is Clone] to [1]
show
repeat until <(Brawl Live) = [0]>
    if <(Page HUD) = [1]> then
        hide
    else
        show
    end
    switch costume to (join (item (My Id) of [B Kind]) (join [ ] (item (My Id) of [B Stock])))
    if <(item (My Id) of [B Alive]) = [1]> then
        set [ghost] effect to [0]
    else
        set [ghost] effect to [60]
    end
end
delete this clone
```

> Name and lives (dots) for each fighter. The big number next to it is their damage %.

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Brawl Shadow

Costumes: shadow
Sprite-only variables: Is Clone, My Id, H

```
when green flag clicked
hide
set [Is Clone] to [0]
```

```
when I receive [brawl go]
if <(Is Clone) = [0]> then
    set [My Id] to [0]
    repeat [4]
        change [My Id] by [1]
        create clone of (myself)
    end
end
```

```
when I start as a clone
set [Is Clone] to [1]
repeat until <(Brawl Live) = [0]>
    if <<(item (My Id) of [B Alive]) = [1]> and <(item (My Id) of [B SY]) > [-9000]>> then
        set [H] to ((item (My Id) of [B Y]) - (item (My Id) of [B SY]))
        set size to (((Zoom) * [52]) * ([1] - ((H) / [300]))) %
        set [ghost] effect to ([15] + ((H) / [3]))
        go to x: (((item (My Id) of [B X]) - (Cam X)) * (Zoom)) y: (((item (My Id) of [B SY]) - (Cam Y)) * (Zoom))
        show
    else
        hide
    end
end
delete this clone
```

> Each fighter's shadow sits on the platform under them, smaller and fainter the higher they jump.

```
when I receive [brawl clear]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [show title]
if <(Is Clone) = [1]> then
    delete this clone
end
```

```
when I receive [choose hero]
if <(Is Clone) = [1]> then
    delete this clone
end
```

## Cannonball

Costumes: ball, truck, truck l, coconut, fish, raptor, raptor 2, raptor l, raptor l 2
Sprite-only variables: Done, J, KD

```
define (cannon frame)   [run without screen refresh]
change [CB X] by (CB VX)
change [CB Y] by (CB VY)
change [CB VY] by ([-1] * (CB G))
set size to ((CB Size) * (Zoom)) %
if <(CB Kind) contains [raptor]?> then
    if <((floor of ((timer) * [8])) mod [2]) = [0]> then
        switch costume to (CB Kind)
    else
        switch costume to (join (CB Kind) [ 2])
    end
end
go to x: (((CB X) - (Cam X)) * (Zoom)) y: (((CB Y) - (Cam Y)) * (Zoom))
set [J] to [0]
repeat [4]
    change [J] by [1]
    if <<<<(Done) = [0]> and <(item (J) of [B Alive]) = [1]>> and <(abs of ((item (J) of [B X]) - (CB X))) < (CB W)>> and <(abs of (((item (J) of [B Y]) + [35]) - (CB Y))) < [40]>> then
        set [Done] to [1]
        if <(CB VX) = [0]> then
            if <(item (J) of [B X]) > (CB X)> then
                set [KD] to [1]
            else
                set [KD] to [-1]
            end
        else
            if <(CB VX) > [0]> then
                set [KD] to [1]
            else
                set [KD] to [-1]
            end
        end
        replace item (J) of [B Hit] with ((item (J) of [B Hit]) + [12])
        replace item (J) of [B KX] with ((KD) * ([7] + ((item (J) of [B Dmg]) / [9])))
        replace item (J) of [B KY] with ([7] + ((item (J) of [B Dmg]) / [11]))
        broadcast [brawl ko]
    end
end
```

```
when green flag clicked
hide
forever
    if <<(Brawl On) = [1]> and <<<<<(Stage Key) = [pirate]> or <(Stage Key) = [jungle]>> or <(Stage Key) = [dino]>> or <(Stage Key) = [highway]>> or <(Stage Key) = [pond]>>> then
        if <(Stage Key) = [pirate]> then
            wait (pick random [6] to [10]) seconds
            if <(pick random [1] to [2]) = [1]> then
                set [CB Dir] to [1]
            else
                set [CB Dir] to [-1]
            end
            set [CB Kind] to [ball]
            set [CB Size] to [60]
            set [CB W] to [24]
            set [CB X] to ((CB Dir) * [-520])
            set [CB Y] to (pick random [-85] to [40])
            set [CB VX] to ([10] * (CB Dir))
            set [CB VY] to [0]
            set [CB G] to [0]
            set [Pop Text] to [CANNON!]
            broadcast [cannon fire]
        end
        if <(Stage Key) = [jungle]> then
            wait (pick random [3] to [6]) seconds
            set [CB Kind] to [coconut]
            set [CB Size] to [70]
            set [CB W] to [22]
            set [CB X] to (pick random [-270] to [270])
            set [CB Y] to [280]
            set [CB VX] to [0]
            set [CB VY] to [-2]
            set [CB G] to [0.6]
            set [Pop Text] to [COCONUT!]
            broadcast [whirl sfx]
        end
        if <(Stage Key) = [dino]> then
            wait (pick random [5] to [9]) seconds
            if <(pick random [1] to [2]) = [1]> then
                set [CB Dir] to [1]
            else
                set [CB Dir] to [-1]
            end
            set [CB Size] to [100]
            set [CB W] to [36]
            if <(CB Dir) = [1]> then
                set [CB Kind] to [raptor]
            else
                set [CB Kind] to [raptor l]
            end
            set [CB X] to ((CB Dir) * [-540])
            set [CB Y] to [-92]
            set [CB VX] to ([11] * (CB Dir))
            set [CB VY] to [0]
            set [CB G] to [0]
            set [Pop Text] to [RAPTOR! JUMP!]
            broadcast [screech]
        end
        if <(Stage Key) = [highway]> then
            wait (pick random [5] to [9]) seconds
            if <(pick random [1] to [2]) = [1]> then
                set [CB Dir] to [1]
            else
                set [CB Dir] to [-1]
            end
            set [CB Size] to [100]
            set [CB W] to [62]
            if <(CB Dir) = [1]> then
                set [CB Kind] to [truck]
            else
                set [CB Kind] to [truck l]
            end
            set [CB X] to ((CB Dir) * [-540])
            set [CB Y] to [-78]
            set [CB VX] to ([9] * (CB Dir))
            set [CB VY] to [0]
            set [CB G] to [0]
            set [Pop Text] to [TRUCK! JUMP!]
            broadcast [honk]
        end
        if <(Stage Key) = [pond]> then
            wait (pick random [4] to [7]) seconds
            set [CB Kind] to [fish]
            set [CB Size] to [80]
            set [CB W] to [24]
            set [CB X] to (pick random [-100] to [100])
            set [CB Y] to [-210]
            set [CB VX] to [0]
            set [CB VY] to [16]
            set [CB G] to [0.55]
            set [Pop Text] to [SPLASH!]
            broadcast [boing]
        end
        if <<(Brawl On) = [1]> and <<<<<(Stage Key) = [pirate]> or <(Stage Key) = [jungle]>> or <(Stage Key) = [dino]>> or <(Stage Key) = [highway]>> or <(Stage Key) = [pond]>>> then
            set [Done] to [0]
            switch costume to (CB Kind)
            broadcast [popup]
            show
            go to [front] layer
            repeat until <<<<(Done) = [1]> or <(abs of (CB X)) > [560]>> or <(CB Y) < [-320]>> or <(Brawl Live) = [0]>>
                (cannon frame)
            end
            hide
        end
    else
        wait [0.3] seconds
    end
end
```

> Stage hazards: cannonballs on the PIRATE SHIP, trucks on the HIGHWAY, raptors in DINO VALLEY, coconuts in the JUNGLE and jumping fish at the FISHING POND. Jump out of the way!

```
when I receive [brawl clear]
hide
```

```
when I receive [show title]
hide
```

## Stage Button

Costumes: stage 0, stage 1, stage 2, stage 3, stage 4, stage 5, stage 6, stage 7, stage 8, stage 9, stage 10, stage 11, stage 12, stage 13, stage 14

```
when green flag clicked
hide
```

```
when I receive [choose hero]
if <(Mode) = [brawl]> then
    switch costume to (join [stage ] (Stage Pick))
    go to x: [40] y: [-162]
    show
    go to [front] layer
else
    hide
end
```

```
when I receive [hero picked]
hide
```

```
when I receive [show title]
hide
```

```
when this sprite clicked
change [Stage Pick] by [1]
if <(Stage Pick) > [14]> then
    set [Stage Pick] to [0]
end
switch costume to (join [stage ] (Stage Pick))
broadcast [swing sfx]
```

> Tap to choose the BRAWL stage, or RANDOM.

## P1 Marker

Costumes: arrow

```
when green flag clicked
hide
forever
    if <<(Brawl Live) = [1]> and <(item [1] of [B Alive]) = [1]>> then
        go to x: (P1 Screen X) y: ((P1 Screen Y) + ((P1 Screen Size) * [2.05]))
        show
        go to [front] layer
    else
        hide
    end
end
```

> The yellow P1 arrow shows which fighter is you.

