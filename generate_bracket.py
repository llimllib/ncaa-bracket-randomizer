#!/usr/bin/env python3
"""Generate bracket JSON from bracket prediction text, Torvik CSV, and ESPN IDs."""

import csv
import json

# Load barthag data
barthag = {}
with open("2026_team_results.csv") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        team = row[1]
        b = float(row[8])
        barthag[team] = b

# Load ESPN IDs
with open("espn_ids.json") as f:
    espn_ids = json.load(f)

# Name mappings: bracket name -> torvik/ESPN name
name_map = {
    "UConn": "Connecticut",
    "N. Iowa": "Northern Iowa",
    "McNeese": "McNeese St.",
    "N. Dakota St.": "North Dakota St.",
    "NC State": "N.C. State",
    "N. Carolina": "North Carolina",
    "Miami": "Miami FL",
    "Miami (OH)": "Miami OH",
    "Prairie View": "Prairie View A&M",
}


def get_team(name, seed):
    lookup = name_map.get(name, name)
    b = barthag[lookup]
    eid = espn_ids[lookup]
    return {"name": name, "seed": seed, "barthag": round(b, 6), "espn_id": eid}


# Layout: East plays Midwest in FF, South plays West in FF
# East & Midwest on the left side, South & West on the right side
bracket = {
    "layout": {
        "topLeft": "east",
        "bottomLeft": "midwest",
        "topRight": "south",
        "bottomRight": "west",
    }
}

# --- East ---
east = {
    "1": get_team("Duke", 1),
    "16": get_team("Furman", 16),
    "8": get_team("Georgia", 8),
    "9": get_team("Villanova", 9),
    "5": get_team("St. John's", 5),
    "12": get_team("Penn", 12),
    "4": get_team("Kansas", 4),
    "13": get_team("High Point", 13),
    "6": get_team("Tennessee", 6),
    "11": get_team("Santa Clara", 11),  # Play-in: Santa Clara vs SMU
    "3": get_team("Michigan St.", 3),
    "14": get_team("N. Dakota St.", 14),
    "7": get_team("Miami", 7),
    "10": get_team("UCF", 10),
    "2": get_team("UConn", 2),
    "15": get_team("Kennesaw St.", 15),
}
bracket["east"] = east

# --- Midwest ---
# 16 seed play-in: LIU vs Howard (placeholder: LIU)
# 11 seed play-in: Miami (OH) vs Missouri (placeholder: Miami OH)
midwest = {
    "1": get_team("Michigan", 1),
    "16": get_team("LIU", 16),  # Play-in: LIU vs Howard
    "8": get_team("Utah St.", 8),
    "9": get_team("Iowa", 9),
    "5": get_team("Arkansas", 5),
    "12": get_team("N. Iowa", 12),
    "4": get_team("Nebraska", 4),
    "13": get_team("Hofstra", 13),
    "6": get_team("Louisville", 6),
    "11": get_team("Miami (OH)", 11),  # Play-in: Miami (OH) vs Missouri
    "3": get_team("Iowa St.", 3),
    "14": get_team("Wright St.", 14),
    "7": get_team("UCLA", 7),
    "10": get_team("Texas", 10),
    "2": get_team("Vanderbilt", 2),
    "15": get_team("Tennessee St.", 15),
}
bracket["midwest"] = midwest

# --- South ---
# 16 seed play-in: Lehigh vs Prairie View (placeholder: Lehigh)
south = {
    "1": get_team("Florida", 1),
    "16": get_team("Lehigh", 16),  # Play-in: Lehigh vs Prairie View
    "8": get_team("Ohio St.", 8),
    "9": get_team("NC State", 9),
    "5": get_team("Texas Tech", 5),
    "12": get_team("McNeese", 12),
    "4": get_team("Gonzaga", 4),
    "13": get_team("Hawaii", 13),
    "6": get_team("N. Carolina", 6),
    "11": get_team("VCU", 11),
    "3": get_team("Illinois", 3),
    "14": get_team("Troy", 14),
    "7": get_team("Saint Mary's", 7),
    "10": get_team("Texas A&M", 10),
    "2": get_team("Houston", 2),
    "15": get_team("Siena", 15),
}
bracket["south"] = south

# --- West ---
west = {
    "1": get_team("Arizona", 1),
    "16": get_team("UMBC", 16),
    "8": get_team("Clemson", 8),
    "9": get_team("TCU", 9),
    "5": get_team("Wisconsin", 5),
    "12": get_team("Akron", 12),
    "4": get_team("Alabama", 4),
    "13": get_team("Cal Baptist", 13),
    "6": get_team("BYU", 6),
    "11": get_team("South Florida", 11),
    "3": get_team("Virginia", 3),
    "14": get_team("Idaho", 14),
    "7": get_team("Kentucky", 7),
    "10": get_team("Saint Louis", 10),
    "2": get_team("Purdue", 2),
    "15": get_team("Queens", 15),
}
bracket["west"] = west

with open("2026.bracket.json", "w") as f:
    json.dump(bracket, f, indent=2)
    f.write("\n")

print("Wrote 2026.bracket.json")
