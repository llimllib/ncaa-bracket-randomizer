import { chromium } from 'playwright';
import assert from 'node:assert';
import { test, describe, before, after, beforeEach } from 'node:test';

const URL = process.env.URL || 'http://localhost:8000';

let browser, page;

before(async () => {
  browser = await chromium.launch();
});

after(async () => {
  await browser.close();
});

beforeEach(async () => {
  page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  await page.goto(URL, { waitUntil: 'networkidle' });
});

describe('initial state', () => {
  test('loads with R64 teams visible', async () => {
    // First team in south region should be Auburn (1 seed)
    const firstTeam = page.locator('.team').first();
    const text = await firstTeam.textContent();
    assert.match(text, /Auburn/);
  });

  test('later rounds are empty', async () => {
    const emptyTeams = page.locator('.team.empty');
    const count = await emptyTeams.count();
    // 4 regions × (8+4+2) empty slots in rounds 2-4 = 56, plus semis (4) + champ (2) + final four slots
    assert.ok(count > 50, `Expected many empty slots, got ${count}`);
  });

  test('no champion banner on load', async () => {
    const banner = page.locator('.champion-banner');
    const text = await banner.textContent();
    assert.strictEqual(text.trim(), '');
  });
});

describe('click to advance', () => {
  test('clicking a team advances them to the next round', async () => {
    // Click Auburn (first clickable team)
    await page.locator('.team.clickable').first().click();
    await page.waitForTimeout(100);

    // Auburn should now appear in R32 (second column)
    const r32Teams = page.locator('.round').nth(1).locator('.team:not(.empty)');
    const count = await r32Teams.count();
    assert.ok(count >= 1, 'Expected at least one team in R32');
    const text = await r32Teams.first().textContent();
    assert.match(text, /Auburn/);
  });

  test('changing a pick clears downstream', async () => {
    // Advance Auburn to R32
    await page.locator('.team.clickable').first().click();
    await page.waitForTimeout(100);

    // Verify Auburn is in R32
    let r32Text = await page.locator('.round').nth(1).locator('.team:not(.empty)').first().textContent();
    assert.match(r32Text, /Auburn/);

    // Now click Alabama St. instead (second team in first matchup)
    const firstMatchup = page.locator('.matchup').first();
    const alabamaSt = firstMatchup.locator('.team').nth(1);
    await alabamaSt.click();
    await page.waitForTimeout(100);

    // R32 should now show Alabama St., not Auburn
    r32Text = await page.locator('.round').nth(1).locator('.team:not(.empty)').first().textContent();
    assert.match(r32Text, /Alabama St/);
  });

  test('can advance teams all the way through a region', async () => {
    // Click through all 8 R64 matchups in south (first region), picking the top team each time
    const round1 = page.locator('.bracket > .round').first();
    for (let i = 0; i < 8; i++) {
      const matchup = round1.locator('.matchup').nth(i);
      await matchup.locator('.team').first().click();
      await page.waitForTimeout(50);
    }

    // Now R32 should have 8 teams filled — click through 4 matchups
    const round2 = page.locator('.bracket > .round').nth(1);
    for (let i = 0; i < 4; i++) {
      const matchup = round2.locator('.matchup').nth(i);
      await matchup.locator('.team').first().click();
      await page.waitForTimeout(50);
    }

    // S16: 2 matchups
    const round3 = page.locator('.bracket > .round').nth(2);
    for (let i = 0; i < 2; i++) {
      const matchup = round3.locator('.matchup').nth(i);
      await matchup.locator('.team').first().click();
      await page.waitForTimeout(50);
    }

    // E8: 1 matchup
    const round4 = page.locator('.bracket > .round').nth(3);
    await round4.locator('.matchup').first().locator('.team').first().click();
    await page.waitForTimeout(50);

    // The region winner should now appear in the semifinal
    const semi1 = page.locator('.semi-matchup').first();
    const semiTeams = semi1.locator('.team:not(.empty)');
    const count = await semiTeams.count();
    assert.ok(count >= 1, 'Expected region winner in semifinal');
  });
});

