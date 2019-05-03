# -*-coding: utf8-*-
from flask import Flask, request
import logging
import json
import requests

#https://www.pythonanywhere.com/user/alwin123/files/home/alwin123
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}]
    logging.info(req['request']['command'])
    if req['session']['new']:
        start_pos = 'r n b q k b n r\np p p p p p p p\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\nP P P P P P P P\nR N B Q K B N R'
        res["response"]["text"] = make_field(start_pos)
        return
    return

def make_field(bad_field):
    global topline, midline, botline, tpl, pieces, vbar
    bad_field = list(map(lambda x: x.split(), bad_field.split('\n')))
    bad_good = {'r':4, 'n':2, 'b':3, 'q':5,'k':6, 'p':1, 'R':-4, 'N':-2, 'B':-3, 'Q':-5, 'K':-6, 'P':-1, '.':0}
    for el in range(len(bad_field)):
        for elim in range(len(bad_field[el])):
            bad_field[el][elim] = bad_good[bad_field[el][elim]]
    version_info = (0, 1)
    version = ".".join(map(str, version_info))
    # some noise
    pieces = u''.join(chr(9812 + x) for x in range(12))
    pieces = u' ' + pieces[:6][::-1] + pieces[6:]
    allbox = u''.join(chr(9472 + x) for x in range(200))
    box = [ allbox[i] for i in (2, 0, 12, 16, 20, 24, 44, 52, 28, 36, 60) ]
    (vbar, hbar, ul, ur, ll, lr, nt, st, wt, et, plus) = box
    h3 = hbar * 2
    # useful constant unicode strings to draw the square borders
    topline = '. ' +ul + (h3 + nt) * 7 + h3 + ur
    midline = '. '+wt + (h3 + plus) * 7 + h3 + et
    botline = '. ' +ll + (h3 + st) * 7 + h3 + lr
    tpl = u' {0}  ' + vbar
    game = lambda squares: "\n".join(_game(squares))
    game.__doc__ = """Return the chessboard as a string for a given position.
        position is a list of 8 lists or tuples of length 8 containing integers
    """
    ans = game(bad_field) + '\n　 A　  B　  C　  D　  E　  F　  G　  H'
    return ans

def inter(num, *args):
    """Return a unicode string with a line of the chessboard.

    args are 8 integers with the values
        0 : empty square
        1, 2, 3, 4, 5, 6: white pawn, knight, bishop, rook, queen, king
        -1, -2, -3, -4, -5, -6: same black pieces
    """
    assert len(args) == 8
    listi = []
    for a in args:
        if a == 0:
            listi.append(tpl.format(pieces[a]))
        else:
            tpl1 = ' {0}  ' + vbar
            listi.append(tpl1.format(pieces[a]))
    return str(num) + vbar + ''.join(listi)

def _game(position):
    yield topline
    yield inter(8, *position[0])
    for row in range(len(position[1:])):
        yield midline
        yield inter(7 - row, *position[1:][row])
    yield botline

if __name__ == '__main__':
    app.run()

