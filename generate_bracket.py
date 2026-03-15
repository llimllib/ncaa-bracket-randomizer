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
    "Miami (Ohio)": "Miami OH",
    "Prairie View": "Prairie View A&M",
}


def get_team(name, seed):
    lookup = name_map.get(name, name)
    b = barthag[lookup]
    eid = espn_ids[lookup]
    return {"name": name, "seed": seed, "barthag": round(b, 6), "espn_id": eid}


# Layout: East vs South on left, West vs Midwest on right
bracket = {
    "layout": {
        "topLeft": "east",
        "bottomLeft": "south",
        "topRight": "west",
        "bottomRight": "midwest",
    }
}

# --- East (left top) ---
bracket["east"] = {
    "1": get_team("Duke", 1),
    "16": get_team("Siena", 16),
    "8": get_team("Ohio St.", 8),
    "9": get_team("TCU", 9),
    "5": get_team("St. John's", 5),
    "12": get_team("N. Iowa", 12),
    "4": get_team("Kansas", 4),
    "13": get_team("Cal Baptist", 13),
    "6": get_team("Louisville", 6),
    "11": get_team("South Florida", 11),
    "3": get_team("Michigan St.", 3),
    "14": get_team("N. Dakota St.", 14),
    "7": get_team("UCLA", 7),
    "10": get_team("UCF", 10),
    "2": get_team("UConn", 2),
    "15": get_team("Furman", 15),
}

# --- South (left bottom) ---
# 16 seed play-in: Prairie View vs Lehigh
bracket["south"] = {
    "1": get_team("Florida", 1),
    "16": get_team("Lehigh", 16),  # Play-in: Prairie View vs Lehigh
    "8": get_team("Clemson", 8),
    "9": get_team("Iowa", 9),
    "5": get_team("Vanderbilt", 5),
    "12": get_team("McNeese", 12),
    "4": get_team("Nebraska", 4),
    "13": get_team("Troy", 13),
    "6": get_team("N. Carolina", 6),
    "11": get_team("VCU", 11),
    "3": get_team("Illinois", 3),
    "14": get_team("Penn", 14),
    "7": get_team("Saint Mary's", 7),
    "10": get_team("Texas A&M", 10),
    "2": get_team("Houston", 2),
    "15": get_team("Idaho", 15),
}

# --- West (right top) ---
# 11 seed play-in: Texas vs NC State
bracket["west"] = {
    "1": get_team("Arizona", 1),
    "16": get_team("LIU", 16),
    "8": get_team("Villanova", 8),
    "9": get_team("Utah St.", 9),
    "5": get_team("Wisconsin", 5),
    "12": get_team("High Point", 12),
    "4": get_team("Arkansas", 4),
    "13": get_team("Hawaii", 13),
    "6": get_team("BYU", 6),
    "11": get_team("NC State", 11),  # Play-in: Texas vs NC State
    "3": get_team("Gonzaga", 3),
    "14": get_team("Kennesaw St.", 14),
    "7": get_team("Miami", 7),
    "10": get_team("Missouri", 10),
    "2": get_team("Purdue", 2),
    "15": get_team("Queens", 15),
}

# --- Midwest (right bottom) ---
# 16 seed play-in: UMBC vs Howard
# 11 seed play-in: Miami (Ohio) vs SMU
bracket["midwest"] = {
    "1": get_team("Michigan", 1),
    "16": get_team("UMBC", 16),  # Play-in: UMBC vs Howard
    "8": get_team("Georgia", 8),
    "9": get_team("Saint Louis", 9),
    "5": get_team("Texas Tech", 5),
    "12": get_team("Akron", 12),
    "4": get_team("Alabama", 4),
    "13": get_team("Hofstra", 13),
    "6": get_team("Tennessee", 6),
    "11": get_team("SMU", 11),  # Play-in: Miami (Ohio) vs SMU
    "3": get_team("Virginia", 3),
    "14": get_team("Wright St.", 14),
    "7": get_team("Kentucky", 7),
    "10": get_team("Santa Clara", 10),
    "2": get_team("Iowa St.", 2),
    "15": get_team("Tennessee St.", 15),
}

with open("2026.bracket.json", "w") as f:
    json.dump(bracket, f, indent=2)
    f.write("\n")

print("Wrote 2026.bracket.json")
