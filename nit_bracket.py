import re
from math import ceil, floor

bracket = eval(file("nit.dat").read())

teamre = '\s*(\d+) <a href="[^"]+">([^<]+)</a>\s*<a href=.*?</a></a>\s*(\d+-\d+)\s*(\.\d+)\s*([\d.]*)\/(\d+)\s*([\d.]*)\/(\d+)'
kenpom = [x.groups() for x in [re.search(teamre, line) for line in file("pom2010.html")] if x]
#kenpom is a list of tuples:
#(rank, name, record, pythagorean score, adjusted O, adj O rank, adjusted D, adj D rank)
kenpom = dict((x[1], x) for x in kenpom)

#make sure we agree on all our team names
for r in bracket:
  for t in bracket[r].values():
    if type(t) == type([]):
      for t2 in t:
        assert(t2 in kenpom)
    else:
      assert(t in kenpom)

#let's build a dictionary {"region" -> {seed -> [name, pyth, adjo, adjd]}}
merged = {}
for region in ("a", "b", "c", "d"):
  merged[region] = {}
  for seed, teamname in bracket[region].items():
      rank, name, record, pyth, adjo, adjorank, adjd, adjdrank = kenpom[teamname]
      merged[region][seed] = [name, pyth, adjo, adjd]

class Game(object):
  def __init__(self, region, round, gameno, seed1=None, team1=None, seed2=None, team2=None):
    self.region = region
    self.round = round
    self.gameno = gameno
    self.seed1 = seed1 or ""
    self.team1 = team1 or [""]
    self.seed2 = seed2 or ""
    self.team2 = team2 or [""]
    self.child = None
    self.rows = [None, None]

  def __repr__(self):
    return "%s vs %s round %s game %s region %s rows %s" % (self.team1[0],
      self.team2[0], self.round, self.gameno, self.region, self.rows)

games = []
game = 1
for region in merged:
  for seed in (1,4,3,2):
    oppseed = 9-seed
    t1 = merged[region][seed]
    t2 = merged[region][oppseed]
    games.append(Game(region, 1, game, seed, t1, oppseed, t2))
    game += 1

for round in (2,3):
  i = iter(g for g in games if g.round==round-1)
  roundg = []
  for g in i:
    g2 = i.next()
    gg = Game(g.region, round, game)
    roundg.append(gg)
    g.child = g2.child = gg
    game += 1
  games.extend(roundg)

rf1, rf2 = [g for g in games if g.round==3 and g.region in ("a", "b")]
rf3, rf4 = [g for g in games if g.round==3 and g.region in ("c", "d")]
ff1 = Game("final four", 4, game)
ff2 = Game("final four", 4, game+1)
games.append(ff1)
games.append(ff2)
rf1.child = rf2.child = ff1
rf3.child = rf4.child = ff2

c = Game("final four", 5, game+2)
games.append(c)
ff1.child = ff2.child = c

winner = Game("final four", 6, game+3)
games.append(winner)
c.child = winner

class Table(object):
  def __init__(self):
    self.data = [[]]

  def __getitem__(self, (x,y)):
    return self.data[y][x]

  def __setitem__(self, (x,y), val):
    try:
      self.data[y][x] = val
    except IndexError:
      self.resize(x, y)
      self.data[y][x] = val
    except:
      print y, x
      raise

  #we're fine with *horrible* efficiency in this particular app
  def resize(self, x, y):
    for i in range(y - len(self.data) + 1):
      self.data.append([])
    for row in self.data:
      for i in range(x - len(row) + 1):
        row.append(None)

  def __repr__(self):
    return self.data.__repr__()

  def tableize(self):
    o = []
    for y, row in enumerate(self.data):
      o.append("<tr>")
      for x, elt in enumerate(row):
        if x == 0:
          #TODO: 16v17
          pass
        elif not elt: o.append('<td class="none"></td>')
        elif elt.rows[0] == y: 
          if x == 1:
            o.append('''<td class="top" width="200">%s. <span class="round-%s game-%s"
                            >%s (%s, %s, %s)</span></td>''' % (
              elt.seed1, elt.round, elt.gameno, elt.team1[0], elt.team1[1],
              elt.team1[2], elt.team1[3]))
          else:
            o.append('''<td class="top" width="180">&nbsp;<span
                            class="round-%s game-%s"></span>''' % (
              elt.round, elt.gameno))
        elif elt.rows[1] == y:
          if x in (0,1):
            o.append('''<td class="bottom">%s. <span class="round-%s game-%s"
                            >%s (%s, %s, %s)</span></td>''' % (
              elt.seed2, elt.round, elt.gameno, elt.team2[0], elt.team2[1],
              elt.team2[2], elt.team2[3]))
          else:
            o.append('''<td class="bottom">&nbsp;<span class="round-%s game-%s"></span>''' % (
              elt.round, elt.gameno))
        else:
          o.append('<td class="middle">&nbsp;</td>')
    return '\n'.join(o)
    
t = Table()

#insert the games into the table in the proper spot
row = 0
for region in ("a", "b", "c", "d"):
  for g in [x for x in games if x.round==1 and x.region==region]:
    g.rows = [row, row+2]
    t[1, row] = g
    t[1, row+1] = g
    t[1, row+2] = g
    g.child.rows[1 if g.child.rows[0] else 0] = row+1
    row += 3

  for round in (2,3):
    for g in [x for x in games if x.round==round and x.region==region]:
      miny, maxy = g.rows
      for i in range(0, maxy - miny + 1):
        t[round, miny + i] = g
        g.child.rows[1 if g.child.rows[0] else 0] = miny + int(ceil(float(maxy-miny)/2))

