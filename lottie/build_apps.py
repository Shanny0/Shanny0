#!/usr/bin/env python3
"""Scene: the two app tiles (assets/frame76-apps.svg).

A window fills with content, two app tiles spin in from opposite corners, and a pulse is
handed from one to the other and back - the two apps talking to each other.
Tweak the timeline constants below and re-run `python3 build.py`.
"""

import os

import lottiekit as lk
from lottiekit import (anim, comp, fill, grp, layer, opacity, pos, rc, scale, sh, stack,
                       stroke, svg_paths, tr, wipe, el)
from lottiekit import SHEET, PANEL

SVG_PATH = os.path.join(lk.HERE, "assets", "frame76-apps.svg")
STEM = "frame76-apps"

W, H = 515, 325
FPS = 60
DUR = 300
lk.setup(W, H, FPS, DUR)

TILE_EDGE = "#F1EFE4"
CLAUDE = "#D97757"
GEM = "#26251E"
LIGHT_RED, LIGHT_GREEN = "#FF0808", "#21E63B"

# --- geometry lifted from the source svg -------------------------------------
PLATE_R = (68.7383, 0, 395, 294, 32)
LIGHTS = [(95.3867, 21.0962, LIGHT_RED), (117.263, 21.0962, PANEL),
          (139.14, 21.0962, LIGHT_GREEN)]
LIGHT_S = (12.9911, 12.2365, 6.11825)
BAR_H, BAR_R = 8.87354, 4.43677
BARS = [(198.389, 99.4434, 135.701), (216.609, 114.698, 99.2588),
        (197.129, 189.365, 108.524), (335.348 - 26.2607, 189.365, 26.2607)]
BLOCK_R = (157.555, 134.688, 217.368, 46.1416, 12)
# each tile is rotated about its own top-left corner, so its centre lands off to one side
TILE_L = (-3.29774, 227.893, 109.22, 109.22, 21.5574)
TILE_L_ROT, TILE_L_C = -23.8664, (68.73, 255.74)
TILE_R = (419.928, 11.9824, 98.7316, 98.7316, 19.6395)
TILE_R_ROT, TILE_R_C = 13.5948, (456.31, 71.56)

# the hand-off route, tile to tile, bowed slightly over the window
ROUTE = [(68.73, 255.74), (160, 205), (260, 145), (360, 105), (456.31, 71.56)]

# --- timeline ----------------------------------------------------------------
PLATE_IN, PLATE_OUT = (0, 24), (266, 292)
LIGHT_T0, LIGHT_T1 = 12, 254
CONTENT_T0, CONTENT_STEP = 28, 7       # bars and block filling in
CONTENT_OUT0, CONTENT_STEP_OUT = 236, 5
TILE_L_IN, TILE_L_OUT = (58, 84), (226, 252)
TILE_R_IN, TILE_R_OUT = (70, 96), (220, 246)
HANDOFF = ((104, 146), (176, 218))     # there and back


def ctr(x, y, w, h):
    return (x + w / 2.0, y + h / 2.0)


def tile(name, geo, angle, center, mark, mark_color, t_in, t_out, dx, dy, spin, pulses):
    """An app tile: plate, outline and logo, spun in from off-frame."""
    a, b = t_in
    c, e = t_out
    beat = [(0, 1.0, "linear")]
    for t in pulses:
        beat += [(t, 1.0, "out"), (t + 7, 1.09, "out"), (t + 20, 1.0, "soft")]
    beat.append((DUR, 1.0, "linear"))
    contents = [
        grp([rc(*geo[:4], r=geo[4]), fill(SHEET)], "plate", tr(anchor=geo[:2], r=angle)),
        grp([rc(*geo[:4], r=geo[4]), stroke(TILE_EDGE, 5)], "edge",
            tr(anchor=geo[:2], r=angle)),
        grp(sh(mark) + [fill(mark_color)], "mark", tr(anchor=center, s=scale(beat))),
    ]
    return layer(name, [grp(stack(contents), name, tr(
        anchor=center,
        p=pos(center, [(0, (dx, dy), "out"), (a, (dx, dy), "out"), (b, (0, 0), "out"),
                       (150, (0, -5), "soft"), (200, (0, 4), "soft"),
                       (c, (0, 0), "in"), (e, (dx, dy), "in")]),
        r=anim([(0, spin, "out"), (a, spin, "out"), (b, 0, "out"), (150, -1.5, "soft"),
                (200, 1.5, "soft"), (c, 0, "in"), (e, -spin, "in")]),
        s=scale([(0, 0.7, "out"), (a, 0.7, "out"), (b - 6, 1.06, "out"), (b, 1.0, "out"),
                 (c, 1.0, "in"), (e, 0.7, "in")]),
        o=opacity([(0, 0, "out"), (a, 0, "out"), (a + 12, 100, "out"),
                   (c, 100, "in"), (e, 0, "in")])))])


