from get_games import get_games, get_kenpom
from results import actual_winners
from random import Random
from copy import deepcopy
from cPickle import load, dump

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
        a, b = t1.pyth, t2.pyth
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
        fav, dog = maxmin(t1.pyth, t2.pyth)
        pct = log5(fav, dog)
        for i in range(self.reps):
            if rand() < pct:
                return t1 if fav == t1.pyth else t2
        return t1 if dog == t1.pyth else t2

    def __str__(self): return "Pomeroy Random Model %s reps" % self.reps

class SeedModel(object):
    def __init__(self):
        self.mutable = False

    def __call__(self, game):
        t1, t2 = game.team1, game.team2
        if t1.seed == t2.seed:
            return t1 if rand() < .5 else t2
        return t1 if t1.seed < t2.seed else t2

    def __str__(self): return "Seed Model"

class PureRandomModel(object):
    def __init__(self):
        self.mutable = True

    def __call__(self, game):
        return game.team1 if rand() < .5 else game.team2

    def __str__(self): return "Pure Random Model"

models = [KenPomStrictModel(), KenPomRandomModel(1), KenPomRandomModel(2),
          KenPomRandomModel(3), SeedModel(), PureRandomModel()]
#DEBUGGING TODO DELETEME
#models = [KenPomStrictModel()]
kenpom = get_kenpom()
games = get_games()

for round in actual_winners:
    for team in actual_winners[round]:
        assert any(True for t in kenpom if t.name==team)
        for game in (g for g in games if g.round==round):
            if game.team1.name == team:   game.winner = game.team1; break
            elif game.team2.name == team: game.winner = game.team2; break

def average(a):
    """Average a list of tuples of the form (value, number of items with that value)"""
    sum = 0
    total = 0
    for v,n in a:
        sum += v*n 
        total += n
    return sum/float(total)

def possible_points(games):
    """points scored + how many points could still be scored?"""
    p = 0
    eliminated = set([])
    for round in range(1,7):
        this_rounds_pts = 2**(round-1)
        for game in (g for g in games if g.round==round):
            if hasattr(game, 'winner'):
                if game.winner == game.predicted:
                    #if the game was correctly predicted, add the points
                    p += this_rounds_pts
                else:
                    #otherwise, the predicted team has been eliminated
                    eliminated.add(game.predicted)
            else:
                if game.predicted not in eliminated:
                    p += this_rounds_pts
    return p

def test_models(n_reps):
    results = {}
    for model in models:
        repetitions = n_reps if model.mutable else 1
        ncorrect_bins = {}
        possible_point_bins = {}

        for i in range(repetitions):
            ncorrect = 0
            for round in range(1,7):
                for game in (g for g in games if g.round==round):
                    game.predicted = model(game)
                    game.advance(game.predicted)
                    if hasattr(game, 'winner') and game.winner == game.predicted:
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

        if repetitions == 1:
            ncorrect_bins[ncorrect_bins.keys()[0]] *= n_reps / 2
            possible_point_bins[possible_point_bins.keys()[0]] *= n_reps / 4

        ncorrect_list = sorted([[k,v] for k,v in ncorrect_bins.iteritems()])
        possible_list = sorted([[k,v] for k,v in possible_point_bins.iteritems()])

        print "model %s avg: %s, distribution: %s" % (
            str(model), average(list(ncorrect_bins.iteritems())), ncorrect_list)

        results[str(model)] = (ncorrect_list, possible_list)

    return results

#dump(test_models(10000), file("test_models.pkl", "w"))
results = load(file("test_models.pkl"))

out = file("analyze.html", "w")

ncorrect_data = []
possible_data = []
for model, (ncorrect, possible) in results.iteritems():
    if len(ncorrect) > 1:
        ncorrect_data.append("{label: '%(model)s', data: %(ncorrect)s}" % locals())
        possible_data.append("{label: '%(model)s', data: %(possible)s}" % locals())
    else:
        #this makes it so that a line will be drawn to the single point.
        k,v = ncorrect[0]
        ncorrect.append([k-.0001, 0])
        k,v = possible[0]
        possible.append([k-.0001, 0])

        ncorrect_data.append("{label: '%(model)s', data: %(ncorrect)s}" % locals())
        possible_data.append("{label: '%(model)s', data: %(possible)s}" % locals())
ncorrect_data = ",".join(ncorrect_data)
possible_data = ",".join(possible_data)

out.write("""
<html><head><title>Analyze</title>
<script language="javascript" type="text/javascript" src="flot/jquery.js"></script> 
<script language="javascript" type="text/javascript" src="flot/jquery.flot.js"></script> 
<script>
function log10 (arg) {
    return Math.log(arg)/Math.LN10;
}

$(function () {
    var options = {
        legend: {position: 'nw'},
        /*yaxis: {
            transform: function (v) { return log10(v); },
            inverseTransform: function (v) { return Math.pow(10, v); }
        },*/
        series: {
            lines: { show: true },
        }}
    $.plot($("#ncorrect"), [%(ncorrect_data)s], options);
    $.plot($("#possible"), [%(possible_data)s], options);
    options.xaxis = {min:100, max:200}
    $.plot($("#possiblezoom"), [%(possible_data)s], options);
});
</script>
</head>
<body>
    <div id="ncorrect" style="width:600px;height:400px"></div> 
    <div id="possible" style="width:600px;height:400px"></div> 
    <div id="possiblezoom" style="width:600px;height:400px"></div> 
</body>
</html>
""" % locals())

out.close()
