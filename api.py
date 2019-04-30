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


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    global board
    if req['session']['new']:
        board = chess.Board()
        sessionStorage[user_id] = {'suggests': ["Помощь", "Посмотреть поле", "Что ты умеешь?"]}
        res['response']['text'] = 'Привет! Сыграем партию в шахматы? Вы играете белыми. Можете сделать ход "е2е4" или другой.'
        return
    res['response']['buttons'] = get_suggests(user_id)

    if board.is_game_over():
        res['response']['text'] = 'Вы выиграли. Хотеите играть снова?'
        sessionStorage[user_id] = {'suggests': [
            "Нет",
            "Да"]}
        if req['request']['original_utterance'].lower() == 'нет':
            res['response']['end_session'] = True
        else:
            res['response']['text'] = 'Отлично, сыграем ещё раз!'
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
        res['response']['text'] = str(board).replace('r', '♜').replace('n', '♞').replace('b', '♝').replace('q', '♛')\
            .replace('k', '♚').replace('p', '♟').replace('R', '♖').replace('N', '♘').replace('B', '♗')\
            .replace('Q', '♕').replace('K', '♔').replace('P', '♙').replace('.', ' ')
        return

    try:
        mymv = chess.Move.from_uci(a)
        board.push_san(board.san(mymv))

        b = board.legal_moves
        mv = chess.Move.from_uci(str(random.choice(list(b))))
        board.push_san(board.san(mv))
        res['response']['text'] = str(mv)
    except Exception as e:
        res['response']['text'] = 'Так ходить нельзя!'
        return


# Функция возвращает подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем подсказки из массива.
    suggests = [{'title': suggest, 'hide': True}
                for suggest in session['suggests']]

    return suggests


if __name__ == '__main__':
    app.run()
