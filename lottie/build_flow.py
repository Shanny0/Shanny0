#!/usr/bin/env python3
"""Scene: the flow diagram (assets/frame76-flow.svg).

The graph builds itself in flow order - start, card, decision - and a pulse travels each
connector, popping the node it arrives at. The error branch fires last, in red.
Tweak the timeline constants below and re-run `python3 build.py`.
"""

import os

import lottiekit as lk
from lottiekit import (anim, comp, el, fill, grp, layer, opacity, pos, rc, scale, sh,
                       stack, svg_paths, tr, wipe)
from lottiekit import SHEET, PANEL, PURPLE, RED

SVG_PATH = os.path.join(lk.HERE, "assets", "frame76-flow.svg")
STEM = "frame76-flow"

W, H = 385, 366
FPS = 60
DUR = 300
SHOW_CARD = False
lk.setup(W, H, FPS, DUR)

PAPER = "#E9E8DE"
WIRE = "#D7D5C8"

# --- geometry lifted from the source svg -------------------------------------
CARD_R = (0, 0, W, 365.5, 32)
START = (91.9404, 82.6846, 41.3857)                        # the circle node
CARD_N = (248.789, 41.2988, 92.0039, 76.5254, 12)
NODES = [(46.6406, 156.478, 123.5, 53.5625, 12, PURPLE),
         (46.6406, 218.629, 123.5, 53.5625, 12, SHEET),
         (46.6406, 280.744, 123.5, 53.6333, 12, RED)]
DIAMOND = (294.789, 199.407, 65.0573, 65.0573, 10)         # rotated 45 about its origin
DIAMOND_C = (294.789, 245.41)                              # ... which puts its centre here
LABELS = [(166.887, 76.0117, 51.2295, 13.3473, 6.67365),
          (269.176, 153.603, 51.2295, 13.3473, 6.67365)]
BAR_H, BAR_R = 10.9213, 5.46067
CARD_BARS = [(261.426, 58.5371, 39.8694), (261.426, 74.1016, 61.3762),
             (261.426, 89.666, 61.3762)]
NODE_BARS = [[(61.2539, 169.86, 45.6006), (61.25, 185.771, 87.6299)],
             [(61.2539, 231.977, 45.6006), (61.25, 247.887, 87.6299)],
             [(61.2539, 294.145, 45.6006), (61.25, 310.056, 87.6299)]]

# Waypoints a pulse follows along each connector, taken off the source paths.
ROUTES = [
    [(135, 83.1), (246, 83.1)],                                        # start -> card
    [(294.8, 120.5), (294.8, 200)],                                    # card -> decision
    [(253, 245.4), (231, 245.4), (224.9, 239), (224.9, 214),           # decision -> purple
     (219, 187), (200, 183.3), (176, 183.3)],
    [(253, 245.4), (176, 246.3)],                                      # decision -> cream
    [(253, 245.4), (231, 245.4), (224.9, 252), (224.9, 276),           # decision -> red
     (219, 303), (200, 307.5), (176, 307.5)],
]

# --- timeline ----------------------------------------------------------------
START_IN, START_OUT = (0, 18), (272, 292)
WIRE_IN = [(16, 28), (54, 64), (92, 104), (92, 104), (92, 104)]
WIRE_OUT = [(262, 276), (256, 270), (238, 252), (238, 252), (238, 252)]
PULSE = [(18, 40), (58, 78), (100, 120), (122, 142), (144, 164)]       # first run
PULSE2 = [(186, 208), (194, 214), (204, 224), (208, 228), (212, 232)]  # idle second run
CARD_IN, CARD_OUT = (36, 52), (258, 274)
LABEL_IN = [(50, 62), (88, 100)]
LABEL_OUT = [(254, 266), (248, 260)]
DIAMOND_IN, DIAMOND_OUT = (76, 92), (242, 258)
NODE_IN = [(116, 132), (138, 154), (160, 176)]
NODE_OUT = [(226, 242), (230, 246), (234, 250)]
ALARM = (176, 224)                                          # the red node keeps flashing


def ctr(x, y, w, h):
    return (x + w / 2.0, y + h / 2.0)


def pop(name, items, center, t_in, t_out, s0=0.6, over=1.07, extra_scale=()):
    a, b = t_in
    c, e = t_out
    keys = [(0, s0, "out"), (a, s0, "out"), (b - 5, over, "out"), (b, 1.0, "out")]
    keys += list(extra_scale) + [(c, 1.0, "in"), (e, s0, "in")]
    return grp(items, name, tr(
        anchor=center, s=scale(keys),
        o=opacity([(0, 0, "out"), (a, 0, "out"), (a + 9, 100, "out"),
                   (c, 100, "in"), (e, 0, "in")])))


