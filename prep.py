# -*- coding: utf8 -*-

import csv
import json

combined = {}

kenpom = {}
with open("kenpom_2023.csv") as kp:
    rows = csv.reader(kp)
    header = next(rows)
    for row in rows:
        teamdata = dict(zip(header, row))
        kenpom[teamdata["TeamName"]] = {
            "name": teamdata["TeamName"],
            "rating": float(teamdata["AdjEM"]),
        }


def maketeam(name, seed):
    team = kenpom[name]
    team["seed"] = seed
    return team


bracket = json.loads(open("bracket.json").read())
for region, teams in bracket.items():
    combined[region] = {}
    for seed, team in teams.items():
        seed = int(seed)
        if isinstance(team, list):
            for t in team:
                assert t in kenpom, "{} not in kenpom".format(t)
            # for now, ignore the first four... pick the higher ranked team to win
            if kenpom[team[0]]["rating"] > kenpom[team[1]]["rating"]:
                combined[region][seed] = maketeam(team[0], seed)
            else:
                combined[region][seed] = maketeam(team[1], seed)
        else:
            assert team in kenpom, "{} not in kenpom".format(team)
            combined[region][seed] = maketeam(team, seed)

shortnames = {
    "Stephen F. Austin": "SF Austin",
    "Louisiana Lafayette": "Louisiana Laf.",
    "Western Michigan": "Western Mich.",
    "Eastern Kentucky": "Eastern Ky.",
    "Northern Kentucky": "Northern Ky.",
    "North Dakota St.": "ND State",
    "New Mexico St.": "NM State",
    "George Washington": "George Wash.",
    "Coastal Carolina": "Coast. Car.",
    "Eastern Washington": "E Washington",
    "UC Santa Barbara": "UCSB",
    "Texas A&M Corpus Christi": "Texas A&M CC",
}
for region in combined:
    for seed in combined[region]:
        if combined[region][seed]["name"] in shortnames:
            combined[region][seed]["name"] = shortnames[combined[region][seed]["name"]]

json.dump(combined, open("teams.json", "w"))
