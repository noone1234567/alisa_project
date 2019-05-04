# импортируем библиотеки
from flask import Flask, request
import logging
import chess
import random

import json


app = Flask(__name__)
board = chess.Board()


logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи библиотеки json
    # преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def make_field(bad_field):
    def _game(position):
        yield topline
        yield inter(8, *position[0])
        for row in range(len(position[1:])):
            yield midline
            yield inter(7 - row, *position[1:][row])
        yield botline

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
                tpl1 = '{0}' + vbar
                listi.append(tpl1.format(pieces[a]))
        return str(num) + vbar + ''.join(listi)

    global topline, midline, botline, tpl, pieces, vbar
    bad_field = list(map(lambda x: x.split(), bad_field.split('\n')))
    bad_good = {'r': -4, 'n': -2, 'b': -3, 'q': -5, 'k': -6, 'p': -1, 'R': 4, 'N': 2, 'B': 3, 'Q': 5, 'K': 6, 'P': 1,
                '.': 0}
    for el in range(len(bad_field)):
        for elim in range(len(bad_field[el])):
            bad_field[el][elim] = bad_good[bad_field[el][elim]]
    # some noise
    pieces = u''.join(chr(9812 + x) for x in range(12))
    pieces = u'　' + pieces[:6][::-1] + pieces[6:]
    allbox = u''.join(chr(9472 + x) for x in range(200))
    # box = [allbox[i] for i in (2, 0, 12, 16, 20, 24, 44, 52, 28, 36, 60)]
    # (vbar, hbar, ul, ur, ll, lr, nt, st, wt, et, plus) = box
    (vbar, hbar, ul, ur, ll, lr, nt, st, wt, et, plus) = '┇ ┅ ┏ ┓ ┗ ┛ ┳ ┻ ┣ ┫ ╋'.split()

    h3 = hbar  # * 2
    # useful constant unicode strings to draw the square borders
    topline = ' ' + ul + (h3 + nt) * 7 + h3 + ur
    midline = ' ' + wt + (h3 + plus) * 7 + h3 + et
    botline = ' ' + ll + (h3 + st) * 7 + h3 + lr
    tpl = u'{0}' + vbar
    game = lambda squares: "\n".join(_game(squares))
    game.__doc__ = """Return the chessboard as a string for a given position.
        position is a list of 8 lists or tuples of length 8 containing integers
    """
    ans = game(bad_field) + '\n　  A　 B　 C　 D　 E　 F　 G　 H'
    return ans


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    global board
    if req['session']['new']:
        board = chess.Board()
        sessionStorage[user_id] = {'suggests': ["Помощь", "Посмотреть поле", "Что ты умеешь?"]}
        res['response'][
            'text'] = 'Привет! Сыграем партию в шахматы? Вы играете белыми. Можете сделать ход "е2е4" или другой.'
        res['response']['buttons'] = get_suggests(user_id)
        return
    res['response']['buttons'] = get_suggests(user_id)

    if board.is_game_over():
        res['response']['text'] = 'Вы выиграли. Хотеите играть снова?'
        sessionStorage[user_id] = {'suggests': [
            "Нет",
            "Да"]}
        return
    if req['request']['original_utterance'].lower() == 'нет':
        res['response']['end_session'] = True
        return 
    elif req['request']['original_utterance'].lower() == 'да':
        res['response']['text'] = 'Отлично, сыграем ещё раз!'
        sessionStorage[user_id] = {'suggests': ["Помощь", "Посмотреть поле", "Что ты умеешь?"]}
        board = chess.Board()
        return

    res['response']['text'] = 'Ваш ход'
    a = req['request']['original_utterance']
    if not a:
        return

    if a.lower() == 'помощь' or a.lower() == 'что ты умеешь?':
        res['response']['text'] = 'Это шахматы. Я пока только учусь. ' \
                                  'Ход указывайте в виде "e2e4". ' \
                                  'Если вы хотите увидеть всё игровое поле, нажмите кнопку "Посмотреть поле".'
        return

    elif a.lower() == 'посмотреть поле':
        res['response']['text'] = make_field(str(board))
        return

    try:
        mymv = chess.Move.from_uci(a)
        board.push_san(board.san(mymv))

        b = board.legal_moves
        mv = chess.Move.from_uci(str(random.choice(list(b))))
        board.push_san(board.san(mv))
        res['response']['text'] = str(mv)
    except Exception as e:
        res['response']['text'] = 'Так ходить нельзя! {}'.format(e)
        return

    '''user_id = req['session']['user_id']

    if req['session']['new']:

        sessionStorage[user_id] = {'suggests': [
                "Не хочу.",
                "Давай"]}

        res['response']['text'] = 'Привет! Сыграем в шахматы?'

        return
    if req['request']['original_utterance'].lower() in ['ладно',
                                                        'хорошо',
                                                        'давай',
                                                        'да',
                                                        'уговорила',
                                                        "договорились"]:
        # Пользователь согласился, прощаемся.

        game()

        """res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return"""

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = 'Ладно, пока!'
    return'''


# Функция возвращает подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем подсказки из массива.
    suggests = [{'title': suggest, 'hide': True}
                for suggest in session['suggests']]

    return suggests


if __name__ == '__main__':
    app.run()
