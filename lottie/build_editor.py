#!/usr/bin/env python3
"""Scene: the code editor (assets/frame76-editor.svg).

The editor opens, code types itself in line by line, an error toast slides in pointing at
the highlighted line, the caret blinks and the Go Live button pulses - then it unwinds.
Tweak the timeline constants below and re-run `python3 build.py`.
"""

import os

import lottiekit as lk
from lottiekit import (anim, comp, el, fill, grp, layer, opacity, pos, rc, scale, sh,
                       stack, stroke, svg_paths, tr, wipe)
from lottiekit import SHEET, PANEL, PURPLE, RED, WHITE

SVG_PATH = os.path.join(lk.HERE, "assets", "frame76-editor.svg")
STEM = "frame76-editor"

W, H = 386, 366
FPS = 60
DUR = 300
SHOW_CARD = False
lk.setup(W, H, FPS, DUR)

PAPER = "#E9E8DE"
ORANGE = "#FFC05A"                     # the highlighted line the error points at
BLUE = "#1C50FC"                       # the logo
TOAST_BG = "#C7AFFF"
LIGHT_RED, LIGHT_GREEN = "#FF0808", "#21E63B"

# --- geometry lifted from the source svg -------------------------------------
CARD_R = (0, 0, W, 365.5, 32)
PLATE_R = (26.7578, 26.6582, 332.482, 305.341, 31.0187)
LIGHTS = [(291.328, 44.1367, LIGHT_RED), (309.727, 44.1367, PANEL),
          (328.121, 44.1377, LIGHT_GREEN)]
LIGHT_S = (10.9253, 10.2907, 5.14533)
LINE_H, LINE_R = 13.3473, 6.67365
# code lines in reading order: (x, y, width, colour)
CODE = [(49.3789, 100.324, 103.654), (158.773, 100.324, 176.419),
        (49.3789, 126.093, 131.864), (309.723 - 118.664, 126.093, 118.664),
        (49.3789, 151.861, 36.8817), (90.6523, 151.861, 125.055),
        (220.098, 151.861, 102.798),
        (49.3789, 179.328, 102.798, ORANGE), (235.059 - 71.837, 179.328, 71.837),
        (49.3789, 206.796, 69.7324), (128.355, 206.796, 52.8896),
        (49.3789, 234.264, 85.5062), (146.219, 234.264, 64.8535),
        (49.3789, 261.73, 85.5062), (146.219, 261.73, 35.0254),
        (49.3789, 289.197, 85.5062)]
ERROR_LINE = 7                         # index into CODE - the orange one
CARET = (49.3789 + 102.798 + 5, 179.328, 2.8, LINE_H, 1.4)
BTN_R = (146, 318.384, 104, 36, 12.9782)
RING_R = (143.5, 315.884, 109, 41, 15.4782)
DOT = (171.001, 336.384, 6.23145)
TOAST_R = (231.23, 199.958, 150, 41, 10)
TOAST_TILT = 1.83912
TOAST_AVATAR = (249.185, 221.045, 11.6227)

# --- timeline ----------------------------------------------------------------
PLATE_IN, PLATE_OUT = (0, 24), (268, 292)
LIGHT_T0, LIGHT_T1 = 12, 258
LOGO_IN, LOGO_OUT = (20, 38), (250, 266)
TYPE_T0, TYPE_STEP, TYPE_LEN = 30, 3, 10          # code typing itself in
UNTYPE_T0, UNTYPE_STEP = 218, 2
FLASH = 92                             # the error line flashes as the toast arrives
TOAST_IN, TOAST_OUT = (98, 122), (206, 228)
BTN_IN, BTN_OUT = (84, 104), (214, 232)
CARET_ON, CARET_OFF = 88, 206
PULSES = (130, 172, 214)               # go-live ring + dot


def ctr(x, y, w, h):
    return (x + w / 2.0, y + h / 2.0)


def load_paths():
    d = svg_paths(SVG_PATH)
    assert len(d) == 4, "unexpected path count in source svg: %d" % len(d)
    return {"logo": d[0], "btn_text": d[1], "toast_1": d[2], "toast_2": d[3]}


