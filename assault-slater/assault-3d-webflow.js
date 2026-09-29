// Phones: no 3D (the still barbed-wire and ring images show instead).
// Desktop: Three.js is only downloaded when the manifesto comes within 600px of the screen.
var section3d = document.querySelector(".section_manifesto");
if (section3d && !window.matchMedia("(max-width: 767px)").matches) {
  await new Promise(function (go) {
    if (!("IntersectionObserver" in window)) return go();
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); go(); } }, { rootMargin: "600px 0px" });
    io.observe(section3d);
  });
  if (window.assaultGsap) { try { await window.assaultGsap; } catch (e) {} }
  var THREE, mergeGeometries;
  try {
    THREE = await import("https://cdn.jsdelivr.net/npm/three@0.186.0/+esm");
    mergeGeometries = (await import("https://cdn.jsdelivr.net/npm/three@0.186.0/examples/jsm/utils/BufferGeometryUtils.js/+esm")).mergeGeometries;
  } catch (e) {
    THREE = await import("three");
    mergeGeometries = (await import("three/addons/utils/BufferGeometryUtils.js")).mergeGeometries;
  }

/* ASSAULT — electrified barbed wire, 3D chains + chain ring round the line-up title (Three.js)
   Snaps taut when it enters the screen, current pulses along it on the beat (140 BPM),
   barbs spark when the current passes. Click = send a charge, cursor = push + light. */
