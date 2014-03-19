import json, csv

kenpom = {}
with open("kenpom_2014.csv") as kp:
    rows = csv.reader(kp)
    header = rows.next()
    for row in rows:
        teamdata = dict(zip(header, row))
        kenpom[teamdata["TeamName"]] = {
            "name": teamdata["TeamName"],
            "rating": float(teamdata["Pythag"])
        }

kenpom_names = {
    "North Carolina St.": "NC State"
}

for name in kenpom:
    if name in kenpom_names:
        newname = kenpom_names[name]
        kenpom[newname] = kenpom[name]
        kenpom[newname]["name"] = newname
        del kenpom[name]

combined = {}

natesilver_names = {
    "Michigan State": "Michigan St.",
    "Wichita State": "Wichita St.",
    "Ohio State": "Ohio St.",
    "Iowa State": "Iowa St.",
    "Oklahoma State": "Oklahoma St.",
    "Virginia Commonwealth": "VCU",
    "San Diego State": "San Diego St.",
    "Arizona State": "Arizona St.",
    "Kansas State": "Kansas St.",
    "Saint Joseph's": "St. Joseph's",
    "Brigham Young": "BYU",
    "North Carolina State": "NC State",
    "Massachusetts": "UMass",
    "North Dakota State": "North Dakota St.",
    "New Mexico State": "New Mexico St.",
    "North Carolina Central": "NC Central",
    "Louisiana-Lafayette": "Louisiana Lafayette",
    "American University": "American",
    "Weber State": "Weber St.",
    "Massachusetts": "UMass",
    "North Carolina State": "NC State",
}

natesilver = {}
with open("natesilver.csv") as ns:
    rows = csv.reader(ns)
    header = rows.next()
    for row in rows:
        teamdata = dict(zip(header, row))
        teamdata["team"] = natesilver_names.get(teamdata["team"], teamdata["team"])
        if teamdata["team"] not in kenpom:
            print "missing {}".format(teamdata["team"])
        for key in ["round1", "round2", "round3", "round4", "round5", "round6"]:
            if teamdata[key] == "<.01":
                teamdata[key] = .001
            teamdata[key] = float(teamdata[key])
        natesilver[teamdata["team"]] = teamdata

def maketeam(name, seed):
    team = kenpom[name]
    team["seed"] = seed
    team["round1"] = natesilver[name]["round1"]
    team["round2"] = natesilver[name]["round2"]
    team["round3"] = natesilver[name]["round3"]
    team["round4"] = natesilver[name]["round4"]
    team["round5"] = natesilver[name]["round5"]
    team["round6"] = natesilver[name]["round6"]
    return team

bracket = json.loads(file("bracket.json").read())
for region, teams in bracket.iteritems():
    combined[region] = {}
    for seed, team in teams.iteritems():
        seed = int(seed)
        if isinstance(team, list):
            for t in team:
                assert t in kenpom and t in natesilver
            # for now, ignore the first four... pick the higher ranked team to win
            if kenpom[team[0]]["rating"] > kenpom[team[1]]["rating"]:
                combined[region][seed] = maketeam(team[0], seed)
            else:
                combined[region][seed] = maketeam(team[1], seed)
        else:
            assert team in kenpom and team in natesilver, "couldn't find team {}".format(team)
            combined[region][seed] = maketeam(team, seed)

shortnames = {
    "Stephen F. Austin": "SF Austin",
    "Louisiana Lafayette": "Louisiana Laf.",
    "Western Michigan": "Western Mich.",
    "Eastern Kentucky": "Eastern Ky.",
    "North Dakota St.": "ND State",
    "New Mexico St.": "NM State",
    "George Washington": "George Wash.",
    "Coastal Carolina": "Coast. Car.",
}
for region in combined:
    for seed in combined[region]:
        if combined[region][seed]["name"] in shortnames:
            combined[region][seed]["name"] = shortnames[combined[region][seed]["name"]]

json.dump(combined, open("teams.json", 'w'))
