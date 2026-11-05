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
    dict(n=4, key="quake", tag="QUAKE", color="#ea580c", size=120, hp=50, pow=12, speed=4, body=26, gear="spikes"),
    dict(n=5, key="shadow", tag="SHADOW KING", color="#1e1b4b", size=125, hp=90, pow=12, speed=4, body=26, gear="crown"),
]

CHAPTERS = [
    # backdrop, chapter card lines, dialogue lines (speaker, text)
    dict(backdrop="Yard", title="CHAPTER 1", lines=["The Training Yard", "Beat the Rival to get", "through the gate."],
         talk=[("enemy", "Nobody gets past the gate!"), ("hero", "Then let's fight!")]),
    dict(backdrop="Woods", title="CHAPTER 2", lines=["Ivy's Woods", "Low shot? JUMP!", "High shot? Stay down."],
         talk=[("enemy", "My vines see everything."), ("hero", "Then watch me jump!")]),
    dict(backdrop="Pass", title="CHAPTER 3", lines=["The Rocky Pass", "Brute says Ready?", "then charges. Move!"],
         talk=[("enemy", "BRUTE... SMASH!"), ("hero", "Not if I move first!")]),
    dict(backdrop="Volcano", title="CHAPTER 4", lines=["The Volcano Gate", "Quake stomps the ground.", "Jump over the wave!"],
         talk=[("enemy", "Feel the ground shake!"), ("hero", "I'll jump right over it!")]),
    dict(backdrop="Castle", title="FINAL CHAPTER", lines=["Shadow Castle", "He uses every trick.", "Use your SUPER!"],
         talk=[("enemy", "The Golden Crown is MINE!"), ("hero", "Not for long!")]),
]

WEAPONS = [
    # random number, key, bonus, reach, uses
    dict(n=1, key="sword", bonus=4, reach=28, uses=10, shout="SWORD!"),
    dict(n=2, key="hammer", bonus=9, reach=12, uses=5, shout="HAMMER!"),
    dict(n=3, key="boomerang", bonus=0, reach=0, uses=6, shout="BOOMERANG!"),
]
BOOMERANG_HIT = 7

PUNCH_REACH = 70
KICK_REACH = 82
SUPER_PER_HIT = 6
SUPER_PER_HURT = 8
SUPER_PER_PERFECT = 25
COMBO_WINDOW = 1.2
COMBO_BONUS = 3
ARCADE_HEAL = 30

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
    if gear == "crown":
        return (
            f'<path d="M{hx - 15} {hy - 12} L{hx - 15} {hy - 30} L{hx - 7} {hy - 20} L{hx} {hy - 34} L{hx + 7} {hy - 20} '
            f'L{hx + 15} {hy - 30} L{hx + 15} {hy - 12} Z" fill="#a855f7" stroke="#facc15" stroke-width="2"/>'
        )
    return ""


