# AGENTS.md — Notes for AI assistants working on this project

## Project Overview

NCAA tournament bracket simulator. Single-page vanilla HTML/CSS/JS app — no React, no build tools, no external libraries. Displays a 68-team bracket and lets users simulate or manually pick games.

## Key Files

- `index.html` — The entire app. Inline CSS + JS, single file.
- `2025.bracket.json` — Test bracket data (2025 teams with 2026 barthag values). This is placeholder data; will be replaced when the real 2026 bracket is announced on Selection Sunday.
- `2026_team_results.csv` — Torvik ratings data. Key columns: `team` (col 2), `barthag` (col 9).
- `logos/` — Team logo PNGs, named by ESPN team ID (e.g., `150.png` for Duke). Downloaded from ESPN CDN.
- `bracket.test.mjs` — Playwright test suite (15 tests). Run with `node --test bracket.test.mjs`.
- `screenshot.mjs` — Playwright script to take a screenshot. Usage: `node screenshot.mjs [url] [outfile] [slider_value]`.
- `espn_ids.json` — Manifest mapping all 365 D1 team names (Torvik naming convention) to ESPN team IDs. Used for looking up `espn_id` when generating bracket JSON. Team names match the `var teams` array in Torvik's `tranketology.html`.
- `tranketology.html` — Saved copy of Torvik's T-Ranketology bracket projection page. Contains the `var teams` array of all D1 team names and the projected bracket table. Useful reference for team names and bubble teams.
- `PLAN.md` — Original design document (partially outdated; this file is more current).

## Architecture

### Data Format (`*.bracket.json`)

```json
{
  "layout": {
    "topLeft": "south",
    "bottomLeft": "midwest",
    "topRight": "east",
    "bottomRight": "west"
  },
  "south": {
    "1": { "name": "Auburn", "seed": 1, "barthag": 0.858, "espn_id": 2 },
    "16": { "name": "Alabama St.", "seed": 16, "barthag": 0.212, "espn_id": 2011 },
    ...
  },
  ...
}
```

- `layout` controls which region goes in which quadrant of the bracket. This is set by the committee on Selection Sunday.
- Each region has 16 teams keyed by seed ("1" through "16").
- `barthag` is Torvik's probability of beating an average D-1 team. Used for Log5 win probability calculation.
- `espn_id` maps to logo files in `logos/{espn_id}.png`.

### Simulation Math

**Log5 formula** converts two barthag values to head-to-head win probability:

```
P(A beats B) = (pA - pA * pB) / (pA + pB - 2 * pA * pB)
```

**Power transform** for the chaos/chalk slider:

```
p_adjusted = p^k / (p^k + (1-p)^k)
```

- k=1: true odds (Log5 as-is)
- k<1: more chaos (upsets more likely)
- k>1: more chalk (favorites more likely)
- Slider maps [0, 2] → k=[0.25, 5] via piecewise exponential

Verified against barttorvik.com: Duke vs Florida St. = 93% matches Torvik's own calculation.

### Bracket Layout (CSS Grid)

9-column, 2-row grid:

```
Col:  1    2    3    4    5     6    7    8    9
      R64  R32  S16  E8   Center E8  S16  R32  R64
      |--- left regions --|     |-- right regions -|
```

- Row 1: top-left and top-right regions
- Row 2: bottom-left and bottom-right regions
- Col 5: Championship (top) + two semifinals side-by-side (bottom), spanning both rows
- Right-side regions are column-reversed (R64 on the outside)
- Region labels span cols 1-4 or 6-9, vertically centered on their region

### State Management

Mutable `state` object holds the bracket:

```js
state.regions[pos].rounds[r][i]  // team or null
state.finalFour.semi1, semi2, semi1Winner, semi2Winner, champion
```

- `rounds[0]` = 16 R64 teams (always filled from JSON)
- `rounds[1]` through `rounds[4]` = winners (null until picked/simulated)
- Clicking a team calls `advanceInRegion()` which sets the winner and cascade-clears downstream if the pick changed
- `simulateAll()` fills everything at once (Randomize button)
- `initState()` resets to R64 only (Clear button)

### Logo Display

