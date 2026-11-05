# Block listing for Arthur's Arena: Legends

Made by `tools/build_legends_sb3.py` from the same blocks that are inside
`projects/arthurs-arena-legends.sb3`. Use it to find a script in the editor.

## Stage

Costumes: Title, Select, Yard, Woods, Pass, Factory, Volcano, Castle, Arcade, Ending
Sounds: hit, big hit, hurt, jump, swing, pickup, super, perfect, ko, charge, charged, fireball, big fireball, boom, spikes, clang, win

```
when green flag clicked
set [State] to [title]
set [Fight On] to [0]
set [Score] to [0]
set [Weapon] to [none]
hide variable [Score]
hide variable [Wave]
hide variable [Best]
broadcast [show title]
```

> Green flag. Best and Crown are kept, so a saved project remembers them.

```
when I receive [show title]
set [State] to [title]
set [Fight On] to [0]
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
set [Hero HP] to (Hero Max)
set [Score] to [0]
set [Super] to [0]
if <(Mode) = [story]> then
    set [Chapter] to [1]
    broadcast [story scene]
else
    set [Wave] to [1]
    broadcast [start fight]
end
```

> Each fighter has different health, speed, punch, kick and super.

```
when I receive [load enemy]
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
        switch backdrop to (Volcano)
    end
    if <(Chapter) = [6]> then
        switch backdrop to (Castle)
    end
    set [Pace] to [1]
else
    if <((Wave) mod [6]) = [0]> then
        set [Enemy Type] to [6]
    else
        set [Enemy Type] to ((((Wave) - [1]) mod [6]) + [1])
    end
    switch backdrop to (Arcade)
    set [Pace] to ([8] / ([7] + (Wave)))
end
if <(Enemy Type) = [1]> then
    set [Enemy Name] to [rival]
    set [Enemy Title] to [RIVAL]
    set [Enemy Max] to [24]
    set [Enemy Power] to [6]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [10]
    set [Enemy Size] to [78]
end
if <(Enemy Type) = [2]> then
    set [Enemy Name] to [ivy]
    set [Enemy Title] to [IVY]
    set [Enemy Max] to [32]
    set [Enemy Power] to [8]
    set [Enemy Speed] to [1]
    set [Enemy Body] to [10]
    set [Enemy Size] to [82]
end
if <(Enemy Type) = [3]> then
    set [Enemy Name] to [brute]
    set [Enemy Title] to [BRUTE]
    set [Enemy Max] to [44]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [1]
    set [Enemy Body] to [22]
    set [Enemy Size] to [110]
end
if <(Enemy Type) = [4]> then
    set [Enemy Name] to [spikebot]
    set [Enemy Title] to [SPIKE BOT]
    set [Enemy Max] to [40]
    set [Enemy Power] to [10]
    set [Enemy Speed] to [3]
    set [Enemy Body] to [22]
    set [Enemy Size] to [100]
end
if <(Enemy Type) = [5]> then
    set [Enemy Name] to [quake]
    set [Enemy Title] to [QUAKE]
    set [Enemy Max] to [50]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [26]
    set [Enemy Size] to [120]
end
if <(Enemy Type) = [6]> then
    set [Enemy Name] to [shadow]
    set [Enemy Title] to [SHADOW KING]
    set [Enemy Max] to [90]
    set [Enemy Power] to [12]
    set [Enemy Speed] to [4]
    set [Enemy Body] to [26]
    set [Enemy Size] to [125]
end
if <(Mode) = [arcade]> then
    change [Enemy Max] by ([8] * ((Wave) - [1]))
    change [Enemy Power] by (floor of (((Wave) - [1]) / [2]))
end
set [Enemy HP] to (Enemy Max)
set [Enemy Phase] to [1]
```

> Story: the chapter picks the enemy. Arcade: waves 1-5 cycle, every 6th wave is the Shadow King, and each wave is tougher and faster.

