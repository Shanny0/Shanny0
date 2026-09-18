#!/usr/bin/env python3
"""Scene: the app window (assets/frame76-window.svg).

A window opens, chrome and content load in, the media block shimmers while it loads,
the bird settles and blinks, a progress bar fills - then it all packs away again.
Tweak the timeline constants below and re-run `python3 build.py`.
"""

import os
import re

import lottiekit as lk
from lottiekit import (anim, comp, el, fill, grp, layer, linear_gradient, opacity, pos,
                       rc, rounded_mask, scale, sh, tr, val)
from lottiekit import SHEET, PANEL, PURPLE, WHITE

SVG_PATH = os.path.join(lk.HERE, "assets", "frame76-window.svg")
STEM = "frame76-window"

W, H = 386, 366
FPS = 60
DUR = 300                      # 5s loop; frame 300 == frame 0 so the loop is seamless
SHOW_CARD = False              # the paper-coloured card behind everything; off = transparent
                               # background, so the animation takes the page/section colour
lk.setup(W, H, FPS, DUR)

PAPER = "#E9E8DE"
BIRD = "#E6E4DB"
LIGHT_RED, LIGHT_GREY, LIGHT_GREEN = "#FF0808", "#D9D9D9", "#21E63B"

# --- geometry lifted from the source svg -------------------------------------
CARD_R = (0, 0, W, 365.5, 32)
WIN_R = (26.0273, 35.3047, 333.945, 373.171, 12.7217)   # taller than the card, so it is
                                                        # clipped to the card's bottom edge
MEDIA_R = (38.7773, 98.8613, 304.2257, 126.1067, 12.7217)
TILE_R = (38.7773, 234.282, 151.609, 126.107, 12.7217)  # the purple block
PANE_R = (198.27, 234.282, 144.736, 80.4153, 12.7217)
BAR_R = (198.27, 322.736, 143.149, 37.6522, 12.7217)
PILL_L = (152.684, 70.2217, 143.149, 16.0228, 8.01138)
PILL_R = (343.004 - 40.8466, 70.2217, 40.8466, 16.0228, 8.01138)
AVATAR = (50.0921, 78.2337, 11.3148)
LIGHTS = [(42.2138, 50.2621, LIGHT_RED), (53.0692, 50.2621, LIGHT_GREY),
          (63.9208, 50.2621, LIGHT_GREEN)]
LIGHT_R = 3.43641
EYE = (315.682, 150.328, 4.83018)
BIRD_PIVOT = (295.719, 176.596)        # where the wedge converges - the body's centre

# --- timeline ----------------------------------------------------------------
WIN_IN, WIN_OUT = (0, 24), (268, 292)
LIGHT_T0, LIGHT_T1 = 14, 258           # first light in / first light out, 3f apart
AVATAR_IN, AVATAR_OUT = (18, 36), (254, 272)
PILLL_IN, PILLL_OUT = (22, 40), (250, 268)
PILLR_IN, PILLR_OUT = (26, 44), (246, 264)
MEDIA_IN, MEDIA_OUT = (30, 52), (240, 262)
BIRD_IN, BIRD_OUT = (46, 76), (228, 254)
TILE_IN, TILE_OUT = (56, 80), (222, 242)
PANE_IN, PANE_OUT = (62, 84), (218, 236)
BAR_IN, BAR_OUT = (68, 90), (214, 232)
SWEEPS = ((96, 136), (176, 216))       # loading shimmer across the media block
BLINKS = (145, 196)
FILL_T = (104, 170)                    # the progress bar filling


def ctr(x, y, w, h):
    return (x + w / 2.0, y + h / 2.0)


def load_paths():
    d = re.findall(r'<path\s+d="([^"]+)"', open(SVG_PATH).read())
    assert len(d) == 3, "unexpected path count in source svg: %d" % len(d)
    return {"bird": d[1]}                      # d[0]/d[2] are the media block + its clip


def block(name, items, center, tin, tout, dx, dy, s0=0.94, pop=0.0, mask=None,
          extra_scale=()):
    """A panel that slides/pops in, holds, then leaves the way it came."""
    a, b = tin
    c, e = tout
    s_keys = [(0, s0, "out"), (a, s0, "out")]
    if pop:
        s_keys += [(b - 6, 1.0 + pop, "out"), (b, 1.0, "out")]
    else:
        s_keys += [(b, 1.0, "out")]
    s_keys += list(extra_scale) + [(c, 1.0, "in"), (e, s0, "in")]
    return layer(name, [grp(items, name, tr(
        anchor=center,
        p=pos(center, [(0, (dx, dy), "out"), (a, (dx, dy), "out"), (b, (0, 0), "out"),
                       (c, (0, 0), "in"), (e, (dx, dy), "in")]),
        s=scale(s_keys),
        o=opacity([(0, 0, "out"), (a, 0, "out"), (b, 100, "out"),
                   (c, 100, "in"), (e, 0, "in")])))],
        anchor=center, mask=mask)


