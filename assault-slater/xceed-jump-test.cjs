const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const embed = fs.readFileSync(process.argv[2] || __dirname + '/webflow/xceed-embed.html', 'utf8');
const page = `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">
<a id="gt" href="#tickets" style="position:fixed;top:0;left:0;z-index:9;background:#fff">Get tickets</a>
<div style="height:3000px;background:#234">hero</div><div id="lineup" style="height:1500px;background:#333">LINEUP</div>
<div style="height:1200px;background:#555"></div><section id="tickets" style="height:800px;background:#777">${embed}</section>
<div style="height:2000px"></div></body></html>`;
const widgets = {
  scrollIntoView: `w.scrollIntoView();`,
  smoothIntoView: `w.scrollIntoView({behavior:"smooth"});`,
  windowScrollTo: `window.scrollTo(0, w.getBoundingClientRect().top + scrollY);`,
  focusInput: `w.querySelector("input").focus();`,
  iframeAutofocus: `var f=document.createElement("iframe");f.style.height="400px";f.srcdoc='<input autofocus>';w.appendChild(f);`,
};
(async () => {
  const b = await chromium.launch();
  const run = async (name, js, mode) => {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    const p = await ctx.newPage();
    await p.route('https://widget.xceed.me/**', r => r.fulfill({ contentType: 'application/javascript', body:
      `setTimeout(function(){var w=document.getElementById("xceed-widget");w.insertAdjacentHTML("beforeend",'<div style="height:300px;background:red">WIDGET <input id="wi"></div>');${js}window.__ran=1;},700);` }));
    await p.route('http://t.local/', r => r.fulfill({ contentType: 'text/html', body: page }));
    await p.goto('http://t.local/');
    if (mode === 'click') { await p.click('#gt'); await p.waitForTimeout(2500); }
    else {
      for (let i = 0; i < 38; i++) { await p.mouse.wheel(0, 100); await p.waitForTimeout(30); }
      await p.waitForTimeout(300);
      await p.evaluate(() => { const y0 = scrollY; window.__max = 0; (function f() { window.__max = Math.max(window.__max, Math.abs(scrollY - y0)); requestAnimationFrame(f); })(); });
      if (mode === 'swipe') await p.evaluate(async () => { for (let i = 0; i < 60; i++) { window.dispatchEvent(new Event('touchmove')); scrollBy(0, 4); await new Promise(r => requestAnimationFrame(r)); } });
      await p.waitForTimeout(2500);
    }
    const r = await p.evaluate(() => ({ y: Math.round(scrollY), maxMove: Math.round(window.__max || 0), ran: !!window.__ran, inert: document.getElementById('xceed-widget').inert }));
    // then the visitor scrolls down to the widget: it must be usable (not inert) and focusable
    for (let i = 0; i < 25; i++) { await p.mouse.wheel(0, 100); await p.waitForTimeout(30); }
    await p.waitForTimeout(400);
    r.atWidget = await p.evaluate(() => ({ inert: document.getElementById('xceed-widget').inert, y: Math.round(scrollY) }));
    await p.click('#wi').catch(e => r.clickErr = e.message.slice(0, 60));
    r.focused = await p.evaluate(() => document.activeElement && document.activeElement.id);
    console.log(name.padEnd(34), JSON.stringify(r));
    await ctx.close();
  };
  for (const [k, js] of Object.entries(widgets)) await run(k, js, 'still');
  await run('scrollIntoView while swiping', widgets.scrollIntoView, 'swipe');
  await run('Get tickets tap (must reach)', widgets.scrollIntoView, 'click');
  await b.close();
})();
