// 판매용 이미지(2000x2000 PNG) 생성: node listing.mjs <outDir>
import { chromium } from 'playwright';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const out = resolve(process.argv[2] || 'listing_en');
const fonts = 'file://' + resolve('fonts/en.css');
const exe = '/opt/pw-browsers/chromium';
const base = `<link rel="stylesheet" href="${fonts}"><style>
body{margin:0}*{box-sizing:border-box}
.s{width:1000px;height:1000px;position:relative;overflow:hidden;color:#fff;font-family:'Inter';
background:radial-gradient(ellipse at 30% 10%,#2c3b63 0%,#0f1629 70%)}
.snow{position:absolute;inset:0;background-image:radial-gradient(#ffffff55 2px,transparent 3px),radial-gradient(#ffffff30 1.5px,transparent 2.5px);
background-size:70px 70px,43px 43px;background-position:0 0,20px 27px}
.pf{font-family:'Playfair Display'}.k{letter-spacing:.3em;color:#f3a3a3;font-weight:700;font-size:22px}
.pill{border:2px solid #ffffff66;border-radius:99px;padding:8px 20px;font-weight:700;font-size:22px}
.card{background:#fbfaf7;color:#1d2230;border-radius:14px;padding:26px;box-shadow:0 20px 50px #0008}
</style>`;
const slides = {
  '1_cover': `<div class="s"><div class="snow"></div><div style="position:absolute;left:80px;right:80px;bottom:90px">
<div class="k">PRINTABLE MURDER MYSTERY GAME</div>
<div class="pf" style="font-weight:900;font-size:110px;line-height:1.02;margin-top:20px">Murder at<br>White Snow<br>Lodge</div>
<div class="pf" style="font-size:36px;color:#c9d2ea;margin-top:24px">A K-Drama murder mystery party</div>
<div style="display:flex;gap:12px;margin-top:36px">${['6–8 players','~2 hours','Instant download'].map(t=>`<span class="pill">${t}</span>`).join('')}</div></div></div>`,
  '2_inside': `<div class="s"><div class="snow"></div><div style="position:absolute;inset:70px">
<div class="k">WHAT'S INSIDE</div><div class="pf" style="font-weight:900;font-size:64px;margin:14px 0 10px">Everything you need</div><div style="font-size:24px;color:#c9d2ea;margin-bottom:30px">US Letter PDF · print at home, cut, play tonight</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:22px">
${[['Host Guide','Setup, rules, round-by-round script, ballots & score sheet'],['6 Character Booklets','Secrets, true timelines, personal goals'],
['20 Clue Cards','3 rounds: crime scene → search → second look'],['6 Invitations','Send before the party to assign roles'],
['Sealed Solution','Full deduction chain + epilogue'],['8-Player Expansion','2 extra suspects, 3 clues, invitations']].map(([a,b])=>
`<div class="card"><div class="pf" style="font-weight:900;font-size:30px">${a}</div><div style="font-size:21px;color:#5b6275;margin-top:8px;line-height:1.45">${b}</div></div>`).join('')}
</div></div></div>`,
  '3_suspects': `<div class="s"><div class="snow"></div><div style="position:absolute;inset:70px">
<div class="k">SIX TO EIGHT SUSPECTS · ONE LIAR</div><div class="pf" style="font-weight:900;font-size:60px;margin:14px 0 30px">Who killed the novelist?</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
${[['Seo Ha-jin','The editor who knows too much'],['Kang Min-jae','The lawyer with missing money'],['Yoon Se-ah','The niece about to be disinherited'],
['Baek Do-hyun','The caretaker with a new name'],['Oh Ji-yu','The protégée with a teal pen'],['Han Gyeol','The journalist with a camera']].map(([a,b])=>
`<div class="card" style="padding:22px 26px"><div class="pf" style="font-weight:900;font-size:32px">${a}</div><div style="font-size:21px;color:#9b2c2c;margin-top:4px">${b}</div></div>`).join('')}
</div><div style="margin-top:30px;font-size:24px;color:#c9d2ea">Every role can be played by anyone. Only the killer may lie.</div></div></div>`,
};
const b = await chromium.launch(existsSync(exe) ? { executablePath: exe } : {});
const p = await b.newPage({ viewport: { width: 1000, height: 1000 }, deviceScaleFactor: 2 });
for (const [name, html] of Object.entries(slides)) {
  // file:// 페이지여야 로컬 글꼴을 읽을 수 있다
  mkdirSync(resolve('out'), { recursive: true });
  const tmp = resolve('out', `listing_${name}.html`);
  writeFileSync(tmp, '<!doctype html><meta charset="utf-8">' + base + html);
  await p.goto('file://' + tmp, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: `${out}/${name}.png` });
  console.log('✔ ' + name);
}
await b.close();
