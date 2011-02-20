from math import floor
from mako.template import Template

bkt = eval(file("teams.dat").read())

# 11 columns = len(round 1,2,3,4,5,6,5,4,3,2,1)
# 64 rows = 2 for every team per side
table = [['<td></td>']*13 for _ in range(47)]

#this year the west plays the southeast and the southwest plays the east.
game_order = [1,8,5,4,6,3,7,2]
divs = ["West", "Southeast", "Southwest", "East"]
tid = 1
teams = {}
for div in divs:
    for game in game_order:
        teams[tid] = bkt[div][game]
        tid += 1
        teams[tid] = bkt[div][17-game]
        tid += 1
print teams

spacers = []

for game in range(1,33):
    nextroundgame = int(floor((game/2.)+.5))
    nextup = "u" if game%2==1 else "l"
    side = "left" if game < 17 else "right"

    col = 0 if game < 17 else -1
    row = ((game-1)%16) * 3

    spacers.append(row+2)

    tid = (game-1)*2+1
    table[row][col] = '<td round=1 game=%s upper="" side="%s"><a team=%s href="#2-%s-%s">%s</a></td>' % (game, side, tid, nextroundgame, nextup, teams[tid])
    table[row+1][col] = '<td round=1 game=%s lower="" side="%s"><a team=%s href="#2-%s-%s">%s</a></td>' % (game, side, tid+1, nextroundgame, nextup, teams[tid+1])

for game in range(1, 17):
    side = "left" if game < 9 else "right"
    
    col = 1 if game < 9 else -2
    row = ((game-1) % 8)*6

    table[row][col] = '<td round=2 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1, 3):
        table[row+i][col] = '<td round=2 game=%s side="%s"></td>' % (game, side)
    table[row+3][col] = '<td round=2 game=%s lower="" side="%s"></td>' % (game, side)

for game in range(1, 9):
    side = "left" if game < 5 else "right"
    
    col = 2 if game < 5 else -3
    row = ((game-1) % 4)*12+1

    table[row][col] = '<td round=3 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1,6):
        table[row+i][col] = '<td round=3 game=%s side="%s"></td>' % (game, side)
    table[row+6][col] = '<td round=3 game=%s lower="" side="%s"></td>' % (game, side)

for game in range(1, 5):
    side = "left" if game < 3 else "right"
    
    col = 3 if game < 3 else -4
    row = ((game-1) % 2)*24+4

    table[row][col] = '<td round=4 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1,14):
        table[row+i][col] = '<td round=4 game=%s side="%s"></td>' % (game, side)
    table[row+14][col] = '<td round=4 game=%s lower="" side="%s"></td>' % (game, side)

for game in range(1, 3):
    side = "left" if game == 1 else "right"
    
    col = 4 if game == 1 else -5
    row = 9

    table[row][col] = '<td round=5 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1,25):
        table[row+i][col] = '<td round=5 game=%s side="%s"></td>' % (game, side)
    table[row+25][col] = '<td round=5 game=%s lower="" side="%s"></td>' % (game, side)

table[17][5]  = '<td round=6 game=1 upper="" side="left"></td>'
table[27][-6] = '<td round=6 game=1 lower="" side="right"></td>'

table[22][6] = '<td round=7 game=1 upper="" lower="" side="left"></td>'

file("kumquats.html", 'w').write(Template(filename="bracket_template.html").render(table=table, spacers=spacers))

#kenpom data notes:
#raw tempo, raw tempo rank, adj tempo, adj tempo rank, raw OE, raw OE rank, adj OE, adj OE rank, raw DE, raw DE rank, adj DE, adjDE rank, kenpom ranking, kenpom rank
