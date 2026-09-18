#!/usr/bin/env python3
"""Scene: the phone notification (assets/frame76-phone.svg).

A phone assembles, a push notification drops in over it with a tilt and a shadow, its
avatar and text land, it nudges for attention, then it is flicked away.
Tweak the timeline constants below and re-run `python3 build.py`.
"""

import os

import lottiekit as lk
from lottiekit import (anim, comp, el, fill, grp, layer, opacity, pos, rc, rounded_mask,
                       scale, stack, stroke, tr, wipe)
from lottiekit import SHEET, PANEL, PURPLE

STEM = "frame76-phone"

W, H = 399, 382
FPS = 60
DUR = 300
SHOW_CARD = False
lk.setup(W, H, FPS, DUR)

PAPER = "#E9E8DE"
CREAM = "#FBF9ED"                      # notification foreground
# The phone group is 81% opaque in the source, which only reads right over the paper card.
# With the card gone that just makes the phone translucent, so the blend is baked in here
# and the group is drawn at full opacity.
BODY = "#FBF9ED"                       # #FFFDF0 over the paper at 81%
EDGE = "#DAD9CC"                       # #D7D5C8 over the paper at 81%
SCREEN_FILL = "#F1EFE3"                # #F3F1E4 over the paper at 81%
INK = "#000000"

# --- geometry lifted from the source svg -------------------------------------
CARD_R = (0, 0, 398.304, 381.381, 33.1058)
PHONE_R = (45.0278, 31.8696, 308.25, 651.194, 65.2487)   # runs off the bottom of the card
NOTCH_R = (163.035, 55.0352, 75.3723, 22.6117, 11.3058)
SCREEN = [(71.0625, 102.693, 259.335, 159.498, 12.4147),
          (71.0625, 271.757, 259.335, 81.0086, 12.4147),
          (71.0625, 362.333, 259.335, 81.0086, 12.4147)]
PHONE_OPACITY = 100                    # see BODY/EDGE/SCREEN_FILL above
TILT = 4.13382                         # the notification's rest angle
NOTIF_R = (32.3984, 102.981, 342.438, 111.574, 24.8294)
NOTIF_AVATAR = (82.9858, 162.57, 31.9924)
NOTIF_LINES = [(133.395, 138.531, 159.133, 24.111, 8.27645),
               (130.836, 173.93, 111.956, 24.111, 8.27645)]

# --- timeline ----------------------------------------------------------------
PHONE_IN, PHONE_OUT = (0, 26), (266, 292)
NOTCH_IN, NOTCH_OUT = (14, 32), (258, 276)
SCREEN_IN = [(20, 40), (26, 46), (32, 52)]
SCREEN_OUT = [(246, 266), (240, 260), (234, 254)]
DROP = (60, 88)                        # the notification falling in
AVATAR_IN = (82, 100)
LINE_IN = [(88, 106), (94, 112)]
NUDGE = 140                            # attention wiggle
FLICK = (200, 228)                     # swiped away


def ctr(x, y, w, h):
    return (x + w / 2.0, y + h / 2.0)


