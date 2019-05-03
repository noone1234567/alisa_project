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
    global topline, midline, botline, tpl, vbar, pieces
    user_id = req['session']['user_id']
    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}]
    logging.info(req['request']['command'])
    if req['session']['new']:
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
        start_position = (
            [
                (-4, -2, -3, -5, -6, -3, -2, -4),
                (-1,) * 8,
            ] +
            [ (0,) * 8 ] * 4 +
            [
                (1,) * 8,
                (4, 2, 3, 5, 6, 3, 2, 4),
            ]
        )
        game = lambda squares: "\n".join(_game(squares))
        game.__doc__ = """Return the chessboard as a string for a given position.
            position is a list of 8 lists or tuples of length 8 containing integers
        """
        res['response']['text'] = game(start_position) + '\n　 A　  B　  C　  D　  E　  F　  G　  H'
        return
    return

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