def build():
    P = svg_paths(SVG_PATH)
    assert len(P) == 5, "unexpected path count in source svg: %d" % len(P)
    back_to_front = []
    add = back_to_front.append

    if SHOW_CARD:
        add(layer("card", [grp([rc(*CARD_R[:4], r=CARD_R[4]), fill(PAPER)], "card")]))

    # 1. connectors - they simply fade up; the pulses below carry the motion
    wires = []
    for i, d in enumerate(P):
        a, b = WIRE_IN[i]
        c, e = WIRE_OUT[i]
        wires.append(grp(sh(d) + [fill(RED if i == 4 else WIRE)], "wire%d" % i, tr(
            o=opacity([(0, 0, "out"), (a, 0, "out"), (b, 100, "out"),
                       (c, 100, "in"), (e, 0, "in")]))))
    add(layer("wires", wires))

    # 2. nodes, in flow order
    add(layer("start", [pop("start", [el(*START), fill(SHEET)], START[:2],
                            START_IN, START_OUT)]))

    ca, cb = CARD_IN
    card_items = [grp([rc(*CARD_N[:4], r=CARD_N[4]), fill(SHEET)], "plate")]
    card_items += [wipe((x, y, w, BAR_H, BAR_R), PANEL, (cb - 4 + i * 5, cb + 8 + i * 5),
                        (CARD_OUT[0] - i * 3, CARD_OUT[0] + 8 - i * 3), name="cardbar%d" % i)
                   for i, (x, y, w) in enumerate(CARD_BARS)]
    add(layer("card-node", [pop("card", stack(card_items), ctr(*CARD_N[:4]),
                                CARD_IN, CARD_OUT)]))

    # the decision diamond spins into place (its 45 deg sits on the inner group)
    da, db = DIAMOND_IN
    dc, dd = DIAMOND_OUT
    add(layer("decision", [grp([grp([rc(*DIAMOND[:4], r=DIAMOND[4]), fill(SHEET)], "square",
                                    tr(anchor=DIAMOND[:2], r=45))], "decision", tr(
        anchor=DIAMOND_C,
        r=anim([(0, -50, "out"), (da, -50, "out"), (db, 0, "out"),
                (dc, 0, "in"), (dd, 40, "in")]),
        s=scale([(0, 0.3, "out"), (da, 0.3, "out"), (db - 5, 1.08, "out"), (db, 1.0, "out"),
                 (dc, 1.0, "in"), (dd, 0.3, "in")]),
        o=opacity([(0, 0, "out"), (da, 0, "out"), (da + 9, 100, "out"),
                   (dc, 100, "in"), (dd, 0, "in")])))]))

    for i, geo in enumerate(NODES):
        a, b = NODE_IN[i]
        c, e = NODE_OUT[i]
        items = [grp([rc(*geo[:4], r=geo[4]), fill(geo[5])], "plate")]
        items += [wipe((x, y, w, BAR_H, BAR_R), PANEL, (b - 2 + j * 5, b + 10 + j * 5),
                       (c - j * 3, c + 8 - j * 3), name="bar%d" % j)
                  for j, (x, y, w) in enumerate(NODE_BARS[i])]
        # the error node keeps flashing once it has arrived
        extra = ()
        if i == 2:
            extra = tuple(k for t in range(ALARM[0], ALARM[1], 24) for k in
                          ((t, 1.0, "out"), (t + 6, 1.035, "out"), (t + 16, 1.0, "soft")))
        add(layer("node%d" % i, [pop("node%d" % i, stack(items), ctr(*geo[:4]),
                                     NODE_IN[i], NODE_OUT[i], s0=0.8, over=1.05,
                                     extra_scale=extra)]))

    for i, geo in enumerate(LABELS):
        add(layer("label%d" % i, [pop("label%d" % i, [rc(*geo[:4], r=geo[4]), fill(SHEET)],
                                      ctr(*geo[:4]), LABEL_IN[i], LABEL_OUT[i],
                                      s0=0.7, over=1.06)]))

    # 3. the pulses that travel the connectors
    pulses = []
    for i, route in enumerate(ROUTES):
        color = RED if i == 4 else PURPLE
        keys, fade = [], [(0, 0, "linear")]
        for run, (a, b) in enumerate(((PULSE[i]), (PULSE2[i]))):
            span = b - a
            for j, (x, y) in enumerate(route):
                t = a + int(round(span * j / float(len(route) - 1)))
                keys.append((t, (x - route[0][0], y - route[0][1]),
                             "soft" if 0 < j < len(route) - 1 else "out"))
            if run == 0:
                keys.append((b + 1, (0, 0), "linear"))      # reset while invisible
            fade += [(a - 1, 0, "out"), (a + 3, 100, "linear"), (b - 4, 100, "in"),
                     (b, 0, "linear")]
        fade.append((DUR, 0, "linear"))
        pulses.append(grp([el(route[0][0], route[0][1], 3.4), fill(color)], "pulse%d" % i, tr(
            anchor=route[0], p=pos(route[0], keys), o=opacity(fade))))
    add(layer("pulses", pulses))

    return comp(back_to_front, "Frame 76 - Flow Diagram")


def main():
    lk.setup(W, H, FPS, DUR)
    lk.write(build(), STEM)


if __name__ == "__main__":
    main()
