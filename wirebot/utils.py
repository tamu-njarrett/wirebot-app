import simple_websocket, os
from flask import request, current_app
from sqlalchemy import MetaData, update
from wirebot import db
from wirebot.models import Status, Buttons

# update status message to Jetson to start wirebot operation
def run_wirebot():
    db.session.execute(update(Buttons), [{'id': 1, 'start': 1}])
    db.session.commit()

# update status message to Jetson to stop wirebot operation
def stop_wirebot():
    db.session.execute(update(Buttons), [{'id': 1, 'stop': 1}])
    db.session.commit()

def reset_buttons():
    db.session.execute(update(Buttons), [{'id': 1, 'start': 0}])
    db.session.execute(update(Buttons), [{'id': 1, 'stop': 0}])
    db.session.commit()

# Row (id) 1 of status SQL class holds boolean status code
# Each function updates the row with appropriate 1's or 0's
def reset_status():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'connection': 0},
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 0},
            {'id': 1, 'shifting': 0},
            {'id': 1, 'finishing': 0},
        ],
    )
    db.session.commit()

def connection():
    db.session.execute(update(Status), [{'id': 1, 'connection': 1}])
    db.session.commit()

def capturing():
    db.session.execute(update(Status),[{'id': 1, 'capturing': 1}])
    db.session.commit()

def rotating():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 1},
        ],
    )
    db.session.commit()

def shifting():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'rotating': 0},
            {'id': 1, 'shifting': 1},
        ],
    )
    db.session.commit()

def finishing():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 0},
            {'id': 1, 'shifting': 0},
            {'id': 1, 'finishing': 1},
        ],
    )
    db.session.commit()


def send_status_update(status_update):
    ws = simple_websocket.Server(request.environ)
    if ws.connected:
        print('Connected, preparing to send status update...')
    try:
        while True:
            ws.send(f'status={status_update}')
            data = ws.receive()
            print(data)

    except simple_websocket.ConnectionClosed:
        print(f'Client disconnected, code: {ws.close_reason}')

    ws.close()

    return ''
