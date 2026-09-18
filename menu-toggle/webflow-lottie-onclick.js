/* Menu toggle icon: hold the Lottie on frame 0 (burger) and play it only on click. Forward to the X on open, reverse on close, reversing from wherever it got to. */
(function () {
  function bind() {
    var wrap = document.querySelector('.toggle_wrap');
    if (!wrap) { return false; }
    if (wrap.getAttribute('data-burger-bound')) { return true; }
    var player = null;
    try { player = window.Webflow && window.Webflow.require('lottie').lottie; } catch (e) { return false; }
    if (!player || !player.getRegisteredAnimations) { return false; }
    var list = player.getRegisteredAnimations();
    var anim = null;
    for (var i = 0; i < list.length; i++) {
      if (list[i].wrapper && wrap.contains(list[i].wrapper)) { anim = list[i]; break; }
    }
    if (!anim) { return false; }
    wrap.setAttribute('data-burger-bound', '1');
    anim.loop = false;
    anim.autoplay = false;
    anim.goToAndStop(0, true);
    var open = false;
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    wrap.addEventListener('click', function () {
      open = !open;
      if (still) { anim.goToAndStop(open ? anim.totalFrames - 1 : 0, true); return; }
      anim.setDirection(open ? 1 : -1);
      anim.play();
    });
    return true;
  }
  var tries = 0;
  var timer = setInterval(function () { if (bind() || ++tries > 60) { clearInterval(timer); } }, 100);
  if (window.Webflow && window.Webflow.push) { window.Webflow.push(bind); }
})();
