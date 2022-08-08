import copy

from flask import Flask, render_template,session,request
from flask_session import Session
from flask_socketio import SocketIO, emit
from uuid import uuid4
from Web_Server.game_backend.game_handler import JointPursuitGame
import time

app = Flask(__name__)
APP_KEY = '92659'
app.config['SECRET_KEY'] = APP_KEY
# configure the session, making it permanent and setting the session type to the filesystem.
# app.config["SESSION_PERMANENT"] = True #set the session to permanent. This means that the session cookies won’t expire when the browser closes.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem" # We set the session type to the filesystem, which means that the cookies are going to be stored locally on the server-side.
Session(app)
app.config['SECRET_KEY'] = uuid4().hex # Configure secret key for encryption
app.debug = True
socketio = SocketIO(app)
GAME = JointPursuitGame()



@socketio.on('connect', namespace='/test')
def connect():
    """
    store in the session the user socket ID sid. We store it when the user first connects to the page using.
    When the connect() event happens, we store the user socket ID on the session variable sid.
    """
    session['sid'] = request.sid

@app.route("/", methods=['GET', 'POST'])
def home():
    global timer_start
    GAME.update()
    if request.method == 'POST':
        is_pretrial = (GAME.MASTER_STAGE == GAME.MASTER_STAGES['pretrial'])
        is_trial    = (GAME.MASTER_STAGE == GAME.MASTER_STAGES['trial'])
        is_debrief  = (GAME.MASTER_STAGE == GAME.MASTER_STAGES['debrief'])
        is_close    = (GAME.MASTER_STAGE == GAME.MASTER_STAGES['close'])
        #####################################################################################
        # PRETRIAL STAGE ####################################################################
        if is_pretrial:
            if request.form.get("submit_back"):
                GAME.pretrial_stage -= 1
                print(f'PRETRIAL: back button pressed => stage = {GAME.pretrial_stage}')
            elif request.form.get("submit_continue"):
                GAME.pretrial_stage += 1
                print(f'PRETRIAL: continue button pressed => stage = {GAME.pretrial_stage}')
            elif request.form.get("submit_survey_response"):
                responses = [request.form[f"row-{iQ+1}"] for iQ in range(7)]
                print(f'-------------------------')
                print(f'PRETRIAL SURVEY RESPONSES')
                print(f'-------------------------')
                for i,response in enumerate(responses): print(f'\t| Q{i}: {response}')
                GAME.pretrial_stage += 1
            GAME.pretrial_stage = max(GAME.pretrial_stage, 0)
        #####################################################################################
        # TRIAL STAGE #######################################################################
        elif is_trial:
            if request.form.get("submit_play"):
                timer_start = time.time()
                GAME.trial_stage += 1
                print(f'TRIAL: beginining game => stage = {GAME.trial_stage}')
            elif request.form.get("submit_survey_response"):
                responses = [request.form.get(f"row-{iQ+1}") for iQ in range(7)]
            GAME.pretrial_stage = max(GAME.pretrial_stage, 0)

        #####################################################################################
        # DEBRIEF STAGE #####################################################################
        elif is_debrief:
            pass
        elif is_close:
            pass
        else:
            pass
        #####################################################################################
        # RENDER ############################################################################
        GAME.report()
        return GAME.get_page()

    return GAME.get_page()


@socketio.on('next_pos')
def next_pos(message):
    print(f'ACTOiM DETECTED: ')
    print(f'\t| pos0 = {GAME.pos}')

    if message['action']   == 'left':   pos = GAME.move_player([-1 , 0])
    elif message['action'] == 'right':  pos = GAME.move_player([ 1 , 0])
    elif message['action'] == 'up':     pos = GAME.move_player([ 0, -1])
    elif message['action'] == 'down':   pos = GAME.move_player([ 0,  1])
    else: pos = GAME.move_player([0, 0])
    # GAME.pos[1] = GAME.pos[2] #<============= DEBUGGING =========================-
    # GAME.player_pen = -5 #<============= DEBUGGING =========================-

    # RESPOND TO THE CLIENT --------------------
    # Emit the updated position back to canvas.js
    # if : socketio.emit('game_running', {"running": 1}, room=session['sid'])
    data = {}
    data['pos'] = pos
    data['timer'] = GAME.get_timer()
    data['moves'] = GAME.moves
    data['player_pen'] = GAME.player_pen
    data['received_penalty'] = GAME.check_player_in_penalty()
    data['finished'] = GAME.check_finished()

    for key in data: print(f'\t| {key} = {data[key]}')
    # socketio.emit('update_status',data, room=session['sid'])
    socketio.emit('update_status', data)



##########################################################
# UPDATE TIMER FREQUENTLY ################################
enable_timer = True
timer_start = time.time()
def push_timer():
    delay = 0.1
    while True:
        with app.test_request_context('/'):
            now = time.time()
            GAME.timer = (now-timer_start) % 2 - 1
            GAME.moves = 20-int((now - timer_start)/2)
            data = {}
            data['timer'] = GAME.get_timer()
            data['moves'] = GAME.moves

            # data = {}
            # data['pos'] = GAME.pos
            # data['timer'] = GAME.get_timer()
            # data['moves'] = GAME.moves
            # data['player_pen'] = GAME.player_pen
            # data['received_penalty'] = GAME.check_player_in_penalty()
            # data['finished'] = GAME.check_finished()

            # socketio.emit('update_timer', {'timer': GAME.get_timer()})
            socketio.emit('update_timer', data)
            socketio.sleep(delay)












##########################################################
# RUN APP ################################################
if __name__ == "__main__":
    # app.run(debug=True)
    socketio.start_background_task(target=push_timer)
    socketio.run(app,host="192.168.0.137",port=8080, debug=True,use_reloader=False)
