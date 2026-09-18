#!/usr/bin/env python3
"""Scene: the collaborative design canvas (assets/frame76-canvas.svg).

A design file assembling itself, two cursors working on it, then a reset.
Tweak the timeline constants below and re-run `python3 build.py`.
"""

import os
import re

import lottiekit as lk
from lottiekit import (anim, comp, el, fill, grp, layer, linear_gradient, opacity, pos,
                       rc, rgb, rounded_mask, scale, sh, stroke, trim, tr, val)
from lottiekit import PAPER, SHEET, PANEL, PURPLE, PURPLE_DEEP, RED, RED_TINT, INK, WHITE

SVG_PATH = os.path.join(lk.HERE, "assets", "frame76-canvas.svg")
STEM = "frame76-canvas"

W, H = 385, 366
FPS = 60
DUR = 300                      # 5s loop; frame 300 == frame 0 so the loop is seamless
SHOW_CARD = False              # the paper-coloured card behind everything; off = transparent
                               # background, so the animation takes the page/section colour
lk.setup(W, H, FPS, DUR)

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

    # 1. the stage. The card is the paper-coloured plate the whole scene sits on; with
    #    SHOW_CARD off it is simply absent, leaving the composition on transparency.
    if SHOW_CARD:
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

    return comp(back_to_front, "Frame 76 - Collab Canvas")




def main():
    lk.setup(W, H, FPS, DUR)
    lk.write(build(), STEM)


if __name__ == "__main__":
    main()