def build():
    P = load_paths()
    media_mask = rounded_mask(*MEDIA_R[:4], r=MEDIA_R[4], name="media-clip")
    media_c = ctr(*MEDIA_R[:4])
    back_to_front = []
    add = back_to_front.append

    if SHOW_CARD:
        add(layer("card", [grp([rc(*CARD_R[:4], r=CARD_R[4]), fill(PAPER)], "card")]))

    # 1. the window opens. It is taller than the frame, so it is masked to the card
    #    shape and its animation rides the group transform (masks ignore layer transforms).
    win_c = (W / 2.0, 200.0)
    a, b = WIN_IN
    c, e = WIN_OUT
    add(layer("window", [grp([rc(*WIN_R[:4], r=WIN_R[4]), fill(SHEET)], "window", tr(
        anchor=win_c,
        p=pos(win_c, [(0, (0, 18), "out"), (b, (0, 0), "out"),
                      (c, (0, 0), "in"), (e, (0, 18), "in")]),
        s=scale([(0, 0.94, "out"), (b, 1.0, "out"), (c, 1.0, "in"), (e, 0.94, "in")]),
        o=opacity([(0, 0, "out"), (b - 8, 100, "out"), (c, 100, "in"), (e, 0, "in")])))],
        anchor=win_c, mask=rounded_mask(*CARD_R[:4], r=CARD_R[4], name="card-clip")))

    # 2. traffic lights pop on one by one; the green one blips while the app is busy
    lights = []
    for i, (cx, cy, color) in enumerate(LIGHTS):
        t_in, t_out = LIGHT_T0 + i * 3, LIGHT_T1 + i * 2
        keys = [(0, 0.1, "out"), (t_in, 0.1, "out"), (t_in + 7, 1.3, "out"),
                (t_in + 12, 1.0, "out")]
        if color == LIGHT_GREEN:                      # activity blip
            for t in (105, 165, 225):
                keys += [(t, 1.0, "out"), (t + 7, 1.35, "out"), (t + 15, 1.0, "out")]
        keys += [(t_out, 1.0, "in"), (t_out + 10, 0.1, "in")]
        lights.append(grp([el(cx, cy, LIGHT_R), fill(color)], "light%d" % i,
                          tr(anchor=(cx, cy), s=scale(keys),
                             o=opacity([(0, 0, "out"), (t_in, 0, "out"), (t_in + 5, 100, "out"),
                                        (t_out, 100, "in"), (t_out + 10, 0, "in")]))))
    add(layer("traffic-lights", lights))

    # 3. the media block
    add(block("media", [rc(*MEDIA_R[:4], r=MEDIA_R[4]), fill(PANEL)],
              media_c, MEDIA_IN, MEDIA_OUT, 0, 10, s0=0.96))

    # 4. the bird flies in and settles, then blinks. Bird and eye share one outer group so
    #    the eye rides along; inside a group the FIRST item paints on top, hence eye first.
    ba, bb = BIRD_IN
    bc, bd = BIRD_OUT
    blink_s, blink_o = [(0, 1.0, "linear")], [(0, 0, "linear")]
    for t in BLINKS:
        blink_s += [(t, 1.0, "inout"), (t + 3, 0.08, "inout"), (t + 6, 1.0, "linear")]
    eye_scale = anim([(t, [100, v * 100], e) for t, v, e in blink_s])
    add(layer("bird", [grp([
        grp([el(*EYE), fill(PANEL)], "eye", tr(
            anchor=EYE[:2], s=eye_scale,
            o=opacity([(0, 0, "out"), (bb - 8, 0, "out"), (bb, 100, "out"),
                       (bc, 100, "in"), (bc + 10, 0, "in")]))),
        grp(sh(P["bird"]) + [fill(BIRD)], "body"),
    ], "bird", tr(
        anchor=BIRD_PIVOT,
        p=pos(BIRD_PIVOT, [(0, (74, -12), "out"), (ba, (74, -12), "out"), (bb, (0, 0), "out"),
                           (130, (0, 3), "soft"), (190, (0, -2), "soft"),
                           (bc, (0, 0), "in"), (bd, (74, -12), "in")]),
        r=anim([(0, -22, "out"), (ba, -22, "out"), (bb, 0, "out"), (130, -2.5, "soft"),
                (190, 2.0, "soft"), (bc, 0, "in"), (bd, 18, "in")]),
        s=scale([(0, 0.9, "out"), (ba, 0.9, "out"), (bb, 1.0, "out"),
                 (bc, 1.0, "in"), (bd, 0.9, "in")]),
        o=opacity([(0, 0, "out"), (ba, 0, "out"), (ba + 16, 100, "out"),
                   (bc, 100, "in"), (bd, 0, "in")])))],
        mask=media_mask))

    # 5. loading shimmer - a soft band raked across the media block, twice
    band_w, band_h = 74.0, 230.0
    sweep_p, sweep_o = [(0, (-235, 0), "linear")], [(0, 0, "linear")]
    for i, (s0, s1) in enumerate(SWEEPS):
        sweep_p += [(s0, (-235, 0), "inout"), (s1, (235, 0), "linear")]
        if i + 1 < len(SWEEPS):
            sweep_p += [(s1 + 1, (-235, 0), "linear")]     # reset while invisible
        sweep_o += [(s0, 0, "out"), (s0 + 8, 100, "linear"), (s1 - 6, 100, "in"),
                    (s1, 0, "linear")]
    sweep_p.append((DUR, (235, 0), "linear"))
    sweep_o.append((DUR, 0, "linear"))
    add(layer("shimmer", [grp([
        rc(media_c[0] - band_w / 2, media_c[1] - band_h / 2, band_w, band_h),
        linear_gradient([(0, WHITE), (0.5, WHITE), (1, WHITE)],
                        (media_c[0] - band_w / 2, media_c[1]),
                        (media_c[0] + band_w / 2, media_c[1]),
                        alpha=[(0, 0), (0.5, 0.42), (1, 0)]),
    ], "band", tr(anchor=media_c, p=pos(media_c, sweep_p), r=16))],
        o=opacity(sweep_o), mask=media_mask))

    # 6. the purple tile, with a slow breath while the window is live
    add(block("tile", [rc(*TILE_R[:4], r=TILE_R[4]), fill(PURPLE)],
              ctr(*TILE_R[:4]), TILE_IN, TILE_OUT, 0, 18, s0=0.9, pop=0.05,
              extra_scale=[(120, 1.0, "soft"), (170, 1.015, "soft"), (220, 1.0, "in")]))

    add(block("pane", [rc(*PANE_R[:4], r=PANE_R[4]), fill(PANEL)],
              ctr(*PANE_R[:4]), PANE_IN, PANE_OUT, 22, 0))

    # 7. the bottom strip doubles as a progress bar: an inset fill grows left to right
    fa, fb = FILL_T
    inset = 6.0
    fill_x = BAR_R[0] + inset
    fill_c = ctr(fill_x, BAR_R[1] + inset, BAR_R[2] - inset * 2, BAR_R[3] - inset * 2)
    add(block("bar", [
        grp([rc(fill_x, BAR_R[1] + inset, BAR_R[2] - inset * 2, BAR_R[3] - inset * 2, 12),
             fill(PURPLE)], "progress", tr(
            anchor=(fill_x, fill_c[1]),
            s=anim([(0, [0, 100], "out"), (fa, [0, 100], "out"), (fb, [100, 100], "out")]))),
        rc(*BAR_R[:4], r=BAR_R[4]), fill(PANEL),
    ], ctr(*BAR_R[:4]), BAR_IN, BAR_OUT, 22, 0))

    # 8. window chrome
    chrome = []
    for name, geo, t_in, t_out, dx in (("pill-l", PILL_L, PILLL_IN, PILLL_OUT, -28),
                                       ("pill-r", PILL_R, PILLR_IN, PILLR_OUT, 28)):
        a, b = t_in
        c, e = t_out
        gc = ctr(*geo[:4])
        chrome.append(grp([rc(*geo[:4], r=geo[4]), fill(PANEL)], name, tr(
            anchor=gc,
            p=pos(gc, [(0, (dx, 0), "out"), (a, (dx, 0), "out"), (b, (0, 0), "out"),
                       (c, (0, 0), "in"), (e, (dx, 0), "in")]),
            o=opacity([(0, 0, "out"), (a, 0, "out"), (b, 100, "out"),
                       (c, 100, "in"), (e, 0, "in")]))))
    aa, ab = AVATAR_IN
    ac, ad = AVATAR_OUT
    chrome.append(grp([el(*AVATAR), fill(PANEL)], "avatar", tr(
        anchor=AVATAR[:2],
        s=scale([(0, 0.3, "out"), (aa, 0.3, "out"), (ab - 5, 1.08, "out"), (ab, 1.0, "out"),
                 (ac, 1.0, "in"), (ad, 0.3, "in")]),
        o=opacity([(0, 0, "out"), (aa, 0, "out"), (aa + 10, 100, "out"),
                   (ac, 100, "in"), (ad, 0, "in")]))))
    add(layer("chrome", chrome))

    return comp(back_to_front, "Frame 76 - App Window")


def main():
    lk.setup(W, H, FPS, DUR)
    lk.write(build(), STEM)


if __name__ == "__main__":
    main()