```
when I receive [start fight]
set [Fight On] to [0]
set [State] to [fight]
broadcast [load enemy] and wait
if <(Mode) = [story]> then
    set [Hero HP] to (Hero Max)
else
    show variable [Wave]
end
show variable [Score]
hide variable [Best]
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
set [Banner] to [ready]
broadcast [banner]
wait [1.1] seconds
set [Banner] to [fight]
broadcast [banner]
wait [0.3] seconds
set [Want Punch] to [0]
set [Want Kick] to [0]
set [Want Jump] to [0]
set [Want Dodge] to [0]
set [Want Super] to [0]
set [Fight On] to [1]
broadcast [fight on]
```

> READY... FIGHT! Taps before FIGHT! are thrown away.

```
when I receive [hero hits]
if <<(Fight On) = [1]> and <(timer) > (Enemy Stun Until)>> then
    set [Enemy Stun Until] to ((timer) + [0.15])
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
        change [Super] by [6]
        if <not <(Super) < [100]>> then
            set [Super] to [100]
            broadcast [super ready]
        end
    end
    broadcast [enemy hurt]
    if <<<<(Enemy Type) = [6]> and <(Enemy Phase) = [1]>> and <(Enemy HP) > [0]>> and <(Enemy HP) < ((Enemy Max) / [2])>> then
        set [Enemy Phase] to [2]
        set [Pace] to ((Pace) * [0.7])
        broadcast [king angry]
    end
    if <(Enemy HP) < [1]> then
        set [Enemy HP] to [0]
        set [Fight On] to [0]
        broadcast [enemy down]
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
start sound (ko)
set [Banner] to [ko]
broadcast [banner]
wait [1.4] seconds
if <(Mode) = [story]> then
    if <(Chapter) = [6]> then
        change [Score] by ([1000] + ((Hero HP) * [5]))
        if <(Score) > (Best)> then
            set [Best] to (Score)
        end
        broadcast [ending]
    else
        start sound (win)
        set [Banner] to [clear]
        broadcast [banner]
        change [Score] by ([500] + ((Hero HP) * [5]))
        wait [2] seconds
        change [Chapter] by [1]
        broadcast [story scene]
    end
else
    start sound (win)
    set [Banner] to [wave clear]
    broadcast [banner]
    change [Score] by ([200] + ((Wave) * [50]))
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
    change [Wave] by [1]
    broadcast [start fight]
end
```

> Story: next chapter, or the ending after the Shadow King. Arcade: heal a little and start the next, harder wave.

```
when I receive [hero down]
start sound (ko)
set [State] to [over]
if <(Score) > (Best)> then
    set [Best] to (Score)
end
wait [0.6] seconds
set [Banner] to [ko]
broadcast [banner]
wait [1.4] seconds
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

## Ground Shake

Costumes: shadow

```
when green flag clicked
go to x: [0] y: [-80]
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

Costumes: arthur idle, arthur punch, arthur kick, arthur jump, arthur hurt, arthur win, arthur dodge, arthur special, arthur down, arthur charge, nova idle, nova punch, nova kick, nova jump, nova hurt, nova win, nova dodge, nova special, nova down, nova charge, rocko idle, rocko punch, rocko kick, rocko jump, rocko hurt, rocko win, rocko dodge, rocko special, rocko down, rocko charge
Sprite-only variables: Line Until

```
when green flag clicked
set rotation style [left-right]
point in direction [90]
forever
    set [Hero X] to (x position)
    set [Hero Y] to (y position)
    if <<(Fight On) = [1]> and <(Hero Lock) = [0]>> then
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
```

