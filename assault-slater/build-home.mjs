import { minify } from "terser";
import fs from "fs";
const W = new URL(".", import.meta.url).pathname; // run from assault-slater (needs: npm i terser)
const src = fs.readFileSync(W + "assault-home.js", "utf8");
const r = await minify(src, { ecma: 2020, compress: { passes: 2 }, mangle: true, format: { comments: false } });
if (/<\/script/i.test(r.code)) throw new Error("</script>");
let head = fs.readFileSync(W + "webflow/site-head.html", "utf8");
const a = "<!-- ASSAULT Home (EN + ES) script, runs only on / and /es (readable source: assault-home.js) -->\n<script>";
const i = head.indexOf(a) + a.length, j = head.indexOf("</script>", i);
if (head.indexOf(a) < 0 || j < 0) throw new Error("markers");
head = head.slice(0, i) + r.code + head.slice(j);
const g = ".page_grain{", k = head.indexOf("}", head.indexOf(g)) + 1;
if (!head.includes(".page_grain.is-still")) head = head.slice(0, k) + ".page_grain.is-still{mix-blend-mode:normal;opacity:.05}" + head.slice(k);
fs.writeFileSync(W + "webflow/site-head.html", head);
console.log("head", head.length, "script", r.code.length);