- Appear starting in Sweet 16 (round index ≥ 2), larger in E8/FF/Championship
- Round index 2 (S16): `round-with-logos` class, 18×18px logos
- Round index 3+ (E8, FF, Champ): `round-large-logos` class, 22×22px logos
- Champion banner has a spinning golden sunburst (`conic-gradient` + CSS animation)
- Logo files are local in `logos/` — named by `espn_id`

### Team Name Mismatches

Torvik CSV and ESPN use different names for some teams. Known mappings:
- `Omaha` (bracket) → `Nebraska Omaha` (Torvik)
- `McNeese` → `McNeese St.`
- `SIUE` → `SIU Edwardsville`
- `Grand Canyon` → ESPN calls them "Lopes" not "Antelopes"

ESPN API names that differ from Torvik names (all correctly mapped in `espn_ids.json`):
- `Connecticut` → ESPN: `UConn Huskies`
- `Mississippi` → ESPN: `Ole Miss Rebels`
- `Illinois Chicago` → ESPN: `UIC Flames`
- `LIU` → ESPN: `Long Island University Sharks` (ESPN ID: 112358)
- `Appalachian St.` → ESPN: `App State Mountaineers`
- `FIU` → ESPN: `Florida International Panthers`
- `IU Indy` → ESPN: `IU Indianapolis Jaguars`
- `UMKC` → ESPN: `Kansas City Roos`
- `San Jose St.` → ESPN: `San José State Spartans`

When generating new bracket JSON, watch for name mismatches between the bracket announcement, Torvik CSV, and ESPN API.

### Logos

Logo source URL pattern: `https://a.espncdn.com/i/teamlogos/ncaa/500/{espn_id}.png`

As of March 2026, `logos/` contains 148 PNGs covering all teams in Torvik's T-Ranketology projected bracket plus last year's tournament field. When the real bracket drops, any team not already in `logos/` can be downloaded using the ESPN ID from `espn_ids.json`. Notable ESPN IDs for teams that were tricky to find:
- **Queens** → `2511` (not 2833 which 404s)
- **LIU** (Long Island University) → `112358`
- **Hawaii** → `62` (listed as Hawai'i on ESPN)

## Testing

```bash
node --test bracket.test.mjs
```

Requires `playwright` npm package and a dev server on port 8000 (e.g., `devd .`). Override URL with `URL=http://... node --test bracket.test.mjs`.

Tests cover: initial state, click-to-advance with cascade clearing, hover tooltips, randomize, clear, chaos slider behavior.

## Updating Torvik Data & Regenerating Bracket

1. **Download fresh Torvik CSV:**
   ```bash
   curl -s "https://barttorvik.com/2026_team_results.csv" -o 2026_team_results.csv
   ```

2. **Regenerate bracket JSON** (picks up new barthag values):
   ```bash
   python3 generate_bracket.py
   ```

3. **Check for missing logos:**
   ```python
   python3 -c "
   import json, os
   with open('2026.bracket.json') as f:
       b = json.load(f)
   for region in ['east','south','west','midwest']:
       for seed, team in b[region].items():
           if not os.path.exists(f'logos/{team[\"espn_id\"]}.png'):
               print(f'Missing: {team[\"name\"]} -> logos/{team[\"espn_id\"]}.png')
   "
   ```

4. **Download any missing logos:**
   ```bash
   curl -s -o logos/{espn_id}.png "https://a.espncdn.com/i/teamlogos/ncaa/500/{espn_id}.png"
   ```

5. **Run tests** (requires dev server on port 8000):
   ```bash
   node --test bracket.test.mjs
   ```

If the bracket itself changes (not just barthag updates), edit `generate_bracket.py` to reflect the new regions/seeds/teams, then re-run steps 2–5. If the first team in the top-left region changes, update the hardcoded team names in `bracket.test.mjs` too (tests reference the 1-seed and 16-seed of that region).

## What's Not Done Yet

- **First Four play-in games** — depends on Selection Sunday announcement
- **Print stylesheet polish** — basic `@media print` exists but not tested

## Dev Server

The owner uses `devd` to serve locally. Don't start a dev server yourself. The Playwright tests and screenshot script expect port 8000 by default.

## Style Preferences

- No frameworks, no build tools — keep it vanilla
- Single HTML file with inline CSS and JS
- Small, readable team slots (9px font in R64/R32, scaling up in later rounds)
- Logos from Sweet 16 onward only — don't clutter early rounds
- The bracket should be roughly printable-page-shaped and centered on screen
