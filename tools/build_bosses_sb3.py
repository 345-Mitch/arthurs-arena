#!/usr/bin/env python3
"""Build Arthur's Arena boss fights as a Scratch 3 project.

The kid-facing guide is BOSSES.md. This script is the reproducible way to
rebuild projects/arthurs-arena-bosses.sb3 and projects/BLOCK_LISTING.md.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SB3_PATH = ROOT / "projects" / "arthurs-arena-bosses.sb3"
LISTING_PATH = ROOT / "projects" / "BLOCK_LISTING.md"

# Small numbers on purpose. The template's bosses use 5000, 7000, and 8200,
# which a kid cannot count down. These values are a few punches each.
ARTHUR_MAX = 100
RIVAL_HP = 10
BRUTE_HP = 24
IVY_HP = 24
QUAKE_HP = 30
PUNCH = 5
KICK = 8
RIVAL_HURT = 6
BRUTE_HURT = 10
IVY_HURT = 8
QUAKE_HURT = 12

# Which Fight: 1 Rival (normal enemy), 2 Brute, 3 Ivy, 4 Quake.
FIGHTS = ((1, "Rival"), (2, "Brute"), (3, "Ivy"), (4, "Quake"))


def svg_doc(width: float, height: float, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0,0,{width},{height}">{body}</svg>'
    )


def text_el(content: str, x: float, y: float, size: int, fill: str, anchor: str = "middle") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Verdana,Arial,sans-serif" '
        f'font-size="{size}" font-weight="700" fill="{fill}">{escape(content)}</text>'
    )


def stick_svg(color: str, pose: str, label: str | None = None, face: str = "smile") -> str:
    """A stick figure in a 100 by 180 box. Feet sit on y=168."""
    poses = {
        "idle": [(50, 64, 50, 112), (50, 78, 26, 100), (50, 78, 74, 100), (50, 112, 34, 168), (50, 112, 66, 168)],
        "punch": [(50, 64, 50, 112), (50, 78, 24, 90), (50, 78, 96, 72), (50, 112, 34, 168), (50, 112, 66, 168)],
        "kick": [(52, 64, 56, 112), (56, 78, 30, 68), (56, 78, 78, 90), (56, 112, 36, 168), (56, 112, 98, 122)],
        "jump": [(50, 74, 50, 112), (50, 84, 24, 58), (50, 84, 76, 58), (50, 112, 32, 146), (50, 112, 68, 146)],
        "hurt": [(42, 70, 58, 116), (42, 82, 18, 70), (42, 82, 70, 98), (58, 116, 36, 168), (58, 116, 78, 168)],
        "win": [(50, 70, 50, 114), (50, 80, 18, 42), (50, 80, 82, 42), (50, 114, 32, 168), (50, 114, 68, 168)],
        "lean": [(40, 66, 62, 116), (40, 80, 16, 96), (40, 80, 58, 102), (62, 116, 40, 168), (62, 116, 82, 168)],
        "charge": [(62, 70, 34, 116), (48, 82, 16, 90), (48, 82, 78, 68), (34, 116, 16, 150), (34, 116, 58, 168)],
        "aim": [(50, 64, 50, 112), (50, 78, 24, 92), (50, 78, 90, 64), (50, 112, 34, 168), (50, 112, 66, 168)],
        "raise": [(50, 68, 50, 114), (50, 78, 22, 36), (50, 78, 78, 36), (50, 114, 30, 168), (50, 114, 70, 168)],
        "slam": [(50, 64, 50, 116), (50, 86, 14, 124), (50, 86, 86, 124), (50, 116, 26, 168), (50, 116, 74, 168)],
        "angry": [(50, 66, 50, 114), (50, 76, 18, 34), (50, 76, 82, 34), (50, 114, 26, 168), (50, 114, 74, 168)],
    }
    lines = poses[pose]
    parts = []
    parts.append(
        '<g fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">'
    )
    parts.append('<circle cx="50" cy="48" r="18" fill="#ffffff" stroke="#ffffff"/>')
    for x1, y1, x2, y2 in lines:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    parts.append("</g>")
    parts.append(
        f'<g fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">'
    )
    parts.append(f'<circle cx="50" cy="48" r="16" fill="{color}" stroke="{color}"/>')
    for x1, y1, x2, y2 in lines:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    parts.append("</g>")
    if pose == "aim":
        parts.append('<circle cx="92" cy="62" r="8" fill="#facc15" stroke="#ffffff" stroke-width="3"/>')
    # Friendly face, drawn after the head so it stays visible.
    parts.append('<circle cx="44" cy="46" r="2.4" fill="#ffffff"/>')
    parts.append('<circle cx="56" cy="46" r="2.4" fill="#ffffff"/>')
    if face == "angry":
        parts.append('<path d="M40 38 L48 42" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
        parts.append('<path d="M60 38 L52 42" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
        parts.append('<path d="M44 56 Q50 52 56 56" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
    elif face == "hurt":
        parts.append('<path d="M44 56 Q50 60 56 56" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
    else:
        parts.append('<path d="M43 54 Q50 60 57 54" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
    if label:
        parts.append(text_el(label, 50, 18, 14, "#0f172a"))
        parts.append(text_el(label, 50, 17, 13, "#ffffff"))
    return svg_doc(100, 180, "".join(parts))


def button_svg(label: str, fill: str, ink: str) -> str:
    body = (
        f'<rect x="2" y="2" width="68" height="40" rx="12" fill="{fill}" stroke="#ffffff" stroke-width="3"/>'
        + text_el(label, 36, 27, 13, ink)
    )
    return svg_doc(72, 44, body)


def bar_svg(width: int, height: int, fill: str) -> str:
    body = (
        f'<rect x="0" y="2" width="{width}" height="{height - 4}" rx="6" fill="{fill}" '
        f'stroke="#0f172a" stroke-width="2"/>'
    )
    return svg_doc(width, height, body)


def label_svg(word: str, fill: str, width: int, height: int, size: int) -> str:
    body = (
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" fill="{fill}"/>'
        + text_el(word, width / 2, height * 0.68, size, "#ffffff")
    )
    return svg_doc(width, height, body)


def card_svg(title: str, lines: list[str], accent: str) -> str:
    body = [
        '<rect x="8" y="8" width="404" height="224" rx="22" fill="#ffffff" stroke="#0f172a" stroke-width="6"/>',
        f'<rect x="8" y="8" width="404" height="64" rx="22" fill="{accent}"/>',
        '<rect x="8" y="40" width="404" height="32" fill="{accent}"/>'.replace("{accent}", accent),
        text_el(title, 210, 52, 36, "#ffffff"),
    ]
    y = 108
    for line in lines:
        body.append(text_el(line, 210, y, 22, "#0f172a"))
        y += 36
    return svg_doc(420, 240, "".join(body))


def backdrop_svg(kind: str) -> str:
    if kind == "Title":
        body = (
            '<rect width="480" height="360" fill="#1e1b4b"/>'
            '<circle cx="70" cy="60" r="3" fill="#fef3c7"/>'
            '<circle cx="140" cy="100" r="2" fill="#fef3c7"/>'
            '<circle cx="400" cy="50" r="3" fill="#fef3c7"/>'
            '<circle cx="340" cy="90" r="2" fill="#fef3c7"/>'
            '<circle cx="430" cy="130" r="2" fill="#fef3c7"/>'
            + text_el("Arthur's Arena", 240, 78, 48, "#ffffff")
            + text_el("Tap Start", 240, 118, 22, "#fde68a")
        )
    elif kind == "Arena":
        body = (
            '<rect width="480" height="360" fill="#dbeafe"/>'
            '<rect y="200" width="480" height="160" fill="#15803d"/>'
            '<rect y="200" width="480" height="8" fill="#166534"/>'
            + text_el("Arthur's Arena", 240, 48, 28, "#1e3a8a")
        )
    elif kind == "Win":
        body = (
            '<rect width="480" height="360" fill="#fde68a"/>'
            + text_el("Arthur wins!", 240, 150, 52, "#92400e")
            + text_el("You are the champion!", 240, 200, 26, "#b45309")
        )
    else:
        body = (
            '<rect width="480" height="360" fill="#44403c"/>'
            + text_el("Arthur got knocked down.", 240, 150, 28, "#fef3c7")
            + text_el("Tap Try again or Home.", 240, 196, 22, "#ffffff")
        )
    return svg_doc(480, 360, body)


def impact_svg() -> str:
    body = (
        '<g fill="none" stroke="#f97316" stroke-width="8" stroke-linecap="round">'
        '<line x1="20" y1="40" x2="20" y2="10"/>'
        '<line x1="60" y1="40" x2="60" y2="6"/>'
        '<line x1="100" y1="40" x2="100" y2="14"/>'
        "</g>"
    )
    return svg_doc(120, 50, body)


def shot_svg() -> str:
    body = '<circle cx="12" cy="12" r="9" fill="#facc15" stroke="#7c3aed" stroke-width="3"/>'
    return svg_doc(24, 24, body)


def wave_svg() -> str:
    body = (
        '<ellipse cx="50" cy="18" rx="46" ry="12" fill="#fb923c" stroke="#9a3412" stroke-width="3"/>'
        '<path d="M14 18 Q30 8 50 18 Q70 28 86 18" fill="none" stroke="#fff7ed" stroke-width="3"/>'
    )
    return svg_doc(100, 36, body)


class Builder:
    def __init__(self, name: str, globals_: dict, broadcasts: dict):
        self.name = name
        self.globals = globals_
        self.bcasts = broadcasts
        self.locals: dict[str, tuple[str, object]] = {}
        self.blocks: dict[str, dict] = {}
        self.comments: dict[str, dict] = {}
        self.costumes: list[dict] = []
        self.assets: dict[str, bytes] = {}
        self.i = 0
        self.ci = 0
        self.y = 40
        self.visible = False
        self.x = 0
        self.sy = 0
        self.sprite_size = 100
        self.notes: list[str] = []

    def add_local(self, name: str, value: object) -> None:
        self.locals[name] = (f"local_{self.name}_{name}".replace(" ", "_"), value)

    def lookup(self, name: str) -> tuple[str, str]:
        if name in self.locals:
            return self.locals[name][0], name
        if name not in self.globals:
            raise KeyError(f"{self.name} has no variable {name}")
        return self.globals[name][0], name

    def add_costume(self, name: str, svg: str, cx: float, cy: float) -> None:
        data = svg.encode("utf-8")
        digest = hashlib.md5(data).hexdigest()
        self.assets[f"{digest}.svg"] = data
        self.costumes.append(
            {
                "name": name,
                "bitmapResolution": 1,
                "dataFormat": "svg",
                "assetId": digest,
                "md5ext": f"{digest}.svg",
                "rotationCenterX": cx,
                "rotationCenterY": cy,
            }
        )

    def b(self, opcode, *, parent=None, fields=None, shadow=False, top=False, x=0, y=0, mutation=None):
        self.i += 1
        bid = f"{self.name[:4]}{self.i}"
        block = {
            "opcode": opcode,
            "next": None,
            "parent": parent,
            "inputs": {},
            "fields": fields or {},
            "shadow": shadow,
            "topLevel": top,
        }
        if top:
            block["x"] = x
            block["y"] = y
        if mutation is not None:
            block["mutation"] = mutation
        self.blocks[bid] = block
        return bid

    def spot(self) -> tuple[int, int]:
        y = self.y
        self.y += 420
        return 48, y

    def note(self, bid: str, text: str, x: int, y: int) -> None:
        self.ci += 1
        cid = f"{self.name[:4]}note{self.ci}"
        self.comments[cid] = {
            "blockId": bid,
            "x": x,
            "y": y,
            "width": 260,
            "height": 110,
            "minimized": False,
            "text": text,
        }
        self.blocks[bid]["comment"] = cid

    def hat(self, opcode, fields=None, comment=None):
        x, y = self.spot()
        bid = self.b(opcode, fields=fields, top=True, x=x, y=y)
        if comment:
            self.note(bid, comment, x + 380, y)
        return bid

    def hat_flag(self, comment=None):
        return self.hat("event_whenflagclicked", comment=comment)

    def hat_click(self, comment=None):
        return self.hat("event_whenthisspriteclicked", comment=comment)

    def hat_msg(self, message, comment=None):
        return self.hat(
            "event_whenbroadcastreceived",
            fields={"BROADCAST_OPTION": [message, self.bcasts[message]]},
            comment=comment,
        )

    def _chain(self, ids, parent_of_first):
        self.blocks[ids[0]]["parent"] = parent_of_first
        for left, right in zip(ids, ids[1:]):
            self.blocks[left]["next"] = right
            self.blocks[right]["parent"] = left
        return ids[0]

    def attach(self, hat, stmts):
        stmts = [item for item in stmts if item]
        if stmts:
            self.blocks[hat]["next"] = self._chain(stmts, hat)
        return hat

    def num(self, n):
        if isinstance(n, float) and n.is_integer():
            n = int(n)
        return [1, [4, str(n)]]

    def whole(self, n):
        return [1, [6, str(int(n))]]

    def pos(self, n):
        return [1, [5, str(n)]]

    def text(self, s):
        return [1, [10, str(s)]]

    def ivar(self, parent, name):
        vid, vname = self.lookup(name)
        bid = self.b("data_variable", parent=parent, fields={"VARIABLE": [vname, vid]})
        return [3, bid, [12, vname, vid]]

    def set_num(self, name, n):
        vid, vname = self.lookup(name)
        bid = self.b("data_setvariableto", fields={"VARIABLE": [vname, vid]})
        self.blocks[bid]["inputs"] = {"VALUE": self.num(n)}
        return bid

    def set_text(self, name, value):
        vid, vname = self.lookup(name)
        bid = self.b("data_setvariableto", fields={"VARIABLE": [vname, vid]})
        self.blocks[bid]["inputs"] = {"VALUE": self.text(value)}
        return bid

    def set_xpos(self, name):
        vid, vname = self.lookup(name)
        bid = self.b("data_setvariableto", fields={"VARIABLE": [vname, vid]})
        rep = self.b("motion_xposition", parent=bid)
        self.blocks[bid]["inputs"] = {"VALUE": [3, rep, [4, "0"]]}
        return bid

    def change_num(self, name, n):
        vid, vname = self.lookup(name)
        bid = self.b("data_changevariableby", fields={"VARIABLE": [vname, vid]})
        self.blocks[bid]["inputs"] = {"VALUE": self.num(n)}
        return bid

    def change_by_neg(self, name, sub):
        vid, vname = self.lookup(name)
        bid = self.b("data_changevariableby", fields={"VARIABLE": [vname, vid]})
        subb = self.b("operator_subtract", parent=bid)
        self.blocks[subb]["inputs"] = {"NUM1": self.num(0), "NUM2": self.ivar(subb, sub)}
        self.blocks[bid]["inputs"] = {"VALUE": [3, subb, [4, "0"]]}
        return bid

    def costume(self, name):
        bid = self.b("looks_switchcostumeto")
        menu = self.b("looks_costume", parent=bid, shadow=True, fields={"COSTUME": [name, None]})
        self.blocks[bid]["inputs"] = {"COSTUME": [1, menu]}
        return bid

    def backdrop(self, name):
        bid = self.b("looks_switchbackdropto")
        menu = self.b("looks_backdrops", parent=bid, shadow=True, fields={"BACKDROP": [name, None]})
        self.blocks[bid]["inputs"] = {"BACKDROP": [1, menu]}
        return bid

    def say(self, message, secs):
        bid = self.b("looks_sayforsecs")
        self.blocks[bid]["inputs"] = {"MESSAGE": self.text(message), "SECS": self.num(secs)}
        return bid

    def wait(self, secs):
        bid = self.b("control_wait")
        self.blocks[bid]["inputs"] = {"DURATION": self.pos(secs)}
        return bid

    def show(self):
        return self.b("looks_show")

    def hide(self):
        return self.b("looks_hide")

    def goto(self, x, y):
        bid = self.b("motion_gotoxy")
        self.blocks[bid]["inputs"] = {"X": self.num(x), "Y": self.num(y)}
        return bid

    def set_x(self, n):
        bid = self.b("motion_setx")
        self.blocks[bid]["inputs"] = {"X": self.num(n)}
        return bid

    def set_y(self, n):
        bid = self.b("motion_sety")
        self.blocks[bid]["inputs"] = {"Y": self.num(n)}
        return bid

    def set_y_var(self, name):
        bid = self.b("motion_sety")
        self.blocks[bid]["inputs"] = {"Y": self.ivar(bid, name)}
        return bid

    def change_x(self, n):
        bid = self.b("motion_changexby")
        self.blocks[bid]["inputs"] = {"DX": self.num(n)}
        return bid

    def change_y(self, n):
        bid = self.b("motion_changeyby")
        self.blocks[bid]["inputs"] = {"DY": self.num(n)}
        return bid

    def change_x_neg_var(self, name):
        bid = self.b("motion_changexby")
        subb = self.b("operator_subtract", parent=bid)
        self.blocks[subb]["inputs"] = {"NUM1": self.num(0), "NUM2": self.ivar(subb, name)}
        self.blocks[bid]["inputs"] = {"DX": [3, subb, [4, "0"]]}
        return bid

    def glide(self, secs, x, y):
        bid = self.b("motion_glidesecstoxy")
        self.blocks[bid]["inputs"] = {"SECS": self.num(secs), "X": self.num(x), "Y": self.num(y)}
        return bid

    def glide_x_var(self, secs, name, y):
        bid = self.b("motion_glidesecstoxy")
        self.blocks[bid]["inputs"] = {"SECS": self.num(secs), "X": self.ivar(bid, name), "Y": self.num(y)}
        return bid

    def size(self, n):
        bid = self.b("looks_setsizeto")
        self.blocks[bid]["inputs"] = {"SIZE": self.num(n)}
        return bid

    def size_input(self, parent_input_block):
        self.blocks[parent_input_block]["inputs"] = {"SIZE": [3, parent_input_block and None, [4, "100"]]}

    def set_var_from_var(self, dest, source):
        vid, vname = self.lookup(dest)
        bid = self.b("data_setvariableto", fields={"VARIABLE": [vname, vid]})
        self.blocks[bid]["inputs"] = {"VALUE": self.ivar(bid, source)}
        return bid

    def front(self):
        return self.b("looks_gotofrontback", fields={"FRONT_BACK": ["front", None]})

    def broadcast(self, name, wait=False):
        op = "event_broadcastandwait" if wait else "event_broadcast"
        bid = self.b(op)
        self.blocks[bid]["inputs"] = {"BROADCAST_INPUT": [1, [11, name, self.bcasts[name]]]}
        return bid

    def color_effect(self, n):
        bid = self.b("looks_seteffectto", fields={"EFFECT": ["COLOR", None]})
        self.blocks[bid]["inputs"] = {"VALUE": self.num(n)}
        return bid

    def clear_fx(self):
        return self.b("looks_cleargraphiceffects")

    def show_var(self, name):
        vid, vname = self.lookup(name)
        return self.b("data_showvariable", fields={"VARIABLE": [vname, vid]})

    def hide_var(self, name):
        vid, vname = self.lookup(name)
        return self.b("data_hidevariable", fields={"VARIABLE": [vname, vid]})

    def stop(self):
        return self.b(
            "control_stop",
            fields={"STOP_OPTION": ["this script", None]},
            mutation={"tagName": "mutation", "children": [], "hasnext": "false"},
        )

    def repeat(self, times, body):
        bid = self.b("control_repeat")
        inputs = {"TIMES": self.whole(times)}
        if body:
            inputs["SUBSTACK"] = [2, self._chain(body, bid)]
        self.blocks[bid]["inputs"] = inputs
        return bid

    def forever(self, body):
        bid = self.b("control_forever")
        self.blocks[bid]["inputs"] = {"SUBSTACK": [2, self._chain(body, bid)]}
        return bid

    def if_(self, cond_fn, body, else_body=None):
        bid = self.b("control_if_else" if else_body else "control_if")
        cond = cond_fn(bid)
        inputs = {"CONDITION": [2, cond]}
        if body:
            inputs["SUBSTACK"] = [2, self._chain(body, bid)]
        if else_body:
            inputs["SUBSTACK2"] = [2, self._chain(else_body, bid)]
        self.blocks[bid]["inputs"] = inputs
        return bid

    def eq_num(self, parent, name, n):
        bid = self.b("operator_equals", parent=parent)
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, name), "OPERAND2": self.num(n)}
        return bid

    def eq_text(self, parent, name, value):
        bid = self.b("operator_equals", parent=parent)
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, name), "OPERAND2": self.text(value)}
        return bid

    def gt_num(self, parent, name, n):
        bid = self.b("operator_gt", parent=parent)
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, name), "OPERAND2": self.num(n)}
        return bid

    def lt_num(self, parent, name, n):
        bid = self.b("operator_lt", parent=parent)
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, name), "OPERAND2": self.num(n)}
        return bid

    def gt_mul(self, parent, left, right, factor):
        bid = self.b("operator_gt", parent=parent)
        mul = self.b("operator_multiply", parent=bid)
        self.blocks[mul]["inputs"] = {"NUM1": self.ivar(mul, right), "NUM2": self.num(factor)}
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, left), "OPERAND2": [3, mul, [4, "0"]]}
        return bid

    def lt_div(self, parent, left, right, divisor):
        bid = self.b("operator_lt", parent=parent)
        div = self.b("operator_divide", parent=bid)
        self.blocks[div]["inputs"] = {"NUM1": self.ivar(div, right), "NUM2": self.num(divisor)}
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, left), "OPERAND2": [3, div, [4, "0"]]}
        return bid

    def both(self, parent, fn_a, fn_b):
        bid = self.b("operator_and", parent=parent)
        left = fn_a(bid)
        right = fn_b(bid)
        self.blocks[bid]["inputs"] = {"OPERAND1": [2, left], "OPERAND2": [2, right]}
        return bid

    def touching(self, parent, sprite_name):
        bid = self.b("sensing_touchingobject", parent=parent)
        menu = self.b(
            "sensing_touchingobjectmenu",
            parent=bid,
            shadow=True,
            fields={"TOUCHINGOBJECTMENU": [sprite_name, None]},
        )
        self.blocks[bid]["inputs"] = {"TOUCHINGOBJECTMENU": [1, menu]}
        return bid

    def gt_var_xpos(self, parent, name):
        bid = self.b("operator_gt", parent=parent)
        xp = self.b("motion_xposition", parent=bid)
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, name), "OPERAND2": [3, xp, [4, "0"]]}
        return bid

    def lt_var_xpos(self, parent, name):
        bid = self.b("operator_lt", parent=parent)
        xp = self.b("motion_xposition", parent=bid)
        self.blocks[bid]["inputs"] = {"OPERAND1": self.ivar(bid, name), "OPERAND2": [3, xp, [4, "0"]]}
        return bid

    def lt_xpos(self, parent, n):
        bid = self.b("operator_lt", parent=parent)
        xp = self.b("motion_xposition", parent=bid)
        self.blocks[bid]["inputs"] = {"OPERAND1": [3, xp, [4, "0"]], "OPERAND2": self.num(n)}
        return bid

    def gt_xpos(self, parent, n):
        bid = self.b("operator_gt", parent=parent)
        xp = self.b("motion_xposition", parent=bid)
        self.blocks[bid]["inputs"] = {"OPERAND1": [3, xp, [4, "0"]], "OPERAND2": self.num(n)}
        return bid

    def percent_of(self, dest, numer, denom):
        vid, vname = self.lookup(dest)
        bid = self.b("data_setvariableto", fields={"VARIABLE": [vname, vid]})
        mul = self.b("operator_multiply", parent=bid)
        div = self.b("operator_divide", parent=mul)
        self.blocks[div]["inputs"] = {"NUM1": self.ivar(div, numer), "NUM2": self.ivar(div, denom)}
        self.blocks[mul]["inputs"] = {"NUM1": [3, div, [4, "0"]], "NUM2": self.num(100)}
        self.blocks[bid]["inputs"] = {"VALUE": [3, mul, [4, "0"]]}
        return bid

    def size_bar_percent_times(self, factor):
        """set size to (Bar Percent * factor). Bar Percent is 0 to 100."""
        bid = self.b("looks_setsizeto")
        mul = self.b("operator_multiply", parent=bid)
        self.blocks[mul]["inputs"] = {"NUM1": self.ivar(mul, "Bar Percent"), "NUM2": self.num(factor)}
        self.blocks[bid]["inputs"] = {"SIZE": [3, mul, [4, "100"]]}
        return bid

    def size_boss_bar(self):
        """set size to ((Bar Percent * Boss Bar Scale) / 100)."""
        bid = self.b("looks_setsizeto")
        div = self.b("operator_divide", parent=bid)
        mul = self.b("operator_multiply", parent=div)
        self.blocks[mul]["inputs"] = {
            "NUM1": self.ivar(mul, "Bar Percent"),
            "NUM2": self.ivar(mul, "Boss Bar Scale"),
        }
        self.blocks[div]["inputs"] = {"NUM1": [3, mul, [4, "0"]], "NUM2": self.num(100)}
        self.blocks[bid]["inputs"] = {"SIZE": [3, div, [4, "100"]]}
        return bid

    def hop(self):
        return [
            self.change_y(8),
            self.wait(0.06),
            self.change_y(-8),
        ]

    def export(self, layer: int) -> dict:
        variables = {vid: [name, value] for name, (vid, value) in self.locals.items()}
        return {
            "isStage": False,
            "name": self.name,
            "variables": variables,
            "lists": {},
            "broadcasts": {},
            "blocks": self.blocks,
            "comments": self.comments,
            "currentCostume": 0,
            "costumes": self.costumes,
            "sounds": [],
            "volume": 100,
            "layerOrder": layer,
            "visible": self.visible,
            "x": self.x,
            "y": self.sy,
            "size": self.sprite_size,
            "direction": 90,
            "draggable": False,
            "rotationStyle": "don't rotate",
        }


def fight_on_and_which(sprite: Builder, which: int):
    return lambda parent: sprite.both(
        parent,
        lambda p: sprite.eq_num(p, "Fight On", 1),
        lambda p: sprite.eq_num(p, "Which Fight", which),
    )


def hit_checks(sprite: Builder, power: int):
    stacks = []
    for which, name in FIGHTS:
        stacks.append(
            sprite.if_(
                lambda p, which=which: sprite.eq_num(p, "Which Fight", which),
                [
                    sprite.if_(
                        lambda p, name=name: sprite.touching(p, name),
                        [sprite.set_num("Hit Power", power), sprite.broadcast("arthur hits boss")],
                    )
                ],
            )
        )
    return stacks


def color_bar_costumes(sprite: Builder, width: int, height: int) -> None:
    # Left edge is the rotation center so the bar shrinks toward the right.
    for costume, fill in (("green", "#16a34a"), ("yellow", "#eab308"), ("red", "#dc2626"), ("track", "#334155")):
        sprite.add_costume(costume, bar_svg(width, height, fill), 0, height / 2)


def add_color_logic(sprite: Builder, percent_var_setup: list):
    return [
        *percent_var_setup,
        sprite.if_(
            lambda p: sprite.gt_num(p, "Bar Percent", 100),
            [sprite.set_num("Bar Percent", 100)],
        ),
        sprite.if_(
            lambda p: sprite.lt_num(p, "Bar Percent", 0),
            [sprite.set_num("Bar Percent", 0)],
        ),
        sprite.if_(
            lambda p: sprite.gt_num(p, "Bar Percent", 60),
            [sprite.costume("green")],
            [
                sprite.if_(
                    lambda p: sprite.gt_num(p, "Bar Percent", 30),
                    [sprite.costume("yellow")],
                    [sprite.costume("red")],
                )
            ],
        ),
    ]


def build():
    variables = {
        "Arthur Health": ("varArthurHealth", ARTHUR_MAX),
        "Arthur Max Health": ("varArthurMax", ARTHUR_MAX),
        "Boss Health": ("varBossHealth", 0),
        "Boss Max Health": ("varBossMax", 1),
        "Which Fight": ("varWhichFight", 0),
        "Fight On": ("varFightOn", 0),
        "Game State": ("varGameState", "title"),
        "Hit Power": ("varHitPower", PUNCH),
        "Hurt Power": ("varHurtPower", RIVAL_HURT),
        "Arthur X": ("varArthurX", -150),
        "Arthur Jumping": ("varArthurJumping", 0),
        "Arthur Busy": ("varArthurBusy", 0),
        "Arthur Hurting": ("varArthurHurting", 0),
        "Boss Hurting": ("varBossHurting", 0),
        "Quake Phase": ("varQuakePhase", 1),
        "Charge X": ("varChargeX", 160),
        "Shot Height": ("varShotHeight", 0),
        "Wave Speed": ("varWaveSpeed", 16),
    }
    messages = [
        "show title",
        "start fight",
        "intro done",
        "move left",
        "move right",
        "punch",
        "kick",
        "jump",
        "arthur hits boss",
        "boss hits arthur",
        "arthur wins round",
        "round clear",
        "arthur champion",
        "arthur loses",
        "ivy shot",
        "quake wave",
        "quake angry",
        "shake",
    ]
    broadcasts = {name: f"msg_{name.replace(' ', '_')}" for name in messages}
    sprites: list[Builder] = []

    def make(name, **kwargs):
        sprite = Builder(name, variables, broadcasts)
        sprite.visible = kwargs.get("visible", False)
        sprite.x = kwargs.get("x", 0)
        sprite.sy = kwargs.get("y", 0)
        sprite.sprite_size = kwargs.get("size", 100)
        sprite.notes = kwargs.get("notes", [])
        sprites.append(sprite)
        return sprite

    # --- Stage is built separately; scripts that need a Builder use a stage builder. ---
    stage = Builder("Stage", variables, broadcasts)
    stage.add_costume("Title", backdrop_svg("Title"), 240, 180)
    stage.add_costume("Arena", backdrop_svg("Arena"), 240, 180)
    stage.add_costume("Win", backdrop_svg("Win"), 240, 180)
    stage.add_costume("Lose", backdrop_svg("Lose"), 240, 180)

    flag = stage.hat_flag(
        "Green flag resets the arena. Which Fight: 1 Rival, 2 Brute, 3 Ivy, 4 Quake. "
        "Game State is title, intro, fight, boss, win, or lose."
    )
    stage.attach(
        flag,
        [
            stage.backdrop("Title"),
            stage.set_num("Arthur Health", ARTHUR_MAX),
            stage.set_num("Arthur Max Health", ARTHUR_MAX),
            stage.set_num("Boss Health", 0),
            stage.set_num("Boss Max Health", 1),
            stage.set_num("Which Fight", 0),
            stage.set_num("Fight On", 0),
            stage.set_text("Game State", "title"),
            stage.set_num("Hit Power", PUNCH),
            stage.set_num("Hurt Power", RIVAL_HURT),
            stage.set_num("Arthur X", -150),
            stage.set_num("Arthur Jumping", 0),
            stage.set_num("Arthur Busy", 0),
            stage.set_num("Arthur Hurting", 0),
            stage.set_num("Boss Hurting", 0),
            stage.set_num("Quake Phase", 1),
            stage.set_num("Charge X", 160),
            stage.set_num("Shot Height", 0),
            stage.set_num("Wave Speed", 16),
            stage.hide_var("Arthur Health"),
            stage.hide_var("Boss Health"),
            stage.hide_var("Game State"),
            stage.broadcast("show title"),
        ],
    )

    show_title = stage.hat_msg("show title", "Home and the green flag both come back here.")
    stage.attach(
        show_title,
        [
            stage.set_num("Which Fight", 0),
            stage.set_num("Fight On", 0),
            stage.set_text("Game State", "title"),
            stage.set_num("Arthur Health", ARTHUR_MAX),
            stage.set_num("Arthur Busy", 0),
            stage.set_num("Arthur Jumping", 0),
            stage.backdrop("Title"),
            stage.hide_var("Arthur Health"),
            stage.hide_var("Boss Health"),
        ],
    )

    start = stage.hat_msg("start fight", "The name card runs first. Fight On stays 0 until intro done.")
    stage.attach(
        start,
        [
            stage.set_text("Game State", "intro"),
            stage.set_num("Fight On", 0),
            stage.set_num("Arthur Health", ARTHUR_MAX),
            stage.set_num("Arthur Hurting", 0),
            stage.set_num("Boss Hurting", 0),
            stage.set_num("Arthur Busy", 0),
            stage.set_num("Arthur Jumping", 0),
            stage.backdrop("Arena"),
            stage.hide_var("Arthur Health"),
            stage.hide_var("Boss Health"),
        ],
    )

    intro = stage.hat_msg("intro done", "Rival is a normal fight. Brute, Ivy, and Quake are bosses.")
    stage.attach(
        intro,
        [
            stage.set_num("Fight On", 1),
            stage.if_(
                lambda p: stage.eq_num(p, "Which Fight", 1),
                [stage.set_text("Game State", "fight")],
                [stage.set_text("Game State", "boss")],
            ),
            stage.show_var("Arthur Health"),
            stage.show_var("Boss Health"),
        ],
    )

    arthur_hit = stage.hat_msg(
        "arthur hits boss",
        "Hit Power is 5 for a punch and 8 for a kick. Boss Hurting makes one hit count once.",
    )
    stage.attach(
        arthur_hit,
        [
            stage.if_(
                lambda p: stage.both(
                    p,
                    lambda pp: stage.eq_num(pp, "Fight On", 1),
                    lambda pp: stage.eq_num(pp, "Boss Hurting", 0),
                ),
                [
                    stage.set_num("Boss Hurting", 1),
                    stage.change_by_neg("Boss Health", "Hit Power"),
                    stage.if_(
                        lambda p: stage.both(
                            p,
                            lambda pp: stage.eq_num(pp, "Which Fight", 4),
                            lambda pp: stage.both(
                                pp,
                                lambda q: stage.eq_num(q, "Quake Phase", 1),
                                lambda q: stage.both(
                                    q,
                                    lambda r: stage.gt_num(r, "Boss Health", 0),
                                    lambda r: stage.lt_div(r, "Boss Health", "Boss Max Health", 2),
                                ),
                            ),
                        ),
                        [
                            stage.set_num("Quake Phase", 2),
                            stage.set_num("Fight On", 0),
                            stage.broadcast("quake angry"),
                            stage.wait(1.6),
                            stage.set_num("Fight On", 1),
                        ],
                    ),
                    stage.if_(
                        lambda p: stage.lt_num(p, "Boss Health", 1),
                        [
                            stage.set_num("Boss Health", 0),
                            stage.set_num("Fight On", 0),
                            stage.broadcast("arthur wins round"),
                        ],
                    ),
                    stage.wait(0.35),
                    stage.set_num("Boss Hurting", 0),
                ],
            )
        ],
    )

    boss_hit = stage.hat_msg(
        "boss hits arthur",
        "Hurt Power is set by the attacker just before this message. A jump does not come through here.",
    )
    stage.attach(
        boss_hit,
        [
            stage.if_(
                lambda p: stage.both(
                    p,
                    lambda pp: stage.eq_num(pp, "Fight On", 1),
                    lambda pp: stage.eq_num(pp, "Arthur Hurting", 0),
                ),
                [
                    stage.set_num("Arthur Hurting", 1),
                    stage.change_by_neg("Arthur Health", "Hurt Power"),
                    stage.if_(
                        lambda p: stage.lt_num(p, "Arthur Health", 1),
                        [
                            stage.set_num("Arthur Health", 0),
                            stage.set_num("Fight On", 0),
                            stage.broadcast("arthur loses"),
                        ],
                    ),
                    stage.wait(0.6),
                    stage.set_num("Arthur Hurting", 0),
                ],
            )
        ],
    )

    wins = stage.hat_msg("arthur wins round", "The last boss is fight 4, Quake. Anyone else is a round win.")
    stage.attach(
        wins,
        [
            stage.set_num("Fight On", 0),
            stage.if_(
                lambda p: stage.eq_num(p, "Which Fight", 4),
                [stage.set_text("Game State", "win"), stage.broadcast("arthur champion")],
                [stage.broadcast("round clear")],
            ),
        ],
    )

    loses = stage.hat_msg("arthur loses")
    stage.attach(
        loses,
        [
            stage.set_num("Fight On", 0),
            stage.set_text("Game State", "lose"),
            stage.backdrop("Lose"),
            stage.hide_var("Arthur Health"),
            stage.hide_var("Boss Health"),
        ],
    )

    champ = stage.hat_msg("arthur champion")
    stage.attach(champ, [stage.backdrop("Win"), stage.hide_var("Arthur Health"), stage.hide_var("Boss Health")])

    # --- Arthur ---
    arthur = make("Arthur", visible=True, x=-110, y=-10, size=110, notes=["The hero. His costumes say Arthur."])
    for pose, face in (
        ("idle", "smile"),
        ("punch", "smile"),
        ("kick", "smile"),
        ("jump", "smile"),
        ("hurt", "hurt"),
        ("win", "smile"),
    ):
        arthur.add_costume(pose, stick_svg("#2563eb", pose, "Arthur", face), 50, 168)
    arthur.attach(
        arthur.hat_flag("This forever block remembers Arthur's x so Brute and Rival can read it."),
        [
            arthur.show(),
            arthur.clear_fx(),
            arthur.forever([arthur.set_xpos("Arthur X")]),
        ],
    )
    arthur.attach(
        arthur.hat_msg("show title"),
        [
            arthur.show(),
            arthur.clear_fx(),
            arthur.goto(-110, -10),
            arthur.size(110),
            arthur.costume("idle"),
            arthur.say("I'm Arthur!", 2),
        ],
    )
    arthur.attach(
        arthur.hat_msg("start fight"),
        [arthur.show(), arthur.clear_fx(), arthur.goto(-150, -30), arthur.size(100), arthur.costume("idle")],
    )
    arthur.attach(
        arthur.hat_msg("move left", "Each tap steps Arthur. He cannot walk off the left edge."),
        [
            arthur.if_(
                lambda p: arthur.eq_num(p, "Fight On", 1),
                [
                    arthur.change_x(-24),
                    arthur.if_(lambda p: arthur.lt_xpos(p, -200), [arthur.set_x(-200)]),
                ],
            )
        ],
    )
    arthur.attach(
        arthur.hat_msg("move right"),
        [
            arthur.if_(
                lambda p: arthur.eq_num(p, "Fight On", 1),
                [
                    arthur.change_x(24),
                    arthur.if_(lambda p: arthur.gt_xpos(p, 110), [arthur.set_x(110)]),
                ],
            )
        ],
    )
    arthur.attach(
        arthur.hat_msg("punch", "A punch hits for Hit Power 5. Arthur Busy stops punch, kick, and jump from stacking."),
        [
            arthur.if_(
                lambda p: arthur.both(
                    p,
                    lambda pp: arthur.eq_num(pp, "Fight On", 1),
                    lambda pp: arthur.eq_num(pp, "Arthur Busy", 0),
                ),
                [
                    arthur.set_num("Arthur Busy", 1),
                    arthur.costume("punch"),
                    *hit_checks(arthur, PUNCH),
                    arthur.wait(0.18),
                    arthur.costume("idle"),
                    arthur.set_num("Arthur Busy", 0),
                ],
            )
        ],
    )
    arthur.attach(
        arthur.hat_msg("kick", "A kick steps forward and hits for Hit Power 8."),
        [
            arthur.if_(
                lambda p: arthur.both(
                    p,
                    lambda pp: arthur.eq_num(pp, "Fight On", 1),
                    lambda pp: arthur.eq_num(pp, "Arthur Busy", 0),
                ),
                [
                    arthur.set_num("Arthur Busy", 1),
                    arthur.costume("kick"),
                    arthur.change_x(28),
                    *hit_checks(arthur, KICK),
                    arthur.wait(0.18),
                    arthur.change_x(-28),
                    arthur.costume("idle"),
                    arthur.set_num("Arthur Busy", 0),
                ],
            )
        ],
    )
    arthur.attach(
        arthur.hat_msg("jump", "Arthur Jumping is 1 the whole time he is in the air. Quake's wave checks that."),
        [
            arthur.if_(
                lambda p: arthur.both(
                    p,
                    lambda pp: arthur.eq_num(pp, "Fight On", 1),
                    lambda pp: arthur.eq_num(pp, "Arthur Busy", 0),
                ),
                [
                    arthur.set_num("Arthur Busy", 1),
                    arthur.set_num("Arthur Jumping", 1),
                    arthur.costume("jump"),
                    arthur.repeat(8, [arthur.change_y(10)]),
                    arthur.wait(0.12),
                    arthur.repeat(8, [arthur.change_y(-10)]),
                    arthur.costume("idle"),
                    arthur.set_num("Arthur Jumping", 0),
                    arthur.set_num("Arthur Busy", 0),
                ],
            )
        ],
    )
    arthur.attach(
        arthur.hat_msg("boss hits arthur"),
        [arthur.color_effect(40), arthur.wait(0.12), arthur.color_effect(0)],
    )
    arthur.attach(
        arthur.hat_msg("round clear"),
        [arthur.costume("win"), arthur.say("Arthur wins!", 2), arthur.costume("idle")],
    )
    arthur.attach(
        arthur.hat_msg("arthur champion"),
        [arthur.costume("win"), arthur.say("Arthur wins!", 2), arthur.say("You are the champion!", 2)],
    )
    arthur.attach(
        arthur.hat_msg("arthur loses"),
        [arthur.costume("hurt"), arthur.say("Arthur got knocked down.", 2)],
    )

    # --- Rival, the normal enemy ---
    rival = make("Rival", x=160, y=-30, size=80, notes=["Normal enemy. Small health bar. No boss card."])
    rival.add_costume("idle", stick_svg("#64748b", "idle"), 50, 168)
    rival.add_costume("hurt", stick_svg("#64748b", "hurt", face="hurt"), 50, 168)
    rival.attach(
        rival.hat_msg("show title"),
        [rival.hide()],
    )
    rival.attach(
        rival.hat_msg("start fight", "Rival walks toward Arthur. He is not a boss."),
        [
            rival.if_(
                lambda p: rival.eq_num(p, "Which Fight", 1),
                [
                    rival.show(),
                    rival.clear_fx(),
                    rival.goto(160, -30),
                    rival.size(80),
                    rival.costume("idle"),
                    rival.say("Let's fight!", 1),
                ],
                [rival.hide()],
            )
        ],
    )
    rival.attach(
        rival.hat_flag("One loop for the whole game. It walks only when Which Fight is 1."),
        [
            rival.hide(),
            rival.forever(
                [
                    rival.if_(
                        fight_on_and_which(rival, 1),
                        [
                            rival.if_(
                                lambda p: rival.touching(p, "Arthur"),
                                [
                                    rival.set_num("Hurt Power", RIVAL_HURT),
                                    rival.broadcast("boss hits arthur"),
                                    rival.wait(0.7),
                                ],
                                [
                                    rival.if_(
                                        lambda p: rival.gt_var_xpos(p, "Arthur X"),
                                        [rival.change_x(-5)],
                                        [rival.change_x(5)],
                                    ),
                                    rival.wait(0.05),
                                ],
                            )
                        ],
                        [rival.wait(0.1)],
                    )
                ]
            )
        ],
    )
    for message in ("round clear", "arthur champion", "arthur loses"):
        rival.attach(rival.hat_msg(message), [rival.hide()])
    rival.attach(
        rival.hat_msg("arthur hits boss"),
        [
            rival.if_(
                lambda p: rival.eq_num(p, "Which Fight", 1),
                [rival.color_effect(40), rival.wait(0.12), rival.color_effect(0)],
            )
        ],
    )

    # --- Brute ---
    brute = make("Brute", x=160, y=-30, size=150, notes=["Boss 1. Charging rush with a Ready? telegraph."])
    for pose in ("idle", "lean", "charge", "hurt"):
        face = "hurt" if pose == "hurt" else "smile"
        brute.add_costume(pose, stick_svg("#dc2626", pose, face=face), 50, 168)
    brute.attach(brute.hat_msg("show title"), [brute.hide()])
    brute.attach(
        brute.hat_msg("start fight", "Splash: Brute starts big in the middle, says his name, then walks to his side."),
        [
            brute.if_(
                lambda p: brute.eq_num(p, "Which Fight", 2),
                [
                    brute.show(),
                    brute.clear_fx(),
                    brute.goto(0, 20),
                    brute.size(200),
                    brute.costume("idle"),
                    brute.say("Brute!", 1),
                    brute.glide(0.5, 160, -30),
                    brute.size(150),
                ],
                [brute.hide()],
            )
        ],
    )
    brute.attach(
        brute.hat_flag(
            "One loop for the whole game. He saves Arthur X, says Ready?, then glides to that saved x. Move during Ready? and he misses.",
        ),
        [
            brute.hide(),
            brute.forever(
                [
                    brute.if_(
                        fight_on_and_which(brute, 2),
                        [
                            brute.set_var_from_var("Charge X", "Arthur X"),
                            brute.costume("lean"),
                            brute.say("Ready?", 0.7),
                            brute.if_(
                                lambda p: brute.eq_num(p, "Fight On", 1),
                                [
                                    brute.costume("charge"),
                                    brute.glide_x_var(0.35, "Charge X", -30),
                                    brute.if_(
                                        lambda p: brute.touching(p, "Arthur"),
                                        [
                                            brute.set_num("Hurt Power", BRUTE_HURT),
                                            brute.broadcast("boss hits arthur"),
                                            brute.broadcast("shake"),
                                            *brute.hop(),
                                        ],
                                    ),
                                    brute.costume("idle"),
                                    brute.glide(0.4, 160, -30),
                                ],
                            ),
                        ],
                        [brute.wait(0.1)],
                    )
                ]
            )
        ],
    )

    for message in ("round clear", "arthur champion", "arthur loses"):
        brute.attach(brute.hat_msg(message), [brute.hide()])
    brute.attach(
        brute.hat_msg("arthur hits boss"),
        [
            brute.if_(
                lambda p: brute.eq_num(p, "Which Fight", 2),
                [brute.color_effect(40), brute.wait(0.12), brute.color_effect(0)],
            )
        ],
    )

    # --- Ivy ---
    ivy = make("Ivy", x=180, y=-30, size=130, notes=["Boss 2. Three shots, one at a time: low, high, low."])
    for pose in ("idle", "aim", "hurt"):
        face = "hurt" if pose == "hurt" else "smile"
        ivy.add_costume(pose, stick_svg("#7c3aed", pose, face=face), 50, 168)
    ivy.attach(ivy.hat_msg("show title"), [ivy.hide()])
    ivy.attach(
        ivy.hat_msg("start fight", "Splash: Ivy starts big, says her name, then steps back to her side."),
        [
            ivy.if_(
                lambda p: ivy.eq_num(p, "Which Fight", 3),
                [
                    ivy.show(),
                    ivy.clear_fx(),
                    ivy.goto(0, 20),
                    ivy.size(180),
                    ivy.costume("idle"),
                    ivy.say("Ivy!", 1),
                    ivy.glide(0.5, 180, -30),
                    ivy.size(130),
                ],
                [ivy.hide()],
            )
        ],
    )

    def one_shot(height, callout):
        return [
            ivy.costume("aim"),
            ivy.say(callout, 0.35),
            ivy.set_num("Shot Height", height),
            ivy.broadcast("ivy shot", wait=True),
        ]

    ivy.attach(
        ivy.hat_flag(
            "One loop for the whole game. She says Low or High before each shot. Jump the low ones. Stay down for the high one.",
        ),
        [
            ivy.hide(),
            ivy.forever(
                [
                    ivy.if_(
                        fight_on_and_which(ivy, 3),
                        [
                            ivy.wait(0.4),
                            *one_shot(0, "Low!"),
                            *one_shot(156, "High!"),
                            *one_shot(0, "Low!"),
                            ivy.costume("idle"),
                            ivy.wait(0.5),
                        ],
                        [ivy.wait(0.1)],
                    )
                ]
            )
        ],
    )
    for message in ("round clear", "arthur champion", "arthur loses"):
        ivy.attach(ivy.hat_msg(message), [ivy.hide()])
    ivy.attach(
        ivy.hat_msg("arthur hits boss"),
        [
            ivy.if_(
                lambda p: ivy.eq_num(p, "Which Fight", 3),
                [ivy.color_effect(40), ivy.wait(0.12), ivy.color_effect(0)],
            )
        ],
    )

    shot = make("Ivy Shot", x=150, y=0, size=100, notes=["One ball. Ivy sends it three times. No clones."])
    shot.add_costume("ball", shot_svg(), 12, 12)
    shot.attach(shot.hat_flag(), [shot.hide()])
    shot.attach(
        shot.hat_msg("ivy shot", "The ball moves left. High and low are just the y value Ivy set."),
        [
            shot.show(),
            shot.set_x(150),
            shot.set_y_var("Shot Height"),
            shot.repeat(
                18,
                [
                    shot.if_(
                        lambda p: shot.lt_num(p, "Fight On", 1),
                        [shot.hide(), shot.stop()],
                    ),
                    shot.change_x(-20),
                    shot.if_(
                        lambda p: shot.touching(p, "Arthur"),
                        [
                            shot.set_num("Hurt Power", IVY_HURT),
                            shot.broadcast("boss hits arthur"),
                            shot.hide(),
                            shot.stop(),
                        ],
                    ),
                ],
            ),
            shot.hide(),
        ],
    )
    for message in ("show title", "round clear", "arthur champion", "arthur loses"):
        shot.attach(shot.hat_msg(message), [shot.hide()])

    # --- Quake ---
    quake = make(
        "Quake",
        x=150,
        y=-30,
        size=170,
        notes=["Boss 3. Ground slam. Phase 2 starts under half health and the wave gets faster."],
    )
    for pose, color, face in (
        ("idle", "#ea580c", "smile"),
        ("raise", "#ea580c", "smile"),
        ("slam", "#ea580c", "smile"),
        ("angry", "#b91c1c", "angry"),
        ("hurt", "#ea580c", "hurt"),
    ):
        quake.add_costume(pose, stick_svg(color, pose, face=face), 50, 168)
    quake.attach(quake.hat_msg("show title"), [quake.hide()])
    quake.attach(
        quake.hat_msg("start fight", "Splash: Quake starts huge, says his name, then steps to his side."),
        [
            quake.if_(
                lambda p: quake.eq_num(p, "Which Fight", 4),
                [
                    quake.show(),
                    quake.clear_fx(),
                    quake.goto(0, 20),
                    quake.size(220),
                    quake.costume("idle"),
                    quake.say("Quake!", 1),
                    quake.glide(0.5, 150, -30),
                    quake.size(170),
                ],
                [quake.hide()],
            )
        ],
    )

    def stomp(pause, wave_speed, costume_name):
        return [
            quake.wait(pause),
            quake.costume(costume_name),
            quake.say("STOMP!", 0.7 if costume_name == "raise" else 0.25),
            quake.costume("slam"),
            *quake.hop(),
            quake.set_num("Wave Speed", wave_speed),
            quake.broadcast("shake"),
            quake.broadcast("quake wave", wait=True),
            quake.costume("idle" if costume_name == "raise" else "angry"),
        ]

    quake.attach(
        quake.hat_flag(
            "One loop for the whole game. Phase 1 waits longer and the wave is slower. Phase 2 is the angry costume and a faster wave.",
        ),
        [
            quake.hide(),
            quake.forever(
                [
                    quake.if_(
                        fight_on_and_which(quake, 4),
                        [
                            quake.if_(
                                lambda p: quake.eq_num(p, "Quake Phase", 1),
                                stomp(0.8, 16, "raise"),
                                stomp(0.25, 26, "angry"),
                            )
                        ],
                        [quake.wait(0.1)],
                    )
                ]
            )
        ],
    )
    for message in ("round clear", "arthur champion", "arthur loses"):
        quake.attach(quake.hat_msg(message), [quake.hide()])
    quake.attach(
        quake.hat_msg("arthur hits boss"),
        [
            quake.if_(
                lambda p: quake.eq_num(p, "Which Fight", 4),
                [quake.color_effect(40), quake.wait(0.12), quake.color_effect(0)],
            )
        ],
    )

    wave = make("Quake Wave", x=150, y=-40, size=80, notes=["Orange wave on the ground. Jumping Arthur is safe."])
    wave.add_costume("wave", wave_svg(), 50, 18)
    wave.attach(wave.hat_flag(), [wave.hide()])
    wave.attach(
        wave.hat_msg(
            "quake wave",
            "If Arthur Jumping is 1, the wave does not hurt him, even if the pictures touch.",
        ),
        [
            wave.show(),
            wave.goto(150, -40),
            wave.size(80),
            wave.repeat(
                24,
                [
                    wave.if_(
                        lambda p: wave.lt_num(p, "Fight On", 1),
                        [wave.hide(), wave.stop()],
                    ),
                    wave.change_x_neg_var("Wave Speed"),
                    wave.if_(
                        lambda p: wave.both(
                            p,
                            lambda pp: wave.touching(pp, "Arthur"),
                            lambda pp: wave.eq_num(pp, "Arthur Jumping", 0),
                        ),
                        [
                            wave.set_num("Hurt Power", QUAKE_HURT),
                            wave.broadcast("boss hits arthur"),
                        ],
                    ),
                ],
            ),
            wave.hide(),
        ],
    )
    for message in ("show title", "round clear", "arthur champion", "arthur loses"):
        wave.attach(wave.hat_msg(message), [wave.hide()])

    # --- Bars ---
    arthur_back = make("Arthur Bar Back", x=-220, y=110, size=70, notes=["Gray track for Arthur's health. Smaller than a boss bar."])
    color_bar_costumes(arthur_back, 150, 14)
    arthur_back.attach(arthur_back.hat_flag(), [arthur_back.hide(), arthur_back.costume("track")])
    arthur_back.attach(
        arthur_back.hat_msg("intro done"),
        [arthur_back.show(), arthur_back.goto(-220, 110), arthur_back.size(70), arthur_back.costume("track")],
    )
    for message in ("show title", "arthur loses", "arthur champion", "round clear"):
        arthur_back.attach(arthur_back.hat_msg(message), [arthur_back.hide()])

    arthur_bar = make("Arthur Bar", x=-220, y=110, size=70, notes=["Color bar. Green above 60 percent, yellow above 30, then red."])
    arthur_bar.add_local("Bar Percent", 100)
    color_bar_costumes(arthur_bar, 150, 14)
    arthur_bar.attach(
        arthur_bar.hat_flag("Left edge of the costume is the center, so the bar shrinks to the right."),
        [
            arthur_bar.hide(),
            arthur_bar.forever(
                [
                    arthur_bar.if_(
                        lambda p: arthur_bar.eq_num(p, "Fight On", 1),
                        [
                            arthur_bar.show(),
                            arthur_bar.goto(-220, 110),
                            arthur_bar.if_(
                                lambda p: arthur_bar.lt_num(p, "Arthur Max Health", 1),
                                [arthur_bar.set_num("Arthur Max Health", 1)],
                            ),
                            *add_color_logic(
                                arthur_bar,
                                [arthur_bar.percent_of("Bar Percent", "Arthur Health", "Arthur Max Health")],
                            ),
                            arthur_bar.size_bar_percent_times(0.7),
                        ],
                        [arthur_bar.hide()],
                    )
                ]
            ),
        ],
    )

    boss_back = make(
        "Boss Bar Back",
        x=-20,
        y=110,
        size=100,
        notes=["Gray track. Size 55 for Rival, size 100 for a boss, so the boss bar is bigger."],
    )
    color_bar_costumes(boss_back, 240, 22)
    boss_back.attach(boss_back.hat_flag(), [boss_back.hide(), boss_back.costume("track")])
    boss_back.attach(
        boss_back.hat_msg("intro done"),
        [
            boss_back.show(),
            boss_back.goto(-20, 110),
            boss_back.costume("track"),
            boss_back.if_(
                lambda p: boss_back.eq_num(p, "Which Fight", 1),
                [boss_back.size(55)],
                [boss_back.size(100)],
            ),
        ],
    )
    for message in ("show title", "arthur loses", "arthur champion", "round clear"):
        boss_back.attach(boss_back.hat_msg(message), [boss_back.hide()])
    # Round clear hides it, and the next intro done shows the new size. Good.

    boss_bar = make("Boss Bar", x=-20, y=110, size=100, notes=["Same colors as Arthur's bar, but the boss size is 100."])
    boss_bar.add_local("Bar Percent", 100)
    boss_bar.add_local("Boss Bar Scale", 100)
    color_bar_costumes(boss_bar, 240, 22)
    boss_bar.attach(
        boss_bar.hat_flag(),
        [
            boss_bar.hide(),
            boss_bar.forever(
                [
                    boss_bar.if_(
                        lambda p: boss_bar.eq_num(p, "Fight On", 1),
                        [
                            boss_bar.show(),
                            boss_bar.goto(-20, 110),
                            boss_bar.if_(
                                lambda p: boss_bar.eq_num(p, "Which Fight", 1),
                                [boss_bar.set_num("Boss Bar Scale", 55)],
                                [boss_bar.set_num("Boss Bar Scale", 100)],
                            ),
                            boss_bar.if_(
                                lambda p: boss_bar.lt_num(p, "Boss Max Health", 1),
                                [boss_bar.set_num("Boss Max Health", 1)],
                            ),
                            *add_color_logic(
                                boss_bar,
                                [boss_bar.percent_of("Bar Percent", "Boss Health", "Boss Max Health")],
                            ),
                            boss_bar.size_boss_bar(),
                        ],
                        [boss_bar.hide()],
                    )
                ]
            ),
        ],
    )

    label = make("Boss Label", x=90, y=145, size=100, notes=["RIVAL is the small label. BOSS is the big one."])
    label.add_costume("RIVAL", label_svg("RIVAL", "#64748b", 90, 28, 14), 45, 14)
    label.add_costume("BOSS", label_svg("BOSS", "#b91c1c", 120, 36, 20), 60, 18)
    label.attach(label.hat_flag(), [label.hide()])
    label.attach(
        label.hat_msg("intro done"),
        [
            label.show(),
            label.goto(100, 145),
            label.if_(
                lambda p: label.eq_num(p, "Which Fight", 1),
                [label.costume("RIVAL"), label.size(70)],
                [label.costume("BOSS"), label.size(120)],
            ),
        ],
    )
    for message in ("show title", "arthur loses", "arthur champion", "round clear"):
        label.attach(label.hat_msg(message), [label.hide()])

    # --- Boss card ---
    card = make("Boss Card", x=0, y=20, size=100, notes=["Name card before each boss. Rival skips the big card."])
    card.add_costume(
        "brute card",
        card_svg("BRUTE", ["Boss 1", "He runs where you stand.", "Move when he says Ready!"], "#dc2626"),
        210,
        120,
    )
    card.add_costume(
        "ivy card",
        card_svg("IVY", ["Boss 2", "Low, high, low.", "Jump the low shots."], "#7c3aed"),
        210,
        120,
    )
    card.add_costume(
        "quake card",
        card_svg("QUAKE", ["Boss 3", "He stomps. Jump the wave.", "Half health makes him faster."], "#ea580c"),
        210,
        120,
    )
    card.add_costume(
        "angry card",
        card_svg("QUAKE IS ANGRY", ["Faster stomps!", "Keep jumping."], "#b91c1c"),
        210,
        120,
    )
    card.attach(card.hat_flag(), [card.hide()])
    card.attach(card.hat_msg("show title"), [card.hide()])
    card.attach(
        card.hat_msg("start fight", "The card sets the health for this fight, then says Get ready!"),
        [
            card.if_(
                lambda p: card.eq_num(p, "Which Fight", 1),
                [
                    card.hide(),
                    card.set_num("Boss Max Health", RIVAL_HP),
                    card.set_num("Boss Health", RIVAL_HP),
                    card.wait(1.2),
                    card.broadcast("intro done"),
                ],
            ),
            card.if_(
                lambda p: card.eq_num(p, "Which Fight", 2),
                [
                    card.costume("brute card"),
                    card.show(),
                    card.front(),
                    card.goto(0, 20),
                    card.set_num("Boss Max Health", BRUTE_HP),
                    card.set_num("Boss Health", BRUTE_HP),
                    card.say("Get ready!", 2.4),
                    card.hide(),
                    card.broadcast("intro done"),
                ],
            ),
            card.if_(
                lambda p: card.eq_num(p, "Which Fight", 3),
                [
                    card.costume("ivy card"),
                    card.show(),
                    card.front(),
                    card.goto(0, 20),
                    card.set_num("Boss Max Health", IVY_HP),
                    card.set_num("Boss Health", IVY_HP),
                    card.say("Get ready!", 2.4),
                    card.hide(),
                    card.broadcast("intro done"),
                ],
            ),
            card.if_(
                lambda p: card.eq_num(p, "Which Fight", 4),
                [
                    card.costume("quake card"),
                    card.show(),
                    card.front(),
                    card.goto(0, 20),
                    card.set_num("Boss Max Health", QUAKE_HP),
                    card.set_num("Boss Health", QUAKE_HP),
                    card.set_num("Quake Phase", 1),
                    card.say("Get ready!", 2.4),
                    card.hide(),
                    card.broadcast("intro done"),
                ],
            ),
        ],
    )
    card.attach(
        card.hat_msg("quake angry", "Shown at half health. The stage pauses the fight while this card is up."),
        [
            card.costume("angry card"),
            card.show(),
            card.front(),
            card.goto(0, 20),
            card.say("Quake is angry!", 1.3),
            card.hide(),
        ],
    )
    card.attach(
        card.hat_msg("round clear", "Arthur already said Arthur wins! This waits, then starts the next fight."),
        [card.wait(2), card.change_num("Which Fight", 1), card.broadcast("start fight")],
    )

    # --- Feel ---
    ground = make("Ground", visible=True, x=0, y=-120, size=100, notes=["Shakes on a heavy hit. Buttons never shake."])
    ground.add_costume("floor", bar_svg(460, 36, "#166534"), 230, 18)
    ground.attach(ground.hat_flag(), [ground.show(), ground.goto(0, -120), ground.costume("floor")])
    ground.attach(
        ground.hat_msg("shake", "Three little hops, then the ground is back where it started."),
        [ground.repeat(3, [ground.change_y(6), ground.wait(0.05), ground.change_y(-6), ground.wait(0.05)])],
    )

    impact = make("Impact", x=0, y=-60, size=100, notes=["Orange marks during a shake. It stays behind the buttons."])
    impact.add_costume("marks", impact_svg(), 60, 40)
    impact.attach(impact.hat_flag(), [impact.hide()])
    impact.attach(
        impact.hat_msg("shake"),
        [
            impact.show(),
            impact.goto(0, -60),
            impact.repeat(3, [impact.change_y(8), impact.wait(0.05), impact.change_y(-8)]),
            impact.hide(),
        ],
    )

    # --- Buttons ---
    def add_fight_button(name, label, fill, ink, x, y, message, comment):
        button = make(name, x=x, y=y, notes=[comment])
        button.add_costume("button", button_svg(label, fill, ink), 36, 22)
        button.attach(button.hat_flag(), [button.hide(), button.goto(x, y)])
        button.attach(button.hat_click(comment), [button.broadcast(message)])
        button.attach(button.hat_msg("intro done"), [button.show(), button.front()])
        for hide_msg in ("start fight", "show title", "arthur loses", "arthur champion"):
            button.attach(button.hat_msg(hide_msg), [button.hide()])
        return button

    add_fight_button("Left Button", "LEFT", "#0284c7", "#ffffff", -190, -150, "move left", "Tap to step left.")
    add_fight_button("Right Button", "RIGHT", "#0284c7", "#ffffff", -100, -150, "move right", "Tap to step right.")
    add_fight_button("Jump Button", "JUMP", "#16a34a", "#ffffff", 0, -150, "jump", "Tap to jump. This dodges Quake's wave and Ivy's low shots.")
    add_fight_button("Punch Button", "PUNCH", "#ea580c", "#ffffff", 100, -150, "punch", "Tap to punch. A punch does 5 damage.")
    add_fight_button("Kick Button", "KICK", "#ca8a04", "#1f2937", 190, -150, "kick", "Tap to kick. A kick steps forward and does 8 damage.")

    start_btn = make("Start Button", visible=True, x=90, y=-20, notes=["Start on the title. Play again after the champion."])
    start_btn.add_costume("start", button_svg("START", "#16a34a", "#ffffff"), 36, 22)
    start_btn.add_costume("again", button_svg("AGAIN", "#16a34a", "#ffffff"), 36, 22)
    start_btn.attach(
        start_btn.hat_flag(),
        [start_btn.costume("start"), start_btn.goto(90, -20), start_btn.show(), start_btn.front()],
    )
    start_btn.attach(
        start_btn.hat_click("Sets Which Fight to 1, the Rival, then starts that fight."),
        [
            start_btn.hide(),
            start_btn.set_num("Which Fight", 1),
            start_btn.set_num("Arthur Health", ARTHUR_MAX),
            start_btn.broadcast("start fight"),
        ],
    )
    start_btn.attach(
        start_btn.hat_msg("show title"),
        [start_btn.costume("start"), start_btn.goto(90, -20), start_btn.show(), start_btn.front()],
    )
    start_btn.attach(start_btn.hat_msg("start fight"), [start_btn.hide()])
    start_btn.attach(
        start_btn.hat_msg("arthur champion"),
        [start_btn.costume("again"), start_btn.goto(0, -40), start_btn.show(), start_btn.front()],
    )

    try_again = make("Try Again", x=-80, y=-40, notes=["Shows only after a loss. Starts the same fight again."])
    try_again.add_costume("button", button_svg("RETRY", "#16a34a", "#ffffff"), 36, 22)
    try_again.attach(try_again.hat_flag(), [try_again.hide()])
    try_again.attach(try_again.hat_msg("show title"), [try_again.hide()])
    try_again.attach(try_again.hat_msg("start fight"), [try_again.hide()])
    try_again.attach(
        try_again.hat_msg("arthur loses"),
        [try_again.goto(-80, -40), try_again.show(), try_again.front()],
    )
    try_again.attach(
        try_again.hat_click("Does not change Which Fight, so you retry the same person."),
        [try_again.hide(), try_again.broadcast("start fight")],
    )

    home = make("Home Button", x=80, y=-40, notes=["Back to the title. Shows after a loss."])
    home.add_costume("button", button_svg("HOME", "#475569", "#ffffff"), 36, 22)
    home.attach(home.hat_flag(), [home.hide()])
    home.attach(home.hat_msg("show title"), [home.hide()])
    home.attach(home.hat_msg("start fight"), [home.hide()])
    home.attach(
        home.hat_msg("arthur loses"),
        [home.goto(80, -40), home.show(), home.front()],
    )
    home.attach(home.hat_click("Goes back to the title screen."), [home.hide(), home.broadcast("show title")])

    return stage, sprites, variables, broadcasts


def decompile(stage, sprites, variables, broadcasts):
    id_to_name = {vid: name for name, (vid, _value) in variables.items()}
    lines = [
        "# Block listing for Arthur's Arena bosses",
        "",
        "Generated by `tools/build_bosses_sb3.py` from the same blocks that are inside",
        "`projects/arthurs-arena-bosses.sb3`. If this file and the project ever disagree,",
        "run the script again. Do not edit this file by hand.",
        "",
        "Each heading is a sprite. Each stack is the blocks in order, the way they look",
        "in Scratch. Square brackets are words typed into a block. Parentheses are numbers",
        "or menu choices.",
        "",
        "Which Fight is 1 Rival, 2 Brute, 3 Ivy, 4 Quake.",
        f"Health: Arthur {ARTHUR_MAX}, Rival {RIVAL_HP}, Brute {BRUTE_HP}, Ivy {IVY_HP}, Quake {QUAKE_HP}.",
        f"Arthur's hits: punch {PUNCH}, kick {KICK}.",
        f"Their hits: Rival {RIVAL_HURT}, Brute {BRUTE_HURT}, Ivy {IVY_HURT}, Quake {QUAKE_HURT}.",
        "",
    ]

    def target_lines(name, builder, costume_note):
        out = [f"## {name}", ""]
        if builder.notes:
            for note in builder.notes:
                out.append(note)
            out.append("")
        out.append("Costumes: " + ", ".join(c["name"] for c in builder.costumes) + costume_note)
        out.append("")
        out.append("```")
        hats = [bid for bid, block in builder.blocks.items() if block.get("topLevel")]
        hats.sort(key=lambda bid: (builder.blocks[bid].get("y", 0), builder.blocks[bid].get("x", 0)))
        for hat in hats:
            comment_id = builder.blocks[hat].get("comment")
            if comment_id:
                out.append("// " + builder.comments[comment_id]["text"])
            out.extend(render_stack(builder, hat, 0, id_to_name))
            out.append("")
        out.append("```")
        out.append("")
        return out

    lines.extend(target_lines("Stage", stage, " (these are backdrops)"))
    for sprite in sprites:
        lines.extend(target_lines(sprite.name, sprite, ""))
    return "\n".join(lines).rstrip() + "\n"


def render_stack(builder, bid, indent, id_to_name):
    lines = []
    while bid:
        block = builder.blocks[bid]
        op = block["opcode"]
        pad = "  " * indent
        if op == "event_whenflagclicked":
            lines.append(f"{pad}when green flag clicked")
        elif op == "event_whenthisspriteclicked":
            lines.append(f"{pad}when this sprite clicked")
        elif op == "event_whenbroadcastreceived":
            lines.append(f"{pad}when I receive [{block['fields']['BROADCAST_OPTION'][0]}]")
        elif op == "data_setvariableto":
            lines.append(f"{pad}set [{block['fields']['VARIABLE'][0]}] to {value_of(builder, block, 'VALUE', id_to_name)}")
        elif op == "data_changevariableby":
            lines.append(
                f"{pad}change [{block['fields']['VARIABLE'][0]}] by {value_of(builder, block, 'VALUE', id_to_name)}"
            )
        elif op == "data_showvariable":
            lines.append(f"{pad}show variable [{block['fields']['VARIABLE'][0]}]")
        elif op == "data_hidevariable":
            lines.append(f"{pad}hide variable [{block['fields']['VARIABLE'][0]}]")
        elif op == "looks_switchcostumeto":
            menu = builder.blocks[block["inputs"]["COSTUME"][1]]
            lines.append(f"{pad}switch costume to ({menu['fields']['COSTUME'][0]})")
        elif op == "looks_switchbackdropto":
            menu = builder.blocks[block["inputs"]["BACKDROP"][1]]
            lines.append(f"{pad}switch backdrop to ({menu['fields']['BACKDROP'][0]})")
        elif op == "looks_sayforsecs":
            lines.append(
                f"{pad}say {value_of(builder, block, 'MESSAGE', id_to_name)} for {value_of(builder, block, 'SECS', id_to_name)} seconds"
            )
        elif op == "looks_show":
            lines.append(f"{pad}show")
        elif op == "looks_hide":
            lines.append(f"{pad}hide")
        elif op == "looks_setsizeto":
            lines.append(f"{pad}set size to {value_of(builder, block, 'SIZE', id_to_name)} %")
        elif op == "looks_gotofrontback":
            lines.append(f"{pad}go to {block['fields']['FRONT_BACK'][0]} layer")
        elif op == "looks_seteffectto":
            lines.append(
                f"{pad}set [{block['fields']['EFFECT'][0]}] effect to {value_of(builder, block, 'VALUE', id_to_name)}"
            )
        elif op == "looks_cleargraphiceffects":
            lines.append(f"{pad}clear graphic effects")
        elif op == "motion_gotoxy":
            lines.append(
                f"{pad}go to x: {value_of(builder, block, 'X', id_to_name)} y: {value_of(builder, block, 'Y', id_to_name)}"
            )
        elif op == "motion_glidesecstoxy":
            lines.append(
                f"{pad}glide {value_of(builder, block, 'SECS', id_to_name)} secs to x: "
                f"{value_of(builder, block, 'X', id_to_name)} y: {value_of(builder, block, 'Y', id_to_name)}"
            )
        elif op == "motion_changexby":
            lines.append(f"{pad}change x by {value_of(builder, block, 'DX', id_to_name)}")
        elif op == "motion_changeyby":
            lines.append(f"{pad}change y by {value_of(builder, block, 'DY', id_to_name)}")
        elif op == "motion_setx":
            lines.append(f"{pad}set x to {value_of(builder, block, 'X', id_to_name)}")
        elif op == "motion_sety":
            lines.append(f"{pad}set y to {value_of(builder, block, 'Y', id_to_name)}")
        elif op == "control_wait":
            lines.append(f"{pad}wait {value_of(builder, block, 'DURATION', id_to_name)} seconds")
        elif op == "event_broadcast":
            lines.append(f"{pad}broadcast {value_of(builder, block, 'BROADCAST_INPUT', id_to_name)}")
        elif op == "event_broadcastandwait":
            lines.append(f"{pad}broadcast {value_of(builder, block, 'BROADCAST_INPUT', id_to_name)} and wait")
        elif op == "control_stop":
            lines.append(f"{pad}stop {block['fields']['STOP_OPTION'][0]}")
        elif op in ("control_if", "control_if_else"):
            lines.append(f"{pad}if {expr(builder, block['inputs']['CONDITION'][1], id_to_name)} then")
            sub = block["inputs"].get("SUBSTACK")
            if sub:
                lines.extend(render_stack(builder, sub[1], indent + 1, id_to_name))
            if op == "control_if_else":
                lines.append(f"{pad}else")
                sub2 = block["inputs"].get("SUBSTACK2")
                if sub2:
                    lines.extend(render_stack(builder, sub2[1], indent + 1, id_to_name))
            lines.append(f"{pad}end")
        elif op == "control_repeat":
            lines.append(f"{pad}repeat {value_of(builder, block, 'TIMES', id_to_name)}")
            sub = block["inputs"].get("SUBSTACK")
            if sub:
                lines.extend(render_stack(builder, sub[1], indent + 1, id_to_name))
            lines.append(f"{pad}end")
        elif op == "control_forever":
            lines.append(f"{pad}forever")
            sub = block["inputs"].get("SUBSTACK")
            if sub:
                lines.extend(render_stack(builder, sub[1], indent + 1, id_to_name))
            lines.append(f"{pad}end")
        else:
            lines.append(f"{pad}[{op}]")
        bid = block.get("next")
    return lines


def value_of(builder, block, name, id_to_name):
    inp = block["inputs"][name]
    kind = inp[0]
    if kind == 1:
        prim = inp[1]
        if prim[0] == 11:
            return f"[{prim[1]}]"
        return f"[{prim[1]}]"
    return expr(builder, inp[1], id_to_name)


def expr(builder, bid, id_to_name):
    block = builder.blocks[bid]
    op = block["opcode"]
    if op == "data_variable":
        return f"({block['fields']['VARIABLE'][0]})"
    if op == "motion_xposition":
        return "(x position)"
    if op == "operator_add":
        return f"({value_of(builder, block, 'NUM1', id_to_name)} + {value_of(builder, block, 'NUM2', id_to_name)})"
    if op == "operator_subtract":
        return f"({value_of(builder, block, 'NUM1', id_to_name)} - {value_of(builder, block, 'NUM2', id_to_name)})"
    if op == "operator_multiply":
        return f"({value_of(builder, block, 'NUM1', id_to_name)} * {value_of(builder, block, 'NUM2', id_to_name)})"
    if op == "operator_divide":
        return f"({value_of(builder, block, 'NUM1', id_to_name)} / {value_of(builder, block, 'NUM2', id_to_name)})"
    if op == "operator_equals":
        return f"<{value_of(builder, block, 'OPERAND1', id_to_name)} = {value_of(builder, block, 'OPERAND2', id_to_name)}>"
    if op == "operator_gt":
        return f"<{value_of(builder, block, 'OPERAND1', id_to_name)} > {value_of(builder, block, 'OPERAND2', id_to_name)}>"
    if op == "operator_lt":
        return f"<{value_of(builder, block, 'OPERAND1', id_to_name)} < {value_of(builder, block, 'OPERAND2', id_to_name)}>"
    if op == "operator_and":
        left = expr(builder, block["inputs"]["OPERAND1"][1], id_to_name)
        right = expr(builder, block["inputs"]["OPERAND2"][1], id_to_name)
        return f"<{left} and {right}>"
    if op == "sensing_touchingobject":
        menu = builder.blocks[block["inputs"]["TOUCHINGOBJECTMENU"][1]]
        return f"<touching ({menu['fields']['TOUCHINGOBJECTMENU'][0]}) ?>"
    return f"[{op}]"


def validate(stage, sprites):
    names = {sprite.name for sprite in sprites}
    backdrops = {costume["name"] for costume in stage.costumes}
    errors = []

    def check(builder, is_stage=False):
        costumes = {costume["name"] for costume in builder.costumes}
        local_ids = {vid for _name, (vid, _value) in builder.locals.items()} if not is_stage else set()
        global_ids = {vid for _name, (vid, _value) in builder.globals.items()}
        known_vars = local_ids | global_ids
        for bid, block in builder.blocks.items():
            if block["opcode"] == "looks_switchcostumeto":
                menu = builder.blocks[block["inputs"]["COSTUME"][1]]
                costume_name = menu["fields"]["COSTUME"][0]
                if not is_stage and costume_name not in costumes:
                    errors.append(f"{builder.name} missing costume {costume_name}")
            if block["opcode"] == "looks_switchbackdropto":
                menu = builder.blocks[block["inputs"]["BACKDROP"][1]]
                backdrop_name = menu["fields"]["BACKDROP"][0]
                if backdrop_name not in backdrops:
                    errors.append(f"{builder.name} missing backdrop {backdrop_name}")
            if block["opcode"] == "sensing_touchingobject":
                menu = builder.blocks[block["inputs"]["TOUCHINGOBJECTMENU"][1]]
                touched = menu["fields"]["TOUCHINGOBJECTMENU"][0]
                if touched not in names:
                    errors.append(f"{builder.name} touches missing sprite {touched}")
            for field in block.get("fields", {}).values():
                if (
                    isinstance(field, list)
                    and len(field) == 2
                    and isinstance(field[1], str)
                    and field[1].startswith("var")
                    and field[1] not in known_vars
                ):
                    errors.append(f"{builder.name} bad variable {field}")
                if (
                    isinstance(field, list)
                    and len(field) == 2
                    and isinstance(field[1], str)
                    and field[1].startswith("msg_")
                    and field[1] not in builder.bcasts.values()
                ):
                    errors.append(f"{builder.name} bad broadcast {field}")
            nxt = block.get("next")
            if nxt:
                if nxt not in builder.blocks:
                    errors.append(f"{builder.name} next missing {nxt}")
                elif builder.blocks[nxt].get("parent") != bid:
                    errors.append(f"{builder.name} next/parent mismatch {bid} -> {nxt}")
            parent = block.get("parent")
            if parent:
                if parent not in builder.blocks:
                    errors.append(f"{builder.name} parent missing {parent}")
            elif not block.get("topLevel"):
                errors.append(f"{builder.name} block {bid} {block['opcode']} has no parent")
            for key, inp in block.get("inputs", {}).items():
                if not isinstance(inp, list) or not inp:
                    errors.append(f"{builder.name} bad input {key}")
                    continue
                if inp[0] in (2, 3):
                    if inp[1] not in builder.blocks:
                        errors.append(f"{builder.name} input block missing {inp[1]}")
                    elif builder.blocks[inp[1]].get("parent") != bid:
                        errors.append(f"{builder.name} input parent mismatch {key} {inp[1]}")
                if inp[0] == 1 and isinstance(inp[1], list) and inp[1][0] == 11:
                    if inp[1][2] not in builder.bcasts.values():
                        errors.append(f"{builder.name} broadcast id {inp[1]}")
                if inp[0] == 3 and isinstance(inp[2], list) and inp[2][0] == 12:
                    if inp[2][2] not in known_vars:
                        errors.append(f"{builder.name} reporter var {inp[2]}")
        if not builder.costumes:
            errors.append(f"{builder.name} has no costumes")

    check(stage, is_stage=True)
    for sprite in sprites:
        check(sprite)
    if len({sprite.name for sprite in sprites}) != len(sprites):
        errors.append("duplicate sprite name")
    if errors:
        raise SystemExit("validation failed:\n" + "\n".join(errors))


def write_sb3(stage, sprites, variables):
    assets = {}
    assets.update(stage.assets)
    targets = []
    stage_target = {
        "isStage": True,
        "name": "Stage",
        "variables": {vid: [name, value] for name, (vid, value) in variables.items()},
        "lists": {},
        # Scratch stores broadcasts as id -> name. The builder keeps name -> id.
        "broadcasts": {bid: name for name, bid in stage.bcasts.items()},
        "blocks": stage.blocks,
        "comments": stage.comments,
        "currentCostume": 0,
        "costumes": stage.costumes,
        "sounds": [],
        "volume": 100,
        "layerOrder": 0,
        "tempo": 60,
        "videoTransparency": 50,
        "videoState": "off",
        "textToSpeechLanguage": None,
    }
    targets.append(stage_target)
    for index, sprite in enumerate(sprites, start=1):
        assets.update(sprite.assets)
        targets.append(sprite.export(index))
    project = {
        "targets": targets,
        "monitors": [
            {
                "id": variables["Arthur Health"][0],
                "mode": "default",
                "opcode": "data_variable",
                "params": {"VARIABLE": "Arthur Health"},
                "spriteName": None,
                "value": ARTHUR_MAX,
                "width": 0,
                "height": 0,
                "x": 5,
                "y": 5,
                "visible": False,
                "sliderMin": 0,
                "sliderMax": 100,
                "isDiscrete": True,
            },
            {
                "id": variables["Boss Health"][0],
                "mode": "default",
                "opcode": "data_variable",
                "params": {"VARIABLE": "Boss Health"},
                "spriteName": None,
                "value": 0,
                "width": 0,
                "height": 0,
                "x": 250,
                "y": 5,
                "visible": False,
                "sliderMin": 0,
                "sliderMax": 100,
                "isDiscrete": True,
            },
        ],
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "2.3.0", "agent": "arthurs-arena bosses builder"},
    }
    SB3_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(project, indent=1).encode("utf-8")
    with zipfile.ZipFile(SB3_PATH, "w") as archive:
        info = zipfile.ZipInfo("project.json")
        info.date_time = (2026, 11, 3, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, payload)
        for filename in sorted(assets):
            asset_info = zipfile.ZipInfo(filename)
            asset_info.date_time = (2026, 11, 3, 0, 0, 0)
            asset_info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(asset_info, assets[filename])
    return project


def assert_listing(text: str):
    required = [
        "Arthur's Arena",
        "I'm Arthur!",
        "Arthur wins!",
        "say [Get ready!]",
        "say [Ready?]",
        "say [Low!]",
        "say [High!]",
        "say [STOMP!]",
        "say [Quake is angry!]",
        "set [Quake Phase] to [2]",
        "(Boss Max Health) / [2]",
        "set [Boss Bar Scale] to [100]",
        "set [Boss Bar Scale] to [55]",
        "set [Hit Power] to [5]",
        "set [Hit Power] to [8]",
        "broadcast [shake]",
        "when this sprite clicked",
        "switch costume to (green)",
        "switch costume to (yellow)",
        "switch costume to (red)",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit("listing missing:\n" + "\n".join(missing))
    for sprite_name in ("Arthur", "Rival", "Brute", "Ivy", "Quake", "Ivy Shot", "Quake Wave", "Boss Card"):
        if f"## {sprite_name}" not in text:
            raise SystemExit(f"listing missing sprite {sprite_name}")


def parse_with_scratch(path: Path):
    parser_dir = Path("/tmp/scratch-tools")
    if not (parser_dir / "node_modules" / "scratch-parser").exists():
        print("scratch-parser not installed; skipped schema check")
        return
    script = """
