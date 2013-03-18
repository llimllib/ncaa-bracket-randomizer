from math import floor
from mako.template import Template

def output_bracket(kenpom_teams):
    bkt = eval(file("teams.dat").read())

    # 17 columns = len(round 0,space,1,2,3,4,5,6,7,6,5,4,3,2,1,space,0)
    # 47 rows = 1 for every team per side + 15 spacers
    table = [['<td></td>']*17 for _ in range(47)]

    game_order = [1,8,5,4,6,3,7,2]

    #this year the west plays the east and the southwest plays the southeast.
    divs = ["Midwest", "West", "South", "East"]

    #the kenpom stats for the teams that are in the tournament. The key is the
    #team id, and the value is the team's stats and name
    kenpom_keep = {}

    tid = 1
    teams = {}
    for div in divs:
        for game in game_order:
            pro = bkt[div][game]
            opp = bkt[div][17-game]

            #assert that the names in teams.dat match up with kenpom's names
            assert pro in kenpom_teams, pro
            if isinstance(opp, list):
                a,b = opp
                assert a in kenpom_teams, a
                assert b in kenpom_teams, b
            else:
                assert opp in kenpom_teams, opp

            #add each team to the teams and kenpom_keep dictionaries
            if isinstance(opp, list):
                teams[tid] = pro
                kenpom_keep[tid] = kenpom_teams[pro]
                tid += 1
                teams[tid] = opp[0]
                kenpom_keep[tid] = kenpom_teams[opp[0]]
                tid += 1
                teams[tid] = opp[1]
                kenpom_keep[tid] = kenpom_teams[opp[1]]
                tid += 1
            else:
                teams[tid] = bkt[div][game]
                kenpom_keep[tid] = kenpom_teams[pro]
                tid += 1
                teams[tid] = bkt[div][17-game]
                kenpom_keep[tid] = kenpom_teams[opp]
                tid += 1

    display_names = {
        "North Carolina St.": "NC State",
        "Nevada Las Vegas": "UNLV",
        "Brigham Young": "BYU",
        "Virginia Commonwealth": "VCU",
        "South Florida": "USF",
        "Miami FL": "Miami",
    }

    for tid, team in teams.iteritems():
        if team in display_names:
            teams[tid] = display_names[team]
            kenpom_keep[tid][8] = display_names[team]

    spacers = []

    #qualifiers
    table[1][0] = '<td round=0 game=2 upper="" side="left"><a team=2 href="#1-1-l">%s</a></td>' % teams[2]
    table[2][0] = '<td round=0 game=2 side="left"></td>'
    table[3][0] = '<td round=0 game=2 lower="" side="left"><a team=3 href="#1-1-l">%s</a></td>' % teams[3]
    table[1][1] = '<td bottom=""></td>'

    table[13][0] = '<td round=0 game=1 upper="" side="left"><a team=11 href="#1-5-l">%s</a></td>' % teams[11]
    table[14][0] = '<td round=0 game=1 side="left"></td>'
    table[15][0] = '<td round=0 game=1 lower="" side="left"><a team=12 href="#1-5-l">%s</a></td>' % teams[12]
    table[13][1] = '<td bottom=""></td>'

    table[34][0] = '<td round=0 game=4 upper="" side="left"><a team=26 href="#1-12-l">%s</a></td>' % teams[26]
    table[35][0] = '<td round=0 game=4 side="left"></td>'
    table[36][0] = '<td round=0 game=4 lower="" side="left"><a team=27 href="#1-12-l">%s</a></td>' % teams[27]
    table[34][1] = '<td bottom=""></td>'

    table[25][-1] = '<td round=0 game=3 upper="" side="right"><a team=53 href="#1-25-l">%s</a></td>' % teams[53]
    table[26][-1] = '<td round=0 game=3 side="right"></td>'
    table[27][-1] = '<td round=0 game=3 lower="" side="right"><a team=54 href="#1-25-l">%s</a></td>' % teams[54]
    table[25][-2] = '<td bottom=""></td>'

    games = {
        1: 1, 2: [4,5], 3: [6,7], 4: [8,9], 5: 10, 6: [13,14], 7: [15,16], 8: [17,18],
        9: [19,20], 10: [21,22], 11: [23,24], 12: 25, 13: [28,29], 14: [30,31], 15: [32,33], 16: [34,35],
        17: [36,37], 18: [38,39], 19: [40,41], 20: [42,43], 21: [44, 45], 22: [46,47], 23: [48,49], 24: [50,51],
        25: 52, 26: [55, 56], 27: [57, 58], 28: [59,60], 29: [61,62], 30: [63,64], 31: [65,66], 32: [67,68]
    }

    #round one
    for game in range(1,33):
        nextroundgame = int(floor((game/2.)+.5))
        nextup = "u" if game%2==1 else "l"
        side = "left" if game < 17 else "right"

        col = 2 if game < 17 else -3
        row = ((game-1)%16) * 3

        spacers.append(row+2)

        seed = [1,8,5,4,6,3,7,2][(game-1)%8]

        opponents = games[game]
        if isinstance(opponents, list):
            tid = opponents[0]
            table[row][col] = '<td round=1 game=%s upper="" side="%s"><a team=%s href="#2-%s-%s">%s. %s</a></td>' % (game, side, tid, nextroundgame, nextup, seed, teams[tid])
            table[row+1][col] = '<td round=1 game=%s lower="" side="%s"><a team=%s href="#2-%s-%s">%s. %s</a></td>' % (game, side, tid+1, nextroundgame, nextup, 17-seed, teams[tid+1])
        else:
            tid = opponents
            table[row][col] = '<td round=1 game=%s upper="" side="%s"><a team=%s href="#2-%s-%s">%s. %s</a></td>' % (game, side, tid, nextroundgame, nextup, seed, teams[tid])
            table[row+1][col] = '<td round=1 game=%s lower="" side="%s">%s. &nbsp;</td>' % (game, side, 17-seed)

    for game in range(1, 17):
        side = "left" if game < 9 else "right"

        col = 3 if game < 9 else -4
        row = ((game-1) % 8)*6

        table[row][col] = '<td round=2 game=%s upper="" side="%s"></td>' % (game, side)
        for i in range(1, 3):
            table[row+i][col] = '<td round=2 game=%s side="%s"></td>' % (game, side)
        table[row+3][col] = '<td round=2 game=%s lower="" side="%s"></td>' % (game, side)

    for game in range(1, 9):
        side = "left" if game < 5 else "right"

        col = 4 if game < 5 else -5
        row = ((game-1) % 4)*12+1

        table[row][col] = '<td round=3 game=%s upper="" side="%s"></td>' % (game, side)
        for i in range(1,6):
            table[row+i][col] = '<td round=3 game=%s side="%s"></td>' % (game, side)
        table[row+6][col] = '<td round=3 game=%s lower="" side="%s"></td>' % (game, side)

    for game in range(1, 5):
        side = "left" if game < 3 else "right"

        col = 5 if game < 3 else -6
        row = ((game-1) % 2)*24+4

        table[row][col] = '<td round=4 game=%s upper="" side="%s"></td>' % (game, side)
        for i in range(1,14):
            table[row+i][col] = '<td round=4 game=%s side="%s"></td>' % (game, side)
        table[row+14][col] = '<td round=4 game=%s lower="" side="%s"></td>' % (game, side)

    for game in range(1, 3):
        side = "left" if game == 1 else "right"

        col = 6 if game == 1 else -7
        row = 9

        table[row][col] = '<td round=5 game=%s upper="" side="%s"></td>' % (game, side)
        for i in range(1,25):
            table[row+i][col] = '<td round=5 game=%s side="%s"></td>' % (game, side)
        table[row+25][col] = '<td round=5 game=%s lower="" side="%s"></td>' % (game, side)

    table[16][7]  = '<td round=6 game=1 upper="" side="left"></td>'
    table[27][-8] = '<td round=6 game=1 lower="" side="right"></td>'

    table[22][8] = '<td round=7 game=1 upper="" lower="" side="left"></td>'

    file("index.html", 'w').write(Template(filename="bracket_template.html")
                         .render(table=table, spacers=spacers, kenpom=kenpom_keep))

def read_kenpom():
    #kenpom data notes:
    #team, raw tempo, raw tempo rank, adj tempo, adj tempo rank, raw OE, raw OE rank, adj OE, adj OE rank, raw DE, raw DE rank, adj DE, adjDE rank, kenpom ranking, kenpom rank
    teams = {}
    for line in file("kenpom_2013.csv"):
        kenpomrank, team, _, _, kenpom, oe, oerank, de, derank, tempo, temporank = line.strip().split(",")[:11]
        teams[team] = map(float, [tempo, temporank, oe, oerank, de, derank, kenpom, kenpomrank]) + [team]
    return teams

if __name__=="__main__":
    teams = read_kenpom()
    output_bracket(teams)
