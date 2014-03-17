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

combined = {}

bracket = json.loads(file("bracket.json").read())
for region, teams in bracket.iteritems():
    combined[region] = {}
    for seed, team in teams.iteritems():
        seed = int(seed)
        if isinstance(team, list):
            for t in team:
                assert t in kenpom
            # for now, ignore the first four... pick the higher ranked team to win
            if kenpom[team[0]]["rating"] > kenpom[team[1]]["rating"]:
                combined[region][seed] = kenpom[team[0]]
                combined[region][seed]["seed"] = seed
            else:
                combined[region][seed] = kenpom[team[1]]
                combined[region][seed]["seed"] = seed
        else:
            assert team in kenpom
            combined[region][seed] = kenpom[team]
            combined[region][seed]["seed"] = seed

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
