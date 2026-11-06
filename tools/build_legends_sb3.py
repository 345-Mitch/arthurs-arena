#!/usr/bin/env python3
"""Build "Arthur's Arena: Legends" as a Scratch 3 project.

Story mode, Arcade mode, three playable fighters, weapon drops, combos,
a super meter, perfect dodges, and a final boss.

The guide for Arthur is LEGENDS.md. Run:

    python3 tools/build_legends_sb3.py

It writes projects/arthurs-arena-legends.sb3 and projects/LEGENDS_BLOCKS.md.
tools/test_legends.js plays the built project in Scratch's own engine.

Two rules this file follows on purpose:

* Buttons never start long scripts with a broadcast. In Scratch a broadcast
  restarts a script that is already running, which can leave "busy" stuck
  on. Buttons set a "Want ..." variable instead, and Hero's loops act on it.
* Hits use distance, not "touching". It behaves the same on every device
  and it can be tested without a screen.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import random
import struct
import sys
import wave
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SB3_PATH = ROOT / "projects" / "arthurs-arena-legends.sb3"
LISTING_PATH = ROOT / "projects" / "LEGENDS_BLOCKS.md"

GROUND = -75  # y of everyone's feet
VERSION = "3.7"
APPLE_HEAL = 25

# ---------------------------------------------------------------- tuning --
HEROES = [
    # key, display, color, hp, step, punch, kick, special power, special name, trait
    dict(key="arthur", name="ARTHUR", color="#2563eb", hp=100, step=22, punch=5, kick=8,
         special=18, special_name="HERO SLASH", trait="All-rounder", gear="headband",
         line="I'm Arthur!", stats=(3, 3, 3)),
    dict(key="nova", name="NOVA", color="#c026d3", hp=80, step=32, punch=4, kick=7,
         special=15, special_name="STAR DASH", trait="Super fast", gear="star",
         line="Too slow!", stats=(2, 5, 2)),
    dict(key="rocko", name="ROCKO", color="#15803d", hp=130, step=15, punch=7, kick=10,
         special=22, special_name="ROCK SLAM", trait="Super strong", gear="spikes",
         line="Rock solid!", stats=(5, 1, 5)),
]

ENEMIES = [
    # type number, key, tag, color, size, hp, power, speed, body
    dict(n=1, key="rival", tag="RIVAL", color="#64748b", size=78, hp=24, pow=6, speed=4, body=10, gear="none"),
    dict(n=2, key="ivy", tag="IVY", color="#7c3aed", size=82, hp=32, pow=8, speed=1, body=10, gear="leaf"),
    dict(n=3, key="brute", tag="BRUTE", color="#dc2626", size=110, hp=44, pow=12, speed=1, body=22, gear="horns"),
    dict(n=4, key="spikebot", tag="SPIKE BOT", color="#64748b", size=100, hp=40, pow=10, speed=3, body=22, gear="robot"),
    dict(n=5, key="megaspike", tag="MEGA SPIKE", color="#7f1d1d", size=125, hp=80, pow=12, speed=4, body=34, gear="robot"),
    dict(n=6, key="ninja", tag="NINJA", color="#1f2937", size=80, hp=40, pow=9, speed=5, body=12, gear="ninja"),
    dict(n=7, key="kage", tag="MASTER KAGE", color="#111827", size=100, hp=85, pow=11, speed=6, body=18, gear="ninja boss"),
    dict(n=8, key="quake", tag="QUAKE", color="#ea580c", size=120, hp=50, pow=12, speed=4, body=26, gear="spikes"),
    dict(n=9, key="shadow", tag="SHADOW KING", color="#1e1b4b", size=125, hp=90, pow=12, speed=4, body=26, gear="crown"),
]
SPIKEBOT = 4
MEGA = 5   # MEGA SPIKE, the spiked robot boss
NINJA = 6
KAGE = 7   # MASTER KAGE, the ninja boss
QUAKE = 8
KING = 9   # the Shadow King's Enemy Type
BOSSES = (MEGA, KAGE, KING)
NINJA_KINDS = ("ninja", "kage")

CHAPTERS = [
    # backdrop, chapter card lines, dialogue lines (speaker, text)
    dict(backdrop="Yard", title="CHAPTER 1", lines=["The Training Yard", "Beat the Rival to get", "through the gate."],
         talk=[("enemy", "Nobody gets past the gate!"), ("hero", "Then let's fight!")]),
    dict(backdrop="Woods", title="CHAPTER 2", lines=["Ivy's Woods", "Low shot? JUMP!", "High shot? Stay down."],
         talk=[("enemy", "My vines see everything."), ("hero", "Then watch me jump!")]),
    dict(backdrop="Pass", title="CHAPTER 3", lines=["The Rocky Pass", "Brute says Ready?", "then charges. Move!"],
         talk=[("enemy", "BRUTE... SMASH!"), ("hero", "Not if I move first!")]),
    dict(backdrop="Factory", title="CHAPTER 4", lines=["The Robot Factory", "Spikes out? Don't punch!", "Hold FIRE for a fireball."],
         talk=[("enemy", "BZZT! SPIKES... ONLINE!"), ("hero", "Then I'll use FIREBALLS!")]),
    dict(backdrop="Fortress", title="BOSS: CHAPTER 5", lines=["The Spike Fortress", "MEGA SPIKE is spiky ALL over.", "Hit it while it cools down!"],
         talk=[("enemy", "I AM MEGA SPIKE! FEEL MY SPIKES!"), ("hero", "Then I'll fight smart!")]),
    dict(backdrop="Bamboo", title="CHAPTER 6", lines=["The Bamboo Forest", "Ninjas jump out of the trees!", "Fight them all, use POWER!"],
         talk=[("enemy", "You will never see us coming..."), ("hero", "I can see you right now!")]),
    dict(backdrop="Dojo", title="BOSS: CHAPTER 7", lines=["The Ninja Dojo", "MASTER KAGE vanishes in smoke", "and his ninjas attack!"],
         talk=[("enemy", "I am MASTER KAGE. My ninjas are everywhere!"), ("hero", "Then I'll beat every one of them!")]),
    dict(backdrop="Volcano", title="CHAPTER 8", lines=["The Volcano Gate", "Quake stomps the ground.", "Jump over the wave!"],
         talk=[("enemy", "Feel the ground shake!"), ("hero", "I'll jump right over it!")]),
    dict(backdrop="Castle", title="FINAL CHAPTER", lines=["Shadow Castle", "He uses every trick.", "Use your SUPER!"],
         talk=[("enemy", "The Golden Crown is MINE!"), ("hero", "Not for long!")]),
]

WEAPONS = [
    # random number, key, bonus, reach, uses
    dict(n=1, key="sword", bonus=4, reach=28, uses=10, shout="SWORD!"),
    dict(n=2, key="hammer", bonus=9, reach=12, uses=5, shout="HAMMER!"),
    dict(n=3, key="boomerang", bonus=0, reach=0, uses=6, shout="BOOMERANG!"),
    dict(n=4, key="spear", bonus=5, reach=48, uses=8, shout="SPEAR!"),
    dict(n=5, key="nunchucks", bonus=2, reach=6, uses=12, shout="NUNCHUCKS!"),
    dict(n=6, key="shield", bonus=2, reach=0, uses=6, shout="SHIELD!"),
]
WEAPON_GRIP = {"spear": (30, 100)}   # hand position in the picture (others: 30, 66)
SHIELD_BLOCK = 3                      # a shield divides the damage you take by this
BOOMERANG_HIT = 7

PUNCH_REACH = 70
WHIRL_HIT = 4          # each of the WHIRLWIND KICK's hits
WHIRL_COOLDOWN = 1.2
DOUBLE_TAP = 0.6       # second KICK within this many seconds = WHIRLWIND KICK (HELICOPTER KICK in the air)
HELI_HIT = 3           # each of the HELICOPTER KICK's hits (up to 6)
HELI_FRAMES = 30       # how long the helicopter spins (frames)
TALK_Y = 22             # the enemy's speech bubble starts this high (the health bars are near the top)
HOLD_TIME = 0.22       # hold PUNCH or KICK this long to start charging a power move
MELEE_RATE = 3         # charge per frame: full (100) in about a second
JUMP_UP = 15        # first jump speed
FLIP_UP = 11        # second jump (front flip) speed
HERO_GRAV = 1.3
FLIP_FRAMES = 16    # one full turn
KICK_REACH = 82
SUPER_PER_HIT = 4
SUPER_PER_HURT = 8
SUPER_PER_PERFECT = 25
COMBO_WINDOW = 1.2
JOY_DEADZONE = 0.2
JOY_SPEED = 0.28  # pixels per frame = Joy X * Step * this
COMBO_BONUS = 3
ARCADE_HEAL = 30
SPIKE_OUCH = 5       # what bare hands take from punching spikes
RAIN_SPIKES = 5      # spikes in one Spike Rain
# Difficulty: name, enemy health x, enemy power x, enemy speed (Pace) x. Normal makes fights longer than before.
DIFFICULTIES = [
    ("easy", "EASY", "#16a34a", 1.2, 0.75, 1.2),
    ("normal", "NORMAL", "#2563eb", 2.0, 1.0, 1.0),
    ("hard", "HARD", "#ea580c", 2.8, 1.25, 0.85),
    ("champion", "CHAMPION", "#7c3aed", 3.6, 1.5, 0.72),
]
# Power levels: win fights to earn XP. Each level gives more health and harder hits,
# a new POWER move, a new aura colour, and tougher enemies.
#   level, key, aura colour, aura glow, XP needed, POWER move
POWER_LEVELS = [
    (1, "red", "#ef4444", "#f97316", 0, "none"),
    (2, "orange", "#f97316", "#fde047", 3, "FLAME DASH"),
    (3, "gold", "#facc15", "#fefce8", 7, "THUNDER STRIKE"),
    (4, "blue", "#3b82f6", "#e0f2fe", 12, "BLUE STORM"),
    (5, "ultra", "#a855f7", "#ffffff", 18, "ULTRA STORM"),
]
POWER_COOLDOWN = 6
POWER_HP_PER_LEVEL = 10
BOSS_WEAPONS = {"brute": "club", "megaspike": "mace", "ninja": "katana", "kage": "katana", "quake": "hammer",
                "shadow": "dark sword"}
MINION_HP = 7
MINION_HP_PER_LEVEL = 0.35   # small enemies get tougher with your power level too (x2.4 at level 5)
# ADVENTURE: stage after stage. Each stage = waves of small enemies, then its boss. After the last stage: LAP 2 (harder).
ADVENTURE = [
    dict(name="TRAINING YARD", backdrop="Yard", kind="grunt", waves=(3, 4), boss=3),     # Brute
    dict(name="BAMBOO FOREST", backdrop="Bamboo", kind="ninja", waves=(3, 4), boss=7),   # MASTER KAGE
    dict(name="ROBOT FACTORY", backdrop="Factory", kind="robot", waves=(4, 5), boss=5),  # MEGA SPIKE
    dict(name="VOLCANO GATE", backdrop="Volcano", kind="mix", waves=(4, 5), boss=8),     # Quake
    dict(name="SHADOW CASTLE", backdrop="Castle", kind="mix", waves=(4, 5, 6), boss=9),  # Shadow King
]
MINION_KINDS = ("ninja", "grunt", "robot")
BOSS_WEAPON_POWER = 3
RAIN_HURT = 8
CHARGE_RATE = 3.5    # charge per frame: full (100) in about one second
FIRE_FULL_BONUS = 4  # extra damage for a fully charged fireball

# ------------------------------------------------------------------ svg --


def svg_doc(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0,0,{width},{height}">{body}</svg>'
    )


def text_el(content, x, y, size, fill, anchor="middle", weight=700):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Verdana,Arial,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(content)}</text>'
    )


def outlined_text(content, x, y, size, fill, stroke="#0f172a"):
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Verdana,Arial,sans-serif" '
        f'font-size="{size}" font-weight="900" fill="{fill}" stroke="{stroke}" stroke-width="{max(2, size // 9)}" '
        f'paint-order="stroke">{escape(content)}</text>'
    )


POSES = {
    "idle": [(50, 64, 50, 112), (50, 78, 30, 104), (50, 78, 72, 96), (50, 112, 36, 168), (50, 112, 66, 168)],
    "punch": [(52, 64, 54, 112), (52, 78, 30, 92), (52, 78, 98, 74), (54, 112, 34, 168), (54, 112, 70, 168)],
    "kick": [(46, 64, 50, 112), (48, 78, 24, 66), (48, 78, 70, 90), (50, 112, 32, 168), (50, 112, 98, 118)],
    "jump": [(50, 70, 50, 112), (50, 82, 24, 58), (50, 82, 76, 58), (50, 112, 30, 142), (50, 112, 70, 142)],
    "hurt": [(42, 70, 58, 116), (42, 82, 18, 70), (42, 82, 70, 98), (58, 116, 36, 168), (58, 116, 78, 168)],
    "win": [(50, 70, 50, 114), (50, 80, 20, 40), (50, 80, 80, 40), (50, 114, 32, 168), (50, 114, 68, 168)],
    "dodge": [(40, 74, 30, 118), (38, 86, 10, 100), (38, 86, 60, 98), (30, 118, 14, 168), (30, 118, 62, 160)],
    "special": [(56, 70, 46, 116), (54, 82, 98, 60), (54, 82, 96, 92), (46, 116, 22, 168), (46, 116, 84, 168)],
    "windup": [(40, 66, 58, 116), (40, 80, 14, 92), (40, 80, 22, 60), (58, 116, 38, 168), (58, 116, 82, 168)],
    "charge": [(62, 70, 36, 116), (54, 82, 96, 70), (54, 82, 92, 96), (36, 116, 16, 150), (36, 116, 60, 168)],
    "aim": [(50, 64, 50, 112), (50, 78, 26, 94), (50, 78, 94, 66), (50, 112, 34, 168), (50, 112, 66, 168)],
    "raise": [(50, 68, 50, 114), (50, 78, 22, 34), (50, 78, 78, 34), (50, 114, 30, 168), (50, 114, 70, 168)],
    "slam": [(50, 66, 50, 116), (50, 86, 14, 126), (50, 86, 86, 126), (50, 116, 24, 168), (50, 116, 76, 168)],
    "down": [(20, 150, 72, 150), (40, 150, 24, 128), (40, 150, 62, 128), (72, 150, 90, 136), (72, 150, 94, 160)],
}
HEAD = {"down": (8, 140)}


def gear_svg(gear, color, hx, hy):
    if gear == "headband":
        return (
            f'<rect x="{hx - 17}" y="{hy - 9}" width="34" height="7" rx="3" fill="#dc2626"/>'
            f'<path d="M{hx - 16} {hy - 6} L{hx - 30} {hy - 12} M{hx - 16} {hy - 5} L{hx - 30} {hy + 2}" '
            'stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>'
        )
    if gear == "star":
        pts = []
        for k in range(10):
            r = 9 if k % 2 == 0 else 4
            a = -math.pi / 2 + k * math.pi / 5
            pts.append(f"{hx + 10 + r * math.cos(a):.1f},{hy - 16 + r * math.sin(a):.1f}")
        return (
            f'<path d="M{hx - 14} {hy - 6} Q{hx - 30} {hy + 6} {hx - 26} {hy + 22}" stroke="{color}" '
            'stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<polygon points="{" ".join(pts)}" fill="#facc15" stroke="#ffffff" stroke-width="2"/>'
        )
    if gear == "spikes":
        return (
            f'<path d="M{hx - 14} {hy - 8} L{hx - 10} {hy - 26} L{hx - 3} {hy - 12} L{hx + 2} {hy - 30} '
            f'L{hx + 7} {hy - 12} L{hx + 14} {hy - 24} L{hx + 15} {hy - 6} Z" fill="{color}" stroke="#ffffff" stroke-width="2"/>'
        )
    if gear == "leaf":
        return (
            f'<path d="M{hx} {hy - 16} Q{hx + 18} {hy - 34} {hx + 26} {hy - 18} Q{hx + 12} {hy - 8} {hx} {hy - 16} Z" '
            'fill="#22c55e" stroke="#ffffff" stroke-width="2"/>'
        )
    if gear == "horns":
        return (
            f'<path d="M{hx - 12} {hy - 12} Q{hx - 26} {hy - 22} {hx - 22} {hy - 36} Q{hx - 14} {hy - 22} {hx - 6} {hy - 16} Z" fill="#fef3c7" stroke="#0f172a" stroke-width="2"/>'
            f'<path d="M{hx + 12} {hy - 12} Q{hx + 26} {hy - 22} {hx + 22} {hy - 36} Q{hx + 14} {hy - 22} {hx + 6} {hy - 16} Z" fill="#fef3c7" stroke="#0f172a" stroke-width="2"/>'
        )
    if gear == "ninja":
        return (f'<path d="M{hx - 14} {hy - 8} L{hx - 30} {hy - 14} M{hx - 14} {hy - 6} L{hx - 28} {hy + 2}" '
                'stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>')
    if gear == "ninja boss":
        return (f'<rect x="{hx - 16}" y="{hy - 13}" width="32" height="5" rx="2" fill="#facc15"/>'
                f'<path d="M{hx - 15} {hy - 10} L{hx - 34} {hy - 20} M{hx - 15} {hy - 8} L{hx - 32} {hy + 4}" '
                'stroke="#dc2626" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M{hx - 10} {hy + 14} Q{hx} {hy + 22} {hx + 12} {hy + 14}" stroke="#dc2626" stroke-width="6" fill="none"/>')
    if gear == "crown":
        return (
            f'<path d="M{hx - 15} {hy - 12} L{hx - 15} {hy - 30} L{hx - 7} {hy - 20} L{hx} {hy - 34} L{hx + 7} {hy - 20} '
            f'L{hx + 15} {hy - 30} L{hx + 15} {hy - 12} Z" fill="#a855f7" stroke="#facc15" stroke-width="2"/>'
        )
    return ""


# Jointed stick figures: elbows and knees bend, the spine can fold, and the
# far arm and leg are drawn a little darker so the body has depth.
# Joints (facing right, feet on y=168): h head, n neck, c chest, p hip,
# fe/fh far elbow/hand, ne/nh near elbow/hand, fk/ff far knee/foot, nk/nf near knee/foot.
SKEL = {
    "idle":    dict(h=(52, 46), n=(51, 64), c=(51, 86), p=(49, 110), fe=(40, 84), fh=(55, 72), ne=(63, 88), nh=(72, 72),
                    fk=(41, 138), ff=(33, 168), nk=(61, 138), nf=(67, 168)),
    "idle b":  dict(h=(52, 48), n=(51, 66), c=(51, 88), p=(49, 110), fe=(40, 87), fh=(55, 75), ne=(63, 91), nh=(72, 76),
                    fk=(41, 139), ff=(33, 168), nk=(61, 139), nf=(67, 168)),
    "walk 1":  dict(h=(54, 47), n=(53, 65), c=(52, 87), p=(50, 110), fe=(58, 88), fh=(66, 102), ne=(42, 88), nh=(36, 102),
                    fk=(58, 137), ff=(68, 166), nk=(44, 138), nf=(32, 160)),
    "walk 2":  dict(h=(54, 45), n=(53, 63), c=(52, 85), p=(50, 108), fe=(52, 88), fh=(54, 104), ne=(50, 88), nh=(50, 104),
                    fk=(50, 138), ff=(48, 168), nk=(57, 134), nf=(52, 158)),
    "walk 3":  dict(h=(54, 47), n=(53, 65), c=(52, 87), p=(50, 110), fe=(42, 88), fh=(36, 102), ne=(60, 88), nh=(68, 102),
                    fk=(44, 138), ff=(32, 160), nk=(58, 137), nf=(68, 166)),
    "walk 4":  dict(h=(54, 45), n=(53, 63), c=(52, 85), p=(50, 108), fe=(50, 88), fh=(50, 104), ne=(52, 88), nh=(54, 104),
                    fk=(57, 134), ff=(52, 158), nk=(50, 138), nf=(48, 168)),
    "punch 1": dict(h=(47, 47), n=(47, 65), c=(48, 87), p=(50, 110), fe=(58, 82), fh=(66, 70), ne=(40, 92), nh=(46, 78),
                    fk=(40, 138), ff=(30, 168), nk=(60, 138), nf=(66, 168)),
    "punch":   dict(h=(58, 47), n=(56, 65), c=(54, 87), p=(50, 110), fe=(46, 84), fh=(56, 72), ne=(76, 72), nh=(97, 70),
                    fk=(38, 138), ff=(28, 168), nk=(64, 136), nf=(74, 168)),
    "kick 1":  dict(h=(46, 46), n=(46, 64), c=(47, 86), p=(49, 110), fe=(32, 80), fh=(24, 92), ne=(62, 80), nh=(70, 70),
                    fk=(46, 139), ff=(42, 168), nk=(70, 106), nf=(64, 132)),
    "kick":    dict(h=(40, 50), n=(42, 67), c=(45, 88), p=(50, 112), fe=(30, 78), fh=(20, 90), ne=(56, 82), nh=(62, 70),
                    fk=(46, 140), ff=(42, 168), nk=(74, 112), nf=(99, 106)),
    "jump":    dict(h=(52, 50), n=(51, 68), c=(51, 88), p=(50, 108), fe=(36, 76), fh=(26, 60), ne=(66, 76), nh=(76, 60),
                    fk=(40, 124), ff=(34, 146), nk=(62, 120), nf=(66, 142)),
    "fall":    dict(h=(52, 48), n=(51, 66), c=(51, 87), p=(50, 108), fe=(34, 70), fh=(26, 54), ne=(68, 70), nh=(76, 54),
                    fk=(44, 134), ff=(40, 158), nk=(58, 134), nf=(62, 158)),
    # hit in the belly: the body folds over, hands to the stomach
    "hurt":    dict(h=(70, 76), n=(64, 88), c=(56, 98), p=(44, 112), fe=(52, 108), fh=(60, 110), ne=(66, 104), nh=(62, 112),
                    fk=(40, 140), ff=(34, 168), nk=(56, 140), nf=(60, 168)),
    # hit in the head: it snaps back, arms fly out
    "hurt high": dict(h=(34, 48), n=(41, 64), c=(46, 86), p=(52, 112), fe=(30, 68), fh=(18, 56), ne=(56, 76), nh=(44, 62),
                      fk=(46, 140), ff=(36, 168), nk=(64, 138), nf=(72, 168)),
    "win":     dict(h=(50, 48), n=(50, 66), c=(50, 88), p=(50, 112), fe=(34, 52), fh=(26, 30), ne=(66, 52), nh=(74, 30),
                    fk=(42, 140), ff=(36, 168), nk=(58, 140), nf=(64, 168)),
    "dodge":   dict(h=(40, 72), n=(42, 88), c=(44, 104), p=(50, 122), fe=(30, 100), fh=(22, 112), ne=(54, 104), nh=(46, 118),
                    fk=(36, 140), ff=(24, 168), nk=(62, 142), nf=(66, 168)),
    "special": dict(h=(60, 52), n=(58, 70), c=(54, 90), p=(48, 114), fe=(74, 76), fh=(96, 72), ne=(76, 84), nh=(98, 86),
                    fk=(34, 140), ff=(22, 168), nk=(66, 140), nf=(80, 168)),
    "windup":  dict(h=(44, 48), n=(45, 66), c=(47, 88), p=(52, 112), fe=(30, 84), fh=(20, 70), ne=(36, 70), nh=(24, 56),
                    fk=(42, 140), ff=(34, 168), nk=(62, 140), nf=(70, 168)),
    "charge":  dict(h=(70, 62), n=(64, 76), c=(56, 92), p=(44, 114), fe=(70, 92), fh=(88, 96), ne=(74, 84), nh=(94, 78),
                    fk=(30, 136), ff=(14, 150), nk=(56, 140), nf=(62, 168)),
    "aim":     dict(h=(52, 46), n=(51, 64), c=(51, 86), p=(49, 110), fe=(42, 86), fh=(56, 76), ne=(72, 70), nh=(94, 66),
                    fk=(40, 138), ff=(32, 168), nk=(62, 138), nf=(68, 168)),
    "raise":   dict(h=(50, 50), n=(50, 68), c=(50, 90), p=(50, 114), fe=(36, 50), fh=(32, 28), ne=(64, 50), nh=(68, 28),
                    fk=(38, 140), ff=(30, 168), nk=(62, 140), nf=(70, 168)),
    "slam":    dict(h=(54, 62), n=(52, 78), c=(50, 98), p=(48, 120), fe=(34, 106), fh=(22, 128), ne=(66, 106), nh=(80, 128),
                    fk=(32, 140), ff=(24, 168), nk=(66, 140), nf=(76, 168)),
    "down":    dict(h=(20, 150), n=(32, 152), c=(46, 154), p=(64, 156), fe=(38, 140), fh=(48, 132), ne=(40, 162), nh=(52, 166),
                    fk=(78, 144), ff=(92, 152), nk=(80, 160), nf=(95, 166)),
    # ninjas
    # tucked into a ball for the front flip (it is drawn turning round in 4 steps)
    "spin 1":  dict(h=(48, 44), n=(49, 62), c=(50, 84), p=(50, 106), fe=(36, 76), fh=(24, 70), ne=(62, 76), nh=(72, 68),
                    fk=(44, 132), ff=(48, 154), nk=(74, 104), nf=(99, 100)),
    "spin 2":  dict(h=(50, 44), n=(50, 62), c=(50, 84), p=(50, 106), fe=(40, 74), fh=(30, 64), ne=(60, 74), nh=(70, 64),
                    fk=(46, 132), ff=(48, 154), nk=(58, 118), nf=(62, 128)),
    "spin 3":  dict(h=(52, 44), n=(51, 62), c=(50, 84), p=(50, 106), fe=(64, 76), fh=(76, 70), ne=(38, 76), nh=(28, 68),
                    fk=(56, 132), ff=(52, 154), nk=(26, 104), nf=(1, 100)),
    "spin 4":  dict(h=(50, 44), n=(50, 62), c=(50, 84), p=(50, 106), fe=(60, 74), fh=(70, 64), ne=(40, 74), nh=(30, 64),
                    fk=(54, 132), ff=(52, 154), nk=(42, 118), nf=(38, 128)),
    # HELICOPTER KICK: legs split wide like rotor blades, drawn turning round in 4 steps
    "heli 1":  dict(h=(50, 44), n=(50, 62), c=(50, 84), p=(50, 106), fe=(34, 70), fh=(16, 64), ne=(66, 70), nh=(84, 64),
                    fk=(28, 116), ff=(4, 122), nk=(72, 116), nf=(96, 122)),
    "heli 2":  dict(h=(50, 44), n=(50, 62), c=(50, 84), p=(50, 106), fe=(42, 72), fh=(34, 66), ne=(58, 72), nh=(66, 66),
                    fk=(44, 122), ff=(38, 136), nk=(58, 120), nf=(66, 130)),
    "heli 3":  dict(h=(50, 44), n=(50, 62), c=(50, 84), p=(50, 106), fe=(66, 70), fh=(84, 64), ne=(34, 70), nh=(16, 64),
                    fk=(72, 116), ff=(96, 122), nk=(28, 116), nf=(4, 122)),
    "heli 4":  dict(h=(50, 44), n=(50, 62), c=(50, 84), p=(50, 106), fe=(58, 72), fh=(66, 66), ne=(42, 72), nh=(34, 66),
                    fk=(58, 120), ff=(66, 130), nk=(44, 122), nf=(36, 134)),
    # SKY KICK: one foot shoots straight up and forward
    "sky kick": dict(h=(38, 58), n=(41, 75), c=(45, 96), p=(50, 118), fe=(30, 88), fh=(20, 100), ne=(52, 90), nh=(60, 102),
                     fk=(44, 142), ff=(40, 168), nk=(66, 98), nf=(84, 66)),
    "tuck":    dict(h=(58, 82), n=(54, 96), c=(50, 106), p=(44, 120), fe=(58, 104), fh=(66, 116), ne=(62, 102), nh=(70, 114),
                    fk=(62, 112), ff=(56, 132), nk=(64, 116), nf=(58, 136)),
    # powering up: wide crouch, fists clenched, head back, yelling
    "charge up": dict(h=(48, 44), n=(49, 62), c=(50, 86), p=(50, 112), fe=(34, 92), fh=(25, 110), ne=(66, 92), nh=(75, 110),
                      fk=(33, 138), ff=(20, 168), nk=(67, 138), nf=(80, 168)),
    "slash":   dict(h=(60, 50), n=(58, 68), c=(54, 90), p=(48, 112), fe=(44, 82), fh=(52, 92), ne=(74, 80), nh=(92, 96),
                    fk=(36, 140), ff=(24, 168), nk=(64, 138), nf=(76, 168)),
    "run 1":   dict(h=(66, 52), n=(62, 68), c=(56, 88), p=(48, 110), fe=(40, 94), fh=(30, 106), ne=(70, 86), nh=(78, 100),
                    fk=(66, 130), ff=(76, 150), nk=(42, 138), nf=(26, 152)),
    "run 2":   dict(h=(66, 54), n=(62, 70), c=(56, 90), p=(48, 112), fe=(70, 88), fh=(78, 102), ne=(40, 96), nh=(30, 108),
                    fk=(42, 138), ff=(28, 156), nk=(64, 132), nf=(72, 166)),
    "flip":    dict(h=(50, 112), n=(52, 96), c=(54, 86), p=(50, 70), fe=(38, 90), fh=(34, 104), ne=(62, 90), nh=(66, 104),
                    fk=(40, 54), ff=(34, 40), nk=(60, 54), nf=(66, 40)),
}


ROBOT_HANDS = {  # x, y of the arm end and the compass direction it points (robots have no elbow)
    "idle": (76, 124, 180), "windup": (76, 124, 180), "attack": (95, 105, 100), "hurt": (74, 122, 170), "down": (84, 152, 90),
}


def hand_of(pose, rot=0):
    """Where the front hand is in a 100x180 costume (feet at 50,168), and which way the forearm points
    (Scratch compass: 0 up, 90 right)."""
    if pose.startswith("robot:"):
        x, y, d = ROBOT_HANDS[pose[6:]]
        return x - 50, 168 - y, d
    j = SKEL[pose]
    (ex, ey), (hx, hy) = j["ne"], j["nh"]
    if rot:
        a = math.radians(rot)

        def turn(px, py):
            px, py = px - 54, py - 108
            return 54 + px * math.cos(a) - py * math.sin(a), 108 + px * math.sin(a) + py * math.cos(a)
        ex, ey = turn(ex, ey)
        hx, hy = turn(hx, hy)
    direction = math.degrees(math.atan2(hx - ex, -(hy - ey)))
    return round(hx - 50, 1), round(168 - hy, 1), round(direction, 1)


HERO_POSE_SRC = {"charge": "aim"}
ENEMY_POSE_SRC = {
    "attack": {"rival": "punch", "ivy": "aim", "brute": "charge", "quake": "slam", "shadow": "special", "ninja": "slash", "kage": "slash"},
    "windup": {"quake": "raise", "shadow": "raise"},
}


def costume_hand(name, kind):
    """The hand for one costume name of the Hero or the Enemy sprite."""
    if kind == "hero":
        if " flip " in name:
            return hand_of("tuck", 90 * (int(name.rsplit(" ", 1)[1]) - 1))
        for p_ in sorted(SKEL, key=len, reverse=True) + ["charge"]:
            if name.endswith(" " + p_):
                return hand_of(HERO_POSE_SRC.get(p_, p_))
        raise ValueError(name)
    key, pose = name.split(" ", 1)
    if name in ("shadow angry", "shadow spikes"):
        return hand_of("raise")
    if key in ("spikebot", "megaspike"):
        rp = {"idle b": "idle", "hurt high": "hurt"}.get(pose, "idle" if pose.startswith("walk") else pose)
        return hand_of("robot:" + rp)
    if pose in ENEMY_POSE_SRC:
        return hand_of(ENEMY_POSE_SRC[pose].get(key, "windup" if pose == "windup" else pose))
    return hand_of(pose)


def shade(color, amount=0.35):
    """The same colour, darker: for the far arm and leg."""
    c = color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(int(v * (1 - amount)) for v in (r, g, b))


HAIR = {"gold": ("#facc15", "#a16207"), "silver": ("#f1f5f9", "#64748b")}


def hair_svg(kind, hx, hy):
    """Spiky super-form hair (Dragon Ball style)."""
    fill, edge = HAIR[kind]
    pts = [(-17, -2), (-27, -20), (-12, -15), (-10, -40), (1, -19), (9, -44), (12, -17), (28, -30), (18, -4), (0, -12)]
    path = " ".join(f"{hx + x},{hy + y}" for x, y in pts)
    return f'<polygon points="{path}" fill="{fill}" stroke="{edge}" stroke-width="2.5" stroke-linejoin="round"/>'


def fighter_svg(color, pose, gear="none", face="smile", glow=None, hair=None, rot=0):
    """rot turns the whole figure around its middle (for the front flip)."""
    svg = _fighter_svg(color, pose, gear, face, glow, hair)
    if not rot:
        return svg
    inner = svg[svg.index(">") + 1: -len("</svg>")]
    return svg_doc(100, 180, f'<g transform="rotate({rot} 54 108)">{inner}</g>')


def _fighter_svg(color, pose, gear="none", face="smile", glow=None, hair=None):
    """A jointed stick figure in a 100 by 180 box, facing right. Feet sit on y=168."""
    j = SKEL[pose]
    hx, hy = j["h"]
    dark = shade(color)
    far = [(j["n"], j["fe"], j["fh"]), (j["p"], j["fk"], j["ff"])]
    near_leg = (j["p"], j["nk"], j["nf"])
    near_arm = (j["n"], j["ne"], j["nh"])
    spine = (j["n"], j["c"], j["p"])
    line = lambda pts: "polyline points=\"" + " ".join(f"{x},{y}" for x, y in pts) + "\""  # noqa: E731
    parts = []
    if glow:
        parts.append(f'<ellipse cx="50" cy="100" rx="46" ry="78" fill="{glow}" opacity="0.35"/>')
    # white outline under everything so fighters stand out on any stage
    parts.append('<g fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">')
    parts.append(f'<circle cx="{hx}" cy="{hy}" r="18" fill="#ffffff"/>')
    parts += [f"<{line(seg)}/>" for seg in (*far, spine, near_leg, near_arm, (j["n"], (hx, hy)))]
    parts.append("</g>")
    common = 'fill="none" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    parts += [f'<{line(seg)} stroke="{dark}" {common}/>' for seg in far]
    parts.append(f'<{line((j["n"], (hx, hy)))} stroke="{color}" {common}/>')
    parts.append(f'<{line(spine)} stroke="{color}" {common.replace('stroke-width="7"', 'stroke-width="8"')}/>')
    parts.append(f'<{line(near_leg)} stroke="{color}" {common}/>')
    parts.append(f'<{line(near_arm)} stroke="{color}" {common}/>')
    # fists and feet: small rounded ends make the poses read better
    parts.append(f'<circle cx="{j["nh"][0]}" cy="{j["nh"][1]}" r="4.5" fill="{color}"/>')
    parts.append(f'<circle cx="{hx}" cy="{hy}" r="16" fill="{color}"/>')
    if face == "yell":
        parts.append(f'<ellipse cx="{hx + 6}" cy="{hy + 7}" rx="4" ry="5" fill="#ffffff"/>')
    if hair:
        parts.append(hair_svg(hair, hx, hy))
    parts.append(gear_svg(gear, color, hx, hy))
    ex = hx + 4
    if gear in ("ninja", "ninja boss"):
        # ninja mask: only the eyes show
        parts.append(f'<rect x="{hx - 15}" y="{hy - 6}" width="30" height="9" rx="4" fill="#f5f5f4"/>')
        eye = "#dc2626" if gear == "ninja boss" else "#0f172a"
        parts.append(f'<circle cx="{ex - 1}" cy="{hy - 1.5}" r="2.4" fill="{eye}"/><circle cx="{ex + 8}" cy="{hy - 1.5}" r="2.4" fill="{eye}"/>')
        return svg_doc(100, 180, "".join(parts))
    if face == "ko":
        parts.append(f'<path d="M{ex - 4} {hy - 5} l5 5 m0 -5 l-5 5 M{ex + 6} {hy - 5} l5 5 m0 -5 l-5 5" stroke="#ffffff" stroke-width="2"/>')
    else:
        parts.append(f'<circle cx="{ex - 2}" cy="{hy - 2}" r="2.4" fill="#ffffff"/>')
        parts.append(f'<circle cx="{ex + 8}" cy="{hy - 2}" r="2.4" fill="#ffffff"/>')
    if face == "angry":
        parts.append(f'<path d="M{ex - 6} {hy - 10} L{ex + 1} {hy - 6} M{ex + 13} {hy - 10} L{ex + 6} {hy - 6}" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<path d="M{ex - 2} {hy + 9} Q{ex + 3} {hy + 5} {ex + 8} {hy + 9}" stroke="#ffffff" stroke-width="2" fill="none"/>')
    elif face in ("hurt", "ko"):
        parts.append(f'<circle cx="{ex + 3}" cy="{hy + 8}" r="3" fill="#ffffff"/>')
    else:
        parts.append(f'<path d="M{ex - 3} {hy + 6} Q{ex + 3} {hy + 12} {ex + 9} {hy + 6}" stroke="#ffffff" stroke-width="2" fill="none"/>')
    return svg_doc(100, 180, "".join(parts))


def button_svg(label, fill, ink="#ffffff", width=62, height=44, size=12):
    body = (
        f'<rect x="2" y="2" width="{width - 4}" height="{height - 4}" rx="12" fill="{fill}" stroke="#ffffff" stroke-width="3"/>'
        + text_el(label, width / 2, height / 2 + size * 0.38, size, ink)
    )
    return svg_doc(width, height, body)


def hud_info():
    """Names and colours of every fighter, for the app page's own health bars (JSON in the HUD Info variable)."""
    info = {}
    for k in BRAWL_KINDS:
        info[k["key"]] = [k["tag"], k["color"]]
    for e in ENEMIES:
        info[e["key"]] = [e["tag"], e["color"] if e["n"] != KING else "#581c87"]
    for h in HEROES:
        info[h["key"]] = [h["name"], h["color"]]
    return json.dumps(info, separators=(",", ":"))


def bar_svg(width, height, fill):
    return svg_doc(width, height, f'<rect x="0" y="1" width="{width}" height="{height - 2}" rx="{height / 2 - 1}" fill="{fill}" stroke="#0f172a" stroke-width="2"/>')


def tag_svg(word, fill="#0f172a"):
    width = 12 + 10 * len(word)
    return svg_doc(width, 20, f'<rect x="0" y="0" width="{width}" height="20" rx="6" fill="{fill}" opacity="0.85"/>' + text_el(word, width / 2, 15, 13, "#ffffff"))


def card_svg(title, lines, accent):
    body = [
        '<rect x="8" y="8" width="404" height="224" rx="22" fill="#fffbeb" stroke="#0f172a" stroke-width="6"/>',
        f'<path d="M8 72 L8 30 Q8 8 30 8 L390 8 Q412 8 412 30 L412 72 Z" fill="{accent}"/>',
        outlined_text(title, 210, 54, 34, "#ffffff"),
    ]
    y = 112
    for line in lines:
        body.append(text_el(line, 210, y, 21, "#0f172a"))
        y += 36
    return svg_doc(420, 240, "".join(body))


def banner_size(word):
    size = 60 if len(word) <= 8 else int(560 / len(word))
    return size, max(260, int(len(word) * size * 0.78) + 20)


def banner_svg(word, fill):
    size, width = banner_size(word)
    return svg_doc(width, 90, outlined_text(word, width / 2, 45 + size * 0.36, size, fill))


def hero_card_svg(hero):
    color = hero["color"]
    fig = fighter_svg(color, "win", hero["gear"])
    fig_inner = fig[fig.index(">") + 1 : -len("</svg>")]
    rows = []
    for i, (label, value) in enumerate(zip(("POWER", "SPEED", "HEALTH"), hero["stats"])):
        y = 196 + i * 18
        rows.append(text_el(label, 12, y + 9, 11, "#334155", anchor="start"))
        for k in range(5):
            on = k < value
            rows.append(f'<rect x="{68 + k * 13}" y="{y}" width="11" height="10" rx="2" fill="{color if on else "#cbd5e1"}"/>')
    body = (
        '<rect x="3" y="3" width="134" height="250" rx="16" fill="#ffffff" stroke="#0f172a" stroke-width="5"/>'
        f'<rect x="3" y="3" width="134" height="36" rx="14" fill="{color}"/>'
        + text_el(hero["name"], 70, 28, 18, "#ffffff")
        + f'<g transform="translate(30,34) scale(0.8)">{fig_inner}</g>'
        + text_el(hero["trait"], 70, 186, 13, "#0f172a")
        + "".join(rows)
    )
    return svg_doc(140, 256, body)


def boss_weapon_svg(kind):
    if kind == "club":
        art = ('<path d="M26 72 L22 30 Q20 6 32 4 Q44 6 40 30 L34 72 Z" fill="#92400e" stroke="#451a03" stroke-width="2.5"/>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="2.5" fill="#d6d3d1"/>' for x, y in ((26, 16), (37, 20), (30, 28), (34, 10))))
    elif kind == "mace":
        spikes = "".join(
            f'<polygon points="{30 + 13 * math.cos(a) - 4 * math.sin(a):.1f},{18 + 13 * math.sin(a) + 4 * math.cos(a):.1f} '
            f'{30 + 24 * math.cos(a):.1f},{18 + 24 * math.sin(a):.1f} '
            f'{30 + 13 * math.cos(a) + 4 * math.sin(a):.1f},{18 + 13 * math.sin(a) - 4 * math.cos(a):.1f}" fill="#e5e7eb" stroke="#1f2937" stroke-width="2"/>'
            for a in [k * math.pi / 4 for k in range(8)])
        art = ('<rect x="27" y="28" width="6" height="46" rx="2" fill="#57534e" stroke="#1c1917" stroke-width="2"/>'
               + spikes + '<circle cx="30" cy="18" r="14" fill="#78716c" stroke="#1c1917" stroke-width="2.5"/>')
    elif kind == "katana":
        art = ('<path d="M29 0 Q36 26 32 56 L27 56 Q30 26 26 2 Z" fill="#e5e7eb" stroke="#334155" stroke-width="1.5"/>'
               '<ellipse cx="29.5" cy="57" rx="9" ry="3" fill="#facc15" stroke="#713f12" stroke-width="1"/>'
               '<rect x="26.5" y="59" width="6" height="15" rx="2" fill="#111827"/>'
               '<path d="M27 62 l5 3 M27 66 l5 3 M27 70 l5 3" stroke="#dc2626" stroke-width="1.5"/>')
    elif kind == "dark sword":
        art = ('<path d="M27 2 L33 2 L35 54 L25 54 Z" fill="#a855f7" stroke="#3b0764" stroke-width="2"/>'
               '<path d="M29 6 L30 50" stroke="#e9d5ff" stroke-width="2"/>'
               '<rect x="14" y="54" width="32" height="6" rx="3" fill="#facc15" stroke="#713f12" stroke-width="1.5"/>'
               '<rect x="27" y="60" width="6" height="14" rx="2" fill="#1e1b4b"/>')
    else:
        return weapon_svg(kind)
    return svg_doc(60, 76, art)


def aura_svg(frame, level=1):
    """Fire around a fighter (100 x 180 box, feet at 168), one of 4 animation frames. Each power level has more
    and longer flames, more layers, a hotter core and (from level 3) crackling lightning."""
    _n, _key, c1, c2, _xp, _move = POWER_LEVELS[level - 1]
    count = 12 + 3 * level
    reach = 1 + 0.07 * (level - 1)
    phase = frame * math.pi / 2

    def ring(n, rx, ry, length, width, colors, spin, opacity):
        out = []
        for k in range(n):
            a = k * 2 * math.pi / n + spin
            # each flame tongue flickers longer and shorter from frame to frame, and leans upward
            flick = 1 + 0.18 * math.sin(phase + k * 1.7) + 0.08 * math.sin(2 * phase + k * 0.9)
            up = 1 + 0.25 * max(0.0, -math.sin(a))          # flames on top reach higher
            cx, cy = 50 + rx * math.cos(a), 98 + ry * math.sin(a)
            tx = 50 + (rx + length) * flick * reach * math.cos(a - 0.22)
            ty = 98 + (ry + length * 1.5) * flick * up * reach * math.sin(a - 0.22) - 6 * flick
            out.append(f'<path d="M{cx - width * math.sin(a):.1f} {cy + width * math.cos(a):.1f} Q{tx:.1f} {ty:.1f} '
                       f'{cx + width * math.sin(a):.1f} {cy - width * math.cos(a):.1f} Z" fill="{colors[k % 2]}" opacity="{opacity}"/>')
        return "".join(out)
    layers = ""
    if level >= 3:   # an outer layer of long, see-through flames
        layers += ring(count - 4, 44, 80, 34, 11, (c1, c2), 0.4 + frame * 0.12, 0.45)
    layers += ring(count, 40, 76, 22, 9, (c1, c2), frame * 0.22, 0.95)
    if level >= 2:   # an inner layer of short bright flames
        layers += ring(count // 2 + 2, 30, 64, 14, 6, (c2, "#ffffff"), 0.6 - frame * 0.18, 0.7)
    core = f'<ellipse cx="50" cy="98" rx="{30 + 2 * level}" ry="{66 + 2 * level}" fill="{c2}" opacity="{0.22 + 0.05 * level:.2f}"/>'
    if level >= 4:   # white-hot middle
        core += '<ellipse cx="50" cy="104" rx="20" ry="52" fill="#ffffff" opacity="0.25"/>'
    sparks = ""
    if level >= 3:   # lightning crackles in the aura, more each level, jumping about from frame to frame
        for k in range({3: 1, 4: 3, 5: 6}[level]):
            a = k * 2.4 + frame * 1.3
            x0, y0 = 50 + 46 * math.cos(a), 98 + 82 * math.sin(a)
            sparks += (f'<path d="M{x0:.0f} {y0:.0f} l{5 + frame} -9 l-5 2 l{6 - frame} -11 l-4 1 l5 -9" stroke="#ffffff" '
                       'stroke-width="2.4" fill="none" stroke-linejoin="round"/>')
    return svg_doc(150, 240, (
        '<g transform="translate(25,30)">'
        f'<ellipse cx="50" cy="98" rx="48" ry="86" fill="{c1}" opacity="0.32"/>'
        + layers + core + sparks + '</g>'))


def ki_spark_svg(level):
    """A streak of energy that shoots up around a fighter powering up (in the colour of the power level)."""
    _n, _key, c1, c2, *_r = POWER_LEVELS[level - 1]
    return svg_doc(16, 60, (
        f'<defs><linearGradient id="ks" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/>'
        f'<stop offset="0.35" stop-color="{c2}"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></linearGradient></defs>'
        '<path d="M8 2 Q13 20 10 58 L6 58 Q3 20 8 2 Z" fill="url(#ks)"/>'))


def ki_rays_svg(level):
    """A burst of light rays when the power-up reaches its peak: more rays each level."""
    _n, _key, c1, c2, *_r = POWER_LEVELS[level - 1]
    n = 8 + 3 * level
    rays = []
    for k in range(n):
        a = k * 2 * math.pi / n
        r = 118 if k % 2 else 90
        x1, y1 = 120 + r * math.cos(a - 0.07), 120 + r * math.sin(a - 0.07)
        x2, y2 = 120 + r * math.cos(a + 0.07), 120 + r * math.sin(a + 0.07)
        rays.append(f'<polygon points="120,120 {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}" fill="{c2 if k % 2 else c1}" opacity="0.8"/>')
    return svg_doc(240, 240, "".join(rays) + f'<circle cx="120" cy="120" r="26" fill="#ffffff" opacity="0.85"/>'
                   f'<circle cx="120" cy="120" r="40" fill="{c2}" opacity="0.4"/>')


def _old_aura_svg(frame):
    flames = []
    for k in range(14):
        a = k * 2 * math.pi / 14 + (0.22 if frame else 0)
        cx, cy = 50 + 40 * math.cos(a), 98 + 76 * math.sin(a)
        tx, ty = 50 + (60 + 8 * (k % 2)) * math.cos(a - 0.25), 98 + (96 + 8 * (k % 2)) * math.sin(a - 0.25)
        flames.append(f'<path d="M{cx - 9 * math.sin(a):.1f} {cy + 9 * math.cos(a):.1f} Q{tx:.1f} {ty:.1f} '
                      f'{cx + 9 * math.sin(a):.1f} {cy - 9 * math.cos(a):.1f} Z" fill="{"#ef4444" if k % 2 else "#f97316"}"/>')
    return svg_doc(140, 220, (
        '<g transform="translate(20,20)">'
        '<ellipse cx="50" cy="98" rx="46" ry="84" fill="#ef4444" opacity="0.35"/>'
        + "".join(flames) +
        '<ellipse cx="50" cy="98" rx="34" ry="70" fill="#fca5a5" opacity="0.25"/></g>'))


def bolt_svg(core, glow):
    """A lightning bolt from the sky; its tip (the bottom) is the rotation centre."""
    pts = [(30, 0), (22, 70), (38, 120), (18, 200), (36, 250), (20, 330), (34, 370), (30, 420)]
    path = " ".join(f"{x},{y}" for x, y in pts)
    return svg_doc(60, 430, (
        f'<polyline points="{path}" fill="none" stroke="{glow}" stroke-width="18" stroke-linejoin="round" opacity="0.5"/>'
        f'<polyline points="{path}" fill="none" stroke="{core}" stroke-width="7" stroke-linejoin="round"/>'
        '<polyline points="38,120 52,150 46,170" fill="none" stroke="#ffffff" stroke-width="3"/>'
        '<polyline points="36,250 14,280 18,300" fill="none" stroke="#ffffff" stroke-width="3"/>'
        f'<ellipse cx="30" cy="420" rx="28" ry="9" fill="{glow}" opacity="0.8"/>'))


def bolt_warning_svg():
    return svg_doc(70, 18, '<ellipse cx="35" cy="9" rx="32" ry="8" fill="#fde047" opacity="0.7" stroke="#a16207" stroke-width="2"/>'
                           '<path d="M35 1 l-5 8 l4 0 l-4 8" stroke="#a16207" stroke-width="2" fill="none"/>')


def power_badge_svg(level):
    _n, _key, c1, c2, _xp, move = POWER_LEVELS[level - 1]
    stars = "".join(f'<circle cx="{104 + 10 * i}" cy="21" r="3.5" fill="{c1 if i < level else "#334155"}"/>' for i in range(5))
    return svg_doc(160, 30, f'<rect x="1" y="1" width="158" height="28" rx="10" fill="#0f172a" stroke="{c1}" stroke-width="3"/>'
                   + text_el(f"POWER LV {level}", 50, 15, 11, c2 if level > 2 else c1)
                   + text_el(move if move != "none" else "win to level up", 50, 25, 7, "#cbd5e1") + stars)


def difficulty_svg(word, fill):
    return svg_doc(190, 40, f'<rect x="2" y="2" width="186" height="36" rx="12" fill="#0f172a" stroke="{fill}" stroke-width="4"/>'
                   + text_el("LEVEL:", 52, 26, 13, "#cbd5e1") + text_el(word, 126, 26, 15, fill))


def weapon_svg(kind, sparkle=False):
    glow = '<circle cx="30" cy="40" r="28" fill="#fde68a" opacity="0.7"/>' if sparkle else ""
    if kind == "sword":
        art = (
            '<path d="M27 6 L33 6 L34 52 L26 52 Z" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>'
            '<rect x="16" y="52" width="28" height="6" rx="3" fill="#ca8a04" stroke="#713f12" stroke-width="1.5"/>'
            '<rect x="27" y="58" width="6" height="14" rx="2" fill="#78350f"/>'
        )
    elif kind == "hammer":
        art = (
            '<rect x="27" y="22" width="6" height="50" rx="2" fill="#92400e" stroke="#451a03" stroke-width="1.5"/>'
            '<rect x="10" y="6" width="40" height="22" rx="4" fill="#94a3b8" stroke="#334155" stroke-width="2"/>'
        )
    elif kind == "spear":
        # a long spear, held near the bottom (110 tall)
        glow = '<ellipse cx="30" cy="55" rx="28" ry="52" fill="#fde68a" opacity="0.7"/>' if sparkle else ""
        art = (
            '<rect x="27" y="22" width="6" height="86" rx="2" fill="#a16207" stroke="#713f12" stroke-width="1.5"/>'
            '<path d="M30 2 L38 24 L30 30 L22 24 Z" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>'
            '<path d="M24 30 L36 30 L33 36 L27 36 Z" fill="#dc2626"/>'
        )
        return svg_doc(60, 110, glow + art)
    elif kind == "nunchucks":
        art = (
            '<rect x="25" y="40" width="9" height="32" rx="4" fill="#1f2937" stroke="#facc15" stroke-width="1.5"/>'
            '<path d="M30 40 Q36 34 30 28" stroke="#94a3b8" stroke-width="2.5" fill="none" stroke-dasharray="3 2"/>'
            '<rect x="22" y="2" width="9" height="30" rx="4" fill="#1f2937" stroke="#facc15" stroke-width="1.5" transform="rotate(-20 26 28)"/>'
        )
    elif kind == "shield":
        art = (
            '<path d="M8 12 Q30 2 52 12 L50 40 Q46 62 30 72 Q14 62 10 40 Z" fill="#1d4ed8" stroke="#1e3a8a" stroke-width="3"/>'
            '<path d="M14 16 Q30 8 46 16 L44 40 Q40 56 30 64 Q20 56 16 40 Z" fill="#3b82f6"/>'
            '<path d="M30 18 L34 32 L48 32 L37 40 L41 54 L30 46 L19 54 L23 40 L12 32 L26 32 Z" fill="#facc15"/>'
        )
    else:
        art = (
            '<path d="M12 64 Q14 24 46 10 Q40 20 24 40 Q18 52 22 66 Z" fill="#f97316" stroke="#7c2d12" stroke-width="2"/>'
            '<path d="M22 66 Q30 50 52 46 Q44 54 22 66 Z" fill="#fb923c" stroke="#7c2d12" stroke-width="2"/>'
        )
    return svg_doc(60, 76, glow + art)


def backdrop_svg(kind):
    g = 180 - GROUND  # svg y of the ground line
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fef3c7"/>' for x, y, r in (
        (40, 40, 2), (90, 90, 3), (150, 30, 2), (330, 40, 3), (390, 100, 2), (440, 50, 2), (260, 70, 2)))
    if kind == "Title":
        body = (
            '<rect width="480" height="360" fill="#1e1b4b"/>' + stars
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#312e81"/>'
            + '<path d="M200 128 L210 100 L225 118 L240 92 L255 118 L270 100 L280 128 Z" fill="#facc15" stroke="#fde68a" stroke-width="3"/>'
            + outlined_text("Arthur's Arena", 240, 70, 50, "#ffffff", "#4c1d95")
            + text_el("LEGENDS OF THE GOLDEN CROWN", 240, 160, 16, "#fde68a")
            + text_el(f"v{VERSION}", 470, 352, 10, "#a5b4fc", anchor="end")
        )
    elif kind == "Select":
        body = (
            '<rect width="480" height="360" fill="#0f172a"/>'
            '<path d="M0 360 L240 120 L480 360 Z" fill="#1e293b"/>'
            + outlined_text("CHOOSE YOUR FIGHTER", 240, 44, 30, "#facc15")
        )
    elif kind == "Yard":
        body = (
            '<rect width="480" height="360" fill="#bae6fd"/>'
            '<rect x="20" y="120" width="440" height="140" fill="#a16207" opacity="0.25"/>'
            + "".join(f'<rect x="{x}" y="150" width="10" height="110" fill="#92400e"/>' for x in range(30, 470, 48))
            + '<rect x="20" y="160" width="440" height="8" fill="#92400e"/><rect x="20" y="200" width="440" height="8" fill="#92400e"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#ca8a04"/><rect y="{g}" width="480" height="6" fill="#a16207"/>'
        )
    elif kind == "Woods":
        trees = "".join(
            f'<rect x="{x + 14}" y="120" width="14" height="{g - 120}" fill="#78350f"/>'
            f'<circle cx="{x + 21}" cy="110" r="44" fill="#166534"/><circle cx="{x + 4}" cy="140" r="30" fill="#15803d"/>'
            for x in (0, 120, 260, 400)
        )
        body = (
            '<rect width="480" height="360" fill="#dcfce7"/>' + trees
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#4d7c0f"/><rect y="{g}" width="480" height="6" fill="#365314"/>'
        )
    elif kind == "Pass":
        body = (
            '<rect width="480" height="360" fill="#fed7aa"/>'
            '<path d="M0 260 L80 120 L160 230 L250 80 L350 220 L420 130 L480 200 L480 360 L0 360 Z" fill="#a8a29e"/>'
            '<path d="M230 110 L250 80 L270 110 Z" fill="#ffffff"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#78716c"/><rect y="{g}" width="480" height="6" fill="#57534e"/>'
        )
    elif kind == "Factory":
        def gear(cx, cy, r, fill):
            teeth = "".join(
                f'<rect x="{cx - 5}" y="{cy - r - 8}" width="10" height="12" fill="{fill}" transform="rotate({a} {cx} {cy})"/>'
                for a in range(0, 360, 45))
            return teeth + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/><circle cx="{cx}" cy="{cy}" r="{r / 3:.0f}" fill="#334155"/>'
        body = (
            '<rect width="480" height="360" fill="#475569"/>'
            '<rect x="0" y="40" width="480" height="14" fill="#334155"/><rect x="0" y="100" width="480" height="10" fill="#334155"/>'
            + gear(80, 120, 40, "#64748b") + gear(150, 80, 26, "#94a3b8") + gear(400, 130, 46, "#64748b")
            + '<rect x="250" y="60" width="16" height="200" fill="#1e293b"/><rect x="250" y="60" width="120" height="16" fill="#1e293b"/>'
            + '<circle cx="310" cy="160" r="12" fill="#ef4444"/><circle cx="310" cy="160" r="5" fill="#fecaca"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#1f2937"/>'
            + "".join(f'<path d="M{x} {g} l20 0 l-14 14 l-20 0 Z" fill="#facc15"/>' for x in range(0, 500, 40))
        )
    elif kind == "Fortress":
        wall_spikes = "".join(f'<polygon points="{x},{y} {x + 14},{y} {x + 7},{y - 26}" fill="#d6d3d1" stroke="#1c1917" stroke-width="2"/>'
                              for x in range(0, 480, 24) for y in (110,))
        body = (
            '<rect width="480" height="360" fill="#450a0a"/>'
            '<circle cx="380" cy="60" r="34" fill="#f87171" opacity="0.5"/>'
            '<rect x="0" y="110" width="480" height="150" fill="#292524"/>' + wall_spikes
            + "".join(f'<rect x="{x}" y="140" width="40" height="70" rx="4" fill="#1c1917"/>' for x in (40, 150, 290, 400))
            + "".join(f'<circle cx="{x + 20}" cy="160" r="6" fill="#ef4444"/>' for x in (40, 150, 290, 400))
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#1c1917"/>'
            + "".join(f'<polygon points="{x},{g} {x + 10},{g} {x + 5},{g - 10}" fill="#78716c"/>' for x in range(0, 480, 30))
        )
    elif kind == "Bamboo":
        stalks = "".join(
            f'<rect x="{x}" y="0" width="{w}" height="{g}" fill="{c}"/>'
            + "".join(f'<rect x="{x - 1}" y="{y}" width="{w + 2}" height="4" fill="#14532d"/>' for y in range(30, g, 55))
            + f'<path d="M{x + w} {g - 120} q24 -10 34 4 q-20 2 -34 -4 Z" fill="#22c55e"/>'
            for x, w, c in ((20, 16, "#4d7c0f"), (70, 12, "#65a30d"), (130, 18, "#3f6212"), (300, 14, "#4d7c0f"),
                            (350, 20, "#365314"), (420, 12, "#65a30d")))
        body = (
            '<rect width="480" height="360" fill="#14532d"/><circle cx="240" cy="90" r="50" fill="#fef9c3" opacity="0.85"/>'
            + stalks + f'<rect y="{g}" width="480" height="{360 - g}" fill="#3f3f12"/><rect y="{g}" width="480" height="5" fill="#1a2e05"/>'
        )
    elif kind == "Dojo":
        screens = "".join(f'<rect x="{x}" y="70" width="70" height="{g - 70}" fill="#fef3c7" stroke="#78350f" stroke-width="5"/>'
                          f'<line x1="{x + 35}" y1="70" x2="{x + 35}" y2="{g}" stroke="#78350f" stroke-width="3"/>'
                          f'<line x1="{x}" y1="140" x2="{x + 70}" y2="140" stroke="#78350f" stroke-width="3"/>'
                          for x in (10, 100, 310, 400))
        body = (
            '<rect width="480" height="360" fill="#7c2d12"/><rect y="0" width="480" height="60" fill="#451a03"/>' + screens
            + '<rect x="190" y="70" width="100" height="120" fill="#dc2626"/><circle cx="240" cy="120" r="26" fill="#fef3c7"/>'
            + '<path d="M228 110 l24 0 M240 104 l0 34 M230 130 l20 0" stroke="#111827" stroke-width="5"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#a16207"/>'
            + "".join(f'<line x1="0" y1="{y}" x2="480" y2="{y}" stroke="#854d0e" stroke-width="2"/>' for y in (g + 20, g + 45, g + 75))
        )
    elif kind == "Volcano":
        body = (
            '<rect width="480" height="360" fill="#7f1d1d"/>'
            '<path d="M120 260 L210 70 L270 70 L360 260 Z" fill="#451a03"/>'
            '<path d="M210 70 L270 70 L255 100 L240 85 L225 100 Z" fill="#f97316"/>'
            '<circle cx="230" cy="40" r="14" fill="#57534e" opacity="0.7"/><circle cx="252" cy="22" r="18" fill="#57534e" opacity="0.6"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#292524"/>'
            + f'<path d="M0 {g + 30} Q120 {g + 10} 240 {g + 36} T480 {g + 26}" stroke="#f97316" stroke-width="5" fill="none"/>'
        )
    elif kind == "Castle":
        body = (
            '<rect width="480" height="360" fill="#1e1b4b"/>' + stars
            + '<rect x="90" y="90" width="300" height="170" fill="#312e81"/>'
            + "".join(f'<rect x="{x}" y="70" width="30" height="30" fill="#312e81"/>' for x in range(90, 390, 60))
            + '<rect x="200" y="150" width="80" height="110" rx="40" fill="#0f172a"/>'
            + '<circle cx="140" cy="140" r="10" fill="#a855f7"/><circle cx="340" cy="140" r="10" fill="#a855f7"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#3b0764"/><rect y="{g}" width="480" height="6" fill="#a855f7"/>'
        )
    elif kind == "Arcade":
        grid = "".join(f'<line x1="{240 + (x - 240) * 3}" y1="360" x2="240" y2="{g}" stroke="#ec4899" stroke-width="2"/>' for x in range(0, 481, 60))
        grid += "".join(f'<line x1="0" y1="{y}" x2="480" y2="{y}" stroke="#ec4899" stroke-width="2"/>' for y in (g + 12, g + 32, g + 62))
        body = (
            '<rect width="480" height="360" fill="#020617"/>'
            '<circle cx="240" cy="200" r="90" fill="#f472b6" opacity="0.5"/>'
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#1e1b4b"/>' + grid
            + outlined_text("ARCADE", 240, 120, 26, "#22d3ee", "#0f172a")
        )
    elif kind == "Ending":
        rays = "".join(
            f'<path d="M240 150 L{240 + 400 * math.cos(a):.0f} {150 + 400 * math.sin(a):.0f} L{240 + 400 * math.cos(a + 0.2):.0f} {150 + 400 * math.sin(a + 0.2):.0f} Z" fill="#fde68a"/>'
            for a in [k * 0.4 for k in range(16)]
        )
        body = (
            '<rect width="480" height="360" fill="#fbbf24"/>' + rays
            + f'<rect y="{g}" width="480" height="{360 - g}" fill="#b45309"/>'
            + outlined_text("CHAMPION!", 240, 64, 46, "#ffffff", "#92400e")
        )
    else:
        raise ValueError(kind)
    return svg_doc(480, 360, body)


def robot_svg(pose, mega=False):
    """Spike Bot: a box robot on treads, facing right. Spikes come out to attack.
    mega=True is MEGA SPIKE: dark armor, a spike crown, and spikes that never fully go in."""
    spikes = pose in ("attack", "windup")
    eye = "#ef4444" if spikes else ("#f97316" if mega else "#22d3ee")
    parts = []
    if pose == "attack":
        parts.append('<ellipse cx="50" cy="110" rx="48" ry="62" fill="#ef4444" opacity="0.25"/>')
    spike_pts = []
    long_ = 16 if pose == "attack" else (9 if spikes else 4)
    if mega:
        long_ += 5
    for y in (96, 116, 136):
        spike_pts.append(f"24,{y - 6} {24 - long_},{y} 24,{y + 6}")
        spike_pts.append(f"76,{y - 6} {76 + long_},{y} 76,{y + 6}")
    for x in (38, 50, 62):
        spike_pts.append(f"{x - 6},50 {x},{50 - long_} {x + 6},50")
    if mega:  # spiked shoulders and a big spike crown
        spike_pts += ["22,88 8,74 30,84", "78,88 92,74 70,84", "34,48 28,22 42,46", "66,48 72,22 58,46", "44,46 50,10 56,46"]
    spike_svg = "".join(f'<polygon points="{pt}" fill="{"#fca5a5" if mega and spikes else "#e5e7eb"}" stroke="#1f2937" '
                        'stroke-width="2.5" stroke-linejoin="round"/>' for pt in spike_pts)
    arm = ('<rect x="70" y="100" width="26" height="9" rx="4" fill="#64748b" stroke="#1f2937" stroke-width="2.5"/>'
           if pose == "attack" else
           '<rect x="72" y="96" width="9" height="28" rx="4" fill="#64748b" stroke="#1f2937" stroke-width="2.5"/>')
    face = (f'<path d="M50 62 l8 8 m0 -8 l-8 8 M60 62 l8 8 m0 -8 l-8 8" stroke="#1f2937" stroke-width="3"/>'
            if pose == "down" else f'<rect x="46" y="60" width="26" height="13" rx="5" fill="{eye}" stroke="#1f2937" stroke-width="2"/>'
            '<rect x="50" y="63" width="8" height="4" rx="2" fill="#ffffff" opacity="0.8"/>')
    bot = (
        spike_svg
        + '<rect x="16" y="146" width="68" height="22" rx="11" fill="#334155" stroke="#0f172a" stroke-width="3"/>'
        + "".join(f'<circle cx="{x}" cy="157" r="6.5" fill="#94a3b8" stroke="#0f172a" stroke-width="2"/>' for x in (28, 50, 72))
        + f'<rect x="24" y="86" width="52" height="62" rx="10" fill="{"#57534e" if mega else "#94a3b8"}" stroke="#1f2937" stroke-width="4"/>'
        + '<g><rect x="33" y="112" width="34" height="18" rx="3" fill="#facc15" stroke="#1f2937" stroke-width="2"/>'
        + "".join(f'<path d="M{x} 112 l8 0 l-8 18 l-8 0 Z" fill="#1f2937"/>' for x in (39, 51, 63)) + '</g>'
        + arm
        + '<line x1="50" y1="50" x2="50" y2="34" stroke="#1f2937" stroke-width="3"/>'
        + f'<circle cx="50" cy="30" r="5.5" fill="{eye}" stroke="#1f2937" stroke-width="2"/>'
        + f'<rect x="30" y="48" width="42" height="38" rx="12" fill="{"#78716c" if mega else "#cbd5e1"}" stroke="#1f2937" stroke-width="4"/>'
        + face
    )
    if pose == "hurt":
        bot = f'<g transform="rotate(-10 50 160)">{bot}</g><path d="M78 60 l8 -8 l-2 8 l8 -4" stroke="#facc15" stroke-width="3" fill="none"/>'
    elif pose == "down":
        bot = (f'<g transform="translate(-2 74) rotate(-90 50 100) scale(0.95)">{bot}</g>'
               '<circle cx="70" cy="110" r="8" fill="#94a3b8" opacity="0.6"/><circle cx="80" cy="96" r="10" fill="#94a3b8" opacity="0.45"/>')
    elif pose == "attack":
        bot = f'<g transform="rotate(8 50 160)">{bot}</g>'
    parts.append(bot)
    return svg_doc(100, 180, "".join(parts))


def spike_armor_svg(base_svg):
    """Adds a ring of spikes around a stick figure (the Shadow King's Spike Armor)."""
    pts = []
    for k in range(12):
        a = -math.pi / 2 + k * 2 * math.pi / 12
        cx, cy = 50 + 30 * math.cos(a), 100 + 62 * math.sin(a)
        tx, ty = 50 + 48 * math.cos(a), 100 + 82 * math.sin(a)
        nx, ny = -math.sin(a) * 6, math.cos(a) * 6
        pts.append(f"{cx + nx:.1f},{cy + ny:.1f} {tx:.1f},{ty:.1f} {cx - nx:.1f},{cy - ny:.1f}")
    ring = "".join(f'<polygon points="{p}" fill="#c084fc" stroke="#1e1b4b" stroke-width="2.5" stroke-linejoin="round"/>' for p in pts)
    inner = base_svg[base_svg.index(">") + 1: -len("</svg>")]
    return svg_doc(100, 180, ring + inner)


def falling_spike_svg():
    return svg_doc(30, 64, '<polygon points="4,0 26,0 15,62" fill="#e5e7eb" stroke="#1f2937" stroke-width="3" stroke-linejoin="round"/>'
                           '<rect x="4" y="0" width="22" height="8" fill="#7f1d1d"/>')


def warning_svg():
    return svg_doc(60, 16, '<ellipse cx="30" cy="8" rx="28" ry="7" fill="#ef4444" opacity="0.75" stroke="#7f1d1d" stroke-width="2"/>')


def spike_shot_svg():
    return svg_doc(50, 20, '<polygon points="0,4 36,4 50,10 36,16 0,16" fill="#e5e7eb" stroke="#1f2937" stroke-width="2.5" stroke-linejoin="round"/>'
                           '<rect x="0" y="4" width="10" height="12" fill="#7f1d1d"/>')


INTRO_FIGURES = [
    # who, pose, left edge of the 100x180 box on the page, scale
    ("arthur", "win", 26, 1.1),
    ("nova", "punch", 138, 1.1),
    ("rocko", "kick", 250, 1.1),
    ("ninja", "slash", 356, 1.1),
]
INTRO_FEET = 300  # page y of the feet
PENCIL = "#3f3f46"


def paper_svg():
    lines = "".join(f'<line x1="0" y1="{y}" x2="480" y2="{y}" stroke="#93c5fd" stroke-width="1.5"/>' for y in range(56, 360, 26))
    return svg_doc(480, 360, '<rect width="480" height="360" fill="#fffdf5"/>' + lines
                   + '<line x1="44" y1="0" x2="44" y2="360" stroke="#f87171" stroke-width="2"/>'
                   + "".join(f'<circle cx="18" cy="{y}" r="7" fill="#e5e7eb"/>' for y in (60, 180, 300)))


def pencil_svg():
    """A yellow pencil leaning to the right; its tip (20, 72) is the rotation centre."""
    return svg_doc(70, 78, ('<g transform="rotate(32 20 72)">'
                            '<rect x="14" y="8" width="12" height="46" fill="#facc15" stroke="#a16207" stroke-width="1.5"/>'
                            '<rect x="14" y="2" width="12" height="6" fill="#9ca3af"/><rect x="14" y="-6" width="12" height="8" rx="2" fill="#f472b6"/>'
                            '<path d="M14 54 L20 72 L26 54 Z" fill="#fde68a" stroke="#a16207" stroke-width="1.5"/>'
                            '<path d="M18 66 L20 72 L22 66 Z" fill="#27272a"/></g>'))


def _figure_strokes(pose, ox, scale):
    """Pencil strokes for one figure, in page coordinates, in drawing order."""
    j = SKEL[pose]
    oy = INTRO_FEET - 168 * scale

    def pt(xy):
        return (ox + xy[0] * scale, oy + xy[1] * scale)

    hx, hy = pt(j["h"])
    r = 16 * scale
    head = [(hx + r * math.cos(a), hy + r * math.sin(a)) for a in [k * 2 * math.pi / 24 for k in range(25)]]
    return [head, [pt(j["n"]), pt(j["c"]), pt(j["p"])], [pt(j["n"]), pt(j["ne"]), pt(j["nh"])],
            [pt(j["n"]), pt(j["fe"]), pt(j["fh"])], [pt(j["p"]), pt(j["nk"]), pt(j["nf"])],
            [pt(j["p"]), pt(j["fk"]), pt(j["ff"])]]


def _partial(points, t):
    """The first t (0..1) of a polyline, and where the pencil tip is."""
    segs = list(zip(points, points[1:]))
    lengths = [math.dist(a, b) for a, b in segs]
    goal = sum(lengths) * t
    out = [points[0]]
    for (a, b), length in zip(segs, lengths):
        if goal >= length:
            out.append(b)
            goal -= length
        else:
            f = goal / length if length else 0
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            break
    return out, out[-1]


def intro_frames():
    """Frames of the stick figures being drawn, stroke by stroke, then coloured in.
    Returns (svg, pencil tip in stage coordinates or None)."""
    strokes = []
    for _hero, pose, ox, sc in INTRO_FIGURES:
        strokes += _figure_strokes(pose, ox, sc)
    frames = []

    def sketch(done, partial=None):
        body = []
        for pts in done + ([partial] if partial else []):
            path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            body.append(f'<polyline points="{path}" fill="none" stroke="{PENCIL}" stroke-width="4" stroke-linecap="round" '
                        'stroke-linejoin="round" opacity="0.9"/>')
            # a second, lighter line slightly off: it looks hand-drawn
            path2 = " ".join(f"{x + 1.2:.1f},{y - 0.8:.1f}" for x, y in pts)
            body.append(f'<polyline points="{path2}" fill="none" stroke="{PENCIL}" stroke-width="1.4" opacity="0.45"/>')
        return svg_doc(480, 360, "".join(body))

    done = []
    for st in strokes:
        for t in (0.5, 1.0):
            part, tip = _partial(st, t)
            frames.append((sketch(done, part), (round(tip[0] - 240, 1), round(180 - tip[1], 1))))
        done.append(st)
    # colour in, one fighter at a time
    coloured = []
    for hero, pose, ox, sc in INTRO_FIGURES:
        h = next((x for x in HEROES if x["key"] == hero), {"color": "#1f2937", "gear": "ninja"})
        fig = fighter_svg(h["color"], pose, h["gear"])
        inner = fig[fig.index(">") + 1: -len("</svg>")]
        coloured.append(f'<g transform="translate({ox},{INTRO_FEET - 168 * sc}) scale({sc})">{inner}</g>')
        pencil_left = sketch(done)[:-len("</svg>")]
        frames.append((pencil_left + "".join(coloured) + "</svg>", None))
    return frames


def apple_svg():
    return svg_doc(60, 60, ('<circle cx="30" cy="34" r="27" fill="#fde68a" opacity="0.6"/>'
                            '<path d="M30 20 C14 12 6 30 12 44 C18 56 26 52 30 50 C34 52 42 56 48 44 C54 30 46 12 30 20 Z" '
                            'fill="#dc2626" stroke="#7f1d1d" stroke-width="2.5"/>'
                            '<path d="M30 20 Q31 12 35 8" stroke="#78350f" stroke-width="3" fill="none"/>'
                            '<path d="M33 13 Q42 6 46 14 Q38 18 33 13 Z" fill="#22c55e"/>'
                            '<ellipse cx="21" cy="30" rx="4" ry="7" fill="#ffffff" opacity="0.5"/>'))


def help_svg():
    rows = [("◀ ▶  /  joystick", "walk (push up to jump)"), ("JUMP", "jump; tap again to flip"), ("PUNCH", "tap: hit; HOLD: METEOR PUNCH"),
            ("KICK", "HOLD: SKY KICK; tap twice: spin"), ("JUMP + KICK x2", "HELICOPTER KICK"), ("DODGE", "safe for a moment"), ("FIRE (hold)", "charge a fireball, let go"),
            ("SUPER", "when the bar is full"), ("POWER", "your power-level move"), ("Walk over", "weapons and apples")]
    body = ['<rect x="6" y="6" width="428" height="308" rx="22" fill="#fffbeb" stroke="#0f172a" stroke-width="6"/>',
            '<path d="M6 60 L6 28 Q6 6 28 6 L412 6 Q434 6 434 28 L434 60 Z" fill="#2563eb"/>',
            outlined_text("HOW TO PLAY", 220, 47, 30, "#ffffff")]
    y = 88
    for key, what in rows:
        body.append(text_el(key, 150, y, 15, "#7c2d12", anchor="end"))
        body.append(text_el(what, 162, y, 15, "#0f172a", anchor="start", weight=600))
        y += 22
    body.append(text_el("Tap this card to close it.", 220, 300, 12, "#475569"))
    return svg_doc(440, 320, "".join(body))


def speaker_svg(on):
    waves = ('<path d="M30 14 Q38 22 30 30 M34 9 Q46 22 34 35" stroke="#ffffff" stroke-width="3" fill="none" stroke-linecap="round"/>'
             if on else '<path d="M30 14 L42 30 M42 14 L30 30" stroke="#ef4444" stroke-width="4" stroke-linecap="round"/>')
    return svg_doc(48, 44, '<rect x="2" y="2" width="44" height="40" rx="12" fill="#334155" stroke="#ffffff" stroke-width="3"/>'
                           '<path d="M10 17 L17 17 L25 10 L25 34 L17 27 L10 27 Z" fill="#ffffff"/>' + waves)


def shuriken_svg():
    pts = []
    for k in range(8):
        r = 13 if k % 2 == 0 else 4
        a = k * math.pi / 4
        pts.append(f"{14 + r * math.cos(a):.1f},{14 + r * math.sin(a):.1f}")
    return svg_doc(28, 28, f'<polygon points="{" ".join(pts)}" fill="#94a3b8" stroke="#0f172a" stroke-width="2"/>'
                           '<circle cx="14" cy="14" r="3" fill="#0f172a"/>')


def smoke_svg():
    return svg_doc(90, 70, "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e5e7eb" opacity="0.85"/>'
                                   for x, y, r in ((30, 40, 22), (55, 32, 24), (45, 50, 20), (66, 48, 16), (22, 52, 14))))


def swirl_svg(frame):
    """Motion lines whirling round a spinning kick (160 x 60, centre in the middle)."""
    off = 45 * frame
    return svg_doc(160, 60, (
        f'<ellipse cx="80" cy="30" rx="76" ry="20" fill="none" stroke="#ffffff" stroke-width="5" opacity="0.85" '
        f'stroke-linecap="round" stroke-dasharray="70 34" stroke-dashoffset="{off}"/>'
        f'<ellipse cx="80" cy="30" rx="60" ry="13" fill="none" stroke="#7dd3fc" stroke-width="4" opacity="0.9" '
        f'stroke-linecap="round" stroke-dasharray="44 26" stroke-dashoffset="{-off * 0.7}"/>'
        f'<ellipse cx="80" cy="30" rx="40" ry="7" fill="none" stroke="#e0f2fe" stroke-width="3" opacity="0.7" '
        f'stroke-linecap="round" stroke-dasharray="20 18" stroke-dashoffset="{off * 0.5}"/>'
    ))


def power_glow_svg(inner, mid, outer):
    """A blazing ball of power with spiky rays, for a charging fist or foot (80 x 80)."""
    rays = []
    for k in range(10):
        a = k * math.pi / 5
        x1, y1 = 40 + 16 * math.cos(a), 40 + 16 * math.sin(a)
        x2, y2 = 40 + 38 * math.cos(a + 0.12), 40 + 38 * math.sin(a + 0.12)
        rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{mid}" stroke-width="3" '
                    f'stroke-linecap="round" opacity="0.8"/>')
    return svg_doc(80, 80, (
        f'<circle cx="40" cy="40" r="30" fill="{outer}" opacity="0.35"/>' + "".join(rays) +
        f'<circle cx="40" cy="40" r="19" fill="{mid}" opacity="0.85"/>'
        f'<circle cx="40" cy="40" r="10" fill="{inner}"/>'
    ))


def crack_svg(level):
    """The ground splitting open under a powering-up fighter (260 x 50, centre in the middle). Bigger each level."""
    rnd_ = __import__("random").Random(level * 7)
    parts = [f'<ellipse cx="130" cy="25" rx="{18 + 8 * level}" ry="{5 + 2 * level}" fill="#1c1917" opacity="0.85"/>']
    for k in range(2 + 2 * level):
        side = -1 if k % 2 else 1
        x, y = 130 + side * (10 + 4 * level), 25 + rnd_.uniform(-3, 3)
        pts = [(x, y)]
        for _ in range(3 + level):
            x += side * rnd_.uniform(10, 14 + 5 * level)
            y += rnd_.uniform(-5, 5)
            pts.append((x, max(4, min(46, y))))
        parts.append('<polyline points="' + " ".join(f"{a:.0f},{b:.0f}" for a, b in pts) + '" fill="none" '
                     f'stroke="#292524" stroke-width="{2 + level * 0.6:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
    for _ in range(3 + 2 * level):
        cx, cy = 130 + rnd_.uniform(-60 - 20 * level, 60 + 20 * level), rnd_.uniform(8, 30)
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rnd_.uniform(5, 9 + level):.0f}" fill="#d6d3d1" opacity="0.55"/>')
    return svg_doc(260, 50, "".join(parts))


def shockwave_svg():
    return svg_doc(220, 60, (
        '<ellipse cx="110" cy="30" rx="104" ry="24" fill="none" stroke="#fef9c3" stroke-width="8" opacity="0.9"/>'
        '<ellipse cx="110" cy="30" rx="96" ry="19" fill="none" stroke="#ffffff" stroke-width="4"/>'
        '<ellipse cx="110" cy="30" rx="86" ry="15" fill="none" stroke="#fde68a" stroke-width="3" opacity="0.6"/>'
    ))


def boulder_svg():
    return svg_doc(60, 52, (
        '<polygon points="6,34 10,14 24,4 42,6 56,20 54,40 40,50 16,48" fill="#57534e" stroke="#292524" stroke-width="3"/>'
        '<polyline points="24,10 28,22 22,32" fill="none" stroke="#292524" stroke-width="2"/>'
        '<polyline points="44,14 38,26 46,36" fill="none" stroke="#292524" stroke-width="2"/>'
        '<polygon points="12,18 22,8 30,12 18,22" fill="#a8a29e" opacity="0.6"/>'
        '<path d="M10 44 Q20 52 30 46 Q40 54 50 44" fill="#78350f" opacity="0.8"/>'
    ))


def shadow_svg():
    return svg_doc(70, 16, '<ellipse cx="35" cy="8" rx="34" ry="7" fill="#000000" opacity="0.35"/>')


def fireball_svg(frame):
    flick = 4 if frame else -4
    return svg_doc(80, 52, (
        f'<path d="M6 26 Q20 {10 + flick} 34 14 Q30 22 44 18 Q40 26 46 34 Q30 32 34 40 Q20 {42 - flick} 6 26 Z" fill="#f97316" opacity="0.85"/>'
        '<circle cx="54" cy="26" r="22" fill="#f97316"/>'
        '<circle cx="57" cy="25" r="15" fill="#facc15"/>'
        '<circle cx="60" cy="24" r="7" fill="#fff7ed"/>'
    ))


def glow_svg():
    return svg_doc(60, 60, (
        '<circle cx="30" cy="30" r="28" fill="#fb923c" opacity="0.35"/>'
        '<circle cx="30" cy="30" r="18" fill="#f97316" opacity="0.8"/>'
        '<circle cx="30" cy="30" r="9" fill="#fef3c7"/>'
    ))


def wave_svg():
    return svg_doc(100, 40, (
        '<ellipse cx="50" cy="26" rx="46" ry="12" fill="#fb923c" stroke="#9a3412" stroke-width="3"/>'
        '<path d="M14 24 Q30 6 50 22 Q70 2 86 24" fill="#fdba74" stroke="#9a3412" stroke-width="3"/>'
    ))


def shot_svg(color="#facc15", ring="#7c3aed"):
    return svg_doc(28, 28, f'<circle cx="14" cy="14" r="10" fill="{color}" stroke="{ring}" stroke-width="4"/>')


def spark_svg():
    pts = []
    for k in range(16):
        r = 30 if k % 2 == 0 else 12
        a = k * math.pi / 8
        pts.append(f"{40 + r * math.cos(a):.1f},{40 + r * math.sin(a):.1f}")
    return svg_doc(80, 80, f'<polygon points="{" ".join(pts)}" fill="#fde047" stroke="#f97316" stroke-width="4"/>')


def crown_svg():
    return svg_doc(44, 30, (
        '<path d="M3 27 L3 7 L13 17 L22 3 L31 17 L41 7 L41 27 Z" fill="#facc15" stroke="#a16207" stroke-width="3"/>'
        '<circle cx="22" cy="20" r="3.5" fill="#dc2626"/>'
    ))


def dot_svg():
    return svg_doc(4, 4, '<rect width="4" height="4" fill="#ffffff" opacity="0"/>')


def floor_svg():
    return svg_doc(480, 10, '<rect width="480" height="10" fill="#000000" opacity="0.18"/>')


# ---------------------------------------------------------------- sound --


def tone_wav(parts, rate=22050):
    """parts: list of (seconds, start_hz, end_hz, kind, volume)."""
    rng = random.Random(7)
    frames = []
    for secs, f0, f1, kind, vol in parts:
        n = int(secs * rate)
        phase = 0.0
        for i in range(n):
            t = i / max(1, n - 1)
            freq = f0 + (f1 - f0) * t
            phase += freq / rate
            env = (1 - t) ** 1.5 * min(1.0, i / 60)
            if kind == "noise":
                s = rng.uniform(-1, 1)
            elif kind == "square":
                s = 1.0 if (phase % 1) < 0.5 else -1.0
            else:
                s = math.sin(2 * math.pi * phase)
            frames.append(int(max(-1, min(1, s * env * vol)) * 32767))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack(f"<{len(frames)}h", *frames))
    return buf.getvalue(), len(frames), rate


SOUNDS = {
    "screech": [(0.12, 1500, 2300, "square", 0.22), (0.2, 2300, 900, "square", 0.22)],
    "honk": [(0.18, 330, 330, "square", 0.3), (0.05, 1, 1, "sine", 0.0), (0.22, 262, 262, "square", 0.3)],
    "hit": [(0.09, 300, 80, "noise", 0.7)],
    "big hit": [(0.05, 500, 200, "noise", 0.9), (0.2, 120, 40, "sine", 0.9)],
    "hurt": [(0.16, 300, 120, "square", 0.35)],
    "ki roar": [(1.4, 70, 340, "square", 0.22), (0.2, 340, 340, "noise", 0.2)],
    "ki flare": [(0.45, 150, 600, "square", 0.2)],
    "transform": [(0.08, 2400, 2400, "sine", 0.5), (0.5, 900, 80, "noise", 0.7)],
    "scribble": [(0.07, 3000, 2200, "noise", 0.18), (0.05, 2600, 2000, "noise", 0.12)],
    "page": [(0.25, 1800, 300, "noise", 0.3)],
    "jump": [(0.12, 300, 700, "square", 0.25)],
    "whirl": [(0.1, 1400, 500, "noise", 0.35), (0.1, 1400, 500, "noise", 0.3), (0.12, 1400, 400, "noise", 0.3)],
    "swing": [(0.12, 900, 300, "noise", 0.35)],
    "pickup": [(0.08, 660, 660, "square", 0.3), (0.12, 990, 990, "square", 0.3)],
    "super": [(0.45, 200, 1200, "square", 0.3)],
    "perfect": [(0.08, 1200, 1200, "sine", 0.5), (0.18, 1600, 1600, "sine", 0.5)],
    "ko": [(0.6, 500, 60, "square", 0.35)],
    "charge": [(0.95, 180, 900, "sine", 0.35)],
    "charged": [(0.07, 1320, 1320, "square", 0.3), (0.07, 1760, 1760, "square", 0.3), (0.16, 2093, 2093, "sine", 0.4)],
    "fireball": [(0.22, 1400, 300, "noise", 0.5)],
    "big fireball": [(0.12, 900, 400, "noise", 0.7), (0.35, 160, 60, "square", 0.45)],
    "boom": [(0.08, 800, 200, "noise", 1.0), (0.45, 90, 30, "noise", 0.9)],
    "spikes": [(0.05, 2400, 2400, "square", 0.3), (0.05, 3000, 3000, "square", 0.3), (0.1, 1800, 1200, "square", 0.25)],
    "clang": [(0.04, 3200, 3200, "square", 0.5), (0.25, 900, 700, "sine", 0.5)],
    "thunder": [(0.06, 3000, 800, "noise", 1.0), (0.6, 120, 40, "noise", 0.7)],
    "power up": [(0.1, 392, 392, "square", 0.3), (0.1, 523, 523, "square", 0.3), (0.1, 659, 659, "square", 0.3),
                 (0.35, 400, 1600, "sine", 0.4)],
    "alarm": [(0.18, 880, 660, "square", 0.3), (0.18, 880, 660, "square", 0.3), (0.18, 880, 660, "square", 0.3)],
    "poof": [(0.18, 900, 200, "noise", 0.45)],
    "shuriken": [(0.12, 2600, 1800, "square", 0.18), (0.08, 2200, 1500, "square", 0.15)],
    "spike fall": [(0.25, 2000, 400, "sine", 0.3)],
    "win": [(0.12, 523, 523, "square", 0.3), (0.12, 659, 659, "square", 0.3), (0.3, 784, 784, "square", 0.3)],
}

# --------------------------------------------------------- expressions --


def V(name):
    return ("var", name)


def add(a, b):
    return ("operator_add", a, b)


def sub(a, b):
    return ("operator_subtract", a, b)


def mul(a, b):
    return ("operator_multiply", a, b)


def div(a, b):
    return ("operator_divide", a, b)


def mod(a, b):
    return ("operator_mod", a, b)


def rnd(a, b):
    return ("operator_random", a, b)


def join(a, b):
    return ("operator_join", a, b)


def item(lst, i):
    return ("item", lst, i)


def listlen(lst):
    return ("listlen", lst)


def round_(a):
    return ("operator_round", a)


def abs_(a):
    return ("mathop", "abs", a)


def floor_(a):
    return ("mathop", "floor", a)


def eq(a, b):
    return ("operator_equals", a, b)


def lt(a, b):
    return ("operator_lt", a, b)


def gt(a, b):
    return ("operator_gt", a, b)


def and_(*xs):
    out = xs[0]
    for x in xs[1:]:
        out = ("operator_and", out, x)
    return out


def or_(*xs):
    out = xs[0]
    for x in xs[1:]:
        out = ("operator_or", out, x)
    return out


def not_(a):
    return ("operator_not", a)


XPOS = ("motion_xposition",)
COSTUME = ("costume_name",)


def contains(a, b):
    return ("operator_contains", a, b)
YPOS = ("motion_yposition",)
TIMER = ("sensing_timer",)
MOUSE_DOWN = ("sensing_mousedown",)
SIZE = ("looks_size",)

BOOL_OPS = {"operator_equals", "operator_lt", "operator_gt", "operator_and", "operator_or", "operator_not", "sensing_mousedown",
            "operator_contains",
            "keypressed"}
BINARY = {
    "operator_add": ("NUM1", "NUM2", "num"),
    "operator_subtract": ("NUM1", "NUM2", "num"),
    "operator_multiply": ("NUM1", "NUM2", "num"),
    "operator_divide": ("NUM1", "NUM2", "num"),
    "operator_mod": ("NUM1", "NUM2", "num"),
    "operator_random": ("FROM", "TO", "num"),
    "operator_join": ("STRING1", "STRING2", "text"),
    "operator_contains": ("STRING1", "STRING2", "text"),
    "operator_equals": ("OPERAND1", "OPERAND2", "text"),
    "operator_lt": ("OPERAND1", "OPERAND2", "text"),
    "operator_gt": ("OPERAND1", "OPERAND2", "text"),
    "operator_and": ("OPERAND1", "OPERAND2", "bool"),
    "operator_or": ("OPERAND1", "OPERAND2", "bool"),
}


# ------------------------------------------------------------- builder --


class Game:
    def __init__(self):
        self.globals: dict[str, tuple[str, object]] = {}
        self.broadcasts: dict[str, str] = {}
        self.targets: list[Target] = []

    def var(self, name, value=0):
        self.globals[name] = ("var_" + name.replace(" ", "_"), value)

    def list(self, name, values=None):
        if not hasattr(self, "lists"):
            self.lists = {}
            self.list_values = {}
        self.lists[name] = "list_" + name.replace(" ", "_")
        if values is not None:
            self.list_values[name] = values

    def msg(self, name):
        if name not in self.broadcasts:
            self.broadcasts[name] = "msg_" + name.replace(" ", "_")
        return name

    def sprite(self, name, **kw):
        t = Target(self, name, **kw)
        self.targets.append(t)
        return t

    def get(self, name):
        return next(t for t in self.targets if t.name == name)


class Target:
    def __init__(self, game, name, is_stage=False, x=0, y=0, size=100, visible=False, rotation="left-right", layer_note=""):
        self.game = game
        self.name = name
        self.is_stage = is_stage
        self.x, self.y, self.size, self.visible = x, y, size, visible
        self.rotation = rotation
        self.locals: dict[str, tuple[str, object]] = {}
        self.blocks: dict[str, dict] = {}
        self.comments: dict[str, dict] = {}
        self.costumes: list[dict] = []
        self.sounds: list[dict] = []
        self.assets: dict[str, bytes] = {}
        self.n = 0
        self.hat_y = 0
        self.prefix = "".join(ch for ch in name if ch.isalnum())[:6] + "_"

    # -- assets
    def costume(self, name, svg, cx, cy):
        data = svg.encode("utf-8")
        digest = hashlib.md5(data).hexdigest()
        self.assets[f"{digest}.svg"] = data
        self.costumes.append(dict(name=name, bitmapResolution=1, dataFormat="svg", assetId=digest,
                                  md5ext=f"{digest}.svg", rotationCenterX=cx, rotationCenterY=cy))

    def sound(self, name):
        data, count, rate = tone_wav(SOUNDS[name])
        digest = hashlib.md5(data).hexdigest()
        self.assets[f"{digest}.wav"] = data
        self.sounds.append(dict(name=name, assetId=digest, dataFormat="wav", format="", rate=rate,
                                sampleCount=count, md5ext=f"{digest}.wav"))

    def local(self, name, value=0):
        # "loc_" keeps sprite-only ids apart from the shared "var_" ids (Hero's "Look" vs the global "Hero Look")
        self.locals[name] = (f"loc_{self.prefix}{name.replace(' ', '_')}", value)

    def lookup_list(self, name):
        lists = getattr(self.game, "lists", {})
        if name not in lists:
            raise KeyError(f"{self.name}: no list {name!r}")
        return lists[name]

    def list_add(self, name, value):
        return self.blk("data_addtolist", {"ITEM": ("text", value)}, {"LIST": [name, self.lookup_list(name)]})

    def list_clear(self, name):
        return self.blk("data_deletealloflist", fields={"LIST": [name, self.lookup_list(name)]})

    def list_delete(self, name, index):
        return self.blk("data_deleteoflist", {"INDEX": ("int", index)}, {"LIST": [name, self.lookup_list(name)]})

    def list_set(self, name, index, value):
        return self.blk("data_replaceitemoflist", {"INDEX": ("int", index), "ITEM": ("text", value)},
                        {"LIST": [name, self.lookup_list(name)]})

    def lookup(self, name):
        if name in self.locals:
            return self.locals[name][0]
        if name in self.game.globals:
            return self.game.globals[name][0]
        raise KeyError(f"{self.name}: no variable {name!r}")

    # -- raw blocks
    def blk(self, opcode, inputs=None, fields=None, shadow=False, mutation=None, top=False):
        self.n += 1
        bid = f"{self.prefix}{self.n}"
        block = {"opcode": opcode, "next": None, "parent": None, "inputs": {}, "fields": fields or {},
                 "shadow": shadow, "topLevel": top}
        if top:
            block["x"], block["y"] = 0, self.hat_y
            self.hat_y += 600
        if mutation is not None:
            block["mutation"] = mutation
        self.blocks[bid] = block
        for key, value in (inputs or {}).items():
            self.set_input(bid, key, value)
        return bid

    def set_input(self, bid, key, value):
        """value is (kind, expr) or a ready-made list."""
        if isinstance(value, list):
            self.blocks[bid]["inputs"][key] = value
            for item in value[1:]:
                if isinstance(item, str) and item in self.blocks:
                    self.blocks[item]["parent"] = bid
            return
        kind, expr = value
        self.blocks[bid]["inputs"][key] = self.compile(expr, kind, bid)

    def compile(self, e, kind, parent):
        prim = {"num": 4, "pos": 5, "int": 7, "angle": 8, "text": 10}
        if kind == "bool":
            bid = self.reporter(e, parent)
            return [2, bid]
        if isinstance(e, bool):
            raise TypeError("use eq() for booleans")
        if isinstance(e, (int, float)):
            if isinstance(e, float) and e.is_integer():
                e = int(e)
            code = prim["text"] if kind == "text" else prim.get(kind, 4)
            return [1, [code, str(e)]]
        if isinstance(e, str):
            return [1, [prim["text"] if kind == "text" else prim.get(kind, 4), e]]
        shadow = [10, ""] if kind == "text" else [prim.get(kind, 4), "0"]
        if e[0] == "var":
            return [3, [12, e[1], self.lookup(e[1])], shadow]
        bid = self.reporter(e, parent)
        if e[0] in BOOL_OPS:
            return [3, bid, shadow]
        return [3, bid, shadow]

    def reporter(self, e, parent):
        op = e[0]
        if op == "var":
            raise TypeError("a variable cannot fill a boolean slot")
        if op in BINARY:
            k1, k2, kind = BINARY[op]
            bid = self.blk(op)
            self.set_input(bid, k1, (kind, e[1]))
            self.set_input(bid, k2, (kind, e[2]))
        elif op == "operator_not":
            bid = self.blk(op)
            self.set_input(bid, "OPERAND", ("bool", e[1]))
        elif op == "operator_round":
            bid = self.blk(op)
            self.set_input(bid, "NUM", ("num", e[1]))
        elif op == "mathop":
            bid = self.blk("operator_mathop", fields={"OPERATOR": [e[1], None]})
            self.set_input(bid, "NUM", ("num", e[2]))
        elif op == "of":
            bid = self.blk("sensing_of", fields={"PROPERTY": [e[1], None]})
            menu = self.blk("sensing_of_object_menu", fields={"OBJECT": [e[2], None]}, shadow=True)
            self.set_input(bid, "OBJECT", [1, menu])
        elif op == "costume_name":
            bid = self.blk("looks_costumenumbername", fields={"NUMBER_NAME": ["name", None]})
        elif op == "item":
            bid = self.blk("data_itemoflist", fields={"LIST": [e[1], self.lookup_list(e[1])]})
            self.set_input(bid, "INDEX", ("int", e[2]))
        elif op == "listlen":
            bid = self.blk("data_lengthoflist", fields={"LIST": [e[1], self.lookup_list(e[1])]})
        elif op == "keypressed":
            bid = self.blk("sensing_keypressed")
            menu = self.blk("sensing_keyoptions", fields={"KEY_OPTION": [e[1], None]}, shadow=True)
            self.set_input(bid, "KEY_OPTION", [1, menu])
        elif op in ("motion_xposition", "motion_yposition", "sensing_timer", "sensing_mousedown", "looks_size"):
            bid = self.blk(op)
        else:
            raise ValueError(op)
        self.blocks[bid]["parent"] = parent
        return bid

    # -- scripts
    def chain(self, ids):
        # a step may be a list of blocks (a helper that makes several); it is spliced in place
        flat = []
        for i in ids:
            flat.extend(i if isinstance(i, list) else [i])
        ids = [i for i in flat if i]
        for left, right in zip(ids, ids[1:]):
            self.blocks[left]["next"] = right
            self.blocks[right]["parent"] = left
        return ids[0] if ids else None

    def script(self, hat, body, note=None):
        first = self.chain(body)
        if first:
            self.blocks[hat]["next"] = first
            self.blocks[first]["parent"] = hat
        if note:
            cid = f"{self.prefix}note{len(self.comments) + 1}"
            self.comments[cid] = dict(blockId=hat, x=520, y=self.blocks[hat]["y"], width=300, height=120,
                                      minimized=False, text=note)
            self.blocks[hat]["comment"] = cid
        return hat

    def on_flag(self, *body, note=None):
        return self.script(self.blk("event_whenflagclicked", top=True), list(body), note)

    def on_msg(self, name, *body, note=None):
        self.game.msg(name)
        hat = self.blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": [name, self.game.broadcasts[name]]}, top=True)
        return self.script(hat, list(body), note)

    def on_click(self, *body, note=None):
        return self.script(self.blk("event_whenthisspriteclicked", top=True), list(body), note)

    def on_stage_click(self, *body, note=None):
        return self.script(self.blk("event_whenstageclicked", top=True), list(body), note)

    def on_key(self, key, *body, note=None):
        return self.script(self.blk("event_whenkeypressed", fields={"KEY_OPTION": [key, None]}, top=True), list(body), note)

    def define(self, name, *body, note=None):
        """A custom block that runs without screen refresh (Scratch's "run without screen refresh").
        Loops inside it finish in one frame instead of pausing a frame on every turn."""
        hat = self.blk("procedures_definition", top=True)
        proto = self.blk("procedures_prototype", shadow=True, mutation={
            "tagName": "mutation", "children": [], "proccode": name, "argumentids": "[]",
            "argumentnames": "[]", "argumentdefaults": "[]", "warp": "true"})
        self.set_input(hat, "custom_block", [1, proto])
        return self.script(hat, list(body), note)

    def call(self, name):
        return self.blk("procedures_call", mutation={"tagName": "mutation", "children": [], "proccode": name,
                                                     "argumentids": "[]", "warp": "true"})

    def on_clone(self, *body, note=None):
        return self.script(self.blk("control_start_as_clone", top=True), list(body), note)

    # -- statements
    def set(self, name, value):
        kind = "text"
        return self.blk("data_setvariableto", {"VALUE": (kind, value)}, {"VARIABLE": [name, self.lookup(name)]})

    def change(self, name, value):
        return self.blk("data_changevariableby", {"VALUE": ("num", value)}, {"VARIABLE": [name, self.lookup(name)]})

    def show_var(self, name):
        return self.blk("data_showvariable", fields={"VARIABLE": [name, self.lookup(name)]})

    def hide_var(self, name):
        return self.blk("data_hidevariable", fields={"VARIABLE": [name, self.lookup(name)]})

    def wait(self, secs):
        return self.blk("control_wait", {"DURATION": ("pos", secs)})

    def wait_until(self, cond):
        return self.blk("control_wait_until", {"CONDITION": ("bool", cond)})

    def _substack(self, bid, key, body):
        first = self.chain(body)
        if first:
            self.blocks[bid]["inputs"][key] = [2, first]
            self.blocks[first]["parent"] = bid

    def if_(self, cond, body, else_body=None):
        bid = self.blk("control_if_else" if else_body else "control_if", {"CONDITION": ("bool", cond)})
        self._substack(bid, "SUBSTACK", body)
        if else_body:
            self._substack(bid, "SUBSTACK2", else_body)
        return bid

    def repeat(self, times, body):
        bid = self.blk("control_repeat", {"TIMES": ("int", times)})
        self._substack(bid, "SUBSTACK", body)
        return bid

    def until(self, cond, body):
        bid = self.blk("control_repeat_until", {"CONDITION": ("bool", cond)})
        self._substack(bid, "SUBSTACK", body)
        return bid

    def forever(self, body):
        bid = self.blk("control_forever")
        self._substack(bid, "SUBSTACK", body)
        return bid

    def stop(self, option="this script"):
        return self.blk("control_stop", fields={"STOP_OPTION": [option, None]},
                        mutation={"tagName": "mutation", "children": [], "hasnext": "true" if option.startswith("other") else "false"})

    def clone(self):
        bid = self.blk("control_create_clone_of")
        menu = self.blk("control_create_clone_of_menu", fields={"CLONE_OPTION": ["_myself_", None]}, shadow=True)
        self.set_input(bid, "CLONE_OPTION", [1, menu])
        return bid

    def delete_clone(self):
        return self.blk("control_delete_this_clone")

    def broadcast(self, name, wait=False):
        self.game.msg(name)
        return self.blk("event_broadcastandwait" if wait else "event_broadcast",
                        {"BROADCAST_INPUT": [1, [11, name, self.game.broadcasts[name]]]})

    def wear(self, name):
        """switch costume to name (text or expression)."""
        bid = self.blk("looks_switchcostumeto")
        default = name if isinstance(name, str) else self.costumes[0]["name"]
        menu = self.blk("looks_costume", fields={"COSTUME": [default, None]}, shadow=True)
        if isinstance(name, str):
            self.set_input(bid, "COSTUME", [1, menu])
        else:
            self.blocks[bid]["inputs"]["COSTUME"] = [3, self.compile(name, "text", bid)[1], menu]
        self.blocks[menu]["parent"] = bid
        return bid

    def backdrop(self, name):
        bid = self.blk("looks_switchbackdropto")
        menu = self.blk("looks_backdrops", fields={"BACKDROP": [name if isinstance(name, str) else "Title", None]}, shadow=True)
        if isinstance(name, str):
            self.set_input(bid, "BACKDROP", [1, menu])
        else:
            self.blocks[bid]["inputs"]["BACKDROP"] = [3, self.compile(name, "text", bid)[1], menu]
        self.blocks[menu]["parent"] = bid
        return bid

    def play(self, name):
        bid = self.blk("sound_play")
        menu = self.blk("sound_sounds_menu", fields={"SOUND_MENU": [name, None]}, shadow=True)
        self.set_input(bid, "SOUND_MENU", [1, menu])
        return bid

    def volume(self, n):
        return self.blk("sound_setvolumeto", {"VOLUME": ("num", n)})

    def stop_sounds(self):
        return self.blk("sound_stopallsounds")

    def say(self, message, secs=None):
        if secs is None:
            return self.blk("looks_say", {"MESSAGE": ("text", message)})
        return self.blk("looks_sayforsecs", {"MESSAGE": ("text", message), "SECS": ("num", secs)})

    def show(self):
        return self.blk("looks_show")

    def hide(self):
        return self.blk("looks_hide")

    def front(self):
        return self.blk("looks_gotofrontback", fields={"FRONT_BACK": ["front", None]})

    def back(self):
        return self.blk("looks_gotofrontback", fields={"FRONT_BACK": ["back", None]})

    def size_to(self, n):
        return self.blk("looks_setsizeto", {"SIZE": ("num", n)})

    def size_by(self, n):
        return self.blk("looks_changesizeby", {"CHANGE": ("num", n)})

    def effect(self, which, n):
        return self.blk("looks_seteffectto", {"VALUE": ("num", n)}, {"EFFECT": [which, None]})

    def effect_by(self, which, n):
        return self.blk("looks_changeeffectby", {"CHANGE": ("num", n)}, {"EFFECT": [which, None]})

    def clear_fx(self):
        return self.blk("looks_cleargraphiceffects")

    def goto(self, x, y):
        return self.blk("motion_gotoxy", {"X": ("num", x), "Y": ("num", y)})

    def glide(self, secs, x, y):
        return self.blk("motion_glidesecstoxy", {"SECS": ("num", secs), "X": ("num", x), "Y": ("num", y)})

    def set_x(self, x):
        return self.blk("motion_setx", {"X": ("num", x)})

    def set_y(self, y):
        return self.blk("motion_sety", {"Y": ("num", y)})

    def dx(self, n):
        return self.blk("motion_changexby", {"DX": ("num", n)})

    def dy(self, n):
        return self.blk("motion_changeyby", {"DY": ("num", n)})

    def move(self, n):
        return self.blk("motion_movesteps", {"STEPS": ("num", n)})

    def point(self, d):
        return self.blk("motion_pointindirection", {"DIRECTION": ("angle", d)})

    def turn(self, d):
        return self.blk("motion_turnright", {"DEGREES": ("num", d)})

    def rotation_style(self, style):
        return self.blk("motion_setrotationstyle", fields={"STYLE": [style, None]})

    def clamp_x(self, lo, hi):
        return [self.if_(lt(XPOS, lo), [self.set_x(lo)]), self.if_(gt(XPOS, hi), [self.set_x(hi)])]

    # -- export
    def export(self, layer):
        variables = {vid: [name, value] for name, (vid, value) in self.locals.items()}
        if self.is_stage:
            variables.update({vid: [name, value] for name, (vid, value) in self.game.globals.items()})
            return {
                "isStage": True, "name": "Stage", "variables": variables,
                "lists": {lid: [name, list(getattr(self.game, "list_values", {}).get(name, []))]
                          for name, lid in getattr(self.game, "lists", {}).items()},
                "broadcasts": {bid: name for name, bid in self.game.broadcasts.items()},
                "blocks": self.blocks, "comments": self.comments, "currentCostume": 0,
                "costumes": self.costumes, "sounds": self.sounds, "volume": 100, "layerOrder": 0,
                "tempo": 60, "videoTransparency": 50, "videoState": "off", "textToSpeechLanguage": None,
            }
        return {
            "isStage": False, "name": self.name, "variables": variables, "lists": {}, "broadcasts": {},
            "blocks": self.blocks, "comments": self.comments, "currentCostume": 0, "costumes": self.costumes,
            "sounds": self.sounds, "volume": 100, "layerOrder": layer, "visible": self.visible,
            "x": self.x, "y": self.y, "size": self.size, "direction": 90, "draggable": False,
            "rotationStyle": self.rotation,
        }


# ---------------------------------------------------------------- game --

FIGHT_HIDE = ("show title", "choose hero", "story scene", "hero down", "enemy down", "ending")


# ------------------------------------------------------------------ brawl --
# Smash-style BRAWL: four fighters, platforms and ramps, a camera that follows
# and zooms, damage %, knockback and ring-outs. Everything lives in "world"
# coordinates; each sprite turns world -> screen with Cam X, Cam Y and Zoom.

BRAWL_SIZE = 45          # fighters are drawn small, like a platform fighter
GRAV = 1.0
JUMP_V = 13.5
DJUMP_V = 12
MAX_FALL = -15
BLAST_X = 560
BLAST_LOW = -360
BLAST_HIGH = 470
STOCKS = 3
BRAWL_KINDS = [
    # key, tag, color, gear, run speed, punch, kick, weight
    dict(key="arthur", tag="ARTHUR", color="#2563eb", gear="headband", speed=3.4, punch=4, kick=7, weight=1.0),
    dict(key="nova", tag="NOVA", color="#c026d3", gear="star", speed=4.4, punch=3, kick=6, weight=0.85),
    dict(key="rocko", tag="ROCKO", color="#15803d", gear="spikes", speed=2.7, punch=5, kick=9, weight=1.3),
    dict(key="rival", tag="RIVAL", color="#64748b", gear="none", speed=3.3, punch=4, kick=7, weight=1.0),
    dict(key="ivy", tag="IVY", color="#7c3aed", gear="leaf", speed=3.6, punch=3, kick=6, weight=0.9),
    dict(key="brute", tag="BRUTE", color="#dc2626", gear="horns", speed=2.6, punch=5, kick=9, weight=1.35),
    dict(key="quake", tag="QUAKE", color="#ea580c", gear="spikes", speed=2.5, punch=5, kick=10, weight=1.4),
    dict(key="shadow", tag="SHADOW KING", color="#1e1b4b", gear="crown", speed=3.5, punch=5, kick=8, weight=1.1),
    dict(key="ninja", tag="NINJA", color="#1f2937", gear="ninja", speed=4.8, punch=4, kick=6, weight=0.8),
]
CPU_POOL = ["rival", "ivy", "brute", "quake", "shadow", "ninja"]
# per level: chance a CPU attacks each frame when in reach, CPU hit power x
BRAWL_AI = [(0.05, 0.75), (0.11, 1.0), (0.2, 1.15), (0.3, 1.3)]
BRAWL_STAGES = [
    # solid = how many of the first platforms are floors you cannot drop through
    dict(key="sky", name="SKY RUINS", sky=("#7dd3fc", "#e0f2fe"), solid=1,
         plats=[(-290, -100, 290, -100), (-235, -10, -105, -10), (105, -10, 235, -10), (-65, 78, 65, 78)]),
    dict(key="ramps", name="RAMP VALLEY", sky=("#fdba74", "#fef3c7"), solid=3,
         plats=[(-340, -150, -135, -65), (-135, -65, 135, -65), (135, -65, 340, -150),
                (-215, 35, -95, 35), (95, 35, 215, 35), (-45, 115, 45, 115)]),
    dict(key="pagoda", name="PAGODA ROOFS", sky=("#0f172a", "#7f1d1d"), solid=1,
         plats=[(-300, -130, 300, -130), (-265, -40, -175, 5), (-175, 5, -85, -40), (85, -40, 175, 5), (175, 5, 265, -40),
                (-45, 85, 45, 85)]),
    # platforms may have a 5th value (bouncy) and a 6th (conveyor push per frame)
    dict(key="pirate", name="PIRATE SHIP", sky=("#38bdf8", "#e0f2fe"), solid=1, hazard="cannon",
         plats=[(-300, -110, 300, -110), (-205, 15, -125, 15), (125, 15, 205, 15), (-50, 105, 50, 105), (190, -55, 300, -55)]),
    dict(key="castle", name="CASTLE WALLS", sky=("#60a5fa", "#dbeafe"), solid=1,
         plats=[(-310, -130, 310, -130), (-290, -25, -180, -25), (180, -25, 290, -25), (-180, -130, -110, -70),
                (-110, 45, 110, 45), (110, -70, 180, -130)]),
    dict(key="space", name="SPACE STATION", sky=("#020617", "#1e1b4b"), solid=2, grav=0.55,
         plats=[(-280, -110, -30, -110), (30, -110, 280, -110), (-25, -30, 25, -30), (-200, 40, -110, 40), (110, 40, 200, 40),
                (-40, 130, 40, 130)]),
    dict(key="snow", name="SNOWY PEAK", sky=("#93c5fd", "#f8fafc"), solid=3, grip=0.07,
         plats=[(-320, -140, -60, -60), (-60, -60, 60, -60), (60, -60, 320, -140), (-230, 30, -120, 30), (120, 30, 230, 30)]),
    dict(key="candy", name="CANDY LAND", sky=("#f9a8d4", "#fdf2f8"), solid=1,
         plats=[(-300, -110, 300, -110), (-255, -45, -195, -45, 1), (195, -45, 255, -45, 1), (-120, 40, -40, 40), (40, 40, 120, 40),
                (-30, 140, 30, 140, 1)]),
    dict(key="factory", name="ROBOT FACTORY", sky=("#475569", "#94a3b8"), solid=3,
         plats=[(-120, -110, 120, -110), (-320, -110, -120, -110, 0, 1.8), (120, -110, 320, -110, 0, -1.8),
                (-220, 10, -80, 10, 0, 1.5), (80, 10, 220, 10, 0, -1.5), (-40, 100, 40, 100)]),
    dict(key="towers", name="TOWER STEPS", sky=("#312e81", "#a5b4fc"), solid=5,
         plats=[(-330, -130, -185, -130), (-185, -130, -95, -60), (-95, -60, 95, -60), (95, -60, 185, -130),
                (185, -130, 330, -130), (-300, 5, -200, 5), (200, 5, 300, 5), (-60, 60, 60, 60)]),
    # from Hermes's themed worlds. A 7th platform value is a picture ("trex", "truck", "raft", "vine");
    # "movers" are platforms that drive back and forth: (platform number, leftmost x1, rightmost x1, speed)
    dict(key="jungle", name="JUNGLE", sky=("#14532d", "#bbf7d0"), solid=1, hazard="coconut",
         plats=[(-300, -110, 300, -110), (-260, -15, -150, -15), (150, -15, 260, -15), (-55, 75, 55, 75),
                (-40, -55, 40, -55, 0, 0, "vine"), (270, -70, 320, -70, 1)],
         movers=[(5, -230, 150, 1.6)]),
    dict(key="dino", name="DINO VALLEY", sky=("#ea580c", "#fde68a"), solid=1, hazard="raptor",
         plats=[(-320, -120, 320, -120), (-80, -40, 70, -40, 0, 0, "trex"), (-290, 45, -185, 45), (185, 45, 290, 45),
                (-45, 120, 45, 120), (150, -72, 260, -72, 0, 0, "trike")],
         movers=[(2, -250, 100, 1.3), (6, -300, 190, -0.9)]),
    dict(key="highway", name="HIGHWAY", sky=("#0284c7", "#e0f2fe"), solid=1, hazard="truck",
         plats=[(-330, -110, 330, -110), (-290, -35, -130, 40), (-130, 40, 130, 40), (130, 40, 290, -35),
                (-60, 72, 50, 72, 0, 0, "truck"), (-300, 125, -210, 125), (210, 125, 300, 125)],
         movers=[(5, -125, 15, 1.2)]),
    dict(key="pond", name="FISHING POND", sky=("#4ade80", "#ecfccb"), solid=2, hazard="fish",
         plats=[(-330, -100, -120, -100), (120, -100, 330, -100), (-50, -118, 50, -118, 0, 0, "raft"),
                (-245, 5, -150, 5), (150, 5, 245, 5), (-75, 85, 75, 85), (-15, -150, 15, -150, 1)],
         movers=[(3, -118, 18, 1.3)]),
]
ART_MARGIN = 72   # room either side of a picture platform for a head, a tail or a cab
THICK = 18
# the controls a second player sends in Wi-Fi play (P2 Joy X and so on), plus their own SUPER and fireball charge
P2_VARS = ("Joy X", "Joy Y", "Want Jump", "Want Drop", "Want Punch", "Want Kick", "Want Super", "Want Power", "Want Dodge",
           "Fire Held", "Super", "Charge", "Power Ready At")


def _mottle(seed, n, xr, yr, color, rx=(2, 5), op=0.35):
    """Seeded random blotches for a natural skin pattern."""
    rnd_ = __import__("random").Random(seed)
    return "".join(f'<ellipse cx="{rnd_.uniform(*xr):.1f}" cy="{rnd_.uniform(*yr):.1f}" rx="{rnd_.uniform(*rx):.1f}" '
                   f'ry="{rnd_.uniform(rx[0] * 0.6, rx[1] * 0.7):.1f}" fill="{color}" opacity="{op}"/>' for _ in range(n))


def trex_svg(w, m, step=False):
    """A realistic Tyrannosaurus from the side, facing right, with a riding saddle.
    Drawn in local units: the flat back runs from x=0 to x=w at y=0 (the platform), the feet stand at y=80."""
    T = 42
    B = w
    ink = "#1b2010"
    defs = ('<defs>'
            '<linearGradient id="rx_skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b4523"/>'
            '<stop offset="0.45" stop-color="#5f6b37"/><stop offset="0.8" stop-color="#9a9461"/><stop offset="1" stop-color="#d3c79c"/></linearGradient>'
            '<linearGradient id="rx_leg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4d5830"/>'
            '<stop offset="1" stop-color="#2c331a"/></linearGradient>'
            '<linearGradient id="rx_shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#000" stop-opacity="0.35"/></linearGradient>'
            '<radialGradient id="rx_eye" cx="0.4" cy="0.4" r="0.6"><stop offset="0" stop-color="#fde68a"/>'
            '<stop offset="1" stop-color="#c2410c"/></radialGradient>'
            '<clipPath id="rx_clip"><path id="rx_body_clip" d="BODY"/></clipPath></defs>')
    body_d = (f'M-62 20 C-42 9 -16 1 4 0 L{B - 20} 0 C{B - 12} -1 {B - 6} -6 {B - 2} -15 '
              f'C{B + 2} -24 {B + 8} -32 {B + 18} -35 C{B + 32} -40 {B + 50} -37 {B + 60} -30 '
              f'C{B + 65} -27 {B + 66} -21 {B + 63} -16 L{B + 36} -12 L{B + 60} -8 '
              f'C{B + 58} -3 {B + 48} 1 {B + 32} 1 C{B + 22} 2 {B + 14} 5 {B + 8} 12 '
              f'C{B + 2} 20 {B - 2} 28 {B - 12} 34 C{B - 24} 42 {B - 44} 45 {B - 62} 45 '
              f'C{B - 84} 45 {B - 104} 41 {B - 112} 35 C{B - 126} 30 -14 26 -62 23 Z')
    defs = defs.replace("BODY", body_d)

    def leg(hx, ang, dark):
        """Thigh, knee, long shin, ankle, then a three-toed foot flat on the ground."""
        fill = "#2c331a" if dark else "url(#rx_leg)"
        return (f'<g transform="rotate({ang} {hx} 10)">'
                # the huge thigh muscle
                f'<path d="M{hx - 18} 4 C{hx - 28} 26 {hx - 14} 46 {hx + 6} 46 C{hx + 20} 46 {hx + 26} 36 {hx + 22} 22 '
                f'C{hx + 18} 8 {hx + 4} 0 {hx - 18} 4 Z" fill="{fill}" stroke="{ink}" stroke-width="2"/>'
                f'<path d="M{hx - 10} 14 C{hx - 12} 26 {hx - 4} 36 {hx + 8} 40" stroke="{ink}" stroke-width="1" fill="none" opacity="0.5"/>'
                # shin down and back to the ankle, then the long foot bones forward to the toes
                f'<path d="M{hx} 40 L{hx + 14} 42 L{hx + 2} 66 L{hx + 12} 78 L{hx - 2} 79 L{hx - 10} 66 Z" fill="{fill}" '
                f'stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>'
                f'</g>')

    def foot(hx, ang, dark):
        # the foot is drawn level so it always stands on the ground, under where the leg ends
        import math as _m
        fx = hx + 4 + 70 * _m.sin(_m.radians(-ang))
        col = "#2c331a" if dark else "#3f4826"
        return (f'<path d="M{fx - 8} 80 L{fx + 22} 80 Q{fx + 27} 79 {fx + 24} 76 L{fx + 8} 73 L{fx - 4} 74 Z" fill="{col}" stroke="{ink}" stroke-width="1.8"/>'
                + "".join(f'<path d="M{fx + c} 80 q4 -1 5 -4 l-6 1 Z" fill="#e7e5e4" stroke="#44403c" stroke-width=".7"/>' for c in (8, 15, 22)))
    # long stride, then a shorter one: both legs always show
    near, far = (2, -3) if step else (11, -11)
    teeth = "".join(f'<path d="M{B + x} -12.5 l1.6 4.5 l1.6 -4.5 Z" fill="#f5f5f0" stroke="#a8a29e" stroke-width=".4"/>' for x in range(38, 62, 4))
    teeth += "".join(f'<path d="M{B + x} -7.5 l1.5 -3.8 l1.5 3.8 Z" fill="#f5f5f0" stroke="#a8a29e" stroke-width=".4"/>' for x in range(40, 58, 4))
    art = (
        defs
        + leg(86, far, True) + foot(86, far, True)
        + f'<path d="{body_d}" fill="url(#rx_skin)"/>'
        # skin pattern, shadow underneath and the dark open mouth, all kept inside the body outline
        + '<g clip-path="url(#rx_clip)">'
        + _mottle(7, 60, (-50, B + 40), (-30, 22), "#273016", (2, 6), 0.35)
        + "".join(f'<path d="M{x} 0 q-5 11 1 22" stroke="#2a3317" stroke-width="5" fill="none" opacity="0.45" stroke-linecap="round"/>'
                  for x in range(-40, B - 10, 16))
        + f'<path d="{body_d}" fill="url(#rx_shade)"/>'
        + f'<path d="M{B + 36} -12 L{B + 64} -16 L{B + 61} -8 Z" fill="#5f1414"/>' + teeth
        + '</g>'
        + f'<path d="{body_d}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linejoin="round"/>'
        # a light edge along the back where the sun catches it
        + f'<path d="M-40 11 C-20 3 0 1 10 1 L{B - 22} 1" stroke="#a3ad6e" stroke-width="1.6" fill="none" opacity="0.7"/>'
        # neck wrinkles
        + "".join(f'<path d="M{B + x} {y} q4 6 2 12" stroke="{ink}" stroke-width="1" fill="none" opacity="0.55"/>'
                  for x, y in ((0, -6), (5, -10), (10, -12)))
        # skull: the big opening in front of the eye, the bony bump over the eye, the eye, nostril and lip line
        + f'<ellipse cx="{B + 44}" cy="-24" rx="8" ry="4" fill="#2f381b" opacity="0.5"/>'
        f'<path d="M{B + 23} -32 Q{B + 28} -38 {B + 34} -33" fill="#56602f" stroke="{ink}" stroke-width="1.6"/>'
        f'<ellipse cx="{B + 29}" cy="-27" rx="3.6" ry="3" fill="url(#rx_eye)" stroke="{ink}" stroke-width="1.2"/>'
        f'<ellipse cx="{B + 29.4}" cy="-27" rx=".9" ry="2.4" fill="#111"/>'
        f'<ellipse cx="{B + 60}" cy="-27" rx="2.2" ry="1.3" fill="{ink}"/>'
        f'<path d="M{B + 20} -14 C{B + 30} -13 {B + 46} -14 {B + 62} -17" stroke="{ink}" stroke-width="1.1" fill="none" opacity="0.7"/>'
        # scutes along the neck and tail
        + "".join(f'<path d="M{x - 2.5:.1f} {y:.1f} l2.5 -3.5 l2.5 3.5 Z" fill="#4a552b" stroke="{ink}" stroke-width=".8"/>'
                  for x, y in ((-50, 15), (-40, 10), (-30, 6), (-20, 3), (B + 2, -18), (B + 8, -27)))
        # the tiny two-fingered arm
        + f'<path d="M{B - 4} 22 Q{B + 6} 26 {B + 9} 33" stroke="#3b4523" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
        f'<path d="M{B + 9} 33 l4 -1 M{B + 9} 33 l2 4" stroke="#e7e5e4" stroke-width="1.6" stroke-linecap="round"/>'
        # near leg in front of the body
        + leg(66, near, False) + foot(66, near, False)
        # riding saddle and girth strap
        + f'<path d="M{B * 0.5:.0f} 1 L{B * 0.5:.0f} 44" stroke="#5b2d0c" stroke-width="5"/>'
        f'<path d="M{B * 0.34:.0f} 3 Q{B * 0.34:.0f} -2 {B * 0.4:.0f} -0.5 L{B * 0.6:.0f} -0.5 Q{B * 0.66:.0f} -3 {B * 0.66:.0f} 3 '
        f'Q{B * 0.5:.0f} 11 {B * 0.34:.0f} 3 Z" fill="#8a3c12" stroke="#3b1a06" stroke-width="1.8"/>'
        f'<path d="M{B * 0.38:.0f} 3 Q{B * 0.5:.0f} 8 {B * 0.62:.0f} 3" stroke="#c2703a" stroke-width="1.2" fill="none"/>'
        f'<rect x="{B * 0.5 - 3:.0f}" y="10" width="6" height="7" rx="1.5" fill="#d4a017" stroke="#5b3d07"/>'
    )
    return f'<g transform="translate({m} {T})">{art}</g>', T


def trike_svg(w, m, step=False):
    """A realistic Triceratops from the side, facing right, with a saddle. Local units: the flat back runs
    from x=0 to x=w at y=0, the feet stand at y=52."""
    T = 46
    B = w
    ink = "#231b12"
    body_d = (f'M-40 22 C-26 9 -10 1 6 0 L{B - 8} 0 C{B + 2} 1 {B + 9} 6 {B + 12} 13 C{B + 15} 22 {B + 12} 30 {B + 4} 33 '
              f'C{B - 14} 42 {B - 50} 44 22 40 C8 38 -14 32 -40 26 Z')
    defs = ('<defs><linearGradient id="tc_skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f4232"/>'
            '<stop offset="0.5" stop-color="#7a6a52"/><stop offset="1" stop-color="#c2b08c"/></linearGradient>'
            '<linearGradient id="tc_shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0.5" stop-color="#000" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#000" stop-opacity="0.35"/></linearGradient>'
            '<radialGradient id="tc_frill" cx="0.35" cy="0.65" r="0.85"><stop offset="0" stop-color="#e2b07a"/>'
            '<stop offset="0.7" stop-color="#a5502a"/><stop offset="1" stop-color="#5e2a14"/></radialGradient>'
            '<linearGradient id="tc_horn" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#8a7d68"/>'
            f'<stop offset="1" stop-color="#f3ecdc"/></linearGradient><clipPath id="tc_clip"><path d="{body_d}"/></clipPath></defs>')

    def leg(x, ang, front, dark):
        fill = "#3a3024" if dark else "#6b5a44"
        top = 8 if front else 4
        w2 = 9 if front else 11
        return (f'<g transform="rotate({ang} {x} {top + 6})">'
                # a heavy muscled upper leg that narrows at the knee, then a stout lower leg and a broad round foot
                f'<path d="M{x - w2 - 3} {top} C{x - w2 - 8} {top + 16} {x - w2 - 1} 31 {x - w2 + 2} 37 '
                f'C{x - w2 + 1} 42 {x - w2 - 1} 48 {x - w2 - 1} 50 Q{x - w2 - 1} 52.5 {x - w2 + 3} 52.5 L{x + w2 + 1} 52.5 '
                f'Q{x + w2 + 4} 52.5 {x + w2 + 3} 49 C{x + w2 + 1} 45 {x + w2 - 1} 41 {x + w2 - 1} 37 '
                f'C{x + w2 + 4} 29 {x + w2 + 6} {top + 8} {x + w2 + 1} {top - 3} Z" fill="{fill}" stroke="{ink}" stroke-width="2"/>'
                f'<path d="M{x - w2} {top + 6} C{x - w2 - 2} {top + 18} {x - 2} 30 {x + 2} 33" stroke="{ink}" stroke-width=".9" fill="none" opacity="0.5"/>'
                f'<path d="M{x - w2 + 2} 38 q{w2} 3 {2 * w2 - 4} 0 M{x - w2 + 1} 43 q{w2} 2 {2 * w2 - 2} 0" stroke="{ink}" stroke-width=".8" fill="none" opacity="0.5"/>'
                + "".join(f'<path d="M{x - w2 + c:.1f} 52.5 q2 -3.5 4 0 Z" fill="#ece6da" stroke="#57534e" stroke-width=".6"/>'
                          for c in (0.5, w2 - 1.5, 2 * w2 - 3.5))
                + '</g>')
    a, b = (6, -6) if step else (-6, 6)
    rim = [(B + 18 + 24 * math.cos(t), -6 + 32 * math.sin(t)) for t in [math.pi * (0.62 + 0.1 * k) for k in range(10)]]
    art = (
        defs
        + leg(22, b, False, True) + leg(B - 14, a, True, True)
        # the great bony frill, its scalloped edge and the knobs round the rim
        + f'<g transform="rotate(-24 {B + 18} -6)">'
          f'<ellipse cx="{B + 18}" cy="-6" rx="24" ry="32" fill="url(#tc_frill)" stroke="{ink}" stroke-width="2.4"/>'
        + "".join(f'<path d="M{x - 3.5:.1f} {y:.1f} l3.5 -5 l3.5 5 Z" fill="#efe3c7" stroke="{ink}" stroke-width=".9" '
                  f'transform="rotate({math.degrees(t) + 90:.0f} {x:.1f} {y:.1f})"/>'
                  for (x, y), t in zip(rim, [math.pi * (0.62 + 0.1 * k) for k in range(10)]))
        + f'<ellipse cx="{B + 16}" cy="-10" rx="11" ry="17" fill="none" stroke="#3b1a0b" stroke-width="2" opacity="0.5"/>'
          f'<path d="M{B + 6} -30 Q{B + 18} -10 {B + 8} 14" stroke="#3b1a0b" stroke-width="1.2" fill="none" opacity="0.5"/></g>'
        # body, with its pattern and shadow kept inside the outline
        + f'<path d="{body_d}" fill="url(#tc_skin)"/>'
        + '<g clip-path="url(#tc_clip)">'
        + _mottle(11, 40, (-30, B), (-2, 24), "#3a2f22", (2, 5), 0.35)
        # big round scales on the flank
        + "".join(f'<circle cx="{x}" cy="{y}" r="2.3" fill="none" stroke="#3a2f22" stroke-width=".8" opacity="0.55"/>'
                  for x in range(0, B, 9) for y in (10, 19, 27) if (x // 9 + y) % 2)
        + "".join(f'<path d="M{x} 0 q-4 9 1 18" stroke="#3a2f22" stroke-width="4" fill="none" opacity="0.4" stroke-linecap="round"/>'
                  for x in range(-24, B - 6, 15))
        + f'<path d="{body_d}" fill="url(#tc_shade)"/></g>'
        + f'<path d="{body_d}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linejoin="round"/>'
        + f'<path d="M-24 13 C-12 4 0 1 8 1 L{B - 8} 1" stroke="#a8977a" stroke-width="1.4" fill="none" opacity="0.7"/>'
        # skin folds at the shoulder
        + "".join(f'<path d="M{B + x} {y} q-3 7 0 14" stroke="{ink}" stroke-width="1" fill="none" opacity="0.5"/>'
                  for x, y in ((-6, 4), (-1, 6), (4, 8)))
        # head: long face, a hooked beak, the eye, a cheek horn
        + f'<path d="M{B + 4} 8 C{B + 12} -1 {B + 30} -4 {B + 42} 4 C{B + 50} 10 {B + 56} 18 {B + 58} 27 '
          f'C{B + 56} 31 {B + 50} 32 {B + 46} 30 C{B + 36} 33 {B + 22} 35 {B + 10} 30 Z" fill="url(#tc_skin)" '
          f'stroke="{ink}" stroke-width="2.4" stroke-linejoin="round"/>'
        f'<path d="M{B + 46} 16 C{B + 52} 18 {B + 57} 22 {B + 58} 27 C{B + 56} 31 {B + 50} 32 {B + 46} 30 Z" fill="#3f342a"/>'
        f'<path d="M{B + 14} 26 L{B + 9} 32 L{B + 18} 29 Z" fill="url(#tc_horn)" stroke="{ink}" stroke-width="1"/>'
        f'<circle cx="{B + 28}" cy="12" r="4" fill="#3b3024"/><circle cx="{B + 28}" cy="12" r="2.4" fill="#1c1410"/>'
        f'<circle cx="{B + 28.8}" cy="11.2" r=".8" fill="#fff"/>'
        f'<path d="M{B + 18} 22 Q{B + 32} 27 {B + 46} 24" stroke="{ink}" stroke-width="1" fill="none" opacity="0.7"/>'
        # the two long brow horns (the far one darker) and the short nose horn
        + f'<path d="M{B + 20} 6 C{B + 30} -8 {B + 44} -20 {B + 62} -30 C{B + 50} -16 {B + 38} -4 {B + 30} 8 Z" fill="#9c907a" stroke="{ink}" stroke-width="1.4"/>'
        f'<path d="M{B + 25} 7 C{B + 36} -6 {B + 50} -16 {B + 68} -24 C{B + 54} -12 {B + 42} 0 {B + 34} 9 Z" fill="url(#tc_horn)" stroke="{ink}" stroke-width="1.4"/>'
        f'<path d="M{B + 44} 15 L{B + 50} 2 L{B + 52} 17 Z" fill="url(#tc_horn)" stroke="{ink}" stroke-width="1.2"/>'
        # near legs in front
        + leg(10, a, False, False) + leg(B - 24, b, True, False)
        # saddle and strap
        + f'<path d="M{B * 0.45:.0f} 1 L{B * 0.45:.0f} 38" stroke="#5b2d0c" stroke-width="5"/>'
        f'<path d="M{B * 0.28:.0f} 3 Q{B * 0.28:.0f} -2 {B * 0.35:.0f} -0.5 L{B * 0.55:.0f} -0.5 Q{B * 0.62:.0f} -3 {B * 0.62:.0f} 3 '
        f'Q{B * 0.45:.0f} 11 {B * 0.28:.0f} 3 Z" fill="#8a3c12" stroke="#3b1a06" stroke-width="1.8"/>'
        f'<rect x="{B * 0.45 - 3:.0f}" y="10" width="6" height="7" rx="1.5" fill="#d4a017" stroke="#5b3d07"/>'
    )
    return f'<g transform="translate({m} {T})">{art}</g>', T


def raptor_svg(step=False):
    """A feathered dromaeosaur sprinting to the right (110 x 72, feet at y=70)."""
    ink = "#24160a"
    body_d = ('M3 24 C18 22 32 20 44 20 C56 15 66 15 72 19 C77 14 81 9 87 8 C95 6 103 8 107 12 '
              'C109 14 107 16 104 17 L92 17.5 L103 19.5 C100 22.5 92 22.5 86 22 C82 24 80 28 76 32 '
              'C70 40 58 42 48 40 C40 38 34 33 26 31 C18 29.5 10 28.5 3 27.5 Z')

    def leg(ang, dark, lift):
        fill = "#5b3a1e" if dark else "#8a6236"
        return (f'<g transform="rotate({ang} 46 30)">'
                # feathered thigh, then shin, then the long foot bones and toes with the sickle claw held up
                f'<path d="M37 27 C33 40 42 48 53 46 C60 41 59 31 51 26 Z" fill="{fill}" stroke="{ink}" stroke-width="1.5"/>'
                + "".join(f'<path d="M{x} {y} q2 4 0 7" stroke="{ink}" stroke-width=".8" fill="none" opacity="0.5"/>' for x, y in ((41, 32), (46, 34), (51, 33)))
                + f'<path d="M51 44 L46 {57 - lift} L{52} {68 - lift} L{64} {69 - lift}" stroke="{ink}" stroke-width="6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
                f'<path d="M51 44 L46 {57 - lift} L{52} {68 - lift} L{64} {69 - lift}" stroke="{fill}" stroke-width="3.6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
                f'<path d="M53 {67 - lift} q-2 -6 3 -8" stroke="#f5f5f4" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
                '</g>')
    near, far = (-24, 22) if step else (22, -24)
    art = (
        '<defs><linearGradient id="rp_skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b3f1b"/>'
        '<stop offset="0.6" stop-color="#a77744"/><stop offset="1" stop-color="#e3cfa6"/></linearGradient>'
        f'<clipPath id="rp_clip"><path d="{body_d}"/></clipPath></defs>'
        + leg(far, True, 6 if not step else 0)
        # tail feather fan
        + "".join(f'<path d="M10 26 L{-2 + d} {26 + e} L{6 + d} {27 + e * 0.6:.0f} Z" fill="#8a2f12" stroke="{ink}" stroke-width=".7"/>'
                  for d, e in ((0, -6), (1, -2), (0, 2), (2, 6)))
        + f'<path d="{body_d}" fill="url(#rp_skin)"/>'
        + '<g clip-path="url(#rp_clip)">'
        # dark stripes and layered feathers along the back and neck
        + "".join(f'<path d="M{x} 18 q-3 7 1 14" stroke="#3e220c" stroke-width="3" fill="none" opacity="0.6" stroke-linecap="round"/>'
                  for x in (22, 30, 38, 46, 54, 62))
        + "".join(f'<path d="M{x} {y} q4 -3 8 0" stroke="#4a2a10" stroke-width="1" fill="none" opacity="0.6"/>'
                  for x in range(24, 80, 6) for y in (21, 25) if (x + y) % 4)
        + '</g>'
        + f'<path d="{body_d}" fill="none" stroke="{ink}" stroke-width="1.8" stroke-linejoin="round"/>'
        # neck ruff of feathers
        + "".join(f'<path d="M{x} {y} l-4 3 l5 1 Z" fill="#9a3412" stroke="{ink}" stroke-width=".5"/>' for x, y in ((76, 16), (80, 12), (84, 9)))
        # head: eye with a dark stripe through it, nostril, teeth
        + '<path d="M86 12 L100 13" stroke="#3e220c" stroke-width="2" opacity="0.6"/>'
          '<circle cx="93" cy="12.5" r="2.2" fill="#facc15" stroke="#1c1917" stroke-width=".9"/><circle cx="93.3" cy="12.5" r=".8" fill="#111"/>'
          '<ellipse cx="104" cy="12" rx="1.2" ry=".8" fill="#24160a"/>'
        + "".join(f'<path d="M{x} 17.5 l1.2 2.6 l1.2 -2.6 Z" fill="#fff"/>' for x in (93, 96, 99, 102))
        # folded feathered arm (like a wing) with claws
        + '<path d="M70 28 Q80 34 79 41 Q70 43 61 37 Q64 31 70 28 Z" fill="#9a3412" stroke="#24160a" stroke-width="1.3"/>'
          + "".join(f'<path d="M{x} {y} l-6 4" stroke="#5c1d08" stroke-width="1" opacity="0.8"/>' for x, y in ((76, 34), (74, 37), (71, 39)))
          + '<path d="M79 41 l4 1 M78 42 l2 3" stroke="#f5f5f4" stroke-width="1.4" stroke-linecap="round"/>'
        + leg(near, False, 0 if not step else 6)
    )
    return svg_doc(110, 72, art)


def art_platform_svg(art, w, left=False, step=False):
    """A platform that is a picture: its flat top is where fighters stand. Returns svg, centre x, centre y."""
    m = ART_MARGIN
    if art == "trex":
        body, top = trex_svg(w, m, step)
        width, height = w + 2 * m, top + 84
    elif art == "trike":
        body, top = trike_svg(w, m, step)
        width, height = w + 2 * m, top + 56
    elif art == "truck":
        top = 8
        body = (
            f'<rect x="{m}" y="{top}" width="{w}" height="14" fill="#f59e0b" stroke="#78350f" stroke-width="3"/>'
            f'<rect x="{m}" y="{top + 14}" width="{w + 6}" height="10" fill="#334155"/>'
            f'<path d="M{m + w + 6} {top + 24} L{m + w + 6} {top - 10} L{m + w + 34} {top - 10} L{m + w + 46} {top + 6} L{m + w + 46} {top + 24} Z" '
            f'fill="#dc2626" stroke="#7f1d1d" stroke-width="3"/>'
            f'<path d="M{m + w + 28} {top - 6} L{m + w + 40} {top + 6} L{m + w + 28} {top + 6} Z" fill="#bae6fd"/>'
            + "".join(f'<circle cx="{m + x}" cy="{top + 26}" r="8" fill="#111827" stroke="#9ca3af" stroke-width="3"/>'
                      for x in (16, w - 16, w + 32))
        )
        width, height = w + 2 * m, top + 36
    elif art == "raft":
        top = 6
        body = ("".join(f'<rect x="{m + x}" y="{top}" width="18" height="16" rx="8" fill="#a16207" stroke="#713f12" stroke-width="2"/>'
                        for x in range(0, w - 8, 17))
                + f'<path d="M{m - 10} {top + 20} q12 -6 24 0 t24 0 t24 0 t24 0 t24 0" stroke="#e0f2fe" stroke-width="3" fill="none"/>'
                + f'<rect x="{m + w / 2 - 2:.0f}" y="{top - 50}" width="4" height="50" fill="#78350f"/>'
                f'<path d="M{m + w / 2 + 2:.0f} {top - 48} L{m + w / 2 + 30:.0f} {top - 14} L{m + w / 2 + 2:.0f} {top - 14} Z" fill="#f8fafc" stroke="#cbd5e1"/>')
        width, height = w + 2 * m, top + 26
    else:  # vine: a log seat hanging from two long vines
        top = 220
        body = (f'<path d="M{m + 8} {top} Q{m - 4} {top / 2:.0f} {m + 14} 0" stroke="#166534" stroke-width="5" fill="none"/>'
                f'<path d="M{m + w - 8} {top} Q{m + w + 4} {top / 2:.0f} {m + w - 14} 0" stroke="#166534" stroke-width="5" fill="none"/>'
                + "".join(f'<ellipse cx="{m + 10 + (k % 2) * (w - 20)}" cy="{30 + 40 * k}" rx="8" ry="4" fill="#22c55e"/>' for k in range(5))
                + f'<rect x="{m}" y="{top}" width="{w}" height="16" rx="8" fill="#92400e" stroke="#451a03" stroke-width="3"/>')
        width, height = w + 2 * m, top + 20
    svg = svg_doc(width, height, body)
    if left:   # face the other way
        inner = svg[svg.index(">") + 1: -len("</svg>")]
        svg = svg_doc(width, height, f'<g transform="translate({width} 0) scale(-1 1)">{inner}</g>')
    return svg, m, top


def platform_svg(stage, x1, y1, x2, y2, bounce=0, push=0):
    w = x2 - x1
    top = max(y1, y2)
    h = abs(y2 - y1) + THICK + 4
    ty1, ty2 = top - y1 + 2, top - y2 + 2
    colors = {"sky": ("#a8a29e", "#57534e", "#86efac"), "ramps": ("#b45309", "#78350f", "#fcd34d"),
              "towers": ("#6366f1", "#312e81", "#c4b5fd"), "pagoda": ("#991b1b", "#450a0a", "#fbbf24"),
              "pirate": ("#92400e", "#451a03", "#fbbf24"), "castle": ("#a8a29e", "#44403c", "#e7e5e4"),
              "space": ("#64748b", "#1e293b", "#22d3ee"), "snow": ("#bae6fd", "#0369a1", "#ffffff"),
              "candy": ("#f472b6", "#9d174d", "#fde68a"), "factory": ("#57534e", "#1c1917", "#facc15"),
              "jungle": ("#78350f", "#3f1d0b", "#4ade80"), "dino": ("#a8a29e", "#57534e", "#84cc16"),
              "highway": ("#475569", "#1e293b", "#fde047"), "pond": ("#a16207", "#713f12", "#d6d3d1")}[stage]
    if bounce:
        colors = ("#a3e635", "#3f6212", "#ecfccb")
    extra = ""
    if bounce:  # a springy pad
        extra = "".join(f'<path d="M{x} {ty1 + 6} l6 6 l6 -6" stroke="#3f6212" stroke-width="2" fill="none"/>' for x in range(4, w - 8, 14))
    if push:    # a conveyor belt with arrows
        arrow = "&gt;" if push > 0 else "&lt;"
        extra = "".join(text_el(arrow.replace("&gt;", ">").replace("&lt;", "<"), x, ty1 + THICK - 3, 14, "#facc15")
                        for x in range(14, w - 6, 26))
    body = (f'<polygon points="0,{ty1} {w},{ty2} {w},{ty2 + THICK} 0,{ty1 + THICK}" fill="{colors[0]}" '
            f'stroke="{colors[1]}" stroke-width="3" stroke-linejoin="round"/>'
            f'<polyline points="0,{ty1 + 1.5} {w},{ty2 + 1.5}" stroke="{colors[2]}" stroke-width="5" fill="none"/>' + extra)
    return svg_doc(w, h, body), ty1


def brawl_sky_svg(stage):
    top, bottom = stage["sky"]
    deco = {
        "sky": "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r * 2}" ry="{r}" fill="#ffffff" opacity="0.8"/>'
                       for x, y, r in ((80, 70, 18), (300, 50, 24), (420, 120, 14), (180, 150, 12))),
        "ramps": '<circle cx="380" cy="80" r="40" fill="#fde047"/>'
                 '<path d="M0 260 L90 170 L190 240 L300 150 L480 250 L480 360 L0 360 Z" fill="#c2410c" opacity="0.45"/>',
        "pagoda": '<circle cx="390" cy="70" r="34" fill="#fef3c7"/>'
                  + "".join(f'<rect x="{x}" y="{y}" width="14" height="20" rx="5" fill="#ef4444"/><rect x="{x + 5}" y="{y - 8}" '
                            f'width="4" height="8" fill="#fbbf24"/>' for x, y in ((60, 60), (150, 90), (300, 50), (440, 120)))
                  + '<path d="M0 300 L120 230 L200 280 L330 210 L480 290 L480 360 L0 360 Z" fill="#1e1b4b" opacity="0.8"/>',
        "pirate": '<circle cx="400" cy="60" r="30" fill="#fde047"/>'
                  '<rect y="250" width="480" height="110" fill="#0369a1"/>'
                  + "".join(f'<path d="M{x} 262 q15 -10 30 0" stroke="#bae6fd" stroke-width="3" fill="none"/>' for x in range(0, 480, 60))
                  + '<rect x="90" y="40" width="10" height="210" fill="#78350f"/><path d="M100 50 L170 90 L100 150 Z" fill="#f5f5f4"/>'
                  '<rect x="380" y="70" width="10" height="180" fill="#78350f"/><path d="M390 80 L440 110 L390 150 Z" fill="#f5f5f4"/>'
                  '<path d="M100 40 l24 8 l-24 8 Z" fill="#111827"/>',
        "castle": '<path d="M0 260 L0 140 L40 140 L40 120 L60 120 L60 140 L100 140 L100 120 L120 120 L120 140 L360 140 L360 120 '
                  'L380 120 L380 140 L420 140 L420 120 L440 120 L440 140 L480 140 L480 260 Z" fill="#78716c" opacity="0.6"/>'
                  '<rect x="200" y="60" width="80" height="120" fill="#78716c" opacity="0.6"/><path d="M190 60 L240 20 L290 60 Z" fill="#b91c1c"/>'
                  '<path d="M240 20 L240 0 L262 8 L240 14" fill="#facc15"/>',
        "space": "".join(f'<circle cx="{(k * 97) % 480}" cy="{(k * 53) % 360}" r="{1 + k % 2}" fill="#ffffff"/>' for k in range(40))
                 + '<circle cx="380" cy="90" r="46" fill="#7c3aed"/><ellipse cx="380" cy="90" rx="74" ry="12" fill="none" stroke="#c4b5fd" stroke-width="5"/>'
                   '<circle cx="80" cy="280" r="60" fill="#0ea5e9" opacity="0.6"/>',
        "snow": '<path d="M0 250 L100 120 L170 200 L260 70 L360 190 L430 110 L480 160 L480 360 L0 360 Z" fill="#cbd5e1"/>'
                '<path d="M230 110 L260 70 L290 110 Z M80 145 L100 120 L120 145 Z" fill="#ffffff"/>'
                + "".join(f'<circle cx="{(k * 71) % 480}" cy="{(k * 37) % 300}" r="2.5" fill="#ffffff"/>' for k in range(30)),
        "candy": "".join(f'<ellipse cx="{x}" cy="{y}" rx="40" ry="16" fill="#ffffff" opacity="0.85"/>' for x, y in ((80, 60), (330, 40), (430, 110)))
                 + "".join(f'<rect x="{x - 3}" y="170" width="6" height="90" fill="#f5f5f4"/><circle cx="{x}" cy="160" r="26" fill="{c}"/>'
                           f'<path d="M{x - 18} 160 Q{x} 140 {x + 18} 160 Q{x} 180 {x - 18} 160" stroke="#ffffff" stroke-width="4" fill="none"/>'
                           for x, c in ((60, "#f43f5e"), (240, "#8b5cf6"), (420, "#14b8a6"))),
        "factory": '<rect x="0" y="40" width="480" height="14" fill="#334155"/>'
                   + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#64748b"/><circle cx="{x}" cy="{y}" r="{r // 3}" fill="#334155"/>'
                             for x, y, r in ((70, 130, 40), (400, 110, 50), (250, 70, 24)))
                   + '<rect x="200" y="90" width="18" height="170" fill="#1e293b"/><circle cx="310" cy="170" r="10" fill="#ef4444"/>',
        "towers": "".join(f'<circle cx="{x}" cy="{y}" r="2" fill="#ffffff"/>' for x, y in ((40, 40), (130, 80), (260, 30), (390, 60), (450, 140)))
                  + '<circle cx="90" cy="70" r="26" fill="#e0e7ff"/>',
        # far trees (pale), near trees (dark) and hanging vines: layers of depth
        "jungle": "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.8:.0f}" fill="#4ade80" opacity="0.5"/>'
                          for x, y, r in ((40, 150, 60), (160, 120, 70), (300, 140, 60), (430, 120, 70)))
                  + "".join(f'<rect x="{x}" y="0" width="22" height="360" fill="#3f1d0b"/><ellipse cx="{x + 11}" cy="20" rx="70" ry="45" fill="#166534"/>'
                            for x in (20, 440))
                  + "".join(f'<path d="M{x} 0 Q{x + 14} 80 {x} {h}" stroke="#15803d" stroke-width="4" fill="none"/>'
                            f'<ellipse cx="{x + 4}" cy="{h}" rx="7" ry="4" fill="#22c55e"/>' for x, h in ((90, 140), (200, 100), (330, 160), (390, 90)))
                  + '<circle cx="250" cy="250" r="10" fill="#f97316"/><path d="M243 246 l-10 -6 M257 246 l10 -6" stroke="#f97316" stroke-width="3"/>',
        "dino": '<circle cx="380" cy="70" r="36" fill="#fef08a"/>'
                '<path d="M0 260 L70 170 L120 210 L190 120 L230 150 L250 80 L280 150 L330 200 L400 140 L480 220 L480 360 L0 360 Z" fill="#7c2d12" opacity="0.7"/>'
                '<path d="M240 85 L250 80 L262 88 Q256 60 250 40 Q246 60 240 85 Z" fill="#ef4444"/>'
                '<path d="M250 40 Q230 10 260 -10 Q290 10 250 40" fill="#9ca3af" opacity="0.6"/>'
                # a long-necked sauropod walking far away on the plain (hazy, so it looks distant)
                '<g opacity="0.55" fill="#5b3a1e">'
                '<path d="M330 236 Q342 214 372 214 Q392 214 400 226 Q416 222 440 236 Q414 232 400 236 Z"/>'
                '<path d="M352 218 Q338 180 322 156 Q318 150 312 152 Q306 154 310 158 Q326 168 344 220 Z"/>'
                '<rect x="350" y="230" width="7" height="22"/><rect x="364" y="232" width="7" height="20"/>'
                '<rect x="384" y="230" width="7" height="22"/><rect x="396" y="232" width="7" height="20"/></g>'
                # pterosaurs gliding: pointed wings, a crest and a long beak
                + "".join(f'<g transform="translate({x} {y}) scale({k})" fill="#3b1d0e" opacity="0.8">'
                          '<path d="M0 0 Q-14 -10 -34 -4 Q-18 -2 -4 4 Z M0 0 Q14 -12 34 -6 Q18 -2 4 4 Z"/>'
                          '<path d="M-2 2 L10 0 L-2 -2 Z M-1 -1 L-8 -6 L-2 0 Z"/></g>'
                          for x, y, k in ((130, 80, 1.0), (175, 105, 0.6)))
                # cycads and tree ferns in front of the hills
                + "".join(f'<rect x="{x - 3}" y="{232 - h}" width="6" height="{h + 30}" fill="#3f2a14"/>'
                          + "".join(f'<path d="M{x} {232 - h} q{dx} {-14 + abs(dx) // 3} {dx * 2} {6}" stroke="#166534" stroke-width="4" fill="none" stroke-linecap="round"/>'
                                    for dx in (-16, -9, -3, 3, 9, 16))
                          for x, h in ((40, 40), (70, 22), (440, 46), (465, 26))),
        "highway": '<circle cx="80" cy="60" r="30" fill="#fef08a"/>'
                   + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{260 - y}" fill="#94a3b8" opacity="0.7"/>'
                             for x, y, w in ((150, 120, 40), (195, 90, 50), (250, 140, 34), (290, 100, 44), (340, 130, 30)))
                   + '<rect y="255" width="480" height="105" fill="#334155"/>'
                   + "".join(f'<rect x="{x}" y="300" width="34" height="6" fill="#fde047"/>' for x in range(10, 480, 70)),
        "pond": '<circle cx="400" cy="60" r="32" fill="#fef9c3"/>'
                '<ellipse cx="240" cy="300" rx="260" ry="90" fill="#0ea5e9"/>'
                '<ellipse cx="240" cy="290" rx="200" ry="50" fill="#38bdf8"/>'
                + "".join(f'<ellipse cx="{x}" cy="{y}" rx="16" ry="6" fill="#16a34a"/><circle cx="{x + 6}" cy="{y - 3}" r="3" fill="#f9a8d4"/>'
                          for x, y in ((120, 300), (330, 320), (200, 330)))
                + "".join(f'<rect x="{x}" y="220" width="4" height="50" fill="#65a30d"/><ellipse cx="{x + 2}" cy="220" rx="4" ry="11" fill="#78350f"/>'
                          for x in (30, 44, 440, 452)),
    }[stage["key"]]
    body = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient></defs><rect width="480" height="360" fill="url(#g)"/>' + deco)
    return svg_doc(480, 360, body)


def hud_svg(kind, stocks):
    width, height = 104, 34
    dots = "".join(f'<circle cx="{58 + 13 * i}" cy="25" r="5" fill="{kind["color"] if i < stocks else "#334155"}" '
                   'stroke="#ffffff" stroke-width="1.5"/>' for i in range(STOCKS))
    name = kind["tag"] if len(kind["tag"]) <= 7 else kind["tag"].split()[0]
    return svg_doc(width, height, f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" fill="#0f172a" '
                   f'opacity="0.85" stroke="{kind["color"]}" stroke-width="2"/>'
                   + text_el(name, 76, 14, 10, "#ffffff") + dots)


def marker_svg():
    return svg_doc(30, 26, '<path d="M3 2 L27 2 L15 22 Z" fill="#facc15" stroke="#0f172a" stroke-width="2.5"/>'
                   + text_el("P1", 15, 13, 9, "#0f172a"))


def declare_brawl(game):
    for name in ("B SY", "B X", "B Y", "B Dmg", "B Stock", "B Alive", "B Hit", "B KX", "B KY", "B Kind", "B Pool",
                 "Plat X1", "Plat Y1", "Plat X2", "Plat Y2", "Plat Bounce", "Plat Push", "Plat Art",
                 "Mv Id", "Mv Min", "Mv Max", "Mv V"):
        game.list(name)
    for name, value in (("Brawl On", 0), ("Brawl Live", 0), ("Brawl Stage", 0), ("Cam X", 0), ("Cam Y", 0), ("Zoom", 1),
                        ("P1 Screen X", 0), ("P1 Screen Y", 0), ("P1 Screen Size", BRAWL_SIZE), ("Brawl Winner", 0),
                        ("BF X", 0), ("BF Y", 0), ("BF Dir", 1), ("BF Power", 0), ("Plat Count", 0),
                        ("Solid Count", 1), ("Joy Y", 0), ("Want Drop", 0), ("Stage Grav", 1), ("Stage Grip", 0.45),
                        ("Stage Key", ""), ("Stage Pick", 0), ("CB X", 0), ("CB Y", 0), ("CB Dir", 1),
                        ("CB VX", 0), ("CB VY", 0), ("CB G", 0), ("CB W", 24), ("CB Kind", "ball"), ("CB Size", 60),
                        ("P1 %", 0), ("P2 %", 0), ("P3 %", 0), ("P4 %", 0),
                        # Wi-Fi play: fighter 2 is a friend on another phone (Net Players = 2), driven by the P2 controls.
                        # My Slot (1 or 2) only changes what this screen shows: which fighter wears the P1 arrow and aura.
                        ("Net Players", 0), ("P2 Kind", "nova"), ("My Slot", 1), ("BF Owner", 1), ("Bolt From", 1),
                        *[(f"P2 {n}", 0) for n in P2_VARS], ("Stage Names", json.dumps([st["name"] for st in BRAWL_STAGES]))):
        game.var(name, value)


def build_brawl(game, s, button, FIGHT_HIDE_):
    declare_brawl(game)
    for st in BRAWL_STAGES:
        s.costume(f"brawl {st['key']}", brawl_sky_svg(st), 240, 180)
    N = 4

    # ---------------------------------------------------- stage: set up --
    s.local("K", 0)
    s.local("Pick", 0)
    s.local("MI", 0)
    s.define(
        "move platforms",
        s.set("K", 0),
        s.repeat(listlen("Mv Id"), [
            s.change("K", 1), s.set("MI", item("Mv Id", V("K"))),
            s.list_set("Plat X1", V("MI"), add(item("Plat X1", V("MI")), item("Mv V", V("K")))),
            s.list_set("Plat X2", V("MI"), add(item("Plat X2", V("MI")), item("Mv V", V("K")))),
            s.if_(or_(lt(item("Plat X1", V("MI")), item("Mv Min", V("K"))), gt(item("Plat X1", V("MI")), item("Mv Max", V("K")))),
                  [s.list_set("Mv V", V("K"), mul(-1, item("Mv V", V("K"))))]),
            # whoever stands on it rides along (the same push a conveyor belt uses)
            s.list_set("Plat Push", V("MI"), item("Mv V", V("K"))),
        ]),
        note="Moving platforms (the T-Rex, the truck, the raft, the vine swing) drive back and forth.",
    )
    s.on_flag(s.forever([s.if_(and_(eq(V("Brawl Live"), 1), gt(listlen("Mv Id"), 0)), [s.call("move platforms")])]),
              note="Moves the moving platforms once a frame during a BRAWL.")
    load_stage = []
    for i, st in enumerate(BRAWL_STAGES, start=1):
        rows = []
        for pl in st["plats"]:
            x1, y1, x2, y2 = pl[:4]
            bounce = pl[4] if len(pl) > 4 else 0
            push = pl[5] if len(pl) > 5 else 0
            rows += [s.list_add("Plat X1", x1), s.list_add("Plat Y1", y1), s.list_add("Plat X2", x2), s.list_add("Plat Y2", y2),
                     s.list_add("Plat Bounce", bounce), s.list_add("Plat Push", push), s.list_add("Plat Art", 1 if len(pl) > 6 else 0)]
        for idx, lo, hi, speed in st.get("movers", []):
            rows += [s.list_add("Mv Id", idx), s.list_add("Mv Min", lo), s.list_add("Mv Max", hi), s.list_add("Mv V", speed)]
        load_stage.append(s.if_(eq(V("Brawl Stage"), i), [s.backdrop(f"brawl {st['key']}"), *rows,
                                                          s.set("Plat Count", len(st["plats"])), s.set("Solid Count", st["solid"]),
                                                          s.set("Stage Grav", st.get("grav", 1)), s.set("Stage Grip", st.get("grip", 0.45)),
                                                          s.set("Stage Key", st["key"]),
                                                          s.set("Pop Text", st["name"]), s.broadcast("popup")]))
    s.on_msg(
        "brawl start",
        s.set("State", "brawl"), s.set("Brawl On", 0), s.set("Brawl Live", 0), s.set("Fight On", 0),
        s.broadcast("brawl clear", wait=True),
        # the STAGE button picks one; RANDOM (0) picks for you
        s.if_(eq(V("Stage Pick"), 0), [s.set("Brawl Stage", rnd(1, len(BRAWL_STAGES)))], [s.set("Brawl Stage", V("Stage Pick"))]),
        *[s.list_clear(n) for n in ("Plat X1", "Plat Y1", "Plat X2", "Plat Y2", "Plat Bounce", "Plat Push", "Plat Art",
                                    "Mv Id", "Mv Min", "Mv Max", "Mv V", "B X", "B Y", "B Dmg", "B Stock",
                                    "B Alive", "B Hit", "B KX", "B KY", "B Kind", "B Pool")],
        *load_stage,
        *[s.list_add("B Pool", k) for k in CPU_POOL],
        s.list_add("B Kind", V("Hero Name")),
        s.if_(eq(V("Net Players"), 2), [s.list_add("B Kind", V("P2 Kind"))]),
        s.repeat(sub(N - 1, mul(1, eq(V("Net Players"), 2))), [s.set("Pick", rnd(1, listlen("B Pool"))), s.list_add("B Kind", item("B Pool", V("Pick"))),
                         s.list_delete("B Pool", V("Pick"))]),
        s.list_clear("B SY"),
        s.repeat(N, [s.list_add("B SY", -9999), s.list_add("B X", 0), s.list_add("B Y", 0), s.list_add("B Dmg", 0), s.list_add("B Stock", STOCKS),
                     s.list_add("B Alive", 1), s.list_add("B Hit", 0), s.list_add("B KX", 0), s.list_add("B KY", 0)]),
        s.set("Cam X", 0), s.set("Cam Y", 0), s.set("Zoom", 0.8), s.set("Super", 0), s.set("Brawl Winner", 0),
        *[s.set(f"P2 {n}", 0) for n in P2_VARS],
        s.hide_var("Score"), s.hide_var("Wave"), s.hide_var("Best"),
        s.if_(eq(V("Page HUD"), 0), [s.show_var(f"P{i} %") for i in range(1, N + 1)]),
        s.if_(not_(eq(V("State"), "brawl")), [s.stop()]),
        s.set("Brawl Live", 1), s.broadcast("brawl go"),
        s.wait(0.8), s.if_(not_(eq(V("State"), "brawl")), [s.stop()]),
        s.set("Banner", "ready"), s.broadcast("banner"), s.wait(1.1),
        s.if_(not_(eq(V("State"), "brawl")), [s.stop()]),
        s.set("Banner", "fight"), s.broadcast("banner"), s.wait(0.3),
        s.if_(not_(eq(V("State"), "brawl")), [s.stop()]),
        s.set("Want Punch", 0), s.set("Want Kick", 0), s.set("Want Jump", 0), s.set("Want Dodge", 0), s.set("Want Super", 0),
        s.set("Brawl On", 1),
        note="BRAWL: picks the next stage, loads its platforms and ramps into lists, and picks 3 CPU fighters at random. "
             "Each fighter is a clone of Brawler and keeps its own place in the B lists (1 is you).",
    )

    # ---------------------------------------------- stage: camera + rules --
    s.local("Min X", 0)
    s.local("Max X", 0)
    s.local("Min Y", 0)
    s.local("Max Y", 0)
    s.local("Alive", 0)
    s.local("Zoom To", 1)
    s.define(
        "camera frame",
                s.set("Min X", 9999), s.set("Max X", -9999), s.set("Min Y", 9999), s.set("Max Y", -9999), s.set("Alive", 0),
                s.set("K", 0),
                s.repeat(N, [
                    s.change("K", 1),
                    s.if_(eq(item("B Alive", V("K")), 1), [
                        s.change("Alive", 1),
                        s.if_(lt(item("B X", V("K")), V("Min X")), [s.set("Min X", item("B X", V("K")))]),
                        s.if_(gt(item("B X", V("K")), V("Max X")), [s.set("Max X", item("B X", V("K")))]),
                        s.if_(lt(item("B Y", V("K")), V("Min Y")), [s.set("Min Y", item("B Y", V("K")))]),
                        s.if_(gt(item("B Y", V("K")), V("Max Y")), [s.set("Max Y", item("B Y", V("K")))]),
                    ]),
                ]),
                *[s.set(f"P{i} %", join(round_(item("B Dmg", i)), "%")) for i in range(1, N + 1)],
                s.if_(gt(V("Alive"), 0), [
                    # keep the view inside the stage area so the camera never chases a fighter flying off
                    s.if_(lt(V("Min X"), -420), [s.set("Min X", -420)]), s.if_(gt(V("Max X"), 420), [s.set("Max X", 420)]),
                    s.if_(lt(V("Min Y"), -200), [s.set("Min Y", -200)]), s.if_(gt(V("Max Y"), 260), [s.set("Max Y", 260)]),
                    s.set("Zoom To", div(420, add(sub(V("Max X"), V("Min X")), 200))),
                    s.if_(gt(V("Zoom To"), div(250, add(sub(V("Max Y"), V("Min Y")), 190))),
                          [s.set("Zoom To", div(250, add(sub(V("Max Y"), V("Min Y")), 190)))]),
                    s.if_(gt(V("Zoom To"), 1.15), [s.set("Zoom To", 1.15)]),
                    s.if_(lt(V("Zoom To"), 0.5), [s.set("Zoom To", 0.5)]),
                    s.change("Zoom", mul(sub(V("Zoom To"), V("Zoom")), 0.06)),
                    s.change("Cam X", mul(sub(div(add(V("Min X"), V("Max X")), 2), V("Cam X")), 0.1)),
                    s.change("Cam Y", mul(sub(add(div(add(V("Min Y"), V("Max Y")), 2), 35), V("Cam Y")), 0.1)),
                ]),
                s.if_(and_(eq(V("Brawl On"), 1), not_(eq(V("Net Players"), 2)), or_(eq(item("B Alive", 1), 0), lt(V("Alive"), 2))), [
                    s.set("Brawl On", 0),
                    s.if_(eq(item("B Alive", 1), 1), [s.set("Brawl Winner", 1)], [s.set("Brawl Winner", 0)]),
                    s.broadcast("brawl end"),
                ]),
                # Wi-Fi play: friend against friend. As soon as one of them is out of lives the other one wins
                # (or the last fighter standing wins, if the computer fighters knocked both out)
                s.if_(and_(eq(V("Brawl On"), 1), eq(V("Net Players"), 2),
                           or_(eq(item("B Alive", 1), 0), eq(item("B Alive", 2), 0), lt(V("Alive"), 2))), [
                    s.set("Brawl On", 0), s.set("Brawl Winner", 0),
                    s.if_(eq(item("B Alive", 1), 1), [s.set("Brawl Winner", 1)]),
                    s.if_(eq(item("B Alive", 2), 1), [s.set("Brawl Winner", 2)]),
                    s.if_(and_(eq(item("B Alive", 1), 1), eq(item("B Alive", 2), 1)), [s.set("Brawl Winner", 0),
                        s.set("K", 0), s.repeat(N, [s.change("K", 1),
                                                    s.if_(eq(item("B Alive", V("K")), 1), [s.set("Brawl Winner", V("K"))])])]),
                    s.broadcast("brawl end"),
                ]),
    )
    s.on_flag(
        s.forever([
            s.if_(eq(V("Brawl Live"), 1), [s.call("camera frame")]),
        ]),
        note="The camera: finds the box around every fighter still in the game, then slides and zooms to fit it, "
             "like a platform fighter. Also copies everyone's damage into P1 % to P4 %, and ends the match when "
             "you are out or only one fighter is left.",
    )
    s.on_msg(
        "brawl end",
        s.play("ko"), s.set("Banner", "game"), s.broadcast("banner"), s.wait(1.8),
        s.if_(not_(eq(V("State"), "brawl")), [s.stop()]),
        s.if_(eq(V("Brawl Winner"), V("My Slot")), [
            s.play("win"), s.change("Score", mul(1000, V("Difficulty"))),
            s.set("XP Gain", 2), s.broadcast("gain xp"),
            s.if_(gt(V("Score"), V("Best")), [s.set("Best", V("Score"))]),
        ]),
        s.set("Brawl Live", 0), s.set("State", "over"),
        s.broadcast("brawl clear", wait=True),
        *[s.hide_var(f"P{i} %") for i in range(1, N + 1)],
        s.broadcast("game over"),
    )
    s.on_msg("brawl clear", s.set("Fire Held", 0))
    s.on_msg("brawl hit", s.play("hit"))
    s.on_msg("boing", s.play("jump"))
    s.on_msg("cannon fire", s.play("big hit"))
    s.on_msg("honk", s.play("honk"))
    s.on_msg("screech", s.play("screech"))
    s.on_msg("brawl smash", s.play("big hit"))
    s.on_msg("brawl ko", s.play("boom"))
    for m in ("show title", "choose hero"):
        s.on_msg(m, s.set("Brawl Live", 0), s.set("Brawl On", 0), *[s.hide_var(f"P{i} %") for i in range(1, N + 1)])

    # ---------------------------------------------------------- fighters --
    br = game.sprite("Brawler", size=BRAWL_SIZE, rotation="left-right")
    for k in BRAWL_KINDS:
        for pose in ("idle", "punch", "kick", "jump", "hurt", "special", "idle b", "walk 1", "walk 2", "walk 3", "walk 4",
                     "fall", "hurt high", "spin 1", "spin 2", "spin 3", "spin 4"):
            br.costume(f"{k['key']} {pose}", fighter_svg(k["color"], pose, k["gear"], "hurt" if pose == "hurt" else "smile",
                                                         glow="#ef4444" if pose == "special" else None), 50, 168)
        for f in range(4):
            br.costume(f"{k['key']} flip {f + 1}", fighter_svg(k["color"], "tuck", k["gear"], rot=90 * f), 50, 168)
    B = br
    for name, value in (("Is Clone", 0), ("My Id", 0), ("Kind", ""), ("X", 0), ("Y", 0), ("VX", 0), ("VY", 0),
                        ("Ground", 0), ("Was Ground", 0), ("Jumps", 0), ("Stun", 0), ("Atk CD", 0), ("Pose Until", 0),
                        ("Speed", 3), ("Punch", 4), ("Kick", 7), ("Weight", 1), ("Face", 1), ("Inv Until", 0),
                        ("Tgt", 0), ("Think", 0), ("Dir", 0), ("Want Atk", 0), ("Want Hop", 0), ("J", 0),
                        ("Surf", 0), ("NX", 0), ("NY", 0), ("Reach", 50), ("Power", 4), ("KB", 0), ("Move Dir", 0),
                        ("Move Until", 0), ("Smash", 0), ("Dash", 9), ("Flip", 0), ("Spin", 0), ("Whirl", 5),
                        ("Kick At", 0), ("Whirl Ready At", 0), ("Best D", 0), ("D", 0), ("On Plat", 0), ("Drop", 0)):
        B.local(name, value)

    stats = []
    for k in BRAWL_KINDS:
        stats.append(B.if_(eq(V("Kind"), k["key"]), [B.set("Speed", k["speed"]), B.set("Punch", k["punch"]),
                                                    B.set("Kick", k["kick"]), B.set("Weight", k["weight"])]))
    ai_chance = [B.if_(eq(V("Difficulty"), i), [B.set("Think", ch)]) for i, (ch, _p) in enumerate(BRAWL_AI, start=1)]
    def cpu_power():
        return [B.if_(eq(V("Difficulty"), i), [B.set("Power", mul(mul(V("Power"), p), add(1, mul(0.1, sub(V("Power Level"), 1)))))])
                for i, (_c, p) in enumerate(BRAWL_AI, start=1)]

    def pose(name):
        return B.wear(join(V("Kind"), " " + name))

    def attack(reach, base_key, smash=False, both=False):
        """Hit every other fighter in reach in front of me (both=True: on both sides, knocked away from me)."""
        hit = [
            # knockback grows with the target's damage %, like a platform fighter
            B.set("KB", add(add(3, mul(V("Power"), 0.5)), mul(mul(add(item("B Dmg", V("J")), V("Power")), V("Power")), 0.019))),
            B.list_set("B Hit", V("J"), add(item("B Hit", V("J")), V("Power"))),
            *([B.if_(gt(item("B X", V("J")), V("X")), [B.list_set("B KX", V("J"), V("KB"))],
                     [B.list_set("B KX", V("J"), sub(0, V("KB")))])] if both else
              [B.list_set("B KX", V("J"), mul(V("Face"), V("KB")))]),
            B.list_set("B KY", V("J"), add(mul(V("KB"), 0.6), 3)),
            B.if_(eq(V("My Id"), 1), [B.if_(lt(V("Super"), 100), [B.change("Super", 5)]),
                                       B.if_(gt(V("Super"), 100), [B.set("Super", 100)])]),
            B.if_(and_(eq(V("My Id"), 2), eq(V("Net Players"), 2)), [B.if_(lt(V("P2 Super"), 100), [B.change("P2 Super", 5)]),
                                                                     B.if_(gt(V("P2 Super"), 100), [B.set("P2 Super", 100)])]),
            B.broadcast("brawl smash" if smash else "brawl hit"),
        ]
        return [
            B.set("Reach", reach), B.set("Power", V(base_key)),
            *([] if smash else [B.if_(gt(V("My Id"), 1), cpu_power())]),
            B.set("J", 0),
            B.repeat(N, [
                B.change("J", 1),
                B.if_(and_(not_(eq(V("J"), V("My Id"))), eq(item("B Alive", V("J")), 1),
                           lt(abs_(sub(item("B X", V("J")), V("X"))), V("Reach")),
                           lt(abs_(sub(item("B Y", V("J")), V("Y"))), 50),
                           *([] if both else [gt(mul(sub(item("B X", V("J")), V("X")), V("Face")), -12)])), hit),
            ]),
        ]

    on_plat = and_(not_(lt(V("NX"), item("Plat X1", V("J")))), not_(gt(V("NX"), item("Plat X2", V("J")))))
    surf = add(item("Plat Y1", V("J")), mul(sub(V("NX"), item("Plat X1", V("J"))),
                                             div(sub(item("Plat Y2", V("J")), item("Plat Y1", V("J"))),
                                                 sub(item("Plat X2", V("J")), item("Plat X1", V("J"))))))

    def player_input_for(pre):
        """The controls of a player: pre is "" for player 1, "P2 " for a Wi-Fi friend on fighter 2."""
        def P(n):
            return pre + n if n in P2_VARS else n
        return [
            B.if_(gt(abs_(V(P("Joy X"))), 0.2), [B.set("Dir", V(P("Joy X")))],
                  [B.if_(lt(TIMER, V("Move Until")), [B.set("Dir", V("Move Dir"))], [B.set("Dir", 0)])]),
            B.if_(eq(V(P("Want Jump")), 1), [B.set(P("Want Jump"), 0), B.set("Want Hop", 1)]),
            # push the stick down (or the down arrow) to drop through a thin platform
            B.if_(or_(lt(V(P("Joy Y")), -0.6), eq(V(P("Want Drop")), 1)), [B.set(P("Want Drop"), 0), B.if_(and_(eq(V("Ground"), 1), gt(V("On Plat"), V("Solid Count"))), [B.set("Drop", 8), B.set("Ground", 0)])]),
            B.if_(eq(V(P("Want Punch")), 1), [B.set(P("Want Punch"), 0), B.set("Want Atk", 1)]),
            B.if_(eq(V(P("Want Kick")), 1), [
                B.set(P("Want Kick"), 0),
                B.if_(and_(lt(sub(TIMER, V("Kick At")), DOUBLE_TAP), gt(TIMER, V("Whirl Ready At"))),
                      [B.set("Kick At", 0), B.set("Whirl Ready At", add(TIMER, WHIRL_COOLDOWN)), B.set("Want Atk", 5)],
                      [B.set("Kick At", TIMER), B.set("Want Atk", 2)]),
            ]),
            B.if_(eq(V(P("Want Super")), 1), [B.set(P("Want Super"), 0), B.if_(eq(V(P("Super")), 100), [B.set("Want Atk", 3)])]),
            # POWER move: level 2 FLAME DASH, level 3+ lightning on everyone near you
            B.if_(eq(V(P("Want Power")), 1), [
                B.set(P("Want Power"), 0),
                B.if_(and_(gt(V("Power Level"), 1), gt(TIMER, V(P("Power Ready At")))), [
                    B.set(P("Power Ready At"), add(TIMER, POWER_COOLDOWN)), B.broadcast("power flash"),
                    B.if_(eq(V("Power Level"), 2), [B.set("Want Atk", 4)],
                          [B.set("Pop Text", "THUNDER!"), B.broadcast("popup"), B.set("Bolt From", V("My Id")), B.broadcast("brawl bolt")]),
                ]),
            ]),
            B.if_(eq(V(P("Want Dodge")), 1), [B.set(P("Want Dodge"), 0), B.set("Inv Until", add(TIMER, 0.45)),
                                           B.set("VX", mul(V("Face"), -6))]),
            # fireball: hold FIRE, let go to shoot
            B.if_(or_(eq(V(P("Fire Held")), 1), ("keypressed", "f")), [
                B.if_(lt(V(P("Charge")), 100), [B.change(P("Charge"), 3.5)]),
                B.if_(gt(V(P("Charge")), 99), [B.set(P("Charge"), 100)]),
                B.set("Dir", mul(V("Dir"), 0.4)),
            ], [
                B.if_(and_(gt(V(P("Charge")), 0), eq(V("BF Power"), 0)), [
                    B.set("BF X", add(V("X"), mul(20, V("Face")))), B.set("BF Y", add(V("Y"), 40)),
                    B.set("BF Dir", V("Face")), B.set("BF Owner", V("My Id")), B.set("BF Power", add(V(P("Charge")), 1)), B.broadcast("brawl fire"),
                    B.set("Fire Power", V(P("Charge"))), B.broadcast("fire"),
                ]),
                B.set(P("Charge"), 0),
            ]),
        ]
    cpu_input = [
        # pick the closest fighter now and then
        B.if_(or_(eq(V("Tgt"), 0), eq(rnd(1, 20), 1), eq(item("B Alive", V("Tgt")), 0)), [
            B.set("Best D", 99999), B.set("J", 0),
            B.repeat(N, [B.change("J", 1),
                         B.if_(and_(not_(eq(V("J"), V("My Id"))), eq(item("B Alive", V("J")), 1)), [
                             B.set("D", add(abs_(sub(item("B X", V("J")), V("X"))), abs_(sub(item("B Y", V("J")), V("Y"))))),
                             B.if_(lt(V("D"), V("Best D")), [B.set("Best D", V("D")), B.set("Tgt", V("J"))]),
                         ])]),
        ]),
        B.set("Dir", 0),
        # off the stage? head back to the middle and jump
        B.if_(or_(lt(V("X"), -300), gt(V("X"), 300), lt(V("Y"), -150)), [
            B.if_(gt(V("X"), 0), [B.set("Dir", -1)], [B.set("Dir", 1)]),
            B.if_(and_(lt(V("VY"), 0), lt(V("Jumps"), 2)), [B.set("Want Hop", 1)]),
        ], [
            B.if_(gt(V("Tgt"), 0), [
                B.set("D", sub(item("B X", V("Tgt")), V("X"))),
                B.if_(gt(abs_(V("D")), 38), [B.if_(gt(V("D"), 0), [B.set("Dir", 1)], [B.set("Dir", -1)])]),
                # higher up: jump, then double jump while still below
                B.if_(gt(sub(item("B Y", V("Tgt")), V("Y")), 45), [
                    B.if_(and_(eq(V("Ground"), 1), eq(rnd(1, 6), 1)), [B.set("Want Hop", 1)]),
                    B.if_(and_(eq(V("Ground"), 0), eq(V("Jumps"), 1), lt(V("VY"), 1)), [B.set("Want Hop", 1)]),
                ]),
                # lower down: drop through a thin platform
                B.if_(and_(lt(sub(item("B Y", V("Tgt")), V("Y")), -50), eq(rnd(1, 15), 1)), [B.if_(and_(eq(V("Ground"), 1), gt(V("On Plat"), V("Solid Count"))), [B.set("Drop", 8), B.set("Ground", 0)])]),
                B.if_(and_(lt(abs_(V("D")), 48), lt(abs_(sub(item("B Y", V("Tgt")), V("Y"))), 45),
                           lt(rnd("0.0", "1.0"), V("Think"))), [B.set("Want Atk", rnd(1, 2))]),
            ]),
        ]),
    ]

    physics = [
        # 1. take any hits that landed on me
        B.if_(gt(item("B Hit", V("My Id")), 0), [
            B.if_(gt(V("Inv Until"), TIMER), [B.list_set("B Hit", V("My Id"), 0)], [
                B.list_set("B Dmg", V("My Id"), add(item("B Dmg", V("My Id")), item("B Hit", V("My Id")))),
                B.list_set("B Hit", V("My Id"), 0),
                B.set("VX", div(item("B KX", V("My Id")), V("Weight"))),
                B.set("VY", div(item("B KY", V("My Id")), V("Weight"))),
                B.set("Stun", add(8, mul(abs_(V("VX")), 1.6))), B.set("Ground", 0),
                B.if_(gt(V("VY"), 8), [pose("hurt high")], [pose("hurt")]),
                B.effect("BRIGHTNESS", 50),
            ]),
        ]),
        # 2. controls (player buttons or CPU brain); none while knocked back
        B.set("Want Atk", 0), B.set("Want Hop", 0), B.set("Dir", 0),
        B.if_(and_(eq(V("Brawl On"), 1), not_(gt(V("Stun"), 0))),
              [B.if_(eq(V("My Id"), 1), player_input_for(""),
                     [B.if_(and_(eq(V("My Id"), 2), eq(V("Net Players"), 2)), player_input_for("P2 "), cpu_input)])]),
        B.if_(gt(V("Stun"), 0), [B.change("Stun", -1), B.set("VX", mul(V("VX"), 0.96)),
                                 B.if_(lt(V("Stun"), 1), [B.effect("BRIGHTNESS", 0)])], [
            # Stage Grip: 0.45 normally, very low on ice so you slide
            B.if_(eq(V("Ground"), 1), [B.change("VX", mul(sub(mul(V("Dir"), V("Speed")), V("VX")), V("Stage Grip")))],
                  [B.change("VX", mul(sub(mul(V("Dir"), V("Speed")), V("VX")), 0.12))]),
            B.if_(gt(V("Dir"), 0.1), [B.set("Face", 1)]), B.if_(lt(V("Dir"), -0.1), [B.set("Face", -1)]),
        ]),
        B.if_(and_(eq(V("Want Hop"), 1), lt(V("Jumps"), 2)), [
            B.if_(eq(V("Jumps"), 0), [B.set("VY", JUMP_V)], [B.set("VY", DJUMP_V)]),
            B.if_(eq(V("Jumps"), 1), [B.set("Flip", 16)]),
            B.change("Jumps", 1), B.set("Ground", 0), B.broadcast("jump sfx"),
        ]),
        # 3. attacks
        B.if_(gt(V("Atk CD"), 0), [B.change("Atk CD", -1)]),
        B.if_(and_(gt(V("Want Atk"), 0), not_(gt(V("Atk CD"), 0))), [
            B.if_(eq(V("Want Atk"), 1), [pose("punch"), *attack(46, "Punch"), B.set("Atk CD", 9)]),
            B.if_(eq(V("Want Atk"), 2), [pose("kick"), *attack(56, "Kick"), B.set("Atk CD", 16)]),
            B.if_(eq(V("Want Atk"), 3), [pose("special"), B.if_(eq(V("My Id"), 2), [B.set("P2 Super", 0)], [B.set("Super", 0)]), B.set("Smash", 16),
                                         *attack(70, "Smash", smash=True), B.set("Atk CD", 20),
                                         B.set("Pop Text", "SMASH!"), B.broadcast("popup")]),
            B.if_(eq(V("Want Atk"), 4), [pose("special"), B.set("VX", mul(V("Face"), 15)), B.set("Dash", 9),
                                         *attack(64, "Dash", smash=True), B.set("Atk CD", 14),
                                         B.set("Pop Text", "FLAME DASH!"), B.broadcast("popup")]),
            B.if_(eq(V("Want Atk"), 5), [
                B.set("Spin", 15), B.set("VY", 7), B.set("VX", mul(V("Face"), 6)), B.set("Ground", 0), B.set("Whirl", 5),
                *attack(58, "Whirl", both=True), B.set("Atk CD", 18),
                B.set("Pop Text", "WHIRLWIND KICK!"), B.broadcast("popup"), B.broadcast("whirl sfx"),
            ]),
            B.set("Pose Until", add(TIMER, 0.18)),
        ]),
        # the WHIRLWIND KICK keeps spinning and hits again half way
        B.if_(gt(V("Spin"), 0), [
            B.change("Spin", -1), B.set("Pose Until", add(TIMER, 0.05)),
            B.wear(join(V("Kind"), join(" spin ", add(mod(floor_(div(V("Spin"), 2)), 4), 1)))),
            B.if_(eq(V("Spin"), 8), [*attack(58, "Whirl", both=True)]),
        ]),
        # 4. move and land on platforms and ramps
        B.if_(gt(V("Drop"), 0), [B.change("Drop", -1)]),
        B.change("VY", mul(-GRAV, V("Stage Grav"))), B.if_(lt(V("VY"), MAX_FALL), [B.set("VY", MAX_FALL)]),
        B.set("NX", add(V("X"), V("VX"))), B.set("NY", add(V("Y"), V("VY"))),
        B.set("Was Ground", V("Ground")), B.set("Ground", 0),
        B.if_(not_(gt(V("VY"), 0)), [
            B.set("J", 0),
            B.repeat(V("Plat Count"), [
                B.change("J", 1),
                B.if_(and_(eq(V("Ground"), 0), on_plat, or_(not_(gt(V("Drop"), 0)), not_(gt(V("J"), V("Solid Count"))))), [
                    B.set("Surf", surf),
                    # land if I was above it (12 lets you walk up a ramp), or stick to it walking down
                    B.if_(and_(not_(gt(V("NY"), V("Surf"))), not_(lt(add(V("Y"), 12), V("Surf")))),
                          [B.set("NY", V("Surf")), B.set("VY", 0), B.set("Ground", 1), B.set("Jumps", 0), B.set("Flip", 0), B.set("On Plat", V("J"))],
                          [B.if_(and_(eq(V("Was Ground"), 1), gt(V("NY"), V("Surf")), lt(sub(V("NY"), V("Surf")), 10),
                                      not_(gt(V("Stun"), 0))),
                                 [B.set("NY", V("Surf")), B.set("VY", 0), B.set("Ground", 1), B.set("Jumps", 0), B.set("Flip", 0), B.set("On Plat", V("J"))])]),
                ]),
            ]),
        ]),
        B.set("X", V("NX")), B.set("Y", V("NY")),
        B.if_(eq(V("Ground"), 1), [
            # conveyor belts carry you; bouncy pads throw you up
            B.change("X", item("Plat Push", V("On Plat"))),
            B.if_(eq(item("Plat Bounce", V("On Plat")), 1), [
                B.set("VY", 17), B.set("Ground", 0), B.set("Jumps", 1), B.broadcast("boing"),
            ]),
        ]),
        B.list_set("B X", V("My Id"), V("X")), B.list_set("B Y", V("My Id"), V("Y")),
        # 5. flew past the edge of the screen: lose a life
        B.if_(or_(gt(abs_(V("X")), BLAST_X), lt(V("Y"), BLAST_LOW), gt(V("Y"), BLAST_HIGH)), [
            B.set("Pop Text", "K.O.!"),
            B.broadcast("popup"), B.broadcast("brawl ko"),
            B.list_set("B Stock", V("My Id"), sub(item("B Stock", V("My Id")), 1)),
            B.if_(gt(item("B Stock", V("My Id")), 0), [
                B.set("X", rnd(-80, 80)), B.set("Y", 230), B.set("VX", 0), B.set("VY", 0), B.set("Stun", 0),
                B.list_set("B Dmg", V("My Id"), 0), B.set("Inv Until", add(TIMER, 2.5)),
                B.list_set("B X", V("My Id"), V("X")), B.list_set("B Y", V("My Id"), V("Y")),
            ], [
                B.list_set("B Alive", V("My Id"), 0), B.hide(),
            ]),
        ]),
        # 6. draw: world -> screen
        B.if_(and_(gt(TIMER, V("Pose Until")), not_(gt(V("Stun"), 0))), [
            B.if_(eq(V("Ground"), 1), [
                B.if_(gt(abs_(V("VX")), 0.6),
                      [B.wear(join(V("Kind"), join(" walk ", add(floor_(mod(div(add(V("X"), 1000), 13), 4)), 1))))],
                      [B.if_(eq(mod(round_(mul(TIMER, 1.6)), 2), 0), [pose("idle")], [pose("idle b")])]),
            ], [B.if_(gt(V("Flip"), 0),
                      [B.change("Flip", -1),
                       B.wear(join(V("Kind"), join(" flip ", add(floor_(mod(div(sub(16, V("Flip")), 4), 4)), 1))))],
                      [B.if_(gt(V("VY"), 0), [pose("jump")], [pose("fall")])])]),
        ]),
        # shadow: the highest platform under me
        B.set("Surf", -9999), B.set("NX", V("X")), B.set("J", 0),
        B.repeat(V("Plat Count"), [
            B.change("J", 1),
            B.if_(on_plat, [B.set("D", surf),
                            B.if_(and_(not_(gt(V("D"), add(V("Y"), 1))), gt(V("D"), V("Surf"))), [B.set("Surf", V("D"))])]),
        ]),
        B.list_set("B SY", V("My Id"), V("Surf")),
        B.if_(eq(V("Face"), 1), [B.point(90)], [B.point(-90)]),
        B.if_(gt(V("Inv Until"), TIMER), [B.effect("GHOST", mul(40, mod(round_(mul(TIMER, 10)), 2)))], [B.effect("GHOST", 0)]),
        B.size_to(mul(BRAWL_SIZE, V("Zoom"))),
        B.goto(mul(sub(V("X"), V("Cam X")), V("Zoom")), mul(sub(V("Y"), V("Cam Y")), V("Zoom"))),
        B.if_(eq(V("My Id"), V("My Slot")), [B.set("P1 Screen X", XPOS), B.set("P1 Screen Y", YPOS), B.set("P1 Screen Size", SIZE)]),
    ]

    B.define("fighter frame", *physics,
             note="Everything one fighter does in one frame. It is a custom block with \"run without screen refresh\" "
                  "so its loops over fighters and platforms finish in one frame.")
    B.on_flag(B.hide(), B.set("Is Clone", 0))
    B.on_msg(
        "brawl go",
        B.if_(eq(V("Is Clone"), 0), [
            B.set("My Id", 0),
            B.repeat(N, [B.change("My Id", 1), B.clone()]),
        ]),
        note="Makes the four fighters. Clone 1 is you; 2, 3 and 4 are CPU fighters.",
    )
    B.on_clone(
        B.set("Is Clone", 1), B.set("Kind", item("B Kind", V("My Id"))), *stats, *ai_chance,
        B.set("X", sub(mul(V("My Id"), 110), 275)), B.set("Y", 220), B.set("VX", 0), B.set("VY", 0),
        B.set("Face", 1), B.if_(gt(V("X"), 0), [B.set("Face", -1)]), B.set("Smash", 16), B.set("Dash", 9),
        B.set("Stun", 0), B.set("Jumps", 0), B.if_(eq(V("My Id"), 1), [B.set("Charge", 0)]), B.if_(eq(V("My Id"), 2), [B.set("P2 Charge", 0)]), B.clear_fx(), pose("jump"), B.show(), B.front(),
        B.until(eq(V("Brawl Live"), 0), [
            B.if_(eq(item("B Alive", V("My Id")), 1), [B.call("fighter frame")]),
        ]),
        B.delete_clone(),
        note="One fighter, every frame: 1 take hits (damage % goes up, knockback grows with it), 2 controls or the CPU brain, "
             "3 attacks, 4 gravity and landing on platforms and ramps, 5 flying off the screen loses a life, "
             "6 draw it where the camera sees it.",
    )
    for d, sign in (("left", -1), ("right", 1)):
        B.on_msg(f"move {d}", B.if_(and_(eq(V("Is Clone"), 1), eq(V("My Id"), 1)),
                                    [B.set("Move Dir", sign), B.set("Move Until", add(TIMER, 0.16))]))
    for m in ("brawl clear", "show title", "choose hero"):
        B.on_msg(m, B.if_(eq(V("Is Clone"), 1), [B.delete_clone()]))

    # ---------------------------------------------------------- fireball --
    bf = game.sprite("Brawl Fireball", size=40, rotation="left-right")
    bf.costume("flame", fireball_svg(0), 54, 26)
    BF = bf
    BF.local("J", 0)
    BF.local("Done", 0)
    BF.local("Power", 0)
    BF.on_flag(BF.hide(), BF.set("BF Power", 0))
    BF.on_msg(
        "brawl fire",
        BF.set("Power", sub(V("BF Power"), 1)), BF.set("Done", 0), BF.point(mul(90, V("BF Dir"))), BF.show(), BF.front(),
        BF.until(or_(eq(V("Done"), 1), gt(abs_(V("BF X")), BLAST_X), eq(V("Brawl Live"), 0)), [BF.call("fireball frame")]),
        BF.hide(), BF.set("BF Power", 0),
        note="Your fireball in BRAWL. Bigger charge = more damage and more knockback.",
    )
    BF.define(
        "fireball frame",
            BF.change("BF X", mul(add(8, div(V("Power"), 25)), V("BF Dir"))),
            BF.size_to(mul(add(30, mul(V("Power"), 0.7)), V("Zoom"))),
            BF.goto(mul(sub(V("BF X"), V("Cam X")), V("Zoom")), mul(sub(V("BF Y"), V("Cam Y")), V("Zoom"))),
            BF.set("J", 0),
            BF.repeat(N, [
                BF.change("J", 1),
                BF.if_(and_(eq(V("Done"), 0), not_(eq(V("J"), V("BF Owner"))), eq(item("B Alive", V("J")), 1), lt(abs_(sub(item("B X", V("J")), V("BF X"))), 24),
                            lt(abs_(sub(add(item("B Y", V("J")), 38), V("BF Y"))), 44)), [
                    BF.set("Done", 1),
                    BF.list_set("B Hit", V("J"), add(item("B Hit", V("J")), add(3, round_(div(V("Power"), 10))))),
                    BF.list_set("B KX", V("J"), mul(V("BF Dir"), add(4, div(mul(V("Power"), add(item("B Dmg", V("J")), 20)), 500)))),
                    BF.list_set("B KY", V("J"), add(4, div(mul(V("Power"), add(item("B Dmg", V("J")), 20)), 800))),
                    BF.if_(gt(V("Power"), 99), [BF.broadcast("brawl ko")], [BF.broadcast("brawl hit")]),
                ]),
            ]),
    )
    for m in ("brawl clear", "show title"):
        BF.on_msg(m, BF.hide(), BF.set("BF Power", 0))

    # ---------------------------------------------------------- platforms --
    pl = game.sprite("Brawl Platform", size=100, rotation="don't rotate")
    for st in BRAWL_STAGES:
        for i, plat in enumerate(st["plats"], start=1):
            x1, y1, x2, y2 = plat[:4]
            if len(plat) > 6:
                for left in (False, True):
                    for step in (False, True):
                        svg, cx, cy = art_platform_svg(plat[6], x2 - x1, left, step)
                        pl.costume(f"{st['key']} {i}" + (" l" if left else "") + (" s" if step else ""), svg, cx, cy)
                continue
            svg, cy = platform_svg(st["key"], x1, y1, x2, y2, plat[4] if len(plat) > 4 else 0, plat[5] if len(plat) > 5 else 0)
            pl.costume(f"{st['key']} {i}", svg, 0, cy)
    PL = pl
    PL.local("Is Clone", 0)
    PL.local("My Id", 0)
    PL.local("Stage Key", "")
    PL.local("Suf", "")
    keys = [PL.if_(eq(V("Brawl Stage"), i), [PL.set("Stage Key", st["key"])]) for i, st in enumerate(BRAWL_STAGES, start=1)]
    PL.on_flag(PL.hide(), PL.set("Is Clone", 0))
    PL.on_msg("brawl go", PL.if_(eq(V("Is Clone"), 0), [
        *keys, PL.set("My Id", 0), PL.repeat(V("Plat Count"), [PL.change("My Id", 1), PL.clone()]),
    ]))
    PL.on_clone(
        PL.set("Is Clone", 1), PL.wear(join(V("Stage Key"), join(" ", V("My Id")))), PL.show(),
        PL.until(eq(V("Brawl Live"), 0), [
            PL.size_to(mul(100, V("Zoom"))),
            # a T-Rex, truck or raft turns round when it drives the other way
            PL.if_(eq(item("Plat Art", V("My Id")), 1), [
                PL.set("Suf", ""),
                PL.if_(lt(item("Plat Push", V("My Id")), 0), [PL.set("Suf", " l")]),
                # a walking step every fifth of a second (the T-Rex's legs move)
                PL.if_(eq(mod(floor_(mul(TIMER, 5)), 2), 1), [PL.set("Suf", join(V("Suf"), " s"))]),
                PL.wear(join(V("Stage Key"), join(" ", join(V("My Id"), V("Suf"))))),
            ]),
            PL.goto(mul(sub(item("Plat X1", V("My Id")), V("Cam X")), V("Zoom")),
                    mul(sub(item("Plat Y1", V("My Id")), V("Cam Y")), V("Zoom"))),
        ]),
        PL.delete_clone(),
        note="Each platform or ramp is a clone that redraws itself where the camera sees it.",
    )
    for m in ("brawl clear", "show title", "choose hero"):
        PL.on_msg(m, PL.if_(eq(V("Is Clone"), 1), [PL.delete_clone()]))

    # ------------------------------------------------------------- HUD --
    slots = [4, 110, 262, 368]
    hud = game.sprite("Brawl HUD", size=100, rotation="don't rotate")
    for k in BRAWL_KINDS:
        for n in range(STOCKS + 1):
            hud.costume(f"{k['key']} {n}", hud_svg(k, n), 52, 17)
    HD = hud
    HD.local("Is Clone", 0)
    HD.local("My Id", 0)
    HD.on_flag(HD.hide(), HD.set("Is Clone", 0))
    HD.on_msg("brawl go", HD.if_(eq(V("Is Clone"), 0), [
        HD.set("My Id", 0),
        *[x for i, sx in enumerate(slots, start=1) for x in (HD.change("My Id", 1), HD.goto(sx + 52 - 240, 180 - 21), HD.clone())],
    ]))
    HD.on_clone(
        HD.set("Is Clone", 1), HD.show(),
        HD.until(eq(V("Brawl Live"), 0), [
            HD.if_(eq(V("Page HUD"), 1), [HD.hide()], [HD.show()]),
            HD.wear(join(item("B Kind", V("My Id")), join(" ", item("B Stock", V("My Id"))))),
            HD.if_(eq(item("B Alive", V("My Id")), 1), [HD.effect("GHOST", 0)], [HD.effect("GHOST", 60)]),
        ]),
        HD.delete_clone(),
        note="Name and lives (dots) for each fighter. The big number next to it is their damage %.",
    )
    for m in ("brawl clear", "show title", "choose hero"):
        HD.on_msg(m, HD.if_(eq(V("Is Clone"), 1), [HD.delete_clone()]))

    bsh = game.sprite("Brawl Shadow", size=100, rotation="don't rotate")
    bsh.costume("shadow", shadow_svg(), 35, 8)
    BS = bsh
    BS.local("Is Clone", 0)
    BS.local("My Id", 0)
    BS.local("H", 0)
    BS.on_flag(BS.hide(), BS.set("Is Clone", 0))
    BS.on_msg("brawl go", BS.if_(eq(V("Is Clone"), 0), [BS.set("My Id", 0), BS.repeat(N, [BS.change("My Id", 1), BS.clone()])]))
    BS.on_clone(
        BS.set("Is Clone", 1),
        BS.until(eq(V("Brawl Live"), 0), [
            BS.if_(and_(eq(item("B Alive", V("My Id")), 1), gt(item("B SY", V("My Id")), -9000)), [
                BS.set("H", sub(item("B Y", V("My Id")), item("B SY", V("My Id")))),
                BS.size_to(mul(mul(V("Zoom"), 52), sub(1, div(V("H"), 300)))),
                BS.effect("GHOST", add(15, div(V("H"), 3))),
                BS.goto(mul(sub(item("B X", V("My Id")), V("Cam X")), V("Zoom")), mul(sub(item("B SY", V("My Id")), V("Cam Y")), V("Zoom"))),
                BS.show(),
            ], [BS.hide()]),
        ]),
        BS.delete_clone(),
        note="Each fighter's shadow sits on the platform under them, smaller and fainter the higher they jump.",
    )
    for m in ("brawl clear", "show title", "choose hero"):
        BS.on_msg(m, BS.if_(eq(V("Is Clone"), 1), [BS.delete_clone()]))

    cb = game.sprite("Cannonball", size=60, rotation="don't rotate")
    cb.costume("ball", svg_doc(40, 40, '<circle cx="20" cy="20" r="16" fill="#1f2937" stroke="#f97316" stroke-width="3"/>'
                                       '<circle cx="14" cy="14" r="4" fill="#9ca3af"/>'), 20, 20)
    truck = ('<rect x="4" y="6" width="96" height="44" rx="4" fill="#2563eb" stroke="#1e3a8a" stroke-width="3"/>'
             '<path d="M100 50 L100 18 L124 18 L136 34 L136 50 Z" fill="#facc15" stroke="#a16207" stroke-width="3"/>'
             '<path d="M106 22 L120 22 L130 34 L106 34 Z" fill="#bae6fd"/>'
             + "".join(f'<circle cx="{x}" cy="54" r="9" fill="#111827" stroke="#9ca3af" stroke-width="3"/>' for x in (24, 80, 120))
             + '<rect x="134" y="40" width="6" height="6" fill="#fef08a"/>')
    cb.costume("truck", svg_doc(144, 66, truck), 72, 34)
    cb.costume("truck l", svg_doc(144, 66, f'<g transform="translate(144 0) scale(-1 1)">{truck}</g>'), 72, 34)
    cb.costume("coconut", svg_doc(36, 36, '<circle cx="18" cy="18" r="15" fill="#78350f" stroke="#3f1d0b" stroke-width="3"/>'
                                          '<circle cx="13" cy="12" r="2.5" fill="#1c1917"/><circle cx="21" cy="11" r="2.5" fill="#1c1917"/>'
                                          '<circle cx="17" cy="18" r="2.5" fill="#1c1917"/>'), 18, 18)
    cb.costume("fish", svg_doc(60, 40, '<path d="M8 20 Q28 0 48 20 Q28 40 8 20 Z" fill="#f97316" stroke="#9a3412" stroke-width="3"/>'
                                       '<path d="M46 20 L58 8 L58 32 Z" fill="#fb923c" stroke="#9a3412" stroke-width="3"/>'
                                       '<circle cx="18" cy="17" r="3" fill="#111827"/>'
                                       '<path d="M26 12 q4 8 0 16" stroke="#fed7aa" stroke-width="2" fill="none"/>'), 30, 20)
    for left in (False, True):
        for step in (False, True):
            svg = raptor_svg(step)
            if left:
                inner = svg[svg.index(">") + 1: -len("</svg>")]
                svg = svg_doc(110, 72, f'<g transform="translate(110 0) scale(-1 1)">{inner}</g>')
            cb.costume("raptor" + (" l" if left else "") + (" 2" if step else ""), svg, 55, 42)
    CB = cb
    CB.local("Done", 0)
    CB.local("J", 0)
    CB.local("KD", 1)
    CB.define(
        "cannon frame",
        CB.change("CB X", V("CB VX")), CB.change("CB Y", V("CB VY")), CB.change("CB VY", mul(-1, V("CB G"))),
        CB.size_to(mul(V("CB Size"), V("Zoom"))),
        # a raptor runs: swap its legs
        CB.if_(contains(V("CB Kind"), "raptor"), [
            CB.if_(eq(mod(floor_(mul(TIMER, 8)), 2), 0), [CB.wear(V("CB Kind"))], [CB.wear(join(V("CB Kind"), " 2"))]),
        ]),
        CB.goto(mul(sub(V("CB X"), V("Cam X")), V("Zoom")), mul(sub(V("CB Y"), V("Cam Y")), V("Zoom"))),
        CB.set("J", 0),
        CB.repeat(N, [
            CB.change("J", 1),
            CB.if_(and_(eq(V("Done"), 0), eq(item("B Alive", V("J")), 1), lt(abs_(sub(item("B X", V("J")), V("CB X"))), V("CB W")),
                        lt(abs_(sub(add(item("B Y", V("J")), 35), V("CB Y"))), 40)), [
                CB.set("Done", 1),
                # knocked the way it was going (or away from it, for things that fall or jump)
                CB.if_(eq(V("CB VX"), 0), [CB.if_(gt(item("B X", V("J")), V("CB X")), [CB.set("KD", 1)], [CB.set("KD", -1)])],
                       [CB.if_(gt(V("CB VX"), 0), [CB.set("KD", 1)], [CB.set("KD", -1)])]),
                CB.list_set("B Hit", V("J"), add(item("B Hit", V("J")), 12)),
                CB.list_set("B KX", V("J"), mul(V("KD"), add(7, div(item("B Dmg", V("J")), 9)))),
                CB.list_set("B KY", V("J"), add(7, div(item("B Dmg", V("J")), 11))),
                CB.broadcast("brawl ko"),
            ]),
        ]),
    )
    hazard_keys = [st["key"] for st in BRAWL_STAGES if st.get("hazard")]
    has_hazard = or_(*[eq(V("Stage Key"), k) for k in hazard_keys])

    def side():
        return CB.if_(eq(rnd(1, 2), 1), [CB.set("CB Dir", 1)], [CB.set("CB Dir", -1)])

    launch = {
        "pirate": [CB.wait(rnd(6, 10)), side(), CB.set("CB Kind", "ball"), CB.set("CB Size", 60), CB.set("CB W", 24),
                   CB.set("CB X", mul(V("CB Dir"), -520)), CB.set("CB Y", rnd(-85, 40)),
                   CB.set("CB VX", mul(10, V("CB Dir"))), CB.set("CB VY", 0), CB.set("CB G", 0),
                   CB.set("Pop Text", "CANNON!"), CB.broadcast("cannon fire")],
        "highway": [CB.wait(rnd(5, 9)), side(), CB.set("CB Size", 100), CB.set("CB W", 62),
                    CB.if_(eq(V("CB Dir"), 1), [CB.set("CB Kind", "truck")], [CB.set("CB Kind", "truck l")]),
                    CB.set("CB X", mul(V("CB Dir"), -540)), CB.set("CB Y", -78),
                    CB.set("CB VX", mul(9, V("CB Dir"))), CB.set("CB VY", 0), CB.set("CB G", 0),
                    CB.set("Pop Text", "TRUCK! JUMP!"), CB.broadcast("honk")],
        "dino": [CB.wait(rnd(5, 9)), side(), CB.set("CB Size", 100), CB.set("CB W", 36),
                 CB.if_(eq(V("CB Dir"), 1), [CB.set("CB Kind", "raptor")], [CB.set("CB Kind", "raptor l")]),
                 CB.set("CB X", mul(V("CB Dir"), -540)), CB.set("CB Y", -92),
                 CB.set("CB VX", mul(11, V("CB Dir"))), CB.set("CB VY", 0), CB.set("CB G", 0),
                 CB.set("Pop Text", "RAPTOR! JUMP!"), CB.broadcast("screech")],
        "jungle": [CB.wait(rnd(3, 6)), CB.set("CB Kind", "coconut"), CB.set("CB Size", 70), CB.set("CB W", 22),
                   CB.set("CB X", rnd(-270, 270)), CB.set("CB Y", 280), CB.set("CB VX", 0), CB.set("CB VY", -2), CB.set("CB G", 0.6),
                   CB.set("Pop Text", "COCONUT!"), CB.broadcast("whirl sfx")],
        "pond": [CB.wait(rnd(4, 7)), CB.set("CB Kind", "fish"), CB.set("CB Size", 80), CB.set("CB W", 24),
                 CB.set("CB X", rnd(-100, 100)), CB.set("CB Y", -210), CB.set("CB VX", 0), CB.set("CB VY", 16), CB.set("CB G", 0.55),
                 CB.set("Pop Text", "SPLASH!"), CB.broadcast("boing")],
    }
    CB.on_flag(
        CB.hide(),
        CB.forever([
            CB.if_(and_(eq(V("Brawl On"), 1), has_hazard), [
                *[CB.if_(eq(V("Stage Key"), k), launch[k]) for k in hazard_keys],
                CB.if_(and_(eq(V("Brawl On"), 1), has_hazard), [
                    CB.set("Done", 0), CB.wear(V("CB Kind")), CB.broadcast("popup"), CB.show(), CB.front(),
                    CB.until(or_(eq(V("Done"), 1), gt(abs_(V("CB X")), 560), lt(V("CB Y"), -320), eq(V("Brawl Live"), 0)),
                             [CB.call("cannon frame")]),
                    CB.hide(),
                ]),
            ], [CB.wait(0.3)]),
        ]),
        note="Stage hazards: cannonballs on the PIRATE SHIP, trucks on the HIGHWAY, raptors in DINO VALLEY, coconuts in the JUNGLE "
             "and jumping fish at the FISHING POND. Jump out of the way!",
    )
    for m in ("brawl clear", "show title"):
        CB.on_msg(m, CB.hide())

    pick = game.sprite("Stage Button", x=40, y=-162, rotation="don't rotate")
    pick.costume("stage 0", difficulty_svg("RANDOM", "#facc15").replace("LEVEL:", "STAGE:"), 95, 20)
    for i, st in enumerate(BRAWL_STAGES, start=1):
        pick.costume(f"stage {i}", difficulty_svg(st["name"], "#facc15").replace("LEVEL:", "STAGE:")
                     .replace('font-size="15"', 'font-size="12"'), 95, 20)
    PK = pick
    PK.on_flag(PK.hide())
    PK.on_msg("choose hero", PK.if_(eq(V("Mode"), "brawl"), [PK.wear(join("stage ", V("Stage Pick"))), PK.goto(40, -162),
                                                             PK.show(), PK.front()], [PK.hide()]))
    for m in ("hero picked", "show title"):
        PK.on_msg(m, PK.hide())
    PK.on_click(PK.change("Stage Pick", 1), PK.if_(gt(V("Stage Pick"), len(BRAWL_STAGES)), [PK.set("Stage Pick", 0)]),
                PK.wear(join("stage ", V("Stage Pick"))), PK.broadcast("swing sfx"),
                note="Tap to choose the BRAWL stage, or RANDOM.")

    mk = game.sprite("P1 Marker", size=80, rotation="don't rotate")
    mk.costume("arrow", marker_svg(), 15, 26)
    MK = mk
    MK.on_flag(MK.hide(), MK.forever([
        MK.if_(and_(eq(V("Brawl Live"), 1), eq(item("B Alive", 1), 1)), [
            MK.goto(V("P1 Screen X"), add(V("P1 Screen Y"), mul(V("P1 Screen Size"), 2.05))), MK.show(), MK.front(),
        ], [MK.hide()]),
    ]), note="The yellow P1 arrow shows which fighter is you.")

    return slots


def build():
    game = Game()
    G = game.var
    for name, value in [
        ("Mode", "story"), ("State", "title"), ("Hero", 1), ("Hero Name", "arthur"), ("Hero Title", "ARTHUR"),
        ("Step", 22), ("Punch Power", 5), ("Kick Power", 8), ("Special Power", 18), ("Special Name", "HERO SLASH"),
        ("Hero Max", 100), ("Hero HP", 100), ("Hero X", -150), ("Hero Y", GROUND), ("Facing", 1),
        ("Hero Air", 0), ("Hero Lock", 0), ("Hero Safe", 0), ("Hero Safe Until", 0), ("Perfect Until", 0),
        ("Want Punch", 0), ("Want Kick", 0), ("Want Jump", 0), ("Want Dodge", 0), ("Want Super", 0),
        ("Super", 0), ("Combo", 0), ("Combo Clock", 0),
        ("Weapon", "none"), ("Weapon Uses", 0), ("Weapon Bonus", 0), ("Weapon Reach", 0), ("Boomerang Out", 0),
        ("Enemy Type", 1), ("Enemy Name", "rival"), ("Enemy Title", "RIVAL"), ("Enemy HP", 1), ("Enemy Max", 1),
        ("Enemy Power", 6), ("Enemy Speed", 4), ("Enemy Body", 10), ("Enemy Size", 80), ("Enemy X", 150),
        ("Enemy Facing", -1), ("Enemy Stun Until", 0), ("Enemy Phase", 1), ("Pace", 1),
        ("Chapter", 1), ("Wave", 1), ("Score", 0), ("Best", 0), ("Crown", 0), ("Fight On", 0),
        ("Hit Power", 5), ("Hurt Power", 6), ("Shot Y", GROUND + 18), ("Shot Dir", -1), ("Wave Dir", -1),
        ("Line", ""), ("Line Secs", 2), ("Skip", 0), ("Pop Text", ""), ("Banner", "fight"),
        ("Joy X", 0), ("Touch Pad", 0), ("Spikes", 0), ("Difficulty", 2), ("Enemy Weapon", "none"), ("Enemy Swing Until", 0),
        ("Turn Until", 0), ("Turn Dir", 1), ("Kick At", 0), ("Whirl Ready At", 0), ("Summon Kind", "ninja"), ("Wave Phase", 0), ("Adv Stage", 1), ("Lap", 1),
        ("Beaten", 0), ("Wave Total", 0), ("Spawned", 0), ("Wave Num", 0), ("Hero Look", "arthur"), ("Powering", 0), ("Pen X", 999), ("Pen Y", 0), ("Sound On", 1), ("Debug", 0), ("FPS", 0), ("Minions", 0), ("Summon Count", 1), ("Smoke X", 0), ("Smoke Y", GROUND),
        ("Area X", 0), ("Area R", 0), ("Area Power", 0), ("Area Kind", "hit"), ("Fire Stop", 0),
        ("Power Level", 1), ("Power XP", 0), ("XP Gain", 0), ("Want Power", 0), ("Power Ready At", 0), ("Power Move", "none"),
        ("Bolt X", 0), ("Bolt Y", GROUND), ("Bolt Owner", "hero"), ("Bolt Power", 0), ("Bolt Size", 100),
        ("Fire Held", 0), ("Charge", 0), ("Fire Power", 0), ("Fireball Out", 0),
        ("Pop Seq", 0), ("Ki", 0), ("Enemy Says", ""), ("Page HUD", 0), ("HUD Info", hud_info()), ("Game Version", VERSION), ("Punch Held", 0), ("Kick Held", 0), ("Melee Charge", 0), ("Glow DX", 0), ("Glow DY", 60), ("Glow Kind", "punch"),
        ("Swirl On", 0),
        ("Shot X", 999), ("Shot Live", 0), ("Shot Cancel", 0), ("Boom X", 0),
    ]:
        G(name, value)

    declare_brawl(game)
    game.list("M X")
    for prefix in ("Hand", "EHand"):
        for n in ("X", "Y", "Dir"):
            game.list(f"{prefix} {n}")
    stage = Target(game, "Stage", is_stage=True)
    game.stage = stage
    for kind in ("Title", "Select", "Yard", "Woods", "Pass", "Factory", "Fortress", "Bamboo", "Dojo", "Volcano", "Castle", "Arcade", "Ending"):
        stage.costume(kind, backdrop_svg(kind), 240, 180)
    for name in SOUNDS:
        stage.sound(name)

    s = stage
    # ---------------------------------------------------------- stage --
    s.on_flag(
        s.set("State", "title"), s.set("Fight On", 0), s.set("Score", 0), s.set("Weapon", "none"),
        s.hide_var("Score"), s.hide_var("Wave"), s.hide_var("Best"),
        s.broadcast("intro"),
        note="Green flag. Best and Crown are kept, so a saved project remembers them. The paper intro plays first.",
    )
    s.on_msg("show title", s.set("State", "title"), s.set("Fight On", 0), s.set("Wave Phase", 0), s.backdrop("Title"),
             s.clear_fx(), s.hide_var("Score"), s.hide_var("Wave"), s.show_var("Best"))
    s.on_msg("choose hero", s.set("State", "select"), s.backdrop("Select"), s.hide_var("Best"))

    # hero picked: copy the fighter's numbers
    picks = []
    for i, h in enumerate(HEROES, start=1):
        picks.append(s.if_(eq(V("Hero"), i), [
            s.set("Hero Name", h["key"]), s.set("Hero Title", h["name"]), s.set("Hero Max", h["hp"]),
            s.set("Step", h["step"]), s.set("Punch Power", h["punch"]), s.set("Kick Power", h["kick"]),
            s.set("Special Power", h["special"]), s.set("Special Name", h["special_name"]),
        ]))
    s.on_msg(
        "hero picked", *picks,
        s.change("Hero Max", mul(POWER_HP_PER_LEVEL, sub(V("Power Level"), 1))),
        s.set("Hero HP", V("Hero Max")), s.set("Score", 0), s.set("Super", 0),
        s.if_(eq(V("Mode"), "story"),
              [s.set("Chapter", 1), s.broadcast("story scene")],
              [s.if_(eq(V("Mode"), "brawl"), [s.set("Score", 0), s.broadcast("brawl start")],
                     [s.if_(eq(V("Mode"), "adventure"),
                            [s.set("Adv Stage", 1), s.set("Lap", 1), s.set("Score", 0), s.broadcast("adventure stage")],
                            [s.set("Wave", 1), s.broadcast("start fight")])])]),
        note="Each fighter has different health, speed, punch, kick and super.",
    )

    # load enemy numbers from Enemy Type
    loads = []
    for e in ENEMIES:
        loads.append(s.if_(eq(V("Enemy Type"), e["n"]), [
            s.set("Enemy Name", e["key"]), s.set("Enemy Title", e["tag"]), s.set("Enemy Max", e["hp"]),
            s.set("Enemy Power", e["pow"]), s.set("Enemy Speed", e["speed"]), s.set("Enemy Body", e["body"]),
            s.set("Enemy Size", e["size"]), s.set("Enemy Weapon", BOSS_WEAPONS.get(e["key"], "none")),
        ]))
    chapter_backdrops = [s.if_(eq(V("Chapter"), i), [s.backdrop(c["backdrop"])]) for i, c in enumerate(CHAPTERS, start=1)]
    s.on_msg(
        "load enemy",
        s.if_(eq(V("Mode"), "practice"), [s.set("Enemy Type", 1), s.backdrop("Yard"), s.set("Pace", 1)]),
        s.if_(eq(V("Mode"), "adventure"), [
            *[s.if_(eq(V("Adv Stage"), i), [s.set("Enemy Type", st["boss"]), s.backdrop(st["backdrop"])])
              for i, st in enumerate(ADVENTURE, start=1)],
            s.set("Pace", sub(1, mul(0.08, sub(V("Lap"), 1)))),
        ]),

        s.if_(eq(V("Mode"), "story"),
              [s.set("Enemy Type", V("Chapter")), *chapter_backdrops, s.set("Pace", 1)],
              [s.if_(not_(eq(V("Mode"), "arcade")), [], [s.if_(eq(mod(V("Wave"), KING), 0),
                     [s.set("Enemy Type", KING)],
                     [s.set("Enemy Type", add(mod(sub(V("Wave"), 1), KING), 1))]),
               s.backdrop("Arcade"),
               s.set("Pace", div(8, add(7, V("Wave"))))])]),
        *loads,
        s.if_(eq(V("Mode"), "adventure"), [
            s.set("Enemy Max", mul(V("Enemy Max"), add(1, mul(0.35, sub(V("Lap"), 1))))),
            s.change("Enemy Power", mul(2, sub(V("Lap"), 1))),
        ]),
        s.if_(eq(V("Mode"), "arcade"), [
            s.change("Enemy Max", mul(8, sub(V("Wave"), 1))),
            s.change("Enemy Power", floor_(div(sub(V("Wave"), 1), 2))),
        ]),
        s.if_(not_(eq(V("Enemy Weapon"), "none")), [s.change("Enemy Power", BOSS_WEAPON_POWER)]),
        *[s.if_(eq(V("Difficulty"), i), [
            s.set("Enemy Max", round_(mul(V("Enemy Max"), hp))),
            s.set("Enemy Power", round_(mul(V("Enemy Power"), pw_))),
            s.set("Pace", mul(V("Pace"), pace)),
        ]) for i, (_k, _w, _c, hp, pw_, pace) in enumerate(DIFFICULTIES, start=1)],
        # enemies grow with your power level, too
        s.set("Enemy Max", round_(mul(V("Enemy Max"), add(1, mul(0.2, sub(V("Power Level"), 1)))))),
        s.change("Enemy Power", sub(V("Power Level"), 1)),
        s.set("Pace", mul(V("Pace"), sub(1, mul(0.05, sub(V("Power Level"), 1))))),
        s.set("Enemy HP", V("Enemy Max")), s.set("Enemy Phase", 1),
        note="Story: the chapter picks the enemy. Arcade: waves 1-6 cycle (wave 5 is the MEGA SPIKE boss), every 7th wave is the Shadow King, and each wave is tougher and faster.",
    )

    s.on_msg(
        "start fight",
        s.set("Fight On", 0), s.set("State", "fight"),
        s.broadcast("load enemy", wait=True),
        s.if_(and_(eq(V("Mode"), "arcade"), eq(V("Page HUD"), 0)), [s.show_var("Wave")],
              [s.if_(not_(eq(V("Mode"), "adventure")), [s.set("Hero HP", V("Hero Max"))])]),
        s.list_clear("M X"), s.repeat(3, [s.list_add("M X", 9999)]),
        s.if_(eq(V("Page HUD"), 0), [s.show_var("Score")]), s.hide_var("Best"),
        s.set("Minions", 0), s.set("Combo", 0), s.set("Weapon", "none"), s.set("Weapon Uses", 0), s.set("Boomerang Out", 0),
        s.set("Hero Lock", 0), s.set("Hero Safe", 0), s.set("Hero Air", 0),
        s.set("Spikes", 0), s.set("Charge", 0), s.set("Fireball Out", 0), s.set("Shot Live", 0),
        s.set("Hero Safe Until", 0), s.set("Enemy Stun Until", 0),
        s.broadcast("fighters ready", wait=True),
        s.broadcast("power up show", wait=True),
        s.if_(or_(*[eq(V("Enemy Type"), b) for b in BOSSES]), [
            s.play("alarm"), s.set("Banner", "boss"), s.broadcast("banner"), s.wait(1.5),
        ]),
        s.set("Banner", "ready"), s.broadcast("banner"), s.wait(1.1),
        s.set("Banner", "fight"), s.broadcast("banner"), s.wait(0.3),
        s.set("Want Punch", 0), s.set("Want Kick", 0), s.set("Want Jump", 0), s.set("Want Dodge", 0), s.set("Want Super", 0),
        s.set("Fight On", 1), s.broadcast("fight on"),
        s.if_(eq(V("Mode"), "practice"), [s.set("Pop Text", "PRACTICE: try every move!"), s.broadcast("popup")]),
        note="READY... FIGHT! Taps before FIGHT! are thrown away.",
    )

    # hero hits enemy -- no waits here, so a fast second hit cannot break it
    s.on_msg(
        "hero hits",
        s.if_(and_(eq(V("Fight On"), 1), gt(TIMER, V("Enemy Stun Until")), eq(V("Wave Phase"), 0)), [
            s.set("Enemy Stun Until", add(TIMER, 0.15)),
            s.change("Hit Power", sub(V("Power Level"), 1)),
            s.if_(lt(sub(TIMER, V("Combo Clock")), COMBO_WINDOW), [s.change("Combo", 1)], [s.set("Combo", 1)]),
            s.set("Combo Clock", TIMER),
            s.if_(and_(gt(V("Combo"), 2), eq(mod(V("Combo"), 3), 0)), [
                s.change("Hit Power", COMBO_BONUS),
                s.set("Pop Text", join(join("COMBO x", V("Combo")), "!")), s.broadcast("popup"),
            ]),
            s.change("Enemy HP", sub(0, V("Hit Power"))),
            s.change("Score", add(mul(V("Hit Power"), 10), mul(V("Combo"), 5))),
            s.if_(lt(V("Super"), 100), [
                s.change("Super", SUPER_PER_HIT),
                s.if_(not_(lt(V("Super"), 100)), [s.set("Super", 100), s.broadcast("super ready")]),
            ]),
            s.broadcast("enemy hurt"),
            s.if_(and_(or_(*[eq(V("Enemy Type"), b) for b in BOSSES]), eq(V("Enemy Phase"), 1), gt(V("Enemy HP"), 0),
                       lt(V("Enemy HP"), div(V("Enemy Max"), 2))), [
                s.set("Enemy Phase", 2), s.set("Pace", mul(V("Pace"), 0.7)), s.broadcast("king angry"),
            ]),
            s.if_(lt(V("Enemy HP"), 1), [
                s.if_(eq(V("Mode"), "practice"), [
                    # the practice dummy never goes down: it fills back up
                    s.set("Enemy HP", V("Enemy Max")), s.set("Pop Text", "Nice! Again!"), s.broadcast("popup"),
                ], [s.set("Enemy HP", 0), s.set("Fight On", 0), s.broadcast("enemy down")]),
            ]),
        ]),
        note="Hit Power is set just before this message. Hits inside 1.2 seconds build a combo; every 3rd hit is a bonus. The Shadow King gets angry at half health.",
    )

    s.on_msg(
        "enemy hits hero",
        s.if_(eq(V("Fight On"), 1), [
            s.if_(eq(V("Hero Safe"), 1), [
                s.if_(gt(TIMER, V("Perfect Until")), [
                    s.set("Perfect Until", add(TIMER, 0.8)),
                    s.change("Super", SUPER_PER_PERFECT), s.if_(gt(V("Super"), 99), [s.set("Super", 100)]),
                    s.change("Score", 100),
                    s.set("Pop Text", "PERFECT DODGE!"), s.broadcast("popup"), s.play("perfect"),
                ]),
            ], [
                s.if_(and_(eq(V("Hero Safe"), 0), gt(TIMER, V("Hero Safe Until"))), [
                    s.set("Hero Safe Until", add(TIMER, 0.6)),
                    # a SHIELD blocks most of the hit and wears down a little
                    s.if_(and_(eq(V("Weapon"), "shield"), gt(V("Weapon Uses"), 0)), [
                        s.set("Hurt Power", round_(div(V("Hurt Power"), SHIELD_BLOCK))), s.change("Weapon Uses", -1),
                        s.set("Pop Text", "BLOCKED!"), s.broadcast("popup"), s.broadcast("swing sfx"),
                        s.if_(lt(V("Weapon Uses"), 1), [s.broadcast("weapon break")]),
                    ]),
                    s.change("Hero HP", sub(0, V("Hurt Power"))),
                    s.set("Combo", 0),
                    s.if_(lt(V("Super"), 100), [s.change("Super", SUPER_PER_HURT),
                                                 s.if_(gt(V("Super"), 99), [s.set("Super", 100), s.broadcast("super ready")])]),
                    s.broadcast("hero hurt"),
                    s.if_(lt(V("Hero HP"), 1), [s.set("Hero HP", 0), s.set("Fight On", 0), s.broadcast("hero down")]),
                ]),
            ]),
        ]),
        note="Hurt Power is set by the attacker. Dodging at the last moment is a PERFECT DODGE: no damage and a big super boost.",
    )

    s.local("New Level", 1)
    s.on_msg(
        "gain xp",
        s.change("Power XP", V("XP Gain")), s.set("New Level", 1),
        *[s.if_(not_(lt(V("Power XP"), xp)), [s.set("New Level", n)]) for n, _k, _c1, _c2, xp, _m in POWER_LEVELS],
        s.if_(gt(V("New Level"), V("Power Level")), [s.set("Power Level", V("New Level")), s.broadcast("power up")]),
        note="Win a fight: +1 XP (a boss or a brawl win: +2). At 3, 7, 12 and 18 XP your POWER LEVEL goes up: "
             "more health, harder hits, a new POWER move and a new aura colour. Enemies get stronger with you.",
    )
    move_names = [s.if_(eq(V("Power Level"), n), [s.set("Power Move", m)]) for n, _k, _c1, _c2, _xp, m in POWER_LEVELS]
    s.on_msg(
        "power up",
        *move_names, s.play("power up"), s.set("Banner", "power up"), s.broadcast("banner"),
        s.if_(eq(V("State"), "fight"), [s.broadcast("power up show")]),
        s.set("Pop Text", join("POWER LEVEL ", join(V("Power Level"), join(": ", V("Power Move"))))), s.broadcast("popup"),
        s.repeat(4, [s.effect("BRIGHTNESS", 50), s.wait(0.06), s.effect("BRIGHTNESS", 0), s.wait(0.06)]),
    )
    s.on_msg("bolt strike", s.play("thunder"), s.effect("BRIGHTNESS", 70), s.wait(0.05), s.effect("BRIGHTNESS", 25),
             s.wait(0.05), s.effect("BRIGHTNESS", 0))
    s.on_msg("power flash", s.play("power up"), s.effect("COLOR", 40), s.wait(0.12), s.clear_fx())
    s.on_key("g", s.set("Want Power", 1), note="G: your POWER move (from power level 2).")
    s.local("Frames", 0)
    s.local("Second", 0)
    s.on_flag(
        s.forever([
            s.volume(mul(100, V("Sound On"))),
            # frames per second, for the debug overlay
            s.change("Frames", 1),
            s.if_(gt(TIMER, add(V("Second"), 1)), [s.set("FPS", V("Frames")), s.set("Frames", 0), s.set("Second", TIMER)]),
        ]),
        note="Sound on/off (only the Stage plays sounds, so setting its volume is enough) and a frames-per-second count.",
    )
    s.on_key("d", s.broadcast("toggle debug"), note="D: Mitch's debug overlay (or tap the version number on the title).")
    debug_vars = ("FPS", "State", "Mode", "Fight On", "Hero HP", "Enemy HP", "Enemy Name", "Minions", "Power Level", "Brawl Live")
    s.on_msg("toggle debug", s.set("Debug", sub(1, V("Debug"))),
             s.if_(eq(V("Debug"), 1), [s.show_var(n) for n in debug_vars], [s.hide_var(n) for n in debug_vars]))
    s.on_msg(
        "adventure stage",
        s.set("Wave Phase", 1), s.set("Fight On", 0),
        *[s.if_(eq(V("Adv Stage"), i), [s.set("Pop Text", f"STAGE {i}: {st['name']}"), s.set("Summon Kind", st["kind"])])
          for i, st in enumerate(ADVENTURE, start=1)],
        s.broadcast("start fight"), s.wait(0.6), s.broadcast("popup"),
        note="ADVENTURE: a stage starts with waves of small enemies (the boss stays hidden), then the boss comes.",
    )
    s.local("Waves", 1)
    s.local("Near", 9999)
    s.local("I", 0)
    s.define(
        "aim at nearest",
        # the hero turns toward the closest small enemy (Enemy X is what the hero faces)
        s.set("Near", 99999), s.set("I", 0),
        s.repeat(3, [
            s.change("I", 1),
            s.if_(and_(lt(item("M X", V("I")), 9000), lt(abs_(sub(item("M X", V("I")), V("Hero X"))), V("Near"))), [
                s.set("Near", abs_(sub(item("M X", V("I")), V("Hero X")))), s.set("Enemy X", item("M X", V("I"))),
            ]),
        ]),
    )
    wave_counts = [s.if_(eq(V("Adv Stage"), i), [s.set("Waves", len(st["waves"]))]) for i, st in enumerate(ADVENTURE, start=1)]

    def wave_size():
        out = []
        for i, st in enumerate(ADVENTURE, start=1):
            for w, n in enumerate(st["waves"], start=1):
                out.append(s.if_(and_(eq(V("Adv Stage"), i), eq(V("Wave Num"), w)), [s.set("Wave Total", add(n, sub(V("Lap"), 1)))]))
        return out
    s.on_msg(
        "fight on",
        s.if_(and_(eq(V("Mode"), "adventure"), eq(V("Wave Phase"), 1)), [
            *wave_counts, s.set("Wave Num", 0),
            s.repeat(V("Waves"), [
                s.change("Wave Num", 1), *wave_size(), s.set("Beaten", 0), s.set("Spawned", 0),
                s.set("Enemy Max", V("Wave Total")), s.set("Enemy HP", V("Wave Total")),
                s.set("Pop Text", join("WAVE ", join(V("Wave Num"), join(" of ", V("Waves"))))), s.broadcast("popup"),
                s.until(or_(not_(lt(V("Beaten"), V("Wave Total"))), eq(V("Fight On"), 0)), [
                    s.if_(and_(lt(V("Minions"), 3), lt(V("Spawned"), V("Wave Total"))), [
                        s.change("Spawned", 1), s.set("Summon Count", 1), s.broadcast("ninja summon"), s.wait(0.45),
                    ]),
                    s.set("Enemy HP", sub(V("Wave Total"), V("Beaten"))),
                    s.call("aim at nearest"),
                ]),
                s.if_(eq(V("Fight On"), 0), [s.stop()]),
                s.wait(0.8),
            ]),
            # the boss arrives (its health is loaded first, so no hit can land while the bar still says "0 left")
            s.broadcast("load enemy", wait=True), s.set("Wave Phase", 0), s.set("Enemy X", 170),
            s.play("alarm"), s.set("Banner", "boss"), s.broadcast("banner"),
            s.broadcast("boss enter", wait=True), s.wait(0.6),
            s.broadcast("fight on"),
        ]),
        note="The waves: small enemies come in (up to 3 at once) until the wave is beaten; the enemy bar shows how many are left. "
             "Then the boss arrives with a BOSS FIGHT! warning.",
    )
    s.on_msg("enemy hurt", s.play("hit"))
    s.on_msg("charge start", s.play("charge"))
    s.on_msg("charge full", s.play("charged"), s.set("Pop Text", "FULL POWER!"), s.broadcast("popup"))
    s.on_msg("fire", s.stop_sounds(), s.if_(lt(V("Fire Power"), 100), [s.play("fireball")], [s.play("big fireball")]),
             note="Each stage of the fireball has its own sound: charging, full power, small or big fireball, and BOOM.")
    s.on_msg("boom", s.play("boom"))
    s.on_msg("spikes out", s.play("spikes"))
    s.on_msg("poof sfx", s.play("poof"))
    s.on_msg("shuriken sfx", s.play("shuriken"))
    s.on_msg("spike fall sfx", s.wait(0.7), s.play("spike fall"))
    s.on_msg(
        "spike ouch",
        s.play("clang"), s.set("Pop Text", "OUCH! SPIKES!"), s.broadcast("popup"),
        s.set("Hurt Power", SPIKE_OUCH), s.broadcast("enemy hits hero"),
        note="Punching Spike Bot with bare hands while its spikes are out hurts you. Fireballs, weapons and SUPER still work.",
    )
    s.on_msg("hero hurt", s.play("hurt"))
    s.on_msg("shake", s.play("big hit"))
    s.on_msg("weapon get", s.play("pickup"))
    s.on_msg("swing sfx", s.play("swing"))
    s.on_msg("whirl sfx", s.play("whirl"))
    s.on_msg("jump sfx", s.play("jump"))
    s.on_msg("super flash", s.play("super"),
             s.repeat(3, [s.effect("BRIGHTNESS", 40), s.wait(0.05), s.effect("BRIGHTNESS", 0), s.wait(0.05)]))
    s.on_msg("king angry", s.effect("COLOR", 150), s.wait(0.25), s.clear_fx())

    s.on_msg(
        "enemy down",
        s.play("ko"), s.set("Banner", "ko"), s.broadcast("banner"),
        s.wait(1.4),
        s.if_(eq(V("Mode"), "story"), [
            s.if_(eq(V("Chapter"), len(CHAPTERS)), [
                s.change("Score", add(1000, mul(V("Hero HP"), 5))),
                s.if_(gt(V("Score"), V("Best")), [s.set("Best", V("Score"))]),
                s.set("XP Gain", 2), s.broadcast("gain xp"),
                s.broadcast("ending"),
            ], [
                s.play("win"), s.set("Banner", "clear"), s.broadcast("banner"),
                s.change("Score", add(500, mul(V("Hero HP"), 5))),
                s.set("XP Gain", 1), s.if_(or_(*[eq(V("Enemy Type"), b) for b in BOSSES]), [s.set("XP Gain", 2)]),
                s.broadcast("gain xp"),
                s.wait(2), s.change("Chapter", 1), s.broadcast("story scene"),
            ]),
        ], [s.if_(eq(V("Mode"), "adventure"), [
            s.play("win"), s.set("Banner", "stage clear"), s.broadcast("banner"),
            s.change("Score", add(800, mul(V("Hero HP"), 5))),
            s.set("XP Gain", 2), s.broadcast("gain xp"),
            s.change("Hero HP", ARCADE_HEAL), s.if_(gt(V("Hero HP"), V("Hero Max")), [s.set("Hero HP", V("Hero Max"))]),
            s.if_(gt(V("Score"), V("Best")), [s.set("Best", V("Score"))]),
            s.wait(2), s.change("Adv Stage", 1),
            s.if_(gt(V("Adv Stage"), len(ADVENTURE)), [
                s.set("Adv Stage", 1), s.change("Lap", 1),
                s.set("Pop Text", join("LAP ", join(V("Lap"), "! Enemies are tougher!"))), s.broadcast("popup"), s.wait(1),
            ]),
            s.broadcast("adventure stage"),
        ], [
            s.play("win"), s.set("Banner", "wave clear"), s.broadcast("banner"),
            s.change("Score", add(200, mul(V("Wave"), 50))),
            s.set("XP Gain", 1), s.if_(or_(*[eq(V("Enemy Type"), b) for b in BOSSES]), [s.set("XP Gain", 2)]),
            s.broadcast("gain xp"),
            s.change("Hero HP", ARCADE_HEAL), s.if_(gt(V("Hero HP"), V("Hero Max")), [s.set("Hero HP", V("Hero Max"))]),
            s.set("Pop Text", f"+{ARCADE_HEAL} HEALTH"), s.broadcast("popup"),
            s.if_(gt(V("Score"), V("Best")), [s.set("Best", V("Score"))]),
            s.wait(1.8), s.change("Wave", 1), s.broadcast("start fight"),
        ])]),
        note="Adventure: heal and go on to the next stage. Story: next chapter, or the ending after the Shadow King. Arcade: heal a little and start the next, harder wave.",
    )
    s.on_msg(
        "hero down",
        s.play("ko"), s.set("State", "over"),
        s.if_(gt(V("Score"), V("Best")), [s.set("Best", V("Score"))]),
        s.wait(0.6), s.set("Banner", "ko"), s.broadcast("banner"), s.wait(1.4),
        s.broadcast("game over"),
    )
    s.on_msg("ending", s.set("State", "ending"), s.backdrop("Ending"), s.hide_var("Wave"), s.hide_var("Score"))

    # keyboard, for a laptop
    s.on_key("left arrow", s.broadcast("move left"), note="Keyboard: arrows move, up or space jumps, Z punch, X kick, C dodge, V super. Hold F to charge a fireball (Hero's fire loop checks the F key).")
    s.on_key("right arrow", s.broadcast("move right"))
    s.on_key("up arrow", s.set("Want Jump", 1))
    s.on_key("space", s.set("Want Jump", 1))
    s.on_key("z", s.set("Want Punch", 1))
    s.on_key("x", s.set("Want Kick", 1))
    s.on_key("c", s.set("Want Dodge", 1))
    s.on_key("v", s.set("Want Super", 1))
    s.on_key("down arrow", s.set("Want Drop", 1), note="BRAWL: down arrow drops through a thin platform.")


    # ------------------------------------------------------------ floor --
    # ----------------------------------------------------------- debris --
    db = game.sprite("Debris", size=60, rotation="all around")
    db.costume("rock 1", svg_doc(30, 26, '<polygon points="4,18 9,5 21,2 28,12 22,24 9,24" fill="#78716c" stroke="#44403c" stroke-width="2"/>'), 15, 13)
    db.costume("rock 2", svg_doc(22, 18, '<polygon points="2,12 7,3 18,4 20,14 10,17" fill="#a8a29e" stroke="#57534e" stroke-width="2"/>'), 11, 9)
    db.costume("boulder", boulder_svg(), 30, 26)
    DR = db
    DR.local("Is Clone", 0)
    DR.local("Rise", 3)
    DR.on_flag(DR.hide(), DR.set("Is Clone", 0))

    PLV = V("Power Level")
    spread = add(80, mul(18, PLV))

    def rocks(n, gap):
        return DR.if_(eq(V("Is Clone"), 0), [DR.repeat(n, [
            DR.goto(add(V("Hero X"), rnd(mul(-1, spread), spread)), add(GROUND, rnd(-4, 4))), DR.clone(), DR.wait(gap)])])
    DR.on_msg("ki rise", rocks(add(6, mul(4, PLV)), 0.04),
              note="Rocks rip out of the ground while you power up. The higher your power level, the more rocks, "
                   "the further out they come from, and from level 2 some are big boulders.")
    DR.on_msg("ki flare", rocks(5, 0.07))
    DR.on_clone(
        DR.set("Is Clone", 1), DR.effect("GHOST", 0),
        DR.if_(lt(rnd(1, 6), PLV), [
            # a boulder: it shudders, tears loose, then floats up slowly
            DR.wear("boulder"), DR.size_to(rnd(55, add(70, mul(14, PLV)))), DR.set("Rise", rnd(2, add(2, PLV))), DR.show(), DR.front(),
            DR.repeat(3, [DR.dx(3), DR.wait(0.03), DR.dx(-3), DR.wait(0.03)]),
        ], [
            DR.if_(eq(rnd(1, 2), 1), [DR.wear("rock 1")], [DR.wear("rock 2")]), DR.size_to(rnd(40, 95)),
            DR.set("Rise", rnd(2, add(4, PLV))), DR.show(), DR.front(),
        ]),
        DR.repeat(add(18, mul(3, PLV)), [DR.dy(V("Rise")), DR.dx(rnd(-1, 1)), DR.turn(rnd(3, 11)), DR.wait(0.04)]),
        DR.repeat(6, [DR.effect_by("GHOST", 16), DR.dy(V("Rise")), DR.wait(0.04)]), DR.delete_clone(),
    )

    # ground cracks and a shockwave ring under the hero while powering up
    ck = game.sprite("Ground Crack", size=100, rotation="don't rotate")
    for lv in (1, 2, 3):
        ck.costume(f"crack {lv}", crack_svg(lv), 130, 25)
    CK = ck
    CK.on_flag(CK.hide())
    CK.on_msg(
        "ki rise",
        CK.if_(gt(PLV, 1), [
            CK.if_(gt(PLV, 3), [CK.wear("crack 3")], [CK.if_(gt(PLV, 2), [CK.wear("crack 2")], [CK.wear("crack 1")])]),
            CK.goto(V("Hero X"), sub(GROUND, 4)), CK.size_to(30), CK.effect("GHOST", 0), CK.show(), CK.back(),
            CK.repeat(10, [CK.size_by(add(5, mul(2, PLV))), CK.wait(0.04)]),
            CK.wait(add(0.6, mul(0.2, PLV))),
            CK.repeat(10, [CK.effect_by("GHOST", 10), CK.wait(0.04)]), CK.hide(),
        ]),
        note="From power level 2 the ground cracks open under you. It gets wider every level.",
    )
    for m in ("show title", "choose hero", "story scene", "brawl clear", "brawl start"):
        CK.on_msg(m, CK.hide())
    sw_ring = game.sprite("Shockwave", size=100, rotation="don't rotate")
    sw_ring.costume("ring", shockwave_svg(), 110, 30)
    SR = sw_ring
    SR.on_flag(SR.hide())
    SR.on_msg(
        "shockwave",
        SR.goto(V("Hero X"), add(GROUND, 6)), SR.size_to(20), SR.effect("GHOST", 0), SR.show(), SR.front(),
        SR.repeat(14, [SR.size_by(add(8, mul(4, PLV))), SR.effect_by("GHOST", 7), SR.wait(0.03)]), SR.hide(),
        note="A ring of power blasts out along the ground (power level 2 and up, and when you transform).",
    )
    for m in ("show title", "choose hero", "story scene", "brawl clear", "brawl start"):
        SR.on_msg(m, SR.hide())

    # motion lines for the spinning kicks, and the blazing fist or foot while charging a power move
    swl = game.sprite("Swirl", size=100, rotation="don't rotate")
    swl.costume("swirl 1", swirl_svg(0), 80, 30)
    swl.costume("swirl 2", swirl_svg(1), 80, 30)
    SW = swl
    SW.on_flag(
        SW.hide(), SW.effect("GHOST", 15),
        SW.forever([
            SW.if_(and_(eq(V("Swirl On"), 1), eq(V("State"), "fight")), [
                SW.goto(V("Hero X"), add(V("Hero Y"), 40)),
                SW.if_(eq(mod(round_(mul(TIMER, 20)), 2), 0), [SW.wear("swirl 1")], [SW.wear("swirl 2")]),
                SW.show(), SW.front(),
            ], [SW.hide()]),
        ]),
        note="Whirling motion lines round the WHIRLWIND and HELICOPTER KICKs.",
    )
    # energy streaks that stream up around the hero while powering up: more, bigger and faster as Ki builds
    ks = game.sprite("Ki Spark", size=60, rotation="don't rotate")
    for n, *_r in POWER_LEVELS:
        ks.costume(f"lv{n}", ki_spark_svg(n), 8, 30)
    KS2 = ks
    KS2.local("Is Clone", 0)
    KS2.local("Rise", 8)
    KS2.local("Spread", 30)
    KS2.define(
        "spawn ki",
        KS2.set("Spread", add(26, mul(7, V("Power Level")))),
        KS2.repeat(add(1, floor_(mul(add(1, V("Power Level")), div(add(20, V("Ki")), 100)))), [
            KS2.goto(add(V("Hero X"), rnd(mul(-1, V("Spread")), V("Spread"))), add(V("Hero Y"), rnd(-5, 45))),
            KS2.clone(),
        ]),
    )
    KS2.on_flag(
        KS2.hide(), KS2.set("Is Clone", 0),
        KS2.forever([
            KS2.if_(and_(eq(V("Is Clone"), 0), gt(V("Powering"), 0), eq(V("State"), "fight")), [KS2.call("spawn ki")]),
        ]),
        note="While powering up, streaks of energy shoot upward round the hero. More of them, bigger and faster as the "
             "power builds, and more each power level.",
    )
    KS2.on_clone(
        KS2.set("Is Clone", 1), KS2.wear(join("lv", V("Power Level"))), KS2.size_to(rnd(45, add(70, mul(14, V("Power Level"))))),
        KS2.set("Rise", add(rnd(5, 9), add(V("Power Level"), div(V("Ki"), 25)))), KS2.effect("GHOST", 10), KS2.show(), KS2.front(),
        KS2.repeat(add(8, V("Power Level")), [KS2.dy(V("Rise")), KS2.effect_by("GHOST", 9)]),
        KS2.delete_clone(),
    )
    for m in ("show title", "choose hero", "story scene", "brawl start", "enemy down", "hero down"):
        KS2.on_msg(m, KS2.if_(eq(V("Is Clone"), 1), [KS2.delete_clone()]))

    # the screen darkens round the hero as the power builds (it sits behind every sprite, over the backdrop only)
    dim = game.sprite("Ki Dim", size=100, rotation="don't rotate")
    dim.costume("dark", svg_doc(480, 360, '<rect width="480" height="360" fill="#000000"/>'), 240, 180)
    KD = dim
    KD.local("Dim", 0)
    KD.on_flag(
        KD.hide(), KD.set("Dim", 0),
        KD.forever([
            KD.if_(and_(eq(V("Powering"), 1), eq(V("State"), "fight")), [
                KD.set("Dim", mul(V("Ki"), add(0.14, mul(0.05, V("Power Level"))))),
                KD.goto(0, 0), KD.effect("GHOST", sub(100, V("Dim"))), KD.show(), KD.back(),
            ], [
                # fade back out afterwards
                KD.if_(gt(V("Dim"), 0), [KD.change("Dim", -3), KD.effect("GHOST", sub(100, V("Dim")))], [KD.hide()]),
            ]),
        ]),
        note="While powering up the backdrop darkens a little more each moment (and more each power level), "
             "so the aura blazes out of the dark.",
    )

    # a burst of light rays when the power-up peaks (and when the hero transforms)
    rays = game.sprite("Ki Rays", size=30, rotation="all around")
    for n, *_r in POWER_LEVELS:
        rays.costume(f"lv{n}", ki_rays_svg(n), 120, 120)
    KR = rays
    KR.on_flag(KR.hide())
    KR.on_msg(
        "ki burst",
        KR.wear(join("lv", V("Power Level"))), KR.goto(V("Hero X"), add(V("Hero Y"), 62)), KR.size_to(20), KR.point(90),
        KR.effect("GHOST", 15), KR.show(), KR.front(),
        KR.repeat(add(10, V("Power Level")), [KR.size_by(add(10, mul(5, V("Power Level")))), KR.turn(4), KR.effect_by("GHOST", 7)]),
        KR.hide(),
        note="The peak of a power-up: a burst of light rays, bigger with more rays each power level.",
    )
    for m in ("show title", "choose hero", "story scene", "brawl start"):
        KR.on_msg(m, KR.hide())

    pf = game.sprite("Power Fist", size=50, rotation="don't rotate")
    pf.costume("punch", power_glow_svg("#fffbeb", "#facc15", "#f97316"), 40, 40)
    pf.costume("kick", power_glow_svg("#f0f9ff", "#38bdf8", "#6366f1"), 40, 40)
    PF = pf
    PF.on_flag(
        PF.hide(),
        PF.forever([
            PF.if_(and_(gt(V("Melee Charge"), 0), eq(V("State"), "fight")), [
                PF.goto(add(V("Hero X"), mul(V("Glow DX"), V("Facing"))), add(V("Hero Y"), V("Glow DY"))),
                PF.wear(V("Glow Kind")), PF.size_to(add(25, mul(V("Melee Charge"), 0.75))),
                PF.turn(15),
                PF.if_(eq(V("Melee Charge"), 100), [PF.effect("BRIGHTNESS", mul(35, mod(round_(mul(TIMER, 10)), 2)))],
                       [PF.effect("BRIGHTNESS", 0)]),
                PF.show(), PF.front(),
            ], [PF.hide()]),
        ]),
        note="Hold PUNCH or KICK: power gathers in your fist (gold) or foot (blue) and grows until you let go.",
    )
    for m in ("show title", "choose hero", "story scene", "brawl clear"):
        DR.on_msg(m, DR.if_(eq(V("Is Clone"), 1), [DR.delete_clone()]))

    # ------------------------------------------------------------ intro --
    stage.costume("Paper", paper_svg(), 240, 180)
    sk = game.sprite("Sketch", x=0, y=0, rotation="don't rotate")
    frames = intro_frames()
    for i, (svg, _tip) in enumerate(frames, start=1):
        sk.costume(f"frame {i}", svg, 240, 180)
    pen = game.sprite("Pencil", x=0, y=0, rotation="don't rotate")
    pen.costume("pencil", pencil_svg(), 20, 72)
    KS = sk
    steps = []
    for i, (_svg, tip) in enumerate(frames, start=1):
        steps.append(KS.wear(f"frame {i}"))
        if tip is not None:
            steps.append(KS.set("Pen X", tip[0]))
            steps.append(KS.set("Pen Y", tip[1]))
            if i % 2 == 1:
                steps.append(KS.broadcast("scribble"))
            steps.append(KS.wait(0.03))
        else:
            steps += [KS.set("Pen X", 999), KS.broadcast("color in"), KS.wait(0.3)]
    KS.on_flag(KS.hide())
    KS.on_msg(
        "intro",
        KS.set("State", "intro"), KS.backdrop("Paper"), KS.goto(0, 0), KS.effect("GHOST", 0), KS.show(), KS.front(),
        KS.wait(0.2), *steps, KS.wait(0.6),
        KS.broadcast("page"), KS.repeat(8, [KS.effect_by("GHOST", 12), KS.dx(-40), KS.wait(0.03)]),
        KS.hide(), KS.set("Pen X", 999), KS.broadcast("show title"),
        note="The intro: a pencil draws Arthur, Nova and Rocko on notebook paper, stroke by stroke, then colours them in "
             "and turns the page to the title. Tap anywhere to skip.",
    )
    skip_i = game.sprite("Skip Intro", x=196, y=-156, rotation="don't rotate")
    skip_i.costume("skip", button_svg("SKIP ▶▶", "#334155", "#ffffff", 84, 40, 13), 42, 20)
    SI = skip_i
    SI.on_flag(SI.hide())
    SI.on_msg("intro", SI.goto(196, -156), SI.show(), SI.front())
    SI.on_msg("show title", SI.hide())
    SI.on_click(SI.hide(), SI.broadcast("skip intro"), note="Skip the drawing and go straight to the title.")
    KS.on_msg("skip intro", KS.stop("other scripts in sprite"), KS.hide(), KS.set("Pen X", 999), KS.broadcast("show title"))
    KS.on_click(KS.if_(eq(V("State"), "intro"), [KS.broadcast("skip intro")]))
    s.on_stage_click(s.if_(eq(V("State"), "intro"), [s.broadcast("skip intro")]), note="Tap during the intro to skip it.")
    s.on_msg("scribble", s.play("scribble"))
    s.on_msg("ki rise", s.play("ki roar"), s.repeat(add(5, mul(2, V("Power Level"))), [s.broadcast("shake"), s.wait(0.17)]))
    s.on_msg("ki flare", s.play("ki flare"))
    s.on_msg("transform", s.play("transform"), s.broadcast("popup"),
             s.repeat(3, [s.effect("BRIGHTNESS", 90), s.wait(0.05), s.effect("BRIGHTNESS", 0), s.wait(0.05)]))
    s.on_msg("color in", s.play("pickup"))
    s.on_msg("page", s.play("page"))
    PN = pen
    PN.on_flag(PN.hide(), PN.forever([
        PN.if_(and_(eq(V("State"), "intro"), lt(V("Pen X"), 900)), [PN.goto(V("Pen X"), V("Pen Y")), PN.show(), PN.front()],
               [PN.hide()]),
    ]), note="The pencil follows the line being drawn.")

    floor = game.sprite("Ground Shake", x=0, y=GROUND - 5, visible=True, rotation="don't rotate")
    floor.costume("shadow", floor_svg(), 240, 5)
    floor.on_flag(floor.goto(0, GROUND - 5), floor.show())
    floor.on_msg("brawl start", floor.hide())
    floor.on_msg("intro", floor.hide())
    floor.on_msg("start fight", floor.show())
    floor.on_msg("show title", floor.show())
    floor.on_msg("shake", floor.repeat(3, [floor.goto(0, GROUND - 1), floor.wait(0.04), floor.goto(0, GROUND - 9), floor.wait(0.04)]),
                 floor.goto(0, GROUND - 5))

    # ------------------------------------------------------------- hero --
    hero = game.sprite("Hero", x=-150, y=GROUND, size=75, visible=True)
    for h in HEROES:
        for look, hair in (("", None), (" gold", "gold"), (" silver", "silver")):
            for pose in ("idle", "punch", "kick", "jump", "hurt", "win", "dodge", "special", "down", "charge",
                         "idle b", "walk 1", "walk 2", "walk 3", "walk 4", "punch 1", "kick 1", "hurt high", "charge up",
                         "spin 1", "spin 2", "spin 3", "spin 4", "heli 1", "heli 2", "heli 3", "heli 4", "sky kick", "windup"):
                face = "hurt" if pose == "hurt" else ("ko" if pose == "down" else ("yell" if pose == "charge up" else "smile"))
                glow = {"special": "#facc15", "charge": "#fb923c"}.get(pose)
                hero.costume(f"{h['key']}{look} {pose}", fighter_svg(h["color"], "aim" if pose == "charge" else pose, h["gear"],
                                                                    face, glow=glow, hair=hair), 50, 168)
            for k in range(4):
                hero.costume(f"{h['key']}{look} flip {k + 1}", fighter_svg(h["color"], "tuck", h["gear"], "smile", hair=hair,
                                                                            rot=90 * k), 50, 168)
    H = hero

    def pose(name):
        return H.wear(join(V("Hero Look"), " " + name))

    def rest_pose():
        return H.if_(eq(V("Hero Air"), 1), [pose("jump")], [pose("idle")])

    def face_enemy():
        return H.if_(lt(TIMER, V("Turn Until")), [
            H.if_(gt(V("Turn Dir"), 0), [H.point(90), H.set("Facing", 1)], [H.point(-90), H.set("Facing", -1)]),
        ], [
            H.if_(lt(V("Enemy X"), sub(XPOS, 4)), [H.point(-90), H.set("Facing", -1)],
                  [H.if_(gt(V("Enemy X"), add(XPOS, 4)), [H.point(90), H.set("Facing", 1)])]),
        ])

    def in_reach(reach):
        return lt(abs_(sub(V("Enemy X"), V("Hero X"))), add(add(reach, V("Weapon Reach")), V("Enemy Body")))

    def area(r, power, kind="hit", at=None):
        """Tell every ninja minion near this spot that it was hit."""
        return H.if_(gt(V("Minions"), 0), [
            H.set("Area X", at if at is not None else add(V("Hero X"), mul(V("Facing"), r))), H.set("Area R", r),
            H.set("Area Power", power), H.set("Area Kind", kind), H.broadcast("area hit"),
        ])

    def land_hit():
        return H.if_(and_(eq(V("Spikes"), 1), eq(V("Weapon Bonus"), 0)), [H.broadcast("spike ouch")], [
            H.broadcast("hero hits"), H.if_(eq(V("Weapon"), "hammer"), [H.broadcast("shake")]),
        ])

    def weapon_swing():
        return H.if_(gt(V("Weapon Bonus"), 0), [
            H.change("Weapon Uses", -1), H.broadcast("swing"),
        ], [H.broadcast("swing sfx")])

    def break_check():
        return H.if_(and_(not_(eq(V("Weapon"), "none")), lt(V("Weapon Uses"), 1), eq(V("Boomerang Out"), 0)),
                     [H.broadcast("weapon break")])

    H.on_flag(
        H.rotation_style("left-right"), H.point(90),
        H.forever([
            H.set("Hero X", XPOS), H.set("Hero Y", YPOS),
            H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Lock"), 0)), [face_enemy()]),
        ]),
        note="Hero X and Hero Y are read by everyone else. In a fight, Hero faces the way you are walking, "
             "then turns back to face the enemy, so you can fight ninjas on both sides.",
    )

    H.local("Last X", 0)
    H.local("HVY", 0)
    H.local("Spin", 0)
    H.local("Jumps", 0)
    H.local("Flip", 0)
    H.local("Look", "")
    H.local("Hold Until", 0)
    H.on_flag(
        H.forever([
            H.set("Look", COSTUME),
            H.if_(and_(or_(eq(V("State"), "fight"), eq(V("State"), "story")),
                       or_(contains(V("Look"), "idle"), contains(V("Look"), "walk"))), [
                H.if_(and_(eq(V("Hero Air"), 0), gt(abs_(sub(XPOS, V("Last X"))), 0.6)), [
                    # walking: the stride follows how far you have moved
                    H.wear(join(V("Hero Look"), join(" walk ", add(floor_(mod(div(add(XPOS, 1000), 11), 4)), 1)))),
                ], [
                    # standing: breathe in and out
                    H.if_(eq(mod(round_(mul(TIMER, 1.6)), 2), 0), [pose("idle")], [pose("idle b")]),
                ]),
            ]),
            H.set("Last X", XPOS),
        ]),
        note="Makes the stick figure feel alive: breathing while standing, a 4-step walk cycle while moving. "
             "It only changes the standing and walking pictures, never a punch or a kick.",
    )

    punch = [
        pose("punch 1"), H.wait(0.06), pose("punch"),
        H.if_(and_(eq(V("Weapon"), "boomerang"), eq(V("Boomerang Out"), 0)), [
            H.set("Boomerang Out", 1), H.change("Weapon Uses", -1), H.broadcast("throw boomerang"), H.broadcast("swing sfx"),
        ], [
            H.set("Hit Power", add(V("Punch Power"), V("Weapon Bonus"))),
            weapon_swing(),
            H.if_(in_reach(PUNCH_REACH), [land_hit()]), area(PUNCH_REACH * 0.55, V("Hit Power")),
            # nunchucks: the second stick whips round for another hit
            H.if_(eq(V("Weapon"), "nunchucks"), [
                H.wait(0.17), pose("punch 1"), H.wait(0.04), pose("punch"), H.broadcast("swing"),
                H.if_(in_reach(PUNCH_REACH), [land_hit()]), area(PUNCH_REACH * 0.55, V("Hit Power")),
            ]),
        ]),
        H.wait(0.16), break_check(), rest_pose(),
    ]
    kick = [
        pose("kick 1"), H.wait(0.07), pose("kick"), H.move(14), *H.clamp_x(-215, 215),
        H.set("Hit Power", add(V("Kick Power"), V("Weapon Bonus"))),
        weapon_swing(),
        H.if_(in_reach(KICK_REACH), [land_hit()]), area(KICK_REACH * 0.55, V("Hit Power")),
        H.wait(0.22), H.move(-14), *H.clamp_x(-215, 215), break_check(), rest_pose(),
    ]
    def whirl_hit():
        return [H.set("Hit Power", WHIRL_HIT),
                H.if_(lt(abs_(sub(V("Enemy X"), V("Hero X"))), add(64, V("Enemy Body"))), [land_hit()]),
                area(64, WHIRL_HIT, at=V("Hero X"))]

    whirl = [
        # WHIRLWIND KICK: lift off, spin with one leg out, travel forward, hit on both sides up to 3 times
        H.set("Hero Lock", 1), H.set("Whirl Ready At", add(TIMER, WHIRL_COOLDOWN)),
        H.set("Pop Text", "WHIRLWIND KICK!"), H.broadcast("popup"), H.broadcast("whirl sfx"),
        H.if_(eq(V("Hero Air"), 0), [H.dy(16)]),
        H.set("Spin", 0), H.set("Swirl On", 1),
        H.repeat(15, [
            H.change("Spin", 1),
            H.wear(join(V("Hero Look"), join(" spin ", add(mod(floor_(div(V("Spin"), 2)), 4), 1)))),
            H.move(7), *H.clamp_x(-215, 215),
            H.if_(eq(mod(V("Spin"), 5), 1), whirl_hit()),
        ]),
        H.set("Swirl On", 0),
        H.if_(eq(V("Hero Air"), 0), [H.set_y(GROUND)]),
        rest_pose(), H.set("Hero Lock", 0),
    ]

    def heli_hit():
        return [H.set("Hit Power", HELI_HIT),
                H.if_(lt(abs_(sub(V("Enemy X"), V("Hero X"))), add(70, V("Enemy Body"))), [land_hit()]),
                area(70, HELI_HIT, at=V("Hero X"))]

    heli = [
        # HELICOPTER KICK (in the air): legs out like rotor blades, spin fast, hover down slowly, hit both sides
        H.set("Hero Lock", 1), H.set("Whirl Ready At", add(TIMER, WHIRL_COOLDOWN)),
        H.set("Pop Text", "HELICOPTER KICK!"), H.broadcast("popup"), H.broadcast("whirl sfx"),
        H.set("HVY", 7), H.set("Jumps", 2), H.set("Flip", 0), H.set("Spin", 0), H.set("Swirl On", 1),
        H.until(or_(gt(V("Spin"), HELI_FRAMES), eq(V("Hero Air"), 0), eq(V("Fight On"), 0)), [
            H.change("Spin", 1),
            H.wear(join(V("Hero Look"), join(" heli ", add(mod(V("Spin"), 4), 1)))),
            # the spinning legs hold Hero up: fall slowly
            H.if_(lt(V("HVY"), -1), [H.set("HVY", -1)]),
            H.move(5), *H.clamp_x(-215, 215),
            H.if_(eq(mod(V("Spin"), 5), 1), heli_hit()),
            H.if_(eq(mod(V("Spin"), 10), 0), [H.broadcast("whirl sfx")]),
        ]),
        H.set("Swirl On", 0), rest_pose(), H.set("Hero Lock", 0),
    ]

    # ---- hold PUNCH or KICK: charge a power move, let go to unleash it ----
    punch_held = or_(eq(V("Punch Held"), 1), ("keypressed", "z"))
    kick_held = or_(eq(V("Kick Held"), 1), ("keypressed", "x"))

    def still_held(held):
        # wait a moment: a quick tap is a normal move, a hold starts charging
        return [H.set("Hold Until", add(TIMER, HOLD_TIME)),
                H.until(or_(not_(held), gt(TIMER, V("Hold Until")), eq(V("Fight On"), 0)), [])]

    def charge_melee(held, kind, pose_name, dx, dy):
        return [
            H.set("Hero Lock", 1), H.set("Melee Charge", 1), H.set("Glow Kind", kind), H.set("Glow DX", dx),
            H.set("Glow DY", dy), pose(pose_name), H.broadcast("charge start"),
            H.until(or_(not_(held), eq(V("Fight On"), 0)), [
                H.if_(lt(V("Melee Charge"), 100), [
                    H.change("Melee Charge", MELEE_RATE),
                    H.if_(not_(lt(V("Melee Charge"), 100)), [H.set("Melee Charge", 100), H.broadcast("charge full")]),
                ]),
                # tremble harder as the power builds
                H.dx(mul(sub(mul(mod(round_(mul(TIMER, 30)), 2), 2), 1), div(V("Melee Charge"), 40))),
            ]),
        ]

    def melee_done(held, want, flag):
        return [H.set("Melee Charge", 0), break_check(), rest_pose(), H.set("Hero Lock", 0),
                H.wait_until(not_(held)), H.set(flag, 0), H.set(want, 0)]

    full = eq(V("Melee Charge"), 100)
    meteor = [
        # METEOR PUNCH: a blazing dash; the longer you held, the further and harder
        H.set("Hit Power", add(add(V("Punch Power"), V("Weapon Bonus")), round_(div(V("Melee Charge"), 9)))),
        H.set("Pop Text", "METEOR PUNCH!"), H.broadcast("popup"), H.broadcast("whirl sfx"),
        H.set("Glow DX", 36), H.set("Glow DY", 74), pose("punch"),
        H.repeat(6, [H.move(add(4, div(V("Melee Charge"), 12))), *H.clamp_x(-215, 215)]),
        weapon_swing(),
        H.if_(in_reach(PUNCH_REACH + 10), [land_hit()]), area(PUNCH_REACH * 0.7, V("Hit Power")),
        H.if_(full, [H.broadcast("shake"), H.broadcast("ki flare")]),
        H.wait(0.25),
    ]
    sky_kick = [
        # SKY KICK: a rising kick that hits twice
        H.set("Hit Power", add(add(V("Kick Power"), V("Weapon Bonus")), round_(div(V("Melee Charge"), 12)))),
        H.set("Pop Text", "SKY KICK!"), H.broadcast("popup"), H.broadcast("whirl sfx"),
        H.set("Glow DX", 26), H.set("Glow DY", 76), pose("sky kick"), weapon_swing(),
        H.if_(eq(V("Hero Air"), 0), [H.set("Hero Air", 1)]),
        H.set("Jumps", 2), H.set("Flip", 0), H.set("HVY", add(9, div(V("Melee Charge"), 14))),
        H.repeat(4, [H.move(5), *H.clamp_x(-215, 215)]),
        H.if_(in_reach(KICK_REACH), [land_hit()]), area(KICK_REACH * 0.6, V("Hit Power")),
        H.repeat(5, [H.move(3), *H.clamp_x(-215, 215)]),
        H.set("Hit Power", round_(div(V("Hit Power"), 2))),
        H.if_(in_reach(KICK_REACH), [land_hit()]), area(KICK_REACH * 0.6, V("Hit Power")),
        H.if_(full, [H.broadcast("shake"), H.broadcast("ki flare")]),
        H.wait(0.2),
    ]

    dodge = [
        H.set("Hero Lock", 1), H.set("Hero Safe", 1), pose("dodge"), H.effect("GHOST", 45), H.broadcast("swing sfx"),
        H.repeat(6, [H.move(-10), *H.clamp_x(-215, 215)]),
        H.wait(0.14), H.effect("GHOST", 0), H.set("Hero Safe", 0), pose("idle"), H.set("Hero Lock", 0), H.wait(0.12),
    ]

    def super_hit(power):
        return [H.set("Hit Power", power), H.broadcast("hero hits"), area(90, power, at=V("Hero X"))]

    special = [
        H.set("Hero Lock", 1), H.set("Hero Safe", 2), H.set("Super", 0),
        H.set("Pop Text", join(V("Special Name"), "!")), H.broadcast("popup"), H.broadcast("super flash"),
        pose("special"), H.wait(0.35),
        H.if_(eq(V("Hero"), 1), [
            H.glide(0.18, sub(V("Enemy X"), mul(45, V("Facing"))), GROUND),
            *super_hit(V("Special Power")), H.broadcast("shake"), H.wait(0.4),
        ]),
        H.if_(eq(V("Hero"), 2), [
            H.repeat(3, [
                H.glide(0.1, sub(V("Enemy X"), mul(40, V("Facing"))), GROUND), pose("kick"),
                *super_hit(round_(div(V("Special Power"), 3))), H.wait(0.2), pose("special"), H.move(-40),
                *H.clamp_x(-215, 215),
            ]),
        ]),
        H.if_(eq(V("Hero"), 3), [
            pose("jump"), H.repeat(6, [H.dy(18)]),
            H.glide(0.15, sub(V("Enemy X"), mul(40, V("Facing"))), GROUND),
            pose("special"), *super_hit(V("Special Power")), H.broadcast("shake"), H.wait(0.4),
        ]),
        H.set_y(GROUND), *H.clamp_x(-215, 215), pose("idle"), H.set("Hero Safe", 0), H.set("Hero Lock", 0),
    ]
    def bolt_on_enemy(power, spread=0):
        return [H.set("Bolt X", add(V("Enemy X"), rnd(-spread, spread)) if spread else V("Enemy X")),
                H.set("Bolt Y", GROUND), H.set("Bolt Owner", "hero"), H.set("Bolt Power", power), H.set("Bolt Size", 100),
                H.broadcast("bolt")]

    power_move = [
        H.set("Hero Lock", 1), H.set("Hero Safe", 2), H.set("Power Ready At", add(TIMER, POWER_COOLDOWN)),
        pose("charge up"), H.set("Powering", 1), H.broadcast("ki flare"), H.say("HAA!", 0.3), H.set("Powering", 0),
        *[H.if_(eq(V("Power Level"), n), [H.set("Power Move", m)]) for n, _k, _c1, _c2, _xp, m in POWER_LEVELS],
        H.set("Pop Text", join(V("Power Move"), "!")), H.broadcast("popup"), H.broadcast("power flash"),
        H.if_(eq(V("Power Level"), 2), [
            # FLAME DASH: a burning dash straight through the enemy
            pose("special"), H.glide(0.16, add(V("Enemy X"), mul(45, V("Facing"))), GROUND), *H.clamp_x(-215, 215),
            H.set("Hit Power", 9), H.broadcast("hero hits"), area(90, 9, at=V("Hero X")), H.broadcast("shake"), H.wait(0.3),
        ]),
        H.if_(eq(V("Power Level"), 3), [
            # THUNDER STRIKE: one big bolt from the sky
            pose("win"), H.wait(0.2), *bolt_on_enemy(13), H.wait(0.55),
        ]),
        H.if_(eq(V("Power Level"), 4), [
            # BLUE STORM: three bolts
            pose("win"), H.wait(0.15),
            H.repeat(3, [*bolt_on_enemy(7, 18), H.wait(0.25)]), H.wait(0.3),
        ]),
        H.if_(eq(V("Power Level"), 5), [
            # ULTRA STORM: five bolts, the last one huge
            pose("win"), H.wait(0.15),
            H.repeat(4, [*bolt_on_enemy(6, 30), H.wait(0.2)]), *bolt_on_enemy(14), H.broadcast("shake"), H.wait(0.4),
        ]),
        H.set_y(GROUND), pose("idle"), H.set("Hero Safe", 0), H.set("Hero Lock", 0),
    ]

    H.on_flag(
        H.forever([
            H.if_(eq(V("Fight On"), 1), [
                H.if_(and_(eq(V("Want Super"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Super", 0),
                    H.if_(and_(eq(V("Super"), 100), eq(V("Hero Air"), 0)), special),
                ]),
                H.if_(and_(eq(V("Want Power"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Power", 0),
                    H.if_(and_(gt(V("Power Level"), 1), gt(TIMER, V("Power Ready At")), eq(V("Hero Air"), 0)), power_move,
                          [H.if_(eq(V("Power Level"), 1), [H.set("Pop Text", "Win fights to unlock POWER!"),
                                                            H.broadcast("popup")])]),
                ]),
                H.if_(and_(eq(V("Want Punch"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Punch", 0), *still_held(punch_held),
                    H.if_(and_(punch_held, eq(V("Fight On"), 1)), [
                        *charge_melee(punch_held, "punch", "windup", -20, 84),
                        H.if_(eq(V("Fight On"), 1), meteor), *melee_done(punch_held, "Want Punch", "Punch Held"),
                    ], punch),
                ]),
                H.if_(and_(eq(V("Want Kick"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Kick", 0),
                    H.if_(and_(lt(sub(TIMER, V("Kick At")), DOUBLE_TAP), gt(TIMER, V("Whirl Ready At"))),
                          [H.set("Kick At", 0), H.if_(eq(V("Hero Air"), 1), heli, whirl)], [
                        *still_held(kick_held),
                        H.if_(and_(kick_held, eq(V("Fight On"), 1)), [
                            *charge_melee(kick_held, "kick", "kick 1", 12, 40),
                            H.if_(eq(V("Fight On"), 1), sky_kick), *melee_done(kick_held, "Want Kick", "Kick Held"),
                        ], [H.set("Kick At", TIMER), *kick]),
                    ]),
                ]),
                H.if_(and_(eq(V("Want Dodge"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Dodge", 0), H.if_(eq(V("Hero Air"), 0), dodge),
                ]),
            ], [
                H.if_(not_(eq(V("State"), "brawl")), [
                    H.set("Want Punch", 0), H.set("Want Kick", 0), H.set("Want Dodge", 0), H.set("Want Super", 0),
                    H.set("Want Power", 0)]),
            ]),
        ]),
        note="The action loop. Buttons only set Want Punch, Want Kick and so on; this loop does one move at a time. "
             "A tap during a move waits its turn (a short input buffer, like big fighting games).",
    )
    H.on_flag(
        H.forever([
            H.if_(and_(eq(V("Want Jump"), 1), not_(eq(V("State"), "brawl"))), [
                H.set("Want Jump", 0),
                H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Lock"), 0)), [
                    H.if_(eq(V("Hero Air"), 0), [
                        H.set("Hero Air", 1), H.set("Jumps", 1), H.set("HVY", JUMP_UP), pose("jump"), H.broadcast("jump sfx"),
                    ], [
                        # second tap in the air: jump again with a front flip
                        H.if_(eq(V("Jumps"), 1), [H.set("Jumps", 2), H.set("HVY", FLIP_UP), H.set("Flip", FLIP_FRAMES),
                                                  H.broadcast("jump sfx")]),
                    ]),
                ]),
            ]),
            H.if_(eq(V("Hero Air"), 1), [
                H.dy(V("HVY")), H.change("HVY", -HERO_GRAV),
                H.if_(gt(V("Flip"), 0), [
                    H.change("Flip", -1),
                    H.if_(and_(eq(V("Hero Lock"), 0), not_(contains(COSTUME, "punch")), not_(contains(COSTUME, "kick"))), [
                        H.if_(gt(V("Flip"), 0),
                              [H.wear(join(V("Hero Look"), join(" flip ", add(floor_(mod(div(sub(FLIP_FRAMES, V("Flip")), 4), 4)), 1))))],
                              [pose("jump")]),
                    ]),
                ]),
                H.if_(not_(gt(YPOS, GROUND)), [
                    H.set_y(GROUND), H.set("Hero Air", 0), H.set("Jumps", 0), H.set("HVY", 0), H.set("Flip", 0),
                    H.if_(eq(V("Hero Lock"), 0), [pose("idle")]),
                ]),
            ]),
        ]),
        note="The jump loop runs beside the action loop, so you can punch and kick in the air. "
             "Tap JUMP again while in the air for a second jump with a front flip.",
    )
    holding = or_(eq(V("Fire Held"), 1), ("keypressed", "f"))
    H.on_flag(
        H.forever([
            H.if_(and_(eq(V("Fight On"), 1), eq(V("Fireball Out"), 0), eq(V("Hero Lock"), 0), holding), [
                H.set("Charge", 1), H.broadcast("charge start"), pose("charge"),
                H.until(or_(not_(holding), eq(V("Fight On"), 0), eq(V("Hero Lock"), 1)), [
                    H.if_(lt(V("Charge"), 100), [
                        H.change("Charge", CHARGE_RATE),
                        H.if_(not_(lt(V("Charge"), 100)), [H.set("Charge", 100), H.broadcast("charge full")]),
                    ]),
                ]),
                H.set("Fire Held", 0),
                H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Fire Power", V("Charge")), H.set("Charge", 0), H.set("Fireball Out", 1), H.broadcast("fire"),
                    pose("punch"), H.wait(0.15), rest_pose(),
                ]),
                H.set("Charge", 0),
            ]),
        ]),
        note="The fire loop. Hold FIRE (or F) to charge; let go to shoot. "
             "A quick tap is a small fireball; a full charge (about 1 second) is a giant one that explodes.",
    )
    H.on_flag(
        H.forever([
            H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Lock"), 0),
                       gt(abs_(V("Joy X")), JOY_DEADZONE)), [
                H.dx(mul(mul(V("Joy X"), V("Step")), JOY_SPEED)), *H.clamp_x(-215, 215),
                H.set("Turn Dir", V("Joy X")), H.set("Turn Until", add(TIMER, 0.3)),
            ]),
        ]),
        note="Joystick walking. The Android app's joystick sets Joy X from -1 (left) to 1 (right) "
             "and Hero walks every frame. Faster fighters walk faster.",
    )
    for direction, sign in (("left", -1), ("right", 1)):
        H.on_msg(f"move {direction}", H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Lock"), 0)), [
            H.dx(mul(sign, V("Step"))), *H.clamp_x(-215, 215),
            H.set("Turn Dir", sign), H.set("Turn Until", add(TIMER, 0.45)),
        ]))
    H.on_msg("hero hurt", H.if_(eq(V("Hero Lock"), 0), [
                 H.if_(eq(rnd(1, 2), 1), [pose("hurt")], [pose("hurt high")]), H.move(-12), *H.clamp_x(-215, 215)]),
             H.effect("COLOR", 60), H.wait(0.15), H.effect("COLOR", 0), H.if_(eq(V("Hero Lock"), 0), [rest_pose()]))
    H.on_msg("show title", H.show(), H.clear_fx(), H.point(90), H.set("Hero Name", "arthur"), H.wear("arthur idle"),
             H.goto(-212, GROUND), H.size_to(90), H.front(), H.say("I'm Arthur!", 2))
    H.on_msg("choose hero", H.hide())
    H.on_msg("intro", H.hide())
    H.on_msg("story scene", H.hide())
    H.on_msg("fighters ready", H.show(), H.clear_fx(), H.point(90), H.set("Facing", 1), H.set("Hero Look", V("Hero Name")),
             pose("idle"),
             H.size_to(75), H.goto(-150, GROUND),
             *[H.if_(eq(V("Hero"), i), [H.say(h["line"], 1)]) for i, h in enumerate(HEROES, start=1)],
             note="Each fighter has a catchphrase before READY... FIGHT!")
    H.on_msg("scene setup", H.show(), H.clear_fx(), H.point(90), H.set("Hero Look", V("Hero Name")), pose("idle"), H.size_to(75), H.goto(-150, GROUND))
    H.local("Line Until", 0)
    H.on_msg(
        "power up show",
        H.set("Hero Lock", 1), pose("charge up"), H.say("Hmmmm...", 0.45),
        H.set("Ki", 0), H.set("Powering", 1), H.broadcast("ki rise"), H.say("HAAAAAA!"),
        H.if_(gt(V("Power Level"), 1), [H.broadcast("shockwave")]),
        # the power builds (Ki 0 to 100): the aura swells, sparks stream up, the hero glows brighter.
        # The higher the power level, the longer, harder and brighter it is.
        H.repeat(add(9, V("Power Level")), [
            H.change("Ki", div(100, add(9, V("Power Level")))),
            H.effect("BRIGHTNESS", mul(V("Ki"), add(0.08, mul(0.05, V("Power Level"))))),
            H.dx(add(1, V("Power Level"))), H.wait(0.04), H.dx(mul(-1, add(1, V("Power Level")))), H.wait(0.04)]),
        H.set("Ki", 100), H.broadcast("ki burst"),
        # level 3 and up: transform! golden hair (silver at level 5)
        H.if_(gt(V("Power Level"), 2), [
            H.if_(gt(V("Power Level"), 4), [H.set("Hero Look", join(V("Hero Name"), " silver"))],
                  [H.set("Hero Look", join(V("Hero Name"), " gold"))]),
            H.if_(gt(V("Power Level"), 4), [H.set("Pop Text", join("ULTRA ", join(V("Hero Title"), "!")))],
                  [H.set("Pop Text", join("SUPER ", join(V("Hero Title"), "!")))]),
            pose("charge up"), H.broadcast("transform"), H.broadcast("shockwave"), H.broadcast("ki burst"),
        ]),
        H.repeat(4, [H.dx(2), H.wait(0.04), H.dx(-2), H.wait(0.04)]),
        H.say(""), H.set("Powering", 0), H.set("Ki", 0), H.effect("BRIGHTNESS", 0), pose("idle"), H.set("Hero Lock", 0),
        note="Powering up, Dragon Ball style: crouch, yell HAAAAA!, and the power builds: the aura grows from a flicker to a "
             "blaze, energy streams upward, the screen darkens and the hero glows, then a burst of light. "
             "The ground shakes and rocks float up. "
             "From power level 3 the hair turns golden (silver at level 5) for the rest of the fight.",
    )
    H.on_msg(
        "super ready",
        H.if_(and_(eq(V("Fight On"), 1), eq(V("Powering"), 0)), [
            H.set("Powering", 2), H.broadcast("ki flare"), H.wait(0.8), H.if_(eq(V("Powering"), 2), [H.set("Powering", 0)]),
        ]),
        note="A quick flare of power when the SUPER bar fills up. You can keep fighting while it flares.",
    )
    H.on_msg("hero line", H.say(V("Line")), H.set("Line Until", add(TIMER, V("Line Secs"))),
             H.wait_until(or_(gt(TIMER, V("Line Until")), eq(V("Skip"), 1))), H.say(""))
    H.on_msg("enemy down", H.wait(1.3), H.set_y(GROUND), H.clear_fx(), pose("win"),
             H.if_(eq(V("Mode"), "story"), [H.say("Yes!", 1.2)], [H.say(join("Wave ", join(V("Wave"), " clear!")), 1.2)]))
    H.on_msg("hero down", H.set_y(GROUND), H.clear_fx(), pose("down"))
    H.on_msg("ending", H.point(90), H.goto(-170, GROUND), pose("win"))

    # ------------------------------------------------------------ enemy --
    enemy = game.sprite("Enemy", x=150, y=GROUND, size=80)
    for e in ENEMIES:
        angry = "angry" if e["n"] >= 3 else "smile"
        for p in ("idle", "windup", "attack", "hurt", "down", "idle b", "walk 1", "walk 2", "walk 3", "walk 4", "hurt high"):
            if e["gear"] == "robot":
                rp = {"idle b": "idle", "hurt high": "hurt"}.get(p, "idle" if p.startswith("walk") else p)
                enemy.costume(f"{e['key']} {p}", robot_svg(rp, mega=e["n"] == MEGA), 50, 168)
                continue
            src = {"attack": {"rival": "punch", "ivy": "aim", "brute": "charge", "quake": "slam", "shadow": "special",
                              "ninja": "slash", "kage": "slash"}[e["key"]],
                   "windup": {"quake": "raise", "shadow": "raise"}.get(e["key"], "windup")}.get(p, p)
            face = {"hurt": "hurt", "down": "ko"}.get(p, angry)
            enemy.costume(f"{e['key']} {p}", fighter_svg(e["color"], src, e["gear"], face,
                                                        glow="#a855f7" if e["n"] == KING else None), 50, 168)
        if e["n"] == KING:
            enemy.costume("shadow angry", fighter_svg("#7f1d1d", "raise", "crown", "angry", glow="#ef4444"), 50, 168)
            enemy.costume("shadow spikes", spike_armor_svg(fighter_svg("#1e1b4b", "raise", "crown", "angry", glow="#a855f7")), 50, 168)
    E = enemy

    def enemy_say(message, secs=None):
        """The enemy talks through the Enemy Talk sprite, so the bubble stays below the health bars."""
        if secs is None:
            return E.set("Enemy Says", message)
        return [E.set("Enemy Says", message), E.wait(secs), E.set("Enemy Says", "")]
    E.say = enemy_say
    E.local("Pick", 1)
    E.local("Line Until", 0)

    def epose(name):
        return E.wear(join(V("Enemy Name"), " " + name))

    def swing():
        return E.set("Enemy Swing Until", add(TIMER, 0.3))

    def hit_hero():
        return [swing(), E.set("Hurt Power", V("Enemy Power")), E.broadcast("enemy hits hero")]

    def face_hero():
        return E.if_(lt(V("Hero X"), XPOS), [E.point(-90), E.set("Enemy Facing", -1)], [E.point(90), E.set("Enemy Facing", 1)])

    def pw(secs):
        return mul(secs, V("Pace"))

    def walker():
        return [
            E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(38, V("Enemy Body"))), lt(sub(V("Hero Y"), GROUND), 60)), [
                epose("attack"), *hit_hero(), E.wait(pw(0.3)), epose("idle"), E.wait(pw(0.45)),
            ], [
                E.move(V("Enemy Speed")), *E.clamp_x(-210, 210), E.wait(0.03),
            ]),
        ]

    def shot(high):
        return [
            epose("windup"), E.say("High!" if high else "Low!", pw(0.45)),
            E.set("Shot Y", GROUND + (125 if high else 18)), E.set("Shot Dir", V("Enemy Facing")),
            epose("attack"), E.broadcast("enemy shot", wait=True), epose("idle"),
        ]

    def thrower():
        return [
            E.if_(lt(abs_(sub(V("Hero X"), XPOS)), 130), [
                E.glide(0.35, add(XPOS, mul(-110, V("Enemy Facing"))), GROUND), *E.clamp_x(-205, 205), face_hero(),
            ]),
            E.wait(pw(0.35)),
            E.if_(eq(rnd(1, 2), 1), shot(False), shot(True)),
            E.wait(pw(0.55)),
        ]

    def charger():
        return [
            epose("windup"), E.say("Ready?", pw(0.75)),
            E.set("Pick", V("Hero X")), epose("attack"), E.broadcast("swing sfx"), swing(),
            E.glide(pw(0.4), V("Pick"), GROUND),
            E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(34, V("Enemy Body"))), lt(sub(V("Hero Y"), GROUND), 50)),
                  [*hit_hero(), E.broadcast("shake")]),
            epose("idle"), E.wait(pw(0.45)),
            E.glide(0.5, add(XPOS, mul(-100, V("Enemy Facing"))), GROUND), *E.clamp_x(-205, 205),
            E.wait(pw(0.3)),
        ]

    def smoke_here():
        return [E.set("Smoke X", XPOS), E.set("Smoke Y", add(GROUND, 40)), E.broadcast("smoke")]

    def slash_if_close():
        return E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(42, V("Enemy Body"))), lt(sub(V("Hero Y"), GROUND), 70)),
                     hit_hero())

    def teleport_slash():
        return [
            *smoke_here(), E.effect("GHOST", 100), E.wait(pw(0.35)),
            # reappear behind the hero
            E.set_x(sub(V("Hero X"), mul(70, V("Facing")))), *E.clamp_x(-205, 205), face_hero(),
            E.effect("GHOST", 0), *smoke_here(),
            epose("windup"), E.wait(pw(0.18)), epose("attack"), swing(), E.broadcast("swing sfx"), slash_if_close(),
            E.wait(pw(0.35)), epose("idle"),
        ]

    def dash_slash():
        return [
            epose("windup"), E.say("Hyah!", pw(0.35)), epose("attack"), swing(), E.broadcast("swing sfx"),
            E.set("Pick", V("Hero X")), E.glide(pw(0.22), V("Pick"), GROUND), slash_if_close(),
            E.glide(0.3, add(XPOS, mul(-80, V("Enemy Facing"))), GROUND), *E.clamp_x(-205, 205), epose("idle"),
            E.wait(pw(0.35)),
        ]

    def shuriken(high):
        return [
            epose("windup"), E.say("Shuriken!" if not high else "High!", pw(0.3)),
            E.set("Shot Y", GROUND + (125 if high else 18)), E.set("Shot Dir", V("Enemy Facing")),
            epose("attack"), E.broadcast("enemy shot", wait=True), epose("idle"),
        ]

    def summon(count):
        return E.if_(lt(V("Minions"), 3), [
            epose("windup"), E.say("NINJA SQUAD!", pw(0.6)), E.set("Summon Kind", "ninja"), E.set("Summon Count", count),
            E.broadcast("ninja summon"),
            epose("idle"), E.wait(pw(0.5)),
        ], [*teleport_slash()])

    def ninja():
        return [
            E.set("Pick", rnd(1, 4)),
            E.if_(eq(V("Pick"), 1), [*shuriken(False), E.wait(pw(0.3))]),
            E.if_(eq(V("Pick"), 2), dash_slash()),
            E.if_(eq(V("Pick"), 3), teleport_slash()),
            E.if_(eq(V("Pick"), 4), [E.if_(lt(V("Minions"), 1), [summon(1)], [*shuriken(True), E.wait(pw(0.3))])]),
        ]

    def kage_moves():
        return [
            E.set("Pick", rnd(1, 5)),
            # shuriken fan: low, high, low
            E.if_(eq(V("Pick"), 1), [*shuriken(False), *shuriken(True), *shuriken(False), E.wait(pw(0.4))]),
            E.if_(eq(V("Pick"), 2), [*teleport_slash(), *teleport_slash()]),
            E.if_(eq(V("Pick"), 3), dash_slash()),
            E.if_(eq(V("Pick"), 4), [E.if_(eq(V("Enemy Phase"), 2), [summon(3)], [summon(2)])]),
            E.if_(eq(V("Pick"), 5), [*teleport_slash(), *shuriken(False)]),
        ]

    def kage():
        return zaps(kage_moves())

    def stomper():
        return [
            epose("windup"), E.say("STOMP!", pw(0.6)), epose("attack"), swing(),
            E.dy(10), E.wait(0.05), E.set_y(GROUND), E.broadcast("shake"),
            E.set("Wave Dir", V("Enemy Facing")), E.broadcast("ground wave", wait=True),
            epose("idle"), E.wait(pw(0.5)),
            E.if_(gt(abs_(sub(V("Hero X"), XPOS)), 160), [E.repeat(8, [E.move(V("Enemy Speed"))]), *E.clamp_x(-205, 205)]),
        ]

    def spikebot():
        return [
            epose("windup"), E.say("SPIKES OUT!", pw(0.55)),
            E.set("Spikes", 1), epose("attack"), E.broadcast("spikes out"),
            E.set("Pick", 0),
            E.until(or_(gt(V("Pick"), 40), eq(V("Fight On"), 0)), [
                E.change("Pick", 1), E.move(mul(V("Enemy Speed"), 2)), *E.clamp_x(-210, 210),
                E.if_(or_(gt(XPOS, 209), lt(XPOS, -209)), [E.set("Pick", 99)]),
                E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(30, V("Enemy Body"))), lt(sub(V("Hero Y"), GROUND), 55)), [
                    *hit_hero(), E.broadcast("shake"), E.set("Pick", 99),
                ]),
            ]),
            E.set("Spikes", 0), epose("idle"),
            E.say("Cooling down...", pw(1.7)),
        ]

    def spike_roll(steps, speed_mul):
        return [
            E.set("Spikes", 1), epose("attack"), E.broadcast("spikes out"),
            E.set("Pick", 0),
            E.until(or_(gt(V("Pick"), steps), eq(V("Fight On"), 0)), [
                E.change("Pick", 1), E.move(mul(V("Enemy Speed"), speed_mul)), *E.clamp_x(-205, 205),
                E.if_(or_(gt(XPOS, 204), lt(XPOS, -204)), [E.set("Pick", 999)]),
                E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(30, V("Enemy Body"))), lt(sub(V("Hero Y"), GROUND), 70)), [
                    *hit_hero(), E.broadcast("shake"), E.set("Pick", 999),
                ]),
            ]),
        ]

    def megaspike():
        return zaps(megaspike_moves())

    def megaspike_moves():
        cool = mul(V("Pace"), 1.4)
        return [
            E.set("Spikes", 1), E.set("Pick", rnd(1, 3)),
            E.if_(eq(V("Pick"), 1), [epose("windup"), E.say("SPIKE ROLL!", pw(0.6)), *spike_roll(45, 2.2)]),
            E.if_(eq(V("Pick"), 2), [*shot(False), *shot(True),
                                      E.if_(eq(V("Enemy Phase"), 2), shot(False))]),
            E.if_(eq(V("Pick"), 3), [epose("windup"), E.say("SPIKE RAIN!", pw(0.6)), epose("attack"),
                                      E.broadcast("spike rain", wait=True)]),
            E.set("Spikes", 0), epose("idle"), E.say("Cooling down...", cool),
        ]

    def lightning():
        return [
            epose("windup"), E.say("LIGHTNING!", pw(0.5)), epose("attack"), swing(),
            E.repeat(V("Power Level"), [
                E.set("Bolt X", V("Hero X")), E.set("Bolt Y", GROUND), E.set("Bolt Owner", "enemy"),
                E.set("Bolt Power", V("Enemy Power")), E.set("Bolt Size", 100), E.broadcast("bolt"), E.wait(pw(0.45)),
            ]),
            epose("idle"), E.wait(pw(0.7)),
        ]

    def zaps(normal):
        """From power level 3, bosses sometimes call lightning instead (more bolts at higher levels)."""
        return [E.if_(and_(gt(V("Power Level"), 2), eq(rnd(1, 4), 1)), lightning(), normal)]

    def king():
        return zaps(king_moves())

    def king_moves():
        return [
            E.if_(eq(V("Enemy Phase"), 2), [E.set("Pick", rnd(1, 5))], [E.set("Pick", rnd(1, 4))]),
            E.if_(eq(V("Pick"), 5), [
                E.wear("shadow spikes"), E.set("Spikes", 1), E.broadcast("spikes out"), E.say("SPIKE ARMOR!", pw(0.5)),
                E.repeat(25, [E.move(V("Enemy Speed")), *E.clamp_x(-205, 205),
                              E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(30, V("Enemy Body"))),
                                         lt(sub(V("Hero Y"), GROUND), 60)), [*hit_hero()])]),
                E.wait(pw(0.6)), E.set("Spikes", 0), epose("idle"), E.wait(pw(0.4)),
            ]),
            E.if_(eq(V("Pick"), 1), charger()),
            E.if_(eq(V("Pick"), 2), [
                E.wait(pw(0.2)), *shot(False),
                E.if_(eq(V("Enemy Phase"), 2), shot(True)),
                E.wait(pw(0.3)),
            ]),
            E.if_(eq(V("Pick"), 3), stomper()),
            E.if_(eq(V("Pick"), 4), [E.repeat(12, [E.move(mul(V("Enemy Speed"), 1.5)), *E.clamp_x(-210, 210)]), *walker()]),
        ]

    E.local("Last X", 0)
    E.local("Look", "")
    E.on_flag(
        E.forever([
            E.set("Look", COSTUME),
            E.if_(and_(eq(V("State"), "fight"), or_(contains(V("Look"), "idle"), contains(V("Look"), "walk"))), [
                E.if_(gt(abs_(sub(XPOS, V("Last X"))), 0.6), [
                    E.wear(join(V("Enemy Name"), join(" walk ", add(floor_(mod(div(add(XPOS, 1000), 11), 4)), 1)))),
                ], [
                    E.if_(eq(mod(round_(mul(TIMER, 1.4)), 2), 0), [epose("idle")], [epose("idle b")]),
                ]),
            ]),
            E.set("Last X", XPOS),
        ]),
        note="Enemies breathe while they wait and walk with a stride cycle.",
    )
    E.on_flag(
        E.rotation_style("left-right"), E.hide(),
        E.forever([E.if_(eq(V("Wave Phase"), 0), [E.set("Enemy X", XPOS)])]),
        note="Enemy X is read by Hero and the weapons.",
    )
    E.on_msg(
        "fight on",
        E.until(eq(V("Fight On"), 0), [
            face_hero(),
            E.if_(or_(lt(TIMER, V("Enemy Stun Until")), eq(V("Mode"), "practice"), eq(V("Wave Phase"), 1)), [E.wait(0.05)], [
                E.if_(eq(V("Enemy Type"), 1), walker()),
                E.if_(eq(V("Enemy Type"), 2), thrower()),
                E.if_(eq(V("Enemy Type"), 3), charger()),
                E.if_(eq(V("Enemy Type"), SPIKEBOT), spikebot()),
                E.if_(eq(V("Enemy Type"), MEGA), megaspike()),
                E.if_(eq(V("Enemy Type"), NINJA), ninja()),
                E.if_(eq(V("Enemy Type"), KAGE), kage()),
                E.if_(eq(V("Enemy Type"), QUAKE), stomper()),
                E.if_(eq(V("Enemy Type"), KING), king()),
                E.if_(eq(V("Fight On"), 1), [epose("idle")]),
            ]),
        ]),
        note="One brain for every enemy. 1 Rival walks in and punches. 2 Ivy throws low and high shots. "
             "3 Brute says Ready? then charges where you were. 4 Spike Bot rolls at you with spikes out, then cools down. "
             "5 BOSS MEGA SPIKE: spike roll, spike shots and Spike Rain, then it cools down. "
             "6 Quake stomps a ground wave. 7 the Shadow King mixes them all, and grows Spike Armor when angry.",
    )
    E.on_msg("enemy hurt", E.if_(eq(rnd(1, 2), 1), [epose("hurt")], [epose("hurt high")]), E.move(-12), *E.clamp_x(-210, 210), E.effect("BRIGHTNESS", 60),
             E.wait(0.1), E.effect("BRIGHTNESS", 0))
    E.on_msg("king angry",
             E.if_(eq(V("Enemy Type"), KAGE), [E.say("Shadow clones... ATTACK!", 1.4), E.set("Summon Kind", "ninja"), E.set("Summon Count", 2),
                                               E.broadcast("ninja summon")]),
             E.if_(eq(V("Enemy Type"), KING), [E.wear("shadow angry"), E.say("You're strong... but I'm STRONGER!", 1.6),
                                                E.wear("shadow idle")],
                   [E.if_(eq(V("Enemy Type"), MEGA), [E.wear("megaspike attack"), E.say("OVERDRIVE!!", 1.2),
                                                      E.wear("megaspike idle")])]))
    for m in ("show title", "choose hero"):
        E.on_msg(m, E.hide())
    E.on_msg("fighters ready", E.show(), E.clear_fx(), E.size_to(V("Enemy Size")), E.point(-90), E.set("Enemy Facing", -1),
             E.goto(150, GROUND), epose("idle"), E.say(""), E.if_(eq(V("Wave Phase"), 1), [E.hide()]))
    E.on_msg("boss enter", E.clear_fx(), E.size_to(V("Enemy Size")), E.point(-90), E.set("Enemy Facing", -1),
             E.goto(170, GROUND), epose("idle"), E.set("Smoke X", 170), E.set("Smoke Y", add(GROUND, 40)), E.broadcast("smoke"),
             E.show(), E.say(V("Enemy Title"), 1.2),
             note="ADVENTURE: the stage boss bursts in after the waves.")
    E.on_msg("scene setup", E.show(), E.clear_fx(), E.size_to(V("Enemy Size")), E.point(-90), E.goto(150, GROUND), epose("idle"))
    E.on_msg("story scene", E.hide())
    E.on_msg("enemy line", E.say(V("Line")), E.set("Line Until", add(TIMER, V("Line Secs"))),
             E.wait_until(or_(gt(TIMER, V("Line Until")), eq(V("Skip"), 1))), E.say(""))
    E.on_msg("enemy down", E.say(""), E.set("Spikes", 0), E.wait(0.2), E.set_y(GROUND), epose("down"), E.wait(1.3),
             E.repeat(10, [E.effect_by("GHOST", 10), E.wait(0.03)]),
             E.if_(not_(and_(eq(V("Mode"), "story"), eq(V("Chapter"), len(CHAPTERS)))), [E.hide()]),
             E.effect("GHOST", 0))
    E.on_msg("hero down", E.wait(0.3), epose("idle"), E.say("Ha! Try again!", 2))
    E.on_msg("ending", E.show(), E.goto(170, GROUND), E.point(-90), E.wear("shadow down"))

    # ------------------------------------------------------- projectiles --
    shot_s = game.sprite("Enemy Shot", size=100, rotation="left-right")
    shot_s.costume("ball", shot_svg(), 14, 14)
    shot_s.costume("spike", spike_shot_svg(), 25, 10)
    shot_s.costume("shuriken", shuriken_svg(), 14, 14)
    S = shot_s
    S.local("Hit", 0)
    S.local("Spin", 0)
    S.on_flag(S.hide())
    S.on_msg(
        "enemy shot",
        S.set("Spin", 0), S.rotation_style("left-right"),
        S.if_(eq(V("Enemy Name"), "megaspike"), [S.wear("spike")], [
            S.if_(or_(eq(V("Enemy Name"), "ninja"), eq(V("Enemy Name"), "kage")),
                  [S.wear("shuriken"), S.set("Spin", 1), S.rotation_style("all around"), S.broadcast("shuriken sfx")],
                  [S.wear("ball")])]),
        S.point(mul(90, V("Shot Dir"))),
        S.goto(add(V("Enemy X"), mul(30, V("Shot Dir"))), V("Shot Y")), S.set("Hit", 0), S.show(), S.front(),
        S.set("Shot Cancel", 0), S.set("Shot Live", 1),
        S.until(or_(gt(abs_(XPOS), 235), eq(V("Hit"), 1), eq(V("Fight On"), 0), eq(V("Shot Cancel"), 1)), [
            S.dx(mul(12, V("Shot Dir"))), S.set("Shot X", XPOS), S.if_(eq(V("Spin"), 1), [S.turn(40)]),
            S.if_(and_(lt(abs_(sub(XPOS, V("Hero X"))), 18), gt(sub(V("Shot Y"), V("Hero Y")), -10),
                       lt(sub(V("Shot Y"), V("Hero Y")), 108)), [
                S.set("Hit", 1), S.set("Hurt Power", V("Enemy Power")), S.broadcast("enemy hits hero"),
            ]),
        ]),
        S.hide(), S.set("Shot Live", 0), S.set("Shot X", 999),
        note="Low shots fly at knee height: jump them. High shots fly over your head: stay down. Dodge works on both. "
             "A fireball can knock a shot out of the air.",
    )
    for m in FIGHT_HIDE:
        S.on_msg(m, S.hide())

    wave_s = game.sprite("Ground Wave", size=80, rotation="left-right")
    wave_s.costume("wave", wave_svg(), 50, 36)
    W = wave_s
    W.local("Hit", 0)
    W.on_flag(W.hide())
    W.on_msg(
        "ground wave",
        W.goto(add(V("Enemy X"), mul(40, V("Wave Dir"))), GROUND), W.set("Hit", 0), W.show(), W.front(),
        W.until(or_(gt(abs_(XPOS), 235), eq(V("Fight On"), 0)), [
            W.dx(mul(mul(V("Enemy Speed"), 3), V("Wave Dir"))),
            W.if_(and_(eq(V("Hit"), 0), lt(abs_(sub(XPOS, V("Hero X"))), 28), lt(sub(V("Hero Y"), GROUND), 25)), [
                W.set("Hit", 1), W.set("Hurt Power", V("Enemy Power")), W.broadcast("enemy hits hero"),
            ]),
        ]),
        W.hide(),
        note="The wave rolls along the ground. If Hero is up in the air, it rolls underneath.",
    )
    for m in FIGHT_HIDE:
        W.on_msg(m, W.hide())

    # ------------------------------------------------------------ weapons --
    held = game.sprite("Held Weapon", size=70, rotation="all around")
    for w in WEAPONS:
        held.costume(w["key"], weapon_svg(w["key"]), *WEAPON_GRIP.get(w["key"], (30, 66)))
    HW = held
    HW.local("Swing Until", 0)
    HW.local("C", 1)
    HW.local("D", 0)
    HW.on_flag(
        HW.hide(),
        HW.forever([
            HW.if_(and_(eq(V("State"), "fight"), not_(eq(V("Weapon"), "none")), eq(V("Boomerang Out"), 0)), [
                HW.wear(V("Weapon")),
                # the hand of whatever picture Hero shows right now (lists made by the build script)
                HW.set("C", ("of", "costume #", "Hero")),
                HW.goto(add(V("Hero X"), mul(mul(item("Hand X", V("C")), 0.75), V("Facing"))),
                        add(V("Hero Y"), mul(item("Hand Y", V("C")), 0.75))),
                HW.set("D", item("Hand Dir", V("C"))),
                HW.if_(lt(TIMER, V("Swing Until")), [HW.change("D", 35)]),
                # the weapon is drawn pointing up, so it lines up with the forearm at "forearm + 90"; mirror when facing left
                HW.if_(eq(V("Facing"), 1), [HW.point(add(V("D"), 90))], [HW.point(sub(90, V("D")))]),
                HW.show(), HW.front(),
            ], [HW.hide()]),
        ]),
        note="The weapon sits in Hero's front hand and lines up with the forearm, for every picture Hero can show "
             "(Hand X, Hand Y and Hand Dir are worked out from the poses when the game is built).",
    )
    HW.on_msg("swing", HW.set("Swing Until", add(TIMER, 0.15)), HW.broadcast("swing sfx"))
    HW.on_msg("weapon break",
              HW.set("Pop Text", join("Oh no! The ", join(V("Weapon"), " broke!"))), HW.broadcast("popup"),
              HW.set("Weapon", "none"), HW.set("Weapon Bonus", 0), HW.set("Weapon Reach", 0), HW.set("Weapon Uses", 0))

    drop = game.sprite("Weapon Drop", size=70, rotation="don't rotate")
    for w in WEAPONS:
        drop.costume(w["key"], weapon_svg(w["key"], sparkle=True), 30, 55 if w["key"] == "spear" else 40)
    D = drop
    D.local("Kind", "sword")
    D.local("Life", 0)
    D.local("Got", 0)
    equip = []
    for w in WEAPONS:
        equip.append(D.if_(eq(V("Kind"), w["key"]), [
            D.set("Weapon Bonus", w["bonus"]), D.set("Weapon Reach", w["reach"]), D.set("Weapon Uses", w["uses"]),
            D.set("Pop Text", w["shout"]),
        ]))
    D.on_flag(
        D.hide(),
        D.forever([
            D.if_(and_(eq(V("Fight On"), 1), eq(V("Weapon"), "none")), [
                D.wait(rnd(3, 7)),
                D.if_(and_(eq(V("Fight On"), 1), eq(V("Weapon"), "none")), [
                    D.set("Kind", rnd(1, len(WEAPONS))),
                    *[D.if_(eq(V("Kind"), w["n"]), [D.set("Kind", w["key"])]) for w in WEAPONS],
                    D.wear(V("Kind")), D.goto(rnd(-170, 60), 170), D.show(), D.front(),
                    D.until(lt(YPOS, GROUND + 30), [D.dy(-10)]), D.set_y(GROUND + 25),
                    D.set("Life", 0), D.set("Got", 0),
                    D.until(or_(eq(V("Got"), 1), gt(V("Life"), 150), eq(V("Fight On"), 0)), [
                        D.change("Life", 1),
                        D.if_(and_(lt(abs_(sub(XPOS, V("Hero X"))), 36), lt(sub(V("Hero Y"), GROUND), 60)), [D.set("Got", 1)]),
                        D.if_(gt(V("Life"), 110), [D.effect("GHOST", mul(sub(V("Life"), 110), 2))]),
                    ]),
                    D.hide(), D.effect("GHOST", 0),
                    D.if_(and_(eq(V("Got"), 1), eq(V("Fight On"), 1), eq(V("Weapon"), "none")), [
                        *equip, D.set("Weapon", V("Kind")), D.broadcast("popup"), D.broadcast("weapon get"),
                    ]),
                ]),
            ], [D.wait(0.2)]),
        ]),
        note="Every 3 to 7 seconds a weapon falls from the sky. Walk over it to pick it up. "
             "Sword: +4 power, longer reach, 10 swings. Hammer: +9 power and a shake, 5 swings. "
             "Boomerang: PUNCH throws it, 6 throws. Spear: +5 power and the longest reach, 8 jabs. "
             "Nunchucks: every punch hits twice, 12 swings. Shield: blocks most of the damage you take "
             "(each block uses it up a bit) and you can bash with it.",
    )
    for m in FIGHT_HIDE:
        D.on_msg(m, D.hide())

    apple = game.sprite("Apple", size=60, rotation="don't rotate")
    apple.costume("apple", apple_svg(), 30, 34)
    AP = apple
    AP.local("Life", 0)
    AP.local("Got", 0)
    AP.on_flag(
        AP.hide(),
        AP.forever([
            AP.if_(and_(eq(V("Fight On"), 1), eq(V("State"), "fight"), not_(eq(V("Mode"), "practice"))), [
                AP.wait(rnd(10, 16)),
                AP.if_(and_(eq(V("Fight On"), 1), lt(V("Hero HP"), V("Hero Max"))), [
                    AP.goto(rnd(-180, 120), 170), AP.show(), AP.front(),
                    AP.until(lt(YPOS, GROUND + 26), [AP.dy(-8), AP.turn(0)]), AP.set_y(GROUND + 22),
                    AP.set("Life", 0), AP.set("Got", 0),
                    AP.until(or_(eq(V("Got"), 1), gt(V("Life"), 160), eq(V("Fight On"), 0)), [
                        AP.change("Life", 1),
                        AP.if_(and_(lt(abs_(sub(XPOS, V("Hero X"))), 32), lt(sub(V("Hero Y"), GROUND), 60)), [AP.set("Got", 1)]),
                        AP.if_(gt(V("Life"), 120), [AP.effect("GHOST", mul(sub(V("Life"), 120), 2))]),
                    ]),
                    AP.hide(), AP.effect("GHOST", 0),
                    AP.if_(and_(eq(V("Got"), 1), eq(V("Fight On"), 1)), [
                        AP.change("Hero HP", APPLE_HEAL), AP.if_(gt(V("Hero HP"), V("Hero Max")), [AP.set("Hero HP", V("Hero Max"))]),
                        AP.set("Pop Text", f"YUM! +{APPLE_HEAL} HEALTH"), AP.broadcast("popup"), AP.broadcast("weapon get"),
                    ]),
                ]),
            ], [AP.wait(0.3)]),
        ]),
        note="Grok's healing apple: when you are hurt, an apple sometimes falls. Walk over it for +25 health.",
    )
    for m in FIGHT_HIDE:
        AP.on_msg(m, AP.hide())

    boom = game.sprite("Boomerang", size=60, rotation="all around")
    boom.costume("spin", weapon_svg("boomerang"), 30, 40)
    BM = boom
    BM.local("Dir", 1)
    BM.local("Hit", 0)
    BM.local("Steps", 0)
    BM.on_flag(BM.hide())
    BM.on_msg(
        "throw boomerang",
        BM.set("Dir", V("Facing")), BM.set("Hit", 0), BM.set("Steps", 0),
        BM.goto(add(V("Hero X"), mul(20, V("Dir"))), add(V("Hero Y"), 50)), BM.show(), BM.front(),
        BM.until(or_(gt(V("Steps"), 16), gt(abs_(XPOS), 230), eq(V("Hit"), 1)), [
            BM.change("Steps", 1), BM.dx(mul(15, V("Dir"))), BM.turn(45),
            BM.if_(lt(abs_(sub(XPOS, V("Enemy X"))), add(26, V("Enemy Body"))), [
                BM.set("Hit", 1), BM.set("Hit Power", BOOMERANG_HIT), BM.broadcast("hero hits"),
            ]),
        ]),
        BM.set("Steps", 0),
        BM.until(or_(lt(abs_(sub(XPOS, V("Hero X"))), 20), gt(V("Steps"), 45)), [
            BM.change("Steps", 1), BM.turn(45),
            BM.if_(lt(XPOS, V("Hero X")), [BM.dx(16)], [BM.dx(-16)]),
            BM.set_y(add(V("Hero Y"), 50)),
        ]),
        BM.hide(), BM.set("Boomerang Out", 0),
        BM.if_(lt(V("Weapon Uses"), 1), [BM.broadcast("weapon break")]),
        note="Flies out, hits once, then comes back to Hero's hand.",
    )
    for m in FIGHT_HIDE:
        BM.on_msg(m, BM.hide(), BM.set("Boomerang Out", 0))

    # ------------------------------------------------------------ smoke --
    sm = game.sprite("Smoke", size=60, rotation="don't rotate")
    sm.costume("puff", smoke_svg(), 45, 35)
    SM = sm
    SM.local("Is Clone", 0)
    SM.on_flag(SM.hide(), SM.set("Is Clone", 0))
    SM.on_msg("smoke", SM.if_(eq(V("Is Clone"), 0), [SM.goto(V("Smoke X"), V("Smoke Y")), SM.clone()]),
              note="A puff of smoke when a ninja vanishes or appears. Only the original makes clones.")
    SM.on_clone(SM.set("Is Clone", 1), SM.size_to(50), SM.effect("GHOST", 0), SM.show(), SM.front(), SM.broadcast("poof sfx"),
                SM.repeat(10, [SM.size_by(9), SM.effect_by("GHOST", 10), SM.dy(1), SM.wait(0.03)]), SM.delete_clone())
    for m in ("show title", "choose hero", "story scene", "brawl clear"):
        SM.on_msg(m, SM.if_(eq(V("Is Clone"), 1), [SM.delete_clone()]))

    # ---------------------------------------------------- ninja minions --
    nm = game.sprite("Ninja Minion", size=70, rotation="left-right")
    for pose_ in ("idle", "run 1", "run 2", "slash", "hurt", "hurt high", "flip", "down"):
        face = "ko" if pose_ == "down" else "smile"
        nm.costume(f"ninja {pose_}", fighter_svg("#374151", pose_, "ninja", face), 50, 168)
        grunt_pose = {"slash": "punch", "flip": "jump"}.get(pose_, pose_)
        nm.costume(f"grunt {pose_}", fighter_svg("#78716c", grunt_pose, "none", "hurt" if "hurt" in pose_ else face), 50, 168)
        robot_pose = {"run 1": "attack", "run 2": "windup", "slash": "attack", "hurt high": "hurt", "flip": "idle"}.get(pose_, pose_)
        nm.costume(f"robot {pose_}", robot_svg(robot_pose), 50, 168)
    NM = nm
    for name, value in (("Is Clone", 0), ("HP", MINION_HP), ("Hit Until", 0), ("Was Hit", 0), ("Atk Until", 0),
                        ("Dir", 1), ("D", 0), ("Side", 1), ("Gap", 34), ("Kind", "ninja"), ("Slot", 0), ("J", 0), ("Speed", 3)):
        NM.local(name, value)

    def mpose(name):
        return NM.wear(join(V("Kind"), " " + name))
    NM.on_flag(NM.hide(), NM.set("Is Clone", 0), NM.set("Minions", 0), NM.list_clear("M X"),
               NM.repeat(3, [NM.list_add("M X", 9999)]))
    NM.define(
        "pick slot",
        NM.set("Slot", 0), NM.set("J", 0),
        NM.repeat(3, [NM.change("J", 1),
                      NM.if_(and_(eq(V("Slot"), 0), not_(lt(item("M X", V("J")), 9000))), [NM.set("Slot", V("J"))])]),
        NM.if_(gt(V("Slot"), 0), [NM.list_set("M X", V("Slot"), XPOS)]),
    )
    NM.on_msg(
        "ninja summon",
        NM.if_(eq(V("Is Clone"), 0), [
            NM.repeat(V("Summon Count"), [
                NM.if_(and_(lt(V("Minions"), 3), eq(V("Fight On"), 1)), [
                    NM.set("Kind", V("Summon Kind")),
                    NM.if_(eq(V("Kind"), "mix"), [NM.set("J", rnd(1, 3)), *[NM.if_(eq(V("J"), i), [NM.set("Kind", k)])
                                                                            for i, k in enumerate(MINION_KINDS, start=1)]]),
                    NM.if_(eq(rnd(1, 2), 1), [NM.set("Side", -1)], [NM.set("Side", 1)]),
                    NM.goto(mul(V("Side"), rnd(150, 215)), GROUND), NM.call("pick slot"),
                    NM.if_(gt(V("Slot"), 0), [
                        NM.change("Minions", 1),
                        NM.set("Smoke X", XPOS), NM.set("Smoke Y", add(GROUND, 40)), NM.broadcast("smoke"), NM.clone(),
                    ]),
                    NM.wait(0.25),
                ]),
            ]),
        ]),
        note="Calls small enemies (up to 3 at once): ninjas, gray grunts or small robots (Summon Kind; \"mix\" picks any). "
             "MASTER KAGE's NINJA SQUAD and the ADVENTURE waves both use this.",
    )
    NM.on_clone(
        NM.set("Is Clone", 1), NM.set("Gap", rnd(26, 58)), NM.set("HP", round_(mul(add(MINION_HP, mul(2, V("Difficulty"))), add(1, mul(MINION_HP_PER_LEVEL, sub(V("Power Level"), 1)))))),
        NM.set("Was Hit", 0),
        NM.set("Atk Until", add(TIMER, 0.6)), NM.set("Speed", add(3, mul(0.5, V("Difficulty")))),
        NM.if_(eq(V("Kind"), "robot"), [NM.size_to(55), NM.change("Speed", 1.5), NM.change("HP", -2)], [NM.size_to(70)]),
        NM.if_(eq(V("Kind"), "grunt"), [NM.change("HP", 1)]),
        NM.change("HP", mul(2, sub(V("Lap"), 1))),
        mpose("flip"), NM.show(), NM.front(), NM.wait(0.15),
        NM.until(or_(lt(V("HP"), 1), eq(V("Fight On"), 0)), [
            NM.list_set("M X", V("Slot"), XPOS),
            NM.if_(eq(V("Was Hit"), 1), [
                NM.set("Was Hit", 0), NM.if_(eq(rnd(1, 2), 1), [mpose("hurt")], [mpose("hurt high")]),
                NM.effect("BRIGHTNESS", 60), NM.move(-14), *NM.clamp_x(-220, 220), NM.wait(0.15), NM.effect("BRIGHTNESS", 0),
            ], [
                NM.set("D", sub(V("Hero X"), XPOS)),
                NM.if_(gt(V("D"), 0), [NM.point(90)], [NM.point(-90)]),
                NM.if_(gt(abs_(V("D")), V("Gap")), [
                    NM.move(V("Speed")),
                    NM.if_(eq(mod(round_(mul(TIMER, 9)), 2), 0), [mpose("run 1")], [mpose("run 2")]),
                ], [
                    NM.if_(and_(gt(TIMER, V("Atk Until")), lt(abs_(V("D")), 45)), [
                        mpose("slash"), NM.broadcast("swing sfx"),
                        NM.if_(lt(sub(V("Hero Y"), GROUND), 50),
                               [NM.set("Hurt Power", add(3, V("Power Level"))), NM.broadcast("enemy hits hero")]),
                        NM.set("Atk Until", add(TIMER, sub(1.1, mul(0.1, V("Difficulty"))))), NM.wait(0.18),
                    ], [
                        mpose("idle"),
                        # too far to attack: step in now and then
                        NM.if_(and_(gt(TIMER, V("Atk Until")), eq(rnd(1, 20), 1)), [NM.set("Gap", rnd(26, 40))]),
                    ]),
                ]),
            ]),
        ]),
        NM.list_set("M X", V("Slot"), 9999),
        NM.if_(lt(V("HP"), 1), [
            mpose("down"), NM.change("Score", 50), NM.change("Beaten", 1), NM.wait(0.35),
        ]),
        NM.set("Smoke X", XPOS), NM.set("Smoke Y", add(GROUND, 30)), NM.broadcast("smoke"),
        NM.change("Minions", -1), NM.if_(lt(V("Minions"), 0), [NM.set("Minions", 0)]),
        NM.delete_clone(),
        note="One small enemy: runs at you, attacks when close, flinches when hit, vanishes in smoke when beaten. "
             "Robots are smaller and faster; grunts are a little tougher.",
    )
    NM.on_msg(
        "area hit",
        NM.if_(and_(eq(V("Is Clone"), 1), gt(V("HP"), 0), gt(TIMER, V("Hit Until")),
                    lt(abs_(sub(XPOS, V("Area X"))), add(V("Area R"), 14))), [
            NM.change("HP", sub(0, V("Area Power"))), NM.set("Hit Until", add(TIMER, 0.18)), NM.set("Was Hit", 1),
            NM.broadcast("brawl hit"),
            NM.if_(eq(V("Area Kind"), "fire"), [NM.set("Fire Stop", 1)]),
        ]),
        note="Your punches, kicks, fireballs, lightning and SUPER moves also hit ninjas near them.",
    )
    for m in ("show title", "choose hero", "story scene"):
        NM.on_msg(m, NM.if_(eq(V("Is Clone"), 1), [NM.delete_clone()], [NM.hide(), NM.set("Minions", 0)]))

    # ----------------------------------------------------------- shadows --
    for who, xvar, yvar, cond, scale in (
        ("Hero Shadow", V("Hero X"), V("Hero Y"), or_(eq(V("State"), "fight"), eq(V("State"), "over")), 75),
        ("Enemy Shadow", V("Enemy X"), None, and_(eq(V("State"), "fight"), gt(V("Enemy HP"), 0), eq(V("Wave Phase"), 0)), None),
    ):
        sh = game.sprite(who, size=100, rotation="don't rotate")
        sh.costume("shadow", shadow_svg(), 35, 8)
        SH = sh
        size = (sub(scale, mul(sub(yvar, GROUND), 0.3)) if yvar is not None else mul(V("Enemy Size"), 0.95))
        SH.on_flag(SH.hide(), SH.forever([
            SH.if_(cond, [
                SH.goto(xvar, add(GROUND, 1)), SH.size_to(size),
                *([SH.effect("GHOST", add(10, mul(sub(yvar, GROUND), 0.5)))] if yvar is not None else []),
                SH.back(), SH.show(),
            ], [SH.hide()]),
        ]), note="A shadow on the floor gives depth: it shrinks and fades when you jump.")

    # -------------------------------------------------------- spike rain --
    rain = game.sprite("Spike Rain", size=100, rotation="don't rotate")
    rain.costume("warning", warning_svg(), 30, 8)
    rain.costume("spike", falling_spike_svg(), 15, 62)
    RN = rain
    RN.local("Hit", 0)
    RN.on_flag(RN.hide())
    RN.local("Is Clone", 0)
    RN.on_msg(
        "spike rain",
        RN.if_(eq(V("Is Clone"), 0), [
            RN.wear("warning"),
            RN.goto(V("Hero X"), GROUND), RN.clone(),
            RN.repeat(RAIN_SPIKES - 1, [RN.goto(rnd(-210, 210), GROUND), RN.clone()]),
            RN.broadcast("spike fall sfx"),
            RN.wait(1.6),
        ]),
        note="One spike falls where the hero is standing and the rest land anywhere. A red mark shows where. Move away, or DODGE. "
             "Only the original makes spikes (clones hear messages too).",
    )
    RN.on_clone(
        RN.set("Is Clone", 1), RN.wear("warning"), RN.set_y(GROUND), RN.set("Hit", 0), RN.show(),
        RN.repeat(4, [RN.effect("GHOST", 50), RN.wait(0.09), RN.effect("GHOST", 0), RN.wait(0.09)]),
        RN.wear("spike"), RN.set_y(190), RN.front(),
        RN.until(or_(lt(YPOS, GROUND + 4), eq(V("Fight On"), 0)), [
            RN.dy(-22),
            RN.if_(and_(eq(V("Hit"), 0), lt(abs_(sub(XPOS, V("Hero X"))), 20),
                        lt(YPOS, add(V("Hero Y"), 120)), gt(YPOS, sub(V("Hero Y"), 10))), [
                RN.set("Hit", 1), RN.set("Hurt Power", RAIN_HURT), RN.broadcast("enemy hits hero"),
            ]),
        ]),
        RN.wait(0.25), RN.delete_clone(),
    )
    for m in FIGHT_HIDE:
        RN.on_msg(m, RN.hide())

    # ---------------------------------------------------------- fireball --
    glow = game.sprite("Charge Glow", size=30, rotation="don't rotate")
    glow.costume("glow", glow_svg(), 30, 30)
    CG = glow
    CG.on_flag(
        CG.hide(),
        CG.forever([
            CG.if_(and_(gt(V("Charge"), 0), eq(V("State"), "brawl")), [
                CG.goto(add(V("P1 Screen X"), mul(mul(V("P1 Screen Size"), 0.5), V("Facing"))),
                        add(V("P1 Screen Y"), mul(V("P1 Screen Size"), 0.9))),
                CG.size_to(mul(add(25, mul(V("Charge"), 0.9)), div(V("P1 Screen Size"), 75))), CG.show(), CG.front(),
            ]),
            CG.if_(and_(gt(V("Charge"), 0), eq(V("State"), "fight")), [
                CG.goto(add(V("Hero X"), mul(36, V("Facing"))), add(V("Hero Y"), 66)),
                CG.size_to(add(25, mul(V("Charge"), 0.9))),
                CG.if_(eq(V("Charge"), 100), [CG.effect("BRIGHTNESS", mul(30, mod(round_(mul(TIMER, 8)), 2)))],
                       [CG.effect("BRIGHTNESS", 0)]),
                CG.show(), CG.front(),
            ], [CG.hide()]),
        ]),
        note="The glowing ball in Hero's hand grows while FIRE is held.",
    )

    fb = game.sprite("Fireball", size=60, rotation="left-right")
    fb.costume("flame 1", fireball_svg(0), 54, 26)
    fb.costume("flame 2", fireball_svg(1), 54, 26)
    F = fb
    F.local("Power", 0)
    F.local("Dir", 1)
    F.local("Done", 0)
    F.on_flag(F.hide(), F.set("Fireball Out", 0))
    F.on_msg(
        "fire",
        F.set("Power", V("Fire Power")), F.set("Dir", V("Facing")), F.set("Done", 0),
        F.point(mul(90, V("Dir"))), F.size_to(add(35, mul(V("Power"), 0.9))),
        F.goto(add(V("Hero X"), mul(40, V("Dir"))), add(V("Hero Y"), 62)), F.show(), F.front(),
        F.until(or_(gt(abs_(XPOS), 235), eq(V("Done"), 1), eq(V("Fight On"), 0)), [
            F.dx(mul(add(9, div(V("Power"), 25)), V("Dir"))),
            F.if_(eq(mod(round_(mul(TIMER, 12)), 2), 0), [F.wear("flame 1")], [F.wear("flame 2")]),
            # knock an enemy shot out of the air
            F.if_(and_(eq(V("Shot Live"), 1), lt(abs_(sub(XPOS, V("Shot X"))), 26), lt(abs_(sub(YPOS, V("Shot Y"))), 34)), [
                F.set("Shot Cancel", 1), F.set("Pop Text", "BLOCKED!"), F.broadcast("popup"),
                F.if_(lt(V("Power"), 100), [F.set("Done", 1)]),
            ]),
            F.if_(gt(V("Minions"), 0), [
                F.set("Fire Stop", 0), F.set("Area X", XPOS), F.set("Area R", add(14, div(V("Power"), 8))),
                F.set("Area Power", add(3, round_(div(V("Power"), 12)))), F.set("Area Kind", "fire"), F.broadcast("area hit"),
                F.if_(and_(eq(V("Fire Stop"), 1), lt(V("Power"), 100)), [F.set("Done", 1)]),
            ]),
            F.if_(lt(abs_(sub(XPOS, V("Enemy X"))), add(add(14, V("Enemy Body")), div(V("Power"), 8))), [
                F.set("Done", 1),
                F.set("Hit Power", add(3, round_(div(V("Power"), 12)))),
                F.if_(eq(V("Power"), 100), [
                    F.change("Hit Power", FIRE_FULL_BONUS), F.set("Boom X", XPOS), F.broadcast("boom"), F.broadcast("shake"),
                ]),
                F.broadcast("hero hits"),
            ]),
        ]),
        F.hide(), F.set("Fireball Out", 0),
        note="Flies forward. Small fireball: 3 to 7 damage. Full power: 15 damage, a BOOM and a shake. "
             "It always gets past Spike Bot's spikes.",
    )
    for m in FIGHT_HIDE:
        F.on_msg(m, F.hide(), F.set("Fireball Out", 0))

    boom = game.sprite("Explosion", size=60, rotation="all around")
    boom.costume("boom", spark_svg().replace("#fde047", "#fb923c").replace("#f97316", "#dc2626"), 40, 40)
    BX = boom
    BX.on_flag(BX.hide())
    BX.on_msg("boom", BX.goto(V("Boom X"), add(GROUND, 70)), BX.size_to(60), BX.effect("GHOST", 0), BX.show(), BX.front(),
              BX.repeat(8, [BX.size_by(25), BX.turn(15), BX.effect_by("GHOST", 12), BX.wait(0.02)]), BX.hide())

    # ------------------------------------------------------- power aura --
    aura = game.sprite("Power Aura", size=75, rotation="don't rotate")
    for n, *_r in POWER_LEVELS:
        for fr in range(4):
            aura.costume(f"lv{n} {fr + 1}", aura_svg(fr, n), 75, 198)
    AU = aura
    AU.local("Lit", 0)
    AU.local("Grow", 1)
    powered = or_(eq(V("Super"), 100), eq(V("Hero Safe"), 2), eq(V("Charge"), 100), eq(V("Melee Charge"), 100))
    # 4 flame frames; higher levels (and a power-up building up) flicker faster
    rate = add(add(8, mul(3, V("Power Level"))), div(V("Ki"), 6))

    def frame_wear():
        return AU.wear(join("lv", join(V("Power Level"), join(" ", add(mod(floor_(mul(TIMER, rate)), 4), 1)))))
    flicker = frame_wear()
    AU.on_flag(
        AU.hide(),
        AU.forever([
            AU.if_(powered, [AU.set("Lit", 1)], [AU.set("Lit", 0)]),
            AU.if_(gt(V("Powering"), 0), [AU.set("Lit", 1)]),
            # higher level = brighter (less see-through), bigger, faster flicker; powered up = full blaze
            AU.effect("GHOST", sub(sub(88, mul(13, V("Power Level"))), mul(30, V("Lit")))),
            AU.effect("BRIGHTNESS", add(mul(5, V("Power Level")), mul(20, V("Lit")))),
            AU.set("Grow", add(add(0.92, mul(0.05, V("Power Level"))), mul(0.12, V("Lit")))),
            # a quick flare (SUPER ready): the aura surges and pulses
            AU.if_(eq(V("Powering"), 2), [AU.change("Grow", add(0.35, mul(0.12, mod(round_(mul(TIMER, 12)), 2))))]),
            # powering up: the aura starts small and faint and builds as Ki rises, bigger and brighter each level
            AU.if_(eq(V("Powering"), 1), [
                AU.set("Grow", mul(add(0.5, mul(0.0075, V("Ki"))), add(1, mul(0.12, V("Power Level"))))),
                AU.change("Grow", mul(mul(0.06, div(V("Ki"), 100)), mod(round_(mul(TIMER, 14)), 2))),
                AU.effect("GHOST", sub(85, mul(V("Ki"), add(0.4, mul(0.09, V("Power Level")))))),
                AU.effect("BRIGHTNESS", mul(V("Ki"), add(0.12, mul(0.06, V("Power Level"))))),
            ]),
            AU.if_(eq(V("State"), "fight"), [
                AU.goto(V("Hero X"), V("Hero Y")), AU.size_to(mul(75, V("Grow"))), flicker, AU.show(),
            ], [
                AU.if_(and_(eq(V("State"), "brawl"), eq(V("Brawl Live"), 1), eq(item("B Alive", 1), 1)), [
                    AU.goto(V("P1 Screen X"), V("P1 Screen Y")), AU.size_to(mul(V("P1 Screen Size"), V("Grow"))),
                    AU.if_(eq(V("Brawl On"), 1), [AU.show()], [AU.hide()]),
                ], [
                    AU.if_(and_(eq(V("State"), "title"), gt(V("Power Level"), 1)), [
                        AU.goto(-212, GROUND), AU.size_to(mul(90, V("Grow"))), AU.show(),
                    ], [AU.hide()]),
                ]),
            ]),
            AU.if_(not_(eq(V("State"), "fight")), [frame_wear()]),
        ]),
        note="Your aura shows your POWER LEVEL: red, orange, gold, blue, then purple-white with lightning sparks. "
             "Each level has more flames and layers, is brighter and bigger and flickers faster. While powering up it "
             "starts small and builds with Ki to a blaze. It blazes when you are powered up "
             "(SUPER full, during a SUPER or POWER move, or a full fireball charge).",
    )

    # -------------------------------------------------------- lightning --
    lt_ = game.sprite("Lightning", size=100, rotation="don't rotate")
    lt_.costume("bolt hero", bolt_svg("#fefce8", "#facc15"), 30, 420)
    lt_.costume("bolt enemy", bolt_svg("#fecaca", "#a855f7"), 30, 420)
    lt_.costume("warn", bolt_warning_svg(), 35, 9)
    LT = lt_
    for name, value in (("Is Clone", 0), ("Bx", 0), ("By", 0), ("Who", "hero"), ("Pw", 0), ("Sz", 100)):
        LT.local(name, value)
    LT.on_flag(LT.hide(), LT.set("Is Clone", 0))
    LT.on_msg(
        "bolt",
        LT.if_(eq(V("Is Clone"), 0), [
            LT.set("Bx", V("Bolt X")), LT.set("By", V("Bolt Y")), LT.set("Who", V("Bolt Owner")),
            LT.set("Pw", V("Bolt Power")), LT.set("Sz", V("Bolt Size")), LT.clone(),
        ]),
        note="Lightning from the sky. An enemy's bolt shows a yellow mark first: move away or DODGE. "
             "Only the original makes clones (clones hear messages too).",
    )
    LT.on_clone(
        LT.set("Is Clone", 1), LT.effect("GHOST", 0),
        LT.if_(eq(V("Who"), "enemy"), [
            LT.wear("warn"), LT.size_to(100), LT.goto(V("Bx"), V("By")), LT.show(),
            LT.repeat(4, [LT.effect("GHOST", 60), LT.wait(0.08), LT.effect("GHOST", 0), LT.wait(0.08)]),
        ]),
        LT.if_(eq(V("Who"), "enemy"), [LT.wear("bolt enemy")], [LT.wear("bolt hero")]),
        LT.size_to(V("Sz")), LT.goto(V("Bx"), V("By")), LT.show(), LT.front(), LT.broadcast("bolt strike"),
        LT.if_(and_(eq(V("Who"), "hero"), eq(V("Fight On"), 1)), [
            LT.set("Hit Power", V("Pw")), LT.broadcast("hero hits"),
            LT.if_(gt(V("Minions"), 0), [LT.set("Area X", V("Bx")), LT.set("Area R", 40), LT.set("Area Power", V("Pw")),
                                         LT.set("Area Kind", "bolt"), LT.broadcast("area hit")]),
        ]),
        LT.if_(and_(eq(V("Who"), "enemy"), eq(V("Fight On"), 1), lt(abs_(sub(V("Hero X"), V("Bx"))), 30)), [
            LT.set("Hurt Power", V("Pw")), LT.broadcast("enemy hits hero"),
        ]),
        LT.repeat(3, [LT.effect("GHOST", 0), LT.wait(0.04), LT.effect("GHOST", 55), LT.wait(0.04)]),
        LT.delete_clone(),
    )
    for m in ("show title", "choose hero", "story scene", "brawl clear"):
        LT.on_msg(m, LT.if_(eq(V("Is Clone"), 1), [LT.delete_clone()], [LT.hide()]))
    # BRAWL: your THUNDER hits every fighter near you
    LT.local("J", 0)
    LT.on_msg(
        "brawl bolt",
        LT.if_(eq(V("Is Clone"), 0), [
            LT.set("J", 0),
            LT.repeat(4, [
                LT.change("J", 1),
                LT.if_(and_(not_(eq(V("J"), V("Bolt From"))), eq(item("B Alive", V("J")), 1),
                            lt(abs_(sub(item("B X", V("J")), item("B X", V("Bolt From")))), mul(110, sub(V("Power Level"), 1)))), [
                    LT.list_set("B Hit", V("J"), add(item("B Hit", V("J")), add(6, mul(2, V("Power Level"))))),
                    LT.if_(gt(item("B X", V("J")), item("B X", V("Bolt From"))), [LT.set("Pw", 1)], [LT.set("Pw", -1)]),
                    LT.list_set("B KX", V("J"), mul(add(3, div(item("B Dmg", V("J")), 12)), V("Pw"))),
                    LT.list_set("B KY", V("J"), add(9, div(item("B Dmg", V("J")), 9))),
                    LT.set("Bx", mul(sub(item("B X", V("J")), V("Cam X")), V("Zoom"))),
                    LT.set("By", mul(sub(item("B Y", V("J")), V("Cam Y")), V("Zoom"))),
                    LT.set("Who", "brawl"), LT.set("Pw", 0), LT.set("Sz", mul(div(sub(200, V("By")), 420), 100)),
                    LT.clone(), LT.wait(0.12),
                ]),
            ]),
        ]),
    )

    bw = game.sprite("Boss Weapon", size=80, rotation="all around")
    bw.local("C", 1)
    bw.local("D", 0)
    for kind in ("club", "mace", "hammer", "dark sword", "katana"):
        bw.costume(kind, boss_weapon_svg(kind), 30, 66)
    BW = bw
    BW.on_flag(
        BW.hide(),
        BW.forever([
            BW.if_(and_(eq(V("State"), "fight"), not_(eq(V("Enemy Weapon"), "none")), gt(V("Enemy HP"), 0), eq(V("Wave Phase"), 0),
                        or_(eq(V("Fight On"), 1), gt(V("Enemy X"), -300))), [
                BW.wear(V("Enemy Weapon")),
                BW.size_to(mul(V("Enemy Size"), 0.8)),
                BW.set("C", ("of", "costume #", "Enemy")),
                BW.goto(add(V("Enemy X"), mul(mul(item("EHand X", V("C")), div(V("Enemy Size"), 100)), V("Enemy Facing"))),
                        add(("of", "y position", "Enemy"), mul(item("EHand Y", V("C")), div(V("Enemy Size"), 100)))),
                BW.set("D", item("EHand Dir", V("C"))),
                BW.if_(lt(TIMER, V("Enemy Swing Until")), [BW.change("D", 40)]),
                BW.if_(eq(V("Enemy Facing"), 1), [BW.point(add(V("D"), 90))], [BW.point(sub(90, V("D")))]),
                BW.show(),
            ], [BW.hide()]),
        ]),
        note="Bosses carry weapons: Brute a club, MEGA SPIKE a spiked mace, ninjas and MASTER KAGE a katana, Quake a hammer, the Shadow King a dark sword. "
             "Each adds 3 to their hits. It swings when they attack.",
    )
    for m in ("enemy down", "show title", "choose hero", "story scene"):
        BW.on_msg(m, BW.hide())

    # ------------------------------------------------------------ crown --
    crown = game.sprite("Crown", size=80, rotation="don't rotate")
    crown.costume("crown", crown_svg(), 22, 30)
    C = crown
    C.on_flag(
        C.hide(),
        C.forever([
            C.if_(and_(eq(V("Crown"), 1), or_(eq(V("State"), "fight"), and_(eq(V("State"), "over"), not_(eq(V("Mode"), "brawl"))))), [
                C.goto(V("Hero X"), add(V("Hero Y"), 104)), C.size_to(80), C.show(), C.front(),
            ], [
                C.if_(and_(eq(V("Crown"), 1), eq(V("State"), "brawl"), eq(item("B Alive", 1), 1)), [
                    C.goto(V("P1 Screen X"), add(V("P1 Screen Y"), mul(V("P1 Screen Size"), 1.4))),
                    C.size_to(mul(V("P1 Screen Size"), 1.05)), C.show(), C.front(),
                ], [C.if_(not_(eq(V("State"), "ending")), [C.hide()])]),
            ]),
        ]),
        note="Beat Story mode once and every fighter wears the Golden Crown.",
    )

    # -------------------------------------------------------------- HUD --
    def bar(name, x, y, width, height, value, maximum, colors=True, anchor_right=False):
        b = game.sprite(name, x=x, y=y, size=100, rotation="don't rotate")
        if colors:
            for c, fill in (("green", "#16a34a"), ("yellow", "#eab308"), ("red", "#dc2626")):
                b.costume(c, bar_svg(width, height, fill), width if anchor_right else 0, height / 2)
        else:
            b.costume("charging", bar_svg(width, height, "#f59e0b"), 0, height / 2)
            b.costume("full", bar_svg(width, height, "#fde047"), 0, height / 2)
        b.local("Pct", 100)
        b.on_flag(
            b.hide(),
            b.forever([
                b.if_(and_(eq(V("State"), "fight"), eq(V("Page HUD"), 0)), [
                    b.set("Pct", mul(div(value, maximum), 100)),
                    b.if_(lt(V("Pct"), 1), [b.set("Pct", 1)]),
                    b.size_to(V("Pct")),
                    *([b.if_(gt(V("Pct"), 60), [b.wear("green")],
                             [b.if_(gt(V("Pct"), 30), [b.wear("yellow")], [b.wear("red")])])] if colors else
                      [b.if_(eq(V("Super"), 100), [b.wear("full"),
                                                   b.effect("BRIGHTNESS", mul(25, mod(round_(mul(TIMER, 6)), 2)))],
                             [b.wear("charging"), b.effect("BRIGHTNESS", 0)])]),
                    b.goto(x, y), b.show(),
                ], [b.hide()]),
            ]),
        )
        return b

    def track(name, x, y, width, height, anchor_right=False):
        t = game.sprite(name, x=x, y=y, rotation="don't rotate")
        t.costume("track", bar_svg(width, height, "#334155"), width if anchor_right else 0, height / 2)
        t.on_flag(t.hide(), t.forever([t.if_(and_(eq(V("State"), "fight"), eq(V("Page HUD"), 0)), [t.goto(x, y), t.show()], [t.hide()])]))
        return t

    track("Hero Bar Back", -228, 156, 150, 16)
    bar("Hero Bar", -228, 156, 150, 16, V("Hero HP"), V("Hero Max"))
    track("Super Bar Back", -228, 138, 150, 10)
    bar("Super Bar", -228, 138, 150, 10, V("Super"), 100, colors=False)
    track("Enemy Bar Back", 228, 156, 150, 16, anchor_right=True)
    bar("Enemy Bar", 228, 156, 150, 16, V("Enemy HP"), V("Enemy Max"), anchor_right=True)

    hero_tag = game.sprite("Hero Tag", x=-228, y=174, rotation="don't rotate")
    for h in HEROES:
        hero_tag.costume(h["key"], tag_svg(h["name"], h["color"]), 0, 10)
    hero_tag.on_flag(hero_tag.hide(), hero_tag.forever([
        hero_tag.if_(and_(eq(V("State"), "fight"), eq(V("Page HUD"), 0)), [hero_tag.wear(V("Hero Name")), hero_tag.goto(-228, 174), hero_tag.show()],
                     [hero_tag.hide()])]))
    enemy_tag = game.sprite("Enemy Tag", x=228, y=174, rotation="don't rotate")
    for e in ENEMIES:
        word = e["tag"]
        enemy_tag.costume(e["key"], tag_svg(word, e["color"] if e["n"] != KING else "#581c87"), 12 + 10 * len(word), 10)
    enemy_tag.costume("squad", tag_svg("ENEMY WAVE", "#b45309"), 12 + 10 * len("ENEMY WAVE"), 10)
    enemy_tag.on_flag(enemy_tag.hide(), enemy_tag.forever([
        enemy_tag.if_(and_(eq(V("State"), "fight"), eq(V("Page HUD"), 0)), [
            enemy_tag.if_(eq(V("Wave Phase"), 1), [enemy_tag.wear("squad")], [enemy_tag.wear(V("Enemy Name"))]),
            enemy_tag.goto(228, 174), enemy_tag.show()],
                      [enemy_tag.hide()])]))

    # pop-up words (combo, perfect, weapon names) as clones that float up
    pop = game.sprite("Popup", size=100, rotation="don't rotate")
    pop.costume("dot", dot_svg(), 2, 2)
    P = pop
    P.local("My Text", "")
    P.on_flag(P.hide())
    P.local("Is Clone", 0)
    P.local("My Seq", 0)
    P.on_msg("popup", P.if_(eq(V("Is Clone"), 0), [
        P.set("My Text", V("Pop Text")), P.change("Pop Seq", 1),
        # top middle of the screen, above the fighters, so it never covers the fight
        P.if_(eq(V("State"), "brawl"), [P.goto(-70, 92)], [P.goto(-70, 80)]),
        P.clone()]),
             note="Shows Pop Text at the top middle of the screen, away from the fighters. A new pop-up replaces "
                  "the old one, so they never pile up. Clones hear messages too, so only the original makes new clones.")
    P.on_clone(P.set("Is Clone", 1), P.set("My Seq", V("Pop Seq")), P.show(), P.say(V("My Text")),
               P.repeat(18, [P.if_(gt(V("Pop Seq"), V("My Seq")), [P.delete_clone()]), P.wait(0.06)]), P.delete_clone())
    P.on_msg("super ready", P.if_(eq(V("Is Clone"), 0), [
        P.set("My Text", "SUPER READY! Tap SUPER"), P.change("Pop Seq", 1), P.goto(-70, 80), P.clone()]))

    talk = game.sprite("Enemy Talk", size=100, rotation="don't rotate")
    talk.costume("dot", dot_svg(), 2, 2)
    TK = talk
    TK.local("Said", "")
    TK.on_flag(
        TK.set("Enemy Says", ""), TK.set("Said", ""), TK.say(""), TK.show(),
        TK.forever([
            TK.if_(not_(eq(V("Enemy Says"), "")), [
                # beside the enemy, low enough that the bubble never covers the health bars at the top
                TK.goto(sub(V("Enemy X"), 30), TALK_Y),
                TK.if_(not_(eq(V("Said"), V("Enemy Says"))), [TK.set("Said", V("Enemy Says")), TK.say(V("Enemy Says"))]),
                TK.front(),
            ], [
                TK.if_(not_(eq(V("Said"), "")), [TK.set("Said", ""), TK.say("")]),
            ]),
        ]),
        note="Says what the enemy or boss says (Enemy Says), next to them but below the health bars.",
    )
    for m in ("show title", "choose hero", "brawl start", "intro"):
        TK.on_msg(m, TK.set("Enemy Says", ""))

    spark = game.sprite("Hit Spark", size=50, rotation="all around")
    spark.costume("spark", spark_svg(), 40, 40)
    SP = spark
    SP.on_flag(SP.hide())
    SP.local("Is Clone", 0)
    SP.on_msg("enemy hurt", SP.if_(eq(V("Is Clone"), 0), [SP.goto(V("Enemy X"), add(GROUND, 60)), SP.clone()]),
              note="Only the original makes sparks; clones hear messages too.")
    SP.on_msg("hero hurt", SP.if_(eq(V("Is Clone"), 0), [SP.goto(V("Hero X"), add(GROUND, 50)), SP.clone()]))
    SP.on_clone(SP.set("Is Clone", 1), SP.point(rnd(0, 90)), SP.size_to(40), SP.show(), SP.front(),
                SP.repeat(5, [SP.size_by(14), SP.effect_by("GHOST", 18), SP.wait(0.02)]), SP.delete_clone())

    banner = game.sprite("Banner", x=0, y=40, rotation="don't rotate")
    for key, word, fill in (("ready", "READY...", "#facc15"), ("fight", "FIGHT!", "#ef4444"), ("ko", "K.O.!", "#f97316"),
                            ("clear", "CHAPTER CLEAR!", "#22c55e"), ("wave clear", "WAVE CLEAR!", "#22d3ee"), ("boss", "BOSS FIGHT!", "#ef4444"), ("game", "GAME!", "#facc15"), ("stage clear", "STAGE CLEAR!", "#22c55e"), ("power up", "POWER UP!", "#a855f7")):
        banner.costume(key, banner_svg(word, fill), banner_size(word)[1] / 2, 45)
    BN = banner
    BN.on_flag(BN.hide())
    BN.on_msg("banner", BN.wear(V("Banner")), BN.goto(0, 40), BN.size_to(40), BN.show(), BN.front(),
              BN.repeat(6, [BN.size_by(10)]), BN.wait(0.7), BN.hide())
    for m in ("show title", "choose hero", "story scene", "game over"):
        BN.on_msg(m, BN.hide())

    # ----------------------------------------------------------- story --
    card = game.sprite("Story Card", x=0, y=30, rotation="don't rotate")
    card.costume("prologue", card_svg("THE GOLDEN CROWN", [
        "The Shadow King stole the", "Golden Crown of the Arena!", "Win it back, champion!"], "#7c3aed"), 210, 120)
    for i, c in enumerate(CHAPTERS, start=1):
        card.costume(f"chapter {i}", card_svg(c["title"], c["lines"], ["#2563eb", "#16a34a", "#dc2626", "#475569", "#991b1b", "#166534", "#7f1d1d", "#ea580c", "#4c1d95"][i - 1]), 210, 120)
    card.costume("game over", card_svg("GAME OVER", ["Tap RETRY to fight again", "or HOME for the title."], "#475569"), 210, 120)
    card.costume("arcade over", card_svg("GAME OVER", ["How far did you get?", "Check Score and Best.", "Tap RETRY or HOME."], "#db2777"), 210, 120)
    card.costume("brawl win", card_svg("YOU WIN!", ["Last fighter standing!", "Tap RETRY for the next stage", "or HOME."], "#16a34a"), 210, 120)
    card.costume("brawl lose", card_svg("KNOCKED OUT", ["You ran out of lives.", "Tap RETRY to try again", "or HOME."], "#475569"), 210, 120)
    card.costume("the end", card_svg("THE END", ["The Golden Crown is back!", "You are the CHAMPION.", "Now try ARCADE mode!"], "#ca8a04"), 210, 120)
    card.costume("angry", card_svg("HE'S ANGRY!", ["Faster, double shots,", "and SPIKE ARMOR!"], "#b91c1c"), 210, 120)
    card.costume("kage angry", card_svg("SHADOW CLONES!", ["MASTER KAGE calls", "more ninjas. Use POWER!"], "#7f1d1d"), 210, 120)
    card.costume("overdrive", card_svg("OVERDRIVE!", ["MEGA SPIKE is faster", "and shoots more spikes!"], "#b91c1c"), 210, 120)
    K = card
    K.local("Until", 0)

    def card_wait(secs):
        return [K.set("Until", add(TIMER, secs)), K.wait_until(or_(gt(TIMER, V("Until")), eq(V("Skip"), 1)))]

    def talk(who, text, secs=2.2):
        return K.if_(eq(V("Skip"), 0), [K.set("Line", text), K.set("Line Secs", secs),
                                         K.broadcast(f"{who} line", wait=True)])

    scenes = []
    for i, c in enumerate(CHAPTERS, start=1):
        lines = [talk(who, text) for who, text in c["talk"]]
        scenes.append(K.if_(eq(V("Chapter"), i), [
            *([K.wear("prologue"), K.size_to(100), K.goto(0, 30), K.show(), K.front(), *card_wait(3.2)] if i == 1 else []),
            K.wear(f"chapter {i}"), K.size_to(100), K.goto(0, 30), K.show(), K.front(), *card_wait(2.6), K.hide(),
            K.broadcast("scene setup", wait=True),
            *lines,
        ]))
    K.on_flag(K.hide())
    K.on_msg(
        "story scene",
        K.set("State", "story"), K.set("Skip", 0), K.hide(),
        K.broadcast("load enemy", wait=True),
        K.broadcast("skip on"),
        *scenes,
        K.broadcast("skip off"),
        K.broadcast("start fight"),
        note="Chapter card, then the hero and the enemy talk. SKIP jumps straight to the fight.",
    )
    K.on_msg(
        "ending",
        K.set("Skip", 0), K.broadcast("skip on"),
        talk("enemy", "No! My crown..."),
        talk("hero", "It belongs to the whole arena!"),
        K.broadcast("crown fall", wait=True),
        talk("hero", "I did it!"),
        K.broadcast("skip off"),
        K.set("Crown", 1),
        K.wear("the end"), K.size_to(70), K.goto(0, 82), K.show(), K.front(), K.wait(0.5),
        K.broadcast("show home"),
        note="After the Shadow King: the crown drops onto the hero. Beating Story once gives every fighter the crown.",
    )
    K.on_msg("king angry", K.if_(eq(V("Enemy Type"), KING), [K.wear("angry")],
                                 [K.if_(eq(V("Enemy Type"), KAGE), [K.wear("kage angry")], [K.wear("overdrive")])]), K.size_to(80), K.goto(0, 60), K.show(), K.front(), K.wait(1.4), K.hide())
    K.on_msg("game over", K.if_(eq(V("Mode"), "arcade"), [K.wear("arcade over")], [K.wear("game over")]),
             K.if_(eq(V("Mode"), "brawl"), [K.if_(eq(V("Brawl Winner"), V("My Slot")), [K.wear("brawl win")], [K.wear("brawl lose")])]),
             K.size_to(85), K.goto(0, -5), K.show(), K.front())
    for m in ("show title", "choose hero", "start fight", "fight on", "brawl start"):
        K.on_msg(m, K.hide(), K.size_to(100))

    C.on_msg("crown fall", C.goto(V("Hero X"), 190), C.show(), C.front(),
             C.glide(1.2, V("Hero X"), add(V("Hero Y"), 104)), C.wait(0.3))

    # ------------------------------------------------------- buttons --
    def button(name, label, fill, x, y, ink="#ffffff", width=62, height=44, size=12):
        b = game.sprite(name, x=x, y=y, rotation="don't rotate")
        b.costume("button", button_svg(label, fill, ink, width, height, size), width / 2, height / 2)
        b.on_flag(b.hide())
        return b

    controls = [
        ("Left Button", "◀ LEFT", "#0284c7", "move left"),
        ("Right Button", "RIGHT ▶", "#0284c7", "move right"),
        ("Jump Button", "JUMP", "#16a34a", "Want Jump"),
        ("Dodge Button", "DODGE", "#64748b", "Want Dodge"),
        ("Punch Button", "PUNCH", "#ea580c", "Want Punch"),
        ("Kick Button", "KICK", "#ca8a04", "Want Kick"),
        ("Fire Button", "FIRE", "#dc2626", "Fire Held"),
        ("Power Button", "POWER", "#7c3aed", "Want Power"),
        ("Super Button", "SUPER", "#475569", "Want Super"),
    ]
    for i, (name, label, fill, action) in enumerate(controls):
        x = -212 + 53 * i
        b = button(name, label, fill, x, -152, width=51, size=10)
        if action in ("Want Punch", "Want Kick"):
            held = action.replace("Want", "") + " Held"
            held = held.replace("  ", " ").strip()
            b.on_click(b.set(action, 1), b.set(held, 1), b.wait_until(not_(MOUSE_DOWN)), b.set(held, 0),
                       note=f"Tap for a quick move. Hold to charge a power move ({held}).")
        elif action == "Fire Held":
            b.on_click(b.set("Fire Held", 1), b.wait_until(not_(MOUSE_DOWN)), b.set("Fire Held", 0),
                       note="Hold to charge a fireball, let go to shoot.")
        elif action.startswith("move"):
            b.on_click(b.broadcast(action), b.wait(0.25),
                       b.until(not_(MOUSE_DOWN), [b.broadcast(action), b.wait(0.09)]),
                       note="Tap to step. Hold to keep walking.")
        else:
            b.on_click(b.set(action, 1), note=f"Sets {action}. Hero's loop does the move.")
        b.on_msg("fight on", b.goto(x, -152), b.if_(eq(V("Touch Pad"), 0), [b.show(), b.front()]),
                 note="Hidden in the Android app, which has its own joystick and buttons (Touch Pad is 1 there).")
        for m in FIGHT_HIDE:
            b.on_msg(m, b.hide())
        if name == "Super Button":
            b.costume("ready", button_svg("SUPER!", "#facc15", "#7c2d12", 51, 44, 10), 25.5, 22)
            b.on_flag(b.forever([b.if_(eq(V("Super"), 100), [b.wear("ready")], [b.wear("button")])]))

    badge = game.sprite("Power Badge", x=-160, y=-140, rotation="don't rotate")
    for n, *_r in POWER_LEVELS:
        badge.costume(f"lv{n}", power_badge_svg(n), 80, 15)
    PB = badge
    PB.on_flag(PB.hide())
    PB.on_msg("show title", PB.goto(-160, -140), PB.wear(join("lv", V("Power Level"))), PB.show(), PB.front(),
              note="Your POWER LEVEL on the title screen.")
    PB.on_msg("choose hero", PB.hide())
    practice = button("Practice Button", "PRACTICE", "#0d9488", 132, -90, width=100, height=36, size=13)
    practice.on_msg("show title", practice.goto(132, -90), practice.show(), practice.front())
    practice.on_msg("choose hero", practice.hide())
    practice.on_click(practice.set("Mode", "practice"), practice.broadcast("choose hero"),
                      note="Grok's practice fight: a dummy that never hits back and never goes down. Try every move.")

    helpb = button("Help Button", "?", "#2563eb", 214, -136, width=40, height=36, size=20)
    helpb.on_msg("show title", helpb.goto(214, -136), helpb.show(), helpb.front())
    helpb.on_msg("choose hero", helpb.hide())
    helpb.on_click(helpb.broadcast("show help"))
    card_help = game.sprite("Help Card", x=0, y=0, rotation="don't rotate")
    card_help.costume("help", help_svg(), 220, 160)
    HC = card_help
    HC.on_flag(HC.hide())
    HC.on_msg("show help", HC.size_to(85), HC.goto(0, 22), HC.show(), HC.front(), note="Grok's how-to-play card.")
    HC.on_click(HC.hide())
    for m in ("choose hero", "start fight", "brawl start"):
        HC.on_msg(m, HC.hide())

    snd = game.sprite("Sound Button", x=166, y=-136, rotation="don't rotate")
    snd.costume("on", speaker_svg(True), 24, 22)
    snd.costume("off", speaker_svg(False), 24, 22)
    SB = snd
    SB.on_flag(SB.hide())
    SB.on_msg("show title", SB.goto(166, -136), SB.if_(eq(V("Sound On"), 1), [SB.wear("on")], [SB.wear("off")]), SB.show(), SB.front())
    SB.on_msg("choose hero", SB.hide())
    SB.on_click(SB.set("Sound On", sub(1, V("Sound On"))), SB.if_(eq(V("Sound On"), 1), [SB.wear("on")], [SB.wear("off")]),
                note="Grok's sound on/off. The app remembers it.")

    ver = game.sprite("Version", x=214, y=-172, rotation="don't rotate")
    ver.costume("v", svg_doc(60, 22, '<rect width="60" height="22" fill="#000000" opacity="0.01"/>'), 30, 11)
    VR = ver
    VR.on_flag(VR.hide())
    VR.on_msg("show title", VR.goto(214, -172), VR.show())
    VR.on_msg("choose hero", VR.hide())
    VR.on_click(VR.broadcast("toggle debug"), note="Tap the version number to show or hide Mitch's debug overlay.")

    diff_btn = game.sprite("Level Button", x=-30, y=-90, rotation="don't rotate")
    for key, word, fill, *_ in DIFFICULTIES:
        diff_btn.costume(key, difficulty_svg(word, fill), 95, 20)
    DB = diff_btn
    def show_level():
        return [DB.if_(eq(V("Difficulty"), i), [DB.wear(k)]) for i, (k, *_r) in enumerate(DIFFICULTIES, start=1)]
    DB.on_flag(DB.hide())
    DB.on_msg("show title", DB.goto(-30, -90), *show_level(), DB.show(), DB.front())
    DB.on_msg("choose hero", DB.hide())
    DB.on_click(DB.change("Difficulty", 1), DB.if_(gt(V("Difficulty"), len(DIFFICULTIES)), [DB.set("Difficulty", 1)]),
                *show_level(), DB.broadcast("swing sfx"),
                note="Tap to change the level: EASY, NORMAL, HARD, CHAMPION. Higher levels give enemies more health "
                     "(longer fights), harder hits and faster attacks.")
    story_btn = button("Story Button", "STORY", "#2563eb", -130, -25, width=90, height=50, size=16)
    adv_btn = button("Adventure Button", "ADVENTURE", "#16a34a", -26, -25, width=110, height=50, size=14)
    arcade_btn = button("Arcade Button", "ARCADE", "#db2777", 78, -25, width=90, height=50, size=16)
    brawl_btn = button("Brawl Button", "BRAWL", "#ea580c", 176, -25, width=90, height=50, size=16)
    for b, mode in ((story_btn, "story"), (adv_btn, "adventure"), (arcade_btn, "arcade"), (brawl_btn, "brawl")):
        b.on_msg("show title", b.show(), b.front())
        b.on_msg("choose hero", b.hide())
        b.on_click(b.set("Mode", mode), b.broadcast("choose hero"))

    for i, h in enumerate(HEROES, start=1):
        x = -150 + 150 * (i - 1)
        c = game.sprite(f"Pick {h['name'].title()}", x=x, y=-10, rotation="don't rotate")
        c.costume("card", hero_card_svg(h), 70, 128)
        c.on_flag(c.hide())
        c.on_msg("choose hero", c.goto(x, -10), c.size_to(100), c.show())
        for m in ("show title", "hero picked"):
            c.on_msg(m, c.hide())
        c.on_click(c.set("Hero", i), c.broadcast("hero picked"),
                   note=f"{h['name']}: {h['trait']}. Super move: {h['special_name']}.")

    skip = button("Skip Button", "SKIP ▶▶", "#334155", 190, -152, width=80)
    skip.on_msg("skip on", skip.show(), skip.front())
    for m in ("skip off", "show title", "start fight"):
        skip.on_msg(m, skip.hide())
    skip.on_click(skip.set("Skip", 1), skip.hide(), note="Skips the talking, like a cutscene skip.")

    retry = button("Retry Button", "RETRY", "#16a34a", -70, -150, width=100, height=48, size=16)
    retry.on_msg("game over", retry.goto(-70, -150), retry.show(), retry.front())
    for m in ("show title", "start fight", "brawl start"):
        retry.on_msg(m, retry.hide())
    retry.on_click(
        retry.hide(),
        retry.if_(eq(V("Mode"), "arcade"), [retry.set("Wave", 1), retry.set("Score", 0), retry.set("Hero HP", V("Hero Max"))]),
        retry.set("Super", 0),
        retry.if_(eq(V("Mode"), "brawl"), [retry.set("Score", 0), retry.broadcast("brawl start")], [
            retry.if_(eq(V("Mode"), "adventure"), [retry.set("Hero HP", V("Hero Max")), retry.broadcast("adventure stage")],
                      [retry.broadcast("start fight")])]),
        note="Story: try the same chapter again (no talking). Arcade: a new run from wave 1.",
    )

    home = button("Home Button", "HOME", "#475569", 70, -150, width=100, height=48, size=16)
    home.on_msg("game over", home.goto(70, -150), home.show(), home.front())
    home.on_msg("show home", home.goto(0, -150), home.show(), home.front())
    for m in ("show title", "start fight", "brawl start"):
        home.on_msg(m, home.hide())
    home.on_click(home.hide(), home.broadcast("show title"))

    quit_btn = button("Quit Button", "✕", "#334155", 0, 165, width=30, height=26, size=14)
    # the app page has its own ✕ in its top bar (Page HUD = 1); the Scratch editor uses this one
    quit_btn.on_msg("fight on", quit_btn.if_(eq(V("Page HUD"), 0), [quit_btn.goto(0, 165), quit_btn.show(), quit_btn.front()]))
    quit_btn.on_msg("brawl go", quit_btn.if_(eq(V("Page HUD"), 0), [quit_btn.goto(0, 165), quit_btn.show(), quit_btn.front()]))
    quit_btn.on_msg("brawl end", quit_btn.hide())
    quit_btn.on_msg("choose hero", quit_btn.goto(-218, -160), quit_btn.show(), quit_btn.front())
    for m in ("show title", "hero down", "enemy down", "story scene", "hero picked"):
        quit_btn.on_msg(m, quit_btn.hide())
    quit_btn.on_click(quit_btn.hide(), quit_btn.set("Fight On", 0), quit_btn.broadcast("show title"),
                      note="Back to the title at any time.")

    game.brawl_slots = build_brawl(game, s, button, FIGHT_HIDE)
    hands = [costume_hand(c["name"], "hero") for c in game.get("Hero").costumes]
    ehands = [costume_hand(c["name"], "enemy") for c in game.get("Enemy").costumes]
    for prefix, rows in (("Hand", hands), ("EHand", ehands)):
        game.list(f"{prefix} X", [r[0] for r in rows])
        game.list(f"{prefix} Y", [r[1] for r in rows])
        game.list(f"{prefix} Dir", [r[2] for r in rows])
    return game


# -------------------------------------------------------------- checks --


def validate(game):
    errors = []
    names = {t.name for t in game.targets}
    if len(names) != len(game.targets):
        errors.append("duplicate sprite name")
    backdrops = {c["name"] for c in game.stage.costumes}
    for t in [game.stage, *game.targets]:
        costumes = {c["name"] for c in t.costumes}
        sounds = {s["name"] for s in t.sounds}
        known = {vid for _n, (vid, _v) in t.locals.items()} | {vid for _n, (vid, _v) in game.globals.items()}
        for bid, b in t.blocks.items():
            op = b["opcode"]
            if op == "looks_costume" and b["fields"]["COSTUME"][0] not in costumes:
                errors.append(f"{t.name}: costume {b['fields']['COSTUME'][0]}")
            if op == "looks_backdrops" and b["fields"]["BACKDROP"][0] not in backdrops:
                errors.append(f"{t.name}: backdrop {b['fields']['BACKDROP'][0]}")
            if op == "sound_sounds_menu" and b["fields"]["SOUND_MENU"][0] not in sounds:
                errors.append(f"{t.name}: sound {b['fields']['SOUND_MENU'][0]}")
            if "LIST" in b["fields"] and b["fields"]["LIST"][1] not in getattr(game, "lists", {}).values():
                errors.append(f"{t.name}: list {b['fields']['LIST']}")
            if "VARIABLE" in b["fields"] and b["fields"]["VARIABLE"][1] not in known:
                errors.append(f"{t.name}: variable {b['fields']['VARIABLE']}")
            if b["next"] and t.blocks[b["next"]]["parent"] != bid:
                errors.append(f"{t.name}: next/parent {bid}")
            if not b["parent"] and not b["topLevel"]:
                errors.append(f"{t.name}: orphan {bid} {op}")
            if b["parent"] and b["parent"] not in t.blocks:
                errors.append(f"{t.name}: missing parent {bid}")
            for key, inp in b["inputs"].items():
                for item in inp[1:]:
                    if isinstance(item, str):
                        if item not in t.blocks:
                            errors.append(f"{t.name}: {bid}.{key} -> missing {item}")
                        elif t.blocks[item]["parent"] != bid:
                            errors.append(f"{t.name}: {bid}.{key} parent mismatch {item}")
                    elif isinstance(item, list) and item and item[0] == 12 and item[2] not in known:
                        errors.append(f"{t.name}: reporter variable {item}")
                    elif isinstance(item, list) and item and item[0] == 11 and item[2] not in game.broadcasts.values():
                        errors.append(f"{t.name}: broadcast {item}")
        if not t.costumes:
            errors.append(f"{t.name}: no costumes")
        names_ = [c["name"] for c in t.costumes]
        if len(names_) != len(set(names_)):
            errors.append(f"{t.name}: two costumes with the same name")
        # Clones hear every message too. A sprite that makes clones from a message
        # must check "Is Clone" or each clone makes more clones.
        if any(b["opcode"] == "control_create_clone_of" for b in t.blocks.values()) and "Is Clone" not in t.locals:
            errors.append(f"{t.name}: makes clones but has no Is Clone guard")
    # no two variables may share an id
    seen = {}
    for vid, owner in [(vid, "Stage") for _n, (vid, _v) in game.globals.items()] + \
            [(vid, t.name) for t in game.targets for _n, (vid, _v) in t.locals.items()]:
        if vid in seen and seen[vid] != owner or (vid in seen and owner == "Stage"):
            errors.append(f"variable id {vid} used twice ({seen[vid]} and {owner})")
        seen[vid] = owner
    # every message that is listened for is also sent, and the other way round
    sent, heard = set(), set()
    for t in [game.stage, *game.targets]:
        for b in t.blocks.values():
            if b["opcode"] in ("event_broadcast", "event_broadcastandwait"):
                sent.add(b["inputs"]["BROADCAST_INPUT"][1][1])
            if b["opcode"] == "event_whenbroadcastreceived":
                heard.add(b["fields"]["BROADCAST_OPTION"][0])
    for m in sorted(sent - heard):
        errors.append(f"message sent but nobody listens: {m}")
    for m in sorted(heard - sent):
        errors.append(f"message heard but never sent: {m}")
    if errors:
        raise SystemExit("validation failed:\n  " + "\n  ".join(errors))


def write_sb3(game):
    assets = {}
    targets = [game.stage.export(0)]
    assets.update(game.stage.assets)
    for i, t in enumerate(game.targets, start=1):
        targets.append(t.export(i))
        assets.update(t.assets)

    def monitor(name, x, y, visible=False):
        vid, value = game.globals[name]
        return {"id": vid, "mode": "default", "opcode": "data_variable", "params": {"VARIABLE": name},
                "spriteName": None, "value": value, "width": 0, "height": 0, "x": x, "y": y, "visible": visible,
                "sliderMin": 0, "sliderMax": 100, "isDiscrete": True}

    project = {
        "targets": targets,
        "monitors": [monitor("Score", 196, 28), monitor("Wave", 205, 54), monitor("Best", 200, 310)]
        + [dict(monitor(f"P{i} %", sx + 4, 6), mode="large")
           for i, sx in enumerate(getattr(game, "brawl_slots", []), start=1)]
        + [monitor(n, 4, 40 + 22 * i) for i, n in enumerate(("FPS", "State", "Mode", "Fight On", "Hero HP", "Enemy HP",
                                                             "Enemy Name", "Minions", "Power Level", "Brawl Live"))],
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "2.3.0", "agent": "arthurs-arena legends builder"},
    }
    SB3_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamp = (2026, 11, 5, 0, 0, 0)
    with zipfile.ZipFile(SB3_PATH, "w") as z:
        info = zipfile.ZipInfo("project.json", stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, json.dumps(project, separators=(",", ":")))
        for fn in sorted(assets):
            info = zipfile.ZipInfo(fn, stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, assets[fn])
    return project


# ------------------------------------------------------------- listing --


def listing(game):
    out = [
        "# Block listing for Arthur's Arena: Legends",
        "",
        "Made by `tools/build_legends_sb3.py` from the same blocks that are inside",
        "`projects/arthurs-arena-legends.sb3`. Use it to find a script in the editor.",
        "",
    ]

    def ex(t, inp):
        if inp is None:
            return "()"
        item = inp[1]
        if isinstance(item, list):
            if item[0] == 12:
                return f"({item[1]})"
            if item[0] == 11:
                return f"[{item[1]}]"
            return f"[{item[1]}]"
        b = t.blocks[item]
        op = b["opcode"]
        f = lambda k: ex(t, b["inputs"].get(k))  # noqa: E731
        sym = {"operator_add": "+", "operator_subtract": "-", "operator_multiply": "*", "operator_divide": "/",
               "operator_mod": "mod", "operator_equals": "=", "operator_lt": "<", "operator_gt": ">",
               "operator_and": "and", "operator_or": "or"}
        if op in sym:
            k1, k2, _ = BINARY[op]
            return f"<{f(k1)} {sym[op]} {f(k2)}>" if op in BOOL_OPS else f"({f(k1)} {sym[op]} {f(k2)})"
        if op == "operator_not":
            return f"<not {f('OPERAND')}>"
        if op == "operator_random":
            return f"(pick random {f('FROM')} to {f('TO')})"
        if op == "operator_join":
            return f"(join {f('STRING1')} {f('STRING2')})"
        if op == "operator_round":
            return f"(round {f('NUM')})"
        if op == "operator_mathop":
            return f"({b['fields']['OPERATOR'][0]} of {f('NUM')})"
        if op == "sensing_of":
            return f"([{b['fields']['PROPERTY'][0]}] of {f('OBJECT')})"
        if op == "looks_costumenumbername":
            return "(costume name)"
        if op == "operator_contains":
            return f"<{f('STRING1')} contains {f('STRING2')}?>"
        if op == "data_itemoflist":
            return f"(item {f('INDEX')} of [{b['fields']['LIST'][0]}])"
        if op == "data_lengthoflist":
            return f"(length of [{b['fields']['LIST'][0]}])"
        if op == "sensing_keypressed":
            return f"<key {f('KEY_OPTION')} pressed?>"
        if op in ("looks_costume", "looks_backdrops", "sound_sounds_menu", "control_create_clone_of_menu", "sensing_keyoptions",
                  "sensing_of_object_menu"):
            return f"({list(b['fields'].values())[0][0]})"
        names = {"motion_xposition": "(x position)", "motion_yposition": "(y position)", "sensing_timer": "(timer)",
                 "sensing_mousedown": "<mouse down?>", "looks_size": "(size)"}
        return names.get(op, f"({op})")

    def stack(t, bid, depth):
        lines = []
        while bid:
            b = t.blocks[bid]
            op = b["opcode"]
            pad = "    " * depth
            f = lambda k: ex(t, b["inputs"].get(k))  # noqa: E731
            var = b["fields"].get("VARIABLE", [""])[0]
            text = {
                "event_whenflagclicked": "when green flag clicked",
                "event_whenthisspriteclicked": "when this sprite clicked",
                "control_start_as_clone": "when I start as a clone",
                "data_setvariableto": f"set [{var}] to {f('VALUE')}",
                "data_changevariableby": f"change [{var}] by {f('VALUE')}",
                "data_showvariable": f"show variable [{var}]",
                "data_hidevariable": f"hide variable [{var}]",
                "control_wait": f"wait {f('DURATION')} seconds",
                "control_wait_until": f"wait until {f('CONDITION')}",
                "control_forever": "forever",
                "control_repeat": f"repeat {f('TIMES')}",
                "control_repeat_until": f"repeat until {f('CONDITION')}",
                "control_if": f"if {f('CONDITION')} then",
                "control_if_else": f"if {f('CONDITION')} then",
                "event_broadcast": f"broadcast {f('BROADCAST_INPUT')}",
                "event_broadcastandwait": f"broadcast {f('BROADCAST_INPUT')} and wait",
                "looks_switchcostumeto": f"switch costume to {f('COSTUME')}",
                "looks_switchbackdropto": f"switch backdrop to {f('BACKDROP')}",
                "looks_say": f"say {f('MESSAGE')}",
                "looks_sayforsecs": f"say {f('MESSAGE')} for {f('SECS')} seconds",
                "looks_show": "show", "looks_hide": "hide",
                "looks_setsizeto": f"set size to {f('SIZE')} %",
                "looks_changesizeby": f"change size by {f('CHANGE')}",
                "looks_cleargraphiceffects": "clear graphic effects",
                "motion_gotoxy": f"go to x: {f('X')} y: {f('Y')}",
                "motion_glidesecstoxy": f"glide {f('SECS')} secs to x: {f('X')} y: {f('Y')}",
                "motion_setx": f"set x to {f('X')}", "motion_sety": f"set y to {f('Y')}",
                "motion_changexby": f"change x by {f('DX')}", "motion_changeyby": f"change y by {f('DY')}",
                "motion_movesteps": f"move {f('STEPS')} steps",
                "motion_turnright": f"turn right {f('DEGREES')} degrees",
                "motion_pointindirection": f"point in direction {f('DIRECTION')}",
                "sound_play": f"start sound {f('SOUND_MENU')}",
                "sound_stopallsounds": "stop all sounds",
                "data_addtolist": f"add {f('ITEM')} to [{b['fields'].get('LIST', [''])[0]}]",
                "data_deletealloflist": f"delete all of [{b['fields'].get('LIST', [''])[0]}]",
                "data_deleteoflist": f"delete {f('INDEX')} of [{b['fields'].get('LIST', [''])[0]}]",
                "data_replaceitemoflist": f"replace item {f('INDEX')} of [{b['fields'].get('LIST', [''])[0]}] with {f('ITEM')}",
                "control_create_clone_of": "create clone of (myself)",
                "control_delete_this_clone": "delete this clone",
                "control_stop": f"stop [{b['fields'].get('STOP_OPTION', [''])[0]}]",
            }.get(op)
            if op == "procedures_definition":
                proto = t.blocks[b["inputs"]["custom_block"][1]]
                text = f"define ({proto['mutation']['proccode']})   [run without screen refresh]"
            elif op == "procedures_call":
                text = f"({b['mutation']['proccode']})"
            elif op == "event_whenbroadcastreceived":
                text = f"when I receive [{b['fields']['BROADCAST_OPTION'][0]}]"
            elif op == "event_whenstageclicked":
                text = "when stage clicked"
            elif op == "event_whenkeypressed":
                text = f"when [{b['fields']['KEY_OPTION'][0]}] key pressed"
            elif op == "looks_seteffectto":
                text = f"set [{b['fields']['EFFECT'][0].lower()}] effect to {f('VALUE')}"
            elif op == "looks_changeeffectby":
                text = f"change [{b['fields']['EFFECT'][0].lower()}] effect by {f('CHANGE')}"
            elif op == "looks_gotofrontback":
                text = f"go to [{b['fields']['FRONT_BACK'][0]}] layer"
            elif op == "motion_setrotationstyle":
                text = f"set rotation style [{b['fields']['STYLE'][0]}]"
            lines.append(pad + (text or op))
            for key in ("SUBSTACK", "SUBSTACK2"):
                if key in b["inputs"]:
                    if key == "SUBSTACK2":
                        lines.append(pad + "else")
                    lines += stack(t, b["inputs"][key][1], depth + 1)
            if op in ("control_if", "control_if_else", "control_forever", "control_repeat", "control_repeat_until"):
                lines.append(pad + "end")
            bid = b["next"]
        return lines

    for t in [game.stage, *game.targets]:
        out.append(f"## {t.name}")
        out.append("")
        out.append("Costumes: " + ", ".join(c["name"] for c in t.costumes))
        if t.sounds:
            out.append("Sounds: " + ", ".join(s["name"] for s in t.sounds))
        if t.locals:
            out.append("Sprite-only variables: " + ", ".join(t.locals))
        out.append("")
        for bid, b in t.blocks.items():
            if b["topLevel"]:
                out.append("```")
                out += stack(t, bid, 0)
                out.append("```")
                if "comment" in b:
                    out.append("")
                    out.append("> " + t.comments[b["comment"]]["text"])
                out.append("")
    return "\n".join(out) + "\n"


def main():
    game = build()
    validate(game)
    write_sb3(game)
    LISTING_PATH.write_text(listing(game), encoding="utf-8")
    blocks = sum(len(t.blocks) for t in [game.stage, *game.targets])
    print(f"wrote {SB3_PATH.relative_to(ROOT)} and {LISTING_PATH.relative_to(ROOT)}")
    print(f"sprites: {len(game.targets)}  blocks: {blocks}  messages: {len(game.broadcasts)}")


if __name__ == "__main__":
    sys.exit(main())
