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
        sessionStorage[user_id] = {'suggests': ["Помощь", "Посмотреть поле"]}
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

    if a.lower() == 'помощь':
        res['response']['text'] = 'Это игра в шахматы. Почти. Во время вашего хода вы вводите значение вида "e2e4" ' \
                                  'Чтобы сходить фигурой с клетки e2 на клетку e4. Затем в мой ход я делаю тоже самое.'\
                                  'Также вы можете посмотреть всё поле.'
        return

    elif a.lower() == 'посмотреть поле':
        res['response']['text'] = str(board).replace('.', '  .  ')
        return

    try:
        mymv = chess.Move.from_uci(a)
        board.push_san(board.san(mymv))

        b = board.legal_moves
        mv = chess.Move.from_uci(str(random.choice(list(b))))
        board.push_san(board.san(mv))
        res['response']['text'] = str(mv)
    except Exception as e:
        res['response']['text'] = str(e)
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
