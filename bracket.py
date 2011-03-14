from math import floor
from mako.template import Template

def output_bracket(kenpom_teams):
    bkt = eval(file("teams.dat").read())

    # 13 columns = len(round 0,1,2,3,4,5,6,7,6,5,4,3,2,1,0)
    # 47 rows = 1 for every team per side + 15 spacers
    table = [['<td></td>']*17 for _ in range(47)]

    #this year the west plays the southeast and the southwest plays the east.
    game_order = [1,8,5,4,6,3,7,2,-1]
    divs = ["West", "Southeast", "Southwest", "East"]
    tid = 1
    qtid = -1
    teams = {}
    for div in divs:
        #a play-in game, if it exists
        pair = None

        for game in game_order:
            if game > 0:
                pro = bkt[div][game]
                opp = bkt[div][16-game]

                assert pro in kenpom_teams, pro
                if isinstance(opp, list):
                    a,b = opp
                    assert a in kenpom_teams, a
                    assert b in kenpom_teams, b
                else:
                    assert opp in kenpom_teams, opp

                if isinstance(opp, list):
                    teams[tid] = pro
                    pair = opp
                    tid += 2
                else:
                    teams[tid] = bkt[div][game]
                    tid += 1
                    teams[tid] = bkt[div][17-game]
                    tid += 1
            elif pair:
                qa, qb = pair

                teams[tid] = qa
                tid += 1
                teams[tid] = qb
                tid += 1

    spacers = []

    #qualifiers
    table[1][0] = '<td round=0 game=1 upper="" side="left"><a team=17 href="#1-1-l">%s</a></td>' % teams[17]
    table[2][0] = '<td round=0 game=1 side="left"></td>'
    table[3][0] = '<td round=0 game=1 lower="" side="left"><a team=18 href="#1-1-l">%s</a></td>' % teams[18]
    table[1][1] = '<td bottom=""></td>'

    table[25][0] = '<td round=0 game=2 upper="" side="left"><a team=17 href="#1-9-l">%s</a></td>' % teams[35]
    table[26][0] = '<td round=0 game=2 side="left"></td>'
    table[27][0] = '<td round=0 game=2 lower="" side="left"><a team=18 href="#1-9-l">%s</a></td>' % teams[36]
    table[25][1] = '<td bottom=""></td>'

    table[1][-1] = '<td round=0 game=3 upper="" side="right"><a team=17 href="#1-17-l">%s</a></td>' % teams[17]
    table[2][-1] = '<td round=0 game=3 side="right"></td>'
    table[3][-1] = '<td round=0 game=3 lower="" side="right"><a team=18 href="#1-17-l">%s</a></td>' % teams[18]
    table[1][-2] = '<td bottom=""></td>'

    table[25][-1] = '<td round=0 game=4 upper="" side="right"><a team=17 href="#1-25-l">%s</a></td>' % teams[35]
    table[26][-1] = '<td round=0 game=4 side="right"></td>'
    table[27][-1] = '<td round=0 game=4 lower="" side="right"><a team=18 href="#1-25-l">%s</a></td>' % teams[36]
    table[25][-2] = '<td bottom=""></td>'

    #round one
    for game in range(1,33):
        nextroundgame = int(floor((game/2.)+.5))
        nextup = "u" if game%2==1 else "l"
        side = "left" if game < 17 else "right"

        col = 2 if game < 17 else -3
        row = ((game-1)%16) * 3

        spacers.append(row+2)

        tid = int(floor((game-1)/8)*18+((game-1)%8)*2+1)
        table[row][col] = '<td round=1 game=%s upper="" side="%s"><a team=%s href="#2-%s-%s">%s</a></td>' % (game, side, tid, nextroundgame, nextup, teams[tid])
        if game not in [1,9,17,25]:
            table[row+1][col] = '<td round=1 game=%s lower="" side="%s"><a team=%s href="#2-%s-%s">%s</a></td>' % (game, side, tid+1, nextroundgame, nextup, teams[tid+1])
        else:
            table[row+1][col] = '<td round=1 game=%s lower="" side="%s">&nbsp;</td>' % (game, side)

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

    file("kumquats.html", 'w').write(Template(filename="bracket_template.html").render(table=table, spacers=spacers))

def read_kenpom():
    #kenpom data notes:
    #team, raw tempo, raw tempo rank, adj tempo, adj tempo rank, raw OE, raw OE rank, adj OE, adj OE rank, raw DE, raw DE rank, adj DE, adjDE rank, kenpom ranking, kenpom rank
    teams = {}
    for line in file("kenpom_2_17_11.csv"):
        team, _, _, tempo, temporank, _, _, oe, oerank, _, _, de, derank, kenpom, kenpomrank = line.split(",")
        teams[team] = (tempo, temporank, oe, oerank, de, derank, kenpom, kenpomrank)
    return teams

if __name__=="__main__":
    teams = read_kenpom()
    output_bracket(teams)
