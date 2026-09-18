#!/usr/bin/env python3
"""Build the burger -> X menu toggle as a Lottie (assets/menu-toggle.svg).

Frame 0 is the burger, frame 30 is the X: play it forward to open, backwards to close.
It deliberately does not loop. The css version in menu-toggle.html does the same thing
without a player and is easier to drive from a click, so this is the alternative for
anywhere that already renders Lottie.

    python3 build_menu.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lottie"))

import lottiekit as lk                                            # noqa: E402
from lottiekit import anim, comp, fill, grp, layer, opacity, parse_path, pos, sh, tr  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(HERE, "assets", "menu-toggle.svg")
OUT = os.path.join(HERE, "menu-toggle.json")

W, H = 45, 43
FPS = 60
END = 30                               # 0.5s, one direction
DUR = END + 1                          # a lottie stops one frame before its out point,
                                       # so the comp runs one past the last keyframe
COLOR = "#FBF9EF"
ICON_C = (22.5, 21.5)                  # where the two strokes cross

# the css does the same thing with transform-box: fill-box
SQUASH = (92.0, 36.0)                  # the bun flattens into a stroke as it turns
NARROW = (92.0, 100.0)                 # the base shortens to match it
SWING = 45.0
OVERSHOOT = 3.0

lk.TIME_SCALE = 1.0                    # this one is a UI transition, not part of the set
lk.setup(W, H, FPS, DUR)


def bbox(d, steps=24):
    """Tight bounding box of a path, sampled along its curves (css fill-box equivalent)."""
    xs, ys = [], []
    for sub in parse_path(d):
        v, i_, o = sub["v"], sub["i"], sub["o"]
        n = len(v)
        last = n if sub["c"] else n - 1
        for k in range(last):
            p0, p3 = v[k], v[(k + 1) % n]
            p1 = (p0[0] + o[k][0], p0[1] + o[k][1])
            p2 = (p3[0] + i_[(k + 1) % n][0], p3[1] + i_[(k + 1) % n][1])
            for s in range(steps + 1):
                t = s / float(steps)
                u = 1 - t
                xs.append(u**3 * p0[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * p3[0])
                ys.append(u**3 * p0[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * p3[1])
    return min(xs), min(ys), max(xs), max(ys)


def centre(d):
    x0, y0, x1, y1 = bbox(d)
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)


def build():
    paths = lk.svg_paths(SVG_PATH)
    assert len(paths) == 3, "expected bun, base and patty: got %d" % len(paths)
    bun, base, patty = paths
    bun_c, base_c, patty_c = centre(bun), centre(base), centre(patty)
    delay = 4                                      # the filling leaves first

    def swing(d, c, angle, end_scale):
        return layer("stroke", [grp(sh(d) + [fill(COLOR)], "stroke", tr(
            anchor=c,
            p=pos(c, [(0, (0, 0), "soft"), (delay, (0, 0), "soft"),
                      (END, (ICON_C[0] - c[0], ICON_C[1] - c[1]), "soft")]),
            r=anim([(0, 0, "soft"), (delay, 0, "soft"),
                    (END - 6, angle + (OVERSHOOT if angle > 0 else -OVERSHOOT), "soft"),
                    (END, angle, "soft")]),
            s=anim([(0, [100, 100], "soft"), (delay, [100, 100], "soft"),
                    (END, list(end_scale), "soft")])))])

    return comp([
        layer("patty", [grp(sh(patty) + [fill(COLOR)], "patty", tr(
            anchor=patty_c,
            s=anim([(0, [100, 100], "inout"), (11, [15, 15], "inout")]),
            o=opacity([(0, 100, "inout"), (9, 0, "inout")])))]),
        swing(base, base_c, -SWING, NARROW),
        swing(bun, bun_c, SWING, SQUASH),
    ], "Menu toggle - burger to X")


if __name__ == "__main__":
    import json
    doc = build()
    with open(OUT, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    print("wrote menu-toggle.json (0-%d, %.2fs one way, %.1f KB)"
          % (END, END / float(doc["fr"]), os.path.getsize(OUT) / 1024.0))
