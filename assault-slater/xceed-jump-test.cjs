const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const embed = fs.readFileSync(__dirname + '/webflow/xceed-embed.html', 'utf8');
const page = `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">
<a id="gt" href="#tickets" style="position:fixed;top:0;left:0;z-index:9;background:#fff">Get tickets</a>
<div style="height:3000px;background:linear-gradient(#123,#456)">hero..lineup</div>
<div id="lineup" style="height:1500px;background:#333">LINEUP</div>
<div style="height:1200px;background:#555"></div>
<section id="tickets" style="height:800px;background:#777">${embed}</section>
<div style="height:2000px"></div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const run = async (name, mode, jumpMode) => {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: mode === 'touch' });
    const p = await ctx.newPage();
    let loaded = 0;
    await p.route('https://widget.xceed.me/**', r => { loaded++; r.fulfill({ contentType: 'application/javascript', body:
      `setTimeout(function(){var w=document.getElementById("xceed-widget");w.innerHTML='<div style="height:600px;background:red">WIDGET</div>';w.scrollIntoView(${jumpMode === 'smooth' ? '{behavior:"smooth"}' : ''});window.__jumped=1;},800);` }); });
    await p.route('http://t.local/', r => r.fulfill({ contentType: 'text/html', body: page }));
    await p.goto('http://t.local/');
    let out = {};
    if (mode === 'touch') {
      // finger swipes: touchstart/touchmove, the page moves 60px per frame, then ~1s of momentum with no touch events
      await p.evaluate(async (keepSwiping) => {
        const fr = () => new Promise(r => requestAnimationFrame(r));
        const touch = t => window.dispatchEvent(new Event(t));
        while (scrollY < 3800) { touch("touchmove"); scrollBy(0, 60); await fr(); }
        for (let i = 0; i < 60; i++) { scrollBy(0, Math.max(1, 20 - i / 3)); await fr(); }   // momentum
        if (keepSwiping) for (let i = 0; i < 60; i++) { touch("touchmove"); scrollBy(0, 8); await fr(); }
      }, jumpMode === "swiping");
      await p.waitForTimeout(2500);
    } else if (mode === 'click') {
      await p.click('#gt'); await p.waitForTimeout(2500);
    } else {
      for (let i = 0; i < 38; i++) { await p.mouse.wheel(0, 100); await p.waitForTimeout(30); } // to ~3000 = lineup
      if (mode === 'still') await p.waitForTimeout(2500);
      if (mode === 'scrolling') { for (let i = 0; i < 12; i++) { await p.mouse.wheel(0, 20); await p.waitForTimeout(100); } await p.waitForTimeout(1000); }
    }
    out.afterJump = await p.evaluate(() => Math.round(scrollY));
    out.widgetTop = await p.evaluate(() => Math.round(document.getElementById('xceed-widget').getBoundingClientRect().top + scrollY));
    out.jumped = await p.evaluate(() => !!window.__jumped); out.loaded = loaded;
    for (let i = 0; i < 7; i++) { await p.mouse.wheel(0, 100); await p.waitForTimeout(40); } await p.waitForTimeout(400); out.afterMore = await p.evaluate(() => Math.round(scrollY));
    console.log(name.padEnd(28), JSON.stringify(out));
    await ctx.close();
  };
  await run('still, instant jump', 'still', 'instant');
  await run('scrolling, instant jump', 'scrolling', 'instant');
  await run('still, smooth jump', 'still', 'smooth');
  await run('touch, still, jump', 'touch', 'instant');
  await run('touch, swiping, jump', 'touch', 'swiping');
  await run('tap Get tickets (allow)', 'click', 'instant');
  await b.close();
})();
