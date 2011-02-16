from math import floor
from mako.template import Template

bkt = eval(file("teams.dat").read())

# 11 columns = len(round 1,2,3,4,5,6,5,4,3,2,1)
# 64 rows = 2 for every team per side
table = [['<td>&nbsp;</td>']*13 for _ in range(64)]

#this year the west plays the southeast and the southwest plays the east.
#but we'll pretend with last year's data that the midwest plays the west
upper = False
for game in range(1,33):
    nextroundgame = int(floor((game/2.)+.5))
    upper = False if upper else True
    upstring = "upper" if upper else "lower"
    nextup = "u" if game%2==1 else "l"
    side = "left" if game < 17 else "right"

    col = 0 if game < 17 else -1
    row = ((game-1) % 16)*4

    tid = (game-1)*2+1
    table[row][col] = '<td round=1 game=%s upper="" side="%s"><a team=%s href="#2-%s-%s">team%s</a></td>' % (game, side, tid, nextroundgame, nextup, tid)
    table[row+1][col] = '<td round=1 game=%s side="%s">&nbsp;</td>' % (game, side)
    table[row+2][col] = '<td round=1 game=%s lower="" side="%s"><a team=%s href="#2-%s-%s">team%s</a></td>' % (game, side, tid+1, nextroundgame, nextup, tid+1)

upper = False
for game in range(1, 17):
    nextroundgame = int(floor((game/2)+.5))+1
    upper = False if upper else True
    upstring = "upper" if upper else "lower"
    nextup = "u" if game%2==1 else "l"
    side = "left" if game < 9 else "right"
    
    col = 1 if game < 9 else -2
    row = ((game-1) % 8)*8+1

    table[row][col] = '<td round=2 game=%s upper="" side="%s"></td>' % (game, side)
    table[row+1][col] = '<td round=2 game=%s side="%s"></td>' % (game, side)
    table[row+2][col] = '<td round=2 game=%s side="%s"></td>' % (game, side)
    table[row+3][col] = '<td round=2 game=%s side="%s"></td>' % (game, side)
    table[row+4][col] = '<td round=2 game=%s lower="" side="%s"></td>' % (game, side)

upper = False
for game in range(1, 9):
    nextroundgame = int(floor((game/2)+.5))+1
    upper = False if upper else True
    upstring = "upper" if upper else "lower"
    nextup = "u" if game%2==1 else "l"
    side = "left" if game < 5 else "right"
    
    col = 2 if game < 5 else -3
    row = ((game-1) % 4)*16+3

    table[row][col] = '<td round=3 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1,8):
        table[row+i][col] = '<td round=3 game=%s side="%s"></td>' % (game, side)
    table[row+8][col] = '<td round=3 game=%s lower="" side="%s"></td>' % (game, side)

upper = False
for game in range(1, 5):
    nextroundgame = int(floor((game/2)+.5))+1
    upper = False if upper else True
    upstring = "upper" if upper else "lower"
    nextup = "u" if game%2==1 else "l"
    side = "left" if game < 3 else "right"
    
    col = 3 if game < 3 else -4
    row = ((game-1) % 2)*32+5

    table[row][col] = '<td round=4 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1,18):
        table[row+i][col] = '<td round=4 game=%s side="%s"></td>' % (game, side)
    table[row+18][col] = '<td round=4 game=%s lower="" side="%s"></td>' % (game, side)

upper = False
for game in range(1, 3):
    nextroundgame = int(floor((game/2)+.5))+1
    upper = False if upper else True
    upstring = "upper" if upper else "lower"
    nextup = "u" if game%2==1 else "l"
    side = "left" if game == 1 else "right"
    
    col = 4 if game == 1 else -5
    row = 15

    table[row][col] = '<td round=5 game=%s upper="" side="%s"></td>' % (game, side)
    for i in range(1,32):
        table[row+i][col] = '<td round=5 game=%s side="%s"></td>' % (game, side)
    table[row+32][col] = '<td round=5 game=%s lower="" side="%s"></td>' % (game, side)

table[28][5]  = '<td round=6 game=1 upper="" side="left"></td>'
table[36][-6] = '<td round=6 game=1 upper="" side="right"></td>'

table[32][6] = '<td round=7 game=1 upper="" side="left"></td>'

file("bananas.html", 'w').write(Template(filename="test2_mako.html").render(table=table))
