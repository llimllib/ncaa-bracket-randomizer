import re
from math import ceil, floor

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

    return dict((x[1], x) for x in kenpom)

def get_games():
    bracket = eval(file("2010teams.dat").read())

    kenpom = get_kenpom()

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
    for region in ("Midwest", "West", "East", "South"):
        merged[region] = {}
        for seed, teamname in bracket[region].items():
            if type(teamname) == type([]):
                t1, t2 = teamname 
                rank, name, record, pyth, adjo, adjorank, adjd, adjdrank = kenpom[t1]
                merged[region][16] = [name, pyth, adjo, adjd]
                rank, name, record, pyth, adjo, adjorank, adjd, adjdrank = kenpom[t2]
                merged[region][17] = [name, pyth, adjo, adjd]
            else:
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
        for seed in (1,8,5,4,6,3,7,2):
            oppseed = 17-seed
            t1 = merged[region][seed]
            t2 = merged[region][oppseed]
            games.append(Game(region, 1, game, seed, t1, oppseed, t2))
            game += 1
    return games

    rf1, rf2 = [g for g in games if g.round==4 and g.region in ("Midwest", "West")]
    rf3, rf4 = [g for g in games if g.round==4 and g.region in ("East", "South")]
    ff1 = Game("final four", 5, game)
    ff2 = Game("final four", 5, game+1)
    games.append(ff1)
    games.append(ff2)
    rf1.child = rf2.child = ff1
    rf3.child = rf4.child = ff2

    c = Game("final four", 6, game+2)
    games.append(c)
    ff1.child = ff2.child = c

    winner = Game("final four", 7, game+3)
    games.append(winner)
    c.child = winner