ff1.rows = [6, 18]
for i in range(6,19): t[4, i] = ff1
ff2.rows = [30, 42]
for i in range(30,43): t[4, i] = ff2
c.rows = [13, 36]
for i in range(13,37): t[5, i] = c
winner.rows = [23, 24]
t[6, 23] = winner

out = file("nit.html", "w")
#TODO: if you change a team in an early game, update later games
#TODO: color teams based on pythagorean diff
#TODO: better randomizer
out.write("""
<html><head><title>Bill Mill Bracket Randomizer</title>
<script src="js/jquery-1.3.2.min.js" type="text/javascript"></script>
<link type="text/css" href="css/ui-lightness/jquery-ui-1.7.2.custom.css" rel="stylesheet" />    
<script type="text/javascript" src="js/jquery-ui-1.7.2.custom.min.js"></script>

<script>
rounds = {0:0, 1: 16, 2: 24, 3: 28, 4:30, 5:31};

function handleClick(that) {
  var atts = that.attr("class");
  var game = parseFloat(atts.match(/game-(\d+)/)[1]);
  var round = parseFloat(atts.match(/round-(\d+)/)[1]);
  var game_parity = (game - rounds[round-1]) % 2 == 0 ? 1 : 0;
  if (round < 3) {
    var nextgame = (Math.ceil((game-rounds[round-1])/2) + rounds[round]).toString();
    var firstorlast = game_parity ? ":last" : ":first";
  }
  else {
    if (game == 25 || game == 27) {
      var nextgame = 29;
      var firstorlast = game == 25 ? ":first" : ":last";
    }
    else if (game==26 || game==28) {
      var nextgame = 30;
      var firstorlast = game == 26 ? ":first" : ":last";
    }
    else if (game == 29 || game == 30) {
      var nextgame = 31;
      var firstorlast = game == 29 ? ":first" : ":last";
    }
    else if (game == 31) {
      var nextgame = 32;
      var firstorlast = ":first";
    }
  }
  that.click(function() {
    //console.log("game, round, nextgame, (g-r[r-1]) ", game, round, nextgame, game - rounds[round-1], firstorlast);
    $(".game-" + nextgame + firstorlast).html(that.html());
  });
}

function randomize() {
  for (i=0; i < 6; i++) {
    $("td.top > span.round-" + i).each(function(_) {
      var that = $(this);
      var atts = that.attr("class");
      var game = atts.match(/game-\d+/)[0];
      var opp = $("." + game + ":last");
      function parsepoints(obj) {
        console.log(obj);
        p = obj.html().match(/(.*?) \((.\d+), (\d+\.\d+), (\d+\.\d+)/);
        return [p[1], parseFloat(p[2]), parseFloat(p[3]), parseFloat(p[4])]
      }
      var topp = parsepoints(that);
      var oppp = parsepoints(opp);

      var favorite = topp[1] > oppp[1] ? that : opp;
      var underdog = topp[1] < oppp[1] ? that : opp;

      var a = parsepoints(favorite)[1];
      var b = parsepoints(underdog)[1];

      //use the log5 formula
      var log5 = (a - a * b) / (a + b - 2 * a * b);

      var pct = (log5 - .5) * 2;
      var green = "#00" + parseInt(255 * pct).toString(16) + "00";
      var red = "#" + parseInt(255 * pct).toString(16) + "0000";
      favorite.css("color", green);
      underdog.css("color", red);

      //console.log(topp[0] + " vs " + oppp[0] + " %: ", log5);
      
      if (amount_of_randomness == 0) {
        favorite.click();
      }
      else {
        for (j=0; j < (4-amount_of_randomness); j++) {
          fav_wins = false;
          if (log5 > Math.random()) {
            favorite.click();
            fav_wins = true;
            break;
          }
        }
        if (!fav_wins) {
          underdog.click();
        }
      }
    });
  }
}

$(document).ready(function() {
  for (i=0; i < 8; i++) {
    $(".round-" + i).each(function(i) { handleClick($(this)); });
  }
  $("td.top > span.round-1").each(function(i) { $(this).parent().css("height", "30px").css("vertical-align", "bottom"); })
  $("#randomize").click(function() { randomize(); });

  amount_of_randomness = 3;

  // Slider
  $('#slider').slider({
    min: 0,
    max: 3,
    step: 1,
    value: amount_of_randomness,
    slide: function(event, ui) {
      amount_of_randomness = parseInt(ui.value);
      //console.log("amount of randomness:", amount_of_randomness, ui);
      var labels = ["None", "Almost None", "Some", "Lots"];
      $("#desc").html(labels[amount_of_randomness])
    }
  });
});
</script>
<style>
.top {  border-bottom: 1px solid #aaaaaa; padding: 0px 5px 0px 5px; }
.bottom { border-bottom: 1px solid #aaaaaa; border-right: 1px solid #aaaaaa; padding: 0px 5px 0px 5px; }
.middle { border-right: 1px solid #aaaaaa; padding: 0px 5px 0px 5px; }
tr { padding-bottom: 10px; font-size: 12px; }
span { cursor: pointer; }
#slider { width: 200px; }
body { font: 16px serif; }
/* fix the jquery UI text size changing */
#text { font: 16px serif; padding-right: 20px;}
#desc { margin-left: 20px; }
</style>
</head>
<body>
<p>Go Uconn!.
<p><table><tr><td id="text">Randomness:</td><td><div id="slider"></div></td><td id="text"><span id="desc">Lots</span></td></tr></table>
<p><input type="submit" id="randomize" value="randomize"><table cellspacing=0 width=1200 style='table-layout:fixed'>
""")
out.write(t.tableize())
out.write("</table></body></html>")
out.close()
