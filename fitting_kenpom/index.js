const puppeteer = require("puppeteer");
const fs = require("fs");

const HEADLESS = false;

/* print progress in blue */
function progress(s) {
  console.log("\x1b[34m%s\x1b[0m", s);
}

/* print debug in red */
function debug(s) {
  console.log("\x1b[31m%s\x1b[0m", s);
}

function sanitize(s) {
  return s.replace(/[^a-z0-9]/gi, "_").toLowerCase();
}

function decodeEntities(encodedString) {
  var translate_re = /&(nbsp|amp|quot|lt|gt);/g;
  var translate = {
    nbsp: " ",
    amp: "&",
    quot: '"',
    lt: "<",
    gt: ">",
  };
  return encodedString
    .replace(translate_re, function (_match, entity) {
      return translate[entity];
    })
    .replace(/&#(\d+);/gi, function (_match, numStr) {
      var num = parseInt(numStr, 10);
      return String.fromCharCode(num);
    });
}

async function getLoggedInPage(browser) {
  progress("logging in kenpom");

  const page = await browser.newPage();
  await page.goto("https://kenpom.com");

  /* log messages from the page console to our console */
  page.on("console", (msg) => {
    for (let i = 0; i < msg.args().length; ++i)
      console.log(`${i}: ${msg.args()[i]}`);
  });

  /* wait for the login elements, and fill them in */
  await page.waitForSelector('input[name="email"]');
  const emailBox = 'input[name="email"]';
  const pwBox = 'input[name="password"]';
  await page.type(emailBox, process.env.USERNAME);
  await page.type(pwBox, process.env.PASSWORD);

  /* click the submit button and log in */
  await Promise.all([
    page.click('input[name="submit"]'),
    page.waitForNavigation({ waitUntil: "networkidle0" }),
  ]);

  return page;
}

async function getTeamData(page, teamDataFile) {
  await page.goto("https://kenpom.com");
  await page.waitForSelector("#ratings-table");
  const teams = await page.$$eval("tr.tourney", (trs) =>
    trs.map((tr) =>
      Array.from(tr.querySelectorAll("td")).map((td) => td.innerHTML)
    )
  );
  fs.writeFileSync(teamDataFile, JSON.stringify(teams, null, 2));
}

function cleanRank(rankLink) {
  let [_, rank] = rankLink.match(/>(\d+)</);
  return parseInt(rank);
}

function cleanTeamData(teamDataFile) {
  const teamData = JSON.parse(fs.readFileSync(teamDataFile));
  cleanData = {};

  for (const team of teamData) {
    [
      overallRank,
      nameLink,
      confLink,
      record,
      adjEM,
      adjO,
      adjORank,
      adjD,
      adjDRank,
      adjT,
      adjTRank,
      luck,
      luckRank,
      sosAdjEM,
      sosAdjEMRank,
      sosOppO,
      sosOppORank,
      sosOppD,
      sosOppDRank,
      ncSOS,
      ncSOSRank,
    ] = team;
    let [_, teamLink, name, seed] = nameLink.match(
      /href="(.*?)".*?>(.*?)<.*?seed.*?(\d+)/
    );
    let [__, conf] = confLink.match(/>(.*?)</);
    name = decodeEntities(name);
    const cleanTeam = {
      overall: parseInt(overallRank),
      name: name,
      teamLink: teamLink,
      seed: parseInt(seed),
      conference: conf,
      record: record.split("-").map((x) => parseInt(x)),
      adjEM: parseFloat(adjEM),
      adjO: parseFloat(adjO),
      adjORank: cleanRank(adjORank),
      adjD: parseFloat(adjD),
      adjDRank: cleanRank(adjDRank),
      adjT: parseFloat(adjT),
      adjTRank: cleanRank(adjTRank),
      luck: parseFloat(luck),
      luckRank: cleanRank(luckRank),
    };
    cleanData[name] = cleanTeam;
  }

  fs.writeFileSync("teams_clean.json", JSON.stringify(cleanData, null, 2));
  return cleanData;
}

