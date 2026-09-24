// out/*.html → pdf/*.pdf (A4). 사용: node pdf.mjs <htmlDir> <pdfDir>
import { chromium } from 'playwright';
import { readdirSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

const [src, dst] = process.argv.slice(2).map((p) => resolve(p));
const exe = '/opt/pw-browsers/chromium';
const browser = await chromium.launch(existsSync(exe) ? { executablePath: exe } : {});
for (const f of readdirSync(src).filter((f) => f.endsWith('.html'))) {
  const page = await browser.newPage();
  await page.goto('file://' + join(src, f), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: join(dst, f.replace(/\.html$/, '.pdf')), format: 'A4', printBackground: true, preferCSSPageSize: true });
  console.log('✔ pdf/' + f.replace(/\.html$/, '.pdf'));
  await page.close();
}
await browser.close();