def build():
    P = load_paths()
    back_to_front = []
    add = back_to_front.append

    if SHOW_CARD:
        add(layer("card", [grp([rc(*CARD_R[:4], r=CARD_R[4]), fill(PAPER)], "card")]))

    # 1. the editor plate
    a, b = PLATE_IN
    c, e = PLATE_OUT
    plate_c = ctr(*PLATE_R[:4])
    add(layer("plate", [grp([rc(*PLATE_R[:4], r=PLATE_R[4]), fill(SHEET)], "plate", tr(
        anchor=plate_c,
        s=scale([(0, 0.95, "out"), (b, 1.0, "out"), (c, 1.0, "in"), (e, 0.95, "in")]),
        o=opacity([(0, 0, "out"), (b - 8, 100, "out"), (c, 100, "in"), (e, 0, "in")])))],
        anchor=plate_c))

    # 2. window lights
    lights = []
    for i, (x, y, color) in enumerate(LIGHTS):
        t_in, t_out = LIGHT_T0 + i * 3, LIGHT_T1 + i * 2
        gc = ctr(x, y, LIGHT_S[0], LIGHT_S[1])
        lights.append(grp([rc(x, y, LIGHT_S[0], LIGHT_S[1], LIGHT_S[2]), fill(color)],
                          "light%d" % i, tr(
            anchor=gc,
            s=scale([(0, 0.1, "out"), (t_in, 0.1, "out"), (t_in + 7, 1.3, "out"),
                     (t_in + 12, 1.0, "out"), (t_out, 1.0, "in"), (t_out + 10, 0.1, "in")]),
            o=opacity([(0, 0, "out"), (t_in, 0, "out"), (t_in + 5, 100, "out"),
                       (t_out, 100, "in"), (t_out + 10, 0, "in")]))))
    add(layer("lights", lights))

    # 3. the logo
    la, lb = LOGO_IN
    lc, ld = LOGO_OUT
    logo_c = (68.8, 61.4)
    add(layer("logo", [grp(sh(P["logo"]) + [fill(BLUE, rule=2)], "logo", tr(
        anchor=logo_c,
        s=scale([(0, 0.4, "out"), (la, 0.4, "out"), (lb - 5, 1.1, "out"), (lb, 1.0, "out"),
                 (lc, 1.0, "in"), (ld, 0.4, "in")]),
        o=opacity([(0, 0, "out"), (la, 0, "out"), (la + 10, 100, "out"),
                   (lc, 100, "in"), (ld, 0, "in")])))]))

    # 4. the code types itself in, line by line, and untypes on the way out
    lines = []
    n = len(CODE)
    for i, row in enumerate(CODE):
        x, y, w = row[0], row[1], row[2]
        color = row[3] if len(row) > 3 else PANEL
        t_in = TYPE_T0 + i * TYPE_STEP
        t_out = UNTYPE_T0 + (n - 1 - i) * UNTYPE_STEP
        lines.append(wipe((x, y, w, LINE_H, LINE_R), color,
                          (t_in, t_in + TYPE_LEN), (t_out, t_out + TYPE_LEN),
                          name="code%d" % i))
    add(layer("code", lines))

    # the error line gets a nudge of attention when the toast lands
    ex, ey, ew = CODE[ERROR_LINE][:3]
    err_c = ctr(ex, ey, ew, LINE_H)
    add(layer("error-line", [grp([rc(ex, ey, ew, LINE_H, LINE_R), fill(ORANGE)], "flash", tr(
        anchor=err_c,
        s=scale([(0, 1.0, "out"), (FLASH, 1.0, "out"), (FLASH + 6, 1.06, "out"),
                 (FLASH + 16, 1.0, "out")]),
        o=opacity([(0, 0, "linear"), (FLASH, 0, "out"), (FLASH + 6, 100, "out"),
                   (FLASH + 30, 0, "linear"), (DUR, 0, "linear")])))]))

    # 5. the caret, blinking where the code stopped
    blink = [(0, 0, "linear"), (CARET_ON - 1, 0, "linear")]   # stay dark until it opens
    t = CARET_ON
    while t < CARET_OFF:
        blink += [(t, 100, "linear"), (t + 16, 100, "linear"),
                  (t + 17, 0, "linear"), (t + 30, 0, "linear")]
        t += 32
    blink.append((DUR, 0, "linear"))
    add(layer("caret", [grp([rc(*CARET[:4], r=CARET[4]), fill(PURPLE)], "caret")],
              o=opacity(blink)))

    # 6. Go Live, with a ring that pulses out of the button
    ba, bb = BTN_IN
    bc, bd = BTN_OUT
    btn_c = ctr(*BTN_R[:4])
    ring_s, ring_o = [(0, 1.0, "linear")], [(0, 0, "linear")]
    for t in PULSES:
        ring_s += [(t, 1.0, "out"), (t + 30, 1.22, "linear"), (t + 34, 1.0, "linear")]
        ring_o += [(t - 1, 0, "out"), (t + 2, 60, "soft"), (t + 30, 0, "linear")]
    ring_s.append((DUR, 1.0, "linear"))
    ring_o.append((DUR, 0, "linear"))
    add(layer("go-live", [grp(stack([
        grp([rc(*RING_R[:4], r=RING_R[4]), stroke(RED, 5, op=14)], "ring"),
        grp([rc(*RING_R[:4], r=RING_R[4]), stroke(RED, 5)], "pulse",
            tr(anchor=btn_c, s=scale(ring_s), o=opacity(ring_o))),
        grp([rc(*BTN_R[:4], r=BTN_R[4]), fill(RED)], "button"),
        grp([el(*DOT), fill(SHEET)], "dot", tr(
            anchor=DOT[:2],
            s=scale([(0, 1.0, "linear")] + [k for t in PULSES for k in
                     ((t, 1.0, "out"), (t + 6, 1.3, "out"), (t + 16, 1.0, "linear"))] +
                    [(DUR, 1.0, "linear")]))),
        grp(sh(P["btn_text"]) + [fill(WHITE)], "label"),
    ]), "go-live", tr(
        anchor=btn_c,
        p=pos(btn_c, [(0, (0, 18), "out"), (ba, (0, 18), "out"), (bb, (0, 0), "out"),
                      (bc, (0, 0), "in"), (bd, (0, 18), "in")]),
        s=scale([(0, 0.85, "out"), (ba, 0.85, "out"), (bb - 5, 1.05, "out"),
                 (bb, 1.0, "out"), (bc, 1.0, "in"), (bd, 0.85, "in")]),
        o=opacity([(0, 0, "out"), (ba, 0, "out"), (ba + 12, 100, "out"),
                   (bc, 100, "in"), (bd, 0, "in")])))]))

    # 7. the error toast slides in from the right
    ta, tb = TOAST_IN
    tc, td = TOAST_OUT
    toast_c = ctr(*TOAST_R[:4])
    add(layer("toast", [grp(stack([
        grp([rc(*TOAST_R[:4], r=TOAST_R[4]), fill(TOAST_BG)], "plate",
            tr(anchor=TOAST_R[:2], r=TOAST_TILT)),
        grp([el(*TOAST_AVATAR), fill(PURPLE)], "avatar", tr(
            anchor=TOAST_AVATAR[:2],
            s=scale([(0, 0.2, "out"), (tb - 10, 0.2, "out"), (tb + 2, 1.12, "out"),
                     (tb + 8, 1.0, "out"), (tc, 1.0, "in"), (tc + 10, 0.2, "in")]))),
        grp(sh(P["toast_1"]) + sh(P["toast_2"]) + [fill(PURPLE)], "text", tr(
            anchor=toast_c,
            o=opacity([(0, 0, "out"), (tb, 0, "out"), (tb + 12, 100, "out"),
                       (tc, 100, "in"), (tc + 8, 0, "in")]))),
    ]), "toast", tr(
        anchor=toast_c,
        p=pos(toast_c, [(0, (150, 0), "out"), (ta, (150, 0), "out"), (tb - 5, (-8, 0), "out"),
                        (tb, (0, 0), "out"), (tc, (0, 0), "in"), (td, (150, 0), "in")]),
        r=anim([(0, 5, "out"), (ta, 5, "out"), (tb, 0, "out"), (tc, 0, "in"), (td, 4, "in")]),
        o=opacity([(0, 0, "out"), (ta, 0, "out"), (ta + 10, 100, "out"),
                   (tc, 100, "in"), (td - 6, 0, "in")])))]))

    return comp(back_to_front, "Frame 76 - Code Editor")


def main():
    lk.setup(W, H, FPS, DUR)
    lk.write(build(), STEM)


if __name__ == "__main__":
    main()
