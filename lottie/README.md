# Lottie animations

Looping Lottie animations built from the Frame 76 illustration set. Each one is a seamless
5s loop at 60fps with a **transparent background**, so it takes the colour of whatever page
or section it sits in.

| | |
| --- | --- |
| ![canvas](frame76-canvas.gif) | ![window](frame76-window.gif) |
| **frame76-canvas** — a design file assembling itself, two cursors working on it, then a reset | **frame76-window** — an app window opening, loading its content, then packing away |

## Files

Every animation ships as three files plus its source illustration:

| file | what it is |
| --- | --- |
| `<name>.json` | the animation — drop this into Webflow, lottie-web, Figma, iOS or Android |
| `<name>.html` | self-contained player (play/pause, scrub, speed, light/dark) — just open it |
| `<name>.gif` | 30fps transparent flipbook, for READMEs and chats |
| `assets/<name>.svg` | the source illustration |

| animation | size | layers | json |
| --- | --- | --- | --- |
| frame76-canvas | 385x366 | 16 | ~62 KB |
| frame76-window | 386x366 | 9 | ~26 KB |

## Beat sheets

**frame76-canvas** — 0–42 wireframe blocks stagger in from under the canvas edge, purple CTA
last · 30–70 selection frame draws itself, corner ticks pop, measure line extends · 50–96
**You** and **Me** arrive · 84 You clicks the CTA, ripples fire · 86–116 avatar badge pops,
connector slides out from the left edge · 108–226 live: marching ants, presence pulses,
cursor drift · 214–292 everything leaves in reverse.

**frame76-window** — 0–24 the window opens · 14–32 traffic lights pop one by one · 18–44
chrome: avatar and toolbar pills · 30–52 the media block · 46–76 the bird flies in, settles
and its eye opens · 56–90 purple tile, side pane, bottom strip · 96–216 loading: two shimmer
sweeps rake the media block, the bottom strip fills like a progress bar, the bird blinks
twice, the green light blips · 214–292 packs away in reverse.

## Regenerating

```bash
python3 build.py            # rebuilds every animation
python3 build_window.py     # or just one
```

No dependencies — stdlib only.

| file | role |
| --- | --- |
| `lottiekit.py` | shared toolkit: shapes, easing, keyframes, SVG path parser, preview page |
| `build_canvas.py`, `build_window.py` | one scene per illustration — geometry and timeline |
| `build.py` | builds all of them |

Each scene parses its source SVG's path data directly, so the vector shapes stay identical
to the illustration; only geometry that needed semantic grouping (panels, cursors, the bird)
is named explicitly. Timeline constants sit near the top of each scene file.

Both scenes have `SHOW_CARD = False`, which drops the paper-coloured card the illustration
was drawn on. Set it to `True` for the original opaque card. One thing to watch on
frame76-canvas: its measurement frame, ticks and connector are drawn in black, so they need
a light background.

## Using them

```bash
npm i lottie-web
```

```js
import lottie from 'lottie-web';
import animationData from './frame76-window.json';

lottie.loadAnimation({ container: el, renderer: 'svg', loop: true, autoplay: true, animationData });
```

React (`lottie-react`): `<Lottie animationData={data} loop />`.
Webflow: Add panel → Media → Lottie animation, upload the JSON, set Trigger to Autoplay and
Loop to infinite. Keep the SVG renderer — trim paths, dashes, gradients and masks all depend
on it.
Figma / After Effects: import the JSON through the LottieFiles plugin.

Built from plain shape layers — no expressions, images or fonts — so they render the same in
lottie-web, lottie-ios, lottie-android and rlottie. The `<name>.html` previews pull the
player from jsDelivr, so they need a connection the first time.