(function () {
  var section = document.querySelector(".section_manifesto");
  if (!section) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var coarse = window.matchMedia("(hover: none)").matches;

  var holder = document.createElement("div");
  holder.className = "wire_canvas";
  holder.setAttribute("aria-hidden", "true");
  section.insertBefore(holder, section.firstChild);

  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  } catch (e) { holder.remove(); return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, coarse ? 1.5 : 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  holder.appendChild(renderer.domElement);
  document.documentElement.classList.add("has-webgl-wire");

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(28, 1, 0.1, 100);
  var wire = new THREE.Group();
  scene.add(wire);

  /* ---------- Studio reflections: white softboxes + violet strips ---------- */
  function studioEnv(r) {
    var env = new THREE.Scene();
    env.background = new THREE.Color(0x0c0322);
    var panel = function (w, h, hex, k, x, y, z) {
      var m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(hex).multiplyScalar(k), side: THREE.DoubleSide }));
      m.position.set(x, y, z); m.lookAt(0, 0, 0); env.add(m);
    };
    panel(16, 4, 0xffffff, 7, 0, 9, 3);
    panel(3, 10, 0xffffff, 3, -9, 1, 4);
    panel(2, 10, 0x8f5bff, 8, 9, 0, 2);
    panel(16, 2, 0x6400fa, 5, 0, -8, 3);
    panel(10, 5, 0xb48cff, 3.5, 0, 2, 10);
    return new THREE.PMREMGenerator(r).fromScene(env, 0.02).texture;
  }
  scene.environment = studioEnv(renderer);

  /* ---------- Worn, pitted silver (matches the ASSAULT logo) ---------- */
  function grungeTexture() {
    var S = 512, c = document.createElement("canvas"); c.width = c.height = S;
    var g = c.getContext("2d");
    g.fillStyle = "#7a7a7a"; g.fillRect(0, 0, S, S);
    for (var o = 0; o < 4; o++) { // soft blotches at several scales
      var n = [60, 180, 600, 1800][o], rMax = [70, 28, 10, 3][o];
      for (var i = 0; i < n; i++) {
        var v = 20 + Math.random() * 200;
        g.fillStyle = "rgba(" + v + "," + v + "," + v + "," + (0.06 + Math.random() * 0.16) + ")";
        g.beginPath(); g.arc(Math.random() * S, Math.random() * S, Math.random() * rMax + 0.5, 0, Math.PI * 2); g.fill();
      }
    }
    for (i = 0; i < 260; i++) { // scratches
      var x = Math.random() * S, y = Math.random() * S, a = Math.random() * Math.PI, l = 8 + Math.random() * 60, w2 = 150 + Math.random() * 100;
      g.strokeStyle = "rgba(" + w2 + "," + w2 + "," + w2 + "," + (0.1 + Math.random() * 0.3) + ")";
      g.lineWidth = Math.random() * 1.2;
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
    }
    for (i = 0; i < 900; i++) { // pits
      g.fillStyle = "rgba(20,20,20," + (0.25 + Math.random() * 0.5) + ")";
      g.beginPath(); g.arc(Math.random() * S, Math.random() * S, Math.random() * 1.8 + 0.3, 0, Math.PI * 2); g.fill();
    }
    var d = g.getImageData(0, 0, S, S), px = d.data; // fine grain
    for (i = 0; i < px.length; i += 4) { var gr = (Math.random() - 0.5) * 38; px[i] += gr; px[i + 1] += gr; px[i + 2] += gr; }
    g.putImageData(d, 0, 0);
    var t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.colorSpace = THREE.NoColorSpace;
    t.anisotropy = 8;
    return t;
  }
  var brushLine = grungeTexture(); brushLine.repeat.set(48, 1);
  var brushBarb = brushLine.clone(); brushBarb.repeat.set(5, 1); brushBarb.needsUpdate = true;
  var grungeLink = brushLine.clone(); grungeLink.repeat.set(3, 1); grungeLink.needsUpdate = true;
  // the same grime also darkens the base colour, like the worn stone-metal of the logo
  var asColor = function (t) { var c = t.clone(); c.colorSpace = THREE.SRGBColorSpace; c.needsUpdate = true; return c; };
  var silver = function (tex) {
    var m = new THREE.MeshPhysicalMaterial({
      color: 0xd6d0de, map: asColor(tex), metalness: 1, roughness: 0.6, roughnessMap: tex, bumpMap: tex, bumpScale: 1.6,
      emissive: 0x000000, envMapIntensity: 1.6
    });
    electrify(m);
    return m;
  };

  /* ---------- Current: up to 4 pulses travelling along x, injected into the metal shader ---------- */
  var NP = 4, pulses = [], pulseU = { value: [] };
  for (var q = 0; q < NP; q++) pulseU.value.push(new THREE.Vector4(0, 0, 1, 0));
  var electrify = function (mat) {
    mat.onBeforeCompile = function (sh) {
      sh.uniforms.uPulse = pulseU;
      sh.vertexShader = "varying float vPX;\n" + sh.vertexShader.replace("#include <begin_vertex>",
        "#include <begin_vertex>\nvec4 pxw = vec4(transformed, 1.0);\n#ifdef USE_INSTANCING\npxw = instanceMatrix * pxw;\n#endif\nvPX = (modelMatrix * pxw).x;");
      sh.fragmentShader = "varying float vPX;\nuniform vec4 uPulse[" + NP + "];\n" + sh.fragmentShader.replace("#include <emissivemap_fragment>",
        "#include <emissivemap_fragment>\nfloat pz = 0.0;\nfor (int i = 0; i < " + NP + "; i++) { float dd = (vPX - uPulse[i].x) / uPulse[i].z; pz += uPulse[i].y * exp(-dd * dd); }\n" +
        "pz = min(pz, 1.6);\ntotalEmissiveRadiance += vec3(0.42, 0.16, 1.0) * pz * 1.25 + vec3(0.85, 0.75, 1.0) * pow(pz, 4.0) * 0.35;");
    };
  };

  var W = 16, SAG = 0.95, M = 72;
  var lineMat = silver(brushLine), barbMat = silver(brushBarb);

  /* ---------- Tube with a radius profile (for tapered, cut barb points) ---------- */
  function profileTube(curve, seg, radial, rFn) {
    var frames = curve.computeFrenetFrames(seg, false);
    var pos = [], nor = [], uv = [], idx = [], P = new THREE.Vector3(), n = new THREE.Vector3();
    for (var i = 0; i <= seg; i++) {
      var t = i / seg, r = rFn(t);
      curve.getPointAt(t, P);
      var N = frames.normals[i], B = frames.binormals[i];
      for (var j = 0; j <= radial; j++) {
        var v = (j / radial) * Math.PI * 2, s = Math.sin(v), c = -Math.cos(v);
        n.set(c * N.x + s * B.x, c * N.y + s * B.y, c * N.z + s * B.z).normalize();
        pos.push(P.x + r * n.x, P.y + r * n.y, P.z + r * n.z);
        nor.push(n.x, n.y, n.z);
        uv.push(t, j / radial);
      }
    }
    for (i = 1; i <= seg; i++) for (j = 1; j <= radial; j++) {
      var a = (radial + 1) * (i - 1) + (j - 1), b = (radial + 1) * i + (j - 1), c2 = (radial + 1) * i + j, d = (radial + 1) * (i - 1) + j;
      idx.push(a, b, d, b, c2, d);
    }
    var g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx);
    return g;
  }
  var FnCurve = class extends THREE.Curve {
    constructor(fn) { super(); this.fn = fn; }
    getPoint(t, target) { return this.fn(t, target || new THREE.Vector3()); }
  };

  /* ---------- Line wire: two strands twisted into a rope ---------- */
  var SR = 0.078, HR = 0.074, TURNS = 34;
  var strands = [0, Math.PI].map(function (ph) {
    var curve = new FnCurve(function (t, o) {
      var a = TURNS * Math.PI * 2 * t + ph;
      return o.set(-W / 2 + t * W, HR * Math.cos(a), HR * Math.sin(a));
    });
    var geo = profileTube(curve, coarse ? 900 : 1500, coarse ? 8 : 12, function () { return SR; });
    geo.userData.bp = geo.attributes.position.array.slice();
    geo.userData.bn = geo.attributes.normal.array.slice();
    var mesh = new THREE.Mesh(geo, lineMat);
    mesh.frustumCulled = false;
    wire.add(mesh);
    return geo;
  });

  /* ---------- Barb: a wire wrapped round the line, both ends bent out and cut sharp ---------- */
  var BR = 0.05, RC = HR + SR + BR * 0.85, PRONG = 0.95;
  function barbWire(angle, dir) {
    var len = 0.34, turns = 2.5;
    var coil = new FnCurve(function (t, o) {
      var a = angle + dir * turns * Math.PI * 2 * t;
      return o.set(-len / 2 + t * len, RC * Math.cos(a), RC * Math.sin(a));
    });
    var parts = [profileTube(coil, 90, 10, function () { return BR; })];
    [0, 1].forEach(function (end) {
      var a = angle + dir * turns * Math.PI * 2 * end, x = -len / 2 + end * len;
      var radial = new THREE.Vector3(0, Math.cos(a), Math.sin(a));
      var circ = new THREE.Vector3(0, -Math.sin(a), Math.cos(a)).multiplyScalar(dir * (end ? 1 : -1));
      var p0 = new THREE.Vector3(x, 0, 0).addScaledVector(radial, RC);
      var p1 = p0.clone().addScaledVector(circ, 0.18).addScaledVector(radial, 0.12);
      var p2 = p0.clone().addScaledVector(radial, PRONG).addScaledVector(circ, 0.28).add(new THREE.Vector3((end ? 1 : -1) * 0.12, 0, 0));
      var prong = new THREE.QuadraticBezierCurve3(p0, p1, p2);
      parts.push(profileTube(prong, 40, 10, function (t) { return t < 0.72 ? BR : Math.max(0.002, BR * (1 - (t - 0.72) / 0.28) * (1 - (t - 0.72) / 0.28 * 0.15)); }));
    });
    return mergeGeometries(parts);
  }
  var barbGeo = mergeGeometries([barbWire(0.3, 1), barbWire(0.3 + Math.PI / 2, -1).translate(0.05, 0, 0)]);
  var NB = 10, barbX = [], barbTwist = [], barbPop = [];
  for (var b = 0; b < NB; b++) {
    barbX.push(-W / 2 + (b + 0.5) * (W / NB) + (Math.random() - 0.5) * 0.35);
    barbTwist.push(Math.random() * Math.PI * 2);
    barbPop.push(reduce ? 0 : -1); // -1 = not grown yet, otherwise the time it popped
  }
  var barbs = new THREE.InstancedMesh(barbGeo, barbMat, NB);
  barbs.frustumCulled = false;
  wire.add(barbs);

  /* ---------- Sparks ---------- */
  var NS = coarse ? 160 : 320, sp = { p: new Float32Array(NS * 3), c: new Float32Array(NS * 3), v: new Float32Array(NS * 3), life: new Float32Array(NS), max: new Float32Array(NS) }, sHead = 0;
  var sparkGeo = new THREE.BufferGeometry();
  sparkGeo.setAttribute("position", new THREE.BufferAttribute(sp.p, 3));
  sparkGeo.setAttribute("color", new THREE.BufferAttribute(sp.c, 3));
  var dotTex = (function () {
    var c = document.createElement("canvas"); c.width = c.height = 64;
    var g = c.getContext("2d"), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.25, "rgba(220,200,255,.9)"); gr.addColorStop(1, "rgba(120,60,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  })();
  var sparks = new THREE.Points(sparkGeo, new THREE.PointsMaterial({ size: 0.2, map: dotTex, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
  sparks.frustumCulled = false;
  scene.add(sparks);
  var burst = function (x, y, z, n, power) {
    for (var k = 0; k < n; k++) {
      var i = sHead; sHead = (sHead + 1) % NS;
      var a = Math.random() * Math.PI * 2, r = Math.random();
      sp.p[i * 3] = x; sp.p[i * 3 + 1] = y; sp.p[i * 3 + 2] = z;
      sp.v[i * 3] = (Math.random() - 0.5) * 3 * power;
      sp.v[i * 3 + 1] = (Math.cos(a) * 3 + 1.5) * power * (0.4 + r);
      sp.v[i * 3 + 2] = Math.sin(a) * 3 * power * (0.4 + r);
      sp.max[i] = sp.life[i] = 0.35 + Math.random() * 0.5;
    }
  };

  /* ---------- Lights ---------- */
  scene.add(new THREE.AmbientLight(0x7a4cff, 0.6));
  var key = new THREE.DirectionalLight(0xffffff, 1.2); key.position.set(-3, 6, 5); scene.add(key);
  var rim = new THREE.DirectionalLight(0x8f5bff, 2.4); rim.position.set(5, -3, -4); scene.add(rim);
  var glint = new THREE.PointLight(0xe6dcff, 18, 10, 1.5); glint.position.set(-3, 2.2, 2.6); scene.add(glint);
  var cursorLight = new THREE.PointLight(0xc4a8ff, 0, 8, 1.6); cursorLight.position.set(0, 0, 2); scene.add(cursorLight);
  var zap = new THREE.PointLight(0xb48cff, 0, 5, 1.4); zap.position.set(0, 0, 1.2); scene.add(zap);

  /* ---------- Physics: a spring string pinned at both ends ---------- */
  var oy = new Float32Array(M), oz = new Float32Array(M), vy = new Float32Array(M), vz = new Float32Array(M), xs = new Float32Array(M);
  for (var i = 0; i < M; i++) xs[i] = -W / 2 + (i / (M - 1)) * W;
  var sag = function (x) { var u = (2 * x) / W; return -SAG * (1 - u * u) + SAG * 0.35; };
  var sample = function (arr, x) {
    var u = ((x + W / 2) / W) * (M - 1), i0 = Math.max(0, Math.min(M - 2, Math.floor(u))), f = u - i0;
    return arr[i0] * (1 - f) + arr[i0 + 1] * f;
  };
  var wireY = function (x) { return sag(x) + sample(oy, x); };

  /* ---------- Sizing: fit the full span AND the full height of the barbs ---------- */
  var HALF_H = 2.15; // world units that must stay visible above/below the centre
  function resize() {
    var r = holder.getBoundingClientRect(), w = Math.max(1, r.width), h = Math.max(1, r.height);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    var tanH = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    var dW = (W * 0.86) / (2 * tanH * camera.aspect), dH = HALF_H / tanH;
    camera.position.set(0, -0.35, Math.max(dW, dH));
    camera.lookAt(0, -0.35, 0);
    camera.updateProjectionMatrix();
    camBase.copy(camera.position);
  }
  var camBase = new THREE.Vector3();
  resize();
  window.addEventListener("resize", resize);

  /* ---------- Current ---------- */
  var fire = function (x, dir, strength, speed) {
    if (pulses.length >= NP) pulses.shift();
    pulses.push({ x: x, dir: dir, s: strength, speed: speed || 15, w: 0.55 });
  };

  /* ---------- Pointer: push, light, click = charge ---------- */
  var mouse = { x: 0, y: 0, active: false, strength: 0 };
  var ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), hit = new THREE.Vector3(), zPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  var toWorld = function (cx, cy) {
    var r = holder.getBoundingClientRect();
    ndc.set(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    return ray.ray.intersectPlane(zPlane, hit) ? hit : null;
  };
  var inside = function (cx, cy, pad) {
    var r = holder.getBoundingClientRect();
    return cx > r.left - pad && cx < r.right + pad && cy > r.top - pad && cy < r.bottom + pad;
  };
  var spin = 0, shake = 0, live = false;
  window.addEventListener("pointermove", function (e) {
    if (!inside(e.clientX, e.clientY, 80)) { mouse.active = false; return; }
    var p = toWorld(e.clientX, e.clientY);
    if (p) { mouse.x = p.x; mouse.y = p.y; mouse.active = true; }
  }, { passive: true });
  window.addEventListener("pointerdown", function (e) {
    if (!live || !inside(e.clientX, e.clientY, 0)) return;
    var p = toWorld(e.clientX, e.clientY);
    if (!p || Math.abs(p.y - wireY(p.x)) > 1.6) return;
    for (var i = 1; i < M - 1; i++) {
      var d = Math.abs(xs[i] - p.x);
      if (d < 1.6) { var f = 1 - d / 1.6; vy[i] += (p.y > sag(xs[i]) ? -1 : 1) * 0.9 * f; vz[i] += 0.6 * f; }
    }
    fire(p.x, -1, 1.2, 18); fire(p.x, 1, 1.2, 18);
    burst(p.x, wireY(p.x), 0.2, 26, 1.2);
    zap.position.x = p.x; zap.intensity = 60; shake = Math.max(shake, 0.5);
    spin += 0.8;
  }, { passive: true });

  /* ---------- Intro: the wire is thrown in slack and yanked taut ---------- */
  var introAt = -1, stiff = 1;
  var startIntro = function () {
    if (introAt >= 0 || reduce) return;
    introAt = clockT || 0;
    wire.visible = true;
    for (var i = 0; i < M; i++) {
      var u = i / (M - 1);
      oy[i] = -1.25 * Math.sin(Math.PI * u) + 0.45 * Math.sin(3 * Math.PI * u + 0.5);
      oz[i] = 1.1 * Math.sin(2 * Math.PI * u);
      vy[i] = vz[i] = 0;
    }
    stiff = 3.2; shake = 1;
    fire(-W / 2 - 0.5, 1, 1.3, 13); fire(W / 2 + 0.5, -1, 1.3, 13);
  };
  if (!reduce) wire.visible = false;

  /* ---------- Scroll: roll + jolt on fast scrolls ---------- */
  var rollScroll = 0, lastScroll = window.scrollY, scrollKick = 0, secProg = 0.5;
  if (window.gsap && window.ScrollTrigger && !reduce) {
    ScrollTrigger.create({ trigger: section, start: "top 88%", once: true, onEnter: function () { startIntro(); } });
    ScrollTrigger.create({ trigger: section, start: "top bottom", end: "bottom top",
      onUpdate: function (self) { rollScroll = self.progress * Math.PI * 2.5; secProg = self.progress; } });
  } else if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { startIntro(); io.disconnect(); } }, { threshold: 0.3 });
    io.observe(holder);
  }
  window.addEventListener("scroll", function () {
    var dy = window.scrollY - lastScroll; lastScroll = window.scrollY;
    scrollKick += Math.max(-40, Math.min(40, dy)) * 0.004;
  }, { passive: true });

  var visible = true;
  if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }, { rootMargin: "100px" }).observe(holder);


  /* =====================================================================
     3D CHAINS behind the manifesto — same violet chrome, same current
     ===================================================================== */
  var chainVisible = false, chainTick = null;
  (function () {
    var small = window.matchMedia("(max-width: 767px)").matches;
    var box = document.createElement("div");
    box.className = "chain_canvas";
    box.setAttribute("aria-hidden", "true");
    section.insertBefore(box, holder.nextSibling);
    var r2;
    try { r2 = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" }); } catch (e) { box.remove(); return; }
    r2.setPixelRatio(Math.min(window.devicePixelRatio || 1, small ? 1 : 1.5));
    r2.outputColorSpace = THREE.SRGBColorSpace;
    r2.toneMapping = THREE.ACESFilmicToneMapping;
    r2.toneMappingExposure = 1.2;
    box.appendChild(r2.domElement);

    var sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(30, 1, 0.1, 300);
    sc.environment = studioEnv(r2);
    sc.add(new THREE.AmbientLight(0x7a4cff, 0.5));
    var k1 = new THREE.DirectionalLight(0xffffff, 1.3); k1.position.set(-4, 8, 6); sc.add(k1);
    var k2 = new THREE.DirectionalLight(0x8f5bff, 2.6); k2.position.set(6, -4, -5); sc.add(k2);
    var sweep = new THREE.PointLight(0xe6dcff, 30, 14, 1.4); sc.add(sweep);
    var hand = new THREE.PointLight(0xc4a8ff, 0, 10, 1.5); sc.add(hand);

    var chainMat = silver(grungeLink);

    /* One link: a stadium-shaped ring of round wire */
    var LS = 0.22, LR = 0.2, LW = 0.085, PITCH = 0.56;
    var linkGeo = new THREE.TubeGeometry(new FnCurve(function (t, o) {
      var L = 4 * LS + 2 * Math.PI * LR, d = t * L;
      if (d < 2 * LS) return o.set(-LS + d, LR, 0);
      d -= 2 * LS;
      if (d < Math.PI * LR) { var a = Math.PI / 2 - d / LR; return o.set(LS + LR * Math.cos(a), LR * Math.sin(a), 0); }
      d -= Math.PI * LR;
      if (d < 2 * LS) return o.set(LS - d, -LR, 0);
      d -= 2 * LS;
      var c = -Math.PI / 2 - d / LR; return o.set(-LS + LR * Math.cos(c), LR * Math.sin(c), 0);
    }), coarse ? 40 : 64, LW, coarse ? 8 : 12, true);

    /* Layout in canvas-normalised coords (u across, v down), z = depth, k = link size */
    var defs = [
      { k: 1.35, z: 2, pts: [[1.18, 0.02], [0.97, 0.1], [0.84, 0.23], [0.86, 0.38], [0.97, 0.48], [1.18, 0.55]], sway: 0.16 },  // heavy, wraps the book
      { k: 0.6, z: 0.4, pts: [[-0.14, 0.08], [0.05, 0.2], [0.14, 0.36], [0.08, 0.52], [-0.14, 0.64]], sway: 0.14 },         // left
      { k: 0.6, z: 0.4, pts: [[-0.12, 0.93], [0.25, 0.8], [0.55, 0.86], [0.84, 0.74], [1.12, 0.68]], sway: 0.1 }            // low, same size as the left one
    ];
    if (small) defs = [defs[1], defs[2], { k: 0.9, z: 1.5, pts: [[1.2, 0.02], [0.9, 0.12], [0.82, 0.3], [1.2, 0.42]], sway: 0.12 }];

    var D = 40, aspect = 1, V = new THREE.Vector3(), mouseC = { x: 0, y: 0, s: 0, on: false };
    var toWorld = function (u, v, z, out) {
      var f = (D - z) / D; // keep the layout the same at every depth
      return out.set((u - 0.5) * 16 * f, (0.5 - v) * (16 / aspect) * f, z);
    };
    var chains = defs.map(function (d, ci) {
      var base = [];
      if (d.loop) for (var i = 0; i < 10; i++) { var a = (i / 10) * Math.PI * 2; base.push([d.c[0] + Math.cos(a) * d.rx, d.c[1] + Math.sin(a) * d.ry * 1.6, (Math.sin(a * 2) * 0.4)]); }
      else d.pts.forEach(function (p, i) { base.push([p[0], p[1], Math.sin(i * 1.7 + ci) * 0.6]); });
      var ctrl = base.map(function () { return new THREE.Vector3(); });
      var curve = new THREE.CatmullRomCurve3(ctrl, !!d.loop, "centripetal");
      var mesh = new THREE.InstancedMesh(linkGeo, chainMat, 400);
      mesh.frustumCulled = false;
      sc.add(mesh);
      return { d: d, base: base, ctrl: ctrl, curve: curve, mesh: mesh, n: 0, seed: ci * 2.3 };
    });

    var layoutCtrl = function (c, t) {
      var d = c.d, par = (secProg - 0.5) * (2.2 + d.z * 0.6);
      for (var i = 0; i < c.base.length; i++) {
        var b = c.base[i];
        toWorld(b[0], b[1], d.z + b[2], c.ctrl[i]);
        c.ctrl[i].x += Math.sin(t * 0.45 + i * 1.1 + c.seed) * d.sway * 2;
        c.ctrl[i].y += Math.cos(t * 0.38 + i * 1.7 + c.seed) * d.sway * 2 + par;
        c.ctrl[i].z += Math.sin(t * 0.3 + i + c.seed) * d.sway * 3;
        if (mouseC.s > 0.01) { // push away from the cursor
          var dx = c.ctrl[i].x - mouseC.x, dy = c.ctrl[i].y - mouseC.y, dist = Math.sqrt(dx * dx + dy * dy) + 0.001;
          if (dist < 3) { var f = (1 - dist / 3) * mouseC.s * 1.2; c.ctrl[i].x += dx / dist * f; c.ctrl[i].y += dy / dist * f; c.ctrl[i].z += f * 0.8; }
        }
      }
      c.curve.needsUpdate = true;
    };

    function resize2() {
      var r = box.getBoundingClientRect(), w = Math.max(1, r.width), h = Math.max(1, r.height);
      r2.setSize(w, h, false);
      aspect = w / h;
      cam.aspect = aspect;
      D = 8 / (Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)) * aspect);
      cam.position.set(0, 0, D); cam.lookAt(0, 0, 0);
      cam.near = Math.max(0.1, D - 20); cam.far = D + 30;
      cam.updateProjectionMatrix();
      sc.fog = new THREE.Fog(0x010101, D - 1, D + 7);
      chains.forEach(function (c) { // link count from the path length
        layoutCtrl(c, 0);
        c.n = Math.min(400, Math.max(6, Math.floor(c.curve.getLength() / (PITCH * c.d.k))));
        c.mesh.count = c.n;
      });
    }
    resize2();
    if ("ResizeObserver" in window) new ResizeObserver(resize2).observe(box); else window.addEventListener("resize", resize2);

    /* cursor, in the chain plane */
    var rc = new THREE.Raycaster(), nd = new THREE.Vector2(), pl = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), hp = new THREE.Vector3();
    window.addEventListener("pointermove", function (e) {
      var r = box.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) { mouseC.on = false; return; }
      nd.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      rc.setFromCamera(nd, cam);
      if (rc.ray.intersectPlane(pl, hp)) { mouseC.x = hp.x; mouseC.y = hp.y; mouseC.on = true; }
    }, { passive: true });

    var m4 = new THREE.Matrix4(), T = new THREE.Vector3(), Y = new THREE.Vector3(), Z = new THREE.Vector3(), Zup = new THREE.Vector3(0, 0, 1), Yup = new THREE.Vector3(0, 1, 0), Pp = new THREE.Vector3(), Yr = new THREE.Vector3(), Zr = new THREE.Vector3();
    chainTick = function (dt, t) {
      mouseC.s += ((mouseC.on ? 1 : 0) - mouseC.s) * 0.06;
      for (var ci = 0; ci < chains.length; ci++) {
        var c = chains[ci], k = c.d.k;
        layoutCtrl(c, t);
        var closed = !!c.d.loop;
        for (var i = 0; i < c.n; i++) {
          var u = closed ? i / c.n : i / (c.n - 1);
          c.curve.getPointAt(u, Pp);
          c.curve.getTangentAt(u, T);
          Y.crossVectors(T, Zup);
          if (Y.lengthSq() < 1e-4) Y.crossVectors(T, Yup);
          Y.normalize(); Z.crossVectors(T, Y);
          // links alternate 90°, with a slow roll along the chain
          var th = (i % 2 ? Math.PI / 2 : 0) + Math.sin(t * 0.6 + i * 0.25 + c.seed) * 0.25;
          Yr.copy(Y).multiplyScalar(Math.cos(th)).addScaledVector(Z, Math.sin(th));
          Zr.crossVectors(T, Yr);
          m4.makeBasis(T, Yr, Zr).scale(V.set(k, k, k)).setPosition(Pp);
          c.mesh.setMatrixAt(i, m4);
        }
        c.mesh.instanceMatrix.needsUpdate = true;
      }
      sweep.position.set(Math.sin(t * 0.3) * 9, Math.cos(t * 0.23) * 6, 6);
      hand.intensity += ((mouseC.on ? 40 : 0) - hand.intensity) * 0.08;
      hand.position.set(mouseC.x, mouseC.y, 3);
      r2.render(sc, cam);
    };
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { chainVisible = en[0].isIntersecting; }, { rootMargin: "150px" }).observe(box);
    else chainVisible = true;
  })();

  /* =====================================================================
     3D CHAIN RING around the LINE-UP title — the back half renders behind
     the title, the front half in front of it (two canvases, one scene)
     ===================================================================== */
  var ringVisible = false, ringTick = null;
  (function () {
    var stage = document.querySelector(".lineup_title-stage");
    if (!stage) return;
    var small = window.matchMedia("(max-width: 767px)").matches;
    var mk = function (cls, after) {
      var el = document.createElement("div");
      el.className = "ring_canvas " + cls;
      el.setAttribute("aria-hidden", "true");
      if (after && after.parentNode === stage) stage.insertBefore(el, after.nextSibling); else stage.appendChild(el);
      return el;
    };
    var backBox = mk("is-back", stage.querySelector(".lineup_bg-text")), frontBox = mk("is-front", null);
    var mkR = function (box) {
      var r = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
      r.setPixelRatio(Math.min(window.devicePixelRatio || 1, small ? 1.5 : 2));
      r.outputColorSpace = THREE.SRGBColorSpace;
      r.toneMapping = THREE.ACESFilmicToneMapping;
      r.toneMappingExposure = 1.25;
      box.appendChild(r.domElement);
      return r;
    };
    var rb, rf;
    try { rb = mkR(backBox); rf = mkR(frontBox); } catch (e) { backBox.remove(); frontBox.remove(); return; }
    document.documentElement.classList.add("has-webgl-ring");
    // back canvas keeps the far half (z < 0), front canvas the near half (z > 0)
    rb.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0, 0, -1), 0)];
    rf.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)];

    var sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(24, 1, 0.1, 400);
    sc.environment = studioEnv(rb);
    var envF = studioEnv(rf);
    sc.add(new THREE.AmbientLight(0x7a4cff, 0.5));
    var k1 = new THREE.DirectionalLight(0xffffff, 1.4); k1.position.set(-4, 8, 6); sc.add(k1);
    var k2 = new THREE.DirectionalLight(0x8f5bff, 2.4); k2.position.set(6, -4, -5); sc.add(k2);
    var sweep = new THREE.PointLight(0xe6dcff, 40, 16, 1.4); sc.add(sweep);

    var ringMat = silver(grungeLink);

    var LS = 0.22, LR = 0.2, LW = 0.085, PITCH = 0.56, R = 6, TILT = THREE.MathUtils.degToRad(14);
    var linkGeo = new THREE.TubeGeometry(new FnCurve(function (t, o) {
      var L = 4 * LS + 2 * Math.PI * LR, d = t * L;
      if (d < 2 * LS) return o.set(-LS + d, LR, 0);
      d -= 2 * LS;
      if (d < Math.PI * LR) { var a = Math.PI / 2 - d / LR; return o.set(LS + LR * Math.cos(a), LR * Math.sin(a), 0); }
      d -= Math.PI * LR;
      if (d < 2 * LS) return o.set(LS - d, -LR, 0);
      d -= 2 * LS;
      var c = -Math.PI / 2 - d / LR; return o.set(-LS + LR * Math.cos(c), LR * Math.sin(c), 0);
    }), coarse ? 32 : 48, LW, coarse ? 8 : 10, true);

    var group = new THREE.Group(), spinner = new THREE.Group();
    group.add(spinner); sc.add(group);
    group.position.y = 0.35;
    var mesh = new THREE.InstancedMesh(linkGeo, ringMat, 600);
    mesh.frustumCulled = false;
    spinner.add(mesh);
    var N = 0, k = 0.34, shown = reduce ? 1 : 0, revealAt = -1, charged = false;

    function build() {
      var r = stage.getBoundingClientRect(), w = Math.max(1, r.width), h = Math.max(1, r.height);
      rb.setSize(w, h, false); rf.setSize(w, h, false);
      cam.aspect = w / h;
      var ringPx = Math.min(small ? 350 : 800, w * 0.9), ppu = ringPx / (2 * R);
      var visW = w / ppu, dist = (visW / 2) / (Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)) * cam.aspect);
      cam.position.set(0, 0, dist); cam.lookAt(0, 0, 0); cam.near = Math.max(0.1, dist - 12); cam.far = dist + 12;
      cam.updateProjectionMatrix();
      k = (small ? 13 : 22) / (0.98 * ppu);
      N = Math.min(600, Math.round((2 * Math.PI * R) / (PITCH * k)));
      var m4 = new THREE.Matrix4(), T = new THREE.Vector3(), P = new THREE.Vector3(), Y = new THREE.Vector3(), Z = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0), Yr = new THREE.Vector3(), Zr = new THREE.Vector3(), S = new THREE.Vector3();
      for (var i = 0; i < N; i++) {
        var a = (i / N) * Math.PI * 2;
        P.set(Math.cos(a) * R, 0, Math.sin(a) * R);            // ring lies flat in XZ…
        T.set(-Math.sin(a), 0, Math.cos(a));
        Y.copy(P).normalize(); Z.crossVectors(T, Y);
        var th = i % 2 ? Math.PI / 2 : 0;
        Yr.copy(Y).multiplyScalar(Math.cos(th)).addScaledVector(Z, Math.sin(th));
        Zr.crossVectors(T, Yr);
        m4.makeBasis(T, Yr, Zr).scale(S.set(k, k, k)).setPosition(P);
        mesh.setMatrixAt(i, m4);
      }
      mesh.instanceMatrix.needsUpdate = true;
      mesh.count = Math.round(N * shown);
    }
    build();
    if ("ResizeObserver" in window) new ResizeObserver(build).observe(stage); else window.addEventListener("resize", build);

    // …then tipped towards the camera so it reads as an ellipse, tilted like the old ring
    var baseRotZ = THREE.MathUtils.degToRad(-6.3), scrollRot = 0, tiltX = 0, tiltY = 0, tx = 0, ty = 0;
    group.rotation.set(TILT, 0, baseRotZ);
    if (window.gsap && window.ScrollTrigger && !reduce) {
      ScrollTrigger.create({ trigger: stage, start: "top bottom", end: "bottom top",
        onUpdate: function (self) { scrollRot = THREE.MathUtils.degToRad(-10 + self.progress * 20); } });
      ScrollTrigger.create({ trigger: stage, start: "top 75%", once: true, onEnter: function () { revealAt = clockT || 0; } });
    } else shown = 1;
    mesh.count = Math.round(N * shown);

    window.addEventListener("pointermove", function (e) {
      var r = stage.getBoundingClientRect();
      if (e.clientY < r.top || e.clientY > r.bottom) { tx = ty = 0; return; }
      tx = ((e.clientY - r.top) / r.height - 0.5) * 0.35;
      ty = ((e.clientX - r.left) / r.width - 0.5) * 0.5;
    }, { passive: true });

    ringTick = function (dt, t) {
      if (revealAt >= 0 && shown < 1) { // the chain winds itself round the title
        var q = Math.min(1, (t - revealAt) / 1.6);
        shown = q < 0.5 ? 2 * q * q : 1 - Math.pow(-2 * q + 2, 2) / 2;
        mesh.count = Math.round(N * shown);
        if (q >= 1 && !charged) { charged = true; fire(-W / 2 - 1, 1, 1.2, 16); }
      }
      spinner.rotation.y = -t * 0.12;                               // links travel round the loop
      tiltX += (tx - tiltX) * 0.06; tiltY += (ty - tiltY) * 0.06;
      group.rotation.set(TILT + tiltX + Math.sin(t * 0.7) * 0.03, tiltY, baseRotZ + scrollRot);
      sweep.position.set(Math.sin(t * 0.5) * 8, 3, 6);
      rb.render(sc, cam);
      var e0 = sc.environment; sc.environment = envF; rf.render(sc, cam); sc.environment = e0;
    };
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { ringVisible = en[0].isIntersecting; }, { rootMargin: "100px" }).observe(stage);
    else ringVisible = true;
  })();

  var timer = new THREE.Timer(), roll = 0, clockT = 0, nextBeat = 0, beat = 0;
  var BAR = 60 / 140 * 4; // one bar at 140 BPM
  var mtx = new THREE.Matrix4(), qT = new THREE.Quaternion(), qR = new THREE.Quaternion(), P = new THREE.Vector3(), S = new THREE.Vector3(1, 1, 1);
  var X = new THREE.Vector3(1, 0, 0), tan = new THREE.Vector3(), tip = new THREE.Vector3();
  var elastic = function (t) { return t >= 1 ? 1 : t <= 0 ? 0 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI) / 3) + 1; };

  function step(dt, t) {
    mouse.strength += ((mouse.active ? 1 : 0) - mouse.strength) * 0.08;
    stiff += (1 - stiff) * Math.min(1, dt * 1.6);
    var kick = scrollKick; scrollKick *= 0.85;
    for (var i = 1; i < M - 1; i++) {
      var x = xs[i], y = sag(x) + oy[i];
      var ay = -oy[i] * 6 * stiff + (oy[i - 1] + oy[i + 1] - 2 * oy[i]) * 900 * stiff - vy[i] * 3.2;
      var az = -oz[i] * 6 * stiff + (oz[i - 1] + oz[i + 1] - 2 * oz[i]) * 900 * stiff - vz[i] * 3.2;
      ay += Math.sin(t * 1.1 + x * 0.55) * 0.3 + Math.sin(t * 2.3 + x * 1.7) * 0.1;
      ay -= kick * 40 * Math.sin(Math.PI * (i / (M - 1)));
      if (mouse.strength > 0.01) {
        var dx = x - mouse.x, dy = y - mouse.y, d = Math.sqrt(dx * dx + dy * dy);
        if (d < 1.9) { var f = 1 - d / 1.9; f = f * f * mouse.strength; ay += (dy >= 0 ? 1 : -1) * f * 38; az += f * 22; }
      }
      vy[i] += ay * dt; vz[i] += az * dt;
    }
    for (i = 1; i < M - 1; i++) { oy[i] += vy[i] * dt; oz[i] += vz[i] * dt; }
    spin *= Math.pow(0.95, dt * 60);
    roll += (0.1 + spin) * dt;
  }

  function current(dt, t) {
    // travel + fade, pop barbs / throw sparks where the current passes
    for (var k = pulses.length - 1; k >= 0; k--) {
      var p = pulses[k], x0 = p.x;
      p.x += p.dir * p.speed * dt;
      p.s *= Math.pow(0.55, dt);
      for (var b = 0; b < NB; b++) {
        var bx = barbX[b];
        if ((x0 - bx) * (p.x - bx) > 0) continue; // not crossed this frame
        if (barbPop[b] < 0) { barbPop[b] = t; burst(bx, wireY(bx), 0.3, 30, 1.2); }
        else if (Math.random() < 0.55 * p.s) {
          tip.set(0, Math.cos(barbTwist[b] + roll), Math.sin(barbTwist[b] + roll)).multiplyScalar(PRONG * 0.9);
          burst(bx + (Math.random() - 0.5) * 0.3, wireY(bx) + tip.y, tip.z, 6 + Math.round(8 * p.s), 0.7 * p.s);
        }
      }
      if (p.x < -W / 2 - 3 || p.x > W / 2 + 3 || p.s < 0.05) pulses.splice(k, 1);
    }
    for (var i = 0; i < NP; i++) {
      var pp = pulses[i];
      pulseU.value[i].set(pp ? pp.x : 0, pp ? pp.s : 0, pp ? pp.w : 1, 0);
    }
    // on the beat: one pulse per bar, a heavier one every 4th bar
    if (introAt >= 0 && t - introAt > 1.8 && t >= nextBeat) {
      beat++;
      var heavy = beat % 4 === 0, dir = Math.random() < 0.5 ? 1 : -1;
      fire(dir > 0 ? -W / 2 - 1 : W / 2 + 1, dir, heavy ? 1.15 : 0.7, heavy ? 20 : 14);
      if (heavy) { shake = Math.max(shake, 0.35); spin += 0.4; }
      nextBeat = t + BAR;
    }
    if (nextBeat === 0 && introAt >= 0) nextBeat = introAt + 1.8;
    // sparks
    for (var j = 0; j < NS; j++) {
      if (sp.life[j] <= 0) { sp.c[j * 3] = sp.c[j * 3 + 1] = sp.c[j * 3 + 2] = 0; continue; }
      sp.life[j] -= dt;
      sp.v[j * 3 + 1] -= 7 * dt;
      sp.v[j * 3] *= 0.985; sp.v[j * 3 + 2] *= 0.985;
      sp.p[j * 3] += sp.v[j * 3] * dt; sp.p[j * 3 + 1] += sp.v[j * 3 + 1] * dt; sp.p[j * 3 + 2] += sp.v[j * 3 + 2] * dt;
      var l = Math.max(0, sp.life[j] / sp.max[j]);
      sp.c[j * 3] = 1.1 * l; sp.c[j * 3 + 1] = 0.9 * l * l + 0.25 * l; sp.c[j * 3 + 2] = 1.5 * l;
    }
    sparkGeo.attributes.position.needsUpdate = true;
    sparkGeo.attributes.color.needsUpdate = true;
  }

  function update(elapsed) {
    var a = roll + rollScroll, ca = Math.cos(a), sa = Math.sin(a);
    for (var s = 0; s < strands.length; s++) {
      var g = strands[s], p = g.attributes.position.array, nm = g.attributes.normal.array, bp = g.userData.bp, bn = g.userData.bn;
      for (var v = 0; v < p.length; v += 3) {
        var bx = bp[v], by = bp[v + 1], bz = bp[v + 2];
        p[v] = bx;
        p[v + 1] = by * ca - bz * sa + sag(bx) + sample(oy, bx);
        p[v + 2] = by * sa + bz * ca + sample(oz, bx);
        var ny = bn[v + 1], nz = bn[v + 2];
        nm[v + 1] = ny * ca - nz * sa; nm[v + 2] = ny * sa + nz * ca;
      }
      g.attributes.position.needsUpdate = true;
      g.attributes.normal.needsUpdate = true;
    }
    for (var b = 0; b < NB; b++) {
      var x0 = barbX[b], e = 0.05;
      tan.set(2 * e, wireY(x0 + e) - wireY(x0 - e), sample(oz, x0 + e) - sample(oz, x0 - e)).normalize();
      qT.setFromUnitVectors(X, tan);
      // barbs twist into place as they pop out
      var pop = reduce ? 1 : barbPop[b] < 0 ? 0 : elastic((elapsed - barbPop[b]) / 0.9);
      qR.setFromAxisAngle(X, a + barbTwist[b] + (1 - Math.min(pop, 1)) * 2.5);
      P.set(x0, wireY(x0), sample(oz, x0));
      S.setScalar(Math.max(0.0001, pop));
      mtx.compose(P, qT.multiply(qR), S);
      barbs.setMatrixAt(b, mtx);
    }
    barbs.instanceMatrix.needsUpdate = true;
    glint.position.x = Math.sin(elapsed * 0.35) * 6;
    cursorLight.intensity += ((mouse.active ? 34 : 0) - cursorLight.intensity) * 0.08;
    cursorLight.position.x += (mouse.x - cursorLight.position.x) * 0.15;
    cursorLight.position.y += (mouse.y - cursorLight.position.y) * 0.15;
    zap.intensity *= 0.9;
    // light follows the strongest pulse
    var best = null;
    for (var k = 0; k < pulses.length; k++) if (!best || pulses[k].s > best.s) best = pulses[k];
    if (best && best.x > -W / 2 - 1 && best.x < W / 2 + 1) { zap.position.x = best.x; zap.position.y = wireY(Math.max(-W / 2, Math.min(W / 2, best.x))); zap.intensity = Math.max(zap.intensity, 18 * best.s); }
    // camera shake
    shake *= 0.9;
    camera.position.set(camBase.x + (Math.random() - 0.5) * 0.16 * shake, camBase.y + (Math.random() - 0.5) * 0.16 * shake, camBase.z);
  }

  function frame() {
    requestAnimationFrame(frame);
    timer.update();
    clockT = timer.getElapsed();
    if (!visible && !chainVisible && !ringVisible) return;
    var dt = Math.min(timer.getDelta(), 1 / 30);
    live = introAt >= 0;
    current(dt, clockT); // the current runs through the wire and the chains
    if (visible) {
      for (var k = 0; k < 3; k++) step(dt / 3, clockT);
      update(clockT);
      renderer.render(scene, camera);
    }
    if (chainVisible && chainTick) chainTick(dt, clockT);
    if (ringVisible && ringTick) ringTick(dt, clockT);
  }
  if (reduce) {
    update(0); renderer.render(scene, camera);
    if (chainTick) chainTick(0, 0);
    if (ringTick) ringTick(0, 0);
    window.addEventListener("resize", function () { renderer.render(scene, camera); if (chainTick) chainTick(0, 0); if (ringTick) ringTick(0, 0); });
  } else frame();

})();
}