describe('hover tooltip', () => {
  test('shows win probabilities on hover', async () => {
    const firstMatchup = page.locator('.matchup').first();
    await firstMatchup.hover();
    await page.waitForTimeout(300);

    const tooltip = page.locator('.tooltip');
    const count = await tooltip.count();
    assert.strictEqual(count, 1, 'Expected one tooltip');

    const text = await tooltip.textContent();
    assert.match(text, /Auburn/);
    assert.match(text, /Alabama St/);
    assert.match(text, /%/);
  });

  test('tooltip disappears on mouse leave', async () => {
    const firstMatchup = page.locator('.matchup').first();
    await firstMatchup.hover();
    await page.waitForTimeout(300);

    // Move mouse away
    await page.mouse.move(0, 0);
    await page.waitForTimeout(300);

    const count = await page.locator('.tooltip').count();
    assert.strictEqual(count, 0, 'Tooltip should disappear');
  });

  test('no tooltip on empty matchups', async () => {
    // Hover over an empty R32 matchup
    const r32Matchup = page.locator('.round').nth(1).locator('.matchup').first();
    await r32Matchup.hover();
    await page.waitForTimeout(300);

    const count = await page.locator('.tooltip').count();
    assert.strictEqual(count, 0, 'No tooltip on empty matchup');
  });
});

describe('randomize', () => {
  test('fills entire bracket', async () => {
    await page.click('#randomize');
    await page.waitForTimeout(200);

    // Should have a champion
    const banner = page.locator('.champion-banner');
    const text = await banner.textContent();
    assert.ok(text.includes('🏆'), 'Expected champion banner');

    // No empty team slots in the regions (all filled)
    // Every round should have teams
    const emptyInRegions = page.locator('.round .team.empty');
    const emptyCount = await emptyInRegions.count();
    assert.strictEqual(emptyCount, 0, `Expected no empty slots after randomize, got ${emptyCount}`);
  });

  test('produces different results on multiple runs', async () => {
    const champions = new Set();
    for (let i = 0; i < 10; i++) {
      await page.click('#randomize');
      await page.waitForTimeout(50);
      const text = await page.locator('.champion-banner').textContent();
      champions.add(text);
    }
    // With 10 runs, we should get at least 2 different champions (extremely likely)
    assert.ok(champions.size >= 2, `Expected varied results, got ${champions.size} unique champions`);
  });
});

describe('clear', () => {
  test('resets bracket after randomize', async () => {
    await page.click('#randomize');
    await page.waitForTimeout(100);
    await page.click('#clear');
    await page.waitForTimeout(100);

    const banner = page.locator('.champion-banner');
    const text = await banner.textContent();
    assert.strictEqual(text.trim(), '', 'Champion should be cleared');

    const emptyTeams = page.locator('.team.empty');
    const count = await emptyTeams.count();
    assert.ok(count > 50, 'Expected many empty slots after clear');
  });

  test('resets bracket after manual picks', async () => {
    // Make a pick
    await page.locator('.team.clickable').first().click();
    await page.waitForTimeout(100);

    // Clear
    await page.click('#clear');
    await page.waitForTimeout(100);

    // R32 should be empty again
    const r32Empty = page.locator('.round').nth(1).locator('.team.empty');
    const count = await r32Empty.count();
    assert.ok(count >= 2, 'R32 should be empty after clear');
  });
});

describe('chaos slider', () => {
  test('max chalk produces chalky results', async () => {
    // Set slider to max chalk
    await page.evaluate(() => {
      const slider = document.getElementById('chaos-slider');
      slider.value = '2';
      slider.dispatchEvent(new Event('input'));
    });

    // Run 20 times, count how often a 1-seed wins
    let oneSeedWins = 0;
    for (let i = 0; i < 20; i++) {
      await page.click('#randomize');
      await page.waitForTimeout(30);
      const text = await page.locator('.champion-banner').textContent();
      // Check if champion is a 1-seed by looking at semis/championship
      const championSeed = await page.evaluate(() => {
        const s = document.querySelector('.center-col .matchup .team.winner .seed');
        return s ? s.textContent : '';
      });
      if (championSeed === '1') oneSeedWins++;
    }
    // At heavy chalk, 1-seeds should win most of the time
    assert.ok(oneSeedWins >= 10, `Expected mostly 1-seed champions at max chalk, got ${oneSeedWins}/20`);
  });

  test('tooltip probabilities change with slider', async () => {
    // Get probability at true odds
    await page.evaluate(() => {
      document.getElementById('chaos-slider').value = '1';
    });
    const firstMatchup = page.locator('.matchup').first();
    await firstMatchup.hover();
    await page.waitForTimeout(200);
    const trueOddsText = await page.locator('.tooltip').textContent();
    await page.mouse.move(0, 0);
    await page.waitForTimeout(200);

    // Set to max chaos
    await page.evaluate(() => {
      document.getElementById('chaos-slider').value = '0';
    });
    await firstMatchup.hover();
    await page.waitForTimeout(200);
    const chaosText = await page.locator('.tooltip').textContent();

    // The percentages should differ
    assert.notStrictEqual(trueOddsText, chaosText, 'Probabilities should change with slider');
  });
});