> Hero X and Hero Y are read by everyone else. In a fight, Hero always turns to face the enemy.

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
                switch costume to (join (Hero Name) [ special])
                wait [0.35] seconds
                if <(Hero) = [1]> then
                    glide [0.18] secs to x: ((Enemy X) - ([45] * (Facing))) y: [-75]
                    set [Hit Power] to (Special Power)
                    broadcast [hero hits]
                    broadcast [shake]
                    wait [0.4] seconds
                end
                if <(Hero) = [2]> then
                    repeat [3]
                        glide [0.1] secs to x: ((Enemy X) - ([40] * (Facing))) y: [-75]
                        switch costume to (join (Hero Name) [ kick])
                        set [Hit Power] to (round ((Special Power) / [3]))
                        broadcast [hero hits]
                        wait [0.2] seconds
                        switch costume to (join (Hero Name) [ special])
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
                    switch costume to (join (Hero Name) [ jump])
                    repeat [6]
                        change y by [18]
                    end
                    glide [0.15] secs to x: ((Enemy X) - ([40] * (Facing))) y: [-75]
                    switch costume to (join (Hero Name) [ special])
                    set [Hit Power] to (Special Power)
                    broadcast [hero hits]
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
                switch costume to (join (Hero Name) [ idle])
                set [Hero Safe] to [0]
                set [Hero Lock] to [0]
            end
        end
        if <<(Want Punch) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Punch] to [0]
            switch costume to (join (Hero Name) [ punch])
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
            end
            wait [0.16] seconds
            if <<<not <(Weapon) = [none]>> and <(Weapon Uses) < [1]>> and <(Boomerang Out) = [0]>> then
                broadcast [weapon break]
            end
            if <(Hero Air) = [1]> then
                switch costume to (join (Hero Name) [ jump])
            else
                switch costume to (join (Hero Name) [ idle])
            end
        end
        if <<(Want Kick) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Kick] to [0]
            switch costume to (join (Hero Name) [ kick])
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
                switch costume to (join (Hero Name) [ jump])
            else
                switch costume to (join (Hero Name) [ idle])
            end
        end
        if <<(Want Dodge) = [1]> and <(Hero Lock) = [0]>> then
            set [Want Dodge] to [0]
            if <(Hero Air) = [0]> then
                set [Hero Lock] to [1]
                set [Hero Safe] to [1]
                switch costume to (join (Hero Name) [ dodge])
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
                switch costume to (join (Hero Name) [ idle])
                set [Hero Lock] to [0]
                wait [0.12] seconds
            end
        end
    else
        set [Want Punch] to [0]
        set [Want Kick] to [0]
        set [Want Dodge] to [0]
        set [Want Super] to [0]
    end
end
```

> The action loop. Buttons only set Want Punch, Want Kick and so on; this loop does one move at a time. A tap during a move waits its turn (a short input buffer, like big fighting games).

```
when green flag clicked
forever
    if <(Want Jump) = [1]> then
        set [Want Jump] to [0]
        if <<<(Fight On) = [1]> and <(Hero Air) = [0]>> and <(Hero Lock) = [0]>> then
            set [Hero Air] to [1]
            switch costume to (join (Hero Name) [ jump])
            broadcast [jump sfx]
            repeat [8]
                change y by [11]
            end
            wait [0.1] seconds
            repeat [8]
                change y by [-11]
            end
            set y to [-75]
            set [Hero Air] to [0]
            if <(Hero Lock) = [0]> then
                switch costume to (join (Hero Name) [ idle])
            end
        end
    end
