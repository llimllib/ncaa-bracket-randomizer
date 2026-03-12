import { chromium } from 'playwright';

const url = process.argv[2] || 'http://localhost:8000';
const outFile = process.argv[3] || 'screenshot.png';
const sliderValue = process.argv[4]; // optional: set chaos slider value

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
await page.goto(url, { waitUntil: 'networkidle' });

// Optionally set slider value
if (sliderValue !== undefined) {
  await page.evaluate((val) => {
    const slider = document.getElementById('chaos-slider');
    slider.value = val;
    slider.dispatchEvent(new Event('input'));
  }, sliderValue);
}

// Click randomize and wait for the bracket to update
await page.click('#randomize');

// Wait for logo images to load
await page.waitForFunction(() => {
  const imgs = document.querySelectorAll('.logo');
  if (imgs.length === 0) return false;
  return Array.from(imgs).every(img => img.complete && img.naturalWidth > 0);
}, { timeout: 10000 }).catch(() => console.log('Warning: some logos may not have loaded'));

await page.screenshot({ path: outFile, fullPage: true });
console.log(`Saved screenshot to ${outFile}`);
await browser.close();
