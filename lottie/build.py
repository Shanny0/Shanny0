#!/usr/bin/env python3
"""
Build a seamless, looping Lottie animation from the "Frame 76" collaborative-canvas
illustration (lottie/assets/frame76-canvas.svg).

Everything is generated from this script so the animation stays editable: tweak the
timeline constants below, re-run `python3 build.py`, and frame76-canvas.json is rebuilt.

    python3 build.py

Output: frame76-canvas.json  (Lottie / bodymovin v5.7.x schema, 385x366, 60fps, 5s loop)
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(HERE, "assets", "frame76-canvas.svg")
OUT_PATH = os.path.join(HERE, "frame76-canvas.json")

# ---------------------------------------------------------------- composition
W, H = 385, 366
FPS = 60
DUR = 300                      # 5s loop; frame 300 == frame 0 so the loop is seamless

# ------------------------------------------------------------------- palette
PAPER = "#E9E8DE"
SHEET = "#FFFDF0"
PANEL = "#F3F1E4"
PURPLE = "#5F1CFC"
PURPLE_DEEP = "#4816BD"
RED = "#FF352E"
RED_TINT = "#FFECEC"
INK = "#000000"
WHITE = "#FFFFFF"


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)] + [1]


# ------------------------------------------------------------------- easing
# (out_tangent, in_tangent) control points of the segment that starts on a keyframe.
EASES = {
    "linear": ((0.333, 0.333), (0.667, 0.667)),
    "out":    ((0.16, 1.00), (0.30, 1.00)),    # expo-ish settle
    "soft":   ((0.25, 0.10), (0.25, 1.00)),
    "inout":  ((0.65, 0.00), (0.35, 1.00)),
    "in":     ((0.70, 0.00), (0.84, 0.00)),
}


def _ease(name):
    o, i = EASES[name]
    return {"o": {"x": [o[0]], "y": [o[1]]}, "i": {"x": [i[0]], "y": [i[1]]}}


def anim(keys):
    """keys: [(frame, value, ease_for_segment_starting_here), ...]"""
    clean = []
    for t, v, e in keys:
        v = list(v) if isinstance(v, (list, tuple)) else [v]
        if clean and clean[-1][0] == t:      # dedupe stacked keyframes
            clean[-1] = (t, v, e)
            continue
        clean.append((t, v, e))
    if len(clean) == 1:
        return {"a": 0, "k": clean[0][1]}
    out = []
    for idx, (t, v, e) in enumerate(clean):
        kf = {"t": t, "s": v}
        if idx < len(clean) - 1:
            kf.update(_ease(e))
        out.append(kf)
    return {"a": 1, "k": out}


def val(v):
    return {"a": 0, "k": v}


def pos(anchor, keys):
    """Animated position expressed as (dx, dy) offsets from the layer anchor."""
    ax, ay = anchor
    return anim([(t, [ax + d[0], ay + d[1]], e) for t, d, e in keys])


def scale(keys):
    """keys use 1.0 == 100%."""
    return anim([(t, [v * 100.0, v * 100.0], e) for t, v, e in keys])


def opacity(keys):
    return anim([(t, [v], e) for t, v, e in keys])


# ------------------------------------------------------------- svg path parse
_TOKENS = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")
_NUM = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def _nums(chunk):
    return [float(n) for n in _NUM.findall(chunk)]


def parse_path(d):
    """SVG path data -> list of lottie bezier shapes ({i, o, v, c})."""
    subpaths, verts = [], []
    cx = cy = sx = sy = 0.0
    prev_cmd = ""
    prev_ctrl = None

    def flush(closed):
        if len(verts) < 2:
            verts.clear()
            return
        pts = list(verts)
        if closed and abs(pts[0]["p"][0] - pts[-1]["p"][0]) < 1e-9 \
                and abs(pts[0]["p"][1] - pts[-1]["p"][1]) < 1e-9:
            pts[0]["ci"] = pts[-1]["ci"]
            pts.pop()
        subpaths.append({
            "i": [[v["ci"][0] - v["p"][0], v["ci"][1] - v["p"][1]] for v in pts],
            "o": [[v["co"][0] - v["p"][0], v["co"][1] - v["p"][1]] for v in pts],
            "v": [list(v["p"]) for v in pts],
            "c": bool(closed),
        })
        verts.clear()

    def add(p):
        verts.append({"p": p, "ci": p, "co": p})

    for cmd, chunk in _TOKENS.findall(d):
        args = _nums(chunk)
        rel = cmd.islower()
        c = cmd.upper()
        if c == "A":
            raise ValueError("elliptical arcs are not supported by this converter")
        if c == "Z":
            flush(True)
            cx, cy = sx, sy
            add((cx, cy))            # start a fresh subpath at the close point
            verts.clear()
            prev_cmd, prev_ctrl = c, None
            continue
        step = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2}[c]
        for k in range(0, len(args), step):
            a = args[k:k + step]
            if len(a) < step:
                break
            if c == "M":
                x, y = (cx + a[0], cy + a[1]) if rel else (a[0], a[1])
                flush(False)
                cx, cy = sx, sy = x, y
                add((cx, cy))
                c = "L"                       # subsequent pairs are implicit lineto
                prev_ctrl = None
            elif c in ("L", "H", "V", "T"):
                if c == "L":
                    x, y = (cx + a[0], cy + a[1]) if rel else (a[0], a[1])
                elif c == "H":
                    x, y = (cx + a[0], cy) if rel else (a[0], cy)
                elif c == "V":
                    x, y = (cx, cy + a[0]) if rel else (cx, a[0])
                else:                          # T -> smooth quadratic
                    x, y = (cx + a[0], cy + a[1]) if rel else (a[0], a[1])
                if c == "T":
                    q = prev_ctrl if prev_cmd in ("Q", "T") and prev_ctrl else (cx, cy)
                    qx, qy = 2 * cx - q[0], 2 * cy - q[1]
                    verts[-1]["co"] = (cx + 2.0 / 3 * (qx - cx), cy + 2.0 / 3 * (qy - cy))
                    add((x, y))
                    verts[-1]["ci"] = (x + 2.0 / 3 * (qx - x), y + 2.0 / 3 * (qy - y))
                    prev_ctrl = (qx, qy)
                else:
                    add((x, y))
                    prev_ctrl = None
                cx, cy = x, y
            elif c in ("C", "S"):
                if c == "C":
                    x1, y1, x2, y2, x, y = a
                    if rel:
                        x1, y1, x2, y2, x, y = cx + x1, cy + y1, cx + x2, cy + y2, cx + x, cy + y
                else:
                    x2, y2, x, y = a
                    if rel:
                        x2, y2, x, y = cx + x2, cy + y2, cx + x, cy + y
                    if prev_cmd in ("C", "S") and prev_ctrl:
                        x1, y1 = 2 * cx - prev_ctrl[0], 2 * cy - prev_ctrl[1]
                    else:
                        x1, y1 = cx, cy
                verts[-1]["co"] = (x1, y1)
                add((x, y))
                verts[-1]["ci"] = (x2, y2)
                cx, cy, prev_ctrl = x, y, (x2, y2)
            elif c == "Q":
                x1, y1, x, y = a
                if rel:
                    x1, y1, x, y = cx + x1, cy + y1, cx + x, cy + y
                verts[-1]["co"] = (cx + 2.0 / 3 * (x1 - cx), cy + 2.0 / 3 * (y1 - cy))
                add((x, y))
                verts[-1]["ci"] = (x + 2.0 / 3 * (x1 - x), y + 2.0 / 3 * (y1 - y))
                cx, cy, prev_ctrl = x, y, (x1, y1)
            prev_cmd = c
    flush(False)
    return subpaths


# ----------------------------------------------------------------- shape defs
def sh(d, name="path"):
    """SVG path data -> lottie 'sh' items (one per subpath)."""
    return [{"ty": "sh", "ind": n, "ks": val(p), "nm": name, "hd": False}
            for n, p in enumerate(parse_path(d))]


def rc(x, y, w, h, r=0.0, name="rect"):
    return {"ty": "rc", "d": 1, "s": val([w, h]), "p": val([x + w / 2.0, y + h / 2.0]),
            "r": val(r), "nm": name, "hd": False}


def el(cx, cy, r, name="ellipse"):
    return {"ty": "el", "d": 1, "s": val([r * 2, r * 2]), "p": val([cx, cy]),
            "nm": name, "hd": False}


def fill(color, op=100):
    return {"ty": "fl", "c": val(rgb(color)),
            "o": op if isinstance(op, dict) else val(op),
            "r": 1, "bm": 0, "nm": "fill", "hd": False}


def stroke(color, width, op=100, dash=None):
    s = {"ty": "st", "c": val(rgb(color)),
         "o": op if isinstance(op, dict) else val(op),
         "w": width if isinstance(width, dict) else val(width),
         "lc": 2, "lj": 2, "ml": 4, "bm": 0, "nm": "stroke", "hd": False}
    if dash:
        d, g, off = dash
        s["d"] = [{"n": "d", "nm": "dash", "v": val(d)},
                  {"n": "g", "nm": "gap", "v": val(g)},
                  {"n": "o", "nm": "offset", "v": off if isinstance(off, dict) else val(off)}]
    return s


def trim(start, end, offset=0):
    return {"ty": "tm", "s": start if isinstance(start, dict) else val(start),
            "e": end if isinstance(end, dict) else val(end),
            "o": offset if isinstance(offset, dict) else val(offset),
            "m": 1, "nm": "trim", "hd": False}


def tr(anchor=(0, 0), p=None, s=None, r=0, o=100):
    return {"ty": "tr",
            "p": p if isinstance(p, dict) else val(list(p or anchor)),
            "a": val(list(anchor)),
            "s": s if isinstance(s, dict) else val(list(s or [100, 100])),
            "r": r if isinstance(r, dict) else val(r),
            "o": o if isinstance(o, dict) else val(o),
            "sk": val(0), "sa": val(0), "nm": "Transform"}


def grp(items, name="group", transform=None):
    return {"ty": "gr", "np": len(items) + 1, "nm": name, "bm": 0, "hd": False,
            "it": items + [transform or tr()]}


def layer(name, shapes, anchor=(0, 0), p=None, s=None, o=None, r=None, mask=None):
    # `shapes` is written back-to-front for readability; lottie paints the first
    # group in the list on top, so flip it here.
    shapes = list(reversed(shapes))
    lyr = {"ddd": 0, "ind": 0, "ty": 4, "nm": name, "sr": 1,
           "ks": {"o": o if isinstance(o, dict) else val(100 if o is None else o),
                  "r": r if isinstance(r, dict) else val(0 if r is None else r),
                  "p": p if isinstance(p, dict) else val(list(anchor)),
                  "a": val(list(anchor)),
                  "s": s if isinstance(s, dict) else val([100, 100])},
           "ao": 0, "shapes": shapes, "ip": 0, "op": DUR, "st": 0, "bm": 0}
    if mask:
        lyr["hasMask"] = True
        lyr["masksProperties"] = mask
    return lyr


def rounded_mask(x, y, w, h, r=0.0, name="clip"):
    """Rounded-rect alpha mask - mirrors the clip-paths in the source svg.

    Masks live in layer space and are applied before the layer transform, so any
    layer that is masked must animate on its *group* transform instead.
    """
    c = r * 0.5523
    v = [[x + r, y], [x + w - r, y], [x + w, y + r], [x + w, y + h - r],
         [x + w - r, y + h], [x + r, y + h], [x, y + h - r], [x, y + r]]
    o = [[0, 0], [c, 0], [0, 0], [0, c], [0, 0], [-c, 0], [0, 0], [0, -c]]
    i = [[-c, 0], [0, 0], [0, -c], [0, 0], [c, 0], [0, 0], [0, c], [0, 0]]
    return [{"inv": False, "mode": "a", "pt": val({"i": i, "o": o, "v": v, "c": True}),
             "o": val(100), "x": val(0), "nm": name}]


# ============================================================ scene + timeline
def ctr(x, y, w, h):
    return (x + w / 2.0, y + h / 2.0)


def load_paths():
    svg = open(SVG_PATH).read()
    d = re.findall(r'<path\s+d="([^"]+)"', svg)
    assert len(d) == 11, "unexpected path count in source svg: %d" % len(d)
    return {
        "you_text": d[0], "you_arrow": d[1], "measure": d[2], "badge_blob": d[3],
        "mark_s": d[4], "mark_h1": d[5], "mark_h2": d[6], "mark_y": d[7],
        "me_text": d[8], "me_arrow": d[9], "connector": d[10],
    }


# --- geometry lifted from the source svg -------------------------------------
SHEET_R = (34.5234, 90.3408, 315.943, 191.996, 14.582)
TOPBAR_R = (95.6016, 95.8384, 249.148, 37.6085, 14.582)
MAIN_R = (95.6016, 138.946, 143.413, 135.575, 14.582)
SIDE_R = (344.75 - 100.861, 138.946, 100.861, 62.212, 14.582)       # mirrored in svg
CTA_R = (344.75 - 100.861, 274.521 - 69.5238, 100.861, 69.5238, 14.582)  # 180deg in svg
BAR_R = (39.582, 95.8384, 52.7826, 178.682, 9.72134)
SEL_R = (33.6358, 89.4962, 316.551, 192.604)
PILL_YOU = (253.582, 146.744, 53.4674, 21.7211, 10.8606)
PILL_ME = (31.332, 326.431, 58.268, 23.6714, 11.8357)
TICKS = [(348.445, 87.9536), (189.891, 87.9536), (189.891, 280.581), (189.891, 306.902),
         (32.4883, 87.9536), (348.469, 279.74), (32.5117, 279.74)]
TICK_W, TICK_H = 4.04185, 3.64491
HAIR = 0.607584
BADGE_C = (67.8802, 68.2878, 10.7773)
CTA_C = ctr(*CTA_R[:4])

# --- timeline ----------------------------------------------------------------
IN = {"bar": (0, 16), "top": (6, 22), "main": (12, 28), "side": (18, 34), "cta": (24, 42)}
OUT = {"cta": (260, 276), "side": (264, 280), "main": (268, 284),
       "top": (272, 288), "bar": (276, 292)}
SEL_IN, SEL_OUT = (30, 60), (250, 276)
TICK_T0, TICK_T1 = 46, 242
LINE_IN, LINE_OUT = (58, 70), (240, 252)
YOU_IN, YOU_OUT = (50, 80), (230, 250)
ME_IN, ME_OUT = (66, 96), (224, 244)
BADGE_IN, BADGE_OUT = (86, 106), (220, 236)
CONN_IN, CONN_OUT = (96, 116), (214, 232)
CLICK = 84
ANTS_IN, ANTS_OUT = (108, 122), (212, 226)


def sheet_mask():
    return rounded_mask(*SHEET_R[:4], r=SHEET_R[4], name="canvas-clip")


def panel(name, items, center, tin, tout, dx, dy, s0=0.93):
    """A wireframe block that slides in from under the canvas edge and back out."""
    a, b = tin
    c, e = tout
    return layer(name, [grp(items, name, tr(
        anchor=center,
        p=pos(center, [(0, (dx, dy), "out"), (a, (dx, dy), "out"), (b, (0, 0), "out"),
                       (c, (0, 0), "in"), (e, (dx, dy), "in")]),
        s=scale([(0, s0, "out"), (a, s0, "out"), (b, 1.0, "out"),
                 (c, 1.0, "in"), (e, s0, "in")]),
        o=opacity([(0, 0, "out"), (a, 0, "out"), (b, 100, "out"),
                   (c, 100, "in"), (e, 0, "in")])))],
        anchor=center, mask=sheet_mask())


def build():
    P = load_paths()
    back_to_front = []
    add = back_to_front.append

    # 1. the card itself - always on screen, it is the stage
    add(layer("card", [grp([rc(0, 0, W, 365.5, 32), fill(PAPER)], "card")]))
    add(layer("sheet", [grp([rc(*SHEET_R[:4], r=SHEET_R[4]), fill(SHEET)], "sheet")],
              anchor=ctr(*SHEET_R[:4])))

    # 2. wireframe blocks stagger in, then leave in reverse order
    add(panel("topbar", [rc(*TOPBAR_R[:4], r=TOPBAR_R[4]), fill(PANEL)],
              ctr(*TOPBAR_R[:4]), IN["top"], OUT["top"], 0, -14))
    add(panel("main-block", [rc(*MAIN_R[:4], r=MAIN_R[4]), fill(PANEL)],
              ctr(*MAIN_R[:4]), IN["main"], OUT["main"], -12, 10))
    add(panel("side-block", [rc(*SIDE_R[:4], r=SIDE_R[4]), fill(PANEL)],
              ctr(*SIDE_R[:4]), IN["side"], OUT["side"], 12, -10))

    # 3. the purple CTA: pops in, gets clicked at frame 84, breathes while live
    a, b = IN["cta"]
    c, e = OUT["cta"]
    add(layer("cta", [grp([rc(*CTA_R[:4], r=CTA_R[4]), fill(PURPLE)], "cta", tr(
              anchor=CTA_C,
              p=pos(CTA_C, [(0, (0, 16), "out"), (a, (0, 16), "out"), (b, (0, 0), "out"),
                            (c, (0, 0), "in"), (e, (0, 16), "in")]),
              s=scale([(0, 0.9, "out"), (a, 0.9, "out"), (b - 6, 1.06, "out"), (b, 1.0, "out"),
                       (CLICK - 4, 1.0, "out"), (CLICK + 1, 0.945, "out"),
                       (CLICK + 8, 1.035, "out"), (CLICK + 14, 1.0, "soft"),
                       (168, 1.015, "soft"), (c, 1.0, "in"), (e, 0.9, "in")]),
              o=opacity([(0, 0, "out"), (a, 0, "out"), (b, 100, "out"),
                         (c, 100, "in"), (e, 0, "in")])))],
              anchor=CTA_C, mask=sheet_mask()))

    add(panel("sidebar", [rc(*BAR_R[:4], r=BAR_R[4]), fill(PANEL)],
              ctr(*BAR_R[:4]), IN["bar"], OUT["bar"], -26, 0))

    # 4. selection frame draws itself on, retracts the same way on the way out
    sel_center = ctr(*SEL_R)
    add(layer("selection", [grp([rc(*SEL_R),
                                 trim(anim([(0, 0, "out"), (SEL_IN[0], 0, "out"),
                                            (SEL_OUT[0], 0, "in"), (SEL_OUT[1], 100, "in")]),
                                      anim([(0, 0, "out"), (SEL_IN[0], 0, "out"),
                                            (SEL_IN[1], 100, "out")]), -12),
                                 stroke(INK, HAIR)], "selection")],
              anchor=sel_center))

    # 5. marching ants over the selection while the board is "live"
    add(layer("ants", [grp([rc(*SEL_R),
                            stroke(PURPLE, 1.1,
                                   dash=(5, 4, anim([(0, 0, "linear"), (DUR, 240, "linear")])))],
                           "ants")],
              anchor=sel_center,
              o=opacity([(0, 0, "out"), (ANTS_IN[0], 0, "out"), (ANTS_IN[1], 62, "soft"),
                         (ANTS_OUT[0], 62, "in"), (ANTS_OUT[1], 0, "in")])))

    # 6. measurement ticks pop in one by one
    tick_groups = []
    for i, (tx, ty) in enumerate(TICKS):
        t_in = TICK_T0 + i * 3
        t_out = TICK_T1 + i * 2
        tc = ctr(tx, ty, TICK_W, TICK_H)
        tick_groups.append(grp(
            [rc(tx, ty, TICK_W, TICK_H), fill(INK)], "tick%d" % i,
            tr(anchor=tc,
               s=scale([(0, 0.1, "out"), (t_in, 0.1, "out"), (t_in + 8, 1.35, "out"),
                        (t_in + 13, 1.0, "out"), (t_out, 1.0, "in"), (t_out + 10, 0.1, "in")]),
               o=opacity([(0, 0, "out"), (t_in, 0, "out"), (t_in + 5, 100, "out"),
                          (t_out, 100, "in"), (t_out + 10, 0, "in")]))))
    add(layer("ticks", tick_groups))

    # 7. the little measurement line under the frame
    add(layer("measure-line", [grp(sh(P["measure"]) + [
        trim(anim([(0, 0, "out"), (LINE_OUT[0], 0, "in"), (LINE_OUT[1], 100, "in")]),
             anim([(0, 0, "out"), (LINE_IN[0], 0, "out"), (LINE_IN[1], 100, "out")])),
        stroke(INK, HAIR)], "measure")], anchor=(191.91, 295.74)))

    # 8. click ripple on the CTA
    rings = []
    for i, (delay, r, w) in enumerate(((0, 46, 2.0), (7, 34, 1.4))):
        t = CLICK + delay
        rings.append(grp([el(CTA_C[0], CTA_C[1], r), stroke(RED, w)], "ring%d" % i,
                         tr(anchor=CTA_C,
                            s=scale([(0, 0.12, "out"), (t, 0.12, "out"), (t + 26, 1.0, "out")]),
                            o=opacity([(0, 0, "linear"), (t - 1, 0, "out"), (t + 2, 85, "out"),
                                       (t + 26, 0, "linear"), (DUR, 0, "linear")]))))
    add(layer("click-ripple", rings))

    # 9. connector slides out from behind the left edge of the card
    add(layer("connector", [grp(sh(P["connector"]) + [fill(INK)], "connector", tr(
        anchor=(30, 200),
        p=pos((30, 200), [(0, (-46, 0), "out"), (CONN_IN[0], (-46, 0), "out"),
                          (CONN_IN[1], (0, 0), "out"), (CONN_OUT[0], (0, 0), "in"),
                          (CONN_OUT[1], (-46, 0), "in")]),
        o=opacity([(0, 0, "out"), (CONN_IN[0], 0, "out"), (CONN_IN[0] + 12, 100, "out"),
                   (CONN_OUT[0], 100, "in"), (CONN_OUT[1] - 6, 0, "in")])))],
        mask=rounded_mask(0, 0, W, 365.5, 32, name="card-clip")))

    # 10. avatar badge + presence pulses
    ring_keys_s, ring_keys_o = [(0, 1.0, "linear")], [(0, 0, "linear")]
    for t in (112, 158, 204):
        ring_keys_s += [(t, 1.0, "out"), (t + 34, 2.45, "linear"), (t + 45, 1.0, "linear")]
        ring_keys_o += [(t - 1, 0, "out"), (t + 1, 65, "soft"), (t + 34, 0, "linear")]
    ring_keys_s.append((DUR, 1.0, "linear"))
    ring_keys_o.append((DUR, 0, "linear"))
    add(layer("presence-pulse",
              [grp([el(BADGE_C[0], BADGE_C[1], BADGE_C[2]), stroke(PURPLE, 1.6)], "pulse",
                   tr(anchor=BADGE_C[:2], s=scale(ring_keys_s), o=opacity(ring_keys_o)))]))

    badge_anchor = (57.5, 79.5)          # the bubble tail, so it pops from the corner
    ba, bb = BADGE_IN
    bc, bd = BADGE_OUT
    add(layer("avatar-badge", [
        grp(sh(P["badge_blob"]) + [fill(PURPLE)], "bubble"),
        grp([el(*BADGE_C), fill(PURPLE_DEEP)], "disc"),
        grp(sh(P["mark_s"]) + sh(P["mark_h1"]) + sh(P["mark_h2"]) + sh(P["mark_y"]) +
            [fill(WHITE)], "monogram"),
    ], anchor=badge_anchor,
        s=scale([(0, 0.25, "out"), (ba, 0.25, "out"), (bb - 6, 1.09, "out"), (bb, 1.0, "out"),
                 (bc, 1.0, "in"), (bd, 0.25, "in")]),
        o=opacity([(0, 0, "out"), (ba, 0, "out"), (ba + 10, 100, "out"),
                   (bc, 100, "in"), (bd, 0, "in")])))

    # 11. the two cursors
    me_anchor = (98.5, 309.0)
    ma, mb = ME_IN
    mc, md = ME_OUT
    add(layer("cursor-me", [
        grp([rc(*PILL_ME[:4], r=PILL_ME[4]), fill(PURPLE)], "pill"),
        grp(sh(P["me_text"]) + [fill(RED_TINT)], "label"),
        grp(sh(P["me_arrow"]) + [fill(PURPLE)], "arrow"),
    ], anchor=me_anchor,
        p=pos(me_anchor, [(0, (-58, 34), "out"), (ma, (-58, 34), "out"), (mb, (0, 0), "out"),
                          (128, (5, -4), "soft"), (170, (-4, 3), "soft"),
                          (206, (3, 2), "soft"), (mc, (0, 0), "in"), (md, (-58, 34), "in")]),
        s=scale([(0, 0.55, "out"), (ma, 0.55, "out"), (mb - 5, 1.05, "out"), (mb, 1.0, "out"),
                 (mc, 1.0, "in"), (md, 0.55, "in")]),
        o=opacity([(0, 0, "out"), (ma, 0, "out"), (ma + 14, 100, "out"),
                   (mc, 100, "in"), (md, 0, "in")])))

    you_anchor = (245.9, 130.2)
    ya, yb = YOU_IN
    yc, yd = YOU_OUT
    add(layer("cursor-you", [
        grp([rc(*PILL_YOU[:4], r=PILL_YOU[4]), fill(RED)], "pill",
            tr(anchor=PILL_YOU[:2], r=1.71188)),
        grp(sh(P["you_text"]) + [fill(RED_TINT)], "label"),
        grp(sh(P["you_arrow"]) + [fill(RED)], "arrow"),
    ], anchor=you_anchor,
        p=pos(you_anchor, [(0, (76, 52), "out"), (ya, (76, 52), "out"), (yb, (0, 0), "out"),
                           (124, (-4, 5), "soft"), (164, (4, -3), "soft"),
                           (202, (-3, -2), "soft"), (yc, (0, 0), "in"), (yd, (76, 52), "in")]),
        s=scale([(0, 0.5, "out"), (ya, 0.5, "out"), (yb - 6, 1.06, "out"), (yb, 1.0, "out"),
                 (CLICK, 1.0, "out"), (CLICK + 3, 0.88, "out"), (CLICK + 11, 1.0, "soft"),
                 (yc, 1.0, "in"), (yd, 0.5, "in")]),
        o=opacity([(0, 0, "out"), (ya, 0, "out"), (ya + 16, 100, "out"),
                   (yc, 100, "in"), (yd, 0, "in")])))

    layers = list(reversed(back_to_front))          # lottie draws index 0 on top
    for i, lyr in enumerate(layers):
        lyr["ind"] = i + 1

    return {
        "v": "5.7.4", "fr": FPS, "ip": 0, "op": DUR, "w": W, "h": H,
        "nm": "Frame 76 - Collab Canvas", "ddd": 0, "assets": [], "layers": layers,
        "markers": [],
    }


PREVIEW_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Frame 76 - Collab Canvas</title>
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>
<style>
  :root { --bg:#141414; --fg:#e9e8de; --muted:#7c7c74; --accent:#5f1cfc; }
  body.light { --bg:#f3f1e4; --fg:#1b1b1b; --muted:#8a897e; }
  * { box-sizing:border-box; }
  body { margin:0; min-height:100vh; background:var(--bg); color:var(--fg);
         font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;
         display:flex; flex-direction:column; align-items:center; justify-content:center;
         gap:18px; padding:24px; transition:background .25s; }
  #stage { width:min(385px,90vw); aspect-ratio:385/366; }
  .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; justify-content:center;
         width:min(385px,90vw); }
  button { font:inherit; color:var(--fg); background:transparent; cursor:pointer;
           border:1px solid var(--muted); border-radius:999px; padding:6px 14px; }
  button:hover { border-color:var(--accent); color:var(--accent); }
  input[type=range] { flex:1; min-width:140px; accent-color:var(--accent); }
  .meta { color:var(--muted); letter-spacing:.06em; text-transform:uppercase; font-size:11px; }
</style>
</head>
<body>
  <div id="stage"></div>
  <div class="row">
    <button id="toggle">pause</button>
    <input type="range" id="scrub" min="0" max="__DUR__" step="1" value="0">
    <span class="meta" id="counter">0</span>
  </div>
  <div class="row">
    <button data-speed="0.25">0.25x</button>
    <button data-speed="0.5">0.5x</button>
    <button data-speed="1">1x</button>
    <button data-speed="2">2x</button>
    <button id="bg">light</button>
  </div>
  <div class="meta">frame76-canvas &middot; __DUR__f &middot; __FPS__fps &middot; seamless loop</div>
<script>
  const anim = lottie.loadAnimation({
    container: document.getElementById('stage'), renderer: 'svg',
    loop: true, autoplay: true, animationData: __DATA__
  });
  const scrub = document.getElementById('scrub'), counter = document.getElementById('counter'),
        toggle = document.getElementById('toggle');
  anim.addEventListener('enterFrame', () => {
    const f = Math.round(anim.currentFrame);
    scrub.value = f; counter.textContent = f;
  });
  scrub.addEventListener('input', () => { anim.goToAndStop(+scrub.value, true);
    toggle.textContent = 'play'; });
  toggle.onclick = () => {
    if (anim.isPaused) { anim.play(); toggle.textContent = 'pause'; }
    else { anim.pause(); toggle.textContent = 'play'; }
  };
  document.querySelectorAll('[data-speed]').forEach(b =>
    b.onclick = () => anim.setSpeed(parseFloat(b.dataset.speed)));
  document.getElementById('bg').onclick = e => {
    document.body.classList.toggle('light');
    e.target.textContent = document.body.classList.contains('light') ? 'dark' : 'light';
  };
</script>
</body>
</html>
"""


def write_preview(doc):
    html = (PREVIEW_TEMPLATE
            .replace("__DATA__", json.dumps(doc, separators=(",", ":")))
            .replace("__DUR__", str(DUR))
            .replace("__FPS__", str(FPS)))
    with open(os.path.join(HERE, "preview.html"), "w") as f:
        f.write(html)


if __name__ == "__main__":
    doc = build()
    with open(OUT_PATH, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    write_preview(doc)
    print("wrote %s (%d layers, %.1fs loop, %.0f KB)"
          % (os.path.basename(OUT_PATH), len(doc["layers"]), DUR / float(FPS),
             os.path.getsize(OUT_PATH) / 1024.0))