def build():
    back_to_front = []
    add = back_to_front.append

    if SHOW_CARD:
        add(layer("card", [grp([rc(*CARD_R[:4], r=CARD_R[4]), fill(PAPER)], "card")]))

    # 1. the phone. It runs off the bottom of the frame, so the whole group is masked to
    #    the card shape and every part animates on its own group transform.
    parts = []
    pa, pb = PHONE_IN
    pc, pd = PHONE_OUT
    phone_c = ctr(*PHONE_R[:4])
    body_tr = lambda: tr(
        anchor=phone_c,
        p=pos(phone_c, [(0, (0, 22), "out"), (pb, (0, 0), "out"),
                        (pc, (0, 0), "in"), (pd, (0, 22), "in")]),
        s=scale([(0, 0.96, "out"), (pb, 1.0, "out"), (pc, 1.0, "in"), (pd, 0.96, "in")]),
        o=opacity([(0, 0, "out"), (pb - 8, 100, "out"), (pc, 100, "in"), (pd, 0, "in")]))
    # fill and outline are two separate rects in the source, and stay separate here: a
    # group carrying both a fill and a stroke does not paint reliably.
    parts.append(grp([rc(*PHONE_R[:4], r=PHONE_R[4]), stroke(EDGE, 5.17278)], "edge", body_tr()))
    parts.append(grp([rc(*PHONE_R[:4], r=PHONE_R[4]), fill(BODY)], "body", body_tr()))

    na, nb = NOTCH_IN
    nc, nd = NOTCH_OUT
    notch_c = ctr(*NOTCH_R[:4])
    parts.append(grp([rc(*NOTCH_R[:4], r=NOTCH_R[4]), fill(EDGE)], "notch", tr(
        anchor=notch_c,
        s=scale([(0, 0.4, "out"), (na, 0.4, "out"), (nb, 1.0, "out"),
                 (nc, 1.0, "in"), (nd, 0.4, "in")]),
        o=opacity([(0, 0, "out"), (na, 0, "out"), (nb, 100, "out"),
                   (nc, 100, "in"), (nd, 0, "in")]))))

    for i, geo in enumerate(SCREEN):
        a, b = SCREEN_IN[i]
        c, e = SCREEN_OUT[i]
        gc = ctr(*geo[:4])
        parts.append(grp([rc(*geo[:4], r=geo[4]), fill(SCREEN_FILL)], "screen%d" % i, tr(
            anchor=gc,
            p=pos(gc, [(0, (0, 14), "out"), (a, (0, 14), "out"), (b, (0, 0), "out"),
                       (c, (0, 0), "in"), (e, (0, 14), "in")]),
            o=opacity([(0, 0, "out"), (a, 0, "out"), (b, 100, "out"),
                       (c, 100, "in"), (e, 0, "in")]))))
    add(layer("phone", parts, o=PHONE_OPACITY,
              mask=rounded_mask(*CARD_R[:4], r=CARD_R[4], name="card-clip")))

    # 2. the notification. Everything sits inside one group so the drop, the nudge and the
    #    flick move the card, its shadow and its contents as one object.
    da, db = DROP
    fa, fb = FLICK
    notif_c = ctr(*NOTIF_R[:4])

    # a soft shadow, faked as three offset plates - it renders anywhere, unlike a blur
    shadow = [grp([rc(NOTIF_R[0] - k, NOTIF_R[1] - k + 5, NOTIF_R[2] + k * 2,
                      NOTIF_R[3] + k * 2, NOTIF_R[4] + k), fill(INK, 5)],
                  "shadow%d" % k, tr(anchor=NOTIF_R[:2], r=TILT))
              for k in (11, 6, 2)]

    aa, ab = AVATAR_IN
    contents = shadow + [
        grp([rc(*NOTIF_R[:4], r=NOTIF_R[4]), fill(PURPLE)], "plate",
            tr(anchor=NOTIF_R[:2], r=TILT)),
        grp([el(*NOTIF_AVATAR), fill(CREAM)], "avatar", tr(
            anchor=NOTIF_AVATAR[:2],
            s=scale([(0, 0.2, "out"), (aa, 0.2, "out"), (ab - 5, 1.12, "out"),
                     (ab, 1.0, "out"), (fa, 1.0, "in"), (fa + 12, 0.2, "in")]),
            o=opacity([(0, 0, "out"), (aa, 0, "out"), (aa + 8, 100, "out"),
                       (fa, 100, "in"), (fa + 12, 0, "in")]))),
        wipe(NOTIF_LINES[0], CREAM, LINE_IN[0], (fa, fa + 14), TILT),
        wipe(NOTIF_LINES[1], CREAM, LINE_IN[1], (fa + 4, fa + 18), TILT),
    ]

    add(layer("notification", [grp(stack(contents), "notification", tr(
        anchor=notif_c,
        p=pos(notif_c, [(0, (0, -190), "out"), (da, (0, -190), "out"), (db - 6, (0, 8), "out"),
                        (db, (0, 0), "out"), (NUDGE, (0, 0), "soft"),
                        (NUDGE + 8, (6, -3), "soft"), (NUDGE + 20, (0, 0), "soft"),
                        (fa, (0, 0), "in"), (fb, (40, -210), "in")]),
        r=anim([(0, 5.5, "out"), (da, 5.5, "out"), (db, 0, "out"), (NUDGE, 0, "soft"),
                (NUDGE + 8, -2.2, "soft"), (NUDGE + 20, 0, "soft"),
                (fa, 0, "in"), (fb, 4.0, "in")]),
        s=scale([(0, 0.94, "out"), (da, 0.94, "out"), (db, 1.0, "out"),
                 (fa, 1.0, "in"), (fb, 0.9, "in")]),
        o=opacity([(0, 0, "out"), (da, 0, "out"), (da + 10, 100, "out"),
                   (fa + 8, 100, "in"), (fb, 0, "in")])))]))

    return comp(back_to_front, "Frame 76 - Push Notification")


def main():
    lk.setup(W, H, FPS, DUR)
    lk.write(build(), STEM)


if __name__ == "__main__":
    main()