def build():
    marks = svg_paths(SVG_PATH)
    assert len(marks) == 2, "unexpected path count in source svg: %d" % len(marks)
    back_to_front = []
    add = back_to_front.append

    # 1. the window
    a, b = PLATE_IN
    c, e = PLATE_OUT
    plate_c = ctr(*PLATE_R[:4])
    add(layer("plate", [grp([rc(*PLATE_R[:4], r=PLATE_R[4]), fill(SHEET)], "plate", tr(
        anchor=plate_c,
        s=scale([(0, 0.95, "out"), (b, 1.0, "out"), (c, 1.0, "in"), (e, 0.95, "in")]),
        o=opacity([(0, 0, "out"), (b - 8, 100, "out"), (c, 100, "in"), (e, 0, "in")])))]))

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

    # 2. the content fills in, top to bottom
    content = []
    rows = [BARS[0], BARS[1], None, BARS[2], BARS[3]]      # None marks the big block
    for i, row in enumerate(rows):
        t_in = CONTENT_T0 + i * CONTENT_STEP
        t_out = CONTENT_OUT0 + (len(rows) - 1 - i) * CONTENT_STEP_OUT
        if row is None:
            gc = ctr(*BLOCK_R[:4])
            content.append(grp([rc(*BLOCK_R[:4], r=BLOCK_R[4]), fill(PANEL)], "block", tr(
                anchor=gc,
                s=scale([(0, 0.9, "out"), (t_in, 0.9, "out"), (t_in + 14, 1.0, "out"),
                         (t_out, 1.0, "in"), (t_out + 12, 0.9, "in")]),
                o=opacity([(0, 0, "out"), (t_in, 0, "out"), (t_in + 12, 100, "out"),
                           (t_out, 100, "in"), (t_out + 12, 0, "in")]))))
        else:
            x, y, w = row
            content.append(wipe((x, y, w, BAR_H, BAR_R), PANEL,
                                (t_in, t_in + 12), (t_out, t_out + 12), name="bar%d" % i))
    add(layer("content", content))

    # 3. the two app tiles
    add(tile("tile-left", TILE_L, TILE_L_ROT, TILE_L_C, marks[0], CLAUDE,
             TILE_L_IN, TILE_L_OUT, -150, 120, -55,
             pulses=(HANDOFF[0][0], HANDOFF[1][1] - 12)))
    add(tile("tile-right", TILE_R, TILE_R_ROT, TILE_R_C, marks[1], GEM,
             TILE_R_IN, TILE_R_OUT, 150, -120, 55,
             pulses=(HANDOFF[0][1] - 12, HANDOFF[1][0])))

    # 4. the hand-off: orange travels right, the dark mark answers on the way back
    pulses = []
    for i, (a, b) in enumerate(HANDOFF):
        route = ROUTE if i == 0 else list(reversed(ROUTE))
        color = CLAUDE if i == 0 else GEM
        span = b - a
        keys = [(0, (0, 0), "linear"), (a, (0, 0), "out")]
        for j, (x, y) in enumerate(route):
            t = a + int(round(span * j / float(len(route) - 1)))
            keys.append((t, (x - route[0][0], y - route[0][1]),
                         "soft" if 0 < j < len(route) - 1 else "out"))
        keys.append((DUR, (route[-1][0] - route[0][0], route[-1][1] - route[0][1]),
                     "linear"))
        pulses.append(grp([el(route[0][0], route[0][1], 5.2), fill(color)], "pulse%d" % i, tr(
            anchor=route[0], p=pos(route[0], keys),
            o=opacity([(0, 0, "linear"), (a + 2, 0, "out"), (a + 9, 100, "linear"),
                       (b - 9, 100, "in"), (b - 2, 0, "linear"), (DUR, 0, "linear")]))))
    add(layer("handoff", pulses))

    return comp(back_to_front, "Frame 76 - App Handoff")


def main():
    lk.setup(W, H, FPS, DUR)
    lk.write(build(), STEM)


if __name__ == "__main__":
    main()
