#!/usr/bin/env python
import argparse
import csv
import os
from os import stat
import re
from time import time

from bs4 import BeautifulSoup
import requests


def one_hour_old(fname):
    """
    return True if the file given by fname is present or was modified more than
    an hour ago and False if it exists and was modified less than an hour ago
    """
    if not os.path.isfile(fname):
        return True
    return (time() - stat(fname).st_mtime) / (60 * 60) > 1


def save(url, fname):
    """save the contents of url to fname"""
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(res.text, url, fname)
    with open(fname, "w") as f:
        f.write(res.text)


def parse_kenpom_stats():
    soup = BeautifulSoup(open("kenpom.html"), "html.parser")
    table = soup.find("table", {"id": "ratings-table"})
    data = {}
    for trs in table.select("tr.tourney"):
        values = [x.text for x in trs.find_all("td")]
        if not values or not values[0].isdigit():
            continue
        # the only thing we use is the overall pythagorean rating
        data[re.sub(r"\s+\d+$", "", values[1])] = float(values[4])

    # now we need to normalize the AdjEM into a pythagorean rating. This is probably completely bogus to just normalize AdjEM, but whatevs it's all just a roll of the dice anyway
    minv = min(data.values())
    maxv = max(data.values())
    # increase the spread by 5%
    spread = (maxv - minv) * 1.05
    for team in data:
        #            make the value +
        data[team] = str((data[team] - minv) / spread)

    with open("kenpom_2023.csv", "w") as csvfile:
        csvw = csv.writer(csvfile)
        csvw.writerow(["TeamName", "Pythag"])
        csvw.writerows(data.items())


def main(args):
    if one_hour_old("kenpom.html"):
        print("downloading new data")
        save("https://kenpom.com", "kenpom.html")
    parse_kenpom_stats()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download kenpom data")
    args = parser.parse_args()
    main(args)