end
```

> The jump loop runs beside the action loop, so you can punch and kick in the air.

```
when green flag clicked
forever
    if <<<<(Fight On) = [1]> and <(Fireball Out) = [0]>> and <(Hero Lock) = [0]>> and <<(Fire Held) = [1]> or <key (f) pressed?>>> then
        set [Charge] to [1]
        broadcast [charge start]
        switch costume to (join (Hero Name) [ charge])
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
            switch costume to (join (Hero Name) [ punch])
            wait [0.15] seconds
            if <(Hero Air) = [1]> then
                switch costume to (join (Hero Name) [ jump])
            else
                switch costume to (join (Hero Name) [ idle])
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
end
```

```
when I receive [hero hurt]
if <(Hero Lock) = [0]> then
    switch costume to (join (Hero Name) [ hurt])
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
        switch costume to (join (Hero Name) [ jump])
    else
        switch costume to (join (Hero Name) [ idle])
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
go to x: [-195] y: [-75]
set size to [90] %
go to [front] layer
say [I'm Arthur!] for [2] seconds
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
when I receive [fighters ready]
show
clear graphic effects
point in direction [90]
set [Facing] to [1]
switch costume to (join (Hero Name) [ idle])
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
switch costume to (join (Hero Name) [ idle])
set size to [75] %
go to x: [-150] y: [-75]
```

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
switch costume to (join (Hero Name) [ win])
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
switch costume to (join (Hero Name) [ down])
```

```
when I receive [ending]
point in direction [90]
go to x: [-170] y: [-75]
switch costume to (join (Hero Name) [ win])
```

## Enemy

Costumes: rival idle, rival windup, rival attack, rival hurt, rival down, ivy idle, ivy windup, ivy attack, ivy hurt, ivy down, brute idle, brute windup, brute attack, brute hurt, brute down, spikebot idle, spikebot windup, spikebot attack, spikebot hurt, spikebot down, quake idle, quake windup, quake attack, quake hurt, quake down, shadow idle, shadow windup, shadow attack, shadow hurt, shadow down, shadow angry
Sprite-only variables: Pick, Line Until

```
when green flag clicked
set rotation style [left-right]
hide
forever
    set [Enemy X] to (x position)
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
    if <(timer) < (Enemy Stun Until)> then
        switch costume to (join (Enemy Name) [ hurt])
        wait [0.05] seconds
    else
        if <(Enemy Type) = [1]> then
            if <<(abs of ((Hero X) - (x position))) < ([38] + (Enemy Body))> and <((Hero Y) - [-75]) < [60]>> then
                switch costume to (join (Enemy Name) [ attack])
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
                say [Low!] for ([0.45] * (Pace)) seconds
                set [Shot Y] to [-57]
                set [Shot Dir] to (Enemy Facing)
                switch costume to (join (Enemy Name) [ attack])
                broadcast [enemy shot] and wait
                switch costume to (join (Enemy Name) [ idle])
            else
                switch costume to (join (Enemy Name) [ windup])
                say [High!] for ([0.45] * (Pace)) seconds
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
            say [Ready?] for ([0.75] * (Pace)) seconds
            set [Pick] to (Hero X)
            switch costume to (join (Enemy Name) [ attack])
            broadcast [swing sfx]
            glide ([0.4] * (Pace)) secs to x: (Pick) y: [-75]
            if <<(abs of ((Hero X) - (x position))) < ([34] + (Enemy Body))> and <((Hero Y) - [-75]) < [50]>> then
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
            say [SPIKES OUT!] for ([0.55] * (Pace)) seconds
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
                    set [Hurt Power] to (Enemy Power)
                    broadcast [enemy hits hero]
                    broadcast [shake]
                    set [Pick] to [99]
                end
            end
            set [Spikes] to [0]
            switch costume to (join (Enemy Name) [ idle])
            say [Cooling down...] for ([1.7] * (Pace)) seconds
        end
        if <(Enemy Type) = [5]> then
            switch costume to (join (Enemy Name) [ windup])
            say [STOMP!] for ([0.6] * (Pace)) seconds
            switch costume to (join (Enemy Name) [ attack])
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
        if <(Enemy Type) = [6]> then
            set [Pick] to (pick random [1] to [4])
            if <(Pick) = [1]> then
                switch costume to (join (Enemy Name) [ windup])
                say [Ready?] for ([0.75] * (Pace)) seconds
                set [Pick] to (Hero X)
                switch costume to (join (Enemy Name) [ attack])
                broadcast [swing sfx]
                glide ([0.4] * (Pace)) secs to x: (Pick) y: [-75]
                if <<(abs of ((Hero X) - (x position))) < ([34] + (Enemy Body))> and <((Hero Y) - [-75]) < [50]>> then
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
                say [Low!] for ([0.45] * (Pace)) seconds
                set [Shot Y] to [-57]
                set [Shot Dir] to (Enemy Facing)
                switch costume to (join (Enemy Name) [ attack])
                broadcast [enemy shot] and wait
                switch costume to (join (Enemy Name) [ idle])
                if <(Enemy Phase) = [2]> then
                    switch costume to (join (Enemy Name) [ windup])
                    say [High!] for ([0.45] * (Pace)) seconds
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
                say [STOMP!] for ([0.6] * (Pace)) seconds
                switch costume to (join (Enemy Name) [ attack])
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
        if <(Fight On) = [1]> then
            switch costume to (join (Enemy Name) [ idle])
        end
    end
end
```

> One brain for every enemy. 1 Rival walks in and punches. 2 Ivy throws low and high shots. 3 Brute says Ready? then charges where you were. 4 Spike Bot rolls at you with spikes out, then cools down. 5 Quake stomps a ground wave. 6 the Shadow King mixes them all.

```
when I receive [enemy hurt]
switch costume to (join (Enemy Name) [ hurt])
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
switch costume to (shadow angry)
say [You're strong... but I'm STRONGER!] for [1.6] seconds
switch costume to (shadow idle)
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
say []
```

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
say (Line)
set [Line Until] to ((timer) + (Line Secs))
wait until <<(timer) > (Line Until)> or <(Skip) = [1]>>
say []
```

```
when I receive [enemy down]
say []
set [Spikes] to [0]
wait [0.2] seconds
set y to [-75]
switch costume to (join (Enemy Name) [ down])
wait [1.3] seconds
repeat [10]
    change [ghost] effect by [10]
    wait [0.03] seconds
end
if <not <<(Mode) = [story]> and <(Chapter) = [6]>>> then
    hide
end
set [ghost] effect to [0]
```

```
when I receive [hero down]
wait [0.3] seconds
switch costume to (join (Enemy Name) [ idle])
say [Ha! Try again!] for [2] seconds
```

```
when I receive [ending]
show
go to x: [170] y: [-75]
point in direction [-90]
switch costume to (shadow down)
```

## Enemy Shot

Costumes: ball
Sprite-only variables: Hit

```
when green flag clicked
hide
```

```
when I receive [enemy shot]
go to x: ((Enemy X) + ([30] * (Shot Dir))) y: (Shot Y)
set [Hit] to [0]
show
go to [front] layer
set [Shot Cancel] to [0]
set [Shot Live] to [1]
repeat until <<<<(abs of (x position)) > [235]> or <(Hit) = [1]>> or <(Fight On) = [0]>> or <(Shot Cancel) = [1]>>
    change x by ([12] * (Shot Dir))
    set [Shot X] to (x position)
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

Costumes: sword, hammer, boomerang
Sprite-only variables: Swing Until

```
when green flag clicked
hide
forever
    if <<<(State) = [fight]> and <not <(Weapon) = [none]>>> and <(Boomerang Out) = [0]>> then
        switch costume to (Weapon)
        go to x: ((Hero X) + ([18] * (Facing))) y: ((Hero Y) + [48])
        if <(timer) < (Swing Until)> then
            point in direction ([90] + ([100] * (Facing)))
        else
            point in direction ([90] + ([-25] * (Facing)))
        end
        show
        go to [front] layer
    else
        hide
    end
end
```

> Follows Hero's hand while a weapon is held.

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

Costumes: sword, hammer, boomerang
Sprite-only variables: Kind, Life, Got

```
when green flag clicked
hide
forever
    if <<(Fight On) = [1]> and <(Weapon) = [none]>> then
        wait (pick random [3] to [7]) seconds
        if <<(Fight On) = [1]> and <(Weapon) = [none]>> then
            set [Kind] to (pick random [1] to [3])
            if <(Kind) = [1]> then
                set [Kind] to [sword]
            end
            if <(Kind) = [2]> then
                set [Kind] to [hammer]
            end
            if <(Kind) = [3]> then
                set [Kind] to [boomerang]
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

> Every 3 to 7 seconds a weapon falls from the sky. Walk over it to pick it up. Sword: +4 power, longer reach, 10 swings. Hammer: +9 power and a shake, 5 swings. Boomerang: PUNCH throws it, 6 throws.

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

## Charge Glow

Costumes: glow

```
when green flag clicked
hide
forever
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

## Crown

Costumes: crown

```
when green flag clicked
hide
forever
    if <<(Crown) = [1]> and <<(State) = [fight]> or <(State) = [over]>>> then
        go to x: (Hero X) y: ((Hero Y) + [104])
        show
        go to [front] layer
    else
        if <not <(State) = [ending]>> then
            hide
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
    if <(State) = [fight]> then
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
    if <(State) = [fight]> then
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
    if <(State) = [fight]> then
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
    if <(State) = [fight]> then
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
    if <(State) = [fight]> then
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
    if <(State) = [fight]> then
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
    if <(State) = [fight]> then
        switch costume to (Hero Name)
        go to x: [-228] y: [174]
        show
    else
        hide
    end
end
```

## Enemy Tag

Costumes: rival, ivy, brute, spikebot, quake, shadow

```
when green flag clicked
hide
forever
    if <(State) = [fight]> then
        switch costume to (Enemy Name)
        go to x: [228] y: [174]
        show
    else
        hide
    end
end
```

## Popup

Costumes: dot
Sprite-only variables: My Text

```
when green flag clicked
hide
```

```
when I receive [popup]
set [My Text] to (Pop Text)
go to x: ((Hero X) + [10]) y: ((Hero Y) + [125])
create clone of (myself)
```

> Copies Pop Text into a clone so two pop-ups in a row both show.

```
when I start as a clone
show
say (My Text)
repeat [14]
    change y by [2]
    wait [0.06] seconds
end
delete this clone
```

```
when I receive [super ready]
set [My Text] to [SUPER READY! Tap SUPER]
go to x: [-150] y: [120]
create clone of (myself)
```

## Hit Spark

Costumes: spark

```
when green flag clicked
hide
```

```
when I receive [enemy hurt]
go to x: (Enemy X) y: ([-75] + [60])
create clone of (myself)
```

```
when I receive [hero hurt]
go to x: (Hero X) y: ([-75] + [50])
create clone of (myself)
```

```
when I start as a clone
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

Costumes: ready, fight, ko, clear, wave clear

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

Costumes: prologue, chapter 1, chapter 2, chapter 3, chapter 4, chapter 5, chapter 6, game over, arcade over, the end, angry
Sprite-only variables: Until

```
when green flag clicked
hide
```

```
when I receive [story scene]
set [State] to [story]
set [Skip] to [0]
hide
broadcast [load enemy] and wait
broadcast [skip on]
if <(Chapter) = [1]> then
    switch costume to (prologue)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [3.2])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    switch costume to (chapter 1)
    set size to [100] %
    go to x: [0] y: [30]
    show
    go to [front] layer
    set [Until] to ((timer) + [2.6])
    wait until <<(timer) > (Until)> or <(Skip) = [1]>>
    hide
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [Nobody gets past the gate!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <(Skip) = [0]> then
        set [Line] to [Then let's fight!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
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
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [My vines see everything.]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <(Skip) = [0]> then
        set [Line] to [Then watch me jump!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
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
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [BRUTE... SMASH!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <(Skip) = [0]> then
        set [Line] to [Not if I move first!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
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
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [BZZT! SPIKES... ONLINE!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <(Skip) = [0]> then
        set [Line] to [Then I'll use FIREBALLS!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
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
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [Feel the ground shake!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <(Skip) = [0]> then
        set [Line] to [I'll jump right over it!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
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
    broadcast [scene setup] and wait
    if <(Skip) = [0]> then
        set [Line] to [The Golden Crown is MINE!]
        set [Line Secs] to [2.2]
        broadcast [enemy line] and wait
    end
    if <(Skip) = [0]> then
        set [Line] to [Not for long!]
        set [Line Secs] to [2.2]
        broadcast [hero line] and wait
    end
end
broadcast [skip off]
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
switch costume to (angry)
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
go to x: [-206] y: [-152]
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
go to x: [-147] y: [-152]
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
go to x: [-88] y: [-152]
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
go to x: [-29] y: [-152]
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
```

> Sets Want Punch. Hero's loop does the move.

```
when I receive [fight on]
go to x: [30] y: [-152]
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
```

> Sets Want Kick. Hero's loop does the move.

```
when I receive [fight on]
go to x: [89] y: [-152]
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
go to x: [148] y: [-152]
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
go to x: [207] y: [-152]
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
when this sprite clicked
hide
if <(Mode) = [arcade]> then
    set [Wave] to [1]
    set [Score] to [0]
    set [Hero HP] to (Hero Max)
end
set [Super] to [0]
broadcast [start fight]
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
go to x: [0] y: [165]
show
go to [front] layer
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