async function getGames(page, teamData) {
  for (const team of Object.values(teamData)) {
    await page.goto(`https://kenpom.com/${team.teamLink}`);

    const html = await page.content();
    fs.writeFileSync(`teams/${sanitize(team.name)}`, html);
  }
}

async function parseGames(page, teamData) {
  for (const team of Object.values(teamData)) {
    const html = fs.readFileSync(`teams/${sanitize(team.name)}`);
    await page.setContent(html.toString());
    await page.waitForSelector("table");

    /* for now, just grab the win prob and opponent for their next game */
    const games = await page.$$eval("tr.un", (trs) =>
      trs.map((tr) =>
        Array.from(tr.querySelectorAll("td")).map((td) => td.innerHTML)
      )
    );
    team.games = [];
    for (const game of games) {
      let [
        dt,
        _,
        oppSeed,
        oppLink,
        expectedResult,
        expectedTempo,
        winProb,
        loc,
        __,
        ___,
      ] = game;
      let [, opp] = oppLink.match(/>(.*?)</);
      let [, site] = loc.match(/>(.*?)</);
      let [, winOrLoss, score1, score2] = expectedResult.match(
        /b>(.*?)<.*?(\d+)-(\d+)/
      );
      team.games.push({
        oppRank: cleanRank(oppSeed),
        opponent: decodeEntities(opp),
        winProb: parseFloat(winProb) / 100,
        site: site,
        expectedTempo: parseFloat(expectedTempo),
        expectedWinOrLoss: winOrLoss,
        // pretty sure kenpom just puts the higher score as score1
        score: [parseInt(score1), parseInt(score2)],
      });
    }
  }

  fs.writeFileSync("teams_games.json", JSON.stringify(teamData, null, 2));
  return cleanData;
}

function writeDiffs(teamData) {
  const diffs = {};

  for (const team of Object.values(teamData)) {
    if (team.games.length < 1) {
      continue;
    }
    const g = team.games[0];
    const opp = teamData[team.games[0].opponent];

    /* make sure we don't record duplicate games */
    const gameKey = [team.name, opp.name].sort().join("-");
    if (diffs.hasOwnProperty(gameKey)) {
      continue;
    }

    const t1_rating = team.adjEM;
    const t2_rating = opp.adjEM;
    diffs[gameKey] = {
      ratingDiff: Math.abs(t1_rating - t2_rating),
      marginOfVictory: g.score[0] - g.score[1],
      winProb: g.winProb >= 0.5 ? g.winProb : 1 - g.winProb,
      fav: g.winProb >= 0.5 ? team.name : opp.name,
      dog: g.winProb >= 0.5 ? opp.name : team.name,
    };
  }

  fs.writeFileSync("diffs.json", JSON.stringify(diffs, null, 2));
  return diffs;
}

(async () => {
  const teamDataFile = "teams.json";
  let browser = await puppeteer.launch({ headless: HEADLESS });

  /* download summary data */
  if (!fs.existsSync(teamDataFile)) {
    progress("downloading team summary data");
    /* we don't want a logged in page because that has a favorite row that
     * messes up our team row scraping */
    let page = await browser.newPage();
    await getTeamData(page, teamDataFile);
  }

  /* clean summary data */
  progress("cleaning team summary data");
  teamData = cleanTeamData(teamDataFile);

  /* download team pages */
  if (!fs.existsSync("teams")) {
    progress("downloading team data pages");
    fs.mkdirSync("teams");
    let loggedInPage = await getLoggedInPage(browser);
    await getGames(loggedInPage, teamData);
  }

  /* pull desired info from the team pages */
  progress("cleaning game data");
  let localPage = await browser.newPage();
  await parseGames(localPage, teamData);

  await browser.close();

  progress("making diff json");
  writeDiffs(teamData);
})();