def fighter_svg(color, pose, gear="none", face="smile", glow=None):
    """A stick figure in a 100 by 180 box, facing right. Feet sit on y=168."""
    lines = POSES[pose]
    hx, hy = HEAD.get(pose, (lines[0][0], 48 if pose not in ("jump", "hurt", "win", "dodge", "special") else 52))
    if pose == "dodge":
        hx, hy = 44, 62
    parts = []
    if glow:
        parts.append(f'<ellipse cx="50" cy="100" rx="46" ry="78" fill="{glow}" opacity="0.35"/>')
    parts.append('<g fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">')
    parts.append(f'<circle cx="{hx}" cy="{hy}" r="18" fill="#ffffff"/>')
    parts += [f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>' for a, b, c, d in lines]
    parts.append("</g>")
    parts.append(f'<g fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">')
    parts.append(f'<circle cx="{hx}" cy="{hy}" r="16" fill="{color}"/>')
    parts += [f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>' for a, b, c, d in lines]
    parts.append("</g>")
    parts.append(gear_svg(gear, color, hx, hy))
    # face looks to the right
    ex = hx + 4
    if face == "ko":
        parts.append(
            f'<path d="M{ex - 4} {hy - 5} l5 5 m0 -5 l-5 5 M{ex + 6} {hy - 5} l5 5 m0 -5 l-5 5" stroke="#ffffff" stroke-width="2"/>'
        )
    else:
        parts.append(f'<circle cx="{ex - 2}" cy="{hy - 2}" r="2.4" fill="#ffffff"/>')
        parts.append(f'<circle cx="{ex + 8}" cy="{hy - 2}" r="2.4" fill="#ffffff"/>')
    if face == "angry":
        parts.append(
            f'<path d="M{ex - 6} {hy - 10} L{ex + 1} {hy - 6} M{ex + 13} {hy - 10} L{ex + 6} {hy - 6}" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>'
        )
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
    "hit": [(0.09, 300, 80, "noise", 0.7)],
    "big hit": [(0.05, 500, 200, "noise", 0.9), (0.2, 120, 40, "sine", 0.9)],
    "hurt": [(0.16, 300, 120, "square", 0.35)],
    "jump": [(0.12, 300, 700, "square", 0.25)],
    "swing": [(0.12, 900, 300, "noise", 0.35)],
    "pickup": [(0.08, 660, 660, "square", 0.3), (0.12, 990, 990, "square", 0.3)],
    "super": [(0.45, 200, 1200, "square", 0.3)],
    "perfect": [(0.08, 1200, 1200, "sine", 0.5), (0.18, 1600, 1600, "sine", 0.5)],
    "ko": [(0.6, 500, 60, "square", 0.35)],
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
YPOS = ("motion_yposition",)
TIMER = ("sensing_timer",)
MOUSE_DOWN = ("sensing_mousedown",)
SIZE = ("looks_size",)

BOOL_OPS = {"operator_equals", "operator_lt", "operator_gt", "operator_and", "operator_or", "operator_not", "sensing_mousedown"}
BINARY = {
    "operator_add": ("NUM1", "NUM2", "num"),
    "operator_subtract": ("NUM1", "NUM2", "num"),
    "operator_multiply": ("NUM1", "NUM2", "num"),
    "operator_divide": ("NUM1", "NUM2", "num"),
    "operator_mod": ("NUM1", "NUM2", "num"),
    "operator_random": ("FROM", "TO", "num"),
    "operator_join": ("STRING1", "STRING2", "text"),
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
        self.locals[name] = (f"var_{self.prefix}{name.replace(' ', '_')}", value)

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
        elif op in ("motion_xposition", "motion_yposition", "sensing_timer", "sensing_mousedown", "looks_size"):
            bid = self.blk(op)
        else:
            raise ValueError(op)
        self.blocks[bid]["parent"] = parent
        return bid

    # -- scripts
    def chain(self, ids):
        ids = [i for i in ids if i]
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

    def on_key(self, key, *body, note=None):
        return self.script(self.blk("event_whenkeypressed", fields={"KEY_OPTION": [key, None]}, top=True), list(body), note)

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
                "isStage": True, "name": "Stage", "variables": variables, "lists": {},
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
    ]:
        G(name, value)

    stage = Target(game, "Stage", is_stage=True)
    game.stage = stage
    for kind in ("Title", "Select", "Yard", "Woods", "Pass", "Volcano", "Castle", "Arcade", "Ending"):
        stage.costume(kind, backdrop_svg(kind), 240, 180)
    for name in SOUNDS:
        stage.sound(name)

    s = stage
    # ---------------------------------------------------------- stage --
    s.on_flag(
        s.set("State", "title"), s.set("Fight On", 0), s.set("Score", 0), s.set("Weapon", "none"),
        s.hide_var("Score"), s.hide_var("Wave"), s.hide_var("Best"),
        s.broadcast("show title"),
        note="Green flag. Best and Crown are kept, so a saved project remembers them.",
    )
    s.on_msg("show title", s.set("State", "title"), s.set("Fight On", 0), s.backdrop("Title"),
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
        s.set("Hero HP", V("Hero Max")), s.set("Score", 0), s.set("Super", 0),
        s.if_(eq(V("Mode"), "story"),
              [s.set("Chapter", 1), s.broadcast("story scene")],
              [s.set("Wave", 1), s.broadcast("start fight")]),
        note="Each fighter has different health, speed, punch, kick and super.",
    )

    # load enemy numbers from Enemy Type
    loads = []
    for e in ENEMIES:
        loads.append(s.if_(eq(V("Enemy Type"), e["n"]), [
            s.set("Enemy Name", e["key"]), s.set("Enemy Title", e["tag"]), s.set("Enemy Max", e["hp"]),
            s.set("Enemy Power", e["pow"]), s.set("Enemy Speed", e["speed"]), s.set("Enemy Body", e["body"]),
            s.set("Enemy Size", e["size"]),
        ]))
    chapter_backdrops = [s.if_(eq(V("Chapter"), i), [s.backdrop(c["backdrop"])]) for i, c in enumerate(CHAPTERS, start=1)]
    s.on_msg(
        "load enemy",
        s.if_(eq(V("Mode"), "story"),
              [s.set("Enemy Type", V("Chapter")), *chapter_backdrops, s.set("Pace", 1)],
              [s.if_(eq(mod(V("Wave"), 5), 0),
                     [s.set("Enemy Type", 5)],
                     [s.set("Enemy Type", add(mod(sub(V("Wave"), 1), 5), 1))]),
               s.backdrop("Arcade"),
               s.set("Pace", div(8, add(7, V("Wave"))))]),
        *loads,
        s.if_(eq(V("Mode"), "arcade"), [
            s.change("Enemy Max", mul(8, sub(V("Wave"), 1))),
            s.change("Enemy Power", floor_(div(sub(V("Wave"), 1), 2))),
        ]),
        s.set("Enemy HP", V("Enemy Max")), s.set("Enemy Phase", 1),
        note="Story: the chapter picks the enemy. Arcade: waves 1-4 cycle, every 5th wave is the Shadow King, and each wave is tougher and faster.",
    )

    s.on_msg(
        "start fight",
        s.set("Fight On", 0), s.set("State", "fight"),
        s.broadcast("load enemy", wait=True),
        s.if_(eq(V("Mode"), "story"), [s.set("Hero HP", V("Hero Max"))], [s.show_var("Wave")]),
        s.show_var("Score"), s.hide_var("Best"),
        s.set("Combo", 0), s.set("Weapon", "none"), s.set("Weapon Uses", 0), s.set("Boomerang Out", 0),
        s.set("Hero Lock", 0), s.set("Hero Safe", 0), s.set("Hero Air", 0),
        s.set("Hero Safe Until", 0), s.set("Enemy Stun Until", 0),
        s.broadcast("fighters ready", wait=True),
        s.set("Banner", "ready"), s.broadcast("banner"), s.wait(1.1),
        s.set("Banner", "fight"), s.broadcast("banner"), s.wait(0.3),
        s.set("Want Punch", 0), s.set("Want Kick", 0), s.set("Want Jump", 0), s.set("Want Dodge", 0), s.set("Want Super", 0),
        s.set("Fight On", 1), s.broadcast("fight on"),
        note="READY... FIGHT! Taps before FIGHT! are thrown away.",
    )

    # hero hits enemy -- no waits here, so a fast second hit cannot break it
    s.on_msg(
        "hero hits",
        s.if_(and_(eq(V("Fight On"), 1), gt(TIMER, V("Enemy Stun Until"))), [
            s.set("Enemy Stun Until", add(TIMER, 0.15)),
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
            s.if_(and_(eq(V("Enemy Type"), 5), eq(V("Enemy Phase"), 1), gt(V("Enemy HP"), 0),
                       lt(V("Enemy HP"), div(V("Enemy Max"), 2))), [
                s.set("Enemy Phase", 2), s.set("Pace", mul(V("Pace"), 0.7)), s.broadcast("king angry"),
            ]),
            s.if_(lt(V("Enemy HP"), 1), [
                s.set("Enemy HP", 0), s.set("Fight On", 0), s.broadcast("enemy down"),
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

    s.on_msg("enemy hurt", s.play("hit"))
    s.on_msg("hero hurt", s.play("hurt"))
    s.on_msg("shake", s.play("big hit"))
    s.on_msg("weapon get", s.play("pickup"))
    s.on_msg("swing sfx", s.play("swing"))
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
                s.broadcast("ending"),
            ], [
                s.play("win"), s.set("Banner", "clear"), s.broadcast("banner"),
                s.change("Score", add(500, mul(V("Hero HP"), 5))),
                s.wait(2), s.change("Chapter", 1), s.broadcast("story scene"),
            ]),
        ], [
            s.play("win"), s.set("Banner", "wave clear"), s.broadcast("banner"),
            s.change("Score", add(200, mul(V("Wave"), 50))),
            s.change("Hero HP", ARCADE_HEAL), s.if_(gt(V("Hero HP"), V("Hero Max")), [s.set("Hero HP", V("Hero Max"))]),
            s.set("Pop Text", f"+{ARCADE_HEAL} HEALTH"), s.broadcast("popup"),
            s.if_(gt(V("Score"), V("Best")), [s.set("Best", V("Score"))]),
            s.wait(1.8), s.change("Wave", 1), s.broadcast("start fight"),
        ]),
        note="Story: next chapter, or the ending after the Shadow King. Arcade: heal a little and start the next, harder wave.",
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
    s.on_key("left arrow", s.broadcast("move left"), note="Keyboard: arrows move, up or space jumps, Z punch, X kick, C dodge, V super.")
    s.on_key("right arrow", s.broadcast("move right"))
    s.on_key("up arrow", s.set("Want Jump", 1))
    s.on_key("space", s.set("Want Jump", 1))
    s.on_key("z", s.set("Want Punch", 1))
    s.on_key("x", s.set("Want Kick", 1))
    s.on_key("c", s.set("Want Dodge", 1))
    s.on_key("v", s.set("Want Super", 1))

    # ------------------------------------------------------------ floor --
    floor = game.sprite("Ground Shake", x=0, y=GROUND - 5, visible=True, rotation="don't rotate")
    floor.costume("shadow", floor_svg(), 240, 5)
    floor.on_flag(floor.goto(0, GROUND - 5), floor.show())
    floor.on_msg("shake", floor.repeat(3, [floor.goto(0, GROUND - 1), floor.wait(0.04), floor.goto(0, GROUND - 9), floor.wait(0.04)]),
                 floor.goto(0, GROUND - 5))

    # ------------------------------------------------------------- hero --
    hero = game.sprite("Hero", x=-150, y=GROUND, size=75, visible=True)
    for h in HEROES:
        for pose in ("idle", "punch", "kick", "jump", "hurt", "win", "dodge", "special", "down"):
            face = "hurt" if pose == "hurt" else ("ko" if pose == "down" else "smile")
            hero.costume(f"{h['key']} {pose}", fighter_svg(h["color"], pose, h["gear"], face,
                                                          glow="#facc15" if pose == "special" else None), 50, 168)
    H = hero

    def pose(name):
        return H.wear(join(V("Hero Name"), " " + name))

    def rest_pose():
        return H.if_(eq(V("Hero Air"), 1), [pose("jump")], [pose("idle")])

    def face_enemy():
        return H.if_(lt(V("Enemy X"), sub(XPOS, 4)), [H.point(-90), H.set("Facing", -1)],
                     [H.if_(gt(V("Enemy X"), add(XPOS, 4)), [H.point(90), H.set("Facing", 1)])])

    def in_reach(reach):
        return lt(abs_(sub(V("Enemy X"), V("Hero X"))), add(add(reach, V("Weapon Reach")), V("Enemy Body")))

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
        note="Hero X and Hero Y are read by everyone else. In a fight, Hero always turns to face the enemy.",
    )

    punch = [
        pose("punch"),
        H.if_(and_(eq(V("Weapon"), "boomerang"), eq(V("Boomerang Out"), 0)), [
            H.set("Boomerang Out", 1), H.change("Weapon Uses", -1), H.broadcast("throw boomerang"), H.broadcast("swing sfx"),
        ], [
            H.set("Hit Power", add(V("Punch Power"), V("Weapon Bonus"))),
            weapon_swing(),
            H.if_(in_reach(PUNCH_REACH), [H.broadcast("hero hits"),
                                           H.if_(eq(V("Weapon"), "hammer"), [H.broadcast("shake")])]),
        ]),
        H.wait(0.16), break_check(), rest_pose(),
    ]
    kick = [
        pose("kick"), H.move(14), *H.clamp_x(-215, 215),
        H.set("Hit Power", add(V("Kick Power"), V("Weapon Bonus"))),
        weapon_swing(),
        H.if_(in_reach(KICK_REACH), [H.broadcast("hero hits"), H.if_(eq(V("Weapon"), "hammer"), [H.broadcast("shake")])]),
        H.wait(0.22), H.move(-14), *H.clamp_x(-215, 215), break_check(), rest_pose(),
    ]
    dodge = [
        H.set("Hero Lock", 1), H.set("Hero Safe", 1), pose("dodge"), H.effect("GHOST", 45), H.broadcast("swing sfx"),
        H.repeat(6, [H.move(-10), *H.clamp_x(-215, 215)]),
        H.wait(0.14), H.effect("GHOST", 0), H.set("Hero Safe", 0), pose("idle"), H.set("Hero Lock", 0), H.wait(0.12),
    ]

    def super_hit(power):
        return [H.set("Hit Power", power), H.broadcast("hero hits")]

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
    H.on_flag(
        H.forever([
            H.if_(eq(V("Fight On"), 1), [
                H.if_(and_(eq(V("Want Super"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Super", 0),
                    H.if_(and_(eq(V("Super"), 100), eq(V("Hero Air"), 0)), special),
                ]),
                H.if_(and_(eq(V("Want Punch"), 1), eq(V("Hero Lock"), 0)), [H.set("Want Punch", 0), *punch]),
                H.if_(and_(eq(V("Want Kick"), 1), eq(V("Hero Lock"), 0)), [H.set("Want Kick", 0), *kick]),
                H.if_(and_(eq(V("Want Dodge"), 1), eq(V("Hero Lock"), 0)), [
                    H.set("Want Dodge", 0), H.if_(eq(V("Hero Air"), 0), dodge),
                ]),
            ], [
                H.set("Want Punch", 0), H.set("Want Kick", 0), H.set("Want Dodge", 0), H.set("Want Super", 0),
            ]),
        ]),
        note="The action loop. Buttons only set Want Punch, Want Kick and so on; this loop does one move at a time. "
             "A tap during a move waits its turn (a short input buffer, like big fighting games).",
    )
    H.on_flag(
        H.forever([
            H.if_(eq(V("Want Jump"), 1), [
                H.set("Want Jump", 0),
                H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Air"), 0), eq(V("Hero Lock"), 0)), [
                    H.set("Hero Air", 1), pose("jump"), H.broadcast("jump sfx"),
                    H.repeat(8, [H.dy(11)]), H.wait(0.1), H.repeat(8, [H.dy(-11)]),
                    H.set_y(GROUND), H.set("Hero Air", 0),
                    H.if_(eq(V("Hero Lock"), 0), [pose("idle")]),
                ]),
            ]),
        ]),
        note="The jump loop runs beside the action loop, so you can punch and kick in the air.",
    )
    for direction, sign in (("left", -1), ("right", 1)):
        H.on_msg(f"move {direction}", H.if_(and_(eq(V("Fight On"), 1), eq(V("Hero Lock"), 0)), [
            H.dx(mul(sign, V("Step"))), *H.clamp_x(-215, 215),
        ]))
    H.on_msg("hero hurt", H.if_(eq(V("Hero Lock"), 0), [pose("hurt"), H.move(-12), *H.clamp_x(-215, 215)]),
             H.effect("COLOR", 60), H.wait(0.15), H.effect("COLOR", 0), H.if_(eq(V("Hero Lock"), 0), [rest_pose()]))
    H.on_msg("show title", H.show(), H.clear_fx(), H.point(90), H.set("Hero Name", "arthur"), H.wear("arthur idle"),
             H.goto(-195, GROUND), H.size_to(90), H.front(), H.say("I'm Arthur!", 2))
    H.on_msg("choose hero", H.hide())
    H.on_msg("story scene", H.hide())
    H.on_msg("fighters ready", H.show(), H.clear_fx(), H.point(90), H.set("Facing", 1), pose("idle"),
             H.size_to(75), H.goto(-150, GROUND),
             *[H.if_(eq(V("Hero"), i), [H.say(h["line"], 1)]) for i, h in enumerate(HEROES, start=1)],
             note="Each fighter has a catchphrase before READY... FIGHT!")
    H.on_msg("scene setup", H.show(), H.clear_fx(), H.point(90), pose("idle"), H.size_to(75), H.goto(-150, GROUND))
    H.local("Line Until", 0)
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
        for p in ("idle", "windup", "attack", "hurt", "down"):
            src = {"attack": {1: "punch", 2: "aim", 3: "charge", 4: "slam", 5: "special"}[e["n"]],
                   "windup": {1: "windup", 2: "windup", 3: "windup", 4: "raise", 5: "raise"}[e["n"]]}.get(p, p)
            face = {"hurt": "hurt", "down": "ko"}.get(p, angry)
            enemy.costume(f"{e['key']} {p}", fighter_svg(e["color"], src, e["gear"], face,
                                                        glow="#a855f7" if e["n"] == 5 else None), 50, 168)
        if e["n"] == 5:
            enemy.costume("shadow angry", fighter_svg("#7f1d1d", "raise", "crown", "angry", glow="#ef4444"), 50, 168)
    E = enemy
    E.local("Pick", 1)
    E.local("Line Until", 0)

    def epose(name):
        return E.wear(join(V("Enemy Name"), " " + name))

    def hit_hero():
        return [E.set("Hurt Power", V("Enemy Power")), E.broadcast("enemy hits hero")]

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
            E.set("Pick", V("Hero X")), epose("attack"), E.broadcast("swing sfx"),
            E.glide(pw(0.4), V("Pick"), GROUND),
            E.if_(and_(lt(abs_(sub(V("Hero X"), XPOS)), add(34, V("Enemy Body"))), lt(sub(V("Hero Y"), GROUND), 50)),
                  [*hit_hero(), E.broadcast("shake")]),
            epose("idle"), E.wait(pw(0.45)),
            E.glide(0.5, add(XPOS, mul(-100, V("Enemy Facing"))), GROUND), *E.clamp_x(-205, 205),
            E.wait(pw(0.3)),
        ]

    def stomper():
        return [
            epose("windup"), E.say("STOMP!", pw(0.6)), epose("attack"),
            E.dy(10), E.wait(0.05), E.set_y(GROUND), E.broadcast("shake"),
            E.set("Wave Dir", V("Enemy Facing")), E.broadcast("ground wave", wait=True),
            epose("idle"), E.wait(pw(0.5)),
            E.if_(gt(abs_(sub(V("Hero X"), XPOS)), 160), [E.repeat(8, [E.move(V("Enemy Speed"))]), *E.clamp_x(-205, 205)]),
        ]

    def king():
        return [
            E.set("Pick", rnd(1, 4)),
            E.if_(eq(V("Pick"), 1), charger()),
            E.if_(eq(V("Pick"), 2), [
                E.wait(pw(0.2)), *shot(False),
                E.if_(eq(V("Enemy Phase"), 2), shot(True)),
                E.wait(pw(0.3)),
            ]),
            E.if_(eq(V("Pick"), 3), stomper()),
            E.if_(eq(V("Pick"), 4), [E.repeat(12, [E.move(mul(V("Enemy Speed"), 1.5)), *E.clamp_x(-210, 210)]), *walker()]),
        ]

    E.on_flag(
        E.rotation_style("left-right"), E.hide(),
        E.forever([E.set("Enemy X", XPOS)]),
        note="Enemy X is read by Hero and the weapons.",
    )
    E.on_msg(
        "fight on",
        E.until(eq(V("Fight On"), 0), [
            face_hero(),
            E.if_(lt(TIMER, V("Enemy Stun Until")), [epose("hurt"), E.wait(0.05)], [
                E.if_(eq(V("Enemy Type"), 1), walker()),
                E.if_(eq(V("Enemy Type"), 2), thrower()),
                E.if_(eq(V("Enemy Type"), 3), charger()),
                E.if_(eq(V("Enemy Type"), 4), stomper()),
                E.if_(eq(V("Enemy Type"), 5), king()),
                E.if_(eq(V("Fight On"), 1), [epose("idle")]),
            ]),
        ]),
        note="One brain for every enemy. 1 Rival walks in and punches. 2 Ivy throws low and high shots. "
             "3 Brute says Ready? then charges where you were. 4 Quake stomps a ground wave. 5 the Shadow King mixes them all.",
    )
    E.on_msg("enemy hurt", epose("hurt"), E.move(-12), *E.clamp_x(-210, 210), E.effect("BRIGHTNESS", 60),
             E.wait(0.1), E.effect("BRIGHTNESS", 0))
    E.on_msg("king angry", E.wear("shadow angry"), E.say("You're strong... but I'm STRONGER!", 1.6), E.wear("shadow idle"))
    for m in ("show title", "choose hero"):
        E.on_msg(m, E.hide())
    E.on_msg("fighters ready", E.show(), E.clear_fx(), E.size_to(V("Enemy Size")), E.point(-90), E.set("Enemy Facing", -1),
             E.goto(150, GROUND), epose("idle"), E.say(""))
    E.on_msg("scene setup", E.show(), E.clear_fx(), E.size_to(V("Enemy Size")), E.point(-90), E.goto(150, GROUND), epose("idle"))
    E.on_msg("story scene", E.hide())
    E.on_msg("enemy line", E.say(V("Line")), E.set("Line Until", add(TIMER, V("Line Secs"))),
             E.wait_until(or_(gt(TIMER, V("Line Until")), eq(V("Skip"), 1))), E.say(""))
    E.on_msg("enemy down", E.say(""), E.wait(0.2), E.set_y(GROUND), epose("down"), E.wait(1.3),
             E.repeat(10, [E.effect_by("GHOST", 10), E.wait(0.03)]),
             E.if_(not_(and_(eq(V("Mode"), "story"), eq(V("Chapter"), len(CHAPTERS)))), [E.hide()]),
             E.effect("GHOST", 0))
    E.on_msg("hero down", E.wait(0.3), epose("idle"), E.say("Ha! Try again!", 2))
    E.on_msg("ending", E.show(), E.goto(170, GROUND), E.point(-90), E.wear("shadow down"))

    # ------------------------------------------------------- projectiles --
    shot_s = game.sprite("Enemy Shot", size=100, rotation="don't rotate")
    shot_s.costume("ball", shot_svg(), 14, 14)
    S = shot_s
    S.local("Hit", 0)
    S.on_flag(S.hide())
    S.on_msg(
        "enemy shot",
        S.goto(add(V("Enemy X"), mul(30, V("Shot Dir"))), V("Shot Y")), S.set("Hit", 0), S.show(), S.front(),
        S.until(or_(gt(abs_(XPOS), 235), eq(V("Hit"), 1), eq(V("Fight On"), 0)), [
            S.dx(mul(12, V("Shot Dir"))),
            S.if_(and_(lt(abs_(sub(XPOS, V("Hero X"))), 18), gt(sub(V("Shot Y"), V("Hero Y")), -10),
                       lt(sub(V("Shot Y"), V("Hero Y")), 108)), [
                S.set("Hit", 1), S.set("Hurt Power", V("Enemy Power")), S.broadcast("enemy hits hero"),
            ]),
        ]),
        S.hide(),
        note="Low shots fly at knee height: jump them. High shots fly over your head: stay down. Dodge works on both.",
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
        held.costume(w["key"], weapon_svg(w["key"]), 30, 66)
    HW = held
    HW.local("Swing Until", 0)
    HW.on_flag(
        HW.hide(),
        HW.forever([
            HW.if_(and_(eq(V("State"), "fight"), not_(eq(V("Weapon"), "none")), eq(V("Boomerang Out"), 0)), [
                HW.wear(V("Weapon")),
                HW.goto(add(V("Hero X"), mul(18, V("Facing"))), add(V("Hero Y"), 48)),
                HW.if_(lt(TIMER, V("Swing Until")), [HW.point(add(90, mul(100, V("Facing"))))],
                       [HW.point(add(90, mul(-25, V("Facing"))))]),
                HW.show(), HW.front(),
            ], [HW.hide()]),
        ]),
        note="Follows Hero's hand while a weapon is held.",
    )
    HW.on_msg("swing", HW.set("Swing Until", add(TIMER, 0.15)), HW.broadcast("swing sfx"))
    HW.on_msg("weapon break",
              HW.set("Pop Text", join("Oh no! The ", join(V("Weapon"), " broke!"))), HW.broadcast("popup"),
              HW.set("Weapon", "none"), HW.set("Weapon Bonus", 0), HW.set("Weapon Reach", 0), HW.set("Weapon Uses", 0))

    drop = game.sprite("Weapon Drop", size=70, rotation="don't rotate")
    for w in WEAPONS:
        drop.costume(w["key"], weapon_svg(w["key"], sparkle=True), 30, 40)
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
                    D.set("Kind", rnd(1, 3)),
                    D.if_(eq(V("Kind"), 1), [D.set("Kind", "sword")]),
                    D.if_(eq(V("Kind"), 2), [D.set("Kind", "hammer")]),
                    D.if_(eq(V("Kind"), 3), [D.set("Kind", "boomerang")]),
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
             "Boomerang: PUNCH throws it, 6 throws.",
    )
    for m in FIGHT_HIDE:
        D.on_msg(m, D.hide())

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

    # ------------------------------------------------------------ crown --
    crown = game.sprite("Crown", size=80, rotation="don't rotate")
    crown.costume("crown", crown_svg(), 22, 30)
    C = crown
    C.on_flag(
        C.hide(),
        C.forever([
            C.if_(and_(eq(V("Crown"), 1), or_(eq(V("State"), "fight"), eq(V("State"), "over"))), [
                C.goto(V("Hero X"), add(V("Hero Y"), 104)), C.show(), C.front(),
            ], [C.if_(not_(eq(V("State"), "ending")), [C.hide()])]),
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
                b.if_(eq(V("State"), "fight"), [
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
        t.on_flag(t.hide(), t.forever([t.if_(eq(V("State"), "fight"), [t.goto(x, y), t.show()], [t.hide()])]))
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
        hero_tag.if_(eq(V("State"), "fight"), [hero_tag.wear(V("Hero Name")), hero_tag.goto(-228, 174), hero_tag.show()],
                     [hero_tag.hide()])]))
    enemy_tag = game.sprite("Enemy Tag", x=228, y=174, rotation="don't rotate")
    for e in ENEMIES:
        word = e["tag"]
        enemy_tag.costume(e["key"], tag_svg(word, e["color"] if e["n"] != 5 else "#581c87"), 12 + 10 * len(word), 10)
    enemy_tag.on_flag(enemy_tag.hide(), enemy_tag.forever([
        enemy_tag.if_(eq(V("State"), "fight"), [enemy_tag.wear(V("Enemy Name")), enemy_tag.goto(228, 174), enemy_tag.show()],
                      [enemy_tag.hide()])]))

    # pop-up words (combo, perfect, weapon names) as clones that float up
    pop = game.sprite("Popup", size=100, rotation="don't rotate")
    pop.costume("dot", dot_svg(), 2, 2)
    P = pop
    P.local("My Text", "")
    P.on_flag(P.hide())
    P.on_msg("popup", P.set("My Text", V("Pop Text")), P.goto(add(V("Hero X"), 10), add(V("Hero Y"), 125)), P.clone(),
             note="Copies Pop Text into a clone so two pop-ups in a row both show.")
    P.on_clone(P.show(), P.say(V("My Text")), P.repeat(14, [P.dy(2), P.wait(0.06)]), P.delete_clone())
    P.on_msg("super ready", P.set("My Text", "SUPER READY! Tap SUPER"), P.goto(-150, 120), P.clone())

    spark = game.sprite("Hit Spark", size=50, rotation="all around")
    spark.costume("spark", spark_svg(), 40, 40)
    SP = spark
    SP.on_flag(SP.hide())
    SP.on_msg("enemy hurt", SP.goto(V("Enemy X"), add(GROUND, 60)), SP.clone())
    SP.on_msg("hero hurt", SP.goto(V("Hero X"), add(GROUND, 50)), SP.clone())
    SP.on_clone(SP.point(rnd(0, 90)), SP.size_to(40), SP.show(), SP.front(),
                SP.repeat(5, [SP.size_by(14), SP.effect_by("GHOST", 18), SP.wait(0.02)]), SP.delete_clone())

    banner = game.sprite("Banner", x=0, y=40, rotation="don't rotate")
    for key, word, fill in (("ready", "READY...", "#facc15"), ("fight", "FIGHT!", "#ef4444"), ("ko", "K.O.!", "#f97316"),
                            ("clear", "CHAPTER CLEAR!", "#22c55e"), ("wave clear", "WAVE CLEAR!", "#22d3ee")):
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
        card.costume(f"chapter {i}", card_svg(c["title"], c["lines"], ["#2563eb", "#16a34a", "#dc2626", "#ea580c", "#4c1d95"][i - 1]), 210, 120)
    card.costume("game over", card_svg("GAME OVER", ["Tap RETRY to fight again", "or HOME for the title."], "#475569"), 210, 120)
    card.costume("arcade over", card_svg("GAME OVER", ["How far did you get?", "Check Score and Best.", "Tap RETRY or HOME."], "#db2777"), 210, 120)
    card.costume("the end", card_svg("THE END", ["The Golden Crown is back!", "You are the CHAMPION.", "Now try ARCADE mode!"], "#ca8a04"), 210, 120)
    card.costume("angry", card_svg("HE'S ANGRY!", ["The Shadow King is faster", "and throws double shots!"], "#b91c1c"), 210, 120)
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
    K.on_msg("king angry", K.wear("angry"), K.size_to(80), K.goto(0, 60), K.show(), K.front(), K.wait(1.4), K.hide())
    K.on_msg("game over", K.if_(eq(V("Mode"), "arcade"), [K.wear("arcade over")], [K.wear("game over")]),
             K.size_to(85), K.goto(0, -5), K.show(), K.front())
    for m in ("show title", "choose hero", "start fight", "fight on"):
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
        ("Super Button", "SUPER", "#475569", "Want Super"),
    ]
    for i, (name, label, fill, action) in enumerate(controls):
        x = -207 + 69 * i
        b = button(name, label, fill, x, -152)
        if action.startswith("move"):
            b.on_click(b.broadcast(action), b.wait(0.25),
                       b.until(not_(MOUSE_DOWN), [b.broadcast(action), b.wait(0.09)]),
                       note="Tap to step. Hold to keep walking.")
        else:
            b.on_click(b.set(action, 1), note=f"Sets {action}. Hero's loop does the move.")
        b.on_msg("fight on", b.goto(x, -152), b.show(), b.front())
        for m in FIGHT_HIDE:
            b.on_msg(m, b.hide())
        if name == "Super Button":
            b.costume("ready", button_svg("SUPER!", "#facc15", "#7c2d12"), 31, 22)
            b.on_flag(b.forever([b.if_(eq(V("Super"), 100), [b.wear("ready")], [b.wear("button")])]))

    story_btn = button("Story Button", "STORY", "#2563eb", -75, -20, width=120, height=52, size=20)
    arcade_btn = button("Arcade Button", "ARCADE", "#db2777", 75, -20, width=120, height=52, size=20)
    for b, mode in ((story_btn, "story"), (arcade_btn, "arcade")):
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
    for m in ("show title", "start fight"):
        retry.on_msg(m, retry.hide())
    retry.on_click(
        retry.hide(),
        retry.if_(eq(V("Mode"), "arcade"), [retry.set("Wave", 1), retry.set("Score", 0), retry.set("Hero HP", V("Hero Max"))]),
        retry.set("Super", 0),
        retry.broadcast("start fight"),
        note="Story: try the same chapter again (no talking). Arcade: a new run from wave 1.",
    )

    home = button("Home Button", "HOME", "#475569", 70, -150, width=100, height=48, size=16)
    home.on_msg("game over", home.goto(70, -150), home.show(), home.front())
    home.on_msg("show home", home.goto(0, -150), home.show(), home.front())
    for m in ("show title", "start fight"):
        home.on_msg(m, home.hide())
    home.on_click(home.hide(), home.broadcast("show title"))

    quit_btn = button("Quit Button", "✕", "#334155", 0, 165, width=30, height=26, size=14)
    quit_btn.on_msg("fight on", quit_btn.goto(0, 165), quit_btn.show(), quit_btn.front())
    quit_btn.on_msg("choose hero", quit_btn.goto(-218, -160), quit_btn.show(), quit_btn.front())
    for m in ("show title", "hero down", "enemy down", "story scene", "hero picked"):
        quit_btn.on_msg(m, quit_btn.hide())
    quit_btn.on_click(quit_btn.hide(), quit_btn.set("Fight On", 0), quit_btn.broadcast("show title"),
                      note="Back to the title at any time.")

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
        "monitors": [monitor("Score", 196, 28), monitor("Wave", 205, 54), monitor("Best", 200, 310)],
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
        if op in ("looks_costume", "looks_backdrops", "sound_sounds_menu", "control_create_clone_of_menu"):
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
                "control_create_clone_of": "create clone of (myself)",
                "control_delete_this_clone": "delete this clone",
                "control_stop": f"stop [{b['fields'].get('STOP_OPTION', [''])[0]}]",
            }.get(op)
            if op == "event_whenbroadcastreceived":
                text = f"when I receive [{b['fields']['BROADCAST_OPTION'][0]}]"
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
