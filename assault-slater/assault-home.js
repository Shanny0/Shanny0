/* ASSAULT - Home page (English "/" and Spanish "/es"), loaded once in the site head for both languages.
   Countdown, FAQ, gallery, line-up schedule + mobile card stack, marquee, "The format" dial,
   scroll animations (GSAP 3.15). Loads GSAP itself, and only on the Home pages.
   Phones (LITE) get a light version: no intro, no looping/scroll-linked effects, no film grain.

   LINE-UP SCHEDULE: search for LINEUP_SCHEDULE below to change the reveal dates. */
(function () {
  var HOME = /^\/(es\/?)?$/.test(location.pathname);
  // Phone light mode is off: phones get the full animations too (restore the matchMedia check to turn it back on)
  var LITE = false;
  // Phones keep every animation, but the effects that make scrolling stutter there are lightened:
  // still grain without blending, no animated blur filters, no gallery parallax, no marquee speed-up.
  var PHONE = window.matchMedia("(max-width: 767px)").matches;
  function onReady(fn) { if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn); else fn(); }
  function loadGsap() {
    if (window.assaultGsap) return window.assaultGsap;
    var cdn = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/";
    var load = function (name) {
      return window[name.replace(".min", "")] ? Promise.resolve() : new Promise(function (ok, fail) {
        var s = document.createElement("script");
        s.src = cdn + name + ".js"; s.onload = ok; s.onerror = fail;
        document.head.appendChild(s);
      });
    };
    // Phones skip the text-splitting and scramble plugins (their effects are off there)
    var plugins = LITE ? ["ScrollTrigger.min"] : ["ScrollTrigger.min", "SplitText.min", "ScrambleTextPlugin.min"];
    return (window.assaultGsap = load("gsap.min").then(function () {
      return Promise.all(plugins.map(load));
    }).then(function () {
      if (!window.ScrollTrigger) return;
      gsap.registerPlugin(ScrollTrigger);
      // the phone address bar showing/hiding must not recalculate every animation mid-scroll
      ScrollTrigger.config({ ignoreMobileResize: true });
    }));
  }
  // Start downloading GSAP straight away on the Home pages (the 3D script in the site footer waits for it too)
  if (HOME) loadGsap();

  var ES = /^\/es(\/|$)/.test(location.pathname);
  var T = ES ? {"tba":"Artista por anunciar","soon":"Pr\u00f3ximamente","tbaShort":"Por anunciar","unlocks":"Se desbloquea en ","show":"Ver artista ","swipe":"\u2190 Desliza \u2192"} : {"tba":"Artist to be announced","soon":"Coming soon","tbaShort":"To be announced","unlocks":"Unlocks in ","show":"Show artist ","swipe":"\u2190 Swipe \u2192"};

  onReady(function () {
    if (!window.matchMedia('(hover: hover) and (min-width: 992px)').matches) return;
    var faq = document.querySelector('.section_faq'), foot = document.querySelector('.footer_component');
    if (!faq || !foot) return;
    var spot = document.createElement('div');
    spot.className = 'footer_spot is-faq';
    faq.appendChild(spot);
    // Both sections get the same pointer position, so the light crosses the border without a cut
    var move = function (e) {
      [faq, foot].forEach(function (el) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        el.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    };
    faq.addEventListener('pointermove', move);
    foot.addEventListener('pointermove', move);
    faq.addEventListener('pointerenter', function () { faq.classList.add('is-lit'); });
  });

  /* ASSAULT: "The format" dial - six hours (01:00 -> 07:00) drawn on a clock face, split into four sets */
  onReady(function () {
    var box = document.querySelector('.numbers_dial-svg');
    if (!box) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var NS = 'http://www.w3.org/2000/svg', C = 300, R = 236;
    var pt = function (h, r) { var a = (h / 12 * 360 - 90) * Math.PI / 180; return [C + r * Math.cos(a), C + r * Math.sin(a)]; };
    var el = function (tag, attrs, parent) { var n = document.createElementNS(NS, tag); for (var k in attrs) n.setAttribute(k, attrs[k]); (parent || svg).appendChild(n); return n; };
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 600 600'); svg.setAttribute('aria-hidden', 'true');
    var defs = el('defs', {}), g = el('linearGradient', { id: 'dialGrad', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
    el('stop', { offset: 0, 'stop-color': '#b596ff' }, g); el('stop', { offset: 1, 'stop-color': '#6400fa' }, g);
    el('circle', { "class": 'dial-track', cx: C, cy: C, r: R });
    for (var m = 0; m < 60; m++) {
      var h = m / 5, major = m % 5 === 0, a = pt(h, R + 22), b = pt(h, R + (major ? 34 : 28));
      el('line', { "class": 'dial-tick' + (major ? ' is-major' : ''), x1: a[0], y1: a[1], x2: b[0], y2: b[1] });
    }
    for (var hr = 1; hr <= 12; hr++) {
      var p = pt(hr, R + 58), t = el('text', { "class": 'dial-hour' + (hr <= 7 ? ' is-on' : ''), x: p[0], y: p[1], 'text-anchor': 'middle', 'dominant-baseline': 'middle' });
      t.textContent = (hr < 10 ? '0' : '') + hr;
    }
    var s = pt(1, R), e = pt(7, R);
    var arc = el('path', { "class": 'dial-arc', d: 'M ' + s[0] + ' ' + s[1] + ' A ' + R + ' ' + R + ' 0 0 1 ' + e[0] + ' ' + e[1] });
    [2.5, 4, 5.5].forEach(function (q) { var a2 = pt(q, R - 12), b2 = pt(q, R + 12); el('line', { "class": 'dial-cut', x1: a2[0], y1: a2[1], x2: b2[0], y2: b2[1] }); });
    var head = el('circle', { "class": 'dial-head', r: 7, cx: s[0], cy: s[1] });
    box.appendChild(svg);

    var len = arc.getTotalLength();
    arc.style.strokeDasharray = len;
    var at = function (d) { var q = arc.getPointAtLength(d); head.setAttribute('cx', q.x); head.setAttribute('cy', q.y); };
    if (reduce) { arc.style.strokeDashoffset = 0; at(len); return; }
    arc.style.strokeDashoffset = len; head.style.opacity = 0;
    var start = function () {
      var t0 = performance.now(), draw = 1600, loop = 7000;
      head.style.opacity = 1;
      (function f(now) {
        var k = now - t0;
        if (k < draw) { var u = 1 - Math.pow(1 - k / draw, 3); arc.style.strokeDashoffset = len * (1 - u); at(len * u); }
        else { arc.style.strokeDashoffset = 0; at(len * (((k - draw) % loop) / loop)); }
        requestAnimationFrame(f);
      })(t0);
    };
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); start(); } }, { threshold: 0.35 });
      io.observe(box);
    } else start();
  });
  /* Gallery: each card is a link to its Instagram post; a drag/swipe on the slider must not open it */
  onReady(function () {
    document.querySelectorAll('.gallery_link').forEach(function (a) {
      var sx = 0, sy = 0;
      a.addEventListener('pointerdown', function (e) { sx = e.clientX; sy = e.clientY; });
      a.addEventListener('click', function (e) { if (e.detail && (Math.abs(e.clientX - sx) > 6 || Math.abs(e.clientY - sy) > 6)) e.preventDefault(); });
      a.addEventListener('dragstart', function (e) { e.preventDefault(); });
    });
  });

  function main() {
  var d = document, root = d.documentElement;
  var ready = function () { root.classList.remove("is-loading"); };
  setTimeout(ready, 3000);
  var pad = function (n) { return String(n).padStart(2, "0"); };
  var hasGsap = !!window.gsap;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var animate = hasGsap && !reduce;
  var desktop = window.matchMedia("(hover: hover) and (min-width: 992px)").matches;
  if (hasGsap) {
    if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
    if (window.SplitText) gsap.registerPlugin(SplitText);
    if (window.ScrambleTextPlugin) gsap.registerPlugin(ScrambleTextPlugin);
  }
  var canScramble = animate && !!window.ScrambleTextPlugin;

  /* =========================================================
     LINE-UP SCHEDULE
     The first card is always shown. The others stay LOCKED
     (blurred, name hidden, "Coming soon") until their date.
     Names must match the card heading exactly.
     ========================================================= */
  var LINEUP_SCHEDULE = {
    "KaraH": "2026-10-06T19:30:00+02:00",
    "David": "2099-01-01T12:00:00+01:00",
    "Rav": "2099-01-01T12:00:00+01:00"
  };
  var LOCK_SVG = '<svg width="16" height="18" viewBox="0 0 16 18" fill="none" aria-hidden="true"><rect x="1" y="8" width="14" height="9" stroke="currentColor" stroke-width="1.4"/><path d="M4 8V5a4 4 0 0 1 8 0v3" stroke="currentColor" stroke-width="1.4"/></svg>';
  var maskName = function (name) { return name.replace(/\S/g, "\u25ae"); };
  var fmtLeft = function (ms) {
    var m = Math.floor(ms / 60000), dd = Math.floor(m / 1440), hh = Math.floor(m % 1440 / 60), mm = m % 60;
    return (dd ? dd + "d " : "") + pad(hh) + "h " + pad(mm) + "m";
  };
  var unlock = function (card) {
    var h = card.querySelector("h3"), lk = card.querySelector(".lineup_lock");
    card.classList.remove("is-locked"); card.classList.add("is-revealed");
    if (h && card._realName) { h.textContent = card._realName; h.removeAttribute("aria-label"); }
    var img = card.querySelector(".lineup_portrait");
    if (img && card._realAlt) img.alt = card._realAlt;
    if (lk) lk.remove();
    if (animate) {
      gsap.fromTo(card.querySelector(".lineup_portrait"), { filter: "blur(14px) grayscale(1) brightness(0.45)", scale: 1.15 }, { filter: "blur(0px) grayscale(0) brightness(1)", scale: 1, duration: 1.4, ease: "expo.out", clearProps: "filter,scale" });
      if (h && canScramble) gsap.fromTo(h, { scrambleText: { text: maskName(card._realName || ""), chars: "\u25ae" } }, { scrambleText: { text: card._realName, chars: "ASSAULT0123456789", speed: 0.6 }, duration: 1.2 });
    }
  };
  var lockedCards = [];
  d.querySelectorAll(".lineup_item").forEach(function (card, i) {
    if (i === 0) { card.classList.add("is-revealed"); return; }
    var h = card.querySelector("h3"), name = h ? h.textContent.trim() : "";
    var t = Date.parse(LINEUP_SCHEDULE[name] || card.getAttribute("data-reveal-date") || "");
    if (!isNaN(t) && Date.now() >= t) { card.classList.add("is-revealed"); return; }
    card._realName = name; card._unlockAt = t;
    card.classList.add("is-locked");
    if (h) { h.textContent = maskName(name); h.setAttribute("aria-label", T.tba); }
    var img = card.querySelector(".lineup_portrait");
    if (img) { card._realAlt = img.alt; img.alt = T.tba; }
    var wrap = card.querySelector(".lineup_portrait-wrap");
    if (wrap) {
      var lk = d.createElement("div");
      lk.className = "lineup_lock";
      lk.innerHTML = '<div class="lineup_lock-icon">' + LOCK_SVG + '</div><div class="lineup_lock-title">' + T.soon + '</div><div class="lineup_lock-meta">' + T.tbaShort + '</div>';
      wrap.appendChild(lk);
      card._meta = lk.querySelector(".lineup_lock-meta");
    }
    lockedCards.push(card);
  });
  var tickLocks = function () {
    lockedCards = lockedCards.filter(function (card) {
      var t = card._unlockAt;
      if (isNaN(t) || t - Date.now() > 365 * 864e5) return true; // far away / no date: keep "To be announced"
      var left = t - Date.now();
      if (left <= 0) { unlock(card); return false; }
      if (card._meta) card._meta.textContent = T.unlocks + fmtLeft(left);
      return true;
    });
  };
  tickLocks(); setInterval(tickLocks, 30000);

  /* ---------- Countdown ---------- */
  var cd = d.querySelector("[data-countdown]"), cdUnits = {};
  var cdTick = function () {};
  if (cd) {
    var end = new Date(cd.getAttribute("data-countdown")).getTime();
    cd.querySelectorAll("[data-countdown-unit]").forEach(function (e) { cdUnits[e.getAttribute("data-countdown-unit")] = e; });
    cdTick = function (force) {
      if (cd._scrambling && !force) return;
      var s = Math.max(0, end - Date.now()) / 1000;
      if (cdUnits.days) cdUnits.days.textContent = Math.floor(s / 86400);
      if (cdUnits.hours) cdUnits.hours.textContent = pad(Math.floor(s % 86400 / 3600));
      if (cdUnits.minutes) cdUnits.minutes.textContent = pad(Math.floor(s % 3600 / 60));
      if (cdUnits.seconds) cdUnits.seconds.textContent = pad(Math.floor(s % 60));
    };
    cdTick(); setInterval(cdTick, 1000);
  }

  /* ---------- FAQ accordion ---------- */
  var items = d.querySelectorAll("[data-faq-item]");
  var setOpen = function (it, open) {
    var icon = it.querySelector("[data-faq-icon]"), ans = it.querySelector("[data-faq-answer]");
    if (it.classList.contains("is-open") === open) return;
    it.classList.toggle("is-open", open);
    if (icon) icon.classList.toggle("is-open", open);
    if (!ans) return;
    if (animate) {
      if (open) {
        ans.classList.add("is-open");
        gsap.fromTo(ans, { height: 0 }, { height: "auto", duration: 0.6, ease: "expo.out" });
        gsap.fromTo(ans.children, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, delay: 0.1, ease: "power3.out" });
      } else gsap.to(ans, { height: 0, duration: 0.4, ease: "power3.inOut", onComplete: function () { ans.classList.remove("is-open"); } });
    } else ans.classList.toggle("is-open", open);
  };
  items.forEach(function (it) {
    var t = it.querySelector("[data-faq-trigger]");
    if (!t) return;
    t.setAttribute("role", "button"); t.setAttribute("tabindex", "0");
    var go = function () {
      var o = it.classList.contains("is-open");
      items.forEach(function (x) { setOpen(x, false); });
      if (!o) setOpen(it, true);
    };
    t.addEventListener("click", go);
    t.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
  });

  /* ---------- Gallery slider ---------- */
  var s = d.querySelector("[data-gallery-slider]");
  var galleryParallax = function () {};
  if (s) {
    var cards = [].slice.call(s.children);
    var ctr = d.querySelector("[data-gallery-counter]"), fill = d.querySelector("[data-gallery-fill]");
    var vis = function () { return cards.filter(function (c) { return c.style.display !== "none"; }); };
    var step = function () { var v = vis(); return v[0] ? v[0].offsetWidth + parseFloat(getComputedStyle(s).columnGap || 24) : 300; };
    var upd = function () {
      var v = vis(), i = Math.min(v.length - 1, Math.round(s.scrollLeft / step()));
      if (ctr) ctr.textContent = pad(i + 1) + " / " + pad(v.length);
      if (fill) fill.style.width = ((i + 1) / v.length * 100) + "%";
      galleryParallax();
    };
    var nav = function (dir) { return function (e) { e.preventDefault(); s.scrollBy({ left: dir * step(), behavior: "smooth" }); }; };
    var p = d.querySelector("[data-gallery-prev]"), n = d.querySelector("[data-gallery-next]");
    if (p) p.addEventListener("click", nav(-1));
    if (n) n.addEventListener("click", nav(1));
    s.addEventListener("scroll", upd, { passive: true });
    d.querySelectorAll("[data-gallery-filter]").forEach(function (f, _, all) {
      f.addEventListener("click", function (e) {
        e.preventDefault();
        var k = f.getAttribute("data-gallery-filter");
        all.forEach(function (a) { a.classList.toggle("is-active", a === f); });
        var shown = [];
        cards.forEach(function (c) {
          var on = k === "all" || c.getAttribute("data-gallery-category") === k;
          c.style.display = on ? "" : "none";
          if (on) shown.push(c);
        });
        s.scrollLeft = 0; upd();
        if (animate) gsap.fromTo(shown, { autoAlpha: 0, x: 60, rotation: 2 }, { autoAlpha: 1, x: 0, rotation: 0, stagger: 0.07, duration: 0.8, ease: "expo.out" });
      });
    });
    // Drag to scroll on desktop
    if (desktop) {
      var down = false, sx = 0, sl = 0;
      s.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") return; down = true; sx = e.clientX; sl = s.scrollLeft; s.style.scrollSnapType = "none"; s.style.cursor = "grabbing"; });
      window.addEventListener("pointerup", function () { if (!down) return; down = false; s.style.scrollSnapType = ""; s.style.cursor = ""; });
      window.addEventListener("pointermove", function (e) { if (down) s.scrollLeft = sl - (e.clientX - sx); });
      s.style.cursor = "grab";
    }
    upd();
  }

  /* ---------- Gallery videos ----------
     Each card has a "Gallery Video" component: its Video URL prop (an .mp4 link) replaces
     the card's photo with a muted loop. Empty URL = the photo stays. The photo is also the
     poster and the fallback if the clip fails. Clips only play while on screen. */
  if (s) {
    var vids = [];
    [].slice.call(s.querySelectorAll("[data-gallery-video]")).forEach(function (slot) {
      var src = (slot.textContent || "").trim(), wrap = slot.parentNode, img = wrap && wrap.querySelector(".gallery_image");
      if (!/^https?:\/{2}/.test(src) || !img) return;
      var vid = d.createElement("video");
      vid.className = "gallery_image gallery_video";
      vid.muted = true; vid.loop = true; vid.playsInline = true;
      vid.setAttribute("muted", ""); vid.setAttribute("playsinline", "");
      vid.preload = "metadata";
      vid.poster = img.currentSrc || img.src;
      vid.src = src;
      vid.setAttribute("aria-label", img.alt || "");
      vid.addEventListener("error", function () { vid.remove(); img.style.display = ""; });
      img.style.display = "none";
      img.parentNode.insertBefore(vid, img);
      vids.push(vid);
    });
    if (!reduce && "IntersectionObserver" in window) {
      var vio = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { var p = e.target.play(); if (p && p["catch"]) p["catch"](function () {}); }
          else e.target.pause();
        });
      }, { threshold: 0.25 });
      vids.forEach(function (v) { vio.observe(v); });
    }
  }

  /* ---------- Marquee ---------- */
  var marquee;
  var track = d.querySelector(".numbers_marquee-track");
  if (track && hasGsap) {
    track.style.paddingRight = getComputedStyle(track).columnGap || "3rem";
    var clone = track.cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    track.parentNode.appendChild(clone);
    if (!reduce) marquee = gsap.to([track, clone], { xPercent: -100, duration: 22, ease: "none", repeat: -1 });
  }

  if (!animate || !window.ScrollTrigger) { ready(); return; }

  /* ================= GSAP animations ================= */
  var $ = function (sel) { return d.querySelector(sel); };
  var $$ = function (sel) { return gsap.utils.toArray(sel); };
  var reveal = function (targets, trigger, vars) {
    targets = $$(targets);
    if (!targets.length) return;
    gsap.from(targets, Object.assign({
      autoAlpha: 0, y: 40, duration: 1, ease: "power3.out", stagger: 0.1,
      scrollTrigger: { trigger: trigger || targets[0], start: "top 85%", once: true }
    }, vars || {}));
  };
  var scrub = function (el, fromVars, toVars, trigger, start, end) {
    if (LITE) return; // phones: no scroll-linked parallax
    if (typeof el === "string" ? !$(el) : !el) return;
    gsap.fromTo(el, fromVars, Object.assign({ ease: "none", scrollTrigger: { trigger: trigger || el, start: start || "top bottom", end: end || "bottom top", scrub: true } }, toVars));
  };
  // Masked word reveal (words rise out of a clipped line)
  var wordsUp = function (sel, trigger, vars) {
    $$(sel).forEach(function (el) {
      if (!window.SplitText) return reveal(el, trigger || el);
      var sp = SplitText.create(el, { type: "words", mask: "words" });
      gsap.from(sp.words, Object.assign({ yPercent: 110, duration: 1.1, ease: "expo.out", stagger: 0.06, scrollTrigger: { trigger: trigger || el, start: "top 85%", once: true } }, vars || {}));
    });
  };
  // Gradient headings: wipe up from a clip (keeps the gradient intact)
  var wipeUp = function (sel) {
    $$(sel).forEach(function (el) {
      gsap.fromTo(el, { clipPath: "inset(0% 0% 100% 0%)", y: 30 }, { clipPath: "inset(0% 0% 0% 0%)", y: 0, duration: 1.3, ease: "expo.out", scrollTrigger: { trigger: el, start: "top 85%", once: true } });
    });
  };

  /* ---------- Global: film grain + cursor + magnetic buttons ---------- */
  // Film grain: a full-screen blended layer redrawn 8x a second - desktop only
  if (!LITE) {
    var grain = d.createElement("div");
    grain.className = "page_grain";
    d.body.appendChild(grain);
    if (PHONE) grain.classList.add("is-still"); // phones: still grain, no blending
    else gsap.to(grain, { x: "random(-8, 8, 1)%", y: "random(-8, 8, 1)%", duration: 0.12, ease: "steps(1)", repeat: -1, repeatRefresh: true });
  }

  if (desktop) {
    var dot = d.createElement("div"), ring = d.createElement("div");
    dot.className = "cursor_dot"; ring.className = "cursor_ring";
    d.body.appendChild(dot); d.body.appendChild(ring);
    var dx = gsap.quickTo(dot, "x", { duration: 0.1 }), dy = gsap.quickTo(dot, "y", { duration: 0.1 });
    var rx = gsap.quickTo(ring, "x", { duration: 0.45, ease: "power3" }), ry = gsap.quickTo(ring, "y", { duration: 0.45, ease: "power3" });
    window.addEventListener("pointermove", function (e) { dx(e.clientX); dy(e.clientY); rx(e.clientX); ry(e.clientY); });
    d.querySelectorAll("a, [role=button], .lineup_portrait-wrap, .gallery_item").forEach(function (el) {
      el.addEventListener("mouseenter", function () { ring.classList.add("is-hover"); });
      el.addEventListener("mouseleave", function () { ring.classList.remove("is-hover"); });
    });
    d.querySelectorAll(".button, .gallery_arrow, .footer_host-button").forEach(function (b) {
      var bx = gsap.quickTo(b, "x", { duration: 0.4, ease: "power3" }), by = gsap.quickTo(b, "y", { duration: 0.4, ease: "power3" });
      b.addEventListener("mousemove", function (e) { var r = b.getBoundingClientRect(); bx((e.clientX - r.left - r.width / 2) * 0.3); by((e.clientY - r.top - r.height / 2) * 0.35); });
      b.addEventListener("mouseleave", function () { gsap.to(b, { x: 0, y: 0, duration: 0.8, ease: "elastic.out(1, 0.4)" }); });
    });
  }

  /* ---------- HERO: the gates open ---------- */
  if ($(".hero_symbol")) gsap.set(".hero_symbol", { xPercent: -50, x: 0 });
  if (LITE) {
    // Phones: the hero shows straight away (no intro, no pinned hero)
    ready();
  } else {
  var bg = $(".hero_background");
  var flash = d.createElement("div");
  flash.className = "hero_flash";
  if (bg) bg.appendChild(flash);
  var gap = function () { return window.innerWidth * 0.27; };
  var intro = gsap.timeline({ defaults: { ease: "power3.out" } });
  intro
    .set(".hero_wall.is-left", { x: gap })
    .set(".hero_wall.is-right", { x: function () { return -gap(); } })
    .from(".hero_wall", { autoAlpha: 0, duration: 0.6, ease: "none" })
    .fromTo(flash, { autoAlpha: 0, scaleX: 0.02 }, { autoAlpha: 1, scaleX: 1, duration: 0.5, ease: "expo.in" })
    .to(".hero_wall", { x: 0, duration: 1.8, ease: "expo.inOut" }, "<0.2")
    .to(flash, { autoAlpha: 0, duration: 1.4 }, "<0.6")
    .from(".hero_symbol", { autoAlpha: 0, scale: 0.6, rotation: -30, duration: 2, ease: "expo.out" }, "<0.2")
    .from(".hero_wordmark", { autoAlpha: 0, scale: 1.35, filter: "blur(18px)", duration: 1.1, ease: "expo.out", clearProps: "filter" }, "<0.3")
    .to(".hero_background", { keyframes: { x: [0, -10, 9, -6, 4, -2, 0], y: [0, 5, -4, 3, -2, 1, 0] }, duration: 0.45, ease: "none" }, "<0.15")
    .from(".hero_content > :not(.hero_heading)", { autoAlpha: 0, y: 30, stagger: 0.12, duration: 1 }, "-=0.6")
    .from(".nav_component", { autoAlpha: 0, y: -20, duration: 0.8 }, "<");
  ready();

  // Hero stays pinned while the countdown slides over it like a slab
  ScrollTrigger.create({ trigger: ".section_hero", start: "top top", end: "bottom top", pin: true, pinSpacing: false });
  // Starts only once the page actually scrolls (on tall screens the countdown is already in view at load,
  // which used to dim the logo before any scrolling)
  var heroST = function () { return { trigger: ".section_hero", start: "top top", end: "bottom top", scrub: true }; };
  gsap.to(".hero_wall.is-left", { xPercent: -35, ease: "none", scrollTrigger: heroST() });
  gsap.to(".hero_wall.is-right", { xPercent: 35, ease: "none", scrollTrigger: heroST() });
  gsap.to(".hero_content", { scale: 0.88, autoAlpha: 0.15, ease: "none", scrollTrigger: heroST() });
  gsap.to(".hero_symbol", { rotation: 30, scale: 1.2, ease: "none", scrollTrigger: heroST() });
  }

  /* ---------- Countdown: slot-machine numbers ---------- */
  wipeUp(".countdown_title-wrap .heading-style-h2");
  reveal(".countdown_title-wrap .text-style-eyebrow, .countdown_details > *", ".countdown_head", { stagger: 0.08, y: 24 });
  reveal(".countdown_unit", ".countdown_grid", { y: 100, stagger: 0.12, duration: 1.3, ease: "expo.out" });
  if (cd && canScramble) {
    ScrollTrigger.create({
      trigger: ".countdown_grid", start: "top 80%", once: true,
      onEnter: function () {
        cd._scrambling = true;
        Object.keys(cdUnits).forEach(function (k, i) {
          var el = cdUnits[k];
          gsap.to(el, { duration: 1.4 + i * 0.25, scrambleText: { text: el.textContent, chars: "0123456789", speed: 0.8 }, onComplete: i === 3 ? function () { cd._scrambling = false; cdTick(true); } : null });
        });
      }
    });
  }

  /* ---------- Manifesto ---------- */
  if ($(".manifesto_wire") && !LITE) gsap.fromTo(".manifesto_wire", { clipPath: "inset(0% 100% 0% 0%)" }, {
    clipPath: "inset(0% 0% 0% 0%)", ease: "none",
    scrollTrigger: { trigger: ".section_manifesto", start: "top 95%", end: "top 35%", scrub: 1 }
  });
  var fade = $(".manifesto_lead-fade");
  if (fade && window.SplitText) {
    var split = SplitText.create(fade, { type: "words" });
    gsap.set(fade, { color: "#eeeeee" });
    gsap.fromTo(split.words, PHONE ? { opacity: 0.1 } : { opacity: 0.1, filter: "blur(4px)" }, {
      opacity: 1, filter: PHONE ? "none" : "blur(0px)", stagger: 0.1, ease: "none",
      scrollTrigger: { trigger: ".manifesto_lead", start: "top 75%", end: "bottom 40%", scrub: true }
    });
  } else if (fade) fade.style.color = "#eeeeee"; // phones: final colour, no word-by-word fade
  reveal(".manifesto_head .eyebrow_component", ".manifesto_head", { y: 16 });
  $$(".manifesto_paragraph").forEach(function (el) { reveal(el, el, LITE || PHONE ? { y: 30 } : { y: 30, filter: "blur(6px)", clearProps: "filter" }); });
  // The chant flickers on like failing neon
  $$(".manifesto_chant").forEach(function (el) {
    gsap.fromTo(el, { autoAlpha: 0 }, { keyframes: { autoAlpha: [0, 1, 0.2, 1, 0.4, 0.1, 1] }, duration: 1.2, ease: "none", scrollTrigger: { trigger: el, start: "top 80%", once: true } });
  });
  scrub(".manifesto_book", { yPercent: 14, rotation: 22 }, { yPercent: -14, rotation: 4 }, ".section_manifesto");
  wordsUp(".manifesto_declaration-heading", ".manifesto_declaration", { stagger: 0.08 });
  reveal(".manifesto_details > *", ".manifesto_details", { y: 20, stagger: 0.08 });

  /* ---------- Line-up ---------- */
  var bgText = $(".lineup_bg-text");
  if (bgText) {
    gsap.set(bgText, { xPercent: -50, yPercent: -50, x: 0, y: 0 });
    if (window.SplitText) {
      var bgSplit = SplitText.create(bgText, { type: "chars" });
      gsap.from(bgSplit.chars, { autoAlpha: 0, yPercent: 60, filter: PHONE ? "none" : "blur(30px)", stagger: { each: 0.06, from: "random" }, duration: 1.4, ease: "expo.out", scrollTrigger: { trigger: ".lineup_title-stage", start: "top 80%", once: true } });
    }
    scrub(bgText, { scale: 1.15 }, { scale: 0.92 }, ".lineup_title-stage");
  }
  if ($(".lineup_ring")) {
    gsap.set(".lineup_ring", { xPercent: -50, yPercent: -50, x: 0, y: 0, rotation: -6.3 });
    gsap.from(".lineup_ring", { clipPath: "inset(0% 100% 0% 0%)", duration: 1.6, ease: "expo.inOut", scrollTrigger: { trigger: ".lineup_title-stage", start: "top 75%", once: true } });
    scrub(".lineup_ring", { rotation: -16 }, { rotation: 4 }, ".lineup_title-stage");
  }
  wordsUp(".lineup_title-wrap .heading-style-h1", ".lineup_title-stage", { delay: 0.3 });
  reveal(".lineup_date, .lineup_head-top > *, .lineup_note, .lineup_intro", ".lineup_head", { y: 20 });
  var lineupList = $(".lineup_list");
  if (lineupList && window.matchMedia("(max-width: 767px)").matches) {
    /* Mobile: swipeable 3D card stack (swipe left = next, right = previous) */
    var stack = $$(".lineup_item"), order = stack.slice(), busy = false;
    lineupList.classList.add("is-stack");
    var stackUi = d.createElement("div");
    stackUi.className = "lineup_stack-ui";
    stackUi.innerHTML = '<div class="lineup_stack-count"></div><div class="lineup_stack-dots">' +
      stack.map(function (c, i) { return '<button type="button" class="lineup_stack-dot" aria-label="' + T.show + (i + 1) + '"></button>'; }).join("") +
      '</div><div class="lineup_stack-hint">' + T.swipe + '</div>';
    lineupList.parentNode.insertBefore(stackUi, lineupList.nextSibling);
    var stackCount = stackUi.querySelector(".lineup_stack-count"), stackDots = stackUi.querySelectorAll(".lineup_stack-dot");
    var layout = function (instant, skip) {
      order.forEach(function (c, k) {
        if (c === skip) return;
        gsap.to(c, {
          x: 0, y: -k * 24, z: -k * 60, rotation: k ? (k % 2 ? -3.5 : 3.5) : 0, rotationY: 0, scale: 1 - k * 0.05,
          "--dim": Math.min(k * 0.3, 0.85), zIndex: stack.length - k,
          duration: instant ? 0 : 0.8, ease: "expo.out", overwrite: "auto"
        });
      });
      var i = stack.indexOf(order[0]);
      stackCount.textContent = pad(i + 1) + " / " + pad(stack.length);
      stackDots.forEach(function (dt, j) { dt.classList.toggle("is-active", j === i); });
    };
    var stackGo = function (dir) {
      if (busy) return;
      busy = true;
      if (dir < 0) { // front card flies out, then tucks in at the back
        var c = order.shift(); order.push(c);
        gsap.to(c, { x: -window.innerWidth * 1.1, rotation: -22, rotationY: -30, duration: 0.45, ease: "power2.in", overwrite: true,
          onComplete: function () { gsap.set(c, { zIndex: 0 }); layout(); busy = false; } });
        layout(false, c);
      } else { // last card comes back in from the right
        var b = order.pop(); order.unshift(b);
        gsap.set(b, { zIndex: stack.length + 1 });
        gsap.fromTo(b, { x: window.innerWidth * 1.1, rotation: 22, rotationY: 30 }, { x: 0, y: 0, z: 0, rotation: 0, rotationY: 0, scale: 1, "--dim": 0, duration: 0.7, ease: "expo.out", overwrite: true,
          onComplete: function () { busy = false; } });
        layout(false, b);
      }
    };
    stack.forEach(function (c) { gsap.set(c, { transformOrigin: "50% 0%", force3D: true }); });
    layout(true);
    // Deal in from below, back card first
    gsap.from(stack, {
      yPercent: 45, rotationX: -55, autoAlpha: 0, stagger: { each: 0.12, from: "end" }, duration: 1.3, ease: "expo.out",
      scrollTrigger: { trigger: lineupList, start: "top 80%", once: true },
      onComplete: function () { gsap.to(order[0], { x: -34, rotation: -3, duration: 0.45, ease: "power2.out", yoyo: true, repeat: 1 }); }
    });
    // Drag / swipe
    var lsx = 0, lsy = 0, ddx = 0, dragging = false, moved = false;
    lineupList.addEventListener("pointerdown", function (e) {
      if (busy || !order[0].contains(e.target)) return;
      dragging = true; moved = false; lsx = e.clientX; lsy = e.clientY; ddx = 0;
    });
    window.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      ddx = e.clientX - lsx;
      if (!moved && Math.abs(ddx) < 8) return;
      if (!moved && Math.abs(e.clientY - lsy) > Math.abs(ddx)) { dragging = false; return; } // vertical scroll wins
      moved = true;
      gsap.set(order[0], { x: ddx, rotation: ddx * 0.05, rotationY: ddx * 0.08 });
    }, { passive: true });
    var endDrag = function () {
      if (!dragging) return;
      dragging = false;
      if (Math.abs(ddx) > 70) stackGo(ddx < 0 ? -1 : 1); else layout();
    };
    window.addEventListener("pointerup", endDrag);
    window.addEventListener("pointercancel", endDrag);
    lineupList.addEventListener("dragstart", function (e) { e.preventDefault(); });
    lineupList.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    stackDots.forEach(function (dt, j) {
      dt.addEventListener("click", function () {
        if (busy) return;
        var steps = (stack.indexOf(order[0]) - j + stack.length) % stack.length; // how many cards to bring back
        if (!steps) return;
        var fwd = stack.length - steps;
        if (fwd <= steps) { while (fwd--) order.push(order.shift()); } else { while (steps--) order.unshift(order.pop()); }
        layout();
      });
    });
  } else {
    // Cards deal in like playing cards
    gsap.from(".lineup_item", {
      autoAlpha: 0, y: 120, rotation: function (i) { return (i - 1.5) * 6; }, transformOrigin: "50% 100%",
      stagger: 0.14, duration: 1.3, ease: "expo.out",
      scrollTrigger: { trigger: ".lineup_list", start: "top 85%", once: true }
    });
  }
  $$(".lineup_item").forEach(function (card) {
    var w = card.querySelector(".lineup_portrait-wrap"), img = card.querySelector(".lineup_portrait");
    if (!w || !img) return;
    if (card.classList.contains("is-locked")) {
      if (LITE) return; // phones: the locked card stays still (animated blur is heavy)
      // Locked: the blur breathes, the icon pulses, the name keeps encrypting
      if (!PHONE) gsap.to(img, { filter: "blur(20px) grayscale(1) brightness(0.35)", duration: 2.4, ease: "sine.inOut", yoyo: true, repeat: -1 });
      gsap.to(card.querySelector(".lineup_lock-icon"), { scale: 1.12, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: -1 });
      var h = card.querySelector("h3");
      if (h && canScramble) gsap.to(h, { scrambleText: { text: h.textContent, chars: "ASSAULT\u25ae\u25af01", speed: 0.4 }, duration: 1, repeat: -1, repeatDelay: 2.5 + Math.random() * 2 });
      return;
    }
    if (!desktop) return;
    var tx = gsap.quickTo(img, "x", { duration: 0.6, ease: "power3" }), ty = gsap.quickTo(img, "y", { duration: 0.6, ease: "power3" });
    w.addEventListener("mouseenter", function () { gsap.to(img, { scale: 1.08, duration: 0.6, ease: "power3.out" }); });
    w.addEventListener("mousemove", function (e) { var r = w.getBoundingClientRect(); tx((e.clientX - r.left - r.width / 2) * -0.06); ty((e.clientY - r.top - r.height / 2) * -0.06); });
    w.addEventListener("mouseleave", function () { gsap.to(img, { scale: 1, x: 0, y: 0, duration: 0.8, ease: "power3.out" }); });
  });

  /* ---------- Numbers ---------- */
  if (marquee && !LITE && !PHONE) {
    ScrollTrigger.create({
      trigger: ".section_numbers", start: "top bottom", end: "bottom top",
      onUpdate: function (self) {
        var boost = 1 + Math.min(Math.abs(self.getVelocity()) / 250, 5);
        gsap.timeline({ overwrite: true })
          .to(marquee, { timeScale: boost * (self.direction < 0 ? -1 : 1), duration: 0.25, ease: "power2.out" })
          .to(marquee, { timeScale: self.direction < 0 ? -1 : 1, duration: 1.4, ease: "power2.out" });
      }
    });
  }
  scrub(".numbers_frame-wrap", { yPercent: 10 }, { yPercent: -10 }, ".section_numbers");
  if ($(".numbers_frame")) {
    gsap.from(".numbers_frame", { autoAlpha: 0, scale: 0.85, rotation: -12, duration: 1.4, ease: "expo.out", scrollTrigger: { trigger: ".numbers_frame-wrap", start: "top 80%", once: true } });
    if (!LITE) gsap.fromTo(".numbers_frame", { y: 14, rotation: 2.5 }, { y: -14, rotation: 5.5, duration: 3.4, ease: "sine.inOut", yoyo: true, repeat: -1, delay: 1.4 });
  }
  if ($(".numbers_photo")) scrub(".numbers_photo", { scale: 1.25, yPercent: -6 }, { scale: 1.05, yPercent: 6 }, ".section_numbers");
  $$(".numbers_value").forEach(function (el) {
    var m = el.textContent.trim().match(/^(\d+)(.*)$/);
    if (!m) return;
    var endV = +m[1], suffix = m[2], o = { v: endV === 0 ? 10 : 0 };
    el.textContent = o.v + suffix;
    gsap.to(o, {
      v: endV, duration: endV === 0 ? 1.8 : 1.4, ease: "power2.out",
      onUpdate: function () { el.textContent = Math.round(o.v) + suffix; },
      scrollTrigger: { trigger: el, start: "top 85%", once: true }
    });
  });
  $$(".numbers_stat, .numbers_edition, .numbers_col.is-right > .text-style-eyebrow").forEach(function (el) { reveal(el, el, { y: 50 }); });

  /* ---------- Tickets ---------- */
  reveal(".tickets_head > .text-style-micro", ".tickets_head", { y: 16 });
  wordsUp(".tickets_head .heading-style-h2", ".tickets_head");
  if ($(".tickets_image")) {
    gsap.from(".tickets_image", {
      autoAlpha: 0, y: 140, rotationX: 55, rotationZ: -6, transformPerspective: 1200, transformOrigin: "50% 100%", duration: 1.6, ease: "expo.out",
      scrollTrigger: { trigger: ".tickets_visual", start: "top 85%", once: true }
    });
    var vis2 = $(".tickets_visual"), timg = $(".tickets_image");
    if (vis2 && !LITE) gsap.to(vis2, { y: -10, duration: 3, ease: "sine.inOut", yoyo: true, repeat: -1, delay: 1.6 });
    if (desktop && vis2 && timg) {
      // 3D tilt + moving glare (masked to the ticket shape) + counter-shifting shadow
      gsap.set(vis2, { transformPerspective: 1000, transformStyle: "preserve-3d" });
      var glare = d.createElement("div");
      glare.className = "tickets_glare";
      vis2.appendChild(glare);
      var setMask = function () { var u = "url('" + (timg.currentSrc || timg.src) + "')"; glare.style.webkitMaskImage = u; glare.style.maskImage = u; };
      if (timg.complete) setMask(); else timg.addEventListener("load", setMask);
      var tRX = gsap.quickTo(vis2, "rotationX", { duration: 0.5, ease: "power3" });
      var tRY = gsap.quickTo(vis2, "rotationY", { duration: 0.5, ease: "power3" });
      var baseShadow = "drop-shadow(0px 27px 60px rgba(42, 0, 104, 1)) drop-shadow(0px 0px 40px rgba(100, 0, 250, 0.35))";
      vis2.addEventListener("mouseenter", function () {
        gsap.to(vis2, { scale: 1.04, duration: 0.6, ease: "power3.out" });
        gsap.to(glare, { autoAlpha: 1, duration: 0.4 });
      });
      vis2.addEventListener("mousemove", function (e) {
        var r = vis2.getBoundingClientRect(), px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
        tRY((px - 0.5) * 22); tRX(-(py - 0.5) * 18);
        glare.style.setProperty("--gx", (px * 100) + "%");
        glare.style.setProperty("--gy", (py * 100) + "%");
        gsap.to(timg, { filter: "drop-shadow(" + Math.round(-(px - 0.5) * 50) + "px " + Math.round(27 - (py - 0.5) * 40) + "px 60px rgba(42, 0, 104, 1)) drop-shadow(0px 0px 50px rgba(100, 0, 250, 0.45))", duration: 0.4, overwrite: "auto" });
      });
      vis2.addEventListener("mouseleave", function () {
        tRX(0); tRY(0);
        gsap.to(vis2, { scale: 1, duration: 0.8, ease: "elastic.out(1, 0.5)" });
        gsap.to(glare, { autoAlpha: 0, duration: 0.4 });
        gsap.to(timg, { filter: baseShadow, duration: 0.6 });
      });
    }
  }
  // Mobile vertical ticket (only rendered below 768px)
  var tvWrap = $(".ticket-v_wrap"), tvCard = $(".ticket-v_card"), tvMain = $(".ticket-v_main");
  if (tvWrap && tvCard && tvWrap.offsetParent) {
    gsap.from(tvWrap, {
      autoAlpha: 0, y: 140, rotationX: 55, rotationZ: -6, transformPerspective: 1000, transformOrigin: "50% 100%", duration: 1.6, ease: "expo.out",
      scrollTrigger: { trigger: ".tickets_visual", start: "top 85%", once: true }
    });
    // The stub tears a little, then snaps back
    var tvStub = $(".ticket-v_stub");
    if (tvStub) gsap.fromTo(tvStub, { y: 0, rotation: 0 }, { y: 10, rotation: 2.5, transformOrigin: "0% 0%", duration: 0.35, ease: "power2.out", yoyo: true, repeat: 1, delay: 0.2, scrollTrigger: { trigger: tvStub, start: "top 75%", once: true } });
    // Holographic shine sweeping across the main part
    if (tvMain && !LITE) {
      var shine = d.createElement("div");
      shine.className = "ticket-v_shine";
      tvMain.appendChild(shine);
      gsap.fromTo(shine, { xPercent: -130 }, { xPercent: 130, duration: 1.5, ease: "power2.inOut", repeat: -1, repeatDelay: 2.8, delay: 1.6 });
    }
    // 3D: turns with the scroll, and tilts under the finger
    gsap.set(tvCard, { transformPerspective: 900 });
    scrub(tvCard, { rotationY: -16, rotationX: 10 }, { rotationY: 16, rotationX: -8 }, ".tickets_visual");
    var tvRX = gsap.quickTo(tvWrap, "rotationX", { duration: 0.5, ease: "power3" }), tvRY = gsap.quickTo(tvWrap, "rotationY", { duration: 0.5, ease: "power3" });
    gsap.set(tvWrap, { transformPerspective: 900 });
    tvWrap.addEventListener("pointermove", function (e) {
      var r = tvWrap.getBoundingClientRect();
      tvRY(((e.clientX - r.left) / r.width - 0.5) * 24); tvRX(-((e.clientY - r.top) / r.height - 0.5) * 18);
    });
    ["pointerup", "pointerleave", "pointercancel"].forEach(function (ev) { tvWrap.addEventListener(ev, function () { tvRX(0); tvRY(0); }); });
  }
  reveal(".tickets_perk", ".tickets_perks", { y: 16, stagger: 0.08 });

  /* ---------- Gallery ---------- */
  // Gradient heading: kept whole (splitting breaks the gradient) - wipe up + letter-spacing tightens
  if ($(".gallery_heading")) {
    gsap.fromTo(".gallery_heading", { clipPath: "inset(0% 0% 100% 0%)", letterSpacing: "0.12em", y: 60 }, {
      clipPath: "inset(0% 0% 0% 0%)", letterSpacing: "-0.04em", y: 0, duration: 1.6, ease: "expo.out",
      scrollTrigger: { trigger: ".gallery_band", start: "top 80%", once: true }
    });
  }
  scrub(".gallery_heading", { xPercent: 8 }, { xPercent: -12 }, ".section_gallery");
  reveal(".gallery_top-bar > *", ".gallery_top-bar", { y: 16 });
  gsap.from(".gallery_item", { autoAlpha: 0, x: 140, rotation: 3, stagger: 0.08, duration: 1.2, ease: "expo.out", scrollTrigger: { trigger: ".gallery_slider", start: "top 85%", once: true } });
  var gImgs = LITE || PHONE ? [] : $$(".gallery_image"); // phones: no parallax inside the cards
  if (gImgs.length) gsap.set(gImgs, { scale: 1.2 });
  if (!LITE && !PHONE) galleryParallax = function () {
    if (!s) return;
    var mid = s.getBoundingClientRect().left + s.clientWidth / 2;
    gImgs.forEach(function (img) {
      var r = img.parentNode.getBoundingClientRect();
      var off = (r.left + r.width / 2 - mid) / s.clientWidth;
      gsap.set(img, { xPercent: gsap.utils.clamp(-8, 8, off * -12) });
    });
  };
  galleryParallax();

  /* ---------- FAQ ---------- */
  reveal(".faq_head .eyebrow_component", ".faq_head", { y: 16 });
  wipeUp(".faq_heading");
  reveal(".faq_item", ".faq_list", { y: 30, stagger: 0.07, duration: 0.9 });

  /* ---------- Footer ---------- */
  wipeUp(".footer_call .heading-style-h2");
  reveal(".footer_call .footer_host-button, .footer_col, .footer_bottom > *", ".footer_top", { y: 30, stagger: 0.08 });
  scrub(".footer_wordmark", { yPercent: 45, scale: 0.92 }, { yPercent: 0, scale: 1 }, ".footer_component", "top bottom", "bottom bottom");
  // Violet light breathing behind the gate (all devices)
  var fVis = $(".footer_visual");
  if (fVis) {
    var glow = d.createElement("div"), gateLight = $(".footer_gate-light");
    glow.className = "footer_glow";
    fVis.insertBefore(glow, gateLight ? gateLight.nextSibling : fVis.firstChild);
    gsap.fromTo(glow, { autoAlpha: 0, scale: 0.7 }, {
      autoAlpha: 1, scale: 1, duration: 2.2, ease: "expo.out",
      scrollTrigger: { trigger: ".footer_component", start: "top 75%", once: true },
      onComplete: function () { if (!LITE) gsap.to(glow, { opacity: 0.6, scale: 1.08, duration: 3.2, ease: "sine.inOut", yoyo: true, repeat: -1 }); }
    });
  }
  var foot = $(".footer_component");
  if (foot && desktop) {
    var spot = d.createElement("div");
    spot.className = "footer_spot";
    foot.appendChild(spot);
    foot.addEventListener("pointermove", function (e) {
      var r = foot.getBoundingClientRect();
      foot.style.setProperty("--mx", (e.clientX - r.left) + "px");
      foot.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  }

  // Re-measure once every image has loaded (Slater runs this after DOMContentLoaded, so no window "load" listener)
  if (document.readyState === "complete") ScrollTrigger.refresh();
  else document.addEventListener("readystatechange", function () { if (document.readyState === "complete") ScrollTrigger.refresh(); });
  }

  /* Gallery videos: they only download and play when the gallery is on screen (Webflow would otherwise
     fetch all six at page load). The card keeps its poster until then.
     The videos are caught while the page is still being read, before the browser picks their file. */
  if (HOME && "MutationObserver" in window && "IntersectionObserver" in window) {
    var held = [];
    var holdSource = function (s) {
      if (s.getAttribute("src")) { s.setAttribute("data-held-src", s.getAttribute("src")); s.removeAttribute("src"); }
    };
    var holdVideo = function (v) {
      if (v._held || !v.closest || !v.closest(".gallery_image-wrap")) return;
      v._held = true; held.push(v);
      v.removeAttribute("autoplay"); v.autoplay = false; v.preload = "none";
      [].slice.call(v.querySelectorAll("source")).forEach(holdSource);
    };
    var watch = new MutationObserver(function (records) {
      records.forEach(function (r) {
        [].slice.call(r.addedNodes).forEach(function (n) {
          if (n.nodeName === "VIDEO") holdVideo(n);
          else if (n.nodeName === "SOURCE") { if (n.parentNode && n.parentNode._held) holdSource(n); }
          else if (n.querySelectorAll) [].slice.call(n.querySelectorAll("video")).forEach(holdVideo);
        });
      });
    });
    watch.observe(document.documentElement, { childList: true, subtree: true });
    onReady(function () {
      watch.disconnect();
      [].slice.call(document.querySelectorAll(".gallery_image-wrap video")).forEach(function (v) {
        if (!v._held) { holdVideo(v); v.load(); } // missed while loading: stop its download now
      });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var v = e.target;
          if (e.isIntersecting) {
            if (!v._loaded) {
              v._loaded = true;
              [].slice.call(v.querySelectorAll("source[data-held-src]")).forEach(function (s) { s.setAttribute("src", s.getAttribute("data-held-src")); });
              v.load();
            }
            var p = v.play(); if (p && p["catch"]) p["catch"](function () {});
          } else v.pause();
        });
      }, { rootMargin: "200px" });
      held.forEach(function (v) { io.observe(v); });
    });
  }

  onReady(function () {
    if (!HOME || !document.querySelector(".section_hero")) return;
    loadGsap().then(main, main);
  });
})();
