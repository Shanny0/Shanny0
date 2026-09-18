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
markup and a few lines of JS, and it adapts to where you put it.

**Inside Webflow's Navbar** (Navbar > Menu Button) it makes itself passive: Webflow keeps
handling the click and the icon only mirrors the navbar's open state, watching both the
`w--open` class on the menu button and the `data-nav-menu-open` attribute on the menu. Two
things fighting over one button is what makes these icons stick half-open, so the icon never
toggles itself there. It also hides Webflow's own menu icon and centres the open menu, using
the measured navbar height so the menu centres in the screen that is left rather than in a
full-height box hanging off the bottom. Delete the second `<style>` block to skip that part.

**Anywhere else** the button drives itself: it toggles `.is-open`, keeps `aria-expanded` and
its label in sync, and fires a `burger:toggle` event (`e.detail.open`). Add
`data-burger-target="#nav"` to put `.is-open` on your menu too.
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
