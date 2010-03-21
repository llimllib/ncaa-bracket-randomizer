import re
from math import ceil, floor

class Team(object):
    def __init__(self, name, pyth, adjo, adjd, seed=0):
        self.name = name
        self.pyth = pyth
        self.adjo = adjo
        self.adjd = adjd
        self.seed = seed

    def __repr__(self):
        if self.seed:
            return "%s) %s (%s, %s, %s)" % (
                self.seed, self.name, self.pyth, self.adjo, self.adjd)
        else:
            return "%s (%s, %s, %s)" % (
                self.name, self.pyth, self.adjo, self.adjd)

class Game(object):
    def __init__(self, region, round, gameno, team1=None, team2=None):
        self.region = region
        self.round = round
        self.gameno = gameno
        self.team1 = team1
        self.team2 = team2
        self.child = None
        #is this the upper game or the lower game? <bool>
        self.isupper = None
        self.rows = [None, None]

    def advance(self, team):
        assert team in (self.team1, self.team2)

        if self.isupper:
            self.child.team1 = team
        else:
            self.child.team2 = team

    def __repr__(self):
        return "%s vs %s round %s game %s region %s rows %s" % (self.team1[0],
            self.team2[0], self.round, self.gameno, self.region, self.rows)

def get_kenpom():
    """return a list of tuples:
    (rank, name, record, pythagorean score, adjusted O, adj O rank, adjusted D, adj D rank)"""

    teamre = '\s*(\d+) <a href="[^"]+">([^<]+)</a>\s*<a href=.*?</a></a>\s*(\d+-\d+)\s*(\.\d+)\s*([\d.]*)\/(\d+)\s*([\d.]*)\/(\d+)'

    kenpom = [x.groups() for x in [re.search(teamre, line) for line in file("pom2010.html")] if x]
    #convert strings to numbers where appropriate
    for i in range(len(kenpom)):
        team = list(kenpom[i])
        team[0] = int(team[0])
        for j in (3,4,5,6,7):
            team[j] = float(team[j])
        kenpom[i] = tuple(team)

    return [Team(team[1], team[3], team[4], team[6]) for team in kenpom]

def get_games():
    bracket = eval(file("2010teams.dat").read())

    kenpom = get_kenpom()

    #make sure we agree on all our team names
    for r in bracket:
        for t in bracket[r].values():
            if type(t) == type([]):
                for t2 in t:
                    assert any(True for team in kenpom if t2 == team.name)
            else:
                assert any(True for team in kenpom if t == team.name)

    #let's build a dictionary {"region" -> {seed -> [name, pyth, adjo, adjd]}}
    merged = {}
    for region in ("Midwest", "West", "East", "South"):
        merged[region] = {}
        for seed, teamname in bracket[region].items():
            if type(teamname) == type([]):
                t1, t2 = teamname 
                team = [t for t in kenpom if t.name == t1][0]
                team.seed = 16
                merged[region][16] = team
                team = [t for t in kenpom if t.name == t2][0]
                team.seed = 17
                merged[region][17] = team
            else:
                team = [t for t in kenpom if t.name == teamname][0]
                team.seed = seed
                merged[region][seed] = team

    games = []
    game = 1
    for region in merged:
        for seed in (1,8,5,4,6,3,7,2):
            oppseed = 17-seed
            t1 = merged[region][seed]
            t2 = merged[region][oppseed]
            games.append(Game(region, 1, game, t1, t2))
            game += 1

    for round in (2,3,4):
      i = iter(g for g in games if g.round==round-1)
      roundg = []
      for g in i:
        g2 = i.next()
        gg = Game(g.region, round, game)
        roundg.append(gg)
        g.child = g2.child = gg
        g.isupper = True
        g2.isupper = False
        game += 1
      games.extend(roundg)

    rf1, rf2 = [g for g in games if g.round==4 and g.region in ("Midwest", "West")]
    rf3, rf4 = [g for g in games if g.round==4 and g.region in ("East", "South")]
    ff1 = Game("final four", 5, game)
    ff2 = Game("final four", 5, game+1)
    games.append(ff1)
    games.append(ff2)
    rf1.child = rf2.child = ff1
    rf1.isupper = True
    rf2.isupper = False
    rf3.child = rf4.child = ff2
    rf3.isupper = True
    rf4.isupper = False

    c = Game("final four", 6, game+2)
    games.append(c)
    ff1.child = ff2.child = c
    ff1.isupper = True
    ff2.isupper = False

    winner = Game("final four", 7, game+3)
    games.append(winner)
    c.child = winner
    c.isupper = True

    return games
