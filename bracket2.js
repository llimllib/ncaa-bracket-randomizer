//a dummy console function so console.log doesn't kill shitty browsers
if(typeof console === "undefined") { console = { log: function() { } }; }

function log5(a, b) {
  return (a - a * b) / (a + b - 2 * a * b);
}

var roundOffsets = {1: 0, 2: 32, 3: 48, 4: 56, 5: 60, 6: 62, 7: 63};
function nextgame(round, gid) {
  return roundOffsets[round+1] + Math.ceil((gid - roundOffsets[round]) / 2);
}

// return a if a wins, else b
function whowins(a, b, randomness) {
  var fav = Math.max(a, b);
  var dog = Math.min(a, b);
  var odds = log5(fav, dog);

  // TODO return of the randomness slider
  if (randomness == "0") {
    return fav;
  }
  if (randomness == "1") {
    if (Math.random() > odds && Math.random() > odds) {
      return dog;
    }
    return fav;
  }
  if (randomness == "2") {
    if (Math.random() > odds) {
      return dog;
    }
    return fav;
  }
}

function advance(team, nextgid, gid) {
  var is_top = gid % 2 == 1;

  //championship game
  if (nextgid == 64) {
    d3.select("#game63").datum().topteam = team;
    return;
  }

  game = d3.select("#game" + nextgid).datum();
  if (is_top) {
    game.topteam = team;
  } else {
    game.bottomteam = team;
  }
}

function drawWinners() {
  for (var round=2; round < 7; round++) {
    d3.selectAll(".round" + round + " text").remove();

    d3.selectAll(".round" + round)
      .append("text")
        .attr("x", function(d) { return d.round * roundwidth + 3; })
        .attr("y", function(d) { return bottomliney(d) - 1; })
        .style("font", "10px sans-serif")
        .text(function(d) { if (d.bottomteam) { return d.bottomteam.name; }});

    d3.selectAll(".round" + round)
      .append("text")
        .attr("x", function(d) { return d.round * roundwidth + 3; })
        .attr("y", function(d) { return topliney(d) - 1; })
        .style("font", "10px sans-serif")
        .text(function(d) { if (d.topteam) { return d.topteam.name; }});
  }

  var lastline = (lineheight * ((Math.pow(2, 6)-1) / 2) + lineheight);

  d3.select(".winner text").remove();
  d3.select(".winner")
    .append("text")
    .attr("x", 7 * roundwidth + 3)
    .attr("y", lastline - 1)
    .style("font", "10px sans-serif")
    .text(function(d) { return d.winner; });
}

function randomize() {
  var randomness = $("#randomness input:checked").attr("randomness");
  for (var round=0; round < 7; round++) {
    d3.selectAll(".round" + round).each(function(d) {
      var nextgid = nextgame(d.round, d.gid);
      if (!(nextgid >= 1 && nextgid <= 64)) { throw new Error("invalid gid ", gid, d.round, d.gid); }

      var winner = whowins(d.topteam.rating, d.bottomteam.rating, randomness);
      if (winner == d.topteam.rating) {
        //console.log(d.topteam.name, d.topteam.rating, "beats", d.bottomteam.name, d.bottomteam.rating)
        advance(d.topteam, nextgid, d.gid);
      } else {
        //console.log(d.bottomteam.name, d.bottomteam.rating, "beats", d.topteam.name, d.topteam.rating)
        advance(d.bottomteam, nextgid, d.gid);
      }
    });
  }

  drawWinners();
}

var regionoffset = {"south": 0, "west": 8, "east": 16, "midwest": 24};

function findgame(region, gameoffset) {
  var gid = regionoffset[region] + gameoffset;
  for (var i=0; i < games.length; i++) {
    if (games[i].gid == gid) return games[i];
  }
  throw new Error("couldn't find game " + gid);
}

function set(region, gameoffset, topteam, bottomteam) {
  var game = findgame(region, gameoffset);
  game.topteam = topteam;
  game.bottomteam = bottomteam;
}

var width = 920,
    height = 700,
    roundwidth = 100,
    lineheight = 18,
    textpadding = 2, // space between bracket line and text
    gameheight = 30,
    linecolor = "#ddd";

