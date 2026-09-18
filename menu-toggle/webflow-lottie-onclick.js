/* Menu toggle icon: hold the Lottie on frame 0 (burger) and play it only on click.
   Forward to the X on open, reverse on close, reversing from wherever it got to.
   Nothing here is allowed to throw into Webflow's init - the menu must work even
   if this fails outright. */
(function () {
  var TOGGLE = '.toggle_wrap';
  var tries = 0;
  var timer = setInterval(step, 120);
  step();

  function step() {
    var done = false;
    try { done = bind(); } catch (e) { done = false; }
    if (done || ++tries > 80) { clearInterval(timer); }
  }

  function bind() {
    var wrap = document.querySelector(TOGGLE);
    if (!wrap || wrap.getAttribute('data-burger-bound')) { return !!wrap; }

    var mod = window.Webflow && window.Webflow.require && window.Webflow.require('lottie');
    var player = mod && mod.lottie;
    if (!player || typeof player.getRegisteredAnimations !== 'function') { return false; }

    var list = player.getRegisteredAnimations() || [];
    var anim = null;
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].wrapper && wrap.contains(list[i].wrapper)) { anim = list[i]; break; }
    }
    if (!anim || !anim.isLoaded) { return false; }   /* wait until it can be scrubbed */

    wrap.setAttribute('data-burger-bound', '1');
    anim.loop = false;
    anim.autoplay = false;
    anim.goToAndStop(0, true);

    var open = false;
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    wrap.addEventListener('click', function () {
      try {
        open = !open;
        if (still) { anim.goToAndStop(open ? anim.totalFrames - 1 : 0, true); return; }
        anim.setDirection(open ? 1 : -1);
        anim.play();
      } catch (e) {}
    });
    return true;
  }
})();
