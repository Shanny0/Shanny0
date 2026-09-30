const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const mk = embed => `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">
<nav class="nav_component" style="position:fixed;top:0;left:0;right:0;height:60px;background:#000;z-index:9"><a id="gt" href="#tickets">Get tickets</a> <a id="gl" href="#lineup">Line-up</a> <a id="gr" href="#/events">widget route</a></nav>
<div style="height:3000px">hero</div><div id="lineup" style="height:1500px;background:#333">LINEUP</div>
<div style="height:1200px"></div><section id="tickets" style="height:900px;background:#777">${embed}</section><div style="height:2000px"></div></body></html>`;
// fake Xceed: hash router - "#/..." or empty = OK, anything else = 404; re-renders on hashchange
const fake = `(function(){var w=document.getElementById("xceed-widget");function r(){var h=location.hash;w.dataset.page=(!h||/^#\\//.test(h))?"OK "+(h||"home"):"404";w.textContent="WIDGET "+w.dataset.page;}r();addEventListener("hashchange",r);addEventListener("popstate",r);})();`;
(async () => {
  const b = await chromium.launch();
  const run = async (label, embedFile, url, steps) => {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } }); const p = await ctx.newPage();
    await p.route('https://widget.xceed.me/**', r => r.fulfill({ contentType: 'application/javascript', body: fake }));
    await p.route('http://t.local/**', r => r.fulfill({ contentType: 'text/html', body: mk(fs.readFileSync(embedFile, 'utf8')) }));
    await p.goto(url); await p.waitForTimeout(800);
    const out = [];
    for (const s of steps) { await p.click(s); await p.waitForTimeout(1800); out.push(s + '→' + JSON.stringify(await p.evaluate(() => ({ widget: (document.getElementById('xceed-widget').dataset.page) || 'not loaded', url: location.hash || '(none)', y: Math.round(scrollY), tickets: Math.round(document.getElementById('tickets').getBoundingClientRect().top + scrollY - 60), lineup: Math.round(document.getElementById('lineup').getBoundingClientRect().top + scrollY - 60) })))); }
    if (!steps.length) out.push('load→' + JSON.stringify(await p.evaluate(() => ({ widget: document.getElementById('xceed-widget').dataset.page || 'not loaded', url: location.hash || '(none)' }))));
    console.log(label.padEnd(34), out.join('  '));
    await ctx.close();
  };
  for (const [name, f] of [['NEW', __dirname + '/webflow/xceed-embed.html']]) {
    await run(name + ' tap Get tickets, then Line-up', f, 'http://t.local/', ['#gt', '#gl']);
    await run(name + ' open /#tickets directly', f, 'http://t.local/#tickets', []);
  }
  await b.close();
})();