function main() {

  var bracket = d3.select("#bracket").append("svg")
      .attr("class", "bracket")
      .attr("width", width)
      .attr("height", height);

  var line = d3.svg.line();

  function gameregion(gid) {
    if ((gid >= 1 && gid <= 8) || (gid >= 33 && gid <= 36) ||
        (gid >= 49 && gid <= 50) || (gid == 57)) { return "south"; }
    if ((gid >= 9 && gid <= 16) || (gid >= 37 && gid <= 40) ||
        (gid >= 51 && gid <= 52) || (gid == 58)) { return "west"; }
    if ((gid >= 17 && gid <= 24) || (gid >= 41 && gid <= 44) ||
        (gid >= 53 && gid <= 54) || (gid == 59)) { return "east"; }
    if ((gid >= 25 && gid <= 32) || (gid >= 45 && gid <= 48) ||
        (gid >= 55 && gid <= 56) || (gid == 60)) { return "midwest"; }
    if (gid == 61) { return "south-east"; }
    if (gid == 62) { return "west-midwest"; }
    if (gid == 63) { return "south-east-west-midwest"; }

    // raise an error if we fall through
    throw new Error("undefined region for gid " + gid);
  }

  // returns the y coordinate for the game within its region
  // (hence height/2)
  var gamey = d3.scale.linear()
    .domain([1, 9])
    .range([0, height/2]);

  var rounds = [1,2,3,4,5,6];
  var ngames = 32;
  var gid = 0;
  var regions = ["west", "east", "south", "midwest"];
  games = [];

  // create the games array without teams
  $.each(rounds, function(i, round) {
    var roundgame = 1;
    var regiongame = {"south": 1, "west": 1, "east": 1, "midwest": 1};
    for (var i=0; i < ngames; i++) {
      gid += 1;
      region = gameregion(gid);
      games.push({
        gid: gid,
        round: round,
        roundgame: roundgame,
        region: region,
        regiongame: regiongame[region],
        topteam: undefined,
        bottomteam: undefined
      });
      roundgame += 1;
      regiongame[region] += 1;
    }
    ngames /= 2;
  });

  d3.json("teams.json", function(error, json) {
    $.each(json, function(region, seeds) {
      set(region, 1, seeds["1"], seeds["16"]);
      set(region, 2, seeds["8"], seeds["9"]);
      set(region, 3, seeds["5"], seeds["12"]);
      set(region, 4, seeds["4"], seeds["13"]);
      set(region, 5, seeds["6"], seeds["11"]);
      set(region, 6, seeds["3"], seeds["14"]);
      set(region, 7, seeds["7"], seeds["10"]);
      set(region, 8, seeds["2"], seeds["15"]);
    });

    gamedivs = bracket.selectAll(".game")
      .data(games)
      .enter()
      .append("g")
        .attr("class", function(d) { return "game round" + d.round; })
        .attr("id", function(d) { return "game" + d.gid; });

    linewidth = 1;

    var ipad = {1: 0, 2: 22, 3: 63, 4: 145, 5: 80, 6: 80};
    function innerpadding(d) {
      return ipad[d.round];
    }

    gamegs = d3.selectAll(".game").filter(function(g) { return g.gid < 61; });

    // top line
    gamegs.append("line")
      .attr("x1", 0)
      .attr("x2", roundwidth)
      .attr("y1", lineheight + textpadding)
      .attr("y2", lineheight + textpadding)
      .style("stroke", linecolor);

    // bottom line
    gamegs.append("line")
      .attr("x1", 0)
      .attr("x2", roundwidth)
      .attr("y1", function(d) { return innerpadding(d) + 2*lineheight + 2*textpadding; })
      .attr("y2", function(d) { return innerpadding(d) + 2*lineheight + 2*textpadding; })
      .style("stroke", linecolor);

    function rightline(d) {
      if (d.region == "east" || d.region == "midwest") {
        return 0;
      } else {
        return roundwidth;
      }
    }

    // right line
    gamegs.append("line")
      .attr("x1", rightline)
      .attr("x2", rightline)
      .attr("y1", lineheight + textpadding)
      .attr("y2", function(d) { return innerpadding(d) + 2*lineheight + 2*textpadding; })
      .style("stroke", linecolor);

    //top teams
    gamegs.append("text")
      .attr("x", 0)
      .attr("y", lineheight)
      .style("font", "10px sans-serif")
      .text(function(d) { if (d.topteam) {return d.topteam.seed + ". " + d.topteam.name; }});

    //top teams
    gamegs.append("text")
      .attr("x", 0)
      .attr("y", function(d) { return innerpadding(d) + 2* lineheight + textpadding; })
      .style("font", "10px sans-serif")
      .text(function(d) { if (d.bottomteam) {return d.bottomteam.seed + ". " + d.bottomteam.name; }});

    var regionheight = {"south": 0, "west": height/2, "east": 0, "midwest": height/2};
    var roundheight = {1: 0, 2: 10, 3: 30, 4: 75, 5: 80, 6: 80};
    var gamepadding = {1: 5, 2: 24, 3: 66, 4: 0, 5: 0, 6: 0};

    function layout(d) {
      var gameheight = 2*lineheight + innerpadding(d);
      var y = regionheight[d.region] + roundheight[d.round] + (d.regiongame-1) * (gameheight + gamepadding[d.round]);
      // these are on the right side
      if (d.region == "east" || d.region == "midwest") {
        var x = width-(d.round)*roundwidth;
      } else {
        var x = (d.round-1)*roundwidth;
      }
      return "translate("+x+","+y+")"
    }

    gamegs.attr("transform", layout);

    // South - East semifinal
    d3.select("#game61")
      .attr("transform", "translate(400, 180)")
      .append("line")
      .attr("x1", 0)
      .attr("x2", 120)
      .attr("y1", 0)
      .attr("y2", 0)
      .style("stroke", linecolor);

    // West - Midwest semifinal
    d3.select("#game62")
      .attr("transform", "translate(400, 530)")
      .append("line")
      .attr("x1", 0)
      .attr("x2", 120)
      .attr("y1", 0)
      .attr("y2", 0)
      .style("stroke", linecolor);

    // final
    d3.select("#game63")
      .attr("transform", "translate(400, 330)")
      .append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", 120)
      .attr("height", 40)
      .style("fill", "white")
      .style("stroke", linecolor);
  });
}

$(document).ready(function() {
  $("#randomize").click(randomize);
  $("#some").click();
  main();
});
