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
    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True},
                                  {'title': 'http://translate.yandex.ru/', 'hide': True, 'url': 'http://translate.yandex.ru/'}]
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
        topline = ul + (h3 + nt) * 7 + h3 + ur
        midline = wt + (h3 + plus) * 7 + h3 + et
        botline = ll + (h3 + st) * 7 + h3 + lr
        tpl = u' {0} ' + vbar
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
        res['response']['text'] = game(start_position)
        return
    return


def translate(word):
    lang = "en"
    key = "trnsl.1.1.20190430T184245Z.d64c8ccf0b01b8d1.8221599076bea49f91cbc451af19b77fdcc703e2"
    req = "https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&text={}&lang={}".format(key, word, lang)

    response = requests.get(req)

    return response.json()['text'][0] if response else None

def inter(*args):
    """Return a unicode string with a line of the chessboard.

    args are 8 integers with the values
        0 : empty square
        1, 2, 3, 4, 5, 6: white pawn, knight, bishop, rook, queen, king
        -1, -2, -3, -4, -5, -6: same black pieces
    """
    assert len(args) == 8
    return ' ' + vbar + ''.join((tpl.format(pieces[a]) for a in args))

def _game(position):
    yield topline
    yield inter(*position[0])
    for row in position[1:]:
        yield midline
        yield inter(*row)
    yield botline

if __name__ == '__main__':
    app.run()