const fs = require('fs');
const parser = require('scratch-parser');
parser(fs.readFileSync(process.argv[1]), false, function (err, project) {
  if (err) {
    console.error(JSON.stringify(err.sb3Errors || err, null, 2).slice(0, 4000));
    process.exit(1);
  }
  console.log('scratch-parser ok', project[0].targets.length, 'targets');
});
"""
    import subprocess

    result = subprocess.run(
        ["node", "-e", script, str(path)],
        cwd=parser_dir,
        capture_output=True,
        text=True,
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit("scratch-parser rejected the sb3")


def main():
    stage, sprites, variables, broadcasts = build()
    validate(stage, sprites)
    listing = decompile(stage, sprites, variables, broadcasts)
    assert_listing(listing)
    LISTING_PATH.parent.mkdir(parents=True, exist_ok=True)
    LISTING_PATH.write_text(listing, encoding="utf-8")
    write_sb3(stage, sprites, variables)
    # Arthur's name is drawn on every hero costume.
    arthur = next(sprite for sprite in sprites if sprite.name == "Arthur")
    for costume in arthur.costumes:
        svg = arthur.assets[costume["md5ext"]].decode("utf-8")
        if "Arthur" not in svg:
            raise SystemExit(f"Arthur costume {costume['name']} does not draw his name")
    title = stage.assets[stage.costumes[0]["md5ext"]].decode("utf-8")
    if "Arthur's Arena" not in title:
        raise SystemExit("title backdrop is missing Arthur's Arena")
    win = stage.assets[stage.costumes[2]["md5ext"]].decode("utf-8")
    if "Arthur wins!" not in win:
        raise SystemExit("win backdrop is missing Arthur wins!")
    parse_with_scratch(SB3_PATH)
    print(f"wrote {SB3_PATH} and {LISTING_PATH}")
    print(f"sprites: {len(sprites)} blocks: {sum(len(s.blocks) for s in sprites) + len(stage.blocks)}")


if __name__ == "__main__":
    main()
