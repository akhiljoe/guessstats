import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import json
import random
import logging
import netifaces
import qrcode
import io
import random

room_code = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# --- Game state ---
players = []
avatars = {}
game_started = False
admin_name = None
current_turn = 0
answers = {}
scores = {}


def generate_room_code():
    return str(random.randint(1000, 9999))

# Questions setup
with open('questions.json') as f:
    all_questions = json.load(f)

used_questions = []
questions_queue = []
NUM_QUESTIONS_PER_PLAYER = 3
current_question = None

# Logging config
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

@app.route('/game')
def game():
    return render_template('game.html')

# --- Socket handlers ---
@socketio.on('join')
def handle_join(data):
    global admin_name
    name = data['name']
    avatar = data['avatar']
    if name not in players:
        players.append(name)
        avatars[name] = avatar
        scores[name] = 0
        if admin_name is None:
            admin_name = name
    emit('lobby_update', {
        'players': players,
        'avatars': avatars,
        'admin_name': admin_name
    }, broadcast=True)

@socketio.on('start_game')
def handle_start():
    global game_started, current_turn, questions_queue, used_questions, answers
    for name in players:
        scores[name] = 0
    answers.clear()

    logging.info("[EVENT] Received start_game event")
    if not game_started:
        game_started = True
        current_turn = 0
        used_questions.clear()
        total_required = NUM_QUESTIONS_PER_PLAYER * len(players)
        questions_queue[:] = random.sample(all_questions, k=min(len(all_questions), total_required))
        logging.info("[GAME] Game started 🎮")
        socketio.emit('game_started')
        socketio.sleep(2)
        start_round()


def start_round():
    global current_question
    if not players or not questions_queue:
        logging.info("[GAME] No more questions. Game over.")
        socketio.emit('game_over', {'scores': scores})
        return

    player = players[current_turn % len(players)]
    current_question = questions_queue.pop(0)
    used_questions.append(current_question)

    logging.info(f"[ROUND] Asking {player}: {current_question['question']} (Answer: {current_question['answer']}%)")
    socketio.emit('start_round', {
        'player': player,
        'avatar': avatars[player],
        'question': current_question['question'],
        'allPlayers': {p: avatars[p] for p in players}
    })

@socketio.on('submit_answer')
def handle_submit_answer(data):
    global answers
    player = data['player']
    percent = int(data['percent'])
    logging.info(f"[ANSWER] {player} answered {percent}%")

    answers['target'] = {'player': player, 'percent': percent}
    answers['revealed'] = False
    answers['guesses'] = {}
    socketio.emit('guess_hilo', {'player': player, 'percent': percent})

@socketio.on('submit_guess')
def handle_guess(data):
    global answers
    player = data['player']
    guess = data['guess']
    logging.info(f"[GUESS] {player} guessed {guess}")

    answers['guesses'][player] = guess
    logging.info(f"[GUESS DEBUG] {len(answers['guesses'])}/{len(players) - 1} guesses collected")

    if len(answers['guesses']) == len(players) - 1 and not answers.get('revealed'):
        answers['revealed'] = True
        reveal_answer_and_score()

def reveal_answer_and_score():
    global current_turn, answers, current_question

    real_val = current_question['answer']
    target = answers['target']
    tp = target['player']
    tv = target['percent']
    hilo = 'higher' if real_val > tv else 'lower'

    # Score guesses
    for p, g in answers['guesses'].items():
        if g == hilo:
            scores[p] += 100
            logging.info(f"[SCORE] {p} guessed correctly (+100 => {scores[p]})")
        else:
            logging.info(f"[SCORE] {p} guessed incorrectly")

    # Score target
    if abs(real_val - tv) <= 10:
        scores[tp] += 200
        logging.info(f"[SCORE] {tp} was close (+200 => {scores[tp]})")

    socketio.emit('reveal', {
        'real_answer': real_val,
        'scores': scores,
        'correct_direction': hilo,
        'target_player': tp,
        'next_turn': players[(current_turn + 1) % len(players)]
    })

    current_turn += 1

    if current_turn < NUM_QUESTIONS_PER_PLAYER * len(players):
        socketio.sleep(4)
        answers.clear()
        start_round()
    else:
        logging.info("[GAME] All rounds completed. Game over.")
        socketio.emit('game_over', {'scores': scores})

# --- Utility ---
def get_local_ip():
    try:
        return netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
    except:
        return '127.0.0.1'

@socketio.on('start_timer')
def handle_start_timer(data):
    emit('show_timer', {'timeLeft': data['timeLeft']}, broadcast=True)

@socketio.on('update_timer')
def handle_update_timer(data):
    emit('show_timer', {'timeLeft': data['timeLeft']}, broadcast=True)


@socketio.on('update_guessing_percent')
def handle_update_guessing_percent(data):
    emit('update_guessing_percent', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    logging.info(f"🌐 Game running at: http://{get_local_ip()}:5001")
    socketio.run(app, host='0.0.0.0', port=5001)
