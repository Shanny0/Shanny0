# Burger menu toggle

![the toggle](toggle-frames.png)

The burger icon comes apart into an X and back: the filling shoots out, then the two buns
swing across each other. Closing runs it in reverse, with the filling dropping back in last.

| file | what it is |
| --- | --- |
| `menu-toggle.html` | the component — paste the whole file into a Webflow Embed |
| `menu-toggle.json` | the same transition as a Lottie, frame 0 = burger, frame 30 = X |
| `build_menu.py` | generator for the Lottie |
| `assets/menu-toggle.svg` | the source icon |

## Use the HTML one

Paste `menu-toggle.html` into an Embed. That is the whole install — it carries its own CSS,
markup and a few lines of JS.

- The button toggles `.is-open` on itself and keeps `aria-expanded` and its label in sync.
- Add `data-burger-target="#nav"` to put `.is-open` on your menu as well, or listen for the
  `burger:toggle` event (`e.detail.open`).
- Inside Webflow's built-in Navbar, drop it into the menu button: the CSS also reacts to the
  `w--open` class Webflow puts on that button, so the icon follows the navbar even when
  Webflow is the one opening the menu.
- Restyle through `--size`, `--color` and `--speed` on `.burger`.
- `prefers-reduced-motion` is honoured: the state still changes, it just doesn't animate.

It is CSS transitions rather than a player, so an interrupted toggle reverses from wherever
it got to instead of jumping — which is what you want on a button people can spam.

## Or the Lottie one

`menu-toggle.json` is the same motion for anywhere that already renders Lottie: play
0 → 30 to open and 30 → 0 to close. It does not loop, and it can't reverse mid-flight as
gracefully as the CSS version, so prefer the embed for a menu button.

```bash
python3 build_menu.py        # rebuilds menu-toggle.json
```

The generator reuses the toolkit in `../lottie/lottiekit.py` and computes each piece's
bounding-box centre by sampling its curves, which is what `transform-box: fill-box` does in
the CSS version — so both turn around exactly the same points.

## The geometry

Everything rotates about its own centre, then moves to where the strokes cross (22.5, 21.5):

| piece | open state |
| --- | --- |
| bun | `translate(-.7, 9.7) rotate(45deg) scale(.92, .36)` — the dome flattens into a stroke |
| base | `translate(.3, -17) rotate(-45deg) scaleX(.92)` |
| filling | `scale(.15)`, faded out |
