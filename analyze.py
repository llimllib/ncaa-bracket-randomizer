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
        self.mutable = True 

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
          KenPomRandomModel(3), KenPomRandomModel(4), SeedModel(), PureRandomModel()]
#DEBUGGING TODO DELETEME
#models = [KenPomStrictModel()]
kenpom = get_kenpom()
games = get_games()

for round in actual_winners:
    for team in actual_winners[round]:
        assert any(True for t in kenpom if t.name==team)
        for game in (g for g in games if g.round==round):
            if game.team1 and game.team1.name == team:
                game.advance(game.team1)
                break
            elif game.team2 and game.team2.name == team:
                game.advance(game.team2)
                break

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
    possible = 0
    actual = 0
    eliminated = set([])

    for round in range(1,7):
        this_rounds_pts = 2**(round-1)
        for game in (g for g in games if g.round==round):
            #if the game has been played in real life, compare to reality
            if game.winner:
                if game.winner == game.predicted_winner:
                    #if the game was correctly predicted, add the points
                    possible += this_rounds_pts
                    actual += this_rounds_pts
                else:
                    #otherwise, the predicted team has been eliminated
                    eliminated.add(game.predicted_winner)
            else:
                if game.predicted_winner not in eliminated:
                    possible += this_rounds_pts

    return (actual, possible)

def test_models(n_reps):
    results = {}
    for model in models:
        repetitions = n_reps if model.mutable else 1
        ncorrect_bins = {}
        possible_point_bins = {}
        actual_point_bins = {}

        for i in range(repetitions):
            ncorrect = 0
            for round in range(1,7):
                for game in (g for g in games if g.round==round):
                    predicted = model(game)
                    game.advance_predicted(predicted)
                    if game.winner == predicted:
                            ncorrect += 1

            ncorrect_bins[ncorrect] = ncorrect_bins.setdefault(ncorrect, 0) + 1

            a, p = possible_points(games)
            possible_point_bins[p] = possible_point_bins.setdefault(p, 0) + 1
            actual_point_bins[a] = actual_point_bins.setdefault(a, 0) + 1

        if repetitions == 1 and n_reps > 1:
            ncorrect_bins[ncorrect_bins.keys()[0]] *= n_reps / 2
            possible_point_bins[possible_point_bins.keys()[0]] *= n_reps / 4
            actual_point_bins[actual_point_bins.keys()[0]] *= n_reps / 4

        ncorrect_list = sorted([[k,v] for k,v in ncorrect_bins.iteritems()])
        possible_list = sorted([[k,v] for k,v in possible_point_bins.iteritems()])
        actual_list = sorted([[k,v] for k,v in actual_point_bins.iteritems()])

        print "model %s avg: %s, distribution: %s" % (
            str(model), average(list(ncorrect_bins.iteritems())), ncorrect_list)

        results[str(model)] = (ncorrect_list, possible_list, actual_list)

    return results

#dump(test_models(10000), file("test_models.pkl", "w"))
results = load(file("test_models.pkl"))

out = file("analyze.html", "w")

ncorrect_data = []
possible_data = []
actual_data = []
for model, (ncorrect, possible, actual) in results.iteritems():
    if len(ncorrect) > 1:
        ncorrect_data.append("{label: '%(model)s', data: %(ncorrect)s}" % locals())
    else:
        #draw a line as a single point.
        k,v = ncorrect[0]
        ncorrect.append([k-.0001, 0])
        ncorrect_data.append("{label: '%(model)s', data: %(ncorrect)s}" % locals())

    if len(possible) > 1:
        possible_data.append("{label: '%(model)s', data: %(possible)s}" % locals())
    else:
        k,v = possible[0]
        possible.append([k-.0001, 0])
        possible_data.append("{label: '%(model)s', data: %(possible)s}" % locals())

    if len(actual) > 1:
        actual_data.append("{label: '%(model)s', data: %(actual)s}" % locals())
    else:
        k,v = actual[0]
        actual.append([k-.0001, 0])
        actual_data.append("{label: '%(model)s', data: %(actual)s}" % locals())

ncorrect_data = ",".join(sorted(ncorrect_data))
possible_data = ",".join(sorted(possible_data))
actual_data = ",".join(sorted(actual_data))

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
        yaxis: {max: 5000},
        series: {
            lines: { show: true },
        }}
    $.plot($("#ncorrect"), [%(ncorrect_data)s], options);
    $.plot($("#possible"), [%(possible_data)s], options);
    $.plot($("#actual"), [%(actual_data)s], options);
    options.xaxis = {min:75, max:150}
    options.yaxis = {max:1000}
    $.plot($("#possiblezoom"), [%(possible_data)s], options);
    options.xaxis = {min:158}
    options.yaxis = {max:10}
    $.plot($("#possiblezoom2"), [%(possible_data)s], options);
});
</script>
</head>
<body>
    <div id="ncorrect" style="width:600px;height:400px"></div> 
    <div id="possible" style="width:600px;height:400px"></div> 
    <div id="possiblezoom" style="width:600px;height:400px"></div> 
    <div id="possiblezoom2" style="width:600px;height:400px"></div> 
    <div id="actual" style="width:600px;height:400px"></div> 
</body>
</html>
""" % locals())

out.close()
