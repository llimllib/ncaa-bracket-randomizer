from get_games import get_games, get_kenpom
from results import actual_winners
from random import Random
from copy import deepcopy

rand = Random().random

def log5(a, b):
    return (a - a * b) / (a + b - 2 * a * b)

def maxmin(a, b):
    if a > b: return (a,b)
    else:     return (b,a)

class KenPomStrictModel(object):
    def __init__(self):
        self.mutable = False

    def __call__(self, game):
        t1, t2 = game.team1, game.team2
        #compare pomeroy ratings and pick the higher one
        a, b, = t1[1], t2[1]
        if a > b:
            return t1
        return t2

    def __str__(self): return "Pomeroy Strict Model"

class KenPomRandomModel(object):
    def __init__(self, reps):
        self.mutable = True
        self.reps = reps

    def __call__(self, game):
        t1, t2 = game.team1, game.team2
        #compare pomeroy ratings and pick the higher one
        fav, dog = maxmin(t1[1], t2[1])
        pct = log5(fav, dog)
        for i in range(self.reps):
            if rand() < pct:
                return t1 if fav == t1[1] else t2
        return t1 if dog == t1[1] else t2

    def __str__(self): return "Pomeroy Random Model %s reps" % self.reps

class SeedModel(object):
    def __init__(self):
        self.mutable = False

    def __call__(self, game):
        t1, t2 = game.team1, game.team2
        if game.seed1 == game.seed2:
            return t1 if rand() < .5 else t2
        return t1 if game.seed1 < game.seed2 else t2

    def __str__(self): return "Seed Model"

class PureRandomModel(object):
    def __init__(self):
        self.mutable = True

    def __call__(self, game):
        t1, t2 = game.team1, game.team2
        return t1 if rand() < .5 else t2

    def __str__(self): return "Pure Random Model"

models = [KenPomStrictModel(), KenPomRandomModel(1), KenPomRandomModel(2),
          KenPomRandomModel(3), SeedModel(), PureRandomModel()]
kenpom = get_kenpom()
games = get_games()

for round in actual_winners:
    for team in actual_winners[round]:
        assert(team in kenpom)
        for game in (g for g in games if g.round==round):
            if game.team1[0] == team or game.team2[0] == team:
                game.winner = team

def average(a):
    """Average a list of tuples of the form (value, number of items with that value)"""
    sum = 0
    total = 0
    for v,n in a:
        sum += v*n 
        total += n
    return sum/float(total)

def possible_points(games):
    """how many points could still be scored?"""
    pass #TODO

for model in models:
    repetitions = 1000 if model.mutable else 1
    ncorrect_bins = {}
    possible_point_bins = {}

    for i in range(repetitions):
        ncorrect = 0
        for round in range(1,7):
            for game in (g for g in games if g.round==round):
                game.predicted = model(game)
                if game.winner and game.winner == game.predicted[0]:
                    ncorrect += 1

        if ncorrect not in ncorrect_bins:
            ncorrect_bins[ncorrect] = 1
        else:
            ncorrect_bins[ncorrect] += 1

        p = possible_points(games)
        if not p in possible_point_bins:
            possible_point_bins[p] = 1
        else:
            possible_point_bins[p] += 1


    print "model %s avg: %s, distribution: %s" % (str(model),
        average(list(ncorrect_bins.iteritems())),
        sorted([(k,v) for k,v in ncorrect_bins.iteritems()]))
