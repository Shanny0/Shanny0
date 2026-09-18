#!/usr/bin/env python3
"""
Toolkit for hand-building Lottie animations from the Frame 76 illustration set.

Shapes, easing, keyframes, an SVG path parser and the preview page live here; each
illustration gets its own scene file (build_canvas.py, build_window.py) that composes
these into layers. Run `python3 build.py` to rebuild every animation.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- composition
# Defaults; each scene calls setup() with its own size and length. Functions below read
# these at call time, so a scene's setup() applies to everything it builds afterwards.
W, H = 385, 366
FPS = 60
DUR = 300                      # 5s loop; frame DUR == frame 0 so the loop is seamless


def setup(w, h, fps, dur):
    global W, H, FPS, DUR
    W, H, FPS, DUR = w, h, fps, dur

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


def fill(color, op=100, rule=1):
    """rule 1 = nonzero (svg default), 2 = evenodd."""
    return {"ty": "fl", "c": val(rgb(color)),
            "o": op if isinstance(op, dict) else val(op),
            "r": rule, "bm": 0, "nm": "fill", "hd": False}


def svg_paths(svg_file):
    """Every <path> d attribute in a file, in document order (d need not come first)."""
    return re.findall(r'<path[^>]*?\sd="([^"]+)"', open(svg_file).read())


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


def linear_gradient(stops, start, end, alpha=None, name="gradient"):
    """Linear gradient fill. stops: [(pos, hex)]; alpha: [(pos, 0-1)] opacity stops."""
    k = []
    for pos, hx in stops:
        c = rgb(hx)
        k += [pos, c[0], c[1], c[2]]
    for pos, a in (alpha or []):
        k += [pos, a]
    return {"ty": "gf", "o": val(100), "r": 1, "bm": 0,
            "g": {"p": len(stops), "k": val(k)},
            "s": val(list(start)), "e": val(list(end)), "t": 1, "nm": name, "hd": False}


def wipe(geo, color, t_in, t_out, angle=0.0, name="line"):
    """A bar that wipes open from its left edge, then closes the same way.

    Nested on purpose: the inner group scales from the left edge, the outer one carries the
    bar's rotation about its own origin, exactly as the source svg does it.
    """
    a, b = t_in
    c, e = t_out
    left = (geo[0], geo[1] + geo[3] / 2.0)
    return grp([grp([rc(*geo[:4], r=geo[4]), fill(color)], "bar", tr(
        anchor=left,
        s=anim([(0, [0, 100], "out"), (a, [0, 100], "out"), (b, [100, 100], "out"),
                (c, [100, 100], "in"), (e, [0, 100], "in")])))],
        name, tr(anchor=geo[:2], r=angle))


def stack(items):
    """Write nested group contents back-to-front; lottie paints the first item on top."""
    return list(reversed(items))


def comp(layers, name):
    """Wrap back-to-front layers into a lottie document (index 0 is drawn on top)."""
    layers = list(reversed(layers))
    for i, lyr in enumerate(layers):
        lyr["ind"] = i + 1
    return {"v": "5.7.4", "fr": FPS, "ip": 0, "op": DUR, "w": W, "h": H,
            "nm": name, "ddd": 0, "assets": [], "layers": layers, "markers": []}


PREVIEW_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
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
  <div class="meta">__STEM__ &middot; __DUR__f &middot; __FPS__fps &middot; seamless loop</div>
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


def write_preview(doc, stem):
    html = (PREVIEW_TEMPLATE
            .replace("__DATA__", json.dumps(doc, separators=(",", ":")))
            .replace("__TITLE__", doc["nm"])
            .replace("__STEM__", stem)
            .replace("__DUR__", str(doc["op"]))
            .replace("__FPS__", str(doc["fr"])))
    with open(os.path.join(HERE, stem + ".html"), "w") as f:
        f.write(html)


def write(doc, stem):
    """Write <stem>.json next to this file, plus its standalone preview page."""
    path = os.path.join(HERE, stem + ".json")
    with open(path, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    write_preview(doc, stem)
    print("wrote %s.json (%d layers, %.1fs loop, %.0f KB)"
          % (stem, len(doc["layers"]), doc["op"] / float(doc["fr"]),
             os.path.getsize(path) / 1024.0))
